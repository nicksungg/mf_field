---
name: patterns
description: Cross-project / cross-cycle patterns identified during the factory's work. Append entries here when a pattern recurs across projects or experiments.
metadata:
  type: reference
tags:
  - factory
  - patterns
source: factory-archivist
date: 2026-05-15
---

# Factory Patterns

Append entries as patterns surface across projects/cycles. Only entries supported by ≥1 observation should be here.

## Per-fidelity output normalization is the cheapest large win for value-scale-shift MF datasets

Discovered in **factory_mffp cycle 001** while diagnosing F1 (`ifc_poisson` test value-scale collapse). The Poisson solution magnitude collapses ~40× from L1 (8×8) to L4 (64×64) due to finite-difference normalization (solution scale ∝ h²). Predicting `y / scaler[m]` (where `scaler[m] = max-abs of training y at fidelity m`) could drop ifc_poisson nRMSE from 18.5 to ~1.0 *without changing the backbone*. Cheap to implement, large impact when value-scale shift exists.

**Confirmed (factory_mffp cycle 001 H1 R4, 2026-05-15)**: observed scalers
`[0.0773, 0.0237, 0.0069, 0.0018]` on `ifc_poisson` validate the diagnosed
~40× collapse (0.0773 / 0.0018 ≈ 43×). With normalization + FNO + B(m) head,
`ifc_poisson` dropped 18.50 → 0.7725 (−95.8%); the projected
normalization-alone target of ~1.0 was within 30% of the realized 0.7725, and
the architecture stack adds the remaining margin. See
[[factory_mffp-001-experiment]].

**How to detect**: per-fidelity y-range tables show >5× range collapse from LF to HF.

**Source**: [[cycle-001-cross-cutting-findings]], [[factory_mffp-001-experiment]].

## Continuous-fidelity index beats gated per-stream mixing for MF surrogates

Discovered in **factory_mffp cycle 001**. Every literature method beating baselines on IFC datasets (IFC-ODE2, IFC-GPODE, MFRNP-on-related-data) encodes fidelity as either (a) a continuous variable in the architecture, or (b) a residual stack across discrete levels. Gated softmax over per-stream attention (as in v9) does *not* encode fidelity → unable to express value-scale shifts.

**Confirmed (factory_mffp cycle 001 H1 R4, 2026-05-15)**: H1 added an explicit
continuous-m basis `B(m)=MLP([m, m²])` and a Σ_k B_k(m)·h_k(x) head, and
immediately captured the cross-fidelity rescaling that v9's gated softmax
could not — composite_nRMSE 1.6595 → 0.1092 (−93.4%). See
[[factory_mffp-001-experiment]].

**Architectural rule**: any new MF family must encode fidelity explicitly (continuous-m basis, FiLM-from-m, fidelity-aware FNO, or per-fidelity stacked residual).

**Source**: [[cycle-001-cross-cutting-findings]], [[li2022ifc]], [[niu2024mfrnp]], [[factory_mffp-001-experiment]].

## FNO > Transolver for regular-grid PDE data

Discovered in **factory_mffp cycle 001**. Transolver's slice-attention is designed for unstructured meshes; on a regular grid it adds O(N·K) cost without inductive-bias benefit. FNO's spectral conv is O(N log N) with smaller hidden state, and is resolution-invariant by design.

**Confirmed (factory_mffp cycle 001 H1 R4, 2026-05-15)**: at similar parameter
count (4.75M vs v9's Transolver hidden_dim=128 budget), `ifc_heat` test nRMSE
dropped 0.149 → 0.0154 (~10× better), beating the IFC-ODE2 paper bar (0.074)
by 4.8×. See [[factory_mffp-001-experiment]].

**Architectural rule**: prefer FNO as the backbone for any model family targeting regular-grid PDE datasets.

**Source**: [[cycle-001-cross-cutting-findings]], [[li2020fno]], [[wu2024transolver]], [[factory_mffp-001-experiment]].

## Factory precheck `score_direction` is polarity-buggy on lower-is-better metrics (load-bearing — 7-for-7 cycle overrides; precheck-subsystem overhaul is on the cycle-006 critical path)

Discovered in **factory_mffp cycle 001 H1 R4** (2026-05-15). The CLI's
`finalize` precheck applies a `score_direction` check with `threshold=0.0`
that incorrectly fails when the metric is **lower-is-better and strictly
positive** (here `composite_nRMSE`). Even though H1 improved composite_nRMSE
from 1.6595 → 0.1092 (−93.4%), the precheck reported a `score_direction`
failure and the `finalize` gate auto-overrode CEO `keep` → `verdict='revert'`.
The branch was preserved physically, but the bookkeeping recorded a revert.

**Confirmed 2nd time (factory_mffp cycle 001 H2 R4, 2026-05-15)**: identical
override applied. H2 composite_nRMSE 1.6595 → 0.11173 (−93.3% vs project
state) was flagged as "Score regressed: 1.6595 → 0.1117 (delta=−1.5478)"
and `finalize` auto-overrode CEO `keep` → `verdict='revert'`. The
`eval/smoke_config.json` file already carries
`primary_metric_lower_is_better=true`; the precheck does not read it. See
[[factory_mffp-002-experiment]].

**Confirmed 3rd time (factory_mffp cycle 002 H4 R4, 2026-05-15)**:
identical override applied. H4 composite_nRMSE 1.6595 → 0.07719 (−95.3%
vs project state, 21.5× improvement) was flagged as a regression and
`finalize` auto-overrode CEO `keep` → `verdict='revert'`. **The
score_direction polarity bug has now overridden 3 consecutive
substantively-improving experiments** — every cycle-001 AND cycle-002
result. See [[factory_mffp-003-experiment]].

**Confirmed 4th time (factory_mffp cycle 002 H3 R4, 2026-05-15)** —
**load-bearing at 4-of-4 cycle overrides; bug pattern fully reproducible**:
identical override applied. H3 composite_nRMSE 1.6595 → 0.04420 (−97.3%
vs project state, **37.5× improvement; project best by a wide margin —
first family to beat the paper composite geomean**) was flagged as
"Score regressed: 1.6595 → 0.0442 (delta=-1.6153)" — the **deepest
improvement the bug has overridden yet** — and `finalize` auto-overrode
CEO `keep` → `verdict='revert'`. **All four cycle-001 + cycle-002
experiments (H1, H2, H4, H3) hit the same 4 precheck failures.** The
bug pattern is fully reproducible across 4 independent experiments with
4 independent architectures (single-family basis head, single-family
residual stack, residual stack + capacity + loss-weight, hybrid
basis-head over MFRNP residual stack) — there is no remaining doubt
that this is a precheck infrastructure bug rather than an
experiment-specific anomaly. See [[factory_mffp-004-outcome]].

**Confirmed 5th time (factory_mffp cycle 003 H1 R4, 2026-05-15)**:
identical polarity bug fired even on the first **genuine** REVERT in
project history. Cycle-003 H1 composite_nRMSE regressed 0.04420 →
0.08472 (+91.7% genuine research regression — CEO intent = REVERT for
the first time). The precheck threshold `>0.0` still tripped on the
positive delta (0.08472 > 0.04420), so the precheck "agreed" with the
CEO by accident — the underlying polarity bug remains; the precheck
just happens to give the right answer when the metric genuinely
regresses. **The bug is not "the precheck reverts when it shouldn't";
it is "the precheck never reads `primary_metric_lower_is_better`".**

**Confirmed 6th time (factory_mffp cycle 005 H1 R4, 2026-06-02)**:
identical override applied. Cycle-005 H1 was a 1-line REPO_ROOT fix
with pre-registered zero impact on composite; the precheck flagged
the noise-level positive delta as a regression and `finalize`
auto-overrode CEO `keep` → `verdict='revert'`. The script of the
bug here is even cleaner — H1 was *explicitly* a "no-composite-move"
experiment, and the polarity bug still tripped. See [[factory_mffp-006]].

**Confirmed 7th time (factory_mffp cycle 005 H2 R4, 2026-06-02) —
project-best evaluation overridden by the same bug, again**: cycle-005
H2 composite_nRMSE 0.033726 → 0.029357 (**−13%, first sub-0.030
composite in project history, NEW PROJECT BEST**) was flagged as
"Score regressed: 0.0337 → 0.0294 (delta=−0.00437)" and `finalize`
auto-overrode CEO `keep` → `verdict='revert'`. **The deepest
project-relative improvement the bug has overridden since cycle-002 H3
(which was the prior project best at the time it was overridden)**.
See [[factory_mffp-007]].

**Confirmed 8th time (factory_mffp cycle 007 H1 R4, 2026-06-02) —
single largest cycle-on-cycle improvement the bug has overridden
yet**: cycle-007 H1 composite_nRMSE 0.039578 → 0.030408 (**−23.17%,
single-file +9/-7 LOC constructor fix recovering cycle-005 cached
`fno_coregionalization` heat 0.01551 within ≈+1e-8**) was flagged as
"Score regressed" (polarity flips −23% improvement to +23% regression)
and the standard `revert_bookkeeping_keep_intent` protocol applied.
Branch `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`
preserved as the cycle-008 entry baseline. **All 3 real precheck checks
(`ground_truth_leakage`, `anti_pattern`, `smoke_test`) PASSED;
Reviewer issued substantive PASS; Evaluator R4 = "PASS — KEEP" ("the
cleanest H1 validation we have had in 6 cycles").** The polarity bug
is the sole reason this `−23%` improvement is recorded as a REVERT.
See [[cycle-007-exp-9]].

**Status**: this is the **dominant blocker** in the factory pipeline,
now confirmed **8-of-8 on lower-is-better evaluations** in project
history (001 H1, 001 H2, 002 H4, 002 H3, 003 H1, 005 H1, 005 H2,
007 H1).
Every cycle-001 / 002 / 003 / 005 experiment has hit it; every future
lower-is-better experiment will hit it. The cumulative cost across
seven cycles, plus the certainty of recurrence on the first cycle-006
eval, makes the precheck-bookkeeping subsystem overhaul **load-bearing
on the cycle-006 critical path** — without it, cycle-006 will close
`revert_bookkeeping_keep_intent` for the 6th consecutive keep-intent
eval (8th-of-8 polarity-bug override) regardless of research outcome.
Promote to a cycle-006 Strategist hypothesis at the highest priority:
"fix `factory precheck` `score_direction` to honor
`primary_metric_lower_is_better` from the smoke config".

**Workaround for future cycles**: either (a) feed a reciprocal /
negated 'higher-is-better' transform of the score into the precheck, or
(b) treat the precheck `score_direction` failure as an automatic
false-positive when the underlying metric is lower-is-better and use the CEO
override pathway. The CEO should always re-record the intended verdict in
the experiment archive note when the bookkeeping disagrees.

**Source**: [[factory_mffp-001-experiment]], [[factory_mffp-002-experiment]].

## Factory precheck reports empty-detail `scope` / `fixed_surfaces` failures that contradict the standalone guard (2 cycles)

Discovered in **factory_mffp cycle 001 H1 R4** (2026-05-15). The CLI
`finalize` precheck reported `scope` and `fixed_surfaces` failures with
**empty detail bodies**, while the standalone
`factory guard --check-scope --check-surfaces` tool independently reported
**clean** on the same diff at the same commit. The precheck and the
standalone guard disagree.

**Confirmed 2nd time (factory_mffp cycle 001 H2 R4, 2026-05-15)**: identical
empty-detail `scope` and `fixed_surfaces` failures on H2. Standalone
`factory guard --check-scope --baseline <master>` returned **clean**.
`git diff --name-only master..experiment/2-fno_mf_stack` listed only files
under `models/fno_mf_stack/`, all in mutable_surfaces. The precheck's
sub-checks are systematically broken — they are now expected false
positives on any mutable-surface-only diff.

**Confirmed 3rd time (factory_mffp cycle 007 H1 R4, 2026-06-02)**: identical
empty-detail `scope` and `fixed_surfaces` failures on H1. Standalone
`factory guard --check-scope` independently returned **`clean`** on the
same diff at commit `1249f2d` against base `be36cba`. The H1 diff touches
exactly 1 file (`models/fno_coregionalization/model.py`, +9/-7 LOC), all
under mutable_surfaces (`models/**`). Reviewer's substantive PASS cited
the standalone clean result; CEO ratified PROCEED. Combined with the
`score_direction` polarity bug (now 8-of-8), the precheck infrastructure
has now overridden a **−23.17% composite improvement** as REVERT —
the largest cycle-on-cycle improvement in project history to be
formally recorded as a revert. See [[cycle-007-exp-9]].

**Workflow rule**: before accepting any `scope` or `fixed_surfaces`
precheck failure, the CEO must re-run the standalone
`factory guard --check-scope --check-surfaces` and treat the standalone
result as authoritative. If the standalone is clean, override the precheck.
**Long-term fix required (out-of-cycle):** `precheck.py` lives at
`/orcd/data/faez/001/nick/mf_field/akash/remote-factory-main` (outside
the factory_mffp cycle mutable surface). Two infra fixes needed:
(i) honor `primary_metric_lower_is_better` from `eval/smoke_config.json`
for `score_direction`; (ii) refuse to emit `scope` / `fixed_surfaces`
failures when the violation-detail list is empty (the standalone guard
is authoritative).

**Combined-bug instance — cycle-005 H2 + cycle-007 H1 are sibling
cases of the same compound bookkeeping failure**: both have
(a) real research metric monotonically improving on a
lower-is-better metric AND (b) all real safety checks passing AND
(c) the polarity bug + empty-detail bugs all firing → guaranteed
false-positive REVERT. The `revert_bookkeeping_keep_intent` protocol
(branch preservation + CEO `keep` intent recorded in archive note)
is the only in-cycle mitigation. Cycle-008 should treat the new
banked composite (0.030408 on `experiment/9 @ 1249f2d`) as the
monotonic-improvement baseline, NOT the formal-verdict-reported
"reverted" value.

**Source**: [[factory_mffp-001-experiment]], [[factory_mffp-002-experiment]],
[[cycle-007-exp-9]].

## Factory leakage-check fingerprints `factory.md` itself and produces false-positive medium-risk on shared vocabulary

Discovered in **factory_mffp cycle 001** — first observed at H1 Builder phase
(see [[factory_mffp-001-build]] §Hard-gate results), confirmed again at H1
R4 finalize. `factory leakage-check` walks all text files in `fixed_surfaces`
and fingerprints `factory.md` / `README.md` themselves; this means any model
code that conforms to `eval/MODEL_CONTRACT.md` will share vocabulary tokens
with the project docs (`name`, `description`, `supports`, `frozen`,
`dataset`, `ifc_raw`, ...) and trigger `risk_level=medium` flags. None of
these are real leakage — they are inherent to the contract.

**Confirmed 3rd time (factory_mffp cycle 001 H2 Builder, 2026-05-15)**:
identical pattern at H2 — `risk_level=medium`, 6 findings with the same
shared-vocabulary tokens (`description`, `metric_value`, `ifc_raw`,
`dataset`, `frozen`). CEO override applied with the same rationale. The
pattern is **routine, not surprising** — any future Builder following the
model contract will trip the same flags. See [[factory_mffp-002-build]].

**Confirmed 4th time and extended to numerical-substring collisions
(factory_mffp cycle 001 H2 R4, 2026-05-15)**: the precheck flagged
`specific_value: '0.10' from factory.md`. Substring `0.10` appears in
`factory.md` lines 51–52 (`- hygiene: 0.10`, `- growth: 0.10` — eval
weight constants) AND in the hypothesis text (target
`ifc_heat → ≤0.10`). The scanner matched purely on substring without
distinguishing **value-class semantics** (eval-weight constant vs.
paper-baseline metric vs. hypothesis target). When the hypothesis text is
stripped of this incidental substring, `factory leakage-check` returns
`flagged=False, risk_level=none`. The model code itself contains no
numerical paper-baseline values from `baselines/paper_baselines.json`.
See [[factory_mffp-002-experiment]].

**Sub-pattern recorded**: the leakage-check failure mode is **any
substring collision**, not just "shared vocabulary". Eval-weight constants
in `factory.md` (`0.10`, `0.20`, …) will match any hypothesis target or
threshold that happens to contain the same numeric substring. Either
(a) exclude `factory.md` constants from the scanner corpus, or (b)
require token-boundary matches with value-class tags.

**Workflow rule**: when leakage-check reports `risk_level=medium`, the CEO
must inspect the findings list directly and treat as true leakage **only**
specific numerical values from `baselines/paper_baselines.json` or `data/**`
that appear verbatim in the diff. Shared-vocabulary tokens are
false-positives and warrant override. Either fix the scanner to exclude
self-referential text files from its corpus, or treat shared-vocabulary
overrides as routine.

**Confirmed 5th time and extended to dataset-name dispatch-key
sub-class (factory_mffp cycle 007 H2 Builder, 2026-06-02)**: H2's
`+29/-0 LOC` source change at
`models/fno_coreg_residual/smoke_eval.py` introduced the literal
string `"ifc_poisson"` as a `_DATASET_RECIPES` dictionary key — the
public dispatch API surfaced via `args.dataset_name`. The leakage
scanner walked `factory.md` and matched the substring `"ifc_poisson"`
against research-constraints text on the same line, raising a
`medium-risk` flag. CEO override applied with rationale:

> Dataset name `ifc_poisson` is the public dispatch API via
> `args.dataset_name`, not a ground-truth value — same false-positive
> class as cycle-001 shared-vocabulary findings; sub-class extended
> to dataset-name dispatch keys.

**NEW sub-class recorded**: dataset-name tokens used as
**public dispatch API keys** trip the scanner against
research-constraints text in `factory.md`. Distinct from prior
sub-classes (shared-vocabulary, numerical-substring) because the
token is **intentionally** part of the public API — the model
needs to dispatch on dataset name, and the dataset name will
necessarily appear in the source. Token-class differentiation in
the scanner would need to recognize `args.dataset_name` as a public
API boundary distinct from ground-truth answer values. See
[[cycle-007-exp-10-build]].

**Confirmed 6th time and pinned as "5th consecutive Builder-phase
leakage substring collision" (factory_mffp cycle-008 H2 Builder,
2026-06-02)**: H2's `+828/-0 LOC` change at the NEW family
`models/fno_coreg_conditioned/**` (4 new files — `model.py`,
`smoke_eval.py`, `manifest.json`, `INSPIRATION.md`) triggered the
scanner with 4 findings — `satisfy`, `description`, `ifc_raw`,
`frozen`. CEO override applied with explicit rationale:

> All 4 tokens are substring collisions with REQUIRED manifest
> schema fields per `eval/MODEL_CONTRACT.md` (`description`,
> `frozen`) AND with the REQUIRED `supports` array value per
> research_constraints field 4 ("New families must support at least
> the `ifc_raw` dataset loader"), OR with generic English (`satisfy`
> in both the diff code comment and `README.md`). Excluding any of
> them would make the manifest contract-invalid; `ifc_raw` is the
> mandated dataset-loader name; `satisfy` is a generic English word.

**Pattern stabilization recorded**: this is the **5th consecutive
operator-flagged Builder-phase 'leakage substring collision'
bookkeeping bug** — the specific name was pinned in the cycle-007
standup, then re-confirmed at cycle-007 H1 Builder, cycle-007 H2
Builder, cycle-008 H1 Builder, and now cycle-008 H2 Builder. Two
distinct architectures (capacity-bump on existing family vs
NEW-family addition) trip the same scanner with the same token
classes (schema/dispatch/generic English). The scanner failure
mode is **structurally guaranteed** on any Builder commit that
either (a) ships a `manifest.json` honoring the contract, or
(b) references `ifc_raw` (which is mandated by research-constraint
field 4 for any new family). See [[cycle-008-exp-12-build]].

**Source**: [[factory_mffp-001-experiment]], [[factory_mffp-001-build]],
[[factory_mffp-002-build]], [[cycle-007-exp-10-build]],
[[cycle-008-exp-11-build]], [[cycle-008-exp-12-build]].

## `smoke_eval.py` may not consume `full_config.json` — Builder smoke defaults silently flow into the 200-epoch SLURM run

Discovered in **factory_mffp cycle 001 H2 Builder** (2026-05-15). The
Builder for H2 (`fno_mf_stack`) shipped a `full_config.json` with hidden=64,
modes=(4,8,12,12), 3 blocks, 400 epochs — but `smoke_eval.py` reads its
defaults from `SMOKE_DEFAULTS = dict(hidden=16, modes_per_level=(4,5,5,5))`
inline and **does not load `full_config.json` at all**. Since
`scripts/cycle_eval.sh` invokes the same `smoke_eval.py` for the 200-epoch
SLURM run, the SLURM run uses the small CPU-smoke sizes, not the
full-config sizes. The `full_config.json` ends up as documentation only.

**Why this happens**: spec instructs Builders to verify the CPU smoke runs
end-to-end in 2 epochs. Builders shrink defaults to fit the CPU smoke
budget, ship `full_config.json` as reference for a hypothetical "full" run
that the factory pipeline never wires up. CEO may proceed despite the
deviation if normalization (the cross-cutting hygiene) is the dominant
driver, but should pre-register a fallback "bump capacity" hypothesis for
the next cycle.

**Workflow rule for Strategist (future cycles)**: when writing a hypothesis
spec, either (a) require `smoke_eval.py` to load `full_config.json` directly
for SLURM runs, OR (b) state explicitly that the spec sizes are the
*smoke-and-SLURM* defaults (no inline-vs-config split). Otherwise
Builders will silently downsize and the 200-epoch SLURM run won't get the
spec capacity.

**Workflow rule for CEO**: when reviewing Builder output, grep
`smoke_eval.py` for whether it loads `full_config.json`. If not, verify the
inline defaults are within the spec range. If they are not, decide explicitly
whether to PROCEED (cheap hygiene dominates) or REDIRECT (capacity matters).

**Empirically confirmed (factory_mffp cycle 001 H2 R4, 2026-05-15)**: the
prediction was borne out. H2 ran at hidden=16, modes=(4,5,5,5), 2 blocks
(`SMOKE_DEFAULTS` from `smoke_eval.py`) — the `full_config.json` hidden=64,
modes=(4,8,12,12), 3 blocks was never loaded. Outcomes:
- **`ifc_heat`**: 0.1275, **8.3× worse than H1** (0.0154) at 1/49 the
  params. The cap was real: Heat needed the full capacity. Recoverable in
  cycle 002 with one edit.
- **`ifc_poisson`**: 0.0979, **7.9× better than H1** at 1/49 the params.
  The residual-stack inductive bias plus normalization dominated even at
  tiny capacity — for value-scale-collapse-dominated datasets, structure
  beats capacity.

**Cycle-002 pre-registered hypothesis (CEO)**: bump `fno_mf_stack`
`SMOKE_DEFAULTS` to `hidden=32, modes=(4,8,12,12)` (or load
`full_config.json` directly), re-run R4 — one-knob test for whether the
undersized smoke defaults caused the `ifc_heat` regression. If yes, H2
becomes a strict superset of H1's Heat win as well; if no, the residual
stack's Heat-side bias is genuinely weaker than the coregionalization
head's, and the right cycle-003 move is the H1/H2 ensemble.

**Empirically validated (factory_mffp cycle 002 H4 R4, 2026-05-15)**:
the cycle-002 H4 experiment bumped `SMOKE_DEFAULTS` to `hidden=32,
modes=(4,8,12,12), 3 blocks` (the exact pre-registered values) and
re-ran R4. Outcome: `ifc_heat` 0.1275 → **0.0999** (22% recovery
from the H2 regression). The cap was real and capacity-recoverable —
the cycle-001 prediction is now confirmed. `fno_mf_stack` at H4
capacity is now a strict win over H2 on Heat (though still 6.5×
worse than H1's 0.0154, suggesting a residual inductive-bias gap
that capacity alone cannot fully close). See
[[factory_mffp-003-experiment]].

**Source**: [[factory_mffp-002-build]], [[factory_mffp-002-experiment]],
[[factory_mffp-003-experiment]].

## Aggregate-metric failure cycles do not need a failure_analyst spawn

Discovered in **factory_mffp cycle 001-baseline**. The composite_nRMSE metric has no per-instance axis to classify (only per-dataset/per-split nRMSE). Spawning the failure_analyst agent on this baseline:
- yielded no useful classification (no instance-level rows to assign causes to);
- timed out at the default 300 s on two attempts due to wrapper cold-start cost.

**Process rule**: for projects whose metric is a per-dataset aggregate (no instance axis), prefer a manual CEO aggregate-level analysis stub at `.factory/research/runs/<cycle>/failure_analysis.md` rather than spawning failure_analyst. The Researcher can still consume the stub.

## Coregionalization head and MFRNP residual stack are a complementary architecture pair on IFC-style MF datasets

Discovered in **factory_mffp cycle 001** (2026-05-15), comparing H1
(`fno_coregionalization` — FNO + `B(m)=MLP([m, m²])` head) against H2
(`fno_mf_stack` — 4 small FNOs + MFRNP residual stacking with
decoder-in-the-aggregation). On the same `ifc_raw` datasets at comparable
training budget, the two families produced **inverse per-dataset profiles**:

| Family                      | `ifc_heat`              | `ifc_poisson`               |
|---                          |---                      |---                          |
| H1 — coregionalization       | **0.0154 (beats paper)**| 0.7725 (21× over paper)    |
| H2 — residual stack          | 0.1275 (1.7× over paper)| **0.0979 (2.7× over paper)** |

H1 wins big on Heat, loses on Poisson. H2 wins big on Poisson, loses on
Heat. Both achieve essentially the same composite (0.10919 vs 0.11173) via
disjoint mechanisms.

**Architectural rule**: when an MF dataset family has substantial
**inter-dataset heterogeneity** (clean dynamics + stiff /
value-scale-shift dynamics under one suite), no single inductive bias
dominates both — propose a **per-dataset gated ensemble** or a **hybrid
network combining both inductive biases** as the next cycle's hypothesis,
rather than another single-family iteration.

**Concrete next-cycle proposals**:
- `fno_ensemble_h1_h2` — per-dataset selector or convex combination, gating
  learned on validation. Cheap.
- `coreg_plus_residual_stack` — continuous-m basis head feeding into an
  MFRNP residual stack (or vice versa). Heavier; combines both inductive
  biases in a single network.

**Source**: [[factory_mffp-001-experiment]], [[factory_mffp-002-experiment]].

## HF residual head should condition on the aggregator baseline (Builder extension to MFRNP)

Discovered in **factory_mffp cycle 001 H2 Builder** (2026-05-15). The
Builder extended MFRNP by having the HF (L4) FNO consume the aggregated LF
baseline as an **extra input channel** before predicting the residual
`δ` — so `δ` conditions on the baseline rather than being agnostic to it.
The literal MFRNP recipe does not specify this; it just says
`final = aggregate(LFs) + δ`.

**Empirically confirmed (factory_mffp cycle 001 H2 R4, 2026-05-15)**: H2's
`ifc_poisson` came in at **0.0979 — 7.9× better than H1's coregionalization
head (0.7725)** and **189× better than v9 baseline (18.50)**, at 49× fewer
parameters than H1. The 7.9× win on a value-scale-collapse-dominated
dataset suggests the conditioning helps the HF head specialize as a
**baseline corrector** rather than a from-scratch predictor — an inductive
bias well suited to stiff regimes where the LF baseline is already
qualitatively right.

**Architectural rule**: any future residual-stacking MF family should
condition the HF head on the LF aggregate as an explicit input channel,
not treat the residual prediction as baseline-agnostic. The
baseline-as-input extension is **load-bearing** for the Poisson result.

**Source**: [[factory_mffp-002-build]], [[factory_mffp-002-experiment]],
[[niu2024mfrnp]].

## R4 evaluator agent timeout can fire even when `cycle_eval.sh` itself succeeds — write summary.json directly when EXIT=0

Discovered in **factory_mffp cycle 002 H4 R4** (2026-05-15). When the
underlying eval is **CPU-bound and large** (H4: ~28 min wall —
1727 s — for 4 FNOs + MFRNP aggregator at hidden=32, modes=(4,8,12,12),
3 blocks, 200 epochs × 2 datasets), the Claude Evaluator agent's
ClaudeRunner timed out at the 3600 s mark waiting on the
`bash scripts/cycle_eval.sh` invocation. The agent reports a timeout
failure even though:

- `cycle_eval.sh` exited 0 (verified by inspecting the agent's tool
  log — the script ran to completion).
- `results/smoke_latest.json` was populated with the full per-dataset
  table and computed composite metric.
- All training/eval artefacts on disk are intact and self-consistent.

The agent's timeout is **orthogonal** to the eval succeeding — the
agent waits for a wrapper Python call to return, while
`cycle_eval.sh` runs subprocesses that write artefacts as they go.
When the wrapper takes longer than the agent's tool-call timeout, the
agent fails its turn even though the data is on disk.

**Why H1 didn't hit this**: H1 used SLURM (L40S, ~12 min) and the
agent's tool call blocks only on the `sbatch` queueing / poll, not
the training itself. H2 used CPU but at 1/49 the params (~530 s wall,
well under 3600 s). H4 used CPU at full capacity, ~28 min wall —
crossed the agent's tool-call budget.

**Workflow rule**: when the R4 evaluator agent reports a timeout
failure, **first inspect `results/smoke_latest.json` and
`.factory/research/runs/<cycle>/`** before respawning the agent or
declaring the experiment failed. If the artefact is complete and
`cycle_eval.sh` exited 0, the CEO can write `summary.json` directly
from the complete data — no respawn, no new compute. Cache for both
trained datasets is now warm; any subsequent invocation would hit it
anyway.

**Implementation options for future cycles**:
- Bump the agent's `--timeout` to match expected CPU wall (e.g.,
  3600 → 7200 for CPU runs at full capacity).
- Route H4-sized experiments to H100 SLURM by default (CEO can request
  SLURM in the R4 evaluator instruction).
- Have the CEO check for `results/smoke_latest.json` and `cycle_eval.sh
  EXIT=0` before treating an evaluator timeout as a failure signal.

**Source**: [[factory_mffp-003-experiment]],
`.factory/research/runs/cycle-002-H4/summary.json`,
`results/smoke_latest.json`.

## MFRNP `Poisson5_config.yaml` knobs (capacity + per-fidelity loss weighting) are independently load-bearing and orthogonally decompose by dataset

Discovered in **factory_mffp cycle 002 H4 R4** (2026-05-15). The two
pre-registered MFRNP knobs applied on top of H2's residual-stack
architecture decomposed cleanly into disjoint per-dataset contributions:

| Knob                                                                 | Heat path                       | Poisson path                     | Independent contribution        |
|---                                                                   |---                              |---                               |---                              |
| Knob 1 — capacity (`hidden 16→32, modes (4,5,5,5)→(4,8,12,12), blocks 2→3`) | gating off (1.0/1.0), full effect | gating on, capacity stacks       | Heat 0.1275 → **0.0999** (22% recovery; Knob 2 inert on Heat) |
| Knob 2 — Poisson-gated loss weighting (HF=2.0/LF=0.25)                | gating off (1.0/1.0), inert     | gating on (8× HF up-weighting)   | Poisson 0.0979 → **0.0596** (39% improvement; on top of capacity) |

The two knobs target disjoint datasets and **stack cleanly without
negative interaction**. The composite improvement (0.11173 → 0.07719,
31%) is fully explained by the per-dataset wins.

**Why this matters for cycle planning**: the Researcher's
4-orthogonal-lever decomposition for Poisson (capacity / LF-down-weighting
/ epochs / basis K) is **empirically validated** at the first two
levers. Levers can be exercised independently in subsequent cycles —
they do not require co-tuning. Each remaining lever (epochs, basis K)
is a candidate single-knob cycle-003 hypothesis with predictable
per-dataset effect.

**Why MFRNP recipes port across architectures**: the
`Poisson5_config.yaml` HF=2/LF=0.25 weighting was published for MFRNP's
own residual stack. Applying it verbatim to `fno_mf_stack` (a
different residual-stack family with FNO backbones rather than MFRNP's
original components) reproduced the predicted Poisson improvement.
This suggests the loss-weighting recipe is
**inductive-bias-agnostic** within the family of residual-stack
MF architectures.

**Architectural rule**: when porting a published config from one MF
family to a related family with a different backbone, the per-fidelity
loss-weighting and capacity knobs are good first ports — they are
backbone-orthogonal. Architectural knobs (depth, attention vs spectral,
ODE vs MLP basis) do NOT port and must be re-justified.

**Source**: [[factory_mffp-003-experiment]],
`models/fno_mf_stack/smoke_eval.py` Knob 1 + Knob 2,
[[niu2024mfrnp]] (Poisson5_config.yaml),
[[research-cycle-002]] (4-lever decomposition).

## Within-family F5 resolution — exhaust capacity + dataset-gated loss weighting on existing family before proposing a hybrid

Discovered in **factory_mffp cycle 002 H4 R4** (2026-05-15). Cycle 001
surfaced the F5 `INVERSE_COMPLEMENTARY_FAMILIES` failure mode: H1
(coregionalization) wins Heat 0.0154 / loses Poisson 0.7725; H2
(residual stack) wins Poisson 0.0979 / loses Heat 0.1275. The natural
cycle-002 response was a hybrid (cycle-002 H3 `fno_coreg_residual`)
combining both inductive biases into one architecture.

H4 partially resolves F5 **within the residual-stack family alone**,
without needing the hybrid:

| Family + cycle                  | `ifc_heat`              | `ifc_poisson`            |
|---                              |---                      |---                       |
| H1 — coregionalization (cycle 1)  | **0.0154 (beats paper)**| 0.7725 (21× over paper) |
| H2 — residual stack (cycle 1)    | 0.1275 (1.7× over paper)| **0.0979 (2.7× over paper)** |
| **H4 — residual stack + capacity + Poisson loss (cycle 2)** | **0.0999 (1.35× over paper)** | **0.0596 (1.66× over paper)** |

H4 produces a **single-family architecture that wins both datasets
versus all priors except H1's Heat result**. The structural argument
for the hybrid (no single inductive bias dominates both regimes) is
weakened — at sufficient capacity + dataset-gated loss weighting,
the residual-stack family dominates Heat-and-Poisson-but-not-H1's-Heat.

**Architectural rule**: before proposing a hybrid family to address
F5 (inverse complementary families), exhaust capacity and
dataset-gated training-loss knobs on the existing best-of-each-family
candidates. F5 may be a **smoke-config artefact** in disguise — when
the existing family hits its true capacity, F5 may partially or fully
collapse.

**Residual gap to H1's Heat**: H4 is still ~6.5× worse than H1 on
`ifc_heat` (0.0999 vs 0.0154). This is the only remaining structural
gap and it argues that the H1 coregionalization head's continuous-m
basis carries an inductive-bias advantage on clean dynamics that the
H4 residual stack cannot fully match through capacity scaling alone.
The H3 hybrid (continuous-m basis head over residual stack) remains a
sensible **upside test** for closing this gap; it just is no longer
load-bearing for project-overall capability.

**Cycle planning rule**: when F5 is at least partially resolved
within-family, demote any planned hybrid hypothesis to "optional
upside test" priority and prefer **single-knob extensions of the
winning family** (e.g., more epochs, larger K/modes) as the
higher-EV next move.

**Update (factory_mffp cycle 002 H3 R4, 2026-05-15)**: the demoted-but-
not-cancelled H3 hybrid was run as an "optional upside test" and turned
out to **further resolve F5 at the architectural level** beyond what H4
achieved within-family — see §"F5 architectural resolution: compose
orthogonal inductive biases as basis-head + MFRNP residual stack"
below for the canonical recipe. The within-family rule above still
stands as the **first move**: exhaust capacity + loss-weighting before
proposing a hybrid. The architectural-resolution rule applies as the
**follow-on move** when within-family resolution leaves a residual
per-dataset gap that motivates composition with a different family's
inductive bias.

**Source**: [[factory_mffp-003-experiment]],
[[factory_mffp-001-experiment]] (H1 Heat 0.0154 reference),
[[factory_mffp-002-experiment]] (H2 baseline 0.1275/0.0979),
[[failure-analysis-cycle-002]] (F5 original framing),
[[cycle-002-strategy]] (H3 hybrid hypothesis — now validated as
upside),
[[factory_mffp-004-outcome]] (H3 architectural resolution).

## F5 architectural resolution: compose orthogonal inductive biases as basis-head + MFRNP residual stack

Discovered in **factory_mffp cycle 002 H3 R4** (2026-05-15). The F5
`INVERSE_COMPLEMENTARY_FAMILIES` failure mode — where two model
families each beat the published paper on one of two datasets but fail
on the other — **CAN be resolved by composing the two inductive biases
in a single architecture**, provided each bias attacks an orthogonal
bottleneck. The composition pattern that worked here:

1. **Keep the residual-stack-with-decoder-in-the-aggregation backbone**
   (H2's MFRNP pattern from `niu2024mfrnp` — right for stiff dynamics
   with few HF samples). This is the base anchor — provides the LF
   ensemble + decoder + aggregator structure that the Poisson result
   depends on.
2. **Replace the standard MLP HF head with a continuous-m basis head**
   (H1's coregionalization pattern from `li2022ifc` — right for smooth
   fidelity progression on clean dynamics). HF prediction becomes
   `y_HF = MFRNPAggregator(...) + Σ_{k=1..K} B_k(m) · h_k(x)`,
   with `B(m) = MLP_B([m, m²])` and K=10. The basis residual term is
   the load-bearing addition that unlocks the Heat regime.
3. **Keep per-fidelity output normalization mandatory**
   (cross-cutting cycle-001 finding — mechanically resolves the
   y-scale-across-fidelities shift; observed ~40× collapse on
   `ifc_poisson`). Without normalization the composition does not
   train.
4. **Initialize the basis-head last layer to zero** so the
   architecture starts as the better-of-the-two-parents baseline
   (pure MFRNP aggregator at epoch 0) and optimisation grows the
   residual. Critical safety mechanism — the basis residual cannot
   destabilise training because it contributes zero at initialisation.

**Empirical result** (factory_mffp cycle 002 H3 R4, 2026-05-15): the
composition **works** — the dominant per-dataset wins from each parent
family survive in the hybrid:

| Family + cycle                                                | `ifc_heat`                       | `ifc_poisson`                | Composite | Beats paper geomean? |
|---                                                            |---                               |---                           |---:       |---                   |
| H1 — coregionalization (cycle 1)                                | **0.0154 (beats paper 4.8×)**   | 0.7725 (21× over paper)     | 0.10919   | no                   |
| H2 — residual stack (cycle 1)                                   | 0.1275 (1.7× over paper)         | **0.0979 (2.7× over paper)** | 0.11173   | no                   |
| H4 — residual stack + capacity + Poisson loss (cycle 2)         | 0.0999 (1.35× over paper)        | **0.0596 (1.66× over paper)** | 0.07719  | no                   |
| **H3 — basis-head + residual-stack hybrid (cycle 2)**            | **0.02634 (beats paper 2.81×)**   | 0.07416 (2.06× over paper)  | **0.04420** | **YES (0.86×, first time)** |

- Heat: H3 dramatically improves over H4 (0.0999 → 0.02634, 74%) by
  inheriting H1's basis-head inductive bias. **Beats published paper
  bar 0.074 by 2.81×.** First family in project history (other than
  H1) to beat the paper Heat bar.
- Poisson: H3 holds the H2-family direction (0.07416, well under H1's
  0.7725 by 10×) but regresses 25% vs H4 (0.07416 vs 0.0596). The
  regression is **fully accounted for** by the H4 Poisson loss-weight
  knob (HF=2.0/LF=0.25) not being ported into H3 — a mechanical fix,
  not a composition failure. Cycle-003 H5 is pre-registered as exactly
  this port.
- Composite: H3 is the **first family in project history to beat the
  published paper composite-geomean** (0.04420 < 0.05157, 0.86×).

**Architectural rule**: when an MF dataset family exhibits F5
(inverse complementary family wins across datasets), and within-family
resolution (capacity + dataset-gated loss weighting) leaves a residual
per-dataset gap, propose the basis-head + MFRNP-residual-stack
composition as the next cycle's hypothesis. Each of the four steps
above is load-bearing:

- Step 1 alone (MFRNP only) = H4-family behaviour. Heat regression
  remains.
- Step 2 alone (basis head only) = H1-family behaviour. Poisson
  regression remains.
- Step 3 (normalisation) is mandatory regardless of composition —
  Poisson value-scale shift must be addressed independently.
- Step 4 (zero-init) is the safety mechanism enabling Step 2 + Step 1
  to coexist at training start; without it the basis residual may
  destabilise the aggregator anchor.

**Composition validity is target-predictable**: the strategist
predicted composite ~0.04 conditional on both parent wins surviving
composition. Realised composite = 0.04420 — **target hit spot-on**.
This pattern is suitable for ex-ante target setting in future
F5-shaped cycles.

**Limits of the recipe** (open empirical question):
- The recipe was validated on a 2-dataset suite (`ifc_heat`,
  `ifc_poisson`) where the two parent inductive biases attacked
  visibly orthogonal bottlenecks (smoothness vs. stiff HF correction).
  Whether the same recipe generalises to 3+ datasets with multiple
  inductive-bias mismatches is unknown.
- The recipe assumed both parent families had **already cleared the
  per-fidelity normalization hygiene** — composition over un-normalised
  inductive biases has not been tested.
- The cycle-003 H5 port of H4's Poisson loss reweighting is the
  natural next test of whether the architectural composition stacks
  cleanly with the training-recipe lever (predicted: yes; predicted
  composite ~0.035-0.040).

**Source**: [[factory_mffp-004-outcome]] (full empirical detail),
[[factory_mffp-004-build]] (architectural spec + line-by-line
verification),
[[factory_mffp-001-experiment]] (H1 basis-head inductive bias
provenance — beats paper Heat 4.8×),
[[factory_mffp-002-experiment]] (H2 MFRNP residual stack inductive
bias provenance — beats paper Poisson direction),
[[factory_mffp-003-experiment]] (H4 within-family F5 resolution +
Poisson loss-weight knob — the cycle-003 H5 piece not yet ported),
[[li2022ifc]] (basis head + continuous m source),
[[niu2024mfrnp]] (MFRNP residual stack + decoder-in-aggregation +
Poisson5_config.yaml source).

## MFRNP per-fidelity loss-weighting recipes are backbone-coupled across MF aggregation architectures (REFINES the "MFRNP knobs orthogonally decompose" cycle-002 pattern)

Discovered in **factory_mffp cycle 003 H1 R4** (2026-05-15). Static
per-fidelity loss-weighting recipes from MFRNP-family configs (e.g.
the verbatim `Poisson5_config.yaml` `(HF=2.0, LF=0.25)` 8:1 HF
up-weighting) **do NOT port cleanly across all MF-aggregation
architectures**. The recipe is **backbone-coupled**, not
backbone-independent. The cycle-002 H4 framing that the recipe is
"inductive-bias-agnostic within residual-stack MF architectures" is
**bounded** — it ports within the residual-stack-on-FNO family
(MFRNP's own backbone → `fno_mf_stack`) but does NOT port across to
the hybrid basis-head + MFRNP-residual-stack family
(`fno_coreg_residual`).

**Empirical decisive test** (cycle-003 H1, same `(2.0, 0.25)` recipe,
same `'poisson'` gating, same per-fidelity normalization, same
2-dataset `ifc_heat` / `ifc_poisson` suite, same eval — only the
backbone differs):

| Backbone family                              | ifc_poisson before knob | ifc_poisson after (2.0, 0.25) knob | Delta              |
|---                                           |---:                     |---:                                |---                 |
| `models/fno_mf_stack` (cycle-002 H4)         | 0.0999                  | **0.0596**                         | **−39% (helps)**   |
| `models/fno_coreg_residual` (cycle-003 H1)    | 0.07416                 | **0.27287**                        | **+268% (catastrophic harm; 3.68×)** |

**Mechanism hypothesis** (val/test gap analysis on H1):
`best_val_nRMSE=0.0783` vs `test=0.27287` on H1+poisson suggests the
H3 hybrid's per-fidelity y-scaler + MFRNP decoder-in-the-aggregation
+ continuous-m basis head over HF latent **interacts destructively**
with the asymmetric weighting: upweighting the HF residual (×2.0)
overconcentrates the model's gradient budget on a narrow HF feature
set that overfits, while down-weighting LF supervision (×0.25)
starves the cross-fidelity sharing that H3's coregionalization stack
depends on for generalization. The simpler `fno_mf_stack` aggregation
does not have the same cross-fidelity sharing dependency, so the
asymmetric weighting helps there without the same starvation risk.

**Refuted framing**: the cycle-003 strategy described the recipe as
**"PDE-class-bound (elliptic), not backbone-bound"**, supporting a
compositional argument that H3's IFC-path architectural asymmetry
would compose orthogonally with the MFRNP-path loss-weighting
asymmetry. The clean H1 data refutes this — the recipe is bound to
both the PDE class AND the backbone, and there is no decomposition
into orthogonal architectural and training-recipe factors.

**Architectural rule (REFINED)**: when porting a static MFRNP
loss-weighting recipe across MF families, do NOT assume the recipe is
backbone-portable. The right defaults are:

1. **Within the same residual-stack-on-FNO family** (MFRNP → H2 →
   H4): static recipes port with high confidence. Continue treating
   these as "free pre-registered knobs".
2. **Across to hybrid families** (`fno_coreg_residual` and successors
   that compose basis-head with MFRNP-residual-stack): static
   per-fidelity weighting must be either (a) re-tuned per backbone or
   (b) replaced with an **adaptive scheme** — GradNorm-lite,
   uncertainty-weighted, or PCGrad-style — that learns per-step
   per-fidelity weights from observed gradient magnitudes.
3. **As a milder fallback**: try a less aggressive asymmetric ratio
   (e.g. (1.5, 0.5) instead of (2.0, 0.25)) when re-tuning per
   backbone is not affordable. The 8:1 ratio is the published number
   for MFRNP's own backbone; nothing privileges that exact value as
   universal.

**Why this matters for cycle planning**: every future cycle that
proposes "lift a training-recipe knob from family X to family Y" must
explicitly answer "is family Y's MF-aggregation structurally similar
enough to family X that the recipe will transfer?" — and prefer
adaptive variants when the answer is unclear or the families differ
in cross-fidelity sharing structure. The cycle-002 H4 → cycle-003 H1
port was a clean test of the recipe-portability question; the answer
is "no, not across to hybrid families".

**Status**: this pattern **bounds** but does NOT invalidate the
cycle-002 H4 finding ([[patterns]] §"MFRNP `Poisson5_config.yaml`
knobs (capacity + per-fidelity loss weighting) are independently
load-bearing and orthogonally decompose by dataset"). Both patterns
stand:
- **Within-residual-stack-on-FNO**: the H4 finding still holds —
  capacity and Poisson-only loss-weighting decompose cleanly by
  dataset and stack without interaction.
- **Across to hybrid families**: this new H1 finding refines the H4
  pattern — the loss-weighting half of the H4 finding does NOT
  generalize beyond the residual-stack family.

**Process rule**: when a published config (MFRNP `Poisson5_config.yaml`,
`pde_config.yaml`, etc.) is proposed for porting in a cycle plan,
the Strategist must explicitly cite the **backbone family** the
config was published on, and the Researcher must surface any evidence
that the recipe has been replicated on a different backbone family
before the Strategist treats it as "backbone-portable". Absent such
evidence, the recipe is **provisionally backbone-coupled** by default
— either re-tune per backbone or use an adaptive replacement.

**Source**: [[factory_mffp-005-experiment]] (full empirical detail,
val/test gap analysis, contamination handling),
[[factory_mffp-005-build]] (build-phase spec + Builder design choice
on anchor scaling),
[[factory_mffp-003-experiment]] (cycle-002 H4 — recipe ported within
residual-stack family, providing the framing this pattern refutes),
[[factory_mffp-004-outcome]] (cycle-002 H3 — the hybrid architecture
this cycle attempted to extend; project-best baseline preserved by
the REVERT),
[[niu2024mfrnp]] (MFRNP architecture template + Poisson5_config.yaml
provenance),
[[li2022ifc]] (basis-head provenance carried through cycle-003 H1),
[[chen2018gradnorm]] (cycle-004 adaptive-weighting candidate framework).

---

## `revert_bookkeeping_keep_intent` is the universal verdict — substring-collision precheck bug gates every eval (cycles 001–007)

**First observed**: cycle-001 H1 (`fno_coregionalization` poisson 5×
loss-reweighting).
**Most recent re-confirmation**: cycle-007 H1
(`fno_coregionalization` anisotropic-modes constructor fix; new
reproducible project best composite 0.030408), 2026-06-02.
**Cumulative count**: **8 evals run, 8 evals gated by precheck
bookkeeping → 8 `revert_bookkeeping_keep_intent` verdicts.**
**Cycle coverage**: **6-of-6** cycles run (001, 002, 003, 005, 006,
007 — 004 not run as a cycle).

### Catalog

| Cycle | Hypothesis | Precheck failure mode | Verdict |
|---    |---         |---                    |---      |
| 001 H1 | `fno_coregionalization` Poisson 5× loss-reweighting | substring-collision `"poisson"` | `revert_bookkeeping_keep_intent` |
| 001 H2 | `fno_mf_stack` extra fidelity ladder | substring-collision `"001"` (dataset-name token) | `revert_bookkeeping_keep_intent` |
| 002 H4 | `fno_mf_stack` capacity + Poisson loss bump | substring-collision `"poisson"` | `revert_bookkeeping_keep_intent` |
| 002 H3 | `fno_coreg_residual` hybrid (NEW PROJECT BEST 0.04420) | substring-collision + score improvement | `revert_bookkeeping_keep_intent` (project best preserved on branch) |
| 003 H1 | `fno_coreg_residual` Poisson loss-reweighting port | substring-collision + score regression (genuine revert) | `revert_bookkeeping_keep_intent` |
| 005 H1 | `mf_fno_transfer_bar` REPO_ROOT off-by-one fix | pre-existing dirty tree + downstream + substring-collision (5 tokens) | `revert_bookkeeping_keep_intent` |
| 005 H2 | `fno_coregionalization` two-stage LF→HF transfer (NEW PROJECT BEST 0.029357 — aspirational, later non-reproducible) | score_direction polarity (FP on lower-is-better improvement) + pre-existing dirty tree + downstream + substring-collision (`modify`/`satisfy`/`ifc_raw`) | `revert_bookkeeping_keep_intent` (preserved on `experiment/7-fno_coreg_lf_hf_transfer @ be36cba`) |
| **007 H1** | **`fno_coregionalization` anisotropic-modes constructor fix (NEW REPRODUCIBLE PROJECT BEST 0.030408, −23.17% in single cycle)** | **score_direction polarity (FP — flips −23% improvement to +23% "regression") + empty-detail `scope` + empty-detail `fixed_surfaces` (3 infra bugs; standalone `factory guard --check-scope` reports `clean`); all 3 real checks (`ground_truth_leakage`, `anti_pattern`, `smoke_test`) PASSED** | **`revert_bookkeeping_keep_intent` (preserved on `experiment/9-fno_coregionalization-constructor-fix @ 1249f2d`; cycle-008 entry baseline)** |

### Mechanism

The leakage scanner (`factory leakage-check`) does string-substring
matching against ground-truth files under `data/**`. It does NOT
differentiate:

- **Value tokens** (actual ground-truth answers — should flag).
- **Schema/category tokens** (`"description"`, `"frozen"`,
  `"ifc_raw"`, `"ifc_heat"`, `"poisson"`, `"001"` — naming the
  dataset or model family, NOT a ground-truth answer — should NOT
  flag but does).
- **Documentation tokens** (`"modify"` in a sacred-rule sentence,
  `"loader"` in a debug-print format string — generic English /
  programming nouns — should NOT flag but does).

Every cycle that touches a model family whose name (or whose
dataset's name) appears as a token in `manifest.json`, `factory.md`,
or `README.md` will trip the scanner. Since this is *every* family in
the project, **the precheck is structurally guaranteed to fail on
every PR diff**. The override pattern is documented and operational,
but the gate semantics mean main is never directly updated by the
factory; all genuine science accrues on preserved experiment
branches.

### Two consequences for cycle planning

1. **No experiment ever merges to `main`.** Downstream experiments
   that need to inherit a prior fix must branch from the **preserved
   experiment branch**, not from `main`. Cycle-005 H2 is the latest
   instance: H2 branches from `experiment/6-mf_fno_transfer_bar-repo-root-fix`
   to inherit H1's REPO_ROOT fix.
2. **Strategy-phase leakage projections are lower bounds, not
   guarantees.** Cycle-005's strategy snapshot projected "first cycle
   without substring-collision false-positives" because the
   science-edit alone (1 line in `smoke_eval.py`) carried no
   colliding tokens. The Build phase reintroduced the failure mode by
   newly tracking `manifest.json` — which contains schema tokens
   `"description"`, `"ifc_raw"`, `"frozen"`. **What gets committed**,
   not just what the science edit changes, determines whether the
   scanner trips.

### Out-of-scope (open since cycle-001)

The scanner needs token-class differentiation (value vs schema vs
documentation). This is factory-infrastructure work, not
model-science work — out of scope for any experiment in this
project. Tracked as the longest-running open follow-up.

### How to apply this pattern in future cycle reviews

- A `revert_bookkeeping_keep_intent` verdict on an experiment whose
  science is correct is **not** a science failure — preserve the
  branch, do not delete it, and use it as the base for downstream
  experiments that depend on the fix.
- A strict-playbook reading of "precheck FAIL → revert" must be
  overridden by the documented `revert_bookkeeping_keep_intent`
  precedent when (a) all flagged tokens are documentation/schema
  rather than ground-truth values, and (b) the science edit is
  verified correct by direct file read.
- Strategy snapshots that claim "this cycle will pass precheck" must
  account for **all files in the eventual PR diff**, not just the
  science-edit file. If a strategy plans to newly track a
  `manifest.json`, expect the scanner to fire.

**Source**: [[factory_mffp-006]] (cycle-005 H1 full detail; the
6-for-6 tally),
[[factory_mffp-005-experiment]] (cycle-003 H1 — also a genuine
revert that happened to be covered by the same bookkeeping pattern),
[[factory_mffp-004-outcome]] (cycle-002 H3 — project best preserved
on branch because of this same bug),
[[factory_mffp-003-outcome]] (cycle-002 H4),
[[factory_mffp-002-experiment]] (cycle-001 H1/H2 — pattern origin).



## Multi-fidelity transfer-learning recipes are PDE-class-coupled across datasets within the same architecture

Discovered in **factory_mffp cycle 005 H2 R4** (2026-06-02). The
two-stage LF→HF transfer-learning schedule from
`mf_fno_transfer_bar` (`pretrain_lr=1e-3`, `finetune_lr=3e-4`,
`pretrain_frac=0.25`, fresh `Adam` + `CosineAnnealingLR` per stage)
was ported verbatim into `fno_coregionalization` — training-schedule
only, architecture unchanged. Originally framed as "same recipe, two
datasets, opposite outcomes (−24% Heat, +15× Poisson regression)";
**cycle-006 cache-hash forensics CORRECT this framing** — see the
correction block immediately below.

### CRITICAL FRAMING CORRECTION (cycle-006 baseline, 2026-06-02)

The cycle-005 H2 session-summary framing that "H2 broke Poisson 15×"
was an **across-family comparison error**. Cache hash forensics in the
cycle-006 baseline `summary.json` show:

| Stage                                                | hash       | `fno_coregionalization` Poisson nRMSE |
|---                                                   |---         |---:                                   |
| Pre-H2 (cycle-005 R0 baseline)                       | `9528aeef` | **0.77562** (already architecturally broken) |
| Post-H2 (cycle-005 H2 = cycle-006 R0)                 | `2954a13e` | **0.75015** (−3.3% improvement)        |

**H2's actual per-dataset effect on `fno_coregionalization`:**

| Dataset       | Pre-H2 (cycle-005 R0) | Post-H2 (R4)      | Δ                                |
|---            |---:                   |---:               |---                               |
| `ifc_heat`    | 0.02047               | **0.01551**       | **−24.2%** (NEW family-best, holds #1; gap to mf_fno_transfer_bar grew from 1.6× to 2.1×) |
| `ifc_poisson` | **0.77562**           | **0.75015**       | **−3.3% (improvement)** (architecture already broken on Poisson pre-H2; schedule essentially neutral) |

The "+15×" figure compared `fno_coregionalization`'s **own** Poisson
nRMSE (0.75015) against the **other family's** Poisson winner
(`fno_coreg_residual` @ 0.05556) — a 13.5× ratio against a different
family's number, not against `fno_coregionalization`'s prior Poisson.
**H2 did NOT introduce the Poisson failure**; the failure predates H2
and is architectural (single shared FNO trunk + K=10 basis head cannot
encode Poisson's cross-fidelity scale mismatch — see
[[failure-analysis-cycle-006]] §C.1).

**Mechanism (grounded in earlier patterns), revised:**
- ifc_heat: smooth fidelity correlation; LF→HF transfer easy; Stage 1
  LF warm-up converges the K=10 basis head to a representation that
  Stage 2 joint training refines without overfit. H2 delivers a clean
  −24%.
- ifc_poisson: stiff value-scale shift across fidelities (see
  [[patterns]] §"Per-fidelity output normalization is the cheapest
  large win for value-scale-shift MF datasets" — Poisson solution
  magnitude collapses ~40× from L1 to L4) AND the basis head's K=10
  capacity is insufficient to encode the cross-fidelity scale mismatch.
  The architectural failure is upstream of any LF→HF schedule, so H2
  acts uniformly small (−3.3%) regardless of the schedule design.

**This is a clean variant of the cycle-003 H1 finding** that "MFRNP
per-fidelity loss-weighting recipes are backbone-coupled". The
cycle-003 version was *recipe-couples-to-backbone* (within a fixed
dataset); the cycle-005 H2 version is *recipe-couples-to-PDE-class*
(within a fixed backbone). Combined rule: **multi-fidelity training
recipes are not portable knobs — they couple to both the backbone
and the PDE class.** Any port of a recipe across either dimension
needs an A/B per-dataset to confirm direction.

**Cycle-006 refinement (post-correction)**: the PDE-class coupling
manifests *through pre-existing architectural failure modes*, not
necessarily as recipe-induced regressions. On `fno_coregionalization`
the architecture's K=10 basis head could not encode Poisson's
cross-fidelity scale mismatch *before* the H2 schedule was applied;
H2 acted approximately neutrally on Poisson because the failure is
upstream of the schedule. The detection signature is therefore
"recipe does opposite things on dataset A vs B" — but the underlying
mechanism may be (i) recipe directly hurts one dataset, OR (ii)
architecture is pre-broken on one dataset and the schedule can't fix
it. Both still warrant dataset-conditional gating.

**How to detect (pre-experiment screen)**:
- If the target dataset has >5× per-fidelity value-scale collapse
  (Poisson-class, elliptic-class with finite-difference normalization),
  treat LF-pretrain schedules as a risk, not a default.
- If the donor recipe was tuned on a dataset that has *also* used
  per-fidelity scaling, the recipe is implicitly compensating for
  value-scale shift in the donor and may de-tune the target.

**Cycle-006 design rule (load-bearing)**: any LF→HF transfer schedule
on a multi-PDE-class smoke harness must be **dataset-conditional** —
gate `n_warmup` (or the LF-only Subset filter) on dataset name, by
analogy with cycle-002 H4's `resolve_fidelity_weights(dataset_name)`
per-dataset switch. Concrete proposed lever: set `n_warmup=0` (skip
Stage 1) when `"poisson"` in dataset name, retain the bar recipe
otherwise. Expected outcome: ifc_poisson recovers to ~0.05 (back to
R0), ifc_heat preserved at 0.01551, composite improves further from
0.029357 toward ~0.024 (crosses bar parallel-bench 0.02743).

**Confirmed (factory_mffp cycle 005 H2 R4, 2026-06-02)**: see
[[factory_mffp-007]]. Composite-level performance is unaffected
because the per-dataset best-family partitioning routes Poisson to
`fno_coreg_residual` (still owns ifc_poisson at 0.05556) — but the
side effect would be project-fatal on any cycle that elevates
`fno_coregionalization` to the poisson leader without dataset-
conditional gating.

**Source**: [[factory_mffp-007]] (cycle-005 H2 R4; LF→HF schedule
opposite-direction outcomes across Heat vs Poisson),
[[factory_mffp-005-experiment]] (cycle-003 H1; MFRNP loss-weighting
recipe is backbone-coupled — the precursor variant of this rule),
[[failure-analysis-cycle-006]] (cycle-006 baseline; cache-hash
forensics that corrected the H2 framing).

---

## `PDE_CLASS_ARCH_RECIPE_COUPLING` is the dominant in-tree failure mode at cycle 006 — 80% of (family × dataset) instances are not the dataset winner

Discovered in **factory_mffp cycle 005 H2** as the NEW PATTERN;
**re-confirmed in cycle 006 baseline** (2026-06-02). One global
`SMOKE_DEFAULTS` per family with no dataset-name gating; the
recipe-tuned good behavior on dataset A breaks the family on B. The
composite metric papers over this by routing each dataset to whichever
family currently owns it, but **no single in-tree family is
simultaneously competitive on both** `ifc_heat` and `ifc_poisson`.

### Evidence — 5 in-tree families × 2 datasets = 10 instances (cycle-006 baseline)

| family ↓ / dataset →            | ifc_heat        | ifc_poisson    |
|---                              |---              |---             |
| fno_coregionalization (H2)      | #1 0.01551 ✓     | #5 0.75015 ✗    |
| fno_coreg_residual              | #3 0.03519 ~     | #1 0.05556 ✓    |
| fno_mf_stack                    | #5 0.13010 ✗     | #3 0.08829 ~    |
| transolver_residual             | #4 0.11430 ✗     | #6 2.59704 ✗    |
| transolver_attention_fusion     | #7 0.14916 ✗     | #4 0.38327 ✗    |
| (bar) mf_fno_transfer_bar       | #2 0.03317 ~     | #2 0.08333 ~    |

The **only family with comparable per-dataset rank is the bar** —
`mf_fno_transfer_bar` sits at #2 on both. Every in-tree family is
dataset-coupled.

### Failure distribution (10 instances)

```
PDE_CLASS_ARCH_RECIPE_COUPLING:   2 / 10 (20%)   fno_coregionalization·poisson, fno_mf_stack·heat
NO_TRANSFER_SIGNAL_*:             2 / 10 (20%)   fno_coreg_residual·heat (#3), fno_mf_stack·poisson (#3)
ARCH_QUALITY_FAILURE:             4 / 10 (40%)   transolver_residual + transolver_attention_fusion × both
PASS (winner):                    2 / 10 (20%)   fno_coregionalization·heat, fno_coreg_residual·poisson
```

**80% of in-tree instances are not the dataset winner.** Half are
PDE-coupling failures within an otherwise viable architecture (fixable
by recipe gating); half are architecture-quality failures (fixable only
by backbone change). Fixing the 40% arch-quality instances
(transolver_*) does NOT close the composite gap — Poisson winner is
already `fno_coreg_residual` at 0.0556.

### Cheapest fix — dataset-conditional recipe gating

The first-move fix that costs ~5 lines in `models/<family>/smoke_eval.py`:
read `args.dataset_name`, look up `_DATASET_RECIPES[dataset_name]`,
merge into `SMOKE_DEFAULTS`. Documented as cycle-006 F.1 / F.2 in
[[failure-analysis-cycle-006]]. The gating is **monotonic** — it
adds no new failure paths, only preserves existing wins while
unblocking dataset-specific recipe experimentation.

### New sub-categories named at cycle 006

- **`NO_TRANSFER_SIGNAL_HEAT`** — family has the right backbone but
  lacks the LF→HF transfer/curriculum trick that the leader uses on
  Heat (e.g., `fno_coreg_residual` at #3 on Heat — no LF warmup at all
  in its smoke recipe).
- **`NO_TRANSFER_SIGNAL_POISSON`** — mirror of above on Poisson.

These are the "fixable by recipe gating" half of the 80% of non-winning
instances.

**Architectural rule (cycle-006 update)**: when building a new MF
family on a multi-PDE-class smoke harness, **never** ship a single
global `SMOKE_DEFAULTS` for all datasets. Every recipe knob with
PDE-class-sensitive effect (transfer schedule, loss weighting,
per-fidelity scaler choice, basis K) must be selectable per-dataset
via `_DATASET_RECIPES[dataset_name]`. Default fallback preserves
existing behavior so unrelated datasets are unaffected.

**Source**: [[failure-analysis-cycle-006]] (cycle-006 baseline 10-instance
breakdown), [[factory_mffp-007]] (cycle-005 H2 — pattern origin name),
[[factory_mffp]] (project dashboard with current per-dataset leaderboard).

---

## Local-archive fallback survives WebSearch outage when prior cycle has conducted equivalent web research

Discovered in **factory_mffp cycle 006 Research** (2026-06-02). The
Researcher session attempted ≥10 distinct WebSearch / WebFetch queries
across the cycle-006 question set (loss reweighting, transfer-learning
composition, post-2024 elliptic-PDE FNO variants, spectral-attention
gating). **Every query returned HTTP 529 (overloaded).** The Researcher
proceeded by drawing entirely from the local archive
(`.factory/archive/sources/`) and the in-tree inline citations in
`mf_fno_transfer_bar/smoke_eval.py` and `fno_coregionalization/smoke_eval.py`.

The fallback worked **because cycle-003 had already conducted ~20
web-sourced citations on this exact problem space** (HF/LF loss
reweighting in MF training), preserved as
[[research-cycle-003]]. Every citation in cycle-006's Researcher output
carries an original BibTeX key and an arXiv ID / DOI traceable to
cycle-003 or to in-tree code — **no hallucinated references**.

**Why this matters:** the factory's institutional memory just demonstrated
its load-bearing role under degraded external conditions. Cycle-003's
Mode-4 research investment paid off three cycles later when the API was
unavailable, by pre-staging the four theoretical lenses (effective-sample-mass,
Green's-function global support, gradient pathology, empirical precedent)
that the cycle-006 Top-1 recommendation depends on.

### Process rule

When WebSearch / WebFetch returns repeated HTTP 529 or similar
service-unavailable errors:

1. **Do NOT hallucinate.** Acknowledge the outage explicitly in the
   Researcher output. Do not generate plausible-looking arXiv IDs or
   DOIs without verifying them against the local archive.
2. **Audit the local archive first.** Before declaring "cannot answer",
   grep `.factory/archive/sources/` for prior cycles' research on the same
   problem space. Cycle-003-style Mode-4 research sessions often produce
   carry-forward citation libraries that survive multiple downstream cycles.
3. **Cite preserved BibTeX keys verbatim** with their original arXiv /
   DOI links. Do not "translate" or paraphrase a citation key — the
   archive's link integrity is the proof against hallucination.
4. **Flag deferred queries** explicitly for the next cycle to retry —
   keep a list at the bottom of the cycle's research note so the next
   Researcher knows what to revisit when the API recovers.

### When this fallback will NOT work

- **New problem space the archive has not covered.** If the Researcher
  needs post-2024 papers on a topic the factory has never investigated,
  the archive cannot substitute for the API. In that case the right
  move is to (a) acknowledge the gap, (b) draw the strongest possible
  inference from in-tree code + prior cycles' related-but-not-identical
  work, and (c) explicitly mark the inference as bounded by the
  outage.
- **Citations requiring real-time verification.** If the cycle plan
  depends on confirming a specific paper's recent benchmark number, the
  archive's snapshot may be stale — flag and proceed cautiously.

### Cycle-006 instance details

- ≥10 distinct queries attempted; 0 successful.
- 100% of cycle-006 Researcher citations are traceable to the local
  archive or in-tree code; verified by the CEO review
  (`.factory/reviews/ceo-verdict-researcher.md` §"Acknowledged honestly
  the WebSearch HTTP 529 outage; substantiated the fall-back via the
  rich local archive").
- Deferred queries for cycle-007: post-2024 selective HF-modes-only
  capacity bump for elliptic problems; adapter/LoRA-style lightweight
  HF heads on top of LF-pretrained FNO; spectral-attention /
  frequency-conditional gating for FNO modes; direct FNO-trunk +
  FNO-residual-head transfer reference (would confirm Top-3 composition
  argument empirically).

**Source**: [[research-cycle-006]], [[research-cycle-003]] (the
load-bearing prior research investment that made this fallback viable),
`.factory/reviews/ceo-verdict-researcher.md` (cycle-006).

---

## Cross-architecture recipe portability is NOT guaranteed even when receiving architecture shares structural family

Discovered in **factory_mffp cycle 006 H1** (2026-06-02, REVERT verdict).
This pattern is the **architecture-axis** complement to the cycle-005
H2 PDE-class-coupling pattern. Together they bound the portability
hypothesis-space for MF recipes.

### Evidence

The MFRNP `(HF=2.0, LF=0.25)` per-fidelity loss-weighting recipe — a
cite-grounded Poisson winner on `fno_mf_stack` @ 0.0596 — was ported
into `fno_coreg_residual`, which **shares the same structural family**
(per-fidelity FNO ladder + coregionalization basis head). Cycle-003
Strategist Hand-off predicted "clean transfer because of structural
family share". Result:

| Family                 | ifc_poisson before recipe | ifc_poisson after recipe | Δ                |
|---                     |---:                       |---:                      |---:              |
| `fno_mf_stack`         | (literature baseline)     | 0.0596 (cited)           | (recipe winner)  |
| `fno_coreg_residual`   | 0.05556                   | 0.05756                  | **+3.6% regress**|

**The recipe did NOT transfer.** And as an unexpected side effect, the
*architectural* part of the bundle (K=10→20, b_hidden→128) improved
Heat on `fno_coreg_residual` by −13.1% (0.03519 → 0.03059) —
disambiguating the architectural-capacity contribution from the
loss-weighting contribution.

### Mechanism

The receiving family had an **implicit handler** for the asymmetry the
recipe was designed to address. `fno_coreg_residual`'s residual decoder
pathway already absorbs the LF/HF gradient asymmetry that the MFRNP
loss weights manually impose on the simpler `fno_mf_stack`. **Adding the
recipe over-weights an asymmetry that's already handled implicitly**,
producing a regression rather than a no-op.

### Architectural rule

When porting a recipe across architectures within the same structural
family, the receiver's gradient pathway must be empirically verified to
NOT already implement the asymmetry the recipe imposes. Check before
porting:

1. Does the receiving architecture have a residual / skip / decoder
   pathway that could absorb the LF/HF asymmetry implicitly?
2. Does the receiving architecture have a basis / output head that
   re-balances per-fidelity scale at decode time?
3. Is the source-architecture's recipe-win attributable to the
   *recipe* or to the *recipe + architecture interaction*?

If any of (1)–(3) is unverified, do **NOT** rely on structural-family
heuristics; require empirical pilot or treat as exploratory.

### Cite-grounding gives FALSE confidence on this axis

A citation that the recipe works on architecture A is **NOT** evidence
that the recipe will work on architecture B, even when A and B share
structural family. Cycle-003's confidence in the Hand-off prediction
came from a single-architecture citation. Cycle-006 demonstrates this
is insufficient — Researcher / Strategist must explicitly downgrade
confidence when a recipe has not been cited on the *receiving*
architecture.

### Joint application with PDE-class-coupling pattern

MF recipe portability is **two-dimensional**:

- **PDE-class axis** (cycle-005 H2 pattern): recipe-tuned good behavior
  on PDE-class A breaks the family on PDE-class B → use
  `_DATASET_RECIPES` dispatch.
- **Architecture axis** (cycle-006 H1 pattern, this entry):
  recipe-tuned good behavior on architecture A does not improve (and
  may regress) architecture B → require empirical pilot, do not trust
  structural-family heuristics.

Composite cycle-007 rule: a new MF recipe is only "production-ready"
once verified on (PDE-class × architecture) pairs that the deployment
target spans.

### Cycle-006 instance details

- Source-architecture citation: `fno_mf_stack` ifc_poisson 0.0596
  (MFRNP HF=2.0, LF=0.25 recipe + basis head).
- Receiving architecture: `fno_coreg_residual` (same structural family
  per cycle-003 Strategist analysis).
- Result: ifc_poisson 0.05556 → 0.05756 (+3.6% regress); ifc_heat
  −13.1% improved as architectural side effect (K=20 + b_hidden=128
  capacity bump, disambiguable from loss reweighting).
- Verdict: REVERT (CEO override of `score_direction` polarity bug
  false-positive PASS).
- Side effect bankable: K=20 + b_hidden=128 architectural bump is a
  standalone cycle-007 candidate (decoupled from loss reweighting).

### Cycle-007 H2 reinforcement (2-for-2 — now confirmed at higher confidence)

The same MFRNP `(HF=2.0, LF=0.25)` recipe was re-ported into
`fno_coreg_residual` in cycle-007 H2, this time with the recipe
isolated **per-dataset** (anti-pattern #5 from cycle-006 honored —
no Heat-specific entry). Result on `ifc_poisson` alone:

| Source                | ifc_poisson | Δ vs cycle-007 R0 baseline 0.07419 |
|---                    |---:         |---:                                |
| cycle-005 cache target| 0.05556     | (target)                           |
| cycle-007 H2 result   | **0.06087** | **−17.96% (real improvement)**     |
| `fno_mf_stack` winner | 0.05961     | (still leaderboard)                |

- The recipe **directionally** worked this time (−17.96% real
  improvement, distinct from cycle-006's +3.6% regression — note that
  cycle-006's baseline was 0.05556 already at the cycle-005 target;
  cycle-007 R0 was at the higher 0.07419 because of the
  silent-regression cache pattern. The directional improvement is
  with respect to the cycle-007 baseline, not the cycle-005 target.)
- But the magnitude fell **+9.55% short** of the cycle-005 cache
  target 0.05556 — recipe alone does NOT fully recover the cycle-005
  frontier on the receiving architecture.
- And the recipe did NOT take the poisson leaderboard from
  `fno_mf_stack` (0.05961 < 0.06087 by 2.1%). The source architecture
  retains the title.

**Refined rule from 2 instances:**

Cross-architecture recipe portability is **partial at best**, even
within the same structural family. The receiving architecture's
implicit handlers (residual decoder pathway in `fno_coreg_residual`)
absorb some — but not all — of the recipe's intended benefit. Expect:

- Directional sign of effect is usually preserved (the recipe still
  improves the targeted cell, sometimes).
- Magnitude of effect on receiving architecture is typically 50–100%
  of source-architecture's effect.
- Leaderboard movement is rare — the source architecture's native
  optimization for the recipe usually retains the title.

**Strategist projection rule:** when porting a recipe across
architectures within the same structural family, project the
receiving-architecture effect as **0.5 × source-architecture effect**
with high variance, NOT as the source's effect verbatim. Cycle-006
showed the lower bound (+3.6% regress at 100% transfer projection);
cycle-007 H2 showed a middling case (−17.96% improvement, 50% of
the source's win, did not take leaderboard).

### Coupling with the fresh-train invariance pattern

Cycle-007 H2 also exposed a *second*-order failure: when the same
codepath edit that adds the recipe touches the cache hash, even cells
NOT targeted by the recipe (Heat here) can regress because of
fresh-train trajectory variance. See [[patterns]] §"Fresh-train
variance can swamp claimed invariance" for the full mechanism. The
net cycle-007 H2 verdict (REVERT) is the sum of:
- Real Poisson gain (−17.96%, partial portability win).
- Unintended Heat regression (+32.70%, fresh-train invariance failure).
- Composite (geomean): +12.36% regression — Heat side overwhelms
  Poisson side in the geomean composite.

**Source**: [[cycle-006-exp-8]], [[cycle-006-summary]],
[[cycle-007-exp-10]] (cycle-007 H2 reinforcement),
[[factory_mffp]] (project dashboard cycle-006 and cycle-007
close-out sections).

---

## Builder clean-isolation requires pre-clean working tree (`git add <named-file>` is insufficient if file is already dirty)

Discovered in **factory_mffp cycle 006 H1** (2026-06-02). Builder
hygiene pattern. Recurring failure mode of multi-cycle factory work.

### Evidence

Cycle-006 H1 Builder attempt #1 (commit `b0e6cd2`) was instructed to
"`git add` the specific files we modified" — but the named files
(`models/fno_coreg_residual/smoke_eval.py` and `manifest.json`) were
**already dirty** at session start due to pre-existing 15-file data
adapters migration cruft on the working tree. `git add` on an
already-dirty file stages **all** of the pre-existing dirty state, not
just the intended diff.

Result: Builder's "+30/-3" intended scope ballooned to **357 added
lines** — including `hidden=64→32` capacity cut, `supported_datasets`
expansion, and unrelated data-adapter changes, **none of which were
part of H1's hypothesis**. Eval would have measured a confounded
result.

Clean isolation only achieved via Builder redirect #1 (1 of 2 budget
used): `git reset --hard experiment/7-fno_coreg_lf_hf_transfer`
followed by **surgical re-application of only** the loss-weighting +
basis bumps, yielding the +30/-3 LOC final commit `59b741f`.

### Mechanism

`git add <file>` stages the **current working-tree state** of the
file, not "only the changes I just made". If the file was modified
before the session began (i.e., already in working-tree diff), every
pre-session edit is captured by the same `git add`.

### Process rule (mandatory for future Builder sessions)

Before staging hypothesis-scope changes, the Builder must guarantee a
**clean working tree** by one of:

1. **Pre-clean at session start.** If `git status` shows non-empty
   working-tree diff at session start, the Builder must surface this
   to the CEO and either (a) commit / stash / discard the pre-existing
   diff coherently, or (b) abort and request a clean branch checkpoint.
2. **`git checkout HEAD -- <file>` before editing.** For files the
   Builder intends to modify, explicitly reset to `HEAD` before
   applying the hypothesis edits. This guarantees `git add <file>`
   captures only the hypothesis diff.
3. **`git diff --cached HEAD` audit before commit.** Even after
   applying (1) and (2), the Builder must audit the staged diff
   line-by-line against the hypothesis scope and reject any line that
   does not match.

### When this pattern is most likely

- Multi-cycle work where the working tree carries forward
  un-committed migration / refactor cruft.
- Sessions started from a checkpoint that did not include a
  `git status` check.
- Hypotheses that touch the same files as a prior cycle's deferred /
  in-progress work.

### Side effect — cycle-005 H2 baseline integrity loss

Builder redirect #1's `git reset --hard` not only cleaned the H1
working tree but also wiped a **dirty `fno_coregionalization/model.py`
that was never committed** but was load-bearing for the cycle-005 H2
composite baseline (0.029357). The committed
`fno_coregionalization/model.py` has a constructor signature mismatch
with `smoke_eval.py` and is non-runnable. **The cycle-005 H2
project-best is now not reproducible from the committed tree.** This is
a downstream consequence of the same pre-clean failure: had the working
tree been clean at cycle-005 H2 commit time, the dirty `model.py`
would have been committed (or surfaced) and the baseline would be
reproducible.

### Cycle-006 instance details

- Builder redirects used: 1 of 2.
- First-attempt commit (`b0e6cd2`): +357 LOC, scope contamination.
- Recovery commit (`59b741f`): +30/-3 LOC, clean isolation.
- Working tree at session start: 15 files dirty from data-adapters
  migration (pre-existing, not from H1 work).
- Downstream side effect: cycle-005 H2 baseline composite 0.029357 is
  not reproducible from committed `experiment/7` tree because
  load-bearing `fno_coregionalization/model.py` was never committed.

**Source**: [[cycle-006-exp-8]], [[cycle-006-summary]],
[[factory_mffp]] (project dashboard cycle-006 close-out operator
action #1 and #2).

---

## Silent regression masked by the cache layer (cycle-006 → cycle-007, second consecutive instance)

Discovered in **factory_mffp cycle 007 R1** (2026-06-02). Cross-cycle
cache-and-bookkeeping pattern. This is the **second consecutive cycle**
in which a "silent regression" was discovered when the on-disk
`smoke_latest.json` no longer matched the cached numbers from the
supposed last-keep result, after `git reset --hard` wiped uncommitted
load-bearing state.

### The pattern (5 steps)

1. **Experiment branch accumulates dirty working-tree state** that is
   load-bearing for the cycle eval (e.g., cycle-005 H2's dirty
   `models/fno_coregionalization/model.py` had the constructor signature
   `__init__(... modes_h, modes_w, grid, ...)` matched by
   `smoke_eval.py`'s anisotropic call site at line 265).
2. The dirty state is **never committed**. The cycle's banked composite
   (cycle-005 H2: **0.029357**) depends on it. `smoke_latest.json`
   reflects the banked number on disk.
3. A later cycle's Builder issues `git reset --hard` (cycle-006 H1
   Builder redirect #1, recovering from scope contamination per
   [[patterns]] §"Builder clean-isolation requires pre-clean working
   tree") — **wiping the uncommitted dirty file**.
4. The **cache layer hides the loss**: `cycle_eval` re-resolves cached
   results by `__code_hash__` of each `models/<family>/` directory.
   After the reset, the family's code-hash changes (e.g.,
   `9528aeef4a5a` → `4235deb6c27c`); the previously banked cache entry
   simply **does not key-match** the new hash. The cell becomes a
   cache MISS that crashes at construction with a `TypeError`, and
   the cycle eval **silently re-computes the composite without that
   family** — surfacing only the surviving cells.
5. The disk metric (`smoke_latest.json`) and the supposed "last-keep
   result" **diverge**. The divergence is only surfaced when the next
   cycle's R0 evaluator runs end-to-end and reports the actual
   reproducible number (cycle-007 R0: **0.039578**, vs the on-disk
   aspirational 0.029357 — **+34.8% discrepancy**).

### Cycle-006 → cycle-007 evidence trail

- **Cycle-005 H2 (2026-06-02):** banked composite 0.029357 with cached
  cells `fno_coregionalization` hash `9528aeef4a5a` (heat 0.01551) and
  `9be21a0f9ce9` (poisson 0.75015). Dirty `model.py` never committed.
- **Cycle-006 H1 Builder redirect #1 (2026-06-02):** `git reset --hard
  experiment/7-fno_coreg_lf_hf_transfer`. Recovered from scope
  contamination on `models/fno_coreg_residual/*`; **incidentally
  wiped** the dirty `fno_coregionalization/model.py`.
- **Cycle-006 R4 eval (2026-06-02):** `fno_coregionalization` crashes;
  composite computed without it = 0.04196 (aggregate).
- **Cycle-007 R0 eval (2026-06-02):** honest baseline **0.039578**
  with code-hash `4235deb6c27c` for `fno_coregionalization` —
  no cache entry exists at that hash; both
  `fno_coregionalization × {ifc_heat, ifc_poisson}` cells are
  cache MISSes that crash with `TypeError:
  FNOCoregionalization.__init__() got an unexpected keyword argument
  'modes_h'`.
- **Cycle-007 R1 Failure Analyst (2026-06-02):** diagnoses the
  divergence: cache files for `9528aeef4a5a` and `9be21a0f9ce9` are
  **still on disk** but no longer key-resolve against current
  `models/fno_coregionalization/` source.

### Why the cache layer masks the loss

`cycle_eval` cache key = `<family>__<dataset>__<code_hash>`. The
**code_hash is content-addressed against the committed `models/<family>/`
directory** (not against a `git rev-parse HEAD` or working-tree hash).
So:

- If a family's source code changes (file edit, hard reset, branch
  swap), its `code_hash` changes, and **all old cache entries become
  orphans** — still on disk, never queried.
- A crashing cell does not invalidate the cycle's composite — the
  composite is computed as `geomean(min-over-families-per-dataset)`
  with crashed cells skipped. **A formerly-winning cell silently
  drops out of the leaderboard with no error in the composite path.**

### Why this is second-consecutive

| Cycle | Trigger                                | Symptom                              |
|---    |---                                     |---                                   |
| 006   | Builder redirect `git reset --hard` wipes dirty `fno_coregionalization/model.py` | R4 composite drops 0.029357 → 0.04196 (aggregate). Framed as H1 regression initially; cache-hash forensics in R0 diagnostic show H1 contributed only Heat −13%, Poisson +3.6%. The composite drop is mostly from `fno_coregionalization` going dark. |
| 007   | New cycle eval on the same `experiment/7` committed tree at `be36cba` | R0 honest baseline **0.039578**; aspirational 0.029357 not reproducible. Cache cells for old hashes still on disk but orphaned. |

**Both cycles' real failure root is the same upstream root** — dirty
working-tree state that was load-bearing for a banked composite was
never committed and got wiped on a later `git reset`. The cache layer
turned a silent **structural** loss into a delayed **numerical**
loss that surfaces one cycle later.

### Implications and mitigations

1. **A cycle eval that bumps the project-best should additionally
   verify reproducibility from a clean working tree at the commit
   hash.** A delta between `git status`-clean re-eval and the cached
   `smoke_latest.json` is a silent-regression signal.
2. **The `cycle_eval` cache should refuse to bank composite numbers
   when the working tree is dirty** (or incorporate a tree-cleanliness
   tag into the cache key). Banked numbers that depend on uncommitted
   state are not durable across `git reset`s — they are **a debt that
   surfaces when the next Builder cleans up**.
3. **A crashed cell that was previously the dataset winner should
   raise a hard alarm** in the composite path, not silently fall out
   of the leaderboard. Composite recomputation should `assert` that
   every dataset's previous winner is still runnable (or surface an
   explicit `winner_lost_runnability_for: <dataset>` field in
   `summary.json`).
4. **The cycle-006 "Builder clean-isolation" pattern is the upstream
   root cause**; this pattern is the **downstream consequence at the
   cache-layer + composite-bookkeeping boundary**. Fixing either alone
   is insufficient — both must be addressed to prevent recurrence.

### When this pattern is most likely

- A `git reset --hard` is issued by a Builder mid-cycle (typically to
  recover from scope contamination).
- The reset target is an experiment branch that carries committed
  Builder edits AND uncommitted working-tree dirt from a prior cycle.
- The dirty files include constructor signatures, data adapters, or
  any code that the smoke harness's call site depends on.
- The cache for the affected family was populated against a code-hash
  that included the dirty state — so post-reset, the cache and code
  no longer match.

### Connection to other patterns

- **Upstream root cause:** [[patterns]] §"Builder clean-isolation
  requires pre-clean working tree (`git add <named-file>` is
  insufficient if file is already dirty)".
- **Related cache-layer pattern (different shape):** [[patterns]]
  §"Cycle-eval cache resolution depends on content-addressed
  code-hash" (existing entry on cache semantics, if present;
  otherwise this is a sibling pattern).
- **Bookkeeping subsystem fragility (general):** [[patterns]]
  §"Factory precheck `score_direction` is polarity-buggy on
  lower-is-better metrics" (separate cross-cycle precheck failure
  pattern, also 7-for-7 across project history).

**Source**: [[failure-analysis-cycle-007]] (R1, 2026-06-02),
[[cycle-006-exp-8]], [[cycle-006-summary]], [[factory_mffp-007]]
(cycle-005 H2 banked composite that became unreproducible),
[[ceo-verdict-evaluator-r0]] (cycle-007), [[ceo-verdict-failure_analyst]]
(cycle-007).

---

## Fresh-train variance can swamp claimed invariance — code-path equivalence ≠ numerical equivalence when fresh trains are involved

Discovered in **factory_mffp cycle 007 H2** (2026-06-02, GENUINE
REVERT verdict — composite regressed +12.36%). This pattern is a
cross-cutting strategist failure mode that voids the "invariant by
construction" reasoning when the supposedly-invariant cell is a
fresh train (cache miss).

### Pattern statement

A "no-op" code change that touches loss-aggregation logic, training-loop
wiring, optimizer construction, or any line that the cache-key function
hashes is **NEVER truly invariant** when fresh trains are involved on
the supposedly-invariant cell. The cache hash flip forces a retrain;
the new training trajectory may land at a different optimum than the
prior fresh trains. **Source-level code-path equivalence does NOT bind
on the numerical output once a fresh train is involved.**

### Evidence — cycle-007 H2

Strategist R2 claim (literal):

> **"Heat path is invariant by construction."** Defaults `(1.0, 1.0)`;
> gate is `"poisson" in dataset_name.lower()`. The Heat code path will
> execute the *same* `p["hf_loss_weight"]` and `p["lf_loss_weights"]`
> as the baseline.

R4 reality on `fno_coreg_residual / ifc_heat`:

| Cycle | Cache hash       | Heat nRMSE | Source                              |
|---    |---               |---:        |---                                  |
| 005   | (prior)          | 0.03519    | cycle-005 R0 baseline               |
| 006H1 | (prior)          | 0.03059    | cycle-006 H1 fresh train            |
| 007R0 | `1d967ad6e54c`   | 0.02628    | cycle-007 R0 (Strategist anchor)    |
| 007H2 | `528438a274db`   | **0.03487**| **cycle-007 H2 fresh train (this run)** |

- Claimed invariance band: 5%.
- Observed run-to-run variance band: 34% (0.02628 → 0.03519).
- Falsification ratio: 6.5× the claimed band.
- The H2 Heat result is **within the empirical variance envelope** but
  *not* within the claimed invariance band. The Strategist's invariance
  claim was anchored on a single low value (0.02628) without measuring
  the empirical variance.

### Mechanism

Two non-exclusive contributing mechanisms:

**A. Unconditional downstream write side effect.**
The new code path unconditionally writes `p["hf_loss_weight"]` and
`p["lf_loss_weights"]` after the dispatch returns — even when the
dispatch dict `_DATASET_RECIPES.get(name, {})` is empty for Heat.
If the prior code:
- Did not write `p["hf_loss_weight"]` / `p["lf_loss_weights"]` at that
  position, OR
- Wrote them with a different default value, OR
- Wrote `lf_loss_weights` as a different tensor shape (e.g., scalar vs
  `tuple([lf_w] * max(n_levels - 1, 0))`),

then the runtime wiring CHANGED for Heat even though the dispatch dict
was empty. The Strategist's "invariance" reasoning evaluated the
dispatch dict only, not the unconditional downstream writes.

**B. Fresh-train trajectory variance.**
The cache key is content-addressed on `__code_hash__` of the file. A
new line — anywhere — flips the hash and invalidates the cache. Forced
retrain takes a new RNG trajectory through a high-dimensional loss
landscape that is NOT contractive to a single fixed point at the smoke
budget. Different fresh trains land at different optima. The
inter-train variance band must be measured empirically, not assumed.

### Strategist rule (proposed for cycle-008+)

Before claiming "invariant by construction" on a cell that would be a
fresh train (cache miss expected), require **either** of:

1. **Kill-switch on the supposedly-invariant cell** with a band ≥ 20%
   (or whatever the empirical variance is, anchored to ≥ 3 prior
   fresh-train values on that cell). Bands derived from source-level
   reasoning alone are forbidden.
2. **Explicit byte-identical cache-key proof**: demonstrate that the
   `__code_hash__` is preserved across the change (e.g., the new code
   sits in a separate module not hashed by the cache, or behind a
   runtime feature flag whose default state is byte-identical to
   pre-change).

Otherwise the cell must be treated as a fresh-train target with full
risk-of-regression accounting — no invariance assertion permitted.

### CEO hard-gate (proposed for cycle-008+ R2 contract)

Add to the 10-check Strategist hard-gate suite:

> **Hard-gate #11:** For every cell the Strategist claims is
> "invariant" (no kill-switch), require evidence that either
> (a) the cache hash is preserved (proof byte-identical input to
> cache-key function), or (b) the empirical variance band on the
> cell is ≤ the claimed invariance band, measured from ≥ 3 prior
> fresh trains. Reject the strategy if neither is satisfied.

### When this pattern is most likely

- A "purely additive" source change that nonetheless modifies the
  bytes of a file that the cache hashes — appending a helper function,
  adding a module-scope dict, inserting a guarded write.
- A Strategist claim of construction-invariance that reasons over the
  *intended semantics* (dispatch dict values, gate predicates) rather
  than over the *runtime bytes* (downstream unconditional writes,
  tensor shape side effects).
- A cell whose prior fresh-train values span > 10% range, where the
  Strategist anchored on the single lowest value.

### Connection to other patterns

- **Closely related** to [[patterns]] §"Silent regression masked by
  the cache layer" — both patterns turn on cache-hash semantics. The
  silent-regression pattern is about cache MISS-then-orphan after a
  reset; this pattern is about cache MISS-then-fresh-train-divergence
  after an additive source change.
- **Composes with** [[patterns]] §"Cross-architecture recipe
  portability is NOT guaranteed" — the cycle-007 H2 Poisson side
  *did* improve (recipe partially portable, +9.55% short of cycle-005
  target), but the Heat side regressed (invariance-by-construction
  failed). Both patterns must be applied together when porting recipes
  across architectures AND across PDE-class boundaries.
- **Distinct from** [[patterns]] §"Factory precheck `score_direction`
  is polarity-buggy" — this pattern is at the *experiment-hypothesis*
  layer (Strategist claim falsified by real numerical evidence); the
  polarity bug is at the *bookkeeping* layer (precheck infra misreads
  real numerical evidence). H2 is the rare experiment where the
  precheck-streak's `revert_bookkeeping_keep_intent` does NOT apply
  because the composite truly regressed.

### Cycle-007 H2 instance details

- Hypothesis: H2 per-dataset MFRNP recipe dispatch on
  `models/fno_coreg_residual/smoke_eval.py` (+29/-0 LOC, additive).
- Strategist invariance claim: "Heat path invariant by construction"
  (defaults 1.0/1.0; gate excludes 'heat').
- R4 result: Heat 0.02628 → 0.03487 (+32.70%); composite 0.039578 →
  0.044470 (+12.36%, GENUINE REVERT — 2nd genuine revert in project
  history after cycle-003 H1).
- Heat leaderboard flipped: `fno_coreg_residual` → `mf_fno_transfer_bar`
  @ 0.03317.
- Branch `experiment/10-fno_coreg_residual-dataset-recipes @ 87f65b1`
  preserved for reference only; cycle-008 entry baseline UNCHANGED at
  cycle-007 H1's `experiment/9 @ 1249f2d` @ 0.030408.

**Source**: [[cycle-007-exp-10]] (full lifecycle), [[cycle-007-exp-10-build]]
(R3 build), [[evaluator-latest]] (R4 result),
[[ceo-verdict-strategist]] (R2 invariance claim).

## MFRNP-style per-fidelity loss reweighting is DO-NOT-RETRY in factory_mffp (3-for-3 REVERTs across three lever variants)

Consolidating cross-cycle pattern surfaced in **factory_mffp cycle 008
baseline Failure Analyst** (2026-06-02, PROCEED). Three independent
hypotheses on the **same underlying lever** — MFRNP HF=2.0/LF=0.25
per-fidelity loss reweighting — have all REVERTed, exhausting the three
natural variants of the lever:

| Cycle / H  | Variant of the MFRNP-recipe lever                                  | Pre→Post                              | Outcome                                              |
|---         |---                                                                 |---                                    |---                                                   |
| **c003 H1**| Cross-architecture transplant `fno_mf_stack` → `fno_coreg_residual` (uniform application both PDEs) | poisson 0.07416 → 0.27287 (+268%)     | REVERT — recipe is backbone-coupled, NOT PDE-class-bound |
| **c006 H1**| Cross-architecture transplant `fno_coreg_residual` → `fno_mf_stack` (reverse direction)            | composite ≈ flat; primary Poisson bet regressed | REVERT — confirms backbone-coupling in the other direction |
| **c007 H2**| Per-dataset dispatch WITHIN `fno_coreg_residual` (heat keeps current, poisson reverts to MFRNP)    | heat 0.02628 → 0.03487 (+32.7%); composite +12.36% | REVERT — heat invariance falsified at 6.5× the noise band |

**Three variants tested, three REVERTs.** The full lever space is now
covered: cross-architecture forward, cross-architecture reverse, and
within-family per-dataset dispatch. No remaining variant of the same
underlying lever is unexplored.

### Joint mechanism (refined by 3 observations)

MFRNP HF=2.0/LF=0.25 reweighting is **BOTH backbone-coupled AND
dataset-entangled within the same family**:

- **Backbone-coupling** (c003 + c006): the receiving backbone's gradient
  pathway either already absorbs the LF/HF gradient asymmetry the recipe
  manually imposes (over-correction → regression) or lacks the structural
  hook the recipe was tuned for (under-correction → regression). Both
  directions of cross-architecture transfer failed.
- **Dataset-entanglement within family** (c007 H2): even when the recipe
  is gated to a single PDE within the same family, the cache hash flip on
  the gate-bearing source change forces a fresh train; the new
  trajectory lands at a different optimum than prior runs, exceeding the
  source-equivalence-based invariance band. "Heat invariant by construction"
  is a code-path claim, NOT a numerical-trajectory claim.

These two failure modes **compose**: any new MFRNP-style intervention
crosses BOTH boundaries (architecture AND dataset) and inherits BOTH
risks, with no in-family invariance proof available.

### DO-NOT-RETRY rule (cycle-008+)

Any new hypothesis adding MFRNP-style per-fidelity loss reweighting
(cross-family OR per-dataset-within-family) is **DO-NOT-RETRY by
default**. Override requires BOTH of:

1. **Kill-switch on every supposedly-invariant cell** with a band ≥
   empirical variance measured from ≥3 prior fresh-train values on that
   cell. Source-level reasoning ("gate excludes 'heat'", "defaults are
   1.0/1.0") is NOT a substitute for the kill-switch.
2. **Best-of-N (N≥2) seed control with the heat seed frozen** across
   treatment and control. This is the only known mitigation for the
   fresh-train variance + invariance-by-construction failure mode
   surfaced by c007 H2.

Without BOTH, the prior of REVERT is 3-for-3 = 100%; Strategist
hard-gate should reject the hypothesis at R2.

### Connections to other patterns

- **Subsumes** §"Cross-architecture recipe portability is NOT guaranteed
  even when receiving architecture shares structural family" (the
  c003+c006 evidence) by adding the third observation (c007 H2 within-
  family dispatch). The earlier pattern remains correct as a
  cross-architecture statement; this consolidated pattern is the
  stronger statement that includes the within-family case.
- **Composes with** §"Fresh-train variance can swamp claimed invariance"
  — the c007 H2 failure mode is the within-family special case of that
  pattern; this pattern names the *lever* (MFRNP reweighting), the
  fresh-train-variance pattern names the *mechanism*.
- **Distinct from** §"Multi-fidelity transfer-learning recipes are
  PDE-class-coupled across datasets within the same architecture" — the
  PDE-class-coupling pattern is about *transfer-schedule* recipes (the
  c005 H2 LF→HF schedule that broke fno_coregionalization Poisson); this
  pattern is about *loss-weighting* recipes.

### Cycle-008 status (what is now available WITHOUT touching MFRNP)

The c008 baseline Failure Analyst surfaced three NEW transfer-learning
ideas that are NOT MFRNP-recipe interventions and are therefore not
gated by this rule:

- **(a) Re-bind c007 H2 LF→HF two-stage *transfer schedule*** to the
  repaired `fno_coregionalization` constructor (committed code never
  evaluated — H1 reverted to one-stage when fixing the constructor).
- **(b) NEW family `models/fno_coreg_conditioned/`** — m-conditioned
  single HF FNO (architecture-level, not loss-recipe).
- **(c) Curriculum LF→stack→HF-head** on `fno_coreg_residual` — staged
  training composition (multi-stage *training schedule*, not loss
  weights).

The remaining unexplored degrees of freedom for the project are
**architecture** (new family) and **training-schedule** (transfer
curriculum), NOT loss-weighting.

**Source:** [[failure-analysis-cycle-008]] §"Cross-architecture
portability lesson" + §"Five Required Callouts" #4 (CEO PROCEED
2026-06-02); [[failure-analysis-cycle-007]] (cycle-007 H2 instance);
[[failure-analysis-cycle-003]] (c003 H1 instance); [[cycle-006-summary]]
(c006 H1 instance).

## FiLM-via-LayerNorm is the canonical 2024-2025 conditioning channel in PDE neural operators; the IFC outer-product basis `B(m)·h(x)` is a 2022-era design

**Discovered in factory_mffp cycle-008 web round (2026-06-02).**

The current `fno_coregionalization` family uses the IFC outer-product
decomposition `f(x, m) = sum_k B_k(m) · h_k(x)` (Li 2022) with
`B(m) = MLP([m, m²])` — a **2022-era design** for parameter-conditioning of
a neural operator. Three independent 2024-2025 PDE-operator papers now
canonicalise **FiLM-via-LayerNorm** as the leaner alternative:

1. **`herde2024poseidon`** (NeurIPS 2024) — Poseidon / scOT foundation model
   for PDEs uses **time-conditioned LayerNorm** (FiLM-style) across 15
   downstream tasks. Foundation-model-scale validation.
2. **`beggs2025pdecond`** (arXiv:2509.09599, Sep 2025) — explicit precedent:
   "affine parameters in LayerNorm replaced with a learned function of the
   conditioning information; decouples scale and shift from conditioning to
   enable leaner pretraining and better fine-tune transfer." Direct
   architectural blueprint.
3. **`rahman2024codano`** (NeurIPS 2024) — CoDA-NO codomain-attention
   variant of the same conditioning thesis; >36% few-shot transfer
   improvement.

The contemporary 2024-2025 composition is:

```
f(x, m) = FNO(x; γ(m), β(m))      where γ, β : MLP([m, m²])
LayerNorm(z) → γ(m) * LayerNorm(z) + β(m)    (FiLM affines inside spectral blocks)
```

**Lessons for this project:**

- The IFC outer-product `B(m)·h(x)` (Li 2022) and FiLM-via-LayerNorm
  (2024-2025) are **two different ways to inject the m signal** — FiLM
  modulates *all* hidden channels of the FNO trunk; the outer product
  pools the trunk into K basis components first.
- For the cycle-008 `FAMILY_PDE_SPECIALIZATION_ASYMMETRY` failure mode
  (`fno_coregionalization` wins Heat at 0.01551 but loses Poisson at
  0.7501), the diagnostic call is that the K=10 outer product is
  **expressivity-bounded on non-monotone fidelity correlation** (Poisson)
  while FiLM-via-LayerNorm modulating the full hidden width is
  unconstrained by K and may capture both monotone-Heat AND
  non-monotone-Poisson m-correlations.
- `cao2025mflno` proposes an *orthogonal* fix: split the residual into
  a linear LF→HF map + nonlinear corrector — a third design point
  alongside outer-product and FiLM-via-LayerNorm.
- `pan2022hyperfno` (NeurIPS ML4PS 2022) is the *heavier-weight*
  precursor: full-weight hypernetwork generation. The 2024-2025
  literature converged on FiLM-via-LayerNorm because it is sufficient
  AND cheap.

**How to detect**: a family with a hardcoded K-dim outer-product basis
on the m signal is a 2022-era design; check whether the LayerNorm/GroupNorm
affines can be replaced with `γ(m), β(m)` MLPs for a leaner architecture
that scales to multiple PDE classes.

**Architectural rule (proposed for cycle-008+):** new families targeting
parameter-conditioned PDE operators should default to FiLM-via-LayerNorm
unless evidence specifically motivates the heavier hypernet or outer-product
designs.

**Cycle-008 instance**: B1 (`fno_coreg_conditioned`, NEW family) is the
project's first in-tree FiLM-via-LayerNorm experiment.

**Source:** [[research-cycle-008]], [[beggs2025pdecond]],
[[herde2024poseidon]], [[rahman2024codano]], [[cao2025mflno]],
[[pan2022hyperfno]], [[li2022ifc]], [[failure-analysis-cycle-008]].

## Paper-config wire-up on a freshly-repaired constructor is the highest-EV next move after a constructor-fix cycle

Discovered in **factory_mffp cycle 008 H1** — capacity-axis bump on
`fno_coregionalization` SMOKE_DEFAULTS (`hidden_channels 32→128, K 10→20,
n_blocks 4→6, modes_cap 12→16` + new `b_hidden=128` wired through), single
+10/-4 LOC diff on top of the cycle-007 H1 anisotropic-modes constructor
repair, drove composite_nRMSE 0.030408 → 0.027729 (−8.81%) and `ifc_heat`
0.01551 → 0.012898 (−16.84%), closing 89.93% of the bar gap from one cycle.
The cycle-008 failure_analyst predicted `CAPACITY_PARETO` on `fno_coregionalization
× ifc_heat` as the dominant lever (12.6× composite log-weight) — H1 hit it
nearly verbatim against the projection.

**Mechanism**: when an earlier cycle repairs a constructor signature (the
*structural enabler*), the constructor is by construction at its
under-capacity default. The IFC paper / `full_config.json` already records
the intended capacity (the *science lever*). Wiring those values into
SMOKE_DEFAULTS in the very next cycle is:

1. **Cheap** — single-file +10/-4 LOC, no `model.py` edits.
2. **Predictable** — `full_config.json` is published; the magnitudes
   (hidden 128, K 20, n_blocks 6) are the paper's own ablation
   sweet-spot, not a research bet.
3. **Anti-pattern-clean** — does not require MFRNP loss-recipe, does
   not require per-dataset dispatch, does not bundle, does not edit
   fixed surfaces; the surface guard and leakage scan both clear on
   numerical-knob bumps.
4. **Two-cycle decomposition** — the structural enabler (constructor
   fix) and the science lever (capacity values) get measured
   independently against the same baseline. If the bump REVERTs, the
   constructor fix is still banked; if it KEEPs, both effects are
   attributable.

**Lesson for the factory**: after any cycle that closes with `verdict ∈
{revert_bookkeeping_keep_intent, keep}` on a constructor-repair / signature-fix
hypothesis where the repaired constructor accepts paper kwargs that the
SMOKE_DEFAULTS do not currently exercise, the immediate-next cycle's H1
should be the paper-config wire-up. Do NOT bundle with a recipe-axis or
architecture-axis edit on the same hypothesis — keep the axes separable so
the capacity-axis effect is measured cleanly.

**How to detect**: a cycle closes with the repaired constructor accepting
kwargs that `full_config.json` provides but `SMOKE_DEFAULTS` does not pass
through, AND the family's smoke result on the dominant-log-weight dataset
sits in the upper half of the leaderboard for that family. Both conditions
were true for cycle-007 H1 → cycle-008 H1.

**Boundary**: this is a one-shot lever per repaired constructor. After the
paper-config bump, the capacity axis is exhausted for that family (paper-config
IS the natural ceiling); the next gain must come from a different axis
(recipe, schedule, architecture, or a different family).

**Source**: [[cycle-008-exp-11]], [[cycle-008-exp-11-build]],
[[cycle-007-exp-9]], [[failure-analysis-cycle-008]],
[[cycle-008]] (strategy snapshot — H1 priority slot).



## Strategist language imprecision on modes-kwargs convention — Reviewer/Builder follow file precedent, not literal English

**First observed**: cycle-008 H2 (exp 12) Reviewer phase, 2026-06-02. [[cycle-008-exp-12-review]].

**Observation**: The cycle-008 H2 Strategist spec described the modes API as "positional `modes` arg accepts either an int (isotropic) or a `(modes_h, modes_w)` tuple (anisotropic)". The actual H1-established convention in-tree (set by cycle-007 H1's anisotropic-modes constructor repair) is **separate kwargs `modes_h: int = 12, modes_w: int = 12`** — NOT a polymorphic positional arg. Both the bar `mf_fno_transfer_bar/model.py:70` and the repaired `fno_coregionalization/model.py:89-90` use the separate-kwargs form.

**What happened**: the Builder (cycle-008 H2) correctly **mirrored the on-disk file precedent** rather than the Strategist's literal English description, producing `modes_h: int = 12, modes_w: int = 12` in `fno_coreg_conditioned/model.py:150-159`. The Reviewer ratified this independently (`reviewer-latest.md` 2026-06-02T18:29:13Z) and explicitly noted the Strategist's language was imprecise. No modes-tuple regression risk; implementation is correct.

**Mechanism**: when the Strategist describes a constructor convention from memory (rather than diff-reading the source file), small wording slips happen — "positional, int-or-tuple" is a plausible-sounding API but doesn't match the actual H1-established separate-kwargs precedent. Because the Builder + Reviewer both have direct file access and treat the on-disk precedent as canonical, the imprecision does not cause a defect — it surfaces as a documentation-quality note for the next cycle's strategy template.

**Lesson for the factory**:
1. When the Strategist documents an inherited convention (constructor signature, kwarg names, scheduler shape, etc.), **the on-disk file is the canonical source** — Strategist English is a pointer to the file, not the spec itself.
2. Builders and Reviewers should diff against the cited file lines (`fno_coregionalization/model.py:89-90`, `mf_fno_transfer_bar/model.py:70`) NOT the Strategist's English paraphrase.
3. For cycle-009+ strategy templates, when describing the modes API specifically, write:
   > "Constructor uses separate `modes_h: int`, `modes_w: int` kwargs — mirror `fno_coregionalization/model.py:89-90` and `mf_fno_transfer_bar/model.py:70`."
   NOT "positional `modes` accepts int or `(modes_h, modes_w)` tuple".
4. More generally: Strategist convention-descriptions should **cite the file:line precedent** alongside the English description, so any wording slip is immediately disambiguated against the canonical source.

**How to detect this pattern**: a Reviewer's code-review notes flag an "implementation mirrors X file" finding that **differs in shape** from the Strategist's English description, but matches the cited file. The Reviewer correctly favors the file precedent.

**Boundary**: this is a documentation-quality pattern, NOT a research-correctness pattern. The Builder + Reviewer pipeline self-corrected; no rework needed. Update strategy templates so future cycles do not require Reviewer-time reconciliation.

**Source**: [[cycle-008-exp-12-review]], [[cycle-008-exp-12-build]], [[cycle-007-exp-9-build]] (H1 set the separate-kwargs convention), [[anisotropic-spectral-modes-fno]] (cycle-007 R1.5 research finding).



## Bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT — the diagnostic is R5b, not precheck

**First observed**: cycle-008 H2 (exp 12) final eval, 2026-06-02. [[cycle-008-exp-12-final]]. Re-cuts the playbook the CEO has been operating under since the precheck-bookkeeping streak began.

**Observation**: The CEO has been seeing TWO superficially similar verdict shapes that require opposite interpretations:

1. **`revert_bookkeeping_keep_intent`** — precheck false-positive WHEN composite genuinely improves. Composite truly moves in the right direction (e.g., cycle-008 H1: 0.030408 → 0.027729, −8.81%), but the `score_direction` polarity bug, empty-detail `scope`/`fixed_surfaces` checks, or substring-collision `ground_truth_leakage` checks fire false positives. The factory CLI's `finalize` gate auto-overrides CEO `keep` → `verdict='revert'`. CEO override applies: intent = KEEP; result is banked; branch becomes the next cycle's entry baseline. **7 prior occurrences** in factory_mffp through end of cycle-008.

2. **Genuine architecture-falsified REVERT** — precheck false-positives may ALSO fire (or be silent, or flip in opposite polarity), but composite **truly regresses or fails to improve** vs the banked best. CEO override does NOT apply. The hypothesis is killed; the branch is preserved-but-not-merged for historical reference. **4 prior occurrences** in factory_mffp: cycle-003 H1 (composite +91.7%), cycle-006 H1 (cross-architecture recipe non-portability), cycle-007 H2 (heat invariance violated, composite +12.36%), cycle-008 H2 (architecture-falsified on Poisson, composite flat at entry baseline / +9.66% vs banked best).

**The diagnostic is NOT "did precheck fail?"** Precheck-bookkeeping failures occur on BOTH verdict classes — they are noise, not signal. **The diagnostic IS "does Evaluator R5b monotonic check pass against the banked best?"**:
- **R5b PASS** (composite improved or held at banked best) ⇒ if precheck failures are bookkeeping false-positives, this is `revert_bookkeeping_keep_intent`; CEO override applies; intent = KEEP.
- **R5b FAIL** (composite genuinely regressed or stayed flat at entry baseline below the banked best) ⇒ this is a genuine REVERT regardless of what precheck reports; CEO override does NOT apply; intent = REVERT.

**Mechanism**: R5b reads the actual composite_nRMSE numbers from `cycle_eval.sh` against the banked best. It is independent of precheck. Precheck (R5c) is a layer of bookkeeping/hygiene checks that — in factory_mffp's tree — has accumulated bugs that flip polarity, mis-report scope/fixed_surfaces, and false-positive on substring collisions with required schema fields. Since precheck failures occur on BOTH improvement and regression cases, conditioning the CEO decision on precheck is a coin flip; conditioning on R5b is deterministic.

**The cycle-008 H2 case is particularly clean evidence**: this is the first observation of the `score_direction` polarity bug firing in **OPPOSITE polarity** — silencing a genuine +0.0027 nRMSE regression as "Score OK" because the precheck treats higher-after-as-better but composite_nRMSE is lower-is-better. The bug is symmetric: it can mis-report improvements as regressions (9 prior usual-polarity occurrences) OR mis-report regressions as improvements (1 opposite-polarity occurrence on cycle-008 H2). Either way, **precheck is not a reliable signal for the keep-vs-revert decision** — R5b is.

**Lesson for the factory**:
1. The CEO's keep-vs-revert decision must be grounded in **Evaluator R5b** (independent monotonic check against banked best), NOT in precheck (R5c).
2. When precheck fires false-positives, classify by the R5b outcome:
   - R5b PASS + precheck failure ⇒ `revert_bookkeeping_keep_intent` (override; bank).
   - R5b FAIL + precheck failure ⇒ **genuine REVERT** (no override; preserve branch only).
3. The override-class label `revert_bookkeeping_keep_intent` should be reserved for the R5b-PASS case. Do not apply it on R5b-FAIL cases just because precheck happened to fire false-positives.
4. When writing the CEO verdict (`ceo:revert mode=...`), the `reason=` field is the load-bearing distinguisher: `architecture_falsified_on_<dataset>` (or similar substantive cause) vs. `bookkeeping_polarity_bug` (or similar). The downstream archivist / report generator can group by `reason=` to track the genuine-REVERT vs `revert_bookkeeping_keep_intent` counts separately.

**How to detect this pattern next time**: when finalizing a verdict, before reaching for the `revert_bookkeeping_keep_intent` label:
- Confirm Evaluator R5b explicitly reports PASS against banked best.
- Confirm the composite metric value is at-or-below banked best.
- If EITHER fails, the verdict is genuine REVERT, not `revert_bookkeeping_keep_intent`.

**Boundary**: this distinction only matters when CEO intent and formal verdict diverge. When CEO intent = REVERT outright (no override attempted), the label is just `revert` with appropriate `reason=`. When CEO intent = KEEP but formal verdict is forced to REVERT by the precheck-bookkeeping subsystem, the override-class label `revert_bookkeeping_keep_intent` is what allows the dashboard / report generator to separate the "real" project state (composite trajectory) from the "bookkeeping" project state (formal verdicts).

**Source**: [[cycle-008-exp-12-final]] (1st observation of opposite-polarity bug; clean separation of bookkeeping-override vs genuine REVERT), [[cycle-008-exp-11]] (R5b PASS → `revert_bookkeeping_keep_intent` applied), [[cycle-007-exp-9]] (same R5b-PASS pattern), [[cycle-007-exp-10]] (R5b FAIL → genuine REVERT, NOT in bookkeeping streak), [[cycle-006-exp-8]] (R5b FAIL → genuine REVERT). Related: [[score-direction-polarity-bug]].



## FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation — pure m-conditioning is insufficient for Poisson-class datasets

**First observed**: cycle-008 H2 (exp 12) eval, 2026-06-02. [[cycle-008-exp-12-final]].

**Observation**: An m-conditioned single full-resolution HF FNO with FiLM-via-LayerNorm (`GroupNorm(affine=False) + MLP([m, m²]) → γ, β` modulation inside each FNO block) was hypothesized to be a single-family Heat+Poisson candidate — collapsing `FAMILY_PDE_SPECIALIZATION_ASYMMETRY` into one architecture. The architecture landed:
- `ifc_heat` 0.017102 (2nd place, 10% behind `fno_coregionalization` 0.01551 — near-miss).
- `ifc_poisson` 0.749915 (5th place, 12.6× over `fno_mf_stack` winner 0.05961; 5-15× outside Builder's predicted 0.05-0.15 range — **catastrophic**).

The Poisson result is the falsification. Even though the FiLM mechanism is mathematically sound (canonical 2024-2025 PDE-conditioning pattern; cf. `beggs2025pdecond`, `herde2024poseidon`) and the implementation was correct (Reviewer PASS), the architecture **cannot fit Poisson** because it discards the LF input channel by design.

**Mechanism**: The `ifc_poisson` dataset has strong LF→HF correlation signal — `fno_mf_stack` (0.05961) and `fno_coreg_residual` (0.07419) both achieve their wins by consuming the LF input directly and producing the HF output as either a stack of per-fidelity FNO predictions (mf_stack) or as a residual on top of an LF prediction (coreg_residual). The LF samples carry significant **complementary information** that the HF training data alone does not contain.

`fno_coreg_conditioned`'s HF-only architecture has **no LF→HF residual pathway** — only m-conditioning via FiLM affines:
- FiLM γ/β can **re-scale** a learned representation per fidelity.
- FiLM γ/β cannot **CREATE** the LF→HF structure that the multi-fidelity families exploit.

The Heat near-miss (0.01710 vs 0.01551) is consistent: on `ifc_heat`, where LF signal is less dominant (the m-modulation is closer to a simple amplitude rescale of the HF prediction), FiLM-on-HF-only is **competitive** because HF training data alone is sufficient to learn the field structure. On Poisson, where LF samples carry independent complementary information, the same architecture **fails by 12.6×** because the missing LF pathway is load-bearing.

**Lesson for the factory** (cycle-009+ strategy templates and any future MF-FNO architecture proposals):

1. Any single-family Heat+Poisson candidate must either:
   - **(a)** re-introduce the LF→HF pathway (residual ladder, à la `fno_coreg_residual` / `fno_mf_stack`), OR
   - **(b)** condition on LF samples directly in the FiLM affines — e.g., `γ(m, LF_features)` instead of `γ(m, m²)`. The FiLM conditioner input should include encoded LF features, not just the scalar fidelity index.

2. **Pure m-conditioning is insufficient** for Poisson-class datasets (those where the LF→HF correlation signal is informative). The fidelity index `m` alone is not enough to recover the LF information that the HF target depends on.

3. The diagnostic for "is this PDE Poisson-class or Heat-class for the LF→HF criterion?" is: **does the LF-only baseline beat the HF-only baseline at the same parameter count?** If yes, the LF pathway is load-bearing and any architecture without it will under-fit. If no, the dataset is Heat-class and HF-only architectures are viable.

4. The 828 LOC of FiLM-via-LayerNorm scaffolding from cycle-008 H2 is **preserved on `experiment/12-fno_coreg_conditioned-film @ 540e684`** (NOT merged) — a future cycle-009+ hypothesis that adds LF features to the FiLM conditioner inputs (option b above) can re-use the scaffolding directly. The model.py FiLMNorm module is the natural mount point: extend the MLP input from `[m, m²]` to `[m, m², encode_LF(x_LF)]`.

**How to detect this pattern in advance**: when reviewing a proposed MF architecture, check whether the architecture consumes the LF input as a tensor channel (not just as a scalar via `m`). If only `m` is consumed, the architecture has the same failure mode as cycle-008 H2 — it can re-scale but cannot synthesize the LF→HF correlation.

**Boundary**: this lesson applies specifically to MF datasets where LF samples carry **complementary** information to the HF target (as in `ifc_poisson`). For MF datasets where LF samples are merely **noisy or low-resolution** versions of the HF target (without complementary structural information), an m-conditioned HF-only architecture may suffice. The `ifc_heat` near-miss (10% gap) is consistent with this — Heat appears to be closer to the noisy-LF case where the LF channel adds less.

**Source**: [[cycle-008-exp-12-final]] (1st observation, falsified hypothesis), [[cycle-008-exp-12-build]] (Builder's predicted Poisson range 0.05-0.15 and the underlying expected-delta reasoning that was wrong), [[cycle-008]] (cycle-008 R2 strategy snapshot — H2 hypothesis spec), [[cycle-006-exp-8]] (related: cross-architecture recipe non-portability — LF/HF asymmetry is absorbed differently by different architecture families).



## Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs — end-to-end joint training is the right recipe for `fno_coreg_residual` / `fno_coregionalization`

**First observed**: cycle-008 H3 (exp 13) eval, 2026-06-02. [[cycle-008-exp-13-final]].

**Observation**: A three-stage curriculum on `fno_coreg_residual` — (S1) LF-only pretrain of per-fidelity FNOs, (S2) freeze LF stack and train HF residual, (S3) unfreeze and add the coregionalization-residual basis head — was hypothesized to exploit the `TRANSFER_SIGNAL_UNUSED` lever and recover the cycle-005 paper-recipe Poisson number (0.0556) while improving Heat (0.026 → 0.018-0.022). The result was a **catastrophic regression on both PDEs:**

- `fno_coreg_residual × ifc_heat`: **0.026277 → 0.509105 (+1837%, 19× worse, universal kill-switch tripped 26× over 0.0194 threshold)**.
- `fno_coreg_residual × ifc_poisson`: **0.074192 → 0.159364 (+115%, 2.15× worse, +165% out of Builder's predicted 0.05-0.06 range)**.
- val/test gap on Heat: **12× (val 0.043 → test 0.509)** — catastrophic overfitting OR final-state-checkpoint divergence.
- Composite_nRMSE: flat at baseline 0.030408 only because `fno_coreg_residual` regressed so badly it no longer wins either dataset cell on the leaderboard. **+9.66% above the cycle-008 H1 banked best 0.027729.**

The kill-switch design was insufficient: the H3-specific `Stage3/Stage2 Heat ratio > 1.25 → REVERT` did NOT trip (ratio = 1.00) because Stage 2 had already produced 0.509 on Heat — i.e. the curriculum collapsed BEFORE Stage 3 even ran. Only the universal `ifc_heat > 0.0194` caught it, and only post-hoc at finalize time.

**Mechanism**: `fno_coreg_residual` is a **residual ladder design** (`model.py:43-188`). The HF prediction = LF features → residual correction → BasisHead aggregation. The LF and HF networks are designed to **co-evolve** — the HF network learns a correction that depends on the CURRENT LF representation.

Stage 2 of H3 freezes the LF stack (`requires_grad=False`) to force the HF residual to correct against a fixed LF state. But the LF state from Stage 1 (LF-only pretrain, `m != hf_m` samples at `pretrain_lr=1e-3`) is **NOT the LF representation the HF residual was designed to correct** — it's an out-of-distribution frozen LF state from a pretraining regime the architecture wasn't built for.

Result: the HF residual learns garbage in Stage 2, with no information flowing back to the LF stack to fix the mismatch. Stage 3's unfreeze comes too late — the HF residual is already in a poor local minimum. Stage 3 DID improve Poisson 3.46× over the Stage-2 endpoint (0.551 → 0.159) but couldn't recover Heat, and Poisson's absolute level remains 2.15× the paper-recipe baseline.

In contrast, the **prior single-stage `fno_coreg_residual` recipe** (cycle-005 H2) and **cycle-008 H1's capacity bump on `fno_coregionalization`** (which is the same residual-ladder architecture pattern) both train ALL networks **co-evolved end-to-end**. The architecture's inductive bias is preserved.

**Lesson for the factory** (cycle-009+ strategy templates and any future MF curriculum proposals):

1. **Three-stage frozen-LF-HF-residual curricula MAY be appropriate for families where the LF and HF networks are INDEPENDENT BY DESIGN.** Candidate families:
   - **`mf_fno_transfer_bar`** — LF FNO outputs a feature map that's an INPUT (concatenated channel) to the HF FNO, not a co-trained residual; the HF FNO can correct against a frozen LF feature map without architectural mismatch.
   - **`fno_mf_stack`** — per-fidelity stacked predictions; no explicit residual; each fidelity's FNO operates independently and the HF prediction is a learned stack of them.

2. **Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs.** Do NOT propose for:
   - **`fno_coreg_residual`** — HF residual depends on co-trained LF representation (this experiment).
   - **`fno_coregionalization`** — same architectural family; basis head depends on co-trained per-fidelity FNO outputs.
   - **Any future family** where the HF prediction is a residual on top of an LF prediction that the HF network was trained to correct against END-TO-END.

3. **End-to-end joint training** (all parameters trainable, single optimizer, single LR schedule) remains the right recipe for co-evolved residual-ladder families. The cycle-005 H2 schedule (`pretrain_lr=1e-3, finetune_lr=3e-4, pretrain_frac=0.25` applied as a continuous LR schedule on a JOINTLY-TRAINED model, NOT as frozen-stage gating) is the correct interpretation of "LF→HF transfer" for these architectures.

4. **The 474 LOC of three-stage curriculum scaffolding** from cycle-008 H3 is preserved on `experiment/13-fno_coreg_residual-three-stage @ 420a51c` (NOT merged) — but should NOT be cherry-picked into other co-evolved residual-ladder families. It CAN be re-used as a starting point if cycle-009 chooses to test the same three-stage pattern on `mf_fno_transfer_bar` or `fno_mf_stack` (independent-LF-HF designs).

**How to detect this pattern in advance**: when reviewing a proposed multi-stage curriculum for an MF family, check the family's `model.py` for the dependency direction between LF and HF subnetworks:
- If the HF subnetwork takes the LF subnetwork's INTERNAL features as INPUT (residual or coregionalization aggregation), the LF and HF are **co-evolved** — frozen-LF curricula will fail.
- If the HF subnetwork takes the LF subnetwork's OUTPUT (predicted field tensor) as a separate input channel, the LF and HF are **independent** — frozen-LF curricula may work.

**Boundary**: this lesson applies specifically to multi-stage curricula that FREEZE an upstream subnetwork while training a downstream subnetwork. Continuous-LR-schedule "transfer" (high LR for the whole model early, low LR for the whole model later, no freezing) — which is what cycle-005 H2 actually implemented despite the name — does NOT have this failure mode. The distinction is **freeze-and-train** (broken for co-evolved designs) vs **schedule-and-train-jointly** (fine for co-evolved designs).

**Source**: [[cycle-008-exp-13-final]] (1st observation, falsified hypothesis), [[cycle-008-exp-13-build]] (Builder's three-stage implementation with `requires_grad=False` gating and predicted per-cell deltas), [[cycle-005-summary]] (the original "LF→HF schedule" — actually continuous-LR-joint-training — that this experiment misread as a frozen-stage curriculum), [[factory_mffp-2026-06-02]] (cycle-008 R2 strategy — H3 hypothesis spec). Related: [[patterns]] "FiLM-via-LayerNorm on HF-only FNO cannot synthesize LF→HF correlation" (cycle-008 H2 — co-occurring genuine architecture-falsified REVERT in the same cycle).



## Multi-stage curriculum kill-switches MUST include a Stage-2-vs-baseline absolute check, not only an inter-stage Stage3/Stage2 ratio check

**First observed**: cycle-008 H3 (exp 13) eval, 2026-06-02. [[cycle-008-exp-13-final]].

**Observation**: cycle-008 H3's three-stage curriculum was instrumented with two kill-switches:
- **Universal:** `ifc_heat > 0.0194 → REVERT`. TRIPPED at finalize time (post-hoc only) — 0.509 vs 0.0194 = 26× over threshold.
- **H3-specific (inter-stage ratio):** `Stage3/Stage2 Heat ratio > 1.25 → REVERT to Stage 2`. **DID NOT TRIP** (ratio = 1.00).

The inter-stage ratio kill-switch was designed assuming Stage 3's unfreeze would be the source of damage (BasisHead instability + LF unfreeze at `lr=9e-5`). **Reality:** damage occurred in **Stages 1/2**; Stage 2's HF residual training against a frozen out-of-distribution LF state already produced the 0.509 Heat regression. Stage 3 was a no-op on Heat (couldn't fix it) and actually IMPROVED Poisson 3.46× (0.551 → 0.159) — so the Stage3/Stage2 ratio was 1.00 on Heat and < 1 on Poisson.

The universal kill-switch caught it — but only post-hoc at finalize time, after the full smoke wall (50.7 s) had been spent. For longer-wall hypotheses (15-25 min smoke budgets), this would have been a much more expensive false-negative.

**Mechanism**: an inter-stage ratio kill-switch tests **relative regression between consecutive stages**. It assumes the prior stage produced a SANE baseline. If Stage 2 itself produces an INSANE baseline (catastrophic damage internal to Stage 2), the Stage3/Stage2 ratio can be 1.00 or even < 1 while the absolute level is 10-100× the project baseline.

**Lesson for the factory** (cycle-009+ kill-switch design for any multi-stage curriculum):

A multi-stage curriculum kill-switch suite MUST include **both** of the following:

1. **Absolute per-stage threshold vs prior single-stage baseline.** For each intermediate stage S_k (k < final), compute the test metric on the stage-end checkpoint and compare to the family's prior SINGLE-STAGE baseline:
   ```
   stage_k_final_hf_test_nrmse > 1.25 × prior_single_stage_test_nrmse → REVERT to baseline
   ```
   This catches Stage-internal damage **before** subsequent stages waste additional wall time.

2. **Inter-stage ratio thresholds between consecutive stages.** For each transition S_k → S_{k+1}, compute the ratio of stage-end test metrics:
   ```
   stage_{k+1}_final_hf_test_nrmse / stage_k_final_hf_test_nrmse > 1.25 → REVERT to S_k
   ```
   This catches transition-induced damage (e.g. unfreeze-induced divergence).

**Single inter-stage ratio kill-switches are fragile** — they assume damage occurs in the LATER stage, but real damage can occur in any stage. The cycle-008 H3 case is the clean evidence: damage in Stage 2, undetected by the Stage3/Stage2 ratio.

**Builder discipline for cycle-009+:** when proposing any N-stage curriculum (N ≥ 2), the kill-switch specification MUST include:
- An absolute test-metric checkpoint at the END of each non-final stage, compared to the family's prior single-stage baseline.
- An inter-stage ratio check at each transition.
- Both checkpoint metrics MUST be persisted in the result JSON for mechanical Evaluator comparison.

The cycle-008 H3 implementation DID instrument `stage2_final_hf_test_nrmse` in the checkpoint and result JSON (lines 269-287, 571-574, 498, 650 of `smoke_eval.py`) — the Builder followed the strategy spec correctly. The gap was in the strategy spec itself: it required only the Stage3/Stage2 RATIO check, not an ABSOLUTE Stage 2 vs baseline check. The cycle-009+ strategy templates must close this gap.

**How to detect this pattern in advance**: when reviewing a proposed multi-stage curriculum, check the kill-switch spec for the presence of BOTH (a) per-stage absolute thresholds vs the family's prior single-stage baseline AND (b) inter-stage ratio thresholds. If only (b) is present, the kill-switch is fragile — fail the strategy at R2 review and require (a) be added.

**Boundary**: this lesson applies to multi-stage curricula where intermediate stages freeze subsets of parameters or alter loss/data composition in ways that can cause stage-internal damage. It does NOT apply to single-stage training (no intermediate stages) or to continuous-LR-schedule "stages" that share parameters and optimizer state across stage transitions (where intermediate states are not distinct training regimes).

**Source**: [[cycle-008-exp-13-final]] (1st observation, kill-switch design flaw exposed by genuine REVERT), [[cycle-008-exp-13-build]] (Builder implemented strategy spec correctly; gap was in strategy spec), [[factory_mffp-2026-06-02]] (cycle-008 R2 strategy — H3 spec contained only the inter-stage ratio check). Related: [[patterns]] "Three-stage frozen-LF-HF-residual curricula are INCOMPATIBLE with co-evolved residual ladder designs" (same experiment — the architectural-incompatibility lesson and the kill-switch-design lesson are independent learnings from the same REVERT).

## Capacity-axis playbook transfers cross-family — paper-config SMOKE_DEFAULTS bump on the dominant-lever family closes the dominant gap

**Observation**: cycle-009 H1+H2 produced a record −20.08% composite improvement (0.027729 → 0.022161) on `experiment/14-fno_mf_stack-capacity-and-recipe-hash @ 0b6e6eb` by **re-applying the cycle-008 H1 playbook to a different family on a different dataset**. Cycle-008 H1 bumped `fno_coregionalization` SMOKE_DEFAULTS toward paper-config on the Heat side and closed 89.93% of the bar gap. Cycle-009 H1 bumped `fno_mf_stack` SMOKE_DEFAULTS (`hidden 32→64`, `agg_hidden 32→64`, `n_blocks 3→4`, `modes_per_level (4,8,12,12)→(4,8,16,20)`) toward paper-config on the Poisson side and not only closed the remaining +1.09% bar gap but overshot by 19.2% under the bar (gap closed 276.8%). **The parallel-bench bar was dethroned for the first time in 9 cycles**, and Poisson improved on `fno_mf_stack` from 0.05961 → 0.038120 (−36%) — well below the 0.0594 kill-switch with 36% headroom.

**Mechanism**: the paper-config capacity targets (per `models/<family>/full_config.json` mirrors of li2022ifc, lyu2023mffno, etc.) describe **the capacity at which the published baselines were trained**. In-tree SMOKE_DEFAULTS are conservatively under-sized for fast smoke harness wall (~30–90 s/cell) and therefore systematically leave headroom on the largest-error cells. When `failure-analysis-cycle-XXX` identifies a single dominant-lever (family, dataset) pair contributing > 50% of the remaining composite gap, mirroring the paper config on JUST that family's SMOKE_DEFAULTS — with all other recipe knobs (loss weights, lr, schedule) explicitly **UNCHANGED** — has a high prior of delivering a large composite reduction at low risk.

**Empirical support** (2-for-2 in project history):

| Cycle | Family | Dataset | Lever | Δ composite | Δ family×dataset | Risk class | Outcome |
|---|---|---|---|---|---|---|---|
| **cycle-008 H1** | `fno_coregionalization` | `ifc_heat` (Heat dominant) | `hidden 32→128`, `K 10→20`, `n_blocks 4→6`, `modes_cap 12→16`, `b_hidden=128` (NEW key) | **−8.81%** (0.030408 → 0.027729) | 0.01551 → 0.012898 (−16.84%) | LOW (paper-config wire-up, loss weights unchanged) | KEEP intent — closed 89.93% bar gap |
| **cycle-009 H1** | `fno_mf_stack` | `ifc_poisson` (Poisson dominant) | `hidden 32→64`, `agg_hidden 32→64`, `n_blocks 3→4`, `modes_per_level (4,8,12,12)→(4,8,16,20)` | **−20.08%** (0.027729 → 0.022161) | 0.05961 → 0.038120 (−36%); also 0.09995 → 0.038269 (−62%) family-internal Heat | LOW (paper-config-mirroring capacity bump, loss weights unchanged) | KEEP intent — dethroned bar by 19.2% |

**Lesson for the factory**: when a single dominant (family, dataset) pair contributes the majority of the remaining composite gap, **proposing a paper-config-mirroring SMOKE_DEFAULTS capacity bump on that family** has a high prior of working. **Carve-outs that MUST be respected:**

1. **Loss weights UNCHANGED.** Any MFRNP-style loss-weight tuning on coregionalization-family-adjacent recipes is a separate NK3 forbidden zone (3/3 REVERT history). The capacity-axis lever must operate **independently** of the loss-weight axis. Both cycle-008 H1 and cycle-009 H1 explicitly preserved their families' loss weights byte-for-byte.
2. **No `model.py` edits.** If `model.py` needs constructor work to accept the paper-config kwargs, that is a separate cycle (cycle-007 H1 anisotropic-modes constructor fix preceded cycle-008 H1's wire-up). The capacity-bump cycle MUST be wire-up-only on `smoke_eval.py SMOKE_DEFAULTS`.
3. **Single-family scope.** The lever targets ONE family on ITS dominant cell. Bundling capacity bumps across multiple families risks attribution loss — the project genuinely cannot tell which bump moved which cell, and any negative interaction is hard to isolate.
4. **Cache-safety semantic required.** When SMOKE_DEFAULTS change, the corresponding family's `recipe_hash` MUST change so stale cycle-N cache is invalidated (cycle-009 H2 made this automatic). Without cache-invalidation, the eval can silently reuse stale weights from a different recipe — a structural integrity failure separate from the capacity claim.

**Boundary**: this lever applies when:
- A failure analysis identifies one (family, dataset) cell as > 50% of the remaining composite gap.
- The target family has a `full_config.json` paper-config mirror in-tree with capacity larger than current SMOKE_DEFAULTS.
- The family's `model.py` already accepts the paper-config kwargs (no constructor work needed).
- The loss weights, lr schedule, and curriculum are not changed.

It does NOT apply when:
- The dominant gap is distributed across multiple cells with no single family dominating.
- The paper-config capacity equals or is below current SMOKE_DEFAULTS (capacity-axis exhausted; cycle-008 H1 reached this state on `fno_coregionalization` — cycle-009 H1 had to switch family).
- The cell's failure mode is recipe-coupled, not capacity-coupled (e.g. cycle-006 H1 PDE-class-coupled-recipe transfer, cycle-007 H2 per-dataset dispatch — both family-cell-coupled, both genuine REVERTs).

**How to detect in advance**: before proposing a cycle-XXX H1, check the failure-analysis dominant-lever table. If one (family, dataset) cell carries > 50% of the gap AND the family has a paper-config mirror larger than its SMOKE_DEFAULTS AND the family's `model.py` already accepts the paper-config kwargs, the capacity-axis lever is the highest-EV H1 candidate. Reject competing proposals that introduce loss-weight tuning, curriculum, or new architecture in favor of the capacity-axis baseline first.

**Source**: [[cycle-008-exp-11-build]] (1st observation, cycle-008 H1 paper-config wire-up on `fno_coregionalization` × Heat), [[factory_mffp-014-outcome]] (2nd observation, cycle-009 H1 paper-config-mirroring bump on `fno_mf_stack` × Poisson; first cross-family transfer of the lever in project history). Related: [[patterns]] "Paper-config wire-up on a freshly-repaired constructor is the highest-EV next move after a constructor-fix cycle" (specialization to constructor-fix follow-up cycles); [[patterns]] "MFRNP per-fidelity loss-weighting recipes are backbone-coupled across MF aggregation architectures" (NK3, explicit anti-pattern for the loss-axis variant of capacity-axis); [[patterns]] "`PDE_CLASS_ARCH_RECIPE_COUPLING` is the dominant in-tree failure mode at cycle 006" (boundary clarifier — capacity-axis works because it doesn't perturb the family's PDE-class-coupled recipe surface).

## `revert_bookkeeping_keep_intent` ratchets to 8-for-8 at record-improvement scale — precheck bookkeeping ungrasped after 9 cycles

**Observation**: cycle-009 H1+H2 triggered the **8th-consecutive `revert_bookkeeping_keep_intent` formal verdict** at a **record-shattering −20.08% composite improvement scale** (the largest single-cycle composite improvement in project history). All 4 documented precheck bookkeeping bugs fired despite the result being unambiguously the best in project history. CEO override → effectively KEEP; banked as cycle-010 entry baseline at composite 0.022161.

This consolidates the prior `revert_bookkeeping_keep_intent` pattern (cycle 005 H2 first observation) into a 9-cycle structural feature of the factory: **every CEO-keep intent eval in project history has been gated by the same set of bookkeeping bugs, none of which has been fixed.** The pattern is now:

- **Bookkeeping bugs are independent of result magnitude.** Cycle-005 H2 fired at −13% improvement; cycle-007 H1 at −23%; cycle-008 H1 at −8.8%; **cycle-009 H1+H2 at −20.08%** — the polarity bug (`score_direction` for lower-is-better metric) reported the −20.08% improvement as a +20.08% regression with no distinction.
- **Bookkeeping bugs are independent of the hypothesis-axis.** Capacity-axis (cycle-008 H1, cycle-009 H1), constructor-fix (cycle-007 H1), continuous-LR-schedule (cycle-005 H2) all fire identically.
- **Bookkeeping bugs are independent of leakage-scan polarity.** Cycle-008 H1 had a clean leakage scan; cycles 003 H1, 005, 007, 008, 009 all had leakage substring-collision FPs of varying tokens.
- **The number of bookkeeping bugs has ratcheted up over time:** cycle-005 H2 saw 4 bookkeeping subsystems fire; cycle-008 H2 added the OPPOSITE-polarity sub-class of `score_direction`; cycle-009 H1+H2 added the NEW `factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality FP (see separate pattern below). **5 distinct bookkeeping FP classes now active.**
- **R5b monotonic check is the load-bearing gate, not precheck.** The decision is always grounded in R5b composite improvement vs banked best — independent of precheck. CEO override is mechanical: when R5b PASS AND precheck-bookkeeping false-positive, formal verdict is `revert`, intent is KEEP, branch is preserved and banked.

**Mechanism**: each bookkeeping subsystem has a specific failure mode that has been stable across cycles:

1. **`score_direction` polarity** (11 firings, 9 cycles): precheck treats higher-after-as-better but `composite_nRMSE` is lower-is-better. Symmetric: usually flips improvements to "regressions" (10 firings); on cycle-008 H2 it silenced a real regression as "Score OK" (1 firing). Root cause: precheck does not honor `metric_lower_is_better: true` in `results/smoke_latest.json`.
2. **`scope` / `fixed_surfaces` empty-detail** (5 firings, 5 cycles): emits `passed: false` with `"detail": "Guard violations: "` (empty) even when `factory guard --check-scope` independently reports clean. Includes a short-SHA-vs-long-SHA sub-class introduced cycle-009 H1+H2.
3. **Leakage substring-collision** (7-consecutive builder phase): tokens from diff hunk headers or generic English collide with project-doc / fixed-surface content. Cycle-009 H1+H2's token `"17"` matched diff hunk header `@@ -176,9 +178,10 @@` against `factory.md`/`README.md` `"17"` occurrences in unrelated context.
4. **NEW cycle-009: `factory guard --baseline <short-SHA>` short-vs-long-SHA equality** (1 firing — see separate pattern below).

**Lesson for the factory**: until the precheck bookkeeping subsystems are overhauled, the formal verdict label `revert` is **strictly orthogonal to the CEO intent KEEP** for clean keep-intent evals. Future tooling (factory dashboards, ACE reflectors, performance reports) should consume `ceo_intent: keep` and the `revert_bookkeeping_keep_intent` verdict class — NOT the raw `verdict: revert` field — when computing project state. The mechanical CEO playbook is:

```
if R5b PASS AND (precheck has only documented bookkeeping FPs) → label = revert_bookkeeping_keep_intent, intent = keep
if R5b FAIL OR (precheck has substantive findings beyond documented bookkeeping FPs) → label = revert, intent = revert
```

Cycle-009 H1+H2 confirms this playbook holds at extreme improvement scales: the −20.08% magnitude was not enough to "wake up" the precheck subsystem, so future improvements of any size will continue to be gated identically.

**Boundary**: this pattern applies to the precheck bookkeeping subsystems documented above (`score_direction` polarity, `scope`/`fixed_surfaces` empty-detail, leakage substring-collision, guard short-vs-long-SHA equality). It does NOT apply to **genuine** precheck firings (e.g. a real surface-out-of-scope violation, a real ground-truth leakage from `data/` or `baselines/`, a real polarity-correct regression). The distinction is: documented bookkeeping FPs have specific known root causes that the operator backlog will fix; genuine findings have substantive evidence. Cycle-008 H2's `score_direction` polarity fired in OPPOSITE polarity (silencing a real regression) — this is the same bookkeeping subsystem misbehaving in a different polarity, NOT a new finding class.

**How to apply in cycle-010+**: spot-check at R5 whether precheck firings match documented bookkeeping FP signatures. If yes AND R5b PASS, override with `revert_bookkeeping_keep_intent`. If precheck fires a NEW class not on the documented list, treat as substantive and re-evaluate the architecture.

**Source**: [[patterns]] "`revert_bookkeeping_keep_intent` is the universal verdict — substring-collision precheck bug gates every eval (cycles 001–007)" (1st pattern observation), [[factory_mffp-014-outcome]] (8th-consecutive, record-improvement scale evidence), [[cycle-008-exp-12-final]] (OPPOSITE-polarity sub-class observation). Related: [[patterns]] "Bookkeeping-overridable REVERT vs genuine architecture-falsified REVERT — the diagnostic is R5b, not precheck" (cycle-008 H2 — boundary clarifier between bookkeeping-overridable and genuine-substantive REVERTs).

## `factory guard --baseline <short-SHA>` short-vs-long-SHA string-equality false positive — 2nd known guard FP class

**Observation**: cycle-009 H1+H2 surfaced a NEW guard false positive: `factory guard --baseline 18d83a6 --check-scope` reported the branch as NOT rooted at the baseline, but Reviewer manually verified `git merge-base HEAD 18d83a6` returns the full 40-char SHA `18d83a6190d342e0156a2c2547dcf2b2b998d782` which IS the cycle-008 H1 banked-best commit. The branch IS correctly rooted; the guard FP is a string-comparison artifact.

**Root cause**: `factory guard` performs string equality between the caller-supplied baseline argument (typically a 7-char short SHA like `18d83a6`) and the output of `git merge-base HEAD <ref>` (always a full 40-char SHA). Since `len("18d83a6") != len("18d83a6190d342e0156a2c2547dcf2b2b998d782")`, the string `==` check returns `False` even though the short SHA is a prefix of the full SHA referring to the same commit. The git porcelain command `git rev-parse <ref>` would normalize both to the full SHA for comparison; the guard does not perform this normalization.

**Distinction from prior guard FP class**: this is the **2nd known guard false-positive class**. The 1st is the **leakage substring-collision FP** (7-consecutive in cycle-009 H1+H2: token `"17"` matched diff hunk header against `factory.md`/`README.md` `"17"` occurrences in unrelated context). The two FP classes have different root causes and require different fixes:

| FP class | Root cause | Manifested where | Fix shape |
|---|---|---|---|
| Leakage substring-collision | `factory leakage-check` tokenizes diff at substring level; matches against fixed-surface content (project docs marked as fixed_surfaces). | PR diff / strategy file leakage scan | Tokenize at semantic-token level (e.g. python identifiers, not substring `"17"`); exclude diff hunk headers from scan corpus |
| Guard short-vs-long-SHA equality | `factory guard --baseline <ref>` does string `==` between caller arg and `git merge-base` output without `git rev-parse` normalization. | Build-phase Reviewer guard check | Pipe both through `git rev-parse <ref>` before string comparison |

**Mechanism**: when Reviewer runs `factory guard <path> --baseline 18d83a6 --check-scope`, the guard internally does something like:
```python
baseline_arg = "18d83a6"
merge_base = subprocess.check_output(["git", "merge-base", "HEAD", "18d83a6"]).strip()
# merge_base = "18d83a6190d342e0156a2c2547dcf2b2b998d782"
if baseline_arg != merge_base:
    raise GuardError("branch not rooted at baseline")
```
Both refer to the same commit; the prefix is unambiguous (`git rev-parse` would confirm). But string `==` returns `False`. **The correct fix is to `git rev-parse` the caller argument before comparison:**
```python
baseline_full = subprocess.check_output(["git", "rev-parse", "18d83a6"]).strip()
merge_base = subprocess.check_output(["git", "merge-base", "HEAD", baseline_full]).strip()
if baseline_full != merge_base:
    raise GuardError("branch not rooted at baseline")
```

**Lesson for the factory**: when Reviewer encounters `factory guard --baseline` rooting-check failure, **verify manually before treating as substantive**:
```
git merge-base HEAD <short-SHA>   # should return full SHA
git rev-parse <short-SHA>         # should return same full SHA
```
If both commands return the same full SHA AND that full SHA is the expected baseline commit, the guard report is the short-vs-long-SHA FP — override and flag for operator backlog.

**Standing operator override practice**: per cycle-009 H1+H2 Reviewer + CEO precedent, the override mechanic for this FP class is: cite the manual `git merge-base` verification in the CEO verdict, flag in the close-out doc, and proceed as if the guard had passed. Same mechanic as the leakage substring-collision FP.

**Boundary**: this pattern applies when (a) the guard reports a `--baseline` rooting-check failure, (b) the caller passed a short SHA (< 40 chars), and (c) `git merge-base HEAD <short-SHA>` returns a full SHA matching the expected baseline commit. It does NOT apply when the merge-base genuinely does NOT match the expected baseline (e.g. branch cut from the wrong parent) — that case is a substantive guard violation requiring branch re-cut.

**How to apply in cycle-010+**: whenever Reviewer invokes `factory guard --baseline <short-SHA>`, always run the manual `git merge-base HEAD <short-SHA>` check on guard failure. If full SHA matches expected baseline, treat as the documented FP class and override per cycle-009 precedent. If the operator fixes the guard (normalize via `git rev-parse` before string comparison), this pattern can be retired.

**Source**: [[factory_mffp-014-outcome]] (1st observation, cycle-009 H1+H2 Reviewer + CEO documented the FP class and manual override). Related: [[patterns]] "`revert_bookkeeping_keep_intent` is the universal verdict — substring-collision precheck bug gates every eval (cycles 001–007)" (precursor — 1st guard FP class, leakage substring-collision); [[patterns]] "`revert_bookkeeping_keep_intent` ratchets to 8-for-8 at record-improvement scale — precheck bookkeeping ungrasped after 9 cycles" (parent pattern enumerating all 4+1 bookkeeping FP classes).

## Cycle-003 backlog `recipe_hash` portability FULLY CLEARED — cache-safety semantic is now factory infrastructure for FNO family

**Observation**: the cycle-003 H1 stage-resume contamination failure mode — `33s-stale-resume-from-different-recipe-checkpoint` vs `549s-clean-rerun-under-current-recipe` returning different metrics — has been progressively closed across 3 cycles and is **now operationally retired for the entire FNO family**. The fix shape:

- **Cycle-008 H3 inline delivery** (1st observation, `fno_coreg_residual` only): live-verified `recipe_hash` checkpoint guard in `models/fno_coreg_residual/smoke_eval.py` (lines 113-123, 461-485, 495, 498, 505). Stale-rejection log line verified: `[resume] REJECTED stale checkpoint: recipe_hash '148a2641b07fe5da' != '0095c3ff614e17b8'`. The pattern was KEEP-worthy **in isolation** even though the H3 three-stage curriculum architecturally REVERTED.
- **Cycle-009 H2 portable utility promotion** (final delivery, 3 FNO families): the inline pattern was cherry-picked from `transolver_residual`'s canonical 12-LOC implementation (which `models/transolver_residual/smoke_eval.py` already had inline as canonical pattern) into a shared `models/_common/recipe_hash.py` utility and applied via canonical 4-patch-site refactor to `fno_mf_stack`, `fno_coreg_residual`, and `fno_coregionalization`. `transolver_attention_fusion` already had the canonical inline pattern.
- **Live verification at cycle-009 H1+H2 eval:** all 3 FNO families reported `cache_status=miss` and retrained from scratch under the new SMOKE_DEFAULTS hashes. `fno_mf_stack` new hash `acdb1c11caa7` correctly invalidated the cycle-008-era cache (the deliberate cache-safety semantic: H1 capacity bump MUST trigger fresh training, NOT warm-resume from stale weights trained under a different recipe). `fno_coreg_residual` (`1cc35377b46d`) and `fno_coregionalization` (`5011def485a6`) stable hashes confirm SMOKE_DEFAULTS unchanged → the refactor is correctness-preserving for unchanged-recipe families.

**Mechanism**: the helper is 12 lines including docstring:
```python
def recipe_hash(defaults: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(defaults), sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:12]
```
The canonical 4-patch-site refactor per family:
- **A — import**: `sys.path` shim + `from models._common.recipe_hash import recipe_hash`
- **B — compute**: `rh = recipe_hash(SMOKE_DEFAULTS)` at top of training entry
- **C — resume guard**: `ok_recipe` predicate chained with existing family-specific resume checks (`epochs_target`, `cond_dim`, plus family-specific preconditions e.g. `sd.get("grid") == list(grid)` on `fno_coregionalization`)
- **D — save dict**: `recipe_hash` key added to saved checkpoint dict

**Lesson for the factory**: cache-safety is now **factory infrastructure** for the FNO family. Cycle-010+ hypotheses that change SMOKE_DEFAULTS on any of the 5 covered families (3 FNO + 2 Transolver) get **automatic cache invalidation** — operators no longer need to manually delete stale checkpoint files when recipe knobs change. This closes the cycle-003 H1 silent-regression-via-cache failure mode at the infrastructure level rather than per-experiment.

**Boundary**: the helper covers SMOKE_DEFAULTS-recipe identity ONLY. It does NOT cover:
- **Architecture changes** (`model.py` edits): if `model.py` changes change the parameter-shape contract (e.g. add a new module, change layer counts in a way `state_dict.load` ignores), the recipe_hash will not detect the change. Operators must manually invalidate caches for `model.py`-affecting changes.
- **Data-layer changes** (`data.py` edits): if dataset preprocessing changes, training under stale weights from old preprocessing will silently degrade. Out of scope for the recipe_hash; requires a separate data-hash guard.
- **Multi-stage curriculum schedules** (e.g. cycle-008 H3 `stage_strides`): the original cycle-008 H3 inline pattern included `stage_strides` in the recipe_hash payload via `{**SMOKE_DEFAULTS, "stage_strides":[...]}`. The cycle-009 H2 portable utility only hashes `SMOKE_DEFAULTS` — multi-stage hypotheses that introduce stage-specific recipe knobs MUST pass them into the helper via an extended payload (the helper accepts `Mapping[str, Any]` for this reason).

**How to apply in cycle-010+**: hypotheses that change SMOKE_DEFAULTS on any FNO/Transolver family can rely on automatic cache invalidation — no manual cleanup needed. Hypotheses that change architecture (`model.py`), data layer (`data.py`), or introduce multi-stage curriculum-specific knobs MUST either (a) extend the recipe_hash payload to include the new knobs, OR (b) manually invalidate caches at experiment-start.

**Source**: [[cycle-008-exp-13-final]] (1st inline delivery on `fno_coreg_residual` only), [[cycle-009-exp-14-build]] (H2 portable utility build phase), [[factory_mffp-014-outcome]] (live verification, full clearance across 3 FNO families). Cycle-003 originating backlog item: [[cycle-003-summary]]. Related: [[patterns]] "Silent regression masked by the cache layer (cycle-006 → cycle-007, second consecutive instance)" (the failure mode that recipe_hash closes); [[patterns]] "Fresh-train variance can swamp claimed invariance — code-path equivalence ≠ numerical equivalence when fresh trains are involved" (orthogonal failure mode — recipe_hash forces fresh trains where appropriate but does not address fresh-train variance).
