# kdv_1d_generated (fixed)

**PDE:** KdV u_t+6uu_x+delta^2 u_xxx=0  
**Source:** APEBench (arXiv:2411.00180)  
**Ladder:** [[32], [64], [128]]  
**Params (2):** delta in [0.05,0.10], ic_amplitude in [0.3,0.7]  
**Train/Test per fidelity:** 400/100  
dt=5.8e-06 (CFL); IC=16 modes.
Fixed from the original (delta[0.015,0.04]+broadband IC) which decorrelated LF/HF.
