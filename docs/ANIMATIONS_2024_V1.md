# 2024 animations with bruhanimate 1.x

All five existing 2024 visualizations now use the shared v1 player: Days 6, 10,
15, 18 and 23. Day 6 also gains the conventional `animate.py` entrypoint, so the
repository CLI can discover it. Its existing `animated.py` command forwards to
that same implementation.

The project's existing Poetry environment already locks bruhanimate 1.0.0.
No dependency update or new library release is required for these migrations.

## Run them

From the AdventOfCodeSolutions root:

```powershell
poetry install
poetry run python cli.py list --year 2024
poetry run python cli.py animate --year 2024 --day 6
poetry run python cli.py animate --year 2024 --day 10
poetry run python cli.py animate --year 2024 --day 15
poetry run python cli.py animate --year 2024 --day 18
poetry run python cli.py animate --year 2024 --day 23
```

Direct invocation exposes each animation's puzzle and playback options:

```powershell
poetry run python 2024/day06/animate.py --part 1
poetry run python 2024/day06/animated.py --part 2 --show-steps
poetry run python 2024/day10/animate.py --part 2
poetry run python 2024/day15/animate.py --part 2 --input 2024/day15/data
poetry run python 2024/day18/animate.py --part 1 --size 71 --prefix 1024
poetry run python 2024/day18/animate.py --part 2 --size 71
poetry run python 2024/day23/animate.py --part 2 --steps-per-second 60
```

Default input filenames remain `datasmall` for Day 6, `data` for Day 10,
`datasmall4` for Day 15 and `data` for Day 23. Day 18 now reads coordinate input
from `data`, replacing the copied warehouse demo. Its explicit grid default is
71x71; Part 1 uses the first 1024 coordinates. For a smaller example, supply the
appropriate `--size` and `--prefix`; dimensions are not guessed from the input.

Default paths are anchored beside the day script; explicit relative `--input`
paths resolve from the current directory. Missing or malformed input fails
before the terminal opens. Puzzle inputs, session cookies and credentials are
not embedded in the animations, documentation or tests.

Space/p pauses, n/right advances one visual event, +/- changes playback speed,
and q/Escape/Ctrl+C quits. All animations support `--part 1`/`--part 2`,
`--steps-per-second`, `--fps`, `--frames`, `--no-background`, and
`--exit-on-complete`. Final results stay visible by default. A visual event can
be a solver step or a bounded batch of search work; stepping is not necessarily
one full puzzle decision. Detailed patrol mode can take much longer to watch.

## What each migration changes

| Day | Puzzle and visual behavior |
| --- | --- |
| 6 | Guard patrol with visited trails, direction-state loop detection, and candidate-obstruction results. Looping inputs terminate instead of hanging. Optional detailed movement shows each trial. |
| 10 | Height-map trails with per-trailhead highlights and exact summit/path counts. Dynamic programming avoids enumerating every possible route. |
| 15 | Robot-following warehouse with push and blocked-move feedback. Both narrow and wide boxes work; wide pushes move dependency chains atomically. All wrapped input moves are processed instead of silently discarding three quarters. |
| 18 | Falling coordinates, shortest-path search and the first byte that disconnects the exit. This replaces the unrelated warehouse code previously in this day's animation. |
| 23 | Graph triangle search for Part 1, and an exact largest-clique search/password for Part 2. Search work is yielded incrementally instead of eagerly collecting all cliques. |

Drawing clips to the available terminal. See each day's `MIGRATION.md` for its
layout, algorithm choices and any additional options. The graph search remains
exponential in the worst case: bounded visual work keeps it responsive but does
not make arbitrary large-clique problems cheap. Final results are exact rather
than silently sampling/capping the search.

## Structure and originals

Each day's native `animate.py` contains its parser, puzzle rules, lazy frozen
snapshots and drawing. Root `animation_support.py` supplies consistent playback
controls, completion, headers, a subtle optional twinkle background and safe
per-cell ANSI labels. Player and Scene own timing, presentation and cleanup;
drawing never advances the solver. The bruhanimate package itself is unchanged.
Keep the shared root helper when copying one of these animations elsewhere.

Day 6's original is preserved byte for byte as `animated_legacy.py`. The other
four originals are preserved as `animate_legacy.py`. They remain useful for
comparison and still use their original APIs and relative input paths. To run
one with the old package in an isolated environment:

```powershell
cd 2024/day15
uv run --no-project --python 3.13 --with "bruhanimate>=0.2.96,<0.3" python animate_legacy.py
```

Use the corresponding directory/legacy filename for other days. The old Day 18
file is the preserved warehouse code, not a correct falling-byte solver. Keep
the shared project dependency on 1.x for the migrated animations.

## Checks

```powershell
poetry run python -m unittest discover -s tests -p test_2024_animation_integration.py -v
poetry run python -m unittest discover -s 2024/day06 -p test_migration.py -v
poetry run python -m unittest discover -s 2024/day10 -p test_migration.py -v
poetry run python -m unittest discover -s 2024/day15 -p test_migration.py -v
poetry run python -m unittest discover -s 2024/day18 -p test_migration.py -v
poetry run python -m unittest discover -s 2024/day23 -p test_migration.py -v
poetry check --lock
```

The synthetic tests cover puzzle results, parsing, frozen snapshots, clipped and
repeatable drawing, lifecycle completion, import safety and actual CLI startup.
Cross-day tests verify both parts and discovery, including Day 6's new entrypoint.
They use fake clocks and Screens and never read private puzzle input. Run the
animations in a native terminal to judge their appearance and real input speed.

The existing 2025 animation tests remain regression checks; their commands are
in [the general migration guide](ANIMATIONS_V1.md#verification).
