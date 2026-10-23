# Day 6 animation migration

The original `animated.py` is preserved byte for byte as `animated_legacy.py`.
The v1 implementation lives in `animate.py`; `animated.py` now forwards to it,
so the old filename and the shared AoC animation command both work.

```powershell
poetry run python cli.py animate --year 2024 --day 6
poetry run python 2024/day06/animated.py --part 1
poetry run python 2024/day06/animate.py --part 2 --show-steps --steps-per-second 100
```

The default input remains `datasmall`, resolved beside the script regardless of
the working directory. Use `--input 2024/day06/data` to choose the full input
when running from the repository root. Missing or invalid input is reported
before opening the terminal. The default is part 2.

## What changed

- Part 1 follows the guard, showing visited floor and a short fading directional
  trail. Large boards use a clipped camera instead of dropping board cells.
- Part 2 highlights each trial obstruction and marks every loop-producing
  placement with a red `O`. The default advances one complete trial per step;
  `--show-steps` reveals every movement and turn within each trial.
- Loop detection uses `(position, direction)`, so enclosed guards and looping
  trials finish. The original obstacle animation could remain in its inner loop
  indefinitely. Turns at the same position do not count as leaving the map.
- For an exiting baseline, only previously visited floor cells need testing.
  A looping baseline tests all legal floor cells; placing an obstacle away from
  its route can preserve an existing loop and must still count.
- Input is parsed once. Immutable snapshots carry puzzle state; drawing does
  not alter it. The shared `animation_support.py` composes background, playback
  and status layers, with Player owning timing and input routing.

Space pauses, `n`/right advances one source event, `+`/`-` changes the rate, and
`q` quits. Completion holds the answer; `--exit-on-complete` exits instead.
`--no-background`, `--fps`, and `--frames` are also supported. Rates are source
events per second; they are independent of presentation FPS.

## Verification and limits

`test_migration.py` uses synthetic maps, including 80 generated boards checked
against an independent exhaustive-placement oracle. It also covers a looping
baseline with unreachable floor, all guard headings, immutability, clipped pure
drawing, Playback controls, import safety, default input paths, and forwarding
after another day's `animate` module has already been imported. No private input
or physical terminal is used. Run it with:

```powershell
poetry run python 2024/day06/test_migration.py
```

The solver retains one trial at a time; it does not cache full traces or silently
limit candidates. Part 2 still performs a patrol per candidate, so full inputs
can take many steps. Compact mode groups one trial into a synchronous source
advance; detailed mode exposes its individual movement events. The camera shows
a viewport, not a simultaneous overview of the whole oversized board. Native
terminal appearance needs a local run. The preserved original requires its old
environment and retains its original behavior.
