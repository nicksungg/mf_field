# Brainstormer Report — Stream `r2s3_lf_train_signal`, Batch 1

**Stream**: `r2s3_lf_train_signal` (lever)
**Batch**: 1
**Total iterations**: 1 (cap 5)
**Slot filled**: 1 / 1
**Reopen candidates resolved**: 0 (none exist — stream's first card)

## Slot

- **Category**: `lf_train_signal / multi-rung native-resolution supervision`
  (auxiliary MF loss, D2 x D3 composition)
- **Card type**: `model`

- **Motivation**: The websearcher's prior-art verdict scores the two live
  directions as follows (verbatim, `websearches/r2s3_lf_train_signal/batch_1/report.md`
  "## Prior-art verdict"):

  > **D2** — nested multi-resolution auxiliary target heads: shared
  > condition→latent trunk with extra heads regressing the l1/l2 coarse-solve
  > fields, heads discarded at test | **preempted-but-MF-composition-open** |
  > ... | The published composites put LF **inside the test-time prediction
  > path**; keeping the LF heads strictly out of that path, as a pure
  > representation regularizer on a **fully nested** ladder (identical
  > conditions, differing only by grid truncation), was not retrieved.

  > **D3** — LF-as-parameter-coverage on ifc_poisson: use the 100/50/20 LF
  > samples at conditions **disjoint** from the 5 HF conditions, with a matched
  > with/without-LF ablation | **novel** (nearest neighbors named) | ... Both
  > nearest neighbors are *resolution hierarchies of the same problem* aimed at
  > *cost*. Neither covers a coarse level at **different parameter values** than
  > the fine level. Also, iteration 3 term 3 found **no** matched
  > with/without-LF value-of-information ablation at N_hf ~ 5 for field
  > prediction anywhere — that measurement (round-2 success criterion 1) is
  > itself unclaimed.

  The card executes exactly the two open surfaces in one matched design,
  because the on-disk ladder asymmetry (verified by me in `summary_so_far.md`
  §6.2: the 5 sharp/helmholtz datasets carry **bit-identical** condition arrays
  across rungs, while ifc_poisson's four rungs are at **pairwise disjoint**
  conditions — exact overlap counts 0) forces a per-dataset answer to the
  stream's question, and one architecture with a matched no-LF control is the
  only way to get it. Program.md §12.3's demand — "LF-as-signal designs must
  state what information the LF rungs add that the HF rung does not already
  contain" — is answered concretely: **170 disjoint conditions on ifc_poisson;
  nothing but spectral truncation elsewhere.**

- **Concrete config**: new family `models_r2/r2s3_rung_supervised`.
  - **Model** `CondFieldDecoder(cond_dim, hidden=64, n_blocks=4,
    modes_cap=12)` with **`forward(cond, out_hw) -> (B,H,W)`** (new signature:
    the output grid is a forward argument, not bound at construction).
    Coordinate channels built at forward time; lift conv 2->64; 4 blocks of
    [SpectralConv2d with modes clipped to the requested grid's Nyquist + 1x1
    conv + FiLM(cond) affine after GroupNorm + GELU]; projection 1x1
    64->128->1. **FFTs use `norm="forward"`** (not `"ortho"`) so that the same
    mode weights act identically at every rung resolution — the enabling
    detail of the design.
  - **Training** — two stages, matching the declared baseline's structure:
    stage 1 = `--epochs` (200) on the arm's rung row set, AdamW lr 1e-3, wd
    1e-5, cosine, grad-clip 1.0, batch 16, minibatches grouped by rung (one
    forward per rung per step), MSE in scaled units; stage 2 = 200 epochs on
    HF rows only at lr 3e-4. ONE shared scaler `s = max|y|` over all stage-1
    rung fields. No early stopping, no validation-based selection, therefore no
    validation split is consumed (§12.1 train/val discipline; the round-1 D3
    `val_idx` double-consumption caveat cannot arise).
  - **Test path**: `S(cond, HF_work_grid)` only. No LF tensor is constructed at
    test; the LF signal has zero parameters, so it cannot leak into inference.
  - **Arms** (each its own `ROUND2_EVAL_RESULTS`, hence its own `ckpt_dir`):
    | arm | stage-1 rows | datasets | role |
    |---|---|---|---|
    | `hf_only` | HF rung only | panel | matched no-LF control (identical arch/budget/optimizer) |
    | `rung_native` | all rungs, each at its **native** grid | panel | **PRIMARY / scored** |
    | `rung_upsampled` | all rungs bilinearly upsampled to the HF working grid (the `_to_grid` convention of `mf_fno_transfer_film` and every round-1 ladder family) | `ifc_poisson, sharp__cahn_hilliard, sharp__phase_field_crystal_2d` | mechanism control |
  - **Declared baseline** (`mf_fno_transfer_film`, §12.3 mandatory): **cited**,
    with its seed-0/200-epoch panel restated under corrected denominators from
    `round1/eval/results/mf_fno_transfer_film/*_e200_s0.json` — helmholtz
    20.7413, pfc 69.7455, allen_cahn 148.1626, fisher_kpp 12.3501,
    cahn_hilliard 11.6650, ifc_poisson 1.5446, **panel geomean 19.0433** — plus
    a **validity gate**: re-run it on `ifc_poisson` only under the round-2 eval
    layer (0.78 min on p100) and require nRMSE 0.055604 +/- 10% relative.
    Gate, not a clause.
  - **Guard leg**: primary arm on `--datasets guard` at contract tier
    (2 epochs), per §2.3.
  - **Checkpointing**: `<ckpt_dir>/last.pt` every 10 epochs with
    `{stage, epoch, model, opt, sched, rng, epochs_target, arm, grid}`; exact
    resume; `done` marker keyed on `(epochs_target, arm, grid)`.
  - **Score-neutral instrumentation**: per-rung row/grid/`max|y|`/`mean|y|`
    table with exact condition-overlap counts against the HF rung; a
    resolution-consistency probe (rel-L2 between `S(cond, coarse)` and the ADR
    r2-0001 restriction of `S(cond, HF)`) before and after training; per-arm
    train-vs-test nRMSE gap (feeds r2s4's overfitting anatomy); per-rung
    stage-1 loss curves.

- **Recipe**:
```json
{
  "base_family": "none (new from-scratch family; NOT vendored from mf_fno_transfer_film or mf_fno_ladder* — see the differentiator table in iteration_1.md 'Alternatives weighed and rejected' D)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s3_rung_supervised",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S3_ARM": "rung_native",
    "R2S3_RUNGS": "all",
    "R2S3_SCALER": "shared_max_all_rungs",
    "R2S3_SPECTRAL_NORM": "forward",
    "R2S3_LAMBDA": "1.0",
    "R2S3_RESCONSIST_PROBE": "1",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. The --env set for the primary arm is exactly {R2S3_ARM=rung_native, R2S3_RUNGS=all, R2S3_SCALER=shared_max_all_rungs, R2S3_SPECTRAL_NORM=forward, R2S3_LAMBDA=1.0, R2S3_RESCONSIST_PROBE=1}.",
    "_primary_arm": "rung_native",
    "_arms": [
      {"tag": "hf_only", "R2S3_ARM": "hf_only", "R2S3_RUNGS": "hf", "datasets": "panel"},
      {"tag": "rung_native", "R2S3_ARM": "rung_native", "R2S3_RUNGS": "all", "datasets": "panel"},
      {"tag": "rung_upsampled", "R2S3_ARM": "rung_upsampled", "R2S3_RUNGS": "all", "datasets": "ifc_poisson,sharp__cahn_hilliard,sharp__phase_field_crystal_2d"}
    ],
    "_sweep": "ONE SLURM job per seed runs the three arms serially: for each arm, export ROUND2_EVAL_RESULTS=<OUT_DIR>/eval/results_<tag> (so out_json and ckpt_dir cannot collide across arms), then call score_panel.py --family_dir <worktree>/models_r2/r2s3_rung_supervised --datasets <arm datasets> --epochs 200 --seed $SEED --env R2S3_ARM=<...> --env R2S3_RUNGS=<...> --env R2S3_SCALER=shared_max_all_rungs --env R2S3_SPECTRAL_NORM=forward --env R2S3_LAMBDA=1.0 --env R2S3_RESCONSIST_PROBE=1 --out <OUT_DIR>/eval/result_<datasets>_<tag>_s${SEED}.json. score_panel caches per (family,dataset,epochs,seed,code_hash incl. env), so resubmission after preemption skips finished (arm,dataset) pairs — the script is idempotent.",
    "_declared_baseline": {
      "family": "mf_fno_transfer_film",
      "role": "program.md 12.3 mandatory declared baseline (LF-pretrain -> HF-finetune from the condition vector); cited, not re-trained on the panel, per the websearcher's instruction 6",
      "cited_numbers_source": "mffp_autoresearch/round1/eval/results/mf_fno_transfer_film/{ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson}_e200_s0.json, mean of rel_l2_per_sample (= the round-2 metric)",
      "cited_skills_corrected_refs": {"ext__helmholtz_2d": 20.7413, "sharp__phase_field_crystal_2d": 69.7455, "sharp__allen_cahn_2d": 148.1626, "sharp__fisher_kpp_2d": 12.3501, "sharp__cahn_hilliard": 11.6650, "ifc_poisson": 1.5446, "panel_geomean": 19.0433},
      "validity_gate": "re-run read-only via --family_dir <factory_root>/models/mf_fno_transfer_film --datasets ifc_poisson --epochs 200 --seed 0 (0.78 min on p100); must reproduce nRMSE 0.055604 within 10% relative. Validity gate, NOT a falsification clause; no factory file is edited."
    },
    "_guard_leg": "primary arm only: score_panel.py --datasets guard --epochs 2 --seed 0 (contract tier, program.md 2.3)",
    "_slurm": {"gres": "gpu:h100:1", "partition": "gpu", "time": "04:00:00", "budget_note": "~450 min on p100 / ~2.5 h on h100, extrapolated from round1/state/timing_ledger.json (mf_fno_transfer_film, 200 epochs, p100: helmholtz 7.73, pfc 12.35, allen_cahn 44.50, fisher_kpp 44.35, cahn_hilliard 44.35, ifc_poisson 0.78 min)"}
  }
}
```

- **Expected outcome**:
  | quantity | prediction | vs anchor / floor |
  |---|---|---|
  | `hf_only` ifc_poisson skill | ~11 (8-17) | at/above the train-mean floor 11.2063 — 5 samples cannot cover a 5-D condition space |
  | `rung_native` ifc_poisson skill | **~1.0 (0.5-3.0)** | bracketed by transfer_film 1.5446 and round-1 `self_only` 0.6087; beats NN 10.0549 / mean 11.2063 / zero 27.7778 floors by ~10x; possibly < 1 (round-2 criterion 2) |
  | **value-of-LF effect, ifc_poisson** | **~10 skill units** | noise-floor `min_claimable_effect` **0.23990756** -> **~42x the floor** |
  | 5 condition-aligned datasets | `rung_native` ~ `hf_only` within each dataset's `min_claimable_effect` (predicted null, nested-ladder degeneracy) | thresholds 10.6811 / 6.9839 / 14.8152 / 1.2198 / 1.1604 |
  | `rung_native` panel geomean | ~17-19 | anchor **23.0636**; declared baseline **19.0433** |
  | `hf_only` panel geomean | ~26-27 | worse than the anchor — that is the point of the control |
  The card is not expected to move the panel geomean much; its deliverable is
  the certified value-of-LF contrast (round-2 criterion 1's shape) plus a
  possible ifc_poisson skill < 1. Standing caveats carried: helmholtz stays
  report-only (best floor = zero field, 3.3441); pfc claims carry the
  band-limited-denominator caveat (`eval/copylf_baselines.json _notes.pfc`).

- **Expected falsification**: *F1 (primary)* — falsified if `rung_native` fails
  to beat `hf_only` on `ifc_poisson` by more than the certified floor
  **0.23990756** skill units, i.e. if 170 disjoint LF conditions add nothing a
  condition→HF operator can use.
  *F2 (mechanism)* — falsified if `rung_native` fails to beat `rung_upsampled`
  on `ifc_poisson` by more than the same 0.23990756 skill units (the
  native-resolution pathway is then not the differentiator and the round-1/zoo
  upsample convention was already optimal).
  *F3 (degeneracy prediction, pre-registered in both directions)* — the design
  predicts NO LF effect on the 5 condition-aligned datasets; falsified if
  `rung_native` beats `hf_only` on >= 2 of the 5 by more than each dataset's
  `min_claimable_effect` (helmholtz 10.68110662, pfc 6.98392165, allen_cahn
  14.81520561, fisher_kpp 1.21978271, cahn_hilliard 1.16035691), which would
  establish LF as a resolution curriculum independent of parameter coverage.
  Pre-registered 2x2 reading of (F1, F2) is recorded in
  [iteration_1.md](iteration_1.md).

- **Prior-art verdict quoted**: see **Motivation** above — the D2
  (`preempted-but-MF-composition-open`) and D3 (`novel`) rows quoted verbatim
  from `websearches/r2s3_lf_train_signal/batch_1/report.md`. Citations carried
  onto the card: https://arxiv.org/abs/1903.00104 (composite MFNN — LF net from
  the parameter input, LF train-only, no LF solve at inference: the D2
  preemption), https://dl.acm.org/doi/10.1016/j.jcp.2023.112462 (MF-DeepONet),
  https://arxiv.org/html/2604.20061v1 (coarse-graining = irreversible
  information loss — the honest bound on what the rungs can add),
  https://arxiv.org/abs/2505.12940 and https://arxiv.org/abs/2501.12739 (MLMC /
  multiscale training — the D3 nearest neighbours, cost-oriented, same
  parameters per level), https://arxiv.org/pdf/2304.06972 (published
  LF-pretrain->HF-finetune FNO = the declared baseline's external preemption).

- **Immutables self-check**: **pass (11/11)**, with positive evidence per item
  recorded in [iteration_1.md](iteration_1.md) ("Immutables self-check"). Two
  items worth surfacing here: (9) F1/F2's 0.23990756 threshold is the
  ifc_poisson `min_claimable_effect` from `state/noise_floor.json` and the
  predicted effect is ~42x it; (10) the nearest pre-falsified lever is **LF
  low-mode freezing** (`mf_fno_spectral`, r1 §5) — that lever substituted the
  LF field's low modes into the *test-time* prediction, whereas here nothing is
  frozen or substituted, no LF tensor exists at test, and the low-mode
  information enters only as a training loss at conditions the HF rung does not
  contain.

- **Anchor reference**: `null` (program.md §4.5 — round-2 lever stream; the
  own-stream anchor 23.0636 is implicit and quoted throughout).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — `experiment_cards/r2s3_lf_train_signal/` is empty; this is the stream's first card)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B1 | `lf_train_signal / multi-rung native-resolution supervision` | One condition→HF FiLM-FNO operator (`forward(cond, out_hw)`, forward-normalized FFTs) supervised at every rung's native resolution, with a matched no-LF control and an upsample control — predicting a large LF gain on ifc_poisson (disjoint conditions) and a null on the 5 condition-aligned datasets | filled (`model` card) |
