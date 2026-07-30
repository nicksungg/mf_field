# iteration_1 — `s3_warp` batch 2 design

## Design context considered

- `summary_so_far.md` section 6 (six unknowns), especially U1 (is the residual
  displacement predictable from LF+cond?), U3 (does the constant arm still buy
  anything on a corrected input path?) and U5 (the floor arithmetic).
- Prior-art verdict (i) `preempted-but-MF-composition-open`, (ii)
  `preempted (cite)` JUBW, (iii) `preempted-but-MF-composition-open` (weak
  novelty, strong measurement value).
- program.md 12.3 verbatim (quoted in `summary_so_far.md` section 2): warp-then-
  correct vs additive correction; physics-agnostic (ADR 0009); topology
  requirement satisfiable "or scope to datasets where topology is preserved".
- The 8 immutables (program.md section 5), reproduced in the self-check below.
- Noise floor `sharp__cahn_hilliard`: `spread 0.19182714769533593`,
  `min_claimable_effect 0.5533465853654416`, `mean_skill 5.533465853654415`.
- Pre-falsified levers (program.md section 5): WNO backbone swap, LF low-mode
  freezing (`mf_fno_spectral`), diffusion prior for point accuracy.
- ADR 0004 (strict single seed, seed 0), ADR 0005 (H100), ADR 0007 (propose-many
  where applicable), ADR 0009 (no known physics at test time).
- B1 part 7's three mandated comparators and three implementation notes.
- s6_local-B1's measured trained-corrector skill on this dataset: **0.4686**.

## Proposal reasoning

### What the slot has to be

B1 closed with an explicit gate: *"is that displacement field PREDICTABLE from
the LF field a model actually receives, or is it only visible to an HF-fitted
oracle?"* and prescribed a narrow D1 model card on `sharp__cahn_hilliard` with
three comparators. The websearch says the ONE-SIDED instance (no target field at
inference) is the open composition and that the attribution measurement is
unreported anywhere. Those coincide. So: one `model` card, four arms, one
dataset.

### Alternatives weighed and rejected

1. **Re-run B1's diagnostic on the corrected path (another diagnostic card).**
   Rejected: the retrieval bracket is a *lower* bound with a stated confound
   ("a field-conditioned learned head can exceed retrieval"), so a negative
   would not close the stream and a positive would not be a model. The card
   below contains the retrieval-free version of this measurement for free
   (`ref_oracle_phi` prices the ceiling; the trained head prices the achievable
   share), so a separate diagnostic buys nothing.
2. **Add `ext__helmholtz_2d` as a report-only second transport dataset**
   (B1 part 7 suggested it). Rejected for this batch: its 24/96 Dirichlet
   interior-node grids are NOT nested, so the node-aligned single-interpolation
   resampler needs a second, different coordinate convention (B1 F5: the defect
   there is a zero-mean +-1.5-cell stretch, and the correct alignment gives
   0.9077, not ~0.46). That is a separate implementation surface with its own
   failure modes, on a dataset whose floor (9.695) makes it report-only anyway.
   Deferred to B3 with that reason recorded.
3. **Multi-scale / pyramid warp head.** Rejected on the websearcher's gift:
   SuperWarp's stated validity condition is sub-voxel displacement, and B1 F11
   measures 0.64-0.74 cells residual -- inside the single-scale regime. A pyramid
   adds parameters and code for a regime we are not in.
4. **Free-form (dense conv) displacement field.** Rejected: SuperWarp reports
   plain U-Net heads are worst in **untextured regions**, which on cahn_hilliard
   is the bulk; and B1 F13 shows only the C16 (16x16x2 = 512 dof) rung pays. A
   band-limited Fourier `phi` (Fourier-Net) matches both facts and is
   parameter-free on the decode side.
5. **Metamorphosis / intensity-deformation channel** for the 5-6 % topology-
   mismatch samples. Rejected per 12.3's own escape clause and the websearch:
   appearance-vs-geometry balancing is unsolved, the intensity channel steals
   work from the diffeomorphism, and cahn_hilliard is the panel's most nearly
   diffeomorphic dataset. Scope instead; the correction stage absorbs the
   residual topology error and the card reports the mismatch-stratified skill so
   the cost of scoping is measured, not assumed.
6. **Self-supervised / inverse-consistency warp training.** Rejected as a loss
   (Guo et al. 2021 many-to-one failure; LF->HF with topology loss is
   many-to-one). Kept as a free GT-free diagnostic (`E_IC`).
7. **Joint (single-stage) warp+correct vs sequential.** Cannot be settled by
   citation (ablations point both ways) -> the card trains warp and correction
   jointly end-to-end but the warp-off and constant-displacement arms are the
   control that makes the composition attributable, exactly as the websearcher
   demands ("must be a control arm, not an assumption").
8. **Comparing against the champion** (`mf_fno_pinn_transfer`, anchor skill
   5.533). Rejected as the primary comparator: s2-B1 M1 proves the champion is
   LF-blind at inference, so beating it measures nothing about warping. It is
   reported as context only.

### The floor problem, confronted

The parent's directive is "the warp arm must beat BOTH the warp-off control AND
the constant-displacement arm by > 0.553 skill". That reading is
**arithmetically unattainable on this substrate**, and I record the proof rather
than quietly softening it:

- every correction-class arm on `sharp__cahn_hilliard` sits at skill ~0.44-0.48
  (s6_local-B1 trained corrector **0.4686**; LSI closed form **0.4402**;
  zero-parameter node-aligned resample **0.4769**);
- `skill >= 0` by construction (it is a ratio of norms);
- therefore `max margin = skill(control) - 0 ~ 0.47 < 0.5533 =
  min_claimable_effect`.

So the card pre-registers **both** readings the parent asked for, in the only
honest arrangement:

- **Leg A** carries the round's certified floor and clears it: the effect is
  measured against the ONE reference the round pins at exactly 1.0 (frozen
  copy-LF), where an effect up to 1.0 is available. Threshold: scored skill
  `<= 0.440`, i.e. effect `>= 0.560 > 0.5533`. Necessary, **not** sufficient --
  it is also reachable by the zero-parameter LSI (0.4402), which is why Leg A
  alone attributes nothing.
- **Leg B** carries the science: margin over the BEST of the three
  correction/registration-class arms must exceed **0.20** skill units, which
  strictly exceeds the certified per-dataset seed `spread` 0.19182714769533593.
  Equivalently (arithmetic in "Expected outcome") the head must capture **> 51 %**
  of B1's certified oracle benefit.
- **Leg B'** is the parent-directed strict 0.553 arm-vs-arm reading, pre-
  registered **as unattainable with the proof above**. Its firing is not
  evidence about warping; recording it is the card's second deliverable -- a
  measured demonstration that the anchor-referenced `min_claimable_effect`
  convention is degenerate on copy-LF-referenced panel datasets where every arm
  sits far below skill 1. (B1 part 4 set the precedent: "This is declared, not
  worked around.")

### Why this is a genuine experiment either way

If Leg B does not fire, round 1 gains its first LF-consuming model that beats
the defect-correction class on a beyond-copy dataset, and the mechanism (moving
mass, not synthesizing it) is attributed by construction. If Leg B fires while
`ref_oracle_phi` confirms the 83-85 % ceiling, the finding is that the residual
displacement is **oracle-visible but not LF-predictable** -- which is precisely
B1 part 7's stated close-out condition for the stream ("the honest output is to
close s3_warp with a measured negative and hand the registration finding to the
benchmark, not to build the model"). Both outcomes answer 12.3's question.

## Proposal

- **Category**: `mf_composition / one-sided warp-then-correct on the corrected
  LF->HF path -- displacement-vs-intensity attribution on sharp__cahn_hilliard`
- **Card type**: `model`

### Motivation (quotes the prior-art verdict)

Verdict (i), verbatim: *"preempted-but-MF-composition-open ... The **one-sided**
instance: displacement predicted from the LF PDE field + condition vector with
**no target field at inference**, applied to that field before a learned
correction, inside an MF operator surrogate at small N_hf. Registration is
pairwise; mesh-movement nets output nodes not fields; MF/SR fusion is
value-space. Every *component* (band-limited Fourier displacement head,
supervised warp targets, single-interpolation warp) is published -- the claim is
composition + measurement, on ONE dataset (floor 0.553)."* Verdict (ii),
verbatim: *"preempted (cite) ... **Nothing** [remains open]. The 2017 motivation
is verbatim B1 F17 ... It is an implementation obligation to cite, never a
contribution."* Verdict (iii), verbatim: *"**No fetched source, in any field,
reports a quantitative per-term attribution of a displacement-vs-intensity error
split** -- and none does it across two fidelities of one PDE solve."*
B1's open question is the gate: *"is that displacement field PREDICTABLE from
the LF field a model actually receives, or is it only visible to an HF-fitted
oracle?"*

### Concrete config

New family `models_r1/s3_warp_onesided`, factory contract CLI unchanged
(`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`), invoked by
unmodified `eval/score_panel.py` at `--epochs 200 --seed 0 --datasets
sharp__cahn_hilliard`. All arms run in ONE invocation; only the warp arm is
written to `test_hf` (the single scored key -- `score_panel._extract_test_metric`
takes `test*`), every comparator to a `ref_*` key.

**Shared input path (JUBW-compliant; ONE interpolation).** Load the RAW LF at
its native grid (`field_by_fid[2]`, 128x128; HF `fid 3`, 256x256, r=2, 400 train
/ 100 test, `cond_dim 19`). Sample it once at node-aligned HF coordinates plus
the displacement: LF continuous index for HF node k is `k/2 + phi_k/2` (phi in
HF cells). Circular padding (the field is periodic pseudo-spectral; also removes
B1 F4's wrap seam). `phi == 0` therefore reproduces B1 F3 variant C exactly.
The second bilinear resample B1 F17/F10 blames for the mid-band penalty never
happens. JUBW's cited extra trick is used: the sub-cell fractional offsets are
passed to the correction net as two input channels rather than being hidden
inside the sampler.

**Displacement head (one-sided, band-limited).** A small FNO-style encoder on
the raw 128x128 LF plus the broadcast 19-d condition emits `K x K x 2 = 16x16x2 =
512` low Fourier coefficients (the exact dof of B1's C16 rung, F13); zero-pad +
inverse FFT decodes `phi` on the 256x256 grid (Fourier-Net, `arXiv:2211.16342`:
parameter-free decode, accuracy-neutral at 2.2 % of the parameters). `|phi|`
projected onto a 4-cell ball (B1 measured 0.64-0.74; B1's own 16-cell clamp let
the fitter absorb artefacts). Single-scale -- admissible because the target
displacement is sub-voxel (SuperWarp `PMC9645132`). Inputs at inference: LF
field + condition ONLY. No HF, no PDE, no governing equations (ADR 0009);
auditable with `tools/lf_at_inference_audit.py`.

**Supervision (SuperWarp: supervised warps beat self-supervised, EPE -80 %).**
Two-term training loss (training loss is free; the SCORED metric is untouched
and always `eval/nrmse.py`):
`L = relL2(pred, HF) + mu * mean_w[ |phi - phi_oracle|^2 ]`, with
`w = |grad(LF_resampled)| / mean|grad(LF_resampled)|` -- a gradient-evidence mask
(the SuperWarp untextured-bulk remedy: the regression term only speaks where
there IS evidence, and the band-limited parameterization extrapolates into the
bulk). `mu = 1.0` for the first 50 % of epochs, then 0.1. `phi_oracle` comes
from re-running B1's fitter (`warp_core.py`, vendored verbatim) on the
**train split only**, against the **corrected** moving image -- train-split HF is
legal, no physics is used, ADR-0009-safe, and B1's saved `p_train` cannot be
reused because it was fitted on the misregistered image.

**Correction stage.** One small ConvNeXt-style corrector (4 blocks, width 48,
circular padding, ~70-80 k params -- deliberately the same class and size as
s6_local-B1's 77 k corrector) on `[warped_LF, phi_y, phi_x, frac_offset_y,
frac_offset_x, cond broadcast]`, trained jointly with the head, output added to
the warped LF. This is where residual topology mismatch (5-6 % of samples,
mean |dN| 0.11) is absorbed; the card reports skill stratified by
component-mismatch so the cost of scoping is measured.

**Arms** (all in one process, one SLURM job, seed 0):

| result key | arm | trained | role |
|---|---|---|---|
| `test_hf` | one-sided warp + correction | yes | **SCORED**; the proposal |
| `ref_warp_off` | identical net, `phi` forced 0, + correction | yes | architecture-level warp-off control (B1 part 4, LOCKED); the s6-class baseline on this substrate |
| `ref_const_disp` | `phi` restricted to one global 2-vector per sample (head output mean-pooled) + correction | yes | CONSTANT-DISPLACEMENT-ONLY arm (MANDATORY, B1 part 7 / F12) |
| `ref_lsi` | zero-parameter closed-form LSI filter on the same input path | no (fit on train, 0 trained params) | value-add over the defect-correction class (s6's definition, `tools/defect_correction_learnability.py`) |
| `ref_reg_corrected` | `phi = 0`, no correction | no | registration-corrected reference SIDECAR (B1 part 7 item 3) |
| `ref_frozen_copylf` | `eval/panel_data.py::copylf_prediction`, unedited | no | frozen reference, seam check, skill 1.0 |
| `ref_oracle_phi` | oracle `phi` (test-HF-fitted) + the trained corrector | no (report-only) | the ceiling; `do_not_promote`, never a leaderboard entry |

**Pre-registered hard-stop seams** (assert, don't default):
- S1 `ref_frozen_copylf` nRMSE == `eval/copylf_baselines.json`
  `sharp__cahn_hilliard` = 0.08765999100758841 to <= 1e-9.
- S2 `ref_reg_corrected` skill reproduces B1 F3 variant C **0.4769** within
  +-2 % relative (else the node-aligned input path is misbuilt).
- S3 the vendored `warp_core.py`, run with B1's exact knobs on the
  **misregistered** moving image at C16, reproduces B1's recorded C16 test nRMSE
  to <= 1 % relative (vendoring seam).
- S4 the vendored LSI reproduces s6_local-B1's `skill_LSI` 0.4400-0.4413 within
  +-2 % when fitted on the misregistered path (shared-definition seam).
- S5 zeroing every Fourier coefficient gives `phi == 0` to float round-off, and
  the warp arm's forward at init with `phi` zeroed equals `ref_warp_off`'s.

**Free diagnostics** (sidecar `warp_onesided_sharp__cahn_hilliard.json` under
`S3W2_DIAG_OUT`): endpoint error of predicted vs oracle `phi` (masked and
unmasked), median/p90 `|phi_pred|`, inverse-consistency error `E_IC`
(`PMC3915046`; diagnostic only, never a loss), fraction of the oracle benefit
captured, per-band error ratios on B1's band edges, skill stratified by
LF/HF component mismatch, and the derived-in-repo phase-field interface
displacement statistic (`dphi ~ |grad phi| * delta` re-derived locally -- the
websearch could not source it, so it is NOT cited).

Checkpoint resume: one `<ckpt_dir>/last.pt` holding `{arm_index, epoch, model
state, optimizer state, RNG states, cached oracle-phi fits}`; arms train
sequentially and resume mid-arm. Submit-time job env (not a scoring knob, B1
precedent): `ROUND1_EVAL_RESULTS=<outputs>/s3_warp/B2/eval/results`.
Contract-tier (2-epoch) plumbing screen on `sharp__cahn_hilliard` before the
SLURM submit (numbers never reportable, ADR 0007). No guard legs: the family's
declared support is a 2-D nested periodic dyadic ladder, and `heat_local`,
`fluid`, `sharp__sod_1d` are outside it; the card claims a single-dataset skill,
not a panel geomean, and guard legs are recorded as an owed precondition if the
family is ever promoted.
Estimated wall clock: 3 trained arms x ~300-400 s + oracle fits (~150 s) + LSI
(~30 s) + seams ~= 25-35 min on one H100 (ADR 0005). Suggested `--time 02:00:00`.

### Recipe

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

### Expected outcome

Reference: frozen copy-LF nRMSE 0.08765999100758841 (skill 1.0 by definition).

| key | predicted skill | grounding |
|---|---|---|
| `ref_frozen_copylf` | 1.000 exactly | seam S1 |
| `ref_reg_corrected` | 0.477 +- 0.01 | B1 F3 variant C 0.4769 (seam S2) |
| `ref_lsi` | 0.42-0.46 | B1 F15: 0.4631 -> 0.4402 on the corrected path |
| `ref_warp_off` | 0.40-0.47 | s6_local-B1 trained corrector 0.4686 |
| `ref_const_disp` | 0.40-0.47, within 0.03 of `ref_warp_off` | B1 F11 residual DC <= 0.13 cells; F12's 48.9 % was the grid convention |
| **`test_hf`** | **0.15-0.35** (central 0.25) | 0.44 x (1 - 0.85f) with f = captured share of B1's certified 83.4-85.2 % ceiling |
| `ref_oracle_phi` | 0.06-0.09 | B1 F9 ceiling on the corrected C0 |

Predicted predicted-vs-oracle endpoint error 0.30-0.60 cells against an oracle
median `|phi|` of 0.64-0.74; predicted median `|phi_pred|` 0.3-0.7 cells.

**vs the anchor** (`s3_warp-B1`, a `do_not_promote` diagnostic with no numeric
anchor value): B1's numeric legacy is the ceiling (83.4-85.2 % of the corrected
reference's error removable) and the retrieval bracket (63-99 %, measured on the
misregistered path and therefore uninformative). The card's move vs that anchor
is to replace an HF-fitted upper bound with an LF-only achievable number.

**vs the noise floor** (`state/noise_floor.json`, `sharp__cahn_hilliard`):
Leg A's effect vs the frozen reference is `1 - 0.440 = 0.560 > 0.5533 =
min_claimable_effect` (and 2.9x the certified `spread` 0.19182714769533593);
predicted effect 0.65-0.85, comfortably clear. Leg B's arm-vs-arm threshold
0.20 strictly exceeds `spread` 0.19182714769533593 (and equals >51 % of the
oracle benefit); it does NOT exceed `min_claimable_effect` 0.5533, which is
arithmetically impossible for any arm-vs-arm difference here because
`skill(ref_warp_off) ~ 0.47 < 0.5533` and `skill >= 0` -- declared as Leg B'
(and reported to the mentor), not worked around.

### Expected falsification

**Leg A (claimability, clears `min_claimable_effect` 0.5533)** -- falsified if
the scored `test_hf` skill on `sharp__cahn_hilliard` is `> 0.440` (effect vs the
frozen copy-LF reference `< 0.560`), with seams S1-S5 having passed; predicted
NOT to fire, and passing it attributes nothing on its own because the
zero-parameter LSI already reaches 0.4402.
**Leg B (attribution, the scientific leg; threshold 0.20 > certified `spread`
0.19182714769533593)** -- the one-sided displacement head is declared to add
nothing over registration-fixing or plain correction if
`skill(test_hf) > min(skill(ref_warp_off), skill(ref_const_disp),
skill(ref_lsi)) - 0.20`, equivalently if the head captures `<= 51 %` of B1's
certified 83.4-85.2 % oracle ceiling; if it fires with `ref_oracle_phi`
confirming the ceiling, the stream's finding is that cahn_hilliard's residual
displacement is oracle-visible but NOT LF-predictable, and B1 part 7's close-out
applies.
**Leg B' (parent-directed strict reading, pre-registered UNATTAINABLE)** --
margin `> 0.5533` over both controls; recorded and reported, but its firing is
NOT evidence about the warp because `max margin = skill(control) ~ 0.47 <
0.5533` given `skill >= 0`; its purpose is to document that the anchor-referenced
floor convention is degenerate on copy-LF-referenced datasets.
**Leg C (mechanism honesty, reported, non-falsifying)** -- if Leg B is passed
while the predicted median `|phi_pred|` is `< 0.1` HF cells or the masked
endpoint error vs oracle `phi` exceeds the oracle median `|phi|` (0.64-0.74),
the win is intensity correction mislabelled as warping and must be reported as
such, not as geometric alignment.
**Leg D (scoping cost, reported)** -- skill on the 5-6 % topology-mismatch
subset is reported separately; if it exceeds the matched subset's skill by more
than 2x, the scoping decision (no metamorphosis term) is recorded as the binding
limitation for B3.

### Anchor reference

`"s3_warp-B1"` (batch >= 2 chain, per the task's stream policy). Noted: B1 is a
`do_not_promote` diagnostic that created no `state/anchors/s3_warp.json`, so the
reference is to its measured ceiling and comparator mandates, not to a numeric
panel geomean.

## Immutables self-check (positive evidence, 10/10)

1. **Data read-only.** The family only calls
   `eval/panel_data.py::load_split('sharp__cahn_hilliard', 'train'|'test')`
   (verified to return `field_by_fid {1: 64^2, 2: 128^2, 3: 256^2}`, 400/100
   samples, `cond_dim 19`) and reads `field_by_fid[2]` as the raw LF -- the
   real coarse solve at its native grid, never a downsample of HF, never
   regenerated, no extra HF; `N_hf = 400` train / 100 test unchanged. Nothing is
   written under `benchmark_42/**` or `factory_root/data/**`
   (`S3W2_DIAG_OUT` points into `mffp_autoresearch_outputs/`).
2. **Panel + guard set fixed.** The card scores a SUBSET (one panel dataset,
   `sharp__cahn_hilliard`) via `score_panel.py --datasets sharp__cahn_hilliard`,
   which is the documented comma-list path (`score_panel.main`, lines 243-248);
   it adds no dataset and removes none from `project.yaml`.
3. **Eval layer untouched.** Nothing in the card requires an edit to
   `round1/eval/`, `project.yaml`, `program.md`, ADRs, or subagent prompts: the
   family is invoked BY the unmodified `score_panel.py`, imports
   `eval/nrmse.py` and `eval/panel_data.py` read-only, and its comparators live
   in `ref_*` keys precisely so `_extract_test_metric`'s existing `test*`
   selection rule needs no change (verified by reading lines 121-165).
4. **One nRMSE definition.** Every reported number is produced by importing
   `eval/nrmse.py`; the sidecar records `nrmse_def_hash`
   (`d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`, the hash
   carried by s3_warp-B1 and s6_local-B1). The two-term training loss is a
   TRAINING loss, which section 5's "What CAN be changed" explicitly permits
   ("training loss is free; the SCORED metric is not").
5. **Contract CLI fixed.** `smoke_eval.py` exposes exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; every knob
   is an `S3W2_*` environment variable and all 23 are listed in the recipe
   `env` block above, so they enter `score_panel.code_hash` (lines 51-73).
6. **Seeds and tier epochs fixed.** `seeds: [0]` and `epochs: 200` (smoke tier,
   `project.yaml tiers.smoke_epochs`, ADR 0004 strict single seed); the only
   other run is the mandated 2-epoch contract-tier plumbing screen whose numbers
   are explicitly non-reportable.
7. **Guarded factory surfaces untouched.** The family lives in the worktree at
   `models_r1/s3_warp_onesided`; the vendored modules are COPIES into that dir
   (sources: the B1 worktree's own `models_r1/`, and `round1/tools/`, neither of
   which is in the guarded list `factory_root/{eval,baselines,references,scripts,
   data}/`, `factory.md`, `mf_field/akash/**`). No factory path is read or
   written except through `panel_data.load_split`'s read-only adapter import.
8. **Checkpoint resume implementable.** All three trained arms are sequential in
   one process; `last.pt` stores `{arm_index, epoch, model state_dict, optimizer
   state, RNG states, cached oracle-phi tensors}` and is written every epoch, so
   a preemption mid-arm resumes at that arm's epoch and does not refit the
   oracle. Nothing in the design is stateful outside that dict.
9. **Threshold vs the noise floor (numbers quoted).**
   `state/noise_floor.json sharp__cahn_hilliard`: `spread =
   0.19182714769533593`, `min_claimable_effect = 0.5533465853654416`. Leg A's
   threshold implies an effect of `1 - 0.440 = 0.560 > 0.5533` (and 2.92x
   `spread`) -> clears the floor on the only dataset the card cites. Leg B's
   threshold `0.20 > 0.19182714769533593` clears the certified `spread` but NOT
   `min_claimable_effect`; that is arithmetically impossible for an arm-vs-arm
   difference here (`skill(ref_warp_off) ~ 0.4686` measured by s6_local-B1, and
   `skill >= 0`, so `max margin ~ 0.47 < 0.5533`), so it is pre-registered as
   Leg B' with the proof and reported to the mentor -- the same "declared, not
   worked around" treatment B1 part 4 gave the identical structural property.
   No other dataset is cited.
10. **Not a pre-falsified lever.** Nearest of the three is **LF low-mode
    freezing** (`mf_fno_spectral`, "worst on sharp, catastrophic on
    lid-cavity"). Difference: that lever FREEZES the LF's low spectral modes in
    the prediction's value space; this card leaves every LF value free and
    band-limits the **displacement field** instead (a coordinate-space object,
    Fourier-Net `arXiv:2211.16342`), which cannot pin any output mode. The WNO
    backbone swap (no backbone change here -- the correction stage is a
    ConvNeXt-class local net, s6's measured class) and the diffusion prior (no
    generative prior anywhere) are unrelated.

## Status

- Slot covered (one `model` card, 4 comparator arms + 3 reference sidecars,
  scoped to `sharp__cahn_hilliard`).
- Not skipped.
- Reopen candidates resolved: none exist for this stream
  (`s3_warp-B1.reopen_candidate = false`, status `complete`).
- Immutables self-check: **pass (10/10)**, with item 9's Leg B' impossibility
  declared explicitly rather than concealed; no revision pass needed.
