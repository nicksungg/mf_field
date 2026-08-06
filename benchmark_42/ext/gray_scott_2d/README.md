# gray_scott_2d_generated

**PDE:** Gray-Scott reaction-diffusion (v field)  
**Source:** Pearson 1993, Science 261:189 (DOI 10.1126/science.261.5118.189)  
**Ladder:** [[24, 24], [72, 72]]  
**Params (2):** feed_F, kill_k  
**Train/Test (per fidelity):** 400/100

Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). Aligned MF (same params across fidelities).


## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **MF-useless** — LF–HF correlation is 0.008, so the coarse field carries essentially no information about the fine one. Multi-fidelity is pointless here by construction.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for criteria, thresholds, and caveats.

