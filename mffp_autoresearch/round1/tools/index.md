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
| `stage_keep_test_audit.py` | whether a multi-STAGE family's own keep/discard test is honest: base optimism (in-sample vs OOF vs test), the gain the keep test claimed vs what the test split delivered, and the panel geomean with the stage rolled back | s4_hybrid_routing-B2 turn 1 |
| `band_phase_anatomy.py` | splits a corrector's per-band failure into AMPLITUDE vs PHASE (per-band cosine with the copy-LF error, optimal band gain, oracle-gain residual), optionally against the two zero-parameter reference directions | s4_hybrid_routing-B2 turns 2-3 |
| `relative_loss_geometry.py` | whether a per-sample-normalized training objective `(1-cos²)+λ(g-cos)²` is safe on this dataset: the low-amplitude trap, the fraction of samples the objective actively DE-ALIGNS at each λ, and the sample-weight concentration a relative loss silently imposes | s7_loss-B1 turn 1 |
| `collapse_set_attribution.py` | did MY change break these samples or were they already broken? paired per-sample collapse overlap between two arms, rank-AUC of every candidate separator (norm / sharpness / copy-LF / each condition coordinate), subpopulation nRMSE, and the zero-predictor skill | s7_loss-B1 turns 2+3 |
| `registration_skill_split.py` | how much of a predictor's beyond-copy win is the `(r-1)/2`-cell REGISTRATION artifact: its skill re-expressed against every zero-parameter node-aligned denominator, per-sample beat rates, and the no-harm-gate oracle / damage share | s2_beyond_copy-B2 turns 1+3 |
| `target_scale_spread_audit.py` | pre-flight, no model needed: will a GLOBALLY normalized residual target (`(HF-LF)/max\|HF-LF\|` + MSE) degenerate on this dataset? per-sample residual spread, energy share of the worst sample, effective N of the MSE, and how close a typical normalized target is to zero | s2_beyond_copy-B2 turn 3 |
| `target_range_placement_audit.py` | pre-flight, no model needed: is the OUTPUT-TARGET SCALER a lever here? the fluctuation magnification `G = max\|Y\|/sd` and its tail x pedestal decomposition per stage, the effective N under both normalizations (proof a global scalar cannot de-concentrate the loss), and the LF/HF stage-placement seam | s5_tuning-B2 turns 1-3 |
| `paired_arm_displacement.py` | did my change move the learned FUNCTION, and toward the truth? paired displacement between two arms' `preds_test.npz`, its cosine with the control's error (vs the random-direction baseline), the DC/pattern split of the move, and the amplitude share of the score gain | s5_tuning-B2 turns 2-3 |
| `ladder_pair_row_audit.py` | does a multi-fidelity PAIR/ladder row set add data or only REPLICATE it? distinct `(X, Y)` rows vs total, the per-level replication factor and effective loss weight it imposes, steps/epoch, and the source-indexed mismatched-pair defect | s1_poisson-B3 turn 1 |
| `gain_calibration_ceiling.py` | the three ceilings any per-sample multiplicative calibration head can aim at on a given prediction (one global gain / X-linear law / per-sample oracle), all test-fitted and labelled, in noise-floor units | s1_poisson-B3 turn 2 |
| `norm_tail_hedge_audit.py` | is an arm's score bought by ABSTAINING on the samples it cannot fit, and would a per-sample-normalized objective take that hedge away? the `rel < 1 iff g < 2cos` admission rule, the oracle-rescale `hedge_share_of_score`, the low-norm-tail gate (concentration x tail-hardness x amplitude shrink) and the denominator-floor counterfactual | s7_loss-B2 turns 2-3 |
| `boundary_interior_split.py` | is a predictor's error - or a CONTRAST between two predictors - BOUNDARY-BORNE? squared-error share by distance-to-domain-edge against the pixel share, the round's nRMSE recomputed on interior crops, and a `crop_sign_flip` flag that fires when a comparison's VERDICT is decided by the edge strip | s6_local-B2 turns 1-2 |
| `persample_gate_audit.py` | audits a SHIPPED per-sample gate / blend / router weight from predictions alone: the alpha it actually realised vs the per-sample optimum, what it captured of the oracle gain, the metric-sensitivity `w = \|\|C\|\|/\|\|Y\|\|` that explains the shortfall, and the per-sample no-harm violation rate | s6_local-B2 turn 3 |
| `warp_premise_audit.py` | pre-flight for any displacement/warp/registration card: is there any interface displacement to warp (sub-pixel level-set estimator, CALIBRATED on synthetic known shifts so a pixel-lattice "0.0 cells" cannot be misread), what a test-fitted per-sample rigid-shift ORACLE buys on the frozen vs the node-aligned path, and (`--gauge`) whether a fitted `phi` is identifiable or aperture-problem gauge (interface normal vs tangential) | s3_warp-B2 turns 1+3 |
| `band_weight_counterfactual.py` | is that spectacular per-band error RATIO worth anything? the band's share of the reference's error (pooled energy + the round metric's own weighting) next to the ratio, plus the decisive band-swap counterfactual (replace arm A's error in one band by arm B's and re-score) and an optional sample stratum | s3_warp-B2 turn 2 |
| `render_readme.py` | regenerates `round1/README.md` from the experiment cards (housekeeping, not a probe) | round infrastructure |
| `amplitude_shrinkage_audit.py` | whether a predictor's excess error is UNDER-CONVERGED AMPLITUDE (regression toward the mean field) or structural damage; cross-arm defect-axis correlation | s1_poisson-B4 turn 2 |
| `cond_column_sensitivity_audit.py` | which columns of the condition vector a trained FiLM-conditioned model actually uses, and whether its score sits on one untested value of a tag column | s1_poisson-B4 turn 3 |
| `persample_norm_eligibility.py` | pre-flight, model-free GO/NO-GO for PER-SAMPLE target/loss normalisation: effective-N NEED test, a promoted-samples-are-noise SAFETY test, and metric-alignment; supersedes residual SPREAD as the decider | s2_beyond_copy-B3 turns 2-3 |
| `checkpoint_divergence_audit.py` | is a rebuilt/paired CONTROL the same run? weight-space distance + bit-identical tensor count between two checkpoints, next to the scores they produced; flags dataset-dependent training nondeterminism | s2_beyond_copy-B3 turn 1 |
| `stage_scaler_placement_forecast.py` | pre-flight, model-free, PER STAGE: which output-target scaler this dataset should be trained under — the typical-sample placement `F = median_i(sd_i/s_i)`, the target-energy effective N, the equalisation a FOREIGN-FIDELITY per-sample statistic actually delivers, and a centering-risk flag on DC-dominated targets | s5_tuning-B3 turns 2-3 |
| `spectral_prestage_bc_audit.py` | training-free: does a global-FFT stage (LSI defect filter / Wiener transfer function / spectral pre-stage) impose the RIGHT boundary condition on this dataset? the data-driven wrap-continuity test, the same closed form refit under a periodic vs a mirror (non-periodic) extension and scored, and the residual left by each binned by distance-to-boundary | s4_hybrid_routing-B3 turns 1-2 |
| `library_dominance_audit.py` | is a router / discrete super learner / MoE LICENSED at all? weak-dominance matrix over the library at each dataset's certified floor, degenerate ties where two members are the SAME object, and the geomean of every constant router vs the per-dataset oracle (`routing_headroom_pct`) | s4_hybrid_routing-B3 turn 3 |

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

---

## `relative_loss_geometry.py`

**Measures.** Whether a per-sample-normalized training objective is safe on
this dataset, from any saved `(pred, target)` pair. Every objective of the form
`L_λ = (1−cos²) + λ(g−cos)²` (λ=1 **is** the scored rel-L2 squared) reduces
exactly to two scalars per sample, `r = ‖p‖/‖y‖` and `c = cos(p,y)`.

| key | meaning |
|---|---|
| `identity_max_absdiff_rel2_vs_shape_plus_gain` | the reduction's own seam check (expect ~1e-15) |
| `per_lambda[*].frac_perverse_alpha_lt_1_and_drive_lt_0` | fraction of under-shooting samples whose target-aligned component gradient descent would **shrink**. **0 by algebra at λ=1** — anything above 0 is entirely the λ>1 gain term |
| `per_lambda[*].escape_drive_at_this_arms_g_median` | `2λ/(λ−1)·r` (λ>1, vanishes as r→0) vs `2(1−r)` (λ=1, finite): the pull that has to take an untrained net away from a near-zero output |
| `per_lambda[*].low_amplitude_valley_cos_over_g` | `λ/(λ−1)`: the alignment ceiling the objective imposes at low amplitude |
| `sample_weight_concentration.*` | `hf_norm_spread`, the top-decile weight share (**MSE-equivalent 0.10**), and the effective sample fraction `1/Σw²/n` with `w ∝ 1/‖y‖²` |

**Read it as.** `frac_perverse > 0` at your λ → the objective de-aligns that
fraction of the data; move λ toward 1. `escape_drive` ≪ 1 at the arm's own
`g_median` → a network that reaches a small output cannot get back out
(s7-B1: allen_cahn 0.073 at λ=4 vs 1.945 at λ=1, and 198 epochs produced
2.4e-4 of nRMSE progress). Weight share far from 0.10 → you are changing
*which* samples get fitted, not just how they are scored; s7-B1 F13, the two
panel datasets that collapsed had spread 22.7 / 5017 and effective fraction
0.16 / 0.45, the four that did not had spread ≤ 2.55 and 0.55–0.99.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/relative_loss_geometry.py \
    --pred_npz <a.npz> [<b.npz> ...] [--labels a b] [--lambdas 1.0 4.0] \
    [--pred_key pred --target_key target] [--plot p.png] [--out d.json]
```
Seconds; CPU; torch autograd on the reduced 2-D coordinates, no model needed.

**Verified.** Run 2026-07-30 from the round root and again from `/tmp`
(absolute path, no cwd dependence) on `s7_loss-B1`'s shipped
`sharp__allen_cahn_2d` predictions and `s5_tuning-B1`'s MSE cap-32 arm:
reproduced the card's `rel_l2_mean` 1.001375560628003 exactly, `frac_perverse`
0.29 at λ=4 and **0.00 at λ=1**, escape drive 0.0732 vs 1.945, top-decile
weight share 0.6909 — identical to card part 6 findings F2/F3/F5.

**Provenance.** `worktrees/s7_loss/B1/scratchpad/reanalysis_turn_1{,b}.py`;
card `experiment_cards/s7_loss/batch_1/B1.json` part 6, findings F1–F5, F13.

---

## `collapse_set_attribution.py`

**Measures.** Whether a per-dataset regression (or gain) is attributable to
your change at all, from two or more arms' `(pred, target)` on the same test
split. Refuses to run if the arms' targets differ.

| key | meaning |
|---|---|
| `attribution_vs_reference[*].frac_reference_collapsed_also_collapsed_here` | overlap of the collapsed sets. **≈1 ⇒ your lever did not create the failure** |
| `attribution_vs_reference[*].spearman_rho_per_sample_rel` | are the arms ranking the samples the same way? |
| `separators_AUC_for_reference_collapse` | rank-AUC of `‖y‖`, DC energy share, HF sharpness, **LF-side sharpness**, copy-LF rel-L2 and **every condition coordinate** for the collapse label |
| `subpopulation_nrmse` | each arm's and copy-LF's nRMSE on the collapsed / surviving halves — where a dataset-level skill is exposed as a mixture statistic |
| `trivial_predictor` | the zero field's skill `1/reference_nRMSE` (rel-L2 of `p=0` is exactly 1) and `arm_skill_over_zero_predictor_skill…` — **1.0 means the arm IS the zero field** |

**Read it as.** Overlap ≈ 1 with ρ > 0.8 → do not write a mechanism for a
failure your change did not cause (s7-B1: pfc overlap 1.00 / ρ 0.979,
cahn_hilliard 0.92 / 0.810 against an MSE-trained arm). High |AUC−0.5| on a
FIELD feature but ≈ 0.5 on every condition coordinate → the hard subpopulation
is identifiable from the LF field and not from the conditioning, so a family
that does not read LF at inference (`lf_at_inference_audit.py`) cannot route
capacity to it. Arm skill ≈ zero-predictor skill → the arm is abstaining, not
predicting.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/collapse_set_attribution.py \
    --preds arm=<a>/preds_test.npz base=<b>/preds_test.npz \
    [--dataset sharp__cahn_hilliard] [--reference-arm arm] \
    [--collapse-threshold 0.9] [--grid 256 256] [--out d.json]
```
`--dataset` adds the copy-LF / condition-vector separators and the skill block
(loads the test split through `round1/eval/panel_data.py`; ~20 s for a 256²
panel dataset). Without it the arm-pairing block still runs from the npz alone.

**Verified.** Run 2026-07-30 from the round root and from `/tmp` on `s7_loss-B1` vs
`s5_tuning-B1`'s MSE cap-32 arm: `sharp__cahn_hilliard` → overlap 0.9231,
ρ 0.8100, sharpness AUC 0.0988 / LF-side 0.1024, best of 19 condition
coordinates |AUC−0.5| = 0.067, copy-LF recomputed vs the frozen
`eval/copylf_baselines.json` **0.0**; `sharp__allen_cahn_2d` →
`arm_skill_over_zero_predictor_skill` 1.0014 (A1a) vs 0.2648 (MSE) — identical
to card part 6 findings F6/F9/F11.

**Provenance.** `worktrees/s7_loss/B1/scratchpad/reanalysis_turn_2{,b,c}.py`
and `reanalysis_turn_3.py`; card
`experiment_cards/s7_loss/batch_1/B1.json` part 6, findings F6–F9, F11–F12.

---

## Standing warning `relative_loss_geometry` + `collapse_set_attribution` encode

**A per-sample-normalized objective is a sample-reweighting, and an explicit
gain weight λ>1 is a gradient sign change — check both before adopting one.**
`s7_loss-B1` replaced `F.mse_loss` by `(1−cos²)+4(g−cos)²` on the champion
architecture and lost `sharp__allen_cahn_2d` completely (skill 16.33 → 62.00,
27.96× its floor; the trained prediction equals the ZERO field to four
significant figures). The objective's algebra was correct — it decomposes the
scored metric exactly — but λ=4 makes the near-zero-output *initialisation* a
stationary point with a vanishing escape drive, and the arm never left it
(2-epoch nRMSE 1.00161 → 200-epoch 1.00138). Meanwhile the two datasets the
card targeted had `hf_norm_spread` 2.55 and 1.14, i.e. no mis-weighting to fix,
and their apparent bimodal failure was already present under MSE on the same
samples. Second, unrelated warning from the same card: **rel-L2 saturates at 1
for a vanishing prediction, so any dataset where a model's nRMSE exceeds 1
offers a free learning-free "gain"** — substituting the zero field for the
champion's `ext__helmholtz_2d` prediction improves its seed-0 panel geomean
7.1022 → 5.2397, 2.1× the certified geomean floor. Check `trivial_predictor`
before believing a helmholtz-driven panel movement.

---

## `registration_skill_split.py`

**Measures.** For any predictor on any 2-D panel dataset: its score re-expressed
against a *registration-corrected* denominator. Rebuilds
`tools/registration_audit.py`'s zero-parameter variants (`A` eval copy-LF · `A2`
wrap · `B` constant `(r-1)/2` shift · `C` node-aligned bilinear · `D` node-aligned
band-limited · `E` Dirichlet node-aligned) per sample through `eval/nrmse.py`, then
reports `model_skill_vs_best_fix`, `pct_copylf_error_removed_{model,best_fix}`,
per-sample beat rates, and — when the result JSON carries `rel_l2_per_sample` — the
`no_harm_gate_oracle_skill` and the `damage_share_of_model_error`.

**Read it as.** `model_skill_vs_best_fix >= 1` → the card's beyond-copy win is a
learned re-derivation of the resampling convention, not physics; report the corrected
geomean next to the scored one. `pct_copylf_error_removed_model` tracking
`pct_copylf_error_removed_best_fix` across datasets is the signature of a
registration-driven mechanism. `best_fix_skill_vs_copylf ~ 1e-5` → the ladder is
DEGENERATE and there is no fidelity gap to correct. `damage_share > 0.5` → most of the
predictor's error is harm inflicted on samples copy-LF already had right, and a trust
gate is worth more than the mechanism.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/registration_skill_split.py \
    --datasets sharp__phase_field_crystal_2d,ext__helmholtz_2d \
    --result_glob '<results_dir>/{dataset}_e200_s0.json' --out split.json
python tools/registration_skill_split.py --datasets PANEL \
    --model_nrmse 'sharp__cahn_hilliard=0.03973' --out split.json
# [--split test_hf] [--metric_key rel_l2_mean] [--copylf_split ref_copylf_identity]
# [--n_test 100]
```
Pure numpy/scipy on the login node, ~10–40 s per 256² dataset. `--metric_key` defaults
to the round's per-sample-mean `rel_l2_mean`; never point it at the legacy
ratio-of-sums `nRMSE` key. Nothing it prints may become a card score.

**Verified.** Run 2026-07-30 from `round1/` over the five `s2_beyond_copy-B2`
datasets against that card's scored `lf_resid_fno` result JSONs → free-fix skills
`7.121e-06 / 0.1103 / 0.4631 / 0.2063 / 0.9077`, `MODEL/FIX` `2578.1 / 2.606 / 0.979 /
3.898 / 4.557`, geomeans `model_vs_copylf 0.380264` (identical to card part 5),
`model_vs_registration_fixed_denominator 10.3148`, `no_harm_gate_oracle 0.25888` —
reproducing turn 1 (`t1_decomposition.json`) and turn 3 (`t3_helmholtz_and_tail.json`)
exactly.

**Provenance.** `worktrees/s2_beyond_copy/B2/scratchpad/reanalysis_turn_1.py` (+ the
gate oracle from `reanalysis_turn_3.py` block A); card
`experiment_cards/s2_beyond_copy/batch_2/B2.json` part 6, findings F1–F3, F12.

---

## `target_scale_spread_audit.py`

**Measures.** From the TRAIN split alone (no model, no GPU): whether a globally
normalized additive-correction target — `target = (HF - LF_up) / max|HF - LF_up|` under
plain MSE, which is what almost every MF family in this round trains — degenerates on
this dataset. Reports the per-sample `||HF - LF_up||` spread, the shared scaler versus a
typical sample's own scale, the MSE energy share of the worst sample and worst 5 %, the
participation-ratio `effective_n_samples_of_mse`, and `median_normalised_target_max`.

**Read it as.** `OUTLIER_DOMINATED` (top-1 energy share > 0.5, or effective N < 5 % of
N) → the loss is one sample; expect a large, uncorrelated correction emitted on every
query, and fix the objective (per-sample normalization / robust loss / sample weights)
before blaming the architecture — cross-check `tools/relative_loss_geometry.py` before
switching. `NEAR_ZERO_TARGETS` (a typical normalized target < 1e-3) → the family cannot
learn to no-op; expect it to damage samples copy-LF already had exact, and pair it with
`tools/trust_gate_headroom.py`. A `resid_norm_max_over_median` above ~1e4 usually also
means the ladder is partly degenerate — confirm with `tools/registration_audit.py`.
`OK` → a global scaler is fine and any failure is elsewhere.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/target_scale_spread_audit.py --datasets PANEL --out spread.json
python tools/target_scale_spread_audit.py --datasets ext__helmholtz_2d --out spread.json \
    [--split train] [--n_max 400] [--outlier_share 0.5] [--spread 100] [--near_zero 1e-3]
```
Pure numpy on the login node, ~2–10 s per dataset.

**Verified.** Run 2026-07-30 from `round1/` over the five `s2_beyond_copy-B2` datasets →
`ext__helmholtz_2d` **BOTH** (top-1 energy share **0.892**, effective N **1.2 / 400**,
scaler/median-per-sample-max 6398), `sharp__phase_field_crystal_2d`
**NEAR_ZERO_TARGETS** (norm max/median **8.24e4**, scaler ratio 7.95e4), and
`allen_cahn / cahn_hilliard / fisher_kpp` **OK** (spread 2.1–4.0). Those are exactly the
two datasets where B2's `lf_resid_fno` failed (skill 4.14 with 96/100 samples damaged;
and an emitted-noise floor 8206x the truth) and the three where it behaved sanely.

**Provenance.** `worktrees/s2_beyond_copy/B2/scratchpad/reanalysis_turn_3.py` (block D);
card `experiment_cards/s2_beyond_copy/batch_2/B2.json` part 6, findings F6, F8–F10.


---

## `stage_keep_test_audit.py`

**Measures.** Whether a staged family's own **keep/discard test** is honest, from
its shipped result JSONs only (no model, no re-scoring). Per dataset:
`optimism` (the base's val error IN-SAMPLE vs OUT-OF-SAMPLE vs on test),
`keep_claim_pct` (what the stage's held-out test claimed), `test_delivered_pct`
(the paired change on the test split, pre-stage applied leg -> scored value),
`sign_inverted`, and a **panel counterfactual**: the geomean with every kept
stage rolled back to its pre-stage leg, against `state/noise_floor.json`'s
0.884 geomean floor and each dataset's `min_claimable_effect`.

**Read it as.** `oof_over_insample > ~2` -> any keep test scored against the
in-sample base is untrustworthy on that dataset, whatever it reports.
`sign_inverted` on a majority of kept cells -> the stage is a net negative that
its own protocol cannot see, and the fix is to score the stage against a base
that is out-of-sample for the *validation* slice (Wolpert 1992), not to tune the
stage. Panel cost inside the geomean floor but resolvable on one dataset -> the
finding is per-dataset, and the card should say so.

**Invoke.** Key paths are CLI dot paths; `{other.path}` substitutes another key's
VALUE (for "which leg was applied" indirection), so the tool is schema-agnostic.
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/stage_keep_test_audit.py \
    --results "$OUTPUTS_ROOT/<stream>/B<N>/eval/results_<arm>/<family>/*_e200_s0.json" \
    --stage_flag stage3_joint \
    --val_pre  s4_gate.val_rel_l2_hybrid_insample_base_at_applied \
    --val_post val_rel_l2_hybrid \
    --test_pre "s4_alpha_protocol_legs.legs.{s4_alpha_protocol_legs.applied_leg}.test_nrmse" \
    --test_post splits.test_hf.rel_l2_mean \
    --base_insample s4_gate.val_rel_l2_base_insample \
    --base_oof s4_gate.val_rel_l2_base_oof --base_test base_only_rel_l2 \
    [--panel a,b,c] [--geomean_floor 0.884] --out /tmp/stage_audit.json
```
Sub-second, pure JSON reads.

**Verified.** Run 2026-07-30 from `round1/` on both s4-B2 arms: `gate_repair`
2 of 2 kept cells **sign-inverted** (claims +63.76 %/+69.43 %, test delivers
-25.58 %/-20.43 %), panel 5.410183 -> **5.049693** (+0.3605, inside the 0.884
floor, RESOLVABLE on `sharp__cahn_hilliard` at +0.9317 vs floor 0.5533);
`gate_repair_dense` 3 of 3 inverted, panel 3.740551 -> **3.451349** (+0.2892).
Both scored geomeans reproduce the authoritative panel JSONs exactly.

**Provenance.** `worktrees/s4_hybrid_routing/B2/scratchpad/reanalysis_turn_1.py`;
card `experiment_cards/s4_hybrid_routing/batch_2/B2.json` part 6, findings F1-F5.

---

## `band_phase_anatomy.py`

**Measures.** For `pred = copylf + correction`, per radial band:
`E_corr/E_c`, `E_err/E_c`, the **cosine** of the correction with the copy-LF
error, the **optimal band gain** `g*`, and the residual an ORACLE band gain would
leave. It is the missing half of `field_error_decomposition.py`'s `band_rel_err`:
that tool says a band is bad, this one says *why*.

| pattern | verdict |
|---|---|
| `cos ~ 1`, `g* != 1` | **AMPLITUDE** — rescaling that band fixes it |
| `cos ~ 0`, `E_corr/E_c ~ 1` | **PHASE** — full-amplitude, phase-random injection; `E_err/E_c -> 1 + E_corr/E_c` and no gate/gain/capacity knob can repair it |
| `0.25 < cos < 0.9` | partial |

`--with_refs` adds the two zero-parameter directions in the same bands
(`registration_audit.build_variants` variant C, and the s6-B1 LSI transfer
function), i.e. the honest ceiling a learned corrector competes against.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/band_phase_anatomy.py --from_diag <run>/diag_<arm>_<ds>_e200_s0.json
python tools/band_phase_anatomy.py --dataset sharp__fisher_kpp_2d \
    --pred_npz <run>/preds_test.npz --pred_key pred [--n_samples 100] \
    [--bands 0,0.125,0.25,0.5,1.0] [--with_refs] --out band.json
```
`--from_diag` is instant (reads stored band energies; the identity is exact only
where the base IS copy-LF, which the output states). The `--pred_npz` path is
seconds; `--with_refs` adds ~1 min for the LSI fit.

**Verified.** Run 2026-07-30 from `round1/` on s4-B2 arm C
(`sharp__fisher_kpp_2d`): diag path -> top band `E_corr/E_c` **1.058**,
`cos` **0.0336**, `g*` 0.033, oracle-gain residual 0.9989 -> verdict **PHASE**,
bands 1-3 PARTIAL (cos 0.55/0.69/0.64). The `--pred_npz` path on the
seam-verified 4-sample replay agrees (skill 0.774818; top band cos 0.0273) and
`--with_refs` reproduces variant-C skill **0.310942** and LSI skill **0.112820**
with LSI clean in all four bands (cos 0.996/0.997/0.982/0.996) while variant C
is clean below 0.5 Nyquist and **PHASE / 5.17x worse** above it.

**Provenance.** `worktrees/s4_hybrid_routing/B2/scratchpad/reanalysis_turn_2.py`
+ `reanalysis_turn_3.py`; card `experiment_cards/s4_hybrid_routing/batch_2/B2.json`
part 6, findings F6, F9-F11.

---

## Standing warning these two tools encode

**A stage that gates itself on held-out error is only as honest as the BASE that
error is measured against, and a band that looks "hard" may be a band the model
is actively poisoning.** On s4-B2 the repaired OOF gate *unlocked* a joint
fine-tune whose keep test still used the in-sample base (16-55x optimism on
`sharp__cahn_hilliard`); it was kept on 5 of 5 eligible cells, claimed +14…+85 %
and delivered -5…-28 %, costing a resolvable +0.93/+0.62 skill units on
cahn_hilliard. And in the top band (0.5-1.0 Nyquist) that card's attention
corrector emitted 106 % of the needed energy at cosine 0.034 — doubling the
band's error — while a zero-parameter filter reached cosine 0.996 there. Check
`oof_over_insample` before believing any keep test, and per-band `cos` before
believing any "needs more capacity/bandwidth" story.

---

## `target_range_placement_audit.py`

**Measures.** From the TRAIN split alone (no model, no GPU), per stage: whether the
family's output-TARGET SCALER is a lever on this dataset. Reports the fluctuation
magnification `G = max|Y_train| / sd(Y_train)` that a unit-variance scaler buys, its
decomposition `G = (max/rms) x (rms/sd)` into a TAIL and a PEDESTAL factor, where the
target actually sits in output range under `maxabs` (`mu/max`, `sd/max`), the
participation-ratio effective N of the per-sample MSE energy under BOTH normalizations,
the per-sample RMS max/median, and the LF-vs-HF placement seam a two-stage
pretrain/finetune family inherits.

**Read it as.** `SCALER_IS_A_LEVER` (`G` >= `--g_lever`, default 8) -> a unit-variance
target scaler is worth an arm — but **gate it on `tools/dc_pattern_split.py`**: a
LEVEL_ONLY dataset has no pattern channel to magnify and will be inert regardless.
`PEDESTAL_ONLY` -> `G` is mostly a DC offset, which the output layer's bias absorbs for
free; expect a null (this is exactly the trap s5-B2 fell into with `|mu|/sd`).
`SCALER_INERT` -> stop tuning normalization and look for a mechanism that produces
PATTERN. `+STAGE_SEAM` -> the two stages are placed very differently under `maxabs`.
If `eff_n_fraction` is tiny the loss is one sample: **a global scaler cannot fix that**
(the tool prints `eff_n_change_from_zscore` to prove it) — go to
`tools/target_scale_spread_audit.py` / `tools/relative_loss_geometry.py` instead.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/target_range_placement_audit.py --datasets PANEL --out placement.json
python tools/target_range_placement_audit.py --datasets ext__helmholtz_2d,ifc_poisson \
    --out placement.json [--split train] [--n_max 400] [--g_lever 8.0] \
    [--pedestal_ratio 2.0] [--stage_seam 3.0]
```
Pure numpy on the login node, ~2-10 s per dataset.

**Verified.** Run 2026-07-30 from `round1/` over `--datasets PANEL`:
`ext__helmholtz_2d` **SCALER_IS_A_LEVER** (`G` 39.470 = tail 39.436 x pedestal 1.001,
effective N **1.01/400**), `ifc_poisson` **SCALER_IS_A_LEVER** (`G` 9.858 = 5.660 x
1.742, effective N 4.17/5), `sharp__fisher_kpp_2d` **PEDESTAL_ONLY** (`G` 5.997 =
1.546 x **3.880**), `sharp__phase_field_crystal_2d` / `sharp__allen_cahn_2d` /
`sharp__cahn_hilliard` **SCALER_INERT** (`G` 3.814 / 2.537 / 1.322). Those are exactly
the two datasets that moved beyond their floors under s5-B2's `zscore` arm and the four
that did not — including `sharp__fisher_kpp_2d`, the dataset the card's `|mu|/sd`
covariate predicted would move most and which moved least.

**Provenance.** `worktrees/s5_tuning/B2/scratchpad/reanalysis_turn_1.py` (block A),
`reanalysis_turn_2.py` (block A), `reanalysis_turn_3.py` (block A2); card
`experiment_cards/s5_tuning/batch_2/B2.json` part 6, findings F1, F2, F5, F6, F7, F12.

---

## `paired_arm_displacement.py`

**Measures.** From two arms' `preds_test.npz` (the round's dump contract): how far the
learned FUNCTION moved (`||pred_arm - pred_ctrl|| / ||pred_ctrl||`, cosine between the
two predictions), whether it moved TOWARD THE TRUTH (per-sample cosine of the
displacement with the control's own error, against the random-direction baseline
`sqrt(2/(pi n))`, the fraction of samples improving in direction, and the optimal step
along the displacement), whether the LEVEL or the PATTERN moved (DC/pattern share of the
displacement), and how much of any score gain is calibration rather than field content
(`amplitude_share_of_log_gain`, from an oracle per-sample rescale).

**Read it as.** `INERT` -> the knob did not change the function; the null is about the
KNOB. `MOVED_NOT_TOWARD_TRUTH` -> non-informative content was re-rolled; conclude nothing
about direction. `MOVED_TOWARD_TRUTH_UNCASHED` -> the knob helps but the dataset's
headroom / the round's floor is too small to show it; the null is about the DATASET and
the knob may pay in a family that can cash it. `MOVED_AND_PAID` -> check
`amplitude_share_of_log_gain` before claiming pattern. The `--paid_ratio` threshold is
crude; the dataset's own `min_claimable_effect` in `state/noise_floor.json` is the real
arbiter.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/paired_arm_displacement.py --out disp.json \
    --pair ifc_poisson=/abs/arm/preds_test.npz,/abs/control/preds_test.npz
python tools/paired_arm_displacement.py --datasets PANEL --out disp.json \
    --arm_root  /abs/outputs/<stream>/B<N>/eval/results/<arm>/<family> \
    --ctrl_root /abs/control/dir [--toward_truth_cos 0.1] [--inert_disp 0.05] \
    [--paid_ratio 1.10]
```
Targets are asserted equal between the two files; a shorter side (a paired SUBSET regen)
truncates the other and sets `paired_subset`. Pure numpy, CPU, seconds.

**Verified.** Run 2026-07-30 from `round1/` on s5-B2's `zscore` arm vs the `maxabs`
cap-12 control (`worktrees/s5_tuning/B1/scratchpad/cap12_infer`):
`ext__helmholtz_2d` disp **0.993** cos **+0.764** -> MOVED_AND_PAID (6.46804 -> 1.89976);
`ifc_poisson` disp **0.035** cos +0.605, 99 % of samples toward truth -> MOVED_AND_PAID
(0.05563 -> 0.04266); `sharp__phase_field_crystal_2d` disp **0.425** cos +0.539 ->
MOVED_TOWARD_TRUTH_UNCASHED (0.51341 -> 0.50224, 4.6x inside its floor);
`sharp__cahn_hilliard` disp 0.244 cos +0.295 -> MOVED_TOWARD_TRUTH_UNCASHED;
`sharp__allen_cahn_2d` disp 0.026 cos **-0.013** with **46 %** of samples toward truth ->
**INERT**; the `--pair` path on the 24-sample `sharp__fisher_kpp_2d` subset ->
MOVED_NOT_TOWARD_TRUTH (cos +0.076). A dataset whose control preds are missing is
reported with an `error` field and does not stop the sweep.

**Provenance.** `worktrees/s5_tuning/B2/scratchpad/reanalysis_turn_2.py` (block B),
`reanalysis_turn_3.py` (block B), `reanalysis_turn_3b.py`; card
`experiment_cards/s5_tuning/batch_2/B2.json` part 6, findings F3, F8, F9, F10, F13, F15.

---

## Standing warning these two s5-B2 tools encode

**A global output-target scaler is a DYNAMIC-RANGE PLACEMENT device, not a
sample-weighting device — and "the score did not move" is not the same as "the knob did
nothing".** Measured on s5-B2: switching `max|Y|` -> `mean/std` left the effective N of
the training MSE at 1.0145 -> 1.0179 out of 400 samples (a global scalar divides every
sample's energy by the same constant, so it *cannot* de-concentrate an outlier-dominated
loss); the covariate that ordered the panel was `G = max|Y|/sd`, not `|mu|/sd`, because a
pedestal is free to an output bias; 91.6 % of the headline -70.6 % helmholtz gain was
per-sample amplitude calibration; and the one dataset that paid did so from a 3.5 %
function displacement while a dataset that displaced 42.5 % *toward the truth* scored
flat. Run `target_range_placement_audit.py` BEFORE spending an arm on normalization, and
`paired_arm_displacement.py` before writing down any null.

---

## `ladder_pair_row_audit.py`

**Measures.** Whether a multi-fidelity family's "all ordered pairs" / "adjacent
pairs" row set is data amplification or a **loss-weighting knob in disguise**:

| field | question answered |
|---|---|
| `rows_total` / `rows_distinct_XY` | how many of the arm's rows are distinct `(X, Y)` content (compared within a target level, since `n_cells` differs per level) |
| `per_level.replication_factor` | how many times each level's samples are repeated |
| `per_level.share_ratio_vs_self_only` | the effective loss-weight shift each level takes relative to the self-rows-only baseline (exact under per-level target normalization) |
| `steps_per_epoch` | the optimization confound that rides along with any row-count change |
| `index_alignment` + `--cond-from source` | the older defect: source-indexed cross rows on non-aligned fidelity lists pair the wrong parameters with the wrong field |
| `verdict` | `SELF_ROWS_ONLY` / `REPLICATION_ONLY` / `ADDS_ROWS` / `MISMATCHED_PAIRS` |

**Read it as.** `REPLICATION_ONLY` → the pair set adds no supervision; whatever
it does to the score is a **per-level reweighting** (plus more gradient steps),
so compare against `self_only` before claiming a pairing result. Cross-reference
`ladder_level_diagnostic.py::matched_level_predictor_on_test`: if the levels
being **upweighted** are the sparse ones, the arm is trading condition-space
coverage for in-sample fit at the top level. `MISMATCHED_PAIRS` → fix the
indexing before interpreting anything.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/ladder_pair_row_audit.py --dataset ifc_poisson \
    [--modes self_only adjacent allpairs two_level] \
    [--cond-from target|source] [--batch-size 16] [--out audit.json]
```
Read-only, numpy only, seconds.

**Verified.** Run 2026-07-30 from `round1/`. `ifc_poisson` (ifc_raw, 4 levels,
n = 100/50/20/5): `allpairs` **280 rows / 175 distinct / 105 duplicates**, share
ratio 0.62 / 1.25 / 1.88 / **2.50** by level, 18 vs 11 steps/epoch →
`REPLICATION_ONLY`; `adjacent` 250/175; `two_level` 180/175; `--cond-from
source` on `allpairs` → 280 distinct and `MISMATCHED_PAIRS` (the B1-era defect,
`index_aligned false`). Portability: `heat_local` (npz_l, 5 levels × 1024) →
`allpairs` 15360/5120, share ratio 0.33 … 1.67, `REPLICATION_ONLY`. The
`ifc_poisson` numbers reproduce the card's turn-1 measurement exactly.

**Provenance.** `worktrees/s1_poisson/B3/scratchpad/reanalysis_turn_1.py`
(probes P1/P2); card `experiment_cards/s1_poisson/batch_3/B3.json` part 6,
findings T1-F1, T1-F2.

---

## `gain_calibration_ceiling.py`

**Measures.** Before a per-sample calibration head is designed, the three
ceilings it could aim at on a shipped `preds_test.npz`, every one of them fitted
on the test targets and labelled `[TEST-FITTED]`:

1. **one global gain** — a single scalar for the whole split (usually ≈ 0 gain);
2. **X-linear law** — ridge on the standardized condition vector with
   closed-form LOO (PRESS) λ selection, plus its R², per-coordinate variance
   share and clip fraction;
3. **per-sample gain oracle** — one scalar per sample, the hard ceiling.

with `amplitude_share_of_sq_error`, the log-gain dispersion, and (given
`--floor`) every headroom expressed in noise-floor units.

**Read it as.** `amplitude_share_of_sq_error` < ~0.2 → a calibration head has
almost nothing to work with; go look at the pattern channel
(`dc_pattern_split.py`). X-linear ≈ oracle → the gain is a *smooth function of
the conditions*, i.e. a generalization error of the conditional map, and a head
can recover most of it. Every headroom < 1 floor → do not spend a batch on a
head. Complements `field_error_decomposition.py` (which splits the error) and
`residual_gain_learnability.py` (which asks whether the gain is learnable
out-of-sample); this one prices the whole ladder of ceilings in one call.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/gain_calibration_ceiling.py --preds /abs/preds_test.npz \
    [--dataset ifc_poisson] [--split test] [--floor 0.008636672175093287] \
    [--clip 0.5 2.0] [--out ceiling.json]
```
Without `--dataset` only ceilings 1 and 3 are reported. Read-only, numpy, seconds.

**Verified.** Run 2026-07-30 from `round1/` on s1-B3's two bases with
`--floor 0.008636672175093287`. `base__none` (allpairs): amplitude share
**0.585**, raw 0.034264, one global gain 0.035125 (**−0.10 floors**, i.e. a
constant rescale *hurts*), X-linear law 0.024354 (**1.15 floors**, R² 0.9184 /
LOO 0.9093, top coord4 0.669), per-sample oracle 0.022935 (1.31 floors) — these
independently reproduce s1-B2's 0.919 R² / 0.02431 bound / 0.022917 oracle.
`self_only__none`: amplitude share 0.134, every ceiling within **0.14 floors**
of raw → the same head is not worth a batch on that base (and s1-B3 measured it
actively harmful there: 0.021913 → 0.035890).

**Provenance.** `worktrees/s1_poisson/B3/scratchpad/reanalysis_turn_2.py`
(probes Q1/Q3/Q4); card `experiment_cards/s1_poisson/batch_3/B3.json` part 6,
findings T2-F1, T2-F2, T2-F5.

---

## `norm_tail_hedge_audit.py`

**Measures.** Two things an nRMSE cannot show, from any saved
`(pred, target)` on a panel test split (metrics via `round1/eval/nrmse.py`):

1. **The admission rule.** Writing `g = ||p||/||y||`, `cos = <p,y>/(||p|| ||y||)`,
   `rel^2 = 1 + g^2 - 2 g cos`, so **`rel < 1` iff `g < 2 cos`**. The zero field
   scores exactly 1 everywhere, so on a sample whose shape the model cannot get,
   SHRINKING beats predicting — squared error does this automatically, a
   per-sample-normalized objective does not. Reports `frac_g_ge_2cos` (all and
   on the low-norm tail: the share of the split the arm is scored *worse than
   nothing* on), the margins, and `hedge_share_of_score`
   `= 1 - mean sqrt(1-cos^2) / nRMSE` — how much of the score is amplitude
   rather than shape.
2. **The low-norm tail gate**, i.e. whether a per-sample-normalized loss
   (`w ~ 1/||y||^2`) would sacrifice that tail: (i) concentration
   (`hf_norm_spread >= 10` or effective sample fraction <= 0.20), (ii) the
   low-norm decile at least 2x harder than the rest, (iii) the reference
   (MSE-trained) arm *shrinking* amplitude there
   (`g_median(tail)/g_median(all) <= 0.8`). All three -> `RISK`, two -> `WATCH`.
   `--floors` adds the training-free denominator-floor counterfactual (what a
   floor on `||y||` does to the weight concentration), and the amplitude law
   slope `log||pred|| ~ log||y||`.

With two or more arms it also prints the pairwise gap decomposition against the
reference: the share of the gap that is the amplitude channel (gap after an
oracle per-sample rescale) and the share carried by the 5 / 10 worst samples.
Refuses to run if the arms' `target` arrays differ (the pairing seam).

**Complements** `relative_loss_geometry.py` (which prices the *loss*'s own
geometry at each lambda: perverse region, escape drive, weight concentration)
and `collapse_set_attribution.py` (which asks *which samples* broke and what
identifies them). This one prices the *metric*'s asymmetry and the between-sample
reweighting channel that a per-sample (r, cos) reduction cannot see — the channel
that cost s7_loss-B2 1.818 certified floors at lambda = 1.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/norm_tail_hedge_audit.py \
    --preds mse=/abs/a/preds_test.npz [rel=/abs/b/preds_test.npz ...] \
    [--reference-arm mse] [--decile-frac 0.1] [--floors 0.1 0.25 0.5] \
    [--out audit.json] [--plot plane.png]
```
Read-only, numpy, seconds. Single-arm mode reports the gate only.

**Verified.** Run 2026-07-30 from `round1/` on `sharp__allen_cahn_2d`
(`mse` = s5_tuning-B1 `..._modes` cap-32, `rel` = s7_loss-B2 `arm_rel_both`):
reference gate **RISK** (spread 22.0, effective sample fraction 0.163, tail
hardness 4.29, `g_ratio` 0.587); `frac_g_ge_2cos` on the low-norm tail 0.30
(mse) -> 0.80 (rel); amplitude law slope 1.278 -> 1.036; floors
q0.1/q0.25/q0.5 lift the effective sample fraction 0.163 -> 0.316 / 0.631 /
0.872; pairwise gap 0.04702 of which **0.601 is the amplitude channel** and
0.526 sits in 5 samples (worst indices 30, 81, 66, 88, 43). Cross-checked on
`ifc_poisson` (verdict `OK`, n=128, spread 4.32) and `ext__helmholtz_2d`
(verdict `OK` but `hedge_share_of_score` **0.696** and `frac_g_ge_2cos` 0.99 —
the overshoot regime, B1 F10/F11).

**Provenance.** `worktrees/s7_loss/B2/scratchpad/reanalysis_turn_2.py` +
`reanalysis_turn_3.py`; card `experiment_cards/s7_loss/batch_2/B2.json` part 6,
findings F6-F11.

---

## `boundary_interior_split.py`

**Measures.** The EDGE-DISTANCE complement to `interface_locality_profile.py` (which bins
by |grad HF|). For every prediction file, and for every contrast against the first one:

| key | meaning |
|---|---|
| `nrmse_full` | the round's nRMSE (`eval/nrmse.py`) on the whole field |
| `interior_nrmse[m]` | the SAME metric recomputed on the interior crop at margin `m` cells |
| `strip[s].frac_sq_err` / `frac_pixels` / `concentration` | share of the file's squared error inside `distance-to-edge < s`, that strip's pixel share, and their ratio (1.0 = spatially neutral) |
| `verdict` | `BOUNDARY_BORNE` (innermost concentration >= 3) / `MILD` (>= 1.5) / `NEUTRAL` / `INTERIOR_BORNE` (<= 0.67) |
| `contrasts[*].ratio_by_margin` | `nrmse(other)/nrmse(first)` at each crop |
| `contrasts[*].crop_sign_flip` | **True when the ratio crosses 1.0 between the full field and the largest margin** |

**Read it as.** A contrast with `crop_sign_flip = True` is a BOUNDARY-HANDLING result, not
an operator-class result — say which one you mean before reporting it. A flat
`ratio_by_margin` is boundary-independent and may be attributed to representation. A single
arm with `verdict = BOUNDARY_BORNE` has an unfixed padding / extension / seam bug that is
worth more than any capacity knob.

Round 1 keeps producing wins and losses that live in a few cells at the domain edge (zero
padding, circular padding on a non-periodic upsample, an implicitly-periodic FFT control on
a Dirichlet domain, `copylf_prediction`'s `zoom(..., mode="nearest")` wrap seam). This is the
one-pass test for all of them.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/boundary_interior_split.py \
    --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
    [--pred_key pred --target_key target] [--grid H W] \
    [--strips 1 2 4 8 12 16] [--margins 0 4 8 12 16] \
    [--out split.json] [--plot split.png]
```
Pure numpy (+ matplotlib only with `--plot`), seconds. Every file must carry the SAME target
array (it refuses otherwise); square grids are inferred, 1-D layouts (`H == 1`) are handled,
otherwise pass `--grid`.

**Verified.** Run 2026-07-30 from `round1/` on `s6_local-B2`'s replayed arms:
`heat_local` `circ_repair` **MILD** (d<1 concentration 2.58) vs `lsi_ctrl`
**BOUNDARY_BORNE** (14.56), ratio_by_margin 11.70 -> 9.01 (`crop_sign_flip` **False** — the
trained arm's 11.7x guard advantage is NOT a boundary artifact); `sharp__allen_cahn_2d`
ratio_by_margin 0.8885 -> 1.0145 with `crop_sign_flip` **True** — the batch's one prediction
miss, localized to a one-cell rim; `sharp__sod_1d` (1-D, 1x128) 17.13 -> 17.36, flip False.

**Provenance.** `worktrees/s6_local/B2/scratchpad/reanalysis_turn_{1,2}.py`;
card `experiment_cards/s6_local/batch_2/B2.json` part 6, findings F1-F4, F8.

---

## `persample_gate_audit.py`

**Measures.** The counterpart to `trust_gate_headroom.py`: that tool prices whether a
gate is worth BUILDING (oracle ceilings, before the fact); this one audits a gate you
already SHIPPED, from predictions alone. It models `pred = base + alpha_i * (model - base)`
and RECOVERS `alpha_i` by per-sample least-squares projection, so it needs no access to
the gate's internals and works for a trust head, a router weight, a stacking coefficient
or a copy-LF-vs-model switch.

| key | meaning |
|---|---|
| `alpha_implied` / `alpha_star` | the blend weight actually realised, vs the per-sample optimum `<R_i,C_i>/\|\|C_i\|\|^2` (`--alpha_clip` to match the gate's own clip) |
| `recovery.pearson` / `.spearman` | is the gate estimating the right thing at all? |
| `scores.*` | round nRMSE of base / model at `alpha=1` / the shipped gate / the global scalar / the per-sample ORACLE, with `oracle_gain_vs_global_pct` (the headroom chased), `gate_gain_vs_global_pct` (what was delivered) and `captured_fraction_of_oracle_gain` |
| `sensitivity.*` | `w_i = \|\|C_i\|\|/\|\|Y_i\|\|`, the SCORED metric's sensitivity to a per-sample alpha error: `p50` / `max` / `max_over_p50`, `spearman_excess_vs_w`, and the worst samples' `times_mean_excess` |
| `no_harm.*` | fraction of samples ending WORSE than `base` under the gate, at `alpha=1`, and at the global scalar, plus the worst ratio |
| `verdict` | `NO_PERSAMPLE_HEADROOM` / `SENSITIVITY_LIMITED` / `GATE_HELPS` / `GATE_HURTS` |

**Read it as.** High `recovery` + a `gate_gain` worse than `oracle_gain` + a large
`sensitivity.max_over_p50` -> `SENSITIVITY_LIMITED`: the gate estimates alpha well and is
being scored on a handful of samples, so **weight its fit by `w^2`** before changing
anything else. (The per-sample argmin of relative L2 and of squared L2 are the SAME —
`\|\|Y_i\|\|` is constant in alpha — so "fit a different objective" is the wrong diagnosis;
the fit's WEIGHTING is what is wrong.) `oracle_gain_vs_global_pct` inside the dataset's
certified floor -> there is no per-sample headroom and a global scalar is the honest
choice. `no_harm.frac_worse_than_base_gate` >> `..._global` -> the gate traded an exact
no-harm floor for headroom; report that as a cost, because "alpha = 0 reproduces the base
exactly" is a CONSTRUCTION claim, not a per-sample one.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/persample_gate_audit.py \
    --base_npz <copylf_or_base.npz> --model_npz <ungated_model.npz> \
    [--gated_npz <shipped_gated.npz>] [--global_alpha <the run's held-out scalar>] \
    [--alpha_clip 0 1.5] [--pred_key pred --target_key target] \
    [--top_k 3] [--out audit.json]
```
Pure numpy + scipy.stats, seconds. **Always pass `--global_alpha`**: without it the tool
grid-searches the global scalar on the TEST split, which is an oracle reference and
flatters the gate (it is labelled as such in `scores.global_alpha_source`).

**Verified.** Run 2026-07-30 from `round1/` on `s6_local-B2`'s `trust_head_circ`
(reconstructed from the bit-shared `circ_repair` corrector, C3 pairing sha-equal 5/5),
with the run's own held-out scalars and `--alpha_clip 0 1.5`:
`sharp__phase_field_crystal_2d` recovery Pearson **0.9983**, oracle gain **-25.83 %**,
gate gain **+21.51 %** (card: +21.319 %, the gap is CPU-replay precision),
`sensitivity.max_over_p50` **189.3**, `spearman_excess_vs_w` +0.659 -> verdict
**SENSITIVITY_LIMITED**; `ext__helmholtz_2d` oracle gain -49.50 %, gate gain **-29.02 %**,
`captured_fraction_of_oracle_gain` **0.586**, `no_harm` 0.35 (gate) vs 0.00 (global
scalar), worst ratio 1.656 -> verdict **GATE_HELPS**.

**Provenance.** `worktrees/s6_local/B2/scratchpad/reanalysis_turn_3.py` +
`scratchpad/turn3_sensitivity_check.json`; card
`experiment_cards/s6_local/batch_2/B2.json` part 6, findings F10-F13.

---

## `warp_premise_audit.py`

**Measures.** Before a displacement / warp / registration card is built (or, as here,
after one is falsified), the two questions that decide it:

* **(A) premise** — interface displacement between a moving image and the HF target,
  measured with a **sub-pixel** level-set normal estimator `d = (u_mov − u_tgt)/|∇u_tgt|`,
  *and* with the pixel-lattice EDT estimator the round's diagnostics use, *and* an
  `edt_calibration` table built by Fourier-shifting the HF field by known amounts on this
  very data. Plus a test-fitted **per-sample rigid-shift oracle** (exact rel-L2 minimiser
  over a continuous circular shift, Parseval search) on both the frozen copy-LF path and a
  node-aligned corrected path, with the global-constant-shift control.
* **(B) gauge** (`--gauge --phi_npz`) — decomposes a fitted `(N,2,H,W)` displacement into
  interface-**normal** (identifiable) and **tangential** (aperture-problem gauge) parts.

**Read it as.** `levelset.corrected.median ≲ 0.1` cell → **nothing to warp**; a warp can
only add error on the bulk. `levelset.copylf.median ≈ expected_registration_offset_cells`
→ the "displacement" is the round's `(r−1)/2` grid convention (s3_warp-B1 F1/F2), and a
rigid-shift oracle that looks strong on copy-LF is buying registration — check
`rigid_oracle.corrected`. Any EDT-style "0.0 cells" reading must be read against
`edt_calibration` (it reports 0.0 for a true 0.354-cell shift). `gauge.*.interface_normal_
energy_share ≪ 1` → `|φ − φ_oracle|²` is a supervision target made mostly of gauge; project
onto the normal component or supervise the warped **image** instead.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/warp_premise_audit.py --datasets sharp__cahn_hilliard --out a.json
python tools/warp_premise_audit.py --datasets PANEL --out a.json --no_rigid
python tools/warp_premise_audit.py --datasets sharp__cahn_hilliard --out a.json \
    --gauge --phi_npz <outputs>/eval/<fam>_<ds>_phi.npz --phi_keys phi_pred_warp
```
Pure numpy/scipy, login-node fine: ~1 min/dataset without the rigid oracle, ~3 min with it
on 100 × 256². `--tau` sets the interface band (default 0.1, the round convention).

**Verified.** Run 2026-07-30 from `round1/` on `sharp__cahn_hilliard` with the card's own
φ sidecar → `corrected_skill` **0.4769** (= `ref_reg_corrected` 0.47687619181488217),
level-set displacement **0.6959** cells (copy-LF, vs the predicted registration constant
0.7071) → **0.0070** (node-aligned), EDT corrected median **0.0** with the calibration row
`true 0.354 → EDT 0.0`, rigid oracle **0.4193** (median |s| 0.7077) → **0.3989**
(median |s| 0.0447), gauge `phi_pred_warp` |φ| 0.5038 = normal 0.0440 + tangential 0.4943,
normal energy share **0.0346** — matching card part 6 F1–F4 / F9.

**Provenance.** `worktrees/s3_warp/B2/scratchpad/reanalysis_turn_1.py` and
`reanalysis_turn_3.py`; card `experiment_cards/s3_warp/batch_2/B2.json` part 6,
findings F1–F4, F9.

**Known gotcha it encodes.** `models_r1/s3_warp_onesided/diagnostics.py::interface_mask`
returns a **flat** `(N, H*W)` mask (the family reshapes at every one of its own call
sites); the first run of `reanalysis_turn_3.py` crashed on this and the scratchpad copy was
fixed with `.reshape(-1, H, W)`. The family file was not touched.

---

## `band_weight_counterfactual.py`

**Measures.** For two predictions on one dataset, per band: (1) the **weight** — the band's
share of the reference's error, as pooled energy *and* in the round metric's own weighting
(per-sample share of rel-L2², exact by Parseval); (2) the usual ratios; (3) the
**counterfactual** — replace arm A's Fourier error in one band by arm B's and re-score
through `round1/eval/nrmse.py`, giving the share of the A-vs-B skill gap that band actually
owns; (4) optionally all of it on a sample **stratum** (`--strata_npz`), with a
stratum-matched reference denominator.

**Why it matters.** Band ratios are unbounded in near-empty bands. This has now produced
two round-1 headlines worth < 1 % of the metric: s3_warp-B1 F4 (wrap seam, 0.12–0.74 %) and
s3_warp-B2 part 5 F1 (an 11× band-32–64 regression called "the most informative band signal
on the card", actually 0.45 %). Complements `band_phase_anatomy.py`, which splits a band's
failure into amplitude vs phase but does not weight it or re-score.

**Read it as.** `share_of_gap` is the honest attribution — trust it over the ratios.
`weight(metric)` bounds how much a band can ever be worth. If a stratum restriction flips
the ranking, the pooled statistic was a statement about a handful of samples.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/band_weight_counterfactual.py --dataset sharp__cahn_hilliard \
    --arm_a preds_warp.npz:pred --arm_b preds_warp_off.npz:pred --out b.json
# zero-parameter built-ins need no prediction files at all:
python tools/band_weight_counterfactual.py --dataset sharp__cahn_hilliard \
    --arm_a nodealign --arm_b copylf --out b.json
python tools/band_weight_counterfactual.py ... --strata_npz strata.npz:matched
```
`copylf` = `eval/panel_data.py::copylf_prediction`; `nodealign` = one bilinear resample of
the raw LF at `k/r` (s3_warp-B1 F3 variant C). Bands default to the round convention
`[0,.125,.25,.5,1] × k_nyquist`. ~1 min/dataset, pure numpy.

**Verified.** Run 2026-07-30 from `round1/` on `sharp__cahn_hilliard`, arms rebuilt from
`s3_warp-B2`'s checkpoint: A=`warp` skill **0.48376**, B=`warp_off` **0.43166**, gap
**+0.05210**; `share_of_gap` **[0.8567, 0.0593, 0.0045, 0.0039]** and `weight(metric)`
**[0.9964, 3.27e-3, 7.03e-5, 2.68e-4]** — identical to card part 6 F5/F6. With
`--strata_npz` (98 matched) the skills become **0.26987 / 0.19640**, reproducing part 6
F12's matched-stratum table. Built-in mode `--arm_a nodealign --arm_b copylf` reproduces
`ref_reg_corrected` skill **0.47688**.

**Provenance.** `worktrees/s3_warp/B2/scratchpad/reanalysis_turn_2.py` +
`turn2_counterfactual.py`; card `experiment_cards/s3_warp/batch_2/B2.json` part 6,
findings F5–F7.


## `amplitude_shrinkage_audit.py`

**What it measures.** For each `preds_test.npz`: the per-sample oracle gain
`g_i = <p_i,y_i>/<y_i,y_i>`, the regression of `log g_i` on centred `log||y_i||`
(corr / slope / R^2), the amplitude response `d log||p_i|| / d log||y_i||`, the demeaned
regression `beta`, the structure-only nRMSE (after each sample's own oracle gain), and a
verdict `SHRINKAGE` / `NEUTRAL` / `AMPLIFICATION`. With several files on the same
targets it also prints the cross-arm correlation of `log g_i` (do the arms share ONE
defect axis?) and the scored-vs-structure-only spread ratio.

**Why it is not `field_error_decomposition.py`.** That tool reports how MUCH of the
squared error is a per-sample gain (a magnitude). This one reports whether that gain
error is a SHRINKAGE toward the mean (a direction) — the thing that discriminates an
under-trained model from a structurally damaged one.

**Invocation.**
```bash
python tools/amplitude_shrinkage_audit.py \
    --pred_npz <a>/preds_test.npz <b>/preds_test.npz --labels A0 A1 \
    [--pred_key pred --target_key target] [--shrinkage_corr_threshold 0.5] \
    [--out audit.json]
```

**Verified.** Run 2026-07-30 from `round1/` on `s1_poisson-B4`'s A0/A1/A2 arms:
`corr(log g, log||y||)` **-0.0365 / -0.9142 / -0.9096**, amplitude slope
**0.9982 / 0.9256 / 0.8373**, scored spread **2.840x** against a structure-only spread
of **1.288x** — identical to card part 6 T2-F1/T2-F2.

**Provenance.** `worktrees/s1_poisson/B4/scratchpad/reanalysis_turn_2.py`; card
`experiment_cards/s1_poisson/batch_4/B4.json` part 6, findings T2-F1..T2-F4.

## `cond_column_sensitivity_audit.py`

**What it measures.** Inference-only, from one or more family checkpoints:
(R1) the normalised central-difference sensitivity `||d out / d cond_j|| / ||out||` for
every condition column plus each column's share — where did the conditioning capacity
go? (R2) a sweep of ONE column over a list of values, re-scored through
`eval/nrmse.py` — is the score robust to that column, or does it sit on a single
untested value? (R3) an auto-detected FiLM probe (any submodule named `film`): the
across-condition modulation std per module and the same per-column sensitivity inside
the conditioner, which localises R1 in the conditioner rather than the backbone.

**The standing warning it encodes.** A scored number never reveals a tag-column
fragility. On `s1_poisson-B4` the stream's best `ifc_poisson` checkpoint scores
**0.0219 at the contract's eval query `f_src = 0` and 0.1066 at `f_src = 1`** (4.86x),
because `self_only` training makes `f_src` and `f_tgt` perfectly collinear. Run this
before reusing ANY checkpoint at a query it was not scored at.

**Invocation.**
```bash
python tools/cond_column_sensitivity_audit.py \
    --family_dir <worktree>/models_r1/<family> --model_class LadderFNO2d \
    --model_kwargs '{"hidden_channels":64,"n_blocks":4,"modes_h":12,"modes_w":12,
                     "grid":[64,64],"cond_feat_dim":64}' \
    --ckpt <A>/last.pt <B>/last.pt --labels A B \
    --dataset_dir "$FACTORY_ROOT/data/<ds>" --split test \
    --tags 0.0 1.0 --col_names X1 X2 X3 X4 X5 f_src f_tgt \
    --output_scaler <the family's eval-time output scaler> \
    --sweep_col f_src --sweep_values 0 0.3333 0.6667 1 \
    [--n_samples 32] [--eps 0.01] [--device cpu] [--out audit.json]
```
`--model_kwargs` is passed to `--model_class` verbatim with `cond_dim` filled in from
the data + `--tags`; `--tags` are the constant trailing columns of the eval query (omit
for families conditioned on X alone). COST: 2 x n_columns forward passes per checkpoint;
a 128-sample 64^2 six-checkpoint audit took ~19 min on a contended 1-core login node —
use `--n_samples 32`.

**Verified.** Run 2026-07-30 from `round1/` on `s1_poisson-B4`'s A0 (`self_only`) and A1
(`allpairs`) checkpoints, `--n_samples 32`: `f_src` share **0.048 vs 0.005**, `f_src`
sweep nRMSE range **4.658x vs 1.085x**, FiLM `f_src` share **0.122 vs 0.044** —
reproducing card part 6 T3-F2/T3-F3 (full 128-sample values 0.0528/0.0050, 4.86x/1.09x,
0.1227/0.0438).

**Provenance.** `worktrees/s1_poisson/B4/scratchpad/reanalysis_turn_3.py`; card
`experiment_cards/s1_poisson/batch_4/B4.json` part 6, findings T3-F2..T3-F5.

---

## `persample_norm_eligibility.py`

**Measures.** Pre-flight, model-free, no GPU: should this dataset's regression
target (or loss) be normalised PER SAMPLE? Every normalisation is a re-weighting
of the loss by `1/den_i^2`, so the tool runs three checks on the train split and
returns a `verdict` with `reasons`:

* **R1 NEED** — `effective_sample_fraction` = effN of the MSE target energy under
  the CURRENT global scaler, divided by N. Below `--r1_threshold` (0.05) the loss
  is outlier-dominated and only a PER-SAMPLE denominator can fix it (a
  per-dataset scaler provably cannot — s5_tuning-B2).
* **R2 SIGNAL** — do the samples the re-weighting PROMOTES carry signal?
  `min_i ||r_i||/||y_i||` against `--noise_floor` (1e-06), plus the in-band
  (`|k| < --modes_cap`) energy fraction of the smallest-scale decile against the
  white-noise reference, plus `floor_inside_noise` (does the `--floor_q`
  denominator floor sit inside the numerical noise?).
* **R3 METRIC** — does the proposed denominator track the SCORED metric's own
  denominator `||y_i||`? `spearman_log_scale_vs_log_fieldnorm` and
  `KL(weight || metric-implied weight)` for both normalisations.

**Read it as.** `GO` only when R1 fires and R2 passes. `NO_GO_PROMOTES_NOISE` is
the s2-B3 `sharp__phase_field_crystal_2d` case — the panel's LARGEST residual
spread (7.9e04) and a per-sample target normalisation that made it 4.2x worse.
`legacy_spread_statistic` is reported only to be dismissed: **spread is not the
decider, effective N is.**

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/persample_norm_eligibility.py \
    --datasets sharp__phase_field_crystal_2d,ext__helmholtz_2d \
    --out /path/elig.json [--target residual|field] [--r1_threshold 0.05] \
    [--noise_floor 1e-6] [--floor_q 0.25] [--modes_cap 12]
python tools/persample_norm_eligibility.py --datasets PANEL --out elig.json
```
`--target residual` (default) uses `y - copyLF(y)` — residual correctors (s2/s6);
`--target field` uses `y` itself — field regressors (s5/s7). ~10–60 s per 256^2
dataset on the login node.

**Verified.** Run 2026-07-31 on the 5 beyond-copy datasets
(`worktrees/s2_beyond_copy/B3/scratchpad/analyzer/t3_eligibility_tool_check.json`):
`ext__helmholtz_2d` **GO** (effective fraction 0.0031, min relative residual
4.97e-02), `sharp__phase_field_crystal_2d` **NO_GO_PROMOTES_NOISE** (0.3507,
1.21e-08), the other three `NO_GO_NO_NEED` (0.394 / 0.442 / 0.661) — 5/5 in the
direction of the measured 200-epoch outcomes (−88.2 % / +423 % / ±0.9–7.1 %).

**Provenance.** `worktrees/s2_beyond_copy/B3/scratchpad/reanalysis_turn_2.py` +
`reanalysis_turn_2b.py`; card `experiment_cards/s2_beyond_copy/batch_3/B3.json`
part 6, findings F5–F8 and F13 (the unified eligibility rule).

---

## `checkpoint_divergence_audit.py`

**Measures.** Is a "paired"/rebuilt control actually the same run? Weight-space
relative L2 between two checkpoints (complex-safe), the count of bit-identical
tensors, the five worst tensors, and — when the two result JSONs are supplied —
the scores they produced, on the round's `rel_l2_mean` convention.

**Read it as.** `BIT_IDENTICAL` -> the rebuild is faithful and training was
bit-reproducible; any score gap is eval-side and microscopic. `DIVERGED` -> the
two runs learned different functions and no code-diff story is needed (or
admissible). `_summary.divergence_is_dataset_specific` = true (some datasets
bit-identical, others not) is the signature of dataset-dependent training
nondeterminism rather than a build difference — on round 1 the split was by
WORKING GRID (256x256 bit-identical across nodes/jobs; 128x128 and 96x96 not).

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/checkpoint_divergence_audit.py --datasets PANEL \
    --ckpt_a '<OUT_A>/ckpt_{dataset}_e200_s0/last.pt' \
    --ckpt_b '<OUT_B>/ckpt_{dataset}_e200_s0/last.pt' \
    [--result_a '<OUT_A>/{dataset}_e200_s0.json'] \
    [--result_b '<OUT_B>/{dataset}_e200_s0.json'] \
    [--state_key model] [--split test_hf] [--metric_key rel_l2_mean] \
    --out /path/divergence.json
```
CPU, ~1 s per pair.

**Verified.** Run 2026-07-31 on s2_beyond_copy B2 (`lf_resid_fno`) vs B3-A0
(`global_ctrl`), 5 datasets
(`worktrees/s2_beyond_copy/B3/scratchpad/analyzer/t3_divergence_tool_check.json`):
pfc DIVERGED 0.0779 (1/39, score +5.222e-01), helmholtz DIVERGED 0.3189 (1/39,
+2.495e-01), allen_cahn / cahn_hilliard / fisher_kpp BIT_IDENTICAL 39/39 (score
deltas −1.9e-11 / −1.9e-11 / +1.5e-08) — reproducing the card's own continuity
gate exactly.

**Provenance.** `worktrees/s2_beyond_copy/B3/scratchpad/reanalysis_turn_1.py`;
card `experiment_cards/s2_beyond_copy/batch_3/B3.json` part 6, findings F2–F4.


---

## `stage_scaler_placement_forecast.py`

**Measures.** From the TRAIN split alone (no model, no GPU), for EVERY stage of a
multi-fidelity family (each fidelity's train rows is one stage) and every candidate
output-target scaler — `global_maxabs`, `global_zscore`, `per_sample_maxabs`,
`per_sample_zscore` (RevIN as published) and `per_sample_lf_proxy` (`max|LF_i|`, the
only per-sample statistic that is available at test time):

| key | meaning |
|---|---|
| `F_typical_placement` | `median_i(sd_i/s_i)` — where the TYPICAL sample's fluctuation sits inside the network's output range under this scaler. A global scaler places the AGGREGATE well and the typical sample badly whenever one field sets `sd(Y)` or `max|Y|` |
| `n_eff_target_energy` (+ fraction, `top1_energy_share`) | participation ratio of the per-sample MSE energies; forecasts the realized epoch-1 loss concentration |
| `proxy_fidelity.equalisation_delivered_vs_oracle` | what a cross-fidelity per-sample statistic actually buys, as a fraction of the true-scale oracle's repair |
| `dc_energy_share` + `CENTERING_RISK` | replacing a CENTERED global scaler by an UNCENTERED per-sample one costs the level channel on a DC-dominated target |
| `verdict.best_F_test_time_legal_scaler`, `F_gain_..._over_global_zscore`, `flags` | the recommendation and why |

**Read it as.** `NEED_PER_SAMPLE` (global `n_eff/N` < `--need_neff_frac`) → only a
per-SAMPLE denominator can fix the concentration; a global scalar divides every sample's
energy by the same constant. Then pick the largest `F` among test-time-legal scalers.
`PROXY_WEAK` → the LF statistic delivers < 50 % of the oracle's equalisation at this stage;
do NOT pre-register a threshold measured on the oracle. `CENTERING_RISK` → use
`per_sample_zscore`, not `per_sample_maxabs`. No flags and `F_gain ≈ 1` → the scaler is not
a lever here, and a per-sample arm will REGRESS if it also drops the centering (s5-B3's
ifc_poisson oracle: F ratio 0.155×, measured +83.8 % with the TRUE test scale).
Complements — does not replace — `tools/persample_norm_eligibility.py` (NEED / noise-floor
SAFETY / metric alignment, s2-B3) and `tools/target_range_placement_audit.py` (the global-only
`G` decomposition, s5-B2); gate all three on `tools/dc_pattern_split.py`, since a `LEVEL_ONLY`
dataset is inert under any affine scaler.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/stage_scaler_placement_forecast.py --datasets PANEL --out forecast.json
python tools/stage_scaler_placement_forecast.py \
    --datasets ext__helmholtz_2d,ifc_poisson --out forecast.json \
    [--split train] [--n_max 400] [--need_neff_frac 0.05] [--dc_risk 0.5]
```
Pure numpy on the login node, ~2–10 s per dataset.

**Verified.** Run 2026-07-31 from `round1/` on
`ext__helmholtz_2d,ifc_poisson,sharp__fisher_kpp_2d`: helmholtz `LF_pretrain`
**NEED_PER_SAMPLE**, best legal `per_sample_lf_proxy`, F gain **11.78×**, proxy equalisation
**1.00** (at that stage the LF statistic IS the target's own maxabs); helmholtz `HF_finetune`
**NEED_PER_SAMPLE,PROXY_WEAK**, F gain 35.99×, proxy equalisation **0.031**; `ifc_poisson`
every stage best legal `global_zscore`, F gain 1.000, no NEED (n_eff/N 0.69–0.77);
`sharp__fisher_kpp_2d` likewise. Those are exactly the stage where s5-B3's `revin_lf` arm
delivered −76.75 % on helmholtz, the stage whose pre-registered `n_eff ≥ 50` threshold was
unreachable (12.53/400), and the dataset whose true-scale ORACLE regressed.

**Provenance.** `worktrees/s5_tuning/B3/scratchpad/reanalysis_turn_{2,2b,2c}.py`; card
`experiment_cards/s5_tuning/batch_3/B3.json` part 6, findings F6–F9 and interpretation M3.


---

## `spectral_prestage_bc_audit.py`

**Measures.** Any MF stage of the form `C = irfft2(rfft2(LF) * T(k))` — a fitted LSI
defect filter, a Wiener transfer function, a spectral pre-stage — **silently imposes a
PERIODIC boundary condition**. This tool prices that choice before any GPU is spent,
training-free:

| key | meaning |
|---|---|
| `periodicity.verdict` / `wrap_ratio_max` | the model's own data-driven test `RMS(f[0]-f[-1]) / RMS(f[1]-f[0])` on the HF TRAIN split (re-derived from `s6_local-B2 periodicity.py`, cited not imported; no physics assumed, ADR 0009) |
| `branches.{periodic,mirror}.nrmse_prestage` | the SAME closed form fitted under a plain `rfft2` extension and under a MIRROR (even-symmetric ⇒ non-periodic) extension, gain selected by a held-out line search containing 0, scored via `round1/eval/nrmse.py` |
| `mirror_delta_pct` | what swapping the imposed BC is worth, in nRMSE, with zero gradient steps |
| `branches.*.resid_frac` | the `1 - rho_LSI` eligibility statistic: fraction of the fidelity-gap energy the pre-stage leaves on the table |
| `branches.*.ring_profile_resid_frac` | that fraction binned by distance-to-boundary, so a rim-localized failure is visible instead of averaged away |

**Read it as.** `mirror_delta_pct` strongly **negative** → the periodic pre-stage is
leaking at the rim; apply the pre-stage with the same extension the downstream
convolution uses. Strongly **positive** → the periodic BC was correct, do not "repair"
it. **≈ 0 with a large `resid_frac` under both** → the pre-stage's problem is genuine
fit quality, not the BC: gate the pre-stage off. s4-B3 F1 found
`Spearman(1-rho, pre-stage benefit) = +0.857` over 7 datasets with the sign separated
perfectly near `resid_frac ≈ 0.15`.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/spectral_prestage_bc_audit.py --dataset heat_local
python tools/spectral_prestage_bc_audit.py --dataset sharp__allen_cahn_2d \
    [--seed 0] [--holdout-frac 0.2] [--ridge 0.0] [--tol 1.25] [--n-probe 32] \
    [--out bc_audit.json]
```
Pure numpy on the login node, 2-D datasets only, ~5–60 s per dataset.

**Verified.** Run 2026-07-31 from `round1/`. `heat_local`: wrap ratios
**10.6358 / 16.5482** (reproducing `periodicity.py`'s pre-registered numbers) →
NON-PERIODIC; periodic pre-stage nRMSE 1.007874e-3, mirror **6.151774e-4**
(**−38.96 %**), `resid_frac` 0.19274 → **0.07444**, outermost-ring residual fraction
0.1328 → 0.0101. `sharp__phase_field_crystal_2d`: wrap ratios 1.0152 / 0.9908 →
PERIODIC; periodic 6.145764e-4, mirror 4.441501e-2 (**+7126.93 %**), `resid_frac`
0.00021 → 0.98400 — the two-sided control that shows the BC is a real decision, not a
free repair.

**Provenance.** `worktrees/s4_hybrid_routing/B3/scratchpad/reanalysis_turn_{1,2}.py`;
card `experiment_cards/s4_hybrid_routing/batch_3/B3.json` part 6, findings F5 / F7 / F8
and interpretation H2' / H5.


---

## `library_dominance_audit.py`

**Measures.** A discrete super learner / router / mixture-of-experts can only pay if
**no single member weakly dominates the rest**. Given each library member's scored
result JSON (`score_panel.py`'s `result_{panel,guard}_<arm>_s<seed>.json`, or any JSON
with `per_dataset.<ds>.{nRMSE, skill}`):

| key | meaning |
|---|---|
| `dominance` | for every ordered member pair, does A beat B on EVERY dataset at that dataset's certified relative floor (`state/noise_floor.json`), and on how many is it strictly better |
| `dominating_members` | members that weakly dominate the whole library — non-empty ⇒ routing is not licensed |
| `degenerate_ties` | datasets where two members are numerically IDENTICAL (a held-out gain line search containing 0 collapsing one member onto another). These masquerade as measurement ties in a rule table and must not be counted as "untestable cells" |
| `geomeans` / `oracle_geomean` / `routing_headroom_pct` | the panel geomean of every CONSTANT router ("always member m"), of the per-dataset oracle, and the prize a perfect selector would win over the best constant |
| `selector_vs_best_constant_pct` | with `--selector NAME`, what a SHIPPED selector actually realised over the best constant router |

**Read it as.** `routing_headroom_pct` inside the geomean floor ⇒ **the router is not
licensed**; the lever is what the members CONTAIN, not how they are mixed. Run this
BEFORE building a selector, and run it AGAIN after any change to a member's training
target — s4-B3 changed one member into `other_member + gated_correction` (a strict
superset) in the same card that built the router, and the headroom went from **+6.020 %**
to **+0.000 %** without anyone noticing until the mechanism turn.

Complements `routing_headroom.py` (s4-B1, the ceiling of a richer gate WITHIN one
`base + alpha*correction` model) and `persample_gate_audit.py` (s6-B2, what a shipped
per-sample gate realised); this tool works one level up, between whole arms.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/library_dominance_audit.py \
    --arm lsi=$OUT/result_panel_lsi_alone_s0.json \
    --arm dc=$OUT/result_panel_dc_cleaned_s0.json \
    --arm shipped=$OUT/result_panel_router_s0.json --selector shipped \
    [--floors state/noise_floor.json] [--default-floor 0.0] [--out dom.json]
```
Pure JSON parsing, < 1 s.

**Verified.** Run 2026-07-31 from `round1/` on s4-B3's own outputs. CLEANED library
(`lsi_alone`, `dc_cleaned`, selector `router`): `dc_cleaned` weakly dominates
(strictly better on 3/6), degenerate ties on `ext__helmholtz_2d` and
`sharp__cahn_hilliard`, always_lsi 0.197217 / always_dc 0.123308 / oracle 0.123308,
`routing_headroom_pct` **+0.000 %**, verdict **NOT LICENSED**. RAW library
(`lsi_alone`, `dc_raw`): neither dominates, always_dc 0.192577 vs oracle 0.181642,
`routing_headroom_pct` **+6.020 %**, verdict **LICENSED** — the two-sided control.

**Provenance.** `worktrees/s4_hybrid_routing/B3/scratchpad/reanalysis_turn_3.py`; card
`experiment_cards/s4_hybrid_routing/batch_3/B3.json` part 6, findings F10 / F11 and
interpretation H6.

## `aggregate_seed_confirm.py` — end-of-round top-3 seed-confirm aggregation (added 2026-08-01)

Parses the per-seed eval artifacts in `mffp_autoresearch_outputs/round1/` for the top-3
slate (s4-B3 diags, s6-B2 diags, s1-B3 result JSONs), re-derives seed 0 and requires
exact (1e-9) agreement with the cards before trusting seeds 1–2, then writes
`state/seed_confirm_2026-08-01.json` with per-arm 3-seed panel-geomean stats
(mean, sd, min/max, t-based 95% CI, df=2) plus per-seed gate outcomes.
`--update-cards` folds the stats into the three cards' part 5 (`seed_confirm` block;
`mean`/`ci95` promoted to 3-seed only where every check passed).

**Provenance.** `round1_report.md` §8 step 2; seed-confirm jobs 66165252–57.
