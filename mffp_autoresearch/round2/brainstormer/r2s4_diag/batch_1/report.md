# Brainstormer Report — Stream `r2s4_diag`, Batch 1

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 1
**Total iterations**: 1
**Slot filled**: 1 / 1 (no skip)
**Reopen candidates resolved**: 0 (none exist — `experiment_cards/*/` is empty)

## Slot

- **Category**: `diagnostic / floor + seed-spread certification (condition→HF)`
- **Card type**: `diagnostic` (WITH training — the program.md §12.4 exception:
  `epochs = 200`, `seeds = [0,1,2]`)
- **Motivation**: program.md §12.4 pre-directs B1 to "(a) Verify the frozen floors
  reproduce (standing zero-predictor column included); (b) train ONE minimal
  condition→HF baseline … at smoke tier, seeds {0,1,2}, on the panel — its per-dataset
  seed spread replaces the provisional `state/noise_floor.json`". The websearcher's
  verdict says the *methods* are published and must be adopted by citation while the
  *constant* and the *composition* are open (D1a `preempted (cite)`, D1b
  `preempted-but-MF-composition-open (cite)` — quoted verbatim below). The card
  therefore adopts Agarwal et al.'s few-run protocol (IQM + stratified bootstrap) and
  Du's paired per-seed-delta protocol rather than inventing one, and delivers (i) the
  empirical min-claimable-effect constants for this panel/regime, (ii) the open
  composition — training-free floors expressed in copy-LF **skill** units for a
  no-solver-at-test regime, reproduced from the STRIPPED view, (iii) a training-free
  conditional-mean-floor estimate that quantifies ADR r2-0003's stochastic-map barrier,
  and (iv) the pre-registered **without-LF arm** for §12.4's B2 value-of-LF accounting.
- **Concrete config**: new from-scratch family `models_r2/r2s4_cert_min/`
  (`manifest.json`, `model.py`, `smoke_eval.py`, `INSPIRATION.md`) plus two worktree
  probes.
  1. **Certifier** (scored `test_hf` split): condition-only FiLM-FNO decoder — input is
     a normalized coordinate grid (2 channels), 1×1 lift to width 32, **2 FNO blocks at
     16 modes**, per-block FiLM (γ,β) from a 2-layer MLP (width 64) on the per-dim
     train-standardized condition vector, 1×1 head → 1 channel (~1M params). **No field
     input anywhere; no LF read at train or test.** Trained on the HF train split only,
     MSE in global train-z-scored target space, AdamW lr 1e-3 / wd 1e-5, batch 16,
     cosine schedule, grad-clip 1.0, 200 epochs; 10% seeded val split with best-val
     selection, **disabled when N_hf < 20** (ifc_poisson has 5 — final-epoch weights,
     recorded as a caveat). Scored on the NATIVE HF grid (all panel grids ≤ WORK_CAP
     256 ⇒ no interpolation) via `data_adapters.metrics.finalize_and_write`;
     checkpoint-resume from `<ckpt_dir>/last.pt` keyed on (epochs_target, grid, seed).
     Modes 16 rather than the factory default 12 because round-1 finding F22
     ("`modes_cap = 12` never scales with resolution") would band-limit the model at
     256² and artificially *shrink* the very spread this card certifies.
  2. **Floor arms in the same run**: `ref_nn_condition`, `ref_train_mean`, `ref_zero`
     splits recomputed from the stripped view through the same nRMSE path and merged
     after `finalize_and_write` (leaving `test_hf` byte-identical).
  3. **`probes/floor_repro.py`** (training-free, deterministic, once at seed 0, all 9
     panel+guard datasets): reproduces the 3 frozen arms from the stripped view and
     diffs against `state/anchors/floors.json` at 1e-9; reports the ifc_poisson 5-atom
     NN-dictionary caveat (`nn_index_hist_top5` = {0:41,1:17,2:20,3:38,4:12} covering
     all 128 test points) and the helmholtz standing zero column; then computes the
     **k-NN-in-condition mean** curve for k ∈ {1,2,4,8,16,32,64,128,400} (k=1 ≡
     `nn_condition`, k=N ≡ `train_mean` are the sanity anchors), selects k* by
     **leave-one-out on TRAIN only** (no test peeking), and reports test skill at k* as
     the **conditional-mean-floor estimate** (ADR r2-0003 folded into B1).
  4. **`probes/certify_spread.py`** (CPU, after all 3 seeds): emits
     `noise_floor_candidate.json` with per dataset `per_seed_skill`, `iqm`, `mean`,
     `ci95_stratified_bootstrap`, `spread_maxmin`, `paired_null_95`,
     **`min_claimable_effect = max(spread_maxmin, paired_null_95)`**, the sign-flip
     permutation p-value of a same-model seed-pair (null) contrast, and provenance.
     The `max(...)` definition guarantees a usable number **even if the conservative
     paired protocol declares nothing significant** (Du: three seeds never declare
     sub-2-point effects). The ORCHESTRATOR installs the file over
     `state/noise_floor.json` (§4.3/§12.4); the card does not write `state/`.
  **Scope boundary recorded**: the *validation* half of r2s1's D3 (showing the missing
  driver lives in the withheld LF field) is explicitly NOT in B1 — it is LF-side work
  for r2s1/r2s2/r2s3 or a later r2s4 batch. Overfitting anatomy (D3) is deferred: the
  websearcher rates it LOW confidence and asks for a fresh search first.
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
  (`base_commit` = `round2-substrate` HEAD, verified by `git rev-parse round2-substrate`.
  Cost estimate: 6 datasets × 3 seeds × 5k optimizer steps of a ~1M-param FNO ⇒ ≤30 min
  per seed; `state/timing_ledger.json` is empty, so request the 04:00:00 default from
  `resource/logistics/slurm_rules.md`.)
- **Expected outcome** (a diagnostic measures; these are predictions to be scored, in
  skill units under the corrected denominators, anchor = best-floor panel geomean
  **23.0636**):
  - Floor reproduction **exact** — all 9 datasets × 3 arms match `floors.json` to
    ≤1e-12 and `ref_zero` ≡ 1.0. A miss is the highest-value outcome of the card (it
    would invalidate the round's denominators).
  - Certifier skill: helmholtz 3–15 (**report-only**; round-1's condition→field
    `mf_fno_transfer_film` rescaled to 10.06–20.74 there — worse than the 3.3441 zero
    floor), pfc 45–60 (floor 59.8118), allen_cahn 200–280 (269.1959), fisher_kpp 8–12
    (11.9931), cahn_hilliard 20–24 (23.1803), ifc_poisson 8–14 (10.0549). Panel geomean
    **≈ 20–30, i.e. at or slightly worse than the 23.0636 anchor** — the honest prior is
    that a minimal condition-only decoder clears only ~2–3 of the 5 assessable floor
    thresholds, so the falsification clause has a genuine chance of firing.
  - Certified min-claimable-effects vs the provisional (round-1-rescaled) constants:
    predict **smaller** on the sharp panel (pfc ≈ 1–4 vs 6.9839; allen_cahn ≈ 4–15 vs
    14.8152; fisher_kpp ≈ 0.2–0.6 vs 1.2198; cahn_hilliard ≈ 0.2–0.8 vs 1.1604),
    smaller on helmholtz (≈ 1–4 vs 10.6811), and **larger on ifc_poisson** (≈ 0.5–3 vs
    0.2399 — 5 training fields and no val split).
  - Conditional-mean floor (ADR r2-0003): LOO-selected **k\* ≥ 16** on pfc / fisher_kpp
    / allen_cahn with k\*-NN-mean skill within ~10% of `train_mean` (pfc ≈ 55–60 vs
    59.8118; fisher_kpp ≈ 9–12 vs 11.9931) ⇒ the barrier sits near the mean floor
    there; **k\* ≤ 4** on helmholtz and cahn_hilliard (the only sharp dataset with IC
    parameters — 16 of 19 dims are `ic_c*`). If pfc's k\* = 1, ADR r2-0003's
    stochastic-map reading is wrong there and that is a reportable correction.
  - **vs noise floor**: every falsification threshold is `best_floor −
    provisional_min_claimable_effect`, so the required margin *is* the dataset's noise
    floor (numbers in the clause below); F3 is deterministic (training-free floors have
    zero seed noise).
- **Expected falsification**: the card's hypothesis — "a minimal condition-only FiLM-FNO
  decoder is a sound certifier: it reproduces the frozen floors exactly, clears the
  training-free floor panel by more than the provisional noise on most assessable panel
  datasets, and its 3-seed spread licenses smaller effects than the borrowed round-1
  constants" — is falsified if ANY of: **(F1)** the certifier fails to beat the best
  training-free floor by more than the provisional per-dataset min-claimable-effect on
  ≥3 of the 5 assessable panel datasets (skill thresholds **pfc < 52.83**,
  **allen_cahn < 254.38**, **fisher_kpp < 10.77**, **cahn_hilliard < 22.02**,
  **ifc_poisson < 9.81**; helmholtz is report-only because its provisional constant
  10.6811 exceeds its entire best-floor value 3.3441); **(F2)** ≥3 of the 6 certified
  `min_claimable_effect`s land ≥ their provisional counterparts (10.6811 / 6.9839 /
  14.8152 / 1.2198 / 1.1604 / 0.2399), i.e. condition→HF training is noisier than
  round-1's LF-consuming families and 3 seeds license only enormous effects; or **(F3)**
  any recomputed training-free floor deviates from `state/anchors/floors.json` by >1e-9
  relative, or `ref_zero` ≠ 1.0 exactly, on any of the 9 panel+guard datasets.
  *Attached reasoning*: (a) the mandatory floor arms (NN-in-condition / train-mean /
  zero, from `state/anchors/floors.json`) are F1's comparison and are reported as
  `ref_*` splits beside the model on every dataset — a model that does not beat the
  best floor has learned nothing there (§2.2); (b) an F1 failure on
  pfc/fisher_kpp/allen_cahn is not automatically a model failure, because ADR r2-0003
  makes condition→HF stochastic there and the same run's k\*-NN conditional-mean
  estimate says how much of the gap is aleatoric; (c) **Yang et al.'s non-monotone LUPI
  law** (https://arxiv.org/abs/2209.08754: student performance rises then falls as the
  privileged feature becomes more predictive, via teacher variance) is why B1 certifies
  the **without-LF** arm first and pre-registers it for B2 — on this panel the LF field
  is extremely predictive (copy-LF is the reference), so the LUPI prior predicts
  LF-as-teacher may *hurt*; combined with round-1's nested-ladder degeneracy (LF is a
  spectral truncation of HF), a B2 contrast finding LF adds nothing or hurts is a
  positive result under that law, not a bug.
- **Prior-art verdict quoted** (verbatim from
  `websearches/r2s4_diag/batch_1/report.md` §Prior-art verdict):
  > **D1a** — certify a minimum-claimable-effect from a 3-seed condition→HF spread
  > (replaces provisional `noise_floor.json`) | `preempted (cite)` | Agarwal et al.,
  > *Deep RL at the Edge of the Statistical Precipice* —
  > https://ar5iv.labs.arxiv.org/html/2108.13264 ; Du, *When +1% Is Not Enough* —
  > https://arxiv.org/abs/2511.19794 | Nothing methodological. Open item is the
  > **empirical constant** for this panel/regime. Adopt IQM + stratified/paired BCa
  > bootstrap CIs + per-seed deltas instead of a bare max−min spread; expect 3 seeds to
  > license only LARGE effects.

  > **D1b** — training-free floor panel (NN-in-condition / train-mean / zero) as
  > mandatory reported arms | `preempted-but-MF-composition-open (cite)` | McGreivy &
  > Hakim — https://arxiv.org/abs/2407.07218 (79% weak baselines) ; *Predictivity and
  > Utility…* — https://arxiv.org/html/2604.20061v1 (interpolation diagnostic) ;
  > Westermann et al. — https://arxiv.org/abs/2604.00689 (polynomial beats neural, low
  > data) ; Operator Boosting — https://arxiv.org/abs/2606.17460 (mean predictor as
  > floor) | All published floors are **fitted** (ROM, polynomial, GP, kriging). Two
  > dedicated searches found no *training-free* trivial-predictor panel reported as
  > mandatory columns, and none expressed in **copy-LF skill units** for a
  > no-solver-at-test regime. That composition is open.

  Supporting rows used in the falsification reasoning: **D2** —
  `preempted-but-MF-composition-open (cite)`, "Yang et al., *Toward Understanding
  Privileged Features Distillation in LTR* — https://arxiv.org/abs/2209.08754 (matched
  no-distillation arm; non-monotone law)". Cross-stream, from
  `websearches/r2s1_direct/batch_1/report.md`: **D1** (FiLM-conditioned spectral
  decoder) — "**preempted** … Admissible only as a *measurement/baseline arm* on this
  panel against the mandatory floor arms", which is precisely the declared role of the
  certifier here.
- **Immutables self-check**: **pass (11/11)** — positive evidence for each of the 8
  program.md §5 items plus the 3 round-2 extras is recorded in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Highlights: no LF is read
  at any point (settles items 1 and 10 — nearest pre-falsified lever is LF low-mode
  freezing, and there is no LF spectrum to freeze); all 19 knobs appear in
  `recipe.env` (item 5); `seeds: [0,1,2]` is the §12.4 pre-direction, not a deviation
  (item 6); the F1 thresholds are `best_floor − provisional_min_claimable_effect` and
  therefore exceed the noise floor by construction (item 9); helmholtz is excluded from
  F1 and marked report-only because no threshold there could clear its floor.
- **Anchor reference**: `null` (program.md §4.5 / §12 — round-2 streams are
  gap/lever/diag; the own-stream anchor, best-floor panel geomean 23.0636, is implicit;
  no champion-re-targeting tuning stream exists this round).
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _none_ — `experiment_cards/r2s4_diag/` and every other stream's card dir are empty (batch 1 is the round's first card), so no card carries `reopen_candidate: true` | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B1 | `diagnostic / floor + seed-spread certification (condition→HF)` | Reproduce the three training-free floors from the stripped view on all 9 panel+guard datasets (1e-9 seam, standing zero column) and add a LOO-selected k-NN-in-condition **conditional-mean-floor** estimate (ADR r2-0003); train one minimal, LF-free FiLM-FNO condition→HF decoder at smoke tier on the panel at seeds {0,1,2}; certify per-dataset `min_claimable_effect = max(max−min spread, paired-bootstrap 95th-percentile null)` via Agarwal's IQM/stratified bootstrap and Du's paired per-seed-delta protocol, replacing the provisional `noise_floor.json` and pre-registering the without-LF arm for B2. | filled |
