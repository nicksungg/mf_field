# Brainstormer Report — Stream `r2s1_direct`, Batch 1

**Stream**: `r2s1_direct` (class: gap)
**Batch**: 1
**Total iterations**: 1 (cap 5)
**Slot filled**: 1 / 1 (model card)
**Reopen candidates resolved**: 0 of 0 (none exist — stream's first batch)

## Slot

- **Category**: `gap / identifiability-certified condition->HF decoder with a
  condition-predicted amplitude-direction factorization`

- **Card type**: `model`

- **Motivation**: The websearcher's verdict forbids the obvious card and names
  the one that is open: D1 ("FiLM/modulation-conditioned spectral (FNO) decoder:
  condition -> latent -> HF field, no field input") is **`preempted`** —
  "Nothing mechanism-level. Admissible only as a *measurement/baseline arm* on
  this panel against the mandatory floor arms" — and D3 is
  **`preempted-but-MF-composition-open`**: "(i) the barrier diagnostic has never
  been instantiated where the unobserved driver is a *stored coarse solve*,
  making the floor validatable rather than assumed; (ii) NN-in-condition /
  train-mean / zero as a standing certification panel is not done in the fetched
  benchmark literature." This card therefore (a) declares the D1 decoder as its
  baseline architecture, not its contribution; (b) adds the one regime-specific
  element the data demands — a **condition-predicted amplitude head** — which is
  the exact successor round 1 named when s5_tuning closed ("(i) a PREDICTED scale
  head", `round1/experiment_cards/s5_tuning/batch_3/B3.json` part 7, where the
  LF-proxy scaler reached nRMSE 0.367721 on helmholtz but the true-scale oracle
  reached 0.258380 = skill 0.864 under the corrected denominator, and where 60%
  of the damage was the amplitude channel per the two-gate rule); and (c) frames
  every number against the D3 certificate, computed in-job and training-free, so
  ADR r2-0003's conditional-mean reality becomes a measured per-dataset ceiling
  instead of an assumption.

- **Concrete config**: New from-scratch family `models_r2/r2s1_cond_decoder` —
  condition-only forward signature, no field input at any stage of test, no
  round-1 code vendored. Condition standardized on train statistics -> 16 random
  Fourier features -> 128-wide MLP -> 16x16 latent seed grid; 4 FiLM-modulated
  spectral blocks (hidden 64, `modes_cap` 16) with progressive Fourier upsampling
  to the native HF grid (WORK_CAP 256); the decoder output is L2-normalized to a
  unit **direction** field and multiplied by `exp(logamp)` from a separate
  128-wide MLP **amplitude head** trained on `log||y||`. Loss = relative L2 with
  a p25-median denominator floor (round-1 two-gate rule: lambda <= 1 always +
  low-norm tail gate), AdamW lr 1e-3 / wd 1e-5 / cosine / batch 16 / grad-clip
  1.0 / 200 epochs. **Two disjoint train-side folds** (10% model selection, 10%
  blend calibration) — no test-split quantity is ever consulted (the round-1 D3
  val_idx double-consumption caveat); when `N_train < 20` (ifc_poisson, N_hf = 5)
  the blend switches to leave-one-out and training to fixed-epoch, no early stop.
  Final prediction = `lambda * model + (1 - lambda) * b` with `b` in {zero,
  train_mean, nn_condition} and `lambda` on a 21-point grid, both chosen on the
  calibration fold. Emitted splits: `test_hf` (scored, blended arm) plus
  non-scored `ref_raw` (lambda = 1, same checkpoint — free), `ref_pod_lin`
  (rank-50 POD + ridge, the declared D2 linear-reconstruction control, predicted
  in advance to fail on the 4 discontinuous datasets per Lanthaler 2210.01074),
  `ref_zero` / `ref_train_mean` / `ref_nn_condition` (floor arms recomputed
  in-job and asserted equal to `state/anchors/floors.json` within 1e-9 — a seam
  check, NOT a re-certification of r2s4's floors), and `cert_*` (the D3
  certificate: aleatoric estimate from condition-pair differences with a
  distance-slope test and zero-distance extrapolation, a `no_support` verdict
  when the nearest pair distance exceeds 0.5 — `sharp__cahn_hilliard` will trip
  it at 2.822 — the implied maximum achievable skill per dataset, and the
  **LF-carrier cosine** between block-mean HF pair differences and train-LF pair
  differences). Guards run at contract tier (2 epochs). Extra split names
  deliberately avoid the `test*` prefix because
  `eval/score_panel.py::_extract_test_metric` errors on ambiguous test splits.

- **Recipe**:

```json
{
  "base_family": "none (new family built from scratch on the round2-substrate; no round-1 or factory model code vendored; condition-only forward signature)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s1_cond_decoder",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S1_ARM": "amp_dir_blend",
    "R2S1_REF_ARMS": "raw,pod_lin,zero,train_mean,nn_condition",
    "R2S1_HIDDEN": "64",
    "R2S1_BLOCKS": "4",
    "R2S1_MODES_CAP": "16",
    "R2S1_LATENT_GRID": "16",
    "R2S1_COND_EMBED": "128",
    "R2S1_COND_RFF": "16",
    "R2S1_DIR_NORM": "unit_l2",
    "R2S1_AMP_HEAD": "log_norm_mlp",
    "R2S1_AMP_HEAD_WIDTH": "128",
    "R2S1_AMP_LOSS_W": "1.0",
    "R2S1_LOSS": "rel_l2",
    "R2S1_LOSS_LAMBDA": "1.0",
    "R2S1_DENOM_FLOOR": "p25_median",
    "R2S1_BATCH": "16",
    "R2S1_LR": "1e-3",
    "R2S1_WD": "1e-5",
    "R2S1_GRAD_CLIP": "1.0",
    "R2S1_SCHED": "cosine",
    "R2S1_WORK_CAP": "256",
    "R2S1_FOLD_MODEL_FRAC": "0.10",
    "R2S1_FOLD_BLEND_FRAC": "0.10",
    "R2S1_FOLD_DISJOINT": "1",
    "R2S1_SMALL_N_PROTOCOL": "loo",
    "R2S1_SMALL_N_THRESHOLD": "20",
    "R2S1_BLEND_BASES": "zero,train_mean,nn_condition",
    "R2S1_BLEND_GRID": "0:1:21",
    "R2S1_BLEND_SELECT": "oof_val_relL2",
    "R2S1_POD_RANK": "50",
    "R2S1_CERT": "1",
    "R2S1_CERT_PAIRS": "1000",
    "R2S1_CERT_SLOPE_FIT": "linear_on_sq",
    "R2S1_CERT_MIN_SUPPORT_D": "0.5",
    "R2S1_CERT_LF_COSINE": "1",
    "R2S1_FLOOR_SEAM_TOL": "1e-9",
    "R2S1_LEAKAGE_TRIPWIRE": "1",
    "R2S1_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s1_direct/B1/eval",
    "_scored_arm": "amp_dir_blend",
    "_scored_split": "test_hf",
    "_ref_split_prefix": "ref_ (and cert_) — extra splits MUST NOT start with 'test'",
    "_guard_tier": "contract (2 epochs) on heat_local,fluid,sharp__sod_1d",
    "_note": "keys prefixed _ are card directives, NOT passed to --env"
  }
}
```

- **Expected outcome** (primary blended arm, seed 0, 200 epochs, skill units;
  every number `provisional-single-seed`):

| dataset | best floor (arm) | expected | certified ceiling (in-job cert leg) |
|---|---|---|---|
| `ext__helmholtz_2d` | 3.3441 (zero) | 1.3-2.5 **report-only**, zero-floor column shown | ~0 (deterministic map) |
| `sharp__phase_field_crystal_2d` | 59.812 (train_mean) | 44-55 (pfc denominator caveat: 0.007381 under variant C; no fidelity gap under band-limited) | ~41 |
| `sharp__allen_cahn_2d` | 269.196 (NN) | 150-200 | ~35 if deterministic, ~131 if stochastic — the card decides |
| `sharp__fisher_kpp_2d` | 11.993 (train_mean) | 11.0-11.8 | ~11 (essentially exhausted) |
| `sharp__cahn_hilliard` | 23.180 (NN) | 12-19 | `no_support` (min pair distance 2.822 in 19 dims) |
| `ifc_poisson` | 10.055 (NN) | 9-10, **anecdote-grade** (N_hf = 5) | not estimable |

  Panel geomean point estimate **~17.3** vs the launch anchor **23.0636**
  (-25%). Against the noise floor: the geomean leg demands >= 15% vs an implied
  geomean noise of ~12.4%, and every per-dataset leg exceeds its
  `min_claimable_effect` (see below) except `ext__helmholtz_2d`, which is
  report-only for exactly that reason.

- **Expected falsification**: H-r2s1-B1 ("a from-scratch condition->HF decoder
  that predicts the per-sample amplitude from the condition and is blended
  out-of-fold onto the best training-free floor extracts information the floors
  do not have, and its residual gap is bounded by a measurable identifiability
  floor") is FALSIFIED if, at 200 epochs / seed 0 on the stripped view, the
  primary `test_hf` arm's panel geomean skill is `> 19.60` (i.e. fails to beat
  the frozen best-floor anchor 23.0636 by 15%), **or** it fails to beat the best
  frozen floor by >= 25% on BOTH `sharp__cahn_hilliard` (needs `<= 17.39`) and
  `sharp__allen_cahn_2d` (needs `<= 201.90`) — the two datasets the in-job
  certificate says have real headroom — **or** it is worse than 1.15x the best
  frozen floor on any scored panel dataset (`sharp__phase_field_crystal_2d`
  `> 68.78`, `sharp__fisher_kpp_2d` `> 13.79`, `sharp__allen_cahn_2d` `> 309.58`,
  `sharp__cahn_hilliard` `> 26.66`, `ifc_poisson` `> 11.56`), which the
  out-of-fold blend is designed to make impossible and would therefore indict the
  calibration; `ext__helmholtz_2d` carries a report-only prediction (`<= 2.00`
  with the zero-floor column) and no falsification weight, and every number is
  labelled `provisional-single-seed`.

- **Prior-art verdict quoted** (verbatim from
  `websearches/r2s1_direct/batch_1/report.md`):
  - D1 row: "**preempted**" | citations "https://arxiv.org/html/2601.22654v1;
    https://arxiv.org/html/2511.09729v1; ModAFNO
    https://archive.docs.nvidia.com/physicsnemo/26.03/physicsnemo/api/models/fnos.html"
    | "Nothing mechanism-level. Admissible only as a *measurement/baseline arm*
    on this panel against the mandatory floor arms."
  - D2 row: "**preempted**" | "PODNO https://arxiv.org/html/2504.18513v1/
    (fetched); RB-DeepONet https://arxiv.org/abs/2511.18260 (fetched)" | "Only
    the number is unmeasured (fixed basis vs free decoder at N_hf=5). Declare as
    a baseline arm; it is POD-NN/PCA-Net prior art under a new name."
  - D3 row: "**preempted-but-MF-composition-open**" | "Conditional-mean barrier
    arXiv:2605.28076v3 https://arxiv.org/html/2605.28076 (fetched); REALM
    https://arxiv.org/html/2512.18595 (fetched, shows floors are not standard
    practice)" | "Open: (i) the barrier diagnostic has never been instantiated
    where the unobserved driver is a *stored coarse solve*, making the floor
    validatable rather than assumed; (ii) NN-in-condition / train-mean / zero as
    a standing certification panel is not done in the fetched benchmark
    literature."
  - Constraint carried onto the card (report item 6): "Lanthaler et al.
    (arXiv:2210.01074 ...) proves linear-reconstruction architectures —
    DeepONet, PCA-Net, and therefore any fixed-POD-basis D2 arm — are provably
    inefficient for *discontinuous* operators ... If D2 is run as a baseline,
    predict its failure mode in advance."
  - Card `prior_art.verdict` to record: **`preempted-pivoted`** (architecture
    preempted and declared as a baseline; the composition scored is D3's).

- **Immutables self-check**: **pass (11/11)** — positive evidence for all 8
  immutables plus the three round-2 extras is written out in
  [iteration_1.md](iteration_1.md) section "Immutables self-check". Quoted noise
  numbers (skill units, `state/noise_floor.json` `min_claimable_effect`):
  cahn_hilliard 1.1604 vs leg margin 5.79; allen_cahn 14.8152 vs 67.30; no-harm
  margins pfc 8.97 (vs 6.9839), fisher_kpp 1.80 (vs 1.2198), allen_cahn 40.38
  (vs 14.8152), cahn_hilliard 3.48 (vs 1.1604), ifc_poisson 1.51 (vs 0.2399).
  `ext__helmholtz_2d`'s entry (10.6811) exceeds its entire floor (3.3441), so
  that dataset is report-only and carries no falsification weight; the file is
  `_provisional: true` and program.md 4.3 directs direct judgement until
  r2s4-B1 certifies.

- **Anchor reference**: `null` (program.md 4.5 — all four round-2 streams are
  gap/lever/diag; the own-stream anchor 23.0636 is implicit).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| (none — `experiment_cards/r2s1_direct/` contains no prior card) | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| r2s1_direct-B1 | gap / identifiability-certified condition->HF decoder | From-scratch condition-only decoder that predicts per-sample amplitude and direction separately, blended out-of-fold onto the best training-free floor, with an in-job training-free identifiability certificate (aleatoric ceiling + LF-carrier cosine) framing every per-dataset number | filled |
