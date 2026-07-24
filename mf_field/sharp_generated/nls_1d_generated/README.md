# nls_1d_generated (IC-encoded, learnable)

**Source:** classical (split-step)  
**Ladder:** [[128], [256], [512]]  
**Params (17):** nonlinearity, ic_c0, ic_c1, ic_c2, ic_c3, ic_c4, ic_c5, ic_c6, ic_c7, ic_c8, ic_c9, ic_c10, ic_c11, ic_c12, ic_c13, ic_c14, ic_c15  
**Train/Test per fidelity:** 400/100

IC built from low Fourier-mode coefficients stored in x (cond), so field=f(x) is well-posed & learnable.
