# Day 18 animation on bruhanimate 1.x

The original is preserved byte for byte as `animate_legacy.py`. It was a copied
warehouse/box-pushing animation rather than a working falling-byte visualization.
The new version shows this day's memory grid, corruption, BFS search frontier,
shortest route, and the exact first byte that disconnects the exit.

From the repository root:

```powershell
poetry run python cli.py animate --year 2024 --day 18
poetry run python 2024/day18/animate.py --part 1 --size 71 --prefix 1024
poetry run python 2024/day18/animate.py --input path/to/example.txt --size 7 --prefix 12 --part 1
poetry run python 2024/day18/animate.py --input path/to/example.txt --size 7 --part 2
```

Defaults are part 2, input `data` beside the script, a 71-by-71 grid, 30 solver
events/second, and 60 presentation frames/second. `--prefix 1024` applies only to
part 1. Smaller examples need explicit `--size` and, for part 1, `--prefix`;
nothing guesses the dimensions from filenames or private input contents.
Part 2 starts at zero fallen bytes, so an early blocking byte is never skipped.
Missing or malformed input produces an error before opening a terminal.

Space pauses, `n`/right arrow steps one event, `+`/`-` changes speed, and `q` quits.
The final answer holds by default; `--exit-on-complete` exits when the source is
exhausted. `--frames N` bounds presentation; `--no-background` disables twinkles.

Red `#` cells are corrupted memory, cyan `o` cells are the BFS frontier, green
`*` cells form the route, and `X` marks the newest byte. If the grid cannot fit,
the drawing aggregates it into a labeled compressed overview. This can hide
individual narrow passages; the coordinate, path length, and blocker answer
remain exact. Larger terminals show more detail.

BFS keeps one predecessor per discovered cell instead of copying full routes
into the queue. `--search-batch 64` limits queue removals between snapshots.
Part 2 reuses a valid shortest route until a falling byte hits it, then searches
again; all input bytes, including duplicates and blocked endpoints, retain their
correct order. Only current immutable snapshots and the working search survive;
the animation never builds a complete history. Drawing changes no solver state.

Synthetic tests compare random drop sequences and distances against an
independent search, cover endpoints/duplicates/single-cell memory and explicit
prefix validation, and check lazy snapshots, import safety, and tiny buffers.
No private puzzle inputs are used in tests.

```powershell
poetry run python -m unittest discover -s 2024/day18 -p test_migration.py -v
```

The legacy backup requires a separate bruhanimate 0.2.x environment. It is retained
for comparison and does not run under the current 1.x dependency.
