"""Day 1 dial carousel using bruhanimate 1.x, with no import-time playback.

Space/p pauses, n/right advances one visual sample, +/- changes speed, q quits.
The original 0.2.x implementation is preserved in animate_legacy.py.
"""

from __future__ import annotations

import argparse
import math
import re
from collections.abc import Iterator
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path

from bruhcolor import bruhcolored

from bruhanimate import (
    Buffer,
    CallbackEffect,
    FireworkSettings,
    Layer,
    Playback,
    Scene,
    TwinkleSettings,
    effect_registry,
    play,
    text_to_image,
)

SAMPLE_RATE = 60
PALETTE = (196, 226, 46, 51, 201, 165, 129, 93)


@dataclass(frozen=True)
class Rotation:
    direction: str
    clicks: int


@dataclass(frozen=True)
class Snapshot:
    position: int = 50
    motion: float = 0
    instruction: int = 0
    direction: str = "R"
    remaining: int = 0
    stops: int = 0
    crossings: int = 0
    tick: int = 0
    flash_at: int = -SAMPLE_RATE
    phase: str = "ready"
    exit_progress: float = 0


def parse_rotations(text: str) -> tuple[Rotation, ...]:
    """Parse nonempty input containing L/R followed by unsigned ASCII digits."""
    lines = text.strip().splitlines()
    if not lines:
        raise ValueError("Input must contain at least one rotation")
    rotations = []
    for number, line in enumerate(lines, 1):
        if not re.fullmatch(r"[LR][0-9]+", line.strip()):
            raise ValueError(f"Line {number}: expected L or R followed by clicks")
        rotations.append(Rotation(line.strip()[0], int(line.strip()[1:])))
    return tuple(rotations)


def solve(rotations: tuple[Rotation, ...]) -> tuple[int, int, int]:
    """Return Part 1, Part 2 and final position in O(instructions) time.

    Part 1 counts instruction endpoints at zero (including a zero-click stop).
    Part 2 counts clicks arriving at zero; the initial position is never counted.
    """
    position, stops, crossings = 50, 0, 0
    for rotation in rotations:
        right = rotation.direction == "R"
        crossings += (
            (position + rotation.clicks) // 100
            if right
            else (rotation.clicks + (-position) % 100) // 100
        )
        position = (position + rotation.clicks * (1 if right else -1)) % 100
        stops += position == 0
    return stops, crossings, position


def dial_states(rotations: tuple[Rotation, ...], part: int = 2) -> Iterator[Snapshot]:
    """Yield bounded immutable visual samples lazily, at a nominal 60 samples/s.

    Clicks ease between neighboring numbers over 2-12 samples. Longer turns
    accelerate, then slow near zero and at the ends. Drawing never advances time.
    Instruction pauses last 0.2 s; the finite exit lasts 1 s at normal speed.
    Storage stays constant with respect to total clicks; no trace is materialized.
    """
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    state = Snapshot()
    yield state
    for number, rotation in enumerate(rotations, 1):
        direction = 1 if rotation.direction == "R" else -1
        state = replace(
            state,
            instruction=number,
            direction=rotation.direction,
            remaining=rotation.clicks,
            phase="turning",
        )
        for click in range(rotation.clicks):
            target = (state.position + direction) % 100
            ramp = min(click, rotation.clicks - click - 1, 3) / 3
            samples = max(2, round(12 - 10 * ramp))
            if min(target, 100 - target) < 5:
                samples = max(samples, 12 - 2 * min(target, 100 - target))
            origin = state.position
            for sample in range(1, samples + 1):
                tick = state.tick + 1
                arrived = sample == samples
                hit = arrived and target == 0
                stop = hit and click == rotation.clicks - 1
                progress = sample / samples
                eased = progress * progress * (3 - 2 * progress)
                state = replace(
                    state,
                    position=target if arrived else origin,
                    motion=0 if arrived else direction * eased,
                    remaining=rotation.clicks - click - int(arrived),
                    stops=state.stops + stop,
                    crossings=state.crossings + hit,
                    tick=tick,
                    flash_at=tick if (stop if part == 1 else hit) else state.flash_at,
                )
                yield state
        if rotation.clicks == 0:
            stop = state.position == 0
            state = replace(
                state,
                stops=state.stops + stop,
                flash_at=state.tick if part == 1 and stop else state.flash_at,
            )
        for _ in range(round(0.2 * SAMPLE_RATE)):
            state = replace(state, tick=state.tick + 1, phase="pause")
            yield state
    for sample in range(1, SAMPLE_RATE + 1):
        state = replace(
            state,
            tick=state.tick + 1,
            exit_progress=sample / SAMPLE_RATE,
            phase="complete" if sample == SAMPLE_RATE else "finishing",
        )
        yield state


@lru_cache(maxsize=128)
def art(text: str) -> tuple[str, ...]:
    """Cache immutable doom-font rows, bounded even as counters grow."""
    return tuple(text_to_image(text, font="doom"))


def stamp(buffer: Buffer, rows: tuple[str, ...], x: int, y: int, color=None):
    """Clip transparent ASCII art without painting over background spaces."""
    for dy, row in enumerate(rows):
        if not 0 <= y + dy < buffer.height():
            continue
        for dx, char in enumerate(row):
            if char != " " and 0 <= x + dx < buffer.width():
                value = bruhcolored(char, color=color).colored if color else char
                buffer.put_char(x + dx, y + dy, value)


def guide(buffer: Buffer, x: int, y: int):
    """Draw a clipped radial guide from the bottom center to a dial number."""
    origin_x, origin_y = buffer.width() // 2, buffer.height() - 2
    length = max(abs(x - origin_x), abs(y - origin_y), 1)
    char = "│" if abs(x - origin_x) < abs(y - origin_y) else "─"
    for step in range(length + 1):
        px = round(origin_x + (x - origin_x) * step / length)
        py = round(origin_y + (y - origin_y) * step / length)
        if 0 <= px < buffer.width() and 0 <= py < buffer.height():
            buffer.put_char(px, py, bruhcolored(char, color=240).colored)


def draw_dial(state: Snapshot, buffer: Buffer, *, part=2, show_lines=False):
    """Render a snapshot; compact terminals use a readable single-line dial."""
    width, height = buffer.width(), buffer.height()
    center_x, center_y = width // 2, height // 2
    count = state.stops if part == 1 else state.crossings
    flash_age = state.tick - state.flash_at
    color = PALETTE[(flash_age // 4) % len(PALETTE)] if flash_age < 60 else 51
    if width < 45 or height < 20:
        buffer.put_at(0, center_y, f"Dial: {state.position:02d}  Zeros: {count}")
        return
    exit_ease = state.exit_progress**2 * (3 - 2 * state.exit_progress)
    exit_offset = exit_ease * 22 * (-1 if state.position < 50 else 1)
    if state.exit_progress < 1:
        placements = []
        for offset in range(-10, 11):
            visual_offset = offset - state.motion + exit_offset
            rows = art(str((state.position + offset) % 100))
            x = round(center_x + visual_offset * 15 - len(rows[0]) / 2)
            y = round(center_y - len(rows) / 2 + (abs(visual_offset) / 3.9) ** 3 * 17)
            if x + len(rows[0]) <= 0 or x >= width or y >= height:
                continue
            placements.append(
                (rows, x, y, 129 if (state.position + offset) % 100 == 0 else None)
            )
        if show_lines:
            for rows, x, y, _ in placements:
                guide(buffer, x + len(rows[0]) // 2, y + len(rows))
        for rows, x, y, number_color in placements:
            stamp(buffer, rows, x, y, number_color)
    if state.phase not in ("finishing", "complete"):
        rows = art(f"{state.direction} {state.remaining}")
        stamp(buffer, rows, (width - len(rows[0])) // 2, 2)
    rows = art(str(count))
    bottom = height - len(rows) - 2
    target = (height - len(rows)) // 2
    stamp(
        buffer,
        rows,
        (width - len(rows[0])) // 2,
        round(bottom + (target - bottom) * exit_ease),
        color,
    )


def run(
    rotations,
    *,
    part=2,
    speed=1.0,
    fps=60,
    frames=None,
    background=True,
    show_lines=False,
    on_complete="hold",
):
    """Compose independent background layers and a lazy dial Playback."""
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    totals = solve(rotations)
    if not math.isfinite(speed) or not 0 < speed <= 4:
        raise ValueError("speed must be greater than 0 and at most 4")
    playback = Playback(
        dial_states(rotations, part),
        lambda state, buffer: draw_dial(
            state, buffer, part=part, show_lines=show_lines
        ),
        steps_per_second=SAMPLE_RATE * speed,
    )

    def status(buffer):
        state = playback.state
        phase = (
            "Paused" if playback.paused else state.phase.title() if state else "Ready"
        )
        buffer.put_at(
            0, 0, f"Day 1 | Part {part} | {phase} | Answer: {totals[part - 1]}"
        )
        buffer.put_at(
            0, buffer.height() - 1, "Space pause | n/right sample | +/- speed | q quit"
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
        updates_per_second=SAMPLE_RATE,
        frames=frames,
        on_complete=on_complete,
        event_handler=playback.handle_event,
    )


def positive_number(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Value must be positive and finite")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path(__file__).resolve().with_name("data1")
    )
    parser.add_argument("--part", type=int, choices=(1, 2), default=2)
    parser.add_argument("--speed", type=positive_number, default=1)
    parser.add_argument("--fps", type=positive_number, default=60)
    parser.add_argument("--frames", type=int)
    parser.add_argument("--no-background", action="store_true")
    parser.add_argument("--show-lines", action="store_true")
    parser.add_argument("--exit-on-complete", action="store_true")
    args = parser.parse_args(argv)
    if args.frames is not None and args.frames < 0:
        parser.error("--frames must not be negative")
    if args.speed > 4:
        parser.error("--speed must be at most 4")
    try:
        rotations = parse_rotations(args.input.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return run(
        rotations,
        part=args.part,
        speed=args.speed,
        fps=args.fps,
        frames=args.frames,
        background=not args.no_background,
        show_lines=args.show_lines,
        on_complete="exit" if args.exit_on_complete else "hold",
    )


if __name__ == "__main__":
    main()
