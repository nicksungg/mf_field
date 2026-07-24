# Failure Analysis — Cycle 007 R0 (Baseline)

## Summary
- **Instances**: 2 datasets × 7 families = 14 (family, dataset) cells; composite **0.039578**, geomean of best-per-dataset (ifc_heat 0.02628, ifc_poisson 0.05961). 2 cells are hard crashes (`fno_coregionalization`).
- **Dominant failure mode**: **COMMITTED_TREE_BROKEN** (`fno_coregionalization` constructor mismatch). Single-fix expected delta ≈ −0.0091 composite (≈23% relative), the largest single lever available within mutable surfaces.
- **Comparison with prior cycle**: Regression vs cycle-005 H2 (0.029357). Two contributors: (i) cycle-005's heat winner (`fno_coregionalization` @ 0.01551) is no longer runnable on the current committed code-hash, and (ii) `fno_coreg_residual` Poisson drifted up (0.05556 → 0.07419, +33.5%) while its heat improved (0.03519 → 0.02628, −25.3%) — a classic ARCHITECTURE_OVERFIT trade-off across the two PDEs.

Reproducible-baseline note: cycle-005 H2 produced 0.029357 with cached entries that match a **different code hash** (`9528aeef4a5a`, `9be21a0f9ce9`). Those cache files are still on disk but no longer key-resolve against current `models/<family>/` source. The CEO already flagged this; 0.029357 is treated as aspirational, not as a regression bar.

---

## Per-Dataset Gap Analysis

### ifc_heat (best in family → bar 0.0128 → paper 0.074)

| Family                       | Test nRMSE | × bar | × paper | Cache hash    | Verdict |
|------------------------------|------------|-------|---------|---------------|---------|
| fno_coreg_residual           | 0.02628    | 2.05× | 0.36×   | d1967ad6e54c  | #1 in current tree, 2.05× off bar |
| mf_fno_transfer_bar          | 0.03317    | 2.59× | 0.45×   | 94ae4f19ac48  | undertrained — only ~10.5s train_seconds (vs 477s for fno_coreg_residual) |
| fno_mf_stack                 | 0.09995    | 7.81× | 1.35×   | e9476d31380a  | small width (hidden=32, 2.28M params); architecture is undersized for heat |
| transolver_residual          | 0.11456    | 8.95× | 1.55×   | 41252fe50556  | best_val 0.225 → wide test gap; train_seconds ≈ 0 (eval-only) |
| v9_baseline (FIXED)          | 0.14883    | 11.6× | 2.01×   | 48160028a4cb  | reference baseline — not mutable |
| transolver_attention_fusion  | 0.14923    | 11.7× | 2.02×   | 921abb6f1439  | best_val 0.034 but test 0.149 — huge train→test gap |
| fno_coregionalization        | CRASH      | —     | —       | 4235deb6c27c  | TypeError: `modes_h` kwarg on constructor |

Closest to bar: `fno_coreg_residual` at 2.05× the bar (gap 0.01348). Furthest: the two transolver families and `v9_baseline` (~9–12×). The transolver families have low best_val on heat but blow out at test — suggests a train-protocol or evaluation-protocol mismatch, not a pure architectural deficit. **Hold-out**: cycle-005's `fno_coregionalization` heat result was 0.01551 — that family, if reinstated, would already beat the bar on heat.

### ifc_poisson (best in family → bar 0.0587 → paper 0.036)

| Family                       | Test nRMSE | × bar  | × paper | Cache hash    | Verdict |
|------------------------------|------------|--------|---------|---------------|---------|
| fno_mf_stack                 | 0.05961    | 1.015× | 1.66×   | e9476d31380a  | #1; **near parity with bar**; uses HF=2.0/LF=0.25 MFRNP recipe |
| fno_coreg_residual           | 0.07419    | 1.26×  | 2.06×   | d1967ad6e54c  | **regressed +33.5% from cycle-005**; same recipe that helped heat hurt poisson |
| mf_fno_transfer_bar          | 0.08333    | 1.42×  | 2.31×   | 94ae4f19ac48  | undertrained (10s train) |
| transolver_attention_fusion  | 0.38181    | 6.51×  | 10.6×   | 921abb6f1439  | best_val 0.197 → test 0.382 — large gap |
| transolver_residual          | 2.59235    | 44.2×  | 72.0×   | 41252fe50556  | **catastrophic cliff** vs same family's heat 0.11 |
| transolver_attention_fusion  | (above)    | —      | —       | —             | — |
| v9_baseline (FIXED)          | 18.50      | —      | —       | 48160028a4cb  | reference baseline — not mutable |
| fno_coregionalization        | CRASH      | —      | —       | 4235deb6c27c  | constructor mismatch |

Closest to bar: `fno_mf_stack` at 0.05961 — essentially at the bar (1.5% over). Furthest among in-tree families: `transolver_residual` (44× the bar). The Poisson side is the easier "almost there" frontier; small wins compound.

---

## Per-Instance Classification

Format: Status / Stage / Failure / Root cause / Category / Suggested intervention site.

### fno_coregionalization × ifc_heat
- **Status**: ERROR (TypeError, exit=1, 38s wall)
- **Stage**: model construction
- **Failure**: `FNOCoregionalization.__init__()` does not accept `modes_h`, `modes_w`, or `grid` kwargs at `models/fno_coregionalization/smoke_eval.py:265`
- **Root cause**: `models/fno_coregionalization/model.py` declares `__init__(... modes: int, grid_size: int, b_hidden: int)` (single isotropic `modes` and scalar `grid_size`), but the smoke harness was extended to compute and pass anisotropic `(modes_h, modes_w)` along with a tuple `grid`. The two surfaces diverged. CEO note (cycle-006) confirms a dirty `model.py` was the load-bearing signature; that change was lost in a hard reset.
- **Category**: **COMMITTED_TREE_BROKEN**
- **Suggested fix**: bring `models/fno_coregionalization/model.py` constructor and inner FNO blocks to the anisotropic signature used by `smoke_eval.py` (i.e. accept `modes_h, modes_w, grid` and propagate to `SpectralConv2d`/`FNOBlock`). One PR's worth of editing.

### fno_coregionalization × ifc_poisson
- Same as above — same constructor, same cache hash, same crash.
- **Category**: **COMMITTED_TREE_BROKEN**

### fno_coreg_residual × ifc_heat
- **Status**: PASS (best in tree at 0.02628; gap to bar 0.0128 = 2.05×)
- **Stage**: training/inference (no errors)
- **Failure**: 2.05× off bar despite #1 ranking; cycle-005 cache for this family was at 0.03519, so a real improvement has been banked, but the bar requires a further ~2× reduction.
- **Root cause** (behavioural): joint training of LF and HF fidelities with no dedicated LF-pretrain → HF-finetune stage; the "bar" family (`mf_fno_transfer_bar`) uses transfer-learning pretrain, this one does not. Also, the architecture's recipe is shared with Poisson, where the same recipe regresses (carry-over A).
- **Category**: **TRANSFER_SIGNAL_UNUSED** (primary), with secondary **LOSS_RECIPE_GAP**
- **Suggested fix**: add an optional LF→HF two-stage schedule inside `models/fno_coreg_residual/smoke_eval.py` (and the necessary `model.py` plumbing if needed), keeping the basis-head residual on top. Mirrors the be36cba H2 schedule attempted on `fno_coregionalization`.

### fno_coreg_residual × ifc_poisson
- **Status**: PASS (0.07419) but **REGRESSED** vs cycle-005's 0.05556 by +33.5%
- **Stage**: training (loss/recipe)
- **Failure**: same architecture+recipe that improved heat made Poisson worse.
- **Root cause** (behavioural): the recipe knob that helped heat (basis-head/loss-weighting/decoder configuration tuned on heat) is over-shared across datasets. The `full_config.json` does expose a Poisson-only `_poisson_loss_knob` (HF=2.0 / LF=0.25 MFRNP recipe) but the smoke harness does not opt in by dataset, so Poisson runs with the same loss weights as heat. Cycle-006 found that the MFRNP weight recipe "did not transfer" — i.e. needs to be **architecture-decoupled per dataset**, not blanket-applied.
- **Category**: **ARCHITECTURE_OVERFIT** (or, more precisely, recipe-overfit-across-datasets); secondarily **LOSS_RECIPE_GAP**
- **Suggested fix**: in `models/fno_coreg_residual/smoke_eval.py`, gate hyperparameter overrides on `args.dataset_name` (heat keeps current K/b_hidden/loss-weights; Poisson opts into the `_poisson_loss_knob` and/or a smaller basis head). Not a new family, not a new architecture — a dataset-conditional recipe.

### mf_fno_transfer_bar × ifc_heat
- **Status**: PASS (0.03317) — 2.59× off bar despite this family supposedly representing the bar
- **Stage**: training (recipe)
- **Failure**: `train_seconds` ≈ 10.5s, vs ≥150s for the cohort. `n_params` = 4.74M.
- **Root cause** (behavioural): the smoke recipe is undertrained — epoch budget or LF-pretrain length is too small to realise the architecture's known potential (0.0128 on heat at the published recipe). The architecture itself implements the LF→HF transfer mechanism cleanly (see `mf_mechanism: transfer_learning_pretrain_LF_finetune_HF` in notes).
- **Category**: **LOSS_RECIPE_GAP**
- **Suggested fix**: lengthen `epochs` and/or LF-pretrain ratio in `models/mf_fno_transfer_bar/smoke_eval.py`. If a cap on smoke wall-time prevents this, add an explicit `full_config.json` and have the harness use it for this family.

### mf_fno_transfer_bar × ifc_poisson
- **Status**: PASS (0.08333) — 1.42× off bar
- Same root cause as heat: 10.3s of training. Bar-family architecture, undertrained recipe.
- **Category**: **LOSS_RECIPE_GAP**

### fno_mf_stack × ifc_heat
- **Status**: PASS (0.09995) — 7.81× off bar; #3 on heat
- **Stage**: training
- **Failure**: architecture has hidden=32, 2.28M params — smaller than `fno_coreg_residual` (9.12M) and trained on CPU (1724s).
- **Root cause** (behavioural): the family's width and the device (CPU) cap convergence; same family runs at 0.05961 on Poisson because Poisson is easier here, but heat needs more spectral capacity.
- **Category**: **ARCHITECTURE_UNDERFIT** for heat (capacity); **CAPACITY_PARETO** also applies — adding width may help heat but cost device-fit on the CPU path
- **Suggested fix**: bump `hidden_channels` and/or modes, OR move training to GPU. Same `models/fno_mf_stack/smoke_eval.py`.

### fno_mf_stack × ifc_poisson
- **Status**: PASS (0.05961) — **#1 on Poisson, 1.5% over bar**
- This is the strongest single-cell result in the cohort. No intervention needed.
- **Category**: PASS — at bar parity
- **Suggested fix**: leave as is; protect the cache hash by avoiding recipe drift.

### transolver_residual × ifc_heat
- **Status**: PASS (0.11456) but `train_seconds ≈ 0`, eval_seconds 121s — degenerate
- **Stage**: training (the family is cache-only / eval-only in current state)
- **Failure**: best_val 0.225 → test 0.115 — the model never actually trained in the current cache (train_seconds is 1.9e-6).
- **Root cause** (behavioural): the cache hash 41252fe50556 was produced by a path that bypassed training. Architecture (Transolver) on a single-resolution residual stack does not exploit multi-fidelity structure.
- **Category**: **LOSS_RECIPE_GAP** (no training happened in the cached run) and **ARCHITECTURE_OVERFIT** for the Poisson cliff
- **Suggested fix**: re-enable real training in `models/transolver_residual/smoke_eval.py` (or invalidate the degenerate cache). If train_seconds≈0 is intentional (model is frozen), then this family has no leverage on the composite and can be deprioritised.

### transolver_residual × ifc_poisson
- **Status**: PASS (2.5923) — **44× off bar; cliff vs same family's 0.115 on heat**
- **Stage**: training/architecture
- **Failure**: best_val 0.497 on Poisson vs 0.225 on heat — the family's geometry-of-attention prior is dataset-specific.
- **Root cause** (behavioural): the residual-stack Transolver hyperparameters tuned for heat-like smooth fields do not generalise to Poisson's sharper local response.
- **Category**: **ARCHITECTURE_OVERFIT** (distinctive cliff)
- **Suggested fix**: dataset-conditional config in `models/transolver_residual/smoke_eval.py` (lower attention head count or stronger inductive bias for Poisson) — same intervention pattern as `fno_coreg_residual` decoupling.

### transolver_attention_fusion × ifc_heat
- **Status**: PASS (0.14923) but **best_val 0.034 → test 0.149** — 4.4× train→test gap
- **Stage**: validation / generalisation
- **Failure**: model fits validation very well but blows out at test
- **Root cause** (behavioural): suggests data-protocol or normalisation drift between val and test paths, or test-time augmentation, or a leak in val that the test set doesn't have. Not a pure architectural failure.
- **Category**: **LOSS_RECIPE_GAP** (most likely a normalisation/eval-protocol mismatch in the smoke harness)
- **Suggested fix**: audit `models/transolver_attention_fusion/smoke_eval.py` for val-vs-test normalisation symmetry; verify the val split's y-scaler is also applied (or correctly inverted) on test.

### transolver_attention_fusion × ifc_poisson
- **Status**: PASS (0.38181); best_val 0.197 → test 0.382, similar 2× gap pattern
- **Category**: **LOSS_RECIPE_GAP** (same audit as heat)

### v9_baseline × {ifc_heat, ifc_poisson}
- **Not classified** — fixed reference baseline; `eval/`, `checkpoints/` live outside the mutable surface `models/**`. Carries no Builder-actionable signal.

---

## Failure Distribution

Counting (family, dataset) cells inside the mutable surface only (exclude `v9_baseline`'s 2 cells = 12 actionable cells):

| Category                       | Count | Composite-gap weight |
|--------------------------------|-------|----------------------|
| COMMITTED_TREE_BROKEN          | 2     | **Highest** — single fix → composite 0.0397 → ~0.0304 (≈−0.0091, ~−23%) |
| LOSS_RECIPE_GAP                | 5     | Medium — covers mf_fno_transfer_bar both, transolver_attention_fusion both, transolver_residual heat. Best case (closing the bar undertraining on both `mf_fno_transfer_bar` datasets) → composite roughly 0.0274 |
| ARCHITECTURE_OVERFIT           | 3     | Medium — fno_coreg_residual Poisson, transolver_residual Poisson cliff. Closing the fno_coreg_residual regression alone (back to 0.05556) → composite 0.0397 → 0.0382 (~−0.0015) |
| TRANSFER_SIGNAL_UNUSED         | 1     | Medium — fno_coreg_residual heat could approach the bar by adding LF→HF pretraining |
| ARCHITECTURE_UNDERFIT          | 1     | Low — fno_mf_stack heat (CPU-bound, low width) |
| CAPACITY_PARETO                | 0 (latent in fno_mf_stack heat) | Low |
| BAR_PARITY_NEW_FAMILY_NEEDED   | 0     | None observed — no need for a brand-new family yet; the bar is reachable by repairing/configuring existing families |

**Dominant failure mode by composite impact**: **COMMITTED_TREE_BROKEN**. By cell count it's only 2/12, but the impact dominates because it removes the cycle-005 heat winner (0.01551) from the leaderboard. A one-PR constructor repair closes ~57% of the gap between current baseline (0.039578) and the aspirational best (0.029357) on its own.

---

## Cross-Cycle Comparison (cycle-005 → cycle-006 → cycle-007)

| Metric / cell                                | c005-H2  | c006-H1 (exp/8) | c007-R0  | Trend |
|----------------------------------------------|----------|------------------|----------|-------|
| composite_nRMSE                              | 0.029357 | 0.041963         | 0.039578 | regression vs c005, slight improvement vs c006 |
| fno_coregionalization × ifc_heat             | 0.01551  | CRASH            | CRASH    | regressing → broken |
| fno_coreg_residual × ifc_heat                | 0.03519  | 0.03059 (-13%)   | 0.02628 (-25% vs c005) | **improving** |
| fno_coreg_residual × ifc_poisson             | 0.05556  | 0.05756 (+3.6%)  | 0.07419 (+33% vs c005) | **regressing** |
| fno_mf_stack × ifc_poisson                   | n/a      | 0.05961          | 0.05961  | stable at bar parity |
| mf_fno_transfer_bar × ifc_heat               | n/a      | 0.03317          | 0.03317  | stable but undertrained |
| mf_fno_transfer_bar × ifc_poisson            | n/a      | 0.08333          | 0.08333  | stable but undertrained |

**Improvements (c005 → c007)**:
- `fno_coreg_residual` heat down 25.3% — the H2 transfer-schedule line of work has paid off on heat.

**Regressions (c005 → c007)**:
- `fno_coregionalization` not runnable at all (the cycle-005 heat winner is dark — the cache files exist on disk but no longer key-match the current code hash).
- `fno_coreg_residual` poisson up 33.5% — the same recipe path that helped heat hurt Poisson.

**New failures**:
- The `modes_h` constructor mismatch was first hit in cycle-006 H1 and has not been repaired. It is now structurally embedded in the committed tree on experiment/7 (commit be36cba added the two-stage transfer schedule but did not update the constructor surface).

**Carry-overs addressed in this cycle**: none — the H1 MFRNP loss reweighting was reverted in c006 and was not reinstated as a dataset-conditional knob.

---

## Recommended Interventions (ranked by expected composite gain)

### 1. **Repair `fno_coregionalization` constructor signature** [COMMITTED_TREE_BROKEN]
- **Files**: `models/fno_coregionalization/model.py` (primary). Possibly minor mirror in `models/fno_coregionalization/smoke_eval.py` to keep call-site stable.
- **Change shape**: convert `FNOCoregionalization.__init__(..., modes: int, grid_size: int, ...)` to accept `modes_h: int, modes_w: int, grid: tuple[int,int]` and propagate to the inner `FNOBlock`/`SpectralConv2d` constructors. Type of intervention: **(e) constructor-signature fix**.
- **Expected impact**: composite 0.039578 → ~0.0304 if the family recovers anywhere near its cycle-005 cached 0.01551 on heat (assuming Poisson stays at current 0.05961). Net ≈ **−0.0092 composite**, the single largest expected gain.
- **One-PR scope**: yes — the change is local to `model.py` and (if needed) the call site at `smoke_eval.py:265`.

### 2. **Decouple `fno_coreg_residual` recipe per dataset** [ARCHITECTURE_OVERFIT, carry-over A]
- **Files**: `models/fno_coreg_residual/smoke_eval.py` (gate overrides on `args.dataset_name`). The `_poisson_loss_knob` already exists in `models/fno_coreg_residual/full_config.json` but is never read by the smoke harness.
- **Change shape**: when `args.dataset_name == "ifc_poisson"`, apply HF=2.0 / LF=0.25 (the MFRNP Poisson recipe declared in `full_config.json`) **and** reduce K / b_hidden (or revert to pre-bump values) — i.e. the same architectural width that helps heat shouldn't be forced on Poisson. Type: **(c) recipe/loss change**.
- **Expected impact**: restoring Poisson to ≤ 0.05556 (cycle-005 number) lowers composite to geomean(0.02628, 0.05556) ≈ 0.0382, **−0.0016 composite**. If the per-dataset decoupling lets heat keep improving while Poisson returns to or beats cycle-005, the gain is larger.
- **One-PR scope**: yes — pure config-routing logic in `smoke_eval.py`.

### 3. **Add LF→HF two-stage transfer to `fno_coreg_residual`** [TRANSFER_SIGNAL_UNUSED]
- **Files**: `models/fno_coreg_residual/smoke_eval.py` (add `pretrain_frac` arg and a warmup loop using only LF samples), `models/fno_coreg_residual/model.py` (none expected — the residual stack already supports per-level forward). Type: **(d) transfer-pretraining add-on**.
- **Expected impact**: closes part of the 2.05× gap on heat. If heat reaches 0.018 (still 1.4× over bar), composite → geomean(0.018, current 0.0596) ≈ 0.0328, **−0.0068 composite**. Stackable with #2.
- **One-PR scope**: yes — mirrors the H2 schedule the broken `fno_coregionalization` already declares.

### 4. **Restore real training in `mf_fno_transfer_bar`** [LOSS_RECIPE_GAP]
- **Files**: `models/mf_fno_transfer_bar/smoke_eval.py` (`epochs`, LF-pretrain length) and/or introduce `models/mf_fno_transfer_bar/full_config.json` and have the smoke harness honour it. Type: **(c) recipe change**.
- **Expected impact**: if mf_fno_transfer_bar reaches its published-bar numbers (heat 0.0128, poisson 0.0587), composite = 0.0274 — i.e. the bar itself. But Builder needs to verify smoke wall-time budget allows this. **−0.012 composite** if fully realised, otherwise some fraction.
- **One-PR scope**: yes, modulo budget constraints.

### 5. **Audit val/test normalisation in transolver_attention_fusion** [LOSS_RECIPE_GAP]
- **Files**: `models/transolver_attention_fusion/smoke_eval.py` only.
- **Expected impact**: low — even closing the 4× val/test gap on heat brings the family to ~0.034 on heat, which doesn't dethrone `fno_coreg_residual`. Not on the composite-gain critical path; cosmetic.

---

## Failure Taxonomy Update

Categories used this cycle, with refined definitions for next cycle:

- **COMMITTED_TREE_BROKEN** — a family's source code under `models/<family>/` does not compose; crashes prevent it from contributing to the leaderboard at all. Highest priority because repair is mechanical and recovers cached numbers.
- **ARCHITECTURE_UNDERFIT** — family's architecture (width/depth/modes) is too small for the dataset; closing the gap requires capacity, not recipe.
- **ARCHITECTURE_OVERFIT** — family is competitive on one dataset and degenerate on another with the **same** hyperparameters. Diagnostic signature: the recipe that minimises one dataset's loss measurably increases another's. Resolved by dataset-conditional knobs, not a new architecture.
- **LOSS_RECIPE_GAP** — family architecture is competitive but the training loop is undertrained, mis-weighted, or evaluation-protocol-skewed. Resolved by recipe edits.
- **TRANSFER_SIGNAL_UNUSED** — family trains all fidelities jointly with no LF→HF pretrain; the "bar" uses this mechanism explicitly. Resolved by adding a two-stage schedule.
- **CAPACITY_PARETO** — observed only as a latent risk in `fno_mf_stack` (CPU-bound, low hidden). Not currently the dominant driver; would become relevant if Builder bumps width and convergence-on-CPU starts to bind.
- **BAR_PARITY_NEW_FAMILY_NEEDED** — would apply if no in-tree family architecture could compose the bar's mechanism. **Not observed this cycle** — the bar is reachable by repairing/configuring families already present.

No brand-new categories discovered this cycle. The taxonomy is stable across cycles 005/006/007.
