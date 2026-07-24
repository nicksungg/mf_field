---
name: cycle-001-strategy
description: Cycle 001 strategy snapshot — 2 hypotheses (H1 fno_coregionalization, H2 fno_mf_stack), both capability_surface growth, both with per-fidelity output norm + val_frac=0.1. CEO PLAN APPROVED.
metadata:
  type: strategy
tags:
  - factory
  - strategy
  - factory_mffp
  - cycle-001
project: factory_mffp
cycle: "001"
date: 2026-05-15
source: factory-archivist
---

# Strategy: factory_mffp — cycle 001 (2026-05-15)

Research-mode cycle. CEO verdict on Strategist: **PROCEED — PLAN APPROVED**. `--no-github` enabled, so no PR/issue creation.

## Plan

Two hypotheses, both targeting the dominant failure F1 (`ifc_poisson` value-scale-across-fidelities collapse) as primary and F2 (`ifc_heat` backbone gap) as secondary via FNO backbone. F3 (empty `paper_baselines.json` splits) is explicitly out-of-scope (fixed surface — human action).

### H1: `fno_coregionalization`
- **Backlog item:** `.factory/strategy/backlog.md` line 27.
- **Category:** FIX. **Type:** code. **Priority:** high.
- **Growth dimension:** `capability_surface` (new family at `models/fno_coregionalization/`).
- **Architecture:** FNO backbone (3–4 spectral-conv blocks, `k_max=12`, `hidden_channels=64`) outputs latent grid `h(x) ∈ R^{K×H×W}` with K=10; coregionalization head `B(m) = MLP_B([m, m²])` (cheap MLP, NOT neural ODE — the full IFC neural ODE is ~7.84 s/epoch in the paper for K=20 on Poisson, too slow for 30-min smoke budget). Output: `y(x) = Σ_k B_k(m) · h_k(x)`. Continuous `m` read from `cat.pkl` `t_list` (`[0.0, 0.143, 0.429, 1.0]`); at inference m=1.
- **Per-fidelity output normalization (mandatory):** predict `y / scaler[m]`, `scaler[m]=max-abs` of training y at fidelity m.
- **`val_frac=0.1`** (preserves 4–5 of 5 HF training samples).
- **Files (concrete) under `models/fno_coregionalization/`:** `manifest.json`, `INSPIRATION.md`, `model.py`, `data.py`, `smoke_eval.py`, optional `full_config.json`.
- **Inspirations:** [[li2022ifc]] (architecture template), [[li2020fno]] (backbone).
- **Smoke wall time:** 1–3 min on H100.

### H2: `fno_mf_stack`
- **Backlog item:** `.factory/strategy/backlog.md` line 26.
- **Category:** FIX. **Type:** code. **Priority:** high.
- **Growth dimension:** `capability_surface` (new family at `models/fno_mf_stack/`).
- **Architecture:** 4 small FNOs (~50k params each, hidden=32–64, 2–3 spectral conv blocks, `k_max≈12`) — one per fidelity level `{L1,L2,L3,L4}`. MFRNP-style residual stack with decoder-in-the-aggregation: decoded LF predictions upsampled (bilinear) to 64×64, aggregated; HF (L4) FNO predicts residual `δ`; final HF output = `aggregate(decoded_LFs upsampled to 64×64) + δ`. Continuous `m` threaded through aggregator.
- **Per-fidelity output normalization (mandatory):** same as H1.
- **`val_frac=0.1`.**
- **Files (concrete) under `models/fno_mf_stack/`:** `manifest.json`, `INSPIRATION.md`, `model.py`, `data.py`, `smoke_eval.py`, optional `full_config.json`.
- **Inspirations:** [[niu2024mfrnp]] (architecture template), [[li2020fno]] (backbone).
- **Smoke wall time:** 3–5 min on H100.

## CEO HARD GATE results

| Gate | Result |
|---|---|
| Surface check (mutable_surfaces only — `models/**`) | **PASS** — H1/H2 both confined to `models/<family>/**` |
| Leakage check (`factory leakage-check`) | **PASS** — H1 `risk_level=none, flagged=false`; H2 `risk_level=none, flagged=false` |
| Research config validation (`factory validate-research`) | **VALID** — all ground-truth isolation checks pass |
| Hypothesis count vs budget (`max_new=2`) | **PASS** — exactly 2 |
| Growth dimension tag (`min_growth ≥ 1`) | **PASS** — both `capability_surface` |
| Backlog item tags | **PASS** — H1 → line 27, H2 → line 26 |
| Type tag | **PASS** — both `code` |

See [[ceo-verdict-strategist-cycle-001]] for the full HARD GATE table.

## Execution strategy

- **Sequential, not parallel.** Per research-mode protocol R3 ("For each approved hypothesis, sequentially") and CEO playbook `ceo-00009` (no background subagents). Parallel execution is documented under Improve mode for PR-based code review parallelism, not single-shot model training.
- `--no-github` is set: Builder will receive a direct task description, NOT a GitHub issue reference. No PR creation.
- Builder timeout = **1800 s** per hypothesis (code-only, smoke verification at `--epochs 2` is well under).
- Builder MUST run `python models/<family>/smoke_eval.py --epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` end-to-end before declaring ready.
- R4 invokes `bash scripts/cycle_eval.sh` — cache-aware (instant return when model code unchanged from fingerprint), otherwise SLURM submission.

## Expected quantitative impact

Same conservative bound for both hypotheses (per Researcher §Candidate Ranking + §Cross-Cutting):

| Metric | Baseline (v9) | Paper bar (li2022ifc IFC-ODE2 m=1) | H1/H2 conservative target | H1/H2 stretch target |
|---|---:|---:|---:|---:|
| `ifc_poisson` test nRMSE | 18.50 | 0.036 | ≤ 0.5 | 0.05–0.15 |
| `ifc_heat` test nRMSE | 0.149 | 0.074 | ≤ 0.10 | 0.05–0.10 (H2 plausibly < paper bar) |
| `composite_nRMSE` (geomean) | 1.6595 | — | **≤ 0.25** | **≤ 0.10** |

Researcher's cross-cutting finding: per-fidelity output normalization **alone** is projected to drop `ifc_poisson` from 18.5 to ~1.0 without architectural changes — see [[cycle-001-cross-cutting-findings]]. The IFC inductive bias (H1) or residual stacking (H2) then targets the remaining ~10× gap.

## Anti-patterns recorded (do NOT repeat)

From [[cycle-001-failure-diagnosis]] + Strategist's §Anti-patterns section:

1. **No global prior MLP without continuous fidelity index.** v9's `prior_head` averages toward L1 magnitude → predicts 10–40× too large on L4 test set.
2. **No `val_frac = 0.2`** on HF-limited datasets — random_split removes ~1 of 5 HF samples. Both hypotheses use `val_frac = 0.1`.
3. **No Transolver on regular-grid data.** Slice-attention is geometry-general, ill-matched to 64×64 regular grids. Use FNO (spectral conv) instead.
4. **No full IFC neural ODE at smoke scale.** Paper reports ~7.84 s/epoch for K=20 — too slow for 30-min smoke budget. H1 uses cheap `B(m)=MLP([m,m²])` basis.
5. **No skipping per-fidelity output normalization.** Without it, `ifc_poisson` cannot leave the value-scale-collapse regime regardless of backbone quality.
6. **No edits to fixed surfaces.** `data/**`, `baselines/**`, `eval/**`, `references/**`, `factory.md`, `README.md`, `scripts/**` are read-only.
7. **No external weight downloads or API calls at eval time** (research_constraints L65).

## New backlog items

**None this cycle.** CEO directive to Strategist: "Do NOT add **New:** items this cycle — focus on clearing the two highest-priority backlog items." [[sung2026fire]] (training-free MF via tabular foundation models) and `kent2026noisemf` flagged as forward placeholders; persistence at CEO discretion at cycle close.

## Links

- Project dashboard: [[factory_mffp]]
- Prior CEO verdict: [[ceo-verdict-researcher-cycle-001]] (Researcher → Strategist handoff)
- Failure diagnosis: [[cycle-001-failure-diagnosis]]
- Candidate ranking: [[cycle-001-candidate-ranking]]
- Cross-cutting findings: [[cycle-001-cross-cutting-findings]]
- Source papers: [[li2022ifc]], [[niu2024mfrnp]], [[li2020fno]]
