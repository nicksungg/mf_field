# allen_cahn_2d_generated

**PDE module:** allen_cahn  
**Source:** APEBench (arXiv:2411.00180)  
**ndim:** 2  
**Availability:** regenerable (eloise sharp-field solver)  

## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **operator-hard** — the condition vector barely predicts the field (param→field distance correlation 0.012, threshold 0.15). Nothing conditions the prediction. See the caveats in the collection README before excluding this dataset on that basis alone.
- **level-dominated** — copying LF scores 0.0069 relative L2, but only because the field is nearly uniform: after removing each sample's spatial mean the copy error is 0.1465, 21x larger. The headline metric here is dominated by a constant offset that LF reproduces for free, while the structure is still substantially wrong.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for criteria, thresholds, and caveats.

## Fidelity ladder (ablation-driven)

- L1: [64, 64]
- L2: [128, 128]
- L3: [256, 256]

## Inputs/outputs
- `x`: (N,19) condition vector [eps, mobility, mean_composition, ic_c0, ic_c1, ic_c2, ic_c3, ic_c4, ic_c5, ic_c6, ic_c7, ic_c8, ic_c9, ic_c10, ic_c11, ic_c12, ic_c13, ic_c14, ic_c15]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **400**  Test: **78** (trimmed from 100 — see changelog)

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).

## Changelog

- **2026-08-06 — test split trimmed 100 → 78 rows** (MFFP autoresearch ADR r3-0003 D1).
  22 test rows had a per-row copy-LF gap below `max(1e-6, 1% of the dataset median)` — 9 of them bit-identical LF ≡ HF constant fields.
  Those rows contain no prediction task (the dynamics reach the uniform state by the snapshot time for their ε/parameter combos) and bias any copy-LF-referenced score.
  Dropped indices and the trim criterion are recorded in `meta.json` (`test_trim_2026_08_06`); the pre-trim split is available from this repository's git history (revisions before 2026-08-07).
  Train split untouched.
  Scores computed against the pre-trim test split are **not comparable** to post-trim scores.
