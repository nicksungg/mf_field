# euler_generated

**PDE module:** euler  
**Source:** The Well (arXiv:2412.00568); Schulz-Rinne 1993  
**ndim:** 2  
**Availability:** regenerable (eloise sharp-field solver)  

## Fidelity ladder (ablation-driven)

- L1: [32, 32]
- L2: [64, 64]
- L3: [128, 128]

## Inputs/outputs
- `x`: (N,7) condition vector [pTL/pTR, pBL/pTR, pBR/pTR, rTL/rTR, rBL/rTR, rBR/rTR, gamma]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **400**  Test: **100**

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).
