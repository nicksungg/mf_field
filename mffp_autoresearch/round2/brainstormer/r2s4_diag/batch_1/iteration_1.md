# Iteration 1 — `r2s4_diag`, Batch 1

## Design context considered

- **summary_so_far.md §6 unknowns** — the driving ones: (1) the empirical
  condition→HF seed-noise constant is unmeasured and the direction of bias in the
  provisional round-1-rescaled file is unknown; (3) nobody has checked the frozen
  floors reproduce from the stripped view; (4) the ADR r2-0003 conditional-mean
  barrier is asserted but unquantified; (6) no trained condition-only model has been
  scored on this panel under corrected denominators; (7) B2's matched ± LF contrast
  has no pre-registered without-LF arm.
- **Prior-art verdicts**: D1a `preempted (cite)` (adopt Agarwal + Du, don't invent);
  D1b `preempted-but-MF-composition-open (cite)` (training-free floors in copy-LF
  skill units for a no-solver regime is the open composition); D2's Yang et al.
  non-monotone law is the citable falsifiable prediction for the value-of-LF framing;
  D3 (overfitting anatomy) is LOW confidence and the websearcher asks for a fresh
  search before any card leans on it.
- **program.md §12.4** verbatim (quoted in summary §2): B1 pre-directed = (a) verify
  frozen floors reproduce incl. the standing zero column, (b) train ONE minimal
  condition→HF baseline at smoke tier, seeds {0,1,2}, on the panel; diagnostic card
  WITH training; cheap by design.
- **Anchor** `state/anchors/r2s4_diag.json`: best-floor panel geomean **23.0636**
  (`provisional: false`); per-dataset best floors helmholtz 3.3441 (zero), pfc 59.8118
  (mean), allen_cahn 269.1959 (NN), fisher_kpp 11.9931 (mean), cahn_hilliard 23.1803
  (NN), ifc_poisson 10.0549 (NN).
- **Provisional noise floor** `state/noise_floor.json` `min_claimable_effect`:
  helmholtz 10.6811, pfc 6.9839, allen_cahn 14.8152, fisher_kpp 1.2198,
  cahn_hilliard 1.1604, ifc_poisson 0.2399 (`_provisional: true`, judged directly
  per §4.3 — this card's job is to replace it).
- **Immutables block (§4.5 of my prompt / program.md §5)** held verbatim in view
  throughout; self-check at the end of this file.
- **Pre-falsified levers (r1 program §5)**: WNO backbone swap (`wno_transfer_film`),
  LF low-mode freezing (`mf_fno_spectral`), diffusion prior for point accuracy
  (`mf_fno_diffprior`).
- **Measured facts used**: stripped-view npz shapes (read directly):
  helmholtz test_l2 x (100,3) / y (100,9216) = 96², pfc test_l3 y (100,16384) = 128²,
  allen_cahn / fisher_kpp / cahn_hilliard test_l3 y (100,65536) = 256²,
  ifc_poisson test fidelity_64 = 64², train HF 400 (sharp/helmholtz) and 5 (ifc).
  All HF grids ≤ the factory WORK_CAP of 256 ⇒ the certifier can be scored on the
  NATIVE HF grid with no interpolation (no registration artifact re-entry).
- **Contract facts**: `eval/score_panel.py` selects the scored split by preference
  `test_hf` → `test`, prefers `rel_l2_per_sample` (mean of per-sample ratios), and
  refuses any view dir exposing >1 test level; `data_adapters/metrics.finalize_and_write`
  emits `splits.test_hf` with `rel_l2_per_sample` and merges an `extra` dict at top
  level. Round-1 precedent for a diagnostic family carrying `ref_*` splits + a side
  diag JSON with env knobs: `round1/experiment_cards/s2_beyond_copy/batch_1/B1.json`.

## Proposal reasoning

**What B1 must deliver.** §12.4 fixes two deliverables (floor reproduction; a 3-seed
condition→HF spread). The orchestrator adds three constraints: adopt the published
few-seed protocol rather than invent one; make the output usable as a
min-claimable-effect *even if the conservative protocol declares nothing significant*;
and either fold ADR r2-0003's conditional-mean floor in or scope it out explicitly.
That is a well-specified card; the design work is in (i) which architecture certifies
the spread, (ii) how the min-claimable-effect is defined so it always exists, (iii)
whether the conditional-mean estimate belongs here, and (iv) how to falsify a
certification card without circularity.

**(i) Which architecture certifies the spread.** §12.4 offers "smallest reasonable
FiLM-FNO decoder or MLP→field".

- *Rejected: a low-rank / POD-style linear decoder (condition → MLP → R learned basis
  coefficients).* Attractive because it doubles as a parametric conditional-mean
  estimator and is dirt cheap. Rejected because the certified number is consumed as a
  **noise floor for other cards**: a near-convex linear decoder has systematically
  smaller seed-to-seed spread than the spectral/operator models r2s1–r2s3 will run, so
  it would certify a floor that is too small and make every downstream falsification
  threshold too lenient. Conservatism must win here. (It is also r2s1's D2, verdict
  `preempted` — POD-NN/PCA-Net — so it is not free of duplication either.)
- *Rejected: a large/tuned decoder.* Violates "cheap by design", and a strong model
  invites the card to be read as a performance claim, which a certification card
  should not be.
- **Chosen: a minimal FiLM-conditioned FNO decoder** with a coordinate-grid input
  (no field input of any kind), width 32, 2 blocks, 16 modes, ≈1M params. It is the
  same *class* as what r2s1/r2s2/r2s3 will train, so the spread it certifies is
  representative rather than optimistic; it is explicitly a **declared baseline**, not
  a novelty claim — r2s1's verdict D1 says a FiLM-conditioned spectral decoder is
  "**preempted** … Admissible only as a *measurement/baseline arm* on this panel
  against the mandatory floor arms", which is exactly the role it has here. Modes are
  set to 16 rather than the factory default 12 because round-1's audited finding F22
  ("`modes_cap = 12` never scales with resolution — 12 of 128 modes at 256²") means a
  12-mode model on the 256² sharp datasets is band-limited to nearly the smooth bulk,
  which would (a) bias it toward the conditional mean and (b) shrink its seed spread —
  again the anti-conservative direction.
- The certifier reads **no LF at any point, train or test**. That is deliberate: it
  pre-registers the **without-LF arm** of §12.4's B2 value-of-LF accounting, fixing the
  architecture, budget, normalization and val discipline that B2 must hold constant.
  Without this, B2's "matched" claim would be unfalsifiable (summary §6.7).

**(ii) A min-claimable-effect that always exists.** Du's result (3 seeds "never
declaring significance" for 0.6–2.0-point effects) means a design whose deliverable is
"the significant effect size" can return nothing. So the deliverable is defined as a
**conservative envelope**, computed per dataset d from the 3 seed skill values
s₀,s₁,s₂ and the per-sample rel-L2 arrays already in the result JSONs:

- `spread_maxmin_d = max_i s_i − min_i s_i` (round-1's convention, kept for continuity);
- `paired_null_95_d` = the 95th percentile of |Δ| over the 3 seed pairs × B stratified
  bootstrap resamples, where each resample draws test-sample indices ONCE and applies
  them to BOTH members of the pair (Du's paired protocol) — this is the null band for
  a paired comparison whose true effect is zero, which is exactly the shape of every
  future "arm A vs arm B, same seeds" claim, and it aligns with the drift-class rule
  ("only in-job paired controls are controls");
- **`min_claimable_effect_d = max(spread_maxmin_d, paired_null_95_d)`** — a number that
  exists unconditionally;
- reported alongside: IQM (with the honest note that IQM over n = 3 degenerates to the
  median — the power comes from the per-sample bootstrap axis, not the seed axis), the
  95% stratified-bootstrap CI of mean skill, and the sign-flip permutation p-value of a
  same-model seed-pair contrast as a sanity check (expected: non-significant).

Both statistical ingredients are adopted by citation, per the D1a verdict: Agarwal et
al. (IQM + stratified bootstrap for 3–10 runs) and Du (paired per-seed deltas). No new
statistics are invented; the deliverable is the *constant*, which is what the verdict
says is open.

**(iii) The conditional-mean barrier: fold in the training-free half only.** ADR
r2-0003 asserts condition→HF is stochastic on pfc/fisher_kpp/allen_cahn but does not
quantify the barrier. A k-NN-in-condition **mean** predictor is the natural
non-parametric estimator of E[HF|cond], and — decisively for scope — it is the
*interpolant between two floor arms that are already frozen*: k = 1 is exactly
`nn_condition` and k = N is exactly `train_mean`. So the k-sweep is a floor-panel
extension, i.e. squarely r2s4 work, adds essentially zero compute (400 × 100 distances
in ≤19-dim condition space plus field averaging), and needs no training. k is selected
by **leave-one-out on TRAIN ONLY** (no test peeking; the round-1 D3 val_idx
double-consumption caveat is the cautionary tale), then the LOO-selected k* is scored
once on test. The curve shape is itself the diagnostic: k* large ⇒ the condition is
uninformative and the stochastic-map reading of ADR r2-0003 holds; k* = 1 ⇒ it does not.

*Scoped OUT of B1, explicitly*: the **validation** half of r2s1's D3 — demonstrating
that the missing driver lives in the withheld LF field. That requires LF-side probes
and belongs to r2s1/r2s2/r2s3 or a later r2s4 batch (ADR r2-0003 already has a partial
measurement: the pfc nearest pair differs by 1.149 in HF and 1.148 in `train_l1.npz`).
Recording the boundary here prevents a duplicated card.

*Honest caveat to carry on the card*: the scored metric is per-sample relative L2, for
which the conditional mean is not exactly optimal (it is MSE-optimal); the k*-NN mean
is therefore an *estimate* of the barrier, not a certified bound. And on cahn_hilliard
(19-dim condition, 400 samples) and ifc_poisson (5 train fields) the estimator is weak
— report per-dataset, do not aggregate.

**(iv) Falsifying a certification card without circularity.** The card cannot use the
noise floor it is producing. It can use (a) the deterministic frozen floors (zero seed
noise by construction) and (b) the provisional round-1-rescaled constants, which §4.3
says to judge directly. So:

- The **seam clause** is exact: every recomputed training-free floor must match
  `state/anchors/floors.json` to ≤1e-9 relative on all 9 datasets × 3 arms, and the
  zero arm must be exactly nRMSE ≡ 1.0. Deterministic ⇒ no noise-floor issue.
- The **capability clause** requires the certifier to beat the best training-free floor
  *by more than the provisional per-dataset min-claimable-effect* — so the threshold
  exceeds the noise floor by construction. Thresholds (skill): pfc < 59.8118 − 6.9839 =
  **52.83**, allen_cahn < 269.1959 − 14.8152 = **254.38**, fisher_kpp < 11.9931 −
  1.2198 = **10.77**, cahn_hilliard < 23.1803 − 1.1604 = **22.02**, ifc_poisson <
  10.0549 − 0.2399 = **9.81**. **helmholtz is report-only**: its provisional constant
  (10.6811) exceeds its entire best-floor value (3.3441 = the zero field), so no
  assessable threshold exists there — this is itself a finding about the provisional
  file, and the standing zero-floor column is reported per §12.1's helmholtz lesson.
- The **certification-value clause**: if ≥3 of 6 certified `min_claimable_effect`s come
  out ≥ their provisional counterparts, the card has certified that condition→HF at
  smoke tier is *noisier* than round-1's LF-consuming families, i.e. the round can
  license only very large effects. That is a real (and reportable) outcome, and it is
  the honest failure mode of "3 seeds licenses something useful".

I deliberately did NOT rig the capability clause to pass: my own prediction (below) is
that the certifier clears roughly 2–3 of the 5 assessable thresholds, so the ≥3-failure
clause has a genuine chance of firing.

**Rejected alternative directions for B1** (all belong to later batches):
- *Overfitting anatomy at N_hf ∈ {5,20,50}*: §12.4 puts it in "later batches", and the
  D3 verdict is LOW confidence with an explicit "re-search before a B2/B3 card leans on
  this". Proposing it now would burn the round's certification slot on the
  worst-evidenced direction.
- *Running the ± LF contrast already in B1*: doubles scope, and r2s3 owns optimizing
  the LF signal while r2s4 measures it. B1 pre-registers the without-LF arm instead.
- *Including the guard set in the trained arm*: guards are for panel-win claims (§2.3);
  a certification card claims no panel win. Guards ARE covered by the training-free
  floor reproduction (all 9 datasets), which costs nothing.

**Cost.** 6 panel datasets × 3 seeds × 200 epochs of a ~1M-param FNO on ≤256² fields
with ≤400 training samples (25 steps/epoch at batch 16 ⇒ 5k steps/run). Estimated
≤30 min per seed over the whole panel on an H100; request the 04:00:00 default from
`resource/logistics/slurm_rules.md` since `state/timing_ledger.json` has no entries yet.

## Proposal

- **Category**: `diagnostic / floor + seed-spread certification (condition→HF)`
- **Card type**: `diagnostic` (WITH training — the §12.4 exception; `epochs = 200`,
  `seeds = [0,1,2]`)
- **Motivation**: the websearcher's D1a row reads verbatim —
  "**D1a** — certify a minimum-claimable-effect from a 3-seed condition→HF spread
  (replaces provisional `noise_floor.json`) | `preempted (cite)` | Agarwal et al.,
  *Deep RL at the Edge of the Statistical Precipice* —
  https://ar5iv.labs.arxiv.org/html/2108.13264 ; Du, *When +1% Is Not Enough* —
  https://arxiv.org/abs/2511.19794 | Nothing methodological. Open item is the
  **empirical constant** for this panel/regime. Adopt IQM + stratified/paired BCa
  bootstrap CIs + per-seed deltas instead of a bare max−min spread; expect 3 seeds to
  license only LARGE effects." — and the D1b row reads verbatim —
  "**D1b** — training-free floor panel (NN-in-condition / train-mean / zero) as
  mandatory reported arms | `preempted-but-MF-composition-open (cite)` | … | All
  published floors are **fitted** (ROM, polynomial, GP, kriging). Two dedicated
  searches found no *training-free* trivial-predictor panel reported as mandatory
  columns, and none expressed in **copy-LF skill units** for a no-solver-at-test
  regime. That composition is open." The card therefore *adopts* both protocols by
  citation and delivers the missing empirical constants, plus the open composition
  (training-free floors in copy-LF skill units for a no-solver regime).
- **Concrete config**: new from-scratch family `models_r2/r2s4_cert_min/`
  (`manifest.json`, `smoke_eval.py`, `model.py`, `INSPIRATION.md`, plus
  `probes/floor_repro.py` and `probes/certify_spread.py` in the worktree).
  1. **Certifier model** (`test_hf` split, the scored number): condition-only FiLM-FNO
     decoder. Input = normalized coordinate grid (2 channels, x,y ∈ [0,1)) lifted by a
     1×1 conv to width 32; 2 FNO blocks at 16 modes, each followed by per-channel FiLM
     (γ,β) produced by a 2-layer MLP (width 64, GELU) on the per-dim train-standardized
     condition vector; 1×1 conv head → 1 channel. ~1M params. **No field input
     anywhere; no LF read at train or test.** Trained on the HF train split only
     (`cond_by_fid[hf_fid]`, `field_by_fid[hf_fid]`), MSE loss in global train-z-scored
     target space (training loss is free per immutable 4; the scored metric is
     untouched), AdamW lr 1e-3 / wd 1e-5, batch 16, cosine decay, grad-clip 1.0, 200
     epochs. Val split = 10% of train (seeded, disjoint, never the test split) with
     best-val checkpoint selection; if `N_hf < 20` (ifc_poisson: 5) the val split is
     DISABLED and final-epoch weights are used — recorded on the card as an ifc-specific
     caveat. Evaluated on the NATIVE HF grid (all panel grids ≤ 256 = WORK_CAP ⇒ no
     interpolation). Scoring via `data_adapters.metrics.finalize_and_write`
     (`splits.test_hf`, `rel_l2_per_sample`); checkpoint resume from
     `<ckpt_dir>/last.pt` keyed on (epochs_target, grid, seed).
  2. **Mandatory floor arms in the same run** (`ref_nn_condition`, `ref_train_mean`,
     `ref_zero` splits, merged after `finalize_and_write` leaving `test_hf`
     byte-identical): recomputed from the stripped view through the same nRMSE path and
     asserted equal to `state/anchors/floors.json` to ≤1e-9 relative; `ref_zero` must be
     exactly 1.0.
  3. **`probes/floor_repro.py`** (training-free, deterministic, run once at seed 0 over
     all 9 panel+guard datasets): reproduces the 3 frozen floor arms from the STRIPPED
     view and diffs against `floors.json` (tolerance 1e-9); reports the ifc_poisson
     5-atom-dictionary caveat (`nn_index_hist_top5` = {0:41,1:17,2:20,3:38,4:12} over
     128 test points) and the helmholtz standing zero column; then computes the
     **k-NN-in-condition mean** curve for k ∈ {1,2,4,8,16,32,64,128,400}, selects k* by
     leave-one-out on TRAIN ONLY, and reports the test nRMSE/skill at k* as the
     **conditional-mean-floor estimate** (ADR r2-0003 folded in; k=1 ≡ nn_condition and
     k=N ≡ train_mean are the sanity anchors). Writes `floor_repro.json`.
  4. **`probes/certify_spread.py`** (CPU, seconds, run after all 3 seeds): reads the
     three `result_panel_s{0,1,2}.json` plus the per-sample rel-L2 arrays, and emits
     `noise_floor_candidate.json` with, per dataset: `per_seed_skill`, `iqm`, `mean`,
     `ci95_stratified_bootstrap`, `spread_maxmin`, `paired_null_95`,
     `min_claimable_effect = max(spread_maxmin, paired_null_95)`, the sign-flip
     permutation p-value of a same-model seed-pair contrast, `n_seeds: 3`,
     `certifier_family`, `epochs`, and a `_source: r2s4_diag-B1` provenance stamp.
     **The orchestrator — not this card, not the builder — installs it over
     `state/noise_floor.json`** (§4.3/§12.4 pre-direct the replacement; `state/` is
     orchestrator-owned).
- **Recipe**:
```json
{
  "base_family": "none (new from-scratch condition-only family; reuses only the factory data_adapters plumbing: loaders.load_mf_dataset, geometry.resolve_grid, metrics.finalize_and_write)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s4_cert_min",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {
    "R2S4B1_WIDTH": "32",
    "R2S4B1_BLOCKS": "2",
    "R2S4B1_MODES": "16",
    "R2S4B1_FILM_MLP_WIDTH": "64",
    "R2S4B1_BATCH": "16",
    "R2S4B1_LR": "1e-3",
    "R2S4B1_WD": "1e-5",
    "R2S4B1_CLIP": "1.0",
    "R2S4B1_SCHED": "cosine",
    "R2S4B1_TARGET_NORM": "train_zscore_global",
    "R2S4B1_VAL_FRAC": "0.1",
    "R2S4B1_VAL_MIN_N": "20",
    "R2S4B1_FLOOR_ARMS": "nn_condition,train_mean,zero",
    "R2S4B1_KNN_K": "1,2,4,8,16,32,64,128,400",
    "R2S4B1_KNN_SELECT": "loo_train",
    "R2S4B1_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S4B1_FLOOR_TOL": "1e-9",
    "R2S4B1_BOOTSTRAP_B": "10000",
    "R2S4B1_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s4_diag/B1/eval"
  }
}
```
- **Expected outcome** (a diagnostic: nothing "moves" — these are predictions to be
  scored against, all in skill units vs the corrected denominators):
  - **Floor reproduction**: exact — all 27 (9 datasets × 3 arms) values match
    `floors.json` to ≤1e-12, `ref_zero` ≡ 1.0 on every dataset. Prediction confidence
    high; the stripped view removes only test LF files and the floors need train HF +
    test conditions + test HF, all present. A miss here is the most valuable possible
    outcome of the card (it would invalidate the round's denominators).
  - **Certifier skill** (seed-0 point estimates, `provisional-single-seed` labelling
    does not apply since 3 seeds run): helmholtz 3–15 (report-only; round-1's
    condition→field `mf_fno_transfer_film` rescaled to 10.06–20.74 there, *worse than
    the 3.3441 zero floor*), pfc 45–60, allen_cahn 200–280, fisher_kpp 8–12,
    cahn_hilliard 20–24, ifc_poisson 8–14. Panel geomean ≈ 20–30, i.e. **at or slightly
    worse than the 23.0636 anchor** — my honest prior is that a minimal condition-only
    decoder does NOT decisively beat the training-free floor panel, clearing roughly
    2–3 of the 5 assessable thresholds (most likely fisher_kpp and cahn_hilliard;
    least likely ifc_poisson at N_hf = 5 and helmholtz).
  - **Certified min-claimable-effects**: smaller than the provisional constants on the
    sharp datasets (predict pfc ≈ 1–4 vs 6.9839, allen_cahn ≈ 4–15 vs 14.8152,
    fisher_kpp ≈ 0.2–0.6 vs 1.2198, cahn_hilliard ≈ 0.2–0.8 vs 1.1604), similar or
    smaller on helmholtz (≈ 1–4 vs 10.6811), and **larger on ifc_poisson** (≈ 0.5–3 vs
    0.2399 — 5 training fields, no val split, so seed sensitivity should dominate).
    All of these clear the round-1-rescaled provisional values as *comparisons*, which
    is the point: the card replaces a borrowed constant with a measured one.
  - **Conditional-mean floor estimate (ADR r2-0003)**: LOO-selected k* large
    (k* ≥ 16) on pfc, fisher_kpp and allen_cahn with the k*-NN-mean skill within ~10%
    of `train_mean` (pfc ≈ 55–60 vs 59.8118; fisher_kpp ≈ 9–12 vs 11.9931) ⇒ the
    condition carries little information beyond the mean there and the barrier is
    close to the mean floor; k* small (≤ 4) on helmholtz and cahn_hilliard (the only
    sharp dataset with IC parameters — 16 of its 19 dims are `ic_c*`). If pfc's k*
    comes out 1, ADR r2-0003's stochastic-map reading is wrong on that dataset and
    that is a reportable correction.
  - **vs noise floor**: every threshold used below is a *difference* against the frozen
    deterministic floors offset by the provisional per-dataset min-claimable-effect, so
    each exceeds its dataset's noise floor by construction (numbers in the clause).
- **Expected falsification**: the card's hypothesis ("a minimal condition-only FiLM-FNO
  decoder is a sound certifier — it reproduces the frozen floors exactly, clears the
  training-free floor panel by more than the provisional noise on most assessable
  panel datasets, and its 3-seed spread licenses smaller effects than the borrowed
  round-1 constants") is falsified if ANY of: (F1) the certifier fails to beat the best
  training-free floor by more than the provisional per-dataset min-claimable-effect on
  ≥3 of the 5 assessable panel datasets — thresholds skill < 52.83 pfc, < 254.38
  allen_cahn, < 10.77 fisher_kpp, < 22.02 cahn_hilliard, < 9.81 ifc_poisson (helmholtz
  is report-only: its provisional constant 10.6811 exceeds its whole best-floor value
  3.3441, so no assessable threshold exists there); (F2) ≥3 of the 6 certified
  `min_claimable_effect`s land ≥ their provisional counterparts (10.6811 / 6.9839 /
  14.8152 / 1.2198 / 1.1604 / 0.2399), i.e. condition→HF training is noisier than
  round-1's LF-consuming families and 3 seeds license only enormous effects; or (F3)
  any recomputed training-free floor deviates from `state/anchors/floors.json` by
  >1e-9 relative, or `ref_zero` ≠ 1.0 exactly, on any of the 9 panel+guard datasets —
  which would mean the stripped view is not a faithful restriction and would suspend
  every round-2 number until resolved.
  **Reasoning attached to the clause** (required framing, not a threshold):
  (a) the mandatory floor arms (NN-in-condition / train-mean / zero, from
  `state/anchors/floors.json`) are the comparison in F1 and are reported as `ref_*`
  splits next to the model on every dataset — a certifier that does not beat the best
  floor has learned nothing there whatever its skill (§2.2); (b) F1's failure is NOT
  automatically a model failure on pfc/fisher_kpp/allen_cahn, because ADR r2-0003 makes
  condition→HF stochastic there and the k*-NN conditional-mean estimate in the same run
  says how much of the gap is aleatoric; (c) Yang et al.'s non-monotone LUPI law
  (https://arxiv.org/abs/2209.08754 — student performance rises then falls as the
  privileged feature becomes more predictive, via teacher variance) is why this card
  certifies the **without-LF** arm first and pre-registers it for B2: on this panel the
  LF field is extremely predictive (copy-LF is the reference), so the LUPI prior
  predicts LF-as-teacher may *hurt*; a B2 contrast that finds LF adding nothing or
  hurting is a positive result under that law, and it pairs with the round-1
  nested-ladder degeneracy (LF is a spectral truncation of HF and may add no
  information at all) — neither outcome may be read as a bug in the with-LF arm.
- **Anchor reference**: `null` (program.md §4.5 / §12: all four round-2 streams are
  gap/lever/diag; the own-stream anchor — best-floor panel geomean 23.0636 — is
  implicit and there is no champion-re-targeting tuning stream this round).

## Immutables self-check (positive evidence for each)

1. **Data read-only** — the family and both probes only READ
   `stripped_data_root/<ds>` via `loaders.load_mf_dataset` (train + test); nothing
   writes into any dataset dir, no dataset is regenerated, N_hf is whatever the loader
   returns (400 sharp / 5 ifc), and no LF is downsampled from HF anywhere (the
   certifier never touches an LF field at all, at train or test).
2. **Panel + guard fixed** — `recipe.datasets = "panel"` resolves to the six datasets
   in `project.yaml panel:`; the floor-reproduction probe covers exactly those six plus
   the three `guard_set` entries (`heat_local`, `fluid`, `sharp__sod_1d`) that already
   have rows in `state/anchors/floors.json`. No dataset is added or dropped.
3. **Eval layer / spec untouched** — every artifact lives under
   `worktrees/r2s4_diag/B1/{models_r2/r2s4_cert_min,probes,scripts}` and
   `mffp_autoresearch_outputs/round2/r2s4_diag/B1/`; the card invokes the unmodified
   `round2/eval/score_panel.py` CLI, reads `state/anchors/floors.json` read-only, and
   requires no edit to `round2/eval/`, `project.yaml`, `program.md`, or any agent
   prompt. `state/noise_floor.json` is replaced by the ORCHESTRATOR from the card's
   emitted `noise_floor_candidate.json`, which is exactly what program.md §4.3 and
   §12.4 pre-direct.
4. **One nRMSE definition** — the scored number is produced by
   `finalize_and_write` → `splits.test_hf.rel_l2_per_sample`, which
   `score_panel._extract_test_metric` consumes (preferring `test_hf`) and divides by the
   frozen `copylf_baselines.json` denominator; the training loss is MSE in z-scored
   space, which immutable 4 explicitly leaves free. The `ref_*` floor splits go through
   the same per-sample rel-L2 code path.
5. **Contract CLI fixed** — `smoke_eval.py` exposes exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; all 19 tunables are
   environment knobs and all 19 are listed in `recipe.env` (they therefore enter
   `score_panel.code_hash`, which hashes sorted env items).
6. **Seeds and tier epochs fixed** — `epochs: 200` is the smoke tier from
   `project.yaml tiers.smoke_epochs`; `seeds: [0,1,2]` is not a deviation but the
   §12.4 pre-direction ("seeds {0,1,2} … Diagnostic card, but WITH training (3 seeds) —
   the exception is the point"); no full-tier (2500-epoch) run is requested.
7. **Guarded factory surfaces untouched** — the family imports three read-only helpers
   from `mf_field/factory_mffp/data_adapters/` (`loaders.load_mf_dataset`,
   `geometry.resolve_grid`, `metrics.finalize_and_write`) exactly as round-1 families
   did; it creates nothing under `factory_mffp/{eval,baselines,references,scripts,data}`,
   does not touch `factory.md` or `akash/`, and adds no file under
   `factory_mffp/models/`.
8. **Checkpoint resume** — `smoke_eval.py` writes `<ckpt_dir>/last.pt` every epoch with
   `{epoch, model_state, opt_state, sched_state, rng_states, epochs_target, grid, seed,
   best_val, best_state}` and, on start, loads it and continues when
   `(epochs_target, grid, seed)` match, so a `mit_preemptable`/`gpu` preemption resumes
   instead of restarting; the two probes are stateless and idempotent (deterministic,
   re-runnable).
9. **Falsification threshold exceeds the noise floor** — each F1 threshold is
   `best_floor − provisional_min_claimable_effect`, so the required margin IS the noise
   floor: pfc 59.8118 − 6.9839 = 52.83, allen_cahn 269.1959 − 14.8152 = 254.38,
   fisher_kpp 11.9931 − 1.2198 = 10.77, cahn_hilliard 23.1803 − 1.1604 = 22.02,
   ifc_poisson 10.0549 − 0.2399 = 9.81; helmholtz is excluded and marked report-only
   precisely because its provisional constant (10.6811) exceeds its best-floor value
   (3.3441), so no threshold there could clear the floor. F2's comparands are the
   provisional constants themselves; F3 is a deterministic seam check (zero seed noise
   by construction — the floors are training-free).
10. **Not a pre-falsified lever** — the three pre-falsified levers are the WNO backbone
    swap (`wno_transfer_film`), LF low-mode freezing (`mf_fno_spectral`), and the
    diffusion prior for point accuracy (`mf_fno_diffprior`). Nearest is *LF low-mode
    freezing*, and the difference is total: this card reads **no LF at any point**, so
    there is no LF spectrum to freeze; the backbone is a standard FNO (not WNO) and
    there is no generative/diffusion component. Rebadge check (§5.10): no round-1
    family is reused as code, checkpoint, teacher or sub-component; the closest
    round-1 relative, `mf_fno_transfer_film`, differs by being LF-pretrain→HF-finetune
    (it consumes LF at training time) whereas this certifier is HF-only and
    coordinate-input — which is exactly why it is the pre-registered *without-LF* arm.
11. **Floor arms** — this is a `diagnostic` card, so §2.2's model-card rule does not
    bind it; nevertheless all three mandatory arms (NN-in-condition, train-mean, zero)
    from `state/anchors/floors.json` are emitted as `ref_*` splits beside the model on
    every dataset, are the explicit comparison in falsification clause F1, and are
    additionally re-derived from the stripped view and diffed against the frozen file
    in F3. The standing zero column is reported on helmholtz per §12.1.

## Status

- Slot covered: **yes** — one proposal, `diagnostic` card type, category
  `diagnostic / floor + seed-spread certification (condition→HF)`.
- Skipped: no.
- Reopen candidates resolved: none exist (no prior cards in any stream —
  `experiment_cards/*/` empty).
- Immutables self-check: **pass (11/11)** — positive evidence recorded above for each
  of the 8 program.md §5 items and the 3 round-2 extras. No revision needed; no
  `iteration_2.md`.
