> **Round-2 seed note (2026-07-31):** this library was seeded verbatim from
> `../round1/tools/` at round-2 launch. The probes were written against the
> ROUND-1 eval layer (defective copy-LF reference, round1 paths); in
> particular `registration_audit.py`'s variant-A seam guard asserts the OLD
> frozen baseline and will refuse to run against round-2's corrected
> `panel_data.py`. Adapt on use; promote adapted versions via the
> mechanism-analyzer register turn. New round-2 entries append below the
> round-1 block as usual.

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
| `condition_predictability_ceiling.py` | ROUND-2: how much of a dataset's HF field the CONDITION VECTOR determines at all — a training-free aleatoric ceiling in skill units (noise-debiased LOO k-NN upper bound + matched-pair `d->0` extrapolation), with an explicit `no_support` verdict | r2s4_diag-B1 turn 2 |
| `conditional_mean_collapse.py` | ROUND-2: has a condition->field model collapsed to a constant field, and is its condition-driven variation worth its amplitude? own-mean-broadcast arm, fluctuation energy/alignment, shrinkage oracle, per-sample tail attribution, seed same-function test | r2s4_diag-B1 turns 1+3 |
| `band_gain_counterfactual.py` | ROUND-2: is an arm-vs-arm advantage just BAND CALIBRATION? one scalar per radial Fourier band fitted out of fold on a train-side calibration fold, applied to the losing arm's test prediction and re-scored (optionally with the floor blend re-selected), plus `frac_of_gap_closed` against a reference arm. Complements `band_weight_counterfactual.py` (which LOCATES a gap; this one decides whether it SURVIVES recalibration) | r2s1_direct-B1 turn 3 |
| `condition_identifiable_rank.py` | ROUND-2: how many degrees of freedom of the HF field the CONDITION VECTOR determines — per-POD-mode out-of-fold R^2 (identifiable rank), condition-predictable variance fraction and implied floor, a scoreable closed-form rank-r arm vs the ORACLE rank-r truncation (COEFFICIENT_UNIDENTIFIABLE vs BASIS_INADEQUATE verdict), the condition-predicted DC-only arm, the additive-field/centering trap, and a bimodal pattern-gate AUC | r2s1_direct-B1 turns 1+3 |
| `affine_ladder_voi.py` | ROUND-2: training-free value-of-LF certificate in CONDITION-side coordinates — how affine the task is per rung (exact-LOO), how many affine directions the few HF TRAIN rows cannot determine and what share of the true law lives there, the resulting HF-only information limit (min-norm pinv), what each LF rung + one HF-row scalar + an HF-row residual actually scores, and whether the LF rungs recover the unidentifiable direction. Complements `condition_identifiable_rank.py` (field-basis coordinates, no LF rungs) | r2s3_lf_train_signal-B1 turns 2+3 |
| `posthoc_repair_ladder.py` | ROUND-2: how much of a trained arm's error is LEGITIMATELY repairable without retraining — a 5-rung ladder (raw / global scale / radial low-pass / affine residual / low-pass+residual, every choice fitted on the HF TRAIN rows, each with its ORACLE twin) plus optional network AFFINE-ISATION: non-affinity remainder on a random condition design, the arm's implicit law vs the ORACLE law, the null-direction cos/gain, and ORACLE row-space-vs-null coefficient surgery | r2s3_lf_train_signal-B1 turn 3 |
| `reachable_set_rank_audit.py` | ROUND-2: how many dimensions a TRAINED MODEL'S OUTPUT FAMILY spans (on real AND synthetic conditions), against the truth's rank and against the condition-learnable rank on the same split — plus the per-band fixed-pattern test, dictionary-vs-coefficient ORACLE projections, and the nearest-condition-neighbour band continuity that separates a STRUCTURAL ceiling from a LEARNING gap. Third axis of the identifiability triad with `condition_identifiable_rank.py` (field basis) and `affine_ladder_voi.py` (condition-side design) | r2s2_stacked-B1 turn 2 |
| `surrogate_coherence_eligibility.py` | ROUND-2: is a stage-1 surrogate field worth feeding to a downstream corrector at all? per-band energy-weighted coherence with the target + the IN-SAMPLE ORACLE Wiener ceiling (an upper bound on ANY spatially-invariant linear stage) converted to skill units, with an ELIGIBLE / FUTILE / UNDETERMINED verdict on the r2s2-B1-measured gamma_band1 thresholds | r2s2_stacked-B1 turn 3 |
| `ladder_pair_alignment_audit.py` | ROUND-2: are the fidelity rungs PAIRED BY CONDITION or only by ROW INDEX? training-free pre-flight for every `lf = lf[:n_hf]` construction (copy-LF reference, aux LF target, LF teacher input, residual target): paired-vs-nearest condition distance, fraction of rows paired to their nearest, and the disjoint-condition SUPPLY count the truncation discards; `--fail-on` makes it a build gate | r2s4_diag-B2 turn 2 |
| `shrinkage_curve_anatomy.py` | ROUND-2: decomposes any shipped shrinkage curve into its LEVEL (own-mean broadcast) and its FLUCTUATION (condition response: amplitude, effective alignment, λ_opt), and reports whether an arm contrast SIGN-FLIPS between the two — schema-free curve discovery, works on any card that ships `grid` + `*_curve` | r2s4_diag-B2 turns 2-3 |
| `condition_predictability_ceiling_fast.py` | ROUND-2: `condition_predictability_ceiling.py` with a float32 / capped-pair estimator path (imports the frozen tool unmodified; same schema), plus a `--validate` mode that runs BOTH paths and prints the difference. Use when the exact path will not finish inside a turn budget | r2s4_diag-B2 turn 1 |
| `null_family_ceiling_audit.py` | ROUND-2: where does a shipped arm's error live relative to what its HF training rows could constrain? the m-generalised ORACLE ceiling over the NULL family of affine functionals that vanish at every training condition, the complementary ROW family and the full affine family, each with a mandatory RANDOM m-dim subspace control (`null_over_random`), plus the implicit-law null-block amplitude/cosine and an optional LEVEL channel — the three-channel decomposition of an arm-vs-arm gap | r2s3_lf_train_signal-B2 turn 3 |
| `design_coverage_audit.py` | ROUND-2: does this LF pool ADD DESIGN ROWS or only replicate the HF conditions? per rung, rank / null dimension / singular values of `[X,1]` for the HF training rows, the PAIRED pool, the FULL pool and their union, covered-vs-uncovered condition counts, `m_reduction_paired` vs `m_reduction_full`, and (`--fields`) the lifted-LF-vs-HF discrepancy at the covered conditions that decides whether a paired LF target is CONTRADICTORY | r2s3_lf_train_signal-B2 turn 3 |
| `blend_decorrelation_payoff.py` | ROUND-2: what a post-hoc floor-BLEND stage actually pays and WHICH ARM CLASS it pays — fits the one free parameter ρ (arm-vs-base error correlation) of the two-member ensemble model to each shipped calibration λ-surface, with the fit residual, the test-side implied ρ, per-cell `COLLINEAR_WITH_BASE` / `BASE_DOMINATED` verdicts, and an equal-ρ counterfactual between two arms. Decomposes the blend PAYOFF by decorrelation, where `shrinkage_curve_anatomy.py` decomposes a shrinkage curve into level vs fluctuation | r2s1_direct-B2 turn 3 |
| `selection_set_vs_window_audit.py` | ROUND-2: does a training-free selection rule fit the SET its own diagnostic identifies, or only that set's CARDINALITY (the leading window)? reconstructs `{i: stat_i > tau}` vs `{0..r_sel-1}` from the shipped selection diagnostics, prices the mismatch in the rule's own statistic (and optionally in basis energy), and raises `FORM_MISMATCH` when the statistic was measured on a different basis/centering form than the one fitted | r2s1_direct-B2 turn 1 |
| `zero_gradient_stage_ladder.py` | ROUND-2: how much of a TRAINED stack's test-side value is reachable with ZERO gradient steps — an out-of-fold stage ladder (raw intermediate / global gain / closed-form LSI Wiener / two blend rungs / free joint `(k, base, lam)`) read on TEST against the shipped trained arm, ATTRIBUTING the scored gain to {closed-form, gradient, blend} in percent and in skill units vs the certified mce, plus per-rung geometry (cosine / amplitude / structure-only error) and the fitted transfer's dyadic band gains. Seam-checks the shipped calib k-sweep, the frozen floors and `nrmse_after_lsi` rather than assuming them | r2s2_stacked-B2 turn 3 |
| `relative_gain_units_audit.py` | ROUND-2: can a DIMENSIONLESS eligibility threshold ("if the available value-add is below X %, don't build the stage") be stated in this benchmark's claim units? prices the threshold, the realised gain and the cost of OBEYING the rule in skill units and in certified `min_claimable_effect`, with panel verdicts `EXPRESSIBLE` / `COARSE` / `PANEL_INCONSISTENT` / `MISCALIBRATED`. Run it on any rule BEFORE exporting it as a gate | r2s2_stacked-B2 turn 3 |
| `effect_threshold_readings.py` | ROUND-2: is a paired A-vs-B effect measured over REPEATED SPLITS claimable, and does the verdict depend on how the threshold is read? separates the TEST-SAMPLE variance component (paired per-sample bootstrap) from the SPLIT variance component (range, range-derived sd/SE via the control-chart `d2`, log-units), then recounts the verdict under 7 threshold readings and reports `readings_agree` plus `mce_over_observed_split_range` (a provenance smell when « 1). Run it on any falsification clause whose threshold mixes a certified constant with an in-job spread | r2s3_lf_train_signal-B3 turn 1 |
| `map_dispersion_scale_shape.py` | ROUND-2: across repeated training splits, does an arm's learned MAP change or only its SCALE? per split-pair inter-prediction dispersion split into total vs shape-only (`min_a ‖a·p_d − p_d'‖`, i.e. what survives the best per-sample rescale), in `‖y‖` and skill units; plus each split's score at the ORACLE per-sample gain (how much of a score AND of its split-range is the amplitude channel alone) and the split-ENSEMBLE arm as a deliberately non-budget-matched upper bound on any variance-only explanation | r2s3_lf_train_signal-B3 turns 2-3 |
| `hf_row_shapley_value.py` | ROUND-2: what is each TRAINING ROW worth? exact closed-form Shapley over an EXHAUSTIVE `C(m,n)` subset dump (no sampling), per replicate and on the mean, with the marginal-value profile by coalition size (complement vs passenger), every leave-one-out design, the per-TEST-SAMPLE Shapley localised on the nearest-condition-neighbour partition (`concentration_ratio` = does the row buy COVERAGE?), the interference test, an optional amplitude/structure channel split of row value, and the decisive `coverage_spearman` of every descriptive row statistic against measured value | r2s4_diag-B4 turns 2-3 |
| `gain_channel_ladder.py` | ROUND-2: is an arm's headroom a PER-SAMPLE SCALE, and does it move along the design axis? the exact amplitude/structure split and the global-vs-per-sample oracle-gain ladder read across a whole sweep (N_train / width / seed), plus the across-test-row dispersion ratio, the TREND of both against the axis, and the matched-axis two-group CONTRAST split by channel. The ladder form of `field_error_decomposition.py` / `gain_calibration_ceiling.py` (which price ONE arm) | r2s4_diag-B4 turn 3 |

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
| `ledger_contamination_audit.py` | ROUND-2: could this A-vs-B reading have fired at all, and is it measuring what the card thinks? the identical triangle-inequality ceiling `D(arm, baseline)` on \|skill difference\| with a `COULD_NOT_FIRE` flag when it sits below the clause threshold, plus (with a `--control` column) the FUNCTION-CLASS vs TARGET decomposition that separates "is this estimator better" from "did the treatment's target buy anything", plus (`--matched`) the row-count bias when the arms were fitted on different numbers of rows | r2s4_diag-B3 turns 1-2 |
| `band_retention_probe.py` | ROUND-2: what part of the spectrum a predictor actually PRODUCES — per radial band the truth's energy share, the arm's retained energy ratio, and the decisive `band_relative_error` (**1.00 = the arm contributes exactly zero useful energy in that band**), with a `contributes_nothing_above_lowest_band` verdict and (`--advantage A:B`) the per-band localisation of an arm-vs-arm gap | r2s4_diag-B3 turn 3 |
| `gain_head_feasibility_audit.py` | ROUND-2: can a post-hoc per-sample GAIN head be fitted here at all, and is a reported gain CEILING real condition learning or just the head's own clip? the fit rows' calibration-label spread against the eval rows' (**a head fitted on rows the arm interpolated is the identity BY CONSTRUCTION**), the train-fitted head's out-of-fit R² against the true gain, a labelled-holdout learning curve that prices what real labels would buy, and the LOO-on-eval ceiling scored next to TWO zero-information nulls (constant gain at the clip bound, best constant) | r2s3_lf_train_signal-B4 turns 1-2 |
| `effect_concentration_audit.py` | ROUND-2: is a paired A-vs-B effect BROAD-BASED or carried by a handful of test samples, and how much of it survives perfect per-sample amplitude calibration? per-sample effect distribution (median vs mean, win rate, exact sign test), concentration (top-1/5/10 % share of the positive effect, samples-to-halve), the ADVERSARIAL TRIM (effect after deleting the most favourable 5/10 %, judged against the certified mce), and the `E_struct`/`E_amp` split with the per-arm cosine / norm-ratio / fluctuation anatomy | r2s3_lf_train_signal-B4 turns 2-3 |

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

---

## `condition_predictability_ceiling.py`  *(round 2)*

**Measures.** Training-free, TRAIN-split only: how much of the HF field the
condition vector determines at all, i.e. the aleatoric barrier a condition->HF
model cannot cross — with or without LF as a training signal. Two independent
estimators, both reported in the round's per-sample rel-L2 form and in copy-LF
skill units: (1) `loo_knn` — `E||y_i - m_k(i)||^2 = S(1+1/k) + B(k)` so
`S_hat = min_k R(k)/(1+1/k)` is an UPPER bound on the aleatoric energy;
(2) `pair` — bin all train pairs by condition distance `d`, fit the two lowest
bins and extrapolate to `d = 0`. Optional `--preds` places a model against the
ceiling (`over_knn_bound`, `over_pair_bound`).

**Read it as.** `over_knn_bound ~ 1` -> the predictor is AT the barrier; its
residual error is information the condition does not carry and no lever can
recover it (a null result there is uninformative, not a failure).
`over_knn_bound >> 1` -> real headroom. `support.verdict == "no_support"` ->
the nearest train pair is far or there are too few train samples, BOTH estimators
are extrapolations and no aleatoric claim may be made. A predictor scoring BELOW
the k-NN bound only means the bound is loose there.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/condition_predictability_ceiling.py --datasets PANEL --out ceiling.json
python tools/condition_predictability_ceiling.py \
    --datasets sharp__fisher_kpp_2d \
    --preds sharp__fisher_kpp_2d=/path/preds_s0.npy --out ceiling.json
```
Pure numpy on the login node; ~1-4 min per 256^2 dataset (memory-safe: the naive
`(n,k,D)` neighbour tensor is 26 GB at 256^2 and was OOM-killed in the source
probe before the running-mean rewrite). Defaults to the STRIPPED view.

**Verified.** Run 2026-07-31 from `round2/` on `ext__helmholtz_2d,ifc_poisson`
with the r2s4-B1 certifier's seed-0 predictions -> helmholtz knn ceiling
**3.7287** (k=1), pair ceiling **2.6383**, `support=supported`, prediction skill
6.1725 = **x1.655** the knn bound; ifc_poisson knn 4.8946, pair `n/a`,
`support=no_support` (5 train samples). Identical to the source probe.

**Provenance.** `worktrees/r2s4_diag/B1/scratchpad/reanalysis_turn_2.py`; card
`experiment_cards/r2s4_diag/batch_1/B1.json` part 6, findings T2-F1 - T2-F6.

---

## `conditional_mean_collapse.py`  *(round 2)*

**Measures.** For one or more prediction files per dataset (`.npy`,
`(n_test, n_cells)` in loader order): the model's skill next to
**its own mean field broadcast to every test sample** (the model with its
condition-dependence surgically removed - the decisive, metric-consistent
collapse test, scored through `round2/eval/nrmse.py`); the pooled fluctuation
energy ratio `R` and alignment `A` with `useful = 2A*sqrt(R) - R`; a
**TEST-FITTED, labelled** shrinkage oracle `Pbar + lambda*(P - Pbar)` with its
`lambda*`; per-sample rel-L2 quantiles, cosine(pred, hf), amplitude ratio, the
Spearman rho of the error against `||hf||` / the amplitude ratio / the distance
to the nearest TRAIN condition, and the count of samples with per-sample skill
< 1; and, with >= 2 files, the pairwise seed/arm agreement (relative distance,
fluctuation cosine, worst-10 overlap) that separates "same function" from
"same score".

**Read it as.** `skill ~ skill_of_own_mean_field_broadcast` with `R << 1` ->
COLLAPSED (check `condition_predictability_ceiling.py` before calling it a
failure - on `sharp__fisher_kpp_2d` the collapse is the correct answer).
`useful < 0`, `lambda* ~ 0`, low per-sample cosine -> the model is a noise
generator whose only contribution to the error is its own amplitude, and
post-hoc shrinkage calibrated on a held-out TRAIN fold is a mandatory guardrail.
Seed-pair `fluct_cosine ~ 1` -> a small certified seed spread is reproducibility
of ONE solution, not resolving power.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/conditional_mean_collapse.py \
    --preds "sharp__fisher_kpp_2d=/path/s0.npy:/path/s1.npy:/path/s2.npy" \
    --preds "ext__helmholtz_2d=/path/s0.npy" --out collapse.json
```
Pure numpy on the login node; seconds to ~1 min per dataset.

**Verified.** Run 2026-07-31 from `round2/` on the r2s4-B1 certifier's cached
predictions -> `sharp__fisher_kpp_2d` skill 11.5585 / own-mean **11.9810** /
R 0.0590 / A 0.2521 / lambda* 1.0 (all three seeds within 1e-3), and
`ext__helmholtz_2d` skill 6.1725 / own-mean **3.5214** / R 0.0304 / A 0.0451 /
useful **-0.0147** / lambda* **0.0**. Identical to the source probes.

**Provenance.** `worktrees/r2s4_diag/B1/scratchpad/reanalysis_turn_{1,3}.py`;
card `experiment_cards/r2s4_diag/batch_1/B1.json` part 6, findings T1-F1 - T1-F5
and T3-F1 - T3-F5.

---

## `band_gain_counterfactual.py`  *(round 2)*

**Measures.** Whether an arm-vs-arm advantage is REPRESENTATION or merely
per-band amplitude CALIBRATION. Fits one scalar gain per radial Fourier band by
coordinate descent on a TRAIN-side calibration fold (`--fold_seed/--model_frac/
--blend_frac` reproduce the round-2 `common.make_folds` split, or pass
`--cal_idx`), applies the gains to the arm's test prediction, optionally
re-selects the floor blend `(base, lambda)` over {zero, train_mean,
nn_condition} on the same fold, and re-scores through `round2/eval/nrmse.py`.
With `--ref_test` it reports the A-vs-B gap before and after and
`frac_of_gap_closed`. Also prints each band's share of the TEST HF energy (the
most a band can ever be worth). `--fit_on test` is an explicitly labelled
ORACLE mode and its numbers may never enter a card as an arm score.

**Not the same tool as `band_weight_counterfactual.py`** (round 1, s3_warp-B2),
which attributes an EXISTING gap to bands by swapping arm A's per-band error for
arm B's. Use that one to locate a gap, this one to decide whether the gap
survives letting the losing arm rescale its own bands out of fold. No shared
code; either order works.

**Read it as.** `frac_of_gap_closed >= ~0.9` -> the difference was calibration,
and any capacity/architecture claim must be re-made against the calibrated
competitor. Near-uniform gains `< 1` -> a pure global amplitude shrink (the arm
is mis-scaled, not mis-structured). All non-DC gains driven to 0 -> the only
scoreable content is the spatial mean (go to `condition_identifiable_rank.py` /
`dc_pattern_split.py`). Non-monotone gains including a value `> 1` -> the arm
genuinely under-predicts a band; the one signature that does not reduce to
shrinkage.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/band_gain_counterfactual.py \
    --dataset sharp__phase_field_crystal_2d \
    --pred_train tiny_train.npy --pred_test tiny_test.npy \
    --ref_test decoder_test.npy --blend --out bandgain_pfc.json
# 256^2 / large calibration folds: trade calibration quality for wall time
python tools/band_gain_counterfactual.py --dataset sharp__cahn_hilliard \
    --pred_train t_tr.npz:pred --pred_test t_te.npz:pred \
    --gains 11 --passes 1 --max_cal 200 --blend --out bandgain_ch.json
```
Pure numpy on the login node. The calibration set is Fourier-decomposed into
per-band components ONCE, so a coordinate-descent trial is a weighted sum and
not an FFT: the full 31-gain x 2-pass grid runs in **9.3 s** on a 128^2 dataset
and **75.5 s** on 256^2 `sharp__cahn_hilliard`, where the FFT-in-the-loop source
probe blew the 20-minute script cap and had to fall back to 11 gains x 1 pass.
Memory is `n_bands x n_cal x n_cells x 8 B` (1.3 GB at 256^2 x 400) — use
`--max_cal`.

**Verified.** Run 2026-07-31 from `round2/` against the r2s1-B1 arms
(predictions dumped by `worktrees/r2s1_direct/B1/scratchpad/register_dump_preds.py`;
outputs kept at `.../scratchpad/register_toolcheck_bandgain_*.json`):
`sharp__phase_field_crystal_2d` gains **[1.0, 0, 0, 0.05, 0, 1.0]**, tiny head
0.41455 raw / 0.41051 blended -> **0.38425** calibrated+blended against the
shipped decoder's 0.38396 raw, `frac_of_gap_closed` **0.989** — identical to
turn-3 F8 (0.38425). `sharp__cahn_hilliard` at the FULL grid (which turn 3 could
not afford): gains [0, 0.9, 0, 1.5, 0.25, 0], 0.58195 raw -> **0.55990**
calibrated+blended vs the shipped 0.53686, only **12.1 %** of the gap closed —
tightening turn-3 F8's coarse-grid upper bound 0.56297 and leaving the decoder a
**+4.3 %** advantage there.

**Provenance.** `worktrees/r2s1_direct/B1/scratchpad/turn3_followup.py`; card
`experiment_cards/r2s1_direct/batch_1/B1.json` part 6, findings T3-F3, T3-F4,
T3-F8.

---

## `condition_identifiable_rank.py`  *(round 2)*

**Measures.** For a condition->HF task, training-free and TRAIN-split only
(except two rows explicitly suffixed `ORACLE`): the per-POD-mode out-of-fold
R^2 of the coefficient predicted from the condition (bias + standardized
condition + `--cond_rff` random Fourier features, ridge with K-fold alpha), the
identifiable rank (`n_r2_gt_0.10/0.50`), the condition-predictable share of the
centered field variance and the `implied_floor_nrmse` of ANY
`mean_field + f(cond).V` model; a rank sweep giving both a SCOREABLE closed-form
rank-r arm and the ORACLE rank-r truncation of the test fields; the DC anatomy
(HF DC energy share, DC oracle, out-of-fold R^2 of the per-sample spatial mean,
and the condition-predicted DC-ONLY arm with its parameter count); the centering
diagnostic `||mean field|| / geometric-mean ||y||` with both constant
predictors; and (2-D) an auto-detected dominant ring, the bimodality of its
energy share and the out-of-fold AUC of predicting "has the pattern nucleated?"
from the condition, with the DC arm scored per class.

**Read it as.** `verdict = COEFFICIENT_UNIDENTIFIABLE` (ORACLE at `--ref_rank`
under 0.25x the arm, <= 5 identifiable modes) -> the model is
INFORMATION-limited: the basis holds the answer, the condition cannot select the
coefficients, and decoder capacity buys nothing. `BASIS_INADEQUATE` (ORACLE >=
0.8x the arm) -> genuinely high-rank fields; representation is the lever.
`ratio_meanfield_over_geoamp >> 1` -> a fixed ADDITIVE field is a trap under the
per-sample relative metric and a (unit direction x amplitude) factorization is
free money; `<< 1` -> the fields cancel in the mean and factorizing costs you.
`gate.oof_auc ~ 1` with a bimodal ring share -> two problems in one dataset;
score per class before believing a pooled number. Complements
`condition_predictability_ceiling.py` (how much energy is unexplainable) and
`dc_pattern_split.py` (level vs pattern, oracle only).

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/condition_identifiable_rank.py \
    --datasets sharp__phase_field_crystal_2d,sharp__allen_cahn_2d \
    --arm_nrmse "sharp__phase_field_crystal_2d=0.38403,sharp__allen_cahn_2d=0.43527" \
    --out identrank.json
python tools/condition_identifiable_rank.py --datasets ifc_poisson \
    --ranks 1,2,3,4 --max_modes 50 --no_gate --out ip.json   # small-N / cheap
```
Pure numpy on the login node; 5-30 s per panel dataset (dominated by the SVD and
the rank sweep — trim `--ranks` / `--max_modes`). Defaults to the STRIPPED view
and asserts the test split carries no LF fidelity.

**Verified.** Run 2026-07-31 from `round2/` (outputs kept at
`worktrees/r2s1_direct/B1/scratchpad/register_toolcheck_identrank_*.json`):
`sharp__phase_field_crystal_2d` identifiable rank **2**, predictable variance
**0.0536**, rank-50 arm **0.41422** vs ORACLE-50 **0.02844**, DC share 0.7225,
DC out-of-fold R^2 **0.99972**, DC-only arm **0.35017**, dominant ring k=**5**,
patterned fraction 0.375, gate AUC 0.9992 (RFF) / 0.9997 (linear), per-class DC
arm 0.78830 patterned / 0.00593 unpatterned, verdict
**COEFFICIENT_UNIDENTIFIABLE**; `sharp__allen_cahn_2d` rank **1**, predictable
variance **0.9604**, rank-1 arm **0.34086**, rank-50 arm **0.34752**, ORACLE-50
**0.20505**, verdict MIXED; `ifc_poisson` (5 train samples) rank 1, predictable
variance **0.4654**. Every one of these matches the source probes (turn-1 F2/F3/
F5 and turn-3 F6/F7) to the digits reported there; the `centering` block is
computed on the FULL train split where turn-2 F5 used the fitting fold, so those
numbers agree qualitatively but not to the digit.

**Provenance.** `worktrees/r2s1_direct/B1/scratchpad/reanalysis_turn_1.py` and
`.../turn3_followup_b.py`; card `experiment_cards/r2s1_direct/batch_1/B1.json`
part 6, findings T1-F2, T1-F4, T1-F5, T2-F5, T3-F5, T3-F6, T3-F7.

---

## `affine_ladder_voi.py`  *(round 2)*

**Measures.** Training-free, for a condition->HF task with a fidelity ladder, in
the round's own metric: (A1) how AFFINE the map cond->field is at every rung and
on the test rows (exact-LOO ridge over an alpha grid; the test-fitted entry is
suffixed `_ORACLE` and is a benchmark characterisation, never a score);
(A2) the numerical RANK and NULL SPACE of the HF-training design `[X_hf, 1]`,
the singular values, and the fraction of the true law's coefficient energy that
lives in the unidentifiable directions; (A3) HF-only controls including the
**min-norm pinv** fit — with a rank-deficient design this is the exact
INFORMATION LIMIT and it equals A2's row-space projection of the true law;
(A4) each LF rung's affine law transferred to the HF grid with a single scale
fitted on the HF TRAIN rows, next to the scale the grid-ratio-squared amplitude
convention predicts, plus a joint all-rungs fit; (A5) the certificate —
rung-affine base + an affine residual correction on the HF train rows with the
ridge alpha chosen by exact LOO over those rows, full sweep reported;
(A6) per-coefficient cosines against the ORACLE law and the **null-direction
recovery ratio** of each rung; (A7) exact condition-overlap counts between test,
HF train and every LF rung, so a "disjoint conditions" claim is verified.
`verdict.value_of_lf_skill_units` = information limit minus the best legitimate
LF-assisted estimator.

**Not the same tool as `condition_identifiable_rank.py`** (r2s1-B1). That one
works in FIELD-basis coordinates on the train split — per-POD-mode out-of-fold
R^2 of the coefficient predicted from the condition — and has no LF rungs in it.
This one works in CONDITION-side coordinates: whether the few HF rows SPAN the
design at all, and what the LF rows at other conditions are worth as the fix.
A dataset can be `COEFFICIENT_UNIDENTIFIABLE` there and full-rank here, or the
reverse. Run both; they answer different halves of "is this information-limited?".

**Read it as.** `label = RANK_LIMITED_LF_COMPLETES` -> no HF-only estimator of
ANY capacity can beat `hf_only_information_limit_skill`, and the LF rows demonstrably
close the gap: the next batch's job is to build a family that reaches the
`best_lf_assisted_skill_LEGIT` number, and that number is the honest baseline to
beat, not the previous network. `affine_task = true` (A1 test LOO << 1e-3) ->
the benchmark is a closed-form linear map and any skill claim on it measures
RANK RECOVERY, not operator learning — flag it for the round report.
`c_legit_over_grid_ratio_squared` far from 1 -> the ladder carries a
mesh-dependent amplitude convention; a single shared output scaler across rungs
will deflate the HF-row loss by its square (see `ladder_level_diagnostic.py`).
A6 `null_direction_recovery_ratio` ~ 1 with cos ~ 1 -> that rung transfers the
unidentifiable direction faithfully across the resolution gap.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/affine_ladder_voi.py --datasets ifc_poisson --out voi_ifc.json
# cheap affinity scan only (no rank/ladder work), several datasets:
python tools/affine_ladder_voi.py \
    --datasets ext__helmholtz_2d,sharp__allen_cahn_2d \
    --affinity_only --quadratic --out panel_affinity.json
```
Pure numpy (torch only for the bilinear rung upsample) on the login node.
Defaults to the STRIPPED view. 60 s on `ifc_poisson` (64^2, 175 train rows);
76-566 s per sharp/ext dataset in `--affinity_only --quadratic` mode, dominated
by the 8-alpha exact-LOO over 65536-dim fields — trim with `--max_test`.

**Verified.** Run 2026-07-31 from `round2/` (outputs kept at
`worktrees/r2s3_lf_train_signal/B1/scratchpad/register_toolcheck_voi_*.json`):
`ifc_poisson` affine LOO **3.208e-08 / 3.389e-08 / 4.165e-08** (rungs 8/16/32)
and **3.222e-08** on test; design rank **5/6**, null-direction energy share
**0.18828**; min-norm information limit skill **3.47440** = the analytic
row-space projection **3.47440**; rung affine + HF-row scale **5.0072 / 2.3418 /
0.8863**, joint **3.7601**; rung + residual **1.3543 / 0.6382 / 0.24269**;
null-direction recovery **0.940 / 0.982 / 0.9957** at cos **0.979 / 0.995 /
0.9993**; all condition-overlap counts 0; verdict `RANK_LIMITED_LF_COMPLETES`,
value of LF **+3.2317** skill units. Every one of these matches the source probe
(turn-2 B1/B3/B4/B5/B7/B8/B9) to the digits reported there.
Affinity scan: `sharp__allen_cahn_2d` **0.31714** affine / **0.26845** quadratic
and `sharp__fisher_kpp_2d` **0.25074** / **0.25214** match the source probe
exactly; `ext__helmholtz_2d` **2.3141** and `sharp__phase_field_crystal_2d`
**0.4033** are LOWER than the source's 2.5644 / 0.40453 because this tool's
alpha grid extends to 1.0 while `reanalysis_turn_2c.py` capped it at 1e-2 (the
selected alphas here are 1.0 and 0.1) — a better-regularised fit of the same
quantity; the conclusion is unchanged, `ifc_poisson` is seven orders of
magnitude away from every other panel dataset.

**Provenance.** `worktrees/r2s3_lf_train_signal/B1/scratchpad/reanalysis_turn_2.py`
(part B), `.../reanalysis_turn_2c.py`, `.../reanalysis_turn_3b.py`; card
`experiment_cards/r2s3_lf_train_signal/batch_1/B1.json` part 6, findings 6-9
and interpretations M8/M11.

---

## `posthoc_repair_ladder.py`  *(round 2)*

**Measures.** For a shipped arm (predictions only — no checkpoint surgery, no
retraining), how much of its error a next batch could remove by construction.
Five rungs, each fitted on the HF TRAINING rows only and each with an explicitly
labelled `_ORACLE` twin: **L0** raw; **L1** one global scale; **L2** an ideal
radial low-pass with the cutoff selected on the train rows (the target's own
truncation ceiling is reported per cutoff, so "the filter helped" can be told
from "the filter cannot possibly help more than this"); **L3** an affine residual
correction with the ridge alpha chosen by exact LOO over the train rows, full
sweep; **L4** L2 then L3. Reports `best_legitimate_repair` and its gain in skill
units.

With `--cond_probe/--pred_probe` it adds the **affine-isation** block: evaluate
the net at a random condition design (emit it with `--gen_probe_conds`; no field
data is read to build it), fit its own affine surrogate on a fraction of the
design and report the NON-AFFINITY remainder on the rest, the surrogate's law
against the ORACLE law per coefficient, the **null-direction** diagnostic
(fraction of the arm's law energy in the directions the HF train rows cannot
constrain, cosine and recovery ratio against the truth), and ORACLE
row-space-vs-null coefficient **surgery** (arm row + oracle null, oracle row +
arm null, …) which says whether the arm is wrong where it could have known or
where it could not.

**Read it as.** A big L1 gain -> the arm is mis-scaled, not mis-structured. A big
**L1 ORACLE-vs-LEGIT gap** is the important pathology: the miscalibration is
invisible from the training rows, so no early-stopping rule, trust gate or
calibration fitted on them can catch it (r2s3-B1 found a 647-skill arm whose
legitimate 5-row scale was 0.956 while the box-wide one was ~1/30). An L2 gain
with the arm still far from the truncation ceiling -> spectral contamination is
real but the low band is independently wrong. `null_direction.cos_vs_ORACLE ~ -1`
-> the network is confidently extrapolating the WRONG way in a direction its data
never constrained, i.e. its implicit bias is worse than a min-norm least-squares
solution (which puts zero there). `|recovery_ratio| >> 1` with cos > 0 -> right
direction, wrong gain: a calibration lever, not an information problem.
Run `affine_ladder_voi.py` first for the ceiling, this second for the gap to it.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
# optional half: emit a probe condition design, run your family on it, feed back
python tools/posthoc_repair_ladder.py --dataset ifc_poisson \
    --gen_probe_conds 320 --probe_box 0.10,0.90 --probe_out probe_conds.npy
python tools/posthoc_repair_ladder.py --dataset ifc_poisson --arm_name rung_native \
    --pred_test preds_test.npz:pred --pred_hf_train preds_hftrain.npy \
    --cond_probe probe_conds.npy --pred_probe probe_preds.npy \
    --out repair_ladder.json
```
`--pred_*` accept `path.npy` or `path.npz:key`; shapes `(N,H,W)` or
`(N,n_cells)`. Pure numpy on the login node, 54 s on `ifc_poisson`. Producing the
three prediction files is the caller's job — `tools/regen_preds_from_ckpt.py`
covers the test/train pair for contract families; the probe pass needs a family
forward call on an arbitrary condition array.

**Verified.** Run 2026-07-31 from `round2/` against the r2s3-B1 `rung_native` arm
(predictions dumped by
`worktrees/r2s3_lf_train_signal/B1/scratchpad/register_dump_preds.py`, output kept
at `.../register_toolcheck_repair_rung_native.json`): L0 **16.8102**, L1 **16.2271**
(c 0.97335; ORACLE c 0.71904 -> 13.1224), L2 cutoff **8** -> **15.2051** (ORACLE
cutoff 2 -> 14.0218), L3 alpha 0.1 -> **15.5591**, non-affinity **0.19171**, law
rel-L2 vs ORACLE **1.30894**, null-direction cos **0.84967** / recovery **2.65268**
/ arm-law energy share **0.51933**, surgery arm-law **13.0894**, arm-row-only
**9.6701**, arm-row+oracle-null **8.8697**, oracle-row+arm-null **8.1047**,
information limit **3.47440**. All identical to the source probe (turn-3 C1/C2,
D1/D2/D3). **One deliberate difference**: L4 re-fits the global scale AFTER
filtering, where `reanalysis_turn_3.py` reused the unfiltered scale; on this arm
that gives **15.0098** against the probe's 14.6254. Both are legitimate; neither
is load-bearing for the card (its `-6.1150` network-channel figure uses L3).

**Provenance.** `worktrees/r2s3_lf_train_signal/B1/scratchpad/reanalysis_turn_3.py`
(parts C, D) and `.../reanalysis_turn_3b.py` (part E); card
`experiment_cards/r2s3_lf_train_signal/batch_1/B1.json` part 6, findings 10-15
and interpretations M8/M9/M10.

---

## Standing warning `affine_ladder_voi` + `posthoc_repair_ladder` encode

Both tools assume the task is **condition -> HF field with a small HF training
split**, which is round 2's setting; on a dataset with hundreds of HF train rows
the design is full rank, the null-space half returns empty and only the affinity
/ repair-ladder halves are informative. Both take the AFFINE model seriously as a
reference class — that is a virtue when `A1` says the task is affine (it makes
the analysis exact) and a limitation when it does not: a 0.3 affine-LOO residual
means the surrogate law explains only part of the arm, and the surgery numbers
should then be read as a coarse localisation, not an accounting identity. Every
`_ORACLE` key in either tool is fitted on the test split; they exist to say WHERE
an arm is wrong and must never be quoted as an arm score.

---

## `reachable_set_rank_audit.py`  *(round 2)*

**Measures.** For a TRAINED model whose outputs you can dump: the dimension of
the reachable set it actually emits, placed between the dimension of the true
field family and the dimension the condition can select. (A) singular-value
anatomy (participation-ratio effective rank, r90, r99, top-1 energy share,
uncentered and centered) of the truth's train rows and of the model's outputs on
the fit conditions, on synthetic conditions over the train box, and on synthetic
conditions 3 sd around the train mean — the last is an architecture/weights probe
independent of the data distribution; (B) the per-band FIXED-PATTERN test (mean
pairwise |cos| and effective rank of the per-sample Fourier coefficient vectors,
s2-B1 dyadic band grid: 1.0 = one fixed pattern rescaled per sample), model
against truth; (C) dictionary-vs-coefficients — ORACLE projection of the held-out
TRUE fields onto the model's own rank-r output subspace and onto the truth's own
rank-r subspace; (D) the condition-learnable rank on the SAME split (out-of-fold
R^2 of each truth-PC coefficient from ridge and 5-NN, the count above 0.5, and
the nRMSE of basis + LEARNED coefficients at each rank = the training-free
condition-only ceiling in the model's own target space); (E) the
nearest-condition-neighbour continuity test band by band (median relative field
difference and median cosine between a held-out sample and its nearest fit
sample in standardised condition space). Verdict: `RANK_MATCHES_LEARNABLE` /
`RANK_BELOW_LEARNABLE` / `RANK_MATCHES_TRUTH` / `MIXED`, plus
`structural_discontinuity` (band>=1 nn cosine < 0.10 while band0 > 0.90).

**The identifiability TRIAD — this is the third axis, not a duplicate.**
Three round-2 tools ask "is this task information-limited?" in three different
coordinate systems, and a dataset can look limited in one and healthy in another:

| tool | axis | needs a model? | question |
|---|---|---|---|
| `condition_identifiable_rank.py` (r2s1-B1) | FIELD basis (POD modes of the true fields) | no | how many coefficient knobs EXIST for the condition to turn |
| `affine_ladder_voi.py` (r2s3-B1) | CONDITION-side design (rank/null space of the HF training rows) | no | can the DESIGN identify those knobs, and are LF rows at other conditions the fix |
| `reachable_set_rank_audit.py` (this one) | TRAINED-MODEL OUTPUT family | **yes** | how many knobs the fitted weights actually turn — the only one that can say "the model is UNDER the ceiling" rather than "the ceiling is low" |

Order of use: one of the first two for the ceiling, this one for the gap to it.
Section D deliberately re-derives a learnable rank on the model's own split so
the model/ceiling comparison is apples-to-apples;
`condition_identifiable_rank.py` stays the better-regularised standalone (K-fold
alpha, RFF features) when no model is in hand.

**Read it as.** `RANK_MATCHES_LEARNABLE` + `structural_discontinuity = true` ->
rank collapse is the CORRECT response to a target the condition cannot select;
capacity, epochs and richer conditioning paths all buy nothing and the
conditional mean is the answer (r2s2-B1 pfc / allen_cahn / fisher_kpp).
`RANK_BELOW_LEARNABLE` -> the one shape of result that justifies more training
work on the same data (r2s2-B1 found exactly one such panel column,
`ext__helmholtz_2d`). `model_dict_oracle[r]` far above `truth_dict_oracle[r]` ->
the model's SPAN is the bottleneck and a richer output head is worth trying;
equal -> it is not. `pc_learnability.best_learned_reconstruction_nrmse` WORSE
than `verdict.model_heldout_nrmse` (ratio < 1) -> the model is already at or past
the training-free condition-only ceiling; quote that before proposing any better
condition->field design.

**Invoke.** Two steps; the tool never imports or runs your family.
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
# 1. emit the condition design (fit rows, val rows, 2 synthetic draws)
python tools/reachable_set_rank_audit.py --dataset sharp__phase_field_crystal_2d \
    --target lf --gen_conds --conds_out conds.npz --out plan.json
# 2. run YOUR model on conds.npz's X_fit / X_val / X_synth_box / X_synth_wide3sd
#    (same row order), then feed the outputs back
python tools/reachable_set_rank_audit.py --dataset sharp__phase_field_crystal_2d \
    --target lf --conds conds.npz \
    --pred_fit preds.npz:fit --pred_val preds.npz:val \
    --pred_synth_box preds.npz:box --pred_synth_wide preds.npz:wide \
    --out reachable.json
# training-free half only (sections D + E, no model needed)
python tools/reachable_set_rank_audit.py --dataset ifc_poisson --target lf \
    --out ceiling_only.json
```
`--fit_idx/--val_idx` take `.npy` index files when you need YOUR family's exact
split (that is how the r2s2-B1 digits below are reproduced); otherwise a
`--holdout_frac/--seed` split is used and emitted. `--pred_*` accept `path.npy`
or `path.npz:key`, shapes `(N,H,W)` or `(N,n_cells)`. `--target lf|hf` picks the
train-split field family the model imitates (`--rung` for a specific LF rung).
Pure numpy on the login node; 1.5 s on `sharp__phase_field_crystal_2d`
(64^2, 200 fit / 80 val / 160 synthetic rows), 0.2 s on `ifc_poisson`. Defaults
to the STRIPPED view and asserts the test split carries no LF fidelity.

**Verified.** Run 2026-07-31 from `round2/` against the r2s2-B1 emulator on its
OWN split (dumped by `worktrees/r2s2_stacked/B1/scratchpad/register_dump_preds.py
--mode split|preds`; outputs kept at `.../scratchpad/register_toolcheck/`):
`sharp__phase_field_crystal_2d` truth r99 **26**, model r99 **1** (top-1 energy
share **0.9999999670**), model r99 **1** on synthetic box conditions and **1** at
3 sd (top-1 0.9999996597), band>=1 |cos| truth **0.0668** (eff rank **35.60**) vs
model **0.7542** (eff rank **1.55**), model-dict ORACLE r=1 **0.264211** vs
truth-dict ORACLE r=32 **0.039691**, learnable PCs **1**, best learned
reconstruction **0.287300**, nn condition distance **0.1316** with band0
rel-diff 0.0166 / cosine **+1.0000** and band>=1 rel-diff **1.4194** / cosine
**-0.00177**, verdict **RANK_MATCHES_LEARNABLE** with
`structural_discontinuity = true`. Every one of these matches the source probe
(turn-2 F7/F9/F10/F11) to the digits reported there. The model's held-out nRMSE
comes out **0.2653962** against the card's S1 sidecar 0.2654032 — a 2.6e-05
relative deviation from float32 batch-composition nondeterminism in the emulator
forward pass, the same effect turn 3 recorded. The synthetic-condition draws use
this tool's own RNG (one `default_rng(20260731)` per dataset) where turn 2 shared
one generator across eight datasets, so the synthetic columns agree in rank and
top-1 share but are not the same draw. Ceiling-only mode smoke: `ifc_poisson`
truth r99 **2** (turn-2 F7's value) on this tool's default 0.2 holdout, 14
learnable PCs (turn 2 reported 13 of 15 on the family's split — a different
split and a different `r_max`, so qualitative agreement only).

**Provenance.** `worktrees/r2s2_stacked/B1/scratchpad/reanalysis_turn_2.py`
(P1-P4); card `experiment_cards/r2s2_stacked/batch_1/B1.json` part 6, findings
3, 4, 5 and interpretation I2' + the ceiling taxonomy.

---

## `surrogate_coherence_eligibility.py`  *(round 2)*

**Measures.** Training-free, from a dumped surrogate field family and its paired
target on the same grid: the energy-weighted **coherence** gamma of the surrogate
with the target inside each dyadic band (s2-B1 band grid), each band's target
energy share, the input/target amplitude ratio, and the **IN-SAMPLE ORACLE Wiener
transfer T(k)** fitted on the very rows being scored — a strict UPPER BOUND on
what ANY spatially-invariant linear stage (LSI filter, band-gain calibration,
ideal low-pass) could add on that input. Reports `identity_nrmse`,
`oracle_lsi_nrmse_insample`, `oracle_lsi_relative_gain`, and with
`--arm_nrmse/--reference_nrmse` the multiplicative transfer of that gain to a
scored arm in **skill units**. Verdict `CORRECTOR_ELIGIBLE` (gamma_band1 >= 0.95)
/ `CORRECTOR_FUTILE` (<= 0.52) / `UNDETERMINED` in the bracket r2s2-B1 left open.

**Read it as.** This is the PRECONDITION test for any `stage-1 surrogate ->
stage-2 corrector` design, and it is decidable before stage 2 exists. r2s2-B1
measured the same frozen corrector removing 32-100% of the remaining error at
gamma_band1 ~ 1.0 and <= 0.08% at gamma_band1 <= 0.52, with the correction vector
rotating from cos +0.98 to cos ~0 against the residual it must remove; a 10%
admixture of the emulated field into a real LF input already cost 7-48x of the
corrector's value. `CORRECTOR_FUTILE` -> fix stage 1 or change the class; a
corrector cannot restore a realisation its input does not carry. High gamma with
`input_over_target_amp` far from 1 is the GOOD case (right realisation, wrong
gain — exactly what an LSI stage fixes). Low gamma in band0 as well (r2s2-B1
helmholtz 0.139) means the surrogate is not tracking the target anywhere.
Neighbours: `spectral_prestage_bc_audit.py` asks whether a spectral stage is
APPLICABLE (BC/wrap-seam match), this asks whether the input is worth filtering;
`posthoc_repair_ladder.py` rung L2 is the train-fitted ideal-low-pass member of
the same class and this is its unconstrained ceiling; `band_gain_counterfactual.py`
is the held-out-fitted version to run only if this ceiling is worth having.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/surrogate_coherence_eligibility.py \
    --dataset sharp__cahn_hilliard \
    --pred pseudo_lf_upsampled.npy --target hf_train_rows.npy \
    --arm_nrmse 0.47149238 --reference_nrmse 0.04180296 --out coh.json
# target straight from the dataset's TRAIN split at given rows
python tools/surrogate_coherence_eligibility.py --dataset sharp__cahn_hilliard \
    --pred preds.npz:val --target_from_train --rows val_idx.npy --out coh.json
```
`--pred/--target` accept `path.npy` or `path.npz:key`, shapes `(N,H,W)` or
`(N,n_cells)`; both must be on the same (corrector working) grid in the same row
order. Pure numpy, ~1 s for 80 rows at 128^2. Producing the surrogate on the
working grid is the caller's job (it is the upsampled stage-1 output).

**Verified.** Run 2026-07-31 from `round2/` on the r2s2-B1 emulator's own
pseudo-LF, upsampled through the family's convention-keyed upsampler and scored
against the paired TRAIN HF rows (dump script + outputs at
`worktrees/r2s2_stacked/B1/scratchpad/register_toolcheck{,_ch}/`):
`sharp__phase_field_crystal_2d` (80 rows) gamma band0 **0.829** / band1 **0.128**,
identity **0.265395**, oracle LSI **0.301885**, gain **-13.75%** (the oracle
filter is HARMFUL), verdict CORRECTOR_FUTILE; `sharp__cahn_hilliard` (turn-3's
20-row slice) gamma band0 **0.933** / band1 **0.5164**, identity **0.289310**,
gain **+14.07%**, and with the card's scored arm 0.47149238 against the recorded
0.04180296 reference: implied arm nRMSE **0.4051685**, implied skill **9.69234**
from **11.27892**, i.e. **1.5866 skill units** — reproducing the card's
load-bearing "~1.59 skill units, below the clause's own 2.0 threshold" exactly.
All of these match the source probe (turn-3 F15 and the falsification postmortem)
to the digits reported there.

**Provenance.** `worktrees/r2s2_stacked/B1/scratchpad/reanalysis_turn_3.py`
(P6); card `experiment_cards/r2s2_stacked/batch_1/B1.json` part 6, findings 6-8,
interpretations I7/I10 and the falsification postmortem.

---

## Standing warning `reachable_set_rank_audit` + `surrogate_coherence_eligibility` encode

Both tools take the CONDITIONAL MEAN seriously as the reference answer, because
that is what r2s2-B1 measured the panel to be pinned at. Consequences to keep in
mind. (1) `reachable_set_rank_audit` scores a DETERMINISTIC output family: a
stochastic or realisation-sampling emulator will legitimately show a reachable
rank far above its own learnable rank, and the `RANK_MATCHES_LEARNABLE` label
must not be read as a defect there — read the per-band diversity statistics (B)
against the truth's instead. (2) Its `n_pcs_learnable` count uses a fixed
ridge/5-NN pair at lambda 1e-6 and k=5 on the given split; it is a floor on
learnability, not a proof of unlearnability, and `condition_identifiable_rank.py`
with RFF features is the stronger test when the answer matters. (3) Every
`*_oracle` key in either tool (basis projections; the Wiener transfer) is fitted
on the rows being scored and is a CEILING — never an arm value. (4) The
gamma_band1 thresholds 0.95 / 0.52 are the two clusters r2s2-B1 actually
observed, on ONE corrector family (closed-form Wiener + gated local CNN) at one
tier; the region between them is unmeasured, and `oracle_lsi_relative_gain`
converted to skill units is the number to act on, not the label.

---

## `ladder_pair_alignment_audit.py`

**Measures.** Whether a dataset's fidelity rungs are paired by CONDITION or only
by ROW INDEX, on the TRAIN split, from condition vectors alone (no fields, no
model, seconds). Per dataset x LF rung: `max_abs_cond_mismatch_paired` (0 <=>
index-aligned), `paired_cond_distance_mean` vs `nearest_cond_distance_mean`,
`paired_row_is_nearest_frac`, `lf_rows_at_conditions_without_hf` (the
disjoint-condition supply), `lf_rows_discarded_by_truncation`, and a verdict
`PAIRED_ALIGNED | MISPAIRED | DISJOINT_SUPPLY_TRUNCATED | TOO_FEW_ROWS`.

**Why.** `eval/panel_data.py::copylf_prediction` — and every family that vendors
it — pairs rungs with `lf = lf[:n_hf]`. That is true on the five aligned/nested
npz datasets and FALSE on the `ifc_raw` ladder. r2s4-B2's ifc arms trained
against coarse fields belonging to unrelated parameter vectors, and the card's
own seam check (`max_abs_diff = 0.0` against the eval layer) PASSED because both
implementations share the same assumption. A seam check between two
implementations of one assumption certifies nothing; this tool interrogates the
DATA.

**Read it as.** `MISPAIRED` -> no `hf - lf`, LF-target, LF-teacher or copy-LF
number on that dataset is evidence about the value of LF in either direction;
pair by nearest condition, gate the arm off, or drop the dataset from the
contrast. `DISJOINT_SUPPLY_TRUNCATED` -> the rungs carry conditions the HF rung
does not and the truncation rule discards them; that supply is the only channel
by which LF adds DESIGN ROWS rather than a smoothed copy of the HF target
(r2s3-B2 measured A0_nolf 8.1344 -> A2_lf_cov_null 3.4550 skill, +4.68, on ifc_poisson at N_hf = 5, single training seed).

**Complements, does not duplicate.** `ladder_pair_row_audit.py` (s1_poisson-B3)
asks whether an all-pairs ROW SET replicates data and only flags
`MISMATCHED_PAIRS` under `--cond-from source`; r2s2-B1's `V6b` answers the same
question INSIDE a training job (sets `paired_real_lf` /
`arm_semantics_degraded`). Run this BEFORE the build; use a V6b-style in-job gate
to degrade gracefully where it says MISPAIRED.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/ladder_pair_alignment_audit.py --datasets PANEL --out pair_audit.json
python tools/ladder_pair_alignment_audit.py --datasets ifc_poisson \
    --split train --fail-on mispaired      # exit 2 => usable as a build gate
```

**Verified.** Run 2026-08-01 on the stripped view, `--datasets PANEL`: five
panel datasets `PAIRED_ALIGNED` (max|dcond| 0.0, 100% paired-to-nearest, 0
disjoint rows); `ifc_poisson` `MISPAIRED` with rung 32 giving max|dcond|
**0.6819**, paired distance **0.7435** vs nearest **0.2703**, **0%**
paired-to-nearest, and **170** LF rows at conditions with no HF row (100/50/20 at
rungs 8/16/32) — reproducing r2s4-B2 findings T2-F6 and T2-F7 and the T1-F5 row
counts exactly.

**Provenance.** `worktrees/r2s4_diag/B2/scratchpad/reanalysis_turn_2.py` block F
(+ block E's supply counter); card
`experiment_cards/r2s4_diag/batch_2/B2.json` part 6, findings T2-F6 / T2-F7 /
T1-F5 and falsification postmortem section (2).

---

## `shrinkage_curve_anatomy.py`

**Measures.** For every shrinkage curve `f(lambda) = nRMSE(Pbar + lambda(P -
Pbar))` a card ships: the LEVEL `f(0)` (own-mean broadcast — what the trunk
learned that is identical for every condition), the RAW `f(1)`, `min`,
`lambda_argmin`, the model-free fluctuation amplitude (top-of-grid slope), and an
effective sqrt-quadratic fit giving `eff_fluct_over_level`, `eff_alignment`
(cos of the condition response with the truth) and `eff_lambda_opt`, with
`fit_r2` always reported next to the model-free columns. With `--contrast A:B`
it reports `level_delta`, `raw_delta` and a `sign_flip` flag per file.

**Why.** The level and the fluctuation are two different questions averaged into
one nRMSE, and they can point opposite ways. r2s4-B2's helmholtz arms tied at the
level (T0 - T1 = +0.4179 skill, T1 better on 2/3 seeds) and separated with the
opposite sign at lambda = 1 (-0.8980): reported as one number that reads as a
paradox ("the contrast flips sign between the raw and the shrunk column");
decomposed it is one sentence — same mean field, different and anti-aligned
condition response.

**Read it as.** `|level_delta| << |raw_delta|` -> the change did not move the
mean field, it rescaled/reaimed the condition response; check `eff_alignment` and
the seed spread of `slope_top` before claiming anything. `eff_alignment <= 0`
with `lambda_argmin = 0` -> the arm's condition-dependent part is
worthless-to-harmful on this split. `lambda_argmin > 1` -> the fitted deviation
from the mean field is too SMALL (MSE over-smoothing); across an N-sweep,
lambda* crossing 1 is the sample-limited signature (r2s4-B2 T3-F6: cahn_hilliard
0.767 -> 1.117 as N_fit goes 20 -> 320).

Curve discovery is schema-free — it walks the JSON for any object holding a
`grid` plus `*_curve` arrays of matching length — so it runs on any card that
ships a shrinkage column, whatever the surrounding key names.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/shrinkage_curve_anatomy.py \
    --json '<outputs>/r2s4_diag/B2/eval/arms_ext__helmholtz_2d_e200_s*.json' \
    --curves test --contrast T0_cond_only:T1_lf_aux --skill --out anatomy.json
```
`--skill` divides by `eval/copylf_baselines.json` using the `dataset` key inside
each JSON.

**Verified.** Run 2026-08-01 on r2s4-B2's three helmholtz arms JSONs: levels T0
3.7996 / 4.0676 / 4.8507 and T1 3.9134 / 3.6654 / 3.8853 skill, mean level delta
**+0.4179** against mean raw delta **-0.8980**, sign flips **3/3**, T1 argmin
0.00 on all seeds with alignment -0.184 / -0.188 / -0.032 and T0 +0.114 / -0.019
/ +0.119 — reproducing findings T2-F1 and T2-F2 exactly.

**Provenance.** `worktrees/r2s4_diag/B2/scratchpad/reanalysis_turn_2.py` block A
(`curve_anatomy`) and turn 3's lambda*(N) reading; card
`experiment_cards/r2s4_diag/batch_2/B2.json` part 6, findings T2-F1 / T2-F2 /
T3-F6.

---

## `condition_predictability_ceiling_fast.py`

**Measures.** Exactly what `condition_predictability_ceiling.py` measures — it
IMPORTS the frozen tool and swaps in a float32 / capped-pair estimator path, so
the schema, the printed line and the definitions stay in the original file
(untouched, byte-for-byte). Output gains `_estimator_path` and `_max_pairs`.

**Why.** The frozen tool's float64 all-pairs path did not finish one 256^2
dataset inside a 20-minute cap on the round's login node (killed at >20 min on
`sharp__allen_cahn_2d` during r2s4-B2 turn 1), which makes it unusable in a
mechanism turn — the place a training-free ceiling is most often wanted.

**Read it as.** Identical to the frozen tool. One caveat the `--validate` mode
exists to make unmissable: the float32 swap costs ~1e-11, but the DEFAULT pair
cap (20 000 vs the frozen tool's 200 000) changes the pair intercept at the
1e-2 level. If you quote a pair intercept, match `--max_pairs` or report the cap;
the k-NN bound is unaffected.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/condition_predictability_ceiling_fast.py --datasets PANEL --out ceiling.json
python tools/condition_predictability_ceiling_fast.py --validate \
    --datasets ext__helmholtz_2d --out validation.json     # both paths, side by side
```
All other flags of the frozen tool (`--ks --n_bins --preds --data_root`) are
accepted and forwarded unchanged.

**Verified.** Run 2026-08-01. `--validate` on `ext__helmholtz_2d`: k-NN bound
1.1150040817905758 vs 1.1150040817905758, |diff| **0.0**, same k*; pair intercept
|diff| **2.1e-11** at matched `--max_pairs 200000` and **2.1e-2** at the default
20 000 (subsampling, not precision). Full fast run on `sharp__allen_cahn_2d`
(400 x 256^2): **35 s** end-to-end, k-NN ceiling **176.2813** at k* = 8, which
reproduces r2s4-B1's float64 value 176.28128331491402 computed by a different
script on the same split.

**Provenance.** `worktrees/r2s4_diag/B2/scratchpad/reanalysis_turn_1.py`
(`loo_knn_curve_fast` / `pair_extrapolation_fast`, validation artefact
`scratchpad/t1_fast_helmholtz_validation.json`); the estimators are
r2s4_diag-B1's (card part 6, T2-F1...T2-F6).

---

## `null_family_ceiling_audit.py`  *(round 2)*

**Measures.** For one or more shipped arms (predictions only — training-free, no
checkpoint surgery), where their test error lives relative to what their HF
TRAINING rows could ever have constrained. With `[X_hf, 1]` of rank `r` and null
dimension `m = d + 1 - r`, every affine functional in that null space vanishes at
ALL training conditions, so an ORACLE may edit a prediction along it without
touching a single training-row fit. Per arm: raw skill; the ORACLE ceiling over
the `m`-dim **NULL** family, over the complementary `r`-dim **ROW** family and
over the full `(d+1)`-dim **AFFINE** family, reported as `error_null_borne` /
`error_row_borne` / `error_affine_borne`; a mandatory **random `m`-dim subspace
control** (`null_over_random`); the arm's **implicit affine law** (fitted on its
own test predictions) split into the same two blocks and compared with the ORACLE
(test-fitted) law — null-block amplitude ratio, Frobenius cosine, row-block
rel-L2, non-affinity; and with `--level` the third channel (own mean field
swapped for the HF-train mean / lifted LF-rung means / the N-selected-row mean /
the ORACLE test mean). `--contrast A:B` attributes an already-measured arm gap to
the three channels.

**Why the random control is not optional.** An `m`-dim oracle edit is powerful by
DIMENSION alone: on `sharp__cahn_hilliard` (m = 15 of 20) the null family removes
0.89-1.05x what a random 15-dim subspace of the same affine family removes, so
the honest statement there is "LF coverage repairs the whole condition response,
of which 15 directions happen to be unreachable", not "the defect is
null-ALIGNED". On the exactly-affine `ifc_poisson` (m = 1 of 6) the same ratio is
**17.9x** for the no-LF arm. Reporting a null-family ceiling without this control
turns arithmetic into a mechanism claim.

**Read it as.** `null_over_random >> 1` -> the arm's error really is concentrated
in the directions its rows could not see: an identifiability problem, and only
new CONDITIONS (LF rows elsewhere, `design_coverage_audit.py`) can fix it.
`null_over_random ~ 1` -> isotropic error; read the level/row channels and treat
"null" as a dimension count, not a diagnosis. Implicit-law null block with
`recovery_ratio >> 1` and `cos < 0` -> confident wrong-way extrapolation in the
unseeable subspace (worse than a min-norm solution, which puts zero there);
`ratio ~ 1` at `cos ~ 0` -> the arm was merely stopped from inventing a large
wrong component — calibration, not direction transfer; `ratio ~ 1` at `cos ~ +1`
-> genuine direction supply. `m = 0` -> the null half is identically zero by
construction and the tool prints the note; run with `--level`, because that is
where a value-of-LF effect can still live (r2s3-B2 turn 2: 77 % of the
`sharp__fisher_kpp_2d` effect).

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/null_family_ceiling_audit.py --dataset sharp__cahn_hilliard \
    --arm A0_nolf=<outputs>/results_ch_A0_s0/<family>/<ds>_e200_s0_preds.npz \
    --arm A2_lf_cov_null=<outputs>/results_ch_A2_s0/<family>/<ds>_e200_s0_preds.npz \
    --contrast A0_nolf:A2_lf_cov_null --level --out ceilings.json
```
`--arm NAME=path[:key]` repeatable (`.npy` or `.npz:key`, default key
`pred_test`; `(N,H,W)` or `(N,n_cells)`). The HF design comes from the first
arm's `cond_hf_train_raw` unless `--hf_cond path[:key]` / `--hf_rows i,j,...`.
Knobs: `--n_random` (default 5), `--seed`, `--rank_tol`, `--max_test`,
`--skill_denominator`, `--data_root`. Pure numpy (torch only inside the shared
rung loader). 114 s on `sharp__cahn_hilliard` (4 arms, 100 x 256^2, `--level`),
13 s on `sharp__fisher_kpp_2d`, 4 s on `ifc_poisson`.

**Verified.** Run 2026-08-01 from `round2/` on r2s3-B2's shipped dumps (outputs
kept at `worktrees/r2s3_lf_train_signal/B2/scratchpad/register_toolcheck_nullfamily_{ch,ifc,fk}.json`).
`sharp__cahn_hilliard` draw 0, m = 15: null-borne error A0_nolf **12.136507**,
A1_lf_cov **0.365526**, A2_lf_cov_null **0.703992**, A3_lf_paired **12.746983**;
row-borne 6.916788 / 0.092938 / 0.225536 / 7.615289; `null_over_random` 0.930 /
0.892 / 1.048 / 0.896; implicit-law null-block ratios 2.1053 / 0.8861 / 0.9925 /
2.7215 at cos -0.4033 / +0.2172 / +0.0463 / -0.3311; level swap
30.0783 -> 26.2729 (HF-train mean) and 26.27297 (LF rung-1 mean); contrast
A0-A2 gap 16.735753 = 68.3 % null-borne / 40.0 % row-borne / 22.7 % level. Every
one of these matches the source probe (turn 3 T3.3-T3.6, T3.9) to <= 3e-14 — the
tool builds the null basis by SVD of the design where the probe read it from the
family's gate report, so the subspace, and the ceiling, are the same object.
`ifc_poisson` m = 1: null-borne 3.598827 / 0.038837 / 0.665357 / -1.305000
reproduces turn 1d exactly, `null_over_random` **17.877** (A0) vs 0.047 (A1), and
the coordinate-free `A0-A1` contrast is **59.7 %** null-borne — the tool-native
version of turn 1's 57-60 % direction-supply share. `sharp__fisher_kpp_2d` m = 0:
null columns empty as designed, level references `hf_train_mean_full` 11.993111,
`lf_rung2_mean_lifted` 11.991433, `hf_train_mean_n_selected` 13.162407 and the
A0 level swap 16.9436 -> 16.0546, all identical to turn 2 T2.3-T2.5.

**Provenance.** `worktrees/r2s3_lf_train_signal/B2/scratchpad/reanalysis_turn_3.py`
(functional ceilings, level ladder, three-channel contrasts),
`.../reanalysis_turn_3b.py` (blocks 2-3: dimension control, implicit-law null
block) and `.../reanalysis_turn_1d.py` (the m = 1 original); card
`experiment_cards/r2s3_lf_train_signal/batch_2/B2.json` part 6, findings 2/3/7/8/9
and interpretations M1/M2.

---

## `design_coverage_audit.py`  *(round 2)*

**Measures.** Training-free, from condition vectors alone (seconds; fields only
under `--fields`): whether an LF pool changes the AFFINE IDENTIFIABILITY of the
HF training design. Per LF rung — rank, null dimension `m` and singular values of
`[X, 1]` for (a) the HF training rows actually used, (b) the **paired** pool (LF
rows at exactly those conditions), (c) the **full** pool, (d) the union of (a)
and (c); the covered / uncovered condition counts (the disjoint SUPPLY);
`m_reduction_paired` vs `m_reduction_full`; a
`paired_pool_singular_values_identical_to_hf` flag; and with `--fields` the
lifted-LF-vs-HF rel-L2 (per condition, mean, max) and cosine at the covered
conditions. Verdicts per rung: `FULL_POOL_COMPLETES` / `FULL_POOL_REDUCES_DEFICIT`
/ `PAIRED_POOL_ADDS_NO_RANK` / `NO_DEFICIT_TO_FIX` / `POOL_LEAVES_DEFICIT`, plus
`CONTRADICTORY_PAIRED_TARGET` and `DISJOINT_DESIGN_NO_COVERED_CONDITIONS`.

**Why.** LF budget is a design choice before it is an architecture choice. LF rows
at conditions that already carry an HF row cannot reduce `m` — they span the same
row space, and r2s3-B2 verified the singular values are bit-identical — so a
"curriculum"/paired arm has zero access to the deficient subspace; and where the
coarse solve is a genuinely different field rather than a blurred one, those rows
are a CONTRADICTORY target on exactly the rows the HF loss supervises
(`sharp__cahn_hilliard` rung 1: mean rel-L2 0.398, one condition 1.398 — a
different phase-separation morphology). That arm finished 0.83 skill units WORSE
than training with no LF at all. The transportable rule the tool operationalises:
spend the LF budget on NEW CONDITIONS.

**Read it as.** `m_reduction_paired = 0` with `m_reduction_full > 0` -> the value
of the pool is coverage, and any ablation that pairs LF to the HF rows is testing
nothing (it is the no-LF control plus noise). `NO_DEFICIT_TO_FIX` (m = 0) -> no
identifiability story is available on this dataset; look at the level channel
(`null_family_ceiling_audit.py --level`). `CONTRADICTORY_PAIRED_TARGET` -> do not
build an `hf - lf` residual target, an LF-teacher loss or a paired auxiliary loss
at that rung; the rung is not a blurred HF. `DISJOINT_DESIGN_NO_COVERED_CONDITIONS`
-> a paired arm is not even definable (ifc_poisson).

**Complements, does not duplicate.** Four axes, run what you need:
`ladder_pair_alignment_audit.py` (r2s4-B2) — are the rungs paired by CONDITION or
only by ROW INDEX, and what does `lf[:n_hf]` discard; **this tool** — given the
pairing, does the pool change the design's RANK / null dimension, and is a paired
LF field a contradictory target; `affine_ladder_voi.py` (r2s3-B1) — the same
deficiency priced in SKILL units with the fields (law energy in the null space,
what each rung recovers, the HF-only information limit);
`null_family_ceiling_audit.py` (this card) — where a TRAINED arm's error actually
sits with respect to that null space. The field-basis and model-output axes are
`condition_identifiable_rank.py` (r2s1-B1) and `reachable_set_rank_audit.py`
(r2s2-B1).

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/design_coverage_audit.py --dataset sharp__cahn_hilliard \
    --hf_rows_from <outputs>/results_ch_A3_s0/<family>/<ds>_e200_s0_preds.npz \
    --fields --out coverage_ch.json
python tools/design_coverage_audit.py --dataset ifc_poisson        # whole HF split
```
`--hf_rows_from path[:key]` (default key `selected_train_rows`) or
`--hf_rows i,j,...`; default is the whole HF train split. Knobs:
`--max_covered_scored` (25), `--contradiction_tol` (0.2), `--match_decimals`
(12), `--rank_tol`, `--data_root`. Without `--fields` it never loads a field
upsample: 2.4 s on `ifc_poisson`, 5.0 s with fields on `sharp__fisher_kpp_2d`,
12.8 s with fields on `sharp__cahn_hilliard`.

**Verified.** Run 2026-08-01 from `round2/` (outputs kept at
`worktrees/r2s3_lf_train_signal/B2/scratchpad/register_toolcheck_coverage_{ch,ifc,fk,fk_all}.json`).
`sharp__cahn_hilliard` on the A3 arm's own 5 training rows: HF design rank **5**
of 20, m = **15**, singular values 3.940326/3.026555/2.578849/2.059855/1.655111;
both rungs' paired pools rank 5, m 15, singular values identical (flag `true`),
`m_reduction_paired` **0** vs `m_reduction_full` **15**; covered-condition rel-L2
**0.398227** (max **1.398046**, cos 0.8061) at rung 1 and **0.053** at rung 2 ->
`FULL_POOL_COMPLETES+CONTRADICTORY_PAIRED_TARGET` / `FULL_POOL_COMPLETES`. All
identical to turn 3 T3.7/T3.8. `ifc_poisson`: rank 5/6, m = 1, **0** covered
conditions at every rung with 100/50/20 uncovered LF rows — matching
`affine_ladder_voi`'s verified overlap counts and
`ladder_pair_alignment_audit`'s 170 disjoint rows. `sharp__fisher_kpp_2d`:
m = **0** (`NO_DEFICIT_TO_FIX`), and over the whole HF split the covered-condition
discrepancy is 0.1676 / 0.0615, reproducing turn 3b's cross-dataset block
exactly; restricted to the arm's 5 training rows the same statistic is
0.1703 / 0.0625 — the number is sample-set dependent, so quote the row set.

**Provenance.** `worktrees/r2s3_lf_train_signal/B2/scratchpad/reanalysis_turn_3b.py`
blocks (1) and (4), plus `.../reanalysis_turn_3.py`'s
`lf_vs_hf_discrepancy_at_covered_conditions`; card
`experiment_cards/r2s3_lf_train_signal/batch_2/B2.json` part 6, findings 10/12
and interpretation M3.

---

## Standing note the identifiability / coverage family encodes

`condition_identifiable_rank.py` (field basis), `affine_ladder_voi.py`
(condition-side design, priced in skill), `reachable_set_rank_audit.py` (model
output family), `ladder_pair_alignment_audit.py` (rung pairing),
`design_coverage_audit.py` (does the LF pool change the design's rank) and
`null_family_ceiling_audit.py` (where a trained arm's error sits w.r.t. that
design) are six views of one question — *what could these rows have determined,
and did the model get it?* Two shared limitations. (1) They all take the AFFINE
model of `cond -> field` seriously; that is exact on `ifc_poisson` (affine-LOO
3.2e-08) and only half true on the sharp datasets (rung LOO ~0.54 on
`sharp__cahn_hilliard`), where "null-borne error" is a localisation, not an
accounting identity — which is exactly what
`null_family_ceiling_audit`'s random-subspace control exists to expose. (2) They
assume the round-2 setting `N_hf` small: with hundreds of HF training rows the
design is full rank, `m = 0`, and the null halves return empty by construction
(not a bug — see `NO_DEFICIT_TO_FIX`). Every `_ORACLE` key in either new tool is
fitted on the test split and is a CEILING; only DIFFERENCES between two arms'
ceilings are quotable, and never as an arm score.

---

## `blend_decorrelation_payoff.py`  *(round 2)*

**Measures.** For every (dataset, arm, base) cell of a post-hoc blend stage
`pred_final = λ·arm + (1−λ)·base`, the single free parameter of the two-member
ensemble model

```
c(λ)² = λ²a² + (1−λ)²b² + 2λ(1−λ)·ρ·a·b      a = c(1) arm alone, b = c(0) base alone
λ*    = (b² − ρab)/(a² + b² − 2ρab)          c_min = ab√(1−ρ²)/√(a² + b² − 2ρab)
```

fitted by least squares over the **shipped calibration λ-surface**
(`blend_full[arm].cal_table[base]`, typically 21 constraints for 1 parameter),
plus: the fit RMS residual relative to the arm's own nRMSE (the audit number for
the aggregate-norm approximation — the round's nRMSE is a mean of per-sample
relative L2, not a global norm), the λ-clipped `c_min`, the predicted and actual
test-side payoff, the ρ **implied on test** by the shipped `(a, b, λ, final)`
quadruple as an independent second estimate, per-cell verdicts
(`COLLINEAR_WITH_BASE` ρ ≥ 0.99 / `BASE_DOMINATED` λ ≤ 0.25 / `ENSEMBLE_ACTIVE`),
and with `--counterfactual ARM:REF_ARM:BASE` the **equal-ρ counterfactual**: what
ARM would have scored with its own `(a, b)` had its errors been as decorrelated
from the base as REF_ARM's, against REF_ARM's shipped final, in skill and mce
multiples.

**Why.** A floor-blend stage is shipped as a fairness device (identical code path
for every arm) and is not one. Its payoff at fixed `(a, b)` is **monotone in ρ**,
and ρ differs between arm classes *by construction*: a closed-form
condition-regression head can BE the closed-form base (r2s1-B2, allen_cahn: arm
and `dc_only` agree to 1.8e-5, fitted ρ = 1.0000 with RMS residual 1.0e-6, so no
λ can pay it), while a trained decoder sits at ρ ≈ 0.69–0.78 and collects 8.13
skill. That card's decisive falsification cell was decided entirely at this
stage, against a raw comparison of the OPPOSITE sign and 4.3× the magnitude. Any
card with a post-hoc blend, floor-hedge, or ensemble stage should run this before
reading an arm contrast.

**Read it as.** `rho_fit ≥ 0.99` → that arm is unpayable by this stage; a
contrast against an arm at lower ρ is a decorrelation verdict, not an accuracy
verdict. `shipped_lambda ≤ 0.25` → the reported score is mostly the BASE (r2s1-B2
`ifc_poisson`: the decoder was 95 % replaced by a `(d+1)`-parameter ridge), so the
cell compares two bases, not two arms. Both arms COLLINEAR and λ ≈ 0 → a dead
cell: report it as such rather than as evidence. Large `Δρ` between arm classes on
exactly the datasets where the blend moves the verdict → instrument bias, and the
counterfactual block prices it. `fit_rms_resid_rel_to_a` above ~5 % (small
calibration folds) → treat that cell's ρ as indicative only.

Not an achievable arm: ρ is not a free knob. The counterfactual is an ACCOUNTING
decomposition of a shipped comparison, and must be labelled as such wherever it
is quoted.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/blend_decorrelation_payoff.py \
    --diag '<outputs>/r2s1_direct/B2/eval/diag_*_e200_s0.json' \
    --arms test_hf,ref_decoder_big --counterfactual test_hf:ref_decoder_big:dc_only \
    --skill --out payoff.json
```
`--skill` converts with `eval/copylf_baselines.json`; mce multiples come from
`state/noise_floor.json` (both paths default relative to the tool, overridable
with `--copylf` / `--noise_floor`). Every schema assumption is a flag
(`--blend_key --cal_table_key --lambda_grid_key --arm_table_key --arm_nrmse_key
--arm_post_field --final_field --base_field --lambda_field --base_key_prefix`), so
it runs on any card whose blend surface has a different key layout. Runtime ~3 s
for 6 datasets × 21 arms × 4 bases.

**Verified.** Run 2026-08-01 on r2s1-B2's six shipped panel diag JSONs (outputs
kept at `worktrees/r2s1_direct/B2/scratchpad/register_toolcheck_blend_payoff.{json,log}`,
all 21 arms x 4 bases, 3 s). Worst relative fit residual per dataset
`ifc_poisson` **0.0472** / `ext__helmholtz_2d` 0.0161 / `pfc` 0.0152 /
`sharp__cahn_hilliard` 0.0104 / `sharp__allen_cahn_2d` 0.0101 /
`sharp__fisher_kpp_2d` 0.0014, identical to card part 6 T3-F1. allen_cahn
ρ(head, `dc_only`) **1.0000** vs ρ(`ref_decoder_big`) **0.7833** cal-fit /
**0.6885** test-implied, `ref_decoder_small` 0.7586/0.8076 (T3-F3); counterfactual
175.2523 / 165.6534 / 161.1891 skill against the decoder's shipped 167.4768, i.e.
**+1.8234 (2.07× mce)** and **+6.2877 (7.15× mce)** (T3-F4); pfc 0.9937/0.9946 and
fisher_kpp 1.0000/0.9985 both `COLLINEAR_WITH_BASE` (T3-F7); `ifc_poisson` decoder
λ = 0.05 `BASE_DOMINATED` (T3-F6).

**Provenance.** `worktrees/r2s1_direct/B2/scratchpad/reanalysis_turn_3.py`; card
`experiment_cards/r2s1_direct/batch_2/B2.json` part 6, findings T2-F2 / T3-F1…F7
and interpretation I1.

---

## `selection_set_vs_window_audit.py`  *(round 2)*

**Measures.** Given a card's shipped selection diagnostics — a per-component
statistic (per-POD-mode out-of-fold R², per-band SNR, per-channel gain…), its
threshold `tau`, and the count `r_sel` the rule shipped — it reconstructs the
**identified SET** `{i : stat_i > tau}` and the **fitted WINDOW** `{0..r_sel−1}`,
lists the identifiable-but-not-fitted and fitted-but-not-identifiable components
with their statistic values, prices the mismatch as displaced statistic mass (and
energy share, with `--energy_key`), reports what a SET-indexed rule would have
fitted, and raises `FORM_MISMATCH` when `--stat_form` (the basis/centering form
the statistic was computed on, read off the code) differs from the form actually
fitted.

**Why.** The rule shape "count how many components clear tau, then fit the leading
that-many" is extremely common and its two halves are not the same object. Under
an ENERGY-ordered basis they diverge exactly when the predictable content is
low-energy: on r2s1-B2's `sharp__cahn_hilliard` the identifiable set is
{0, 1, 12, 13} (the condition-predictable DC direction sits at modes 12–13,
0.45 % of basis energy) while the rule fitted {0, 1, 2, 3}, buying two noise modes
at OOF R² −0.008/+0.025 and discarding the spatial mean — worth **5.6× mce**
(39.6 % of that card's L2 gap) on a refit with the SAME parameter count and no
test quantity. The defect is invisible in every summary the rule reports, because
the rule reports `r_sel`.

**Read it as.** `ARITY_DEFECT` → the rule's indexing, not its cardinality, is
wrong; the repair is train-side and free (refit on `set_rule_would_fit`), and any
capacity claim resting on that cell is premature until it is applied.
`stat_mass_missed >> stat_mass_spurious` → the window is throwing away real
signal. `contiguous_from_zero: false` on an energy-ordered basis → expect this
defect on every future card using the same rule family.
`FORM_MISMATCH` → the indices are being transferred across incommensurable
decompositions; the numerical damage may be nil (≤ 0.013× mce on r2s1-B2's
helmholtz) but the rule is not doing what it says. This is a DETECTOR: the refit
and rescore need the family's own code and belong in the experiment's scratchpad.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/selection_set_vs_window_audit.py \
    --diag '<outputs>/r2s1_direct/B2/eval/diag_*_e200_s0.json' \
    --stat_form add --out setwindow.json
```
Defaults target the r2s1-B2 schema
(`selection_stage.rank.{mode_r2_oof,rank_tau,r_sel}`, form at
`selection_stage.selected_form`); every one is a dotted-path flag
(`--stat_key --tau_key --count_key --form_key --energy_key --tau`), and `--auto`
walks the JSON for any numeric list whose key contains `--stat_name`. Runtime
< 1 s.

**Verified.** Run 2026-08-01 on r2s1-B2's six shipped panel diag JSONs (outputs
kept at `worktrees/r2s1_direct/B2/scratchpad/register_toolcheck_setwindow.{json,log}`):
`ext__helmholtz_2d` r_sel 3, SET {8, 9, 20} vs WINDOW
{0,1,2} (`ARITY_DEFECT+FORM_MISMATCH`, missed stat mass 1.2435 against a window
mass of −0.0387); `sharp__cahn_hilliard` r_sel 4, SET {0, 1, 12, 13} with modes
12/13 at +0.4744/+0.3658 and the bought modes 2/3 at −0.0083/+0.0249
(`ARITY_DEFECT`); `sharp__phase_field_crystal_2d` SET {0, 1, 7};
`sharp__allen_cahn_2d` / `sharp__fisher_kpp_2d` / `ifc_poisson`
`SET_EQUALS_WINDOW`. Identical to card part 6 T1-F2 and T1-F7.

**Provenance.** `worktrees/r2s1_direct/B2/scratchpad/reanalysis_turn_1.py`
(SET-vs-WINDOW audit) and `reanalysis_turn_1b.py` (cross-form check); card
`experiment_cards/r2s1_direct/batch_2/B2.json` part 6, findings T1-F2 / T1-F3 /
T1-F4 / T1-F7 and interpretation I3.

---

## Standing note the two r2s1-B2 instrument tools encode

`blend_decorrelation_payoff.py` and `selection_set_vs_window_audit.py` are
**instrument audits**, not model diagnostics: they measure defects in the SCORING
and SELECTION machinery a card ships around its arms. Both were found only
because a falsified card was re-read at mechanism level, and both changed what
the falsification licensed without changing the verdict. The standing lesson: when
a card composes a pre-registered selection rule with shared post-hoc stages, audit
the composition before attributing anything to capacity — a rule that reports one
summary number can hide a set-vs-window bug, and a "fair because identical for
every arm" stage can still score arms on a quantity the card never intended to
test.

---

## `zero_gradient_stage_ladder.py`  *(round 2)*

**Measures.** Inside a stack that has already been trained, WHICH OF ITS OWN
STAGES earned the leaderboard number. Rebuilds the stack's intermediates from the
family's own modules and walks a ladder, every choice selected OUT OF FOLD on a
calibration split and read on TEST: `S0 raw` (the intermediate, 0 parameters),
`S1 gain` (one calib-fitted scalar), `S2 lsi` (closed-form Wiener transfer fitted
on the fit fold + the family's own out-of-fold `alpha` line search — **0 gradient
steps**), `S3/S4 blend_raw/blend_lsi` (`lam` and floor `base` on calib),
`S5 free_joint` (joint `(k, base, lam)` on calib, nothing fitted), against the
shipped `S6 arm` / `S7 scored`. Then ATTRIBUTES the scored arm's test-side
improvement over `S0` to {closed-form stage, gradient stage, blend stage} in
percent, in skill units (`nRMSE / copy-LF reference`) and in multiples of the
certified `min_claimable_effect`. Also per-rung geometry (mean cosine, amplitude
ratio, per-sample-gain-oracle = structure-only error) and the fitted transfer's
dyadic band gains `|1 + alpha·T(k)|`. Four seams (shipped calib k-sweep, frozen
floor arms, `nrmse_after_lsi` on the ladder-eval fold, shipped scored/arm nRMSE)
are RECOMPUTED and reported as `abs_dev` — the tool asserts nothing.

**Read it as.** `attribution.pct_of_total.closed_form_lsi` near 100 → the
"trained" arm is a closed-form filter with a decorative network; report the
filter, not the architecture, and treat the gradient stage as an unpaid cost.
`gradient_pct` large on ONE dataset only → a dataset-specific rescue, not a class
property (check it at 3 seeds before believing it). `delta_skill_free_minus_scored
<= 0` → the training-free selection ladder beats the trained stack outright.
Amplitude-only improvement with falling cosine → the stage is exploiting the
relative-error metric's amplitude channel (pair with
`field_error_decomposition.py`). Band gains far from 1 in the SHARP bands → the
closed-form stage is undoing an over-smoothing that the intermediate introduced.
Neighbours: `surrogate_coherence_eligibility.py` gives the training-free CEILING
for the `S2` class and this gives its realised out-of-fold VALUE against the
trained alternative; `posthoc_repair_ladder.py` asks the complementary question
from outside (predictions only, no folds); `relative_gain_units_audit.py`
converts this tool's attribution into a decision statement.

**Needs a family interface, not a prediction dump** (`--family_dir`):
`folds.make_folds`, `ladders.{cond_scaler,neighbour_order,effective_ks,ladder_b_fields}`,
`floors.build`/`floors.FLOOR_ARMS`, `lsi_filter.{fit_transfer,apply_transfer}`,
`local_corrector.fit_alpha`, `bands.band_masks`/`bands.N_BANDS`,
`upsample.upsample_fields` (the round-2 `r2s2_correctability` family and any
descendant). The diagnostics JSON must carry `M3.kstar.raw_calib_nrmse`,
`M3.{scored_rung,arm_test_nrmse,scored_test_nrmse,reference_splits,blend}`,
`M1[rung].verdict.label`, `M1c[rung].nrmse_after_lsi`. Nothing is fitted on test
and no test-side LF array is ever constructed (the test rung is built from the
TRAIN LF pool + test conditions).

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/zero_gradient_stage_ladder.py \
    --family_dir worktrees/r2s2_stacked/B2/models_r2/r2s2_correctability \
    --diag_dir "$OUTPUTS_ROOT/r2s2_stacked/B2/eval" \
    --datasets sharp__cahn_hilliard --out ladder.json
```
**One leg per dataset.** A 4-dataset invocation exceeds the 20-min turn cap, and
on a contended login shell (`nproc = 1`, load ~40) even a single dataset on the
full default `--ks 1,2,4,8,16,64,256,all` does — the cheap configuration is
`--ks <k*> --rungs kstar --gain_step 0.05 --n_lambda 5`, which leaves every seam
and the attribution exact (they do not depend on the gain/λ grids) and finishes
in minutes. Every knob is a CLI arg (`--rungs --ks --fracs --fold_seed --bases
--epochs --seed --diag_pattern --factory_root --eval_dir --stripped_data
--floors_json --copylf_json --noise_floor_json`).

**Verified.** Run 2026-08-01 from `round2/` on r2s2-B2's shipped diagnostics with
the cheap configuration above (`--datasets sharp__cahn_hilliard --ks 16 --rungs
kstar --gain_step 0.05 --n_lambda 5`; outputs kept at
`worktrees/r2s2_stacked/B2/scratchpad/register_toolcheck_ladder.{json,log}`):
`B:16` raw **0.76101**, gain 0.69858 (`a* = 1.500`), LSI **0.65160**
(`alpha = 1.000`), blend 0.65160; attribution **97.0 % closed-form / 3.0 %
gradient / 0.0 % blend** = 2.617 / 0.081 / 0.000 skill units (28.7× / 0.89× /
0× mce); `S5 free_joint` k=16 base=`zero` λ=1.00 → 0.76101 against the scored
0.64823, `delta_skill_free_minus_scored` **+2.6981**; seams
`raw_calib_max_abs_dev` **0.0**, all three frozen floors **0.0**,
`S2.seam_ladder_eval.abs_dev` **0.0** (0.6180310429001807 both sides); shipped
`rule_label_kstar` `CORRECTOR_FUTILE`. Identical to card part 6 findings T3/F3.3,
T3/F3.5 and T3/F3.7 and to the source probe's own log.

**Provenance.** `worktrees/r2s2_stacked/B2/scratchpad/reanalysis_turn_3.py`; card
`experiment_cards/r2s2_stacked/batch_2/B2.json` part 6, findings T3/F3.1-T3/F3.6
and interpretation H-STAGE.

---

## `relative_gain_units_audit.py`  *(round 2)*

**Measures.** Whether a rule of the shape *"if the available value-add is below
X, the stage is not worth building"* can be stated in this benchmark's claim
units at all. The threshold is DIMENSIONLESS (a fraction of the arm's own error);
the round's claim currency is `skill = nRMSE / copy-LF reference` above a
certified `min_claimable_effect`. The conversion factor is
`raw_nrmse / copylf_ref / mce` and it is not constant across a panel. Per dataset
the tool reports `threshold_in_skill_units` and `threshold_over_mce` (how many
minimum claimable effects the gate discards in one step),
`realised_relative_gain` / `realised_gain_over_mce`, `realised_over_calibration`
(how far the gain actually available exceeds the number the threshold was
calibrated on) and `decision_cost_skill_units` / `decision_cost_over_mce` — what
OBEYING the rule costs, i.e. the arm it selects minus the arm it rejects. Panel
verdicts: `EXPRESSIBLE`, `COARSE` (`threshold_over_mce > --coarse_factor`),
`PANEL_INCONSISTENT` (max/min ratio > `--spread_factor`), `MISCALIBRATED`
(`realised/calibration > --calibration_factor`); several can fire at once.

**Read it as.** `COARSE` or `PANEL_INCONSISTENT` → the rule **cannot be exported
as an eligibility gate**; keep it as a DIRECTIONAL predictor and price
eligibility in skill units per dataset instead. A large
`decision_cost_over_mce` is the strongest form of the failure: obeying the rule
as written throws away value the round would have certified as a claim.
`MISCALIBRATED` almost always means the calibration used a FROZEN component where
the decision applies to a REFIT one — the rule measured transferability, not
attainability. Note the asymmetry: `EXPRESSIBLE` is a statement about the
THRESHOLD's units only. It never licenses the rule's science.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
# arms.json:  {"<dataset>": {"raw_nrmse":…, "improved_nrmse":…,
#                            "rule_selected_nrmse":…, "rejected_nrmse":…,
#                            "statistic":… }}
python tools/relative_gain_units_audit.py \
    --arms arms.json --threshold_relative_gain 0.05 \
    --calibration_relative_gain 0.0008 \
    --rule_name "r2s2-B1 coherence eligibility (GAMMA_FUTILE=0.52)" \
    --out units.json
```
`raw_nrmse` is the denominator the dimensionless threshold is written against;
`rule_selected_nrmse` / `rejected_nrmse` are the two arms the DECISION picks
between (default: selected = raw, rejected = improved). `--copylf_json` and
`--noise_floor_json` default to this round's. Pure JSON arithmetic, < 1 s, no
data or model access — it can audit a rule from another stream's numbers.

**Verified.** Run 2026-07-31 from `round2/` on the r2s2-B1 coherence eligibility
rule with r2s2-B2's four sharp-panel arms (inputs/outputs kept at
`worktrees/r2s2_stacked/B2/scratchpad/register_toolcheck_{arms,units_audit}.json`):
`threshold_over_mce` **10.8 / 10.0 / 816.6 / 11.8** (allen_cahn / cahn_hilliard /
fisher_kpp / pfc), spread **81.9×**, `decision_cost_over_mce` **21.9 / 29.6 /
116.1 / 8.8**, `realised_over_calibration` **41.2 / 179.7 / 6.9 / 46.4**, panel
verdict **COARSE + PANEL_INCONSISTENT + MISCALIBRATED**. Identical to card part 6
findings T3/F3.7-T3/F3.9.

**Provenance.** `worktrees/r2s2_stacked/B2/scratchpad/reanalysis_turn_3b.py`;
card `experiment_cards/r2s2_stacked/batch_2/B2.json` part 6, findings
T3/F3.7-T3/F3.9 and interpretation H-RULE-UNITS.

---

## Standing amendment the r2s2-B2 tools make to `surrogate_coherence_eligibility.py`

*(This does not rewrite the r2s2-B1 entry above; it records what r2s2-B2 measured
about the rule that entry ships.)*

`surrogate_coherence_eligibility.py`'s `CORRECTOR_ELIGIBLE` / `CORRECTOR_FUTILE`
LABELS are **not usable as a gate on the round-2 panel**, for three separately
measured reasons (card `r2s2_stacked/batch_2/B2.json` part 6, H-RULE-UNITS).
(1) **Centring.** The gamma statistic must be computed on ensemble-CENTRED fields
and its ceiling taken over the AFFINE class the corrector actually spans; the
uncentered form degenerates to the target's mean-energy share when the input is
dominated by a row-invariant field (r2s2-B2 turn 1: centring moved gamma from
0.16 to 1.00 on the `B:all` rungs and flipped every verdict there).
(2) **Frozen vs refit.** `GAMMA_FUTILE = 0.52` was calibrated on a FROZEN
corrector at "value-add ≤ 0.08 %"; a REFIT closed-form LSI at centred gamma
0.10–0.35 removed 0.55–14.38 % of the test error, 7–180× that bound.
(3) **Units.** The rule's 0.05 relative-gain floor is worth 0.58–9.47 skill units
across the sharp panel — 10× to 817× the certified `min_claimable_effect`, and
82× inconsistent between datasets. Applied as written it labelled every scored
rung of r2s2-B2 `CORRECTOR_FUTILE` and obeying it cost 8.8–116× mce.

**Standing rules this leaves.** (a) The coherence statistic stays useful as a
DIRECTIONAL predictor (high centred gamma → large corrector value-add) — never as
an eligibility gate. (b) Any dimensionless threshold, in any stream, gets run
through `relative_gain_units_audit.py` before it is exported. (c) Before
attributing a stacked arm's number to its trained stage, run
`zero_gradient_stage_ladder.py`: on this panel 33–100 % of the scored gain was a
zero-gradient closed-form Wiener filter and the gated CNN was rejected out of
fold (`alpha_nn = 0`) on 5 of 8 rung cells. (d) Never build a ladder rung that is
leave-one-out on TRAIN and no-self on TEST (r2s2-B2's `B:all`): it is train/test
inconsistent by construction and it fooled three independent clauses at once.

---

## `effect_threshold_readings.py`  *(round 2)*

**Measures.** For a paired A-vs-B contrast measured over REPEATED TRAINING SPLITS
(HF-subset draws, folds, restarts), whether the effect is claimable — and whether
that answer survives a change in how the threshold is read. It separates the two
variance components cards routinely conflate:

- **test-sample** variance (conditional on one split): paired per-sample delta
  `(rel_l2^A_i − rel_l2^B_i)/D`, bootstrap CI over the shared test set, and the
  fraction of test samples the treatment improves;
- **split** variance: per-split effect, its max−min range, the unbiased sd that
  range implies at this `n` (control-chart `d2`), the SE of the split-mean,
  `t = effect/SE`, each arm's own split range and CV, the arm-instability ratio,
  and the whole comparison re-expressed in **log-score** units (the native units
  of a geometric-mean panel metric).

Then it recounts the verdict under **seven readings**: `verbatim_max_mce_spread`,
`mce_only`, `paired_se_over_splits` (`max(mce, 1.96·SE)`),
`persample_ci_excludes_zero`, `median_stat_verbatim`, `worst_split_vs_mce`, and
`log_effect_vs_own_range` — reporting `readings_agree`, `n_readings_pass` and
`mce_over_observed_split_range`.

**Why.** r2s3-B3's primary clause sat exactly on a knife edge: `max(mce, in-job
range)` gave 3/6 datasets passing (FALSIFIED) and `mce` alone gave exactly 5/6
(CONFIRMED at the minimum margin). The tool turns that from an adjudication into
an observation. The decisive fact it surfaces is `mce_over_observed_split_range`:
B3's certified constant came from 3 TRAINING SEEDS of a full-400-row model and
was **0.0012×** the split-to-split range of the control arm it was applied to —
i.e. the `mce`-only reading priced the card's dominant noise source at zero.

**Read it as.** `readings_agree = true` → quote the verdict and move on.
Disagreement confined to the readings that price split variance → the card is
measuring a **variance-reduction** effect and the gate has inherited the CONTROL
arm's instability; the better the treatment works as a stabiliser, the harder the
gate becomes. Prefer `worst_split_vs_mce` (the effect must clear the certified
constant on EVERY split): same conservatism, no coupling between the effect and
its own dispersion. `mce_over_observed_split_range` « 1 is a provenance smell —
check which axis the constant was certified on before quoting it.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/effect_threshold_readings.py --dataset sharp__allen_cahn_2d \
    --arm A0_nolf=<outputs>/results_ac_A0_d0/<fam>/<ds>_e200_s0.json,<...d1>,<...d2> \
    --arm A1_lf_cov=<outputs>/results_ac_A1_d0/<fam>/<ds>_e200_s0.json,<...d1>,<...d2> \
    --contrast A0_nolf:A1_lf_cov --noise_floor state/noise_floor.json \
    --out readings.json
```
`--arm NAME=leg.json[,leg.json...]` repeatable, one leg per split; legs must
carry `splits.<--split>.rel_l2_per_sample` (any `score_panel.py` result JSON
does) and share a test set. Threshold from `--mce` or
`--noise_floor <path> [--mce_key]`; denominator from `state/anchors/floors.json`
unless `--skill_denominator`. Knobs: `--split` (default `test_hf`), `--n_boot`,
`--seed`. Pure numpy, ~2 s on the login node.

**Verified.** Run 2026-08-01 from `round2/` on r2s3-B3's shipped legs.
`sharp__allen_cahn_2d`: per-split effect 761.903 / 36.2541 / 98.5502, mean
298.9024, range 725.6489, `sd_hat` 428.7261, SE 247.5251, **t 1.21**, arm
instability 1773.0×, `mce_over_observed_split_range` 0.00121, readings
3/7 pass (`mce_only`, `worst_split_vs_mce`, `persample_ci_excludes_zero`),
`readings_agree = false`. `sharp__cahn_hilliard`: effect 14.7762, range 5.2888,
t 8.19, **7/7 pass, `readings_agree = true`**. Every point statistic matches the
source probe (turn 1 findings 1/2/4/5/7) exactly; the bootstrap CI matches to
Monte-Carlo error only (206.22–408.80 here vs 208.44–404.75 in the probe — same
seed, different RNG draw order).

**Provenance.** `worktrees/r2s3_lf_train_signal/B3/scratchpad/reanalysis_turn_1.py`;
card `experiment_cards/r2s3_lf_train_signal/batch_3/B3.json` part 6, findings
T1-2 … T1-8 and interpretation M0.

---

## `map_dispersion_scale_shape.py`  *(round 2)*

**Measures.** Training-free, from prediction dumps only: across repeated training
splits, how far apart are an arm's learned maps, and is the difference SCALE or
SHAPE? Per arm, per split-pair `(d, d')`, per test sample:
`cos(p_d, p_d')`, the gain ratio `‖p_d‖/‖p_d'‖`, the total dispersion
`‖p_d − p_d'‖/‖y‖`, and the **shape-only** dispersion
`min_a ‖a·p_d − p_d'‖/‖y‖ = √(1−cos²)·‖p_d'‖/‖y‖` — what survives the best
possible per-sample rescale. Reported in `‖y‖` units and in skill units, so the
dispersion is directly comparable with the arm's own error. Plus, per arm: each
split's score at the **ORACLE per-sample gain** (a ceiling, never an arm score)
with `gain_channel_share_of_skill_range` — how much of the score's split-range is
the amplitude channel alone — and, with `--ensemble`, the **split-ensemble** arm.

**Why.** When a treatment makes an arm's SCORE stable across splits, the natural
story is "it makes the learned function split-independent". On r2s3-B3 that story
was wrong in a specific, reusable way: the LF arm's three `allen_cahn` models
scored within 0.41 skill units of each other while sitting **100.5 skill units
apart** in function space (inter-split cosine 0.9485). What the treatment pinned
was the output AMPLITUDE — **96.9 %** of the control's 726-unit split-range was
one scalar per sample. Any design that assumes a canonical treated map
(single-teacher distillation, weight averaging, "the" regularised solution) is
assuming something this measurement can refute in minutes.

**The ensemble arm is an upper bound, not a control.** It sees every split's
training rows and `n_splits ×` the compute, so it is NOT budget-matched and is
usable in one direction only: a treatment that still beats it is not doing
variance reduction; a treatment that LOSES to it has a cheaper alternative. On
r2s3-B3 the 3-split ensemble of the no-LF arm lost to the LF arm by +219.17
(allen_cahn) and +11.78 (cahn_hilliard) but **beat** it on fisher_kpp (13.378 vs
14.991) and pfc — which is how the card learned that LF supply was the wrong
lever on those two datasets.

**Read it as.** `shape_share_of_dispersion` near 0 → the splits differ by a scale
factor and nothing else; near 1 → genuinely different functions.
`gain_channel_share_of_skill_range` near 1 → the arm's split instability is an
amplitude-calibration artifact and a post-hoc per-sample gain would remove it
(check `gain_channel_share_valid`; the share is meaningless when an arm's raw
range is already below its oracle-gain range). Score stable + dispersion large →
the treatment pins the error LEVEL, not the map.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/map_dispersion_scale_shape.py --dataset sharp__allen_cahn_2d \
    --arm A0_nolf=<outputs>/results_ac_A0_d0/<fam>/<ds>_e200_s0_preds.npz,<...d1>,<...d2> \
    --arm A1_lf_cov=<outputs>/results_ac_A1_d0/<fam>/<ds>_e200_s0_preds.npz,<...d1>,<...d2> \
    --ensemble --out dispersion.json
```
`--arm NAME=pred.npz[,pred.npz...]` repeatable (`.npy` or `.npz:key`, default key
`pred_test`); fields `(N,H,W)` or `(N,n_cells)`. Targets from
`round2/eval/panel_data.py` (offline reference path, read-only) unless
`--targets path[:key]`. Knobs: `--key`, `--skill_denominator`, `--max_test`,
`--ensemble`. Pure numpy. **Runtime is I/O-bound, not CPU-bound**: 2 arms × 3
splits at 100 × 256² is ~6 s of compute but ~1 m 45 s wall on the shared login
filesystem (6 × 52 MB npz). The login shell is nproc-limited (see r2s2-B2's
register note) — for more than ~4 arms × 4 splits at 256², run it from a batch
step or cap with `--max_test`.

**Verified.** Run 2026-08-01 from `round2/` on r2s3-B3's shipped dumps.
`sharp__allen_cahn_2d`: A0_nolf cos 0.6273 / gain ratio 1.7941 / `D_tot` 1.2451 /
`D_shape` 0.3316 (26.6 % shape) = 699.18 skill units; A1_lf_cov 0.9485 / 0.9620 /
0.1789 / 0.1664 (93.0 %) = 100.47; A0 skill range 726.058 → 22.629 at oracle gain
(**gain share 96.9 %**); split-ensemble 431.799 (A0) vs 203.738 (A1).
`sharp__fisher_kpp_2d`: A0 95.3 % shape, gain share 55.5 %, ensemble 13.378 vs
the A1 split-mean 14.991. All match the source probe (turn 3 findings T3-1, T3-3,
T3-5) exactly.

**Complements, does not duplicate.** `field_error_decomposition.py` (r1) splits ONE
predictor's error into amplitude vs structure against the target; **this tool**
splits the disagreement BETWEEN training splits of the same arm, which is the
quantity a variance-reduction claim is actually about.
`null_family_ceiling_audit.py` asks where an arm's error sits relative to its
design's null space; `effect_threshold_readings.py` asks whether the resulting
arm-vs-arm gap is claimable.

**Provenance.** `worktrees/r2s3_lf_train_signal/B3/scratchpad/reanalysis_turn_3.py`
(dispersion, oracle-gain ladder, ensemble) and `.../reanalysis_turn_2_pfc.py`
(the per-sample gain/cosine decomposition); card
`experiment_cards/r2s3_lf_train_signal/batch_3/B3.json` part 6, findings T2-5,
T3-1, T3-2, T3-3, T3-5 and interpretations M1, M1b, M5.

---

## `ledger_contamination_audit.py`  *(round 2)*

**Measures.** For any paired-arm reading `delta = skill(baseline) - skill(arm)`
adjudicated against a threshold, the two ways that reading can be an artifact.

- **Could it have fired?** With
  `D(a,b) := mean_i ||a_i-b_i||_2 / ||y_i||_2 / skill_denominator` (the round's
  nRMSE kernel with the TRUTH denominator held fixed, so a
  prediction-to-prediction distance is on the same scale as either one's
  distance to the truth), the triangle inequality gives
  `|delta| <= D(arm, baseline)` **identically**. `headroom = ceiling/threshold`;
  `could_not_fire` fires when headroom < 1, i.e. the clause was arithmetically
  incapable of breaching and its surviving null is guaranteed by construction.
- **Is it contaminated?** With a `--control` column (the ARM's estimator fitted
  on the SAME rows but on the BASELINE's target),
  `delta = [skill(baseline) - skill(control)]` (**function-class term**)
  `+ [skill(control) - skill(arm)]` (**target term**). Only the target term
  answers "what did the treatment's target buy"; the function-class term is an
  architecture comparison that survives deleting the treatment.
  `contaminated_fraction > 0.5` raises `CONTAMINATED`.
- **Row-count bias.** `--matched` (the arm refitted at the baseline's row count)
  prices the sample-size asymmetry and raises `ROW_COUNT_ARTIFACT` when the
  reading clears its threshold unmatched and fails matched.

Also reports the mean per-sample cosine between the two arms' error fields
(≈1 ⇒ the arms are the same function making the same mistakes).

**Why.** r2s4-B3's ledger read `advantage_reachable = skill(T0) - skill(proj_best)`
and fired its F3 clause. Turn 1 found the one estimator that would have flipped
the verdict (`proj_ridge` on `sharp__cahn_hilliard`, +0.247047 vs a 0.184746
threshold); turn 2 showed 72 % of that was the 320-vs-280 row asymmetry and
99.2 % of the remainder was function class. The exhibit for why the raw quantity
is unsafe is helmholtz, where the two terms were **-21.721113** and
**+21.047550** skill units and nearly cancelled — the reported -0.673563 was the
residue of two large unrelated effects. Separately, the ceiling reading showed
pfc's F1 cell could never have breached (`headroom` 0.265) while the
F3-adjudicating cell had real headroom (5.751), so the two nulls are NOT equally
informative.

**Read it as.** No flag → quote `delta`. `COULD_NOT_FIRE` → the cell is not
evidence, drop it from the "n of m clauses survived" count rather than reporting
it as a survival. `CONTAMINATED` → quote `decomposition.target_term`, never
`delta`; and note that when the arm's estimator IS the baseline's (same
architecture, budget and rows) the function-class term is identically zero, so
that column was already clean. `ROW_COUNT_ARTIFACT` → the effect is a sample-size
bias; match `n_fit` before any claim.

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/ledger_contamination_audit.py \
    --truth  <outputs>/preds_oof_<ds>_e200_s0.npz:hf_true \
    --baseline T0=<same npz>:T0_cond_only \
    --arm      ridge=<same npz>:proj_ridge \
    [--control ridge_on_hf=<control npz>:pred] \
    [--matched ridge_n280=<matched npz>:pred] \
    --dataset <ds> --threshold <skill units> --out audit.json
```
`NAME=path.npz[:key]` everywhere (key defaults to `pred`), so BOTH dump layouts
work: one npz holding every arm (r2s4) or one npz per arm (r2s1). Threshold from
`--threshold`, or `--noise_floor state/noise_floor.json --dataset ...`.
Denominator from `eval/copylf_baselines.json` via `--dataset`, or
`--skill_denominator`. Pure numpy on the login node, ~2-15 s per dataset —
it does no fitting, so the `nproc`-1 contention that kills forward-pass tools
(see the `condition_predictability_ceiling_fast.py` cost note) does not bite.
The one real cost is memory: it holds 4 arrays of `(N, n_cells)` float64
simultaneously (~840 MB at 400×256²), so pass a sample subset on bigger dumps.

**Verified.** Run 2026-08-01 from `round2/`. (a) **On data it was not developed
on** — r2s1_direct-B3's `ext__helmholtz_2d` test dumps (different card, different
npz layout, one file per arm): `ref_decoder_big` 3.532216 vs
`stage_blend_decoder` 3.344110, delta 0.188106, ceiling 1.865910, headroom
0.6319 → `COULD_NOT_FIRE`; with `stage_wiener_decoder` as control, function-class
term +0.225449 vs target term -0.037342 → `CONTAMINATED` (85.8 %),
`identity_residual` exactly 0.0. (b) **Regression against the source card** —
r2s4-B3 `sharp__cahn_hilliard`, baseline `T0_cond_only` / arm `proj_ridge`:
skill 13.418637515037988 / 13.171591306116005, delta 0.24704620892198292,
ceiling 5.183183702052, headroom 28.0557, all matching card part 6 findings T1-2,
T1-6 and turn 1's `D(proj_ridge, T0)` = 5.183184 exactly.

**Provenance.** `worktrees/r2s4_diag/B3/scratchpad/reanalysis_turn_1.py` (ceiling,
headroom, error-field cosines) and `.../reanalysis_turn_2.py` (row-count and
capacity controls); card `experiment_cards/r2s4_diag/batch_3/B3.json` part 6,
findings T1-2 … T1-6 and T2-1 … T2-5, interpretations 1-3.

---

## `band_retention_probe.py`  *(round 2)*

**Measures.** Per log-spaced radial wavenumber band, from prediction dumps only:
`hf_energy_share` (where the truth's energy actually lives),
`retained_energy_ratio = E_arm(b)/E_truth(b)` (does the arm produce energy in
this band at all), and the decisive `band_relative_error = E_{truth-arm}(b)/E_truth(b)`
— **1.00 means the arm contributes EXACTLY ZERO useful energy in that band**
(identical to predicting zero there), > 1 means it injects wrong energy, « 1
means the band is genuinely reconstructed. Raises
`contributes_nothing_above_lowest_band` when that holds in every live band.
`--advantage A:B` adds the per-band share of `E_{truth-A}(b) - E_{truth-B}(b)`,
i.e. WHERE an arm-vs-arm gap lives, with a `localised` flag.

Real `rfft2` with the Hermitian double-count correction on interior columns, so
band energies are exact. Bands below `--min_energy_share` are flagged
`meaningless` (round-off; ratios there routinely reach 1e9) and excluded from
verdicts.

**Why.** r2s4-B3's condition-only arm posted skills of 11-148× copy-LF, which
reads as "a model doing poorly". The band audit showed its `band_relative_error`
is **~1.00 in every band above the lowest** on 3 of the 4 sharp datasets
(pfc 1.20/1.04/1.00/1.01/1.77; allen_cahn 1.03/1.01/1.01/1.01/1.08; fisher_kpp
1.01/1.00/1.00/1.00/1.00) while the LF field reproduces the truth to 1e-2-1e-16
band relative error — not a model doing poorly, a model contributing nothing
above the spatial mean, and the panel's whole gap is realisation structure
carried only by LF. The same probe located the LF teacher's advantage to 1-2
bands (83-100 % of it, a quantitative target for spectral gating) and explained
a primary arm losing to its own zero-field floor (it retained 0.5 % of the
truth's energy in EVERY band, i.e. it had collapsed toward zero).

**Read it as.** `contributes_nothing_above_lowest_band` → the arm is a
spatial-mean predictor; no amount of tuning inside that function class is the
lever, and any claim about its "structure" is unfounded. Compare the retained
ratio of a privileged arm against it to see the information the score cannot
resolve. `advantage.localised` → a band-selective architecture (gate those
bands, learn only a correction) has a quantified target; spread → it does not.
Read `band_relative_error` against `hf_energy_share`: a spectacular ratio in a
band holding 1e-9 of the energy is nothing (use `band_weight_counterfactual.py`
to price it).

**Invoke.**
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/band_retention_probe.py \
    --truth <outputs>/preds_oof_<ds>_e200_s0.npz:hf_true \
    --arm T0=<same npz>:T0_cond_only --arm I1=<same npz>:I1_lf_teacher \
    --dataset <ds> [--advantage T0:I1] [--bands 8] [--grid HxW] --out bands.json
```
`--arm NAME=path.npz[:key]` repeatable; 2-D datasets only. Grid from
`data_adapters.geometry.resolve_grid`, else `--grid`, else the square root.
Knobs: `--bands`, `--min_energy_share`, `--dc_tol` (how close to 1.00 counts as
"contributes nothing"), `--skill_denominator`. Pure numpy FFT on the login node,
~5 s (96²×100) to ~110 s (256²×400 with 3 arms) per dataset — comfortably inside
a 20-minute cap, unlike any tool that refits an estimator per fold (see the
standing note below).

**Verified.** Run 2026-08-01 from `round2/` **on data it was not developed on** —
r2s1_direct-B3's `ext__helmholtz_2d` test dumps (96², 100 rows, one npz per arm):
`ref_decoder_big` retained 1.283/0.044/0.011/…, `stage_blend_decoder` retained
**0.000 in all 8 bands** with `band_relative_error` exactly 1.000 everywhere →
`contributes_nothing_above_lowest_band` fired, and the `ref-blend` advantage came
out BAND-LOCALISED with band 0 carrying 115.9 %. Follow-up confirmed the flag is
literally true: that arm's `pred` array has `max|pred| = 0.0` and its skill
3.3441095587226317 equals r2s4-B3's certified helmholtz `ref_zero` floor
3.3441095587226317 to every digit — **the tool detected a zero-field arm in
another stream's shipped dump on its first foreign run**. Reported to r2s1 as a
cross-stream note; not adjudicated here.

**Provenance.** `worktrees/r2s4_diag/B3/scratchpad/reanalysis_turn_3.py`;
card `experiment_cards/r2s4_diag/batch_3/B3.json` part 6, findings T3-1 … T3-6
and interpretation 4-5.

---

## Standing note the two r2s4-B3 tools encode

**A ledger quantity is only as trustworthy as the estimator symmetry behind it.**
Both tools exist because r2s4-B3's `advantage_reachable = skill(T0) - skill(proj_best)`
looked like one number and was two. The rule they encode, for any card that
compares arms produced by different procedures:

1. Before reading a difference against a threshold, check the **ceiling**
   `D(armA, armB)`. If it is below the threshold, the comparison cannot fire and
   a surviving null is not evidence (`ledger_contamination_audit.py`).
2. If the two arms come from different estimators, ship the **control column**
   (each estimator also fitted on the other's target) or the difference is
   uninterpretable. When the estimators match, the function-class term is
   identically zero and no control is needed — that symmetry is a feature to
   design for, not an accident.
3. Match `n_fit` across arms, or price the gap explicitly. r2s4-B3's 320-vs-280
   asymmetry alone moved a falsification clause across its threshold.
4. Before concluding an arm "predicts structure badly", check that it produces
   structure at all (`band_retention_probe.py`). A `band_relative_error` of 1.00
   is not a bad prediction, it is no prediction.

**Row-order caveat both tools carry.** Prediction dumps are not always in dataset
row order — r2s4-B3's `preds_oof_*.npz` carry an `oof_row_index` PERMUTATION
(`[2, 5, 18, 19, 36, …]`). Both tools only ever compare arrays taken from the
dumps passed on the command line, so they are safe by construction; a probe that
joins a dump to loader-ordered data (LF fields, conditions, params) must permute
first and assert against a pre-registered value. r2s4-B3 turn 3 hit exactly this
and the card's own `prereg_*.json::copylf_train_rel_l2_mean` caught it — that
pre-registered column is a cross-check on downstream ANALYSIS, not just on the
experiment, and is worth reproducing to `rtol=1e-6` in any probe that touches LF.

---

## `gain_head_feasibility_audit.py` (r2s3_lf_train_signal-B4 turns 1-2)

**Question.** Two failures that keep being misread as physics:
*"the calibration head does nothing"* and *"the test-fitted gain ceiling absorbs
X % of the effect"*. Both are routinely instrument artifacts, and this tool
always ships the zero-information null next to the instrument.

| field | meaning |
|---|---|
| `label_degeneracy.c_fit` / `c_eval` / `sd_log_ratio_fit_over_eval` | spread of the per-sample optimal scale `c_i = <p_i,y_i>/‖p_i‖²` on the head's FIT rows vs the EVAL rows. **A ratio near zero means no head of any class can be anything but the identity** — the arm interpolated its fit rows, so the calibration label is a constant |
| `train_fitted_head.R2_vs_true_eval_loggain` / `gain_spread_sd_log` | is the achievable head anti-informative, and is the gain it emits literally constant? |
| `labelled_holdout_learning_curve[n]` | the SAME head class refitted on `n` random EVAL rows WITH REAL LABELS, scored on the remainder: `absorbed_of_oracle` and held-out `R2`. Plateau height = class capacity; curve shape = sample-size cost; the gap to the shipped head's 0.000 = label degeneracy. **A counterfactual price for labels, never an achievable score** |
| `ceiling_reread.law_clipped` / `law_unclipped` / `null_constant_at_clip_lo` / `null_best_constant` | the LOO-on-eval ceiling clipped and unclipped, against two gains carrying NO condition information |
| `ceiling_reread.null_over_law` | **≈1 ⇒ the ceiling number IS the clip.** On r2s3-B4, 6 of 16 draws were bit-identical to a constant gain of 0.5 |
| `verdict` | `DEGENERATE_FIT_SET` / `CLIP_ARTIFACT_CEILING` / `LAW_LEARNABLE` / `NO_LAW` (thresholds `--degenerate_ratio`, `--null_share`, `--r2_learnable`) |

```bash
python tools/gain_head_feasibility_audit.py \
    --preds <arm>_preds.npz --dataset ifc_poisson \
    --floors_json state/anchors/floors.json --out gain_audit.json
# or: --targets_npz t.npz --targets_key y_test (skips the panel loader entirely)
# npz key overrides: --key_pred_test/--key_cond_test/--key_pred_fit/--key_target_fit/--key_cond_fit
```

Head conventions (log-space fit, unpenalised intercept, exact-LOO/PRESS λ,
clipping on law-keyed heads only) are inherited from
`gain_calibration_ceiling.py` via B4's `heads.py`. Scoring is `eval/nrmse.py`;
a closed-form `‖g p − y‖/‖y‖ = √(g²a − 2gb + c)/√c` identity is asserted against
it at `g = 1` (`gram_seam_abs < 1e-10`) before any rescale is scored, so 8 800
rescored subsets never rebuild a field array.

**Verified.** Run 2026-08-01 from `round2/` **on data it was not developed on** —
r2s3-B2's `r2s3_null_supply` arms, a different card and a different family:
`ifc_A5` → `CLIP_ARTIFACT_CEILING` + `NO_LAW` (`null_over_law` 1.0008, clip
fraction 0.961, learning-curve R² plateau −0.045), `ch_A2_s1` →
`DEGENERATE_FIT_SET` + `CLIP_ARTIFACT_CEILING` + `NO_LAW` (sd-log ratio 1.52e-04,
`null_over_law` 1.186). Regression against its provenance card reproduces
r2s3-B4 turn 1/2 exactly on B3's `ifc_A0`: sd-log ratio 3.3675069053836957e-06,
head R² −0.038301842014462295, plateau 0.9268173107474013, `null_over_law`
−1.1105616959545868.

**Runtime.** Arithmetic is seconds; wall time is the panel loader (~1.6 min for
16 legs of 100×65536). Use `--targets_npz` to skip it. `--dataset` materialises
every fidelity through `panel_data.load_split` and drops the non-HF ones — this
is NOT the structural LF-poisoning of B4's `lf_guard.py`; use that module when
you need an auditable no-LF claim.

---

## `effect_concentration_audit.py` (r2s3_lf_train_signal-B4 turns 2-3)

**Question.** A dataset-level effect in skill units is a MEAN over per-sample
relative errors. Two effects that pass the same primary reading can be a
typical-sample claim and a six-sample claim. This tool separates them, on the
SAMPLE axis (complementing `effect_threshold_readings.py`, which works the
draw/split axis) — and it works with a single split.

| field | meaning |
|---|---|
| `effect.E` / `E_over_mce` | `mean_i (rel_i(baseline) − rel_i(treatment))/denom` — exactly the skill-unit effect, by construction |
| `effect.median_over_mce` / `win_rate` / `sign_test_p` | the TYPICAL sample's effect, the fraction of samples actually improved, and an exact two-sided binomial sign test. **A median exceeding the mean = favourably skewed, not tail-carried** |
| `concentration.share_of_positive_top{1,5pct,10pct}` / `n_samples_to_halve_E` | how few samples carry the claim (NaN when the effect is not positive — a share of a negative total is not a share) |
| `trim.top{5,10}pct.E_over_mce` | the effect after DELETING the most favourable 5 / 10 % of samples. **Below 1.0 = the claim does not survive an adversarial trim** |
| `amplitude_vs_structure.E_struct` / `E_amp` / `amplitude_share` | the effect surviving perfect per-sample amplitude calibration on BOTH arms (`rel^struct = √(1−cos²)`). `E_struct < mce` ⇒ the effect was amplitude all along. **Mechanism decomposition of an arm-vs-arm contrast — not priced against any control class** |
| `arm_anatomy.*` | per arm: median/p10 cosine with the truth, `frac_cos_below_0.3`, `‖p‖/‖y‖`, and the across-sample fluctuation ratio (`≪1` = regressed toward the conditional mean) |
| `verdict` | `NEGATIVE_EFFECT` / `NOT_SIGN_SIGNIFICANT` / `TAIL_BORNE` / `BROAD_BASED` / `AMPLITUDE_ONLY` |

```bash
python tools/effect_concentration_audit.py \
    --baseline control_preds.npz --treatment treatment_preds.npz \
    --dataset sharp__cahn_hilliard \
    --floors_json state/anchors/floors.json \
    --noise_floor_json state/noise_floor.json --out effect_audit.json
```

**Verified.** Run 2026-08-01 from `round2/` **on data it was not developed on** —
r2s3-B2 arm pairs: `ifc A5→A0` → `BROAD_BASED` (E 28.18 = 30.05× mce, win rate
0.992, top-10 % share 0.201, 10 %-trim 26.72× mce), the reversed direction →
`NEGATIVE_EFFECT` with the concentration shares correctly NaN, and
`ch A2_s1→A0_s0` → `NEGATIVE_EFFECT` (−185.2× mce, win rate 0.06). Regression
against its provenance card reproduces r2s3-B4 turns 2-3 exactly on B3's
`ch A0_d0 → A1_d0`: E 17.443643917468442, E/mce 191.1729562253453, median/mce
204.63761340473863, win rate 0.91, top-10 % share 0.18344235614450372, trims
181.29 / 172.40× mce, amplitude share 0.3461251574841438, `E_struct` 125.00× mce.

**Runtime.** Seconds of arithmetic; the panel loader dominates (~15-30 s per
dataset). Same `--targets_npz` escape and the same `load_split`-materialises-
every-fidelity caveat as `gain_head_feasibility_audit.py`. The two arms must be
scored on the same test split in the same row order — the tool checks shapes but
cannot check provenance, so the `preds_oof_*` row-permutation caveat in the
r2s4-B3 standing note applies here too.

---

## Standing rule the two r2s3-B4 tools encode

**Publish the zero-information null next to any diagnostic number a card GATES
on.** r2s3-B4 produced three readings that were shaped by the instrument rather
than by the data, and each needed its own null to expose:

1. *"The achievable calibration heads do nothing"* — true, but because their fit
   rows were informationally empty (`sd(log c) ≤ 2.0e-06`), not because the head
   class was weak. Null: refit the SAME class on real labels
   (`labelled_holdout_learning_curve`). It reaches R² 0.927 on ifc.
2. *"The test-fitted ceiling absorbs 26.9 % / 44.3 % / 69.7 %"* — on ch, ac and
   hz those numbers are bit-identical to a constant gain of 0.5, because the
   `[0.5, 2]` clip bound on 89-100 % of samples and the law never evaluated.
   Null: `null_constant_at_clip_lo`. **Exact minimisers (`global_test`,
   `per_sample_oracle`) are unclipped by construction and need no caveat.**
3. *"The effect is N× the certified mce"* — a mean over a concentrated
   distribution. Nulls: the sign test (does the MEDIAN sample benefit?) and the
   adversarial trim (does the claim survive deleting its best 5 %?). On ifc the
   answer to both is no, while its paired bootstrap CI still excludes zero — and
   that disagreement is the finding, not a defect.

Corollary for card design: a falsification clause written against a memorization
statistic (r2s3-B4's F3) can be *inverted* by the mechanism it was meant to
police — memorization was not the threat to the reading, it was the reason the
whole achievable head class was vacuous. Check which side of the clause the
mechanism actually lands on before reading a surviving null as evidence.

---

## `hf_row_shapley_value.py`

**Measures.** What each TRAINING ROW (atom / source / rung) is actually worth,
from an **exhaustive** `C(m, n)` subset dump. With every coalition trained, the
game `v(S) = value of training on subset S` is known everywhere, so the Shapley
value is closed-form — no sampling, no surrogate, no retraining.

| key | meaning |
|---|---|
| `scalar_shapley.phi` / `phi_share_pct` / `phi_in_mce_units` | each player's exact value in the dump's own metric, its share, and its size in claim units; `efficiency_check_sum_phi_minus_v_full` must be 0 |
| `marginals_by_coalition_size` | mean marginal contribution at every `|S|`. **A FLAT profile is a COMPLEMENT** (value that does not decay as the coalition grows); a profile decaying to ≤ 0 is a substitute/passenger |
| `leave_one_out` | every `(m-1)`-player design scored, best/worst named, and `redundant_players_negative_marginal_at_full` |
| `complement_signature` | is the top player the WORST alone and the BEST in company? |
| `per_sample_shapley` | the same exact Shapley on the per-test-sample error vector |
| `nn_partition.concentration_ratio` | ≫ 1 ⇒ the player buys COVERAGE of a test region no other player serves; `interference_test.interferes_off_partition` ⇒ it costs the rows it does not serve |
| `channels` | (`--channels`) row value split into AMPLITUDE vs STRUCTURE on the energy-metric twin, with an additivity check; `players_with_negative_structure_value` |
| `coverage_spearman.spearman_vs_phi` | **the headline warning**: rank correlation of each descriptive statistic (NN share, solo value, anything in `--descriptive_json`) against measured value |
| `verdict` | `COVERAGE_ANTI_INFORMATIVE` / `REDUNDANT_PLAYER` / `TOP_PLAYER_IS_COMPLEMENT` / `NO_FLAG` |

**Read it as.** `COVERAGE_ANTI_INFORMATIVE` ⇒ do **not** select or weight
training rows on a representativeness statistic on this dataset — it picks the
wrong rows. A flat marginal profile plus a high `concentration_ratio` is data
GEOMETRY, not estimator capacity; confirm by re-running on a second
capacity/width arm. The tool refuses a non-exhaustive coalition set (it prints
the missing subsets and exits 2) and requires `v(empty)` to be declared, because
the Shapley axioms are meaningless without it.

```bash
python tools/hf_row_shapley_value.py \
    --legs_json <anatomy.json> --legs_path anatomy.group_A_curve \
    --value_key test_skill --zero_json_path floor_arms.skill.ref_zero \
    --filter width=32 \
    --preds_npz <preds_test.npz> --truth_key hf_true --ref 0.036 \
    --cond_train stripped_data/<ds>/train/fidelity_64/Xs.npy \
    --cond_test  stripped_data/<ds>/test/fidelity_64/Xs.npy \
    --noise_floor_json state/noise_floor.json --dataset ifc_poisson \
    --channels --out shapley.json
```

**Verified.** Run 2026-08-02 (UTC) from `round2/` and from a foreign cwd with
absolute paths, on its provenance card (r2s4_diag-B4, ifc_poisson, 31 coalitions
× 3 inits): reproduces turn 2 exactly
— `phi = {0: 3.5287, 1: 3.6169, 2: 3.7560, 3: 4.2318, 4: 4.3831}`, efficiency
`0.0`, seam `max_abs_diff_mean_persample_vs_eval_nrmse = 0.0` over 93/93 legs,
best LOO design `1234` = 8.2346 vs worst `0123` = 9.9525, row 0's marginal at
`|S| = 4` = **−0.0266** (`REDUNDANT_PLAYER`), row 4's partition concentration
2.4396 with no off-partition interference, and
`coverage_spearman.nn_share_of_test = −0.60` (`COVERAGE_ANTI_INFORMATIVE`).
`--channels` reproduces turn 3 section D: structure φ negative for rows 0-3,
positive only for row 4; full-design channel gain amplitude **+0.8637**,
structure **−0.0433**; additivity ≤ 1e-16. The abort path was exercised on the
same dump filtered to `width=8` (15 of 31 subsets missing → exit 2).

**Runtime.** Seconds (`2^m` scalar lookups; the per-sample path is `2^m × N`
vector ops). Refuses `m > 16`. **Caveats**: the value key must be the SAME metric
for every leg; a replicate mean is taken before the game is played unless you
pass `--filter` down to one replicate; the channel split lives on the
energy-metric twin and is never the round's nRMSE.

---

## `gain_channel_ladder.py`

**Measures.** Whether an arm's remaining error is a PER-SAMPLE SCALE, read
across a whole sweep rather than on one arm. Per `(group, axis)` cell:
`skill_raw`, the exact `rel_l2² = (1−g)² + ‖p − g y‖²/‖y‖²` channel split,
`skill_after_global_gain` vs `skill_after_per_sample_gain` (both ORACLES),
`frac_removed_*`, the mean gain `g`, and the across-test-row `dispersion_ratio`
(`‖P − mean_row P‖_F / ‖Y − mean_row Y‖_F`). Then the two readings that only
exist along an axis: `trend.*` (Spearman + monotonicity of the removable
fraction and of the dispersion against the axis) and `contrast.*` (matched-axis
two-group delta split by channel, with `channel_signs_disagree` when no single
share exists).

**Read it as.** `frac_removed_per_sample ≫ frac_removed_global` ⇒ the headroom
is genuinely per-sample; a global rescale, a loss reweighting or an output
scaler cannot reach it, and the arm needs a per-sample signal (LF field at
inference, a calibration head). Rising `dispersion_ratio` along a SAMPLE-COUNT
axis with a flat/inverted one along a CAPACITY axis ⇒ the conditional-mean
collapse is few-sample regularisation, not a representational limit — adding
parameters will not move it. `contrast.amplitude_share_of_penalty ≈ 0` ⇒ the
change cost SHAPE only. Verdict flags: `PER_SAMPLE_GAIN_HEADROOM`,
`GLOBALLY_MISCALED`, `COLLAPSED_TOWARD_MEAN_FIELD`, `DISPERSION_RISES_WITH_AXIS`.

**How it differs from the round-1 pair.** `field_error_decomposition.py` and
`gain_calibration_ceiling.py` price ONE prediction. This is the ladder: it reads
a whole sweep out of a multi-leg dump in one call and adds the trend and the
matched-axis channel contrast. Use those two for a single arm; use this one when
the question is "does the channel move with N / width / seed?".

```bash
# A) multi-leg dump (one npz key per leg)
python tools/gain_channel_ladder.py \
    --legs_json <anatomy.json> --legs_path anatomy.group_A_curve \
    --preds_npz <preds_test.npz> --truth_key hf_true \
    --leg_key leg --axis_key n --group_key width --metric_key test_nrmse \
    --ref 0.036 --noise_floor_json state/noise_floor.json --dataset ifc_poisson \
    --out ladder.json

# B) one arm per npz, or per KEY inside a multi-arm npz
python tools/gain_channel_ladder.py \
    --arm_npz "p.npz::armA__outer0" "p.npz::armA__outer2" \
    --labels a0 a2 --axis_values 0 2 --group_values armA armA \
    --target_key hf_true --ref 0.2990332650411058 --out ladder.json
```

**Verified.** Run 2026-08-02 (UTC) from `round2/` and from a foreign cwd with
absolute paths. On its provenance card (r2s4_diag-B4) mode A reproduces turn 3 sections C/E exactly: w32 n=5
`8.2612 → 8.2451` global (**0.19 %**) → `2.8584` per-sample (**65.4 %**),
dispersion `0.2524 / 0.3729 / 0.4378 / 0.4819 / 0.4920` at n = 1..5, w8 n=5
`8.7624 → 4.3529` (50.3 %), and the matched-n contrast reproduces the w8−w32
channel deltas (`Δamp² = +0.0121 / −0.0117 / −0.0291`, sign-mirrored because the
contrast is reported w32−w8). Seams: `max_abs_diff_recomputed_vs_declared_metric
= 0.0` against both `eval/nrmse.py` and the dump's own `test_nrmse`; identity
violation 1.8e-15. Mode B was run **on data it was not developed on** —
r2s4_diag-B3's `ext__helmholtz_2d` OOF arms — giving seam 0.0, dispersion
0.043-0.344 (`COLLAPSED_TOWARD_MEAN_FIELD` on both groups) and correctly
*declining* to flag `PER_SAMPLE_GAIN_HEADROOM` where a global rescale already
removes 59 % (`T0_cond_only` outer 0).

**Runtime.** Seconds per leg-set; dominated by loading the npz. **Caveats**: the
per-sample oracle is the exact minimiser of the round's metric so
`frac_removed_per_sample ≥ 0` always, but the GLOBAL scalar minimises total
squared error, not the mean relative norm, so `frac_removed_global` can be
slightly negative — a property of the estimator, not a bug. Both gain arms read
the test truth and are bounds, never scores. All channel quantities live on the
energy-metric twin.
