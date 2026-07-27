# dg_fno — inspiration

DG-FNO unifies the factory's three strongest multi-fidelity ideas as one *gated
operator*. It keeps the Fourier Neural Operator backbone (li2020fno) and the FIRE
decomposition (yu2026fire): a deep ensemble of LF FNOs supplies the low-fidelity
posterior-predictive summary FIELDS (mean, std, quantiles), and the high-fidelity
correction is a residual on top of the LF mean. The novelty is the *injection*. FIRE
(fno_fire_distcond) concatenates those uncertainty fields at the lift; the factory's
leaderboard winner (mf_fno_transfer_film) instead showed that per-block FiLM
modulation (perez2018film; beggs2025pdecond, FiLM-via-norm) beats concatenation for
the global condition vector X. DG-FNO crosses the two: the uncertainty field
modulates every spectral block — Gate A as a per-pixel FiLM affine alongside the
proven global X-FiLM term, and Gate B as a *spectral mode-gate* that scales each kept
Fourier mode of the residual operator by a learned gain derived from the uncertainty's
own spectrum, so the correction's spectral bandwidth opens where LF error is
high-frequency (shocks, boundaries, vortex cores) and stays closed where LF is smooth
and trusted — a modulation that is only meaningful because the operator already lives
in Fourier space. Gate C makes the correction itself heteroscedastic:
`HF = mu_LF + rho(x) * delta`, where `rho(x) in [0, 2]` is a learned spatial gain —
the spatial generalization of the scalar discrepancy gain `rho` in autoregressive
co-kriging (kennedy2000ohagan, `HF = rho * LF + delta`). Every gate is zero-init
(gamma_U = 0, mode-gain = 1, rho = 1), so the operator initializes as an X-FiLM
residual model and grows the gates only where they reduce HF error; the
`DG_GATES` env var toggles each gate for ablation. The learned `rho(x)` doubles as a
discrepancy map: at eval we report its correlation with the true `|HF - mu_LF|` field.

bibtex_keys: li2020fno, yu2026fire, perez2018film, kennedy2000ohagan, beggs2025pdecond

```bibtex
@inproceedings{li2020fno,
  title     = {Fourier Neural Operator for Parametric Partial Differential Equations},
  author    = {Li, Zongyi and Kovachki, Nikola and Azizzadenesheli, Kamyar and Liu, Burigede and Bhattacharya, Kaushik and Stuart, Andrew and Anandkumar, Anima},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2021},
  eprint    = {2010.08895}
}

@article{yu2026fire,
  title   = {FIRE: Distribution-Conditioned Residual Learning for Multi-Fidelity Regression},
  author  = {Yu, and Sung, Nicholas and Ahmed, Faez},
  year    = {2026},
  eprint  = {2601.22371},
  archivePrefix = {arXiv}
}

@inproceedings{perez2018film,
  title     = {FiLM: Visual Reasoning with a General Conditioning Layer},
  author    = {Perez, Ethan and Strub, Florian and de Vries, Harm and Dumoulin, Vincent and Courville, Aaron},
  booktitle = {AAAI Conference on Artificial Intelligence},
  year      = {2018},
  eprint    = {1709.07871}
}

@article{kennedy2000ohagan,
  title   = {Predicting the output from a complex computer code when fast approximations are available},
  author  = {Kennedy, Marc C. and O'Hagan, Anthony},
  journal = {Biometrika},
  volume  = {87},
  number  = {1},
  pages   = {1--13},
  year    = {2000}
}

@article{beggs2025pdecond,
  title   = {FiLM-Conditioned Neural Operators for PDE-Parameter Generalization},
  author  = {Beggs, and others},
  year    = {2025},
  eprint  = {2509.09599},
  archivePrefix = {arXiv}
}
```
