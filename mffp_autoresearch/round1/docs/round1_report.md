# MFFP Autoresearch Round 1 — Final Report

Author: round-1 orchestrator. Date: 2026-07-31.
Sources: experiment cards (`experiment_cards/*/batch_*/B*.json`), decision log
(`state/orchestrator_flow.md`), mentor notes (`docs/operator_notes/`), ADRs (`docs/adr/`).
All numbers are seed-0 point estimates unless marked confirmed (ADR 0004: strict 1-seed
during the round; top-3 get seeds 1–2 at round end, operator-gated).

## 1. Executive summary

Both round success criteria are met, and the round's largest contribution is not a model
but a set of benchmark-integrity findings that change how every skill number in this
program should be read.

- **Criterion 1 (ifc_poisson)**: best claimable skill **0.6087** (s1-B3, `self_only__none`
  arm; F1/F2 confirmed at 1.07× the certified floor). Fragility note: the slate arm scores
  0.1066 at `f_src=1` but 0.0219 at `f_src=0` — the seed-confirm protocol carries this.
- **Criterion 2 (sharp panel)**: best claimable panel geomean skill **0.1233**
  (s4-B3 `dc_cleaned`; 4/5 sharp datasets < 1 already achieved by the s6 DC lineage at
  0.1876–0.1926, which dc_cleaned supersedes by −34.3%).
- **Headline mechanism finding**: the round-best gain is entirely a *boundary-condition
  matched* spectral cleaning stage; the routing and trust-head machinery added exactly
  zero on the panel, for a structural reason (§4, s4).

## 2. Final leaderboard (claimable, seed-0, pending 3-seed confirm)

| Rank | Model / arm | Panel geomean skill | Stream | Note |
|---|---|---|---|---|
| 1 | `dc_cleaned` (BC-matched spectral clean + local corrector) | **0.1233** | s4-B3 | router/head contribute 0.000000; gain is D3 alone |
| 2 | `trust_head` / `circ_repair` (DC lineage) | 0.1876–0.1926 | s6-B2 | previous best; 4/5 sharp < 1 |
| 3 | `self_only__none` (ifc_poisson slate) | 0.6087 (ifc_poisson) | s1-B3 | criterion-1 model; f_src fragility protocol note |

Proposed top-3 seed-confirm slate (awaiting operator go, `submit_seeds_2_3.sh`, smoke
tier): the three rows above. Helmholtz remains report-only (certified floor 9.695; see §5,
zero-predictor finding).

## 3. Stream closures (one paragraph each)

- **s1_poisson (B4 complete)** — Criterion 1 met by B3's `self_only__none`; B4 confirmed
  the slate arm and exposed the `f_src` fragility (0.1066 ↔ 0.0219), now a protocol note
  on the seed-confirm slate.
- **s2_beyond_copy (CLOSED)** — Per-sample residual normalization: repairs collapsed-effN
  datasets and poisons healthy ones; on helmholtz, A1 was the first arm to beat the
  node-aligned free fix (0.669× on 95/100 samples). Produced the unified normalization
  eligibility rule (§6).
- **s3_warp (CLOSED)** — The warp premise is absent by two orders of magnitude on this
  benchmark; the residual target is an aperture-problem gauge. Closed-form registration
  fix derived (B1): the (r−1)/2 half-cell defect (§5).
- **s4_hybrid_routing (CLOSED)** — Round-best 0.1233. Mechanism complete: the cleaning
  stage's decider is boundary-condition match (two-sided causal proof: mirror-extension
  refit recovers −38.9% on heat_local, costs +1840%/+7167% on periodic datasets; the
  damage on zero-padding datasets is a one-pixel boundary ring carrying 49% of error
  energy on 3% of area). The router null is structural: cleaning *nests* the correction
  library, DC dominates 8/8, routing headroom collapses +6.02% → 0.000%. The
  pre-registered rho routing rule reproduced its source lineage to the decimal yet was
  obsolete against the cleaned lineage — static routing rules are lineage-bound.
  (D3 caveat, verbatim from review: "the D3 contrast is mildly asymmetric — dc_cleaned
  consumes val_idx twice, dc_raw once.")
- **s5_tuning (CLOSED)** — Stage dissociation established; the scaler axis fully mapped
  (revin_lf = two scalers: exact at LF-pretrain, 3.1% proxy at HF); no claimable B4.
- **s6_local (CLOSED)** — DC lineage delivered criterion 2's first pass (0.1876–0.1926).
  Its B2 routing rule (trained corrector wins iff 1−rho_LSI(val) ≥ 0.15, decidable
  pre-training) stands **qualified as lineage-bound** by s4-B3: licensed on the raw
  library (+6.0% headroom), obsolete on the cleaned library (headroom exactly 0).
- **s7_loss (CLOSED)** — λ>1 sign pathology plus tail gate; band finding (c) "both
  ingredients contribute"; final rule is two-gate.

## 4. What actually worked (model-side takeaways)

1. **BC-matched spectral cleaning before a local corrector** is the single biggest lever
   found (−36% panel geomean). Eligibility is decidable *before training*: match the
   cleaning stage's implied boundary conditions to the dataset's (proxy: 1−rho; audit
   tool: `tools/spectral_prestage_bc_audit.py`, training-free).
2. **Routing is only worth building when the library is not nested.** Audit first with
   `tools/library_dominance_audit.py`; if one branch weakly dominates, the router's
   ceiling is zero by construction.
3. **Per-sample normalization** helps only where the unified eligibility rule (§6)
   licenses it; spread is not the decider.
4. ~20 reusable probe tools were promoted to `tools/` with index entries.

## 5. Benchmark-integrity findings (for the mentor — the round's most important output)

1. **Registration defect**: the LF→HF interpolation carries a (r−1)/2 half-cell shift;
   closed form derived (s3-B1). Copy-LF skill denominators are inflated 2.0–8.6×, so most
   published-style "skill" here overstates model value. Sharp-panel "wins" were ~96–100%
   re-learned registration (s2-B2).
2. **Wrap-seam defect** in the periodic reference construction (fix list).
3. **Helmholtz zero-predictor**: the zero field beats the round champion (substituting it
   improves the illustrative geomean 7.10 → 5.24); the dataset needs a zero-floor column
   and should stay report-only.
4. **Leg-B′ unclearable floors**: copy-LF-referenced floors > 1.0 exist that a perfect
   model cannot clear — floor semantics, not model failure.
5. **0.018 stretch-bar misattribution** (paper-bar provenance; ADR 0002 keeps bars frozen,
   the note records the caveat).
6. **Drift-class rule**: when n_eff/N < 1%, only in-job paired controls are controls.

Recommended between-rounds fixes (in order): registration + wrap-seam reference fixes →
re-certify floors and seed spreads → per-sample target normalization option → pfc
redesign → helmholtz zero-floor column → re-run `tools/warp_premise_audit.py --datasets
PANEL` against the fixed reference → corrector-input wrap-seam fix → permute-queries
chunking fix.

## 6. Methodological rules established this round

- **Unified normalization eligibility rule** (checks 0–6: stage; need effN < ~0.05;
  signal above numerical noise floor; metric alignment; placement-centering
  F = median(sd_i/s_i); legality-fidelity; N_hf coverage). Spread is not the decider.
- **BC-match rule** for spectral pre-stages (new, s4-B3): eligibility = boundary-condition
  match, decidable training-free.
- **Routing-license rule** (new, s4-B3): audit library dominance before building a router.
- **Lineage-bound caveat**: any static routing/eligibility rule must name the library
  lineage it was fit on.
- **Two-gate loss rule** (s7); **drift-class rule** (§5.6); **claim protocol** for
  concurrent orchestrator instances (process, §7).
- **Nested-ladder degeneracy** (novel remark, we could not find this reported): with
  aligned/nested fidelity ladders, all-pairs multi-fidelity training degenerates to
  replication of the top rung.

## 7. Process findings (harness)

- **H100 nondeterminism envelope ~1.9e-4 rel**: bitwise gates are only decidable on CPU;
  GPU-tier identity gates need two-tier tolerances keyed to checkpoint sha (s4-B3 pattern:
  card-literal 1e-6 where weights are shared, certified envelope where training is
  independent).
- **Two concurrent orchestrator instances** arose from restart replays; the claim protocol
  (stage-file tags, pre-sbatch squeue+card checks, verify-don't-clobber) contained every
  consequence. Restart replays remain the dominant infra hazard.
- **Reviewers never submit SLURM**; screens are non-reportable and gate main runs
  (ADR 0007); automatic screen gates must be checked row-by-row, not violations-only
  (reviewer S1 finding, validated the same day by the V5 incident).

## 8. End-of-round protocol (operator-gated, in order)

1. Freeze the provisional leaderboard (§2) — done in this report.
2. On Eloise's go: seeds 1–2 for the top-3 slate at smoke tier via each card's
   `submit_seeds_2_3.sh`; re-issue the leaderboard with 3-seed means and the certified
   seed spreads.
3. Human-approved 2500-epoch full runs for survivors.
4. Between-rounds fix list (§5) before any round-2 numbers are generated.
5. **Round 2** (condition-vector → HF; spec
   `docs/superpowers/specs/2026-07-30-mffp-autoresearch-round2-design.md`, commit
   12a4c29) — designed and approved; **launch explicitly gated on Eloise**.
