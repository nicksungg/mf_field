# MFFP Autoresearch Round 2 — Final Report

Author: round-2 orchestrator. Date: 2026-08-02 PDT (round closed by operator adjudication 2026-08-03 ~04:1x UTC; Eloise chose "close round, write report" over opening any B4).
Sources: `round2/program.md`, the 14 experiment cards (`experiment_cards/{r2s1_direct,r2s2_stacked,r2s3_lf_train_signal,r2s4_diag}/batch_*/B*.json`), `state/orchestrator_flow.md` (decision log + ADRs), `state/anchors/*.json`, `state/*/current_stage.txt`, `state/maintainer_report.md`, `docs/adr/`.
Round regime (program §1, immutable 9): models predict the HF field from the condition vector alone at test time; LF fields are available only during training (stripped test view — test LF files physically absent).
Scoring (program §2): $\mathrm{skill} = \mathrm{nRMSE}(\text{model}) / \mathrm{nRMSE}(\text{copy-LF})$ under the CORRECTED denominators (ADR r2-0001); lower is better; round-1 numbers are not comparable.
All numbers are seed-0 point estimates judged against the certified panel `min_claimable_effect` 1.1419 (`state/noise_floor.json`), except r2s4-B1/B2 which ran 3 seeds by design; the protocol's end-of-round seeds-1/2 confirms were not launched (operator-gated, see §8).

## 1. Executive summary

Both round success criteria were measured, and — as in round 1 — the round's most important output is a set of benchmark-integrity findings rather than a model.

- **Criterion 2 (skill < 1 on a panel dataset) is EXCLUDED by information argument, not merely unmet.** r2s4-B1 measured training-free aleatoric barriers, in copy-LF skill units, of ~11.44 (fisher_kpp), ~38.6–42.1 (pfc), and ~132.7 (allen_cahn) for ANY condition→HF model; the round's own certifier sits within 1.01–1.14× those barriers (r2s4_diag-B1 part 7; flow 2026-07-31).
  The round's best per-dataset skills (helmholtz 2.815, ifc 2.150) never approached 1.
- **Criterion 1 (a certified value-of-LF measurement) was answered in graded form.** The target-side channel is a certified null: an auxiliary-LF-target head is worth nothing at any $N_{fit} \in [20, 320]$, 15/15 dataset legs (r2s4_diag-B2 part 7). The coverage channel is positive: the matched budget-equal $\pm$LF contrast at $N_{hf} \approx 5$ gives $+4.6794$ skill units on ifc_poisson, 4.99× its floor, card CONFIRMED (r2s3_lf_train_signal-B2 part 6). The final grading against achievable LF-free controls is ch = A (113.5× mce, phase supply), ifc = B (1.41×, amplitude channel, trim-fragile), ac = C (26.9×, tail-borne catastrophe avoidance); fk/pfc/hz retired (r2s3_lf_train_signal-B4, stream stage file).
- **Headline mechanism finding: for condition-only models this panel is scalar-deep.** After granting the closed-form condition→level law, the residual carries 40–211× each dataset's certified mce of oracle value with zero usable condition reachability, while the paired LF field carries it almost perfectly (median fluctuation cosine $\geq 0.997$) — the class headroom is exactly one scalar per sample, and that scalar is free from LF (r2s2_stacked-B3 parts 6–7). Independently, 65.4% of r2s4's ifc error is removable by a per-sample oracle gain vs 0.19% by a global one (r2s4_diag-B4 part 6).
- **Leaderboard**: best scored panel geomean 14.0755 (r2s2-B1) vs the launch anchor 23.0636 (`state/anchors/*.json`); the only certified number is r2s4-B1's 3-seed 19.8178, CI95 [19.385, 20.527].

## 2. Final leaderboard (single-seed except where noted; launch anchor 23.0636, panel mce 1.1419)

| Rank | Card / arm | Panel geomean skill | vs anchor | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | r2s2-B1 `frozen` stack (condition→pseudo-LF → frozen corrector) | **14.0755** | −8.99 | confirmed | stack stage adds only 0.0061 over `emul_only` — the value is the emulator (r2s2-B1 part 6) |
| 2 | r2s3-B3 `A1_lf_cov` (LF-at-train coverage arm) | 17.1150 | −5.95 | falsified (draw dispersion) | round-best ifc_poisson 2.150 |
| 3 | r2s1-B2 closed-form head + Wiener ladder | 18.3622 | −4.70 | falsified | ~150-parameter head |
| 4 | r2s1-B3 out-of-fold-selected head | 18.7500 | −4.31 | falsified (L2 unpassable) | pre-measured, NOT executed B4 two-stage head: 18.6787 |
| 5 | r2s4-B3 `T0` (teacher-projection ledger) | 19.1728 | — | falsified | diagnostic |
| 6 | r2s2-B2 (coherence calibration) | 19.3868 | — | falsified own instruments | diagnostic |
| 7 | r2s1-B1 identifiability-certified decoder | 19.6444 | −3.42 | falsified (0.0444 units = 26× below mce) | 15.85M-parameter FiLM-FNO |
| 8 | **r2s4-B1 certifier (3 seeds, CERTIFIED)** | **19.8178 [19.385, 20.527]** | −3.25 | confirmed | the round's only certified anchor |
| 9 | r2s4-B2 `T0` (3 fold-seeds) | 19.8829 | +0.07 vs 19.8178 | falsified (null-firing F3) | diagnostic |
| 10 | r2s2-B3 retrieval→closed-form + gated corrector | 20.0315 | −3.03 | falsified positive | see §3 |
| 11 | r2s3-B1 multi-rung auxiliary MF loss | 25.3919 | +2.33 | falsified, cratered | shared-scaler defect (see §3) |

r2s3-B2 (3 panel datasets only, by pre-registration) and the training-free diagnostics r2s3-B4 / r2s4-B4 produce no panel geomean.
Every trained model beat the launch anchor except r2s3-B1; none approached skill < 1 anywhere (best per-dataset: helmholtz 2.815 r2s2-B1, ifc 2.150 r2s3-B3, ch 11.279 r2s2-B1, fk 11.574 r2s1-B3, pfc 47.455 r2s2-B1, ac 146.86 r2s1-B3).
Cross-regime caveat (r2s2-B3 part 7): on held-out train rows raw copy-LF beats the round's fitted condition-only arms by 164.9× / 77.0× / 12.3× / 49.5× (ac/ch/fk/pfc) — the no-LF-at-test regime, not architecture, dominates all of these numbers.

## 3. Stream closures (one paragraph each)

- **r2s1_direct (CLOSED at B3, 2026-08-02, operator adjudication)** — Closed at geomean 18.7500 vs anchor 23.0636, at the program's ~3-batch budget.
  The stream's arc: B1's 15.85M-parameter decoder was matched by a ~150-parameter closed-form head on 5/6 panel cells (B2, 18.3622); B3's Bates-Granger falsification was shown UNPASSABLE BY CONSTRUCTION (10/12 blend cells degenerate $\lambda$; tolerance 0.026–0.107$\sigma$ of the calibration estimator's own sampling noise) (r2s1_direct-B3 part 6).
  The standing headroom verdict is **ESTIMATOR FACTORISATION** — not basis width and not an information ceiling: opening the SET gate to all 51 directions makes the panel worse, yet cahn_hilliard's discarded coefficients are 0.92–0.94 predictable from the head's own selected coefficients while appearing as noise to per-direction condition maps (B3 register M-corrections, qualifying B1's COEFFICIENT_UNIDENTIFIABLE verdicts).
  A propagation-aware two-stage closed-form head was pre-measured at panel geomean 18.6787 (ch 11.4148, 0.06× panel mce off the shipped head) but recorded for a future round, NOT executed as B4 (r2s1_direct-B3 part 7; stage file).
  Tools promoted: `head_subspace_surgery.py`, `coefficient_factorisation_audit.py`.
- **r2s2_stacked (CLOSED at B3, 2026-08-02, operator adjudication)** — Closed at 20.0315, a falsified positive: the trained gated corrector did add value, but the value is a per-sample DC recalibration — a scalar regression on the condition vector — that the closed-form LSI stage cannot supply for a structural reason (its DC gain is shared across samples) (r2s2_stacked-B3 part 6).
  The class verdict: headroom beyond the condition→level law is exactly one scalar deep, and that scalar is free from LF (granted-channel residual ladder: 40–211× certified mce of oracle value, zero usable condition reachability, 4/4 decidable; paired-LF fluctuation cosine $\geq 0.997$).
  Part 7 explicitly forbids proposing another condition-only field corrector for this stream; the open question — whether the class's correct next output is a certified impossibility statement — is recorded for a future round, and B4 was not opened.
  Earlier in the stream, B1 delivered the round's best geomean (14.0755) while proving the corrector added nothing (0.0061 units), and B2 falsified its own instruments (all three fired clauses were statistic defects) and stop-exported B1's coherence gate (r2s2_stacked-B2 part 7).
  Tools promoted: `condition_scalar_channel_ladder.py`, `granted_channel_residual_ladder.py`.
- **r2s3_lf_train_signal (CLOSED on B4, 2026-08-01, trigger unfired)** — The round's criterion-1 stream closed CONFIRMED on its terminal card, with the pre-registered B5 trigger unfired and strengthened by the clip finding (ch's apparent 26.9% ceiling absorption is bit-identical to a zero-information constant gain of 0.5) (r2s3_lf_train_signal-B4 parts 6–7).
  The stream's arc: B1 cratered (25.3919) on a shared-scaler instrument defect colliding with ifc's $h^2$ amplitude convention, splitting the verdict into falsified-as-architecture / correct-as-information; B2 repaired three instrument knobs and flipped the same contrast to $+4.6794$ (CONFIRMED, 4.99× floor); B3 completed the panel and was falsified on dispersion — the same amplitude-pinning mechanism that produces LF's effect also produces its draw spread.
  Final grading on the achievable LF-free control gate: ch = A (phase supply — the no-LF arm's median per-sample cosine with truth is 0.0003–0.0385 vs the LF arm's 0.962–0.964), ifc = B (amplitude channel), ac = C (tail-borne: 8–16 of 100 samples carry half the effect); fk/pfc/hz retired with negative $E_{free}$ on all nine draws.
  The transferable finding: LF's signal enters at train time where it does not compete for the empty HF rows, and post-hoc substitution of that signal is priced at ~10 genuinely labelled rows = 3× the round's HF budget (B4 part 6, turn-1 substitution curve; stage file).
  Tools promoted: `gain_head_feasibility_audit.py`, `effect_concentration_audit.py` (+ the zero-information-null standing rule, §6).
- **r2s4_diag (CLOSED at B4, 2026-08-02, operator adjudication; was CLOSE CANDIDATE at 4 batches vs ~3-batch budget)** — The only stream with a certified anchor: `certified_3seed_panel_geomean` 19.8178, CI95 [19.385, 20.527] (r2s4-B1, `state/anchors/r2s4_diag.json`), which superseded the training-free launch anchor 23.0636 by 3.246 with the whole interval below it.
  B1 also measured the aleatoric barriers that exclude criterion 2 (§1); B2 certified the target-side value-of-LF null and killed the auxiliary-target channel; B3's teacher-projection ledger hardened F3 under matched-rows controls (cahn_hilliard's apparent reachable advantage is 72% row asymmetry + 99.2% function-class term).
  B4 — equivalence-bound anatomy on ifc — resolved the falsification as a measurement-units failure (82.1% of the F4 yardstick is a deterministic fold effect, $\leq 3.9$% measurement noise) and established via exact Shapley over the 5 HF rows that the teacher advantage is **condition-invisible realisation information**, bounding all streams; the HF rows act as an amplitude calibration set, four of five carry negative structure Shapley, and the round's ifc mce is an init-replicate scale (r2s4_diag-B4 parts 6–7).
  Tools promoted: `hf_row_shapley_value.py`, `gain_channel_ladder.py`.

## 4. What actually worked (model-side takeaways)

1. **Closed-form condition→coefficient heads are the round's honest baseline class.**
   A ~150-parameter out-of-fold-calibrated head matches or beats a 15.85M-parameter FiLM-FNO decoder on 5/6 panel cells; the single exception (cahn_hilliard, the only 19-dim condition vector) is FACTORISATION_LIMITED, not capacity-limited (r2s1_direct-B2/B3 part 6).
   The measured next step is estimator factorisation (two-stage cross-coefficient expansion, pre-measured 18.6787), not wider bases or bigger decoders.
2. **Condition→pseudo-LF emulation carried the best geomean (14.0755), but the downstream corrector is dead weight.**
   The stack's error is 99.98% stage-1 error on cahn_hilliard; a learned intermediate field is a re-parameterisation of the condition→HF class, never a new information channel (r2s2_stacked-B1 parts 6–7, constraint I8).
3. **The one deployable scalar move: condition→level laws.**
   A 9-feature quadratic ridge on the 3-dim condition vector predicts allen_cahn's HF spatial mean to $1-R^2 = 3.4\times10^{-4}$ and is worth +34.32 skill units = 96.6% of the level oracle = 3.76× the trained CNN's entire gain (r2s2_stacked-B3 part 6).
4. **LF-at-train works through coverage and amplitude, not through auxiliary targets.**
   The repaired coverage arm is the round's best on ifc (2.150); the auxiliary-LF-target head is a certified null at every sample count (r2s3-B2/B3, r2s4-B2).
5. 29 reusable probe tools were promoted to `tools/` across the 14 cards (2–3 per card, indexed).

## 5. Benchmark-integrity findings (for the mentor — the round's most important output)

1. **The condition vector is NOT complete on 4 of 6 panel datasets** (ADR r2-0003, corrected pre-first-card; measured and extended by r2s2-B3): pfc / fisher_kpp / allen_cahn carry no initial-condition parameters (the per-sample random IC lives only in the fields), and the paired-LF cosine measurement extends the incompleteness to cahn_hilliard.
   Condition→HF is therefore a stochastic map there; deterministic models are bounded by the conditional-mean floor, and skill→1 is unreachable in principle.
2. **Criterion-2-style claims are information-theoretically excluded on fisher_kpp / pfc / allen_cahn** for any condition→HF model (aleatoric barriers ~11.44 / ~38.6–42.1 / ~132.7 in copy-LF skill units; the certifier is already within 1.01–1.14× of them) (r2s4_diag-B1 part 7).
   The frozen floors sit 1.3–4.2× ABOVE those barriers, so "beats the best floor" is a weak bar on those datasets.
3. **The generator itself carries the $(r-1)/2$ registration defect**: `mffp_sharp/common/ladder.py` bakes a cell-centred coordinate map into the on-disk `fields_hf` aligned arrays of node-sampled pseudo-spectral fields, and clamp-extends across periodic seams.
   A complete fix package (patch, verification harness, sample round) is at `mffp_autoresearch/ladder_fix_proposal/`, awaiting Eloise review then mentor sign-off — the surface is mentor-owned; nothing has been landed.
4. **Round-level instrument-defect pattern — 7 independent confirmations** (`state/maintainer_report.md`, carried forward across walks): r2s1's post-hoc-blend-stage class (the appended floor-blend stage is not neutral), r2s2-B2's statistic mis-specification (uncentered coherence + biased ceiling), r2s4-B3 turn-2's mis-specified `advantage_reachable`, r2s4-B3 turn-3's self-corrected probe-ordering bug, r2s3-B3's resolved threshold knife-edge, and r2s4-B3's register-turn ledger-contamination and foreign-data zero-field catches.
   The pattern: the round's falsification clauses failed far more often from instrument arithmetic than from model behaviour; §6's rules are the codification.
5. **ifc_poisson is degenerate for this regime**: the HF side is affine (LOO residual $3.2\times10^{-8}$ at every rung, r2s3-B1) and the LF side independently confirms it (r2s2-B1), so ifc criterion-2-style claims measure rank recovery, not operator learning (flow, round-report item).
   Additionally the ladder is MISPAIRED: 170 LF rows sit at conditions carrying no HF row, and 0 conditions are covered at every ifc rung — the same truncation defect invalidates every $hf - lf$, LF-teacher, and copy-LF construction on it (r2s4-B2 + r2s3-B2 part 7, two independent audits).
6. **Cross-regime skill comparisons are dominated by the regime, not the model** (r2s2-B3 part 7): raw copy-LF beats the round's fitted condition-only arms by 12–165× on identical held-out rows.
   Any side-by-side of round-1 and round-2 numbers must carry this, on top of the denominator change.
7. **The certified mce on ifc is an init-replicate scale, not a model-difference scale** (r2s4-B4 part 6): the 3-init max-min range across 31 designs has median 0.938 — essentially the certified `min_claimable_effect` itself — so single-seed per-dataset deltas near 1 mce on ifc are init noise.

## 6. Methodological rules established this round

- **Registration-of-lifts rule** (ADR r2-0004, program §12): any code that resamples a field between grids must use the ADR r2-0001 per-dataset conventions (`eval/panel_data.py` interpolators or `models/_common/lf_registration.py`); a bare `F.interpolate`/`zoom` on a panel dataset is a reviewer FAIL.
- **Target-scaler pre-flight** (program §12): any card training on helmholtz or pfc runs `tools/target_scale_spread_audit.py`; `OUTLIER_DOMINATED` / `NEAR_ZERO_TARGETS` requires per-sample target normalisation or a recorded justification.
- **Zero-information-null publication rule** (r2s3-B4 part 7): any card that gates on a diagnostic number must publish the score of the zero-information version of the same instrument next to it — three of B4's readings were shaped by the instrument, not the data.
- **"Unidentifiable" phrasing rule** (r2s1-B3 part 7, standing correction): a low per-mode out-of-fold $R^2$ of condition→coefficient licenses only "unidentifiable BY THIS MAP FAMILY, at this condition dimension and this row count" — the round measured coefficients invisible to per-direction maps that were 0.92–0.94 predictable through factorisation.
- **Three-channel value-of-LF taxonomy** (r2s3-B2 part 7): every "LF helped by X" claim must name the channel — (i) direction supply (irreplaceable), (ii) row-space fit, (iii) level/amplitude (not evidence about LF at all); `tools/null_family_ceiling_audit.py` computes all three from prediction dumps.
- **Support-not-identifiability rule** (r2s4-B2 part 7): the sample-size regime is set by condition-space support, predictable training-free from the LOO-kNN identifiability index and $d_{min}$.
- **Propagation-aware gates for two-stage heads** (r2s1-B3 part 6, F25): stage-2 gates must be selected AND fitted on out-of-fold stage-1 predictions — the true-input gate costs helmholtz 2.35 skill units.
- **Arm-comparison mis-specification warning** (r2s4-B3 part 7): skill differences between arms produced by different estimation procedures silently sum a function-class term with the effect of interest; compare at matched rows and matched procedure.
- **Stop-export** of r2s2-B1's coherence eligibility gate (r2s2-B2 part 7: COARSE + PANEL_INCONSISTENT + MISCALIBRATED — its 0.05 relative-gain floor is 10–817× the certified mce).

## 7. Process findings (harness)

- **14 cards over 4 streams, 4 batches maximum, closed inside the ~3-batch budget per stream** (r2s4 ran 4 as the round's certification/diagnosis stream; r2s3's B4 was training-free).
  The 1-seed-in-round protocol plus the certified panel mce 1.1419 adjudicated every claim; no round-2 seeds-1/2 confirm was needed in-round.
- **The whole round ran on one hardware tier** (ADR r2-0004 hardware: `gpu:nvidia_h200:1`, switched from a week-long h100 queue before any number was produced; zero jobs ran on h100).
- **Operator halt discipline worked**: the 2026-08-01 halt ("fix all bugs that could affect autoresearch") produced the between-batch integrity repairs (ADR r2-0004 repairs: `lf_registration.py` dispatch across nine `_to_grid` families, assert-don't-default on unliftable families) with no experiment running and no frozen number altered — results uncontaminated, no retraining.
- **Immutable-9 enforcement caught a real leak**: stale killed-agent turn-3 partials for r2s2-B3 had read unstripped test LF; they were rejected and re-derived on the held-out train fold with `_no_test_lf_read=true` (flow 2026-08-02 ~15:3x).
- **The WebFetch "disabled" incident is a summary-fidelity lesson, not a tooling lesson** (flow 2026-08-02): a context-mode PreToolUse hook began intercepting WebFetch mid-round (~16 h window, after ~87 successful calls); the leaf agent diagnosed the redirect correctly, but the upward summary compressed it to "WebFetch disabled" and that shorthand propagated as fact.
  All 4 affected agent registrations were fixed (ctx tools added, curl workaround forbidden); retrieval content needed no re-run.
- **Session mortality is the dominant infra hazard, again**: the orchestrator restarted three times; state-file discipline (stage tags, cards, flow log) made every resume lossless, but the closing entry records ~10 h of idle polling pulses burned against frozen state — polling crons must die with the round.

## 8. End-of-round protocol (operator-gated, in order)

1. Freeze the single-seed leaderboard (§2) — done in this report; the only certified number remains r2s4-B1's 19.8178 [19.385, 20.527].
2. On Eloise's go: seeds 1–2 confirms for the claimable slate (the cards carrying `proceed_to_seeds_1_2`: r2s2-B1, r2s3-B3, r2s1-B2/B3) per the round protocol "1 seed in-round + seeds 1,2 at end-of-round confirm" — **not launched at close**.
3. **`ladder.py` generator-fix proposal**: package at `mffp_autoresearch/ladder_fix_proposal/` (PROPOSAL.md, `ladder_fix.patch`, verification harness + results, sample round) — awaiting Eloise review, then mentor (Nicholas) sign-off; the generator surface is mentor-owned and nothing has been landed.
4. **Round-1 2500-epoch full runs** — still ON HOLD per operator (gated since 2026-08-01; the round-1 s4 gate-relaxation decision remains a prerequisite for s4's slot).
5. Figure/artifact regeneration (dispatched at close, flow 2026-08-03): `tools/render_error_comparison.py` + top-models overview from card JSONs only; then PROFESSOR_UPDATE in the round-1 form (operator-requested), a fact-check pass over this report, and a one-shot auto-sync.
6. **Recorded future-round material (explicitly not executed this round)**:
   the r2s1 B4 candidate — propagation-aware two-stage closed-form head, pre-measured panel geomean 18.6787 plus 2 recipe repairs (fit-set-symmetric blend bases; tolerances priced against the audited statistic's own sampling error);
   the r2s2 open question — whether a certified impossibility statement is the condition-only class's correct next output;
   the r2s3 open question — ch identifiability-vs-trainability (is the phase channel undetermined by 5 rows + 19 dims, or unfound by optimisation);
   the r2s4 option — a training-free ifc identifiability audit (warranted only if training-free; anatomy sweeps are pre-priced).
