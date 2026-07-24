# kuramoto_sivashinsky_1d_generated

**PDE:** KS spatiotemporal chaos  
**Source:** Kuramoto-Tsuzuki 1976 / Sivashinsky 1977  
**Ladder:** [[64, 40], [256, 120]]  
**Params (3):** domain_L, ic_amplitude, ic_phase  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).
