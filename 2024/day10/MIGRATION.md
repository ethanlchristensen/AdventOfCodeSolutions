# Day 10 animation migration

The original `animate.py` is preserved byte for byte as `animate_legacy.py`.
The replacement uses the published bruhanimate 1.x lifecycle and shared runner.

```powershell
poetry run python cli.py animate --year 2024 --day 10
poetry run python 2024/day10/animate.py --part 1
poetry run python 2024/day10/animate.py --part 2 --steps-per-second 80
```

The default input remains `data`, resolved beside this script. `--input` accepts
another map. The default is part 2. Invalid, empty and ragged maps fail before
opening the terminal; dots are accepted as impassable cells.

## What changed

The animation first lights the height map from `9` down to `0`. Each cell combines
the already computed answers of adjacent cells exactly one level higher. It
then highlights each trailhead's reachable routes in cyan, distinct reachable
peaks in green. The current cell/trailhead uses a bold white digit on a purple
background, with pink brackets when space permits. Pink pointers at the left,
right and top edges help track its row/column; the footer shows its coordinates
and explains the current calculation. Other cells are subdued, and adjacent
uphill contributors turn cyan during counting. The default rate is 12 events
per second (formerly 40); `--steps-per-second` or +/- adjusts it.
The status shows both totals:

- **Part 1 / score:** distinct reachable `9` cells, summed per trailhead.
- **Part 2 / rating:** all distinct increasing routes, including routes that
  merge before reaching the same peak.

The previous animation recursively drew directly to Screen, used global mutable
counters and random trailhead IDs, and only tracked distinct peaks. The new
version computes both answers with dynamic programming. Per-cell frozen peak
sets deduplicate destinations; integer path counts preserve multiplicity without
enumerating or recording every route. Each source step is one cell calculation
or one trailhead highlight. A trailhead highlight traverses reachable cells once.

Drawing only reads frozen snapshots and clips to the available terminal area.
The camera follows the calculation/current trailhead on boards too large to fit;
the complete map is still solved. Shared Playback supplies pause, stepping,
speed controls and source cleanup. Scene owns the background/status layers and
Player supplies timing and presentation.

Space pauses, `n`/right advances an event, `+`/`-` changes the rate, and `q` quits.
The final answer holds until quit unless `--exit-on-complete` is supplied.
`--fps` controls presentation independently of `--steps-per-second`.
`--no-background` and `--frames` are also available.

## Verification and limits

`test_migration.py` covers merging routes, shared endpoints, unreachable peaks,
missing trailheads, dots, validation, immutable snapshots, tiny clipped buffers,
Playback controls, anchored paths and inert imports. Generated synthetic gradient
maps are compared to an independent path-enumeration oracle. A branching fixture
has 512 routes but produces only one snapshot per map cell and trailhead, plus
initial/completion states. No private inputs or physical terminal are used.

```powershell
poetry run python 2024/day10/test_migration.py
```

The view explains aggregate reachability and route counts; it does not play every
complete route separately. Highlighted reachable dead ends can have no path to a
peak, which is why only green `9` cells contribute to score. The clipped camera
does not show the whole oversized map simultaneously. Native terminal appearance
still needs a local run. The preserved original needs its old bruhanimate
environment and retains its original behavior.
