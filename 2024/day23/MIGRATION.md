# Day 23: original triangle view on bruhanimate 1.x

The default is now the original triangle presentation: a fixed A-Z coordinate
board, green @ markers and three connecting edges for the current qualifying
triangle. Earlier triangle members turn gray; completion leaves them gray.
The matrix and circular network views have been removed.
Edges use the original DrawLinesEffect sub-cell character renderer (thin=False).

```powershell
# From the repository root: original triangle animation (Part 1)
poetry run python cli.py animate --year 2024 --day 23
poetry run python 2024/day23/animate.py --part 1
# Optional exact largest-group solver with one triangle preview at a time:
poetry run python 2024/day23/animate.py --part 2
```

Each two-letter computer keeps its original coordinates: first letter across,
second letter down. For example, ab is column A, row B. Only triples containing
a lowercase t-name animate in Part 1. Counters still examine all triangles.
Part 1 is the CLI default because the original visualized these triples even
when its unused part setting said two. Part 2 remains an explicit option: cyan
marks its best group, while only up to three green vertices and three edges
preview connections. The password describes the entire exact best group.

Default input is data beside animate.py; playback is 10 events/second at 60 FPS.
Space/p pauses, n/right steps, +/- changes speed, and q/Escape quits. The final
frame holds unless --exit-on-complete is supplied. --frames limits presentation;
--background enables optional twinkles, off by default. --search-batch bounds
solver work between search snapshots. Missing or malformed input fails before
the terminal opens.

The entire fixed board compresses in short terminals; a label warns that some
coordinates may share cells. A terminal at least 60 columns wide and 36 rows
high shows the full alphabet grid without merging coordinates. Other supported
computer names use stable sorted row-major positions instead of letter mapping.
Drawing reads immutable snapshots, and only the set of past triangle members
is retained. No all-cliques list or animation history is built. The Part 2
maximum-clique search is exact but exponential in the worst case.

animate_legacy.py remains byte-exact and requires a separate 0.2.x environment.
The current implementation keeps the native v1 lifecycle and shared controls.

```powershell
poetry run python -m unittest discover -s 2024/day23 -p test_migration.py -v
```

Tests use synthetic inputs and independent solver oracles. They cover original
coordinates, three-edge limits, gray history, both parts, frozen/lazy states,
pure clipped drawing, default triangle mode and import safety.
