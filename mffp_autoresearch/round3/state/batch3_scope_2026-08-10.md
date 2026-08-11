# Batch-3 scope — operator decision record (2026-08-10)

Operator (Eloise) directive: **"do stream rec"** — batch 3 follows each stream's own batch-2 recommendation.
Alongside it she adopted the G5 fit-set re-pricing ("adopt") and asked for a fuller explanation of the ifc affine-floor question before deciding it (that decision stays OPEN; nothing in batch 3 depends on it, but every ifc claim keeps the mandatory affine-floor disclosure as written in program.md §2 until she rules).

## Per-stream scope

- **r3s1_factorised — CONSOLIDATE, no batch-3 card.** Per its part-7 recommendation: no selection-side bet left; the residual cahn_hilliard map-quality bet is not granted a slot.
- **r3s2_field_reach — ONE card: the emulator-ceiling card** (its recommendation's preference order #1). Scope from the card: (a) real-LF oracle vs pseudo-LF ladder on all scored cells with a proper scored arm (S2 exists); (b) corrector regularisation selected on the EMULATOR's held-out output (fix the covariate shift at the selection input); (c) ridge=1e-9 carried as a footnote, not an idea. NOT another corrector-repair or route-contrast card. The panel-composition ADR (preference #2) is available to the operator separately and costs no slot.
- **r3s3_lf_value — ONE card: knee-predictability**, registered against the film-transfer baseline per the operator's round-orientation directive (ADR r3-0006 units).
- **r3s4_audit — CONSOLIDATE, no batch-3 card.** Contract package execution status:
  - (1) F1 ULP tolerances INSTALLED: `state/floor_tolerances.json` (D2 full-config, B=64, verbatim) + `state/floor_tolerances_install_note.json` (affine arm declared NOT YET ADJUDICABLE; per-arm affine bands pinned, all 10 verified against the card-quoted digits).
  - (2) G5 re-pricing ADOPTED (operator): record on r3s4-B2 card (`orchestrator_adjudication_g5_2026_08_10`); comparand addendum on r3s2-B1. Blanket rule: any claim priced against an `nn_condition` best floor carries the arm's fit-set noise band beside tau_rel.
  - (3) Binding-instrument promotion to the anchor-build gate: IN PROGRESS (see contract requirement below + orchestrator queue for the `verify-legs` hard gate and wall-clock-rule retirement).
  - (4) Two routed repairs (zero_work_resume_scan TypeError; UNDERIVABLE coverage gate): DISPATCHED per handoff §3a/§3b.

## Batch-3 clause rules (binding on brainstormers/builders)

1. **Register success clauses against the certified film-transfer baseline** (`state/anchors/film_denominator.json`), in film units. Copy-LF is not a target (operator directive 2026-08-10).
2. **Contract requirement (new, r3s4 package item 3a): every batch-3 family MUST adopt the `models_r3/_common/ckpt_binding.py` save hook** so `data_binding` is written into `last.pt` at every save. Binding coverage is a build-review checklist item.
3. Clause hygiene (from r3s2-B2 postmortem, stream-wide): no falsification leg whose threshold sits inside the fold-to-fold spread of its own statistic; any pre-registered repair grid must justify its FLOOR, not only its ceiling; no 0-epoch selector admitting candidates unscorable out-of-sample at that budget; enumerate the C(Ntr, n_fit) fold population instead of spending seeds on closed-form stages at n_fit ≤ 5.
4. Statistics registered on ENERGY-weighted or held-out-loss quantities, never an unweighted mode mean; calibrate every subset bar on the subset it is read against (`tools/transfer_gain_anatomy.py`, `tools/subset_geomean_unit_audit.py` are the pre-registration checks).
5. Claims priced against an `nn_condition` best floor carry that arm's fit-set noise band (G5 adoption) beside tau_rel; affine reproductions adjudicate against the pinned per-arm band, not the dataset-level table.

Expected close: ~Aug 12–13 (2-slot batch).
