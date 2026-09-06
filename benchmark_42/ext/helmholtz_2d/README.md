# helmholtz_2d_generated

**PDE:** Δu + k²u = f  
**Source:** FNO arXiv:2010.08895 (representative)  
**Ladder:** [[24, 24], [96, 96]]  
**Params (3):** wavenumber_k, source_x, source_y  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).

## Caveat — resonant parameter range (2026-09-06)
Delta u + k^2 u = f on the unit square with homogeneous Dirichlet walls has eigen-wavenumbers pi*sqrt(m^2+n^2) =
4.44, 7.02, 8.89, 9.93, 11.33 ... inside the sampled range k in [4, 12]. Near these the solution amplitude is set by the
distance to resonance, which shifts with the grid, so the 24^2 and 96^2 solutions disagree completely for many samples
(rho-scaled copy-LF rel-L2 = 1.02 on the test split; the theta-only surrogate is also at 1.4). The data is generated
correctly but the coarse level carries almost no usable information; treat as a stress case, not a fidelity-gap benchmark.
