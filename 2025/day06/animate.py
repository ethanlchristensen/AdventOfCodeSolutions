"""Day 6: a scrolling worksheet scanner with exact horizontal/vertical equations."""

from __future__ import annotations

import math
import re
import sys
from collections.abc import Iterator
from dataclasses import dataclass, replace
from pathlib import Path
from textwrap import wrap

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from animation_support import (  # noqa: E402
    argument_parser,
    ink,
    label,
    load_input,
    run_animation,
    run_options,
)

from bruhanimate import Buffer, GridViewport  # noqa: E402


@dataclass(frozen=True)
class Problem:
    start: int
    end: int
    operation: str
    horizontal: tuple[int, ...]
    vertical: tuple[int, ...]
    columns: tuple[int, ...]


@dataclass(frozen=True)
class Worksheet:
    rows: tuple[str, ...]
    operations: str
    problems: tuple[Problem, ...]


@dataclass(frozen=True)
class Snapshot:
    problem: int = 0
    cursor: tuple[int, int] = (0, 0)
    numbers: tuple[int, ...] = ()
    result: int = 0
    total: int = 0
    completed: frozenset[int] = frozenset()
    phase: str = "scanning"


def parse_worksheet(text: str) -> Worksheet:
    """Preserve fixed-width columns, pad ragged right edges, validate blocks.

    Blank separator columns delimit problems. Each block has one +/* operator
    and one unsigned integer per numeric row. Trailing blank lines are harmless.
    Vertical operands read digits top to bottom, columns right to left.
    """
    lines = text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) < 2:
        raise ValueError("Expected numeric rows and a final +/* operator row")
    if any(not re.fullmatch(r"[0-9 ]+", row) for row in lines[:-1]):
        raise ValueError(
            "Numeric worksheet rows may contain only ASCII digits and spaces"
        )
    if not re.fullmatch(r"[+* ]+", lines[-1]):
        raise ValueError("The final worksheet row must contain only +, *, and spaces")
    width = max(map(len, lines))
    rows = tuple(row.ljust(width) for row in lines[:-1])
    operations = lines[-1].ljust(width)
    occupied = [any(row[x] != " " for row in (*rows, operations)) for x in range(width)]
    problems, x = [], 0
    while x < width:
        if not occupied[x]:
            x += 1
            continue
        start = x
        while x < width and occupied[x]:
            x += 1
        end = x
        operation = operations[start:end].strip()
        if operation not in ("+", "*"):
            raise ValueError("Each problem block must contain exactly one + or *")
        tokens = tuple(row[start:end].strip() for row in rows)
        if any(not re.fullmatch(r"[0-9]+", token) for token in tokens):
            raise ValueError("Each problem needs exactly one integer per numeric row")
        columns = tuple(
            column
            for column in range(end - 1, start - 1, -1)
            if any(row[column] != " " for row in rows)
        )
        vertical = tuple(
            int("".join(row[column] for row in rows if row[column] != " "))
            for column in columns
        )
        problems.append(
            Problem(start, end, operation, tuple(map(int, tokens)), vertical, columns)
        )
    if not problems:
        raise ValueError("Worksheet contains no problems")
    return Worksheet(rows, operations, tuple(problems))


def calculate(numbers: tuple[int, ...], operation: str) -> int:
    """Keep repeated operands and zero results; never deduplicate numbers."""
    if operation == "+":
        return sum(numbers)
    if operation == "*":
        return math.prod(numbers)
    raise ValueError("Operation must be + or *")


def worksheet_states(worksheet: Worksheet, part=2) -> Iterator[Snapshot]:
    """Scan one operand per event, show its equation, then commit each result once."""
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    state = Snapshot()
    order = (
        range(len(worksheet.problems))
        if part == 1
        else reversed(range(len(worksheet.problems)))
    )
    for number in order:
        problem = worksheet.problems[number]
        state = replace(state, problem=number, numbers=(), result=0, phase="scanning")
        operands = problem.horizontal if part == 1 else problem.vertical
        for index, operand in enumerate(operands):
            cursor = (
                (problem.start, index) if part == 1 else (problem.columns[index], 0)
            )
            state = replace(state, cursor=cursor, numbers=(*state.numbers, operand))
            yield state
        result = calculate(operands, problem.operation)
        state = replace(state, result=result, phase="calculating")
        for _ in range(4):
            yield state
        state = replace(
            state,
            total=state.total + result,
            completed=state.completed | {number},
            phase="added",
        )
        for _ in range(3):
            yield state
    yield replace(state, phase="complete")


def draw_worksheet(worksheet: Worksheet, state: Snapshot, buffer: Buffer, *, part=2):
    """Pan to the active operand; keep its equation and the grand total below it."""
    width, height = buffer.width(), buffer.height()
    problem = worksheet.problems[state.problem]
    if height < 10:
        buffer.put_at(
            0, height // 2, f"Problem {state.problem + 1} | Total: {state.total}"
        )
        return
    rows = (*worksheet.rows, worksheet.operations)
    region_height = max(1, height // 2 - 3)
    cursor_x, cursor_y = state.cursor
    camera = (
        min(max(0, cursor_x - width // 2), max(0, len(rows[0]) - width)),
        min(max(0, cursor_y - region_height // 2), max(0, len(rows) - region_height)),
    )
    viewport = GridViewport.from_rows(
        buffer, rows, camera=camera, region=(0, 3, width, region_height)
    )

    def glyph(char, x, y):
        if not problem.start <= x < problem.end:
            return ink(char, 240)
        scanner = y == cursor_y if part == 1 else x == cursor_x
        return ink(char, 226 if scanner else 51)

    viewport.draw(rows, glyph)
    for y in range(len(rows)):
        if part == 2:
            viewport.put(cursor_x, y, ink(rows[y][cursor_x], 226))
    equation = f" {problem.operation} ".join(map(str, state.numbers))
    if state.phase != "scanning":
        equation += f" = {state.result}"
    line = height // 2 + 1
    label(
        buffer,
        0,
        line,
        f"Problem {state.problem + 1}/{len(worksheet.problems)} | {'Rows top to bottom' if part == 1 else 'Columns right to left'}",
        51,
    )
    available = max(1, height - line - 4)
    pieces = wrap(
        equation, width=max(1, width), break_long_words=True, break_on_hyphens=False
    )
    for offset, piece in enumerate(pieces[-available:]):
        label(
            buffer,
            0,
            line + 1 + offset,
            piece,
            46 if state.phase in ("added", "complete") else 226,
        )
    label(buffer, 0, height - 2, f"Grand total: {state.total}", 201)


def run(worksheet, *, part=2, **options):
    return run_animation(
        worksheet_states(worksheet, part),
        lambda state, buffer: draw_worksheet(worksheet, state, buffer, part=part),
        title=f"Day 6 | Part {part}",
        describe=lambda state: f"Solved {len(state.completed)}/{len(worksheet.problems)} | Total: {state.total}",
        **options,
    )


def main(argv=None):
    parser = argument_parser(__doc__, __file__, "dataanimate", rate=12)
    args = parser.parse_args(argv)
    worksheet = load_input(parser, args, parse_worksheet)
    return run(worksheet, part=args.part, **run_options(args))


if __name__ == "__main__":
    main()
