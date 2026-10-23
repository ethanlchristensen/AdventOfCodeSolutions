# Advent of Code animations with bruhanimate 1.x

Days 1, 3, 4, 5, 6 and 7 of 2025 use the published bruhanimate 1.0.0 package.
The standalone 2024 animations (Days 6, 10, 15, 18 and 23) use the same API;
see the [2024 migration guide](ANIMATIONS_2024_V1.md) for their options and changes.
The project's existing Poetry dependency and lockfile already select 1.0.0;
these additional migrations do not require another package release.

## Run the animations

From the AdventOfCodeSolutions root:

```powershell
poetry install
poetry run python cli.py animate --year 2025 --day 3
poetry run python cli.py animate --year 2025 --day 4
poetry run python cli.py animate --year 2025 --day 5
poetry run python cli.py animate --year 2025 --day 6
```

Direct invocation exposes part selection and visualization options:

```powershell
# Day 3: two batteries for Part 1, twelve for Part 2 (the default).
poetry run python 2025/day03/animate.py --part 1
poetry run python 2025/day03/animate.py --digits 6 --steps-per-second 15
# Day 4: optional per-roll inspections, using the complete board.
poetry run python 2025/day04/animate.py --detail --input 2025/day04/data
# Day 5: check available ingredients, or merge the complete fresh-ID coverage.
poetry run python 2025/day05/animate.py --part 1
poetry run python 2025/day05/animate.py --part 2
# Day 6: compare horizontal and vertical arithmetic on the same worksheet.
poetry run python 2025/day06/animate.py --part 1
poetry run python 2025/day06/animate.py --part 2 --no-background --exit-on-complete
```

Defaults preserve the input file selected by each original: `data` for Days 3
and 5, `datasmall` for Day 4, and `dataanimate` for Day 6. Default paths are
resolved beside animate.py, regardless of the current working directory.
Explicit relative `--input` paths resolve from the current directory. Missing
or malformed files produce an error before opening the terminal.

All four default to Part 2. Space/p pauses, n/right advances one visual event,
+/- changes speed, and q/Escape/Ctrl+C quits. Some events are transition samples
or short holds, so stepping does not always advance an entire algorithm decision.
The final result stays visible unless `--exit-on-complete` is supplied.

`--steps-per-second` controls event consumption; `--fps` controls presentation
(60 by default). A fixed 60-Hz simulation keeps algorithm timing independent of
presentation FPS. Playback bounds catch-up work during stalls, so unusually high
event rates or slow terminals can take longer than the nominal rate suggests.
`--frames` caps presentations; `--no-background` removes the quiet twinkle field.
The old nested fireworks are replaced with this quieter background.

## What changed visually and logically

| Day | Visualization | Correctness and usability |
| --- | --- | --- |
| 3 | Search-window highlights, chosen digits, falling rejects, gathering digits, recent-bank totals and a following camera | Processes every bank; validates digit count; earliest equal maxima preserve later choices |
| 4 | Green removable rolls, neighbor inspections, staged removal sparks, following camera and whole-board column-density strip | Uses the full board; eligibility is frozen per wave; Part 1 counts one wave, Part 2 repeats until stable |
| 5 | New number-line animation showing incoming/merged intervals and green/red ingredient checks | Replaces the snow-only placeholder; inclusive ranges, adjacency, duplicates and huge IDs are handled exactly without expanding ranges |
| 6 | Scrolling worksheet, highlighted row/column scanner, growing equations and running total | Preserves whitespace and repeated operands, includes zero results, reads Part 2 right to left, pads ragged right edges, and tolerates trailing blank lines |

Large inputs are followed and clipped rather than changing the puzzle's data.
Very short terminals use compact summaries. Day 4's density strip summarizes
columns across the full board, including parts outside the current viewport.
Day 5's number line is a scaled overview: multiple distinct IDs may share a cell;
the displayed numeric bounds and counts remain exact. It lists the last three
merged intervals below the chart when space permits.

## Create a new animation

```powershell
poetry run python cli.py setup --year 2025 --day 13 --animate
poetry run python cli.py animate --year 2025 --day 13 -- --input path/to/example.txt --part 1 --exit-on-complete
poetry run python cli.py animate --year 2024 --day 23 -- --part 2 --steps-per-second 15
poetry run python cli.py animate --year 2024 --day 23 -- --help
```

Put the animation's own flags after `--`. Relative `--input` paths resolve from
the directory where you invoked the CLI, including the `--input=filename` form.
The CLI restores its original directory after completion, errors or help output.
Setup skips existing files rather than replacing your animations. Without
`--download`, setup does not read the session cookie or download puzzle input.

The generated v1 starter previews input lines with frozen snapshots, a lazy
`states()` generator, a pure `draw(state, buffer)` function and explicit `main()`.
Replace `parse_input`, `states` and `draw` with the puzzle's rules and visuals.
It does not compute a puzzle answer. Its default input is `data` beside the
script; pass an existing `--input` file or download the day's data before running.
Imports never open the terminal or load input. Missing files fail before playback.

The shared parser accepts `part=` and `background=` defaults; omitted defaults
remain Part 2 with a background for existing animations. New starters choose
Part 1 with no decorative background. `run_animation` accepts an optional `describe`
callback; without one, it displays an event counter. Snapshots may expose `phase`
for a custom phase label, but plain values (including None) also work.

```powershell
poetry run python -m unittest discover -s tests -p test_cli_scaffolding.py -v
```

These checks generate a new animation in a temporary project, run it through the
actual player/CLI with a fake Screen and clock, and verify forwarding, input
paths, completion, import safety, setup preservation and directory restoration.

## Structure and comparison

Each day's `animate.py` owns input validation, puzzle rules, a lazy generator of
frozen snapshots, and a drawing callback. Generators retain current solver state,
not a materialized animation trace. Draw calls do not advance the simulation.

The small root `animation_support.py` supplies consistent options, clipped
per-cell ANSI labels, a bounded color cache, and the shared native composition:

```python
play(effect_factory=lambda buffer: Scene(
    twinkle_background,
    Playback(states, draw, steps_per_second=rate),
    CallbackEffect(status),
))
```

The actual helper also routes Playback controls, configures completion and fixed
updates, and makes the background optional. Puzzle rules remain in the day files;
there are no legacy renderer adapters or changes to the bruhanimate package.
The day scripts locate this root helper so direct invocation works as well as
the repository CLI. Keep the helper when copying one of these animations.

Every day keeps its original byte for byte as `animate_legacy.py`. Those files
still need the old package. To compare one visually in an isolated environment:

```powershell
cd 2025/day03
uv run --no-project --python 3.13 --with "bruhanimate>=0.2.96,<0.3" python animate_legacy.py
```

Use the corresponding day's directory for the other originals so their relative
input paths work. Keep the shared project dependency on 1.x. Timing and layout
have been redesigned; identical old frames are not a compatibility requirement.

## Verification

```powershell
poetry run python -m unittest discover -s tests -p test_animation_migrations.py -v
poetry run python -m unittest discover -s 2025/day01 -p test_animate.py -v
poetry run python -m unittest discover -s 2025/day07 -p test_animate.py -v
poetry run ruff check animation_support.py tests/test_animation_migrations.py 2025/day03/animate.py 2025/day04/animate.py 2025/day05/animate.py 2025/day06/animate.py
poetry check --lock
```

The new suite uses synthetic inputs, independent counting oracles and fake
clocks/Screens. It tests both parts, parsing, immutable/lazy snapshots, repeatable
clipped drawing, intact ANSI cells, completion with endless backgrounds, controls,
presentation-rate independence and the actual AoC CLI entrypoints. Tests neither
read private puzzle data nor open a real terminal. Local raster previews check
representative layouts; native terminal appearance/performance still needs a
manual run.

## Reusable helpers still worth exploring

Repeated needs now include timed sequences/easing, semantic stepping (an entire
selection or equation instead of a visual sample), following-camera policy and
clipped styled labels. The shared AoC runner removes repetition here without
adding puzzle concepts to the library. A future library helper could cover
these needs after its API and lifecycle contracts are decided. Seeking, rewind,
scrolling history, and independent per-layer pause/rates are not implemented.
