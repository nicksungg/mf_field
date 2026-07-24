# fno_mf_stack — inspiration

This family combines an MFRNP-style residual-stacking architecture (niu2024mfrnp) with
a Fourier Neural Operator backbone (li2020fno). One small FNO is trained per fidelity
level (L1..L4) on the corresponding native-resolution outputs; a small MLP aggregator
("decoder-in-the-aggregation") fuses bilinear-upsampled LF predictions into a baseline
estimate at the HF (64×64) grid, and the HF FNO predicts the *residual* delta on top of
that baseline. The continuous fidelity index `m ∈ {0.0, 0.143, 0.429, 1.0}` is threaded
to the aggregator as a side channel. Per-fidelity output normalization (predict
`y / scaler[m]` where `scaler[m]` is the max-abs of training y at level `m`) is
mandatory: it is the cheap fix for the `ifc_poisson` value-scale collapse documented in
the cycle-000 failure analysis (poisson y_max drops ~40× from L1 to L4). The
residual decomposition lets the 5 HF training samples supervise a *correction* on top
of an LF-only baseline backed by 170 LF samples, rather than learning the full HF
output from 5 examples directly. The spectral-conv backbone of li2020fno is the natural
inductive bias for regular-grid PDE data; per-level routing combined with the residual
stack is the niu2024mfrnp template.

Cycle-002 H4 update (capacity + Poisson-loss provenance): the smoke-path
`SMOKE_DEFAULTS` are now a scaled-down mirror of `full_config.json`
(hidden=32, modes=(4,8,12,12), 3 spectral blocks) so the smoke path no longer
silently diverges from the full config — cycle-001 H2's smoke ran at 1/49 the
parameter count of its full config and that capacity gap dominated the Heat
regression. Per-fidelity loss weighting (`HF_weight=2.0, LF_weight=0.25`,
applied to the already-normalized per-fidelity MSE residuals) is the verbatim
setting from MFRNP `Poisson5_config.yaml` — an 8× HF up-weighting that the
MFRNP paper gates explicitly to Poisson; Heat's published `pde_config.yaml`
uses uniform weighting. We mirror that gating: weights are applied only when
the dataset name contains "poisson", otherwise we fall back to uniform.

bibtex_keys: niu2024mfrnp, li2020fno

```bibtex
@inproceedings{niu2024mfrnp,
  title     = {Multi-Fidelity Residual Neural Processes for Scalable Surrogate Modeling},
  author    = {Niu, Ruijia and Wu, Dongxia and Kim, Kai and Ma, Yian and Watson-Parris, Duncan and Yu, Rose},
  booktitle = {Proceedings of the 41st International Conference on Machine Learning (ICML)},
  year      = {2024}
}

@inproceedings{li2020fno,
  title     = {Fourier Neural Operator for Parametric Partial Differential Equations},
  author    = {Li, Zongyi and Kovachki, Nikola and Azizzadenesheli, Kamyar and Liu, Burigede and Bhattacharya, Kaushik and Stuart, Andrew and Anandkumar, Anima},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2021},
  eprint    = {2010.08895}
}
```
