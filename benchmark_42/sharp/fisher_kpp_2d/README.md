# fisher_kpp_2d_generated

**PDE module:** fisher_kpp  
**Source:** Fisher 1937 / KPP 1937  
**ndim:** 2  
**Availability:** regenerable (eloise sharp-field solver)  

## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **copy-LF-trivial** — lifting LF onto the HF grid already reproduces HF to within 0.0006 relative L2 at full resolution. Copying the coarse field solves the task; there is no fidelity gap to learn.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for the criteria, thresholds, and their caveats.

## Fidelity ladder (ablation-driven)

- L1: [64, 64]
- L2: [128, 128]
- L3: [256, 256]

## Inputs/outputs
- `x`: (N,50) condition vector [D, r, ic_c0, ic_c1, ic_c2, ic_c3, ic_c4, ic_c5, ic_c6, ic_c7, ic_c8, ic_c9, ic_c10, ic_c11, ic_c12, ic_c13, ic_c14, ic_c15, ic_c16, ic_c17, ic_c18, ic_c19, ic_c20, ic_c21, ic_c22, ic_c23, ic_c24, ic_c25, ic_c26, ic_c27, ic_c28, ic_c29, ic_c30, ic_c31, ic_c32, ic_c33, ic_c34, ic_c35, ic_c36, ic_c37, ic_c38, ic_c39, ic_c40, ic_c41, ic_c42, ic_c43, ic_c44, ic_c45, ic_c46, ic_c47]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **400**  Test: **100**

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).
