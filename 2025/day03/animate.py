"""Day 3: greedy battery selection, with search windows and a gathering animation."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from dataclasses import dataclass, replace
from pathlib import Path

# Direct invocation and the repository CLI both use the shared root helper.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from animation_support import (  # noqa: E402
    argument_parser,
    ink,
    label,
    load_input,
    positive_integer,
    run_animation,
    run_options,
)

from bruhanimate import Buffer, GridViewport  # noqa: E402


@dataclass(frozen=True)
class Snapshot:
    bank: int = 0
    selected: tuple[int, ...] = ()
    candidate: int = 0
    start: int = 0
    end: int = 0
    total: int = 0
    phase: str = "entering"
    progress: float = 0
    recent: tuple[tuple[int, int], ...] = ()


def parse_banks(text: str) -> tuple[str, ...]:
    """Validate every bank; no random fallback or hidden 25-bank cutoff."""
    banks = tuple(line.strip() for line in text.strip().splitlines())
    if not banks or any(
        not bank or any(c not in "0123456789" for c in bank) for bank in banks
    ):
        raise ValueError("Each bank must be a nonempty line of ASCII digits")
    return banks


def choose(bank: str, count: int) -> tuple[int, ...]:
    """Return the lexicographically largest ordered subsequence's indices.

    Equal digits choose the earliest index, preserving room for later choices.
    """
    if not 1 <= count <= len(bank):
        raise ValueError("Selected battery count must be between 1 and the bank length")
    selected, start = [], 0
    for remaining in range(count, 0, -1):
        end = len(bank) - remaining + 1
        index = max(range(start, end), key=bank.__getitem__)
        selected.append(index)
        start = index + 1
    return tuple(selected)


def bank_states(banks: tuple[str, ...], count: int) -> Iterator[Snapshot]:
    """Yield immutable visual events lazily, retaining only five recent results."""
    if not banks or any(not 1 <= count <= len(bank) for bank in banks):
        raise ValueError("Every bank must contain at least the requested battery count")
    total, recent = 0, ()
    for number, bank in enumerate(banks):
        state = Snapshot(bank=number, total=total, recent=recent, end=len(bank))
        for tick in range(1, 9):
            yield replace(state, progress=tick / 8)
        selected, start = (), 0
        for remaining in range(count, 0, -1):
            end = len(bank) - remaining + 1
            candidate = max(range(start, end), key=bank.__getitem__)
            state = replace(
                state,
                selected=selected,
                candidate=candidate,
                start=start,
                end=end,
                phase="searching",
                progress=0,
            )
            yield state
            selected += (candidate,)
            state = replace(state, selected=selected, phase="selected")
            for tick in range(3):
                yield replace(state, progress=tick / 2)
            start = candidate + 1
        for phase, samples in (("discarding", 6), ("gathering", 8)):
            for tick in range(1, samples + 1):
                yield replace(state, phase=phase, progress=tick / samples)
        value = int("".join(bank[index] for index in selected))
        total += value
        recent = (*recent[-4:], (number + 1, value))
        state = replace(
            state, phase="bank complete", total=total, recent=recent, progress=1
        )
        yield state
    yield replace(state, phase="complete")


def draw_bank(banks: tuple[str, ...], state: Snapshot, buffer: Buffer):
    """Paint a following camera, eligible window, and falling/gathering digits."""
    bank = banks[state.bank]
    width, height = buffer.width(), buffer.height()
    if height < 7:
        buffer.put_at(
            0,
            max(0, height // 2),
            f"Selected: {''.join(bank[i] for i in state.selected)}",
        )
        return
    y = max(4, height // 2)
    columns = max(1, width // 2)
    camera = min(max(0, state.candidate - columns // 2), max(0, len(bank) - columns))
    viewport = GridViewport(
        buffer,
        len(bank),
        1,
        spacing=(2, 1),
        camera=(camera, 0),
        region=(0, y, width, 1),
    )
    selected = set(state.selected)
    progress = state.progress**2 * (3 - 2 * state.progress)
    gathering = state.phase in ("gathering", "bank complete", "complete")
    for index, digit in enumerate(bank):
        x, row = viewport.to_screen(index, 0)
        if state.phase == "entering":
            x -= round((1 - progress) * width)
        if state.phase == "discarding" and index not in selected:
            row += round(progress * (height - y))
        elif gathering:
            if index not in selected:
                continue
            target = (width - len(selected) * 2) // 2 + state.selected.index(index) * 2
            x = round(x + (target - x) * progress)
        if 0 <= x < width and 3 <= row < height - 1:
            color = (
                46
                if index in selected
                else 51
                if state.start <= index < state.end
                else 240
            )
            if state.phase == "searching" and index == state.candidate:
                color = 226
            buffer.put_char(x, row, ink(digit, color))
            if (
                state.phase in ("searching", "selected")
                and state.start <= index < state.end
                and y + 1 < height - 1
            ):
                buffer.put_char(
                    x, y + 1, ink("^" if index == state.candidate else "─", 51)
                )
    chosen = "".join(bank[index] for index in state.selected)
    buffer.put_at(
        0, 3, f"Bank {state.bank + 1}/{len(banks)} | window [{state.start}:{state.end})"
    )
    if y + 3 < height - 1:
        label(buffer, 0, y + 3, f"Chosen: {chosen or '-'}", 46)
    for row, (number, value) in enumerate(reversed(state.recent), y + 5):
        if row >= height - 1:
            break
        label(buffer, 0, row, f"Bank {number}: {value}", 240)


def run(banks, *, count=12, **options):
    if not banks or any(not 1 <= count <= len(bank) for bank in banks):
        raise ValueError("Every bank must contain at least the requested battery count")
    return run_animation(
        bank_states(banks, count),
        lambda state, buffer: draw_bank(banks, state, buffer),
        title=f"Day 3 | {count} batteries",
        describe=lambda state: f"Bank {state.bank + 1}/{len(banks)} | Picked {len(state.selected)}/{count} | Total: {state.total}",
        **options,
    )


def main(argv=None):
    parser = argument_parser(__doc__, __file__, "data", rate=30)
    parser.add_argument(
        "--digits", type=positive_integer, help="Override the part's battery count"
    )
    args = parser.parse_args(argv)
    banks = load_input(parser, args, parse_banks)
    count = args.digits if args.digits is not None else 2 if args.part == 1 else 12
    if any(len(bank) < count for bank in banks):
        parser.error("Every bank must contain at least the requested battery count")
    return run(banks, count=count, **run_options(args))


if __name__ == "__main__":
    main()
