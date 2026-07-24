# fno_coreg_residual — Inspiration

**Novel hybrid extension — no direct precedent in published multi-fidelity field-prediction literature; the closest analogue (ResPCA / `xing2020deepcoreg`) is the same conceptual compose at lower granularity with a GP backbone.**

This family composes two complementary multi-fidelity inductive biases that, in cycle-001, each carried one of the two smoke datasets but missed the other: a continuous-fidelity coregionalization basis-head (Heat regime; `li2022ifc`) and an MFRNP-style residual stack with decoder-in-the-aggregation (Poisson regime; `niu2024mfrnp`). The backbone is the Fourier Neural Operator (`li2020fno`): four FNOs are instantiated, one per fidelity level (L1=8, L2=16, L3=32, L4=64), each operating at its native resolution with full-config sizes (`hidden=64`, `modes_per_level=(4, 8, 12, 12)`, three spectral conv blocks). Each per-fidelity FNO is paired with a small decoder (MFRNP-published `hidden_dim=32`) that produces a single-channel decoded prediction at the level's native resolution; the decoded LF predictions are bilinear-upsampled to the 64×64 HF grid and passed through a pointwise MLP aggregator that fuses them with a broadcast `m` channel to emit the LF-aggregate field `agg(x, m)`. The HF prediction replaces the vanilla output with a coregionalization residual head: the L4 FNO's latent grid is projected to `K=10` channels `h(x)`, and the final HF prediction is `y_HF(x, m) = agg(x, m) + Σ_k B_k(m) h_k(x)` where `B(m) = MLP_B([m, m²])` is a cheap MLP (NOT a neural ODE) whose last linear is zero-initialised so the architecture begins as the pure MFRNP aggregator and optimisation decides how large to make the basis contribution. Per-fidelity output normalisation (`scaler[m] = max(|y|)` over training samples at fidelity `m`) is mandatory and was the cross-cutting cycle-001 finding that mechanically resolved the per-fidelity scale-mismatch failure mode. The closest published precedent is `xing2020deepcoreg`'s ResPCA, which composes a residual term with a low-rank coregionalization basis but with a Gaussian-process backbone and only single-fidelity bases; the granularity here (per-fidelity FNOs, decoder-in-the-aggregation, continuous-`m` threaded into both the aggregator and the basis head) is a strict extension. `val_frac=0.1` preserves HF training samples. An optional Poisson-only loss-weight knob (`HF_weight=2, LF_weight=0.25`) lives in `full_config.json` behind a one-flag flip — this is the `niu2024mfrnp` Poisson5 recipe, kept off by default in the smoke harness so the H3-vs-(H3 + loss-knob) ablation is one config flip away.

## Bibtex

```bibtex
@inproceedings{li2020fno,
  title     = {Fourier Neural Operator for Parametric Partial Differential Equations},
  author    = {Li, Zongyi and Kovachki, Nikola and Azizzadenesheli, Kamyar and Liu, Burigede and Bhattacharya, Kaushik and Stuart, Andrew and Anandkumar, Anima},
  booktitle = {International Conference on Learning Representations},
  year      = {2021},
  note      = {arXiv:2010.08895}
}

@inproceedings{li2022ifc,
  title     = {Infinite-Fidelity Coregionalization for Physical Simulation},
  author    = {Li, Shibo and Wang, Zheng and Kirby, Robert and Zhe, Shandian},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year      = {2022}
}

@inproceedings{niu2024mfrnp,
  title     = {Multi-Fidelity Residual Neural Processes for Scalable Surrogate Modeling},
  author    = {Niu, Ruijia and Wu, Dongxia and Kim, Kai and Ma, Yi-An and Watson-Parris, Duncan and Yu, Rose},
  booktitle = {International Conference on Machine Learning (ICML)},
  year      = {2024}
}

@article{xing2020deepcoreg,
  title   = {Deep coregionalization for the emulation of simulation-based spatial-temporal fields},
  author  = {Xing, Wei W. and Triantafyllidis, Vasilis and Shah, Akeel A. and Nair, Prasanth B. and Zabaras, Nicholas},
  journal = {Journal of Computational Physics},
  volume  = {428},
  year    = {2021},
  doi     = {10.1016/j.jcp.2020.109984},
  note    = {ResPCA — residual + low-rank coregionalization basis, GP backbone}
}
```
