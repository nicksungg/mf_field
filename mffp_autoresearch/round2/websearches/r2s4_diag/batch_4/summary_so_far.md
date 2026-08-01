# Summary so far — stream `r2s4_diag`, entering batch 4

## What this stream has already established (cards, read directly)

`experiment_cards/r2s4_diag/batch_1/B1.json`, `batch_2/B2.json`, `batch_3/B3.json`.

**B1 (floor + spread certification, pre-directed by program.md §12.4).**
Reproduced the frozen training-free floors, then trained one minimal condition→HF FiLM-FNO decoder (`r2s4_cert_min`, smoke tier, seeds {0,1,2}) on the panel.
That run replaced the provisional noise floor: `state/noise_floor.json` now carries `_certified_utc: 2026-07-31T16:49:04Z`, panel geomean per-seed `[19.3853, 19.5411, 20.5271]`, `min_claimable_effect = 1.1418668211296108` (defined `max(spread_maxmin, paired_null_95)`), and per-dataset MCEs: `ext__helmholtz_2d 2.95299`, `ifc_poisson 0.93770`, `sharp__allen_cahn_2d 0.87970`, `sharp__cahn_hilliard 0.09125`, `sharp__fisher_kpp_2d 0.00071`, `sharp__phase_field_crystal_2d 0.21303`.
It also became the stream anchor (`state/anchors/r2s4_diag.json`, `certified_3seed_panel_geomean`, CI95 `[19.3853, 20.5271]`, per-dataset `ifc_poisson 8.26122`).
B1's aleatoric-barrier estimator had **no support** on `sharp__cahn_hilliard` (19 condition dims) or on `ifc_poisson` (N_hf = 5).

**B2 (target-side LF channel).**
An aux-LF-target head is worth nothing in 15/15 dataset × N cells.
B2 also established that the `ifc_poisson` rung ladder is **unpairable**: 0% of rows pair to their nearest condition under the `lf[:n_hf]` rule, so no ifc LF-paired arm may be built on that rule (the same defect the r2s2-B1 builder and code-reviewer independently reproduced — independent condition draws per rung, min condition distance 0.08–0.30, never 0; `state/maintainer_report.md` lines 44, 85).

**B3 (input-side LF channel).**
The LF teacher's residual advantage is **realisation information** — domain-scale, ~100% unreachable from the condition; the reachable component measures +0.0020 to +0.0038 skill units against thresholds 50–90× larger.
Because the stripped test view carries no LF at all (program.md §5 immutable 9), every stream's test-time predictor is condition-only, so B3's spectral result **bounds** what any stream can produce at test on the sharp panel, not just this card's arm.
Part 7 ships two promoted tools (`ledger_contamination_audit.py`, `band_retention_probe.py`) and four cross-stream notes.

## The open question entering batch 4 (B3 part 7, read in full)

Part 7's verdict is explicit: **no fourth diagnostic is warranted on the sharp panel; ONE is defensible on `ifc_poisson` only.**
The candidate is the stream's single un-executed §12.4 mandate — *overfitting anatomy at N_hf ∈ {5, 20, 50} on the ifc ladder* (train/test gap decomposition, effective sample counts, the drift-class rule "when n_eff/N < 1%, only in-job paired controls are controls").
The case for it: `ifc_poisson` is the only panel dataset with a live round success criterion (the paper bar, `reference_type: paper_bar`, `test_nrmse: 0.036`, `state/anchors/floors.json`), the only one where B1's ceiling estimator had no support, and the only one B2 and B3 both scoped out.
The recorded counter-argument the brainstormer must weigh: at N_hf = 5 the drift-class rule plus the unpairable ladder make **"unclaimable" a real outcome** — a diagnostic result, but not an action-changing one — against a certified `min_claimable_effect` of 0.93770 on a per-dataset skill of 7.94/8.26.
Part 7's recommendation: **close the stream unless the live ifc criterion is still judged reachable**; the brainstormer owns the decision.

## Prior websearch state (binding, do not re-derive)

`websearches/r2s4_diag/batch_3/report.md` (6 turns, cap exceeded by one — recorded), plus batch_1 and batch_2 reports.
Batch-3 verdicts still in force: D1 teacher-projection `preempted-but-MF-composition-open`; D2 coverage-greedy selection `preempted`; D2b training-free regime classifier `preempted-but-MF-composition-open`; D3 metric restatement `preempted-but-MF-composition-open`.
Directly relevant to batch 4: batch-1/2 citations bind that **at N_hf = 5 no ceiling / information-gap claim is defensible** (Lipschitz-operator sample complexity, https://arxiv.org/abs/2410.23440), and MF scaling laws (https://arxiv.org/abs/2511.01830).
Batch-3's do-not-cite list and dead-end list remain in force (notably: `sciencedirect.com/.../abs/pii/*` returns HTTP 403; no arXiv `/pdf/` fetches).

In-repo literature reports (`docs/reports/MF_Leaderboard_Beaters_2026_Report.md`, `docs/reports/MF_Sharp_HighFreq_Report.md`) are prior websearches by another agent and are cited, not re-derived; neither addresses few-shot sample-complexity anatomy or benchmark-criterion retirement, which is what this batch needs.

## What batch 4 must search

1. Sample-complexity / overfitting anatomy at extreme few-shot (N ∈ 5–50) for PDE surrogates and operator learning — is a train/test-gap decomposition at that N published?
2. Learning curves and double descent at tiny N for field/function regression.
3. **Unpaired multi-fidelity ladders** (independent parameter draws per fidelity level) — what claims do they support, and is the pairing requirement stated anywhere?
4. Benchmark-design literature on **when a success criterion should be retired vs pursued** (negative-result / stopping-rule methodology).

The loop must END with a retrieval-grounded prior-art verdict on (a) the ifc overfitting-anatomy card and (b) close-now.
