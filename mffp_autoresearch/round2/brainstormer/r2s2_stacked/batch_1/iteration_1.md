# Iteration 1 — `r2s2_stacked` B1 design

## Design context considered

- **summary_so_far.md §6** (the six unknowns), in particular §6.1 (is
  condition→LF actually easier than condition→HF? measured r = 2 on the sharp
  panel), §6.2 (ADR r2-0003 propagates into the emulator), §6.4 (is the shift
  separable at all?).
- **Prior-art verdict** (`websearches/r2s2_stacked/batch_1/report.md`): D1
  `preempted (cite)`, D2 `preempted-but-MF-composition-open (cite)`, D3
  `preempted (cite)`. Directive: claim nothing for D1; put the stream's claim
  on **D2, the attribution**.
- **program.md §12.2 verbatim** (quoted in summary §2): B1 is pre-directed —
  FiLM-FNO pseudo-LF emulator + best round-1 DC corrector, arms frozen /
  fine-tuned / end-to-end.
- **Immutables block §4.5** (all 8 + the 3 round-2 extras), reproduced in the
  self-check below.
- **Anchor**: best-floor panel geomean **23.0636**
  (`state/anchors/r2s2_stacked.json`, `provisional: false`). Per-dataset floors
  from `state/anchors/floors.json`: helmholtz zero 3.3441 / pfc mean 59.8118 /
  allen_cahn NN 269.1959 / fisher_kpp mean 11.9931 / cahn_hilliard NN 23.1803 /
  ifc_poisson NN 10.0549.
- **Noise floor** (`state/noise_floor.json`, `_provisional: true`,
  `_source: round1-batch0-rescaled`): cahn_hilliard spread 0.4023,
  min_claimable_effect 1.1604; helmholtz spread/min 10.6811; pfc 0.5014/6.9839;
  allen_cahn 0.1283/14.8152; fisher_kpp 0.2680/1.2198; ifc_poisson
  0.2399/0.2399. Per program.md §4.3 a provisional floor is judged directly,
  not applied as a hard numeric gate — I still set the threshold above it.
- **Pre-falsified levers** (program.md §5 / r1 §5): WNO backbone swap, LF
  low-mode freezing, diffusion prior for point accuracy.
- **§12.2 mandated restatement, computed in summary §3**: `dc_cleaned` panel
  geomean **0.1232 → 0.3306** under corrected denominators. This is the stack's
  real-LF oracle ceiling and it is **69.8× better than the anchor 23.0636** —
  the headroom band B1 must locate itself inside.

## Proposal reasoning

### The topology is pre-directed; the design work is in the arms

§12.2 fixes the pipeline (emulator → DC corrector) and names three arms. It
does *not* say how to make the frozen/fine-tuned/end-to-end contrast
**identifiable**, and the websearcher's point 2 says the attribution is the
only open contribution. So the whole of my design effort goes into
identifiability. Three decisions follow.

**Decision A — one emulator, trained once, shared by every arm.** If each arm
trained its own emulator, the `frozen − fine-tuned` delta would be confounded
by emulator-to-emulator variation and the shift estimator would be
uninterpretable. Pre-registering a single shared emulator checkpoint makes
every arm an *in-job paired control* on identical pseudo-LF fields — which the
**drift-class rule** (r1 report §5.6: at n_eff/N < 1% only in-job paired
controls are controls) demands here, and which matters doubly because r2s1-B1
runs in parallel and its direct-condition→HF numbers will not exist when this
card is analyzed.

**Decision B — emulate the LF on its NATIVE grid, then upsample with the
CORRECTED convention.** I checked the grids: the corrector's `S6_LF_FID=max`
rung is 128² (cahn_hilliard), 64² (pfc), 24² (helmholtz) against HF 256²/128²/96².
Two consequences:
1. Predicting the native-grid LF is the only version of this design where the
   "bottleneck" is a real dimensional reduction (4×–16× fewer outputs). If I
   instead had the emulator predict `LF_up` directly on the HF grid (the
   rejected alternative), the emulator's output dimension equals the HF field's
   and the nested-ladder degeneracy (r1 report §6) becomes total — the emulator
   would be a direct condition→HF model wearing a hat, and the stream's
   question would be unanswerable by construction.
2. Upsampling must use the **corrected** convention (`node_aligned_periodic` /
   `dirichlet_node` / `legacy_cell_centred`, keyed exactly as
   `round2/eval/panel_data.py` keys them), vendored into the family dir with a
   provenance comment. Vendoring rather than importing follows the s4_router
   precedent for a hard reason recorded in its `lsi_filter.py` docstring:
   `score_panel.py::code_hash` hashes `family_dir/**/*.py`, so logic outside the
   family dir is invisible to the cache key and can silently poison a score.
   This also means the corrector is **re-fit** on the corrected data path rather
   than loading round-1 weights — so "frozen" here precisely means *frozen with
   respect to the pseudo-LF distribution* (fit on real train LF, never sees
   pseudo-LF), not "round-1 checkpoint". Stating this exactly is necessary to
   avoid a reviewer FAIL on the declared-reuse rule.

**Decision C — add a conditional-mean LF control that §12.2 does not ask for.**
This is the design's one genuinely additive idea and it comes from ADR r2-0003.
The ADR established that on pfc / fisher_kpp / allen_cahn the realized IC is
absent from the condition vector and **present in the LF field** (pfc: nearest
condition pair differs by 1.148 *in `train_l1.npz`*; fisher_kpp 0.412 in LF).
A condition-only emulator therefore inherits the identical conditional-mean
bound: its best possible output on those datasets is E[LF | c], a featureless
field. The stack cannot beat the conditional-mean floor there, whatever the
corrector does.

That is a prediction, and it is cheap to make *decisive* rather than merely
argued: add an arm that feeds the frozen corrector the **train-mean LF field**
(constant across samples, zero emulator capacity, zero trained parameters in
the LF stage). Then

  `frozen − condmean_lf` = exactly the information the emulator's pseudo-LF
  carries *beyond* knowing nothing sample-specific about the LF.

ADR r2-0003 predicts this delta is ≈ 0 on pfc / fisher_kpp / allen_cahn and
> 0 on cahn_hilliard (16 of 19 dims are `ic_c*`) and helmholtz. Note the
corrector remains FiLM-conditioned on `cond` in this arm, so it is not a
strawman — it is "the corrector with full condition information and no LF
information", which is the right null.

### Arms (5 scored, 1 emulator, all paired on identical splits)

| arm | LF input at test | LSI (T, α) fit on | LocalCorrector trained on | role |
|---|---|---|---|---|
| A1 `emul_only` | pseudo-LF (upsampled) | — (no cleaning) | — (no corrector) | stack's internal floor + in-job direct-condition→HF control |
| A2 `frozen` | pseudo-LF | REAL train LF | REAL train LF cleaned residual | **PRIMARY** — pure distribution-shift exposure |
| A3 `finetuned` | pseudo-LF | T fixed from A2; α refit on pseudo | init from A2, fine-tuned on (pseudo-LF, HF) train pairs | shift-adapted; **A2 − A3 = shift estimator** |
| A4 `end_to_end` | pseudo-LF | jointly | emulator + corrector trained jointly, HF loss only, init from A2 | CALM-PDE §4.3 prediction test |
| A5 `condmean_lf` | **train-mean LF** (constant) | REAL train LF | REAL train LF cleaned residual | ADR r2-0003 decisive null; **A2 − A5 = value of the emulator** |

Sidecars (diagnostic JSON only, computed on a held-out slice of the **TRAIN**
split, which legitimately carries LF — no test LF is touched, so §5.9 is not
engaged; the websearcher flagged this construction and asked that it be
confirmed with the builder/reviewer, which the card will request):
- **S1 `emulator_field_error`** — nRMSE(LF̂, LF_real) per dataset. The emulator
  error in field units, which is the first term of the decomposition.
- **S2 `oracle_realLF_trainheldout`** — the A2 corrector fed REAL LF on the same
  held-out train slice: the "perfect emulator" ceiling, measured in-job.
  Cross-check against the external restatement 0.3306 from summary §3.

The full decomposition then reads: A1 vs A2 (does the corrector add anything
over raw pseudo-LF?), A2 vs A5 (does pseudo-LF carry sample-specific
information at all?), A2 vs A3 (shift penalty), A2/A3 vs A4 (two-stage vs
end-to-end), S2 vs A2 (emulator-error contribution). No fetched source performs
this decomposition — that is the D2 claim, and nothing beyond it is claimed.

### Round-1 findings folded in (and one round-1 defect repaired)

- **Drop the trust head and the router entirely.** Round 1 measured their panel
  contribution at *exactly* 0.000000 (r1 report §2, §4: "the routing and
  trust-head machinery added exactly zero on the panel, for a structural
  reason"). Carrying them would add ~20 env knobs and zero information.
- **BC-match rule**: LSI eligibility is decided **training-free before the run**
  via `tools/spectral_prestage_bc_audit.py` (adapted to round-2 paths), recorded
  as sidecar P1. Pre-registered expectation: cleaning eligible on the four
  periodic sharp datasets, α → 0 on helmholtz — round-1's validity gate V2
  observed exactly that self-selection, so it becomes gate V5 here.
- **Wrap-seam caveat** carried on every pfc claim (deep-bulk ratio 0.908), and
  the corrected upsampler (Decision B) is precisely round 1's never-applied
  "corrector-input wrap-seam fix" from its between-rounds list.
- **Repairing the round-1 D3 asymmetry**: the s4-B3 review recorded "the D3
  contrast is mildly asymmetric — dc_cleaned consumes val_idx twice, dc_raw
  once." Here every arm consumes **disjoint, identically-sized val sub-slices**
  (`val_a` for the LSI α line-search, `val_b` for the gate/scalar selector),
  identical across arms — so no arm sees more validation data than another.
  Knob `R2S2_VAL_DISJOINT=1`.
- **ifc_poisson tripwire**: round 1's DC arms silently collapsed to the champion
  transfer path there because the *test* split ships no LF
  (`S6_FALLBACK_NO_TEST_LF=champion`). Pseudo-LF removes that excuse, so the
  fallback must be *impossible*: `R2S2_REQUIRE_PSEUDO_LF=1` asserts it never
  fires (gate V6). Without this the ifc_poisson column would be a silent no-op.

### Alternatives weighed and rejected

1. **Emulator predicts `LF_up` on the HF grid.** Rejected — see Decision B.2:
   it makes the nested-ladder degeneracy total and the stream's question
   unanswerable.
2. **Emulate the *lowest* LF rung (l1, r = 4) instead of `S6_LF_FID=max`
   (l2, r = 2)** for a stronger bottleneck. Genuinely attractive (the r = 2
   bottleneck is weak — summary §6.1), but it changes the corrector's lineage
   away from the `dc_cleaned` stage §12.2 names, and the **lineage-bound
   caveat** says a rule fit on one library does not transfer. Rejected for B1;
   recorded as the natural B2 axis, since B1's S1 sidecar measures exactly the
   quantity (emulator field error per rung) that decides whether it is worth it.
3. **Load round-1 corrector checkpoints verbatim instead of re-fitting.**
   Rejected: round-1 weights were fit against the *defective* upsampling and
   reference; re-fitting on the corrected path is both required for a valid
   comparison and permitted (round-1 branches stay immutable; only code is
   vendored, per §12.2).
4. **Include a real-LF-at-test oracle arm as a scored panel arm.** Rejected —
   direct §5.9 violation (stripped test view). Demoted to the train-held-out
   sidecar S2, which answers the same question legally.
5. **Skip the slot.** Rejected: §12.2 pre-directs B1, the anchor and floors are
   frozen and non-provisional, and the design has a decidable falsification.

## Proposal

- **Category**: `mf_composition / condition→pseudo-LF emulation feeding a
  real-LF-trained defect corrector, with an in-job attribution decomposition of
  stacked error into emulator error, distribution shift, and the
  conditional-mean barrier`
- **Card type**: `model`
- **Motivation**: The stack topology is not novel — the websearcher's verdict is
  verbatim: *"D1 — `preempted (cite)`: Xu, Cao, Yuan, Meschke (2023),
  https://arxiv.org/abs/2310.00057 — frozen LF DeepONet subnet whose predicted
  LF output feeds a residual subnet; Yang et al. (2025),
  https://arxiv.org/html/2503.17941v1 — names 'residual-learning frameworks that
  sequentially combine low and high-fidelity predictions' as an existing
  class."* The stream's claim therefore sits on D2,
  *"`preempted-but-MF-composition-open`"*, where the websearcher records that
  **no fetched source decomposes stacked error into emulator error + downstream
  distribution shift, nor uses the frozen−finetuned delta as the shift
  estimator, on field-valued PDEs**, and that **no source quantifies a
  real-LF-trained corrector's degradation on emulated LF inputs**. B1 measures a
  known composition in an unmeasured regime (copy-LF skill, no solver at test,
  N_hf ∈ {5, 400}) and adds the attribution.
- **Concrete config**: family `models_r2/r2s2_stack`. FiLM-FNO emulator
  (`FNO2d`-class, coords-only input, FiLM on the condition at every block;
  width 64, 4 blocks, 12×12 modes) mapping condition → LF field on the LF rung's
  **native** grid, trained with relative-L2 against the real train LF at
  `S6_LF_FID=max`; a vendored **corrected** upsampler (convention keyed per
  dataset exactly as `round2/eval/panel_data.py`) lifting pseudo-LF to the HF
  working grid; then the round-1 `dc_cleaned` stage vendored with provenance
  from `round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router/`
  (`lsi_filter.py` closed-form Wiener T(k) + α line-search including 0;
  `local_corrector.py::LocalCorrector` `local_pixel_gate` variant, kernel 7,
  depth 4, width 32, zero-init head), router and trust head **removed** (round-1
  panel contribution exactly 0.000000). One emulator trained once and shared by
  all arms; 5 arms A1–A5 as tabulated above; sidecars S1/S2 plus the
  training-free P1 (BC-match audit) and P2 (condition→LF identifiability probe:
  nearest-condition train-pair relative LF difference per dataset, the ADR
  r2-0003 method applied to the LF fields, recorded *before* training so the
  falsification is decidable). Epoch budget split 50/50 by
  `R2S2_EPOCH_SPLIT=0.5` so total optimizer epochs per arm = the tier's 200.
  Six pre-registered in-process validity gates V1–V6 (V1 `emul_only` bit-equals
  the upsampled emulator output; V2 family never opens a non-HF test path;
  V3 `frozen` corrector state sha256 identical to the real-LF fit; V4
  `condmean_lf` LF input has zero across-sample variance; V5 α == 0 selected on
  helmholtz; V6 pseudo-LF fallback never fires).
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

- **Expected outcome**: primary metric is the panel geomean skill of the best
  stack arm. It is bracketed on both sides by numbers I computed: the real-LF
  oracle ceiling **0.3306** (dc_cleaned restated under corrected denominators,
  summary §3) and the anchor **23.0636**. I expect the best arm to land at
  **panel geomean ≈ 2–8**, i.e. **3–10× better than the anchor** but 10–25×
  short of the oracle — because the geomean is dragged up by the three
  ADR r2-0003 datasets where the stack is capped at the conditional-mean floor
  (train_mean skills pfc 59.81, fisher_kpp 11.99, allen_cahn 562.03) and pulled
  down by cahn_hilliard / helmholtz / ifc_poisson where the condition is
  (near-)complete. Per dataset: **cahn_hilliard 3–10** (vs NN floor 23.180 —
  the claim-bearing dataset, Δ ≥ 13 skill units vs the anchor, far above the
  provisional min_claimable_effect 1.1604); **helmholtz 1.5–3** (vs zero floor
  3.3441, but the provisional min_claimable_effect there is 10.6811 — larger
  than the entire plausible range — so helmholtz stays **report-only** per r1
  report §5.3 and carries the zero-floor column, and **no helmholtz-only claim
  is made**); **pfc / fisher_kpp / allen_cahn**: at or near the train_mean floor
  with `frozen − condmean_lf ≈ 0` (the pre-registered ADR r2-0003 prediction);
  **ifc_poisson 2–10**, anecdote-grade at N_hf = 5, but the DC lineage runs
  there for the first time. Secondary: shift penalty `A2 − A3` expected > 0
  (pre-registering CALM-PDE §4.3's direction: end-to-end ≥ two-stage, so
  A4 ≤ A2; a frozen-arm win would be a **reportable inversion**, per the
  websearcher's point 3). pfc claims carry the wrap-seam caveat (deep-bulk ratio
  0.908) and the band-limited denominator caveat.
- **Expected falsification**: On `sharp__cahn_hilliard` — the one panel dataset
  whose condition vector is IC-complete (16 of 19 dims are `ic_c*`) and hence
  the only one where the stacking premise is identifiable at all — the design is
  falsified if the best stack arm fails to improve on the in-job `emul_only` arm
  by at least **2.0 skill units** *and* fails to beat the frozen
  NN-in-condition floor **23.180**, both margins exceeding that dataset's
  provisional noise floor (spread **0.4023**, min_claimable_effect **1.1604**),
  since that would show the LF representation is not a useful bottleneck even
  where the emulator can in principle be accurate.
- **Anchor reference**: `null` (program.md §4.5 — null for all four round-2
  streams; `r2s2_stacked` is a lever stream and its own anchor 23.0636 is
  implicit).

## Status

- **Slot covered**: yes — one `model` card, `r2s2_stacked-B1`.
- **Skipped**: no.
- **Reopen candidates resolved**: none exist (verified round-wide; summary §5).
- **Immutables self-check**: see below — **pass (11/11)**.

## Immutables self-check (positive evidence per item)

1. **Data read-only.** The family only *reads* `stripped_data/<ds>/train_l*.npz`
   and `train/fidelity_*` (LF at train is explicitly free, program.md §5.9) and
   writes exclusively to `--out`/`--ckpt_dir`/`R2S2_DIAG_OUT` under
   `mffp_autoresearch_outputs/round2/`. No regeneration, no extra HF; N_hf stays
   400 (sharp, verified `train_l3.npz x=(400,19)`) and 5 (ifc_poisson, verified
   `floors.json n_train_hf: 5`). LF is used as shipped — never downsampled HF.
2. **Panel + guard fixed.** `datasets: "panel"` resolves through
   `score_panel.py` to `project.yaml panel:` (the 6 listed datasets) and the
   guard invocation to `guard_set: [heat_local, fluid, sharp__sod_1d]`. The
   proposal names no dataset outside those nine.
3. **Eval layer / spec untouched.** The design requires zero edits to
   `round2/eval/`, `project.yaml`, `program.md`, or agent prompts: the corrected
   upsampler is **vendored into the family dir** with a provenance comment
   (s4_router precedent — its `lsi_filter.py` docstring records that
   `score_panel.py::code_hash` only hashes `family_dir/**/*.py`), not edited into
   or imported from `eval/`.
4. **One nRMSE definition.** The scored metric is whatever
   `round2/eval/nrmse.py` computes via `score_panel.py`; the emulator's
   relative-L2 *training* loss on LF targets is a training loss, which §5.4
   leaves free, and the S1 field-error sidecar is a diagnostic, not a scored
   metric. The card will carry `nrmse_def_hash` / `copylf_def_hash` from the
   result JSONs.
5. **Contract CLI fixed.** The family exposes the unchanged six-arg
   `smoke_eval.py` signature; every knob above is passed via
   `score_panel.py --env KEY=VAL` and every one of them appears in the recipe
   `env` block, so the cache key covers them.
6. **Seeds / tier epochs fixed.** `seeds: [0]` (project.yaml
   `seed_protocol.seeds: [0]`, r1 ADR 0004 strict 1-seed in round);
   `epochs: 200` = `tiers.smoke_epochs`; contract tier 2 for the plumbing check.
   `R2S2_EPOCH_SPLIT=0.5` divides the tier's 200 epochs *within* the pipeline
   (emulator 100 + corrector 100) and never exceeds it — the tier budget is
   respected, not changed.
7. **Guarded factory surfaces untouched.** Nothing under
   `mf_field/factory_mffp/{eval,baselines,references,scripts,data}`, `factory.md`
   or `akash/` is read-for-write or modified; all new code lands in
   `<worktree>/models_r2/r2s2_stack/`, and the round-1 donor worktree is read
   only to copy source text (round-1 branches stay immutable, §5.13).
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`.** Implementable and required:
   the pipeline has two sequential trained stages, so `last.pt` stores
   `{emulator_state, lsi_T_packed, alpha, corrector_state, gate_state, stage,
   epoch, arm}` — `lsi_filter.py::pack_transfer` already exists precisely to
   make the closed-form `T(k)` checkpoint-safe (`torch.save` handles plain numpy
   arrays), and `LocalCorrector`/`PixelGate` are ordinary `nn.Module`s.
9. **Falsification threshold vs the noise floor.** The clause cites exactly one
   dataset, `sharp__cahn_hilliard`, whose `state/noise_floor.json` entry is
   `spread: 0.40225775785804174`, `min_claimable_effect: 1.1603569120520159`.
   The required margin is **2.0 skill units**, which exceeds both (2.0 > 1.1604
   > 0.4023). The second limb, "fails to beat the NN floor 23.180", is a
   comparison against a **frozen deterministic** floor
   (`state/anchors/floors.json`), which carries no seed noise at all. I
   deliberately did **not** hang the clause on helmholtz, whose provisional
   min_claimable_effect (10.6811) exceeds the entire plausible effect range —
   helmholtz is report-only. Noted: `state/noise_floor.json` is
   `_provisional: true`, so per program.md §4.3 this is judged directly and will
   be re-checked against r2s4-B1's certified condition→HF spread.
10. **Not a pre-falsified lever.** The three pre-falsified levers are the WNO
    backbone swap, LF low-mode freezing, and a diffusion prior for point
    accuracy. Nearest is **LF low-mode freezing**. Difference: nothing spectral
    is frozen here — the LSI stage fits a full |k|-dependent Wiener transfer
    `T(k)` with an α line-search that includes 0, and the word "frozen" in this
    card refers to the corrector's *parameters being held fixed with respect to
    the pseudo-LF distribution* (fit on real train LF, never exposed to
    pseudo-LF). The falsified lever also presupposed a **real** LF input, which
    does not exist at test in round 2. No pre-falsified lever is re-proposed.
11. **Mandatory floor arms.** Part 5 will report, next to every arm and per
    dataset, the frozen **NN-in-condition**, **train-mean**, and **zero** floors
    from `state/anchors/floors.json`, including the standing zero-floor column on
    helmholtz. The floors are load-bearing in the reasoning, not decorative: the
    falsification clause's second limb *is* the NN floor (23.180), the expected
    outcome is stated per dataset against the floor arm that wins there, and arm
    **A5 `condmean_lf`** is a trained-corrector realization of the conditional-mean
    floor that makes the comparison paired and in-job.
