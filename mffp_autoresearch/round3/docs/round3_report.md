# MFFP Autoresearch Round 3 — Final Report

Author: round-3 orchestrator. Date: 2026-08-12 PDT (round closed 2026-08-12 with all 10 cards `complete`; operator (Eloise) gave the round-close go).
Sources: `round3/program.md`, the 10 experiment cards (`experiment_cards/{r3s1_factorised,r3s2_field_reach,r3s3_lf_value,r3s4_audit}/batch_{1,2}/B{1,2}.json` + `{r3s2_field_reach,r3s3_lf_value}/batch_3/B3.json` — parts 5/6/7 are the adjudicated record), `state/orchestrator_flow.md` (decision log), `state/gates.md`, `state/anchors/*.json`, `state/anchors_repaired/noise_floor.json`, `state/batch3_scope_2026-08-10.md`, `docs/adr/0001–0007`, `index.md` (maintainer dashboard), `tools/index.md`.
Round regime (program §1, unchanged from round 2): models predict the HF field from the condition vector alone at test time; LF fields are available only during training.
What changed at launch: every scored dataset is completeness-certified — the HF field is exactly reconstructible from the stored condition vector — so round 2's "the IC was never exported" excuse is gone, and internal IC reconstruction from the condition is explicitly in scope.
Scoring (program §2): $\mathrm{skill} = \mathrm{nRMSE}(\text{model}) / \mathrm{nRMSE}(\text{reference})$, lower is better, panel geomean; the reference is copy-LF for batch-1/2 registrations and the certified film-transfer baseline for batch-3 registrations (ADR r3-0006; $\mathrm{skill}_{film} = \mathrm{skill}_{copyLF} \times c_{ds}$, exact per-dataset constants in `state/anchors/film_denominator.json`).
**Units are never silently mixed in this report**: batch-1/2 numbers are copy-LF units on the ADR r3-0004 5-dataset panel (allen_cahn, fisher_kpp, cahn_hilliard, ifc_poisson, ifc_heat); batch-3 numbers carry their registration era (r3s3-B3 in film units on the ADR r3-0007 scored panel; r3s2-B3's 6-cell panel and 5-cell anchor-comparand each labelled).
All claims were adjudicated at 3 seeds in-round (PROGRAM_NOTE MUST #4), against the certified noise floor installed 2026-08-10 (`state/anchors_repaired/noise_floor.json`, `_provisional:false`, from r3s4-B1's certification).

## 1. Executive summary

Round 3 asked two questions on the completeness-repaired panel and answered both — and, for the third round running, its most consequential outputs include benchmark-integrity findings alongside the science.

- **Criterion 1 (field reachability) closed in graded form.** The complete condition vector demonstrably pays, but at stage 1 only: exact IC information improves the condition→LF emulator by 3.1× (allen_cahn), 1.3× (cahn_hilliard) and 8.0× (fisher_kpp) with the zero-information null worse everywhere (r3s2-B1 F1 confirmed), and the two-stage factorised head beats the matched one-stage law by $+0.5546$ $[0.5246, 0.5747]$ skill units, attributable entirely to cahn_hilliard (r3s1-B1 confirmed).
  Nothing downstream converts that into field-level structure: the corrector's value is unresolvable at 9–163× below one mce (r3s2-B1 F2), and the emulator-ceiling card proved $\rho \approx 0$ is a **scalar identity** — $\mathrm{nRMSE}(R_1) \approx \mathrm{nRMSE}(R_0) \approx$ the stage-1 emulator's own held-out LF error (log-log slopes 1.035 / 1.004, $r$ = 0.998 / 0.988), with the corrector transmitting stage-1 error at unity gain (0.80–1.02 on 6/6 cells) and the failure concentrated at LOW wavenumber (86–99.8% of the error in the lowest $k$-eighth) — retiring the "sharp small-scale detail" narrative for this route (r3s2-B3 confirmed).
- **Criterion 2 (value of LF-at-train) is answered with a mechanism.** LF's value on the honest panel is ENTIRELY the supply of distinct condition rows: $E_{cov}/E_{total} \in [0.972, 1.024]$ on 30/30 cells, and the covered-conditions arm is behaviourally identical to the no-LF arm — an identifiability result, not regularisation (r3s3-B1 confirmed, 11.0789).
  The coverage channel has a knee (cahn_hilliard $c^* = 80$, r3s3-B2 confirmed) which is the sample-complexity elbow of the condition→field regression itself — reproduced training-free by a kernel ridge at Pearson 0.984 — but the surrogate's knee predictions do NOT transfer: both adjudicable predictive cells missed by 6–19× $\tau_{rel}^{film}$ on every seed while the instrument control hit, because the surrogate is the learning curve of a *different learner* (r3s3-B3 falsified).
- **The round's orientation pivoted mid-course to the best LEARNED baseline** (operator directive 2026-08-10; ADR r3-0006): the film-transfer factory champion replaces copy-LF as the reporting denominator (its own panel value = 14.0770 in copy-LF units on the batch-1/2 panel).
  Film-denominated, batch 1 splits cleanly: r3s3 0.79 and r3s2 0.92 BEAT the learned baseline; r3s4 1.40 and r3s1 1.77 lose to it; the best training-free floor converts to 2.45.
  Batch 3 extends the beats-film set: r3s3-B3's arm scores 0.5780 film units $[0.5606, 0.5897]$ — the round's best learned result against the learned baseline — even though its registered knee claim was falsified.
- **Best certified learned number in copy-LF units: 10.0853** $[9.7249, 10.3528]$ (r3s2-B2, certified stream anchor), 5.65× the certified panel seed-mce below its B1 predecessor; its B3 replication landed at $+0.3910$ = 0.77× seed-mce (not resolvable, as pre-registered).
- **Two stop-the-line events fired and were repaired without contaminating any frozen number**: the pfc scored-cell task-void finding (rung-convention mismatch; ADR r3-0004 report-only → ADR r3-0005 spectral-rung repair, pfc restored to the scored panel) and the stale-checkpoint anchor contamination (14 anchor legs re-scored on repaired data with pre-repair weights; quarantined, fresh-trained, and permanently instrumented — the checkpoint↔data binding gate that batch 2 then priced at 108/108).
- **Panel composition remained the round's live methodological question**: ADR r3-0007 (operator option C) demoted exactly-affine ifc_poisson to report-only mid-round, and the batch-3 evidence for the still-open panel-composition ADR is collected in §12.

## 2. Final leaderboard (3-seed means with CI95; units and panel era stated per row)

Cross-era comparisons are not licensed: batch-1/2 cards registered on the ADR r3-0004 5-dataset panel in copy-LF units; batch-3 cards registered post-ADR r3-0005/0006/0007 (per-entry `_copylf_def_hash` enforces cache-level separation).
Film-unit cells are quoted only where they exist on a primary record (the ADR r3-0006 flow entry for batch 1; card part 5 for r3s3-B3); no conversion is computed for this report.
Convention note (mandatory, ADR r3-0007 check record): `film_denominator.json` ifc rows are AGGREGATE nRMSE while the ifc floor records are per-sample-mean rel-L2 (~1.27× cross-file bias on ifc_heat); this table quotes card-adjudicated skills throughout and never mixes the two file conventions.

Ranks are assigned WITHIN an era only; the two era tables below share no ordinal scale (the panel compositions differ, so a single cross-era rank column would assert exactly the comparison the paragraph above disclaims).

**Batch-1/2 era (ADR r3-0004 5-dataset panel, copy-LF units):**

| Era rank | Card / arm | Panel geomean skill | Film units | Verdict | Notes |
|---|---|---|---|---|---|
| 1 | **r3s2-B2 repaired-corrector stack (CERTIFIED stream anchor)** | **10.0853** [9.7249, 10.3528] | — | falsified-via-G2(iii) | affirmative route; new stream anchor, beats B1 by 2.8704 with the whole interval below it |
| 2 | r3s3-B1 coverage-decomposition arm | 11.0789 [10.8445, 11.2471] | 0.79 | confirmed | vs repaired anchor −0.81% = 0.079× noise floor, not resolvable |
| 3 | r3s2-B1 IC-synthesis stack | 12.9556 [10.3180, 17.8277] | 0.92 | falsified (F2) | F1 reach effect confirmed; wide CI is the deterministic ifc_poisson seed-2 blow-up (2.04 vs 0.15) |
| 4 | **r3s4-B1 certifier (3 seeds, CERTIFIED noise floor)** | 19.6438 [19.4235, 19.9318] | 1.40 | falsified (metrology-limited F1) | the round's measurement stick; F2/F3/F4 confirm |
| 5 | r3s1-B1 two-stage factorised head | 24.9573 [24.8726, 25.0662] | 1.77 | confirmed | one-cell effect (cahn_hilliard); L3 adjudicated VOID (enumerates pfc) |
| 6 | r3s1-B2 cap-lift + predictive criterion (`A2_predcrit`) | 25.1243 [24.9477, 25.2757] | — | falsified (L2 panel + L3 novelty; L1 cell confirmed) | reported per its own clause as the SELECT_MAX bug-fix, no novelty claim |
| — | r3s3-B2 coverage-knee ladder | no panel claim (2-ds diagnostic geomean [0.8898, 1.0040, 0.9508]) | — | confirmed | knee $c^* = 80$; training-free surrogate; pre-registered as diagnostic-only |
| — | r3s4-B2 checkpoint-binding pricing | no panel cells by design (0/0) | — | falsified (3rd conjunct G5 only) | G1 confirmed 108/108; G5 seam adopted by operator 2026-08-10 |

**Batch-3 era (post ADR r3-0005/0006/0007; clauses registered in film units) — UNRANKED: the two rows quote different 5-dataset compositions (the anchor-comparand subset includes ifc_poisson; the ADR r3-0007 scored panel includes pfc instead) and cannot be ranked against each other:**

| Card / arm | Panel geomean skill | Film units | Verdict | Notes |
|---|---|---|---|---|
| r3s2-B3 emulator-ceiling arm, 5-cell anchor-comparand | 10.4763 [10.3176, 10.7785] (anchor subset, era-matched to the anchor by construction) | — | confirmed | does NOT beat the 10.0853 anchor ($\Delta$ +0.3910 = 0.77× seed-mce, pre-registered replication); 6-cell panel 14.1909 [14.0046, 14.5243]; subset audit: see below |
| r3s3-B3 knee-prereg arm | 18.6212 [18.0610, 18.9994] (r3-0007 scored 5-ds) | **0.5780** [0.5606, 0.5897] | falsified | round-best vs the learned baseline (film units, its card's own record); the registered knee claim still failed (see §3) |

Anchors and baselines on file: launch best-floor geomean **53.2146** on the ADR r3-0007 5-dataset scored panel (lineage 75.0673 → 38.6300 → 36.3912 → 34.4198 → 38.8368 → 53.2146, `state/anchors/launch_anchors.json`); film-transfer denominator 14.0770 copy-LF units on the batch-1/2 panel (6-ds era 18.6894; ADR r3-0007 5-ds 32.2165); U-Net/film panel ratio 0.9805 — a statistical dead heat (cross-seed ratios 0.94–1.04), so the film denominator stands.
Every trained round-3 card beat the launch best-floor anchor of its era; the cards that also beat the learned film-transfer baseline (era-matched comparison against its 14.0770 copy-LF panel value, or the card's own film record) are r3s2-B1, r3s2-B2, r3s3-B1 and r3s3-B3, while r3s4-B1 (1.40) and r3s1-B1/B2 (1.77) lose to it.
Subset-geomean audit citations (pre-report gate 2): r3s2-B3's 5-cell comparand and every subset sentence quoted from it passed the card's 3-seed `subset_geomean_unit_audit` re-run — verdict flips NONE, minimum over-bar ratio 3.30× in both unit systems; magnitudes are subset- and unit-dependent (rescale 0.58–1.33), so subset sentences are quoted with their subset named and no magnitude is carried across subsets.
r3s2-B2's "survives restriction to claimable cells" reads 2.42× the bar in copy-LF units and 0.35× in film units per its own audit pass — the registered 5-cell verdict is exactly unit-invariant; the subset magnitude is not.
Mandatory ifc disclosure (program §2, rule unchanged pending the operator's open decision): every ifc number above carries the fitted `affine_on_hf_train` floor WITH its leave-one-out fold range (r3s4-B2 turn-2 repricing, the audit program §2 cites).
The quoted single-fit values are single-draw values of an exactly-determined 6-dof fit on 5 rows, and both cells are fold-catastrophic under leave-one-out:
`ifc_poisson` 1.5938 single-fit → LOO mean 4.2335 (systematic +3.820 ± 0.719 $\tau_{rel}$, 5/5 folds breach $\tau$);
`ifc_heat` 0.9584 single-fit → LOO mean 1.8469 (systematic +5.417 ± 4.890 $\tau_{rel}$, fold sd 10.935 $\tau_{rel}$, p95 20.534 $\tau_{rel}$, 3/5 folds breach — the floor crosses skill 1.0 under leave-one-out).
Per the rule, an ifc claim that does not beat the DISCLOSED RANGE has learned nothing beyond linearity; skill < 1 on ifc_heat is not by itself a strong claim.
This disclosure attaches to every ifc number in this report (the §2 tables above, and the §3 r3s2-B1/r3s2-B2/r3s2-B3 ifc readings), not only to this paragraph.

## 3. Stream closures (one block each)

- **r3s1_factorised (CONSOLIDATED at B2, 2026-08-10, per its own part-7 recommendation — no B3 card).**
  B1 CONFIRMED at 24.9573 [24.8726, 25.0662]: the two-stage cross-coefficient head beats the matched one-stage law by +0.5546 [0.5246, 0.5747], but the entire delta is cahn_hilliard — stage 2 is a bitwise empty gate on the other four cells at every seed.
  The mechanism replaced the card's own discriminator: what orders the panel is stage-1 SET size / residual saturation, not cond_dim, and cahn_hilliard is the only cell with both leftover in-bank energy (0.32) and reachability; its test set is two disjoint seed-invariant populations (27 hard non-identifiable rows / 73 easy).
  B2 FALSIFIED at 25.1243 [24.9477, 25.2757] on L2 (panel) and L3 (novelty scope) with L1 (cell) confirmed: the SELECT_MAX cap lift did exactly what B1 predicted — removing 99.1% of the in-bank-outside-SET penalty — but fisher_kpp's oracle bank ceiling (298.83 skill) is 2.74× $\tau_{rel}$ WORSE than the affine floor (270.54), so the target was unwinnable when the card was written; the permutation selection criterion is a category error ($\{p \leq 0.05\}$ is a strict superset of $\{R^2 \geq 0.1\}$ on all 9 cell × seed), and per L3's own pre-registered text the batch is reported as the SELECT_MAX bug-fix with no novelty claim.
  Standing verdict: no selection-side bet left; the residual cahn_hilliard map-quality bet was explicitly not granted a slot.
  Tools promoted: `per_row_paired_decomposition.py`, `amplitude_calibration_audit.py`, `selection_multiplicity_audit.py`.
- **r3s2_field_reach (CLOSED at B3, 2026-08-12, confirmed — stream question answered).**
  B1 FALSIFIED (F2) at 12.9556 [10.3180, 17.8277]: the reach leg F1 held (exact IC synthesis repairs the one stage that can use it — the emulator, 3.1× / 1.3× / 8.0× on ac/ch/fk, zero-information null worse everywhere) while the corrector's added value is unresolvable at 9–163× below one mce, replicating round 2's ch null; the 3-seed spread is a deterministic sample-starved Wiener-deconvolution defect on ifc_poisson ($n_{fit} = 3$, ridge 0) that reproduces round 2's r2s2-B1 instability bit-for-bit.
  B2 FALSIFIED-via-G2(iii) at **10.0853** [9.7249, 10.3528] — the certified stream anchor: the pre-registered repair worked at panel level (beats B1 by 2.8704, whole interval below), and the falsifying leg was shown to measure dispersion, not gain — per the pre-report gate this is quoted through the `transfer_gain_anatomy` re-read: energy-weighted transfer is $-0.74$ in EVERY band at coherence ~1 on ifc_poisson (unweighted band-3 mean 1.1851 vs energy-weighted 0.7427; guard cell fluid 1.7296 vs 0.6473), and the leg's threshold sits inside the fold-to-fold spread of its own statistic (5 of 10 folds trip).
  B3 CONFIRMED the emulator ceiling at 14.1909 [14.0046, 14.5243] (6-cell) with the 5-cell anchor-comparand 10.4763 [10.3176, 10.7785] not beating the anchor (pre-registered replication, 0.77× seed-mce): primary falsifier 0/4, $\phi_{ceil} \geq 0.9648$, E_hall-dominated on 4 cells; the mechanism is the scalar identity of §1, the ceiling is real but costs 8.7–116.6× more LF accuracy than stage 1 delivers, and C3's ifc failure was adjudicated a real cancellation-breaking bias at $N_{hf} = 5$ (mean signed gap +0.3639 on ifc_poisson — larger than the 0.25 tolerance — vs $|\text{mean}| \leq 0.0369$ on the 400-row cells).
  Its part-5 CI carries the recorded run-to-run caveat: a same-seed cross-node rerun moved the 5-cell subset by 0.62× seed-mce (68% of the across-seed spread), so the intervals are seed+run intervals — upper bounds on the seed effect.
  Tools promoted: `lsi_transfer_stability_audit.py`, `task_linearity_audit.py` (B1); `transfer_gain_anatomy.py`, `subset_geomean_unit_audit.py` (B2); `split_transfer_licence_audit.py`, `stage_error_transmission_audit.py` (B3).
- **r3s3_lf_value (CLOSED at B3, 2026-08-11, falsified — mechanism registered).**
  B1 CONFIRMED at 11.0789 [10.8445, 11.2471]: LF-at-train's value is entirely coverage ($E_{cov}/E_{total} \in [0.972, 1.024]$ on 30/30 cells); the covered-conditions arm is the SAME learned function as the no-LF arm ($D(A_2,A_1) \geq D(A_0,A_1)$ on 5/5 cells) — an identifiability result; what LF restores is the condition-response (alignment from $-0.04$…$+0.22$ to 0.89–0.92 on the sharp cells).
  B1's mechanism turn also discovered STOP-THE-LINE #2 (§6) and correctly recorded its own headline vs-anchor deltas as anchor artefacts; the post-repair recompute found no resolvable delta anywhere (panel $-0.81\%$ = 0.079× noise floor).
  B2 CONFIRMED (diagnostic, 2-ds, no panel claim): the coverage knee sits at cap $c^* = 80$ on cahn_hilliard (deciding step 4.05× the certified clause width), and a training-free kernel-ridge surrogate reproduces the trained ladder (Pearson 0.984 ch / 0.977 ifc_heat, same step-max knee) — the knee is a property of the task, not of the FNO or of MF fusion; the measured LF↔HF exchange rate came in an order of magnitude below prediction (0.67–2.18 rows/HF-row).
  B3 FALSIFIED at 18.6212 [18.0610, 18.9994] (film 0.5780): both adjudicable predictive cells missed the sealed knee at 6.03–6.79× (allen_cahn) and 18.60–19.34× (fisher_kpp) their certified $\tau_{rel}^{film}$ on every seed, while the cahn_hilliard reproduction control HIT its pre-declared cap 80 on all three seeds (instrument-instability branch closed).
  Mechanism: the surrogate is the learning curve of a DIFFERENT learner (closed-form RBF ridge) and transfers only where row efficiency matches the trained FNO ($c_{50}$ ratios 1.05 / 0.59 on the B2 validation cells vs 1.79 / 6.28 on the misses); the coverage-radius reading fails outright (fill distance decays 15–29% over an 80× row increase); the level hypothesis is rejected (mean-removed knees also land at 395 on both misses — the required rel-L2/mean-removed pairing on these level-dominated cells); two design amplifiers were identified (ladder built FROM the prediction; step statistic not log-spacing-normalised — under R-per-nat the robust effect is fisher_kpp alone); and foreseeability was NOT established (3/10 seal-time separators vs 2.0 by chance).
  Its part-5 lost write and 2026-08-12 repair are disclosed in §9 — the repaired part 5 is the adjudicated record, not a caveat on these numbers.
  Tools promoted: `response_decomposition.py`, `stale_checkpoint_audit.py` (B1); `coverage_knee_surrogate.py`, `mediator_collapse_fitform_audit.py` (B2); `cap_ladder_knee_audit.py`, `level_shape_error_split.py` (B3).
- **r3s4_audit (CONSOLIDATED at B2, 2026-08-10, per its own part-7 recommendation — no B3 card; package items executed orchestrator-side).**
  B1 FALSIFIED (metrology-limited) at 19.6438 [19.4235, 19.9318]: F1 fired on the letter ($1.1056 \times 10^{-9}$ vs the fixed $10^{-9}$ tolerance) and was adjudicated METROLOGY-LIMITED — the deviation is ~70× below the float32 loader seam, and the floor arms' round-off band spans $6.03 \times 10^{-11}$ to $1.005 \times 10^{-8}$ across datasets (167×), so one fixed tolerance was wrong by construction; F2/F3/F4 confirmed, and the certified noise floor was installed 2026-08-10 after all batch-1 compute had landed and before any 3-seed claim adjudication consumed it.
  B1's re-analysis also priced the stale-audit rule set (the wall-clock rule: 0 unique true positives, 62 false alarms in 859 legs — deleted in favour of checkpoint-embedded binding) and found 18 pfc zero-work anchor legs the pattern-scoped repair verification had missed (neutralised by ADR r3-0004 by accident, not by instrument — the standing lesson that verification scoped to the known blast radius cannot bound the blast radius).
  B2: G1 CONFIRMED at 108/108 (recall 27/27 · 18/18 · 18/18; 0/27 false RETRAIN, Wilson95 [0, 0.125]); both "buys nothing" ablations failed (whole-dataset certificate: 36/36 wrong retrains on test-only mutations; roles-blind split: 9/27 misses and 0/18 REREFERENCE); the compound hypothesis was falsified in its third conjunct only — the G5 fit-set seam (1.9333× on ch), which the operator ADOPTED 2026-08-10 with the corrected scope (nn_condition fit-set breach rates: ch 61.3%, fk 56.0%, ac 23.0% of fit sets — a property of the arm, not a ch peculiarity).
  B2 also measured the round's least stable mandated quantity — ifc_heat's affine floor crosses skill 1.0 under leave-one-out (0.9584 → 1.8469, fold sd ~10.9 $\tau_{rel}$) — and RETRACTED B1's ifc_poisson over-warning (the conservative bound is 1.0136× certified, not ~2.15×; the proxy was off 84× because the cell's affine map makes its per-row gaps condition-independent, CV 0.00119).
  Consolidation package executed: F1 per-dataset ULP tolerances installed (`state/floor_tolerances.json` + install note, affine arm declared NOT YET ADJUDICABLE with all 10 per-arm bands pinned); G5 adopted; binding-instrument promotion to the anchor-build gate; two tool repairs dispatched.
  Tools promoted: `zero_work_resume_scan.py`, `floor_precision_seam.py` (B1); `fitset_matched_n_audit.py`, `floor_arm_precision_band.py` (B2), plus `ckpt_data_binding.py` vendored to `tools/`.

## 4. What actually worked (model-side takeaways)

1. **Condition completeness pays exactly once, at the first stage that consumes it.**
   The exact IC channel improves the condition→LF emulator up to 8× (r3s2-B1 F1), and the factorised head's stage-2 gate works on precisely the one cell with reachable leftover energy (r3s1-B1) — but no downstream stage converted either into panel-level field structure, and the emulator-ceiling identity (r3s2-B3) says no unity-gain route can.
2. **The best learned results all live in the LF-at-train streams.**
   The certified 10.0853 (r3s2-B2) and the film-beating trio (r3s3-B1 0.79, r3s2-B1 0.92, r3s3-B3 0.5780 film) all exploit LF coverage at train time; the condition-only factorised stream never approached the learned baseline (1.77 film).
3. **LF's channel is coverage, with a measurable knee and a measurable price.**
   Value = distinct condition rows (r3s3-B1); the knee is the task's own sample-complexity elbow (r3s3-B2); the exchange rate is 0.67–2.18 LF condition rows per HF row at the measured budgets — an order of magnitude cheaper-than-predicted for the HF side, and exchange rates must be quoted as local marginal rates at a stated budget.
4. **Training-free surrogates are licensed by row-efficiency match, not by correlation.**
   Pearson 0.98 on two validation cells did not survive transfer to cells where the closed-form learner is 1.8–6.3× more row-efficient than the FNO (r3s3-B3); any surrogate-vs-trained claim must publish the $c_{50}$ ratio alongside the correlation.
5. **The learned baseline itself is architecture-insensitive at this budget**: an operator-requested ConvNeXt-U-Net twin lands at 0.9805× film-transfer on the scored panel — a dead heat — so the ADR r3-0006 denominator is robust to the baseline-architecture choice.
6. 20 reusable probe instruments were promoted to `tools/` across the 10 cards (§7).

## 5. ADR ledger

- **ADR r3-0001** (accepted 2026-08-05; operator go + mentor option-A endorsement; amended A1 same day): launch panel composition and fix-option assignment; ifc_heat promoted to the scored panel under A1.
- **ADR r3-0002** (accepted 2026-08-06, operator "A. Regenerate now"): pfc resampled from the all-crystalline parameter box — the NO_GAP verdict was a sampling-composition artifact, not solver physics.
- **ADR r3-0003** (accepted 2026-08-06, operator "A. Repair, then launch"): per-cell estimator-integrity repairs from the defect-class red team (fifth defect class), including the allen_cahn task-void test-split trim and the score-cache data-binding hole (D4).
- **ADR r3-0004** (accepted 2026-08-07, operator "proceed with plan"): pfc to report-only after the scored-cell task-void finding (stop-the-line #1); scored panel to 5 datasets.
- **ADR r3-0005** (RATIFIED 2026-08-10, option A; Eloise deciding for the mentor): pfc scored cell re-pointed to L1(32²)→L3(128²) with the exact spectral (FFT zero-pad) reference 0.012358; both phases executed 2026-08-10; pfc restored to the scored panel with all seams byte-verified and old-convention cells quarantined.
- **ADR r3-0006** (RATIFIED 2026-08-10, operator instruction over the orchestrator's written keep-copy-LF recommendation): headline scores re-denominated to the certified film-transfer baseline; certified same day (jobs 171858–60, stale-audit clean); batch-3 clauses registered in film units.
- **ADR r3-0007** (RATIFIED 2026-08-10, operator option C, proposed-emailed-decided same day): ifc_poisson demoted to report-only (exactly affine, oracle residual $5.4 \times 10^{-16}$, never beaten copy-LF, arithmetically non-adjudicable at certified noise); ifc_heat retained with disclosures; best-floor 38.8368 → 53.2146; the option-C mean-removed check confirmed film's ifc_heat win is STRUCTURAL (0.0547 mean-removed rel-L2 vs best floor 0.1526, advantage 2.60× raw → 2.79× mean-removed, and film sits below the oracle affine residual 0.0272 vs 0.0377), so option C stands with no operator alert.

## 6. Stop-the-line events (both repaired; no frozen number contaminated)

1. **pfc scored cell task-void (HOLD 2026-08-07 → ADR r3-0004 → ADR r3-0005).**
   The eval layer scores pfc at $\max(\text{lf\_fids})$ = l2(64²)→l3(128²), where the crystalline fields are spectrally converged: all 100 test rows task-void (true per-row copy-LF gap median $1.15 \times 10^{-6}$), and the certified reference 0.018257 was ~100% linear-interpolation error of the frozen lift.
   The rung-convention mismatch — ADR r3-0002's acceptance gap was measured at the bottom rung, which the eval layer never scores — let the box swap certify; the fifth-class preflight caught it only after r3s4-B1's brainstormer escalated the instrument's rung repoint.
   Repair arc: report-only same day (r3-0004), spectral-rung repair ratified and executed 2026-08-10 (r3-0005), 18+3 re-score cells stale-gate clean, pfc restored to the scored panel; pfc claims remain MDD-priced at 65.8% and the pfc mce certification (dispatched 2026-08-10) had not landed at close — batch-3 pfc cells were adjudicated CONDITIONAL / not-$\tau$-certified.
2. **Stale-checkpoint anchor contamination (HOLD 2026-08-08 → cleared 2026-08-10).**
   The launch-anchor ifc_poisson cells were re-SCORED on the repaired ladder but never re-TRAINED — the mandated `last.pt` resume silently restored weights fitted to pre-repair arrays (found by r3s3-B1's mechanism analyzer chasing an anchor gap that "no arm effect could explain").
   14 legs across the 4 anchor cards were quarantined and fresh-trained (jobs 89201–89211), re-audited clean with `--fail-on-stale`, and the anchors rebuilt; the diff was confined to ifc_poisson columns, and every contaminated card's anchor IMPROVED under fresh training — the contamination had been biasing the anchors weak, i.e. flattering vs-anchor deltas.
   Permanent instrumentation: the stale-checkpoint gate is mandatory in every anchor build, and checkpoints now carry content-hash data binding (`models_r3/_common/ckpt_binding.py`, mandatory for batch-3 families; priced at 108/108 by r3s4-B2).
   Residual lesson from r3s4-B1: the repair verification was pattern-scoped to `ifc*` and therefore missed 18 identical pfc zero-work legs — verification scoped to the known blast radius cannot bound the blast radius.

## 7. Instruments promoted to `tools/` this round

Twenty card-promoted probe instruments, all registered with verified invocations in `tools/index.md`:
`response_decomposition.py`, `stale_checkpoint_audit.py`, `lsi_transfer_stability_audit.py`, `task_linearity_audit.py`, `per_row_paired_decomposition.py`, `amplitude_calibration_audit.py`, `selection_multiplicity_audit.py`, `transfer_gain_anatomy.py`, `subset_geomean_unit_audit.py`, `coverage_knee_surrogate.py`, `mediator_collapse_fitform_audit.py`, `zero_work_resume_scan.py`, `floor_precision_seam.py`, `ckpt_data_binding.py`, `fitset_matched_n_audit.py`, `floor_arm_precision_band.py`, `cap_ladder_knee_audit.py`, `level_shape_error_split.py`, `split_transfer_licence_audit.py`, `stage_error_transmission_audit.py`.
Two standing usage gates bind every future consumer (adopted 2026-08-10, and honoured throughout this report):
(1) no `AMPLIFYING` verdict from `lsi_transfer_stability_audit.py` may be quoted except through its `transfer_gain_anatomy.py` re-read (the unweighted mode-mean overstates by up to 8.43×);
(2) every subset-geomean statement must cite its `subset_geomean_unit_audit.py` pass.
Scoped caveats on record: `floor_precision_seam.py` cannot price the affine arm (use `floor_arm_precision_band.py`); `zero_work_resume_scan.py` reads UNDERIVABLE on families that emit no step metadata (the film baseline's witness is the clean ckpt-mtime audit).
Maintenance utilities (not card-promoted) also live in `tools/`: `make_round3_anchors.py`, `make_film_denominator.py`, `recompute_{ac,pfc}_reference_floors.py`, `trim_ac_task_void.py`, `extend_noise_floor_pfc.py`, `render_round3_update_figures.py`.

## 8. Methodological rules established this round

- **Energy-weighted statistics rule** (r3s2-B2 part 7, pre-report gate): band statistics registered on energy-weighted or held-out-loss quantities, never an unweighted mode mean.
- **Subset-unit calibration rule** (r3s2-B2 part 7, pre-report gate): calibrate every subset bar on the subset it is read against; the ADR r3-0006 unit transition makes uncalibrated subset geomeans flip magnitude by up to ~7×.
- **G5 blanket rule** (operator-adopted 2026-08-10): any claim priced against an `nn_condition` best floor carries the arm's fit-set noise band (sd 1.796 / 0.740 / 0.276 $\tau$ on ch/ac/fk) beside $\tau_{rel}$; affine reproductions adjudicate against their pinned per-arm band, not the dataset-level tolerance.
- **F1 tolerances are per-dataset metrology** (r3s4-B1/B2): floor-reproduction tolerances at $\max(10^{-9}, \text{measured ULP band})$, installed in `state/floor_tolerances.json`; a fixed global tolerance is above the seam on some cells and below it on others.
- **Checkpoint↔data binding contract** (r3s4-B2, batch-3 scope rule 2): every family writes role-resolved train/test content hashes into `last.pt` at every save; the stale predicate becomes exact and wall-clock rules are retired (0 unique TPs / 62 FPs).
- **Clause hygiene** (batch-3 scope rules, from the r3s2-B2 postmortem): no falsification leg whose threshold sits inside the fold-to-fold spread of its own statistic; pre-registered repair grids must justify their FLOOR, not only their ceiling; enumerate the $C(N_{tr}, n_{fit})$ fold population for closed-form stages at $n_{fit} \leq 5$.
- **Spacing-invariance rule for self-referential ladders** (r3s3-B3 part 7): any card that derives its measurement ladder/grid from the quantity under test can manufacture its own verdict; check spacing invariance before sealing.
- **Level/shape orthogonal split preferred** (r3s3-B3 part 7): the mean-removed convention moved one quantity across three different knee readings; `level_shape_error_split.py` is convention-free ($\mathrm{nrmse}^2 = \mathrm{level}^2 + \mathrm{shape}^2$ exactly) and is the preferred instrument for the project's rel-L2-is-level-dominated rule.
- **Surrogate licensing rule** (r3s3-B3 part 7): a closed-form surrogate validated against a trained arm is validated for the row efficiency those cells share; publish the $c_{50}$ ratio alongside any correlation.
- **Attribution is quantity-specific** (r3s2-B3 parts 5/7): never carry a per-cell attribution from one delta to another (R1-vs-R0 is 82.5% ifc while the anchor delta is 108.6% allen_cahn on the same card), and never carry a subset magnitude across subsets.
- **Exchange rates as local marginal rates** (r3s3-B2 part 7): quote LF↔HF exchange at a stated budget; pool-fraction ratios recover the wrong law almost exactly.
- **Email-on-decidable rule** (operator directive 2026-08-10, codified globally): decision-ready items are emailed the moment they become decidable, presented together in dependency order.

## 9. Process findings (harness)

- **10 cards over 4 streams closed the round**: two streams fully carded to B3, two consolidated at B2 by their own part-7 recommendations — the first round in which streams closed themselves by recommendation rather than budget exhaustion.
- **In-round 3-seed confirmation (MUST #4) worked**: every claim in §2 is a 3-seed mean with CI; no post-round confirm queue exists.
- **Card-write integrity is the round's dominant new infra hazard (two lost-update incidents, both recovered, one round-4 contract item).**
  r3s4-B2's part 5 was clobbered to null by a concurrent full-card rewrite (batch 2; re-derived from artifacts, no data loss).
  r3s3-B3's 3-seed part-5 write never landed (the analyzer's completion report overstated; the numbers survived in its handoff) and rode two pipeline stages undetected before the 2026-08-12 maintainer walk flagged it; the repair extended part 5 to the 3-seed record with parts 6/7 verified byte-identical (sha), clause text byte-equal to the locked `expected_falsification`, and every seed-0 digit reproduced before extending — the repaired part 5 is the adjudicated record.
  Root pattern: concurrent analyzers collided in a shared scratchpad; the fix class is dispatcher-verified card writes plus disjoint scratch roots (§11).
- **The review loop caught real defects before submission on all four batch-1 builds** (F4 escalation gated on the wrong constant; eval-tree redirect hygiene on 3 of 4 builders — now codified in the builder registration), and the r3s2-B3 sequence demonstrated hold-discipline under a moving clause input: the job was held at 0 s executed, the reviewer conceded its classification on the record, and the release was granted on four written grounds with the tree equal to the reviewed commit at dispatch.
- **One SLURM failure in batch 3, fixed at debug attempt 1** (ALGO: guard-cell shape misclassification — classify by plan knob, not plan structure; relaunched clean); the failed leg is intentionally not ledgered as compute cost per the ledger convention (71 entries at close).
- **Session mortality remained survivable by state discipline**: the 2026-08-11 resume re-claimed the runbook only after a sibling-session check, per the shared-runbook fire-time rule.
- **The outputs repo was never initialized at launch scaffold** — caught by the round-folder-only verification before any commit leaked repo-wide files, then fixed permanently.
- **Standing delegation (2026-08-06) plus stop-the-line MUSTs proved compatible**: evidence-backed scope/panel/recipe decisions executed autonomously with written records, while both defect discoveries still halted the round for operator adjudication.

## 10. Operator-decision ledger (Eloise, this round)

| Date | Decision |
|---|---|
| 2026-08-05 | Launch go (ADR r3-0001, with mentor option-A ratification); Amendment A1 (ifc_heat promoted to the scored panel); degeneracy-audit ruling (keep ifc_poisson as control cell + mandatory affine-floor disclosure); weak-gap adjudication (option A: launch when anchors certify, gap sweep in parallel). |
| 2026-08-06 | ADR r3-0002 ("A. Regenerate now" — pfc crystalline box); defect-class red team commissioned; ADR r3-0003 ("A. Repair, then launch" on the red-team HOLD); STANDING DELEGATION for evidence-backed scope/panel/recipe decisions; Hugging Face update approval. |
| 2026-08-07 | Stop-the-line #1 adjudication ("proceed with plan") → ADR r3-0004, pfc report-only. |
| 2026-08-09 | Stop-the-line #2 repair plan accepted ("continue") → quarantine + fresh-train + audit-gated anchor rebuild. |
| 2026-08-10 | ADR r3-0005 ratified (option A, deciding for the mentor); round-orientation directive (target the best LEARNED baseline) → ADR r3-0006 ("change the denominator to film transfer's RMSE"); best-of-zoo sweep aborted (previously-benchmarked models need no re-test); G5 fit-set re-pricing ADOPTED; batch-3 scope ("do stream rec"); ifc panel membership questioned → ADR r3-0007 proposed and ratified same day (option C); email-on-decidable rule issued; ifc affine-floor rule question left OPEN pending fuller explanation. |
| 2026-08-12 | Round-close go (all 10 cards complete; this report). |

## 11. Round-4 contract items (collected from the flow log and the terminal cards' part 7)

Process contract:
1. **Dispatcher-verified card writes**: every subagent card write is verified by the dispatcher against the artifact before the next pipeline stage (the r3s3-B3 lost write rode two stages), and concurrent analyzers get disjoint scratch roots as standard prompt boilerplate (flow 2026-08-12).
2. **Pin `FAMILY_DIR` to a commit snapshot** — jobs currently execute the mutable worktree path, safe only by sequencing (flow 2026-08-11).
3. **Fold `_sealed_utc` / `_driver.sha256` INTO the seal payload** (flow 2026-08-11).
4. **Lazy-enumerate `transfer_gain_anatomy.py` fold combinations** (OOM on sharp cells; flow 2026-08-11).

Science contract:
5. **Any condition→pseudo-LF→HF route card must state in advance which term of the unity-gain identity it breaks** ($\mathrm{nRMSE}(R_1) \approx \mathrm{nRMSE}(R_0) \approx$ stage-1 held-out error); otherwise it is pre-falsified by r3s2-B3's mechanism (r3s2-B3 part 7).
6. **The stage-1 sampling ladder** — refit stage 1 alone at 100/200/400 condition rows to separate sampling-limited from capacity-limited, deciding whether the route lever is a data question (r3s2-B3 part 7).
7. **Knee designs decouple the confirming ladder from the prediction** (fixed geometric ladder) and normalise the step statistic by log-width, with an abstention guard (register a knee only when $R_{surr}(c_{pred}) \geq 0.80$) and the $c_{50}$ ratio published beside any surrogate correlation (r3s3-B3 part 7).
8. **Split-transfer licences at $N_{hf} = 5$ need a dead-band on rank terms and an explicit exchangeability check** (r3s2-B3 part 7).
9. **The nn_condition floor-definition question** — bagged-1NN expectation floor (an ADR) vs carrying the fit-set band (a reporting convention) — is queued for adjudication; nothing in this round's evidence decides it (r3s4-B2 part 7).
10. **r3s1's open question** (is the stage-2 gain a learned low-dimensional coordinate or a lucky reduction) has a pre-priced closed-form probe set (PCA-3 / random-3 / true-SET / concatenated arms) recorded but not granted a slot (r3s1-B1/B2 part 7).
11. **pfc mce certification** (r3s4_cert_min protocol on the ADR r3-0005 cell) was dispatched 2026-08-10 and had not landed at close; until it does, pfc cells carry no certified $\tau$ and stay CONDITIONAL in adjudications (r3s3-B3 part 5).

## 12. Pending operator decisions (open at close)

1. **ifc affine-floor rule change** — the explainer was delivered 2026-08-10; program.md §2's rule text stands unchanged until she rules (the mandatory disclosure was honoured throughout this report, §2).
2. **Panel-composition ADR** — evidence on file, presented as evidence and not as a decision:
   the registered-4 batch-3 headline ("the LF route beats the matched-budget no-LF denominator") is 59.1% carried by ifc_heat alone — the one cell that fails the split-transfer licence at every seed for a real reason and loses to its own nn_condition floor by 2.30 G5 band-sd;
   ifc_poisson is 55.8% of the same headline on the 6-cell panel AND 98.2% of the cross-node drift while REPORT-ONLY — the cell not allowed to carry a claim carries both the effect and the noise;
   same-seed cross-node drift is 0.62× seed-mce (68% of across-seed spread), so current CIs are seed+run intervals;
   against demotion of ifc_heat: film's win there is structural, not an offset (mean-removed 0.0547 vs floor 0.1526, below the oracle affine residual), per the ADR r3-0007 option-C check.
   (Subset statements above cite r3s2-B3's `subset_geomean_unit_audit` 3-seed pass, §2.)
3. **Round-1 2500-epoch full runs** — still ON HOLD per operator (unchanged since 2026-08-01; the round-1 s4 gate-relaxation decision remains a prerequisite for s4's slot).
4. **Reporting-convention reconciliation** — the ifc_heat per-sample-mean rel-L2 (floor records) vs aggregate nRMSE (`film_denominator.json`) split (~1.27× cross-file bias) is flagged on the anchor file; a single convention should be fixed the next time either file is regenerated (this report never mixes them, §2).
