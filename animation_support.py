"""Small shared bruhanimate 1.x runner for Advent of Code visualizations.

Puzzle rules stay in each day's animate.py. This module composes owned layers,
reserves header/footer rows, and supplies consistent command-line options.
"""

import argparse
import math
from functools import lru_cache
from pathlib import Path

from bruhanimate import (
    Buffer,
    CallbackEffect,
    Playback,
    Scene,
    TwinkleSettings,
    effect_registry,
    play,
)
from bruhcolor import bruhcolored


@lru_cache(maxsize=512)
def ink(text, color):
    """Style one cell; Buffer.put_at must never split a colored ANSI string."""
    if len(str(text)) != 1:
        raise ValueError("ink expects one character; use label for styled text")
    return bruhcolored(str(text), color=color).colored


def label(buffer, x, y, text, color):
    """Paint clipped text as individually styled cells, preserving ANSI escapes."""
    if not 0 <= y < buffer.height():
        return
    for offset, char in enumerate(str(text)):
        if 0 <= x + offset < buffer.width():
            buffer.put_char(x + offset, y, ink(char, color))


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


def argument_parser(
    description, filename, default_input="data", *, rate=20, part=2, background=True
):
    """Return shared options; defaults are anchored beside the caller's script."""
    if part not in (1, 2):
        raise ValueError("part must be 1 or 2")
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--input", type=Path, default=Path(filename).resolve().with_name(default_input)
    )
    parser.add_argument("--part", type=int, choices=(1, 2), default=part)
    parser.add_argument("--steps-per-second", type=positive_number, default=rate)
    parser.add_argument("--fps", type=positive_number, default=60)
    parser.add_argument("--frames", type=int)
    parser.add_argument("--no-background", action="store_true", default=not background)
    parser.add_argument("--exit-on-complete", action="store_true")
    return parser


def load_input(parser, args, parse):
    """Validate options and parse input before opening a terminal."""
    if args.frames is not None and args.frames < 0:
        parser.error("--frames must not be negative")
    try:
        return parse(args.input.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))


def run_animation(
    states,
    draw,
    *,
    title,
    describe=None,
    steps_per_second=20,
    fps=60,
    frames=None,
    background=True,
    on_complete="hold",
):
    """Play one lazy snapshot source; hold its final frame or exit on exhaustion.

    Source steps are algorithm/transition events, independent of presentation
    FPS. Playback owns its iterator; the Scene owns every layer. Each day's
    draw(state, buffer) paints only from its immutable current snapshot. describe
    is optional; arbitrary state types use an event counter and Playing phase.
    """
    playback = Playback(states, draw, steps_per_second=steps_per_second)

    def status(buffer):
        state = playback.state
        phase = (
            "Complete"
            if playback.finished
            else "Paused"
            if playback.paused
            else str(getattr(state, "phase", "playing")).title()
            if playback.has_state
            else "Ready"
        )
        label(buffer, 0, 0, f"{title} | {phase}", 226 if playback.finished else 51)
        if buffer.height() > 2:
            detail = (
                (
                    describe(state)
                    if describe is not None
                    else f"Events: {playback.steps}"
                )
                if playback.has_state
                else "Starting..."
            )
            buffer.put_at(0, 1, detail)
        buffer.put_at(
            0,
            buffer.height() - 1,
            f"Space pause | n/right step | +/- speed ({playback.steps_per_second:g}/s) | q quit",
        )

    def build(buffer):
        layers = []
        if background:
            layers.append(
                effect_registry.create(
                    "twinkle",
                    Buffer(buffer.height(), buffer.width()),
                    " ",
                    settings=TwinkleSettings(density=0.025),
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


def run_options(args):
    """Translate the common argparse options to the runner's keyword arguments."""
    return dict(
        steps_per_second=args.steps_per_second,
        fps=args.fps,
        frames=args.frames,
        background=not args.no_background,
        on_complete="exit" if args.exit_on_complete else "hold",
    )
