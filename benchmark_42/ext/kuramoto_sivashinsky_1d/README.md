# kuramoto_sivashinsky_1d_generated

**PDE:** KS spatiotemporal chaos  
**Source:** Kuramoto-Tsuzuki 1976 / Sivashinsky 1977  
**Ladder:** [[64, 40], [256, 120]]  
**Params (3):** domain_L, ic_amplitude, ic_phase  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).


## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **MF-useless** — LF–HF correlation is -0.057, so the coarse field carries essentially no information about the fine one. Multi-fidelity is pointless here by construction.
- **operator-hard** — the condition vector barely predicts the field (param→field distance correlation 0.079, threshold 0.15). Nothing conditions the prediction. See the caveats in the collection README before excluding this dataset on that basis alone.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for criteria, thresholds, and caveats.

