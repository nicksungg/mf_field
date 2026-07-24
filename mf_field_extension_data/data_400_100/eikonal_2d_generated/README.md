# eikonal_2d_generated

**PDE:** |∇T| = 1/speed (travel time)  
**Source:** Sethian 1996, PNAS 93(4):1591 (DOI 10.1073/pnas.93.4.1591)  
**Ladder:** [[24, 24], [64, 64]]  
**Params (3):** source_x, source_y, log10_inclusion_speed  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).
