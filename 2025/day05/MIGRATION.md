# Day 5 migration

`animate_legacy.py` preserves the original snow-only placeholder. The new
`animate.py` uses bruhanimate 1.0.0 to visualize the actual puzzle.
See [the shared guide](../../../docs/ANIMATIONS_V1.md) for controls and tests.

```powershell
# From the repository root:
poetry run python 2025/day05/animate.py --part 1
poetry run python 2025/day05/animate.py --part 2
```

The default input remains `data`. A scaled number line shows incoming ranges
joining the disjoint union of fresh IDs. Part 1 then checks every listed
ingredient, including duplicate IDs; Part 2 reports the union's inclusive size.
Adjacent ranges merge because integer IDs leave no gap between them. Numeric
projection and counting use exact integer arithmetic, without expanding large
ranges. Distinct intervals can overlap visually at low screen resolution, so
precise bounds and totals are also displayed.
