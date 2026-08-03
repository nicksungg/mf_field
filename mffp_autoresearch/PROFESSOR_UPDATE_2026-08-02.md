# MFFP Autoresearch — Update for Mentor (Round 2 Close)

Date: 2026-08-02. Author: Eloise (with the autoresearch orchestrator).
Updated 2026-08-03: the benchmark-repair pipeline described in §3 has since been executed end-to-end (operator-approved); §6 records what was done and verified.
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
- **As in round 1, the most valuable output is benchmark-integrity findings** (§3): the condition vector is incomplete on 3/6 panel datasets (corrected 2026-08-03 from 4/6), ifc_poisson is affine and its fidelity ladder mispaired, and the generator-side $(r-1)/2$ registration defect had a complete fix package.
  *As of 2026-08-03 both fixes are landed and the affected datasets regenerated — see §6.*
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

- **The condition vector is NOT complete on 3 of 6 panel datasets** (pfc, fisher_kpp, allen_cahn — no initial-condition parameters exist in the vector; the per-sample IC is white noise drawn from an unexported seed).
  Condition→HF is therefore a *stochastic* map there: deterministic models are bounded by the conditional-mean floor and skill→1 is unreachable in principle.
  This is the round's sharpest paper-facing point: a "condition-only" track on this benchmark needs either completed condition vectors or explicitly aleatoric-aware metrics.
  *Correction 2026-08-03 (this update originally said 4 of 6):* cahn_hilliard was wrongly folded in. Its IC is built from its own condition vector, and re-solving from `x` alone reproduces the on-disk field to rel-L2 $1.7\times10^{-14}$ (control 1.346) — the vector is complete, and what was measured there is the support limit of 400 rows in 19 dimensions (closest training pair at standardized distance 2.82). Certificate and fix package: `mffp_autoresearch/condition_completeness_proposal/`.
  The root cause on the other three is a code-path split, not a design choice: the identical bug was fixed on 2026-06-28 in a standalone script (`generate_learnable.py`, 9 variants regenerated) rather than in the `mffp_sharp` package, so datasets generated later through the package path silently reproduced it.
  *Status 2026-08-03: fixed at the package level (IC coefficients drawn in the Latin-hypercube design and exported in `cond`; a training-free completeness certificate now runs as a generation gate and is written into every `meta.json`), and the affected variants regenerated through the fixed path — §6.*
- **The frozen floors sit 1.3–4.2× above the aleatoric barriers**, so "beats the best training-free floor" is a weak bar on the stochastic datasets.
- **The generator itself carries the $(r-1)/2$ registration defect** (`mffp_sharp/common/ladder.py` bakes a cell-centred coordinate map into node-sampled aligned arrays, and clamp-extends across periodic seams).
  The fix package — patch, verification harness (PASS), sample round, including the measurement that the defect inflates allen_cahn's self-metric gap 3.2–4.7× — is at `mffp_autoresearch/ladder_fix_proposal/`.
  *Status 2026-08-03: Eloise approved the package under operator authority (mentor sign-off waived — `condition_completeness_proposal/APPROVAL.md`); the patch is landed (per-PDE node conventions in `assemble_sample`, commit `c29c269`), and the acceptance verification was re-run on the cluster against the landed code: VERDICT PASS, byte-identical results.*
- **ifc_poisson is degenerate for this regime**: the HF side is affine (LOO residual $3.2\times10^{-8}$ at every rung; independently confirmed from the LF side), so criterion-2-style claims on it measure rank recovery, not operator learning.
  Its fidelity ladder is additionally *mispaired* (170 LF rows at conditions with no HF row; 0 conditions covered at every rung — two independent audits), invalidating every $hf-lf$, LF-teacher, and copy-LF construction on it.
  *Status 2026-08-03: confirmed on-disk — every rung pair shares 0 condition rows, and the same measurement shows `ifc_heat` (a guard dataset) is mispaired the same way (preflight row-match 0.2 / 0.4 respectively).*
  *Both are local IFC-protocol replicas of `generate_all_datasets.py` solvers, so a faithful repaired ladder was regenerated with nested conditions (preflight row-match 1.0) and staged at `mffp_autoresearch/ifc_pairing_repair/`; whether it replaces the shipped ladder on the round-3 panel is a launch-ADR decision.*
- **Falsification clauses failed from instrument arithmetic far more often than from model behaviour** (7 independent confirmations across the round) — the codified rules (registration-of-lifts, target-scaler pre-flight, zero-information nulls, matched-procedure arm comparisons, propagation-aware gates) are in the final report §6 and are now program law.
- **Cross-regime comparisons are dominated by the regime, not the model**: on identical held-out rows, raw copy-LF beats the round's fitted condition-only arms by 12–165×.
  Any side-by-side of round-1 and round-2 numbers must carry this caveat on top of the denominator change.

## 4. How the harness itself is performing

- **Throughput**: 14 cards from launch (07-31) to close (08-02), each through the full websearch → pre-registered design → build → adversarial review → GPU run → two-stage analysis pipeline; 29 probe tools promoted for reuse.
- **What the design catches**: the certified-floor + pre-registration discipline turned would-be "wins" into precise negative results (e.g. a falsification clause shown *unpassable by construction* — tolerance set at 0.03–0.11σ of the calibration estimator's own sampling noise); an immutable-rule audit caught and rejected stale analysis partials that had read stripped test LF; a mid-round halt ("fix all bugs that could affect autoresearch") landed integrity repairs between batches with zero result contamination and no retraining.
- **Honest accounting**: the round's best geomean (14.08) is *reported with* its attribution caveat rather than headlined naked; the only number we call certified is the 3-seed 19.8178.
- **Cost of statelessness**: the orchestrator session died and resumed three times, losslessly (state files + append-only cards + SLURM queue as ground truth) — but the close log records ~10 h of idle polling burned against frozen state; polling now dies with the round.

## 5. Gated next steps (in order, each on explicit go — status as of 2026-08-03)

1. **Seeds 1–2 confirms** for the claimable slate (r2s2-B1, r2s3-B3, r2s1-B2/B3) — superseded by the repair pipeline: the slate is being re-scored at 3 seeds *on the repaired panel* (§6), which is both the confirm and round 3's certified launch anchor (PROGRAM_NOTE §7.4).
2. **`ladder.py` fix package review** — DONE: approved by Eloise under operator authority (mentor gate waived), landed, verification PASS (§3, §6).
3. **Round-1 2500-epoch full runs** — still on hold (the round-1 s4 gate-relaxation decision remains a prerequisite for s4's slot).
4. **Round-3 direction adjudication** from the recorded-but-not-executed material: the r2s1 two-stage factorised head (pre-measured 18.6787), the r2s2 certified-impossibility-statement question, the r2s3 phase-channel identifiability-vs-trainability question, and a training-free ifc identifiability audit.
   Round 3's remaining launch prerequisites are listed in `round3/PROGRAM_NOTE.md` §7: panel-composition ADR (helmholtz / ifc / pfc / fisher_kpp), then operator go.

## 6. Repair pipeline execution (2026-08-03, cluster)

Everything in this section ran under the operator approval recorded in `condition_completeness_proposal/APPROVAL.md`; each step was verified against the artifact it produced, and old data was archived, never deleted (round-2 numbers remain reproducible against `_incomplete_backup_2026-08-03/`).

- **Both generator fixes are landed at the package level.**
  IC-encoding: every stochastic-IC PDE now draws its IC coefficients in the Latin-hypercube design and exports them in `cond` (`ic_c0…`); per-module tests pin the field as a function of the exported condition alone (149 passed, 9 skipped).
  Registration: `ladder.py` dispatches per-PDE node conventions (`node_periodic` / `node_dirichlet` / `cell_centered`), raising on unclassified PDEs; acceptance verification re-run on the cluster reads PASS with byte-identical results.
- **A training-free completeness certificate now gates generation.**
  `certify`-style reconstruction (rebuild the IC from `x`, re-solve, compare) runs at the end of every generation and is written into `meta.json` as `condition_completeness`; INCOMPLETE hard-fails the job unless the dataset explicitly declares stochastic-map semantics.
- **The audit heuristic was adjudicated by the certificate, not by pattern.**
  Sweeping every other benchmark variant for the defect class flagged three extension-tree datasets (`ext/cahn_hilliard_2d`, `ext/gray_scott_2d`, `ext/kuramoto_sivashinsky_1d`); all three *reconstruct exactly* (rel-L2 = 0.0) from their stored condition vectors — deterministic ICs, no defect — so no further regeneration was needed.
  (KS fails the nearest-pair witness by chaotic amplification while passing reconstruction — a good example of why the reconstruction certificate, not the witness, is the decisive test.)
- **The mispaired ifc ladders have a staged repair** (§3): nested-condition regeneration through the local solvers, preflight pairing row-match 1.0 vs the shipped 0.2/0.4; panel adoption is a round-3 launch-ADR decision.
- **All five affected sharp variants are regenerated and swapped in.**
  `phase_field_crystal_2d`, `fisher_kpp_2d` (final recipe $T=0.30$), `allen_cahn_2d` (final recipe $\varepsilon$ coupled to the ladder, $T=10$), plus the 1-D pair — every certificate reads COMPLETE at reconstruction rel-L2 = 0.0, cluster metas matching the committed finals to floating-point rounding.
  Old data is archived (never deleted) in `_incomplete_backup_2026-08-03/`, so every round-2 number remains reproducible against the panel it was measured on.
- **Preflight now passes on the repaired panel** (report archived in `round3/state/`), with two instrument false-positives adjudicated by decisive tests before waiving: helmholtz's completeness flag (resonance sensitivity — re-solving from the condition vector reproduces the flagged rows at rel-L2 ~1e-15) and sod's pairing flag (near-duplicate Riemann rows — the ladder's condition arrays are bit-identical across levels).
- **The 3-seed anchor re-score of round 2's claimable slate is running on the repaired panel** (12 GPU jobs), against freshly recomputed copy-LF denominators (round-2 denominators archived).
  One consequence worth flagging now: fisher_kpp's copy-LF reference collapsed 130× under the complete IC (LF ≈ HF), so skills on the regenerated datasets are not comparable to round-2 skills — these runs measure how much of round 2's story survives the data fix, which is exactly their purpose.
- **A same-day hardening pass closed the gate's own blind spots** (found by the condition-completeness briefing, executed under the same approval):
  the certificate now carries a witness veto whose threshold scales with the dataset's own pair-distance scale, plus a two-scale continuity probe that tells a genuine coefficient from an exported RNG seed (a smooth map's response halves when the probe step halves; a seed's does not) — so the illegitimate "export the seed" shortcut can no longer certify COMPLETE;
  the briefing-prescribed repo-wide sweep found a **fourth occurrence** of the defect class (`burgers_param`: per-sample IC phases consumed but never exported), repaired in place without re-solving by re-deriving the phases from the generation seed — post-retrofit, all 500 rows reconstruct from the condition vector at rel-L2 = 0.0;
  and the flagged extension-tree Cahn-Hilliard was adjudicated complete at the artifact level (one shared IC realization; documented, and its batch-order-dependent seeding bug fixed).
- Round 3 is **not** launched; its remaining prerequisites (panel-composition ADR for helmholtz / ifc / pfc / fisher_kpp, operator go) are §5.4.
