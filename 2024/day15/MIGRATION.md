# Day 15 animation: bruhanimate 1.x

The original is preserved byte for byte in `animate_legacy.py`; it requires an
isolated bruhanimate 0.2.x environment. The migrated `animate.py` uses the shared
`animation_support.py` runner, native `Playback`, and a clipped `GridViewport`.
Importing the module opens no terminal and reads no input.

From the AdventOfCodeSolutions root:

```powershell
poetry run python cli.py animate --year 2024 --day 15
poetry run python 2024/day15/animate.py --part 1 --input 2024/day15/data
poetry run python 2024/day15/animate.py --part 2 --steps-per-second 8 --exit-on-complete
```

The default remains **part 2**, using `datasmall4` beside this script. Unlike the
original special case, every move is processed; wrapped movement lines are
concatenated. Input is validated before opening the terminal. There is no silent
fallback or cropping of the warehouse/move stream. Open edges behave as walls.

The robot remains cyan, crates purple, and recent robot positions form a bounded
fading trail. Successful pushes turn gold; blocked crates and obstruction cells
turn red. A following camera keeps the robot visible when the complete warehouse
does not fit; the score always includes every crate, including offscreen ones.
The move strip shows nearby completed/current/upcoming commands. Exact progress,
GPS score, push count, and blocked-attempt count stay in the header. The former
large text-art score/arrow and fireworks were replaced with a compact status
display and the shared optional twinkle background, leaving more room for boxes.

Each attempted move produces one immutable snapshot. Part 2 stores whole box
anchors and resolves every dependent box before committing a push, including
vertical pushes that fan out into multiple crates. A wall in any branch cancels
the entire move. The generator retains the current warehouse and 16 trail points;
it does not materialize the animation history. Draw only reads the current state.

Space pauses, `n`/right steps, `+`/`-` adjusts steps per second, and `q` quits.
The shared player updates at 60 Hz and presents at `--fps` (default 60), while
`--steps-per-second` controls attempted moves (default 16). The final score holds
until quit unless `--exit-on-complete` is supplied. `--frames` limits presentation
frames for smoke checks; `--no-background` disables the decorative layer.

`test_migration.py` uses synthetic maps only: both parts, known GPS scores,
multiline commands, boundary blocking, wide-box horizontal chains and vertical
fan-out, atomic blocked pushes, random comparisons with a mutable cell-grid
reference, box/wall invariants, lazy immutable snapshots, pure clipped drawing,
inert CLI imports, runner delegation, and real player completion/cleanup using a
recording screen and fake clock. Native terminal appearance still needs
an interactive check. Reusable camera-follow and highlighted move-strip helpers
would reduce the remaining application drawing code; crate rules belong here.
