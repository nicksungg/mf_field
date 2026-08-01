# Summary so far — Stream `r2s4_diag`, Batch 3

All paths relative to `mffp_autoresearch/round2/` unless absolute.

## 1. Websearch findings + prior-art verdict (batch 3)

Source: `websearches/r2s4_diag/batch_3/report.md` (6 turns / 18 WebSearch / 12 usable
WebFetch; returned PARTIAL for a 1-turn cap overrun, content complete). The quarantined
`_untrusted_prior_attempt/` is cited nowhere here.

Verdict rows: **D1** teacher-projection / distillability ledger =
`preempted-but-MF-composition-open (cite)`; **D2** coverage-greedy fixed-budget selection =
`preempted (cite)`; **D2b** training-free regime classifier =
`preempted-but-MF-composition-open (cite)`; **D3** helmholtz metric restatement =
`preempted-but-MF-composition-open (cite)`.

The D1 "what remains open" column reads verbatim: *"Splitting privileged advantage into
reachable/unreachable is published - but **no fetched source fits a map from student-observable
inputs to the teacher's own predictions and scores that projection in the task metric**
(AR-OPD: "No explicit function is fit"; CCH is representation-level for classification labels;
ViCuR is a design principle). Nothing for a **field-valued** output in **copy-LF skill** units
with a **coarse PDE solve** as the privileged channel and a **realized random IC** as the
unobservable component; nothing pre-registers the outcome from an independently measured
training-free barrier."*

Binding instructions for me (report section "For the brainstormer"): propose D1 and **sell the
projection, not the distillation**; adopt AR-OPD's total/partial/marginal vocabulary *by
citation* (https://arxiv.org/html/2606.10385v1) rather than inventing statistic names (B2's
`transfer_efficiency` type-mismatch is the cautionary tale); cite
https://arxiv.org/html/2505.09546 ("the student state ... is given by a surjective mapping
f(s~)=s") for the aliasing structure instead of asserting ADR r2-0003; use TRIE
(https://arxiv.org/html/2607.00196) for "deterministic pointwise scoring of a stochastic map
measures a conditional mean"; **do not** propose a bare distil-the-LF-teacher card (preempted
in the surrogate domain itself, S0952197625034293, search-result confidence, fetch 403 - and
it is r2s3's territory); **no ceiling estimator, no n_eff claim**; helmholtz stays report-only
and the mean-of-ratios artifact is **project-local/uncited**; no ifc_poisson LF-paired arm on
the `lf[:n_hf]` rule. Do-not-cite lists from batches 1-3 are binding.

## 2. program.md §12.4 conventions (verbatim, program.md lines 399-417)

> ### 12.4 `r2s4_diag` (diagnostics)
>
> - **B1 is pre-directed**: floor + spread certification. (a) Verify the frozen
>   floors reproduce (standing zero-predictor column included); (b) train ONE
>   minimal condition→HF baseline (smallest reasonable FiLM-FNO decoder or
>   MLP→field) at smoke tier, seeds {0,1,2}, on the panel — its per-dataset
>   seed spread replaces the provisional `state/noise_floor.json` (§4.3).
>   Diagnostic card, but WITH training (3 seeds) — the exception is the point;
>   cheap by design (small model).
> - Later batches: **value-of-LF accounting** — matched architecture ± LF
>   training signal (coordinates with r2s3: r2s4 measures, r2s3 optimizes);
>   **overfitting anatomy** at N_hf ∈ {5, 20, 50} (ifc ladder) and N=400
>   (sharp): train/test gap decomposition, effective sample counts (the
>   **drift-class rule**: when n_eff/N < 1%, only in-job paired controls are
>   controls).
> - The round-1 probe library is seeded in `tools/` (37 files; index header
>   notes they were written against round-1 eval paths — adapt on use, promote
>   adapted versions via the register turn).

Also binding (program.md 12 preamble): quote the launch anchor and the floor table; clear the
noise floor; cite the prior-art verdict; complete recipe. Stream anchor
(`state/anchors/r2s4_diag.json`) is now `certified_3seed_panel_geomean` **19.817845**
(CI [19.3853, 20.5271]), superseding the training-free launch anchor 23.063617.

## 3. Within-stream prior cards

**`r2s4_diag-B1`** (`experiment_cards/r2s4_diag/batch_1/B1.json`, complete, diagnostic):
certified the floors and installed `state/noise_floor.json` from a 3-seed condition->HF
FiLM-FNO (`r2s4_cert_min`, 200 ep). Certified per-dataset `min_claimable_effect`:
helmholtz **2.952992**, pfc **0.213027**, allen_cahn **0.879705**, fisher_kpp **0.000714**,
cahn_hilliard **0.091245**, ifc_poisson **0.937704**; panel **1.141867**.

**`r2s4_diag-B2`** (`batch_2/B2.json`, complete, diagnostic, 3 seeds by reviewer adjudication):
value-of-LF accounting, arms `T0_cond_only` / `T1_lf_aux` / `I1_lf_teacher` / `I2_lf_ablated`,
folds fit 320 / val 40 / inner 40 at `SPLIT_SEED=0`. Key measured facts I depend on:
- Target-side channel **closed**: |T1-T0| inside its operative threshold in **15/15**
  dataset x N cells (T3-F4/T3-F5), on an instrument that resolves the N-effect at
  7.42x/11.57x/27.61x/101.12x the certified floor.
- **Input-side teacher advantage is huge and claimable 5/5**: inner-fold skill
  `I1_lf_teacher` vs `T0_cond_only` = 0.3840 vs 36.363 (pfc), 5.653 vs 120.156 (allen_cahn),
  0.8376 vs 11.323 (fisher_kpp), 0.2944 vs 11.916 (cahn_hilliard), 2.756 vs 6.829 (helmholtz);
  information gap ratios I2/I1 3.16-95.3.
- **Why**: the teacher is a near-identity of LF and LF is a near-copy of HF on the sharp panel
  (T1-F3 train copy-LF rel-L2: allen_cahn 0.00194, pfc 0.00643, cahn_hilliard 0.00937,
  fisher_kpp 0.02086, **helmholtz 0.26506**; T1-F1 centred cos(HF, LF-up) >= 0.997 on the four
  sharp, **0.3099 on helmholtz**, T1-F2).
- **Support-vs-information taxonomy** (T3-F3, proposed round-level rule *candidate*, needs a
  second card): identifiability x d_min predicts the learning-curve regime 5/5; cahn_hilliard
  is the panel's ONE sample/support-limited dataset (b = 0.2327 accelerating, d_min 3.1178 in
  19 standardised dims), the other four are information-limited.
- **T0 fold-fixed 3-seed spreads** (usable as inherited in-job thresholds): helmholtz 1.63633,
  pfc 0.283728, allen_cahn 0.919152, fisher_kpp 0.000459, cahn_hilliard 0.184746.
- **Blockers recorded**: B2 shipped no per-arm predictions/checkpoints, so the projection
  cannot be run as re-analysis; helmholtz must not adjudicate any arm contrast (T2-F5:
  3-seed spread 1.6363 mean-of-ratios vs 0.0656 energy-pooled, 24.9x); ifc_poisson must carry
  no LF-paired arm built on the `lf[:n_hf]` rule (T2-F6: 0% of rows paired to nearest
  condition).
- Part 7 `next_direction`: **Option A (recommended)** = the teacher-projection card;
  Option B = coverage-greedy support repair on cahn_hilliard, with a training-free go/no-go.

## 4. Cross-stream cards touching this stream

- `r2s3_lf_train_signal/batch_2/B2.json` (analyzing): the **supply** channel - ifc_poisson
  `A0_nolf` skill 8.13438 -> `A1_lf_cov` 2.16899 -> primary `A2_lf_cov_null` 3.45497 (single
  training seed, N_hf=5 anecdote-grade). B2's part-7 reporting instruction (d) says B2 and
  r2s3-B2 must be reported together: target-side LF is a certified null, disjoint-condition
  supply-side LF demonstrably is not.
- `r2s2_stacked/batch_2/B2.json` (analyzing) and `r2s1_direct/batch_2/B2.json` (running) -
  scanned; neither adds a constraint on this batch beyond the shared floors/anchor.

## 5. Reopen candidates

**None.** All eight round-2 cards carry `reopen_candidate: false` (verified by reading every
`experiment_cards/*/batch_*/B*.json`). Nothing to retry or drop.

## 6. What is UNKNOWN

1. **Is any of the LF teacher's advantage a function of the condition?** B2 measured the
   advantage (10.5-114.5 skill units on the sharp panel) but never asked whether a
   condition-only map could reproduce any of it. This is the last untouched channel of
   success criterion 1 and the round's cleanest closure statement.
2. **Structural constraint nobody has priced**: under 5.9 the teacher has *no test code
   path* (test LF is physically absent), so B2's part-7 phrasing "fit ... to the LF-teacher
   arm's own **test** predictions" is not implementable. Any projection must be measured on
   **held-out TRAIN rows** - and B2 shipped no predictions, so it needs fresh training.
3. **Is the sharp-panel answer arithmetically pre-determined?** If the teacher ~ HF
   (cos >= 0.997), regressing teacher outputs on the condition ~ regressing HF on the
   condition = what T0 already does, so "reachable ~ 0" may follow from T1-F3 rather than
   from the experiment. Unknown whether the residual - the teacher's output is a *band-limited*
   HF, i.e. a smoothed label - buys a distillation student anything (classic soft-label
   variance reduction). Nobody has measured that here.
4. **ext__helmholtz_2d is the one place the answer could differ** (cos 0.3099, train copy-LF
   rel-L2 0.2651, teacher beats T0 by 4.07 inner skill units) - and is exactly the dataset the
   round's mean-of-ratios metric cannot adjudicate at 3 seeds (T2-F5). Whether a dual-column
   (scored mean-of-ratios + interpretive energy-pooled) protocol can carry it honestly is open.
5. **Is B2's support-vs-information taxonomy reproducible on a second card?** The maintainer
   was asked to keep it a *candidate* until reproduced. If cahn_hilliard (support-limited) is
   the only dataset with a reachable component, that is the second card.
6. **Can a 1-seed card certify any of this?** The strict-1-seed protocol (project.yaml
   `seeds: [0]`) means in-job paired controls must supply the variance (drift-class rule). A
   k-fold rotation gives k in-job paired deltas at one training seed - untested in this round.
7. Not unknown, deliberately out of scope: absolute ceilings / n_eff (both preempted or
   undefensible at N_hf=5, arXiv:2410.23440), and ifc_poisson LF pairing (defect T2-F6).
