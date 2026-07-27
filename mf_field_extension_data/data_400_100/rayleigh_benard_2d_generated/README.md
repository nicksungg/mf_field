# rayleigh_benard_2d_generated

**PDE:** Boussinesq convection (T field)  
**Source:** de Vahl Davis 1983, IJNMF 3(3):249 (DOI 10.1002/fld.1650030305)  
**Ladder:** [[24, 24], [64, 64]]  
**Params (1):** log10_rayleigh  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).
