# MFFP Autoresearch Round 3 — Program

> Universal guideline for every agent in Round 3.
> Round 3 inherits Round 2's pipeline, card format, agents, cron orchestration, tools library, and eval layer unless this document says otherwise.
> Round-2 program: `../round2/program.md` (its §2 score system, §12 methodological rules, and stream conventions apply verbatim except where amended below).
> Launch ADR: `docs/adr/0001-launch-panel-composition.md` (operator go, Eloise, 2026-08-05; mentor option-A ratification).
> Process rules: `PROGRAM_NOTE.md` MUSTs 1–6 are binding in this round.

## 1. Goal and regime

The regime is unchanged from round 2: LF fields are available at train time only; at test a model sees the condition vector alone.
What changed is the panel: every scored dataset is now completeness-certified — the HF field is exactly reconstructible from the stored condition vector (option A, band-limited parametric ICs; ADR D1).
Round 2's headline finding was that its panel was scalar-deep for condition-only models: beyond a closed-form condition→level law, the condition vector carried no usable field-level information, because the ICs were random fields never exported to the vector.
That excuse is gone.
The IC coefficients ARE in the condition vector now.
Round 3 therefore asks:

1. **Field reachability.** Can any trained condition→HF model convert the now-complete condition vector into field-level structure — beating both the best training-free floor and the condition→level closed-form law by a certified margin?
2. **Value of LF at train.** On an honest panel, how much does LF-at-train still help (coverage, amplitude, or newly reachable mechanisms), measured with matched with/without arms?

Reconstructing the IC from the condition vector inside a model (an internal "option C") is explicitly in scope: the condition is complete, so any deterministic feature map of it is fair game.
Calling a numerical PDE solver at test time remains banned (round-2 rule, unchanged).

## 2. Score system

Round-2 §2 applies: one nRMSE definition (`../round2/eval/nrmse.py`), skill = model nRMSE / corrected copy-LF reference, panel geomean.
Amendments:

- **Scored panel (6 datasets, ADR D4 as amended by A1):** `sharp__phase_field_crystal_2d`, `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`, `ifc_poisson`, `ifc_heat` (both on repaired nested ladders; ifc_heat paper bar 0.074, ifc_poisson 0.036).
- `ext__helmholtz_2d` is report-only (ADR D2); every helmholtz mention carries the closed-form-triviality flag.
- Guard set unchanged: `heat_local`, `fluid`, `sharp__sod_1d`.
- Per-dataset cells are produced by the round-2 eval layer (`../round2/eval/score_panel.py`, unchanged bytes; `panel_data.py` amended once under ratified ADR r3-0005, def hashes re-stamped and self-invalidating); the panel aggregation is round-3-side (`tools/make_round3_anchors.py` conventions).
- **Launch anchors** live in `state/anchors/launch_anchors.json`: best-floor geomean **38.8368** on the 6-dataset scored panel (lineage: 75.0673 pre-A1 → 38.6300 ifc_heat promotion → 36.3912 ac trim + pfc box swap → 34.4198 pfc report-only, ADR r3-0004 → 38.8368 pfc restored on the spectral rung-1 cell, ADR r3-0005 phase 2).
  All four round-2 anchor cards CERTIFIED 2026-08-10 over the 6-dataset panel; ADR D6 satisfied.
  **Scored panel (ADR r3-0005, executed 2026-08-10): pfc IS scored** — cell L1(32²)→L3(128²) with the exact spectral (FFT zero-pad) reference 0.012358 (`docs/adr/0005-pfc-spectral-rung-repair.md`). The 5-dataset interval (2026-08-07 → 2026-08-10, ADR r3-0004) is history: batch-1/2 verdicts registered in that era carry their era's panel and are not silently comparable on pfc across the change (per-entry `_copylf_def_hash` enforces this).
- Standing caveats on every claim: pfc/fisher_kpp weak fidelity gap (denominator caveat), ifc_poisson affine structure, no cross-round comparison without the honest-denominator flag.
- **Affine-floor rule (degeneracy audit 2026-08-05, `state/anchors/launch_anchors.json`):** ifc_poisson's condition→HF map is EXACTLY affine on the repaired rows (oracle-affine residual 5.4e-16), and on ifc_heat a 6-dof affine fit on the 5 HF train rows already beats the paper bar (nRMSE 0.0709, skill 0.96). Every card reporting an ifc number therefore reports the fitted `affine_on_hf_train` floor next to it (ifc_poisson skill 1.59, ifc_heat 0.96); an ifc claim that does not beat this floor has learned nothing beyond linearity, and skill < 1 on ifc_heat is not by itself a strong claim.

## 3. Success criteria

1. At least one trained model beats the launch best-floor anchor on the panel geomean AND exceeds the condition→level closed-form law by ≥ 1 certified mce on ≥ 2 scored datasets (field reachability, answerable in either direction — a certified null is a result).
2. A certified matched-arm measurement of LF-at-train value on ≥ 3 scored datasets under the repaired denominators.

`state/anchors_repaired/noise_floor.json` is PROVISIONAL; r3s4 re-certifies mce on the repaired panel before any criterion is adjudicated (round-1 §4.5 discipline).

## 4. Streams

| stream | class | question |
|---|---|---|
| `r3s1_factorised` | gap | Does the recorded two-stage cross-coefficient factorised closed-form head (r2s1-B3 part 7, pre-measured 18.6787 on the OLD panel — number void, direction live) beat the shipped closed-form law on the honest panel? |
| `r3s2_field_reach` | gap | Can any architecture (including internal IC reconstruction from the complete condition vector) recover field-level structure the scalar-deep law cannot — and if not, is the negative certifiable? |
| `r3s3_lf_value` | lever | What is LF-at-train worth on the honest panel (coverage/amplitude mechanisms, ch identifiability-vs-trainability), with matched with/without arms at matched procedure? |
| `r3s4_audit` | diag | Certify the repaired-panel mce and floors; run the training-free instrument audits (including the repaired-ifc audit); own the close-evidence audits of PROGRAM_NOTE MUST #3. |

Per-stream flow, card format, batch budget, retry caps: round-2 conventions (project.yaml `caps`), with the PROGRAM_NOTE amendments:

- A stream closes only on close-evidence (MUST #3): its terminal card must survive an independent instrument audit, or the operator closes it explicitly.
- Seed confirms for claimable cards happen in-round as a close precondition (MUST #4), not as a post-round follow-up.
- The panel is mutable in-round only under an explicit ADR (MUST #5).
- Any defect discovery pauses the round: set `preflight/hold.py` HOLD, stop launches, report blast radius, wait for operator adjudication (MUST #2).
- Pollers/crons die with the round (MUST #6).

## 5. Immutables

Round-2 §12 methodological rules apply verbatim (registration-of-lifts, zero-information nulls, matched-procedure arm comparisons, target-scaler pre-flight, "unidentifiable" phrasing rule, zero-information-null publication rule).
Guarded surfaces unchanged: never edit `mf_field/factory_mffp/{data,baselines,eval,references,scripts}`, `factory.md`, or generator surfaces (`mf_field_eloise_data`, `benchmark_42` generation code) — the ADR-sanctioned data swaps of 2026-08-03/05 are complete and no further generator-side mutation is in scope for this round.
Model/experiment code lives in each experiment's worktree under `models_r2/`-style family dirs (round-2 contract, `../round2/program.md` §9).
