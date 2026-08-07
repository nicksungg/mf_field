# phase_field_crystal_2d_generated

**PDE module:** phase_field_crystal  
**Source:** Elder & Grant 2004  
**ndim:** 2  
**Availability:** regenerable (eloise sharp-field solver)  

## ⚠️ Degeneracy warning

This dataset is flagged **degenerate** in `MANIFEST.csv`. It is not broken, but a model can score well on it without doing anything interesting, so results here should not be read as evidence of multi-fidelity skill.

- **operator-hard** — the condition vector barely predicts the field (param→field distance correlation 0.017, threshold 0.15), and unlike the 2026-08-05 release this now holds even on the two physical parameters alone (0.024).
  The crystalline PFC map is *stiff*: ~1e4 linear amplification from parameters to field, so nearby parameter draws produce effectively uncorrelated crystal patterns.
  This is a property of the physics, not a data defect.
- **top-rung convergence (do not benchmark L2→L3)** — the crystalline fields are spectrally converged at L2 (64²): exact (spectral) interpolation of L2 reproduces L3 to ≤ 1.7e-6 relative L2 on every test row.
  Any task built on the L2→L3 pair has no prediction content, and any nonzero "copy error" measured there is interpolation-method artifact.
  The real fidelity gap lives at **L1→L3** (per-row spectral copy gap, test median 4.5e-3).
  Use L1 as the low-fidelity input, and use spectral (not polynomial) interpolation when lifting for reference baselines.

See the *Degeneracy flags* section of [`../../README.md`](../../README.md) for criteria, thresholds, and caveats.

## Fidelity ladder (ablation-driven)

- L1: [32, 32]
- L2: [64, 64]
- L3: [128, 128]

## Inputs/outputs
- `x`: (N,18) condition vector [r, mean_density, ic_c0, ic_c1, ic_c2, ic_c3, ic_c4, ic_c5, ic_c6, ic_c7, ic_c8, ic_c9, ic_c10, ic_c11, ic_c12, ic_c13, ic_c14, ic_c15]
- `y`: (N, prod(grid)) flattened field at each fidelity

## Sample counts
- Train: **400**  Test: **100**

## File layout
`train_l1.npz`..`train_l3.npz`, `test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).

## Changelog

- **2026-08-06 — full regeneration from a crystalline-only sampling box** (MFFP autoresearch ADR r3-0002).
  The 2026-08-05 release drew (r, mean_density) from a box where roughly half the samples relax to the uniform phase, leaving no LF↔HF gap to learn.
  This release samples `r ∈ [-0.4, -0.3]`, `mean_density ∈ [-0.25, -0.2]` — all-crystalline (σ = −(r + 3ψ̄²) ≥ 0.11) — restoring a real bottom-rung fidelity gap (L1→L3 test median 4.5e-3, spectral).
  All arrays changed; the previous revision is available from this repository's git history (revisions before 2026-08-08).
  Scores are **not comparable** across this regeneration.
- **2026-08-07 — top-rung convergence documented** (MFFP autoresearch ADR r3-0004).
  The crystalline fields are band-limited below the L2 Nyquist, so L2→L3 carries no task (see the warning above).
  The MFFP autoresearch round-3 benchmark scores this dataset as report-only until its evaluation is re-pointed at the L1 rung with a spectral reference.
