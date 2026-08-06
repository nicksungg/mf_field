# allen_cahn_1d_generated

**PDE module:** allen_cahn  
**Source:** APEBench (arXiv:2411.00180)  
**ndim:** 1  
**Availability:** regenerable (eloise sharp-field solver)  

## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **operator-hard** — the condition vector barely predicts the field (param→field distance correlation 0.118, threshold 0.15). Nothing conditions the prediction.
- **copy-LF-trivial** — lifting LF onto the HF grid already reproduces HF to within 0.0027 relative L2 at full resolution. Copying the coarse field solves the task; there is no fidelity gap to learn.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for the criteria, thresholds, and their caveats.

## Fidelity ladder (ablation-driven)

- L1: [128]
- L2: [256]
- L3: [512]

## Inputs/outputs
- `x`: (N,19) condition vector [eps, mobility, mean_composition, ic_c0, ic_c1, ic_c2, ic_c3, ic_c4, ic_c5, ic_c6, ic_c7, ic_c8, ic_c9, ic_c10, ic_c11, ic_c12, ic_c13, ic_c14, ic_c15]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **400**  Test: **100**

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).
