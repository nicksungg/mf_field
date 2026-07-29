# Iteration 1 — s5_tuning batch 2 design

## Design context considered

- `summary_so_far.md` section 6 (the seven unknowns) + the batch-2 prior-art
  verdict table and its binding territory ruling.
- The immutables block (program.md 5) verbatim — reproduced in the self-check
  below, one item at a time.
- Anchor `state/anchors/s5_tuning.json`: **6.703** panel geomean
  (`mf_fno_transfer_film`, 3-seed mean, per_seed [7.1022, 6.2185, 6.7883],
  `provisional: false`). Geomean floor **0.884** = that spread.
  `state/noise_floor.json` `min_claimable_effect`: helmholtz **9.695**,
  allen_cahn **1.633**, pfc **1.151**, cahn_hilliard **0.553**, fisher_kpp
  **0.418**, ifc_poisson **0.240**.
- program.md 12.5 (knobs only; no losses-as-mechanisms, no new paradigms, no
  architecture) + ADR 0004 (strict single seed), ADR 0005 (H100 + the
  same-hardware cap-12 control at geomean 7.1171), ADR 0007 (propose-many /
  screen-cheap / promote-few; screen numbers never reportable; promoted arm
  fixed BEFORE submit), ADR 0009 (no governing equations at test time).
- s5-B1 parts 5-7 (mechanism: helmholtz-only amplitude channel; DC-predictor
  collapse on 3 of 4 sharp sets; LF-blind at inference; part-7 next_direction =
  the normalization knob).
- Cross-stream: s6-B1 geomean 0.2346 (LF-consuming, `analyzing`/under
  scrutiny) — the LF-blind champion is no longer the frontier, so this card is
  framed as mechanism attribution + a portable knob, not a leaderboard play.
- **Five design-time measurements I ran on the read-only train splits** (venv
  python, cwd `mf_field/factory_mffp`, `data_adapters.load_mf_dataset`):

  | dataset | per-sample spread of `max|Y_hf|` | HF/LF `max|.|` ratio p95/p5 (CV) | `max/p99.5` | `max/std` | `|mean|/std` | `scaler_lf/scaler_hf` | kNN-in-X logRMSE (k=3, `max|Y|`) |
  |---|---|---|---|---|---|---|---|
  | ext__helmholtz_2d | **3928.8x** | **1.74 (0.689)** | **46.54** | 39.47 | 0.042 | 0.235 | 0.875 |
  | ifc_poisson (N_hf=5) | 3.2x | n/a (no LF in test) | 1.63 | 9.86 | 1.426 | **42.10** | 0.416 |
  | sharp__allen_cahn_2d | 8.6x | 1.02 (0.0067) | 1.26 | 2.54 | 0.005 | 0.9997 | 0.160 |
  | sharp__cahn_hilliard | 1.2x | 1.001 (0.0017) | 1.08 | 1.32 | 0.0002 | 0.9954 | 0.027 |
  | sharp__fisher_kpp_2d | 1.1x | 1.03 (0.0099) | 1.05 | 6.00 | **3.749** | 0.9947 | 0.009 |
  | sharp__phase_field_crystal_2d | 4.3x | 1.01 (0.0052) | 1.19 | 3.81 | 1.317 | 0.9850 | 0.084 |

  Also verified: `data/ifc_poisson/test/` contains **only** `fidelity_64`, so no
  LF field exists at inference there (train has 8/16/32/64); the five other
  panel datasets ship `test_l1` (the fidelity the family pretrains on).

## Proposal reasoning

### The measurement that reorders the websearcher's ranking

The websearcher ranked "(ii) robust scaler first for defensibility, (i)
per-sample first for upside". The design-time pre-check changes this, and it is
worth stating exactly why, because it is the RevIN conditional-shift caveat
firing before any GPU time is spent:

- **Per-sample scaling is a measured no-op on the four sharp datasets.** Their
  per-sample `max|Y_hf|` spread is 1.1-8.6x and the HF/LF ratio has
  CV 0.0017-0.0099 — there is essentially nothing for a per-sample scale to
  remove. It is a large lever on helmholtz only (3929x spread collapsed to a
  1.74x residual by one LF scalar) — and helmholtz's floor 9.695 forbids a
  numeric claim. It is *unavailable* on ifc_poisson (HF-only test split).
  Consistent with B1 turn 3: "The sharp regression is not amplitude".
- **The robust-quantile scaler is also mostly a helmholtz knob**: `max/p99.5`
  is 46.5 there but 1.05-1.26 on the sharp sets. Its one claimable target is
  ifc_poisson (1.63x, and `max|Y|` over N_hf=5 samples is the noisiest scaler
  the recipe could possibly use).
- **The stage-consistency hypothesis from B1 part 7 is already 80% retired by
  arithmetic**: `scaler_lf/scaler_hf` is 0.985-1.000 on all four sharp sets, so
  "the output scale is re-anchored at fine-tune time" cannot explain the
  sharp-panel pattern collapse. It survives only on ifc_poisson (42.1x) and
  helmholtz (4.3x).
- **The one scaler axis with non-trivial leverage on claimable datasets is the
  affine (centring) part** that the family's `max|Y|` scaler does not have:
  pooled `|mean|/std` is 3.75 (fisher_kpp), 1.43 (ifc_poisson), 1.32 (pfc).
  On those three the network currently spends most of its normalized output
  range reproducing a constant, while the variation the metric scores lives at
  a fraction of it. That is exactly the `UnitGaussianNormalizer` default of the
  reference FNO implementation the family departs from — verdict `preempted`
  (claim nothing, measure).

So the ranking that follows from our own data is **z-score first**, and the
falsifiable content of the card lives on `sharp__fisher_kpp_2d` (floor 0.418,
the tightest on the panel) and `ifc_poisson` (floor 0.240).

### Honest mechanism statement (recorded so the card cannot overclaim)

For every *global* arm, `y -> (y - mu)/s` is an affine reparameterization of the
target; with a bias in the output layer the function class is unchanged. Any
effect therefore runs through optimization conditioning: initialization scale
vs target scale, the fixed `lr_pretrain 1e-3` / `lr_finetune 3e-4`,
`weight_decay 1e-5`, and `grad_clip 1.0` (which interacts directly with the
loss scale — a 39x target rescale on helmholtz changes when clipping bites).
This is a legitimate 12.5 knob (F19/F20-adjacent: the fitted objective's
conditioning vs the scored metric) and it is NOT an information change. Only
arm A3 changes the model's information set (one LF scalar per test sample);
that is flagged in its own row and is one reason it is ranked third.

### Alternatives weighed and rejected

1. **Per-sample LF RevIN as the promoted arm** (the websearcher's upside pick).
   Rejected as the headline: measured no-op on the four sharp sets, unavailable
   on ifc_poisson, and its only real leverage is on the dataset that carries no
   numeric claim. Kept as screened arm A3 because it is the canonical
   construction the verdict licenses and its *pre-registered null* on the sharp
   panel is itself the RevIN caveat, tested.
2. **Clipping at the 99.5th percentile** (QuantileTransformer style). Rejected:
   the same scikit-learn source warns outliers get "collapse[d] ... to the a
   priori defined range boundaries" causing "saturation artifacts", and
   clipping helmholtz's 46x tail would change what the model is asked to fit —
   which would break the knob framing. A1 divides by the quantile and does
   **not** clip, so the target is unchanged up to one constant.
3. **A learnable affine on top of the per-sample normalization** (RevIN's
   `alpha`/`beta`). Rejected twice over: RevIN's own ablation finds it "not
   beneficial in practice", and it would add parameters, moving the card to s6.
4. **modes_cap + muP-LR** (the operator's held branch). Rejected per B1 part 7's
   own recommendation: the extra modes are filled with uncorrelated energy on 5
   of 6 panel datasets, so re-tuning the LR for them optimizes a knob with a
   measured negative sign. `MFFP_MODES_CAP` is held at the champion default 12
   and passed explicitly for provenance.
5. **Re-targeting s6-B1's LF-consuming family instead of the champion.**
   Rejected: s6-B1 is `analyzing` and under scrutiny, not a certified champion,
   and 12.5's anchor is the batch-0 certified champion geomean. The knob is
   built so it transfers to any family later (one env-switchable scaler block).
6. **A dataset-level per-channel z-score with spatial (H,W) statistics.**
   Rejected: fields are single-channel, so `UnitGaussianNormalizer`'s
   `(1,C,1,1)` reduction *is* two scalars — a spatially varying normalizer would
   be a new mechanism (a learned/derived field), i.e. outside 12.5.
7. **Operator's TabPFN / kNN-in-X per-sample scale predictor — EXCLUDED**, with
   three recorded reasons:
   (a) **Territory.** The verdict's zero-parameter clause is about statistics of
   the sample's *own* inference-available data (RevIN's construction). Fitting an
   auxiliary regressor on the train split and inserting its output into the
   forward path is a *second predictor composed with the network* — precisely
   APEX's construction, which the websearcher found the literature frames as an
   **architecture** ("coarse operator + amplitude extraction + flow-matching
   enhancer"). TabPFN specifically would import a pretrained transformer's
   learned weights into the family, which is unambiguously not a knob. My ruling:
   s6/s4 territory, and 12.5's "no new paradigms" clause independently excludes it.
   (b) **Dominated where it matters.** Measured leave-one-out kNN-in-X on
   helmholtz: logRMSE 0.875, pred/true p95/p5 = 14.2 (a ~2.4x typical
   multiplicative error) versus **1.74** for the free LF-field statistic — 8x
   looser on the one dataset with amplitude headroom.
   (c) **No headroom where it is uniquely usable.** ifc_poisson is the only panel
   dataset where X-based scaling reaches and LF does not, and there the raw scale
   spread is just 3.2x with B1 turn 2 measuring alpha ~ 0.996 (amplitude share of
   error 0.098/0.040) — nothing to win.
   Handed to s6/s4 as a cross-stream note *with these numbers*: any APEX-like
   amplitude-anchor composition should read the **LF field**, not X; the kNN
   degraded form needs no new dependency and can be screened for free.

## Proposal

- **Category**: `tuning_target_scaler` (knob sweep on the certified champion).
- **Card type**: `model`.
- **Motivation** (quotes the verdict row this card uses, verbatim from
  `websearches/s5_tuning/batch_2/report.md`):

  Row (ii), verdict `preempted`: "*Nothing novel — defensible ONLY as a
  measurement. Open as measurement: no fetched source quantifies robust-vs-max-abs
  **target** scaling in a **multi-fidelity few-shot** operator-learning regime;
  the nearest MF paper does not state its normalization at all
  (https://arxiv.org/html/2511.01830). Territory: **K**, unambiguously (two
  scalars, `smoke_eval.py:136-137`).*"

  Row (i), verdict `preempted-but-MF-composition-open`: "*Applying per-sample
  normalize/denormalize as a **scaler-only** change **across a fidelity
  boundary** (LF-pretrain -> HF-finetune), network and MSE byte-identical,
  N_hf = 5..400, scored on unchanged per-sample rel-L2. **Territory ruling**: K
  only if the scale comes from an inference-available statistic with zero new
  parameters (LF-field statistic or closed-form function of the condition
  vector).*"

  Row (iii), verdict `novel` (narrow) with unfavourable prior: "*The mechanism
  is unclaimed for a *target scaler* across a fidelity boundary, but the
  transfer literature treats stage-specific statistics as correct, so expect a
  null-or-negative sign. Value is as a **control arm** that removes a
  B1-part-7 hypothesis round-wide. Territory: **K**.*"

  Together with s5-B1 part 7 ("*the leading candidate is the NORMALIZATION
  knob, not another capacity knob*") these license exactly one card: measure the
  champion's output-target scaler, claim no novelty, and put the verdict on the
  datasets whose noise floor permits one.

- **Concrete config**: one worktree family
  `models_r1/mf_fno_transfer_film_scaler`, a copy of
  `mf_field/factory_mffp/models/mf_fno_transfer_film` at substrate commit
  `967562e2a4e3493515edab36b0fcb23655fce71f`, with B1's three plumbing deltas
  (REPO_ROOT fix; knob provenance in result-JSON `extra`; periodic `last.pt`
  with a config-match resume gate) and **one behavioural change**: the target
  scaler block (base `smoke_eval.py:210-211` and the denormalization at `:293`)
  becomes env-switchable, `MFFP_TARGET_SCALER`, default `maxabs` == the anchor
  path. Network, loss (plain `F.mse_loss`), optimizer, schedule, batch size,
  epochs, `modes_cap` (held at 12) all untouched. No learnable affine anywhere.
  The HF **test** field is never used to compute any scaler (no label leakage).

  | arm | `MFFP_TARGET_SCALER` | definition (both stages; denormalized with the same constants) | measured leverage | rank |
  |---|---|---|---|---|
  | A0 | `maxabs` | `s_stage = max(|Y_stage_train|)` — the base family | control / equivalence proof | never promoted |
  | A1 | `p995` | `s_stage = percentile(|Y_stage_train|, 99.5)`, **no clipping** | 46.5x (helm), 1.63x (poisson), 1.05-1.26x (sharp) | 2 |
  | A2 | `zscore` | `mu, sd = mean/std(Y_stage_train)` (two scalars = `UnitGaussianNormalizer` at C=1); `pred = f(x)*sd_hf + mu_hf` | `|mean|/sd` 3.75 fisher_kpp, 1.43 poisson, 1.32 pfc; `max/sd` 1.3-39.5 | **1 (default promotion)** |
  | A3 | `revin_lf` | per-sample `s_i = max(|LF_i|)` on the working grid, both stages, `pred_i = f(x_i)*s_i`; falls back to `maxabs` + `scaler_fallback: true` where the split has no LF (ifc_poisson) | 3929x -> 1.74x residual on helm; CV <= 0.0099 on sharp; unavailable on poisson | 3 |
  | A4 | `shared` | `s = max(|Y_lf_train|)` for BOTH stages (stage-consistency control) | 42.1x poisson, 4.3x helm, <= 1.5% sharp | 4 |

  **Screen (ADR 0007)**: ONE contract-tier job, 2 epochs, seed 0, all five arms
  x the full panel on H100 (B1: a 6-dataset 200-epoch panel took 36.6 min, so
  this is minutes). Screen numbers go to `build_notes` only and are never quoted
  in parts 5-7.

  **Fixed promotion rule (pre-registered, order set by the design-time
  measurements above, NOT by screen scores)**: promote the highest-ranked arm
  that is not *broken* at the screen, where broken := crash, non-finite metric,
  or contract-tier panel geomean > 3x arm A0's contract-tier geomean on the same
  run. Order A2 -> A1 -> A3 -> A4; A0 is never promoted. Close calls do not
  reorder anything. The promoted identity is written into the card before submit.

  **Also required at contract tier**: (a) default-equivalence — `maxabs` on
  `ext__helmholtz_2d,ifc_poisson` must reproduce the untouched factory family
  (the proof that licenses comparing to the batch-0 anchor); (b) `--datasets
  guard` with the promoted arm's env (program.md 2.3); (c) re-run of the
  pre-check as `scripts/precheck_scale_ratio.py` -> `notes/precheck_scale_ratio.json`,
  so the table above is reproduced in-repo and lands in `build_notes`.

  **Reporting additions (free, no novelty claimed)**: every panel number is
  reported alongside the constant-field oracle from `tools/dc_pattern_split.py`
  (each test sample's own spatial mean), citing The Well's "predicting the mean
  value of the target field results in a score of 1"
  (https://arxiv.org/html/2412.00568); the family dumps `preds_test.npz` as in
  B1 so the oracle line and the mechanism probes are computable without
  retraining.

  **Pre-registered dual basis** (fixing B1's `not_resolvable` outcome, whose
  cause was an unfixed comparison basis): PRIMARY = the certified anchor
  (geomean 6.703; per-dataset 3-seed means from `state/noise_floor.json`).
  SECONDARY, reported as a cross-check that cannot flip the verdict = s5-B1's
  H100 same-hardware cap-12 seed-0 control (geomean 7.1171; per-dataset
  `h100_same_hardware_cap12_seed0_skill`).

  **Builder note (verified this run)**: `score_panel.py:238` declares
  `--env nargs="*"` with `default=[]` and no `action="append"`, so a second
  `--env` occurrence REPLACES the first. Both knobs must go in a single
  invocation: `--env MFFP_TARGET_SCALER=<arm> MFFP_MODES_CAP=12`.

- **Recipe**:

```json
{
  "base_family": "mf_fno_transfer_film",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/mf_fno_transfer_film_scaler",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {"MFFP_TARGET_SCALER": "zscore", "MFFP_MODES_CAP": "12"}
}
```

  (`env` records the pre-registered default promotion A2. If the screen finds A2
  broken, the starter/builder substitutes the next arm in the fixed order
  BEFORE submit and records the substitution in `build_notes`; the screen itself
  runs with `MFFP_TARGET_SCALER` set per arm at 2 epochs. `--time 02:00:00`
  per project.yaml; B1's cap-12 panel is well inside it.)

- **Expected outcome** (arm A2 promoted; all vs the PRIMARY basis, seed 0,
  provisional-single-seed):
  - `sharp__fisher_kpp_2d`: **improvement >= 0.418** skill (4.177 -> <= 3.759).
    Why: pooled `|mean|/sd` = 3.75 and `max/sd` = 6.00, the largest affine
    change on the panel; the network stops spending 0.63 of its normalized
    output range on a constant that carries 93.8% of the field energy but
    almost none of the scored variation. This is the card's primary claimable
    threshold and it is exactly the certified floor (0.418).
  - `ifc_poisson`: **improvement >= 0.240** skill (1.566 -> <= 1.326). Why:
    `|mean|/sd` = 1.43, `max/sd` = 9.86, and with N_hf = 5 the `max|Y|` scaler
    is the noisiest statistic available (a mean/std over 5x4096 values is far
    more stable). Clears its floor 0.240 by construction of the threshold.
  - `sharp__phase_field_crystal_2d`: plausible mover (`|mean|/sd` = 1.32) but
    NOT predicted; floor 1.151 (10% relative) is demanding.
  - `sharp__allen_cahn_2d`, `sharp__cahn_hilliard`: **pre-registered NULL**
    (`|delta|` < floor 1.633 / 0.553). Why: `|mean|/sd` = 0.005 / 0.0002, so
    z-scoring is scale-only there (2.54x / 1.32x) — nearly the base recipe.
  - `ext__helmholtz_2d`: large movement likely (`max/sd` = 39.5, and B1 showed
    this dataset's nRMSE is a tail-amplitude statistic) — **reported
    qualitatively only**, floor 9.695, no part of the verdict.
  - Panel geomean: expected -0.3 to -0.9 vs 6.703, most or all of it helmholtz.
    Pre-registered: a geomean improvement that vanishes in the
    leave-helmholtz-out decomposition (anchor LHO geomean 5.842, B1 part 5
    `effect_decomposition`) is recorded as a tail artefact, not a panel win —
    the s5-B1 precedent.
  - vs noise floor: the two predicted movers are stated AT their certified
    floors (0.418, 0.240); every other dataset is a pre-registered null against
    its floor. Honest prior on the headline: ~40% that a claimable per-dataset
    improvement lands; the single most likely outcome is the null, which retires
    the normalization branch of B1 part 7 for the whole round. That is the
    genuine-experiment case under program.md 1 (informative either way).
  - Pre-registered RevIN findings: (1) no learnable affine is added anywhere
    (its ablation calls it "not beneficial in practice", and it would cost knob
    status); (2) the conditional-shift caveat is *already measured* — HF/LF
    ratio CV 0.0017-0.0099 on the four sharp sets means arm A3 cannot work
    there, and the pre-check reproduces this in-repo before any 200-epoch run.

- **Expected falsification** (one sentence, thresholds off helmholtz): if the
  promoted arm's seed-0 200-epoch panel run moves NO non-helmholtz panel dataset
  beyond its own `min_claimable_effect` in either direction (`ifc_poisson`
  0.240, `sharp__fisher_kpp_2d` 0.418, `sharp__cahn_hilliard` 0.553,
  `sharp__phase_field_crystal_2d` 1.151, `sharp__allen_cahn_2d` 1.633) AND the
  leave-helmholtz-out panel geomean moves by less than 0.884 vs the anchor's
  5.842, then the champion's output-target scaler is NOT a lever on the panel
  gap — the amplitude/level channel found in s5-B1 is confined to
  `ext__helmholtz_2d` where the round permits no numeric claim, and
  normalization is retired round-wide as an explanation for the sharp-2D
  DC-predictor collapse.

- **Anchor reference**: `"s5_tuning-B1"` (12.5: "later batches re-target the
  current champion card"; B1 is the stream's only complete card and it supplies
  the H100 same-hardware cap-12 control that this card's secondary basis uses.
  The numeric primary basis remains the batch-0 certified anchor 6.703).

## Status

- Slot **covered** (one `model` card, 5 screened arms, 1 promoted).
- Reopen candidates: **none exist** — all 10 cards in `experiment_cards/**`
  carry `reopen_candidate: false`; nothing to retry or drop.
- Operator suggestion (TabPFN / kNN-in-X scale predictor): **excluded with
  reasons recorded** (territory + dominated + no headroom), and handed to
  s6/s4 with the measured numbers.
- Immutables self-check: **pass (10/10)**, below.

## Immutables self-check (positive evidence, 10 items)

1. **Data read-only** — every array is read through the unmodified
   `data_adapters.load_mf_dataset`; the only new read is a *scalar statistic* of
   the LF field that arm A3's stage already loads (`train["field_by_fid"][lf]`,
   `test["field_by_fid"][lf]`), and the pre-check opens the same arrays
   read-only. Nothing is written under `factory_root/data/**`; N_hf stays 5 on
   ifc_poisson (no arm adds samples); the LF used is the real coarse solve
   (`fidelity_8`, `test_l1`), never a downsample of HF.
2. **Panel + guard fixed** — `recipe.datasets: "panel"` expands from
   `project.yaml`; guard runs at contract tier with the promoted arm's env; no
   dataset is added, dropped or re-weighted. The leave-helmholtz-out geomean is
   an ADDITIONAL decomposition with in-round precedent (B1 part 5
   `effect_decomposition.leave_helmholtz_out_geomean_anchor` = 5.842), not a
   redefinition of the scored panel.
3. **Eval layer / spec untouched** — all five arms live inside
   `<worktree>/models_r1/mf_fno_transfer_film_scaler/smoke_eval.py`; the knob
   reaches the family through machinery that already exists
   (`score_panel.py:238-255` parses `--env`, `_run_one` does
   `child_env.update(env)` at `:94`). No edit to `round1/eval/`, `project.yaml`,
   `program.md`, ADRs or subagent prompts is required by this design.
4. **One nRMSE definition** — the family keeps calling
   `data_adapters.metrics.finalize_and_write` and the score is read by the eval
   layer from `splits.<split>.rel_l2_mean` (B1 part 7 note 5); the scaler changes
   the prediction only, never the metric. `nrmse_def_hash` must equal B1's
   `d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`.
5. **Contract CLI fixed** — the six flags
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`) are
   unchanged; the only knobs are `MFFP_TARGET_SCALER` and the explicitly held
   `MFFP_MODES_CAP=12`, both recorded in `recipe.env`, and both enter the cache
   key via `code_hash(family_dir, env)` (`score_panel.py:51-73`). The single
   `--env` invocation requirement is written into the card as a builder note.
6. **Seeds {0,1,2} / tier epochs fixed** — screen at contract tier (2 epochs),
   promoted run at smoke tier (200 epochs), `recipe.seeds: [0]` per ADR 0004;
   `scripts/submit_seeds_2_3.sh` is still written seed-parameterized for the
   end-of-round top-3 confirmation. No full tier is requested.
7. **Guarded factory surfaces untouched** — the family is COPIED into the
   worktree's `models_r1/` (B1's reviewed-PASS pattern); nothing under
   `factory_root/{eval,baselines,references,scripts,data}/`, `factory.md` or
   `mf_field/akash/**` is edited, and `mf_field/factory_mffp/models/mf_fno_transfer_film`
   is read at a pinned commit only.
8. **Checkpoint resume from `<ckpt_dir>/last.pt`** — B1's periodic in-stage
   saves are retained, and `meta` gains `scaler_mode` with the resume
   `same_cfg` gate extended to it exactly as B1 did for `modes_cap`
   (`smoke_eval.py:226-239` in the B1 worktree), so a preempted run resumes
   mid-stage and an arm-mismatched checkpoint can never half-load. Scalers are
   deterministic functions of the (fixed) train split, so a resumed run
   recomputes them identically.
9. **Falsification threshold exceeds the noise floor for every cited dataset**
   — the clause cites exactly the certified `min_claimable_effect` values:
   `ifc_poisson` 0.23990756 (clause 0.240), `sharp__fisher_kpp_2d` 0.41773550
   (0.418), `sharp__cahn_hilliard` 0.55334659 (0.553),
   `sharp__phase_field_crystal_2d` 1.15110014 (1.151),
   `sharp__allen_cahn_2d` 1.63340708 (1.633), plus the geomean floor 0.884
   (= anchor per-seed spread 7.10224 - 6.21854). `ext__helmholtz_2d`'s floor
   9.695 is deliberately EXCLUDED from the verdict and reported qualitatively.
   The LHO geomean is judged against 0.884, the 6-dataset floor, which is
   conservative for a 5-dataset geomean that drops the widest-spread dataset.
10. **Not a pre-falsified lever** — nearest in-round falsification is s5-B1's
    own `modes_cap` 12->32 (not claimable at the panel level); this card holds
    that knob at its default 12 and changes a disjoint knob (the target
    scaler), and program.md 5's three pre-falsified levers (WNO backbone swap,
    LF low-mode freezing, diffusion prior) are all architecture/mechanism
    swaps that touch nothing in the normalization path. Arm A4 (`shared`)
    carries a documented *unfavourable prior* (AdaBN, https://arxiv.org/abs/1603.04779),
    not a falsification, and is a screened control arm that can only be promoted
    if the three arms above it are broken.
