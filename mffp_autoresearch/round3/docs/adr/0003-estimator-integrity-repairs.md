# ADR r3-0003: per-cell estimator-integrity repairs (red-team FIRES, pre-launch)

**Status:** accepted (operator, Eloise, 2026-08-06 — "A. Repair, then launch" on the HOLD adjudication).
**Evidence:** `mffp_autoresearch/defect_class_redteam/REDTEAM_REPORT.md` + measurement JSONs (14 candidates, fifth defect class: per-cell estimator integrity).

## Decisions

### D1 — allen_cahn_2d: task-void test rows removed (test-split trim)

22/100 test rows have per-row copy-LF gap < max(1e-6, 1% of the dataset median = 1.824e-5) — the red-team's headline 18 was the raw <1e-6 count; 9 rows are bit-identical LF≡HF constant fields — so those rows contain no prediction task and bias the copy-LF reference downward (inflating every skill).
No generator-side validity lever exists for ac (the void rows are ε/parameter combos that reach the uniform state by T=10, the pfc class at ~1/5 instead of ~1/2), so the repair is test-split curation: the 22 rows are removed from the shipped ac test split (originals archived at `_pretrim_backup_2026-08-06/`, dropped indices recorded in the meta), leaving n_test = 78 task-valid rows (post-trim minimum per-row gap 2.15e-5, verified).
The copy-LF reference, floors, and all model scoring recompute on the trimmed split; ac anchor cells (4 cards × 3 seeds) re-score via the quarantine pattern.
Train split untouched.

### D2 — cahn_hilliard: minimum-detectable-delta reporting rule (no data change)

The ch cell is outlier-dominated: top-5 of 100 test rows carry 76% of the copy-LF denominator; bootstrap CI half-width implies a ~166% minimum distinguishable model delta.
Rule (program.md §2): every ch claim reports the cell's bootstrap min-detectable-delta next to the skill; a ch delta below it is not claimable.
The data is legitimate physics (coarsening outliers), so the cell stays; its discriminative power is now priced honestly.

### D3 — ifc_poisson rung-scale finding: documented property, not a defect

The ~(64/r)² LF amplitude scaling is the h² convention recorded in the round-2 report (r2s3 arc; LF value graded through the amplitude channel).
The new `rung_scale_coherence` check encodes a per-dataset convention allowance instead of flagging it.

### D4 — four new preflight checks (the fifth-class instruments)

`degenerate_rows` (per-row copy-LF gap; ≥5% task-void → flag), `cell_stability` (top-5 denominator share > 0.4 or bootstrap CI half-width > 25% → OUTLIER_DOMINATED, always printing min-detectable-delta), `rung_scale_coherence` (RMS ratio within convention allowance), and a launch-time `data_binding` manifest (sha256 of every panel dataset's arrays recorded at launch into `round3/state/data_hashes.json`; the launch script refuses on mismatch — closes the score-cache-has-no-data-hash hole without modifying the frozen round-2 eval layer).
All checks land in `preflight/preflight.py` with selftest coverage.

## Consequences

- ac skills fall panel-wide relative to the pre-trim reference (honest-denominator effect, third instance); no cross-comparison without the flag.
- pfc's regenerated test split is certified by `degenerate_rows` before its swap is accepted (the check that would have caught pfc's class at generation time).
- HOLD clears after: checks implemented + selftested, ac trimmed + re-anchored, pfc landed + swapped + certified, full preflight PASS, anchors rebuilt.
