# ADR r3-0002: pfc regenerated from the crystal-forming parameter box (pre-launch panel mutation)

**Status:** accepted (operator, Eloise, 2026-08-06 — "A. Regenerate now"; PROGRAM_NOTE MUST #5 panel-mutation path).
**Evidence:** `mffp_autoresearch/true_gap_sweep/SWEEP_REPORT.md` (measured 2026-08-05).

## Context

`sharp__phase_field_crystal_2d`'s NO_GAP verdict (canonical gap 8.3e-6 shipped, 1.2e-6 repaired) predates the completeness repair and was carried as a standing caveat.
The sweep proved it is a **sampling-composition artifact**, not solver physics: under the production box (`r_range [-0.4, -0.1]`, `mean_density_range [-0.4, -0.2]`) half the samples satisfy $\sigma = -(r + 3\bar\psi^2) < 0$, sit in the uniform phase, decay to flat fields, and contribute gap ~1e-15, dragging the aggregate onto the no-gap floor.
The crystalline half has a genuine gap (2.2e-3–5.2e-2 at the bottom rung).
An all-crystalline box (`r ∈ [-0.4, -0.3]`, `ψ̄ ∈ [-0.25, -0.2]`, σ ≥ 0.11 everywhere) on the existing 32/64/128 ladder measures median bottom-rung gap **9.8e-3** — cahn_hilliard-class.
The resolution-pair lever is certifiably dead (LF 16/8 rungs blow up to NaN on crystalline samples; LF 64 has no gap), so the ladder stays 32/64/128.

## Decision

1. `configs/sample.yaml` pfc sampling narrows to the crystalline box: `r_range: [-0.4, -0.3]`, `mean_density_range: [-0.25, -0.2]` (uniform-phase region excluded by construction; ic_amplitude and output_time unchanged).
2. `phase_field_crystal_2d` is regenerated through the fixed package path (`generate_standardized.py`, in-job completeness gate) and swapped into `benchmark_42/sharp/` with the current arrays archived, mirroring the 2026-08-03 convention.
3. pfc anchor cells (4 cards × 3 seeds) are void on swap; they are quarantined and re-scored before G3 certifies, exactly as the ifc cells were (ADR r3-0001 D6).
4. Standing caveat replaced: the NO_GAP caveat retires; a **stiff-map caveat** takes its place — the condition→field map has smooth, linear ~1e4 finite-time amplification (verified linear in ε down to 1e-10, not chaos), so nearest-pair sensitivity witnesses will fire at ~1e4 and are adjudicated as steep-map false-positives with re-solve evidence, the same class as helmholtz's resonance waiver.
5. The pfc copy-LF reference (denominator) is recomputed on the regenerated data through the sanctioned mutation path (`round3/make_copylf_baselines_repaired.py` conventions); round-3-launch and post-r3-0002 pfc numbers are not comparable.

## Consequences

- Batch 1 dispatch waits for: regeneration COMPLETE certificate → swap → preflight (fidelity_gap expected PASS; completeness witness waiver per §4) → pfc re-anchor → `make_round3_anchors.py` full certification.
- fisher_kpp is untouched: its production recipe sits at the peak of its gap curve and clears the preflight threshold (sweep §1); the D_range strengthening remains an option for the benchmark paper, not this round.
