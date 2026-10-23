"""Hoof It: height waves and exact trail scores with bruhanimate 1.x."""

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


@dataclass(frozen=True)
class Snapshot:
    rows: tuple[str, ...]
    part: int
    phase: str = "height wave"
    current: Point = (0, 0)
    height: int = 9
    processed: int = 0
    trailhead: Point | None = None
    highlighted: frozenset[Point] = frozenset()
    peaks: frozenset[Point] = frozenset()
    head_score: int = 0
    head_rating: int = 0
    heads_done: int = 0
    heads_total: int = 0
    score: int = 0
    rating: int = 0

    @property
    def answer(self):
        return self.score if self.part == 1 else self.rating


def parse(text):
    """Accept a nonempty rectangular height map; dots are impassable cells."""
    rows = tuple(text.strip().splitlines())
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Expected a nonempty rectangular height map")
    if any(char not in "0123456789." for row in rows for char in row):
        raise ValueError("Height maps may contain only digits and dots")
    return rows


def neighbors(rows, point):
    x, y = point
    for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(rows) and 0 <= nx < len(rows[0]):
            yield nx, ny


def snapshots(rows, part=2):
    """Count a height DAG bottom-up, then illuminate each trailhead's routes.

    Each cell stores an integer path count and a frozen set of reachable peaks.
    Converging paths are counted separately for part 2 but share peak sets for
    part 1. The source yields one cell or one trailhead at a time, never paths.
    """
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    levels = [[] for _ in range(10)]
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char != ".":
                levels[int(char)].append((x, y))
    state = Snapshot(rows, part, heads_total=len(levels[0]))
    yield state
    results = {}
    processed = 0
    for height in range(9, -1, -1):
        for point in levels[height]:
            peaks, count = ({point}, 1) if height == 9 else (set(), 0)
            if height != 9:
                for target in neighbors(rows, point):
                    if target in results and rows[target[1]][target[0]] == str(
                        height + 1
                    ):
                        reachable, paths = results[target]
                        peaks.update(reachable)
                        count += paths
            results[point] = frozenset(peaks), count
            processed += 1
            state = replace(state, current=point, height=height, processed=processed)
            yield state
    score = rating = 0
    for index, head in enumerate(levels[0], 1):
        peaks, count = results[head]
        # Traverse each reachable cell once, rather than enumerating routes.
        highlighted, pending = {head}, [head]
        while pending:
            point = pending.pop()
            height = int(rows[point[1]][point[0]])
            for target in neighbors(rows, point):
                if (
                    rows[target[1]][target[0]] == str(height + 1)
                    and target not in highlighted
                ):
                    highlighted.add(target)
                    pending.append(target)
        head_score = len(peaks)
        score += head_score
        rating += count
        state = replace(
            state,
            phase="trailhead",
            current=head,
            trailhead=head,
            highlighted=frozenset(highlighted),
            peaks=peaks,
            head_score=head_score,
            head_rating=count,
            heads_done=index,
            score=score,
            rating=rating,
        )
        yield state
    yield replace(state, phase="complete")


def draw(state, buffer):
    """Keep a boxed high-contrast cursor visible through counting and trail views."""
    label(
        buffer,
        0,
        2,
        "Pink [n]: cursor | cyan: neighbors/routes | green: reachable peaks",
        245,
    )
    rows = state.rows
    width, height = len(rows[0]), len(rows)
    # Reserve margins for row pointers, a column pointer and the detail footer.
    area_w = max(0, buffer.width() - 4)
    spacing = 2 if area_w >= 18 else 1
    area_h = max(0, buffer.height() - 6)
    visible_w = max(1, (area_w + spacing - 1) // spacing)
    visible_h = max(1, area_h)
    focus = state.current
    camera = (
        max(0, min(width - visible_w, focus[0] - visible_w // 2)),
        max(0, min(height - visible_h, focus[1] - visible_h // 2)),
    )
    view = GridViewport(
        buffer,
        width,
        height,
        spacing=(spacing, 1),
        camera=camera,
        region=(2, 4, area_w, area_h),
    )

    def glyph(char, x, y):
        point = x, y
        if char == ".":
            return ink(".", 235)
        if point in state.peaks:
            return ink(char, 46)
        if point in state.highlighted:
            return ink(char, 51)
        if state.phase == "height wave":
            adjacent = abs(x - focus[0]) + abs(y - focus[1]) == 1
            if adjacent and char == str(state.height + 1):
                return ink(char, 51)
            return ink(char, 245 if int(char) >= state.height else 238)
        return ink(char, 239)

    view.draw(rows, glyph)
    if state.processed:
        x, y = view.to_screen(*focus)
        if 2 <= x < 2 + area_w and 4 <= y < 4 + area_h:
            char = rows[focus[1]][focus[0]]
            buffer.put_char(x, y, f"\x1b[1;38;5;255;48;5;129m{char}\x1b[0m")
            if spacing > 1:
                buffer.put_char(x - 1, y, ink("[", 201))
                buffer.put_char(x + 1, y, ink("]", 201))
            buffer.put_char(x, 3, ink("v", 201))
            buffer.put_char(0, y, ink(">", 201))
            buffer.put_char(buffer.width() - 1, y, ink("<", 201))
    if state.phase == "height wave":
        detail = (
            f"Cursor {focus}, height {state.height}: "
            + (
                "summit (1 ending route)"
                if state.height == 9
                else f"combine adjacent {state.height + 1}s"
            )
            if state.processed
            else "Counting heights 9 -> 0, then highlighting each trailhead"
        )
    else:
        detail = (
            f"Trailhead {state.trailhead}: {state.head_score} distinct peaks / {state.head_rating} routes"
            if state.trailhead is not None
            else "No trailheads (0 cells) in this map"
        )
    if buffer.height() > 5:
        label(buffer, 0, buffer.height() - 2, detail, 51)


def describe(state):
    return (
        f"Cells: {state.processed} | Heads: {state.heads_done}/{state.heads_total} | "
        f"Score: {state.score} | Rating: {state.rating} | Part {state.part}: {state.answer}"
    )


def main(argv=None):
    parser = argument_parser(__doc__, __file__, "data", rate=12)
    args = parser.parse_args(argv)
    rows = load_input(parser, args, parse)
    return run_animation(
        snapshots(rows, args.part),
        draw,
        title=f"2024 Day 10 - Hoof It - Part {args.part}",
        describe=describe,
        **run_options(args),
    )


if __name__ == "__main__":
    main()
