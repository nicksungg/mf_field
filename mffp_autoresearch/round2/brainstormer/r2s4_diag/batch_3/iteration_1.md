# Iteration 1 — Stream `r2s4_diag`, Batch 3

## Design context considered

- `summary_so_far.md` section 6 (unknowns) and the batch-3 D1 verdict row
  (`preempted-but-MF-composition-open (cite)`).
- program.md 12.4 verbatim (summary section 2); 5 immutables 1-8 + round-2 additions 9-13;
  2.2 floor arms; 2.3 panel table; 4.2 strict 1-seed.
- Stream anchor `state/anchors/r2s4_diag.json` = `certified_3seed_panel_geomean` **19.817845**
  (supersedes the training-free 23.063617, preserved in `supersedes`).
- Certified per-dataset `min_claimable_effect` (`state/noise_floor.json`, `_provisional:false`):
  helmholtz 2.95299157437233, pfc 0.21302734961699343, allen_cahn 0.8797047190126648,
  fisher_kpp 0.0007136812826775696, cahn_hilliard 0.09124535322300886,
  ifc_poisson 0.9377041289531141; panel 1.1418668211296108.
- Frozen floors (`state/anchors/floors.json`): best floor per panel dataset - helmholtz zero
  3.3441, pfc train_mean 59.8118, allen_cahn nn_condition 269.1959, fisher_kpp train_mean
  11.9931, cahn_hilliard nn_condition 23.1803, ifc_poisson nn_condition 10.0549.
- `r2s4_diag-B2` parts 5/6/7 (numbers reproduced in summary section 3), including the three
  binding B3 constraints and the "no shipped predictions" blocker.
- `state/timing_ledger.json`: B2 = 44 trainings + 22 ifc LOO legs + 2-epoch guard leg in
  **17.25 min** on h200 (job 66181609); B1 = 6 trainings in 4.42 min.
- Orchestrator notes: last diagnostic batch of the round; favour the card that closes
  value-of-LF accounting for the round report; **strict 1 seed**.

## Proposal reasoning

### Alternatives weighed

**(A) D1 teacher-projection channel ledger — CHOSEN.** B2's part 7 recommends it, the
batch-3 websearcher's instruction 1 says "Propose D1 (Option A), and sell the projection, not
the distillation", and it is the only untouched channel of success criterion 1. B2 proved a
large input-side teacher advantage (10.5-114.5 skill units, claimable 5/5) but never asked
whether any of it is a function of the condition. Answering that closes the round's
value-of-LF ledger with a statement in either direction:
`proj(teacher) ~ T0` => the advantage is realisation information no train-only channel
(distillation included) can carry; `proj(teacher) << T0` => there is a condition-learnable
target the student is not reaching and the failure is optimisation/architecture.

**(B) D2 coverage-greedy support repair on cahn_hilliard — rejected.** Verdict is
`preempted (cite)` (Climaco & Garcke fill-distance with error bounds, arXiv:2307.10988;
PICore arXiv:2507.17151; PCA-KMeans arXiv:2509.06154); only the *gating* is open. It is also a
*lever* (change which rows are fit on to get a better number), i.e. r2s3/r2s1 territory, while
12.4 says "r2s4 measures, r2s3 optimizes". As the round's LAST diagnostic it would leave the
value-of-LF ledger open. Rejected; the free training-free half (identifiability/d_min under
coverage-greedy vs prefix subsets via `tools/condition_predictability_ceiling_fast.py`) is
recorded as a zero-GPU follow-up for the round report rather than a card.

**(C) D2b training-free regime classifier as its own card — rejected as a standalone**, folded
into (A) instead: B2's taxonomy is a rule *candidate* needing a second card to reproduce. (A)
reproduces it for free, because its per-dataset prediction is derived from the taxonomy
(cahn_hilliard = the one support-limited dataset = the one place a reachable component is
predicted).

**(D) A bare "distil the LF teacher into a condition-only student" card — rejected**, on
websearcher instruction 3 (preempted in the surrogate domain itself, S0952197625034293,
search-result confidence) and on the 12.4 division of labour. In (A) the distillation student
appears only as ONE of three projection estimators, i.e. as an instrument that makes the null
robust to "your projection class was too weak", never as a proposed method.

### The structural problem B2's part 7 did not price, and its resolution

B2 wrote "fit an out-of-fold condition -> prediction map ... to the LF-teacher arm's own **test**
predictions". That is not implementable: under immutable 5.9 the stripped test view has no LF
fields, so the teacher has **no test code path at all** (B2's own part 5 records
`arms_mean_test_skill.I1_lf_teacher = null` and "structurally no test code path"). The ledger
must therefore be measured on **held-out TRAIN rows**, in B2's established inner-skill
convention (train-slice nRMSE divided by the frozen test copy-LF denominator). B2 shipped no
predictions, so this needs fresh training - one cheap matched leg, exactly as its part 7 said.

### Why the projection targets must be OUT-OF-FOLD teacher predictions (the key design point)

If the projection map `g` were fitted on the teacher's *in-sample* predictions (the teacher's
fitted values on its own training rows), those values are close to the memorised HF fields, so
`g` would degenerate into "another estimator of E[HF | condition]" - which is what `T0` already
is. `proj ~ T0` would then be true by construction and the diagnostic would be vacuous. Fitting
`g` on the teacher's **out-of-fold** predictions asks the intended question: is the teacher's
*behaviour at unseen conditions* condition-predictable? This forces a two-level design.

### Two-level fold design (leakage-free, and it supplies the variance a 1-seed card needs)

Fold assignment F over the 400 train rows into 5 folds of 80, fixed by `SPLIT_SEED=0`
(ifc_poisson excluded, see below). For each outer fold k:
- `P_k` = the 320 rows outside fold k (matches B2's N_fit = 320 exactly); a 40-row val slice is
  carved inside `P_k` for HF-head model selection, identically for every arm.
- `T0_k` (condition-only) and `I1_k` (coords + upsampled real LF) are trained on `P_k` and
  predict on the evaluation slice `E_k` = fold k.
- **Inner 4-fold cross-fit inside `P_k`**: four more teachers, each trained on 240 of the 320
  rows, give out-of-fold teacher predictions on all of `P_k`. These are `g`'s regression
  targets. No model that ever saw `E_k` contributes to `g`'s targets or to `g`'s fit, so the
  projection is leakage-free by construction (a reviewer can check this structurally).
- Three projection estimators fitted on `(condition_j, teacher-OOF-pred_j)` for j in `P_k`,
  evaluated on `E_k`: `proj_knn` (k-NN in per-dim train-standardised condition space, k on
  {1,2,4,8,16,32,64} by LOO **inside `P_k` only**), `proj_ridge` (closed-form ridge on a
  degree-2 polynomial condition feature map, alpha by GCV inside `P_k` only), and `proj_nn`
  (the SAME FiLM-FNO backbone at the same budget, trained on the teacher-OOF targets - the
  genuine distillation student). `proj_best` = the estimator with the lowest **fit-side**
  criterion, selected without touching `E_k`; all three are reported.

Concatenating over k = 1..5 gives out-of-fold predictions on all 400 train rows for every arm,
and - decisively for a strict-1-seed card - **5 in-job paired fold-level deltas** per contrast.
That is the drift-class rule's "only in-job paired controls are controls" satisfied without
spending seeds.

### Free upgrade: a test-split paired distillation contrast at zero extra training

`proj_nn` is condition-only at test, so each of the 5 fold models can *also* be scored on
`test_hf` and paired with the corresponding `T0_k`. That yields 5 in-job paired deltas of a
real LF-teacher distillation student against a matched condition-only baseline **on the scored
split**, at one training seed and no extra GPU - the round-report sentence "distillation from
an LF-consuming teacher does not beat the condition-only baseline (5 paired folds)" becomes
available. This is a measurement of r2s3's channel, not a proposal of it.

### Seed protocol: strict 1 seed, argued

seeds `[0]` per project.yaml and 4.2. The card does not need a seed spread because (i) every
adjudicated contrast is within-job and paired on identical folds, rows, backbone, budget and
seed; (ii) the operative threshold is
`max(certified per-dataset min_claimable_effect, B2's fold-fixed same-model 3-seed T0 spread,
this card's in-job 5-fold paired spread)` - the second term imports B2's already-paid 3-seed
measurement on the same backbone/folds/recipe, the third is measured in-job; (iii) the
alternative hypothesis is enormous (teacher advantage 10.5-114.5 skill units), so a 1-seed
instrument is far from the resolution limit. No 12.4-certification exception is requested and
no reviewer adjudication is needed.

### What is pre-registered from a training-free quantity (the open part of the D1 verdict)

The card computes, training-free on the TRAIN split (seconds, reproducing B2 T1-F1/T1-F3),
per dataset: centred `cos(HF, LF-upsampled)` and copy-LF train rel-L2. It **pre-registers**
`advantage_reachable ~ 0` wherever cos >= 0.997 (allen_cahn 1.00000 / 0.00194,
pfc 0.99995 / 0.00643, cahn_hilliard 0.99962 / 0.00937, fisher_kpp 0.99718 / 0.02086) and
declares helmholtz (cos 0.3099, rel-L2 0.26506) the only dataset where the answer could differ.
This is exactly what the D1 row says nobody does ("nothing pre-registers the outcome from an
independently measured training-free barrier"), and it also makes the honest arithmetic
explicit up front: on the sharp panel the teacher is a near-copy of HF, so a small reachable
component is *expected*, and the informative content is (a) whether the exception dataset
(cahn_hilliard, the one support-limited one) breaks it, (b) helmholtz's report-only column,
and (c) whether the smoother (band-limited) teacher target buys the distillation student
anything on the scored split.

### Dataset scoping and the three binding B2 constraints

- Ledger datasets: helmholtz + the 4 sharp. **helmholtz is report-only** and adjudicates
  nothing (B2 constraint 1, T2-F5), carried with an interpretive energy-pooled twin column
  (scored numbers stay mean-of-ratios; immutable 5.4 untouched; the artifact is presented as
  project-local per the D3 verdict, with TRIE cited only for the stochastic-map point).
- **ifc_poisson carries NO LF-paired arm** (B2 constraint 2, T2-F6) - only the primary
  condition-only `T0` leg plus floors, labelled anecdote-grade (N_hf = 5, arXiv:2410.23440);
  `tools/ladder_pair_alignment_audit.py --fail-on mispaired` runs as a build pre-flight on
  every dataset carrying an LF arm.
- **Predictions and checkpoints are dumped per arm** (B2 constraint 3): `preds_test.npz` and
  `preds_oof.npz` per arm/fold, so the mechanism turns are not limited to serialised summaries.

### Cost

B2 ran 44 trainings + 22 ifc LOO legs + a guard leg in 17.25 min on h200. This card:
5 ledger datasets x [1 primary T0 + 5 outer folds x (T0_k + I1_k + 4 inner teachers +
proj_nn_k)] = 5 x 36 = 180 legs, + 1 ifc primary leg + 3 guard legs (2 epochs) = 184 legs, most
at N ~ 240-320. Projected 60-110 min; request `--time 03:30:00`. Checkpoint-resume (B2's
single `<ckpt_dir>/last.pt` holding completed legs + the in-flight leg) makes an overrun
recoverable.

## Proposal

- **Category**: `diagnostic / teacher-projection channel ledger (reachable vs unreachable
  privileged advantage) + test-split paired distillation contrast`
- **Card type**: `diagnostic` (with training; no seeds 1-2)
- **Motivation**: quotes the batch-3 D1 verdict row verbatim (see report.md).
- **Concrete config, recipe, expected outcome, expected falsification, anchor reference**:
  as transcribed into `report.md` (single source of truth for the starter).

## Status

- Slot covered (1 proposal, not skipped).
- Reopen candidates resolved: **none exist** - all 8 round-2 cards have
  `reopen_candidate: false`.
- Immutables self-check: **pass (11/11)** - recorded in `report.md`; no revision pass needed,
  so there is no `iteration_2.md`.
