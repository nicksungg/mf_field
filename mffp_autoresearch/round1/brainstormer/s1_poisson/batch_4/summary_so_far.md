# Summary so far — Stream `s1_poisson`, Batch 4

Sources read in full: `websearches/s1_poisson/batch_4/report.md`;
`experiment_cards/s1_poisson/batch_{1,2,3}/B*.json` (B3 parts 3, 5, 6, 7 +
recipe + scripts); `worktrees/s1_poisson/B3/notes/handoff_experiment_mechanism_analyzer.md`;
`worktrees/s1_poisson/B3/scratchpad/reanalysis_turn_1_results.md`;
`worktrees/s1_poisson/B3/models_r1/mf_fno_ladder_gain/smoke_eval.py`;
`worktrees/s1_poisson/B3/scripts/{submit.sh,01_train_eval.sh}`;
`program.md` §2, §4.3-4.6, §5, §12.1, §13.3; `docs/adr/000{4,5,7,9}`;
`state/noise_floor.json`; `state/anchors/s1_poisson.json`.

## 1. Websearch findings + prior-art verdict

`websearches/s1_poisson/batch_4/report.md` (4 iterations, 12 searches, 10
usable fetches). Verdicts, verbatim from its **Prior-art verdict** table:

- **D-A** (the B4 core A/B): **"`preempted` (ML-general methodology) - open
  only as an in-repo measurement"**. Citation:
  *"However, this comparison conflates algorithmic quality with compute: GRPO
  performs 8x more gradient updates per epoch than REINFORCE and POMO"*
  (https://arxiv.org/html/2606.10321v1) - and that paper builds **both**
  matched controls (scale the short arms up to 800 epochs; read the long arm
  off at epoch 12). The report adds the live warning: *"in
  https://arxiv.org/html/2606.10321v1 the epoch-matched ranking **reversed**
  under step-matching."* Also: *"Too frequently, authors propose many tweaks
  absent proper ablation studies, obscuring the source of empirical gains"*
  (https://ar5iv.labs.arxiv.org/html/1807.03341), and dedup changes required
  train steps (https://arxiv.org/abs/2107.06499,
  https://arxiv.org/html/2407.06654).
- **D-B** (per-level weight knob as the mechanism): **"`preempted`
  (MF-general)"** - https://arxiv.org/html/2602.01176v1 (`L_total = L_LF +
  lambda_HF L_HF + ...`). Legal as **instrument**, never as the claim.
- **D-C** (nested-ladder all-pairs degeneracy): **"`novel` (narrow) - 'not
  previously reported', never 'novel method'"**. POSEIDON's O(K^2) rests on the
  semi-group property with a **source-varying input**
  (https://ar5iv.labs.arxiv.org/html/2405.19101); absent under
  `cond_from = target`.
- Section "For the brainstormer" item 5: *"'Importance duplication' carries a
  named failure mode when 'two or more copies of the data point x_i appear in
  a minibatch' ... With bs=16 and 5 HF rows replicated x4, duplicate co-occurrence
  within a minibatch is frequent - so `allpairs` is not *exactly*
  `self_only`-with-weights even at matched steps"*, and *"If the card wants a
  clean weighting arm, prefer an explicit per-sample loss weight over
  replication."*
- Fourth consecutive batch with **no effect sizes at N_hf = 5** in the
  literature.

## 2. `program.md` §12.1 conventions (verbatim)

> ### 12.1 `s1_poisson` (gap)
>
> - **Bar**: paper 0.036 (IFC-ODE2); stretch IFC-GPODE 0.018. Current best zoo:
>   0.042 (`mf_fno_pinn_transfer`, factory bench). Anchor: `state/anchors/s1_poisson.json`.
> - **N_hf = 5.** Every claim is anecdote-grade by sample count; the CI + noise
>   floor conventions are the only defensible reporting. Prefer designs that
>   reduce variance (ensembling across seeds, all-pairs training) or add
>   information (physics residuals) over designs that add capacity.
> - Batch-1 seed direction: **all-pairs fidelity training** applied to the gap -
>   `mf_field/akash/models/mf_fno_allpairs` was the mentor's best on the hard
>   subset (gm 0.0094 vs FiLM 0.0121, FINDINGS.md); its known failure is
>   O(L^2) pair cost on many-level datasets (era5 timeout) - irrelevant here
>   (ifc ladder L=4).
> - Physics fact: Poisson is elliptic with global coupling; the IFC papers'
>   ODE/GPODE methods exploit the fidelity-ladder structure directly.

Anchor (`state/anchors/s1_poisson.json`): `best_skill_on_dataset`,
value **1.5656334312786022** (`mf_fno_transfer_film`), per-seed
[1.5446694, 1.4561617, 1.6960692], `provisional: false`.
Noise floor (`state/noise_floor.json`, `ifc_poisson`):
**`min_claimable_effect` = 0.23990756041925798 skill** (= 0.0086367 nRMSE at
paper_bar 0.036, ADR 0002).

## 3. Within-stream prior cards

- **B1** (`mf_fno_ladder`, complete): the ladder substrate; `MFFP_LADDER_MODE`
  born (`two_level|adjacent|allpairs|legacy_pairing`), `allpairs` the primary.
- **B2** (`mf_fno_ladder_norm`, complete): `MFFP_LADDER_SCALER`
  (`shared|per_level|shared_reweight`), and **the `cond_from = "target"`
  correction** - cross rows are indexed on the target fidelity's own condition
  list. Control 0.034250 nRMSE. Its part 7 named the per-sample gain defect
  (57.10 % of squared error, 0.919-R^2 linear in the 5-D condition vector).
- **B3** (`mf_fno_ladder_gain`, complete, seed 0, job 66058189, 2m28s, 5 arms):
  `gain__ladder_level_intercept` 0.024970/0.6936 (primary);
  **`self_only__none` 0.021913/0.6087 - the round's best claimable
  `ifc_poisson` number**; `base__none` (allpairs control) 0.034264/**0.9518**;
  `gain__hf_only` 0.034243; `gain__ladder_pooled` 0.057489.
  Mechanism turn 1 (`reanalysis_turn_1_results.md`) then proved:
  - **F-T1.1**: all six cross blocks are **exact duplicates** of the self block
    at their target level (`cond_max_abs_diff` = 0.0, `target_field_max_abs_diff`
    = 0.0, 6/6), *"differing **only** in the `f_src` tag"*; distinct (X,Y) rows
    **175 of 280** (allpairs) vs 175 of 175 (self_only).
  - **F-T1.2**: allpairs is a per-level **replication schedule x1/x2/x3/x4**;
    level shares 0.357/0.357/0.214/0.0714 vs self_only 0.571/0.286/0.114/0.0286
    (ratio **0.625/1.25/1.875/2.5**); *"Gradient steps/epoch at bs=16: 18 vs 11."*
  - **F-T1.3**: self_only has **no amplitude defect** (oracle gain std 0.00736
    vs 0.03047) and a 9.9 % lower structure floor.
  - **F-T1.6**: allpairs fits its 5 HF rows **1.34x tighter** and generalizes
    **1.56x worse** (test/train 7.12 vs 3.39).
  - Part 7 `open_question`, verbatim: *"The decisive, cheap experiment is a
    THIRD row set with allpairs' 280 rows and self_only's per-level WEIGHTS
    (or self_only's 175 rows trained for 280/175 x the steps)."*
  - Handoff: *"Do not stack the head on `self_only` - measured 0.021913 ->
    0.035890."* / *"`self_only` vs the primary is 0.354x the floor - still not
    rankable."*

## 4. Cross-stream cards (light scan)

Grep over all `experiment_cards/*/batch_*/B*.json` for `s1_poisson|self_only|
ladder_pair_row_audit`: the only substantive hit is `s7_loss-B2`, and only as
a scheduling note (*"D4's open MF slice is already running as `s1_poisson-B3`"*).
No cross-stream card attacks the replication/weighting constraint. The live
cross-stream link is s1-B3's own part 7: (i) s5-B2 `zscore` and the s1 gain
head act on the **same** per-sample level (DC) channel of `ifc_poisson` (69.28 %
DC energy) - not two stackable levers; (ii) `tools/ladder_pair_row_audit.py`
returns **REPLICATION_ONLY on `heat_local`** too (15360 rows, 5120 distinct),
so the construction warning generalizes.

## 5. Reopen candidates

None. `grep -l '"reopen_candidate": true'` over every card in the round returns
no files; s1-B1/B2/B3 are all `status: complete`, `reopen_candidate: false`.

## 6. What is UNKNOWN

1. **The attribution itself.** `self_only` beats `allpairs` by 0.3431 skill
   (1.43x the 0.2399 floor) and B3 proved the two row sets carry *identical*
   information. Three coupled differences remain, and nothing in the repo
   separates them:
   (a) **effective per-level loss weight** (0.625x/1.25x/1.875x/2.5x; under
   `per_level` normalization row share *is* loss weight - F-T1.2);
   (b) **stage-1 gradient steps** (18 vs 11 per epoch -> 3600 vs 2200 at 200
   epochs, ratio **1.6364**);
   (c) **`f_src`-tag exposure** - self_only never sees a row with
   `f_src != f_tgt`, while the eval query form is `(f_src = lf, f_tgt = hf)`;
   the cross rows are the only stage-1 rows in the eval form.
   Separating these requires training runs. **No literature effect size exists
   for this regime** (websearch, 4th consecutive negative).
2. **Which way it falls.** In-repo evidence leans to (a): F-T1.6's
   fit-tighter/generalize-worse signature is exactly what 2.5x upweighting a
   5-condition level produces, and B3 turn 3's coverage predictor (0.24828 at
   level 8 vs 0.39939 at level 64) says condition coverage predicts HF accuracy
   on this ladder. But the fetched precedent documents an outright **rank
   reversal** under step-matching, so the prior is not decisive.
3. **Whether the round's best `ifc_poisson` number means what the report will
   say it means.** Both arms are legal 200-epoch tier configurations, so the
   *number* survives either way; what is unknown is the *transferable rule* -
   "drop the cross pairs" (a design rule for every ladder family, incl.
   `heat_local`) vs "the joint stage was over-trained" (a schedule knob).
4. **Whether explicit weights reproduce replication at all.** The published
   equivalence is an approximation whose named caveat (duplicates co-occurring
   in a minibatch) fires at bs=16 with x4 replication. The size of that
   gradient-noise residual is unmeasured anywhere.
5. **Whether a step-budget knob is even safe here.** `_train` uses
   `CosineAnnealingLR(T_max=epochs)` stepped per epoch, so any step-matching
   implementation must decide between truncating the anneal (mid-run read) and
   re-scaling `T_max` (own complete schedule). Unknown which the B3 base is
   sensitive to; the choice must be pre-registered, not discovered.
6. **What is spent.** The level channel is spent (post-head level rel-err
   0.00879; remaining calibration ceiling 0.045x the floor); the head must not
   be stacked on `self_only`; K>1 rank extensions are priced below resolution.
   So batch 4 has no model-improvement direction left in this family that is
   worth 200 epochs - only the attribution debt.
