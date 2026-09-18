# cahn_hilliard_2d_generated

**PDE:** c_t = M∇²(c³-c-γ∇²c)  
**Source:** Cahn & Hilliard 1958, JCP 28(2):258 (DOI 10.1063/1.1744102)  
**Ladder:** [[24, 24], [64, 64]]  
**Params (2):** log10_gamma, mean_composition  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).
