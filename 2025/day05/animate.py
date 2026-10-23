"""Day 5: inclusive interval merging and ingredient freshness on a number line."""

from __future__ import annotations

import re
import sys
from bisect import bisect_right
from collections.abc import Iterator
from dataclasses import dataclass, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from animation_support import (  # noqa: E402
    argument_parser,
    ink,
    label,
    load_input,
    run_animation,
    run_options,
)

from bruhanimate import Buffer  # noqa: E402

Interval = tuple[int, int]


@dataclass(frozen=True)
class Inventory:
    ranges: tuple[Interval, ...]
    ingredients: tuple[int, ...]


@dataclass(frozen=True)
class Snapshot:
    merged: tuple[Interval, ...] = ()
    active: Interval | None = None
    processed: int = 0
    ingredient: int | None = None
    checked: int = 0
    fresh: bool | None = None
    count: int = 0
    coverage: int = 0
    phase: str = "merging"


def parse_inventory(text: str) -> Inventory:
    """Parse inclusive, nonnegative ranges and IDs separated by a blank line."""
    lines = text.splitlines()
    separator = next((i for i, line in enumerate(lines) if not line.strip()), None)
    if separator is None or separator == 0:
        raise ValueError("Expected fresh ranges, a blank line, then ingredient IDs")
    ranges, ingredients = [], []
    for line in lines[:separator]:
        if not re.fullmatch(r"[0-9]+-[0-9]+", line.strip()):
            raise ValueError("Ranges must use nonnegative start-end integers")
        start, end = map(int, line.strip().split("-"))
        if start > end:
            raise ValueError("Range start must not exceed its end")
        ranges.append((start, end))
    for line in lines[separator + 1 :]:
        if not line.strip():
            continue
        if not re.fullmatch(r"[0-9]+", line.strip()):
            raise ValueError("Ingredient IDs must be nonnegative integers")
        ingredients.append(int(line.strip()))
    return Inventory(tuple(ranges), tuple(ingredients))


def merge_ranges(ranges: tuple[Interval, ...]) -> tuple[Interval, ...]:
    """Merge overlapping/adjacent inclusive intervals without expanding IDs."""
    merged = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return tuple(merged)


def inventory_states(inventory: Inventory, part=2) -> Iterator[Snapshot]:
    """Yield merge decisions and optional binary-search membership checks."""
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    state = Snapshot()
    yield state
    for number, interval in enumerate(sorted(inventory.ranges), 1):
        yield replace(state, active=interval, processed=number, phase="comparing")
        # Input is sorted, so only the final merged interval can overlap.
        merged = list(state.merged)
        start, end = interval
        if merged and start <= merged[-1][1] + 1:
            old_start, old_end = merged[-1]
            merged[-1] = (old_start, max(old_end, end))
            coverage = state.coverage + max(0, end - old_end)
        else:
            merged.append(interval)
            coverage = state.coverage + end - start + 1
        state = replace(
            state,
            merged=tuple(merged),
            active=interval,
            processed=number,
            coverage=coverage,
            phase="merged",
        )
        yield state
    starts = tuple(start for start, _ in state.merged)
    if part == 1:
        for checked, ingredient in enumerate(inventory.ingredients, 1):
            index = bisect_right(starts, ingredient) - 1
            fresh = index >= 0 and ingredient <= state.merged[index][1]
            state = replace(
                state,
                ingredient=ingredient,
                fresh=fresh,
                checked=checked,
                count=state.count + fresh,
                active=None,
                phase="checking",
            )
            yield state
    yield replace(state, phase="complete", active=None)


def draw_inventory(inventory: Inventory, state: Snapshot, buffer: Buffer):
    """Use exact integer projection; show precise bounds beside the scaled chart."""
    width, height = buffer.width(), buffer.height()
    if width < 12 or height < 10:
        buffer.put_at(
            0, height // 2, f"Fresh IDs: {state.count} | Coverage: {state.coverage}"
        )
        return
    endpoints = tuple(value for interval in inventory.ranges for value in interval)
    low = min((*endpoints, *inventory.ingredients))
    high = max((*endpoints, *inventory.ingredients))
    left, span = 2, max(1, width - 5)

    def project(value):
        return left + (value - low) * span // max(1, high - low)

    def band(interval, row, color):
        start, end = map(project, interval)
        for x in range(start, end + 1):
            buffer.put_char(x, row, ink("█", color))

    y = max(5, height // 2)
    buffer.put_at(0, 3, "Sorted incoming ranges -> disjoint fresh intervals")
    buffer.put_at(0, y - 2, f"Incoming: {state.active if state.active else '-'}")
    if state.active:
        band(state.active, y - 1, 226)
    buffer.put_at(left, y, "─" * (span + 1))
    for interval in state.merged:
        band(interval, y, 46)
    buffer.put_at(left, y + 1, str(low))
    buffer.put_at(max(left, width - len(str(high)) - 1), y + 1, str(high))
    if state.ingredient is not None:
        buffer.put_char(
            project(state.ingredient), y - 1, ink("▼", 46 if state.fresh else 196)
        )
        label(
            buffer,
            0,
            y + 2,
            f"ID {state.ingredient}: {'FRESH' if state.fresh else 'SPOILED'}",
            46 if state.fresh else 196,
        )
    for row, interval in enumerate(state.merged[-3:], y + 3):
        if row >= height - 1:
            break
        buffer.put_at(
            0,
            row,
            f"[{interval[0]}, {interval[1]}] = {interval[1] - interval[0] + 1} IDs",
        )


def run(inventory, *, part=2, **options):
    return run_animation(
        inventory_states(inventory, part),
        lambda state, buffer: draw_inventory(inventory, state, buffer),
        title=f"Day 5 | Part {part}",
        describe=lambda state: f"Ranges {state.processed}/{len(inventory.ranges)} | Checked {state.checked}/{len(inventory.ingredients)} | {'Fresh ingredients: ' + str(state.count) if part == 1 else 'Fresh ID coverage: ' + str(state.coverage)}",
        **options,
    )


def main(argv=None):
    parser = argument_parser(__doc__, __file__, "data", rate=8)
    args = parser.parse_args(argv)
    inventory = load_input(parser, args, parse_inventory)
    return run(inventory, part=args.part, **run_options(args))


if __name__ == "__main__":
    main()
