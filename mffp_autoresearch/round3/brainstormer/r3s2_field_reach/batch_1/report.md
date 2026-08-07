# Brainstormer Report — Stream `r3s2_field_reach`, Batch 1

**Stream**: `r3s2_field_reach` (gap) · **Batch**: 1 · **Total iterations**: 1 · **Slot filled**: 1/1 · **Reopen candidates resolved**: 0 (none exist)

## Slot

- **Category**: `mf_composition / completeness-conditioned re-measurement of the condition->pseudo-LF->corrector stack, with an exact zero-parameter analytic IC-synthesis front end as the matched contrast (conditioning-path vs information attribution)`

- **Card type**: `model`

- **Motivation**: the stream directive fixes batch 1 to the round-2 §12.2 stacking design, and the prior-art verdict fixes what may be claimed for it. **D2, verbatim**: *"`preempted (cite)` (mechanism); open only as a measurement | Only whether completeness changes the round-2 **attribution** (99.98% stage-1 error; corrector worth 0.0061 units). A measurement of this benchmark, never a mechanism. Note the published failure prediction in 2606.17460 weakens any positive claim in advance"* (citations: https://arxiv.org/abs/2302.12682, https://arxiv.org/abs/2310.00057, https://arxiv.org/html/2606.17460v2). **D1, verbatim**: *"`preempted-but-MF-composition-open` | No fetched source uses a **fixed exact reconstruction of a known band-limited parameterization** as an internal zero-parameter layer, and **every** parameter-conditioned emulator found still consumes a field or state at inference. The condition-only, no-field-at-test regime with N_hf in {5, 400}, LF at train only, scored in copy-LF skill units against training-free floors, is unrepresented"* (https://www.nature.com/articles/s42256-026-01267-z, https://arxiv.org/html/2603.12676, https://arxiv.org/html/2604.21753, https://arxiv.org/abs/2601.09491, https://arxiv.org/html/2509.09599, https://arxiv.org/html/2511.09729). The card therefore claims the **regime, the contrast and the attribution**, never the architecture — exactly the shape the websearcher prescribes ("Propose it only as a completeness-conditioned attribution re-measurement with the round-2 numbers pre-registered as the null"), with r2s2_stacked-B1's certified 27.5068 pre-registered as that null. Scientifically the batch is the direct test of round-2's terminal conditional: *"If the missing variable really is the realised random initial condition (ADR r2-0003), then no architecture, capacity or budget can move this panel further"* — round 3 exports that variable (reconstruction rel-L2 = 0.0), so the statement is now decidable.

- **Concrete config**: family `models_r3/r3s2_stack_ic`, vendored with provenance headers from `models_r2/r2s2_stack` @ `6b4e1d48` (itself vendoring round-1 `s4_router` @ `b90d4662`) — **declared round-1/round-2 reuse role (a): the corrector is a frozen test-time sub-component and the reuse IS the experiment (round-2 §5.10a); declare this on the card.**
  - Stage 1 (emulator): FiLM-FNO, width 64, 4 blocks, 12 modes, target `lf_native` at the top LF rung (`S6_LF_FID=max`), rel-L2 loss, one emulator per front end shared by all its stage-2 arms (in-job paired controls on identical pseudo-LF, drift-class rule).
  - Stage 2 (corrector): vendored `dc_cleaned` — closed-form LSI Wiener `T(k)` + alpha line search including 0, then `LocalCorrector` (kernel 7, depth 4, width 32, zero-init head); pseudo-LF lifted to the HF grid by the convention-keyed upsampler (`node_aligned_periodic` / `dirichlet_node` / `legacy_cell_centred`), no bare `F.interpolate`/`zoom` anywhere.
  - **Front ends** (the new contrast): **E0** = FiLM-on-condition only (literal round-2 replay, pre-registered null + replication check); **E1** = exact analytic IC synthesis channel + FiLM on the non-`ic_*` dims; **E1n** = E1 fed row-shuffled IC coefficients (zero-information null for the channel).
  - **Arms (10)**: E0 x {emul_only, frozen, finetuned, end_to_end}, E1 x {emul_only, frozen, finetuned, end_to_end}, E1n x {emul_only}, plus front-end-free `condmean_lf` (train-mean LF, the ADR r2-0003 null; frozen - condmean_lf = value of the emulator). **Scored arm = `E1/frozen`**, pre-registered; the other nine live in `diag_<dataset>_e200_s0.json::arms`.
  - **IC synthesis** (zero learned parameters, condition-only, no PDE solve): `ic_c*` indices resolved from the dataset's own `param_names`; the trigonometric sum `sum_j c_2j cos(kx X + ky Y) + c_{2j+1} sin(kx X + ky Y)` over `(kx,ky) in 0..m-1 \ {(0,0)}` with `m = round(sqrt(len(c)/2 + 1))` evaluated **analytically on each rung's node grid**, normalised by the max-abs constant computed on `res_min` — bit-faithful to the generator's `build_ic` + `spectral_interp` path (`mffp_sharp/common/ic_encoding.py`, `common/spectral.py`, read-only), with an in-job equivalence check to <= 1e-12 against the build-then-zero-pad construction. `scale` is set to 1 and recorded (a known global constant on an input channel). On ifc_poisson / ifc_heat there are no `ic_*` dims, so E1 == E0 **by explicit record** (`ic_synth_applicable: false`), never silently.
  - **Round-2 defect repairs carried**: budget-matched arms (`R3S2_BUDGET_MATCH=arm_equal_total` — the frozen arm spends its extra `E_dc` continuing on REAL LF, so A2-A3 isolates the data, not the budget: reviewer caveat F8); panel geomean reported all-6 **and** over the pairing-valid subset (B1 anomaly 2); pairing gate armed (`paired_real_lf` per dataset; an unpaired column voids that cell's attribution instead of silently re-routing the fit); zero-information nulls published next to every gated diagnostic; the closed-form alternative priced on the same intermediate out of fold with `tools/zero_gradient_stage_ladder.py` before any trained stage is credited; centred-gamma coherence kept **directional only** (r2s2-B2 stop-export), with a permutation null and an affine ceiling; `tools/target_scale_spread_audit.py` pre-flight on pfc.
  - **Mandatory floor arms on every cell**: `nn_condition`, `train_mean`, `zero` from `state/anchors_repaired/floors.json`, plus `affine_on_hf_train` on both ifc cells (round-3 affine-floor rule).

- **Recipe**:
```json
{
  "base_family": "r2s2_stack",
  "base_commit": "6b4e1d4825666e037a43675c83d9bda6289ec9d0",
  "family_dir": "models_r3/r3s2_stack_ic",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R3S2_FRONTEND": "ic_synth",
    "R3S2_ARM": "frozen",
    "R3S2_IC_SYNTH": "analytic_modes",
    "R3S2_IC_SYNTH_NORM": "res_min_maxabs",
    "R3S2_IC_SYNTH_SCALE": "1.0",
    "R3S2_IC_NAMES_FROM": "meta_param_names_ic_prefix",
    "R3S2_IC_FALLBACK": "film_only_recorded",
    "R3S2_IC_EQUIV_CHECK": "1",
    "R3S2_IC_SHUFFLE_NULL": "1",
    "R3S2_EMU_TARGET": "lf_native",
    "R3S2_EMU_RUNG": "max",
    "R3S2_EMU_WIDTH": "64",
    "R3S2_EMU_BLOCKS": "4",
    "R3S2_EMU_MODES": "12",
    "R3S2_EMU_LOSS": "rel_l2",
    "R3S2_EMU_SHARED": "1",
    "R3S2_EPOCH_SPLIT": "0.5",
    "R3S2_BUDGET_MATCH": "arm_equal_total",
    "R3S2_UPSAMPLE": "corrected_by_convention",
    "R3S2_LF_INPUT": "pseudo",
    "R3S2_CORRECTOR_FIT_ON": "real_lf",
    "R3S2_VAL_DISJOINT": "1",
    "R3S2_REQUIRE_PSEUDO_LF": "1",
    "R3S2_PAIRING_GATE": "1",
    "R3S2_PAIRED_SUBSET_GEOMEAN": "1",
    "R3S2_TARGET_SCALER_PREFLIGHT": "pfc_per_sample_if_outlier_dominated",
    "R3S2_FLOOR_ARMS": "nn_condition,train_mean,zero,affine_on_hf_train",
    "R3S2_EMU_ERROR_SIDECAR": "1",
    "R3S2_ORACLE_TRAINHELDOUT_SIDECAR": "1",
    "R3S2_CENTRED_GAMMA_SIDECAR": "directional_only_with_permutation_null",
    "R3S2_ZERO_GRADIENT_LADDER_SIDECAR": "1",
    "R3S2_IC_COS_SIDECAR": "1",
    "R3S2_BC_AUDIT_SIDECAR": "1",
    "R3S2_DIAG_OUT": "mffp_autoresearch_outputs/round3/r3s2_field_reach/B1/eval",
    "S6_VARIANT": "local_pixel_gate",
    "S6_SELECTOR": "heldout_scalar",
    "S6_PAD_MODE": "circular_if_periodic",
    "S6_PERIODIC_TEST": "wrap_continuity_ratio_hf_train",
    "S6_PERIODIC_TOL": "1.25",
    "S6_LF_SOURCE": "dataset_lf_fidelity",
    "S6_LF_FID": "max",
    "S6_KERNEL": "7",
    "S6_DEPTH": "4",
    "S6_WIDTH": "32",
    "S6_GATE_HOLDOUT_FRAC": "0.2",
    "S6_GATE_INIT": "zero",
    "S6_GATE_LINESEARCH_INCLUDES_ZERO": "1",
    "S6_LSI_RIDGE": "0",
    "S6_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S6_LEAKAGE_TRIPWIRE": "1",
    "_substrate_commit": "8aae33a7fab11ef8234f4bb7158c2bc1a8b4bf51",
    "_vendor_source": "mffp_autoresearch/round2/worktrees/r2s2_stacked/B1/models_r2/r2s2_stack @ 6b4e1d48 (smoke_eval.py, model.py::FNO2d, lsi_filter.py, local_corrector.py, bands.py, periodicity.py, upsample.py, probes.py); that family in turn vendors round-1 s4_router @ b90d4662. IC-synthesis math re-implemented from the READ-ONLY generator surfaces mffp_sharp/common/ic_encoding.py::ic_2d and common/spectral.py::spectral_interp with provenance comments (never imported, never edited).",
    "_declared_reuse": "role (a), round-2 program 5.10a: the DC-lineage corrector is a declared frozen test-time sub-component behind a new condition->pseudo-LF front end; the reuse IS the experiment. E0 is the literal round-2 replay arm and is declared as the pre-registered null, not as a novelty claim.",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. score_panel.py --datasets accepts ONLY 'panel' | 'guard' | a comma-list of dataset NAMES, so the guard run is a SEPARATE invocation with --datasets guard (smoke tier 200, seed 0). Wall-clock estimate: r2s2-B1 ran 5 arms x 6 datasets x 200 epochs in 20.1 min on one H200; this card runs 3 emulators + 7 stage-2 fits with budget matching, so budget ~50-70 min/seed and request --time 03:00:00 (>=1h => --mail-user=ezeng@caltech.edu --mail-type=END,FAIL per project.yaml sbatch).",
    "_arms": [
      {"tag": "E0_emul_only",   "R3S2_FRONTEND": "film_only", "R3S2_ARM": "emul_only",   "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "none",      "role": "round-2 replay internal floor; replication check vs certified r2s2-B1"},
      {"tag": "E0_frozen",      "R3S2_FRONTEND": "film_only", "R3S2_ARM": "frozen",      "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "real_lf",   "role": "pre-registered NULL arm (round-2 primary)"},
      {"tag": "E0_finetuned",   "R3S2_FRONTEND": "film_only", "R3S2_ARM": "finetuned",   "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "pseudo_lf", "role": "budget-matched shift estimator on the null front end"},
      {"tag": "E0_end_to_end",  "R3S2_FRONTEND": "film_only", "R3S2_ARM": "end_to_end",  "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "joint",     "role": "two-stage vs end-to-end on the null front end"},
      {"tag": "E1_emul_only",   "R3S2_FRONTEND": "ic_synth",  "R3S2_ARM": "emul_only",   "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "none",      "role": "PRIMARY CONTRAST vs E0_emul_only (clause F1)"},
      {"tag": "E1_frozen",      "R3S2_FRONTEND": "ic_synth",  "R3S2_ARM": "frozen",      "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "real_lf",   "role": "SCORED ARM; pure pseudo-LF distribution-shift exposure"},
      {"tag": "E1_finetuned",   "R3S2_FRONTEND": "ic_synth",  "R3S2_ARM": "finetuned",   "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "pseudo_lf", "role": "budget-matched shift estimator (frozen - finetuned)"},
      {"tag": "E1_end_to_end",  "R3S2_FRONTEND": "ic_synth",  "R3S2_ARM": "end_to_end",  "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "joint",     "role": "two-stage vs end-to-end on the contrast front end"},
      {"tag": "E1n_emul_only",  "R3S2_FRONTEND": "ic_shuffle","R3S2_ARM": "emul_only",   "R3S2_LF_INPUT": "pseudo",     "R3S2_CORRECTOR_FIT_ON": "none",      "role": "ZERO-INFORMATION NULL for the IC channel (row-shuffled coefficients)"},
      {"tag": "condmean_lf",    "R3S2_FRONTEND": "none",      "R3S2_ARM": "condmean_lf", "R3S2_LF_INPUT": "train_mean", "R3S2_CORRECTOR_FIT_ON": "real_lf",   "role": "ADR r2-0003 null; frozen - condmean_lf = value of the emulator"}
    ]
  }
}
```

- **Expected outcome**: scored `E1/frozen` panel geomean **20-28** (point ~25) -> **Delta vs the launch anchor 36.3912 = -8 to -16** skill units; the `E0` arms reproduce the certified r2s2_stacked-B1 mean **27.5068** within its seed band [19.1984, 35.8151]. The discriminating per-dataset prediction (clause F1, `E1/emul_only` vs `E0/emul_only`): **ch** 11.0948 -> 4-9 (Delta 2-7 against the 1.7406 threshold), **ac** 231.7681 -> 140-215 (Delta 17-92 against 24.6334), **pfc** no resolvable change (stiff crystalline-box map, ~1e4 linear amplification; threshold 13.2893), **fk** reported only (its mce 158.3322 is ~79% of the cell's own value — undecidable by construction), **ifc_poisson / ifc_heat** unchanged by construction (no `ic_*` dims) and still expected to LOSE to their `affine_on_hf_train` floors (1.5938 / 0.9584). On the corrector I honestly expect the round-2 null to replicate (best arm minus its own `emul_only` under 1 mce everywhere; round 2 measured 0.0061 on ch) — i.e. **F2 firing is the modal outcome, and that is a certified negative with a mechanism, which round-3 success criterion 1 counts as a result**. All numbers carry the standing caveats: pfc weak-gap/stiff-map, fk weak gap, ac trimmed test n=78, ch outlier domination, ifc affine structure, no cross-round comparison without the honest-denominator flag.

- **Expected falsification**: H — *"the round-2 stacking ceiling was caused by the realised IC being absent from the condition vector, so under the completeness-repaired panel an exact zero-parameter IC-synthesis front end reaches field structure the FiLM-only path cannot, and a realisation-faithful pseudo-LF restores the defect corrector's value"* — is FALSIFIED if **(F1)** `E1/emul_only` fails to beat `E0/emul_only` by >= 1.5x the in-force per-dataset `min_claimable_effect` on at least 2 of {`sharp__cahn_hilliard`, `sharp__allen_cahn_2d`, `sharp__phase_field_crystal_2d`} (interim provisional thresholds **1.7406 / 24.6334 / 13.2893** skill units, from provisional mce 1.1604 / 16.4223 / 8.8595) **OR (F2)** the best stack arm fails to beat its own front-end-matched `emul_only` arm by >= 1.5x that same effect on all three of those datasets — disjunctive and independently reportable, because round-2's conjunctive clause let a decisive sub-failure pass as "confirmed".

- **Prior-art verdict quoted**: verbatim from `round3/websearches/r3s2_field_reach/batch_1/report.md` — **D2**: *"re-test of the stacked condition -> pseudo-LF -> corrector pipeline under the now-complete condition vector | `preempted (cite)` (mechanism); open only as a measurement | https://arxiv.org/abs/2302.12682 ... https://arxiv.org/abs/2310.00057 ... https://arxiv.org/html/2606.17460v2 (snippet: boosted stacks fail when "the full-size baseline already captures the dominant dynamics") | Only whether completeness changes the round-2 **attribution** (99.98% stage-1 error; corrector worth 0.0061 units). A measurement of this benchmark, never a mechanism. Note the published failure prediction in 2606.17460 weakens any positive claim in advance"*; **D1**: *"internal "option C": condition vector -> **exact, zero-parameter analytic synthesis** of the band-limited IC field -> learned operator / rollout to the readout time | `preempted-but-MF-composition-open` | ... | No fetched source uses a **fixed exact reconstruction of a known band-limited parameterization** as an internal zero-parameter layer, and **every** parameter-conditioned emulator found still consumes a field or state at inference. The condition-only, no-field-at-test regime with N_hf in {5, 400}, LF at train only, scored in copy-LF skill units against training-free floors, is unrepresented"*; and the standing instruction *"If you propose D2 (stacked pseudo-LF), expect the reviewer to call it a rebadge. ... Propose it only as a completeness-conditioned attribution re-measurement with the round-2 numbers pre-registered as the null."*

- **Immutables self-check**: **pass (11/11)** — positive evidence per item in [iteration_1.md](iteration_1.md) §"Immutables self-check". Highlights: eval layer needs no edit (`score_panel.py --family_dir` is a free path, knobs go through `--env`); guarded generator surfaces were **read only** and their math re-implemented in the family dir with provenance; thresholds are 1.5x the provisional mce on every cited dataset and fk/ifc_heat are excluded because their floors are unusable/absent; nearest pre-falsified lever is LF low-mode freezing, which this design does not do (fitted Wiener transfer with an alpha line search including 0, on a model-generated pseudo-LF, no LF at test).

- **Anchor reference**: `null` (round-3 policy: gap/lever/diag streams carry `null`; the own-stream launch best-floor anchor 36.3912 is implicit).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| (none) | — | All 14 round-2 cards carry `reopen_candidate: false` (verified by reading every JSON under `round2/experiment_cards/`); `round3/experiment_cards/` does not yet exist, so no round-3 candidate can exist at batch 1. | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B1 | mf_composition / completeness-conditioned stack re-measurement + analytic IC-synthesis front-end contrast | Mandated §12.2 stack (FiLM-FNO pseudo-LF emulator -> vendored DC-lineage corrector, frozen/fine-tuned/end-to-end, budget-matched) re-run on the completeness-repaired panel with a zero-parameter exact IC-synthesis front end and its shuffled-coefficient null, to attribute round-2's ceiling to information vs conditioning path | filled |
