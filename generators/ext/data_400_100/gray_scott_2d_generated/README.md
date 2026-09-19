# gray_scott_2d_generated

**PDE:** Gray-Scott reaction-diffusion (v field)  
**Source:** Pearson 1993, Science 261:189 (DOI 10.1126/science.261.5118.189)  
**Ladder:** [[24, 24], [72, 72]]  
**Params (2):** feed_F, kill_k  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).
