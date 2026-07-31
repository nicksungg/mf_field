# ADR r2-0001: Corrected copy-LF reference convention

Date: 2026-07-31. Status: accepted (round-2 launch prerequisite, spec §3).

## Context

Round 1 established (s3-B1, closed form; report §5) that the round-1 copy-LF
construction — `scipy.ndimage.zoom(..., order=1, grid_mode=True,
mode="nearest")` — reads node-sampled pseudo-spectral fields under a
cell-centred convention, misregistering copy-LF by (r−1)/2 HF cells on both
axes, and clamp-extends across periodic seams (second-order, 0.1–0.7%).
Skill denominators were inflated 2.0–9.1× on the sharp panel and 1.10× on
helmholtz; ~96–100% of round-1 sharp-panel "wins" were re-learned
registration (s2-B2).

## Decision

Round-2 references are computed per dataset (`round2/eval/panel_data.py`):

| datasets | convention | why |
|---|---|---|
| allen_cahn, pfc, fisher_kpp, cahn_hilliard | **variant C**: node-aligned bilinear, periodic wrap (HF pixel k samples LF index k/r) | node-sampled pseudo-spectral solvers on nested dyadic ladders; exact identity `up[::r,::r] == coarse` |
| ext__helmholtz_2d | **variant E**: Dirichlet interior-node map `j = (k+1)(h+1)/(H+1) − 1`, clamped | `grid_xy` puts helmholtz on interior nodes `x_j=(j+1)/(n+1)`, r=4 non-nested |
| heat_local, fluid, sod_1d (guards), ifc_* | round-1 legacy cell-centred zoom | registration audit: NON_NESTED_BUT_CONSISTENT / INCONCLUSIVE — "fixes" make their references worse |
| ifc_poisson | paper bar 0.036 | test ships no LF (r1 ADR 0002), unchanged |

**Variant C (bilinear), NOT variant D (band-limited), defines the denominator**:
D is the physically exact interpolant for band-limited fields but collapses
pfc's denominator to 3.2e-07 (no fidelity gap — the solver's continuous
spectral symbol makes LF≈HF at shared modes), producing meaningless skill
ratios. C keeps the round-1 definition's interpolation class ("bilinearly
interpolated onto the HF grid") and only fixes alignment and boundary
handling. pfc carries a standing caveat either way; the dataset-redesign
recommendation to the mentor stands (r1 report §5 fix list).

`COPYLF_DEF_HASH` (sha256 of panel_data.py) is recorded in the baselines JSON,
every result JSON, and the score cache — closing the round-1 gap where
NRMSE_DEF_HASH covered nrmse.py only and reference changes were invisible.

## Consequences

- Corrected denominators (test nRMSE): helmholtz 0.299033, pfc 0.007381,
  allen_cahn 0.001781, fisher_kpp 0.021450, cahn_hilliard 0.041803. Guards
  reproduce round-1 values bit-for-bit (seam-checked in
  make_copylf_baselines.py).
- Round-2 skills are NOT comparable to round-1 skills on corrected datasets;
  any side-by-side must state both denominators (`r1_frozen_nrmse` is stored
  per dataset).
- The generator-side twin defect (`mffp_sharp/common/ladder.py` cell-centred
  `_cell_centers`) is NOT touched — mentor-owned surface; the operator note
  `../../../round1/docs/operator_notes/2026-07-30-benchmark-registration-note.md`
  is the recommendation of record.
- Regression tests: `eval/tests/test_registration_fix.py` (node identity,
  k/r ramp probe, periodic seam, Dirichlet map, dispatch, unclassified-raises).
