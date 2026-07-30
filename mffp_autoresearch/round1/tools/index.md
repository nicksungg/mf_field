# `tools/` — promoted round-1 probes

Reusable, parameterized diagnostics promoted out of experiment scratchpads.
Every tool: CLI args only (no hardcoded stream/batch paths), read-only w.r.t.
`models/`, `eval/`, `data/`, scored through `round1/eval/nrmse.py` when it
produces a metric.

**Append to this file — never rewrite entries you did not add.** One row per
tool: name, what it measures, invocation, provenance card.

| tool | what it measures | provenance card |
|---|---|---|
| `ladder_level_diagnostic.py` | a multi-fidelity dataset's ladder structure before a model is designed for it (level-to-level field shape, amplitude law, index alignment) | s1_poisson-B1 turn 1 |
| `field_error_decomposition.py` | splits a predictor's test error into per-sample AMPLITUDE vs STRUCTURE, plus the per-sample-gain oracle | s1_poisson-B1 turn 2 |
| `lf_conditioned_headroom.py` | how much of a dataset's copy-LF error is removable, training-free, by conditioning on the per-sample LF FIELD; classifies datasets A (residual-learnable) / B (residual-unlearnable) | s2_beyond_copy-B1 turn 2 |
| `lf_at_inference_audit.py` | whether a model family actually consumes the LF field at inference, or only during training | s2_beyond_copy-B1 turn 3 |
| `dc_pattern_split.py` | whether a prediction's score is a real field prediction or only the DC (spatial-mean) level; constant-field oracle + demeaned pattern error | s5_tuning-B1 turn 3 |
| `regen_preds_from_ckpt.py` | recovers a control arm's `preds_test.npz` from a checkpoint that shipped without one (eval-only resume), with a mandatory seam check | s5_tuning-B1 turn 1 |
| `defect_correction_learnability.py` | training-free: is `hf - interp(lf)` a fixed (mostly linear, compact-stencil) operator of the LF field on this dataset? predicts whether an LF-consuming additive corrector has headroom, and what a ZERO-parameter closed-form filter already gets | s6_local-B1 turn 3 |
| `residual_gain_learnability.py` | whether a predictor's leftover per-sample GAIN error is a learnable function of the condition vector (LOO ridge/kNN R^2 + the nRMSE a calibration head could reach) | s1_poisson-B2 turn 2 |
| `interface_locality_profile.py` | whether a predictor's error is INTERFACE-LOCAL or BULK: relative error binned by decile of \|grad HF\|, next to the target's energy per decile | s1_poisson-B2 turn 2 |
| `trust_gate_headroom.py` | value ceiling of a trust gate at per-pixel vs per-sample granularity, for any `base + correction` model scored against copy-LF | s6_local-B1 turn 1 |
| `correction_anatomy.py` | what a `base + alpha*correction` branch actually adds: a re-derivation of copy-LF, real fidelity-gap information, or nothing | s4_hybrid_routing-B1 turn 2 |
| `routing_headroom.py` | ceiling of a per-sample / per-pixel gate over one scalar `alpha`, for a base that is NOT copy-LF (complements `trust_gate_headroom.py`) | s4_hybrid_routing-B1 turn 3 |
| `registration_audit.py` | whether a dataset's copy-LF REFERENCE is misregistered (grid-convention mismatch between the solver's sampling and `copylf_prediction`'s `zoom(grid_mode=True)`), and what a zero-parameter fix buys; also flags degenerate ladders and projects a fitted LSI filter onto the half-cell phase ramp | s3_warp-B1 turns 1+3 |
| `render_readme.py` | regenerates `round1/README.md` from the experiment cards (housekeeping, not a probe) | round infrastructure |

---

## `lf_conditioned_headroom.py`

**Measures.** A ladder of training-free predictors on one or more panel datasets,
scored with `round1/eval/nrmse.py` against `round1/eval/panel_data.py`'s copy-LF:

`L0 copylf` · `L1 alpha*copylf` (one train-fitted scalar) · `L2 copylf + mean train
residual` · `L3 copylf + kNN-in-X residual` · `L4 field lookup keyed on LF` ·
**`L5 copylf + kNN-in-LF residual`** · `L6 low-passed L5` · `Lx knnX{k} field
lookup` · `O2` per-sample rescale oracle (labelled, uses HF).

**Read it as.** `L5 << 1` → **Class A**, the residual `hf−lf` is a function of the
LF field and an LF-input residual architecture has real headroom. `L5 ≈ 1` and
`L1 ≈ 1` → **Class B**, copy-LF is already near-optimal for what (X, LF) determine
at this `N_train`; target *matching* copy-LF, not beating it. `L3 >> L5` → the
lever is the query KEY (LF-conditioning), not the additive-residual form.
`leak_control_test_over_train_nn_dist ≈ 1` confirms the test set is not a
near-duplicate of train in signature space.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/lf_conditioned_headroom.py \
    --datasets sharp__phase_field_crystal_2d,ext__helmholtz_2d \
    --out /path/to/headroom.json [--sig 16] [--ks 1,5,10]
# whole panel from project.yaml:
python tools/lf_conditioned_headroom.py --datasets PANEL --out headroom.json
```
Pure numpy on the login node; ~1–3 min per 256×256 dataset. Datasets whose test
split ships no LF (e.g. `ifc_poisson`) are skipped with an `error` field.

**Verified.** Run 2026-07-29 on `sharp__phase_field_crystal_2d,ext__helmholtz_2d`
→ `L5_lf_plus_knnLF5_resid` 0.5620 / 0.7851, leak control 1.31 / 1.00 —
identical to the source probe (`s2_beyond_copy-B1` card part 6, F6/F9).

**Provenance.** `worktrees/s2_beyond_copy/B1/scratchpad/reanalysis_turn_2.py`;
card `experiment_cards/s2_beyond_copy/batch_1/B1.json` part 6, findings F6–F9.

---

## `lf_at_inference_audit.py`

**Measures.** For every family directory with a `smoke_eval.py`: each source line
that reads a TEST-split field, the fidelity key used, the declared `mf_mechanism`,
whether an LF surrogate is built from `X_te`, and whether training uses
`min(lf_fids)` or `max(lf_fids)` (copy-LF always uses `max`).

**Why it matters.** `skill = nRMSE(model) / nRMSE(copy-LF)` compares a model
against a baseline that receives the per-sample coarse solve. If the model does
not receive it at inference, the comparison is LF-blind-model vs LF-using-baseline
and any "fusion failure" it reports is an input gap, not a mechanism gap.
`reads_test_lf` is the load-bearing field; `surrogate_lf_at_test` and
`lf_fidelity_used_in_training` are import-graph heuristics — treat as leads.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/lf_at_inference_audit.py \
    --models_dir "$FACTORY_ROOT/models" --out /path/to/lf_audit.json \
    [--families a,b,c] [--verbose]
```
< 2 s, pure file reads.

**Verified.** Run 2026-07-29 over `mf_field/factory_mffp/models` →
**0 of 27 families read the test split's LF field at inference**, matching the
runtime forward-hook audit (M1) recorded in card part 5.

**Provenance.** `worktrees/s2_beyond_copy/B1/scratchpad/reanalysis_turn_3.py`;
card `experiment_cards/s2_beyond_copy/batch_1/B1.json` part 6, finding F14.

---

## `ladder_level_diagnostic.py`

**Measures.** Everything about a multi-fidelity dataset's *ladder* that a model
design should know before it is written:

| block | question answered |
|---|---|
| `amplitude_law` | per-level N / grid / `max\|Y\|` / `RMS\|Y\|`, consecutive RMS ratios, total spread, and the scalar a naive pooled trainer would use as a shared scaler |
| `index_alignment` | `max\|X^(s)[:n] − X^(t)[:n]\|` per pair; `0` ⟺ the fidelity sample lists are index-aligned and naive cross-level row construction is safe |
| `condition_coverage` | per-level condition box + scaled nearest-neighbour distance from the HF-train and TEST conditions to each level's cloud |
| `cross_level_consistency` | nearest-condition-matched, upsampled source vs target field: rel-L2 raw, rel-L2 after ONE optimal global gain, that gain, and Pearson r — does a level carry the HF *shape*? |
| `matched_level_predictor_on_test` | training-free skill floor: nearest-condition sample at level `f`, upsampled, × one gain calibrated on the HF **train** samples only; plus zero- and HF-train-mean-predictor baselines |

**Read it as.** `index_aligned: false` → any family that pairs
`cond_by_fid[s][:n]` with `field_by_fid[t][:n]` is training on mismatched
(parameters, field) rows. Large `max_over_min_rms` with clean consecutive
ratios → a discretization scale law, i.e. a **removable nuisance**: pooling
those levels under one target scaler makes the network learn the gain law along
the fidelity axis. High `cross_level_consistency.pearson_r_mean` with low
`rel_l2_after_optimal_gain` → the coarse levels *do* carry the HF shape, so a
null on "extra levels don't help" is a normalization result, not an information
result. `matched_level_predictor_on_test` is the honest floor any trained model
must clear.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/ladder_level_diagnostic.py --dataset ifc_poisson \
    [--split train] [--test_split test] [--paper_bar 0.036] [--out diag.json]
```
Read-only, pure numpy/torch-interpolate; seconds to ~2 min per dataset.

**Verified.** Run 2026-07-29 on two different on-disk layouts.
`ifc_poisson` (ifc_raw, 4 levels) → `index_aligned: false`, RMS spread
**75.69×**, consecutive ratios 4.379 / 4.196 / 4.120, cross-level Pearson r
0.941–0.989, matched-8²-level test nRMSE **0.24828**.
`sharp__allen_cahn_2d` (npz_l, 3 levels) → `index_aligned: true`, RMS spread
**1.00×**, cross-level r 0.980–0.998. The contrast is the point: the
shared-scaler trap below exists on the first dataset and not on the second.

**Provenance.** `worktrees/s1_poisson/B1/scratchpad/reanalysis_turn_1.py`;
card `experiment_cards/s1_poisson/batch_1/B1.json` part 6, turn-1 findings.

---

## `field_error_decomposition.py`

**Measures.** Whether an nRMSE gap is *amplitude* or *structure*, from any
saved `(pred, target)` pair:

| key | meaning |
|---|---|
| `frac_sq_error_from_gain` | share of squared error explained by a per-sample scalar gain error |
| `nRMSE_after_per_sample_gain` | the STRUCTURE-only error (each sample rescaled by its own oracle gain) |
| `nRMSE_after_global_gain` | one oracle scalar for the whole set — separates constant bias from per-sample spread |
| `var_ratio_pred_over_target` | across-sample variance retained; `≪ 1` = collapsed toward the mean field |
| `nRMSE_centered` | nRMSE of the mean-removed fields |
| `band_rel_err[]`, `target_energy_share[]` | radial-band relative error, and where the target's energy actually is |
| `pearson_r_mean/min` | per-sample shape agreement |

Pass several files to get a comparison block against the first label.

**Read it as.** `frac_sq_error_from_gain` high and
`nRMSE_after_per_sample_gain` ratio ≈ 1 between two models → they learned the
same function up to per-sample scale and the gap is **calibration**, not
architecture. Low `var_ratio_pred_over_target` → the model is regressing toward
the mean field, i.e. it lost the condition dependence. Compare `band_rel_err`
against `target_energy_share` before believing any high-frequency story.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/field_error_decomposition.py \
    --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
    [--pred_key pred --target_key target] [--grid 64 64] [--bands 6] [--out d.json]
```
Seconds. The npz must hold 2-D `(N, n_cells)` arrays — the layout families
write to `preds_test.npz`. If a family does not dump predictions, add a
score-neutral `np.savez` beside its checkpoint (pattern:
`worktrees/s1_poisson/B1/models_r1/mf_fno_ladder/smoke_eval.py:462`); it costs
nothing and it is the only way this probe can be run after the fact.

**Verified.** Run 2026-07-29 on `s1_poisson-B1`'s shipped predictions:
reproduced the card's `two_level` 0.102710 and `allpairs` 0.209275 exactly,
`nrmse_def_hash d3d0ade9…` matching the card's, and showed the **2.0375×**
nRMSE ratio shrinking to a **1.1306×** structure-only ratio.

**Provenance.** `worktrees/s1_poisson/B1/scratchpad/reanalysis_turn_2.py`;
card `experiment_cards/s1_poisson/batch_1/B1.json` part 6, turn-2 findings.

---

## `dc_pattern_split.py`

**Measures.** Whether a prediction is a *field* prediction or only a *level*
prediction, from any saved `(pred, target)` pair. Complementary to
`field_error_decomposition.py`: that tool centers by the across-sample **mean
field**; this one centers each sample by **its own spatial mean** and adds the
constant-field oracle.

| key | meaning |
|---|---|
| `nrmse_constant_field_oracle` | score of predicting each test sample's own spatial mean everywhere — the level-only ceiling |
| `hf_dc_energy_share` | fraction of HF energy in the DC term = how much of the metric is winnable with no pattern at all |
| `nrmse_pattern_only` (+ median) | rel-L2 of the demeaned prediction vs the demeaned truth; `≈ 1` = the pattern is worth exactly nothing |
| `corr_demeaned_mean/median` | per-sample Pearson r of the demeaned fields |
| `relerr_of_spatial_mean` | how well the level itself is predicted |
| `verdict` | `LEVEL_ONLY` / `WEAK_PATTERN` / `REAL_PATTERN` |

**Read it as.** `LEVEL_ONLY` → the model carries no field information; do not
attribute its skill to any spatial mechanism and do not expect capacity, bandwidth
or resolution knobs to move it (s5-B1: raising `modes_cap` on a `LEVEL_ONLY` model
only gave its noise pattern more spectral channels, and every sharp dataset got
worse). `nrmse_raw > nrmse_constant_field_oracle` → a per-sample scalar beats the
model; the honest baseline for that dataset is a level regressor.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/dc_pattern_split.py \
    --preds cap32=<a>/preds_test.npz cap12=<b>/preds_test.npz \
    [--dataset sharp__allen_cahn_2d --include-copylf] [--n-samples 24] [--out d.json]
```
Seconds (arms are paired on the first `min(N)` samples and the tool refuses
mismatched targets). `--include-copylf` loads the full test split — slow for 256²
datasets on a contended login node.

**Verified.** Run 2026-07-29 from `tools/` on `s5_tuning-B1`'s shipped cap-32
predictions and the regenerated cap-12 control: `ifc_poisson` → both arms
`REAL_PATTERN` (corr 0.9942 / 0.9937, nRMSE 0.04748 / 0.05563);
`sharp__allen_cahn_2d` → both arms **`LEVEL_ONLY`, flagged worse than the level
oracle** (constant-field oracle 0.25913 vs 0.26478 / 0.26354; corr 0.0108 / 0.0118;
DC energy share 0.9808) — identical to card part 6 finding F13.

**Provenance.** `worktrees/s5_tuning/B1/scratchpad/reanalysis_turn_3b.py`;
card `experiment_cards/s5_tuning/batch_1/B1.json` part 6, findings F8/F13.

---

## `regen_preds_from_ckpt.py`

**Measures.** Nothing by itself — it *recovers the input* every paired probe needs.
Points a family entrypoint that dumps `preds_test.npz` at a control's `last.pt`,
copied into a scratch dir (source artifacts are never written). Contract families
resume from a finished checkpoint, so `smoke_eval.py` skips training and runs the
eval path only. This is the after-the-fact answer to the note under
`field_error_decomposition.py` ("if a family does not dump predictions…"): the
control does not have to be rebuilt or retrained.

**Two seams it enforces.**
`--verify_json` compares the regenerated score against the control's official result
JSON on the **round's** metric — the per-sample mean (`rel_l2_per_sample` /
`rel_l2_mean`), never the family JSON's legacy ratio-of-sums `nRMSE` field (they
differ by 3× on `ext__helmholtz_2d`); `seam_ok` requires < 1e-3 relative.
`train_seconds` must be ~0 (`resume_clean`): if the `--env` knobs do not reproduce
the CONTROL's configuration, the checkpoint fails its shape check and the family
silently **retrains**, which this catches.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/regen_preds_from_ckpt.py \
    --family_dir <worktree>/models_r1/<family> \
    --dataset_dir "$FACTORY_ROOT/data/<ds>" --dataset_name <ds> \
    --ckpt "$OUTPUTS_ROOT/recert/.../ckpt_<ds>_e200_s0/last.pt" \
    --workdir <scratch>/control_infer --epochs 200 --seed 0 \
    [--env MFFP_MODES_CAP=12] [--verify_json <official>.json] [--timeout 1100]
```
No number from here may enter a card — the official JSON stays the source of truth;
the predictions are for structural decomposition only.

**Verified.** Run 2026-07-29 from `tools/` against the ADR-0005 H100 cap-12 retrain
on `ifc_poisson`: `resume_clean true` (`train_seconds` 7e-07), regenerated 0.0556275
vs official 0.0556311, `rel_delta` 6.5e-05, `seam_ok true`. Same path reproduced
five of six panel datasets to ≤ 6.5e-05; `sharp__fisher_kpp_2d` came in at 9.2e-03
(systematic, one-signed) — see card part 6 surprises.

**Cost warning.** On the login node (`nproc` 1, load ≈ 20 with concurrent agents) a
100-sample 256² FNO forward does **not** fit in a 20-minute cap; it fired twice on
`sharp__cahn_hilliard` / `sharp__fisher_kpp_2d`. Fall back to a paired sample-first
subset (pattern: `worktrees/s5_tuning/B1/scratchpad/regen_cap12_subset.py`) or a GPU.

**Provenance.** `worktrees/s5_tuning/B1/scratchpad/regen_cap12_preds.py`;
card `experiment_cards/s5_tuning/batch_1/B1.json` part 6, probe protocol.

---

## Standing warning `ladder_level_diagnostic` + `field_error_decomposition` encode

**Never pool fidelity levels under one target scaler without checking the
amplitude spread first.** On `ifc_poisson` the levels differ by a `~h²`
discretization law spanning 42–76×; a shared `max|Y_all|` normalizer turns that
law into a nuisance gain the network must learn along the fidelity axis, which
captures the amplitude degree of freedom that should have encoded the condition
dependence. Symptom triple: right shape (Pearson r ≈ 0.97), collapsed
conditional variance (≈ 0.44 of target), ~75 % of squared error removable by a
per-sample gain. Run `ladder_level_diagnostic.py` first; run
`field_error_decomposition.py` before blaming the architecture.

---

## Standing warning `dc_pattern_split` encodes

**Never interpret a panel skill number before checking whether the model predicts a
pattern at all.** On three of the five beyond-copy datasets the certified champion's
demeaned prediction is uncorrelated with the demeaned truth (|r| ≤ 0.012) and its
pattern-only error equals that of predicting zero pattern — it scores 0.26–0.52 only
because 63–98 % of those fields' energy is in the DC term. Symptom triple:
`corr_demeaned_mean` < 0.1, `nrmse_pattern_only` ≈ 1, `nrmse_raw` at or above
`nrmse_constant_field_oracle`. On such a model, capacity/bandwidth/resolution knobs
are not neutral — they are mildly **negative**, because the added degrees of freedom
are filled with uncorrelated energy (s5-B1: cap 32 injected 1.7–18.9× more top-band
energy than cap 12 on all four sharp datasets, and all four scores got worse).

---

## `defect_correction_learnability.py`

**Measures.** Training-free, model-free: fits ONE ridge-regularised per-frequency
transfer function `T(k)` from the interpolated LF field to the residual
`R = HF - interp(LF)` on the HF-train split (20 % held out), then reports

| key | meaning |
|---|---|
| `skill_LSI` / `nrmse_LSI_defect_correction` | score of `LF + T*LF` on the TEST split through `eval/nrmse.py` — a **zero-trained-parameter baseline any learned corrector must beat** |
| `rho_val_heldout` (load-bearing) / `rho_fit_in_sample` / `generalization_gap_rho` | is the defect a *stable* functional of LF, or only memorised? |
| `heldout_trust_switch_alpha` | the s6 stage-3 protocol (line search including 0, MIN_GAIN 1e-3) on the closed-form arm; `0` = "a no-harm gate should switch the corrector off here" |
| `stencil.frac_energy_within_12_cells`, `radius_50pct_energy` | compactness of the fitted operator's impulse response — is defect correction LOCAL? |
| `band_mean_abs_T` | the defect's amplitude law by radial band (round band convention) |
| `predicted_verdict` | STRONG (`rho_val > 0.9`) / MODERATE / WEAK / NO headroom |

**Read it as.** `rho_val > 0.9` -> a nested-ladder defect corrector will win big and
most of the win is a **linear filter**: check `skill_LSI` before attributing anything
to an architecture. `rho_fit` high with `rho_val <= 0` -> the coarse solve is not in
its asymptotic regime (sample-dependent phase/dispersion error); a held-out trust
switch is mandatory and a corrector will shut itself off (this is exactly what
happened on `ext__helmholtz_2d`). Low `frac_energy_within_12_cells` -> the optimal
operator is not local and a small convolutional receptive field is mis-sized.
Datasets whose test split ships no LF (`ifc_poisson`) return an `error` field.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/defect_correction_learnability.py --datasets PANEL --out defect.json
python tools/defect_correction_learnability.py --datasets GUARD --out guard.json
python tools/defect_correction_learnability.py \
    --datasets sharp__cahn_hilliard --out d.json [--ridge 1e-6] [--n_train 320] [--n_test 100]
```
Pure numpy + FFT on the login node; seconds to ~2 min per dataset. Leave `--n_test`
at its default (whole split) if you want `identity_matches_frozen_baseline` to be
exact — truncating the test split will not match `eval/copylf_baselines.json`
(`heat_local` has 512 test samples, `fluid` 256).

**Verified.** Run 2026-07-29 from `round1/` on
`sharp__phase_field_crystal_2d,ext__helmholtz_2d`: pfc `skill_LSI` **0.013883**,
`rho_val` 0.999777, switch 1.0, 94.0 % of stencil energy within 12 cells;
helmholtz `skill_LSI` 7.095513, `rho_val` **-43.8785**, switch **0.0** — identical
to the source probe, and `identity_matches_frozen_baseline` true on both.
Held-out `rho` across the five LF-bearing panel datasets ranks the s6 card's
observed `contribution_d` with **Spearman 1.000**.

**Provenance.** `worktrees/s6_local/B1/scratchpad/reanalysis_turn_3.py`;
card `experiment_cards/s6_local/batch_1/B1.json` part 6, findings F6-F9, F14-F16.

---

## `trust_gate_headroom.py`

**Measures.** For any model whose prediction can be written `copy-LF + correction`,
the **value ceiling of a trust gate at three granularities**: ungated (`g == 1`),
best-possible shared per-pixel map (oracle, fitted on test), best-possible
per-sample scalar (oracle), and — if you can supply the model's corrections on a
held-out TRAIN slice via `--val_pred/--val_idx_npz` — the ACHIEVABLE per-pixel gate.
Plus `pixel_gate_ceiling_frac`, `per_sample_gate_ceiling_frac`,
`corr_absC_gradbase` (is the correction interface-concentrated?) and a
`granularity_verdict`.

**Read it as.** Both ceilings < ~5 % -> a trust gate cannot pay for itself, and a
gate that sits at 1 (or at 0) is reporting the truth rather than failing to train.
Per-sample ceiling >> pixel ceiling -> build a per-SAMPLE trust head, not a
field-valued gate. A *negative* oracle pixel ceiling means one shared pixel map
cannot describe the dataset's sample-to-sample spread at all
(`sharp__cahn_hilliard`: +17 % worse).

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/trust_gate_headroom.py --dataset sharp__phase_field_crystal_2d \
    --pred_npz <run>/preds_test.npz [--pred_key pred | --corr_key corr] \
    [--val_pred <run>/val_corr.npz --val_idx_npz <run>/val_idx.npz] \
    [--n_samples 100] --out gate_headroom.json
```
Seconds; pure numpy. Needs a 2-D `(N, n_cells)` array on the dataset's TEST split.

**Verified.** Run 2026-07-29 from `round1/` on the s6-B1 pfc correction
(`alpha*Delta`, regenerated from the shipped checkpoint): ungated 0.00135270 and
oracle per-sample 0.00104408 reproduce the source probe exactly; oracle per-pixel
0.00128311 vs the probe's 0.00128989 (0.5 %, the cached correction is stored
float32). `pixel_gate_ceiling_frac` 0.0514 vs `per_sample_gate_ceiling_frac`
0.2281 -> verdict "PER-SAMPLE trust only", `base_matches_frozen_baseline` true.

**Provenance.** `worktrees/s6_local/B1/scratchpad/reanalysis_turn_1.py`;
card `experiment_cards/s6_local/batch_1/B1.json` part 6, findings F1-F3.

---

## Standing warning these two tools encode

**On a nested factor-2 ladder, report `skill_LSI` before claiming that an
architecture caused a copy-LF win.** On `sharp__phase_field_crystal_2d`,
`sharp__allen_cahn_2d` and `sharp__cahn_hilliard` a single least-squares transfer
function with no trained parameters beats the round's best 200-epoch model by
2.19x / 1.56x / 1.07x; only `sharp__fisher_kpp_2d` (a local nonlinearity) is won by
the network. And **do not build a field-valued trust gate without measuring its
ceiling first**: on these datasets an oracle per-pixel gate is worth <= 4.1 % and is
negative on one dataset, while an oracle per-sample scalar is worth up to 50.7 %.

---

## `correction_anatomy.py`

**Measures.** For any model written `pred = base + alpha*correction` (residual
hybrid, test-time corrector, boosting stage, two-expert mixture), WHICH of three
things the correction is:

| block | question answered |
|---|---|
| `cosine_correction_vs` | per-sample cosine of the correction with `hf-base` (its trained target), `copylf-base` ("re-derive the coarse solve"), `hf-copylf` (the fidelity gap) |
| `correction_in_span_lfdir_gapdir` | per-sample least squares of the correction on span{`copylf-base`, `hf-copylf`}: coefficient on each direction, `R^2` of the 2-D fit, and `effective_fraction_toward_copylf` = `alpha * c0` |
| `nrmse_base_plus_a_times_lfdir` | the TRIVIAL reference the correction must beat: `base + a*(copylf-base)` for `a` in 0.25/0.5/0.75/1 (`a=1` IS copy-LF) |
| `nrmse_all` / `skill_all` | copy-LF, base, gated hybrid, plus `L5` (kNN-in-LF residual) and `L3` (kNN-in-X residual) computed with `lf_conditioned_headroom.py`'s own functions, so the rungs are comparable to `s2_beyond_copy-B1` |
| `mean_rel_l2_<regime>` | the same predictors split into spatially-CONSTANT vs PATTERNED test samples (s2-B1 F1's bimodality; degenerate on unimodal datasets) |

**Read it as.** `cosine(corr, copylf-base) >= cosine(corr, hf-base)` together with
`cosine(corr, hf-copylf) ~ 0` -> the branch is **re-deriving the coarse solve it
already receives**. Its ceiling is skill 1.0, so tuning it cannot clear the
copy-LF bar, and `nrmse_base_plus_a_times_lfdir` will often show a one-scalar
blend already matching it — the lever is to feed the LF field to the network more
directly, not to grow the corrector. A materially non-zero
`coef_hf_minus_copylf_median` is the case worth scaling: that component carries
information copy-LF does not have. Both cosines ~0 with a tiny
`corr_rms_over_residual_rms` -> the branch collapsed and any gate value it reports
is uninformative.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/correction_anatomy.py --dataset sharp__phase_field_crystal_2d \
    --npz <run>/fields.npz --base_key base_te --corr_key corr_te \
    --corr_scale 2.8695719242095947 --alpha 0.25085851550102234 \
    --out anatomy.json [--sig 16] [--k 5]
```
Seconds; pure numpy. `--npz` holds two `(N, n_cells_hf)` arrays on the HF grid
(base prediction, RAW correction); `--corr_scale` un-scales families that store
the correction in scaler units (`fno_transolver_seq`'s `scaler_r`); `--alpha` is
the gate actually applied. Fewer rows than the test split is fine — the first N
test samples are used. Datasets whose test split ships no LF (`ifc_poisson`) raise.

**Verified.** Run 2026-07-29 from `round1/` on the s4-B1 pfc checkpoint replay
(`cache_sharp__phase_field_crystal_2d_s0.npz`, `corr_scale` 2.8695719242095947,
`alpha` 0.25085851550102234): `cosine(copylf-base)` 0.8342 / 0.9512,
`cosine(hf-copylf)` 0.0232 / 0.0381, span coefficients 3.1576 / 0.0749,
`R^2` median 0.9060, `effective_fraction_toward_copylf` 0.7921, blend curve
0.319056 / 0.215512 / 0.114384 / 0.040545 — identical to the source probe;
hybrid skill 3.1049959 vs the probe's 3.1049908 (1.6e-6, float32 cache).

**Provenance.** `worktrees/s4_hybrid_routing/B1/scratchpad/correction_anatomy.py`;
card `experiment_cards/s4_hybrid_routing/batch_1/B1.json` part 6, findings F6-F9.

---

## `routing_headroom.py`

**Measures.** The value ceiling of replacing the scalar `alpha` in
`pred = base + alpha*correction` with something richer, for an **arbitrary base**:

| rung | gate |
|---|---|
| `G0_alpha0` | `alpha = 0` (base only) |
| `G1_alpha_applied` | the scalar the model actually applied |
| `G2_alpha_global_oracle` | the global ORACLE scalar (fitted on this test set) |
| `G3_alpha_per_sample_oracle` | per-sample ORACLE scalars — the sample-level routing ceiling |
| `G4_alpha_field_splithalf` | per-PIXEL alpha field fitted on one half of the test split and scored on the other, both directions — a leak-free spatial-routing estimate that needs no extra val predictions |
| `G5_alpha_field_insample` | the same pixel field fitted in-sample — the spatial-routing upper bound |

plus `gains_pct_vs_G2`, `per_sample_alpha_oracle_stats` (incl. `cv`) and
`alpha_field_stats`.

**Relationship to `trust_gate_headroom.py`** (s6_local-B1): that tool answers the
same granularity question but requires the base to BE copy-LF (`pred = copylf +
correction`). Use this one when the base is a trained model (e.g. an FNO) and
when you also want the scalar rungs `G1` vs `G2` — the gap between the gate a
family fitted and the best single scalar — which is where a mis-specified gate
objective shows up.

**Read it as.** Compare `gains_pct_vs_G2` with the dataset's
`min_claimable_effect` (`state/noise_floor.json`; 10 % relative on the round-1
sharp panel). All rungs inside the floor -> a routing/gating card is NOT licensed:
one scalar is all the gate structure the artifact supports and the lever is what
the correction CONTAINS, not how it is mixed in. `G4` worse than `G2` (positive
gain) -> a pixel-wise gate cannot even be estimated at this `N_test`, so treat
`G5` as fantasy. A large `G1 - G2` is a gate-calibration defect, not a routing
opportunity.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/routing_headroom.py --dataset sharp__cahn_hilliard \
    --npz <run>/fields.npz --base_key base_te --corr_key corr_te \
    --corr_scale 2.207066297531128 --alpha 0.0 --out routing.json
```
Seconds; pure numpy.

**Verified.** Run 2026-07-29 from `round1/` on the s4-B1 cahn_hilliard checkpoint
replay: `G2` 0.2846013948347478, `G3` −5.3347 %, `G4` **+3.5446 %**, `G5`
−0.9463 %, per-sample oracle-alpha `cv` 0.6278 — identical to the source probe.

**Provenance.** `worktrees/s4_hybrid_routing/B1/scratchpad/routing_headroom.py`;
card `experiment_cards/s4_hybrid_routing/batch_1/B1.json` part 6, finding F11.

---

## Standing warning `correction_anatomy` + `routing_headroom` encode

**Before building a router, price the router; before scaling a corrector, ask what
the corrector contains.** On `fno_transolver_seq` (s4-B1) an ORACLE per-sample
gate is worth ≤ 5.3 % and an honestly-fitted per-pixel gate is *worse* than one
global scalar on 2 of 3 datasets — under every sharp dataset's 10 % floor — while
the correction it was gating is collinear with `copylf − base` (cosine 0.54–0.83)
and orthogonal to `hf − copylf` (cosine ≤ 0.02), i.e. the whole branch was
re-deriving the coarse solve the model already receives. **And check that any
held-out split used to fit a gate is out-of-sample for the BASE, not only for the
new component**: the s4-B1 base scored 0.0083 in-sample vs 0.5007 on test
(58× memorisation) on `sharp__cahn_hilliard`, which forced the gate to veto a
correction worth 43 % of the test error and 4.3× the dataset's noise floor.

---

## `residual_gain_learnability.py`

**Measures.** The follow-up `field_error_decomposition.py` cannot answer: *is the
leftover per-sample gain error a function of something the model already has at
inference?*

| key | meaning |
|---|---|
| `frac_sq_error_from_gain` | share of squared error that is a per-sample scalar gain (same definition as `field_error_decomposition.py`) |
| `nRMSE_oracle_gain` | nRMSE with every sample rescaled by its own ORACLE gain — the floor a perfect calibration head reaches |
| `loo.<model>.r2` | leave-one-out R² of the gain predicted from the condition vector (`ridge_linear`, `knn{1,3,5,10}`) |
| `loo.<model>.nRMSE_after_gain` | nRMSE if that LOO-predicted gain were applied |
| `best_learnable_nRMSE` / `_skill` | the best LOO row — the attainability estimate |
| `n_hf_train`, `cond_dim` | the fit-feasibility check (see below) |

**Read it as.** High `frac_sq_error_from_gain` **and** high `loo.ridge_linear.r2`
→ a condition-conditioned calibration head is a real, cheap lever, and
`best_learnable_nRMSE` sizes it. High `frac_sq_error_from_gain` with LOO R² ≤ 0
→ the amplitude error is sample-specific and no head keyed on `X` can remove it;
look at the field instead. **Two honesty rules travel with every number**:
(1) the LOO fit uses the TEST targets, so `nRMSE_after_gain` is an UPPER BOUND on
a head, never an achieved score; (2) compare `n_hf_train` with `cond_dim + 1` —
with 5 HF training samples a 6-parameter linear gain model is already saturated,
so the honest design estimates the law on the lower-fidelity levels and transfers
it.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/residual_gain_learnability.py \
    --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
    --dataset ifc_poisson [--paper_bar 0.036] [--ridge 1e-3] [--out gain.json]
```
Seconds; pure numpy. Conditions come from `round1/eval/panel_data.py` (test
split, HF fidelity) and must match the prediction file's sample count.

**Verified.** Run 2026-07-29 from `round1/` on `s1_poisson-B2`'s shipped
predictions: `ap_per` nRMSE 0.03425 (the card's scored value),
`frac_sq_error_from_gain` 0.5710, oracle 0.02292, LOO `ridge_linear` R² **0.9190**
→ 0.02431 / skill 0.6753, `n_hf_train` 5; `tl_per` 0.07855 → 0.06125.

**Provenance.** `worktrees/s1_poisson/B2/scratchpad/reanalysis_turn_2.py`;
card `experiment_cards/s1_poisson/batch_2/B2.json` part 6, turn-2 findings.

---

## `interface_locality_profile.py`

**Measures.** The SPATIAL complement to `field_error_decomposition.py`'s spectral
bands: relative error binned by decile of `|grad(HF target)|` (decile 0 =
smoothest), pooled over the whole test split so every arm shares identical bins.

| key | meaning |
|---|---|
| `error_by_grad_decile[10]` | `sqrt(sum e² / sum y²)` inside each gradient decile |
| `target_energy_by_decile[10]` | where the target's energy actually is, so a big relative error on 2 % of the energy is not mistaken for the dominant term |
| `locality_ratio`, `verdict` | decile 9 / decile 0. `> 1.25` INTERFACE-LOCAL, `< 0.8` BULK-DOMINATED, else SPATIALLY FLAT |
| `monotone_increasing` / `_decreasing` | is the profile ordered at all |
| `frac_sq_error_in_top_decile` | share of squared error in the steepest 10 % of cells |
| `ratio_vs_<first label>` | per-decile error ratio between arms — where a contrast's gain lives spatially |

**Read it as.** Round 1's sharp-interface intuition (rel-L2 hides blur in thin
regions) is an empirical claim, and this tool tests it in one pass. A
BULK-DOMINATED verdict means interface-aware losses and local branches are aimed
at the wrong pixels for that dataset.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/interface_locality_profile.py \
    --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
    [--grid 64 64] [--deciles 10] [--out loc.json] [--plot loc.png]
```
Seconds; pure numpy (+ matplotlib only with `--plot`). All files must share the
same target array — the tool refuses otherwise.

**Verified.** Run 2026-07-29 from `round1/` on `s1_poisson-B2`: all three arms
**BULK-DOMINATED**, `locality_ratio` 0.4075 (`ap_per`) / 0.2810 (`tl_per`) /
0.3168 (`ap_shr`), `monotone_decreasing` true for the two `per_level` arms, with
53.05 % of the target energy in the steepest decile.

**Provenance.** `worktrees/s1_poisson/B2/scratchpad/reanalysis_turn_2.py`;
card `experiment_cards/s1_poisson/batch_2/B2.json` part 6, turn-2 findings.

---

## Standing warning these two tools encode

**"X % of the error is amplitude" is not yet a lever, and "the error is at the
interfaces" is usually an assumption.** On `s1_poisson-B2` the amplitude share
(57.1 %) only became actionable once the gain was shown to be 0.919-R² linear in
the condition vector — and the same card's error profile falls MONOTONICALLY from
the smoothest to the steepest gradient decile, so the dataset's error is in the
bulk. Before proposing a calibration head, check `n_hf_train` vs `cond_dim + 1`:
the gain law may be unfittable from the HF split and have to be estimated on the
lower-fidelity levels.

---

## `registration_audit.py`

**Measures.** Whether the round's skill DENOMINATOR on a dataset is misregistered,
and what a zero-parameter fix is worth. `eval/panel_data.py::copylf_prediction`
upsamples with `zoom(..., grid_mode=True)` — the CELL-CENTRED convention — while a
pseudo-spectral solver's state is a POINT sample on the node grid `x_j = j*L/n`,
where LF node `j` coincides physically with HF node `r*j`. Reading one as the other
misregisters copy-LF by **`(r-1)/2` HF cells** (0.5 at r=2, 1.5 at r=4).

| block | question answered |
|---|---|
| `convention.ramp_probe` | the EXACT coordinate map of the real `copylf_prediction`, from pushing a linear index ramp through it (bilinear interpolation of a linear function is exact, so the output IS the sampled coordinate). Contains no physics and no fitting |
| `convention.decimation` | the data's own answer: is the raw LF closer to `HF[::r,::r]` (NODE) or to the r×r block mean (CELL-CENTRE)? |
| `convention.halfdomain_shift_axis0_cells` | is the misregistration CONSTANT or a zero-mean space-varying STRETCH (which no DC statistic can see)? |
| `variants[*]` | the free win: `A` eval copy-LF (seam-checked against `eval/copylf_baselines.json`, hard stop) · `A2` same convention with `grid-wrap` (isolates the wrap seam) · `B` A + a fixed `(r-1)/2`-cell shift · `C` node-aligned bilinear from the raw LF · `D` node-aligned band-limited · `E` Dirichlet interior-node alignment — each with nRMSE, skill, and its closed-form Lucas–Kanade residual shift |
| `hf_energy_above_lf_band` | does HF carry ANY information the LF grid cannot represent? |
| `lsi_ramp_projection` (`--lsi`) | how much of a fitted LSI transfer function (s6-B1's, imported from `defect_correction_learnability.py`) is just the phase ramp |
| `verdict` | `MISREGISTERED_NODE_DATA` (+ `DEGENERATE` flag) / `NON_NESTED_STRETCH` / `NON_NESTED_BUT_CONSISTENT` / `CONSISTENT` / `INCONCLUSIVE` |

**Read it as.** `MISREGISTERED_NODE_DATA` with variant-A `LK ≈ +(r-1)/2` → that
dataset's copy-LF reference is inflated; report skills against variant C/D as well,
and give any model that "beats copy-LF" the fixed-shift arm as its control.
`decimation.node ≤ 1e-6` → the **ladder is degenerate** (coarse solve = fine solve;
a dataset bug report, not a modelling target). `hf_energy_above_lf_band ≈ 0` → the
gap is never "missing fine structure", so bandwidth/capacity knobs cannot address
it. `lsi_ramp_projection.frac_explained > 0.8` with `best_scalar_c ≈ 1` → whatever a
learned linear/convolutional corrector wins there, it is mostly undoing the
resample. `NON_NESTED_STRETCH` → only variant `E` addresses it, and every mean-shift
statistic is blind to it.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/registration_audit.py --datasets PANEL --out reg.json [--lsi]
python tools/registration_audit.py --datasets GUARD --out guard.json
python tools/registration_audit.py --datasets sharp__cahn_hilliard --out d.json \
    [--n_test 100] [--n_train 400] [--seam_tol 1e-9]
```
Pure numpy/scipy on the login node, ~10–40 s per 256² dataset (+~30 s with `--lsi`).
It **refuses to report** if variant A does not reproduce the frozen copy-LF baseline.
Nothing it prints may become a card score — the eval layer stays byte-immutable
during a round and `eval/copylf_baselines.json` remains the reference; the corrected
variants are for interpretation and for control arms. 1-D layouts and LF-less test
splits (`ifc_poisson`) return an `error` field.

**Verified.** Run 2026-07-30 from `round1/` over `PANEL` + `GUARD`:
`MISREGISTERED_NODE_DATA` on all four sharp panel datasets with variant-A LK
`+0.464…+0.502` cells and variant `C` skill **0.1103 / 0.1648 / 0.3425 / 0.4769**
(allen_cahn / pfc / fisher_kpp / cahn_hilliard); pfc additionally flagged
**DEGENERATE** (variant `D` skill 7.1e-06, node decimation 3.02e-07);
`NON_NESTED_STRETCH` on `ext__helmholtz_2d` (half-domain LK difference +1.861 cells,
global ≈ 0, variant `E` skill 0.9077); `NON_NESTED_BUT_CONSISTENT` on `heat_local`
and `INCONCLUSIVE` on `fluid` (their fixes make things worse — the defect is NOT
universal). `--lsi` reproduces s3_warp-B1's F14 (0.9845 / 0.9510 / 0.0002 with
`c` 0.9975 / 1.0025 / 0.2782). Every variant-A nRMSE matched
`eval/copylf_baselines.json` to `0.0` absolute.

**Provenance.** `worktrees/s3_warp/B1/scratchpad/reanalysis_turn_1.py` +
`reanalysis_turn_3.py`; card `experiment_cards/s3_warp/batch_1/B1.json` part 6,
findings F1–F8, F14, F16.

---

## Standing warning `registration_audit` encodes

**Before attributing any sharp-panel skill number to a mechanism, check the
registration of the reference.** On the four round-1 sharp datasets
`copylf_prediction` places the upsampled LF half an HF cell off the HF grid, which
is 50–100 % of copy-LF's entire error: a zero-parameter fixed resample scores skill
0.110–0.477 there (7.1e-06 on `sharp__phase_field_crystal_2d`, whose ladder has no
fidelity gap at all), success criterion 2 is reachable without a model, and two
independent "mechanism" results — s3_warp-B1's 77–85 % oracle-warp ceilings and
s6_local-B1's zero-parameter LSI filter beating a 72k ConvNeXt — turned out to be
the same artefact measured in two languages (87–98 % of that filter's energy is the
half-cell phase ramp at unit amplitude). Symptom triple: a fitted displacement whose
DC is `≈ (r-1)/2` cells in BOTH axes, `decimation.node ≪ decimation.cellmean`, and a
learned corrector whose transfer function grows linearly in |k| with phase ≈ π/2.
The defect is not universal (`heat_local`, `fluid` are clean), so audit per dataset.
