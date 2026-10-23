# Day 7 animation: bruhanimate 1.x

The project now requires `bruhanimate>=1.0.0,<2.0.0`, with 1.0.0 selected in
poetry.lock. Poetry remains the project's environment/dependency manager.

## Run it

From the AdventOfCodeSolutions root, install the locked dependencies:

```powershell
poetry install
poetry run python 2025/day07/animate.py
# The existing CLI also works:
poetry run python cli.py animate --year 2025 --day 7
```

The default input is `datasmall` beside animate.py, independently of your working
directory. An explicitly supplied relative --input path is relative to your
working directory. Missing or malformed input produces an error rather than a
silent fallback.

```powershell
# Aggregate all beams by row on the full input:
poetry run python 2025/day07/animate.py --mode rows --input 2025/day07/data
# A slower sample of at most 20 individual timelines:
poetry run python 2025/day07/animate.py --max-branches 20 --steps-per-second 20
# Close after finishing, without fireworks/twinkles in the background:
poetry run python 2025/day07/animate.py --no-background --exit-on-complete
```

Space/p pauses, n/right arrow steps, +/- changes speed, and q/Escape/Ctrl+C quits.
The final state stays visible by default. --fps changes presentation speed;
--steps-per-second controls snapshot consumption. --spacing controls horizontal
board spacing, and --frames limits presentations. Oversized boards follow the
active beam automatically, and all drawing clips to the available terminal.

Branch mode samples at most 100 routes by default, in depth-first order. The
displayed splitter/timeline totals are computed for the **entire board** using
dynamic programming, independently of that sample. Row mode displays the complete
aggregate beam graph without enumerating timelines. Large quantum traces are not
precomputed or cached.

## What changed

| Before | Now |
| --- | --- |
| EffectRenderer and a custom render_frame loop | play owns timing, input, presentation, and cleanup |
| One large mutable effect | Pure counting/trace generators, immutable Snapshot values, and drawing |
| Precompute every route with a growing queue | Lazy depth-first routes with an explicit sample limit |
| Manually combine a second effect and fireworks/twinkles | Scene with independent Twinkle, transparent Firework, Playback, and status layers |
| Repeated coordinate/centering calculations | GridViewport with spacing, clipping, and follow-camera placement |
| Mutable erase/connector/history sets in the raster | Recompose the current snapshot with connection glyphs |
| Start the animation when importing it | Explicit main(), invoked by the CLI after importing |

The animation implementation is about 40% shorter than the original 750-line file,
while adding controls, validation, lazy playback, a CLI, and tests. The visual
design keeps colored splitters, cyan beams, completed green paths, pulses,
ripples, and the fireworks/twinkle background. Branch order and timing are now
controlled by the new playback model rather than reproducing every old frame.

## Original and other days

`animate_legacy.py` is an unchanged copy of the original for comparison. It and
the other unmigrated animations still require bruhanimate 0.2.x; upgrading the
shared project dependency does not migrate their removed renderer APIs.

To run the original in a separate temporary environment using uv, change into
2025/day07 first so its original relative input paths work:

```powershell
cd 2025/day07
uv run --no-project --python 3.13 --with "bruhanimate>=0.2.96,<0.3" python animate_legacy.py
```

For other legacy demos, use the same isolated 0.2.x environment from the day's
directory, or migrate them individually. Do not downgrade the new shared
dependency to run Day 7's migrated implementation.

## Checks and remaining helpers

```powershell
poetry check --lock
poetry run python -m unittest discover -s 2025/day07 -p test_animate.py -v
```

The tests use synthetic boards, a fake clock, and a headless Screen. They never
read puzzle input, session cookies, or open a real terminal. Headless tests verify
the player/lifecycle integration; try the animation in your terminal to assess
its appearance and speed.

Puzzle-specific logic remains here: splitter rules, route sampling, pulse/ripple
styling, connection-glyph selection, and camera-follow policy. Potential reusable
helpers are connected grid lines that fill spacing gaps, timed transient overlays,
and follow-camera positioning. General independent update rates per layer remain
absent; the scene currently updates at 60 ticks per second. These are candidates
for the animation library after another visualization demonstrates the same need.
