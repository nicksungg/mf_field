# wave_2d_generated

**PDE:** u_tt = c²Δu  
**Source:** PDEBench arXiv:2210.07182 (representative)  
**Ladder:** [[24, 24], [80, 80]]  
**Params (3):** wave_speed, source_x, source_y  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).
