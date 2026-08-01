# Fix proposal — registration defect in the mffp_sharp dataset generator

**To:** Nicholas (mentor — this surface is mentor-owned; this is a recommendation package, nothing has been landed).
**From:** Eloise's agent, 2026-08-01.
**Scope:** `mffp_sharp/common/ladder.py` (`upsample_to_hf`, `assemble_sample`) and its call sites.
**References:** registration-defect note 2026-08-01 item 2; ADR r2-0001 (corrected reference convention); ADR r2-0004 §1 (model-side repair).

## What the defect is

The generator stores each sample twice: the raw native-grid field per fidelity (`/fields/res_R`) and a pre-aligned copy interpolated onto the HF grid (`/fields_hf/res_R`).
`ladder.upsample_to_hf` built every aligned copy with a single cell-centred coordinate map (source points at x_j = (j+0.5)/n).
That map is only correct for finite-volume output; the pseudo-spectral and periodic-FD solvers in this package sample their fields at nodes x_j = j/n, and helmholtz on interior Dirichlet nodes x_j = (j+1)/(n+1).
Applying the cell-centred map to node data reads every output pixel from a coordinate displaced by (r−1)/2 HF cells — half a coarse cell — and clamp-extends across periodic seams instead of wrapping.
So the shift is baked into the aligned arrays on disk and into the LF-vs-HF fidelity-gap metrics the datasets report about themselves.
The raw native-grid arrays were always correct; round-2 eval already sidesteps the stored aligned arrays by rebuilding from raw, but anything that reads them inherits the shift, and any regeneration with the current code reintroduces it.

## What the patch changes (`ladder_fix.patch`, 11 files, +315/−51)

`ladder.py` now dispatches per PDE, mirroring — not reinventing — the two already-audited implementations: `round2/eval/panel_data.py` (ADR r2-0001) and `factory_mffp/models/_common/lf_registration.py`.
Three conventions: `node_periodic` (node-aligned bilinear with periodic wrap; exact at shared nodes on the dyadic ladder), `node_dirichlet` (interior-node map, clamped edges; helmholtz), and `cell_centered` (the original map, kept verbatim — it is correct for the PyClaw finite-volume solvers).
Classification covers all 16 solver modules wired into `generate.py`: 11 spectral/periodic-FD modules are `node_periodic`, helmholtz is `node_dirichlet`, and the 4 PyClaw modules (euler, burgers, sod, shallow_water) are `cell_centered`.
An unclassified PDE **raises** instead of defaulting, matching the eval layer's assert-don't-default policy; `assemble_sample` now requires the PDE name and records the convention used, and `io.py` writes it as an `alignment_convention` HDF5 attribute for provenance.
Call sites updated: `generate.py` (passes the config block's `module`), two figure scripts, and the tests; `tests/test_ladder.py` gains 12 registration tests including the exact-nesting invariant that would have caught the defect on day one.
The patch was developed in a temporary git worktree at monorepo commit `b80e622`; it applies cleanly to the current tree (`git apply --check` verified) and nothing was pushed or edited in place.

## What regeneration would touch

Only the derived aligned arrays (`/fields_hf/res_R` for R < HF) and the self-reported fidelity-gap metrics change.
Raw native-grid solves are byte-identical before and after (verified bit-for-bit in the sample round), so no solver time needs to be re-spent: aligned arrays can be rebuilt from the stored raw fields.
Model training inputs in the factory are unaffected by the stored aligned arrays — the round-2 eval layer and the model-side lifts already rebuild from raw under the corrected conventions (ADR r2-0004 §1).

## Verification evidence (details and numbers in `verification.md`)

A 4-sample demo round on allen_cahn_2d, cahn_hilliard, and helmholtz_2d was generated with the old and the patched code (`sample_round/old`, `sample_round/new`), sample-round scale only per the approval gate.
Raw and HF arrays: bit-identical old vs new.
New aligned arrays: equal to the round-2 eval layer's independent reconstruction-from-raw to ≤1.2e-7 (float32 storage precision), with the exact-nesting invariant holding at exactly 0.0; on the real `sharp__allen_cahn_2d` raw LF fields the patched interpolator agrees with the eval layer to 0.0.
The half-cell shift: measured at exactly (r−1)/2 HF cells in the old aligned arrays (1.5 cells at 32→128, 0.5 at 64→128) and 0.0 in the new ones.
Self-metrics: allen_cahn's reported LF→HF rel-L2 gap was inflated 3.2–4.7x by the shift; cahn_hilliard's bulk numbers barely move but its high-wavenumber `spectral_band` entries change ~3x; helmholtz's `spectral_band` changes ~4x.
`mffp_sharp` pytest on the patched tree: 135 passed, 8 skipped (PyClaw, box-only), 1 pre-existing environment failure (git-ignored `ks_2d_golden.npy` fixture absent on this machine; identical on the unpatched tree).

## Recommendation

1. Review and, if acceptable, apply `ladder_fix.patch` on the SURF/monorepo mainline (mentor's call; we have deliberately not committed it anywhere).
2. Treat every dataset generated with the old ladder as carrying shifted aligned arrays and defective self-metrics; the raw arrays remain trustworthy.
3. Regenerate aligned arrays and self-metrics from the stored raw fields (no re-solving needed) **only after sign-off**, and gate any future dataset release on that regeneration — any generation run before the patch lands reintroduces the defect.
4. Keep the round-2 rule that consumers rebuild alignment from raw until regeneration has happened; the new `alignment_convention` attribute makes corrected files self-identifying.
5. If a new PDE module is ever added, the classification raise forces an explicit grid audit before its datasets can be built — please keep that behaviour.

## Package contents

- `ladder_fix.patch` — the proposed change (apply from monorepo root with `git apply`).
- `sample_round/` — demo configs and old/new HDF5 outputs plus `sample_summary.json` for both runs (HDF5 files are git-ignored artifacts, present on this box).
- `verify_ladder_fix.py` + `verification_results.json` — the acceptance test and its machine-readable results (verdict PASS).
- `verification.md` — the acceptance evidence, human-readable.
