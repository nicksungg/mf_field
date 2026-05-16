# Inspiration — fno_coregionalization

This family combines an FNO spectral-convolution backbone (li2020fno) with an
IFC-style continuous-fidelity coregionalization head (li2022ifc). The model
factors a multi-fidelity field prediction as `f(x, m) = sum_k B_k(m) * h_k(x)`,
where `h(x) ∈ R^{K × H × W}` is a low-rank latent grid produced by the FNO
backbone and `B(m)` is a small MLP basis on `[m, m^2]` for `K=10` latents.
The full IFC neural ODE basis is replaced with the MLP for smoke-time budget
(the paper reports ~7.84 s/epoch for K=20 — too slow at smoke scale). A
per-fidelity output scaler `y / scaler[m]` is applied before loss, where
`scaler[m] = max(|y|)` over training data at fidelity `m`; this addresses the
~40× value-scale collapse across fidelities seen on `ifc_poisson` and is
projected to drop test nRMSE from 18.5 to ~1.0 on its own (cross-cutting
finding from the cycle Researcher). Lower-fidelity inputs are bilinearly
upsampled to the 64×64 HF grid following li2022ifc §6.1, so the FNO sees a
single input resolution and the coregionalization head handles the fidelity
mixing.

bibtex_keys: li2020fno, li2022ifc

```bibtex
@inproceedings{li2020fno,
  title     = {Fourier Neural Operator for Parametric Partial Differential Equations},
  author    = {Li, Zongyi and Kovachki, Nikola and Azizzadenesheli, Kamyar and
               Liu, Burigede and Bhattacharya, Kaushik and Stuart, Andrew and
               Anandkumar, Anima},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2021},
  note      = {arXiv:2010.08895}
}
```

```bibtex
@article{li2022ifc,
  title   = {Infinite-Fidelity Coregionalization for Physical Simulation},
  author  = {Li, Shibo and Wang, Zheng and Kirby, Robert M. and Zhe, Shandian},
  journal = {Advances in Neural Information Processing Systems (NeurIPS)},
  year    = {2022},
  note    = {arXiv:2207.00678}
}
```
