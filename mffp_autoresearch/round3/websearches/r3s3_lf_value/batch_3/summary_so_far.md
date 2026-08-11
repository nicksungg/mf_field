# summary_so_far — stream `r3s3_lf_value`, batch 3

## 1. Binding slot scope (operator, not negotiable)

`state/batch3_scope_2026-08-10.md` (read 2026-08-10): **r3s3_lf_value — ONE card: knee-predictability**, registered against the certified film-transfer baseline (`state/anchors/film_denominator.json`, ADR r3-0006 units), NOT against copy-LF.
Clause-hygiene rules in that doc's §"Batch-3 clause rules" bind the brainstormer: no falsification threshold inside the fold-to-fold spread of its own statistic; enumerate the C(N_tr, n_fit) fold population instead of spending seeds at n_fit <= 5; statistics on energy-weighted or held-out-loss quantities; every batch-3 family adopts `models_r3/_common/ckpt_binding.py`; claims priced against an `nn_condition` best floor carry that arm's fit-set noise band.

## 2. Where the stream stands

- **B1** (`experiment_cards/r3s3_lf_value/batch_1/`): LF-at-train's value on the honest panel is *entirely the supply of distinct condition rows* — E_cov/E_total in [0.972, 1.024] on 30/30 cells; the covered-only arm `A2_lf_covered` is the same learned function as `A0_nolf`.
- **B2** (`experiment_cards/r3s3_lf_value/batch_2/B2.json`, 150 legs, 3 seeds, all COMPLETED): delivered the coverage-ladder **knee** and an exchange rate on `sharp__cahn_hilliard` + `ifc_heat`. Two results matter for batch 3:
  1. A **training-free surrogate** (`tools/coverage_knee_surrogate.py` — RBF kernel-ridge on standardised conditions -> copy-LF-lifted fields, no GPU, no checkpoint) reproduced the trained 200-epoch FNO ladder at Pearson **0.9842** (ch, 63 cells) and **0.9774** (ifc_heat, 21 cells), placed its step-max knee on the **same cap** (80 and 5), and matched ch's deciding step to 2.0 % of one `tau_rel`. Both were **post-hoc fits to ladders that already existed**.
  2. `sharp__cahn_hilliard` has a hard ceiling: 27 of 100 test rows carry 52-64 % of residual error at full LF supply, have **no knee**, and are unmoved by 8x the HF budget (`7_gap_and_future.cross_stream_notes` item 3; corroborated independently by r3s1-B1's two-population split).
- **B2 part-7 `next_direction` (the slot's own mandate)**: run the surrogate on the **film-transfer cells** and **emit the predicted knee caps as a pre-registered clause before any leg is launched**; falsify on the **step-max knee cap** (the seed-stable statistic), *not* an absolute R threshold (part 5's 0.90 knife-edge: seed 1 at 0.89838, 6.5 % of a `tau_rel` under the line); run a **minimal 3-cap confirming ladder** bracketing the prediction; carry the stratified readout (`--strat-mask`) from the start; do **not** re-run the D-D mediator clause in its B2 linear-fit form.

## 3. Prior-art state inherited (all citations already retrieved, do not re-derive)

`websearches/r3s3_lf_value/batch_2/report.md` verdicts, still binding:
- **C1** LF-count sweep genre -> *preempted* (Kirby et al., https://arxiv.org/pdf/2301.01699, fetched: LF 250->500 helps, 500->1000 does not, "because the number of high-fidelity training points is fixed"; benchmark grid https://arxiv.org/pdf/2408.17075, n2 = {1,5,10}xn1 x 10 DoEs). "**The finding must be the measured knee and exchange rate, never the sweep.**"
- **C2** "LF covers what HF does not" -> *mechanism sentence preempted outright* (Kim et al., https://arxiv.org/html/2409.07947v1).
- **C3** forward-sensitive hard subpopulation -> *preempted-but-MF-composition-open, leaning novel*; terminology hazard on "non-identifiable" (PLOS pcbi.1013553).
- Batch-1 D3: any teacher/distillation arm is **preempted**, baseline only.
- Batch-2 **under-searched** dead end flagged for re-run here: sensitivity-screen / local-Lipschitz angle (two WebSearch "unavailable"s).

The two in-repo literature reports (`docs/reports/MF_Leaderboard_Beaters_2026_Report.md`, `MF_Sharp_HighFreq_Report.md`) contain **no** scaling-law / learning-curve / knee material (grepped: one incidental "sample-efficient" line) — nothing to inherit for this batch.

## 4. Open question this batch's search must price

The batch-2 verdicts covered *the sweep*. They did **not** cover the new object: **a-priori (pre-registered) prediction of a sample-efficiency knee from a cheap training-free descriptor**, then confirmation on a held-out cell. Search must therefore refute novelty on four fronts: (a) learning-curve extrapolation / scaling-law breakpoint prediction; (b) broken/piecewise power-law fitting with *pre-declared* breakpoints and knee-detection methodology; (c) multi-fidelity budget allocation / value-of-data — when does adding LF stop substituting for HF; (d) training-free / zero-cost proxies that predict sample efficiency (kernel-ridge or NTK surrogates for a neural learning curve). Additional target: whether anyone has **registered a pre-declared quantitative knee prediction and then tested it** for MF PDE surrogates, versus the standard post-hoc curve description.

## 5. Noise-floor discipline carried in

Certified `tau_rel`: ch **0.36124864** (x copy-LF ref 0.04180296 = 0.015101 nRMSE), ifc_heat **0.16401958** (x 0.074 = 0.012137 nRMSE) — `state/anchors_repaired/noise_floor.json` lineage via B2. In **film units** (`state/anchors/film_denominator.json`): ch film denominator 0.69475, c_ds 0.0601698; ifc_heat film denominator 0.0361336, c_ds 2.04796. Any knee that moves by less than one `tau_rel` is not a knee.
