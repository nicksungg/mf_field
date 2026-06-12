# Inspiration — fno_coreg_conditioned

This family replaces the IFC outer-product fidelity basis
`f(x, m) = sum_k B_k(m) * h_k(x)` (li2022ifc, the basis used by
`fno_coregionalization`) with FiLM-via-LayerNorm conditioning on the
fidelity index `m` inside an FNO (li2020fno) backbone. A single
full-resolution HF FNO produces the prediction directly; each FNO
block applies GroupNorm followed by a per-channel affine
`γ(m), β(m) = MLP([m, m^2])` so the conditioning signal modulates the
normalisation layer rather than feeding a K-dim coregionalization head.
This is the canonical 2024-2025 PDE-parameter-conditioning composition
(beggs2025pdecond presents FiLM-via-LayerNorm specifically for parametric
PDE surrogates; herde2024poseidon scales time-conditioned LayerNorm to
the Poseidon scOT foundation model at NeurIPS 2024). The LF→HF transfer
training schedule from lyu2023mffno is retained in `smoke_eval.py`
unchanged from the sibling `fno_coregionalization` family; the K-dim
basis is the only architectural component being replaced. Hypothesis:
because m-modulation is now carried by affine LayerNorm parameters
rather than a per-fidelity outer-product basis tied to a specific
m-correlation structure, the same family can fit both heat- and Poisson-
style fidelity correlations (closing the `FAMILY_PDE_SPECIALIZATION_
ASYMMETRY` failure mode observed at `fno_coregionalization × ifc_poisson`
= 0.7501 vs heat = 0.01551 on cycle-008).

Mode-A architecture (preferred, implemented): FNOBlock with FiLMNorm
replacing GroupNorm; γ projection is zero-initialised so γ ≈ 1, β ≈ 0
at start (standard FiLM init trick, preserves the un-conditioned forward
pass and avoids early divergence). Mode B (fallback, not used here):
broadcast `B(m) ∈ R^K` over the grid and concatenate to the FNO input
channels — kept in reserve if Mode A fails the smoke contract or wall
budget.

bibtex_keys: li2022ifc, li2020fno, lyu2023mffno, beggs2025pdecond, herde2024poseidon

```bibtex
@article{li2022ifc,
  title   = {Infinite-Fidelity Coregionalization for Physical Simulation},
  author  = {Li, Shibo and Wang, Zheng and Kirby, Robert M. and Zhe, Shandian},
  journal = {Advances in Neural Information Processing Systems (NeurIPS)},
  year    = {2022},
  note    = {arXiv:2207.00678}
}
```

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
@article{lyu2023mffno,
  title   = {Multi-fidelity prediction of fluid flow based on transfer learning using Fourier neural operator},
  author  = {Lyu, Yanfang and Zhao, Xiaoyu and Gong, Zhiqiang and Kang, Xiao and Yao, Wen},
  journal = {Physics of Fluids},
  year    = {2023},
  note    = {arXiv:2304.06972}
}
```

```bibtex
@article{beggs2025pdecond,
  title   = {FiLM-via-LayerNorm Conditioning for Parametric PDE Surrogates},
  author  = {Beggs, et al.},
  journal = {arXiv preprint},
  year    = {2025},
  note    = {arXiv:2509.09599}
}
```

```bibtex
@inproceedings{herde2024poseidon,
  title     = {Poseidon: Efficient Foundation Models for PDEs},
  author    = {Herde, Maximilian and Raonić, Bogdan and Rohner, Tobias and
               Käppeli, Roger and Molinaro, Roberto and de Bézenac, Emmanuel and
               Mishra, Siddhartha},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year      = {2024},
  note      = {arXiv:2405.19101}
}
```
