"""Animate Warehouse Woes with lazy snapshots and atomic crate pushes.

Part 1 uses single-cell crates; part 2 expands each source column into two cells.
Solver steps are attempted moves, independently paced by the shared v1 player.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, replace
from pathlib import Path

from bruhanimate import GridViewport

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from animation_support import (  # noqa: E402
    argument_parser,
    ink,
    label,
    load_input,
    run_animation,
    run_options,
)

Point = tuple[int, int]
DIRECTIONS = {"^": (0, -1), ">": (1, 0), "v": (0, 1), "<": (-1, 0)}


@dataclass(frozen=True)
class Warehouse:
    """Immutable geometry; boxes store left anchors, never detached halves."""

    width: int
    height: int
    walls: frozenset[Point]
    boxes: frozenset[Point]
    robot: Point
    box_width: int

    @property
    def score(self):
        """Return GPS coordinates of all box left anchors."""
        return sum(100 * y + x for x, y in self.boxes)

    def occupancy(self):
        """Map occupied cells to whole-crate anchors for dependency discovery."""
        return {
            (x + offset, y): (x, y)
            for x, y in self.boxes
            for offset in range(self.box_width)
        }


@dataclass(frozen=True)
class Snapshot:
    """One immutable attempted move and a bounded recent robot trail."""

    warehouse: Warehouse
    phase: str
    index: int
    total: int
    moves: str
    move: str = ""
    pushed: frozenset[Point] = frozenset()
    blocked: frozenset[Point] = frozenset()
    trail: tuple[Point, ...] = ()
    pushes: int = 0
    failures: int = 0


def parse(text):
    """Validate a rectangular source map and all whitespace-wrapped moves.

    A blank line separates map and movement stream. Open map edges are allowed;
    stepping beyond the map is blocked. Input is never truncated or substituted.
    """
    lines = text.splitlines()
    separator = next((i for i, line in enumerate(lines) if not line.strip()), None)
    if separator is None or separator == 0:
        raise ValueError("Expected a warehouse map, a blank line, then moves")
    rows = tuple(lines[:separator])
    if not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Warehouse map must be nonempty and rectangular")
    if any(char not in "#.@O" for row in rows for char in row):
        raise ValueError("Warehouse map accepts only # . @ O")
    if sum(row.count("@") for row in rows) != 1:
        raise ValueError("Warehouse map must contain exactly one robot")
    moves = "".join("".join(lines[separator + 1 :]).split())
    if any(move not in DIRECTIONS for move in moves):
        raise ValueError("Moves must be ^ > v <, optionally separated by whitespace")
    return rows, moves


def make_warehouse(rows, part=2):
    """Expand a validated source map for the selected puzzle part."""
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    scale = part
    walls, boxes, robot = set(), set(), None
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            anchor = (x * scale, y)
            if char == "#":
                walls.update((anchor[0] + offset, y) for offset in range(scale))
            elif char == "O":
                boxes.add(anchor)
            elif char == "@":
                robot = anchor
    return Warehouse(
        len(rows[0]) * scale,
        len(rows),
        frozenset(walls),
        frozenset(boxes),
        robot,
        scale,
    )


def attempt(warehouse, move):
    """Resolve the complete crate dependency graph before committing a move.

    Vertical pushes can fan out into several wide crates. A single obstruction
    rejects the whole move, preserving every crate and both halves atomically.
    Returns the new warehouse, affected anchors, and obstructing cells.
    """
    dx, dy = DIRECTIONS[move]
    occupancy = warehouse.occupancy()
    target = warehouse.robot[0] + dx, warehouse.robot[1] + dy

    def obstacle(point):
        x, y = point
        return (
            point in warehouse.walls
            or not 0 <= x < warehouse.width
            or not 0 <= y < warehouse.height
        )

    if obstacle(target):
        return warehouse, frozenset(), frozenset((target,))
    pending = [occupancy[target]] if target in occupancy else []
    moving, blocked = set(pending), set()
    for x, y in pending:
        for offset in range(warehouse.box_width):
            destination = x + offset + dx, y + dy
            if obstacle(destination):
                blocked.add(destination)
            elif (other := occupancy.get(destination)) is not None:
                if other != (x, y) and other not in moving:
                    moving.add(other)
                    pending.append(other)
    if blocked:
        return warehouse, frozenset(moving), frozenset(blocked)
    shifted = frozenset((x + dx, y + dy) for x, y in moving)
    result = replace(
        warehouse, robot=target, boxes=(warehouse.boxes - moving) | shifted
    )
    return result, shifted, frozenset()


def snapshots(parsed, part=2):
    """Yield initial, attempted-move, and final states without saving a trace."""
    rows, moves = parsed
    warehouse = make_warehouse(rows, part)
    trail, pushes, failures = (), 0, 0
    yield Snapshot(warehouse, "ready", 0, len(moves), moves)
    for index, move in enumerate(moves, 1):
        previous = warehouse.robot
        warehouse, pushed, blocked = attempt(warehouse, move)
        if blocked:
            failures += 1
            phase = "blocked"
        else:
            trail = (*trail[-15:], previous)
            pushes += bool(pushed)
            phase = "push" if pushed else "move"
        yield Snapshot(
            warehouse,
            phase,
            index,
            len(moves),
            moves,
            move,
            pushed,
            blocked,
            trail,
            pushes,
            failures,
        )
    yield Snapshot(
        warehouse,
        "complete",
        len(moves),
        len(moves),
        moves,
        trail=trail,
        pushes=pushes,
        failures=failures,
    )


def draw(buffer, state):
    """Paint a clipped robot-following viewport without changing the snapshot."""
    if buffer.height() < 5 or buffer.width() == 0:
        return
    board = state.warehouse
    width, height = buffer.width(), buffer.height() - 5
    camera = (
        min(max(0, board.robot[0] - width // 2), max(0, board.width - width)),
        min(max(0, board.robot[1] - height // 2), max(0, board.height - height)),
    )
    viewport = GridViewport(
        buffer,
        board.width,
        board.height,
        region=(0, 3, width, height),
        camera=camera,
    )
    occupancy = board.occupancy()
    trail = {point: index for index, point in enumerate(state.trail)}
    for y in range(camera[1], min(board.height, camera[1] + height)):
        for x in range(camera[0], min(board.width, camera[0] + width)):
            point = x, y
            if point == board.robot:
                char, color = "@", 51
            elif point in occupancy:
                anchor = occupancy[point]
                char = "O" if board.box_width == 1 else "[" if point == anchor else "]"
                color = (
                    196
                    if state.blocked and anchor in state.pushed
                    else 226
                    if anchor in state.pushed
                    else 141
                )
            elif point in state.blocked:
                char, color = "X", 196
            elif point in board.walls:
                char, color = "#", 240
            elif point in trail:
                char, color = ".", 236 + trail[point] // 2
            else:
                char, color = ".", 234
            viewport.put(x, y, ink(char, color))
    label(buffer, 0, 2, "@ robot | gold push | red blocked | . trail", 245)
    begin = max(0, state.index - 12)
    end = min(state.total, begin + max(1, buffer.width() - 8))
    label(buffer, 0, buffer.height() - 2, "Moves: ", 245)
    for offset, move in enumerate(state.moves[begin:end], 7):
        index = begin + offset - 7
        color = 226 if index == state.index - 1 else 240 if index < state.index else 51
        label(buffer, offset, buffer.height() - 2, move, color)


def describe(state):
    """Summarize exact progress and GPS score, independent of viewport size."""
    return (
        f"Move {state.index}/{state.total} {state.move} | GPS {state.warehouse.score}"
        f" | pushes {state.pushes} | blocked {state.failures}"
    )


def main(argv=None):
    """Validate input, then let the shared player own the finite animation."""
    parser = argument_parser(__doc__, __file__, "datasmall4", rate=16)
    args = parser.parse_args(argv)
    parsed = load_input(parser, args, parse)
    return run_animation(
        snapshots(parsed, args.part),
        lambda state, buffer: draw(buffer, state),
        title=f"2024 Day 15: Warehouse Woes | Part {args.part}",
        describe=describe,
        **run_options(args),
    )


if __name__ == "__main__":
    main()
