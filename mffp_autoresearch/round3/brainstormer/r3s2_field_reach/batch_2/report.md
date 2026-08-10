# Brainstormer Report — Stream `r3s2_field_reach`, Batch 2

**Stream**: `r3s2_field_reach` (gap) · **Batch**: 2 · **Total iterations**: 2 · **Slot filled**: 1/1 · **Reopen candidates resolved**: 0 (none exist)

## Slot

- **Category**: `mf_composition/route_contrast_with_instrument_repair`
- **Card type**: `model`
- **Motivation**: the batch-2 prior-art verdict says E2 is the one direction with an unmeasured composition and instructs *"E2 is the only direction with a genuinely unmeasured composition — build the card on it"*. What is open, verbatim: *"No fetched source runs a **direct parameter→HF arm against a coarse-intermediate arm at matched total optimizer budget where the coarse field cannot be produced at inference**. Every MF comparison retrieved either calls the LF model online (2512.02868's "exact LF"; the MF-ROM line) or feeds a real coarse solve to the corrector (2411.07576, INC). The open question is exactly: *is the LF intermediate worth its place in the graph when it must itself be hallucinated from the condition?* Prior is two-sided — 2512.02868 predicts the stack wins, 2606.17460 + in-repo `MF_Sharp_HighFreq_Report.md` line 101 predict it loses, B1's F2 already measured no resolvable value"*.
  The stream's own conventions name this contrast as its falsification framing (round-2 §12.2: *"Failure is informative: if pseudo-LF → corrector loses to r2s1's direct models, the LF representation is not a useful bottleneck"*), and B1's part 7 says *"r3s2-B2 should be a ROUTE contrast, not another front-end contrast"* — but the contrast is uninterpretable until B1's corrector defect is repaired, because *"the whole 3-seed panel spread [10.3180, 17.8277] … [is a] shadow of that single number"* (M1). The E1 repair is therefore carried on the card as an **instrument acceptance gate only**, per its verdict: *"usable ONLY as an instrument repair, never as a contribution"* and *"Presenting ridge/band-limiting as the *idea* is a rebadge"*. E3 rides along at zero GPU cost as a **prospective** declaration, which is the only part of it left open: *"The **paired** application … used prospectively to rule a cell off-limits for capacity spending"*.

- **Concrete config**: new family `models_r3/r3s2_route`, vendored wholesale from this stream's own B1 family `models_r3/r3s2_stack_ic` @ `d5069a74`, with a new `INSPIRATION.md`. One shared FiLM-FNO trunk (width 64, 4 blocks, 12 modes) behind a **route switch** — `stack`: condition → pseudo-LF (`lf_native`, `S6_LF_FID=max`) → convention-keyed upsample → frozen DC corrector → HF; `direct`: condition → HF — crossed with a **front-end switch** (`ic_synth`, B1's zero-parameter exact analytic IC reconstruction, vs `film_only`). A budget accountant holds every stage-2 and every direct arm at exactly **300** optimizer epochs (`E_emu + 2·E_dc`, `R3S2_BUDGET_MATCH=arm_equal_total`, tier 200, split 0.5), which is B1's own accounting and repairs round-2 caveat F8. The corrector's LSI transfer function is repaired: `T(k)` is zeroed above `k_cut = k_Nyq_HF · N_LF/N_HF` (computed from the actual ladder shapes under ADR r2-0001 registration conventions, `k_cut` recorded) and ridged with a LOOCV-selected coefficient from `{0, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1}` **on the fit fold only** (`S6_LEAKAGE_TRIPWIRE=1`), per arXiv:1810.08360, with arXiv:1511.07030 as the low-sample-support rationale and arXiv:2606.03936 as the frozen-operator per-band precedent — all three cited as preemption, not inspiration.
  **Seven arms** plus the mandatory floors: `A1 stack_ic_reg` (scored primary) · `A2 stack_film_reg` (second, independent replication of the route contrast at the null front end) · `A3 direct_ic` (scored primary comparand) · `A4 direct_film` (r2s1 calibration) · `A5 stack_ic_unreg` (B1 replay at `ridge=0` — repair attribution + anchor replication gate) · `A6 ifc_loo_selector` (closed form, ifc only, zero GPU: leave-one-out over the 5 HF train rows choosing among {`affine_on_hf_train`, `A1`, `A3`}) · `A7 emul_only_ic` (stage-1 reference, 100 epochs) · floor arms `nn_condition, train_mean, zero, affine_on_hf_train`.
  **Accounting mandated on the card**: skill *and* fractional-error-reduction units (M5: F1's 59× ac-vs-ch gap is 20.3× denominator × 2.14× effect); 4-band error columns (Duraisamy 2604.20061's reporting standard); a model-free map-smoothness sidecar on all five cells (the E3 instrument); `n_train_route` disclosure per arm per dataset (on ifc the stack's stage 1 fits **18 of 20 LF rows** while the direct head sees **5 HF rows**); a dataset content hash bound into `last.pt` (discharges r3s4-B1's open question — *"Only a content hash bound into the checkpoint can"* — at zero cost).
  **Explicitly not proposed**: any capacity or conditioning change on `cahn_hilliard` (M7 + handoff caution + websearcher item 5); any new decoder architecture; a re-run of `end_to_end` as primary.

- **Recipe**:

```json
{
  "base_family": "r3s2_stack_ic",
  "base_commit": "76d15c2daf30e1db8031842c722d99c0629f4c0e",
  "family_dir": "models_r3/r3s2_route",
  "datasets": "sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard,ifc_poisson,ifc_heat",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {
    "R3S2B2_ARM": "A1_stack_ic_reg",
    "R3S2B2_ROUTE": "stack",
    "R3S2_FRONTEND": "ic_synth",
    "R3S2_ARM": "frozen",
    "R3S2B2_DIRECT_TARGET": "hf",
    "R3S2B2_DIRECT_TRUNK": "shared_film_fno_w64_b4_m12",
    "R3S2B2_DIRECT_BUDGET": "match_stage2_total",
    "R3S2B2_DIRECT_TRAIN_ROWS": "hf_train_all",
    "R3S2B2_DIRECT_VAL": "disjoint_if_n_train_hf_ge_20_else_none_recorded",
    "R3S2_IC_SYNTH": "analytic_modes",
    "R3S2_IC_SYNTH_NORM": "res_min_maxabs",
    "R3S2_IC_SYNTH_SCALE": "1.0",
    "R3S2_IC_NAMES_FROM": "meta_param_names_ic_prefix",
    "R3S2_IC_FALLBACK": "film_only_recorded",
    "R3S2_IC_EQUIV_CHECK": "1",
    "R3S2_IC_SHUFFLE_NULL": "0_established_in_B1",
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
    "R3S2_TARGET_SCALER_PREFLIGHT": "not_applicable_no_helmholtz_no_pfc_in_datasets",
    "R3S2_FLOOR_ARMS": "nn_condition,train_mean,zero,affine_on_hf_train",
    "R3S2_DIAG_OUT": "mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/eval",
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
    "S6_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S6_LEAKAGE_TRIPWIRE": "1",
    "S6_LSI_RIDGE": "loocv",
    "S6_LSI_RIDGE_GRID": "0,1e-6,1e-4,1e-3,1e-2,1e-1",
    "S6_LSI_RIDGE_SELECT": "loocv_on_fit_fold_only",
    "S6_LSI_BANDLIMIT": "lf_nyquist_from_ladder",
    "S6_LSI_BANDLIMIT_MODE": "zero_above_kcut",
    "S6_LSI_KCUT_SOURCE": "ladder_shape_ratio_adr_r2_0001",
    "R3S2B2_REPORT_UNITS": "skill,fractional_error_reduction",
    "R3S2B2_BAND_ERROR_COLUMNS": "1",
    "R3S2B2_MAP_SMOOTHNESS_SIDECAR": "1",
    "R3S2B2_ROUTE_DATA_DISCLOSURE": "1",
    "R3S2B2_T_STABILITY_AUDIT": "1",
    "R3S2B2_IFC_LOO_SELECTOR": "affine_on_hf_train,A1_stack_ic_reg,A3_direct_ic",
    "R3S2B2_CKPT_DATA_HASH_BIND": "1",
    "R3S2B2_ANCHOR_REPLICATION_CHECK": "12.9556",
    "R3S2_EMU_ERROR_SIDECAR": "1",
    "R3S2_ORACLE_TRAINHELDOUT_SIDECAR": "1",
    "R3S2_ZERO_GRADIENT_LADDER_SIDECAR": "1",
    "R3S2_BC_AUDIT_SIDECAR": "1",
    "_substrate_commit": "d5069a74bb63da837b89b16508ae25a2164780cc",
    "_vendor_source": "mffp_autoresearch/round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic @ d5069a74 (ALL of smoke_eval.py, model.py, front_end.py, ic_synth.py, lsi_filter.py, local_corrector.py, bands.py, periodicity.py, upsample.py, floor_arms.py, probes.py, sidecars.py). NO code is vendored from r2s1_direct or from any round-1 family beyond what r3s2_stack_ic already carried (round-1 s4_router via r2s2_stack). IC-synthesis math remains B1's re-implementation from the READ-ONLY generator surfaces mffp_sharp/common/ic_encoding.py::ic_2d and common/spectral.py::spectral_interp with provenance comments (never imported, never edited).",
    "_declared_reuse": "role (a), round-2 program 5.10a: the DC-lineage corrector remains a declared FROZEN test-time sub-component behind a condition->pseudo-LF front end. A5 (ridge=0) is the literal B1 replay and is declared as the pre-registered replication/attribution arm, not as a novelty claim.",
    "_novelty_declaration": "The new pathway is a SINGLE shared FiLM-FNO trunk behind a ROUTE SWITCH (condition->pseudo-LF->frozen regularised corrector->HF vs condition->HF) with a budget accountant that holds total optimizer epochs equal across routes (E_emu + 2*E_dc = 300) and a REGULARISED LSI transfer stage (LOOCV ridge + band-limit above the LF Nyquist). The direct_* arms are declared MATCHED CONTROLS inside that contrast, not candidate architectures: they carry the zero-parameter analytic IC-synthesis channel (r2s1_direct's heads are FiLM-only on the raw condition vector) and are budget-locked to the stack. A4 direct_film is the pre-registered r2s1 calibration arm (expected near r2s1_direct-B2's certified 23.7753); if it lands far from that, the family and not the route is the story. Reviewer question 'is this a rebadge of r2s1_direct?' is answered here, before the build.",
    "_script_env": {
      "ROUND2_EVAL_RESULTS": "$OUT_DIR/training",
      "ROUND2_EVAL_CACHE": "$OUT_DIR/cache",
      "_why": "MANDATORY, carried from B1's review-FAIL discharge d5069a74: without these, score_panel.py::_results_dir()/_cache_dir() default to EVAL_DIR/{results,cache} and the job writes per-cell JSONs and multi-GB checkpoint trees into the FROZEN round-2 eval layer (immutable 3). Export both after OUT_DIR= and before BOTH score_panel.py invocations, and mkdir -p $OUT_DIR/cache."
    },
    "_note": "Keys prefixed _ are card directives, NOT passed to --env. score_panel.py --datasets accepts ONLY 'panel' | 'guard' | a comma-list of dataset NAMES; the literal 'panel' resolves to the ROUND-2 six-dataset panel via round2/project.yaml and MUST NOT be used (ADR r3-0004). The guard run is a SEPARATE invocation with --datasets guard (smoke tier 200, seed 0). Checkpoint dirs must be FRESH under mffp_autoresearch_outputs/round3/r3s2_field_reach/B2/ckpt (never reused from B1) and R3S2B2_CKPT_DATA_HASH_BIND=1 binds the dataset content hash into last.pt so a resume against changed arrays aborts instead of zero-stepping (r3s3-B1 / STOP-THE-LINE #2). Post-run acceptance: tools/lsi_transfer_stability_audit.py on the B2 tree (G2 leg iii), tools/zero_work_resume_scan.py and tools/stale_checkpoint_audit.py --exclude stale_ckpt (r3s4-B1 part 7b: do NOT read train_seconds_collapsed as evidence of staleness). Wall-clock: B1 ran 10 arms x 5 datasets x 200 epochs (2400 optimizer epochs/dataset) in 44.33/36.55/36.55 min per seed on one H200 (state/timing_ledger.json); B2 spends 1400 optimizer epochs/dataset but 600 of them are on the HF grid (the two direct heads), so estimate 45-70 min/seed and request --time 03:00:00 (>=1h => --mail-user=ezeng@caltech.edu --mail-type=END,FAIL per project.yaml sbatch).",
    "_arms": [
      {
        "tag": "A1_stack_ic_reg",
        "R3S2B2_ROUTE": "stack",
        "R3S2_FRONTEND": "ic_synth",
        "R3S2_ARM": "frozen",
        "S6_LSI_RIDGE": "loocv",
        "S6_LSI_BANDLIMIT": "lf_nyquist_from_ladder",
        "optimizer_epochs": 300,
        "role": "SCORED PRIMARY - the repaired stack; G1 left-hand side, G2 subject"
      },
      {
        "tag": "A2_stack_film_reg",
        "R3S2B2_ROUTE": "stack",
        "R3S2_FRONTEND": "film_only",
        "R3S2_ARM": "frozen",
        "S6_LSI_RIDGE": "loocv",
        "S6_LSI_BANDLIMIT": "lf_nyquist_from_ladder",
        "optimizer_epochs": 300,
        "role": "second, independent replication of the route contrast at the null front end"
      },
      {
        "tag": "A3_direct_ic",
        "R3S2B2_ROUTE": "direct",
        "R3S2_FRONTEND": "ic_synth",
        "R3S2_ARM": "direct",
        "optimizer_epochs": 300,
        "role": "SCORED PRIMARY comparand - matched-budget direct condition->HF control; G1 right-hand side"
      },
      {
        "tag": "A4_direct_film",
        "R3S2B2_ROUTE": "direct",
        "R3S2_FRONTEND": "film_only",
        "R3S2_ARM": "direct",
        "optimizer_epochs": 300,
        "role": "r2s1 CALIBRATION arm - pre-registered to land near r2s1_direct-B2's certified 23.7753"
      },
      {
        "tag": "A5_stack_ic_unreg",
        "R3S2B2_ROUTE": "stack",
        "R3S2_FRONTEND": "ic_synth",
        "R3S2_ARM": "frozen",
        "S6_LSI_RIDGE": "0",
        "S6_LSI_BANDLIMIT": "none",
        "optimizer_epochs": 300,
        "role": "B1 replay - repair attribution AND the anchor replication gate (G2 leg iv, target 12.9556 +- 0.5083)"
      },
      {
        "tag": "A6_ifc_loo_selector",
        "R3S2B2_ROUTE": "selector",
        "datasets": "ifc_poisson,ifc_heat",
        "optimizer_epochs": 0,
        "role": "closed-form, zero-GPU leave-one-out selector over {affine_on_hf_train, A1, A3} on the 5 HF train rows; the ifc HEADLINE (card part 7 item 4). Selection uses train rows ONLY - never the test split"
      },
      {
        "tag": "A7_emul_only_ic",
        "R3S2B2_ROUTE": "stack",
        "R3S2_FRONTEND": "ic_synth",
        "R3S2_ARM": "emul_only",
        "optimizer_epochs": 100,
        "role": "stage-1 reference (the front end alone), so the route delta can be decomposed into stage-1 and transport terms"
      }
    ]
  }
}
```

- **Expected outcome** (skill units, lower better; panel = ADR r3-0004 five datasets, 3 seeds; stream anchor **12.9556**, per-seed [10.7213, 10.3180, 17.8277]):
  | quantity | prediction | Δ vs anchor | vs noise floor |
  |---|---|---|---|
  | `A5` panel geomean (B1 replay) | 12.9556 ± 0.5083 | 0 by construction | replication gate = 1 × panel `seed_mce` 0.5083 |
  | `A1` panel geomean (repaired stack) | ~10.6, per-seed ~[10.3, 10.9] | **−2.4** | **4.7×** the panel `seed_mce` 0.5083 |
  | `A1` ifc_poisson seed-2 nRMSE | 2.0409 → ~0.171 | — | the move is 42.8 skill units = **62×** `tau_rel(ifc_poisson)` 0.6910 |
  | `A1` 3-seed panel spread | 7.5097 → ~0.6 | — | bar 2.0 = **3.9×** panel `seed_mce` 0.5083 |
  | route delta `A1 − A3` | **two-sided, pre-registered both ways** | — | decision bar 0.7624 = 1.5 × panel `seed_mce` |
  | `A4` panel geomean | ~23.7753 (r2s1_direct-B2 certified) | — | calibration only |

  The route delta is the card's actual result and its sign is not assumed. arXiv:2512.02868 predicts the stack wins, "particularly in data-scarce scenarios" — and the ifc cells are exactly that, with the stack's stage 1 seeing 3.6× more rows than the direct head. arXiv:2606.17460, in-repo `MF_Sharp_HighFreq_Report.md` line 101, and B1's own M11/M12 predict the opposite. My prior, weighting the in-repo measurement above the external one: `A3 < A1` on both ifc cells (there the stack loses `affine_on_hf_train` by 1.63×–35.6× while the *same* corrector on real LF beats it by 2.7×/16×), `|A1 − A3| < tau_rel` on ch (the E3 prediction), ac and fk within ±1.5 `tau_rel` with fk the least predictable cell (only 0.50 % of its field variance survives mean removal). Every arm is read against the certified training-free floors first; an arm that fails the best floor on a cell contributes no claimable route delta there.

- **Expected falsification**:
  > **H** — *"once the corrector's sample-starved deconvolution is regularised, the hallucinated LF intermediate earns its place in the graph: at matched total optimizer budget and matched front end, the repaired stack beats a direct condition→HF head"* — is FALSIFIED if **(G1, route)** `A1_stack_ic_reg` fails to beat `A3_direct_ic` by ≥ 1.5 × the certified panel `seed_mce` = **0.7624** skill units on the 3-seed 5-dataset panel geomean **AND** fails to beat it by ≥ 1.5 × the certified per-dataset `tau_rel` on ≥ 2 of the 5 scored datasets (**ac 27.9296 / fk 15.4692 / ch 0.5419 / ifc_poisson 1.0365 / ifc_heat 0.2460**) — the reverse inequality at the same magnitudes being recorded as the affirmative negative ("the LF intermediate is a strict tax"), which is round-2 §12.2's own falsification framing; **OR (G2, instrument acceptance — a pre-registered repair, NOT a contribution)** any of (i) `A1`'s ifc_poisson seed-2 test nRMSE stays above **0.50** (B1: 2.0409, M3 predicts ~0.171; the move required is 42.8 skill units vs `tau_rel` 0.6910), (ii) `A1`'s 3-seed panel geomean max−min spread stays above **2.0** skill units (B1: 7.5097, M3 predicts ~0.6; bar is 3.9 × panel `seed_mce` 0.5083), (iii) `tools/lsi_transfer_stability_audit.py` still reports a band-mean `|T| > 1` on any scored cell, (iv) `A5` fails to reproduce the stream anchor 12.9556 within 1 panel `seed_mce` (0.5083), which would mean the vendoring rather than the repair moved the number; **OR (G3, prospective approximability)** the declaration made *before* the run — *"`sharp__cahn_hilliard` is approximability-limited (nn/random field-difference ratio 0.980), so the ROUTE is not a binding constraint there"* — fails, i.e. `|A1 − A3|` on `sharp__cahn_hilliard` exceeds 1.5 × `tau_rel(ch)` = **0.5419** skill units (affirmative confirmation requires that delta below `tau_rel(ch)` = 0.3612 **and** a route delta above 1.5 × its own `tau_rel` on at least one of {ac, fk, ifc_poisson, ifc_heat}).
  >
  > **Floor-arm rule binding all three clauses** (round-2 §5.12; round-3 §2 affine-floor rule): every arm is reported against the certified `nn_condition / train_mean / zero` floors — ac 475.8568 / 486.4148 / 485.5883; fk 410.2818 / 390.7015 / 6051.5886; ch 23.1803 / 23.9691 / 23.9217; ifc_poisson 8.0409 / 9.0041 / 27.7778; ifc_heat 1.3941 / 1.7666 / 13.5135 — and, on both ifc cells, against `affine_on_hf_train` (1.5938 / 0.9584), because *"an ifc claim that does not beat this floor has learned nothing beyond linearity"*. An arm that does not beat the best of those on a cell yields **no claimable route delta** there. Every ifc route delta carries the `n_train_route` disclosure (stack stage 1: 18 of 20 LF rows; direct: 5 HF rows), and the ifc headline is `A6`, never the raw delta. **No clause enumerates `sharp__phase_field_crystal_2d`** (ADR r3-0004: pfc thresholds are void for claim purposes).

- **Prior-art verdict quoted** (verbatim from `websearches/r3s2_field_reach/batch_2/report.md`):
  - **E2 — `preempted-but-MF-composition-open (cite)`**: *"No fetched source runs a **direct parameter→HF arm against a coarse-intermediate arm at matched total optimizer budget where the coarse field cannot be produced at inference**. Every MF comparison retrieved either calls the LF model online (2512.02868's "exact LF"; the MF-ROM line) or feeds a real coarse solve to the corrector (2411.07576, INC). The open question is exactly: *is the LF intermediate worth its place in the graph when it must itself be hallucinated from the condition?* Prior is two-sided — 2512.02868 predicts the stack wins, 2606.17460 + in-repo `MF_Sharp_HighFreq_Report.md` line 101 predict it loses, B1's F2 already measured no resolvable value"*. Citations: <https://arxiv.org/abs/2411.07576>, <https://arxiv.org/abs/2512.02868>, <https://arxiv.org/abs/2511.12764>, <https://arxiv.org/abs/2510.23111>, <https://arxiv.org/html/2606.17460v2>, <https://arxiv.org/abs/2302.12682>, <https://arxiv.org/abs/2310.00057>.
  - **E1 — `preempted (cite)`** — *"usable ONLY as an instrument repair, never as a contribution"*; open: *"Only the **measurement**: that this published stack's whole panel-level 3-seed spread was 100 % attributable to an unregularised band above the LF Nyquist, and that a one-line ridge/band-limit removes it against the pre-registered prediction (ifc_poisson seed-2 2.041 → ~0.171; panel range [10.32, 17.83] → ~[10.3, 10.9]), acceptance-checked by `tools/lsi_transfer_stability_audit.py`. Presenting ridge/band-limiting as the *idea* is a rebadge"*. Citations: <https://arxiv.org/pdf/1511.07030>, <https://arxiv.org/abs/1810.08360>, <https://arxiv.org/pdf/2606.03936>, in-repo `MF_Sharp_HighFreq_Report.md` lines 224–230/260/293–297.
  - **E3 — `preempted-but-MF-composition-open (cite)`** — open: *"The **paired** application: a completeness-certified condition vector (information provably present — B1's shuffled-IC null) **plus** a model-free condition-space nearest-neighbour sampling-density probe **on a field target**, used prospectively to rule a cell off-limits for capacity spending"*; and *"**This verdict also preempts** any claim that the `affine_on_hf_train` / `task_linearity_audit` accounting on the ifc cells is methodologically new"*. Citations: <https://arxiv.org/html/2604.20061>, <https://arxiv.org/pdf/2512.03113>, <https://arxiv.org/abs/2605.28076>.
  - Standing: **nothing is `novel`** — *"the project's record is now 0-for-7"*.

- **Immutables self-check**: **pass (11/11)** at attempt 2. Attempt 1 flagged three items and was revised (`iteration_1.md` → `iteration_2.md`): **FLAG A** — the direct arms were exposed to immutable §5.10's rebadge test against `r2s1_direct`; closed by a `_novelty_declaration` on the recipe (route switch + budget accountant + regularised LSI is the new pathway; direct arms are declared matched controls carrying the IC-synthesis channel and budget-locked to the stack; no r2s1 code vendored; `A4` pre-registered as the r2s1 calibration arm). **FLAG B** — the E1 repair read as the headline; closed by demoting it to instrument-acceptance clause G2 with the verdict quoted on the card. **FLAG C** — the ifc route delta was stated without the train-row asymmetry; closed by `R3S2B2_ROUTE_DATA_DISCLOSURE=1`, the explicit 18-LF-rows-vs-5-HF-rows disclosure on every ifc delta, and making `A6` (LOO selector) the ifc headline. Full 11-item evidence table in `iteration_2.md`; the noise-floor item reads: G1 panel 0.7624 vs `seed_mce` 0.5083; G1 per-dataset 27.9296 / 15.4692 / 0.5419 / 1.0365 / 0.2460 vs `tau_rel` 18.6198 / 10.3128 / 0.3612 / 0.6910 / 0.1640; G2(i) 42.8 skill units vs 0.6910; G2(ii) 2.0 vs 0.5083; G3 0.5419 vs 0.3612 — all exceed, and `tau_rel` (not `tau_abs`) is the licensed constant because every clause is a same-reference comparison (r3s4-B1 part 7a: *"Same-reference comparisons (arm vs arm, or vs the affine floor) are unaffected — the bar cancels"*).

- **Anchor reference**: `null` — per program.md §4.5 policy, all four round-3 streams (gap/lever/diag) use `null`; the own-stream anchor 12.9556 (`state/anchors/r3s2_field_reach.json`) is implicit and is additionally pinned as an explicit replication gate through `A5` and `R3S2B2_ANCHOR_REPLICATION_CHECK`.

- **Source iteration**: [iteration_2.md](iteration_2.md) (revision of [iteration_1.md](iteration_1.md))

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none)* — all four round-3 batch-1 cards carry `reopen_candidate: false`, verified by reading `experiment_cards/*/batch_1/B1.json`; no round-2 or round-1 candidate is flagged for this stream | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B2 | `mf_composition/route_contrast_with_instrument_repair` | Does a hallucinated LF intermediate earn its place? — repaired-stack vs matched-budget direct condition→HF head, 2×2 over route × front end, on a corrector whose sample-starved Wiener deconvolution is ridge/band-limited first | filled (model card, 5-dataset scored panel, 200 epochs, seeds 0/1/2) |
