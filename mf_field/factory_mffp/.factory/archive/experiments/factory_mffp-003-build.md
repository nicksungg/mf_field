---
name: factory_mffp-003-build
description: H4 fno_mf_stack v2 — Builder phase. Capacity bump (hidden 16→32, modes (4,5,5,5)→(4,8,12,12), 2→3 blocks) + per-fidelity loss weighting (HF=2.0/LF=0.25, Poisson-gated). model.py byte-identical to H2. Pre-flight CPU smoke on heat + poisson both finite. CEO + Reviewer PROCEED.
metadata:
  type: project
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-002
  - build
project: factory_mffp
experiment_id: "003"
phase: build
verdict: PROCEED
date: 2026-05-15
source: factory-archivist
---

# Experiment #003 — Build phase: H4 `fno_mf_stack` v2 (capacity + Poisson-loss bump)

## Hypothesis

Two pre-registered MFRNP `Poisson5_config.yaml` knobs applied on top of the
H2 `fno_mf_stack` baseline (composite 0.11173 @ R4), with `model.py` UNTOUCHED
to keep the experiment a clean one-axis diagnostic of capacity + loss
weighting:

1. **Capacity bump**: `SMOKE_DEFAULTS` `hidden` 16 → 32, `agg_hidden` 16 → 32,
   `modes_per_level` `(4,5,5,5)` → `(4,8,12,12)`, `n_blocks` 2 → 3 — closes
   the cycle-001 H2 anti-pattern where smoke ran at 1/49 the full-config
   parameter count (which under-fit Heat at 200 epochs).
2. **Per-fidelity loss weighting**: HF=2.0, LF=0.25 (verbatim MFRNP
   `Poisson5_config.yaml`, 8× HF up-weighting), gated to Poisson only —
   Heat's published `pde_config.yaml` uses uniform 1.0/1.0, so we mirror that
   gating by dataset name.

Target: F1 (Poisson value-scale residual, 0.0979 → 0.036 paper bar = 4-lever
gap; this addresses the capacity + LF-down-weighting levers; epochs and basis
K are left for future cycles). Composite expected ≈ 0.05 (CEO Strategist
target).

## Branch + commit

- **Branch**: `experiment/3-fno_mf_stack_v2_capacity_loss` (based on
  `experiment/2-fno_mf_stack`).
- **Single new commit**: `ddd221d` — "H4: fno_mf_stack capacity +
  Poisson-loss bump (cycle 002)".
- **Chain**: master ← H2 (`294d96a`, `73e492d`) ← H4 (`ddd221d`).
- `--no-github` honored (no push, no PR creation).

## What the Builder produced

`git diff --stat experiment/2-fno_mf_stack..experiment/3-fno_mf_stack_v2_capacity_loss`:

| File                                 | Lines    | Purpose                              |
|---                                   |---       |---                                   |
| `models/fno_mf_stack/smoke_eval.py`   | +47/-14  | Capacity + loss-weight wiring        |
| `models/fno_mf_stack/full_config.json`| +6/-2    | Mirror knobs + provenance doc        |
| `models/fno_mf_stack/INSPIRATION.md`  | +12/-0   | H4 provenance paragraph              |
| **Total**                            | **+66/-14, 3 files** |                          |

**Critical non-change**: `model.py` is **byte-identical to H2** (verified via
`git diff` returning empty). `manifest.json` untouched. The architecture is
unchanged — this experiment isolates capacity + loss weighting from inductive
bias.

## Knob 1 — Capacity bump (`smoke_eval.py:34-44`)

```python
SMOKE_DEFAULTS = dict(
    ...
    hidden=32,                          # was 16
    agg_hidden=32,                      # was 16
    n_blocks=3,                         # was 2
    modes_per_level=(4, 8, 12, 12),     # was (4, 5, 5, 5)
    ...
)
```

`SMOKE_DEFAULTS` is now an explicit scaled-down mirror of `full_config.json`
(full uses `hidden=64`; same `modes`, same `n_blocks`). This directly
addresses the cycle-001 patterns.md anti-pattern "smoke_eval.py may not
consume full_config.json" by sizing the smoke config close to the full
architecture shape.

## Knob 2 — Per-fidelity loss weighting (`smoke_eval.py:142-148, 60-104, 240-243`)

```python
def resolve_fidelity_weights(dataset_name: str, p: dict) -> tuple[float, float]:
    is_poisson = "poisson" in (dataset_name or "").lower()
    if is_poisson:
        return float(p["poisson_hf_weight"]), float(p["poisson_lf_weight"])  # (2.0, 0.25)
    return 1.0, 1.0
```

- **Order of operations (verified)**: targets are first divided by
  `scaler_tensor[k]` (per-fidelity output normalization), MSE is then computed
  on the normalized residual, and only then multiplied by `hf_fid_weight` /
  `lf_fid_weight`. Weighting acts on **already-normalized** losses, matching
  MFRNP's published formulation.
- **HF weighting scope**: `hf_fid_weight` multiplies both `loss_hf` (the
  residual `δ` loss at m=1) **and** `loss_base` (the baseline anchor at m=1).
  Both live at m=1 fidelity, so this is faithful to "fidelity-index-keyed
  weighting" (Reviewer subtle catch, non-blocking).
- Implementation in `smoke_eval.py` (not `data.py`) — explicitly authorized
  by the H4 hypothesis card ("Builder's choice"); wiring lives next to the
  loss computation, the cleanest place for it.

## Pre-flight CPU smoke verification

Builder ran `--epochs 2` on both target datasets. Both produced finite
`metric_value` and contract-compliant JSON. Gating verified by printed
`[loss-weights]` line:

| Dataset        | `[loss-weights]` line                                          | Outcome                  |
|---             |---                                                             |---                       |
| `ifc_heat`      | `hf_fid_weight=1.0 lf_fid_weight=1.0` (uniform, gating off)     | finite metric_value      |
| `ifc_poisson`   | `hf_fid_weight=2.0 lf_fid_weight=0.25` (gating fires)           | finite metric_value      |

These are sanity-only — the 200-epoch H100 SLURM run via `bash scripts/cycle_eval.sh`
is the actual decision signal. Cache will MISS on `models/fno_mf_stack/`
(smoke_eval.py changed → new code_hash); v9 (under `references/`) will hit
cache. Expected wall: 5–10 min H100.

## Hard-gate results

1. **Surface scope** (`git diff --name-only experiment/2-fno_mf_stack..experiment/3-fno_mf_stack_v2_capacity_loss`):
   3 files, ALL under `models/fno_mf_stack/`. No fixed-surface modifications
   (no `data/`, `baselines/`, `eval/`, `references/`, `scripts/`, `factory.md`,
   `README.md`, no other `models/` families). **PASS.**
2. **Anti-pattern guard**: `model.py` byte-identical (`git diff` returns 0
   bytes). `manifest.json` untouched. No architectural change. **PASS.**
3. **Sacred Rules** (all PASS, Reviewer verified):
   - No deleted tests (`git diff --diff-filter=D` empty)
   - No fixed-surface diff lines
   - No secrets / credentials / external API calls
   - No `eval/` threshold change
4. **Scope clean** via `factory guard --check-scope`: `clean`,
   `eval_immutable=PASS`, `git_clean=PASS`, `experiment_branch=PASS`.
5. **Knob 1 verified in diff**: hidden, agg_hidden, n_blocks, modes_per_level
   all updated as specified (Reviewer cited `smoke_eval.py:36-44`).
6. **Knob 2 verified in diff**: `resolve_fidelity_weights()` gating + order
   of operations correct (Reviewer cited `smoke_eval.py:142-148`).
7. **INSPIRATION.md provenance**: 12 new lines documenting both knobs;
   explicit reference to MFRNP `Poisson5_config.yaml` (8× HF up-weighting,
   Poisson-only gating) and the published Heat `pde_config.yaml` (uniform).

## Reviewer & CEO sign-off

- **CEO verdict** (`.factory/reviews/ceo-verdict-builder.md`, 2026-05-15):
  **PROCEED**, no issues found. One observation noted (loss wiring in
  `smoke_eval.py` not `data.py` — explicitly authorized by the hypothesis
  card).
- **Reviewer verdict** (`.factory/reviews/ceo-verdict-reviewer.md`,
  2026-05-15): **PROCEED**. Substantive multi-section review with line-cited
  acceptance criteria; ran `factory guard --check-scope` (clean PASS), read
  the diff, verified `model.py` byte-identical, verified loss-weight
  order-of-operations. Caught the subtle "`hf_fid_weight` also multiplies
  `loss_base`" detail — non-blocking, faithful to fidelity-index-keyed
  weighting.
- **Both unanimous PROCEED**. Awaiting R4 evaluator for the gate score.

## Pending (R4)

- 200-epoch H100 SLURM run via `bash scripts/cycle_eval.sh` on
  `experiment/3-fno_mf_stack_v2_capacity_loss`. Cycle_eval.sh cache will
  MISS for `fno_mf_stack` (smoke_eval.py content changed → new code_hash);
  v9 will hit cache. Expected wall 5–10 min H100.
- **R5 verdict logic**: monotonic check is `metric_after <= previous_best`.
  `previous_best` on master is **1.6595** (the cycle-002 baseline; H1 and H2
  are not merged). The cycle-001 H2 result (0.11173) serves as a CEO
  sanity-check reference but NOT the monotonic gate. CEO will compute and
  report both deltas in the verdict.
- The H1/H2 precheck `score_direction` polarity bug is known — CEO will
  inspect the precheck JSON and override if it transparently fails only on
  `score_direction` with the actual metric clearly improved.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle strategy: [[cycle-002-strategy]]
- Sibling H2 build (parent branch): [[factory_mffp-002-build]]
- Sibling H2 outcome (baseline for this experiment): [[factory_mffp-002-experiment]]
- Research note: [[research-cycle-002]] — Poisson 4-lever decomposition,
  MFRNP Poisson5 knobs as free pre-registered levers
- Failure analysis: [[failure-analysis-cycle-002]] — F4
  `SMOKE_DEFAULT_UNDER_CAPACITY` (directly addressed by Knob 1)
- Source papers: [[niu2024mfrnp]] (Poisson5_config.yaml provenance for both
  knobs), [[li2020fno]] (spectral conv backbone, unchanged from H2)
- Commit: `ddd221d` on branch `experiment/3-fno_mf_stack_v2_capacity_loss`
- Diff: `experiment/2-fno_mf_stack..experiment/3-fno_mf_stack_v2_capacity_loss`
  (+66 / −14, 3 files; model.py byte-identical)
