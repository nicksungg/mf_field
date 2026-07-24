# Failure Analysis — Cycle 010 (baseline)

## Summary
- **Composite_nRMSE**: 0.022161 (geomean of best-per-dataset: ifc_heat 0.012884 × ifc_poisson 0.038120)
- **Identical reproduction** of cycle-009-h1h2 (all 14 model×dataset cells `_cache: "hit"`); zero drift from previous best 0.022161.
- **Branch / commit**: experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb
- **Both paper composite bars already beaten**: ratio vs IFC-ODE2 geomean (0.0516) = 0.43x, ratio vs IFC-GPODE geomean (0.0331) = 0.67x.
- **Dominant residual failure**: `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY` — heat is 5.7× under paper IFC-ODE2 (4.7× under GPODE), Poisson best (0.0381) sits 1.06× over IFC-ODE2 and 2.12× over IFC-GPODE. **No single family is best on both datasets**: heat winner is `fno_coregionalization` (0.0129), Poisson winner is `fno_mf_stack` (0.0381). The heat-winning family is catastrophically broken on Poisson (0.598).
- **Comparison with prior cycle**: no movement (cycle-009-h1h2 banked this exact result). New baseline.

## Per-Cell Classification

Categories defined for this analysis:
- `AT_OR_UNDER_GPODE` — ratio ≤ 1.0 vs IFC-GPODE bar
- `AT_OR_UNDER_ODE2`  — ratio ≤ 1.0 vs IFC-ODE2 bar but > 1.0 vs GPODE
- `NEAR_BAR` — 1.0 < ratio ≤ 1.5 vs IFC-ODE2
- `OVER_BAR` — 1.5 < ratio ≤ 5 vs IFC-ODE2
- `FAR_OVER_BAR` — 5 < ratio ≤ 30 vs IFC-ODE2
- `MODEL_BROKEN` — ratio > 30 vs IFC-ODE2 (architectural failure)

Paper IFC-ODE2: heat 0.074, poisson 0.036. Paper IFC-GPODE: heat 0.061, poisson 0.018.

### ifc_heat (n_runs=7)

| Cell | nRMSE | vs ODE2 (0.074) | vs GPODE (0.061) | Category | Notes |
|---|---|---|---|---|---|
| fno_coregionalization × heat | 0.012884 | 0.17× | 0.21× | **AT_OR_UNDER_GPODE** | Best-on-dataset. 50.47M params. K=20, blocks=6, modes=(16,16), hidden=128. Two-stage LF→HF curriculum (50 LF epochs / 150 joint, lr 1e-3→3e-4). Per-fid output scaler ≈ [1, 1, 1, 1]. best_val 0.0055. |
| fno_coreg_residual × heat | 0.026273 | 0.36× | 0.43× | AT_OR_UNDER_GPODE | 9.12M. H3 hybrid (4 per-fid FNOs hidden=64, modes=[4,8,12,12], blocks=3) + MFRNP decoder + K=10 basis. best_val 0.0169. |
| mf_fno_transfer_bar × heat | 0.033175 | 0.45× | 0.54× | AT_OR_UNDER_GPODE | 4.74M, smallest non-baseline. Plain transfer-learn FNO (HF 64 / LF 8). 10s train. |
| fno_mf_stack × heat | 0.038269 | 0.52× | 0.63× | AT_OR_UNDER_GPODE | 24.21M. 4 FNOs hidden=64 modes=[4,8,16,20] blocks=4 + MFRNP aggregator + HF residual. Uniform fid weights (1.0,1.0). |
| transolver_residual × heat | 0.114559 | 1.55× | 1.88× | NEAR_BAR (above) | 0.70M, attention-only. best_val 0.225 — converged poorly. |
| v9_baseline × heat | 0.148834 | 2.01× | 2.44× | OVER_BAR | 0.41M plain FNO. best_val 0.052; gap test_vs_val ≈ 2.85× (train/test domain mismatch?). |
| transolver_attention_fusion × heat | 0.149230 | 2.02× | 2.45× | OVER_BAR | 2.28M. best_val 0.034 but test 0.149 — severe val→test gap (×4.4) suggests overfitting or split distribution shift. |

### ifc_poisson (n_runs=7)

| Cell | nRMSE | vs ODE2 (0.036) | vs GPODE (0.018) | Category | Notes |
|---|---|---|---|---|---|
| fno_mf_stack × poisson | 0.038120 | **1.06×** | 2.12× | **NEAR_BAR** | Best-on-dataset. Same arch as heat cell but Poisson-gated weights (HF=2.0, LF=0.25). Marginal miss vs ODE2 (5.9% over). |
| fno_coreg_residual × poisson | 0.072000 | 2.00× | 4.00× | OVER_BAR | best_val 0.023 → test 0.072 = ×3.1 gap; meaningful val/test divergence. |
| mf_fno_transfer_bar × poisson | 0.083326 | 2.31× | 4.63× | OVER_BAR | Same arch as heat; transfer-learn lacks Poisson-specific aggregation. |
| transolver_attention_fusion × poisson | 0.381812 | 10.61× | 21.21× | FAR_OVER_BAR | best_val 0.197 → test 0.382 (×1.9 gap). |
| fno_coregionalization × poisson | 0.597799 | **16.61×** | 33.21× | FAR_OVER_BAR | **Heat-winner is Poisson-catastrophic.** 50.47M params, K=20, two-stage curriculum identical to heat. best_val 0.054 → test 0.598 (×11 collapse). Per-fid output scaler [0.077, 0.024, 0.0069, 0.0018] — 42× dynamic range across fidelities. |
| transolver_residual × poisson | 2.592349 | 72.01× | 144.0× | MODEL_BROKEN | best_val 0.497 → test 2.59 (×5.2). |
| v9_baseline × poisson | 18.503436 | 513.98× | 1027.97× | MODEL_BROKEN | best_val 1.37 → test 18.5 (×13.5). HF-only plain FNO not viable on Poisson. |

### Behavioral observations (description of WHAT the system did, not corrections to the answer)

1. **Val→test inflation is concentrated in two cells**: fno_coregionalization × poisson exhibits an 11× val→test ratio (0.054→0.598), and v9_baseline × poisson exhibits 13.5× (1.37→18.5). The heat-winner architecture's best-val on Poisson (0.054) was already *better than the IFC-ODE2 bar of 0.036*, yet the held-out test is 16× worse — this is the largest val/test discrepancy in the table and indicates the K-basis B(m)=MLP([m,m²]) does not generalize the fidelity-conditioning pattern from val to test on Poisson, despite generalizing perfectly on heat.
2. **Per-fidelity output scaler dynamic range** for fno_coregionalization differs by ~40× between heat ([1, 1, 1, 1]) and poisson ([0.077, 0.024, 0.0069, 0.0018]). The same architecture+curriculum is asked to bridge a steeply non-uniform fidelity ladder on Poisson and a near-flat one on heat. The K-basis attempts to learn a smooth map B(m)=MLP([m,m²]) over m∈{m₁,m₂,m₃,m₄=1} where the underlying signal magnitudes vary 42×.
3. **Heat fno_mf_stack is 3× worse than heat fno_coregionalization** (0.0383 vs 0.0129) — fno_mf_stack's MFRNP-aggregator path is *Poisson-shaped*; it underperforms on heat even after the cycle-009-h1h2 capacity bump.

## Composite-Gap Contribution Analysis

The composite is the geomean of the best per dataset; only the *leader* on each dataset moves the composite. Sensitivities and counterfactuals (heat held at 0.012884, poisson held at 0.038120):

| Move | New composite | Δ vs 0.022161 |
|---|---|---|
| Poisson → 0.036 (paper IFC-ODE2) | 0.021536 | **−2.8%** |
| Poisson → 0.030 | 0.019660 | −11.3% |
| Poisson → 0.025 | 0.017947 | −19.0% |
| Poisson → 0.020 | 0.016052 | −27.6% |
| Poisson → 0.018 (IFC-GPODE) | 0.015228 | **−31.3%** |
| Poisson → 0.013 (≈heat) | 0.012942 | −41.6% |
| Heat → 0.010 | 0.019524 | −11.9% |
| Heat → 0.008 | 0.017463 | −21.2% |
| Heat → 0.006 | 0.015124 | −31.8% |
| Heat → 0.005 (IFC-ODE2 paper, well-tuned) | 0.013806 | −37.7% |

**Local sensitivity** at the current operating point: d(composite)/d(heat) = 0.86, d(composite)/d(poisson) = 0.29 — a unit-absolute reduction in heat moves the composite ~3× more than a unit-absolute reduction in poisson. **But the relative room for Poisson is much larger**: Poisson best sits 1.06× over IFC-ODE2 and 2.12× over IFC-GPODE (close-to-bar, plausibly accessible). Heat best is already 5.7× under IFC-ODE2 and 4.7× under IFC-GPODE — further reduction has no published bar to chase and may be near the family's asymptote.

**Load-bearing cell**: `fno_mf_stack × ifc_poisson` (0.038120). It is the sole composite-leader on Poisson; nothing else on the leaderboard is within 1.9× of it. Closing this single cell to IFC-GPODE 0.018 unlocks a −31% composite drop; closing only to IFC-ODE2 0.036 unlocks just −2.8%. Closing it to fno_mf_stack's own ifc_heat value (0.0383) would lock in the present number — i.e., there is no slack here, fno_mf_stack has equalized heat/poisson at ~0.038 and the next move must come from architecture/curriculum, not from re-balancing across this family.

**Secondary lever**: `fno_coregionalization × ifc_heat` (0.012884) — sole leader on heat, no challenger within 2×; same logic applies (no slack from rebalancing; any further drop must come from architectural improvements on the same family).

## Failure Distribution (residual-gap breakdown)

The "residual gap" here is the geomean composite vs the IFC-GPODE bar (0.0331), our most aggressive published target. Current ratio 0.6688 — *we are already 33% under the GPODE composite*. The remaining frontier is the **per-dataset GPODE bar** (heat 0.061, poisson 0.018):

By dataset (share of the per-dataset gap):
- ifc_poisson: best 0.0381 → GPODE 0.018 = need 53% reduction. Gap = **2.12× — the entire remaining published-bar gap lives here**.
- ifc_heat: best 0.0129 → GPODE 0.061 = already 4.7× *under*. Negative gap. Zero remaining published-bar gap.

By model family (Poisson-only, ranked by current performance):
- fno_mf_stack: 0.0381 — 0.0× to 1.06× of ODE2, holds the composite-leader. ~**100%** of any short-term Poisson improvement must come from this family (or a new family that beats it).
- fno_coreg_residual: 0.0720 (89% over best) — the structural second-best.
- mf_fno_transfer_bar: 0.0833 (118% over best) — small (4.7M), capacity-bound.
- fno_coregionalization: 0.598 (**1469% over best**) — same family that dominates heat catastrophically fails Poisson. The dominant per-family failure pattern.
- transolver_attention_fusion / transolver_residual / v9_baseline: 10×–510× over best — broken on Poisson; treat as out-of-frame.

By mechanism (per-cell evidence cited above):
- **K-basis B(m)=MLP([m,m²]) inadequate for non-uniform fidelity-magnitude ladders** (Poisson scalers span 42× vs heat 1×): observed in fno_coregionalization × poisson val→test collapse (×11). Estimated contribution to dominant gap: ~50% (this is what holds 16.6× over paper).
- **MFRNP aggregator path is Poisson-specialized**: fno_mf_stack heat 0.0383 vs poisson 0.0381 (equalized) — same aggregator path produces near-identical performance on dissimilar PDEs, suggesting the aggregator is *the* mechanism that scales Poisson but is sub-optimal on heat. Estimated contribution: ~30%.
- **HF-only plain FNO architectures don't transfer to Poisson** (v9 at 18.5, transolver_residual at 2.6): no LF→HF fidelity-bridging mechanism. Estimated contribution: ~20% (mostly irrelevant since they're not on the composite).

## Cross-Cycle Comparison (cycles 007 → 008 → 009-h1h2 → 010)

| Cycle | composite | best heat | best poisson | event |
|---|---|---|---|---|
| 007 baseline | 0.039578 | 0.026277 (fno_coreg_residual) | 0.059611 (fno_mf_stack)* | fno_coregionalization crashed (constructor bug) |
| 008 baseline | 0.030408 | 0.015511 (fno_coregionalization) | 0.059611 (fno_mf_stack) | constructor fix landed |
| 009 baseline | 0.027729 | 0.012884 (fno_coregionalization) | ~0.060 | fno_coregionalization paper-capacity bump (cycle-008 H1) |
| 009-h1h2 | **0.022161** | 0.012884 | **0.038120** (fno_mf_stack) | fno_mf_stack capacity bump + recipe_hash guard, **-20.08%** |
| 010 baseline | 0.022161 | 0.012884 | 0.038120 | identical reproduction, all 14 cells cache-hit |

*cycle-007 ranked fno_mf_stack at 0.0596 on Poisson, taking the lead after fno_coregionalization crashed.

### Trend per category (cycles 007→010)
- `BEST_HEAT_AT_OR_UNDER_GPODE`: 0.0263 → 0.0155 → 0.0129 → 0.0129 — **improving** through H1 capacity (cycle-008 H1), plateaued cycles 009-010.
- `BEST_POISSON_NEAR_BAR`: 0.0596 → 0.0596 → 0.0596 → 0.0381 → 0.0381 — **improving** in step at cycle-009-h1h2 (fno_mf_stack capacity bump), plateaued cycle-010.
- `FNO_COREGIONALIZATION_POISSON_FAR_OVER_BAR`: 0.598 → 0.750 → 0.598 → 0.598 — **stable-broken** across cycles. Cycle-008 baseline showed a worse 0.750 because the constructor fix unlocked a Poisson-eval path that had been crashing; this is *unmasked* failure, not regression. The K-basis form has not been touched and the failure persists.

### Improvements vs regressions
- **Improvements**: fno_mf_stack composite via capacity bump (009-h1h2). fno_coregionalization heat via paper-capacity bump (008-H1) and two-stage LF→HF curriculum (008-H2).
- **Regressions**: none cycle-009-h1h2 → cycle-010 (exact reproduction). Cycle 007→008 fno_coregionalization × poisson 0.598 → 0.750 = brief regression on cache miss/non-deterministic retrain, since recovered.
- **New failures**: none this cycle.

## Recommended Interventions

All interventions must live in `models/**`. Ranked by expected composite impact × feasibility × NK-distance.

### 1. **Push fno_mf_stack capacity further (Poisson lever)** — files: `models/fno_mf_stack/smoke_eval.py` (SMOKE_DEFAULTS), `models/fno_mf_stack/full_config.json`, optionally `models/fno_mf_stack/model.py`
- Current SMOKE_DEFAULTS: `hidden=64, modes_per_level=(4,8,16,20), n_blocks=4, agg_hidden=64`
- Proposed sweep ladder: `(4,8,16,24)` → `(4,8,20,28)`; hidden `64→96`; n_blocks `4→5`.
- Rationale: fno_mf_stack is the **load-bearing composite cell** (poisson 0.038 vs paper ODE2 0.036, 5.9% over). One capacity step (cycle-009-h1h2: hidden 32→64, modes (4,8,8,8)→(4,8,16,20), blocks 3→4) delivered −36% on Poisson without saturating. A second step has a high prior on −10 to −20% Poisson, mapping to −3 to −6% composite if heat best holds.
- Wall-clock cost: cycle-009-h1h2 was 414s; expect 600–900s with these bumps.
- **MANDATORY kill switches**: Poisson absolute > 0.0594 (cycle-008 baseline level); wall > 1500s. Identical guard pattern to cycle-009-h1h2.
- NK-clear (NK1/NK2/NK3 do not apply — this is in-family capacity).

### 2. **Two-stage frozen-LF curriculum on fno_mf_stack** — files: `models/fno_mf_stack/smoke_eval.py`, `models/fno_mf_stack/model.py`
- Apply the cycle-008 H2 LF→HF schedule (50 LF-only epochs, then 150 joint with cosine restart) to fno_mf_stack.
- **Carve-out justification vs NK2**: NK2 closed frozen-LF curricula on co-evolved residual ladders (fno_coregionalization, fno_coreg_residual where HF residuals are coupled to LF latents). fno_mf_stack has **independent LF/HF FNOs** stitched only by the MFRNP aggregator on the output — this is the structural difference NK2 calls out as "may work on LF/HF-independent designs".
- **MANDATORY dual kill-switches** (both absolute and inter-stage):
  - Absolute: Poisson test > 0.0594 ; heat test > 0.0594.
  - Inter-stage: stage-2 best_val must reduce stage-1 best_val by ≥10%; else revert.
- Wall-clock: doubles training. Set `wall_kill_switch=1800s`.
- Expected impact: +0 to −10% Poisson; the heat side may benefit since fno_mf_stack heat is 0.038 (the same as Poisson — there's slack there too).

### 3. **fno_coregionalization Poisson-specific K-basis revision** — files: `models/fno_coregionalization/model.py`
- Replace `B(m)=MLP([m, m²])` on Poisson with `B(m, LF_features)` — pass the per-fidelity LF feature vector into the basis MLP so the K-basis can adapt to the 42× signal-magnitude ladder.
- **NK-distance**: this is *not* NK3 (NK3 closed MFRNP-style **loss-weight transfer** to the coregionalization family). NK3 is about loss-weighting; this is about basis parametrization. Distinct mechanism, untouched axis.
- **MANDATORY guard**: heat test ≤ 0.0194 (current best is 0.0129; this is the cycle-008 baseline). Trip if heat regresses to protect the heat composite leader.
- Expected impact: if the K-basis collapse on Poisson is the root cause of the 0.598 cell, even partial recovery to 0.10–0.30 would not improve composite (still over best 0.038), but recovery to <0.038 would create a second contender on Poisson and could unlock a different family-tradeoff.
- **Hedge**: this is exploratory. Lower priority than (1) and (2) for composite movement.

### 4. **Restore / rewrite fno_coreg_conditioned with γ(m, LF_features)** — files: `models/fno_coreg_conditioned/` (currently empty except `__pycache__/model.cpython-312.pyc`)
- The cycle-008 H2 attempt at NK1 (pure m-conditioning on HF-only FNO) failed. The NK1 carve-out is: include the LF→HF pathway in the conditioning. A `γ(m, LF_features)` conditioning that uses LF as input would satisfy that.
- **NK1 anti-pattern explicitly avoided** by including LF features in γ.
- The package directory is empty — this requires reconstructing `model.py`, `smoke_eval.py`, `manifest.json`, `data.py`. Substantial implementation surface.
- Expected impact: speculative. Lowest priority — pursue only if (1)–(3) plateau.

### 5. (Deferred) **MFRNP-Poisson recipe transfer to fno_coreg_residual** — explicitly **NK3-blocked**
- This intervention surface (transferring fno_mf_stack's Poisson loss-weight recipe to a coregionalization-family member) is closed by NK3 (3/3 failures across cycles 003/006/007). Do not pursue.

### 6. (Deferred) **New family proposals** (transolver_residual revamp, MF-DeepONet)
- transolver family is 10×–144× over bar on Poisson; revamp is high-cost low-prior. MF-DeepONet has no implementation surface in the repo. Treat as later-cycle ideas after exhausting (1)–(4).

## Anti-Patterns to Avoid (NKs in force for cycle-010)

1. **NK1** (cycle-008 H2): Pure m-conditioning on HF-only FNO. Any HF-only γ(m) without an LF→HF pathway is closed.
2. **NK2** (cycle-008 H3): Frozen-LF curricula on co-evolved residual ladders (`fno_coregionalization`, `fno_coreg_residual`) — incompatible. Multi-stage curricula are permitted on LF/HF-independent designs (`fno_mf_stack`, `mf_fno_transfer_bar`) **only with mandatory dual kill-switches** (absolute on Poisson nRMSE and inter-stage best_val improvement).
3. **NK3** (cycles 003/006/007): MFRNP-style loss-weight transfer to the coregionalization family — 3/3 failures. Closed.

## Failure Taxonomy Update

New category names introduced this cycle:
- `POISSON_STRUCTURAL_GAP_PER_FAMILY_ASYMMETRY` — dominant failure mode. Different families win different datasets; the heat-winner family is Poisson-broken and vice-versa, blocking any single-family path to composite improvement.
- `K_BASIS_NON_UNIFORM_FIDELITY_LADDER_COLLAPSE` — observed mechanism in `fno_coregionalization × poisson`. The K-basis B(m)=MLP([m,m²]) generalizes from val to test on a near-uniform fidelity scaler ladder (heat: [1,1,1,1]) but collapses by 11× on a 42×-dynamic-range ladder (poisson: [0.077, 0.024, 0.0069, 0.0018]).
- `VAL_TO_TEST_INFLATION` — cross-cell category for val/test ratio > 5× (observed in fno_coregionalization × poisson, v9_baseline × poisson, transolver_residual × poisson). Not a primary lever this cycle but a flag for future generalization-gap analyses.
- `MFRNP_AGGREGATOR_POISSON_SPECIALIZATION` — fno_mf_stack's aggregator equalizes heat/poisson at ~0.038, suggesting it is Poisson-shaped and sub-optimal on heat (where fno_coregionalization sits at 0.013). Carries forward as a separate axis for cycle-011+.
