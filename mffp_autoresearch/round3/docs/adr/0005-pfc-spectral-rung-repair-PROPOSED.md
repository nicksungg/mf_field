# ADR r3-0005 (PROPOSED): pfc scored cell re-pointed to L1 with a spectral reference

**Status: PROPOSED — requires operator (Eloise) AND mentor sign-off before execution.**
This ADR amends the frozen round-2 eval convention (ADR r2-0001) for one dataset; that layer was frozen precisely so rounds stay comparable, so the amendment is not an orchestrator-level decision.
Prepared 2026-08-07 under ADR r3-0004 §4 (repair prepared in parallel; pfc is report-only until this is ratified).

## Problem being repaired

`sharp__phase_field_crystal_2d` is scored at `max(lf_fids)` = L2(64²) → L3(128²).
The crystalline fields (ADR r3-0002) are band-limited below the L2 Nyquist, so that cell is spectrally converged: exact per-row copy gap ≤ 1.66e-6 on all 100 test rows — no prediction task.
The certified reference 0.018257 is ~100% linear-interpolation error of the ADR r2-0001 lift (`map_coordinates order=1`).
The real fidelity gap lives at L1(32²) → L3, which the eval never scores.
Simply re-pointing at L1 under the *existing linear lift* does not work: the linear-lift error at 32²→128² is ~4× larger than at 64²→128² (≈ 0.07), which would again dominate the true gap (≈ 0.012) — the reference must become spectral at the same time.

## Proposed changes (two, inseparable)

1. **Served rungs**: the round-3 stripped view serves pfc fids {1, 3} (L2 withheld), so `max(lf_fids)` = 1 without touching frozen code.
   Raw L2 stays in `benchmark_42` for provenance.
2. **Reference lift**: `panel_data.copylf_prediction` gains a pfc-specific spectral (FFT zero-pad, node-periodic) lift — a per-dataset convention amendment to ADR r2-0001, mirroring how that ADR already assigns per-dataset conventions.
   One dataset entry changes; every other dataset's path is untouched (seam assertion required).

## Measurements (already taken, 2026-08-07)

- Proposed cell (L1→L3, spectral, test split): per-row copy gap **mean 0.012358**, median 0.004520, min 0.002692, max 0.148364.
- `degenerate_rows`: **OK** (0 task-void rows of 100).
- `cell_stability`: **OUTLIER_DOMINATED** — top-5 rows carry 38.8% of the denominator; bootstrap min-detectable-delta **65.8%**.
  The cell is honest but low-resolution: like cahn_hilliard (ADR r3-0003 D2), every pfc claim must report the MDD next to the skill, and deltas below it are not claimable.
- Train-side L1→L3 spectral mean 0.011742 (floors re-price against the new reference).
- Condition→field remains stiff (pf_dist_corr ≈ 0.02 even on physical parameters): models are expected to sit far above the copy-LF reference; the cell mainly prices how much of the crystal's condition-determined structure is recoverable.

## Execution plan on ratification (quarantine pattern, third instance)

1. Stripped-view change (pfc fids {1,3}) + `panel_data` spectral entry (seam-checked, archived).
2. Reference + floors recompute (archive first; ac/pfc-style sanctioned-mutation script).
3. Quarantine current pfc anchor cells; 12 re-score jobs (4 cards × 3 seeds) — same shape as the 2026-08-07 batch, minutes of compute.
4. `make_round3_anchors.py`: pfc returns to `PANEL` (6-dataset scored panel); best-floor lineage extends.
5. Preflight fifth-class on the new cell (expected: OK + OUTLIER_DOMINATED warn as measured); data-hash manifest re-recorded (stripped view changes pfc's served set).
6. Batch-1 cards: pfc thresholds re-issued via addendum (MDD-priced); HF: no array changes (serving-layer only), dataset card gains a "scored at L1" note replacing the report-only status.

## Alternatives considered

- **Report-only permanently** (status quo, ADR r3-0004): loses the panel's only stiff-map dataset; no eval-layer change.
- **Regenerate with a higher-resolution ladder** (e.g. 64/128/256 with sharper physics): larger compute, new physics-validation cycle, and the sweep showed the crystal wavelength — not the grid — sets the convergence point, so the same convergence likely reappears one rung up.
- **Linear lift at L1** (no spectral amendment): rejected — reference would again be ~85% interpolation artifact (measured ≈ 0.07 linear vs 0.012 true).
