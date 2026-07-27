# dg_transfer — inspiration

`dg_transfer` is the corrective follow-up to `dg_fno`. The full-benchmark verdict on
`dg_fno` was that the discrepancy gates (spatial FiLM + spectral mode-gate) genuinely
improve over plain FIRE and that the learned gain field provably locates the LF→HF
error — but they sat on the FIRE *residual* decomposition (`HF = mu_LF + rho*delta`),
which is itself ~1.4× behind the transfer-learning branch and blows up on the Poisson
scale-collapse datasets (`ifc_poisson` ≈ 14.5 rel-L2). The gates were on the wrong
backbone. This family moves them onto the right one.

The backbone is `mf_fno_transfer_film` (li2020fno + perez2018film FiLM, with the
lyu2023mffno LF→HF transfer schedule), the current benchmark #1: a single FNO,
FiLM-conditioned on the parameter vector X, pretrained on abundant low-fidelity data
and fine-tuned on scarce high-fidelity data, with a SEPARATE output scaler per stage
(`scaler_lf`, then `scaler_hf`). That per-stage re-scaling is exactly what lets
transfer dodge the Poisson collapse, so it is kept verbatim. On top of it we add the
FIRE uncertainty signal (Yu, Sung & Ahmed 2026, arXiv:2601.22371): a small LF ensemble
produces per-pixel summary fields [mu, sigma, q10, q50, q90], and those modulate every
block of the transfer network through two zero-init gates — Gate A, a per-pixel spatial
FiLM affine added to the proven global X-FiLM term, and Gate B, a spectral mode-gate
that scales each retained Fourier mode by a learned gain from the uncertainty's own
spectrum. The residual gain (Gate C of `dg_fno`) is intentionally dropped: this network
predicts the HF field directly, so there is no `mu_LF` residual to gate. Because both
gates are zero-init, the network initializes byte-for-byte as `mf_fno_transfer_film`
and grows the uncertainty conditioning only where it lowers HF error — it cannot
regress below #1. The LF ensemble is kept deliberately small (E=3, hidden 32) so the
parameter budget stays near the 4.77M transfer backbone rather than the 28M FIRE
ensemble. Hypothesis: the same conditioning signal that helped on the FIRE residual
will help more on the stronger transfer backbone, since it no longer has to overcome
the residual decomposition's Poisson weakness.

bibtex_keys: li2020fno, perez2018film, lyu2023mffno, yu2026fire

```bibtex
@inproceedings{li2020fno,
  title     = {Fourier Neural Operator for Parametric Partial Differential Equations},
  author    = {Li, Zongyi and Kovachki, Nikola and Azizzadenesheli, Kamyar and Liu, Burigede and Bhattacharya, Kaushik and Stuart, Andrew and Anandkumar, Anima},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2021},
  eprint    = {2010.08895}
}

@inproceedings{perez2018film,
  title     = {FiLM: Visual Reasoning with a General Conditioning Layer},
  author    = {Perez, Ethan and Strub, Florian and de Vries, Harm and Dumoulin, Vincent and Courville, Aaron},
  booktitle = {AAAI Conference on Artificial Intelligence},
  year      = {2018},
  eprint    = {1709.07871}
}

@article{lyu2023mffno,
  title   = {Multi-fidelity prediction of fluid flow based on transfer learning using Fourier neural operator},
  author  = {Lyu, Yanfang and Zhao, Xiaoyu and Gong, Zhiqiang and Kang, Xiao and Yao, Wen},
  journal = {Physics of Fluids},
  year    = {2023},
  eprint  = {2304.06972}
}

@article{yu2026fire,
  title   = {FIRE: Distribution-Conditioned Residual Learning for Multi-Fidelity Regression},
  author  = {Yu, and Sung, Nicholas and Ahmed, Faez},
  year    = {2026},
  eprint  = {2601.22371},
  archivePrefix = {arXiv}
}
```
