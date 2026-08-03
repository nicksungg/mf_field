# phase_field_crystal_2d_generated

**PDE module:** phase_field_crystal  
**Source:** Elder & Grant 2004  
**ndim:** 2  
**Availability:** regenerable (eloise sharp-field solver)  

## Fidelity ladder (ablation-driven)

- L1: [32, 32]
- L2: [64, 64]
- L3: [128, 128]

## Inputs/outputs
- `x`: (N,18) condition vector [r, mean_density, ic_c0, ic_c1, ic_c2, ic_c3, ic_c4, ic_c5, ic_c6, ic_c7, ic_c8, ic_c9, ic_c10, ic_c11, ic_c12, ic_c13, ic_c14, ic_c15]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **8**  Test: **2**

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).
