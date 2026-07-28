# helmholtz_2d_generated

**PDE:** Δu + k²u = f  
**Source:** FNO arXiv:2010.08895 (representative)  
**Ladder:** [[24, 24], [96, 96]]  
**Params (3):** wavenumber_k, source_x, source_y  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).
