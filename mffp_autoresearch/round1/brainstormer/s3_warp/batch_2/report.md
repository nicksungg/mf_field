# Brainstormer Report — Stream `s3_warp`, Batch 2

**Stream**: `s3_warp`
**Batch**: 2
**Total iterations**: 1
**Slot filled**: 1 / 1 (`model` card, 4 comparator arms + 3 reference sidecars)
**Reopen candidates resolved**: 0 of 0 (none exist for this stream)

## Slot

- **Category**: `mf_composition / one-sided warp-then-correct on the corrected
  LF->HF path -- displacement-vs-intensity attribution on sharp__cahn_hilliard`
- **Card type**: `model`
- **Motivation**: B1 part 7's gate question -- *"is that displacement field
  PREDICTABLE from the LF field a model actually receives, or is it only visible
  to an HF-fitted oracle?"* -- is exactly the slice the batch-2 websearch found
  open. Verdict (i), verbatim: *"preempted-but-MF-composition-open ... The
  **one-sided** instance: displacement predicted from the LF PDE field +
  condition vector with **no target field at inference**, applied to that field
  before a learned correction, inside an MF operator surrogate at small N_hf.
  Registration is pairwise; mesh-movement nets output nodes not fields; MF/SR
  fusion is value-space. Every *component* (band-limited Fourier displacement
  head, supervised warp targets, single-interpolation warp) is published -- the
  claim is composition + measurement, on ONE dataset (floor 0.553)."* Verdict
  (iii), verbatim: *"**No fetched source, in any field, reports a quantitative
  per-term attribution of a displacement-vs-intensity error split** -- and none
  does it across two fidelities of one PDE solve."* B1 measured the ceiling
  (83.4-85.2 % of a correctly registered copy-LF's error removable on
  `sharp__cahn_hilliard`, residual median `|phi|` 0.64-0.74 HF cells,
  LSI-refractory at 0.44) but its only learnability evidence was taken against
  the **misregistered** reference, where the retrieved quantity was mostly the
  0.5-cell grid convention. This card replaces that HF-fitted upper bound with
  an LF-only achievable number, and pre-registers the comparators that make the
  number attributable.
- **Concrete config**: new contract family `models_r1/s3_warp_onesided`
  (CLI unchanged), one invocation of the unmodified
  `eval/score_panel.py --datasets sharp__cahn_hilliard --epochs 200 --seed 0`.
  - **Shared input path (JUBW-compliant, ONE interpolation)**: raw LF
    `field_by_fid[2]` (128^2) sampled once at node-aligned HF coordinates
    `k/2 + phi_k/2` (HF `fid 3`, 256^2, r=2, 400 train / 100 test, `cond_dim 19`),
    circular padding. `phi = 0` therefore reproduces B1 F3 variant C (0.4769)
    exactly; the second bilinear resample B1 F10/F17 blames for the mid-band
    penalty never happens. JUBW's cited extra trick used: sub-cell fractional
    offsets passed to the corrector as input channels.
  - **One-sided displacement head**: small FNO-style encoder on the raw LF +
    broadcast 19-d condition -> `16x16x2 = 512` low Fourier coefficients
    (Fourier-Net band-limited parameterization, exactly B1's C16 dof per F13),
    zero-pad + iFFT decode to 256^2, `|phi|` projected onto a 4-cell ball.
    Single-scale (sub-voxel regime, SuperWarp). Inference inputs: LF + condition
    ONLY -- no HF, no PDE (ADR 0009), auditable via
    `tools/lf_at_inference_audit.py`.
  - **Supervision**: `L = relL2(pred,HF) + mu * mean_w|phi - phi_oracle|^2`,
    `w = |grad LF| / mean|grad LF|` (gradient-evidence mask, the SuperWarp
    untextured-bulk remedy), `mu` 1.0 -> 0.1 at 50 % of epochs. `phi_oracle`
    from re-running B1's vendored fitter on the **train split** against the
    **corrected** moving image (B1's saved `p_train` is unusable -- it was fitted
    on the misregistered image).
  - **Correction stage**: 4-block ConvNeXt-style corrector, width 48, circular
    padding, ~70-80 k params (same class/size as s6_local-B1's 77 k), trained
    jointly; absorbs the 5-6 % topology-mismatch residual (scoping, not
    metamorphosis -- 12.3's own escape clause).
  - **Arms** (one process, one job, seed 0; only `test_hf` is scored because
    `score_panel._extract_test_metric` selects `test*`):

    | key | arm | trained | role |
    |---|---|---|---|
    | `test_hf` | one-sided warp + correction | yes | **SCORED** proposal |
    | `ref_warp_off` | identical net, `phi` forced 0, + correction | yes | architecture-level warp-off control (B1 part 4, LOCKED); the s6-class correction baseline |
    | `ref_const_disp` | `phi` = one global 2-vector per sample + correction | yes | CONSTANT-DISPLACEMENT-ONLY arm (MANDATORY, B1 part 7 / F12) |
    | `ref_lsi` | zero-parameter closed-form LSI on the same input path | 0 trained params | value-add over the defect-correction class (s6's definition) |
    | `ref_reg_corrected` | `phi = 0`, no correction | no | registration-corrected reference sidecar (B1 part 7 item 3) |
    | `ref_frozen_copylf` | `panel_data.copylf_prediction`, unedited | no | frozen reference / seam, skill 1.0 |
    | `ref_oracle_phi` | oracle `phi` (test-HF-fitted) + trained corrector | no | ceiling, report-only, `do_not_promote` |

  - **Hard-stop seams**: S1 frozen copy-LF == 0.08765999100758841 to <=1e-9;
    S2 `ref_reg_corrected` reproduces B1 F3 variant C 0.4769 +-2 %; S3 vendored
    `warp_core.py` reproduces B1's recorded C16 nRMSE <=1 % on the misregistered
    path; S4 vendored LSI reproduces s6_local-B1's `skill_LSI` 0.4400-0.4413
    +-2 %; S5 zero Fourier coefficients give `phi == 0` and the warp arm's
    zeroed forward equals `ref_warp_off`'s at init.
  - **Free diagnostics** (sidecar): endpoint error vs oracle `phi` (masked and
    unmasked), median/p90 `|phi_pred|`, inverse-consistency error `E_IC`
    (diagnostic ONLY, never a loss), captured share of the oracle benefit,
    per-band error ratios on B1's band edges, skill stratified by LF/HF
    component mismatch, and an in-repo-derived (NOT cited) phase-field interface
    displacement statistic.
  - Checkpoint resume from `<ckpt_dir>/last.pt` (`{arm_index, epoch, model,
    optimizer, RNG, cached oracle-phi}`), arms sequential. Submit-time job env
    `ROUND1_EVAL_RESULTS=<outputs>/s3_warp/B2/eval/results` (B1 precedent, not a
    scoring knob). Contract-tier 2-epoch plumbing screen first (non-reportable,
    ADR 0007). No guard legs -- the family's declared support is a 2-D nested
    periodic dyadic ladder; guard legs recorded as an owed promotion
    precondition. ~25-35 min on one H100 (ADR 0005); suggested `--time 02:00:00`.

- **Recipe**:
```json
{
  "base_family": "none as a trained base (new family, built from scratch). TWO modules VENDORED VERBATIM with provenance headers: (a) worktrees/s3_warp/B1/models_r1/s3_warp_oracle/warp_core.py from branch round1/exp-s3_warp-B1 @ 4799abdec705d64e8300b18ab0650fb74e012c9b -> models_r1/s3_warp_onesided/warp_core.py (oracle-phi fitter, unmodified, seam S3); (b) fit_transfer/apply_transfer/rho from mffp_autoresearch/round1/tools/defect_correction_learnability.py -> models_r1/s3_warp_onesided/lsi_ref.py (s6_local-B1's LSI definition, unmodified, seam S4). No checkpoint is reloaded from any prior model.",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/s3_warp_onesided",
  "datasets": "sharp__cahn_hilliard",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "S3W2_ARMS": "warp,warp_off,const_disp",
    "S3W2_SCORED_ARM": "warp",
    "S3W2_RESAMPLE": "node_bilinear_single",
    "S3W2_PAD": "circular",
    "S3W2_JUBW_OFFSET_CH": "1",
    "S3W2_PHI_MODES": "16",
    "S3W2_PHI_MAX_CELLS": "4",
    "S3W2_PHI_SUP_MU": "1.0",
    "S3W2_PHI_SUP_MU_LATE": "0.1",
    "S3W2_PHI_SUP_ANNEAL_FRAC": "0.5",
    "S3W2_PHI_SUP_MASK": "grad",
    "S3W2_CORR_BLOCKS": "4",
    "S3W2_CORR_WIDTH": "48",
    "S3W2_LR": "1e-3",
    "S3W2_BATCH": "8",
    "S3W2_ORACLE_RUNGS": "0,4,16",
    "S3W2_ORACLE_ITERS": "400",
    "S3W2_ORACLE_LR": "0.02",
    "S3W2_ORACLE_LAMBDA": "1e-3",
    "S3W2_LSI_RIDGE": "1e-6",
    "S3W2_EIC": "1",
    "S3W2_SEAM_TOL": "0.02",
    "S3W2_DIAG_OUT": "${OUTPUTS_ROOT}/s3_warp/B2/eval"
  }
}
```

- **Expected outcome**: scored metric = `nRMSE` on `sharp__cahn_hilliard`
  `test_hf`, reported as skill vs the frozen copy-LF reference
  0.08765999100758841 (skill 1.0).

  | key | predicted skill | grounding |
  |---|---|---|
  | `ref_frozen_copylf` | 1.000 exactly | seam S1 |
  | `ref_reg_corrected` | 0.477 +- 0.01 | B1 F3 variant C 0.4769 (seam S2) |
  | `ref_lsi` | 0.42-0.46 | B1 F15 (0.4631 -> 0.4402 corrected) |
  | `ref_warp_off` | 0.40-0.47 | s6_local-B1 trained corrector 0.4686 |
  | `ref_const_disp` | 0.40-0.47, within 0.03 of `ref_warp_off` | B1 F11 (residual DC <= 0.13 cells); F12's 48.9 % was the grid convention |
  | **`test_hf`** | **0.15-0.35** (central 0.25) | 0.44 x (1 - 0.85f), f = captured share of B1's 83.4-85.2 % ceiling |
  | `ref_oracle_phi` | 0.06-0.09 | B1 F9 ceiling on the corrected C0 |

  Delta vs the anchor (`s3_warp-B1`): B1 is a `do_not_promote` diagnostic with no
  numeric anchor file; its legacy numbers are the 83.4-85.2 % oracle ceiling and
  the (uninformative, misregistered-path) 63-99 % retrieval bracket. The card's
  move is to convert the ceiling into an LF-only achievable share -- predicted
  30-70 % of it captured.
  **vs the noise floor** (`state/noise_floor.json sharp__cahn_hilliard`:
  `spread 0.19182714769533593`, `min_claimable_effect 0.5533465853654416`):
  Leg A's effect `1 - 0.440 = 0.560 > 0.5533` (2.92x `spread`), predicted
  0.65-0.85 -> clears. Leg B's arm-vs-arm threshold `0.20 > 0.19182714769533593`
  clears the certified `spread`; it cannot clear `min_claimable_effect`, which is
  arithmetically impossible here (see Leg B').

- **Expected falsification**: the one-sided displacement head is falsified as a
  mechanism if it fails to beat the best of `{ref_warp_off, ref_const_disp,
  ref_lsi}` by more than 0.20 skill units on `sharp__cahn_hilliard` (equivalently
  captures <= 51 % of B1's certified 83.4-85.2 % oracle ceiling) with seams
  S1-S5 passed -- in which case the residual displacement is oracle-visible but
  not LF-predictable and B1 part 7's close-out applies; the separate claimability
  leg is falsified if the scored skill exceeds 0.440 (effect vs the frozen
  reference < 0.560 < `min_claimable_effect` 0.5533).

  Full pre-registered leg set (verbatim from `iteration_1.md`):
  - **Leg A (claimability, clears 0.5533)**: falsified if `skill(test_hf) > 0.440`.
    Predicted not to fire; passing attributes nothing on its own (the
    zero-parameter LSI already reaches 0.4402).
  - **Leg B (attribution, threshold 0.20 > `spread` 0.19182714769533593)**:
    falsified if `skill(test_hf) > min(skill(ref_warp_off),
    skill(ref_const_disp), skill(ref_lsi)) - 0.20`.
  - **Leg B' (parent-directed strict reading, pre-registered UNATTAINABLE)**:
    margin `> 0.5533` over both controls -- recorded and reported, but its
    firing is NOT evidence about the warp, because `max margin =
    skill(control) ~ 0.47 < 0.5533` given `skill >= 0` and s6_local-B1's
    measured control-class skill 0.4686. Its purpose is to document that the
    anchor-referenced `min_claimable_effect` convention is degenerate on
    copy-LF-referenced panel datasets. **This is the card's second deliverable
    and is mentor-facing.**
  - **Leg C (mechanism honesty, reported)**: if Leg B passes while median
    `|phi_pred| < 0.1` cells or the masked endpoint error exceeds the oracle
    median `|phi|` (0.64-0.74), the win is intensity correction mislabelled as
    warping and must be reported as such.
  - **Leg D (scoping cost, reported)**: skill on the 5-6 % topology-mismatch
    subset reported separately; > 2x the matched subset makes scoping the
    binding limitation for B3.

- **Prior-art verdict quoted**: (i) *"preempted-but-MF-composition-open"* --
  citations `Flowers https://arxiv.org/html/2603.04430`,
  `MetaRegNet https://arxiv.org/pdf/2303.09088`,
  `Khamlich https://arxiv.org/html/2603.04232v2`,
  `Fourier-Net https://arxiv.org/abs/2211.16342`,
  `SuperWarp https://pmc.ncbi.nlm.nih.gov/articles/PMC9645132/`,
  `M2N https://arxiv.org/abs/2204.11188`, `UM2N https://arxiv.org/abs/2407.00382`,
  `weather-SR flow matching https://arxiv.org/html/2604.00897`; open part
  verbatim: *"The **one-sided** instance: displacement predicted from the LF PDE
  field + condition vector with **no target field at inference**, applied to that
  field before a learned correction, inside an MF operator surrogate at small
  N_hf. Registration is pairwise; mesh-movement nets output nodes not fields;
  MF/SR fusion is value-space. Every *component* (band-limited Fourier
  displacement head, supervised warp targets, single-interpolation warp) is
  published -- the claim is composition + measurement, on ONE dataset (floor
  0.553)."* (ii) *"preempted (cite)"* -- `JUBW: Makansi/Ilg/Brox
  https://arxiv.org/abs/1707.00471`, open part verbatim: *"**Nothing.** The 2017
  motivation is verbatim B1 F17 ... It is an implementation obligation to cite,
  never a contribution."* (iii) *"preempted-but-MF-composition-open (weak
  novelty, strong measurement value)"* -- `MI2A
  https://arxiv.org/abs/2504.11433`, open part verbatim: *"**No fetched source,
  in any field, reports a quantitative per-term attribution of a
  displacement-vs-intensity error split** -- and none does it across two
  fidelities of one PDE solve. Joint-vs-sequential cannot be settled by citation
  (ablations point both ways) -> must be a control arm."* Also cited for the
  GT-free diagnostic: `inverse-consistency error
  https://pmc.ncbi.nlm.nih.gov/articles/PMC3915046/`.
- **Immutables self-check**: **pass (10/10)** — full positive evidence per item
  in [iteration_1.md](iteration_1.md) ("Immutables self-check"). One item flagged
  and resolved by declaration rather than revision: item 9 -- Leg B's arm-vs-arm
  threshold clears the certified `spread` (0.20 > 0.19182714769533593) but cannot
  clear the anchor-referenced `min_claimable_effect` (0.5533465853654416),
  because `skill(ref_warp_off) ~ 0.4686` (s6_local-B1, measured) and `skill >= 0`
  bound any arm-vs-arm margin at ~0.47. Leg A carries the floor instead
  (effect 0.560 > 0.5533) and Leg B' pre-registers the impossibility as a
  reported finding -- the same treatment `s3_warp-B1` part 4 gave the identical
  structural property ("This is declared, not worked around").
- **Anchor reference**: `"s3_warp-B1"`
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| (none) | n/a | `s3_warp-B1` is `status: complete`, `reopen_candidate: false`; the retired `s3_testtime-B1` belongs to a different, retired stream (ADR 0010) | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| `s3_warp-B2` | `mf_composition / one-sided warp-then-correct + attribution` | One-sided band-limited displacement head (supervised on re-fitted train-split oracle `phi`, single JUBW-compliant resample of the raw LF) + joint correction on `sharp__cahn_hilliard`, against a warp-off control, a constant-displacement arm, a zero-parameter LSI comparator and a registration-corrected sidecar | filled |
