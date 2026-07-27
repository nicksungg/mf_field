# Failure Analysis — Cycle 004 (Baseline Entry)

## Summary

- **Instances:** 1/2 datasets at-or-beat paper bar (composite_nRMSE = **0.04415**).
- **Cycle-004 entry baseline = clean re-verification of cycle-002 H3** on `fno_coreg_residual`. Reproduces the reported 0.04420 to within 0.1% under from-scratch GPU training (cache=miss, train_seconds 478s heat / 149s poisson, cuda). The "checkpoint contamination" hypothesis from the cycle-003 retrospective is **REFUTED for the baseline**; the project-best number is valid.
- **Dominant failure mode:** `POISSON_UNDER_PAPER_BAR` — `ifc_poisson` at 0.07419 sits **2.06× over** paper bar 0.036 (HARD by the >2× threshold, but barely). This is 100% of the remaining gap to two-of-two paper-beating.
- **Secondary mode carried in from cycle-003:** `BACKBONE_LOSS_RECIPE_FRAGILITY` — the static MFRNP `(HF=2.0, LF=0.25)` recipe that helps `fno_mf_stack` catastrophically harms `fno_coreg_residual` (3.68× regression on Poisson; cycle-003 H1 REFUTED). Any cycle-004 intervention on Poisson must either drop static recipes, gentle them substantially, or otherwise solve the LF-starvation mechanism on the hybrid backbone.
- **Comparison with prior cycle:** improving relative to cycle-003 H1 (composite 0.08472 → 0.04415, restored from the H1 regression). No change relative to cycle-002 H3 (project best preserved).

## Per-Instance Results

### Instance ifc_heat
- **Status:** PASS (beats paper)
- **Stage:** N/A (training completes cleanly)
- **Metric:** test nRMSE = 0.02628 (best_val 0.01704; train_seconds 477.7)
- **Paper bar:** 0.074 (li2022ifc IFC-ODE2); **status SOLVED** — beats paper by 2.82×.
- **Mechanism behind success:** H3's per-fidelity FNO + continuous-m basis head + per-fidelity y-scaler — Heat path runs under uniform `(1.0, 1.0)` loss weights, so the basis head + aggregation paths get balanced LF/HF supervision and the per-fidelity normalizer eliminates the scale-mismatch failure mode from earlier cycles.
- **Composite contribution:** Heat's log nRMSE is −3.638; the geometric mean (composite) is dominated by it being far below the geomean floor — heat alone covers the entire "below-paper-geomean" margin.
- **Failure category:** None.
- **Suggested action:** **Preserve.** Cycle-004 interventions MUST gate on `"poisson"` substring (or equivalent dataset filter) so the heat path stays at uniform weights and the basis head retains balanced LF/HF gradient signal.

### Instance ifc_poisson
- **Status:** FAIL vs paper (PASS vs cycle-004 entry — this IS the entry).
- **Stage:** Training generalization (basis-head + MFRNP-aggregation, HF residual learning).
- **Metric:** test nRMSE = 0.07419 (best_val 0.02295; train_seconds 149.2).
- **Paper bar:** 0.036 (li2022ifc IFC-ODE2); **status HARD** — ratio 2.06×, just over the >2× HARD threshold; equivalently 1.24× worse than the cycle-002 H4 result (0.0596) on the simpler `fno_mf_stack` backbone with the published MFRNP `(2.0, 0.25)` recipe.
- **Val/test gap:** 0.02295 vs 0.07419 — factor 3.23×. The model trains to a much tighter validation minimum than the held-out test distribution exhibits, indicating limited OOD generalization on Poisson (consistent with the cycle-003 H1 pattern, though far less severe than H1's 3.49× gap of 0.0783→0.27287).
- **Failure category:** `POISSON_UNDER_PAPER_BAR` (renamed from cycle-003's `ABSENT_POISSON_LOSS_WEIGHTING` — the cycle-003 framing that absent loss-weighting was the root cause was REFUTED; the gap persists even when the H3 backbone is given a published static recipe).
- **Mechanism (current best understanding):**
  - H3 trains under uniform `(1.0, 1.0)` per-fidelity loss weights. The HF residual head (`basis_head + agg_anchor`) and the LF decoders (LF1/LF2/LF3) receive equal-weight gradient.
  - Elliptic (Poisson) global coupling is harder than parabolic (Heat) local diffusion — the HF correction the basis head must learn is structurally larger and longer-range than for Heat, but the optimisation budget is split evenly with LF supervision.
  - The `B(m)` MLP last-linear is zero-init, so the basis residual starts at 0 and the architecture begins as pure MFRNP aggregator. Whether the basis head converges to nontrivial weights on Poisson under uniform loss weighting is the open question — if it stays near zero, capacity is the lever; if it grows but is mis-calibrated, calibration is the lever.
- **Composite contribution:** Poisson's log nRMSE is −2.601 — entire remaining margin to paper geomean 0.0516 (log −2.964) sits on this dataset. If Poisson drops to 0.036 with Heat unchanged, composite drops to 0.0307 (−30%). If Poisson drops to the H4 floor 0.0596, composite drops to 0.0396 (−10%, the predicted cycle-003 H1 floor that was missed).
- **Suggested action:** Apply Poisson-only intervention that addresses **either** loss-weighting (adaptive, not static) **or** capacity/calibration on the HF-residual path. See "Recommended Interventions" below.

## Failure Distribution

| Category                            | Instances | %   | Notes |
|---                                  |---:|---:|---|
| `POISSON_UNDER_PAPER_BAR`           | 1 | 50% | ifc_poisson 0.07419 over paper 0.036; 100% of the unbeaten-dataset gap |
| Solved (BEATS_PAPER)                | 1 | 50% | ifc_heat 0.02628 beats paper 0.074 by 2.82× |

**Dominant failure mode:** `POISSON_UNDER_PAPER_BAR` (50% of instances; 100% of the failing-dataset surface).

Carried over from cycle-003 (refuted hypothesis state, not currently active in the baseline but constrains intervention design):
- `BACKBONE_LOSS_RECIPE_FRAGILITY` — the H4 static MFRNP `(2.0, 0.25)` recipe is backbone-coupled, not PDE-class-bound. Applies as a **risk gate** for any cycle-004 intervention that touches per-fidelity loss weighting on `fno_coreg_residual`.

## Cycle-003 H1 Regression Mechanism (Refuted Hypothesis)

**Why did porting MFRNP Poisson5 `(HF=2.0, LF=0.25)` catastrophically harm `fno_coreg_residual` (poisson 0.0742 → 0.27287, 3.68× regression) when it helped `fno_mf_stack` (poisson 0.0999 → 0.0596, 39% improvement)?**

The cycle-003 summary distinguishes four candidate causes; the empirical signal triangulates as follows:

| Candidate cause                                              | Evidence                                                                                          | Verdict                                  |
|---                                                           |---                                                                                                |---                                       |
| **(a) Static recipe backbone-incompatibility (LF starvation)** | Down-weighting LF to 0.25 starves the per-fidelity FNOs that feed the MFRNP decoder; H3's basis-head + aggregation paths rely on balanced LF signal to spread information across fidelities | **DOMINANT (most likely root cause)**     |
| (b) Aggregator-anchor scaling decision (builder applied `hf_fid_weight` to anchor term too) | Effective HF/LF gradient ratio slightly more aggressive than literal 8:1; cycle-003 close-out called this out but noted the 3.68× regression magnitude is too large for anchor-scaling alone | Secondary amplifier; not primary         |
| (c) Val/test generalization gap                              | val_nRMSE 0.0783 vs test 0.27287 — factor 3.49× gap; model fits a narrow HF-feature subset that doesn't generalize | **Symptom, not root cause** — the gap is what (a) produces under aggressive HF up-weighting |
| (d) Combination of (a) + (b)                                 | Most parsimonious explanation: (a) is the dominant mechanism; (b) amplifies the magnitude by ~10-20% | Working hypothesis                       |

**The 3.49× val/test gap is the diagnostic fingerprint of LF starvation:** the model finds an HF-feature subset that fits the validation distribution tightly (val 0.0783 — close to the entry 0.0742), then fails to generalize to the test distribution (0.27287) because the cross-fidelity information-sharing pathway (LF decoders → MFRNP aggregator → HF residual) was starved during training. The fundamental asymmetry is that H4's `fno_mf_stack` has no aggregator-anchor regulariser and no basis-head — it is a pure residual stack — so LF down-weighting only changes per-level supervision intensity. H3 has a multi-path information-fusion architecture, and one of those paths (the aggregator path) is itself what feeds the HF residual at inference. Starving LF starves the aggregator path, which starves the basis residual's effective input at HF time.

**Cycle-003 close-out mechanism hypothesis (cited):** "upweighting the HF residual (×2.0) over the basis-head + aggregation paths overconcentrates the model's gradient budget on a narrow set of HF features that overfit, while down-weighting LF supervision (×0.25) starves the cross-fidelity sharing that H3's coregionalization stack depends on for generalization."

**The cycle-004 baseline confirms this mechanism is specific to the static recipe**: under uniform `(1.0, 1.0)` weights, ifc_poisson sits at 0.07419 with val/test gap 3.23× — a much milder version of the same OOD-generalization signature, suggesting the residual head is still under-capacity / under-trained for Poisson HF features, but not in the catastrophic LF-starvation regime that the H1 recipe induced.

## Dominant Failure Modes for Cycle-004

### Mode 1: `POISSON_UNDER_PAPER_BAR` (primary)
- **Frequency:** 100% of the remaining gap to two-of-two paper-beating (0.07419 vs paper 0.036). Drives the entire composite gap to paper geomean 0.0516.
- **Mechanism (current best understanding):**
  - Elliptic global coupling on Poisson requires longer-range HF correction than the basis-head learns under uniform loss-weighting at the current capacity (K=10, b_hidden=64, decoder_hidden=32).
  - Val/test gap 3.23× indicates the HF residual head fits a narrow validation-distribution subset but fails to generalize — consistent with insufficient effective HF supervision or insufficient capacity in the basis-head/aggregator path.
  - Unlike Heat (already 2.82× under paper, parabolic, locally-supervised structure suits the per-fidelity FNO + zero-init basis residual), Poisson sees a structurally larger HF correction that the current architecture does not converge on.
- **Suggested intervention class:** (i) **adaptive per-fidelity loss-weighting** (GradNorm-lite, uncertainty-weighted) on Poisson; (ii) **gentler static asymmetry** as a fallback (1.5, 0.5 with anchor unscaled); (iii) **per-dataset capacity / basis-head calibration** override on Poisson.
- **Mutable surfaces touched:** `models/fno_coreg_residual/smoke_eval.py` (primarily); `models/fno_coreg_residual/model.py` (if K / b_hidden / decoder_hidden are widened on Poisson); or `models/<new-family>/**` for a fresh-family approach.
- **Risk classification:**
  - Adaptive loss-weighting: **MEDIUM** — addresses the cycle-003 root cause directly but adds tuning complexity (asymmetry rate α, weight learning rate, gradient probe target). Recoverable failure mode (no architectural commitment).
  - Gentler static asymmetry: **HIGH** — still backbone-coupled in the cycle-003 framing; the cycle-003 summary explicitly flagged (1.5, 0.5) as a guess without theoretical anchor. If recipe is fundamentally backbone-incompatible, gentler magnitude may still produce a regression at smaller scale (e.g. 1.3-1.5× worse Poisson rather than 3.68×).
  - Per-dataset capacity / calibration: **LOW** — additive architectural change with zero-init basis residual means failure mode is no-op rather than catastrophic regression. Lower expected upside than the loss-weighting routes but lowest downside.

### Mode 2: `BACKBONE_LOSS_RECIPE_FRAGILITY` (gating constraint, not a primary target)
- **Frequency:** N/A — this is a refuted-hypothesis pattern from cycle-003 H1 that gates how cycle-004 may approach Mode 1. Currently inactive in the baseline (the recipe is not applied).
- **Mechanism (current best understanding):** Static MFRNP `(2.0, 0.25)` recipe assumes a pure residual-stack architecture (`fno_mf_stack`); applying it to a hybrid basis-head + MFRNP-aggregation backbone starves the LF→aggregator information pathway and induces a val/test OOD-generalization collapse.
- **Suggested intervention class:** Avoid static recipes that commit to specific HF/LF ratios on `fno_coreg_residual`. Prefer adaptive schemes that observe per-fidelity gradient magnitudes and rebalance per-step, OR keep loss-weighting fully uniform and address Poisson via the architectural surface.
- **Mutable surfaces touched:** Same as Mode 1.
- **Risk classification:** **N/A** as a target; **HIGH** as a constraint — any cycle-004 hypothesis that ports another static recipe risks reproducing the cycle-003 H1 regression at smaller magnitude.

### Mode 3 (constraint): `HEAT_PRESERVATION_GATE`
- **Frequency:** N/A — preservation requirement, not a failure.
- **Mechanism:** `ifc_heat` at 0.02628 (2.82× below paper bar 0.074) is the entire composite cushion. Cycle-003 H1 preserved it incidentally (resolver gated on "poisson"); any cycle-004 hypothesis must either gate or otherwise prove non-regression via dual-dataset 2-epoch pre-flight smoke.
- **Risk classification:** **HIGH if cycle-004 modifies code paths shared by both datasets** (e.g. unconditional changes to `compute_losses`, the basis head, or the aggregator); **LOW if all changes are Poisson-gated**.

## Cycle-004 Pre-Registered Directions (Assessment)

### 1. Adaptive loss-weighting (GradNorm-lite, uncertainty-weighted, PCGrad) → **PRIMARY CANDIDATE**
- **Expected ifc_poisson impact:** plausibly in [0.04, 0.07] — best case adaptive scheme outperforms static `(2.0, 0.25)` on H3 (which itself targeted H4's measured 0.0596 floor); worst case adaptive scheme is unstable and falls back to ~baseline.
- **Risk of regressing ifc_heat:** LOW if gated to Poisson-only, or if the scheme degenerates to uniform weights on Heat (where per-fidelity gradients are already balanced).
- **Smoke wall-time:** comparable to baseline (149s Poisson currently). GradNorm adds a per-step gradient probe (one extra backward through last shared layer) — overhead ~10-30%.
- **Mutable-surface compatibility:** `models/fno_coreg_residual/{smoke_eval.py, model.py}` only.
- **Strengths:** addresses cycle-003 root cause (static-recipe backbone-coupling) directly; pre-registered by cycle-003 close-out as direction (a); doesn't commit to a specific HF/LF ratio a priori; theoretically grounded (Chen 2018 GradNorm, Kendall 2018 uncertainty-weighted).
- **Risks:** tuning complexity (asymmetry rate α, weight learning rate); if gradient probe is mis-placed (e.g. on a layer that doesn't represent the bottleneck), the scheme can drive weights to unhelpful equilibria.

### 2. Gentler static asymmetry (e.g. (1.5, 0.5)) → **SECONDARY**
- **Expected ifc_poisson impact:** plausibly in [0.05, 0.10] — gentler than (2.0, 0.25); should be less destructive; might preserve more LF signal flow. Cycle-003 summary noted this is a guess without theoretical grounding.
- **Risk of regressing ifc_heat:** LOW if Poisson-gated.
- **Smoke wall-time:** unchanged.
- **Mutable-surface compatibility:** `models/fno_coreg_residual/smoke_eval.py` only.
- **Strengths:** smallest possible code change; preserves the H4-recipe-port spirit at milder magnitude; could be combined with an anchor-unscaling ablation (direction 3) to isolate the cycle-003 H1 mechanism.
- **Risks:** still backbone-coupled per cycle-003 framing; possible smaller-magnitude regression at same mechanism. No theoretical reason `(1.5, 0.5)` is right for H3.

### 3. Aggregator-anchor scaling ablation (unscale anchor under HF up-weighting) → **DEFERRED / SECONDARY-SUB**
- **Expected ifc_poisson impact:** modest at best. Cycle-003 close-out explicitly noted the 3.68× regression magnitude is too large for anchor-scaling alone to explain — root cause is (a) static-recipe-backbone-incompatibility, not (b) anchor-scaling. As a sub-ablation under direction 1 or 2 it has clean isolation value; as a standalone hypothesis its expected upside is small.
- **Risk of regressing ifc_heat:** LOW.
- **Smoke wall-time:** unchanged.
- **Mutable-surface compatibility:** `models/fno_coreg_residual/smoke_eval.py` only (one-line change to `compute_losses`).
- **Strengths:** very low cost; isolates one specific cycle-003 build choice.
- **Risks:** **DEFERRED** — too narrow as a standalone H1; only valuable as a sub-ablation inside another hypothesis.

### 4. New family on a different backbone (transolver_residual, mfgnn_residual, oformer_attention_fusion, etc.) → **DEFERRED**
- **Expected ifc_poisson impact:** unknown — depends entirely on the chosen backbone × MF-concept combination. Cycle-002 evidence shows that backbone capacity matters (H4 hidden=32 → 0.0596 with recipe vs H2 hidden=32 → 0.0979 without), so a fresh backbone at full capacity could in principle match or exceed H3.
- **Risk of regressing ifc_heat:** depends on family — could go either way without preserving the current architecture.
- **Smoke wall-time:** unknown but likely comparable per family. Cycle-004 budget cannot absorb a wall-time blow-out from an unfamiliar backbone.
- **Mutable-surface compatibility:** `models/<new-family>/**` only.
- **Strengths:** clean second-backbone evidence for the backbone-coupling question; addresses scope expansion that the backlog has been flagging since cycle-002.
- **Risks:** **DEFERRED** — new family means new data loaders, model code, full_config validation, dual-dataset wall-time gating. Realistically one cycle's worth of operational work alone, with high risk of operational failure or empty signal. Better suited to cycle-005+ once cycle-004 lands a focused intervention on the existing best backbone.

### 5. Per-dataset capacity / modes override on `fno_coreg_residual` (e.g. Poisson-only `K=20`, `b_hidden=128`, `decoder_hidden=64`, or `modes_per_level=(4,8,12,16)`) → **SECONDARY**
- **Expected ifc_poisson impact:** plausibly in [0.05, 0.07] if basis-head / aggregator capacity was the bottleneck. Could be no-op if zero-init basis-head MLP weights stay near zero under uniform loss weighting (i.e. the basis residual never engages regardless of K). Basis-head calibration probe (cycle-003 strategy backlog item) would diagnose this.
- **Risk of regressing ifc_heat:** LOW if Poisson-gated; MEDIUM if unconditional.
- **Smoke wall-time:** modest increase (basis head and decoder are small; param count today is 9.12M, adding K=10 channels and a wider B(m) MLP adds <500K params).
- **Mutable-surface compatibility:** `models/fno_coreg_residual/{smoke_eval.py, model.py}`.
- **Strengths:** purely additive architectural change with zero-init residual head means failure mode is no-op rather than regression — **LOWEST downside** of any direction. Targets a different mechanism (capacity / calibration) than directions 1-3 (loss weighting), so non-overlapping evidence even if combined later.
- **Risks:** lower expected ceiling than adaptive loss-weighting if the actual bottleneck is per-fidelity supervision balance rather than residual-head capacity.

## Operational Prerequisite Status (recipe_hash hygiene)

**Backlog item #17 (per-family recipe_hash fix in `models/<family>/smoke_eval.py`) — filed, NOT YET IMPLEMENTED.**

Status check on the cycle-004 baseline run:
- The baseline run on 2026-05-15 was operationally clean: `cache=miss` on both datasets, `train_seconds=478s` Heat and `149s` Poisson (cuda, from-scratch), `device=cuda` on both — manually validated by clearing `checkpoints/fno_coreg_residual/` before submission.
- The underlying factory bug remains live: the resume guard in `models/fno_coreg_residual/smoke_eval.py:221-232` accepts a checkpoint whenever `epochs_target == args.epochs AND cond_dim == cond_dim` — it does NOT include any recipe fingerprint. Any cycle-004 H1 that varies SMOKE_DEFAULTS (e.g. new `poisson_hf_weight`, basis-head `K`, optimizer hyperparams) is vulnerable to silently inheriting prior training.

**Recommendation for cycle-004:** include the recipe_hash fix as a **prerequisite landing within the same hypothesis branch** (lower cost than a separate prerequisite cycle, and the hypothesis would otherwise be exposed to the same contamination class). Concrete landing site:
- `models/fno_coreg_residual/smoke_eval.py` (and any new family's `smoke_eval.py` if a new family is added):
  - On checkpoint save (lines 277-286): include `"recipe_hash": stable_hash(SMOKE_DEFAULTS)` in the saved dict.
  - On resume guard (lines 221-232): require `sd.get("recipe_hash") == stable_hash(SMOKE_DEFAULTS)` in addition to the existing checks; otherwise fall through to "starting fresh".
  - `stable_hash` is e.g. `hashlib.sha256(json.dumps(p, sort_keys=True, default=str).encode()).hexdigest()[:12]`.
- This is mechanically a ~10-line change confined to the mutable surface.

The fix is not the cycle-004 hypothesis itself — it's a **co-landing operational dependency**. If cycle-004 H1 chooses to run multiple SLURM jobs (e.g. an ablation matrix), this fix prevents silent cross-contamination between them. If cycle-004 H1 is single-run from-scratch with manual checkpoint-dir clears (cycle-003 H1 pattern), the fix is still strongly recommended but technically deferrable.

## Recommended Interventions

Three concrete intervention candidates ranked by expected impact × risk, all confined to `models/**`:

### Candidate 1 — GradNorm-lite adaptive per-fidelity loss-weighting on `fno_coreg_residual` (Poisson-only)

- **Code change:** `models/fno_coreg_residual/smoke_eval.py` (and small additions to `models/fno_coreg_residual/model.py` for a learnable per-fidelity weight buffer).
- **Mechanism:** introduce learnable per-fidelity loss-weight parameters `w_k` (one per level, initialised at 1.0) on Poisson datasets. At each step, after the main backward, perform a second cheap backward through one shared layer (e.g. the aggregator MLP) to measure per-fidelity gradient norms `G_k`; update `w_k` to drive `G_k → G_target` (a moving average of all `G_k`) via a small auxiliary loss (Chen et al. 2018 GradNorm). Heat path retains uniform `(1.0, 1.0)` via a `"poisson"` substring gate, identical to the cycle-003 H1 dataset filter (same gating mechanism, different per-fidelity scheme).
- **Anchor handling:** explicitly do NOT scale `agg_anchor_weight` by any per-fidelity weight — keep anchor at a fixed `0.5` per current SMOKE_DEFAULTS. This isolates the cycle-003 builder-choice (b) cleanly.
- **Recipe_hash co-landing:** include the resume-guard fix in the same change.
- **Expected `ifc_poisson` outcome:** plausibly in [0.04, 0.07]. Anchored precedent: cycle-002 H4 measured 0.0596 with static `(2.0, 0.25)` on a simpler backbone; adaptive scheme on the richer H3 backbone could plausibly beat 0.0596. Worst case adaptive scheme converges to near-uniform weights (no-op vs baseline 0.0742) or oscillates (modest regression). Reaches paper bar 0.036 only if the cycle-003 framing was correct that loss-weighting alone is the gap — adaptive scheme has a better chance than static at finding the right ratio.
- **Expected `ifc_heat` outcome:** unchanged at ~0.0263 (Poisson-gated; Heat path runs the existing uniform-weight branch).
- **Composite floor / ceiling estimate:** floor `geomean(0.0263, 0.04) ≈ 0.0324` (−27% vs entry); ceiling `geomean(0.0263, 0.0742) = 0.0442` (entry baseline, no improvement).
- **Risk:** **MEDIUM** — tuning complexity (asymmetry rate α typical 1.5, weight learning rate ~1e-3); the scheme can be unstable if gradient probe layer is wrong; but failure mode is recoverable (no architectural commitment, can revert). Highest expected upside of the three candidates.

### Candidate 2 — Per-dataset basis-head capacity expansion on Poisson

- **Code change:** `models/fno_coreg_residual/smoke_eval.py` (gate `K`, `b_hidden`, `decoder_hidden` on `"poisson"` substring) + `models/fno_coreg_residual/model.py` (no change if the constructor already accepts these — appears it does at lines 195-205).
- **Mechanism:** on Poisson datasets, override `K=20` (vs default 10), `b_hidden=128` (vs 64), `decoder_hidden=64` (vs 32). The basis head learns `K` orthogonal HF-residual channels via `B(m) = MLP_B([m, m²])`, last-linear zero-init. Doubling `K` + widening the `B(m)` MLP gives the residual head ~2× capacity for HF correction without committing to a specific loss-weighting ratio. Uniform `(1.0, 1.0)` loss weights preserved. Diagnostic logging: print `‖B.last_linear.weight‖` at epoch 200 to check whether basis head engaged at all (calibration probe).
- **Recipe_hash co-landing:** include the resume-guard fix in the same change.
- **Expected `ifc_poisson` outcome:** plausibly in [0.05, 0.07]. Anchored precedent: cycle-002 F4 (capacity bump on `fno_mf_stack` hidden 32→32 + MFRNP recipe) drove Poisson from 0.0979 to 0.0596 — capacity matters when paired with the right HF emphasis. If H3 basis-head was capacity-limited rather than supervision-limited, expanding K/b_hidden alone could yield similar gains under uniform weights. No-op if basis-head weights stay near zero (calibration probe will diagnose).
- **Expected `ifc_heat` outcome:** unchanged at ~0.0263 (Poisson-gated; Heat path runs default capacity).
- **Composite floor / ceiling estimate:** floor `geomean(0.0263, 0.05) ≈ 0.0363`; ceiling `geomean(0.0263, 0.075) ≈ 0.0444` (essentially baseline).
- **Risk:** **LOW** — additive architectural change with zero-init basis residual; failure mode is no-op rather than regression. Smoke wall-time impact small (adds ≲ 500K params to the 9.12M total). Lowest downside of the three candidates.

### Candidate 3 — Gentler static asymmetry (1.5, 0.5) with anchor-unscaling on `fno_coreg_residual` (Poisson-only)

- **Code change:** `models/fno_coreg_residual/smoke_eval.py` — port the same `resolve_fidelity_weights(dataset_name, p)` helper from `models/fno_mf_stack/smoke_eval.py` that cycle-003 H1 used, but with SMOKE_DEFAULTS `poisson_hf_weight=1.5`, `poisson_lf_weight=0.5` (vs cycle-003 H1's 2.0/0.25). Critically, in `compute_losses` do NOT multiply the `agg_anchor_weight * loss_anchor` term by `hf_fid_weight` — keep anchor unscaled (this is the cycle-003 close-out direction 3, isolating the builder choice (b)).
- **Recipe_hash co-landing:** include the resume-guard fix.
- **Expected `ifc_poisson` outcome:** plausibly in [0.05, 0.10]. Gentler than `(2.0, 0.25)` so less LF-starvation; anchor-unscaling further reduces effective HF/LF ratio asymmetry. But still backbone-coupled in the cycle-003 framing; the magnitude of the cycle-003 regression (3.68×) suggests the recipe is fundamentally backbone-incompatible regardless of degree.
- **Expected `ifc_heat` outcome:** unchanged at ~0.0263 (Poisson-gated).
- **Composite floor / ceiling estimate:** floor `geomean(0.0263, 0.05) ≈ 0.0363`; ceiling `geomean(0.0263, 0.10) ≈ 0.0513` — note the **ceiling overlaps the paper geomean 0.0516**, meaning a downside scenario could regress the entry baseline 0.04415 while still landing above paper geomean. This is a HIGH-RISK ceiling.
- **Risk:** **HIGH** — the cycle-003 close-out explicitly registered (1.5, 0.5) as direction (b) with the same backbone-coupling concern; the empirical evidence from cycle-003 H1 favours `BACKBONE_LOSS_RECIPE_FRAGILITY` as a fundamental rather than magnitude-dependent failure. Standalone hypothesis here is mostly informational (would generate a clean "is recipe magnitude dependent" data point) but expected mean impact is poor.

## Recommended PRIMARY for cycle-004 H1: **Candidate 1 (GradNorm-lite adaptive)**

Rationale: addresses the cycle-003 root cause (static-recipe backbone-coupling) by removing the static commitment entirely; pre-registered by the cycle-003 close-out as direction (a); highest expected upside on the dominant failure mode `POISSON_UNDER_PAPER_BAR`; Heat preservation enforced by the same Poisson-substring gate that cycle-003 H1 validated; risk MEDIUM (tuning) but recoverable. Candidate 2 (capacity expansion) is a strong SECONDARY (LOW risk, non-overlapping mechanism — could be promoted to PRIMARY if Strategist prefers minimum-risk pathing). Candidate 3 is DEFERRED unless a controlled (1.5, 0.5) ablation is explicitly desired to bound the recipe-fragility-by-magnitude question.

## Failure Taxonomy Update

New / refined entries this cycle:

| Category                              | Status      | First seen | Notes |
|---                                    |---          |---         |---|
| `POISSON_UNDER_PAPER_BAR`             | RENAMED     | cycle-002  | Cycle-002/003 called this `ABSENT_POISSON_LOSS_WEIGHTING`; the cycle-003 framing (absent loss-weighting is the root cause) was REFUTED, so the category is renamed to describe the *symptom* (Poisson over paper bar) rather than the *hypothesised root cause* (absent loss-weighting). |
| `BACKBONE_LOSS_RECIPE_FRAGILITY`      | NEW         | cycle-003  | The MFRNP `(HF=2.0, LF=0.25)` recipe is backbone-coupled, not PDE-class-bound. Acts as a gating constraint on cycle-004 loss-weighting hypotheses on `fno_coreg_residual`. |
| `RESUME_GUARD_RECIPE_BLIND`           | OPEN BUG    | cycle-003  | `models/<family>/smoke_eval.py` resume guard ignores SMOKE_DEFAULTS changes; backlog item #17. Co-landing recommended in cycle-004 H1. |
| `HEAT_PRESERVATION_GATE`              | CONSTRAINT  | cycle-002  | `ifc_heat` 2.82× below paper bar — must not regress. Enforced operationally via Poisson-substring gating in all interventions; verified via dual-dataset 2-epoch pre-flight smoke. |
