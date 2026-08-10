# Summary so far — stream `r3s1_factorised`, entering batch 2

## Where the stream stands

Batch 1 (`experiment_cards/r3s1_factorised/batch_1/B1.json`) shipped the two-stage cross-coefficient closed-form head as the scored condition→HF arm and **confirmed its clauses**.
The certified stream anchor is `state/anchors/r3s1_factorised.json` = **24.9573** panel geomean skill, 3-seed CI [24.8726, 25.0662], versus the training-free launch best-floor anchor **34.4198** (program.md §2) and the shipped condition→level law (r2s1_direct-B3) at 25.5119.
The paired delta vs the matched one-stage control is **+0.5546 [0.5246, 0.5747]**, sign-identical at all three seeds.

Two calibration facts govern every batch-2 threshold.
The certified `_panel_geomean` `seed_mce` is **0.5083** (`state/anchors_repaired/noise_floor.json`, installed 2026-08-10 per `state/orchestrator_flow.md`), so the batch-1 panel delta is only **1.09x one mce** — narrow, and any batch-2 claim landing under ~0.51 panel units is noise, not signal.
The win is **one cell**: cahn_hilliard, +1.3073 against `tau_rel` 0.3612 (anchor `caveats`).
Round-3 success criterion 1 needs >= 1 certified mce on **>= 2** scored datasets; the stream currently has one.

## What the mechanism stage actually found

`worktrees/r3s1_factorised/B1/notes/handoff_experiment_mechanism_analyzer.md` replaced the card's pre-registered mechanism story.

- **cond_dim is NOT the discriminator.** At identical cond_dim 19, allen_cahn's stage-1 SET is 17 directions capturing 88.5 % of energy with 6.3 % left over that is pure noise (max OOF R^2 0.0013 from the condition, -0.0038 from the SET coefficients), while cahn_hilliard's SET is 3 directions leaving 32.0 % with pod_5/pod_6 at OOF R^2 0.67/0.65 from the *predicted* SET coefficients. The proposed replacement discriminator is `n_SET` / `E_rem` x reachability, both measurable before the test tensor unlocks.
- **fisher_kpp's affine loss is pure truncation.** `SELECT_MAX = 32` fired (`clip_rule = "raw set oversized -> top-32 by OOF R^2"`), stranding 0.0713 of condition-reachable encoded energy at OOF R^2 0.29-0.31; residual attribution shows the head is *better* than affine inside its SET (-0.0072) and loses entirely outside it (+0.1202), a 17x asymmetry. Named "the cheapest available panel gain in this stream".
- **cahn_hilliard's test set is two disjoint populations.** Exactly 27 of 100 rows, seed-invariant, score worse than `ref_zero` under every condition-only arm, with an empty band in the per-row error histogram between 0.62 and 0.99; they are indistinguishable in condition space (max 0.448 sigma/dim, NN-distance ratio 1.018) but 3.3x farther in field space (0.4202 vs 0.1278 rel-L2). This is condition **incompleteness** on ~27 % of the cell, not an architecture limit.
- A **fair-comparison seam** (reference arms fit on 400 rows vs the scored arm's 320) is routed to r3s4's batch-2 contract; under the matched budget only fisher_kpp remains a resolvable sharp-cell negative.

Card part 7 (`7_gap_and_future`) sets batch 2's priority order: raise `SELECT_MAX`; feed stage 2 `[predicted SET coefficients, condition]`; pre-register `n_SET`/`E_rem` as the discriminator; and it explicitly warns **not** to spend a batch on cahn_hilliard's hard 27 %.

## Prior art already on the record (batch 1)

`websearches/r3s1_factorised/batch_1/report.md` returned `preempted-but-MF-composition-open` twice.
D1: Spyromitros-Xioufis et al., arXiv:1211.6581 (SST/ERC) owns both the cascade and the OOF-corrected gate — and the F25 true-gate reversal is a **rediscovery** of that paper's train/predict discrepancy, not a finding.
D2: the *idea* of a pre-fit "should we share?" predictor is published (arXiv:2310.16241 task affinity; arXiv:2607.06832 heterotopic kriging), with the independent variable left open.
Batch-1 dead ends worth not repeating: gappy POD (partial spatial observations, different mechanism), cascaded-surrogate uncertainty propagation, and two null searches on "stacked single-target on POD modal coefficients".
Batch 1 could not extract PDFs; that limitation is resolved (repo venv has `pypdf`).

## Open questions batch 2 must have prior art on

1. **Adaptive / energy-criterion basis truncation for operator learning at tiny N** — is a *predictability*-based (OOF R^2) rank criterion, as opposed to an energy criterion, already published?
2. **Two-population (non-identifiable subpopulation) structure in PDE benchmark test sets** — is diagnosing and reporting a condition-incomplete subpopulation an established methodology?
3. **Gated residual-subspace correction** — cascading a gate over the *unselected* residual subspace of a reduced basis.

The in-repo literature reports (`docs/reports/MF_Leaderboard_Beaters_2026_Report.md`, `MF_Sharp_HighFreq_Report.md`) were checked for POD/truncation content; they treat spectral-mode truncation as an FNO architectural question, not as a POD rank-selection question, so they do not cover directions 1-3 and are not re-derived here.
