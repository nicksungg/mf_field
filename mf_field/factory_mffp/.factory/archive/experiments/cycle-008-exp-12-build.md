---
name: cycle-008-exp-12-build
description: Cycle-008 H2 (exp 12) — Builder + CEO PROCEED phase. NEW family `fno_coreg_conditioned/` added under `models/`; FiLM-via-LayerNorm on a single full-resolution HF FNO. Branch `experiment/12-fno_coreg_conditioned-film @ 540e684` cut from cycle-008 entry baseline `1249f2d` (cycle-007 H1 anisotropic-modes constructor fix) — **branched independently of H1's `experiment/11` branch per Strategist's R2 H1/H2/H3-must-be-independent-branches anti-pattern**. 4 NEW files all under `models/fno_coreg_conditioned/`, zero existing-family edits (`fno_coregionalization`, `fno_coreg_residual`, `fno_mf_stack`, `mf_fno_transfer_bar`, transolver* all byte-identical to `1249f2d`): `model.py` (218 LOC — `FNOCoregConditioned` class + `FiLMNorm` = `GroupNorm(affine=False) + MLP([m, m²]) → 2·C → γ, β` with zero-init γ-projection so γ ≈ 1 / β ≈ 0 at init; constructor signature mirrors cycle-007 H1 anisotropic-modes pattern — positional `modes` accepts int OR `(modes_h, modes_w)` tuple), `smoke_eval.py` (517 LOC — copied verbatim from `fno_coregionalization/smoke_eval.py` at `1249f2d` baseline with H2 LF→HF schedule fields preserved: `pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`; `SMOKE_DEFAULTS` knobs: K/b_hidden removed, `m_feat_dim=32` added, `hidden_channels=64`, `n_blocks=4` — bar's trunk capacity, not H1's paper bump), `manifest.json` (6 lines — `supports: ["ifc_raw"]`, `frozen: false`), `INSPIRATION.md` (87 lines — 5 bibtex_keys cited: `li2022ifc`, `li2020fno`, `lyu2023mffno`, `beggs2025pdecond`, `herde2024poseidon`). Mode A (FiLM-via-LayerNorm) succeeded — no Mode B fallback needed. Pre-flight smoke verification on BOTH datasets per research-constraint: `ifc_heat` 4,757,121 params 2.04 s for 2-epoch / 222 MB peak → ~3.4 min projection 200 epochs; `ifc_poisson` 4,757,249 params 1.61 s for 2-epoch / 222 MB peak → ~2.7 min projection 200 epochs; combined ~6 min total smoke well below 25-min kill-switch cap. Leakage scanner reported HIGH (4 findings: `satisfy`, `description`, `ifc_raw`, `frozen`) — CEO OVERRIDDEN as documented bookkeeping bug; all 4 tokens are substring collisions with required manifest schema fields (per `eval/MODEL_CONTRACT.md` — `description` + `frozen` are REQUIRED JSON manifest fields; `ifc_raw` is REQUIRED by research_constraints field 4 "New families must support at least the ifc_raw dataset loader") or generic English (`satisfy` in code comment AND `README.md`). This is the **5th consecutive operator-flagged 'leakage substring collision' bookkeeping bug** at Builder phase (the specific name pinned in cycle-007 standup); CEO override is consistent with documented `revert_bookkeeping_keep_intent` precedent established cycles 005-008. `--no-github` honored (no push, no PR, no issue).
metadata:
  type: experiment
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-008
  - build
  - h2
  - fno_coreg_conditioned
  - new-family
  - film-via-layernorm
  - li2022ifc
  - li2020fno
  - lyu2023mffno
  - beggs2025pdecond
  - herde2024poseidon
project: factory_mffp
experiment_id: "012"
cycle: cycle-008
hypothesis_id: H2
phase: build
verdict: PROCEED
ceo_verdict_builder: PROCEED
ceo_verdict_builder_override_class: leakage_substring_collision
ceo_verdict_builder_override_count_consecutive: 5
date: 2026-06-02
branch: experiment/12-fno_coreg_conditioned-film
parent_branch: cycle-008-entry-baseline
parent_commit: 1249f2d
parent_commit_source: cycle-007 H1 (anisotropic-modes constructor fix)
branch_independence_from_h1: true
branch_independence_note: "branched from 1249f2d independent of H1's experiment/11 branch per Strategist R2 H1/H2/H3-must-be-independent-branches anti-pattern (anti-pattern #3 — bundling FORBIDDEN)"
commit: 540e684
commit_message: "feat(fno_coreg_conditioned): NEW family — FiLM-via-LayerNorm on single HF FNO (cycle-008 H2)"
files_changed: 4
files_changed_all_new: true
files_changed_loc_total: 828
files_changed_loc_delta: "+828/-0"
files_under_new_family_dir: true
new_family_dir: models/fno_coreg_conditioned/
existing_family_files_modified: 0
model_py_loc: 218
smoke_eval_py_loc: 517
manifest_json_loc: 6
inspiration_md_loc: 87
mode_a_succeeded: true
mode_b_fallback_used: false
film_implementation: "FiLMNorm = GroupNorm(affine=False) + MLP([m, m²]) → 2·C → γ, β with zero-init γ-projection (γ ≈ 1, β ≈ 0 at init)"
gamma_projection_zero_init: true
beta_projection_zero_init: true
constructor_signature_pattern: "cycle-007 H1 anisotropic-modes — positional modes accepts int OR (modes_h, modes_w) tuple"
single_hf_fno_architecture: true
multi_fidelity_fno_count_in_model: 1
h2_lf_hf_schedule_preserved_verbatim: true
h2_pretrain_lr: 0.001
h2_finetune_lr: 0.0003
h2_pretrain_frac: 0.25
smoke_defaults_hidden_channels: 64
smoke_defaults_n_blocks: 4
smoke_defaults_m_feat_dim: 32
smoke_defaults_K_removed: true
smoke_defaults_b_hidden_removed: true
smoke_defaults_trunk_capacity_source: mf_fno_transfer_bar (bar's trunk, NOT cycle-008 H1's paper bump)
smoke_2ep_dataset_heat: ifc_heat
smoke_2ep_dataset_poisson: ifc_poisson
smoke_2ep_heat_params: 4757121
smoke_2ep_heat_train_seconds: 2.04
smoke_2ep_heat_peak_mem_mb: 221.7
smoke_2ep_heat_200ep_projection_min: 3.4
smoke_2ep_poisson_params: 4757249
smoke_2ep_poisson_train_seconds: 1.61
smoke_2ep_poisson_peak_mem_mb: 221.7
smoke_2ep_poisson_200ep_projection_min: 2.7
smoke_200ep_projection_min_total: 6
smoke_kill_switch_cap_min: 25
smoke_kill_switch_headroom_pct: 76
smoke_warmup_change_needed: false
smoke_epochs_kept: 200
leakage_check_diff_flagged: true
leakage_check_diff_risk_level: HIGH
leakage_check_diff_findings_count: 4
leakage_check_diff_findings: "satisfy, description, ifc_raw, frozen"
leakage_check_diff_override_applied: true
leakage_check_diff_override_rationale: "substring collisions with REQUIRED manifest schema fields (description, frozen) per eval/MODEL_CONTRACT.md, REQUIRED supports value (ifc_raw) per research_constraints field 4, and generic English (satisfy) appearing in both diff code comment and README.md"
leakage_check_substring_collision_consecutive_count: 5
leakage_check_substring_collision_first_named_in: cycle-007 standup
inspiration_bibtex_keys: "li2022ifc, li2020fno, lyu2023mffno, beggs2025pdecond, herde2024poseidon"
inspiration_bibtex_keys_count: 5
surface_guard_baseline: 1249f2d
surface_guard_check_scope: clean
surface_guard_fixed_surfaces_touched: false
surface_guard_existing_family_files_touched: false
readme_md_edited: false
factory_md_edited: false
model_contract_md_edited: false
papers_summary_csv_edited: false
papers_summary_csv_present_in_tree: false
papers_summary_csv_present_in_tree_note: "references/papers_summary.csv NOT present in-tree → no fixed-surface append triggered for INSPIRATION.md bibtex_keys"
no_github_mode: true
no_pr_created: true
no_push: true
no_issue_created: true
gh_calls: 0
git_push_calls: 0
source: factory-archivist
---

# Experiment #012 — Build phase: Cycle-008 H2 NEW family `fno_coreg_conditioned` (FiLM-via-LayerNorm)

## Hypothesis

**Cycle-008 H2 — EXPLORE, MEDIUM-HIGH priority, highest swing-EV, NEW family.** Build a new model family `models/fno_coreg_conditioned/` that conditions a **single full-resolution HF FNO** on the **mean LF feature vector** via FiLM-style affines folded into LayerNorm (GroupNorm w/ no affine + MLP-driven γ, β). No coregionalization basis-head matrix, no residual stack, no per-fidelity FNO ladder — a third architectural axis distinct from cycle-007 H1's repaired-coregionalization and cycle-006's failed residual recipe. Architecture composes 5 papers:
- `li2022ifc` (the IFC dataset / paper-target context),
- `li2020fno` (single full-res FNO backbone),
- `lyu2023mffno` (multi-fidelity conditioning of FNO architectures),
- `beggs2025pdecond` (FiLM-style PDE conditioning as the affine-injection mechanism),
- `herde2024poseidon` (large-scale PDE-foundation precedent for FiLM-via-LayerNorm composition).

Expected impact (per cycle-008 Strategist R2):
- Highest swing-EV among the three hypotheses; biggest expected variance around the projection band.
- `fno_coreg_conditioned × ifc_poisson` is the primary target — single full-res HF FNO with LF conditioning is the architecture most plausibly able to win Poisson at composite-meaningful margin (current Poisson winner `fno_mf_stack @ 0.05961` is a residual-stack, not coregionalization-class; conditioned single-FNO is a third path).
- Composite target: ≤ 0.028 (matching cycle-008 H1 hard target band).
- Kill-switch: combined smoke wall > 25 min/cell on first SLURM run → drop epochs 200 → 120 with cosine warmup.

## Branch + commit

- **Branch**: `experiment/12-fno_coreg_conditioned-film`.
- **Base**: `1249f2d` directly (cycle-008 entry baseline — the cycle-007 H1 anisotropic-modes constructor fix; current reproducible project best @ composite 0.030408). **Branched independently of `experiment/11-fno_coregionalization-paper-capacity` per Strategist R2** — H1/H2/H3 are mandated to be independent branches off the same baseline, NOT chained, so each hypothesis can be evaluated and kept/reverted on its own evidence without bundling-induced confounders.
- **Single new commit**: `540e684` — `feat(fno_coreg_conditioned): NEW family — FiLM-via-LayerNorm on single HF FNO (cycle-008 H2)`.
- **Chain**: `1249f2d` (c007 H1 constructor fix; cycle-008 entry baseline) ← `540e684` (this H2). Note this chain is **shorter than H1's chain** because H2 does NOT inherit from `be36cba` (cycle-005 H2 schedule) through the `fno_coregionalization` family — H2 ships a NEW family with the LF→HF schedule re-implemented inside its own `smoke_eval.py`.
- **GitHub**: no PR, no push (`--no-github` honored — zero `gh` calls, zero `git push` calls).

## What the Builder produced

`git diff --stat 1249f2d 540e684`:

| File | Lines | Purpose |
|---|---:|---|
| `models/fno_coreg_conditioned/model.py` | **+218 / −0** | NEW. `FNOCoregConditioned` class (single full-res HF FNO), `FNOBlock` with `FiLMNorm` replacing standard `GroupNorm`. `FiLMNorm` = `GroupNorm(affine=False) + MLP([m, m²]) → 2·C → γ, β`. γ-projection zero-init (γ ≈ 1, β ≈ 0 at start). Constructor signature mirrors cycle-007 H1 anisotropic-modes pattern (positional `modes` accepts int OR `(modes_h, modes_w)` tuple) per `models/mf_fno_transfer_bar/model.py:62-94`. |
| `models/fno_coreg_conditioned/smoke_eval.py` | **+517 / −0** | NEW. Copied verbatim from `models/fno_coregionalization/smoke_eval.py` at `1249f2d` baseline (so the H2 LF→HF two-stage schedule lands intact). `SMOKE_DEFAULTS` modifications: K removed, b_hidden removed (no coregionalization basis-head), `m_feat_dim=32` added (FiLM conditioner input width), `hidden_channels=64` (bar's trunk capacity, NOT cycle-008 H1's paper bump to 128), `n_blocks=4` (bar's trunk depth, NOT H1's paper bump to 6). H2 LF→HF schedule fields (`pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`) preserved verbatim. |
| `models/fno_coreg_conditioned/manifest.json` | **+6 / −0** | NEW. Required schema: `name`, `description`, `supports: ["ifc_raw"]`, `frozen: false`. Honors research-constraints field 4 ("New families must support at least the `ifc_raw` dataset loader"). |
| `models/fno_coreg_conditioned/INSPIRATION.md` | **+87 / −0** | NEW. Paragraph on FiLM-via-LayerNorm composition. 5 bibtex_keys cited: `li2022ifc`, `li2020fno`, `lyu2023mffno`, `beggs2025pdecond`, `herde2024poseidon`. NOTE: `references/papers_summary.csv` is **not present in-tree** (verified by Builder), so no fixed-surface append was triggered for the bibtex registration. |
| **Total** | **+828 / −0, 4 files** | All under `models/fno_coreg_conditioned/`; zero existing-family / fixed-surface modifications |

**Existing-family files byte-preserved against `1249f2d`** (per Strategist R2 anti-pattern #3 — H1/H2/H3 must be independent branches with zero file overlap):
- `models/fno_coregionalization/**` — UNTOUCHED. Cycle-008 H1's capacity bump exists on `experiment/11-fno_coregionalization-paper-capacity`, not here. H2's branch sees the `1249f2d` baseline of `fno_coregionalization`.
- `models/fno_coreg_residual/**` — UNTOUCHED. (Cycle-008 H3 target surface; not modified by H2.)
- `models/fno_mf_stack/**` — UNTOUCHED. (Poisson leaderboard holder; preserved.)
- `models/mf_fno_transfer_bar/**` — UNTOUCHED. (Bar reference; preserved.)
- `models/transolver/**`, `models/transolver_lite/**` — UNTOUCHED.
- `README.md`, `factory.md`, `eval/MODEL_CONTRACT.md` — UNTOUCHED (CEO line-by-line diff verification).

**H2 LF→HF schedule preserved verbatim** (banked from cycle-005 H2 / cycle-007 H1, copied through into the new family's smoke_eval.py): `pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25` SMOKE_DEFAULTS keys are byte-identical to the cycle-007 H1 `fno_coregionalization/smoke_eval.py` baseline. The two-stage outer loop in `run()` is copied through verbatim. The new family composes on top of the already-banked schedule rather than re-discovering it.

## Mechanism — FiLM-via-LayerNorm (Mode A succeeded; no fallback needed)

The architectural innovation is folding FiLM conditioning into LayerNorm itself, so the conditioning signal modulates every block's normalization affines rather than being applied as a separate add-on layer. The `FiLMNorm` module:

```python
class FiLMNorm(nn.Module):
    def __init__(self, channels, m_feat_dim, groups=8):
        super().__init__()
        # affine=False — γ, β come from the conditioner, not learnable scalars
        self.gn = nn.GroupNorm(num_groups=groups, num_channels=channels, affine=False)
        # MLP([m, m²]) → 2C; zero-init the γ-projection so γ ≈ 1, β ≈ 0 at init
        self.mlp = nn.Sequential(
            nn.Linear(m_feat_dim, 2 * m_feat_dim),
            nn.GELU(),
            nn.Linear(2 * m_feat_dim, 2 * channels),
        )
        nn.init.zeros_(self.mlp[-1].weight)
        nn.init.zeros_(self.mlp[-1].bias)

    def forward(self, x, m):
        # x: (B, C, H, W); m: (B, m_feat_dim) — mean LF feature vector
        x_norm = self.gn(x)
        gamma_delta, beta = self.mlp(m).chunk(2, dim=-1)
        gamma = 1.0 + gamma_delta  # γ ≈ 1 at init (zero-init of γ projection)
        return gamma[:, :, None, None] * x_norm + beta[:, :, None, None]
```

**Why Mode A succeeded** (no Mode B fallback to standalone FiLM layers needed): the GroupNorm-without-affine baseline already provides a numerically stable normalized signal, and the zero-init γ-projection means at initialization the network behaves identically to a plain GroupNorm-with-affine-1 baseline FNO — so the additional capacity is "free" at init (no training instability). Mode B would have been a separate post-block `FiLM = γ * x + β` layer if Mode A had shown init instability; the smoke confirmed Mode A is clean.

**Conditioner input** (`m`): mean LF feature vector — the LF FNO trunk runs first (Stage 1), and its block-output features are spatially mean-pooled to produce an `m_feat_dim=32` vector per sample. This vector then drives every `FiLMNorm` in the HF FNO (Stage 2) via the MLP. The architecture has **a single HF FNO** — distinct from `fno_coregionalization` (K-basis coregionalization head over per-fidelity FNOs), `fno_coreg_residual` (residual decoder over per-fidelity FNOs), `fno_mf_stack` (fidelity ladder of FNOs).

## Constructor signature — anisotropic modes pattern from cycle-007 H1

The new `FNOCoregConditioned.__init__` mirrors the cycle-007 H1 repaired constructor in `models/fno_coregionalization/model.py:83-128`, which itself follows the canonical pattern from `models/mf_fno_transfer_bar/model.py:62-94`. The positional `modes` argument accepts either:
- an `int` (isotropic — interpreted as `(modes, modes)`), or
- a `(modes_h, modes_w)` tuple (anisotropic — explicit per-axis).

This signature inherits the [[anisotropic-spectral-modes-fno]] research finding (cycle-007 R1.5: Li 2020 FNO + Tran 2023 F-FNO canonical `(modes_h, modes_w)` parameterization) without re-discovering it.

## Pre-flight verification — PASSED on BOTH datasets

Builder ran the mandatory smoke check per CEO/Strategist contract on **both** datasets (per research-constraints: "New families must support at least the `ifc_raw` dataset loader" — and `ifc_raw` covers both `ifc_heat` and `ifc_poisson`):

```bash
factory <cmd> smoke_eval.py --epochs 2 --dataset_dir data/ifc_heat \
    --out /tmp/h2_smoke_heat.json --ckpt_dir /tmp/h2_ckpt_heat --seed 0
factory <cmd> smoke_eval.py --epochs 2 --dataset_dir data/ifc_poisson \
    --out /tmp/h2_smoke_poisson.json --ckpt_dir /tmp/h2_ckpt_poisson --seed 0
```

| Metric                  | ifc_heat        | ifc_poisson     | Interpretation |
|---                      |---:             |---:             |--- |
| `train_seconds` (2ep)   | **2.04**        | **1.61**        | ~1.0 s/epoch and ~0.8 s/epoch on H100 — bar-trunk-class speed |
| `params`                | **4,757,121**   | **4,757,249**   | ~4.76M params (small differential is the per-dataset coord-grid embedding) — order-of-magnitude consistent with `hidden_channels=64`, `n_blocks=4`, `m_feat_dim=32`, single HF FNO trunk; **~10× smaller than cycle-008 H1's 50.47M** because H2 uses bar's trunk capacity, not paper-bump capacity |
| `peak_mem`              | **221.7 MB**    | **221.7 MB**    | Tiny memory footprint on H100 (~0.7% of H1's 1.73 GB) |
| **200-epoch projection**| **~3.4 min**    | **~2.7 min**    | Per-cell |
| **Combined 200-ep wall**| **~6 min**      |                 | Total smoke — **76% headroom** under 25-min kill-switch cap |
| exit                    | 0               | 0               | end-to-end successful on both datasets |

**Decision: kept `epochs=200` (no warmup change needed).** The 25-min wall-budget kill-switch was not triggered with massive headroom (~76%). H2 is the fastest-smoke hypothesis in cycle-008 by a large margin: combined smoke wall ~6 min vs H1's ~14-15 min. If R4 SLURM-side timing tracks the H100-smoke prediction, H2 leaves room for fairly aggressive R4 retries (or, after R5, a follow-up cycle-009 capacity-bump on the same family).

**2-epoch values are diagnostic only** — best_val_nRMSE numbers are not the R4 leaderboard signal. What the 2-epoch smoke proves is:

1. **End-to-end runs on both datasets** (no `TypeError`, no shape mismatch, no OOM, no NaN at init). The 4 NEW files compose correctly through the factory CLI on the `ifc_raw` loader path.
2. **FiLMNorm init is stable** (no Mode B fallback needed): the zero-init γ-projection means the network at step 0 behaves as a plain GroupNorm-affine-1 FNO, so the first forward pass produces finite logits and the first backward pass produces finite gradients on both PDE classes.
3. **The H2 LF→HF schedule still runs**: the 2-epoch run with `pretrain_frac=0.25` gives `n_warmup=0` and skips Stage 1, but Stage 2 alone completes both epochs — same diagnostic mode as cycle-005 H2's `--epochs 2`. Architecture/schedule compose without surprise interactions on either PDE class.
4. **Wall-time projection comfortably under kill-switch cap** on both PDE classes independently.

The full 200-epoch numbers will land at R4 via `bash scripts/cycle_eval.sh` on `experiment/12-fno_coreg_conditioned-film` (cache MISS expected on BOTH `fno_coreg_conditioned × ifc_heat` AND `fno_coreg_conditioned × ifc_poisson` — these are new cells the cache has never seen). Existing families' cells should cache-hit (all 8 existing families × 2 datasets = 16 cells) because their source bytes are unchanged from `1249f2d`.

## Hard-gate results (CEO PROCEED — with leakage-bug override)

- **Surface guard**: `factory guard --baseline 1249f2d --check-scope` → diff-name-only shows 4 NEW files all under `models/fno_coreg_conditioned/`, zero existing-family modifications, zero fixed-surface modifications.
- **NEW-family constraint** (cycle-008 Strategist H2 spec — must be a NEW family at `models/fno_coreg_conditioned/`, NOT an edit to any existing family): satisfied. All 4 files are NEW and under the new family directory.
- **Anti-pattern #3 — independent branches** (H1/H2/H3 must NOT be bundled — must be independent branches off the same baseline): satisfied. H2 is on `experiment/12-fno_coreg_conditioned-film` cut from `1249f2d` directly, NOT from `experiment/11`. Zero file overlap with H1's mutable surface.
- **Diff matches hypothesis exactly** (CEO line-by-line verification in `.factory/reviews/ceo-verdict-builder.md`):
  - 4 NEW files: `model.py`, `smoke_eval.py`, `manifest.json`, `INSPIRATION.md` — ALL under `models/fno_coreg_conditioned/` ✓
  - `FNOCoregConditioned` class with `FiLMNorm` = `GroupNorm(affine=False) + MLP([m, m²]) → 2C → γ, β` with zero-init γ-projection ✓
  - Constructor signature mirrors cycle-007 H1 anisotropic-modes pattern (positional `modes` accepts int or tuple) ✓
  - H2 LF→HF schedule fields (`pretrain_lr=1e-3`, `finetune_lr=3e-4`, `pretrain_frac=0.25`) preserved verbatim ✓
  - Single full-res HF FNO architecture (NOT a per-fidelity ladder, NOT a coregionalization head, NOT a residual stack) ✓
  - 5 bibtex_keys cited in INSPIRATION.md (`li2022ifc`, `li2020fno`, `lyu2023mffno`, `beggs2025pdecond`, `herde2024poseidon`) ✓
- **Ground-truth leakage scan**: HIGH (4 findings) — **OVERRIDDEN as documented bookkeeping bug**. All four flagged tokens are demonstrably substring collisions with REQUIRED manifest/schema fields or generic English, NOT ground-truth leakage:
  1. `"satisfy"` — generic English word. Appears in our `smoke_eval.py` comment ("checkpoint MUST not satisfy this guard"); the same word also appears in `README.md`'s sentence "contract every model family must satisfy". Not a value, not a paper-baseline number, not anything from `data/**`.
  2. `"description"` — REQUIRED JSON manifest schema field per `eval/MODEL_CONTRACT.md` (the contract line reads `{ "name": str, "description": str, "supports": ["ifc_raw", "npz"] }`). Excluding the `description` key from the manifest would make the contract invalid; the token is structural, not informational.
  3. `"ifc_raw"` — **REQUIRED by research_constraints field 4** ("New families must support at least the `ifc_raw` dataset loader"); explicitly named in `eval/MODEL_CONTRACT.md` as the required `supports` array value. Including `ifc_raw` is not optional and not leakage — it is the mandated dataset-loader name.
  4. `"frozen"` — REQUIRED JSON manifest schema field (mirrors `fno_coregionalization/manifest.json` and every other family's `manifest.json` — `frozen: bool` is one of the contract fields).

  CEO confirmed via diff-name-only verification: Builder did NOT modify `README.md`, `factory.md`, or `eval/MODEL_CONTRACT.md`. No ground-truth-derived logic embedded in code. Architecture is FiLM-via-LayerNorm composition from first principles + 5 cited papers (`li2022ifc + li2020fno + lyu2023mffno + beggs2025pdecond + herde2024poseidon`). This is the **5th consecutive operator-flagged 'leakage substring collision' bookkeeping bug** at Builder phase — the specific name pinned in the cycle-007 standup. The override is consistent with the `revert_bookkeeping_keep_intent` precedent established cycles 005, 006, 007 (and 008 H1's earlier-today scan, which also produced a clean diff-level scan — though H2's diff trips on the new family's manifest.json + new family's smoke_eval.py copy-through of the same schema tokens).
- **`--no-github` mode**: satisfied. No `gh` calls, no `git push`, no PR, no issue.
- **Smoke verification end-to-end PASS on BOTH datasets**: confirmed (combined ~6 min wall projection, 4.76M params, 222 MB peak, well under the 25-min kill-switch cap with 76% headroom).

## Surface modifications outside hypothesis-declared scope

**None.** All 4 NEW files are under `models/fno_coreg_conditioned/`, which is the NEW family directory explicitly declared by the Strategist as the mutable surface for H2. The `references/papers_summary.csv` (a fixed surface that would normally need an append for the 2 cited `beggs2025pdecond` + `herde2024poseidon` bibtex_keys) is **not present in-tree** in the cycle-008 baseline `1249f2d` — verified by Builder via direct `ls` — so the conditional append rule did not trigger. INSPIRATION.md cites the keys; no fixed surface modification is required by the contract.

## Implementation notes (carry into R4 interpretation)

- **Cache behavior**: the source bytes for the new family `models/fno_coreg_conditioned/**` are entirely new, so the `__code_hash__` for both `fno_coreg_conditioned × ifc_heat` AND `fno_coreg_conditioned × ifc_poisson` cells will be cache MISS at R4 (the cache has never seen these cells). The other 16 cells (8 existing families × 2 datasets) should cache-hit because their source bytes are unchanged from `1249f2d`. **Important**: H2's R4 will produce 2 fresh evals + 16 cache-hits — same overall structure as H1's R4 (which had 2 cache-misses for `fno_coregionalization` and 14 cache-hits for the rest).
- **Wall budget on R4 SLURM**: smoke wall projection ~6 min total fits comfortably inside the 30-min H100 SLURM-side budget per Strategist R2; both new cells (Heat + Poisson) within the same `scripts/cycle_eval.sh` invocation. **H2 has the most R4 wall-budget headroom of any cycle-008 hypothesis** — useful contingency if R4 timing diverges from H100-smoke prediction.
- **Poisson target**: H2 is the cycle-008 Poisson lever (where H1 was the Heat lever). Single full-res HF FNO with FiLM-LayerNorm conditioning is the architecture most plausibly able to displace `fno_mf_stack @ 0.05961` from the Poisson leaderboard, because it composes a richer conditioning signal with a higher-capacity HF representation than a residual stack can support. If `fno_coreg_conditioned × ifc_poisson` lands below 0.05961, H2 takes the Poisson leaderboard outright (assuming Heat does not regress past kill-switch).
- **Heat target**: secondary for H2. Current Heat leaderboard holder is cycle-008 H1's `fno_coregionalization @ 0.012898` (if H1 is kept after R4/R5); prior reproducible leader is `fno_coregionalization @ 0.01551` at `1249f2d`. H2 only needs to land Heat ≤ 0.0194 to avoid the kill-switch; any Heat ≤ 0.013 would be a strong-KEEP signal.
- **Composite target**: ≤ 0.028 (matching H1 hard target). With H2's ~10× smaller param count than H1, this is a different bet — capacity-axis is OFF, conditioning-axis is ON. If both H1 AND H2 land cleanly, cycle-009 could ensemble or further compose; if only H2 lands, the FiLM-via-LayerNorm architecture becomes a new family worth exploring at higher capacity in cycle-009.
- **Kill-switches**: 
  - `ifc_heat` nRMSE > 0.0194 → REVERT (the 0.01551 baseline +25% band, same as H1's kill-switch).
  - Smoke wall > 25 min on first SLURM run → drop epochs 200 → 120 with cosine warmup (NOT expected to trigger; projection is ~6 min with 76% headroom).

## Anti-patterns explicitly NOT triggered (all six cycle-008 anti-patterns)

1. **MFRNP loss-recipe / reweighting** (BANNED; 3/3 REVERTs): satisfied — H2 is architecture-class-new with no `hf_loss_weight` / `lf_loss_weights` edits, no MFRNP recipe knobs anywhere in `smoke_eval.py`. Anti-pattern #1.
2. **Per-dataset MFRNP recipe dispatch** (BANNED; cycle-007 H2 REVERT): satisfied — no `_DATASET_RECIPES` dict, no `resolve_fidelity_weights` helper added to the new family's smoke_eval.py. Anti-pattern #2.
3. **H1+H2+H3 bundling** (FORBIDDEN; cycle-008 H1/H2/H3 must be independent branches): satisfied — H2 is on its own branch (`experiment/12-…`) cut from `1249f2d` directly, NOT chained on `experiment/11` (cycle-008 H1's branch). Zero file overlap with H1's or H3's planned mutable surfaces.
4. **D1 (`mf_fno_transfer_bar` smoke-config bump)** (DEFERRED to cycle-009+): satisfied — no edits to `models/mf_fno_transfer_bar/**` (the bar's trunk capacity was *referenced* by H2 as the inspiration for `hidden_channels=64, n_blocks=4` in the new family's smoke_eval.py, but `mf_fno_transfer_bar/**` itself is untouched).
5. **A3 (F-FNO factorized spectral conv refactor)** (DEFERRED to cycle-009+ as `fno_coreg_ffno`): satisfied — no architectural refactor of existing F-FNO; H2 ships standard FNO blocks with FiLMNorm.
6. **`models/fno_coregionalization/model.py` edits for H1** (FORBIDDEN per Strategist R2): N/A for H2 — H2 does not touch `fno_coregionalization/**` at all. Anti-pattern #6 is structurally satisfied by branch isolation.

## CEO sign-off

- **CEO verdict on Builder** (`.factory/reviews/ceo-verdict-builder.md`, 2026-06-02): **PROCEED with explicit leakage-bug override**. Diff matches hypothesis exactly; NEW-family-only surface (4 NEW files all under `models/fno_coreg_conditioned/`); zero existing-family edits; H2 LF→HF schedule preserved verbatim; Mode A succeeded with no Mode B fallback needed; smoke verification PASS on BOTH datasets with combined wall projection well under cap; leakage scanner HIGH override is documented bookkeeping bug class (5th consecutive at Builder phase).
- Architecture is mathematically reasonable (FiLMNorm = `GroupNorm + MLP-driven γ, β affines with zero-init γ-projection`), composes 5 well-established papers, and runs end-to-end on both PDE classes at init.
- Sibling families (`fno_coregionalization`, `fno_coreg_residual`, `fno_mf_stack`, `mf_fno_transfer_bar`, transolver*) untouched. README.md / factory.md / MODEL_CONTRACT.md untouched.
- Ready for **R3-review** (`factory guard --baseline 1249f2d --check-scope`, 4-file diff sanity, FiLMNorm math verification) and **R4** (200-epoch fresh smoke on `experiment/12-fno_coreg_conditioned-film` via `bash scripts/cycle_eval.sh`).

## Pending (R3-review / R4 / R5)

- **R3 Reviewer**: instructions issued in CEO verdict — run `factory guard . --baseline 1249f2d --check-scope`, verify 4 NEW files all under `models/fno_coreg_conditioned/`, verify NO existing family modified, verify FiLMNorm implementation is mathematically reasonable (`GroupNorm + MLP-driven γ, β affines with zero-init γ-projection`), note the leakage scanner will flag false positives — verify the actual diff does not contain ground-truth-derived logic, print PASS or FAIL.
- **R4 200-epoch run** via `bash scripts/cycle_eval.sh` on `experiment/12-fno_coreg_conditioned-film`. Cache MISS expected on **both** `fno_coreg_conditioned` cells (heat + poisson) — they are entirely new cells. Other 16 cells cache-hit.
- **R4 kill-switches**:
  - `ifc_heat` nRMSE > 0.0194 → REVERT (same heat kill-switch as H1).
  - Wall > 25 min on first SLURM run → drop epochs 200 → 120 with cosine warmup (NOT expected to trigger; projection is ~6 min with 76% headroom).
- **R5 verdict logic**:
  - Monotonic check uses **0.030408** as the cycle-008 entry baseline (cycle-007 H1's R4 result; current reproducible project best at the cycle-008 entry). If H1's R4 has already landed and KEPT at the time of H2's R5, the comparison baseline updates to `0.027729` (H1's R4 reproducible project best) — Strategist/CEO should resolve at H2's R5 entry.
  - Hard targets: `ifc_heat` ≤ 0.0194 (kill-switch) AND `ifc_poisson` ≤ 0.05961 (displace `fno_mf_stack` from poisson leaderboard) AND composite ≤ 0.028 → strong KEEP.
  - Primary win condition for H2: **Poisson leaderboard displacement** (≤ 0.05961). Heat-side is secondary because H1 already holds Heat at 0.012898.
  - The `score_direction` polarity precheck bug will likely flip a real composite improvement back to a "+%" regression at R5 (now a 9-of-9 streak through cycle-008 H1); CEO should pre-register the override at R5 entry.

## Cross-cycle pattern notes

- **First NEW-family hypothesis in cycle-008 (and first since cycle-002 H3's `fno_coreg_residual`).** Cycles 003 / 005 / 006 / 007 / 008 H1 were all single-family-mutation hypotheses (loss-recipe knobs, schedule edits, constructor repairs, capacity bumps on existing families). H2 reopens the family-creation axis with a third architectural direction (single-FNO + LF-feature conditioning) distinct from coregionalization (basis-head, K-rank) and residual (per-fidelity ladder + decoder).
- **Leakage scanner trips on NEW-family manifest.json regardless of architectural intent.** Cycle-005 R0 strategy had projected "first cycle without substring-collision false-positives" — but ANY new family must ship a `manifest.json` with the required `description`, `frozen`, `supports: ["ifc_raw"]` schema fields, AND must copy through a `smoke_eval.py` that contains the same dataset-loader tokens. The scanner is structurally guaranteed to fire on EVERY new-family Builder commit. **Cycle-008 H2 is the 5th consecutive Builder-phase override** (specifically named "leakage substring collision" in the cycle-007 standup) — pattern is permanent until the precheck-infrastructure rewrite lands.
- **H1 + H2 cycle-008 contrast: capacity-axis vs conditioning-axis.** Cycle-008 H1 ships 50.47M params (paper-config capacity bump on the repaired constructor) targeting Heat; cycle-008 H2 ships 4.76M params (bar-trunk capacity with FiLM-LayerNorm conditioning) targeting Poisson. The two hypotheses are explicitly orthogonal in their failure-mode hypotheses: H1 bets that the cycle-007 H1 anisotropic-modes constructor was the blocker (`CAPACITY_PARETO` failure mode); H2 bets that single-full-res-HF-with-LF-conditioning is a winning architecture for value-scale-collapse-dominated Poisson (the residual stack's domain). If BOTH KEEP at R4/R5, cycle-009 could ensemble; if only one KEEPs, cycle-009 targets the other's failure axis at higher capacity.
- **Builder branch hygiene improving — fourth consecutive cycle** (cycle-007 H1, cycle-007 H2, cycle-008 H1, now cycle-008 H2) with a clean single-commit Builder output, zero pre-existing dirty-file contamination committed, despite the 15-file dirty working tree carried since cycle-005. Same structural-easy-case caveat applies — cycle-008 H2 is the structural-easiest case yet because all 4 files are NEW (no pre-existing dirty state on these paths could possibly have leaked in). The [[dirty-tree-staging]] auto-memory rule continues to do its job for new-family builds.
- **Cycle-007 R1.5 inheritance carried forward.** The constructor-signature pattern from cycle-007 H1 (anisotropic `(modes_h, modes_w)` parameterization) is re-used in H2's NEW family — second instance of the pattern propagating across families. [[anisotropic-spectral-modes-fno]] is now a 2-family pattern (`fno_coregionalization`, `fno_coreg_conditioned`).

## Links

- Project dashboard: [[factory_mffp]]
- Cycle-008 strategy: [[cycle-008]] (canonical R2 strategy snapshot — H1 > H2 > H3 plan-approved with bundling-FORBIDDEN anti-pattern)
- Cycle-008 H1 build sibling: [[cycle-008-exp-11-build]] (paper-config capacity bump on `fno_coregionalization`; independent branch `experiment/11`)
- Cycle-008 H1 R4/R5 outcome: [[cycle-008-exp-11]] (NEW REPRODUCIBLE PROJECT BEST 0.027729 — cycle-008 H1 closed at branch `experiment/11 @ 18d83a6`)
- Cycle-008 failure analysis: [[failure-analysis-cycle-008]]
- CEO Builder verdict: `.factory/reviews/ceo-verdict-builder.md` (cycle-008 H2)
- Builder report: `.factory/reviews/builder-latest.md`
- Cycle-007 H1 (parent baseline at `1249f2d` — the anisotropic-modes constructor signature inherited by H2): [[cycle-007-exp-9-build]], [[cycle-007-exp-9]]
- Cycle-005 H2 (banked H2 LF→HF schedule preserved verbatim in this H2's smoke_eval.py copy-through): [[factory_mffp-007]]
- Related source notes inherited:
  [[anisotropic-spectral-modes-fno]] — Li 2020 FNO `(modes_h, modes_w)` pattern; now propagating across 2 families (`fno_coregionalization`, `fno_coreg_conditioned`),
  [[lf-hf-pretrain-fraction-survey]] — cycle-007 R1.5 schedule study; H2 preserves the cycle-005 H2 `pretrain_frac=0.25` verbatim.
- Cycle-008 anti-pattern parents:
  [[patterns]] §"MFRNP recipes are backbone-coupled and dataset-entangled" (3-of-3 REVERTs lock-in; H2 does NOT trigger by construction),
  [[patterns]] §"`revert_bookkeeping_keep_intent` is the universal verdict — substring-collision precheck bug gates every eval" (H2 will likely be the 9th consecutive overall; 5th consecutive at Builder phase specifically),
  [[patterns]] §"Builder clean-isolation requires pre-clean working tree" (dirty-tree-staging precedent; structural-easy-case for H2 because all 4 files are NEW).
- Auto-memory honored: [[dirty-tree-staging]], [[factory-cli-invocation]] (Builder used `factory <cmd>` not `uv run python -m factory`).
- Commit: `540e684` on branch `experiment/12-fno_coreg_conditioned-film`.
- Base: `1249f2d` (cycle-008 entry baseline; cycle-007 H1 anisotropic-modes constructor fix).
- Diff: `git diff 1249f2d..540e684 models/fno_coreg_conditioned/` (+828 / -0 across 4 NEW files; zero existing-family edits).
