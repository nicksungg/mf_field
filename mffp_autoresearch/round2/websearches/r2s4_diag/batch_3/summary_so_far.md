# summary_so_far — `r2s4_diag`, batch 3

*(A prior invocation of this batch was killed mid-run; its files were treated as
untrusted per the orchestrator's instruction and archived to
`_untrusted_prior_attempt/`. Nothing in them is cited. This loop restarts clean.)*

## Where the stream stands

**B1** (`experiment_cards/r2s4_diag/batch_1/B1.json`, complete) certified the
condition→HF 3-seed spread that now IS `state/noise_floor.json`
(`_source: r2s4_diag-B1 …, family r2s4_cert_min`, `_provisional: false`):
per-dataset `min_claimable_effect` = helmholtz 2.95299, pfc 0.21303,
allen_cahn 0.87970, fisher_kpp 0.00071, cahn_hilliard 0.09125, ifc_poisson
0.93770; panel-geomean MCE 1.14187 with certified panel geomean 19.8178 (the
stream's own anchor, `state/anchors/r2s4_diag.json`; launch anchor = best-floor
geomean 23.0636, `state/anchors/floors.json`). It reproduced the frozen floors
exactly and produced a training-free per-dataset conditional-mean/kNN barrier.

**B2** (`experiment_cards/r2s4_diag/batch_2/B2.json`, complete; verdict
*falsified* by a null-firing clause) ran the value-of-LF accounting: arms
T0 (condition-only), T1 (auxiliary-LF-target head), I1 (LF-teacher input, inner
fold only), I2 (LF-ablated). Load-bearing part-6 results:
- **Target-side LF is a certified null**: |T1−T0| below its operative threshold
  in 15/15 dataset × N cells, on an instrument that resolves the N-effect at
  7.4–101× the certified floor (T3-F4). Mechanism: the aux LF target is a
  *duplicate* of the HF target (cos ≥ 0.997, Δidentifiability ≤ 0.0015, T1-F1).
- **Input-side LF advantage is large and claimable** (information gap
  I2/I1 = 3.16–95.3 on 5/5 non-anecdote datasets) but has **no test-time code
  path** in this round (immutable §5.9).
- **Support, not identifiability, sets the sample-size regime** (T3-F3): 4/5
  datasets are within 0.8 % of their N→∞ asymptote at N_fit = 320; cahn_hilliard
  alone is sample-limited (slope 0.2327 on [80,320] and accelerating; d_min
  3.1178 in 19 standardised dims).
- **helmholtz is metric-dominated**: the same shipped predictions give a 3-seed
  spread of 1.6363 skill units under the round's mean-of-ratios vs 0.0656
  energy-pooled (24.9×; spearman(rel-L2, ‖y‖) = −0.673) — no helmholtz arm
  contrast is adjudicable at 3 seeds (T2-F5).
- **ifc_poisson LF pairing is void** (`lf = lf[:n_hf]` index-alignment fails on
  the ifc_raw ladder, T2-F6) — B3 must not build an LF-paired ifc arm on it.

B2 part 7 names two B3 options: **(A, recommended)** the *teacher-projection*
card — fit an out-of-fold condition→prediction map to the LF-teacher arm's own
predictions and score `proj(I1)` against T0, deciding whether ANY of the
teacher's advantage is condition-expressible (i.e. whether a train-only
distillation channel can exist at all); **(B)** coverage-greedy fit-fold
selection on cahn_hilliard, the one support-limited dataset, with a
training-free identifiability × d_min go/no-go. Binding constraints from B2:
helmholtz report-only, no ifc LF-paired arm on `lf[:n_hf]`, dump per-arm test
predictions.

## Prior websearch state for this stream (do not re-derive)

`websearches/r2s4_diag/batch_1/report.md`: D1a `preempted` (Agarwal IQM +
stratified bootstrap; Du paired per-seed deltas), D1b/D2/D3
`preempted-but-MF-composition-open`. `websearches/r2s4_diag/batch_2/report.md`:
D1 (value-of-LF accounting) `preempted-but-MF-composition-open` via DOPD's
advantage-gap split; **D2 (ceiling estimator) `preempted` — do not re-propose
one**; D3 (λ\* as a reported diagnostic column) open; D4 (overfitting anatomy /
n_eff) open with n_eff still uncited after two batches. Both batches' do-not-cite
lists remain in force. The in-repo reports
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` and `MF_Sharp_HighFreq_Report.md`
were grepped for distillation / privileged-information / active-learning / DOE
content: a single architecture-side hit (flow-matching residual distilled to one
step, N2) — not relevant to a diagnostic card.

## Open questions this batch must settle with retrieval

1. Is "**project a privileged/LF teacher onto the student-measurable (condition)
   subspace and score the projection**" published as a *diagnostic* of whether
   privileged advantage is distillable at all (as opposed to a training method)?
2. Is fixed-budget **coverage-greedy training-subset selection** at a known
   sample-limited operating point published, and what composition remains open?
3. Is a **training-free regime classifier** (identifiability × fill distance →
   information-limited vs sample-limited) published?
4. Is the **mean-of-ratios relative-L2 sample-weighting artifact** documented, so
   B3's helmholtz restatement can cite rather than claim novelty?
