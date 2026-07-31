# Brainstormer Report — Stream `r2s2_stacked`, Batch 1

**Stream**: `r2s2_stacked` (lever)
**Batch**: 1
**Total iterations**: 1 (cap 5) — immutables self-check passed on the first pass, no revision needed
**Slot filled**: 1 / 1 (`model` card)
**Reopen candidates resolved**: 0 of 0 (none exist round-wide)

## Slot

- **Category**: `mf_composition / condition→pseudo-LF emulation feeding a
  real-LF-trained defect corrector, with an in-job attribution decomposition of
  stacked error into emulator error, distribution shift, and the
  conditional-mean barrier`

- **Card type**: `model`

- **Motivation**: The stack topology is not novel and the card claims nothing
  for it. The websearcher's verdict, verbatim: *"D1 — `preempted (cite)`: Xu,
  Cao, Yuan, Meschke (2023), https://arxiv.org/abs/2310.00057 — frozen LF
  DeepONet subnet whose predicted LF output feeds a residual subnet; Yang et al.
  (2025), https://arxiv.org/html/2503.17941v1 — names 'residual-learning
  frameworks that sequentially combine low and high-fidelity predictions' as an
  existing class."* The stream's claim therefore sits on **D2**,
  *"`preempted-but-MF-composition-open`"*, where the report records that **no
  fetched source decomposes stacked error into emulator error + downstream
  distribution shift, nor uses the frozen−finetuned delta as the shift
  estimator, on field-valued PDEs**, and (report §"Turn 4") that **no source
  was found quantifying a real-LF-trained corrector's degradation on emulated LF
  inputs**. B1 measures a known composition in an unmeasured regime — copy-LF
  skill, no solver at test, N_hf ∈ {5, 400} — and contributes the attribution.
  Beyond the pre-directed design, the card adds one thing nobody asked for: ADR
  r2-0003 established that on pfc / fisher_kpp / allen_cahn the realized IC is
  absent from the condition vector and **present in the LF field**, so a
  condition-only emulator inherits the identical conditional-mean bound. Arm A5
  turns that from an argument into a paired in-job measurement.

- **Concrete config**: family `models_r2/r2s2_stack`. A FiLM-FNO emulator
  (`FNO2d`-class, coords-only input, FiLM on the condition at every block;
  width 64, 4 blocks, 12×12 modes) maps condition → LF field on the LF rung's
  **native** grid (not the HF grid — otherwise the nested-ladder degeneracy is
  total and the stream's question is unanswerable by construction), trained with
  relative-L2 against real train LF at `S6_LF_FID=max`. A **corrected**
  upsampler (convention keyed per dataset exactly as
  `round2/eval/panel_data.py`: `node_aligned_periodic` / `dirichlet_node` /
  `legacy_cell_centred`), vendored into the family dir with provenance, lifts
  pseudo-LF to the HF working grid — this is round 1's never-applied
  "corrector-input wrap-seam fix". The round-1 `dc_cleaned` stage is then
  vendored with provenance from
  `round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router/`
  (`lsi_filter.py` closed-form Wiener `T(k)` + α line-search including 0;
  `local_corrector.py::LocalCorrector`, `local_pixel_gate`, kernel 7, depth 4,
  width 32, zero-init head). **Router and trust head are removed** — round 1
  measured their panel contribution at exactly 0.000000 (r1 report §2, §4).
  **One emulator is trained once and shared by all arms**, so every arm is an
  in-job paired control on identical pseudo-LF fields (drift-class rule).
  "Frozen" means *frozen with respect to the pseudo-LF distribution* (the
  corrector is re-fit on real train LF via the corrected data path, and never
  sees pseudo-LF) — not a round-1 checkpoint, which was fit against the
  defective reference.

  Five scored arms:

  | arm | LF input at test | LSI (T, α) fit on | LocalCorrector trained on | role |
  |---|---|---|---|---|
  | A1 `emul_only` | pseudo-LF (upsampled) | — | — | stack's internal floor + in-job direct-condition→HF control |
  | A2 `frozen` | pseudo-LF | REAL train LF | REAL train LF cleaned residual | **PRIMARY** — pure distribution-shift exposure |
  | A3 `finetuned` | pseudo-LF | T from A2; α refit on pseudo | init A2, fine-tuned on (pseudo-LF, HF) | **A2 − A3 = shift estimator** |
  | A4 `end_to_end` | pseudo-LF | jointly | emulator + corrector joint, HF loss, init A2 | CALM-PDE §4.3 test |
  | A5 `condmean_lf` | **train-mean LF** (constant) | REAL train LF | REAL train LF cleaned residual | ADR r2-0003 null; **A2 − A5 = value of the emulator** |

  Sidecars on a held-out slice of the **TRAIN** split only (train LF is legal,
  §5.9 untouched): **S1** emulator field error nRMSE(LF̂, LF_real); **S2**
  real-LF oracle ceiling in-job. Training-free pre-registered probes: **P1**
  BC-match audit (`tools/spectral_prestage_bc_audit.py`, adapted); **P2**
  condition→LF identifiability (ADR r2-0003's nearest-condition method applied
  to the LF fields), both recorded *before* training so the falsification is
  decidable. Six in-process validity gates V1–V6, including V6
  `R2S2_REQUIRE_PSEUDO_LF` — the tripwire preventing the silent ifc_poisson
  no-op that round 1 hit (`S6_FALLBACK_NO_TEST_LF=champion`). Round-1's D3
  val-asymmetry defect is repaired: disjoint, identically-sized val sub-slices
  (`val_a` for α, `val_b` for the gate) identical across arms.

- **Recipe**:

```json
{
  "base_family": "s4_router",
  "base_commit": "b90d4662cd12820b6926730d39bdb5af70bba276",
  "family_dir": "models_r2/r2s2_stack",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S2_ARM": "frozen",
    "R2S2_EMU_TARGET": "lf_native",
    "R2S2_EMU_RUNG": "max",
    "R2S2_EMU_WIDTH": "64",
    "R2S2_EMU_BLOCKS": "4",
    "R2S2_EMU_MODES": "12",
    "R2S2_EMU_LOSS": "rel_l2",
    "R2S2_EMU_SHARED": "1",
    "R2S2_EPOCH_SPLIT": "0.5",
    "R2S2_UPSAMPLE": "corrected_by_convention",
    "R2S2_LF_INPUT": "pseudo",
    "R2S2_CORRECTOR_FIT_ON": "real_lf",
    "R2S2_VAL_DISJOINT": "1",
    "R2S2_REQUIRE_PSEUDO_LF": "1",
    "R2S2_EMU_ERROR_SIDECAR": "1",
    "R2S2_ORACLE_TRAINHELDOUT_SIDECAR": "1",
    "R2S2_BC_AUDIT_SIDECAR": "1",
    "R2S2_COND_LF_IDENT_SIDECAR": "1",
    "R2S2_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s2_stacked/B1/eval",
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
    "_substrate_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
    "_vendor_source": "round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router @ b90d4662 (lsi_filter.py, local_corrector.py, bands.py, periodicity.py, model.py::FNO2d); upsampler vendored with provenance from round2/eval/panel_data.py",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. score_panel.py --datasets accepts ONLY the exact keyword 'panel' or 'guard' or a comma-list of dataset NAMES, so the guard run is a SEPARATE invocation with --datasets guard (smoke tier 200, seed 0), matching round-1's recorded guard references.",
    "_arms": [
      {"tag": "emul_only",   "R2S2_ARM": "emul_only",   "R2S2_LF_INPUT": "pseudo",     "R2S2_CORRECTOR_FIT_ON": "none",     "role": "stack's internal floor + in-job direct condition->HF control"},
      {"tag": "frozen",      "R2S2_ARM": "frozen",      "R2S2_LF_INPUT": "pseudo",     "R2S2_CORRECTOR_FIT_ON": "real_lf",  "role": "PRIMARY: pure pseudo-LF distribution-shift exposure"},
      {"tag": "finetuned",   "R2S2_ARM": "finetuned",   "R2S2_LF_INPUT": "pseudo",     "R2S2_CORRECTOR_FIT_ON": "pseudo_lf","role": "shift-adapted; frozen-finetuned = shift estimator"},
      {"tag": "end_to_end",  "R2S2_ARM": "end_to_end",  "R2S2_LF_INPUT": "pseudo",     "R2S2_CORRECTOR_FIT_ON": "joint",    "role": "CALM-PDE two-stage-vs-end-to-end test"},
      {"tag": "condmean_lf", "R2S2_ARM": "condmean_lf", "R2S2_LF_INPUT": "train_mean", "R2S2_CORRECTOR_FIT_ON": "real_lf",  "role": "ADR r2-0003 null; frozen-condmean_lf = value of the emulator"}
    ]
  }
}
```

- **Expected outcome**: primary metric = panel geomean skill of the best stack
  arm, bracketed by two numbers computed in `summary_so_far.md` §3: the real-LF
  oracle ceiling **0.3306** (§12.2's mandated restatement of `dc_cleaned`'s
  0.1232 under the corrected denominators) and the launch anchor **23.0636**.
  Expected landing: **panel geomean ≈ 2–8**, i.e. **Δ vs anchor = 3–10× better**
  but 10–25× short of the oracle. Why: the geomean is dragged up by the three
  ADR r2-0003 datasets where the stack is capped at the conditional-mean floor
  (train_mean skills pfc 59.81 / fisher_kpp 11.99 / allen_cahn 562.03), and
  pulled down by the datasets whose condition is (near-)complete. Per dataset —
  **cahn_hilliard 3–10** vs NN floor 23.180 (the claim-bearing dataset; Δ ≥ 13
  skill units, far above the provisional min_claimable_effect 1.1604 and spread
  0.4023); **helmholtz 1.5–3** vs zero floor 3.3441 — but its provisional
  min_claimable_effect 10.6811 exceeds the entire plausible range, so helmholtz
  stays **report-only** (r1 report §5.3), carries the standing zero-floor
  column, and **no helmholtz-only claim is made**; **pfc / fisher_kpp /
  allen_cahn** at or near the train_mean floor with `A2 − A5 ≈ 0` (the
  pre-registered ADR r2-0003 prediction); **ifc_poisson 2–10**, anecdote-grade
  at N_hf = 5 but the DC lineage runs there for the first time. Secondary (the
  D2 claim): shift penalty `A2 − A3 > 0` and, pre-registering CALM-PDE §4.3's
  direction, `A4 ≤ A2` — a frozen-arm win would be a **reportable inversion**.
  All pfc claims carry the wrap-seam caveat (deep-bulk ratio 0.908) and the
  band-limited denominator caveat.

- **Expected falsification**: On `sharp__cahn_hilliard` — the one panel dataset
  whose condition vector is IC-complete (16 of 19 dims are `ic_c*`) and hence
  the only one where the stacking premise is identifiable at all — the design is
  falsified if the best stack arm fails to improve on the in-job `emul_only`
  arm by at least **2.0 skill units** *and* fails to beat the frozen
  NN-in-condition floor **23.180**, both margins exceeding that dataset's
  provisional noise floor (spread **0.4023**, min_claimable_effect **1.1604**),
  since that would show the LF representation is not a useful bottleneck even
  where the emulator can in principle be accurate.

- **Prior-art verdict quoted** (verbatim from
  `websearches/r2s2_stacked/batch_1/report.md`, "For the brainstormer" §1–2):

  > **D1 — `preempted (cite)`: Xu, Cao, Yuan, Meschke (2023),
  > https://arxiv.org/abs/2310.00057 — frozen LF DeepONet subnet whose predicted
  > LF output feeds a residual subnet; Yang et al. (2025),
  > https://arxiv.org/html/2503.17941v1 — names 'residual-learning frameworks
  > that sequentially combine low and high-fidelity predictions' as an existing
  > class.**

  > **D2 — `preempted-but-MF-composition-open`** … "The open contribution is the
  > *attribution*: decompose stacked error into (emulator error) + (distribution
  > shift on a corrector trained on real LF), using the **frozen − fine-tuned**
  > delta as the shift estimator" — "no fetched source performs this
  > decomposition."

  Supporting citations carried onto the card: CALM-PDE
  https://arxiv.org/abs/2505.12944 (§4.3, end-to-end > two-stage); Conti et al.
  2025 https://arxiv.org/html/2510.13762v1 (frozen lower levels, but LF still
  required at test); Meng & Karniadakis 2020 https://arxiv.org/abs/1903.00104;
  Howard et al. 2023 https://arxiv.org/abs/2204.09157.

- **Immutables self-check**: **pass (11/11)** on the first pass — nothing
  flagged, no revision required. Positive evidence for each of the 8 immutables
  plus the 3 round-2 extras is recorded in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Load-bearing items:
  (3) the corrected upsampler is **vendored, never imported from or edited into
  `eval/`** — following the s4_router precedent that `score_panel.py::code_hash`
  hashes only `family_dir/**/*.py`; (6) `R2S2_EPOCH_SPLIT=0.5` divides the
  tier's 200 epochs *within* the pipeline (100 + 100) and never exceeds it;
  (8) `lsi_filter.py::pack_transfer` already exists to make the closed-form
  `T(k)` checkpoint-safe, so `last.pt` can hold the full two-stage state;
  (9) threshold 2.0 > min_claimable_effect 1.1604 > spread 0.4023 on
  cahn_hilliard, and helmholtz was deliberately **not** used for the clause
  because its min_claimable_effect 10.6811 exceeds the whole plausible effect
  range; (10) nearest pre-falsified lever is **LF low-mode freezing** — nothing
  spectral is frozen here (full |k|-dependent Wiener `T(k)` with an α
  line-search including 0), "frozen" refers to corrector *parameters* w.r.t. the
  pseudo-LF distribution, and the falsified lever presupposed a real LF input
  that does not exist at test in round 2; (11) floor arms are load-bearing, not
  decorative — the NN floor **is** the falsification's second limb, and arm A5
  is a paired in-job realization of the conditional-mean floor.

- **Anchor reference**: `null` (program.md §4.5 — null for all four round-2
  streams; `r2s2_stacked` is a lever stream and its own anchor 23.0636 is
  implicit).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| _(none)_ | — | — | — |

None exist: `experiment_cards/r2s2_stacked/` is empty (B1 is the stream's first
card), and a scan of every round-1 and round-2 card for `reopen_candidate: true`
returned zero hits round-wide. Recorded in `summary_so_far.md` §5.

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| `r2s2_stacked-B1` | `mf_composition` / stacked condition→pseudo-LF→corrector with attribution decomposition | FiLM-FNO native-grid pseudo-LF emulator (trained once, shared) feeding the vendored round-1 `dc_cleaned` stage across 5 paired arms — `emul_only` / `frozen` / `finetuned` / `end_to_end` / `condmean_lf` — decomposing stacked error into emulator error, pseudo-LF distribution shift, and the ADR r2-0003 conditional-mean barrier | **filled** (`model` card) |
