# Summary so far — stream `r2s4_diag`, batch 3

## Where the stream stands

`r2s4_diag` is the round's **diagnostics** stream (program.md §12.4): value-of-LF accounting,
overfitting anatomy at small N, floor certification. Two batches are closed.

**B1** (`experiment_cards/r2s4_diag/batch_1/B1.json`, `complete`) certified the floors and
replaced the provisional noise floor. Its 3-seed condition→HF certifier (`r2s4_cert_min`,
FiLM-FNO decoder, smoke tier) is now the stream anchor (`state/anchors/r2s4_diag.json`:
`certified_3seed_panel_geomean` **19.8178**, CI95 [19.3853, 20.5271], superseding the
training-free floor anchor 23.0636) and the installed `state/noise_floor.json` (panel
`min_claimable_effect` **1.1419**; per-dataset MCEs helmholtz 2.953, ifc_poisson 0.938,
allen_cahn 0.880, cahn_hilliard 0.091, fisher_kpp 0.00071, pfc 0.213). **Anything inside those
intervals is noise, not signal.**

**B2** (`experiment_cards/r2s4_diag/batch_2/B2.json`, `complete registered`, 18 findings over 3
mechanism turns) ran the matched ±LF-training-signal contrast (arms `T0_cond_only`,
`T1_lf_aux`, `I1_lf_teacher`, `I2_lf_ablated`) with an N_fit sweep {20, 80, 320}. Headline
licensed result: **the auxiliary-LF-*target* head is worth nothing at any N** — |T1−T0| below
threshold in 15/15 dataset×N cells on an instrument that resolves the N-effect at 7.4–101× the
certified floor (T3-F4). Mechanism: the upsampled-LF target is a *duplicate* of the HF target
(cos ≥ 0.997, Δidentifiability ≤ 0.0015 — T1-F1), except on `ext__helmholtz_2d` (cos 0.3099,
harmful direction — T1-F2). Explicitly **not** licensed: "LF doesn't help" — the input-side and
disjoint-supply channels are untouched, and r2s3-B2 shows a large single-seed positive on
ifc_poisson's 170 disjoint LF rows (`state/maintainer_report.md`; B2 part 7 item (d)).

## What B2 leaves open (the B3 candidate set)

From `7_gap_and_future`:

- **Option A (analyst-recommended)** — the **teacher-projection diagnostic**: fit an
  out-of-fold condition→prediction map (kNN or ridge) to the LF-teacher arm's own test
  predictions and score `proj(I1)` against `T0`. `proj(I1) ≈ T0` ⇒ the teacher's edge is
  realisation information no train-only channel can carry (the round could close criterion 1
  with a certified "no channel exists"); `proj(I1) ≪ T0` ⇒ an optimisation/architecture failure.
  B2 predicts the first on 4/5 datasets, with helmholtz the only place it could differ.
  Blocker: B2 shipped no predictions/checkpoints — needs one cheap matched training leg.
- **Option B** — **support repair on `sharp__cahn_hilliard`**: the panel's one sample-limited
  dataset (slope b = 0.2327 on [80,320], accelerating; only 24.8% of its asymptotic gain
  realised at N=320; d_min 3.1178 in 19 standardised dims — T3-F1..F3). Under immutable §5.11
  (no new HF data) the only lever is *which rows are fit on*: coverage-greedy fit-fold
  selection at fixed N_fit vs the nested random prefix. Companion: λ* = 1.117 > 1 there
  (expand, not shrink — T3-F6).
- **Round-level rule candidate** — identifiability × support (d_min) predicts the trained
  learning-curve regime **training-free**, 5/5 datasets (T3-F3), in ~35 s/dataset via the
  promoted `tools/condition_predictability_ceiling_fast.py`. Labelled a *candidate* until a
  second card reproduces it.
- **Metric caveat (b)** — helmholtz's 3-seed spread is 1.6363 skill units mean-of-ratios vs
  0.0656 energy-pooled (24.9×), spearman(rel-L2, ‖y‖) = −0.673; no helmholtz arm contrast is
  claimable at 3 seeds. nRMSE is immutable (§5.4) — the fix is interpretive.

## Prior websearch state (do not re-derive)

`websearches/r2s4_diag/batch_1/report.md`: D1a seed-protocol `preempted` (Agarwal
IQM/stratified bootstrap; Du paired protocol); D1b floor panel
`preempted-but-MF-composition-open`; D2 value-of-LF `preempted-but-MF-composition-open` (Yang
et al. LUPI non-monotone law); D3 overfitting anatomy LOW confidence.
`websearches/r2s4_diag/batch_2/report.md`: **binding instruction — do not propose "build a
ceiling estimator"** (D2 `preempted`, the 19-dim failure is theorem-level, and at N_hf = 5
arXiv:2410.23440 forbids a defensible ceiling claim); DOPD advantage-gap split adopted;
shrinkage = James-Stein, sell λ* as the diagnostic; **n_eff still uncited after two batches** —
must be defined locally as a project convention. Both batches' do-not-cite lists remain in
force.

In-repo literature reports (prior websearches by another agent — cite, don't re-derive):
`docs/reports/MF_Sharp_HighFreq_Report.md` §0.3 establishes that MSE + rel-L2 structurally
prefer blur and that "the SURF metric panel matters as much as any architecture change" —
directly relevant to the B2 metric caveat and to reading λ* < 1 collapse.
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` is architecture-side (flow-matching
residual distillation, `mf_fno_flowdelta`) and only marginally relevant to this diagnostics
batch.

## Open questions this batch must resolve

1. Is "project a privileged-information teacher onto the observable-feature σ-algebra and score
   the projection" a published diagnostic (LUPI / distillation theory)?
2. Is coverage-greedy / space-filling subset selection **at fixed budget from an existing pool**
   a published lever for surrogates, and is it ever reported as a *diagnostic* of a
   support-limited regime rather than as a data-reduction or active-learning method?
3. Is there prior art for predicting the learning-curve regime **training-free** from
   nearest-neighbour support statistics in the parameter space?
4. Is the mean-of-ratios vs energy-pooled relative-L2 discrepancy a documented artifact?
