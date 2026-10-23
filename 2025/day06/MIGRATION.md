# Day 6 migration

`animate.py` now uses bruhanimate 1.0.0. `animate_legacy.py` preserves the original.
See [the shared guide](../../../docs/ANIMATIONS_V1.md) for controls and tests.

```powershell
# From the repository root:
poetry run python 2025/day06/animate.py --part 1
poetry run python 2025/day06/animate.py --part 2 --input 2025/day06/data
```

The default input remains `dataanimate`. The scanner follows rows for Part 1 and
vertical columns, right to left, for Part 2. Each equation builds visibly before
its result is committed once to the total. Repeated operands are preserved,
fixing the old `if num not in building_equation` deduplication. Zero results are
completed normally. Parsing preserves alignment, pads ragged right edges,
tolerates trailing blank lines and validates each operator/operand block.
The worksheet remains visible at completion rather than becoming a field of
screen-filling twinkles.
