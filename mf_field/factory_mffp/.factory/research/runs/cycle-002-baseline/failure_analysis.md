# Failure Analysis — Cycle 002 (baseline re-measure on master)

## Summary
- **Instances scored:** 2 / 2 datasets (`ifc_heat`, `ifc_poisson`) — both PASS as runs, both FAIL as research targets.
- **Composite metric (master, v9 only):** `composite_nRMSE = 1.6595` (geomean of `ifc_heat=0.14883`, `ifc_poisson=18.50343`). **Identical to cycle 000-baseline** — neither H1 nor H2 has merged to master, so the on-disk research-target metric has not moved. The cycle-002 baseline run is a cache hit (5 s wall) reusing `results/smoke_latest.json`; the model file under test is still `references/v9_baseline/`.
- **Dominant failure mode:** `POISSON_VALUE_SCALE_COLLAPSE` (F1) — `ifc_poisson` test nRMSE = 18.50 contributes ~95 % of the composite by geomean weight; ~13.6× the v9 val nRMSE and ~514× the paper bar (0.036).
- **Paper bar gap (target = 0.0 composite, paper = li2022ifc IFC-ODE2 m=1):** `ifc_heat` 2.01× over paper (0.074); `ifc_poisson` 514× over paper (0.036). `n_datasets_beating_paper = 0 / 2` on master.
- **Cycle-001 evidence (on disk on `experiment/*` branches, NOT yet merged):** H1 (`fno_coregionalization`) drove the master metric from 1.6595 → 0.1092 (−93.4 %) and **beat the paper bar on `ifc_heat` outright** (0.0154 < 0.074); H2 (`fno_mf_stack`) drove it to 0.1117 (−93.3 %) and **set a new project best on `ifc_poisson`** (0.0979, 7.9× better than H1 on Poisson, 2.7× over paper). The two families are inverse-complementary: H1 wins Heat, H2 wins Poisson, neither wins both. This is the **cycle-002 synthesis gap**.

## Per-Instance Results

### Instance `ifc_heat` (v9_baseline on master)
- **Status:** FAIL (research target)
- **Stage:** model — backbone inductive bias
- **Failure:** test nRMSE 0.14883 vs paper bar 0.074 (2.01× over paper); val→test ratio ~3× (val 0.0524 → test 0.149) so under-trained-but-in-range, not catastrophic.
- **Root cause (behavioral):** v9's Transolver backbone uses slice-attention which is designed for geometry-general / irregular meshes. The IFC datasets sit on a regular 64×64 grid where the dominant signal is a small set of Fourier modes; spectral-conv (FNO) is the literature-matched inductive bias and v9 forgoes it. Capacity (~409 k params) is not the bottleneck — the cycle-001 H1 result at similar scale dropped this by 10× by swapping in FNO + a continuous-m basis.
- **Category:** `BACKBONE_INDUCTIVE_BIAS_MISMATCH` (F2 in the running taxonomy)
- **Suggested fix:** none new — already eliminated on `experiment/1-fno_coregionalization` (Heat went 0.149 → 0.0154 with FNO+coreg). The intervention is "merge or build on top of H1." Cycle-002 risk: H2's residual-stack family **regressed** on Heat (0.1275, 8.3× worse than H1) when its smoke defaults shipped at `hidden=16, modes=(4,5,5,5)`; the pre-registered cycle-002 single-knob fix is to bump those to `hidden=32–64, modes=(4,8,12,12)` to match `full_config.json`.

### Instance `ifc_poisson` (v9_baseline on master)
- **Status:** FAIL (research target)
- **Stage:** model — multi-fidelity transfer / output normalization
- **Failure:** test nRMSE 18.50 vs paper bar 0.036 (514× over paper); val→test ratio ~13.6× (val 1.365 → test 18.50) so val-to-test is itself catastrophic, on top of a poor val number.
- **Root cause (behavioral):** v9 routes the prediction through a global `prior_head` MLP with no continuous fidelity index. Training-data y-magnitudes collapse ~40× from L1 to L4 (scalers observed during H1 build: `[0.0773, 0.0237, 0.0069, 0.0018]`), so the prior averages toward the high-magnitude LF training majority and predicts ~10–40× too large on the L4-only test set. The architecture has no mechanism to learn that "output magnitude depends on fidelity index m."
- **Category:** `POISSON_VALUE_SCALE_COLLAPSE` (F1 in the running taxonomy) — the dominant failure mode.
- **Suggested fix:** none new — both H1 and H2 have already mechanically resolved this in cycle 001. H1 dropped Poisson 18.50 → 0.7725 (95.8 %) via per-fidelity output normalization + continuous-m basis head; H2 dropped Poisson 18.50 → 0.0979 (99.5 %) via per-fidelity output normalization + MFRNP residual stack. The cross-cutting intervention `predict y / scaler[m]` is now confirmed twice across two different architectures. Cycle-002 intervention is "carry the normalization forward in any new family" — not novel.

## Failure Distribution

By composite-penalty share (geomean):

| Category | Instances | Composite share | Severity |
|---|---|---|---|
| `POISSON_VALUE_SCALE_COLLAPSE` (F1) | 1 / 2 | ~95 % | dominant |
| `BACKBONE_INDUCTIVE_BIAS_MISMATCH` (F2) | 1 / 2 | ~5 % | secondary |
| `MISSING_PAPER_BASELINES` (F3, meta) | n/a | not numeric | blocker for `n_datasets_beating_paper` until appended to fixed surface |

Dominant failure mode: `POISSON_VALUE_SCALE_COLLAPSE` (F1). This is unchanged from cycle 000-baseline — master has not moved.

## Cross-Cycle Comparison

Baseline-vs-baseline (no model change on master):

| Metric | Cycle 000 baseline | Cycle 002 baseline | Trend |
|---|---:|---:|---|
| composite_nRMSE | 1.6595 | 1.6595 | **stable** (cache reuse, identical numbers — same v9 model file, same data, same seed) |
| `ifc_heat` test nRMSE | 0.14883 | 0.14883 | stable |
| `ifc_poisson` test nRMSE | 18.50343 | 18.50343 | stable |
| `n_datasets_beating_paper` | 0 / 2 | 0 / 2 | stable |

This is **not a regression and not a new baseline** — it is the same v9 baseline re-measured because the experimental branches were not merged into master.

Cycle-001 experimental evidence (on `experiment/*` branches, archived as kept-intended):

| Run | composite | `ifc_heat` | `ifc_poisson` | Beats paper? | Vs cycle-000 master |
|---|---:|---:|---:|---|---|
| 000-baseline (master, v9) | 1.6595 | 0.1488 | 18.50 | 0 / 2 | — |
| cycle-001-H1 (FNO + coreg) | **0.1092** | **0.0154** | 0.7725 | 1 / 2 (heat) | −93.4 % |
| cycle-001-H2 (FNO + MFRNP stack) | 0.1117 | 0.1275 | **0.0979** | 0 / 2 (poisson 2.7× over) | −93.3 % |
| cycle-002-baseline (master, v9) | 1.6595 | 0.1488 | 18.50 | 0 / 2 | unchanged |

**Improvements (cycle-001 evidence, off-master):**
- F1 mechanically resolved by both H1 and H2 via per-fidelity output normalization `y / scaler[m]`. H2's residual-stack inductive bias adds ~8× on top of that on Poisson (0.7725 → 0.0979). The Researcher-projected "normalization alone lands at ~1.0" was confirmed within 30 % by H1's 0.7725.
- F2 mechanically resolved by H1 via FNO + continuous-m basis (10× improvement on Heat, beats paper).

**Regressions (cycle-001 evidence):**
- H2 regressed on Heat (0.1275, 8.3× worse than H1, 1.7× over paper). Identified root cause is **not** the residual-stack inductive bias itself but a config-only mismatch: `smoke_eval.py:SMOKE_DEFAULTS = (hidden=16, modes=(4,5,5,5), 2 blocks)` vs the spec-faithful `full_config.json = (hidden=64, modes=(4,8,12,12), 3 blocks)`. The smoke path used 49× fewer params than H1.

**New failure modes (cycle-001 evidence):**
- `SMOKE_DEFAULT_UNDER_CAPACITY` — a new failure category. When a new family ships both a `smoke_eval.py` and a `full_config.json`, if the smoke defaults are independently hard-coded undersized, the smoke-time metric can hide otherwise-recoverable performance. Distinct from F2 (backbone-bias mismatch) — it's a config-surface, not an inductive-bias, problem.
- `INVERSE_COMPLEMENTARY_FAMILIES` — a new cycle-spanning pattern, not a per-instance failure. H1 and H2 mirror each other's strengths (Heat-win vs Poisson-win). On their own neither beats paper on both datasets. This is the **structural target for cycle 002**.

## Recommended Interventions

Ranked by expected impact on `composite_nRMSE` against the paper bar (target = 0.0; current = 1.6595 on master). All within mutable surface `models/**`.

### 1. Land H1 and H2 on master (zero new code; precondition for everything below)
**Why:** The on-disk research-target metric is still 1.6595 only because the two experimental branches did not merge. Before any cycle-002 hypothesis, the project should treat H1 + H2 as the new baseline (CEO verdict was KEEP on both; the `factory` bookkeeping `revert` was a precheck polarity-bug artifact, documented in both archive notes). Any cycle-002 strategy must start from project state ≈ 0.1092 (H1 best) and 0.0154 / 0.7725 per-dataset, not 1.6595.
**Suggested mechanism:** rebase the `experiment/1-fno_coregionalization` and `experiment/2-fno_mf_stack` branches onto master so subsequent cycles see them; alternatively, treat H1's checkpoint as the cycle-002 baseline for scoring purposes. This is a human / archivist action and is not itself a model hypothesis, but every model-side intervention below assumes it.

### 2. **Hybrid: coregionalization head over an MFRNP residual stack** (attacks the synthesis gap)
**Why:** H1 wins Heat because the continuous-m basis `B(m)·h(x)` exactly captures Heat's smooth m-dependence; H2 wins Poisson because the residual decomposition `y_HF = aggregate(y_LF) + δ_HF` conditions the HF head on a well-trained LF baseline (Poisson's stiff dynamics + 5 HF samples ruin a from-scratch HF predictor but suit a corrector). The two inductive biases are independent — there is no architectural reason they cannot coexist. The realized Poisson 7.9× gap between H1 and H2 is itself the largest single signal cycle-001 produced.
**Files (new family under mutable surface):** `models/fno_coreg_residual/{manifest.json, INSPIRATION.md, model.py, data.py, smoke_eval.py, full_config.json}`. Build on top of H2's `model.py` (the residual stack + decoder-in-aggregation + per-fidelity normalization is already there) and replace H2's HF FNO output head with H1's `B(m)·h(x)` coregionalization head, so the HF prediction is `aggregate(decoded_LFs upsampled) + Σ_k B_k(m) · h_k(x)`. Keep per-fidelity output normalization (mandatory cross-cutting). Use full config sizes from start (hidden ≥ 32, modes=(4,8,12,12)) to avoid the H2 under-capacity regression on Heat.
**Risk:** H1's basis was good at Heat with 4.75 M params; if the residual-stack budget forces it down to ~100 k it may not capture the Heat regime. Mitigation: allow per-dataset full configs (`full_config.json` already supports this in H2) and let Heat run a heavier config than Poisson.
**Expected impact:** if both wins are preserved, composite drops to ~`sqrt(0.0154 · 0.0979) ≈ 0.039` — comparable to the paper bar on Poisson (0.036) and well below it on Heat (0.074). 2 / 2 datasets beating paper is plausible. This is the single hypothesis with the largest expected gain and is also the natural follow-up the H2 archive note pre-registered as "the cycle-002/003 ensemble lead."

### 3. **Single-knob redirect of H2: bump `SMOKE_DEFAULTS` to match `full_config.json`** (cheap, pre-registered)
**Why:** This is the H2 archive's pre-registered cycle-002 hypothesis. The Heat regression in H2 (0.1275 vs H1's 0.0154) is explained by `smoke_eval.py:SMOKE_DEFAULTS = (hidden=16, modes=(4,5,5,5), 2 blocks)` running 49× fewer params than H1. Bumping to `hidden=32–64, modes=(4,8,12,12), 3 blocks` is a one-knob test that isolates "is the residual-stack inductive bias bad on Heat, or was H2 just under-capacity?"
**Files (edit-only on mutable surface — requires landing H2 to master first):** `models/fno_mf_stack/smoke_eval.py` — read defaults from `full_config.json` instead of hard-coding `(16, (4,5,5,5))`; alternately add a `--config full` flag. No `model.py` change.
**Risk:** Heat may still trail H1 if the residual-stack inductive bias itself is the limiter, not capacity — but at that point we have a clean experimental answer rather than a confounded one. Wall-time risk is small (H2 ran 530 s on CPU at hidden=16; hidden=32 with full modes should stay under 30 min).
**Expected impact:** if under-capacity was the bottleneck, Heat returns to roughly H1's territory (0.02–0.04) while keeping Poisson at 0.0979. Composite → roughly `sqrt(0.03 · 0.10) ≈ 0.055`, also paper-class. Cheap, decisive, and complementary to (2).

### 4. **Tune H1 harder on Poisson** (alternative to a third hypothesis; orthogonal capacity push)
**Why:** H1 already beats paper on Heat by 4.8×; its Poisson 0.7725 is the bottleneck (still 21× over paper). The cycle-001 H1 strategy explicitly notes the K=10 basis was kept small to avoid overfit on 5 HF samples. With more LF supervision routed into B(m) and a careful per-fidelity loss-weight (down-weight L1 which dominates by sample count), H1's Poisson might come down further without losing Heat.
**Files (edit-only on mutable surface — requires landing H1 to master first):** `models/fno_coregionalization/model.py` (raise K, add separate small B-network for HF-only correction); `data.py` (per-fidelity loss weighting). Keep all other surfaces fixed.
**Risk:** lower expected upside than (2) — H2 already showed that residual-stack is 7.9× better than H1's basis at Poisson, so even an optimized H1 likely loses to a hybrid. Worth considering as a fallback only if (2) and (3) both fail.
**Expected impact:** plausibly Poisson 0.7725 → 0.2–0.4 (3–4× improvement). Composite → ~`sqrt(0.015 · 0.3) ≈ 0.067`, still paper-class on Heat only.

### 5. **Third orthogonal family** (deferred)
Backlog candidates that target a different axis (`siren_film_fidelity`, `fire_field`, `transolver_residual`) are deferred unless (2) and (3) both miss. The cycle-001 evidence is that the strongest move from project state is **synthesis**, not diversification.

### Recommended cycle-002 hypothesis pair
- **H1 (cycle-002): `fno_coreg_residual`** (intervention 2) — high priority, attacks the synthesis gap.
- **H2 (cycle-002): `fno_mf_stack` smoke-defaults bump** (intervention 3) — low cost, pre-registered, isolates capacity from inductive-bias on Heat.

Both stay within `models/**` and respect the `hypothesis_budget.max_new = 2` cap from `factory.md`.

## Failure Taxonomy Update

| Code | Name | First observed | Status |
|---|---|---|---|
| F1 | `POISSON_VALUE_SCALE_COLLAPSE` | cycle 000 | confirmed twice fixable by per-fidelity output normalization; residual-stack is 8× stronger than continuous-m basis on Poisson |
| F2 | `BACKBONE_INDUCTIVE_BIAS_MISMATCH` (Transolver vs regular grid) | cycle 000 | fixed by FNO swap; confirmed once on Heat (H1: 0.149 → 0.0154) |
| F3 | `MISSING_PAPER_BASELINES` (meta) | cycle 000 | still open — `baselines/**` is fixed surface |
| **F4 (new)** | `SMOKE_DEFAULT_UNDER_CAPACITY` | cycle 001 (H2) | discovered when H2's hard-coded `(hidden=16, modes=(4,5,5,5))` cost 8.3× on Heat vs H1; recoverable by config edit alone |
| **F5 (new)** | `INVERSE_COMPLEMENTARY_FAMILIES` (cross-cycle pattern, not per-instance) | cycle 001 (H1 vs H2) | not a failure of any single run; describes the cycle-002 synthesis gap |

F4 is the most actionable new category: it identifies a *config surface* failure separate from the model surface, and the fix is a one-knob edit rather than a new family. F5 is the structural target the cycle-002 strategy should aim at directly.
