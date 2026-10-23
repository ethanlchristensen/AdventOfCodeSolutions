# Day 4 migration

`animate.py` now uses bruhanimate 1.0.0. `animate_legacy.py` preserves the original.
See [the shared guide](../../../docs/ANIMATIONS_V1.md) for controls and tests.

```powershell
# From the repository root:
poetry run python 2025/day04/animate.py --part 1
poetry run python 2025/day04/animate.py --part 2 --detail --input 2025/day04/data
```

The default input remains `datasmall`. The complete board is processed instead
of cropping it to 20x20. Default wave mode highlights removable rolls, then
removes them in batches with short spark/fade transitions. `--detail` inspects
each roll and highlights its eight neighbors. A following camera handles large
boards; the column-density strip retains global context. Eligibility is frozen
before each removal wave, so newly exposed rolls wait until the next wave.
Part 1 reports the first wave without mutating it; Part 2 continues until stable.
