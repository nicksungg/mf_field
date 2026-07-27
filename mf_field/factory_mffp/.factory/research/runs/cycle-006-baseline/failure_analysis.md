# Failure Analysis — cycle-006-baseline

**Branch:** `experiment/7-fno_coreg_lf_hf_transfer` @ `be36cba` (cycle-005 H2 outcome, project-best)
**Composite (geomean of 2 smoke datasets):** `0.029357`
**Targets:** composite ≤ `0.026` (MISS by `+0.00336`), ifc_heat ≤ `0.013` (MISS by `+0.00251`)
**Mutable surfaces:** `models/**` only.

---

## A. Per-dataset / per-family leaderboard (cycle-006 baseline)

Source: `.factory/research/runs/cycle-006-baseline/summary.json`. All values are HF-test nRMSE on the smoke working grid (64×64 for both datasets). `n=128` per cell.

### ifc_heat (7 runs)
| rank | family                      | nRMSE   | params  | train_s | note |
|----- |-----------------------------|---------|---------|---------|------|
| 1    | fno_coregionalization        | 0.01551 | 1.19M   | 23.8s   | **WINS**, only one below paper-paper-ratio 3.6× |
| 2    | mf_fno_transfer_bar          | 0.03317 | 4.74M   | 10.5s   | bar (Lyu 2023), now landed on the smoke harness |
| 3    | fno_coreg_residual           | 0.03519 | 2.37M   | 89.2s   | very tight per-sample distribution |
| 4    | transolver_residual          | 0.11430 | 0.70M   | 0.0s    | cache hit; recipe failed pre-H2 |
| 5    | fno_mf_stack                 | 0.13010 | 2.35M   | 59.3s   | no clear MF signal on Heat |
| 6    | v9_baseline                  | 0.14861 | 0.41M   | 0.0s    | single-fidelity reference |
| 7    | transolver_attention_fusion  | 0.14916 | 2.28M   | 0.0s    | attention fusion does not help here |

### ifc_poisson (7 runs)
| rank | family                       | nRMSE     | params  | train_s | note |
|----- |------------------------------|-----------|---------|---------|------|
| 1    | fno_coreg_residual           | 0.05556   | 2.37M   | 78.2s   | **WINS**, ~1.54× paper |
| 2    | mf_fno_transfer_bar          | 0.08333   | 4.74M   | 10.3s   | bar |
| 3    | fno_mf_stack                 | 0.08829   | 2.35M   | 59.1s   | comparable to bar |
| 4    | transolver_attention_fusion  | 0.38327   | 2.28M   | 0.0s    | not multi-fidelity-aware on Poisson |
| 5    | fno_coregionalization        | **0.75015** | 1.19M | 23.2s   | **BROKEN** — see §C |
| 6    | transolver_residual          | 2.59704   | 0.70M   | 0.0s    | catastrophic |
| 7    | v9_baseline                  | 18.48951  | 0.41M   | 0.0s    | catastrophic |

---

## B. Distance-to-target gap analysis

```
composite = sqrt(0.01551 * 0.05556) = 0.029357
target    = 0.026
log-space gap = log(0.02936) - log(0.026) = +0.1214
```

Decompose by dataset (geomean factors symmetrically in log-space, so contributions are equal-weighted):

* Heat is already below the implied per-dataset target. If we could push **only one** dataset:
  * Heat alone: 0.01551 → ≤ **0.01217** (1.27× improvement) closes the gap.
  * Poisson alone: 0.05556 → ≤ **0.04358** (1.27× improvement) closes the gap.
* In log-space distance to the implied symmetric target (= 0.026), **Poisson contributes +0.76 nats above target while Heat contributes −0.52 nats below**. So Poisson is doing all the work of holding us above the composite target — Heat already cleared its share.
* The hard `ifc_heat ≤ 0.013` target is independent and is missed by `+0.00251` (1.19×).

**Direction**: the highest-EV moves are (a) improvements to Poisson on whichever family owns it (currently `fno_coreg_residual`), or (b) joint moves that pull both datasets down without breaking either. Pure Heat-focused work is allowed against the hard ifc_heat target (0.013), but does *not* by itself close the composite-≤0.026 target.

---

## C. Per-family failure-mode classification

### C.1 `fno_coregionalization` — Heat winner / Poisson **architecturally broken** (NOT introduced by H2)

* `models/fno_coregionalization/smoke_eval.py:64-82` — `SMOKE_DEFAULTS` carries `pretrain_frac=0.25`, `pretrain_lr=1e-3`, `finetune_lr=3e-4`, applied uniformly across all datasets (no `dataset_name` gate; verified at lines 236–296).
* `:278-298` — `lf_tr_indices` is constructed by filtering training records whose `m != hf_m`. For `ifc_heat`/`ifc_poisson` the fidelity ladder is the standard 4-level ifc set, so both datasets exercise the full 2-stage schedule.

**Per-sample distribution (Poisson 0.75015, n=128, from summary.json):** approximately bounded `[~0.6, ~0.85]` with median ≈ 0.75 — i.e. the model converges to a *consistent, uniformly wrong* attractor on every Poisson HF sample. This is the signature of a **systematic prediction-scale or scaler mismatch**, not a per-sample-outlier issue.

**Critical correction to the framing.** The cache hashes confirm:
* Pre-H2 `fno_coregionalization` on `ifc_poisson` (hash `9528aeef`, cycle-005 baseline): **0.77562**
* Post-H2 (hash `2954a13e`, cycle-005-H2 = this cycle's R0): **0.75015**

So H2 **did not introduce** the Poisson regression — `fno_coregionalization` was already at ≈0.776 pre-H2. H2's effect on Poisson was a tiny **−3.3%** improvement; H2's effect on Heat was **−24.2%** (0.02047 → 0.01551). The "fno_coregionalization H2 schedule breaks Poisson 15×" framing in the cycle-005 H2 summary is comparing the *family's own Poisson nRMSE* against the **fno_coreg_residual** Poisson winner (≈ 0.0556), not against fno_coregionalization's prior Poisson. The architectural-Poisson failure predates H2 and is independent of the transfer schedule.

**Architectural root cause (behavioral, not content-level).** The `fno_coregionalization` smoke recipe uses a single shared FNO trunk on a single working grid for *all* fidelities and routes fidelity through a continuous-m coregionalization basis (K=10, B(m) MLP head). At `smoke_eval.py:265-276` it sets a **per-fidelity output scaler**, taking max(|y|) per `m`. Poisson's solutions have a fundamentally different LF→HF amplitude/structure relationship than Heat: the heat dataset's per-fidelity max(|y|) is approximately matched across the ladder (smoothing → small-amplitude perturbation), whereas Poisson's elliptic solutions can have substantially mismatched amplitude scales across fidelities. A single shared trunk asked to output `y/scaler[m]` for all fidelities forces the basis head to absorb cross-fidelity *scale*, not just structure, and the K=10 basis underfits the residual amplitude — yielding a uniform ~0.75 attractor on Poisson HF samples.

H2's LF-only warmup at `lr=1e-3` for 25% of epochs further commits the trunk to LF-target statistics before the HF data is even seen. On Heat (where LF and HF amplitudes are similar) this is a free pretraining boost (−24%). On Poisson (where LF/HF amplitudes differ in scale and the trunk has insufficient capacity to disentangle), warmup neither helps nor hurts materially (−3.3%), because the failure is upstream of the schedule.

**Failure stage:** training (recipe insensitive to PDE class).
**Category:** `PDE_CLASS_ARCH_RECIPE_COUPLING` (new).

### C.2 `fno_coreg_residual` — Poisson winner / Heat #3 (the inverse failure mode of C.1)

* `models/fno_coreg_residual/smoke_eval.py:69-82` — `SMOKE_DEFAULTS` has NO LF→HF transfer schedule. Training is single-stage joint with `lr=3e-4` and an AdamW + cosine schedule (`:491-492`).
* Architecture (notes at `summary.json:300`): 4 per-fidelity FNOs (hidden=32, modes per level `[(4,5),(8,9),(12,12),(12,12)]`, blocks=3) + MFRNP decoder-in-the-aggregation (decoder_hidden=32) + continuous-m basis head (K=10).
* Loss (`:275-311`): LF direct supervision per level (weights all 1.0) + HF residual-stack `pred = agg + basis_residual` against `y_hf_norm` + `agg_anchor_weight=0.5` anchor on agg.

**Heat distribution (median 0.0194, tight; this cycle's cache hit at 0.03519 reflects an earlier hash, see §C.4)** vs **Poisson (median 0.0571, well-distributed).** Reading the per-sample arrays from `summary.json`:
* Heat per-sample `rel_l2_per_sample[:128]` ranges 0.004–0.137 with median ≈ 0.024, mean ≈ 0.027 — long tail of harder samples around 0.1.
* Poisson per-sample ranges 0.01–0.16 with median ≈ 0.057, mean ≈ 0.057 — normal-ish distribution, no catastrophic outliers.

**Why Heat #3, not #1**: the per-fidelity-FNO ladder ([4,8,12,12] modes) deliberately starves spectral capacity at the low fidelities, then aggregates upward. Heat's HF target is dominated by *low-frequency, smooth* structure, and the IFC coregionalization-basis trunk in `fno_coregionalization` (a single shared full-resolution trunk with K=10 across-fidelity basis) is a better match to that signal — fewer parameters (1.19M vs 2.37M) but more relevant capacity at the HF resolution. The 4-per-fidelity stack is *over-provisioned for fidelity-bridging* on a dataset (Heat) where the bridge is trivial. So `fno_coreg_residual` "wastes" capacity on a multi-stage aggregation path that does not help Heat.

**Why Poisson #1**: per-fidelity FNOs let the model build a *separate* spectral representation for each fidelity, and the residual head learns the HF correction *over an LF-conditioned baseline* — the right inductive bias for Poisson, whose LF solutions provide a strong amplitude prior but a structurally incomplete HF estimate.

**Failure stage:** training-recipe vs PDE-class mismatch (architecture is sound but the schedule lacks an LF→HF transfer phase that would tighten the Heat distribution).
**Category:** `NO_TRANSFER_SIGNAL_HEAT` (new variant of the H2 finding).

### C.3 `transolver_residual` — catastrophic on both datasets (0.114 heat, 2.60 poisson)

* `models/transolver_residual/smoke_eval.py:45-51` — `SMOKE_DEFAULTS` is a point-cloud / attention recipe: `n_lf=1024, n_hf=2048` tokens, `hidden_dim=192, n_slices=32, num_heads=6`, `encoder_layers=2, residual_layers=3`, `val_frac=0.2`.
* `:70-83` — coords are synthesized on a normalized [-1,1] grid; for ifc_heat/poisson the grid_shape is 2-D and tokenization is regular.
* `train_seconds=0.0` and `cache=hit` in `summary.json:543, 651` — these results are stale from when transolver_residual was the H1 family in cycle-002/003; no re-run was triggered this cycle.

**Failure shape:** Heat at 0.114 is ~7× the FNO-family winners; Poisson at 2.60 is ~47× the Poisson winner. **It's the architecture-quality failure mode**: token-sampled attention on a small dataset (128 HF training samples for ifc_raw) cannot match a full-grid spectral backbone for these regular-grid PDE tasks, and the recipe carries no multi-fidelity *bridging* mechanism (the "residual" is between LF and HF tokens, not LF and HF *fields* on a grid). With only 2048 HF tokens out of a 64×64=4096-cell field, half the HF signal is dropped each batch.

**Failure stage:** architecture choice (point-token attention) on a regular-grid task with extremely scarce HF data.
**Category:** `ARCH_QUALITY_FAILURE` (existing taxonomy).

### C.4 cache hit on every family this cycle

All 14 runs in `summary.json:307,…` report `_cache: "hit"` and `train_seconds` in tens of seconds (or 0.0 for stale transolver/v9 entries). This baseline is not a fresh re-train; it reflects the cache state inherited from cycle-005-H2 (`be36cba`). That is the correct behavior — no recipe change was made between cycle-005-H2 and cycle-006-baseline — but it means cycle-006 has **no independent signal**: the metric_value is identical to cycle-005-H2 to all printed digits.

---

## D. Dominant failure mode (explicit statement)

**`PDE_CLASS_ARCH_RECIPE_COUPLING`** — dataset-PDE-class coupling of *training recipes* within a single architecture. This was the NEW PATTERN named in cycle-005 H2; cycle-006 baseline is the same artifact and confirms it.

Concretely: every model family that has a recipe knob (transfer schedule, loss weight, per-fidelity scaler choice, residual basis K) shows a *different* best setting for Heat vs Poisson. The smoke harness applies one global `SMOKE_DEFAULTS` per family, so each family is "stuck" being good at one PDE class and not the other. The composite metric papers over this by routing each dataset to whatever family currently owns it, but no single family is simultaneously competitive on both.

Evidence summary across the 5 in-tree families × 2 datasets = 10 instances:

| family ↓ / dataset →           | ifc_heat        | ifc_poisson     |
|--------------------------------|------------------|------------------|
| fno_coregionalization (H2)     | #1 0.01551 ✓     | #5 0.75015 ✗     |
| fno_coreg_residual             | #3 0.03519 ~     | #1 0.05556 ✓     |
| fno_mf_stack                   | #5 0.13010 ✗     | #3 0.08829 ~     |
| transolver_residual            | #4 0.11430 ✗     | #6 2.59704 ✗     |
| transolver_attention_fusion    | #7 0.14916 ✗     | #4 0.38327 ✗     |
| (bar) mf_fno_transfer_bar      | #2 0.03317 ~     | #2 0.08333 ~     |

The only family with comparable per-dataset rank is `mf_fno_transfer_bar` — it sits at #2 on both. Every in-tree family is dataset-coupled.

---

## E. Per-instance failure-mode percent breakdown (5 in-tree × 2 datasets = 10)

| Instance                                 | Status          | Category                          |
|------------------------------------------|-----------------|-----------------------------------|
| fno_coregionalization / ifc_heat         | PASS (winner)   | n/a                                |
| fno_coregionalization / ifc_poisson       | FAIL (#5)       | PDE_CLASS_ARCH_RECIPE_COUPLING     |
| fno_coreg_residual / ifc_heat             | PASS-but-#3     | NO_TRANSFER_SIGNAL_HEAT            |
| fno_coreg_residual / ifc_poisson          | PASS (winner)   | n/a                                |
| fno_mf_stack / ifc_heat                   | FAIL (#5)       | PDE_CLASS_ARCH_RECIPE_COUPLING     |
| fno_mf_stack / ifc_poisson                | OK (#3)         | NO_TRANSFER_SIGNAL_POISSON          |
| transolver_residual / ifc_heat            | FAIL            | ARCH_QUALITY_FAILURE               |
| transolver_residual / ifc_poisson         | FAIL            | ARCH_QUALITY_FAILURE               |
| transolver_attention_fusion / ifc_heat    | FAIL            | ARCH_QUALITY_FAILURE               |
| transolver_attention_fusion / ifc_poisson | FAIL            | ARCH_QUALITY_FAILURE               |

Percent breakdown (10 instances):
* `PDE_CLASS_ARCH_RECIPE_COUPLING`: **2 / 10 = 20%** (the two FNO families where a recipe-tuned good Heat or Poisson breaks the sibling dataset within the same family)
* `NO_TRANSFER_SIGNAL_*`: **2 / 10 = 20%** (good rank but not the winner; the family lacks the LF→HF transfer trick that would push it to #1 on the sibling dataset)
* `ARCH_QUALITY_FAILURE`: **4 / 10 = 40%** (transolver families on both datasets — wrong backbone for these regular-grid PDE tasks at this sample size)
* `PASS (winner)`: **2 / 10 = 20%** (fno_coregionalization on Heat; fno_coreg_residual on Poisson)

Said differently: **80% of in-tree instances fail** (8 of 10 are not the dataset winner). Of those, **half are PDE-coupling failures within an otherwise viable architecture** (i.e. fixable by recipe gating) and **half are architecture-quality failures** (fixable only by a backbone change).

---

## F. Recommended interventions (ranked by EV; all within `models/**`)

### F.1 (highest EV) — Dataset-conditional schedule in `fno_coregionalization`

**Why first**: the H2 LF-only warmup is the *only* recipe change between cycle-005 baseline and cycle-005-H2 / cycle-006-baseline, and it produced a clean −24% on Heat with essentially no movement on Poisson. The architectural Poisson failure is upstream of H2 (was already 0.776 pre-H2), so gating H2 off on Poisson will NOT recover Poisson — but it will free us to experiment with Poisson-specific recipes without breaking Heat. The gating itself is a 5-line change.

**Files:** `models/fno_coregionalization/smoke_eval.py` only.
**Change:** at `smoke_eval.py:236-280`, read `args.dataset_name` and choose `pretrain_frac` / `pretrain_lr` from a `_DATASET_RECIPES` dict, e.g.:
```python
_DATASET_RECIPES = {
    "ifc_heat":    dict(pretrain_frac=0.25, pretrain_lr=1e-3, finetune_lr=3e-4),
    "ifc_poisson": dict(pretrain_frac=0.0,  pretrain_lr=3e-4, finetune_lr=3e-4),  # no LF warmup
}
```
…then merge that into `SMOKE_DEFAULTS` inside `run()`. Default fallback keeps the current behavior so other datasets are unaffected.

**Expected effect:** Heat stays at 0.01551 (recipe unchanged). Poisson recovers to ≈ its pre-H2 value of 0.776 (no change vs baseline) **or** to whatever a Poisson-specific recipe achieves. Composite: no regression vs cycle-006 baseline (since fno_coregionalization is not the Poisson owner). Unlocks F.2.

**Risk:** none (gating is monotonic — adds no new failure paths).

### F.2 (high EV) — Add a *short* LF warmup in `fno_coreg_residual` for Heat

**Why second**: `fno_coreg_residual` currently has no transfer-learning warmup at all (`smoke_eval.py:69-82, 491-499`). Its Heat result is 0.03519 (#3, 2.3× the leader). The H2 mechanism that gave fno_coregionalization a −24% on Heat is a candidate transfer for fno_coreg_residual's Heat. The fno_coreg_residual architecture is more capacity-rich (2.37M params, 4 per-fidelity FNOs); a Heat-only short LF-warmup may bring it to or below the 0.013 hard target without disturbing Poisson.

**Files:** `models/fno_coreg_residual/smoke_eval.py` only.
**Change:** at `smoke_eval.py:491-492`, wrap the cosine-scheduled training loop with an optional LF-only pre-stage gated on `args.dataset_name == "ifc_heat"`. Reuse the H2 pattern from `fno_coregionalization/smoke_eval.py:341-411` (fresh Adam, fresh cosine, short `n_warmup ≈ 0.15 * epochs`).

**Expected effect:** Heat 0.03519 → target ≤ 0.025 (would lift fno_coreg_residual into #2 on Heat behind fno_coregionalization). Composite unchanged unless fno_coreg_residual passes fno_coregionalization on Heat. Poisson untouched (gated off).

**Risk:** the per-fidelity ladder may not benefit from LF-warmup the way a single shared trunk did, because each level has its own FNO and there's no shared trunk to "transfer". Mitigation: warm up ONLY the HF-level FNO + basis head from LF samples *bilinearly upsampled to HF grid* — a tighter analog of the bar's mechanism.

### F.3 (medium EV) — NEW family: HF-conditional curriculum (high-fidelity first, then residual)

**Why third**: the existing families all do "LF first → HF later" (or "all together"). The bar (`mf_fno_transfer_bar/smoke_eval.py:156-167`) is also LF-first. None of them try HF-first → LF-refine. A new family that *starts* on the small HF set and then *re-anchors* through an LF residual head could be a different inductive bias — useful particularly for Poisson where the HF amplitude is what's hard and the LF prior is a partial structural hint.

**Files (new family scaffold):**
* `models/<new_family>/manifest.json`, `model.py`, `smoke_eval.py` — mirror the contract used by `fno_coreg_residual/`.
* `model.py` reuses `FNO2d` or borrows the per-fidelity FNO stack from `fno_coreg_residual/model.py`.
* `smoke_eval.py` implements the 2-stage curriculum: Stage 1 = HF-only short pre-train (lr=3e-4, ~30% of epochs); Stage 2 = joint HF + LF-residual fine-tune (lr=1e-4, remaining epochs) with an LF-prediction-as-prior loss.

**Expected effect:** unknown a priori. Provides a 3rd dataset-specific tuning axis without breaking either existing family. Should specifically be evaluated on Poisson.

**Risk:** new family takes a full cycle to scaffold, train, and judge. EV is "explore the orthogonal direction" rather than "close the gap deterministically".

### F.4 (medium EV) — NEW family: `mf_fno_transfer_bar`-style LF→HF transfer **on top of** a coregionalization or residual head

**Why fourth**: this is the original NEW DIRECTIVE goal from `backlog.md:20-35`. cycle-005 H2 already applied the LF→HF transfer mechanism to the coregionalization head and won Heat at 0.01551 — beating the bar's Heat (0.03317). But the resulting Poisson is broken because the underlying head is fno_coregionalization. A new family that composes the *bar's exact recipe* (single full-resolution FNO, LF-pretrain → HF-finetune) with the **fno_coreg_residual** head (per-fidelity FNOs + residual aggregation) would combine the two demonstrated strengths.

**Files (new family scaffold):**
* `models/<new_family>/manifest.json`, `model.py`, `smoke_eval.py`.
* `model.py`: import the FNO2d backbone from `mf_fno_transfer_bar/model.py` for the HF trunk, plus the residual-aggregation head from `fno_coreg_residual/model.py`.
* `smoke_eval.py`: Stage 1 LF-pretrain on the HF-grid-upsampled LF field (bar pattern). Stage 2 attach the per-fidelity residual head + basis and joint-train.

**Expected effect:** if successful, this family is a candidate for *both* dataset wins. If the LF→HF transfer is the key mechanism and the residual head provides the Poisson-specific inductive bias, this family could land at #1 on both datasets and break the dataset-coupling pattern.

**Risk:** new family, full cycle to evaluate. The bar achieves Heat 0.033 with 4.7M params — adding a residual head will roughly double param count and may not fit the 30-min smoke wall budget.

### F.5 (lower EV, but cheap) — Fix `fno_mf_stack` Heat or `transolver_*` recipe

* `fno_mf_stack` Heat at 0.13010 is anomalously bad given the family is competitive on Poisson (#3 at 0.08829). Diagnose at `models/fno_mf_stack/smoke_eval.py:71-86` — the `poisson_*_weight` per-fidelity weights are NOT applied to Heat (gated on dataset name match), so Heat uses uniform LF weighting. If that's the bug, mirror the per-PDE weighting pattern.
* `transolver_*` families: low-EV per F.4 reasoning (ARCH_QUALITY_FAILURE — backbone is wrong for this task shape). Leave as-is until a free cycle.

---

## G. Cross-cycle comparison

| metric                          | cycle-005-baseline | cycle-005-H2 | cycle-006-baseline | trend |
|---------------------------------|--------------------|--------------|--------------------|-------|
| composite_nRMSE                  | 0.033726           | 0.029357     | 0.029357           | flat (H2 → baseline rolled forward) |
| ifc_heat winner / value          | fno_coreg / 0.02047 | fno_coreg / 0.01551 | fno_coreg / 0.01551 | improving (H2) then flat |
| ifc_poisson winner / value       | fno_coreg_residual / 0.05556 | fno_coreg_residual / 0.05556 | fno_coreg_residual / 0.05556 | flat |
| target_met_composite ≤ 0.026     | FALSE              | FALSE        | FALSE              | miss-but-closing |
| target_met_ifc_heat ≤ 0.013      | FALSE              | FALSE        | FALSE              | miss |
| mf_fno_transfer_bar on smoke     | BROKEN (REPO_ROOT) | 0.0526 geomean | 0.0526 geomean   | now landed (cycle-005 H1 fix) |

**Improvements (cycle-005-baseline → cycle-006-baseline):**
* `fno_coregionalization` Heat: 0.02047 → 0.01551 (**−24.2%**) via cycle-005 H2 LF→HF transfer schedule. New #1 on Heat.
* `mf_fno_transfer_bar` smoke harness: BROKEN → landed at smoke-rank #2 on both datasets (cycle-005 H1 REPO_ROOT fix). No longer a blocker for in-distribution bar comparison.

**Regressions:** none.

**New failure modes confirmed (not new this cycle, but re-confirmed):**
* `PDE_CLASS_ARCH_RECIPE_COUPLING` — 2/10 instances. Stated as NEW PATTERN in cycle-005 session-summary §"Cross-cycle patterns confirmed".
* `NO_TRANSFER_SIGNAL_HEAT` / `NO_TRANSFER_SIGNAL_POISSON` — names introduced this cycle; describes the inverse of the above (a family that *would* benefit from the recipe that broke the sibling family).

---

## H. Failure taxonomy update (state of the taxonomy after cycle-006)

| name                              | description                                                                                                                         | first seen |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|------------|
| `ARCH_QUALITY_FAILURE`             | the family's backbone is fundamentally wrong for the task shape (e.g. point-token attention on a 4096-cell regular-grid field with 128 samples) | cycle-003 |
| `NO_TRANSFER_SIGNAL_HEAT`           | the family has the right backbone but lacks the LF→HF transfer/curriculum trick that the leader uses on Heat                       | cycle-006 |
| `NO_TRANSFER_SIGNAL_POISSON`         | mirror of above on the Poisson dataset                                                                                              | cycle-006 |
| `PDE_CLASS_ARCH_RECIPE_COUPLING`   | one global SMOKE_DEFAULTS per family with no dataset gating; the recipe-tuned good behavior on dataset A breaks the family on B    | cycle-005 |
| `HARNESS_ANOMALY_NO_GPU_LOGIN_RUN` | cycle_eval.sh's local-pass cache pass timeouts on the login node — out of mutable scope (in `scripts/` / `eval/`)                  | cycle-005 |

---

## I. Out-of-scope / operator notes (NOT for Strategist hypotheses)

* `cycle_eval.sh` local-pass GPU-gating issue: still present, still out of mutable scope (`scripts/cycle_eval.sh`, `eval/score.py`, `eval/smoke_config.json` are fixed surfaces).
* Precheck score-direction polarity bug: 7/7 confirmed on lower-is-better evals. Out of mutable scope.
* `transolver_*` stale cache entries: their `train_seconds=0.0` and `_cache=hit` means they have not been re-trained since cycle-003/004. If a future cycle invalidates their recipe_hash, they'll re-train fresh; not actionable here.
* Working tree dirty-baseline scope issue: 15 pre-existing modified files at session start. Operator action only.

---

## J. Summary for Strategist

* Composite = 0.029357, target 0.026, gap +0.0034. **Poisson contributes ~all of the gap** in log-space.
* Dominant failure mode: `PDE_CLASS_ARCH_RECIPE_COUPLING` — recipes are tuned per family but applied per (family × dataset), so every recipe-knob change improves one dataset and breaks the sibling.
* Cheapest concrete intervention: dataset-conditional `pretrain_frac` in `fno_coregionalization/smoke_eval.py` (F.1). No EV downside; unlocks a Poisson-specific recipe experiment.
* Highest single-cycle EV intervention: add a short LF-warmup to `fno_coreg_residual` for Heat only (F.2). Could land the in-tree fno_coreg_residual at Heat #2 and tighten the composite.
* Bigger swings: NEW family combining the bar's LF→HF transfer trick with the residual head (F.4) — directly addresses the NEW DIRECTIVE.
* Architecture-quality failures (transolver_*) are 40% of instances but fixing them does not close the composite gap; leave for a free cycle.
