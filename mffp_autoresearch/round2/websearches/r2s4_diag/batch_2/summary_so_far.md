# Summary so far — stream `r2s4_diag`, batch 2

## Where the stream stands

B1 (`experiment_cards/r2s4_diag/batch_1/B1.json`, `status: complete`) was the
round's certification card: a 1M-param condition-only FiLM-FNO decoder
(`r2s4_cert_min`) at smoke tier, seeds {0,1,2}, plus training-free floor
reproduction. It delivered three things the round now runs on:

1. **A certified anchor** (`state/anchors/r2s4_diag.json`): 3-seed panel geomean
   skill **19.8178**, CI95 [19.3853, 20.5271], superseding the training-free
   best-floor anchor 23.0636. Per-dataset mean skill: helmholtz 6.944,
   ifc_poisson 8.261, allen_cahn 147.32, cahn_hilliard 13.178, fisher_kpp 11.558,
   pfc 47.847.
2. **A certified noise floor** (`state/noise_floor.json`, `_provisional: false`):
   panel `min_claimable_effect` **1.1419**; per dataset 2.9530 (helmholtz),
   0.9377 (ifc_poisson), 0.8797 (allen_cahn), 0.0912 (cahn_hilliard), 0.00071
   (fisher_kpp), 0.2130 (pfc). Protocol: Agarwal et al. IQM + stratified
   bootstrap, Du paired per-seed deltas — both adopted on batch-1's websearch
   advice (`websearches/r2s4_diag/batch_1/report.md`, verdict row D1a).
3. **A measured aleatoric barrier** (card `6_analysis`, `7_gap_and_future`):
   two train-only estimators (noise-debiased LOO k-NN bound; matched-pair
   extrapolation to zero condition distance) put the certifier at 1.010x the
   barrier on fisher_kpp, ~1.11x on allen_cahn, 1.139x on pfc, but **1.655x** on
   helmholtz. cahn_hilliard (min train-pair distance 2.822 in 19 dims) and
   ifc_poisson (5 train samples) admit **no** training-free ceiling estimate.
   Promoted tools: `tools/condition_predictability_ceiling.py`,
   `tools/conditional_mean_collapse.py`.

## What B1's part 7 asks B2 to do

`7_gap_and_future.next_direction` names four items: (1) run the matched
+/-LF-training-signal contrast **on helmholtz first** (only certified headroom),
with fisher_kpp/pfc/allen_cahn as **pre-registered null** datasets; (2) build a
ceiling estimator that works at 19 condition dims and at N_hf = 5, where the
current pair/k-NN estimators have **no support**; (3) make **post-hoc shrinkage
toward the model's own mean field**, calibrated on a held-out TRAIN fold, a
required arm on every card (worth 43% on helmholtz; test-fitted oracle lambda* = 0
on helmholtz, 1.0 on pfc/allen_cahn/fisher_kpp, 1.1-1.5 on cahn_hilliard/ifc);
(4) re-certify the seed spread on whatever arm B2 compares.

## Cross-stream context that changes B2's framing

`state/maintainer_report.md` (runs 2026-07-31T18:14Z / 18:31Z): **r2s3-B1 is
`cratered` / `falsified`** — the LF-as-training-signal arm (`rung_native`,
panel geomean 25.3919) lost to its own `hf_only` control (26.8687) except on the
report-only helmholtz column, and on ifc_poisson it *inverted* (16.80 vs 9.45,
7.35 units the wrong way, ~7.8x the certified floor). r2s2-B1's headline: the
pseudo-LF stack adds ~nothing on 5/6 paired panel datasets. So B2's value-of-LF
accounting is no longer measuring an expected gain — it is adjudicating a
**measured near-zero-or-negative** LF effect, which is exactly the regime where
Yang et al.'s non-monotone LUPI law (pre-registered in B1's
`expected_falsification`, https://arxiv.org/abs/2209.08754) predicts harm.

## Open questions this batch must serve

- **Q1 (D2)**: is there a published estimator of the *irreducible / aleatoric*
  error of a parametric-map regression that works with ~400 samples in 19 dims
  and with N = 5? (B1's estimators are essentially difference-based /
  nearest-neighbour variance estimation — near-certainly preempted; the question
  is by what, and what the high-dimensional remedy is.)
- **Q2 (D3)**: is post-hoc shrinkage of a surrogate's prediction toward its own
  conditional mean a published calibration operation, and is reporting it as a
  mandatory arm novel?
- **Q3 (D1)**: is a matched +/-privileged-signal contrast with **pre-registered
  null datasets certified by an information/aleatoric argument** published?
- **Q4 (D4, deferred)**: batch 1 rated the overfitting-anatomy direction
  (train/test gap decomposition, n_eff at N_hf in {5,20,50}) **LOW confidence**
  after one dedicated search and explicitly asked for a fresh batch before any
  card leans on it. This batch owes it a real pass.

## Prior websearch and in-repo literature

- `websearches/r2s4_diag/batch_1/report.md`: verdicts D1a `preempted`, D1b/D2/D3
  `preempted-but-MF-composition-open`; carries a **do-not-cite list**
  (unverified snippet numbers: FNO scaling rate r=0.28, 60.1K samples, SPDEBench
  factor-of-two, the 20-sample MF anecdote) that still binds.
- `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` and
  `docs/reports/MF_Sharp_HighFreq_Report.md` (prior websearches by another
  agent): grepped for `aleatoric|irreducible|shrink|calibrat|effective sample|
  generalization gap|Bayes error`. Both are LF-consuming-mechanism reports
  (residual learning, frequency-calibrated diffusion guidance, elastic Bayesian
  calibration, GP-on-operator-embeddings UQ); the only near-adjacent item is
  FreqNO-DPS's finding that isotropic fusion re-imports a surrogate's spectral
  bias and only frequency-calibrated weighting removes it
  (`MF_Leaderboard_Beaters_2026_Report.md` lines 32/102-108) — an amplitude/
  frequency-calibration precedent worth keeping next to Q2's shrinkage arm.
  Neither report covers aleatoric-ceiling estimation, seed statistics, or
  tiny-N overfitting diagnostics; nothing to re-derive from them here.
