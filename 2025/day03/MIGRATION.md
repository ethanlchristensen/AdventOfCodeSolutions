# Day 3 migration

`animate.py` now uses bruhanimate 1.0.0. `animate_legacy.py` is the unchanged
original. See [the shared guide](../../../docs/ANIMATIONS_V1.md) for architecture,
controls and verification.

```powershell
# From the repository root:
poetry run python 2025/day03/animate.py --part 1
poetry run python 2025/day03/animate.py --part 2
```

Part 1 selects 2 batteries, Part 2 selects 12; `--digits` overrides that count.
The default input remains `data`, resolved beside the script. All banks are now
processed, removing the old silent 25-bank cap. The greedy search window is
highlighted; rejected batteries fall and selected ones gather into the result.
A camera follows the candidate when banks exceed the available width. Only five
recent bank totals are retained. Input errors replace the old random fallback.
