# Summary so far — stream `r3s4_audit`, batch 1

## What this stream owns in round 3

`program.md` §4 assigns `r3s4_audit` (class: diag): *"Certify the repaired-panel mce and floors; run the training-free instrument audits (including the repaired-ifc audit); own the close-evidence audits of PROGRAM_NOTE MUST #3."*
`program.md` §3 makes this blocking for the whole round: `state/anchors_repaired/noise_floor.json` is **PROVISIONAL** and "r3s4 re-certifies mce on the repaired panel before any criterion is adjudicated (round-1 §4.5 discipline)."
Round-2 conventions apply verbatim (`../round2/program.md` §12.4): **B1 is pre-directed** — (a) verify the frozen floors reproduce, standing zero-predictor column included; (b) train ONE minimal condition→HF baseline at smoke tier, seeds {0,1,2}, on the panel; its per-dataset seed spread replaces the provisional noise floor.

## State I read

- `state/anchors_repaired/noise_floor.json` — `_provisional: true`, `_source: round1-batch0-rescaled`, i.e. per-seed spreads from **LF-consuming** round-1 families rescaled under corrected denominators. Its `min_claimable_effect` values are wildly heterogeneous (ifc_poisson 0.2399, cahn_hilliard 1.1604, allen_cahn 16.42, fisher_kpp 158.33, helmholtz 10.68) and several are the 10%-of-mean-skill fallback rather than a measured spread. This is exactly the file B1 must replace, and it was computed on the **pre-repair** panel (pre ifc swap, pre ac trim, pre pfc crystalline-box swap).
- `state/anchors_repaired/floors.json` (rewritten 2026-08-06 09:51, after the pfc box swap) — per-dataset `nn_condition` / `train_mean` / `zero` arms plus the copy-LF `reference` cell with `_nrmse_def_hash` and `_copylf_def_hash`. Archived pre-change copies: `floors_pre_ifc_swap_2026-08-05.json`, `floors_pre_ac_trim_2026-08-06.json`, `floors_pre_pfc_box_2026-08-06.json`.
- `state/anchors/launch_anchors.json` — best-floor panel geomean **38.63** on the 6-dataset ADR-D4+A1 panel; per-dataset best arms are `train_mean` (pfc, fisher_kpp) or `nn_condition` (ac, ch, ifc_poisson, ifc_heat). `program.md` §2 quotes 75.0673 for the same object; the two numbers disagree because the file was rebuilt after the ac trim / pfc swap and the program text was not. **B1 should reconcile this discrepancy as part of floor certification.**
- `program.md` §2 affine-floor rule: ifc_poisson's condition→HF map is EXACTLY affine (oracle residual 5.4e-16); a fitted `affine_on_hf_train` arm (ifc_poisson skill 1.594, ifc_heat 0.96 — already beating the 0.074 paper bar on 5 rows) is a mandatory reported arm.
- `mffp_autoresearch/preflight/README.md` + `docs/adr/0003-estimator-integrity-repairs.md` — the **fifth defect class, per-cell estimator integrity**, with four instruments already landed: `degenerate_rows` (task-void rows deflate the copy-LF denominator; ≥5% → HARD FAIL), `cell_stability` (bootstrap of the mean-of-per-row-ratios cell; top-5 share > 0.4 or CI half-width > 25% → `OUTLIER_DOMINATED`, always emitting `min_detectable_delta`), `rung_scale_coherence`, and `data_binding.py` (sha256 of dataset arrays, closing the "score cache keys on code_hash but not data bytes" staleness hole). ADR D2 records cahn_hilliard's cell as outlier-dominated: top-5 of 100 rows carry **76%** of the denominator, implying a **~166% minimum distinguishable model delta**.
- `state/preflight_launch_2026-08-05.json` — panel preflight with waivers (helmholtz completeness, sod_1d pairing); pfc showed `fidelity_gap: NO_GAP` at that time, since repaired by ADR r3-0002.

## Prior websearch reports (do not re-derive)

`../../../round2/websearches/r2s4_diag/batch_{1..4}/report.md` are the direct ancestors. Binding verdicts:

- **B1/D1a** — MCE from a 3-seed spread: `preempted` (Agarwal et al. *Statistical Precipice* arXiv:2108.13264; Du *When +1% Is Not Enough* arXiv:2511.19794). Recommendation on record: use IQM + stratified/paired bootstrap CIs and per-seed deltas, not bare max−min; 3 seeds license only LARGE effects.
- **B1/D1b** — training-free floor panel as mandatory arms: `preempted-but-MF-composition-open` (McGreivy & Hakim arXiv:2407.07218 — 79% weak baselines; Westermann arXiv:2604.00689). All *published* floors are fitted; a training-free trivial-predictor panel in copy-LF-skill units was not found.
- **B2/D3** — post-hoc shrinkage / λ* diagnostic: composition open.
- **B3/D2b** — training-free regime classifier: composition open; four framings found nothing.
- **B4/A** — overfitting anatomy at N_hf ∈ {5,20,50}: composition open; **n_eff / effective-sample-size is NOT open** (no usable results across two batches — demoted to descriptive statistic).
- **B4/B′** — futility/equivalence-testing framing for stream closure: novel in composition, preempted in every component.

`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` and `docs/reports/MF_Sharp_HighFreq_Report.md` are model-family literature reports for the **LF-consuming** regime (IRNO, flow-matching residual transport, spectral-bias remedies). They carry no methodology relevant to floor/mce certification; cite them only if a B1 instrument touches spectral metrics.

## Open questions this batch must inform

1. What is the defensible per-dataset claim threshold when there are **two independent noise sources** — model seed variance (numerator) and copy-LF reference-cell estimation error (denominator)? Round 2 certified only the first; ADR r3-0003 D2 landed only the second.
2. Is there published methodology for auditing a **ratio/skill-score benchmark cell** for denominator pathology (degenerate rows, outlier domination, mean-of-ratios vs pooled)?
3. Is byte-level **data↔artifact binding** (hash-gated caches/references) an established benchmark-integrity practice, or a project-local invention?
4. What is the nearest published practice for certifying a **training-free floor panel** — including a closed-form/affine floor — as mandatory reported arms for a parametric-PDE surrogate benchmark?
