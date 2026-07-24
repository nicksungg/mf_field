# Researcher Agent Output

- **timestamp:** 2026-06-02T21:21:09Z
- **exit_code:** 0

---

Cycle-010 Mode 4 research report written to `.factory/strategy/research.md`.

**Top-line synthesis:**

- **H1 (LEAD, capacity-axis second step on `fno_mf_stack`):** `hidden=96, modes_per_level=(4,8,16,24), n_blocks=4` — touches only `smoke_eval.py:39-55` SMOKE_DEFAULTS. Cycle-009's −36% Poisson at the first capacity step → realistic −10 to −22% Poisson here (composite −5 to −11%). NK-clear. **HIGH confidence.**

- **H2 (SECONDARY, NK2-carve-out curriculum on `fno_mf_stack`):** Lyu-style two-stage LF→HF with **frozen LF stack** in stage 2 (per `yang2025mfdeeponet`'s freeze pattern), `pretrain_frac=0.40`, fresh `Adam @ 3e-4` + fresh cosine scheduler at the transition. Justified by the LF/HF-independent design (4 separate `SmallFNO` modules) that NK2 explicitly carved out. **MUST land as separate PR from H1.** **MEDIUM-HIGH confidence.**

- **H3 (RESERVE), O4 (DEFER):** Composite-mover prior is weak for non-leader-cell fixes; defer the new `fno_coreg_conditioned_v2` family until H1/H2 plateau.

**Cross-cycle pattern (load-bearing for H1 calibration):** Cycle-009 H1+H2 went 250k → 1.0M params and dropped Poisson 36%; slope ≈ −0.39 in log-params. Second 2× step (1.0M → 2.0M) at the same slope predicts −27%; literature saturation evidence flattens this to realistic −10 to −22%. There is still capacity-axis runway, but cycle-011 is likely diminishing returns.

**New citations validated (5 new + 1 corrected ID):** `mutransferfno2025` (arXiv:2506.19396), `ufnofilm2025` (arXiv:2511.20543), `pirino2025` (arXiv:2510.23810), `fnospectralperspective2024` (arXiv:2404.07200), `mfbpinn2026` (arXiv:2602.01176), `liu2022neuralcoreg` (arXiv:2109.09261). Total ready-keys: 15.
