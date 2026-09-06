# ifc_poisson

**Paper:** li2022ifc
**Domain:** poisson_pde_2d
**License:** MIT
**Availability:** local
**Revision:** repaired 2026-08-03 (see "Repair history" below) — supersedes the copy released 2026-07-28.

## Fidelity ladder

- L1: [8, 8] — 100 train samples
- L2: [16, 16] — 50 train samples
- L3: [32, 32] — 20 train samples
- L4: [64, 64] — 5 train samples

Test ships only at the top fidelity: 128 samples at [64, 64].
Condition vector is 5-dimensional.

## File layout

```
train/fidelity_{8,16,32,64}/{Xs.npy, ys.npy}
test/fidelity_64/{Xs.npy, ys.npy}
pairing_report.json
```

`Xs.npy` has shape `(N, 5)`, `ys.npy` has shape `(N, H, W)`, both `float64`.

## Repair history

The 2026-07-28 release had **disjoint fidelity levels**: the parameter vectors at each
fidelity were drawn independently, so no sample appeared at more than one fidelity.
That breaks the aligned/nested multi-fidelity assumption this benchmark is built on —
`HF - LF` residuals are undefined when no LF solve corresponds to a given HF solve.

This revision regenerates the ladder with **nested** parameter sets: the 50 L2 conditions
are a subset of the 100 L1 conditions, the 20 L3 conditions a subset of L2, and the 5 L4
conditions a subset of L3. Verified directly on the shipped arrays:

```
16 nested in 8:   True
32 nested in 16:  True
64 nested in 32:  True
train(f64) disjoint from test: True
```

Seeds are recorded in `pairing_report.json` (`seed_train` 20260803, `seed_test` 20260804).

**Removed in this revision:** `scalers/fidelity_*/scaler_{Xs,ys}.pkl`. Those were fitted on
the old disjoint sample set, so their means and scales describe data that no longer ships.
Re-shipping them would silently mis-normalize the repaired fields. No model reads them —
the families that normalize per fidelity recompute max-abs from the raw arrays at load
time. Fit your own on the training split if you need them.

**`cat.pkl` is retained.** It is a pure ladder descriptor (`fid_list`, `t_list`, `ns_list`,
`fid_min`/`fid_max`) with no pairing information, and six model families read it to
discover the fidelity ladder. It was dropped in error during the repair and has been
rebuilt from the repaired arrays; the rebuild reproduces the original exactly.

## Load example

```python
import numpy as np

Xs = np.load("train/fidelity_8/Xs.npy")   # (100, 5)
ys = np.load("train/fidelity_8/ys.npy")   # (100, 8, 8)
```

## ⚠️ Known defect (found 2026-09-06)
Same dx^2 amplitude scaling as `core/poisson_generated` / `core/poisson_local` (MANIFEST `copy_lf_rel_l2 = 78.3`):
the LF field is tens of times larger than the HF field because each level solves a differently-scaled problem.
The defect is in the upstream IFC generator. Excluded from the correction track (also: unpaired, HF-only test).
