"""Guard Gallivant: immutable patrol snapshots played by bruhanimate 1.x."""

from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bruhanimate import GridViewport  # noqa: E402

from animation_support import (  # noqa: E402
    argument_parser,
    ink,
    label,
    load_input,
    run_animation,
    run_options,
)

Point = tuple[int, int]
DIRECTIONS = ((0, -1), (1, 0), (0, 1), (-1, 0))
ARROWS = "^>v<"


@dataclass(frozen=True)
class Board:
    rows: tuple[str, ...]
    start: Point
    heading: int


@dataclass(frozen=True)
class Patrol:
    position: Point
    heading: int
    visited: frozenset[Point]
    recent: tuple[tuple[int, int, int], ...]
    looped: bool = False
    exited: bool = False


@dataclass(frozen=True)
class Snapshot:
    board: Board
    patrol: Patrol
    part: int
    phase: str = "patrol"
    obstacle: Point | None = None
    tested: int = 0
    candidates: int = 0
    loops: frozenset[Point] = frozenset()

    @property
    def answer(self):
        return len(self.patrol.visited) if self.part == 1 else len(self.loops)


def parse(text):
    """Validate a rectangular board containing exactly one oriented guard."""
    rows = tuple(text.strip().splitlines())
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Expected a nonempty rectangular guard map")
    guards = []
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char in ARROWS:
                guards.append(((x, y), ARROWS.index(char)))
            elif char not in ".#":
                raise ValueError(f"Invalid map character: {char!r}")
    if len(guards) != 1:
        raise ValueError("Expected exactly one guard")
    start, heading = guards[0]
    return Board(
        tuple(row.translate(str.maketrans("^>v<", "....")) for row in rows),
        start,
        heading,
    )


def patrol(board, obstacle=None, *, detailed=True):
    """Yield a finite patrol; direction is part of the loop-detection state.

    A compact trial yields only its final snapshot. Neither mode retains a
    history: at most four oriented states per map cell can be visited.
    """
    position, heading = board.start, board.heading
    seen, visited = set(), {position}
    recent = [(position[0], position[1], heading)]

    def state(**flags):
        return Patrol(position, heading, frozenset(visited), tuple(recent), **flags)

    if detailed:
        yield state()
    while (position, heading) not in seen:
        seen.add((position, heading))
        dx, dy = DIRECTIONS[heading]
        target = position[0] + dx, position[1] + dy
        x, y = target
        if not (0 <= y < len(board.rows) and 0 <= x < len(board.rows[0])):
            yield state(exited=True)
            return
        if board.rows[y][x] == "#" or target == obstacle:
            heading = (heading + 1) % 4
        else:
            position = target
            visited.add(position)
        recent.append((position[0], position[1], heading))
        recent[:] = recent[-12:]
        if detailed:
            yield state()
    yield state(looped=True)


def snapshots(board, part=2, *, show_steps=False):
    """Animate the baseline or obstacle trials, without storing solver traces.

    If the baseline exits, only its visited floor cells can affect the route.
    A looping baseline instead tests every legal floor cell, including cells
    whose obstruction leaves that existing loop unchanged.
    """
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    initial = Patrol(board.start, board.heading, frozenset({board.start}), ())
    yield Snapshot(board, initial, part, phase="scouting" if part == 2 else "patrol")
    if part == 1:
        for state in patrol(board):
            yield Snapshot(board, state, part)
        yield Snapshot(board, state, part, phase="complete")
        return
    baseline = next(patrol(board, detailed=False))
    floor = (
        baseline.visited
        if baseline.exited
        else {
            (x, y)
            for y, row in enumerate(board.rows)
            for x, char in enumerate(row)
            if char == "."
        }
    )
    candidates = sorted(floor - {board.start}, key=lambda point: (point[1], point[0]))
    loops = frozenset()
    final = Snapshot(board, baseline, part, phase="trials", candidates=len(candidates))
    yield final
    for index, obstacle in enumerate(candidates):
        for state in patrol(board, obstacle, detailed=show_steps):
            final = Snapshot(
                board, state, part, "trials", obstacle, index, len(candidates), loops
            )
            if show_steps:
                yield final
        if state.looped:
            loops = loops | {obstacle}
        final = replace(
            final,
            phase="loop" if state.looped else "exit",
            tested=index + 1,
            loops=loops,
        )
        yield final
    yield replace(final, phase="complete")


def draw(state, buffer):
    """Draw a clipped, following viewport; drawing never changes the patrol."""
    label(
        buffer,
        0,
        2,
        "# wall | cyan trail | yellow guard | X trial | O looping obstacle",
        245,
    )
    rows = state.board.rows
    width, height = len(rows[0]), len(rows)
    area_h = max(0, buffer.height() - 4)
    focus = (
        state.obstacle
        if state.obstacle is not None and state.phase != "trials"
        else state.patrol.position
    )
    visible_w, visible_h = max(1, buffer.width()), max(1, area_h)
    camera = (
        max(0, min(width - visible_w, focus[0] - visible_w // 2)),
        max(0, min(height - visible_h, focus[1] - visible_h // 2)),
    )
    view = GridViewport(
        buffer, width, height, camera=camera, region=(0, 3, buffer.width(), area_h)
    )

    def glyph(char, x, y):
        if char == "#":
            return ink("#", 244)
        return ink(".", 30 if (x, y) in state.patrol.visited else 235)

    view.draw(rows, glyph)
    for index, (x, y, heading) in enumerate(state.patrol.recent):
        view.put(x, y, ink(ARROWS[heading], 238 + index))
    for point in state.loops:
        view.put(*point, ink("O", 196))
    if state.obstacle is not None:
        view.put(*state.obstacle, ink("X", 196 if state.patrol.looped else 51))
    view.put(*state.patrol.position, ink(ARROWS[state.patrol.heading], 226))


def describe(state):
    result = (
        "loop" if state.patrol.looped else "exited" if state.patrol.exited else "moving"
    )
    if state.part == 1:
        return f"Visited: {state.answer} | Guard: {result}"
    return f"Trials: {state.tested}/{state.candidates} | Looping placements: {state.answer} | Guard: {result}"


def main(argv=None):
    parser = argument_parser(__doc__, __file__, "datasmall", rate=25)
    parser.add_argument(
        "--show-steps",
        action="store_true",
        help="Animate every movement inside each obstacle trial",
    )
    args = parser.parse_args(argv)
    board = load_input(parser, args, parse)
    return run_animation(
        snapshots(board, args.part, show_steps=args.show_steps),
        draw,
        title=f"2024 Day 6 - Guard Gallivant - Part {args.part}",
        describe=describe,
        **run_options(args),
    )


if __name__ == "__main__":
    main()
