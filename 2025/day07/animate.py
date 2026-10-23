"""Day 7 beam animation using bruhanimate 1.x; imports never start playback.

Run directly or through cli.py. Space pauses, n/right steps, +/- changes speed,
and q exits. Branch traces are sampled lazily; totals use dynamic programming.
The original implementation is retained in animate_legacy.py.
"""

from __future__ import annotations

import argparse
import math
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

from bruhanimate import (
    Buffer,
    CallbackEffect,
    FireworkSettings,
    GridViewport,
    Layer,
    Playback,
    Scene,
    TwinkleSettings,
    effect_registry,
    play,
)
from bruhcolor import bruhcolored

Point = tuple[int, int]
Edge = tuple[Point, Point]
Board = tuple[str, ...]
PALETTE = (196, 208, 190, 76, 21, 93)
# North/east/south/west bit masks produce junctions without direction bookkeeping.
GLYPHS = {
    1: "║",
    2: "═",
    4: "║",
    8: "═",
    5: "║",
    10: "═",
    3: "╚",
    9: "╝",
    6: "╔",
    12: "╗",
    7: "╠",
    13: "╣",
    11: "╩",
    14: "╦",
    15: "╬",
}


@dataclass(frozen=True)
class Totals:
    splitters: int
    timelines: int


@dataclass(frozen=True)
class Snapshot:
    path: tuple[Point, ...] = ()
    completed: frozenset[Edge] = frozenset()
    branch: int = 0
    pulse: int | None = None
    phase: str = "building"
    tick: int = 0


def parse_board(text: str) -> Board:
    """Validate one top-row S and a nonempty rectangular .^S board."""
    board = tuple(text.strip().splitlines())
    if not board or not board[0] or any(len(row) != len(board[0]) for row in board):
        raise ValueError("Input must be a nonempty rectangular board")
    if any(cell not in ".^S" for row in board for cell in row):
        raise ValueError("Input may contain only '.', '^', and 'S'")
    if sum(row.count("S") for row in board) != 1 or "S" not in board[0]:
        raise ValueError("Input must contain exactly one S in the top row")
    return board


def next_steps(board: Board, point: Point) -> tuple[tuple[Point, ...], ...]:
    """Return each next route suffix, including entry into a splitter."""
    x, y = point
    if y + 1 == len(board):
        return ()
    below = (x, y + 1)
    if board[y + 1][x] == "^":
        return tuple(
            (below, (nx, y + 1)) for nx in (x - 1, x + 1) if 0 <= nx < len(board[0])
        )
    return ((below,),)


def count_timelines(board: Board) -> Totals:
    """Count all timelines with one row of integer counts, without path traces."""
    counts = Counter({board[0].index("S"): 1})
    splitters = 0
    for y in range(len(board) - 1):
        following = Counter()
        for x, count in counts.items():
            splitters += board[y + 1][x] == "^"
            for suffix in next_steps(board, (x, y)):
                following[suffix[-1][0]] += count
        counts = following
    return Totals(splitters, sum(counts.values()))


def iter_branches(board: Board) -> Iterator[tuple[Point, ...]]:
    """Depth-first routes; retain pending branches rather than every timeline."""
    pending = [((board[0].index("S"), 0),)]
    while pending:
        path = pending.pop()
        if path[-1][1] == len(board) - 1:
            yield path
        else:
            pending.extend(
                path + suffix for suffix in reversed(next_steps(board, path[-1]))
            )


def branch_states(board: Board, max_branches: int = 100, pulse_length: int = 5):
    """Build/pulse a bounded sample, accumulating completed edges as snapshots."""
    if max_branches < 1 or pulse_length < 1:
        raise ValueError("Branch limit and pulse length must be positive")
    completed: set[Edge] = set()
    tick = branch = 0
    for branch, path in enumerate(islice(iter_branches(board), max_branches), 1):
        previous = frozenset(completed)
        for length in range(1, len(path) + 1):
            yield Snapshot(path[:length], previous, branch, tick=tick)
            tick += 1
        for pulse in range(len(path) + pulse_length):
            yield Snapshot(path, previous, branch, pulse, "pulsing", tick)
            tick += 1
        completed.update(zip(path, path[1:]))
    yield Snapshot(
        completed=frozenset(completed), branch=branch, phase="complete", tick=tick
    )


def row_states(board: Board):
    """Show the aggregate beam graph one row at a time without branch enumeration."""
    counts = Counter({board[0].index("S"): 1})
    completed: set[Edge] = set()
    yield Snapshot(path=((board[0].index("S"), 0),), phase="scanning")
    for y in range(len(board) - 1):
        following = Counter()
        for x, count in counts.items():
            for suffix in next_steps(board, (x, y)):
                completed.update(zip(((x, y), *suffix), suffix))
                following[suffix[-1][0]] += count
        counts = following
        yield Snapshot(completed=frozenset(completed), phase="scanning", tick=y + 1)
    yield Snapshot(completed=frozenset(completed), phase="complete", tick=len(board))


def viewport(board: Board, state: Snapshot, buffer: Buffer, spacing: int):
    """Center small boards and follow the current beam on oversized boards."""
    rows = max(0, buffer.height() - 3)
    columns = max(1, (buffer.width() + spacing - 1) // spacing)
    if state.path:
        index = (
            len(state.path) - 1
            if state.pulse is None
            else min(state.pulse, len(state.path) - 1)
        )
        x, y = state.path[index]
    else:
        x, y = max(
            (b for _, b in state.completed),
            key=lambda p: p[1],
            default=(board[0].index("S"), 0),
        )
    camera = (
        max(0, min(x - columns // 2, len(board[0]) - columns)),
        max(0, min(y - rows // 2, len(board) - rows)),
    )
    return GridViewport.from_rows(
        buffer,
        board,
        spacing=(spacing, 1),
        camera=camera,
        region=(0, 2, buffer.width(), rows),
    )


def colored(char: str, color: int) -> str:
    return bruhcolored(char, color=color).colored


def draw_snapshot(
    board: Board, state: Snapshot, buffer: Buffer, spacing=2, pulse_length=5
):
    """Draw current state only; fresh scene buffers eliminate manual erase sets."""
    grid = viewport(board, state, buffer, spacing)
    left, top = grid.to_screen(0, 0)
    right = left + (len(board[0]) - 1) * spacing + 1
    for y in range(max(2, top), min(buffer.height() - 1, top + len(board))):
        start, end = max(0, left), min(buffer.width(), right)
        if end > start:
            buffer.put_at(start, y, " " * (end - start))

    def glyph(cell, x, y):
        if cell == "^":
            return colored("✦", PALETTE[(x * 13 + y * 7) % len(PALETTE)])
        if cell == "S":
            return colored("S", 231)
        return colored("·", 232 + round(11.5 * (1 + math.sin(state.tick / 10 + x + y))))

    grid.draw(board, glyph)
    # Each visible screen cell stores connection bits, color priority, and color.
    lines = {}

    def segment(a, b, color, priority):
        ax, ay = a
        bx, by = b
        dx, dy = (bx > ax) - (bx < ax), (by > ay) - (by < ay)
        outward, inward = (2, 8) if dx > 0 else (8, 2) if dx < 0 else (4, 1)
        for step in range(abs(bx - ax) + abs(by - ay)):
            for x, y, bit in (
                (ax + dx * step, ay + dy * step, outward),
                (ax + dx * (step + 1), ay + dy * (step + 1), inward),
            ):
                if 0 <= x < buffer.width() and 2 <= y < buffer.height() - 1:
                    bits, old_priority, old_color = lines.get((x, y), (0, -1, color))
                    lines[x, y] = (
                        bits | bit,
                        max(priority, old_priority),
                        color if priority >= old_priority else old_color,
                    )

    for a, b in state.completed:
        segment(grid.to_screen(*a), grid.to_screen(*b), 28, 0)
    for index, (a, b) in enumerate(zip(state.path, state.path[1:]), 1):
        if state.pulse is not None and index < state.pulse - pulse_length:
            continue
        pulse = (
            state.pulse is not None
            and state.pulse - pulse_length <= index <= state.pulse
        )
        segment(
            grid.to_screen(*a),
            grid.to_screen(*b),
            231 if pulse else 45,
            2 if pulse else 1,
        )

    # Continue beams above/below the board without adding screen positions to state.
    sx, sy = grid.to_screen(board[0].index("S"), 0)
    if sy > 2:
        segment((sx, 2), (sx, sy), 28 if state.completed else 45, 0)
    exits = {b[0] for _, b in state.completed if b[1] == len(board) - 1}
    if state.path and state.path[-1][1] == len(board) - 1:
        exits.add(state.path[-1][0])
    for x in exits:
        sx, sy = grid.to_screen(x, len(board) - 1)
        if sy < buffer.height() - 2:
            segment(
                (sx, sy),
                (sx, buffer.height() - 2),
                28 if state.phase == "complete" else 45,
                0,
            )

    # Ripple age is derived from the snapshot, so repeated drawing is pure.
    for index, (x, y) in enumerate(state.path):
        if not index or board[y][x] != "^" or state.path[index - 1][1] == y:
            continue
        age = len(state.path) - index - 1 + (state.pulse or 0)
        radius = age / 2
        if not 0 < radius <= 15:
            continue
        cx, cy = grid.to_screen(x, y)
        for angle in range(0, 360, 10):
            theta = math.radians(angle)
            rx, ry = (
                round(cx + radius * math.cos(theta)),
                round(cy + radius * math.sin(theta) / 2),
            )
            anchor = (
                left <= rx < right
                and top <= ry < top + len(board)
                and (rx - left) % spacing == 0
            )
            if (
                0 <= rx < buffer.width()
                and 2 <= ry < buffer.height() - 1
                and not anchor
                and (rx, ry) not in lines
            ):
                buffer.put_char(rx, ry, colored("·", round(255 - 23 * radius / 15)))
    for (x, y), (bits, _, color) in lines.items():
        buffer.put_char(x, y, colored(GLYPHS[bits], color))


def run(
    board: Board,
    *,
    mode="branches",
    max_branches=100,
    steps_per_second=60,
    fps=60,
    spacing=2,
    frames=None,
    background=True,
    on_complete="hold",
):
    """Compose independent background effects, finite Playback, and status text."""
    if spacing < 1 or max_branches < 1:
        raise ValueError("Spacing and branch limit must be positive")
    if mode not in ("branches", "rows"):
        raise ValueError("Mode must be branches or rows")
    totals = count_timelines(board)
    states = (
        branch_states(board, max_branches) if mode == "branches" else row_states(board)
    )
    playback = Playback(
        states,
        lambda state, target: draw_snapshot(board, state, target, spacing),
        steps_per_second=steps_per_second,
    )

    def status(buffer):
        state = playback.state
        phase = (
            "Paused" if playback.paused else state.phase.title() if state else "Ready"
        )
        branch = (
            f" | Branch {state.branch if state else 0}/{min(max_branches, totals.timelines)}"
            if mode == "branches"
            else ""
        )
        buffer.put_at(
            0,
            0,
            f"Day 7 | Splitters: {totals.splitters} | Timelines: {totals.timelines}",
        )
        buffer.put_at(0, 1, f"{phase}{branch} | {playback.steps_per_second:g} steps/s")
        buffer.put_at(
            0, buffer.height() - 1, "Space pause | n/right step | +/- speed | q quit"
        )

    def build(buffer):
        layers = []
        if background:
            layers.extend(
                (
                    effect_registry.create(
                        "twinkle",
                        Buffer(buffer.height(), buffer.width()),
                        " ",
                        settings=TwinkleSettings(density=0.05),
                    ),
                    Layer(
                        effect_registry.create(
                            "firework",
                            buffer,
                            " ",
                            settings=FireworkSettings(
                                firework_type="random",
                                color_enabled=True,
                                color_type="twotone",
                                rate=0.02,
                            ),
                        ),
                        transparent=True,
                    ),
                )
            )
        return Scene(*layers, playback, CallbackEffect(status))

    return play(
        effect_factory=build,
        fps=fps,
        updates_per_second=60,
        frames=frames,
        event_handler=playback.handle_event,
        on_complete=on_complete,
    )


def positive_number(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Value must be positive and finite")
    return number


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("Value must be at least 1")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path(__file__).resolve().with_name("datasmall")
    )
    parser.add_argument("--mode", choices=("branches", "rows"), default="branches")
    parser.add_argument("--max-branches", type=positive_integer, default=100)
    parser.add_argument("--steps-per-second", type=positive_number, default=60)
    parser.add_argument("--fps", type=positive_number, default=60)
    parser.add_argument("--spacing", type=positive_integer, default=2)
    parser.add_argument("--frames", type=int)
    parser.add_argument("--no-background", action="store_true")
    parser.add_argument("--exit-on-complete", action="store_true")
    args = parser.parse_args(argv)
    if args.frames is not None and args.frames < 0:
        parser.error("--frames must not be negative")
    try:
        board = parse_board(args.input.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return run(
        board,
        mode=args.mode,
        max_branches=args.max_branches,
        steps_per_second=args.steps_per_second,
        fps=args.fps,
        spacing=args.spacing,
        frames=args.frames,
        background=not args.no_background,
        on_complete="exit" if args.exit_on_complete else "hold",
    )


if __name__ == "__main__":
    main()
