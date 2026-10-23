"""Falling memory bytes, shortest-path waves, and the first blocking byte."""

from __future__ import annotations

import argparse
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from animation_support import (  # noqa: E402
    argument_parser,
    ink,
    label,
    load_input,
    positive_integer,
    run_animation,
    run_options,
)

Point = tuple[int, int]


def parse_input(text: str, size: int = 71) -> tuple[Point, ...]:
    """Read x,y byte coordinates, retaining duplicates and their input order."""
    if size < 1:
        raise ValueError("size must be positive")
    result = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        values = line.strip().split(",")
        if len(values) != 2:
            raise ValueError(f"Line {number}: expected x,y")
        try:
            point = tuple(int(value) for value in values)
        except ValueError as exc:
            raise ValueError(f"Line {number}: expected integer coordinates") from exc
        if not all(0 <= value < size for value in point):
            raise ValueError(f"Line {number}: coordinate outside {size}x{size} memory")
        result.append(point)
    return tuple(result)


@dataclass(frozen=True)
class Snapshot:
    """One immutable byte/search event; coordinates always remain board units."""

    size: int
    phase: str
    blocked: frozenset[Point]
    count: int = 0
    dropped: Point | None = None
    path: tuple[Point, ...] = ()
    visited: frozenset[Point] = frozenset()
    frontier: tuple[Point, ...] = ()
    blocker: Point | None = None
    distance: int | None = None


def search(size, blocked, count, dropped, *, batch=64):
    """Yield at most batch BFS removals per event and return a shortest path.

    Parents store one predecessor per cell; no path list is copied into the
    queue. Blocked endpoints never enter the search. Snapshot count is bounded
    by the board, and closing the source discards its local queue immediately.
    """
    start, goal = (0, 0), (size - 1, size - 1)
    if start in blocked or goal in blocked:
        return ()
    queue = deque([start])
    parents = {start: None}
    visited = set()
    processed = 0
    while queue:
        point = queue.popleft()
        visited.add(point)
        if point == goal:
            route = []
            while point is not None:
                route.append(point)
                point = parents[point]
            return tuple(reversed(route))
        x, y = point
        for neighbor in ((x + 1, y), (x, y + 1), (x - 1, y), (x, y - 1)):
            nx, ny = neighbor
            if (
                0 <= nx < size
                and 0 <= ny < size
                and neighbor not in blocked
                and neighbor not in parents
            ):
                parents[neighbor] = point
                queue.append(neighbor)
        processed += 1
        if processed % batch == 0:
            yield Snapshot(
                size,
                "search",
                blocked,
                count,
                dropped,
                visited=frozenset(visited),
                frontier=tuple(queue),
            )
    return ()


def snapshots(bytes_, *, part=2, size=71, prefix=1024, batch=64):
    """Animate part 1's explicit prefix or part 2's entire fall sequence lazily.

    Part 2 starts from empty memory so an early blocker cannot be skipped by
    --prefix. A retained valid route avoids unnecessary BFS after harmless
    drops; hitting that route triggers a new search. No byte is skipped.
    """
    if part not in (1, 2) or size < 1 or prefix < 0 or batch < 1:
        raise ValueError("invalid part, size, prefix, or search batch")
    if part == 1 and prefix > len(bytes_):
        raise ValueError("--prefix exceeds the input length; supply an explicit prefix")
    blocked = frozenset()
    yield Snapshot(size, "ready", blocked)
    if part == 1:
        for count, point in enumerate(bytes_[:prefix], 1):
            blocked = blocked | {point}
            yield Snapshot(size, "falling", blocked, count, point)
        path = yield from search(size, blocked, prefix, None, batch=batch)
        yield Snapshot(
            size,
            "complete",
            blocked,
            prefix,
            path=path,
            distance=len(path) - 1 if path else None,
        )
        return
    path = yield from search(size, blocked, 0, None, batch=batch)
    path_set = frozenset(path)
    count = 0
    for count, point in enumerate(bytes_, 1):
        blocked = blocked | {point}
        yield Snapshot(size, "falling", blocked, count, point, path=path)
        if point in path_set:
            path = yield from search(size, blocked, count, point, batch=batch)
            path_set = frozenset(path)
        if not path:
            yield Snapshot(size, "complete", blocked, count, point, blocker=point)
            return
        yield Snapshot(
            size, "route", blocked, count, point, path, distance=len(path) - 1
        )
    yield Snapshot(size, "complete", blocked, count, path=path, distance=len(path) - 1)


def draw(state, buffer):
    """Show all memory, compressing cells into a labeled overview if needed."""
    width = min(state.size * 2, buffer.width())
    height = min(state.size, max(0, buffer.height() - 5))
    if width <= 0 or height <= 0:
        return
    x0 = max(0, (buffer.width() - width) // 2)
    y0 = 3
    cells = {}

    def paint(points, char, color, priority):
        for x, y in points:
            screen = (x0 + x * width // state.size, y0 + y * height // state.size)
            if cells.get(screen, (-1, "", 0))[0] <= priority:
                cells[screen] = (priority, char, color)

    paint(((x, y) for y in range(state.size) for x in range(state.size)), ".", 236, 0)
    paint(state.visited, ".", 24, 1)
    paint(state.blocked, "#", 196, 2)
    paint(state.frontier, "o", 51, 3)
    paint(state.path, "*", 82, 4)
    paint(((0, 0),), "S", 226, 5)
    paint(((state.size - 1, state.size - 1),), "E", 226, 5)
    if state.dropped is not None:
        paint((state.dropped,), "X", 201 if state.blocker else 214, 6)
    for (x, y), (_, char, color) in cells.items():
        buffer.put_char(x, y, ink(char, color))
    overview = (
        " | compressed overview" if height < state.size or width < state.size else ""
    )
    label(
        buffer,
        0,
        buffer.height() - 2,
        "# fallen  o frontier  * route  X newest" + overview,
        245,
    )


def describe(state):
    if state.blocker is not None:
        return f"First blocking byte: {state.blocker[0]},{state.blocker[1]} | drop {state.count}"
    distance = (
        str(state.distance)
        if state.distance is not None
        else "unreachable"
        if state.phase == "complete"
        else "searching"
    )
    return (
        f"Bytes: {state.count} | shortest steps: {distance} | {state.size}x{state.size}"
    )


def nonnegative_integer(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("Value must not be negative")
    return number


def main(argv=None):
    parser = argument_parser(__doc__, __file__, "data", rate=30)
    parser.add_argument("--size", type=positive_integer, default=71)
    parser.add_argument(
        "--prefix",
        type=nonnegative_integer,
        default=1024,
        help="part 1 only: number of initial bytes",
    )
    parser.add_argument(
        "--search-batch",
        type=positive_integer,
        default=64,
        help="maximum BFS queue removals per playback step",
    )
    args = parser.parse_args(argv)
    bytes_ = load_input(parser, args, lambda text: parse_input(text, args.size))
    if args.part == 1 and args.prefix > len(bytes_):
        parser.error("--prefix exceeds input length; set --prefix explicitly")
    return run_animation(
        snapshots(
            bytes_,
            part=args.part,
            size=args.size,
            prefix=args.prefix,
            batch=args.search_batch,
        ),
        draw,
        title=f"2024 Day 18 / part {args.part}",
        describe=describe,
        **run_options(args),
    )


if __name__ == "__main__":
    main()
