---
name: factory_mffp-005-build
description: H1 fno_coreg_residual_poisson_loss_reweighting (cycle-003 exp_id=5) — Builder phase. Strict additive single-knob: port resolve_fidelity_weights helper from H4's smoke_eval.py into H3's models/fno_coreg_residual/smoke_eval.py; add poisson_hf_weight=2.0/poisson_lf_weight=0.25 to SMOKE_DEFAULTS; thread (hf_fid_weight, lf_fid_weight) through compute_losses into both LF term sum and HF residual + aggregator anchor sum. 67 insertions / 5 deletions across smoke_eval.py + INSPIRATION.md, single commit a0d932b on experiment/5-fno_coreg_residual_poisson_lossweight cut from experiment/4-fno_coreg_residual. Pre-flight 2-epoch smoke verifies resolver gating (Heat→(1.0,1.0); Poisson→(2.0,0.25)); both contract JSONs include metric_value. Surface guard clean with explicit-SHA baseline; leakage scan = 2 known substring-collision false-positives. CEO PROCEED with documented design-choice note: aggregator anchor term is now scaled by hf_fid_weight (=2.0 on Poisson) — slightly more aggressive than H4's pure 8:1 because of anchor scaling.
metadata:
  type: project
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-003
  - build
  - h1
  - poisson-loss-weighting
project: factory_mffp
experiment_id: "005"
phase: build
verdict: PROCEED
date: 2026-05-15
source: factory-archivist
---

# Experiment #005 — Build phase: H1 `fno_coreg_residual_poisson_loss_reweighting` (cycle-003)

## Hypothesis

**Cycle-003 H1 — FIX, single additive knob.** Port H4's
`resolve_fidelity_weights(dataset_name, p)` helper into H3's
`models/fno_coreg_residual/smoke_eval.py` and wire it into `compute_losses`
so per-fidelity MSE terms are weighted dataset-conditionally — `(HF=2.0,
LF=0.25)` on Poisson, uniform `(1.0, 1.0)` on Heat.

Targets failure mode **F6 `ABSENT_POISSON_LOSS_WEIGHTING`** — the sole
remaining gap to two-of-two paper-beating after cycle-002 H3 hit composite
0.04420 with `ifc_heat=0.02634` (PASS, 2.81× under paper) but
`ifc_poisson=0.07416` (FAIL, 2.06× over paper 0.036). H3 shipped the
MFRNP-path loss-weighting knob as documented dead code under
`full_config.json :: _poisson_loss_knob`; H1 activates it via a
dataset-name-gated resolver that mirrors H4's working implementation.

**Compositional argument (CEO-adopted):** H3 supplies the IFC-path
architectural asymmetry (continuous-m basis head + per-fidelity output
normalization). H1 adds the orthogonal MFRNP-path loss-weighting
asymmetry on top. The two SOTA routes compose on one architecture.

Expected impact (anchored to *measured* H4 Poisson, NOT forecast):
- `ifc_poisson`: floor at H4's 0.0596 (loss-weighting recipe on
  uncomposed FNO backbone at hidden=32); plausible upside below 0.0596
  because H3 has hidden=64 + the basis head over H4's hidden=32.
- `ifc_heat`: unchanged at ≈0.02634 (resolver returns uniform weights
  for non-Poisson dataset names).
- `composite_nRMSE` floor at exact H4-Poisson parity:
  `geomean(0.02634, 0.0596) ≈ 0.0396` (≈10% reduction vs cycle-003 entry
  0.0442; ≈23% reduction below paper geomean 0.0516).
- `n_datasets_beating_paper`: 1 → potentially 2.

## Branch + commit

- **Branch**: `experiment/5-fno_coreg_residual_poisson_lossweight`.
- **Base**: `experiment/4-fno_coreg_residual` (cycle-002 H3 @ `0c46f43`,
  project best composite 0.0442). **NOT master** — master is at 1.6595
  due to precheck-bookkeeping reverts; the H3 implementation that
  achieves 0.0442 lives only on the experiment branch.
- **Single new commit**: `a0d932b` — "cycle-003 H1: port
  resolve_fidelity_weights into fno_coreg_residual; Poisson-conditional
  (2.0, 0.25) MFRNP weights".
- **Chain**: master ← H3 (`0c46f43`) ← H1 (`a0d932b`).
- **GitHub**: no PR, no push (per `--no-github`).

## What the Builder produced

`git diff --stat experiment/4-fno_coreg_residual..experiment/5-fno_coreg_residual_poisson_lossweight`:

| File                                          | Lines           | Purpose                                                      |
|---                                            |---:             |---                                                           |
| `models/fno_coreg_residual/smoke_eval.py`     | (the wiring)    | `resolve_fidelity_weights` helper; `SMOKE_DEFAULTS` adds `poisson_hf_weight=2.0` / `poisson_lf_weight=0.25`; `compute_losses` signature extended with `hf_fid_weight` / `lf_fid_weight` kwargs; `run()` resolves once at top of training loop, logs the active pair, threads through |
| `models/fno_coreg_residual/INSPIRATION.md`    | (cycle-003 ¶)   | Appended paragraph with bibtex for `mfrnp_poisson5_config`, `boulle2023ellipticdata`, `chen2018gradnorm` (theoretical context only, no code ported) |
| **Total**                                     | **+67 / -5, 2 files** | All under `models/fno_coreg_residual/**` |

## Mechanism (verified against H1 spec)

The verbatim Researcher-spec'd, CEO-confirmed resolver:

```python
def resolve_fidelity_weights(dataset_name: str, p: dict) -> tuple[float, float]:
    is_poisson = "poisson" in (dataset_name or "").lower()
    if is_poisson:
        return float(p.get("poisson_hf_weight", 2.0)), float(p.get("poisson_lf_weight", 0.25))
    return float(p.get("hf_loss_weight", 1.0)), 1.0
```

Wiring in `compute_losses`:

- LF terms get scaled by `lf_fid_weight`.
- HF residual + aggregator anchor term **both** get scaled by `hf_fid_weight`:
  ```python
  total = total + hf_fid_weight * (p["hf_loss_weight"] * loss_hf + p["agg_anchor_weight"] * loss_anchor)
  ```

**Builder design choice — aggregator anchor inside HF block.** The H1
spec was written against H4's `smoke_eval.py`, which has no aggregator
anchor (pure residual stack). H3 (the parent here) does have an
`agg_anchor_weight=0.5` regulariser keeping the MFRNP aggregator's LF
baseline meaningful. Builder treated "HF supervision" as a single block
and applied `hf_fid_weight` to both the HF residual term *and* the
aggregator anchor term. Net effect on Poisson:

- HF residual term scaled by 2.0.
- Aggregator anchor term scaled by 2.0 (previously 0.5 → effective 1.0).
- LF terms scaled by 0.25.
- Effective HF/LF gradient ratio is **slightly more aggressive than H4's
  8:1** because the anchor term is now upweighted too.

CEO accepted as-implemented: defensible — there's no fundamental reason
the anchor (which is an LF-aggregate fit term used as a regulariser)
should ride at LF gradient priority when the dataset has Poisson's
HF-up-weighting profile. May help further on Poisson (more HF emphasis
given H3's basis-head capacity) or may over-correct. The eval will tell.

## Pre-flight verification — PASSED both datasets

Builder ran the mandatory 2-epoch CPU smoke on both target datasets:

| Dataset        | `[loss-weights]` log line              | metric_value finite | JSON top-level metric_value |
|---             |---                                     |---                  |---                          |
| `ifc_heat`     | `hf_fid_weight=1.0 lf_fid_weight=1.0`  | ✓                   | ✓                           |
| `ifc_poisson`  | `hf_fid_weight=2.0 lf_fid_weight=0.25` | ✓                   | ✓                           |

- **Heat gating PASS** — resolver returns `(1.0, 1.0)` (no `"poisson"`
  in dataset name). Uniform weighting active, as required by the
  cycle-003 anti-pattern "do NOT activate the Poisson loss override on
  Heat".
- **Poisson gating PASS** — resolver returns `(2.0, 0.25)`, the verbatim
  MFRNP Poisson5 values, same numbers H4 used to recover Poisson to
  0.0596.
- Both contract JSONs include `metric_value` per `eval/MODEL_CONTRACT.md`.

## Hard-gate results

### Surface guard

`factory guard --baseline 0c46f43af50bbc58651fbab4fd425c5440788b89 --check-scope`
→ `clean` with explicit SHA baseline.

- Files modified: only `models/fno_coreg_residual/{smoke_eval.py,
  INSPIRATION.md}` ✓
- Within `mutable_surfaces: models/**` ✓
- Zero touches to `data/**`, `baselines/**`, `eval/**`, `references/**`,
  `factory.md`, `README.md`, `scripts/**` ✓
- No edits to sibling families (`models/fno_coregionalization/`,
  `models/fno_mf_stack/`) ✓

**Guard-tool observation (not a code violation):** passing the baseline
as a branch ref (`experiment/4-fno_coreg_residual`) tripped a "Branch
is not rooted at baseline" violation despite the merge-base equaling
the tip. Using the explicit SHA resolves cleanly. This is a
guard-tool baseline-resolution bug — filed as factory-infrastructure
observation; does NOT block the build.

### Ground-truth leakage scan

`factory leakage-check` on the diff → **2 findings, both known
substring-collision false positives** (same precheck infrastructure
bug pinned in [[patterns]] across cycles 001-002 H1/H2/H4/H3):

1. **`"poisson"`** — from `factory.md` line 42 ("smoke datasets are
   `ifc_heat` and `ifc_poisson`"). Context flagged on the diff is
   "set_name matches `*poisson*` and `(1.0, 1.0)`" — the dataset
   *name*, not a ground-truth value. The H1 mechanism gates on
   dataset name **as published in MFRNP Poisson5_config.yaml**;
   gating on the dataset name is the canonical correct mechanism.
2. **`"001"`** — from `README.md` (path component `/orcd/data/faez/001/...`)
   and `INSPIRATION.md`'s `cycle-001`/`cycle-003` references. Neither
   is a ground-truth value about model outputs. Same substring-collision
   class.

Both findings handled as `revert_bookkeeping_keep_intent` pattern at
R5; the leakage scanner does not differentiate value tokens from
category/path/index tokens. The precheck will likely flag the same.
Out-of-scope follow-up: scanner needs token-class differentiation.

### Sacred rules (all PASS)

- No deleted tests ✓
- No fixed-surface diff lines ✓
- No secrets / credentials / external API calls ✓
- No `eval/` threshold change ✓

## Implementation notes (carry into R4 / R5 interpretation)

- **Anchor-scaled HF/LF ratio**: as documented above, the effective
  Poisson HF/LF ratio is slightly higher than H4's published 8:1
  because the aggregator anchor is included in the HF-weighted block.
  H4 had no anchor; H3 + H1 has an anchor multiplied by 2.0 on Poisson.
- **Resolution timing**: resolver is called once at training-loop entry
  (Builder's choice — equivalent to per-step since dataset name doesn't
  change within a run; cheaper). Active pair logged in the
  `[loss-weights]` debug line.
- **`compute_losses` signature**: now takes `hf_fid_weight` and
  `lf_fid_weight` as explicit kwargs. The existing `hf_loss_weight`
  and `lf_loss_weights` (architecture-level scalars) remain untouched
  — the fidelity-weight kwargs multiply on top of those, matching H4's
  ordering.
- **Per-fidelity output normalization stays in place** — loss weights
  apply on top of the already-normalized residuals, matching H4's
  working order-of-operations.
- **No architectural change.** `model.py`, `data.py`, `manifest.json`,
  `full_config.json` (apart from optional key renaming if Builder
  judged it necessary — not required by the diff) are untouched.

## INSPIRATION.md citations added (cycle-003 paragraph)

- **Primary provenance**: `mfrnp_poisson5_config` — Rose-STL-Lab/MFRNP
  `Poisson5_config.yaml`, the source artifact for the (HF=2.0, LF=0.25)
  Poisson-only weighting. **NOT in the MFRNP paper** — published only
  in the YAML config.
- **Theoretical grounding (elliptic vs parabolic distinction)**:
  `boulle2023ellipticdata` (Boullé & Townsend, PNAS 2023) —
  elliptic-PDE operator learning is provably data-efficient with
  exponential rates; Green's-function global support motivates more
  aggressive LF down-weighting on elliptic-class problems than
  parabolic.
- **Theoretical context only (no code ported)**: `chen2018gradnorm`
  (ICML 2018) — one of four convergent theoretical lenses for why HF
  up-weighting / LF down-weighting helps on MF training. Cited to
  indicate an adaptive scheme (cycle-004 candidate) sits in the same
  conceptual family as the static recipe.

## CEO sign-off

- **CEO verdict** (`.factory/reviews/ceo-verdict-builder.md`,
  2026-05-15): **PROCEED**.
- Diff is the minimum additive change: helper + wiring + defaults
  +citations. No architectural touches, no data-loader change, no
  optimizer change.
- Surface clean (with explicit-SHA baseline workaround for the
  guard-tool bug).
- Leakage flag dismissed as known substring-collision false-positive
  with documented `revert_bookkeeping_keep_intent` precedent.
- Pre-flight both datasets pass: Heat resolver returns `(1.0, 1.0)`
  (Heat win is preserved by construction); Poisson resolver returns
  `(2.0, 0.25)` (the activation that targets F6).
- Implementation-note on anchor scaling acknowledged as a defensible
  Builder design choice — the eval reveals whether the slightly more
  aggressive ratio helps or over-corrects.

**PROCEED to R4 (run `bash scripts/cycle_eval.sh` on the experiment
branch).** Cache will MISS on `models/fno_coreg_residual/` (new
code_hash from the smoke_eval.py + INSPIRATION.md edits); H1/H2/H4
caches and v9 cache unaffected.

## Pending (R4 / R5)

- 200-epoch run via `bash scripts/cycle_eval.sh` on
  `experiment/5-fno_coreg_residual_poisson_lossweight`.
- **R5 verdict logic**: monotonic check is
  `composite_after <= previous_best`. Comparison anchors:
  - master baseline: **1.6595** (v9 geomean)
  - cycle-001 H1 (`fno_coregionalization`): **0.10919**
  - cycle-001 H2 (`fno_mf_stack`): **0.11173**
  - cycle-002 H4 (`fno_mf_stack` v2): **0.07719**
  - cycle-002 H3 (`fno_coreg_residual`): **0.04420** ← **project best**
- Cycle-003 H1 (this experiment) only displaces H3 as project best if
  composite is **< 0.04420**. Floor at exact H4-Poisson parity gives
  composite ≈ 0.0396; plausible upside below that given H3's
  basis-head + hidden=64 over H4's hidden=32.
- Expected precheck infrastructure false-positives at R5 — same 4
  known bugs as cycles 001-002 H1/H2/H4/H3 (score_direction polarity,
  scope/fixed_surfaces empty-detail, ground_truth_leakage
  substring-collision, scope-tuple shape). The
  CEO=KEEP-intent / factory=REVERT-bookkeeping branch-preserved
  pattern will likely apply again — **5th consecutive cycle override**
  if H1 improves the metric.

## Cross-project / cross-cycle pattern notes

- This is the **first time the project ports a knob across families**
  (resolver was implemented in H4 on `fno_mf_stack`; H1 cycle-003 lifts
  it into `fno_coreg_residual` essentially verbatim). The composition
  hypothesis from cycle-002 close-out (IFC-path architectural
  asymmetry + MFRNP-path loss-weighting asymmetry compose) is what's
  being tested here. See [[patterns]] §"F5 architectural resolution"
  and the new candidate §"Cross-family knob portability".
- The aggregator-anchor scaling decision is a **carry-forward concern
  for the eventual GradNorm-lite cycle-004 candidate** — adaptive
  weighting would need to decide whether the anchor term participates
  in the adaptive group with the HF residual or sits in a separate
  group. The Builder's choice here pre-commits to "anchor rides with
  HF" for the static-recipe regime; the cycle-004 design has to address
  whether to inherit that grouping or re-derive it adaptively.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle-003 strategy (H1 spec lines 280-323):
  [[cycle-002-strategy]] (the strategy file appends cycle-003 below
  cycle-002 in `current.md`)
- Cycle-003 failure analysis: [[failure-analysis-cycle-003]]
- Cycle-002 H3 (parent — the project-best architecture H1 extends):
  [[factory_mffp-004-build]], [[factory_mffp-004-outcome]]
- Cycle-002 H4 (provenance of `resolve_fidelity_weights` helper):
  [[factory_mffp-003-build]], [[factory_mffp-003-experiment]]
- Cycle-001 H1 (basis-head provenance):
  [[factory_mffp-001-build]], [[factory_mffp-001-experiment]]
- Cycle-001 H2 (MFRNP residual stack provenance):
  [[factory_mffp-002-build]], [[factory_mffp-002-experiment]]
- Source papers / configs:
  [[mfrnp_poisson5_config]] (primary provenance of the (2.0, 0.25) recipe),
  [[boulle2023ellipticdata]] (elliptic-PDE data-efficiency grounding),
  [[chen2018gradnorm]] (theoretical context only — no code ported),
  [[niu2024mfrnp]] (MFRNP architecture template, parent of the Poisson5
  config),
  [[li2022ifc]] (basis-head provenance carried through H3)
- Commit: `a0d932b` on branch
  `experiment/5-fno_coreg_residual_poisson_lossweight`
- Base: `experiment/4-fno_coreg_residual` @ `0c46f43`
- Diff: `experiment/4-fno_coreg_residual..experiment/5-fno_coreg_residual_poisson_lossweight`
  (+67 / -5, 2 files, both under `models/fno_coreg_residual/**`)
