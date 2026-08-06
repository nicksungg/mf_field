# nls_1d_generated (IC-encoded, learnable)

**Source:** classical (split-step)  
**Ladder:** [[128], [256], [512]]  
**Params (17):** nonlinearity, ic_c0, ic_c1, ic_c2, ic_c3, ic_c4, ic_c5, ic_c6, ic_c7, ic_c8, ic_c9, ic_c10, ic_c11, ic_c12, ic_c13, ic_c14, ic_c15  
**Train/Test per fidelity:** 400/100

IC built from low Fourier-mode coefficients stored in x (cond), so field=f(x) is well-posed & learnable.


## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **operator-hard** — the condition vector barely predicts the field (param→field distance correlation -0.046, threshold 0.15). Nothing conditions the prediction. See the caveats in the collection README before excluding this dataset on that basis alone.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for criteria, thresholds, and caveats.

