# Verification — ladder.py registration fix (acceptance test)

Machine-checked by `verify_ladder_fix.py`; full numbers in `verification_results.json` (verdict: **PASS**, no hard failures).
Re-run with `python verify_ladder_fix.py` (defaults resolve the sample round and the round-2 eval layer from repo-relative paths).
Pass `--patched-src <checkout>/mffp_sharp/src` after applying `ladder_fix.patch` to additionally exercise the patched `ladder` module directly; without it the independent eval-layer reference still fully verifies the stored arrays.

## Setup

Two identical sample rounds (same seed 42, same configs except `out_dir`) were generated into `sample_round/old` (unpatched code at monorepo `b80e622`) and `sample_round/new` (patched worktree).
Datasets: `allen_cahn_2d` and `cahn_hilliard` (node-sampled periodic pseudo-spectral) and `helmholtz_2d` (interior-node Dirichlet) — 4 samples each on the 32/64/128 ladder, covering both corrected conventions.
This is a sample-round demonstration only, per the SURF approval gate; no full generation was run.
`cahn_hilliard` `output_time` was shortened 5.0 → 1.0 for demo runtime; registration is time-independent so this changes nothing about what is verified.

## (a) Raw solves untouched

For all three datasets, every native-grid array under `/fields/res_*` is **bit-identical** between old and new runs, and so is the HF-grid copy of the HF field.
The patch changes only the derived aligned arrays `/fields_hf/res_{32,64}`.

## (b) Corrected aligned arrays match the round-2 eval layer

The new aligned arrays equal the eval layer's independent reconstruction-from-raw (`round2/eval/panel_data.py`, ADR r2-0001) to float32 storage precision:
max abs difference 1.5e-8 (allen_cahn), 1.2e-7 (cahn_hilliard), 9.3e-10 (helmholtz).
Exact-nesting invariant on the periodic sets: `aligned[::r, ::r] == raw` holds **exactly (0.0)** in the new arrays and fails in the old ones (max abs 0.078 allen_cahn, 0.90 cahn_hilliard).
On the **real** `sharp__allen_cahn_2d` dataset (stored raw 128² LF vs 256² grid), the patched `ladder.upsample_to_hf(..., convention="node_periodic")` agrees with `panel_data._node_aligned_periodic_up` to **0.0** max abs difference, and the eval layer's exact-nesting check holds at 0.0.

## (c) The half-cell shift: visible in old, gone in new

Index-ramp probe of the coordinate maps (the same probe as `models/_common/test_lf_registration.py`): the old cell-centred map reads every output pixel from a source coordinate displaced by −(r−1)/2 HF cells (measured −0.5 at r=2, −1.5 at r=4); the node-aligned map's displacement is 0.0.
Fractional-shift scan on the stored demo arrays: the old aligned fields sit 1.5 HF cells (res 32, r=4) and 0.5 HF cells (res 64, r=2) diagonally off the new ones for both periodic datasets — exactly the predicted (r−1)/2.
For helmholtz the diagonal-scan probe reads ≈0.05/0.0; the Dirichlet interior-node misregistration is not a uniform translation (the old map's error varies across the domain), so the eval-layer reconstruction identity in (b) is the authoritative check there.

## (d) Self-reported fidelity-gap metrics before/after

Mean over the 4 demo samples, LF res vs HF (old → new); full panel in `verification_results.json`.

| dataset | res | rel_l2 | linf | spectral_band |
|---|---|---|---|---|
| allen_cahn_2d | 32 | 0.1778 → 0.0562 | 0.0555 → 0.0169 | 0.0136 → 0.0122 |
| allen_cahn_2d | 64 | 0.0584 → 0.0125 | 0.0139 → 0.0035 | 0.0032 → 0.0106 |
| cahn_hilliard | 32 | 1.3510 → 1.3500 | 2.1178 → 2.0057 | 0.0150 → 0.0140 |
| cahn_hilliard | 64 | 0.2455 → 0.2410 | 1.1967 → 1.1487 | 0.0028 → 0.0080 |
| helmholtz_2d | 32 | 4.7846 → 4.7853 | 0.0044 → 0.0045 | 0.0120 → 0.0458 |
| helmholtz_2d | 64 | 1.5556 → 1.5422 | 0.0023 → 0.0024 | 0.0043 → 0.0184 |

Reading: on the smooth-interface allen_cahn fields the reported LF→HF gap was dominated by the artificial shift — rel-L2 drops 3.2x (res 32) and 4.7x (res 64) once registration is correct, matching the 2.0–8.6x reference-denominator inflation the round-1 audit measured on the sharp panel.
On rough/chaotic cahn_hilliard fields the intrinsic under-resolution error dominates and the bulk numbers barely move, but the high-wavenumber `spectral_band` and `linf` panel entries shift — the panel metrics the project uses precisely to see thin sharp regions are the ones the defect contaminates.
Helmholtz bulk rel-L2 is dominated by genuine coarse-grid dispersion error and is essentially unchanged, while `spectral_band` changes ~4x.

## Test suite on the patched worktree

`pytest tests` in `mffp_sharp` (monorepo venv, Python 3.11): **135 passed, 8 skipped, 1 failed**.
The 8 skips are the PyClaw solver tests (`clawpack` is box-only, not installed on this node).
The 1 failure is `test_ks_1d.py::test_2d_output_matches_golden` — `tests/fixtures/ks_2d_golden.npy` is git-ignored (`*.npy`) and absent on this machine; the identical failure occurs on the **unpatched** tree, so it is a pre-existing environment gap, not a patch regression.
New in the patch: 12 registration tests in `tests/test_ladder.py` (exact nesting, index-ramp probe, periodic-wrap seam, shift-gone regression, Dirichlet interior exactness, raise-on-unclassified, and a pin that every module wired into `generate.py` is classified).
