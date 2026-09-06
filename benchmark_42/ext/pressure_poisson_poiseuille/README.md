# pressure_poisson_poiseuille_generated

**Source:** Partin et al. 2022 (arXiv:2205.05187)  
**Ladder:** [[8, 8], [16, 16], [32, 32], [64, 64]] (coarse->fine)  
**Params (2):** radius_r, v_max  
**Train/Test per fidelity:** 400/100

Factory npz (x,y); aligned MF.

## ⚠️ Synthetic low fidelity (2026-09-06)
The coarse levels are **not solver output**: `generate_pressure_poisson_std.py` builds each coarser level as
block-mean(HF) + uniform noise (HF itself is the analytic Hagen-Poiseuille pressure). This is a downsampled-HF ladder,
so it must not be used for the correction track ("theta + real coarse solve -> fine") and any LF-vs-HF gap statistic on it
measures the block filter, not a discretisation error. Kept in the surrogate track with this caveat.
