"""Day 4: simultaneous roll-removal waves, with an optional neighbor scanner."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from dataclasses import dataclass, replace
from itertools import islice
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from animation_support import (  # noqa: E402
    argument_parser,
    ink,
    load_input,
    run_animation,
    run_options,
)

from bruhanimate import Buffer, GridViewport  # noqa: E402

Point = tuple[int, int]
NEIGHBORS = tuple((dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dx or dy)


@dataclass(frozen=True)
class Board:
    width: int
    height: int
    rolls: frozenset[Point]


@dataclass(frozen=True)
class Snapshot:
    rolls: frozenset[Point]
    marked: frozenset[Point] = frozenset()
    removed: frozenset[Point] = frozenset()
    focus: Point = (0, 0)
    wave: int = 1
    total: int = 0
    phase: str = "scanning"
    progress: float = 0


def parse_board(text: str) -> Board:
    """Validate the complete rectangular .@ board without cropping its edges."""
    rows = text.strip().splitlines()
    if (
        not rows
        or not rows[0]
        or any(len(row) != len(rows[0]) for row in rows)
        or any(c not in ".@" for row in rows for c in row)
    ):
        raise ValueError("Input must be a nonempty rectangular board of '.' and '@'")
    return Board(
        len(rows[0]),
        len(rows),
        frozenset(
            (x, y) for y, row in enumerate(rows) for x, c in enumerate(row) if c == "@"
        ),
    )


def neighbor_count(rolls: frozenset[Point], point: Point) -> int:
    x, y = point
    return sum((x + dx, y + dy) in rolls for dx, dy in NEIGHBORS)


def roll_states(board: Board, part=2, *, detail=False) -> Iterator[Snapshot]:
    """Freeze eligibility per wave, then remove in bounded batches.

    Newly exposed rolls are considered only on the next wave. Detailed mode
    yields one neighbor inspection per roll; wave mode skips those inspections.
    Storage is O(board), with no growing trace or removed-roll history.
    """
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    state = Snapshot(board.rolls)
    yield state
    while True:
        marked = set()
        for point in sorted(state.rolls, key=lambda p: (p[1], p[0])):
            if neighbor_count(state.rolls, point) < 4:
                marked.add(point)
            if detail:
                yield replace(
                    state, marked=frozenset(marked), focus=point, phase="scanning"
                )
        eligible = frozenset(marked)
        if not eligible:
            yield replace(
                state, marked=frozenset(), removed=frozenset(), phase="complete"
            )
            return
        state = replace(
            state,
            marked=eligible,
            removed=frozenset(),
            focus=min(eligible, key=lambda p: (p[1], p[0])),
        )
        for sample in range(1, 5):
            yield replace(state, phase="marking", progress=sample / 4)
        if part == 1:
            yield replace(state, phase="complete", total=len(eligible))
            return
        ordered = iter(sorted(eligible, key=lambda p: (p[1], p[0])))
        while batch := tuple(islice(ordered, 32)):
            removed = frozenset(batch)
            state = replace(
                state,
                rolls=state.rolls - removed,
                marked=state.marked - removed,
                removed=removed,
                total=state.total + len(batch),
                focus=batch[-1],
                phase="removing",
            )
            for sample in range(1, 5):
                yield replace(state, progress=sample / 4)
        state = replace(
            state,
            marked=frozenset(),
            removed=frozenset(),
            wave=state.wave + 1,
            phase="scanning",
            progress=0,
        )


def draw_board(board: Board, state: Snapshot, buffer: Buffer):
    """Follow inspections/removals; show a whole-board density overview below."""
    width, height = buffer.width(), buffer.height()
    if height < 7:
        buffer.put_at(
            0, height // 2, f"Remaining: {len(state.rolls)} | Removed: {state.total}"
        )
        return
    region_height = max(1, height - 7)
    sx = 2 if board.width * 2 <= width else 1
    visible_columns = max(1, width // sx)
    camera = (
        min(
            max(0, state.focus[0] - visible_columns // 2),
            max(0, board.width - visible_columns),
        ),
        min(
            max(0, state.focus[1] - region_height // 2),
            max(0, board.height - region_height),
        ),
    )
    viewport = GridViewport(
        buffer,
        board.width,
        board.height,
        spacing=(sx, 1),
        camera=camera,
        region=(0, 3, width, region_height),
    )
    # Iterate only visible cells rather than the entire grid for each draw.
    for y in range(camera[1], min(board.height, camera[1] + region_height)):
        for x in range(camera[0], min(board.width, camera[0] + visible_columns)):
            point = (x, y)
            color = 46 if point in state.marked else 250
            if point == state.focus:
                color = 226
            elif (
                state.phase == "scanning"
                and abs(x - state.focus[0]) <= 1
                and abs(y - state.focus[1]) <= 1
            ):
                color = 51
            if point in state.rolls:
                viewport.put(x, y, ink("@", color))
            elif point in state.removed:
                viewport.put(x, y, ink("*", round(255 - state.progress * 20)))
            else:
                viewport.put(x, y, ink("·", 237))
    buffer.put_at(
        0,
        height - 4,
        f"Focus ({state.focus[0]},{state.focus[1]}) | Neighbors: {neighbor_count(state.rolls, state.focus)}/8 | <4 is removable",
    )
    # A per-column histogram retains global context when the viewport is cropped.
    buckets = [0] * width
    for x, _ in state.rolls:
        buckets[min(width - 1, x * width // board.width)] += 1
    peak = max(buckets, default=0) or 1
    for x, value in enumerate(buckets):
        buffer.put_char(x, height - 3, ink(" .:-=+*#@"[round(value * 8 / peak)], 51))
    buffer.put_at(
        0,
        height - 2,
        "Green: removable | Yellow: focus | Cyan: neighbors / column density",
    )


def run(board, *, part=2, detail=False, **options):
    return run_animation(
        roll_states(board, part, detail=detail),
        lambda state, buffer: draw_board(board, state, buffer),
        title=f"Day 4 | Part {part}",
        describe=lambda state: f"Wave {state.wave} | Available: {len(state.marked)} | {'Accessible' if part == 1 else 'Removed'}: {state.total} | Remaining: {len(state.rolls)}",
        **options,
    )


def main(argv=None):
    parser = argument_parser(__doc__, __file__, "datasmall")
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Inspect every roll's neighbors before each removal wave",
    )
    args = parser.parse_args(argv)
    board = load_input(parser, args, parse_board)
    return run(board, part=args.part, detail=args.detail, **run_options(args))


if __name__ == "__main__":
    main()
