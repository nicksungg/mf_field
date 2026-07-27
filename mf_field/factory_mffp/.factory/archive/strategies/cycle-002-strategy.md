---
name: cycle-002-strategy
description: Cycle 002 strategy snapshot — 2 CEO-approved hypotheses (H4 fno_mf_stack capacity+Poisson-loss bump EXPLOIT, H3 fno_coreg_residual novel hybrid COMBINE). All HARD GATE checks PASS. Execution order H4 first, H3 second.
metadata:
  type: strategy
tags:
  - factory
  - strategy
  - factory_mffp
  - cycle-002
project: factory_mffp
cycle: "002"
date: 2026-05-15
source: factory-archivist
verdict: PLAN_APPROVED
hypothesis_count: 2
---

# Strategy: factory_mffp — cycle 002 (2026-05-15)

Research-mode cycle 002. CEO verdict on Strategist: **PROCEED — PLAN APPROVED** (HARD GATE). `--no-github` enabled.

## Cycle-002 baseline (master)

- `composite_nRMSE = 1.6595` (geomean of `ifc_heat=0.14883`, `ifc_poisson=18.50343`). Identical to cycle 000 baseline — neither H1 nor H2 was merged to master, so on-disk research-target metric has not moved. Master tracks only the v9 reference family.
- Cycle-001 evidence intact on `experiment/1-fno_coregionalization` (H1 composite 0.10919, **beats paper on Heat 4.8×**) and `experiment/2-fno_mf_stack` (H2 composite 0.11173, **project best on Poisson 0.0979**, 2.7× over paper).
- Structural failure mode entering cycle 002: **F5 `INVERSE_COMPLEMENTARY_FAMILIES`** — H1 wins Heat, H2 wins Poisson, neither wins both. F4 `SMOKE_DEFAULT_UNDER_CAPACITY` (config surface, H2 Heat regression) carried over from cycle 001.

## Approved Hypotheses (priority order)

### H4: fno_mf_stack capacity + Poisson-loss bump (EXPLOIT) — runs FIRST

- **Category:** EXPLOIT. **Type:** code. **Priority:** high.
- **Growth dimension:** `experiment_diversity` (capacity/training-hyperparameter axis on existing inductive bias).
- **Failure mode:** F4 primary (cycle-001 H2 archive's pre-registered diagnostic), F1 secondary (Poisson-specific HF-up-weighting attacks remaining residual headroom).
- **Branch from:** `experiment/2-fno_mf_stack` (cycle-001 H2 branch — inherit working H2 implementation, do NOT rebuild from scratch).
- **Mutable surface:** `models/fno_mf_stack/**` only.
- **Two pre-registered MFRNP Poisson5 knobs (both from `Poisson5_config.yaml`):**
  - **Knob 1 (capacity, attacks F4):** `SMOKE_DEFAULTS` moves from `(hidden=16, modes_per_level=(4,5,5,5), spectral_blocks=2)` → `(hidden=32, modes_per_level=(4,8,12,12), spectral_blocks=3)`.
  - **Knob 2 (Poisson loss, attacks F1):** per-fidelity MSE weighting `HF_weight=2` (m=1), `LF_weight=0.25` (m<1). Net 8× HF up-weighting. **Dataset-gated to Poisson only** — Heat retains uniform weighting per the published `pde_config.yaml`.
- **`model.py` UNTOUCHED.** This is config + loss-weight only, NOT an architectural change. Edit list: `smoke_eval.py`, `data.py`, optionally `full_config.json` and `INSPIRATION.md`.
- **Inherited (from H2 branch):** 4 per-fidelity FNOs, MFRNP decoder-in-the-aggregation, per-fidelity output normalization `y/scaler[m]`, `val_frac=0.1`, continuous m threading, `ifc_raw` loader.
- **Expected smoke wall:** 5–10 min on H100.
- **Expected composite:** ~0.05 range (`ifc_heat 0.05–0.10`, `ifc_poisson 0.04–0.07`). Master comparison: 1.6595 → ~0.05, a ~30× improvement.
- **Why first:** lower-risk, lower-cost, faster cheap diagnostic. Resolves whether F4 alone explains the H2 Heat regression vs F2 (intrinsic inductive-bias mismatch).

### H3: fno_coreg_residual novel hybrid (COMBINE) — runs SECOND

- **Category:** COMBINE. **Type:** code. **Priority:** high.
- **Growth dimension:** `capability_surface` (new family at `models/fno_coreg_residual/`).
- **Failure mode:** F5 primary (compose H1's continuous-m basis-head with H2's MFRNP residual stack so a single architecture inherits both family wins); F1 + F2 secondary (both addressed by inherited inductive biases).
- **Branch from:** `master` (clean baseline). Build from scratch — do NOT copy from `references/v9_baseline/` and do NOT branch off H2.
- **Mutable surface:** `models/fno_coreg_residual/**` only (NEW family directory).
- **Architecture (full-config sizes from start per CEO instruction — avoids F4 regression):**
  - 4 per-fidelity FNOs (L1..L4), each `hidden=64`, `modes_per_level=(4,8,12,12)`, 3 spectral conv blocks.
  - MFRNP-style aggregator with decoder-in-the-aggregation (same as cycle-001 H2): decoded LF outputs bilinearly upsampled to 64×64 grid, combined into LF-aggregate field.
  - HF head replaced with H1-style continuous-m basis: `y_HF(x) = agg(x) + Σ_{k=1..K} B_k(m) · h_k(x)`, with `h ∈ R^{K×64×64}` (HF FNO low-rank latent, `K=10`), `B(m) = MLP_B([m, m²])` (cheap MLP, **NOT neural ODE**).
  - Per-fidelity output normalization `y/scaler[m]` — **MANDATORY** (cross-cutting Researcher finding that mechanically resolves F1).
  - Continuous `m` flows into both `B(m)` and MFRNP aggregator.
  - `val_frac=0.1`; bilinear upsample of LF inputs to 64×64; cite `xing2020deepcoreg` (closest analogue — ResPCA), `li2022ifc`, `niu2024mfrnp`, `li2020fno` in INSPIRATION.md.
  - **Explicit label in INSPIRATION.md:** "novel hybrid extension — no direct precedent in published MF field-prediction literature."
- **Optional cross-cutting knob (off by default in initial smoke):** same Poisson-only HF-up-weighting as H4, exposed as a one-flag ablation in `full_config.json`.
- **Expected smoke wall:** 10–20 min on H100. Combined H4+H3 well under 30-min budget.
- **Expected composite (best case):** ~0.04 (`ifc_heat 0.02–0.05`, `ifc_poisson 0.04–0.10`). Master comparison: 1.6595 → ~0.04, a ~40× improvement.
- **Why second:** larger expected upside — capable of carrying both family wins into a single architecture. Higher capacity, higher risk, bigger swing.

## HARD GATE checks (all PASS)

| # | Check | Result |
|---|---|---|
| 1 | hypothesis count = 2 (matches `max_new=2`) | ✓ |
| 2 | all surfaces under `models/**` (H4 in `models/fno_mf_stack/`, H3 in NEW `models/fno_coreg_residual/`) | ✓ |
| 3 | leakage-check both: `risk_level=none, flagged=false` | ✓ |
| 4 | growth tags present & load-bearing (H4=experiment_diversity, H3=capability_surface) | ✓ |
| 5 | backlog item adequacy (H4 = cycle-001 H2 archive pre-registered smoke-defaults bump, UPGRADED to two-knob per CEO R1.5; H3 = cycle-001 archive pre-registered H1+H2 hybrid candidate) | ✓ |
| 6 | operational item validation | N/A (both Type=code) |
| 7 | no redundancy with reverted experiments (H4 builds on H2 KEEP intent; H3 is novel compose) | ✓ |
| 8 | FEEC priority (H4=EXPLOIT cheap-decisive, H3=COMBINE bigger-swing) | ✓ |
| 9 | anti-patterns enumerated (9 explicit) | ✓ |

## Execution order

1. **H4 first** — cheap diagnostic (per Researcher R1.5 order-of-operations).
2. **H3 second** — bigger architectural swing (complementary, not sequential — does NOT depend on H4 outcome).

## Pre-flight requirements (both Builders)

`.venv/bin/python models/<family>/smoke_eval.py --epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` end-to-end before declaring ready. Contract JSON must include `metric_value`. Each Builder commits on a new experiment branch `experiment/<EXP_ID>-<short-desc>`. Per `--no-github`, no PRs opened. Builder is ABORTed if any non-mutable surface is touched.

## Anti-patterns (9 explicit, carry-forward + cycle-002-specific)

- Do NOT modify `model.py` in H4 (preserves clean F4 diagnostic).
- Do NOT branch H3 from `experiment/2-fno_mf_stack` (H3 is a new family; branch from master).
- Do NOT ship H3 with reduced SMOKE_DEFAULTS (CEO: full-config sizes from start to avoid F4 regression).
- Do NOT apply MFRNP Poisson5 loss weights uniformly to Heat in H4 (gate by dataset; default uniform on Heat).
- Do NOT use `val_frac=0.2` (both hypotheses mandate `val_frac=0.1`).
- Do NOT skip per-fidelity output normalization in H3.
- Do NOT use the full IFC neural ODE in H3's basis head (use cheap MLP `B(m)=MLP_B([m,m²])`).
- Do NOT modify any fixed surface (`data/**, baselines/**, eval/**, references/**, factory.md, README.md, scripts/**`).
- Do NOT download external weights or call external APIs at eval time.
- Do NOT copy from `references/v9_baseline/` (Guard L15: implement from source papers).

## No new backlog items this cycle

Researcher R1.5 surfaced 7 new 2024-2026 papers (`xing2020deepcoreg`, `lin2024continuar`, `davis2025rmfnn`, `hu2025hufno`, `wen2022ufno`, `rahman2025adaptfno`, `fno_resnet_2024`) — flagged for human append to `papers_summary.csv` (fixed surface). Deferred candidates remain on cycle-001 backlog or wait for cycle 003+.

## Links

- [[research-cycle-002]] — Researcher R1.5 Mode-4 findings (hybrid novelty + Poisson 4-lever decomposition).
- [[failure-analysis-cycle-002]] — F1/F2/F3/F4/F5 taxonomy.
- [[cycle-001-summary]] — cycle 001 close-out (H1 composite 0.10919 / H2 composite 0.11173).
- [[cycle-001-strategy]] — cycle 001 H1+H2 plan.
- [[factory_mffp-001-experiment]] — H1 outcome (CEO KEEP).
- [[factory_mffp-002-experiment]] — H2 outcome (CEO KEEP).
- Source papers (cited in H3 INSPIRATION.md): [[xing2020deepcoreg]], [[li2022ifc]], [[niu2024mfrnp]], [[li2020fno]].
