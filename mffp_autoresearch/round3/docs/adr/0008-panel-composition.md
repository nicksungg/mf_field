# ADR r3-0008 (RATIFIED — Option C): panel composition for round 4, and the rule for a headline concentrated in one cell

**Status: RATIFIED 2026-08-12 — operator (Eloise) chose Option C**, ruled in-session via the decision brief (artifact `44eb5976`, plain-language restatement of this ADR) after the recommendation below; recorded in `state/orchestrator_flow.md` (2026-08-12 operator-decisions entry).
Execution per the Option C sketch at the end of this document; the subset-audit tool fix (sketch step 2, ruling-independent) was already done and converged earlier the same day (commits `2b72977`–`4291ffd`).

Original proposal follows unchanged.
Nothing in this document is executed, and nothing in it changes a round-3 number.
Raised from round-3 report §12 item 2 ("Panel-composition ADR — evidence on file, presented as evidence and not as a decision"), drafted 2026-08-12 after re-verifying every cited number against its primary artifact.
Builds on ADR r3-0007 (RATIFIED 2026-08-10, option C); it does **not** supersede that ADR's `ifc_heat` / `ifc_poisson` call, and the evidence assembled here does not force reopening it (see "What this does NOT decide").

## Question

Two questions, one of which turns out to be a defect rather than a preference.

1. **Composition.** What is the scored panel for round 4 — carry forward the ADR r3-0007 five (`sharp__phase_field_crystal_2d`, `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`, `ifc_heat`), narrow it, or widen it?
2. **Aggregation rule.** What is the rule for a headline whose effect is concentrated in one or two cells — and, prior to that, is "report-only" actually being honoured in the aggregates that carry round-3 headlines?

Question 2 is the load-bearing one.
The round-3 headline sentence at issue is r3s2-B3's "the deployed route $R_1^{\text{predicted}}$ beats the matched-budget no-LF denominator $R_0^{\text{absent}}$ on the panel and on every subset" (`experiment_cards/r3s2_field_reach/batch_3/B3.json`, `5_actual_result.subset_geomean_unit_audit.sentence_audited`).

## Evidence on file (every number re-verified against its primary artifact)

Sources, abbreviated below:
`B3` = `mffp_autoresearch/round3/experiment_cards/r3s2_field_reach/batch_3/B3.json`;
`AUDIT` = the 3-seed `subset_geomean_unit_audit` output for the $R_1$-vs-$R_0$ arms, recorded in `B3` `5_actual_result.subset_geomean_unit_audit.out` and still present at `/tmp/claude-28156/-resnick-groups-Hippo-ezeng-mf-field/32ff496d-5389-43eb-87bd-02585b2d9f58/scratchpad/r3s2b3_analyzer_3seed/subset_audit_3seed.json` (scratch, regenerable from the recorded invocation, **not archived**);
`NOISE` = `mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json`;
`MEANREM` = `mffp_autoresearch/round3/state/adr0007_meanremoved_check_2026-08-10.json`.

**The registered-4 headline is 59% one cell.**
`AUDIT` `log_space.per_cell_log_delta` (3-seed, $\log(\mathrm{nRMSE}(R_1)/\mathrm{nRMSE}(R_0))$, the additive scale-free form) gives, per cell:
pfc $+0.01498$, allen_cahn $-0.14468$, fisher_kpp $-0.16968$, cahn_hilliard $+0.02258$, ifc_poisson $-0.87469$, ifc_heat $-0.42025$.
Summed over the registered-4 subset (allen_cahn, fisher_kpp, cahn_hilliard, ifc_heat) that is $-0.71204$, of which ifc_heat carries $-0.42025 = 59.0\%$ (`AUDIT`, recomputed here from its own per-cell values).
The report and `B3` `6_analysis.findings[16]` quote $59.1\%$ from an independent T3 reconstruction; the audit artifact itself gives $59.0\%$.
In skill units the registered-4 delta is $-2.7870$ copy-LF / $-0.10760$ film (`AUDIT` `subsets.registered4`), matching the report's $-2.78$.

**The carrying cell loses to its own floor on the same arm.**
`B3` `5_actual_result.C4_floor_arms_read_against_g5_band.registered_cells.ifc_heat.R1_predicted.nn_condition`: margin_mean $+0.016521$ nRMSE against band sd $0.0071919$, i.e. `margin_mean_over_band_sd` $= 2.2972$ — the report's "2.30 G5 band-sd", loss direction, at every seed individually ($2.44 / 2.75 / 1.70$).
It registers at all only because `ladder.registration:274` defines floor-disqualification as beating **none** of the arms, and $R_1$ does beat `train_mean` and zero (`B3`, same block's clause text).
The "fails the split-transfer licence (C3) at every seed" statement is `B3` `6_analysis.interpretation[7]` and the part-5 clause prose; I confirmed the nn_condition floor miss numerically at all three seeds but did not recompute the C3 clause verdict itself.

**The report-only cell carries the effect and the noise.**
On the six-cell panel, `AUDIT` `log_space.per_cell_share_of_panel_delta` gives ifc_poisson $0.55651$ and ifc_heat $0.26738$ — the two ifc cells are $82.4\%$ of the panel delta, ifc_poisson alone $55.7\%$.
The report quotes $55.8\%$ (the T3 reconstruction); `B3` part 5 ships $55.7\%$; the audit artifact computes $55.65\%$.
And ifc_poisson carries $98.2\%$ of the same-seed cross-node drift: from `B3` `6_analysis.findings` T3, the per-cell $\Delta\log$ between jobs 261188 and 346236 is allen_cahn $+0.0196$, fisher_kpp $-0.0047$, cahn_hilliard $+0.0015$, ifc_heat $-0.0068$, pfc $-0.0003$, ifc_poisson $-0.1590$; the variance share of ifc_poisson recomputes here to $98.23\%$.
ifc_poisson has been report-only since 2026-08-10 (ADR r3-0007).

**Current intervals are seed+run intervals, not seed intervals.**
`B3` `5_actual_result.run_to_run_variance_caveat`: the same seed 0 scored twice on different nodes moved the 5-cell anchor subset from $10.6460$ to $10.3328$, $|\Delta| = 0.3132$; against the certified panel $\mathrm{seed\_mce} = 0.5082844$ that is $0.616$ ($\to 0.62\times$), and against the across-seed spread $0.4610$ it is $0.679$ ($\to 68\%$).
Both ratios recompute exactly.
Every ci95 in that card therefore mixes seed and run-to-run variance and is an upper bound on the seed effect.

**Against demoting `ifc_heat`: its win is structural, not an offset.**
`MEANREM` `verdict_reasoning`: film's mean-removed per-sample rel-L2 on ifc_heat is $0.0547$ (worst seed $0.0640$) against $0.1526$ for the best mean-removed floor (`affine_on_hf_train`), $0.2098$ for `nn_condition` and $0.2698$ for `train_mean`; the advantage ratio *rises* from $2.60\times$ raw to $2.79\times$ mean-removed, and film beats the oracle affine residual level ($0.0272$ vs $0.0377$).
The cell is confirmed level-dominated ($88.5\%$ of the mean target norm is the per-sample constant), so the concern was legitimate and was answered.
This is the ADR r3-0007 option-C check and it is about a *different arm and quantity* (film-transfer skill) than the r3s2-B3 route headline above — per the round's own "attribution is quantity-specific" rule (report §8), the two must not be merged.

### The aggregation defect (checked in code and in the anchor files, not asserted)

Report-only **is** honoured where the anchors are built.
`tools/make_round3_anchors.py` separates `PANEL` (five cells, ifc_poisson absent) from `REPORT_ONLY = ["ifc_poisson"]`, aggregates scored geomeans over `PANEL` only, and writes report-only cells to a distinct `report_only_per_dataset_mean_skill` key.
`state/anchors/launch_anchors.json` carries `_panel` (five cells) and `_report_only` (`ifc_poisson`); `state/anchors/film_denominator.json` carries `_panel5_adr0007` and an explicit `_adr_r3_0007` note that ifc_poisson "is retained in `datasets` for reporting but excluded from the scored panel aggregate".
That layer is clean.

It is **not** honoured in the two places the batch-3 headline actually lives, and one of those is a defect:

1. **The card's shipped panel geomean is a six-cell geomean containing a report-only cell.**
   `B3` `5_actual_result.panel_geomean_skill` is $14.1909$ $[14.0046, 14.5243]$ with `_definition` "6-cell recipe.datasets panel", and the report §2 batch-3 table quotes it verbatim as "6-cell panel 14.1909".
   The card locks `recipe.datasets` at creation, which predates ADR r3-0007, so the composition is a launch-era artefact rather than a decision — but the number as published aggregates a cell that is not allowed to carry a claim.
   The card does also publish the ADR-0007 scored-5 and registered-4 subsets, so the honest reading exists on the same record; the six-cell number should not be the one that travels.

2. **The bar the headline is read against is calibrated on the wrong composition, and the audit's own mismatch verdicts are inverted as a result.**
   The bar is $0.5082844$, which is `NOISE` `_panel_geomean.seed_mce`.
   `NOISE` `_panel_geomean.panel` is `[ifc_heat, ifc_poisson, sharp__allen_cahn_2d, sharp__cahn_hilliard, sharp__fisher_kpp_2d]` — the ADR r3-0004 five, certified 2026-08-08.
   That composition **includes the now-report-only `ifc_poisson` and omits the now-scored `pfc`**: it is neither the scored panel nor a report-only-clean set, and no scored-panel-calibrated bar exists on file.
   `tools/subset_geomean_unit_audit.py` takes the bar's calibration panel as a *declared* argument and sets `bar_calibration_verdict = "OK" if sorted(cells) == sorted(panel) else "SUBSET_BAR_MISMATCH"` (lines 178-179).
   In the $R_1$-vs-$R_0$ run the declared `--panel` was the six cells (`AUDIT` `_args.panel`), so the audit blessed `panel6` as `OK` and flagged `adr0004_anchor5` as `SUBSET_BAR_MISMATCH` — whereas `adr0004_anchor5` is *exactly* the bar's true calibration set and `panel6` is not.
   The two verdicts are inverted, and the rescale factors ($0.58$ / $1.33$ / $0.72$) are measured against the wrong reference.
   This violates the round's own "subset-unit calibration rule" (report §8: "calibrate every subset bar on the subset it is read against"), which the same stream established.
   What does **not** change: the sign. The delta is negative on every subset examined, so the direction of the headline survives; it is the magnitude, the $|\Delta|/\text{bar}$ ratios and the "verdict flips NONE, minimum over-bar ratio $3.30\times$" sentence in report §2 that rest on the mis-declared bar.

3. **Provenance gap.** The archived `subset_geomean_unit_audit_*.json` files under `mffp_autoresearch_outputs/round3/r3s2_field_reach/B3/eval/preflight/` are the *certified floor-arms* pass (`nn_condition` vs `train_mean`), a different sentence.
   The $R_1$-vs-$R_0$ 3-seed pass that the report's subset statements actually cite exists only at the scratch path recorded in `B3` part 5.
   It is intact today and it reproduces the shipped numbers, but it is not an archived artifact.

## Panel arithmetic under each option (computed here from `AUDIT` per-cell log deltas; no new jobs)

Log space is the only cross-subset-comparable form; skill-unit magnitudes must not be carried across compositions (report §8).

| subset | cells | $\sum \log(R_1/R_0)$ | per-cell | largest contributor | its share |
|---|---|---|---|---|---|
| panel6 (as shipped) | pfc, ac, fk, ch, ifc_poisson, ifc_heat | $-1.57175$ | $-0.26196$ | ifc_poisson | $55.7\%$ |
| adr0007_scored5 | pfc, ac, fk, ch, ifc_heat | $-0.69705$ | $-0.13941$ | ifc_heat | $60.3\%$ |
| registered4 | ac, fk, ch, ifc_heat | $-0.71204$ | $-0.17801$ | ifc_heat | $59.0\%$ |
| registered-3 (drop ifc_heat) | ac, fk, ch | $-0.29178$ | $-0.09726$ | fisher_kpp | $58.2\%$ |
| sharp4 (drop both ifc) | pfc, ac, fk, ch | $-0.27680$ | $-0.06920$ | fisher_kpp | $61.3\%$ |

Two things follow, and the second is the reason a naive rule would be wrong.

Demoting ifc_poisson under ADR r3-0007 did not de-concentrate the headline — it **re-concentrated** it, from $55.7\%$ ifc_poisson to $60.3\%$ ifc_heat on the resulting scored panel.
And a flat "no cell may carry more than half the delta" cap would disqualify essentially every subset here, including the clean sharp-4 ($61.3\%$ fisher_kpp): with four to six cells, one cell carrying more than $1/n$ of a log-additive delta is ordinary, not pathological.
The discriminating facts are (a) whether the direction survives deleting the largest contributor — here it does, on every subset — and (b) whether the carrying cell is itself claim-eligible on that arm.
On registered-4 it is not: ifc_heat loses to its own `nn_condition` floor by $2.30$ band-sd on the same arm that the headline credits it for.

## Options

Each is stated with its concrete consequence for the round-3 headline and for the round-4 launch.

- **Option A — status quo.**
  Carry the ADR r3-0007 five into round 4; no aggregation rule; keep the disclosures as prose in report §12.
  Round-3 consequence: the six-cell $14.1909$ and the $8.35\times$-bar panel sentence stay quotable, with a defect on record and no fix.
  Round-4 consequence: the next round inherits an uncalibrated bar and a headline whose largest contributor is a floor-losing cell. Cheapest, and the only option I would call unsafe.

- **Option B — aggregation hygiene only (no composition change).**
  Report-only cells are excluded from **every** aggregate that carries a claim, not only from the anchor files: card `recipe.datasets` panels are re-expressed at analysis time against the *current* scored composition, and each aggregate is stamped with its composition and its ADR era.
  The noise-floor bar is recertified on the scored panel, and `subset_geomean_unit_audit` is called with the bar's *true* calibration panel (ideally read from the anchor file rather than passed by hand).
  Round-3 consequence: the six-cell $14.1909$ and the panel6 $-4.2448$ / $8.35\times$ statements are retired as claim-bearing; the licensed forms become the ADR-0007 scored-5 ($-2.8943$ copy-LF, $-0.08984$ film) and registered-4 ($-2.7870$, $-0.10760$) versions, re-read against a correctly calibrated bar. The direction of the headline is unaffected.
  Round-4 consequence: composition changes stop silently re-weighting old numbers.

- **Option C — Option B plus a concentration rule (recommended).**
  Add to the registration contract: any panel- or subset-level headline must publish (i) the per-cell log-delta shares, (ii) the leave-one-cell-out result with the largest contributor removed, and (iii) confirmation that the largest contributor is *claim-eligible on that same arm*.
  A headline whose largest contributor loses to any of its own floor arms on that arm is registerable only as a per-cell claim over the eligible cells, never as a panel claim.
  This also requires tightening `ladder.registration:274`: floor-disqualification as "beats none of the arms" is what let ifc_heat carry a panel headline while losing to `nn_condition`.
  Round-3 consequence: the registered-4 headline is restated as "the LF route beats the matched-budget no-LF denominator on allen_cahn ($\Delta\log -0.145$) and fisher_kpp ($-0.170$), not on cahn_hilliard ($+0.023$); on ifc_heat it does ($-0.420$) but that cell loses to its own `nn_condition` floor by $2.30$ band-sd, so it does not carry the panel claim" — a two-cell effect, direction-robust ($\sum\log$ stays negative under every leave-one-out above).
  Round-4 consequence: concentration is disclosed by construction, so no future round needs a §12 item to say it.

- **Option D — Option C plus demoting `ifc_heat` to report-only** (scored panel becomes sharp-4: pfc, ac, fk, ch).
  Round-3 consequence: the registered-4 headline reduces to the three sharp cells; ADR r3-0007's option-C call is reopened and reversed towards its option B.
  Round-4 consequence: a clean, homogeneous panel — and the round's only genuine learned win (film on ifc_heat, mean-removed $0.0547$ vs floor $0.1526$, structural per `MEANREM`) is no longer a scored result, and the benchmark's claim scope narrows to periodic pseudo-spectral tasks.
  The evidence does not support this: the ifc_heat facts against it are per-arm facts about r3s2-B3's route arm, not about the cell's admissibility, and per-cell verdicts are unit- and composition-invariant.

- **Option E — abolish panel-geomean headlines; per-cell claims only.**
  Round-3 consequence: every panel sentence in the report becomes a table of per-cell verdicts.
  Round-4 consequence: no composition question can ever distort a claim again — at the cost of the benchmark's single comparable summary number, which is the thing the leaderboard and the paper bar are built on. Too blunt for the problem measured.

**Recommendation: Option C**, because the measured defect is in the aggregation and its bar rather than in which cells exist, and because the same arithmetic shows a composition change alone does not fix concentration (removing ifc_poisson raised the top share from $55.7\%$ to $60.3\%$).

Round-4 note, applicable under every option and unchanged from ADR r3-0007: regenerate the ifc pair with $\geq 40$ HF train rows and a non-degenerate condition design, then readmit; and widening the panel (the standing `ext/gray_scott_2d` candidate, ADR r3-0001 A1) is the only structural way to lower per-cell shares.

## What this does NOT decide

- It does **not** reopen ADR r3-0007.
  `ifc_poisson` stays report-only and `ifc_heat` stays scored under Options A, B, C and E; only Option D would change that, and this ADR recommends against it.
- It does **not** decide the **ifc affine-floor rule** (report §12 item 1) — whether the mandatory disclosure keeps the single-fit value with its LOO fold range or moves to a fold-averaged floor definition.
  That is a separate open operator decision and none of the options here presume an answer.
- It does **not** decide the **`nn_condition` floor-definition question** (report §12 item 9: bagged-1NN expectation floor vs carrying the fit-set band).
  Option C's eligibility test uses whatever floor definition is in force; it does not choose one.
- It does **not** re-adjudicate any round-3 card verdict.
  Every per-cell verdict is unit- and composition-invariant and stands as published; what is at stake is the panel/subset *sentences* and their bar ratios.
- It does **not** decide the **reporting-convention reconciliation** (report §12 item 4, the $\sim 1.27\times$ aggregate-nRMSE vs per-sample-mean rel-L2 ifc bias).
- It does **not** authorise any recompute, re-score or GPU spend; the execution sketch below is contingent on ratification.

## Execution sketch if ratified as Option C (no GPU; anchors and cards only)

1. Recertify the noise-floor panel constant on the scored composition, and record its calibration panel in the file so the audit tool can read it rather than be told it.
2. Make `subset_geomean_unit_audit.py` default its `--panel` to the anchor file's `_panel`, and re-run the r3s2-B3 $R_1$-vs-$R_0$ pass with the corrected calibration; archive the output beside the floor-arms passes instead of leaving it in scratch.
3. Add the concentration disclosure (per-cell shares, leave-one-out, largest-contributor eligibility) to the card part-5 template and to the registration contract; tighten `ladder.registration:274`.
4. Restate the affected report §2 / §3 sentences on the licensed compositions (no number is recomputed, only re-scoped), and record the six-cell $14.1909$ as an era-stamped historical value.
5. Fold the composition/era stamp into every aggregate written by `tools/make_round3_anchors.py` so the launch of round 4 starts from an unambiguous panel.
