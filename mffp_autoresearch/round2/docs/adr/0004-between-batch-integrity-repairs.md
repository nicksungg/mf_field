# ADR r2-0004 — Between-batch integrity repairs (2026-08-01 halt window)

Status: accepted.
Date: 2026-08-01.
Context: the round was operator-halted 2026-08-01 with batch 3 in flight.
Eloise directed: "fix all bugs that could affect autoresearch" before resume.
The work list is the open-items section (§06) of the registration-defect note
(`mffp_autoresearch/REGISTRATION_DEFECT_NOTE_2026-08-01.html`) plus two owed
items from the halt checklist.
Every repair below happened while no experiment was running; no frozen
round-1 or round-2 number is altered.

## 1. Model-side registration dispatch (note §06 item 1) — REPAIRED

`factory_mffp/models/_common/lf_registration.py` (commit `f63bcbf`) gives
model code the same per-dataset convention dispatch the eval layer got in ADR
r2-0001, and every LF/HF field lift in the factory zoo now goes through it:
the nine `_to_grid` families (including `mf_fno_transfer_film`, the r2s3
declared baseline and the only round-1 family eligible as a round-2
teacher), `_common/fire_core.py::to_grid` (all `fno_fire_*`), and the three
coregionalization `AdapterMFDataset._resample_to` sites.
`fno_coreg_residual` and `fno_mf_stack`, whose lifts sit inside `hf_predict`,
now refuse node-registered datasets outright (assert-don't-default) instead
of silently mis-registering.
Unclassified datasets keep the historic cell-centred path bit-for-bit (only
the sharp panel is proven node-sampled; `align_corners=False` is correct for
genuinely cell-centred data).
`mf_fno_transfer_bar` is untouched (`manifest.frozen = true`).
Nine tests in `models/_common/test_lf_registration.py` pin the index-ramp
probe, the `up(coarse)[::r,::r] == coarse` invariant, legacy bit-identity,
and torch/numpy agreement; the lift was verified against the eval layer on
real `sharp__allen_cahn_2d` train LF (exact nesting, 7.5e-9 float32
agreement).
Round-2 `models_r2` code needed no repair: r2s2-B1/B2 and r2s3-B2/B3 and
r2s4-B2/B3 already vendor the corrected conventions with agreement asserts;
r2s1's interpolates act on internal learned features (no LF exists in that
stream); r2s3-B1's legacy lift was that card's deliberate mechanism control.
`akash/` carries the same defect but is mentor-owned — recommendation stands,
no edit.
The generator-side defect (`mffp_sharp/common/ladder.py`, note §06 item 2)
is likewise mentor-owned and unrepaired; round-2 eval sidesteps it by
rebuilding copy-LF from raw native-grid LF.

Forward rule for new cards: program §12 (registration-of-model-side-lifts
convention).

## 2. Target-scaling defects (note §06 item 3) — RULE + TOOLING; r1 code frozen

The two concrete defects live in round-1 `s2_beyond_copy-B2`'s
`lf_resid_fno` family, which is immutable with the rest of the round-1
record (immutable 13); they are not silently fixable there and stay on the
record as findings (helmholtz: top-1 sample carries 89.2% of loss energy,
effective N 1.2/400; pfc: global scaler 7.95e4× the median per-sample scale,
emitted-noise floor 8206× truth).
What prevents recurrence in round 2: the pre-flight audit
(`tools/target_scale_spread_audit.py`, verified 2026-07-30 — its verdicts
isolate exactly the two failing datasets) is now mandatory on model cards
training on helmholtz or pfc, with per-sample normalisation required on an
`OUTLIER_DOMINATED`/`NEAR_ZERO_TARGETS` verdict (program §12).
No live round-2 family carries a global-scaler defect today (r2s1 predicts
per-sample amplitude via its `unit_l2` + amp-head design; r2s2/r2s3/r2s4 fit
per-rung or per-sample statistics).

## 3. Helmholtz closed-form solvability (note §06 item 5) — CARRIED FORWARD

Round-1 ADRs 0009/0010 recorded that helmholtz HF test fields reproduce from
the condition vector alone to 2.2e-13 via two FFTs; the flag had not carried
into the round-2 program.
Now in program §2.3 standing caveats: helmholtz cannot support a
multi-fidelity or learning claim of any kind; report-only, every number
flagged.
A dataset redesign (or formal exclusion) remains a mentor-level decision, as
does pfc's (note §06 item 4, unchanged: mandatory caveat).

## 4. Deferred plumbing (note §06 item 7) — RESOLVED BY AUDIT, NOT BY EDIT

- **Corrector input wrap seam**: already applied in the live round-2 stack —
  r2s2-B1 Decision B built the corrected upsampler (wrap seam folded in) and
  B2 re-vendored it byte-identically.  The only remaining legacy copies live
  in frozen round-1 worktrees.  Nothing left to edit.
- **Attention query-chunk permutation** (`s4_hybrid_routing` model.py
  204–214): no live round-2 consumer — the r2s2 stack vendors the s4 LSI
  filter and local corrector, not the attention corrector; the s4 family
  itself is a frozen round-1 record.  Standing instruction: if the s4
  attention corrector is ever reused, permute queries before chunking
  (recovers the unchunked forward pass to 0.014% at zero cost, s4-B2 F7/F8).

## 5. Warp premise re-audit (note §06 item 6) — RUN; PREMISE DEAD POST-FIX

`tools/warp_premise_audit.py --datasets PANEL` re-run 2026-08-01 against the
corrected references; output `state/warp_premise_postfix_2026-08-01.json`.
Residual transport ceiling on the corrected path: the test-fitted per-sample
rigid-shift oracle buys ≤ 3% relative (pfc 0.2218→0.1648 was the copy-LF
column; corrected-path gains are 0.1196→0.1103 allen_cahn, 0.3536→0.3425
fisher, 0.4193→0.3989 ch, with median fitted |shift| 0.000–0.045 cells on
allen_cahn/pfc/ch) and the level-set displacement medians collapse from
≈ 0.7071-cell (the registration expectation) to 0.007–0.051 cells on
allen_cahn/pfc/ch.
Residual worth noting: fisher_kpp keeps a 0.62-cell non-rigid level-set
median (its rigid oracle still buys only 3%) — local, not a constant, and
small; helmholtz's corrected path still shows a ≈ 2.0-cell level-set median
against a 2.12-cell non-nested-grid expectation with a 2% oracle gain
(consistent with the known zero-mean Dirichlet stretch; moot under §3).
`ifc_poisson` errors out (test ships no LF — no moving image to audit; by
design, recorded in the JSON).
Conclusion: round 1's warp/displacement premise was the registration
constant; there is no meaningful transport left to warp on the corrected
references, so no future warp card should launch without quoting this file.

## 6. Halt-checklist repairs

- r2s4-B3 signed-reach probe fix (code-reviewer SUGGEST 1) applied and
  `03_ledger.sh 0` re-run before any analyzer read `diagnostic.json`
  (commit `09e2c6b` on `round2/exp-r2s4_diag-B3`); no verdict flipped.
- Round-1 top-3 seed confirms (submitted 2026-07-31): `s6_local-B2` and
  `s1_poisson-B3` seeds 1/2 COMPLETED; `s4_hybrid_routing-B3` seeds 1/2
  trained to completion but FAILED their own validity gates — V1 pfc dc_raw
  18.8% vs 10% tol, V5 ifc_poisson 0.62–0.71% vs a 1.9e-4
  independent-training envelope (the gate file itself notes bitwise equality
  is not decidable on GPU).  Recorded as a seed-sensitivity finding on the
  round-1 record, not patched into a pass; whether to relax the gates and
  re-verify is an operator/mentor decision.
