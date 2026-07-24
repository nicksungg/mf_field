# Failure Analysis — Cycle 008 baseline

## Summary

- **Composite_nRMSE:** 0.030408 (geomean across ifc_heat best 0.01551 + ifc_poisson best 0.05961).
- **Source:** banked from cycle-007 H1 on `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`. Reproducible from a clean tree — first time the cycle-005 H2 heat number (0.01551) survives a fresh end-to-end re-eval.
- **Bar to dethrone:** `mf_fno_transfer_bar` parallel-bench composite **0.027429** (heat 0.01281, poisson 0.05871). To beat by 10% we need composite ≤ 0.02469.
- **Gap to bar:** +0.002978 composite (+10.86% over bar) — i.e. the smoke leaderboard is **10.9% above bar; about one −10% step short of dethroning** even before targeting −10%.
- **Dominant per-dataset gap to bar (log-space, composite-weighted):** **ifc_heat** (+0.1910 log-ratio, 1.21× over bar) — **12.6× larger composite-gap contribution than ifc_poisson** (+0.0151 log-ratio, 1.015× over bar).
- **Dominant per-cell failure (absolute nRMSE within actionable cells):** `fno_coregionalization` × `ifc_poisson` at **0.7501** — 12.61× over bar, 20.83× over paper. Does NOT enter the composite (Poisson leaderboard winner is `fno_mf_stack` at 0.05961), but **disqualifies fno_coregionalization from being a single-family answer to the project**.
- **Comparison with prior cycle:** REPRODUCIBLE BASELINE re-bank. Identical leaderboard to cycle-007 H1 (same commit 1249f2d). Two formal REVERTs since cycle-005 H2 (cycle-006 H1, cycle-007 H2) but net engineering trajectory is forward: aspirational 0.029357 → reproducible 0.030408 (now backed by committed code, not dirty-tree state).
- **Failure taxonomy:** stable. The dominant 14-cell failure pattern remains `CROSS_ARCHITECTURE_RECIPE_NONPORTABILITY` (3 reverts in row), `FAMILY_PDE_SPECIALIZATION_ASYMMETRY` (fno_coreg perfect on Heat, broken on Poisson; fno_mf_stack inverse), and `BAR_UNDERTRAINING_VS_CACHE` (`mf_fno_transfer_bar` still ~10 s train_seconds in the smoke loop — paper pipeline yields 0.02743 from parallel-bench cache).

---

## Per-Instance Results

The actionable problem set is **2 datasets × 6 families = 12 cells** (we exclude `v9_baseline` as a frozen reference and as the master baseline, but report its number for taxonomy continuity).

### `ifc_heat` (best 0.01551 by `fno_coregionalization`)

```
fno_coregionalization / ifc_heat
  Status:      PASS (leaderboard winner, beats bar 1.21× lower needed)
  Stage:       end-to-end smoke train
  nRMSE:       0.01551   (vs bar 0.01281 → +21.05%;  vs paper 0.074 → 4.77× under)
  Behavior:    K=10 MLP-basis B(m)=MLP([m,m²]) on FNO-trunk latent + per-fidelity normalization.
               This is the only family at HEAT below 0.02 across the leaderboard;
               cycle-005 H2 cache value (0.01551) reproduced under fresh from-scratch SLURM eval.
  Root cause of remaining gap (1.21× over bar): K=10 likely under-capacity vs paper K=20;
               anisotropic (modes_h, modes_w) constructor only restored isotropic-equivalent
               behavior — full anisotropic capacity is unverified.
  Category:    CAPACITY_PARETO (heat winner is capacity-bounded near bar)
  Suggested fix: bump K=10→20 (paper config); bump n_blocks=4→6; widen b_hidden=64→128;
               keep smoke wall-time budget by reducing epochs from 200→100 with stronger
               warmup (or run on H100). All changes are in models/fno_coregionalization/.
  Within mutable surfaces: YES — models/fno_coregionalization/smoke_eval.py SMOKE_DEFAULTS.

fno_coreg_residual / ifc_heat
  Status:      PASS (#2 on heat, 1.69× over bar)
  nRMSE:       0.02628
  Behavior:    Per-fidelity FNOs (K=20, b_hidden=128 banked in cycle-006 H1) + decoder-in-the-
               aggregation + coregionalization residual head with zero-initialized B. Heat
               improved 0.03519 → 0.02628 since cycle-005 (−25.3%) via the K=20/b_hidden=128
               capacity bump.
  Root cause of remaining gap: residual head's contribution still small (zero-init) — basis
               head not exercised; LF→HF transfer schedule (declared in fno_coregionalization
               for cycle-007 H2) NOT applied here.
  Category:    TRANSFER_SIGNAL_UNUSED (LF samples not used in pretrain stage)
  Suggested fix: add LF-only pretrain stage to models/fno_coreg_residual/smoke_eval.py
               (mirror the cycle-007 H2 schedule that already exists in fno_coregionalization).

mf_fno_transfer_bar / ifc_heat
  Status:      PASS (#3 on heat, 2.59× over bar's own parallel-bench number)
  nRMSE:       0.03317 (smoke) — bar parallel-bench delivers 0.01281
  Behavior:    Trains for ~10 s wall in the smoke loop. The parallel-bench pipeline (results/
               bench_metrics.csv) runs the same architecture to 0.01281; the smoke harness
               just doesn't allow it enough compute.
  Root cause:  smoke-harness BAR_UNDERTRAINING — the BAR's own family is underconfigured in
               the smoke loop relative to its parallel-bench self.
  Category:    BAR_UNDERTRAINING_VS_CACHE
  Suggested fix: bump smoke-time epochs / hidden / batch in
               models/mf_fno_transfer_bar/smoke_eval.py SMOKE_DEFAULTS to match results/
               bench_metrics.csv numbers. CAVEAT: mf_fno_transfer_bar is the BAR — improving
               it tightens the dethrone target but does not narrow the smoke gap; only useful
               for honest comparison.

fno_mf_stack / ifc_heat
  Status:      PASS (#4 on heat, 7.81× over bar)
  nRMSE:       0.09995
  Behavior:    MFRNP residual stack on FNO backbone. Strong on Poisson; weak on Heat —
               structural inverse-complementarity with fno_coregionalization. Cycle-002 H4
               bump (hidden=32, modes=(4,8,12,12)) did NOT close heat gap because the LF
               baseline aggregator is the bottleneck for Heat (LF input lacks heat boundary
               signature).
  Root cause:  ARCHITECTURE_INDUCTIVE_BIAS_MISMATCH — residual decomposition is the wrong
               prior for Heat (smooth, no sharp residuals).
  Category:    FAMILY_PDE_SPECIALIZATION_ASYMMETRY (Poisson-good / Heat-bad).
  Suggested fix: do not chase Heat with this family; let fno_coregionalization own Heat.

transolver_residual / ifc_heat
  Status:      PASS (8.97× over bar, last place among Heat-active families)
  nRMSE:       0.11456
  Category:    BACKBONE_INDUCTIVE_BIAS_MISMATCH — Transolver slice-attention is for irregular
               geometry; IFC is regular-grid where FNO dominates.
  Suggested fix: deprioritize — orthogonal inductive bias to the leaderboard winner.

transolver_attention_fusion / ifc_heat
  Status:      PASS (11.69× over bar)
  nRMSE:       0.14923
  Category:    BACKBONE_INDUCTIVE_BIAS_MISMATCH (same as transolver_residual)
  Suggested fix: deprioritize.

v9_baseline / ifc_heat
  Status:      reference (frozen surface)
  nRMSE:       0.14883
  Category:    F2 BACKBONE_INDUCTIVE_BIAS_MISMATCH (carry-over from cycle-002)
```

### `ifc_poisson` (best 0.05961 by `fno_mf_stack`)

```
fno_mf_stack / ifc_poisson
  Status:      PASS (leaderboard winner, near-bar parity)
  Stage:       end-to-end smoke train
  nRMSE:       0.05961   (vs bar 0.05871 → +1.53%;  vs paper 0.036 → 1.66× over paper)
  Behavior:    MFRNP residual stack on FNO backbone with HF=2.0/LF=0.25 loss reweighting
               (verbatim MFRNP Poisson5 config). Per-fidelity output normalization handles
               the 40× value-scale collapse.
  Root cause of remaining gap (1.5% over bar): minimal — at parity. Below-bar requires either
               capacity bump or curriculum schedule the family does not currently run.
  Category:    NEAR_PARITY_INCREMENTAL
  Suggested fix: capacity bump (n_blocks, hidden) under smoke wall-time budget;
               OR pretrain LF→HF curriculum (NEW lever, see Recommended Interventions).

fno_coreg_residual / ifc_poisson
  Status:      PASS (#2 on poisson, 1.26× over bar)
  nRMSE:       0.07419
  Behavior:    Same backbone+head that wins Heat at 0.02628. Was 0.05556 in cycle-005 (paper
               recipe applied via full_config.json); when cycle-006 H1 baked the K=20/b_hidden
               =128 heat-bump into committed defaults, Poisson regressed +33.5%. Cycle-007 H2
               tried to dispatch per-dataset (heat keeps K=20, poisson reverts to original
               recipe) — verdict REVERT (heat invariance broke +32.7% under fresh-train
               variance).
  Root cause:  ARCHITECTURE_OVERFIT — K=20/b_hidden=128 was tuned on Heat and degraded Poisson;
               per-dataset config dispatch did not preserve heat invariance empirically
               (cycle-007 H2 falsification).
  Category:    RECIPE_DATASET_NONPORTABILITY (same architecture, two PDEs with incompatible
               optimal recipes; dispatch tried, fresh-train variance swamped invariance).
  Suggested fix: do NOT add another loss-recipe dispatch (third attempt would be 4th cycle
               on the same lever). Instead, give Poisson a different family path —
               or pre-allocate two seeds × two recipes and BEST-OF, with the heat seed
               frozen.

mf_fno_transfer_bar / ifc_poisson
  Status:      PASS (#3 on poisson smoke, 1.42× over bar's own parallel-bench number)
  nRMSE:       0.08333 (smoke) — bar parallel-bench delivers 0.05871
  Category:    BAR_UNDERTRAINING_VS_CACHE (same as heat side)

transolver_attention_fusion / ifc_poisson
  Status:      PASS but >>bar (6.50× over bar)
  nRMSE:       0.38181
  Category:    BACKBONE_INDUCTIVE_BIAS_MISMATCH

fno_coregionalization / ifc_poisson  *** dominant single-cell failure ***
  Status:      PASS (mathematically) but 12.61× over bar (and 20.83× over paper)
  nRMSE:       0.75015
  Behavior:    Same architecture that wins Heat at 0.01551. K=10 MLP-basis B(m)=MLP([m,m²])
               on FNO-trunk latent + per-fidelity normalization. The number is identical
               (within seed noise) to cycle-005 cache 0.7756 — this is NOT a regression,
               it is the family's intrinsic Poisson failure mode that has persisted since
               cycle-001.
  Root cause:  ARCHITECTURE_FIT_PDE_MISMATCH — the K=10 MLP-basis on the m polynomial
               [m, m²] is rich enough for Heat's smooth m-modulation but cannot fit Poisson's
               m-dependent multi-fidelity correlation (Poisson has 4 fidelity levels with
               40× value-scale collapse AND non-monotone m-correlation; Heat's m-modulation
               is monotone-smooth). Per-fidelity normalization handles the scale; what
               remains is the m-basis expressivity gap.
  Category:    FAMILY_PDE_SPECIALIZATION_ASYMMETRY (Heat-good / Poisson-broken — exact
               inverse of fno_mf_stack)
  Suggested fix: within-family levers that have NOT been tested:
                 (a) K=10→20 (paper config); B-MLP hidden width 64→128.
                 (b) Replace MLP basis with neural ODE basis (per IFC paper) — costly at
                     smoke time but available in full_config.json.
                 (c) The LF→HF two-stage transfer schedule landed in cycle-007 H2
                     (be36cba) — currently sitting in fno_coregionalization/smoke_eval.py
                     and was the H2 schedule, not yet evaluated on Poisson since the
                     constructor was broken when the schedule landed.

transolver_residual / ifc_poisson
  Status:      PASS but 44.16× over bar — catastrophic
  nRMSE:       2.5923
  Category:    BACKBONE_INDUCTIVE_BIAS_MISMATCH + POISSON_VALUE_SCALE_COLLAPSE residual

v9_baseline / ifc_poisson
  Status:      reference (frozen)
  nRMSE:       18.50
  Category:    POISSON_VALUE_SCALE_COLLAPSE (carry-over F1)
```

---

## Failure Distribution

Per-cell categorization, 12 actionable cells (excluding v9_baseline; including mf_fno_transfer_bar as actionable for the smoke side only):

| Category                              | Cells | Composite-gap weight                                                                                       |
|---                                    |---:   |---                                                                                                          |
| CAPACITY_PARETO                       | 1     | **Highest single-lever** — `fno_coregionalization` × ifc_heat (winner, +21% over bar) is the 12.6× dominant contributor in log-space. Closing it under smoke budget: K=10→20, b_hidden→128, n_blocks 4→6, narrower epoch budget. |
| NEAR_PARITY_INCREMENTAL               | 1     | Medium — `fno_mf_stack` × ifc_poisson at +1.5% over bar. Small absolute gap (0.0009) but small log contribution; harder to lever further without curriculum/transfer recipe. |
| TRANSFER_SIGNAL_UNUSED                | 1     | Medium — `fno_coreg_residual` × ifc_heat (no LF-pretrain stage); inheritable from fno_coregionalization's H2 schedule. |
| RECIPE_DATASET_NONPORTABILITY         | 1     | Already-explored failure mode — `fno_coreg_residual` × ifc_poisson, tried in cycle-007 H2, REVERT.        |
| BAR_UNDERTRAINING_VS_CACHE            | 2     | Low — does not help composite; tightens bar number, may RAISE the dethrone target.                        |
| FAMILY_PDE_SPECIALIZATION_ASYMMETRY   | 2     | High structural — `fno_coregionalization` × ifc_poisson (0.7501) and `fno_mf_stack` × ifc_heat (0.0999). Each family is a single-PDE specialist; no current family wins both. |
| BACKBONE_INDUCTIVE_BIAS_MISMATCH      | 4     | Low — transolver_* family in both columns; orthogonal inductive bias.                                      |

**Dominant failure mode by composite-gap log-weight:** `CAPACITY_PARETO` on `fno_coregionalization` × `ifc_heat`. Heat alone contributes **12.6× more** to the composite-gap-to-bar than Poisson in log-space (heat +0.191 vs poisson +0.015). Bringing heat from 0.01551 → 0.01022 (the symmetric −10% target) is the single highest-EV lever on the leaderboard.

**Dominant absolute-nRMSE failure:** `FAMILY_PDE_SPECIALIZATION_ASYMMETRY` on `fno_coregionalization` × `ifc_poisson` at 0.7501. Fixing this would make fno_coregionalization a unified family, but it is NOT mechanically required to dethrone the bar (since `fno_mf_stack` already owns Poisson at near-parity).

---

## Cross-Cycle Comparison (005 → 006 → 007 → 008)

| Metric / cell                                 | c005 H2  | c006 H1 (exp/8)   | c007 R0  | c007 H1 (=c008 base) | Trend                                                |
|---                                            |---:      |---:               |---:      |---:                  |---                                                  |
| composite_nRMSE                               | 0.029357 | 0.041963          | 0.039578 | 0.030408             | aspirational → reproducible (no longer dirty-tree dependent) |
| `fno_coregionalization` × ifc_heat            | 0.01551  | CRASH             | CRASH    | **0.01551**          | recovered to cycle-005 cache exactly (delta +0.00007%)|
| `fno_coregionalization` × ifc_poisson         | 0.77562  | CRASH             | CRASH    | **0.75015**          | recovered to within seed; STILL 12.6× over bar     |
| `fno_coreg_residual` × ifc_heat               | 0.03519  | 0.03059 (−13%)    | 0.02628  | 0.02628              | improving — K=20/b_hidden=128 banked            |
| `fno_coreg_residual` × ifc_poisson            | 0.05556  | 0.05756 (+3.6%)   | 0.07419  | 0.07419              | regressing vs c005 — recipe-overfit-across-datasets (3rd cycle on the same lever) |
| `fno_mf_stack` × ifc_poisson                  | 0.08829  | 0.05961           | 0.05961  | 0.05961              | stable at near-bar parity (banked c002 H4)         |
| `mf_fno_transfer_bar` × ifc_heat (smoke)      | n/a      | 0.03317           | 0.03317  | 0.03317              | stable, ~10 s train_seconds — undertrained        |
| `mf_fno_transfer_bar` × ifc_poisson (smoke)   | n/a      | 0.08333           | 0.08333  | 0.08333              | stable, undertrained                                |

**Improvements c005 → c008:**
- `fno_coreg_residual` × ifc_heat 0.03519 → 0.02628 (−25.3%) — K=20/b_hidden=128 architectural bump from cycle-006 H1 has paid off.
- `fno_coregionalization` re-runnable from committed tree — silent-regression-cache-layer pattern resolved via constructor fix.
- Reproducible best moved from aspirational unreproducible 0.029357 to reproducible 0.030408 (the H1 constructor fix recovered cycle-005's heat cache exactly).

**Regressions c005 → c008:**
- `fno_coreg_residual` × ifc_poisson 0.05556 → 0.07419 (+33.5%) — heat-tuned recipe now shared across both PDEs in committed tree; the c007 H2 dispatch attempt to decouple was empirically REVERTed.

**New failures since c005:** none new. The `modes_h` constructor signature failure was first hit in c006 H1 and was repaired in c007 H1.

**Three formal REVERTs on the cross-architecture-recipe-portability lever (callout #4):**

1. **cycle-003 H1** — port MFRNP Poisson5 recipe (HF=2.0/LF=0.25) from `fno_mf_stack` → `fno_coreg_residual`. Result: ifc_heat unchanged 0.02630 (uniform weights — heat path benign); ifc_poisson regressed 0.07416 → 0.27287 (+268%). FIRST genuine REVERT in project history. The cycle-003 framing "the MFRNP recipe is PDE-class-bound (elliptic), not backbone-bound" was REFUTED; **the recipe is backbone-coupled**.

2. **cycle-006 H1** — MFRNP recipe transplant from `fno_coreg_residual` → `fno_mf_stack`. Result: cross-architecture recipe transfer failed. REVERT.

3. **cycle-007 H2** — per-dataset MFRNP recipe dispatch WITHIN `fno_coreg_residual` (heat keeps current, poisson reverts to MFRNP). Result: heat invariance VIOLATED (0.02628 → 0.03487, +32.7%; the dispatch was supposed to be heat-invariant by construction since the gate excluded 'heat' tokens, but fresh-train variance + shared training infrastructure swamped the invariance). REVERT. The Strategist "Heat invariant by construction" claim was falsified at 6.5× the noise band.

**Lesson:** MFRNP-style HF/LF loss reweighting is BOTH backbone-coupled AND dataset-entangled even within the same family. **Recipe-dispatch as a lever for closing the Poisson gap on fno_coreg_residual should not be tried a fourth time.** The remaining unexplored degree of freedom for that family is best-of-N seeds with a frozen heat-seed, NOT a recipe change.

---

## Recommended Interventions (ranked, all within `models/**`)

### 1. Capacity / config bump on `fno_coregionalization` × ifc_heat — `CAPACITY_PARETO`

- **Files:** `models/fno_coregionalization/smoke_eval.py` (`SMOKE_DEFAULTS` block); possibly `models/fno_coregionalization/model.py` if anisotropic K-routing needs touching.
- **Change shape:** bump `K=10→20` (paper config from `full_config.json`); `b_hidden=64→128`; `n_blocks=4→6`; `hidden_channels` (verify whether anisotropic-mode constructor exposes this); narrow `epochs=200→100–150` if wall-time budget tight.
- **Expected impact (within mutable surfaces):** target heat 0.01551 → ~0.012 (paper-K-config implied), composite → ~0.027. **Closes the 1.21× heat-bar gap that dominates the composite by 12.6× log-weight.** Single-PR scope.
- **Risk:** capacity bump could ALSO move Poisson on the same family from 0.7501 → smaller — neutral for composite (Poisson winner is fno_mf_stack), positive for taxonomy (collapse FAMILY_PDE_SPECIALIZATION_ASYMMETRY).
- **Kill-switch:** existing heat kill-switch (0.0194) — must verify a capacity bump does not break it.

### 2. NEW lever — LF→HF curriculum + coregionalization head on a single HF FNO (callout #5)

The cycle-007 H2 schedule (two-stage LF-pretrain → LF+HF fine-tune) currently sits in `models/fno_coregionalization/smoke_eval.py` and has **never been evaluated** because the constructor was broken when the schedule landed; constructor was fixed in H1 (cycle-008 baseline state) but the H2 schedule was not re-bound to the repaired constructor. Three NEW transfer-learning ideas from the human-injected directive that are NOT yet tested in cycle-008 state:

- **(a) Re-bind H2 LF→HF two-stage schedule to the repaired `fno_coregionalization` constructor.** The schedule is committed code on the parent branch but the H1 commit reverted to a one-stage train when fixing the constructor. Net: H1 = constructor fix WITHOUT the H2 transfer schedule. Re-applying the schedule on top of H1 is a one-PR addition that has been blocked since c007.
  - Files: `models/fno_coregionalization/smoke_eval.py` (re-wire `pretrain_frac` arg + 2-stage optimizer/scheduler reset).
  - Expected impact: H2 was projected at heat ≈ 0.018 (−0.0068 composite) on the residual family; on the coregionalization family with the proper constructor it could move heat further toward bar (0.01281).

- **(b) Single full-resolution HF FNO conditioned on coregionalization-m basis (NEW).** Currently the coregionalization architecture is `f(x,m) = sum_k B_k(m) * h_k(x)` where `h` comes from an FNO trunk. The proposed reshape: feed `B(m)` as a *conditioning channel* into a single full-resolution HF FNO rather than as an outer product over latents. Concretely, broadcast `B(m) ∈ R^K` to spatial dimensions and concatenate with the FNO input, then a single HF FNO outputs the prediction. This is a structural change that decouples m-modulation from the FNO trunk and lets the full FNO capacity be reused per-m.
  - Files: NEW family directory `models/fno_coreg_conditioned/` (sibling, per project rule "do not delete or rename existing model families"); copy from fno_coregionalization as template.
  - Expected impact: speculative; depends on whether m-conditioned FNO matches single-m FNO capacity. If it does, this is a candidate single-family answer (good on both Heat AND Poisson, addressing FAMILY_PDE_SPECIALIZATION_ASYMMETRY).
  - Note: this is a NEW family, not a fix to fno_coregionalization. Project rule allows additions in `models/<new_family>/`.

- **(c) Curriculum LF→stack→HF-head (NEW).** Three-stage training: Stage 1 LF-only pretrain of per-fidelity FNOs in `fno_mf_stack` style (Poisson-tuned recipe); Stage 2 freeze LF stack, train HF FNO residual; Stage 3 unfreeze and add coregionalization-residual head from `fno_coreg_residual` for fine-grained m-modulation. Effectively a "compose two specialists then refine with the basis head" curriculum. This addresses the F5 INVERSE_COMPLEMENTARY_FAMILIES from cycle-002 by training the union of the two inductive biases in stages rather than as a hybrid architecture.
  - Files: probably `models/fno_coreg_residual/smoke_eval.py` (the family already composes residual + coregionalization; a multi-stage schedule is the change).
  - Expected impact: speculative; main risk is checkpoint-resume contamination (cycle-003 incident) — the staged training needs a recipe-fingerprint checkpoint guard.

### 3. Capacity bump on `mf_fno_transfer_bar` × ifc_heat (BAR side) — taxonomy hygiene, NOT composite

- **Files:** `models/mf_fno_transfer_bar/smoke_eval.py` `SMOKE_DEFAULTS`.
- **Change shape:** bring smoke training closer to parallel-bench numbers (epochs, hidden, batch).
- **Impact:** does NOT help our composite directly; raises the bar number we must beat. **Useful for honest comparison** (smoke-bar ≈ parallel-bench-bar) but a 10% dethrone target is then computed against the higher bar. **Tactically defer until intervention 1 lands.**

### 4. Within-family attack on `fno_coregionalization` × ifc_poisson (the 0.7501 cell, callout #2)

The intrinsic Poisson failure of `fno_coregionalization` has persisted since cycle-001. Within-family levers NOT yet tested:
- (a) bump K=10→20 (covered by intervention 1).
- (b) neural ODE basis (per IFC paper, declared in `full_config.json`) — costly at smoke wall-time; would need an H100 partition and budget exception.
- (c) per-PDE basis routing (e.g., wider `b_hidden` only on Poisson) — but this is the same CROSS_ARCHITECTURE_RECIPE_NONPORTABILITY pattern that has REVERTed 3 times. Do not attempt without best-of-N seed control.

**Verdict (callout #2):** the 0.7501 cell IS addressable by anisotropic-modes head or capacity bumps WITHIN the family (intervention 1), but the gap from 0.7501 to bar 0.0587 (12.6×) is large enough that getting there in one cycle is unrealistic. A different family (intervention 2b — single FNO conditioned on the basis) is the more promising path for making fno_coregionalization-family a unified two-PDE solution.

### 5. fno_mf_stack capacity bump on ifc_poisson — `NEAR_PARITY_INCREMENTAL`

- **Files:** `models/fno_mf_stack/smoke_eval.py` `SMOKE_DEFAULTS`.
- **Change shape:** bump `hidden=32→64` and/or `n_blocks=3→4` under wall-time budget.
- **Expected impact:** Poisson 0.05961 → 0.052–0.055 (closing the +1.5% gap to bar's 0.0587 from above). Composite secondary lever — Poisson contributes 12.6× less log-weight than Heat.

---

## Constraint Re-statement on Cross-Architecture Recipe Portability (callout #4)

**Three formal REVERTs (cycle-003 H1, cycle-006 H1, cycle-007 H2) all on MFRNP-style loss-reweighting recipe transfer.** The lesson is:

- The MFRNP HF=2.0/LF=0.25 recipe is **backbone-coupled** (refuted the cycle-003 framing that it was PDE-class-bound).
- The recipe is **dataset-entangled even within the same family** — cycle-007 H2 "heat invariant by construction" was empirically falsified due to fresh-train variance + shared training infra.
- **Conclusion for cycle-008 Strategist:** any new hypothesis that adds an MFRNP-style loss reweighting (cross-family OR per-dataset-within-family) must either:
  (i) declare a kill-switch on heat invariance, AND
  (ii) include best-of-N (N≥2) seed control with the heat seed frozen across treatment/control.
  Otherwise, the prior of REVERT is 3/3.

---

## Constraint Re-statement on Residual Families: Architecture vs Recipe (callout #3)

**`fno_coreg_residual` (Heat 0.02628 #2, Poisson 0.07419 #2):**
- Architecture choice (K=20/b_hidden=128 banked c006) has paid off on Heat (−25.3% vs c005) and explains the heat #2 position.
- Training recipe choice has REVERTed 3 cycles (c003, c006, c007) — per-dataset MFRNP dispatch breaks heat invariance.
- **Verdict:** this family is **architecture-improvable, recipe-stuck**. The remaining levers are LF→HF transfer schedule (intervention 2a-style, not yet applied to this family) and capacity bumps; loss-recipe levers should NOT be retried.

**`fno_mf_stack` (Heat 0.09995 #4, Poisson 0.05961 #1):**
- Architecture choice (smoke-defaults bumped to mirror full_config in c002 H4) has paid off on Poisson (5.86× improvement from c001 H2's 0.7725).
- Training recipe (HF=2.0/LF=0.25 gated to poisson) is paper-canonical and verbatim from MFRNP Poisson5.
- **Verdict:** this family is **at-recipe-parity, capacity-marginal-improvable**. The remaining lever is capacity (NEAR_PARITY_INCREMENTAL); a Heat fix is not in the architecture's reach (inductive bias mismatch).

**Synthesis:** both residual families are constrained more by **architecture choice** than by training recipe at this point — recipe space has been thoroughly explored (and is structurally non-portable). The remaining single-family lever is capacity and/or transfer schedule.

---

## Failure Taxonomy Update

No new categories. Stable taxonomy across c005–c008:

| Category                              | First observed   | Cells in c008 |
|---                                    |---               |---:           |
| POISSON_VALUE_SCALE_COLLAPSE (F1)     | cycle-000        | 0 (resolved everywhere via per-fidelity normalization)  |
| BACKBONE_INDUCTIVE_BIAS_MISMATCH (F2) | cycle-000        | 4 (transolver_* and v9 — orthogonal direction)         |
| SMOKE_DEFAULT_UNDER_CAPACITY (F4)     | cycle-001 H2     | 0 (resolved in c002 H4)                                |
| INVERSE_COMPLEMENTARY_FAMILIES (F5)   | cycle-001 H1/H2  | 2 (still characterizes fno_coreg vs fno_mf_stack)      |
| COMMITTED_TREE_BROKEN                 | cycle-007 R0     | 0 (resolved in c007 H1)                                |
| CROSS_ARCHITECTURE_RECIPE_NONPORTABILITY | cycle-003 H1  | 1 (latent — `fno_coreg_residual`/Poisson; 3 reverts)   |
| RECIPE_DATASET_NONPORTABILITY (within family) | cycle-007 H2 | 1 (latent — `fno_coreg_residual`/Poisson; 1 revert)   |
| FAMILY_PDE_SPECIALIZATION_ASYMMETRY   | cycle-001 (= F5) | 2 (`fno_coregionalization`/Poisson 0.7501; `fno_mf_stack`/Heat 0.09995) |
| CAPACITY_PARETO                       | cycle-006 standup| 1 (`fno_coregionalization`/Heat — leaderboard winner, +21% over bar) |
| NEAR_PARITY_INCREMENTAL               | cycle-008        | 1 (`fno_mf_stack`/Poisson +1.5% over bar)              |
| BAR_UNDERTRAINING_VS_CACHE            | cycle-005 R0     | 2 (`mf_fno_transfer_bar` both datasets, smoke side)    |
| TRANSFER_SIGNAL_UNUSED                | cycle-007 R1     | 1 (`fno_coreg_residual`/Heat — H2 schedule not applied)|

NEW this cycle: **NEAR_PARITY_INCREMENTAL** — promoted from latent to active because `fno_mf_stack`/Poisson is now at 1.015× over bar (was 1.50× in c002 H4 at 0.0883). The category captures cells where the family is at parity and the marginal gap-closer is not a single intervention but a stack of compounding capacity/curriculum tweaks.

---

## Related notes

- [[failure-analysis-cycle-007]] — prior R1 baseline framing; 0.029357 → 0.030408 discrepancy decomposition.
- [[cycle-007-summary]] — REVERT_BOOKKEEPING_KEEP_INTENT framing for H1 (composite genuinely improved −23.17%); H2 substantive REVERT (heat invariance falsified).
- [[failure-analysis-cycle-003]] — first genuine REVERT (cross-architecture recipe portability disproof).
- [[cycle-003-summary]] — MFRNP-recipe-is-backbone-coupled finding.
- [[cycle-006-summary]] — second cross-architecture recipe transfer failure (REVERT).
- [[patterns]] §"silent-regression-cache-layer-masks-uncommitted-load-bearing-state" — fully resolved by cycle-008 reproducible baseline.

## Tags

`failure-analysis`, `cycle-008`, `baseline`, `reproducible-best-recovered`,
`capacity-pareto-heat-dominant`, `family-pde-specialization-asymmetry`,
`cross-architecture-recipe-nonportability-3of3-revert`,
`recipe-dataset-nonportability`, `fno_coregionalization-poisson-intrinsic`,
`bar-undertraining-smoke-vs-parallel-bench`, `lf-hf-transfer-h2-schedule-not-rebound`,
`new-lever-coreg-m-conditioned-fno`, `new-lever-curriculum-lf-stack-hf-head`
