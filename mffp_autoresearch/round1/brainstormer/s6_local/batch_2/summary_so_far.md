# Summary so far — Stream `s6_local`, Batch 2

Packed 2026-07-29 from files read (never recalled): `websearches/s6_local/batch_2/report.md`,
`experiment_cards/s6_local/batch_1/B1.json` (parts 1-7), `experiment_cards/s1_poisson/batch_2/B2.json`,
`experiment_cards/s2_beyond_copy/batch_2/B2.json`, `state/noise_floor.json`,
`state/anchors/{s4_hybrid_routing,s5_tuning}.json`, `program.md`, `docs/adr/000{4,5,7,9}*`,
`tools/defect_correction_learnability.py`, `worktrees/s6_local/B1/models_r1/s6_local_lf_corrector/*`,
`worktrees/s6_local/B1/scratchpad/turn{2,3}_*.json`, plus two read-only probes I ran myself
(scratchpad `periodicity_probe.py`, `residual_boundary_probe.py`; numbers in section 6).

## 1. Websearch findings + prior-art verdict

Batch-2 websearch (5/5 iterations, 15 searches, 9 successful fetches) verdicts, verbatim fragments:

- **(i)** closed-form data-estimated LSI defect filter -> **`preempted-but-MF-composition-open (cite)`
  — preempted as a *method*, open as a *reported baseline***: "No fetched source **solves** the
  coarse->fine defect operator in closed form from paired nested solves **and scores it beside trained
  neural operators on an MF field benchmark**. Claim **zero method novelty**; the contribution is the
  *measured floor* ... A card that says 'we introduce an LSI defect filter' dies on sight."
  Licence to report it: DeepFDM (https://arxiv.org/html/2507.21269v1, fetched); explicit engine
  negative on any paper advocating linear baselines in NO benchmarks.
- **(ii)** circular padding -> **`preempted (cite)` — hygiene, not a contribution**. SineNet ICLR 2024
  Table 3 (fetched): "zero 1.50%/4.19% vs circular 1.02%/1.78%", authors' own words "a simple yet
  crucial component". "**Nothing about the fix.** Only reportable: B1's *measurement* that zero padding
  held **45-81%** of a defect corrector's remaining squared error in a 12-cell band ... plus the
  post-repair delta. Write it as 'known bug, quantified cost'."
- **(iii)** per-sample trust head -> **`preempted-but-MF-composition-open (cite)`**, the batch's best
  open surface: "A **data-driven, physics-free, per-SAMPLE scalar, fitted out-of-fold, deciding
  whether a FIELD-VALUED defect corrector is applied at all, with the scored copy-LF field as the exact
  fallback** appears in no fetched source." MAST = scalar GP, geometric weight, "no involvement with ...
  PDE solution fields"; SelectiveNet trains the selector in-sample; ANCHOR is "inherently
  physics-informed, being computed from the PDE residual" => ADR-0009-disqualified.
- **(iv)** held-out-fold gate -> **`preempted (cite)`** (Wolpert 1992 via https://arxiv.org/pdf/1106.1684);
  "pre-register the ORACLE ceiling ... <=4.1%, **negative on cahn_hilliard** (+17%)".
- **(v)** owed 200-epoch `pointwise_ctrl` -> "**not a novelty question** — a control arm".
- Bonus: Charalampopoulos et al. (fetched abs) states B1's M4 stationarity condition independently —
  chaotic divergence "makes datasets from different resolutions incompatible"; MFFP's nested ladder
  supplies the compatible pair for free.
- Framing guard the report imposes: "**every arm in this card must report `skill_LSI` beside its own
  number**, or the geomean is uninterpretable."

## 2. program.md section 12.6 conventions (verbatim)

> ### 12.6 `s6_local` (lever) — ADDED STREAM, see ADR 0011
> - **Question**: does adding a local representation (CNN/ConvNeXt branch, local kernels) to the FNO fix sharp-2D fusion (hypothesis H2)?
> - **Anchor**: champion's certified panel geomean (batch 0).
> - **Motivating result**: s5-B1 (H1 test): modes_cap 12->32 improved geomean 0.507 < 0.884 floor (provisional-single-seed) — spectral capacity alone is not the claimable lever.
> - **Priors to interrogate, not assume**: the mentor's FNO->CNN two-stage hybrid attempt performed poorly (docs/reports/MF_FNO_CNN_Hybrid_Report.md — batch-1 websearcher MUST read and the brainstormer MUST state the failure mode); `convnext_unet_film` is rank-2 overall in the zoo but loses to `mf_fno_transfer_film` on the panel (bench check 2026-07-29) — capacity is not the question, composition is.
> - ADR 0009 applies (no physics at test time). ADR 0007 applies at the brainstormer (propose 3-5 hybrid compositions, screen at contract tier).
> - Contract CLI unchanged; hybrids live inside the family dir.

Anchor value (batch-0 certified, `state/anchors/s5_tuning.json` == `s4_hybrid_routing.json`):
champion panel geomean **6.703016**, ci95 [6.218536, 7.102240] => geomean floor **0.8837**.
Batch->=2 policy: `anchor_reference = "s6_local-B1"` (this card re-targets B1's 0.234572).

## 3. Within-stream prior cards

`s6_local-B1` (`complete`, "mf_composition / trust-gated LOCAL corrector on the real LF field",
`anchor_reference: null`, `reopen_candidate: false`), family `models_r1/s6_local_lf_corrector` @
build commit `3abc0e3`, 200 ep seed 0 job 66001535 (17.95 min, 6 datasets), screen 66001190,
guard 66005834.

Part 5 (provisional-single-seed): panel geomean **0.234572**; per-dataset skill / nRMSE —
helmholtz 1.000000 / 0.3294501 (gate alpha=0, the prediction *is* copy-LF, report-only), pfc
0.030017 / 0.00134416, allen_cahn 0.080540 / 0.00130074, fisher_kpp 0.095142 / 0.00595834,
cahn_hilliard 0.468582 / 0.04107603, ifc_poisson 1.545326 / 0.05563172 (champion fallback, no claim).
Layer-1 NOT falsified; layer-2 STRONG supported 4/4. Identity path bit-equal to
`eval/copylf_baselines.json` on all five LF-bearing datasets.

Part 6 findings that set batch 2: **F6** a zero-parameter closed-form transfer function `T(k)` beats
the trained 72k ConvNeXt on 3 of 4 winners (pfc 2.19x, allen_cahn 1.56x, cahn_hilliard 1.07x) and
loses only on fisher_kpp (0.77x); **F10** 80.9% / 69.8% / 45.3% of the trained arm's remaining
squared error sits in a 12-cell boundary band covering 34% / 18% / 18% of pixels; **F1/F2/F4/F5** the
pixel gate is worth <=0.63%, its ORACLE <=4.1% and -17% on cahn_hilliard, and stage 2 trains it on
the same `fit_idx` as stage 1 so `g->1` is the correct answer; **F3** the available trust axis is
per-SAMPLE (oracle: pfc -22.8%, helmholtz 0.1623 vs copy-LF 0.3295); **F14** held-out `rho` of an
LF->R fit orders the panel with Spearman 1.000 and reproduces the helmholtz shut-off training-free;
**F15** the optimal operator is compact (radius_50pct 1.4-3.0 cells, 94-99% of energy within 12
cells) — H2's locality content vindicated, its *neural* content not.
Part 7 `next_direction` prescribes: (1) circular padding, (2) LSI control arm, (3) the true
per-pixel-gate test with the <=4.1% ceiling pre-registered, (4) per-sample trust head, (5) the owed
200-epoch `pointwise_ctrl`, and "**Do NOT spend a batch on capacity, depth, receptive field or
modes**". Promoted tools: `tools/defect_correction_learnability.py`, `tools/trust_gate_headroom.py`.

## 4. Cross-stream cards

- `s2_beyond_copy-B2` (`drafted`, building): owns the **trained** LF-residual FNO control
  (`lf_resid_fno`: champion backbone + LF_up channel + zero-init head) and **retrieval** floors
  (`retr_blockmean16_k5` etc., emitted as `ref_*` splits only, never the scored split). Boundary for
  this card: my floor arm is a **closed-form single transfer function `T(k)`, zero trained parameters,
  no gradient steps, no retrieval**, fitted by least squares on the family's own fit split — a
  different construction from both of s2-B2's objects. No duplication; the numbers stay comparable
  because both flow through `eval/nrmse.py` (same `nrmse_def_hash` d3d0ade9...).
- `s1_poisson-B2` (`drafted`): the vendoring precedent this card copies — `git checkout <build_commit>
  -- models_r1/<family>` into a fresh worktree, sha256-16 pins verified before any edit, and a
  reproduction validity gate at 10%.
- `s4_hybrid_routing-B1`: the identical held-out alpha machinery chose alpha=0 on all six datasets on a
  champion-generated base (B1 part 7 item 4) — the base, not the gate, decides.
- `s3_warp`: cahn_hilliard is handed to that stream (B1 M5); this card does not attempt CH's low band.

## 5. Reopen candidates

**None.** `experiment_cards/s6_local/batch_1/B1.json` has `reopen_candidate: false`,
`status: complete`, `skipped_reason: null`; no other s6 card exists.

## 6. What is UNKNOWN

1. **How much of the trained arm's remaining error is the padding handicap vs the target?** F10
   measured the *error* concentration but not whether the *target* is boundary-concentrated. I
   measured it (read-only probe, 400 train samples, `R = Y_hf - LF_up`): the 12-cell band's squared
   energy **density ratio vs interior is 1.043 (pfc) / 1.045 (allen_cahn) / 1.041 (fisher_kpp) /
   1.024 (cahn_hilliard)**, i.e. the achievable target is essentially uniform. So the 45-81% error
   concentration is a *model* handicap, not a hard region — which turns the padding repair from a
   guess into energy-share arithmetic (iteration_1 section 3.2).
2. **Is circular padding even correct on these grids?** Unknown before this batch; the literature
   framing assumes it. My wrap-continuity probe (HF train fields; RMS jump across the seam / RMS jump
   between interior neighbours): pfc **1.015 / 0.991**, allen_cahn **0.991 / 1.021**, fisher_kpp
   **0.999 / 0.987**, cahn_hilliard **1.000 / 1.000**, helmholtz **0.348 / 0.859** — versus guard
   heat_local **10.6 / 16.5** and fluid **2.56 / 1.21**. The four sharp datasets sit on proper
   periodic FFT grids; the guard set does not. A data-driven criterion (ratio <= 1.25 on both axes)
   separates them without assuming any physics (ADR 0009-safe).
3. **A new, unremarked property of the scored baseline**: `eval/panel_data.py::copylf_prediction`
   interpolates with `zoom(..., mode="nearest")`, so **copy-LF itself carries a wrap seam**: LF_up wrap
   ratios are **4.12 / 3.93 (pfc), 3.93 / 4.18 (allen_cahn), 3.99 / 3.89 (fisher_kpp), 4.00 / 4.00
   (cahn_hilliard)** while the HF truth sits at ~1.00. The corrector's job therefore *includes*
   repairing a seam it cannot see across under zero padding. The eval layer is immutable (section 5.3)
   — the model must fix it, and this is a mechanism behind F10. Unknown: how much of the boundary
   excess is the seam vs the missing context.
4. **Does anything neural survive once the handicaps are removed?** B1's own open question, unresolved:
   post-repair, does the trained arm beat `T(k)` on more than one dataset? The arithmetic in
   iteration_1 predicts fisher_kpp yes (+37%), allen_cahn marginal (+5%), pfc and cahn_hilliard no.
5. **Is per-sample trust *learnable* out-of-fold (not merely oracle-available)?** F3 gives only the
   oracle. Unknown which physics-free features carry the signal, and whether per-sample gating
   *breaks* the exact copy-LF no-harm floor on the one dataset where the corrector diverges out of
   sample (helmholtz `rho_val` -0.22).
6. **Is the per-pixel gate question worth a training arm?** Unknown until the ceilings meet the floor
   rule: ORACLE per-pixel <=4.1% (pfc), 1.2%, 0.6%, -17% (CH) — every one below the 10% relative
   `min_claimable_effect` — and F2 already ran the *achievable* val-fitted version (worse than `g==1`
   on 3 of 4). The honest inference (iteration_1 section 3.5) is that the arm cannot produce a
   claimable effect and should be replaced by a free out-of-fold sidecar measurement.
7. **What floor convention applies to a model at skill ~0.03?** `min_claimable_effect` is
   `max(seed spread, 10% of champion mean skill)`; at B2's skill levels absolute skill units are
   meaningless. B1's accepted precedent (part 5 layer 2) rescales to relative terms. Certified
   relative floors: pfc 10.00% (pure seed spread 0.718%), allen_cahn 10.00% (0.087%), fisher_kpp
   10.00% (2.197%), cahn_hilliard 10.00% (3.467%), helmholtz 70.16%, ifc_poisson 15.32%; geomean
   0.8837 / 6.703016 = **13.18%**.
8. **Does the zero-parameter arm beat B1's trained geomean?** Composing F6's numbers with the alpha=0
   helmholtz shut-off and the ifc_poisson fallback gives a predicted LSI panel geomean of **0.1973**,
   15.9% below B1's 0.234572 — above the 13.18% geomean floor. Unknown until scored through
   `score_panel.py`; if it holds, the round's best panel number has zero trained parameters.
