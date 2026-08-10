# Iteration 1 — r3s1_factorised, batch 2

(Persisted verbatim by the orchestrator from the brainstormer's inline return, 2026-08-10; the harness blocked that subagent's report-file writes.)

## Design context considered

- `summary_so_far.md` §7 (unknowns 1–8) and the batch-2 prior-art verdict table (D1 split, D2 repeat-bet, D4/D5 preempted).
- The immutables block (§4.5 of the brainstormer contract) verbatim; round-3 `program.md` §5 + round-2 §5/§12.
- Stream anchor `state/anchors/r3s1_factorised.json` = 24.9573 [24.8726, 25.0662], per-cell 279.1165 / 374.8381 / 11.2577 / 8.2507 / 0.9964.
- Certified `state/anchors_repaired/noise_floor.json` (`_provisional: false`, certified 2026-08-08): `_panel_geomean.seed_mce` 0.5082844; `tau_rel` — ac 18.6198, fk 10.3128, ch 0.3612, ifc_poisson 0.6910, ifc_heat 0.1640.
- Floors `state/anchors_repaired/floors.json` and `state/anchors/launch_anchors.json:ifc_floors_repaired`.
- **Directive deviation, recorded**: the generic §4.2 table for `r3s1_factorised` lists "FiLM-conditioned FNO decoder, DeepONet-style branch–trunk, or spectral/implicit decoder". Those are round-2 §12.1's *design priors*, and the stream's shipped object is a closed-form factorised head (B1, reviewed and certified under exactly this tension). Batch 2 follows the stream's own recorded `next_direction` (part 7) and the orchestrator's course correction, and satisfies the hard parts of the directive: condition→HF only, stripped view, no LF at test, floor arms mandatory, built as a new family dir.

## Proposal reasoning (alternatives weighed and rejected)

**Rejected A — cahn_hilliard's hard 27 % (D3).** Card part 7: *"Do NOT spend a batch on cahn_hilliard's hard 27%: it is a condition-completeness limit, not an architecture limit."* The websearcher routes the open residue to `r3s3_lf_value`, which already holds the seed-invariant mask. Rejected on scope.

**Rejected B — a new decoder/architecture arm (FiLM-FNO, DeepONet, INR).** The mechanism stage says every remaining panel cell is limited at **stage 1**, not by representational capacity, and round-2 T2-F10 already showed a 15.85 M-parameter decoder's deficit is a coordinate problem. A new trained architecture would also break the `epochs: 0` property that makes a full 3-seed panel ~1 min/seed and would contest ground `r3s2_field_reach` owns. Rejected.

**Rejected C — bare `SELECT_MAX` sweep as the headline.** Verdict D1: *"Raising the numeric cap is a bug-fix, not the claim."* Shipping it alone makes the batch a hyperparameter sweep. Kept as an **arm and an instrument**, not as the claim.

**Rejected D — pre-registering `n_SET`/`E_rem`×reachability on the same 5 cells.** Verdict D2 prices this as a repeat bet fitted on its own evidence. Kept only in the form the websearcher licensed: pre-registered on **configurations the mechanism stage never saw**.

**Rejected E — replacing tau AND tau2 with the calibrated criterion in one arm.** Confounds stage 1 and stage 2. `tau2 = 0.1` is frozen across all arms so the only two knobs are the stage-1 rule and the stage-2 input.

**Selected.** A five-arm, single-knob-delta closed-form design on one new family:

| arm | stage-1 selection rule | stage-2 input | role |
|---|---|---|---|
| `A0_b1_replica` | tau 0.1, `SELECT_MAX` 32 | OOF stage-1 predictions | matched control + batch-1 reproduction seam |
| `A1_cap_lift` | tau 0.1, `SELECT_MAX` 51 (bank size ⇒ inactive) | OOF stage-1 predictions | the **bug-fix instrument**, no novelty claim |
| `A2_predcrit` | **permutation-calibrated per-direction threshold**, no cap | OOF stage-1 predictions | **the declared SCORED arm** — D1's claimable criterion |
| `A3_predcrit_sst` | permutation-calibrated, no cap | `[OOF stage-1 predictions, condition]` | combined; report-only, pre-declared ineligible to become the headline ex post |
| `A4_b1_sst` | tau 0.1, `SELECT_MAX` 32 | `[OOF stage-1 predictions, condition]` | isolates D4/SST alone |

**The criterion (the claimable object).** For each bank direction `d`, admit `d` iff `max_f OOF-R²(d, f)` exceeds `q_{0.95}` of its own **permutation null**: draw `B = 200` permutations of the condition rows *within the fit fold only* (one shared permutation of the row order per draw serves all 51 directions), recompute the identical 5-fold OOF R² over the identical map bank `{affine, quadratic, RBF-KR, kNN}`, and take the per-direction 95th percentile. No count cap; `SELECT_MIN = 1` retained. This replaces both arbitrary constants (`tau = 0.1` and `SELECT_MAX = 32`) with a per-direction, per-dataset null. It is strictly *more* conservative than tau = 0.1 on noise directions (allen_cahn's leftover, max OOF R² 0.0013) and strictly *more* permissive on directions the cap stranded (fisher_kpp, 0.29–0.31).

Why this is not round-2's refuted F20: F20 swept **tau** downward, admitting the least-predictable directions, monotonically worse; the cap was never varied and could not fire (fisher_kpp cond_dim 2, 0.9213 of energy off-bank). A1 keeps tau exactly where F20 found it optimal and removes only the integer; A2 keeps the *predictability* principle and calibrates its threshold. Different manipulation, different data (option-A regeneration).

**Small-N fallback (design necessity).** At `N_fit = 5` (both ifc cells, LOO) the permutation null is degenerate. `R3S1B2_PERM_MIN_ROWS = 20` makes A1/A2/A3/A4 revert to A0's shipped rule there, asserted **bitwise** (gate G-F). Consequence, stated up front: the ifc cells contribute zero movement, so all panel movement is sharp-cell movement.

**Row-budget hygiene (part 7 + the r3s4 seam).** Every reference arm is reported twice: `@fit` (the scored arm's own 320-row fit fold — the paired comparand used in every clause) and `@full` (400 rows — the frozen-floor seam, asserted at 1e-9). No clause uses an unmatched comparand.

**Report-only diagnostics answering B1's `open_question`** on cahn_hilliard + allen_cahn only: stage-2 input replaced by (a) PCA-3 of the condition, (b) a seeded random 3-d projection, (c) the true SET coefficients under matched fit/predict. No clause attached.

## Proposal

- **Category**: `gap / factorised-head stage-1 selection — permutation-calibrated per-direction predictability criterion replacing the SELECT_MAX clip, with the cap lift shipped beside it as a named bug-fix instrument, the SST input-space-expansion repair as a named preempted arm, and the n_SET/E_rem x reachability discriminator pre-registered on configurations the mechanism stage never saw`
- **Card type**: `model`
- **Motivation**: see report.md (quotes D1/D4/D5 verdict rows verbatim).
- **Concrete config**: as the arm table above, plus reference arms `head_onestage` (stage 2 disabled, matched folds — also the anchor comparand), `dc_only` (the condition→level law required by round-3 success criterion 1), floors `zero` / `train_mean` / `nn_condition` (seam-checked 1e-9 to `state/anchors_repaired/floors.json`), `affine_on_hf_train` (seam-checked to `launch_anchors.json:ifc_floors_repaired`, reported on all five cells).
- **Build gates**: G-A anchor reproduction (A0 reproduces `state/anchors/r3s1_factorised.json:per_dataset_per_seed_skill` at 1e-9; RAISE, INFRA-class); G-B floor seams at 1e-9; G-C stripped-view leakage tripwire + guard set at the same tier; G-D target-scaler pre-flight on cahn_hilliard before any test tensor is opened; G-E stage-2 empty-gate ⇒ bitwise no-op at 1e-12; **G-F** ifc small-N fallback bitwise no-op (A1/A2/A3/A4 ≡ A0 on both ifc cells at 1e-12); **G-G** permutation-null scope tripwire (the null touches fit-fold rows only; selection frozen before the test tensor is opened).
- **Recipe**: see report.md (complete JSON).
- **Expected outcome / expected falsification / anchor reference**: see report.md.

## Status

- Slot covered: **yes** (1 proposal, `card_type: model`).
- Skipped: no.
- Reopen candidates resolved: **0 of 0** — none exist; all four round-3 batch-1 cards carry `reopen_candidate: false` (read back from each JSON), and no r3s1 slot was skipped in batch 1.
- Immutables self-check: **pending → two items flagged** (see below) → revise in `iteration_2.md`.
  - **Item 6/8 flagged**: a `B = 200` permutation null multiplies the closed-form selection pass by 200. B1 ran 0.92 min/seed for the whole panel; the extrapolated worst case is hours per seed on `mit_preemptable`. I cannot certify "tier budgets fixed" or "checkpoint-resume implementable" without a timing pre-flight and a null-block checkpoint.
  - **Item 9 flagged**: L2 as first drafted ("A2 improves the panel geomean by ≥ 0.5083") is above the certified floor, but I had not verified it is *reachable* — the B3 M14 postmortem (a clause unpassable by construction) forbids shipping a threshold I have not priced. Needs the fisher_kpp-equivalent arithmetic on the record.
