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
