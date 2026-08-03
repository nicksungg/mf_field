# MFFP Autoresearch — Update for Mentor (Round 2 Close)

Date: 2026-08-02. Author: Eloise (with the autoresearch orchestrator).
Authoritative sources: `round2/docs/round2_report.md`, `round2/program.md`, per-experiment cards under `round2/experiment_cards/`.
Companion to the 2026-07-31 update (system setup and round-1 results are described there and are not repeated).

Rendered versions of this update (figures embedded):
[Claude artifact](https://claude.ai/code/artifact/5d16ed1b-c28f-4217-b292-9482250e9d37)
(private until shared from its share menu) ·
[`PROFESSOR_UPDATE_2026-08-02.html`](PROFESSOR_UPDATE_2026-08-02.html) (same page, in-repo).

## TL;DR

- **Round 2 is closed; both success criteria were measured.**
  14 experiment cards across 4 streams (11 scored), closed at the ~3-batch program budget in ~2.5 days; every trained model beat the launch floor anchor (23.0636 panel geomean skill) except one cratered card.
- **Criterion 2 (skill < 1 anywhere) is *excluded by information*, not merely unmet.**
  The diagnostics stream certified training-free aleatoric barriers of ~11.4 (fisher_kpp), ~39–42 (pfc), and ~133 (allen_cahn) skill units for *any* condition→HF model — the per-sample random initial condition simply is not in the condition vector — and the round's own certifier already sits within 1.01–1.14× of those barriers.
- **Criterion 1 (a certified value-of-LF-at-train measurement) was answered in graded form.**
  The auxiliary-target channel is a certified null (15/15 dataset legs, every sample count); the *coverage* channel is positive and CONFIRMED ($+4.68$ skill units on ifc_poisson at 4.99× its floor); final grades on the achievable LF-free control gate: cahn_hilliard = **A** (LF supplies phase: no-LF cosine-with-truth 0.0003–0.0385 vs 0.962–0.964 with LF), ifc = **B** (amplitude), allen_cahn = **C** (tail-borne); fisher/pfc/helmholtz retired.
- **Headline mechanism finding: this panel is *scalar-deep* for condition-only models.**
  After granting a closed-form condition→level law, the leftover residual is worth 40–211× each dataset's certified minimum claimable effect — but has *zero* usable condition reachability, while the paired LF field carries it almost perfectly (fluctuation cosine ≥ 0.997).
  Consistently, a ~150-parameter closed-form head matches a 15.85M-parameter FiLM-FNO decoder on 5/6 panel cells.
- **As in round 1, the most valuable output is benchmark-integrity findings** (§3): the condition vector is incomplete on 4/6 panel datasets, ifc_poisson is affine and its fidelity ladder mispaired, and the generator-side $(r-1)/2$ registration defect now has a complete fix package awaiting review.
- New figures: `round2/docs/figures/error_comparison.png` and `top_models_overview.svg` (both regenerable from cards via `round2/tools/render_*.py`).

## 1. What round 2 asked, and how it ran

**Regime**: models see LF fields only during training; at test they receive the condition vector alone (the stripped data view physically omits test LF — this is the deployment case where a company hands over historical simulation data but no callable solver).
Skill < 1 means *beats actually running the LF solver and copying its output*, under the corrected denominators (registration and wrap-seam fixes landed before any experiment ran; round-1 and round-2 skills are not comparable).

**Scale**: 4 streams (direct decoding / stacked pseudo-LF / LF-as-training-signal / diagnostics), 14 cards, 4 ADRs, 29 reusable probe tools promoted, one hardware tier (H200) for every job.
The protocol was 1 seed in-round adjudicated against a 3-seed certified noise floor (panel minimum claimable effect 1.1419), with seeds 1–2 confirms operator-gated at close.

## 2. Round 2 — results (condition vector → HF; no solver at test)

Final claimable leaderboard (seed 0 unless noted; launch anchor 23.0636):

| Rank | Model | Panel geomean skill (lower = better) | What it is |
|---|---|---|---|
| 1 | r2s2-B1 `frozen` stack | **14.0755** | Condition→pseudo-LF FiLM-FNO emulator feeding the frozen round-1 corrector — but the corrector adds only 0.0061 of it; the value is the emulator, and the ifc column (where most of the gain lives) carries an attribution-validity caveat |
| 2 | r2s3-B3 coverage arm | 17.1150 | LF-at-train coverage; round-best single dataset: **2.150** on ifc_poisson; falsified on draw dispersion |
| 3 | r2s1-B2/B3 closed-form heads | 18.36–18.75 | ~150-parameter out-of-fold-calibrated condition→coefficient heads (the honest baseline class) |
| 4 | **r2s4-B1 certifier (3 seeds, CERTIFIED)** | **19.8178** [19.385, 20.527] | The round's only certified number; supersedes the training-free launch anchor by 3.25 with the whole interval below it |

Headline mechanism results (each backed by a causal probe, not a hunch):

- **One scalar per sample is the whole class headroom.**
  The best deployable move found all round is a closed-form condition→level law: a 9-feature quadratic ridge on allen_cahn's 3-dim condition vector predicts the HF spatial mean to $1-R^2 = 3.4\times10^{-4}$, worth +34.3 skill units = 96.6% of the level oracle = 3.76× the trained CNN's entire gain.
  Beyond that scalar the residual is condition-unreachable — and LF carries it, which is why round 1's corrector worked and no condition-only substitute can.
- **"10 parameters beat 15.85M" is a coordinate statement, not a capacity statement.**
  The big decoder's deficit is one mis-set scalar per dataset (slope 0.954, corr 0.993); a deployable test-label-free subspace surgery closes 94.4% of it.
  The standing headroom is *estimator factorisation* — cahn_hilliard coefficients that look like noise to per-direction maps are 0.92–0.94 predictable from the head's own selected coefficients.
- **Learned intermediate fields are re-parameterisations, not information channels.**
  The best-geomean stack's error is 99.98% stage-1 (emulator) error; the downstream corrector is dead weight without real LF.
- **Where LF's training-time value actually comes from** (the criterion-1 anatomy): coverage (LF rows sit where HF rows don't — irreplaceable, priced at ~10 genuinely labelled HF rows = 3× the round's HF budget) and amplitude calibration; auxiliary-target distillation is a certified nothing.
- **The teacher advantage is condition-invisible realisation information** (exact Shapley over the 5 HF rows, diagnostics stream): the HF rows act as an amplitude-calibration set; 4 of 5 carry *negative* structure value.

Both figures live in `round2/docs/figures/` (regenerate from cards with `tools/render_error_comparison.py` and `tools/render_top_models_overview.py`).

## 3. Benchmark-integrity findings (the part most relevant to the benchmark paper)

- **The condition vector is NOT complete on 4 of 6 panel datasets** (pfc, fisher_kpp, allen_cahn by construction — no initial-condition parameters exist in the vector; cahn_hilliard by measurement).
  Condition→HF is therefore a *stochastic* map there: deterministic models are bounded by the conditional-mean floor and skill→1 is unreachable in principle.
  This is the round's sharpest paper-facing point: a "condition-only" track on this benchmark needs either completed condition vectors or explicitly aleatoric-aware metrics.
- **The frozen floors sit 1.3–4.2× above the aleatoric barriers**, so "beats the best training-free floor" is a weak bar on the stochastic datasets.
- **The generator itself carries the $(r-1)/2$ registration defect** (`mffp_sharp/common/ladder.py` bakes a cell-centred coordinate map into node-sampled aligned arrays, and clamp-extends across periodic seams).
  A complete fix package — patch, verification harness (PASS), sample round, including the measurement that the defect inflates allen_cahn's self-metric gap 3.2–4.7× — is at `mffp_autoresearch/ladder_fix_proposal/`, awaiting Eloise's review then your sign-off; the surface is mentor-owned and nothing has been landed.
- **ifc_poisson is degenerate for this regime**: the HF side is affine (LOO residual $3.2\times10^{-8}$ at every rung; independently confirmed from the LF side), so criterion-2-style claims on it measure rank recovery, not operator learning.
  Its fidelity ladder is additionally *mispaired* (170 LF rows at conditions with no HF row; 0 conditions covered at every rung — two independent audits), invalidating every $hf-lf$, LF-teacher, and copy-LF construction on it.
- **Falsification clauses failed from instrument arithmetic far more often than from model behaviour** (7 independent confirmations across the round) — the codified rules (registration-of-lifts, target-scaler pre-flight, zero-information nulls, matched-procedure arm comparisons, propagation-aware gates) are in the final report §6 and are now program law.
- **Cross-regime comparisons are dominated by the regime, not the model**: on identical held-out rows, raw copy-LF beats the round's fitted condition-only arms by 12–165×.
  Any side-by-side of round-1 and round-2 numbers must carry this caveat on top of the denominator change.

## 4. How the harness itself is performing

- **Throughput**: 14 cards from launch (07-31) to close (08-02), each through the full websearch → pre-registered design → build → adversarial review → GPU run → two-stage analysis pipeline; 29 probe tools promoted for reuse.
- **What the design catches**: the certified-floor + pre-registration discipline turned would-be "wins" into precise negative results (e.g. a falsification clause shown *unpassable by construction* — tolerance set at 0.03–0.11σ of the calibration estimator's own sampling noise); an immutable-rule audit caught and rejected stale analysis partials that had read stripped test LF; a mid-round halt ("fix all bugs that could affect autoresearch") landed integrity repairs between batches with zero result contamination and no retraining.
- **Honest accounting**: the round's best geomean (14.08) is *reported with* its attribution caveat rather than headlined naked; the only number we call certified is the 3-seed 19.8178.
- **Cost of statelessness**: the orchestrator session died and resumed three times, losslessly (state files + append-only cards + SLURM queue as ground truth) — but the close log records ~10 h of idle polling burned against frozen state; polling now dies with the round.

## 5. Gated next steps (in order, each on explicit go)

1. **Seeds 1–2 confirms** for the claimable slate (r2s2-B1, r2s3-B3, r2s1-B2/B3) — not launched at close; fires on explicit go.
2. **`ladder.py` fix package review** — Eloise, then mentor sign-off (generator surface is mentor-owned).
3. **Round-1 2500-epoch full runs** — still on hold (the round-1 s4 gate-relaxation decision remains a prerequisite for s4's slot).
4. **Round-3 direction adjudication** from the recorded-but-not-executed material: the r2s1 two-stage factorised head (pre-measured 18.6787), the r2s2 certified-impossibility-statement question, the r2s3 phase-channel identifiability-vs-trainability question, and a training-free ifc identifiability audit.
