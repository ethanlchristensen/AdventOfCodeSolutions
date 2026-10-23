# Day 1 animation: bruhanimate 1.x

The shared project already locks bruhanimate 1.0.0 following the Day 7 migration.
Day 1 now uses the same native player, scene composition, and playback controls.
`animate_legacy.py` preserves the original byte for byte for comparison.

## Run it

From the AdventOfCodeSolutions root:

```powershell
poetry install
poetry run python cli.py animate --year 2025 --day 1
# Direct invocation exposes additional options:
poetry run python 2025/day01/animate.py --part 2
poetry run python 2025/day01/animate.py --part 1 --input 2025/day01/data
poetry run python 2025/day01/animate.py --speed 2 --no-background --exit-on-complete
```

The default remains Part 2 with `data1`, now resolved beside the script regardless
of the current directory. Explicit relative input paths use the current directory.
Missing or malformed input fails with an error; it does not silently use sample
commands. Importing the module neither reads inputs nor opens the terminal.

Space/p pauses, n/right advances one **visual sample**, +/- changes speed, and
q/Escape/Ctrl+C quits. The final answer stays visible by default;
`--exit-on-complete` closes after the exit animation. `--frames` caps displayed
frames, `--fps` controls presentation, `--show-lines` enables radial guides, and
`--no-background` disables twinkles/fireworks. Speed is a positive multiplier up
to 4; the normal timeline has 60 visual samples per second. Interactive +/- uses
the shared Playback limits (0.25-240 samples per second).

## Before and after

| Before | Now |
| --- | --- |
| 594-line mutable effect with render_frame | About 350 lines separating parsing, counting, lazy snapshots, drawing and composition |
| Custom transition timers and render-frame gates | Immutable visual samples consumed by Playback; Player owns timing and controls |
| Manually sync second effects into the dial buffer | Independent Scene layers for twinkles, transparent fireworks, dial and status |
| Prebuild all 100 number images; regenerate counter art each frame | Lazy, bounded cache of immutable font rows |
| Increment zeros before the dial reaches zero | Count at arrival; Part 1 counts instruction endpoints and Part 2 counts each zero arrival |
| Unused part setting and perpetual completion movement | Selectable parts and a finite exit, with configurable hold or close |
| Import triggers playback under the CLI module name | Explicit main(), using the CLI integration introduced for Day 7 |

The curved doom-font carousel, purple zero, easing, acceleration/deceleration,
rainbow counter flash, centered final counter and background effects remain.
Timing is reworked rather than reproducing old frames exactly. The old dot-based
motion blur is omitted. Small terminals use a compact text dial; larger ones
show the carousel with clipped drawing.

Totals are calculated analytically in O(instructions) time, including full turns,
zero-length rotations and rotations beginning at zero. The animation visits
each click lazily, so memory does not grow with the number of clicks. Very long
instructions can still take a long time to watch; this version does not skip
turns or offer seeking.

## Checks and helpers still worth considering

```powershell
poetry run python -m unittest discover -s 2025/day01 -p test_animate.py -v
poetry run python -m unittest discover -s 2025/day07 -p test_animate.py -v
```

Tests use synthetic rotations and a fake clock/Screen. They verify the counting
against an independent click-by-click oracle, lazy snapshots, pure drawing,
clipping, playback controls, completion with endless backgrounds, presentation
rate independence, import safety, options and the actual AoC CLI entrypoint.
They never read private inputs or credentials. Appearance still needs a real
terminal check.

Potential library helpers surfaced here are a composable timed keyframe/tween
sequence, cached transparent text-art placement, and stepping by semantic events
(a dial click or instruction) rather than an individual visual sample. Those
would shorten the custom timeline/drawing further. Dial wrapping, zero-counting,
carousel geometry and easing policy remain puzzle-specific. No library changes
were needed for this migration.

The original still requires a separate 0.2.x environment. To compare visually:

```powershell
cd 2025/day01
uv run --no-project --python 3.13 --with "bruhanimate>=0.2.96,<0.3" python animate_legacy.py
```

Keep the shared project's 1.x dependency for migrated animations. The original's
unused part setting means it only demonstrates the old zero-crossing behavior.
