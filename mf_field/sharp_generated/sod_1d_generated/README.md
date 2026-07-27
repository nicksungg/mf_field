# sod_1d_generated

**PDE module:** sod  
**Source:** Sod 1978, JCP 27:1  
**ndim:** 1  
**Availability:** regenerable (eloise sharp-field solver)  

## Fidelity ladder (ablation-driven)

- L1: [32]
- L2: [64]
- L3: [128]

## Inputs/outputs
- `x`: (N,3) condition vector [rho_l, p_l, gamma]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **400**  Test: **100**

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).
