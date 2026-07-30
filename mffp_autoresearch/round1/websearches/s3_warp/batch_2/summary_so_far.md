# summary_so_far — `s3_warp`, batch 2

## What batch 1 settled (read from `experiment_cards/s3_warp/batch_1/B1.json` parts 5-7)

B1 was a DIAGNOSTIC (`do_not_promote:true`, no anchor written). Its headline is
a **benchmark defect, closed form**: `round1/eval/panel_data.py::copylf_prediction`
upsamples with `scipy.ndimage.zoom(order=1, grid_mode=True)` — the cell-centred
convention — while the sharp datasets are point samples on a periodic node grid
`x_j = j*L/n`. On the dyadic ladder that misregisters copy-LF by exactly
`(r-1)/2 = 0.5` HF cells (F1, F2: closed-form Lucas–Kanade sees +0.4995/+0.4996
on allen_cahn, +0.5020/+0.4889 on cahn_hilliard). Zero-parameter registration
fixes score skill 0.110-0.497 across the four sharp datasets (F3, F16).
`ext__helmholtz_2d` carries the same defect as a zero-mean +/-1.5-cell *stretch*
(F5). Mentor note filed: `docs/operator_notes/2026-07-30-benchmark-registration-note.md`.

**Consequence for this stream**: after re-referencing to a correctly registered
copy-LF, the residual oracle-warp ceiling collapses to 1.4 % (fisher_kpp),
11.1 % (allen_cahn), 17.0 % (pfc) — and **survives only on
`sharp__cahn_hilliard` at 83.4-85.2 %** (F9), where the residual displacement is
genuinely spatially varying with **median |phi| 0.64-0.74 HF cells** (F11) and is
**not** linear-filter-correctable (the s6 LSI filter leaves skill 0.44 there —
F14/F15/F18). `pfc` has no fidelity gap at all at its scored level pair (F6,
3.19e-07 relative). No sharp dataset's HF field carries energy above the LF band
(F7), so the whole gap is coarse-solve low-mode error.

Two further B1 constraints on any batch-2 model card:
- **F17/F10 — do NOT warp via `grid_sample` on the interpolated LF.** The second
  bilinear resample injects mid-band error (per-band ratio 2.8-8.6x vs copy-LF);
  a 512-dof *oracle* warp on the damaged moving image LOSES to a zero-parameter
  fixed resample on 3 of 4 sharp datasets. Resample ONCE from raw LF at warped
  coordinates, or displace in Fourier space.
- **F12 — the constant-displacement arm is mandatory**: the DC of phi alone
  delivers 89.9-99.5 % of the full warp's error reduction on pfc/allen_cahn/
  fisher_kpp, and 48.9 % on cahn_hilliard.
- **F13** — on the corrected image the C4 rung buys ~nothing; only C16 pays
  (cahn_hilliard 0.0605 -> 0.0306 -> 0.0090). DOF must be budgeted from the
  corrected image.
- **Leg C (topology)**: cahn_hilliard is the panel's most nearly diffeomorphic
  dataset — 5-6 % of samples have a connected-component mismatch, mean |dN| 0.11
  — so the appearance-term clause is satisfiable by *scoping* rather than by a
  metamorphosis term. That is the open design question this batch must price.

Part 7 licenses a **NARROW D1 model card, cahn_hilliard only**, with three
mandatory comparators: the locked warp-off control, a constant-displacement-only
arm, and a registration-corrected copy-LF sidecar (frozen skill stays primary).
Its open question is whether the residual displacement is **predictable from the
LF field the model actually receives**, or only visible to an HF-fitted oracle.

## What batch 1's websearch already adjudicated (`websearches/s3_warp/batch_1/report.md`)

Do not re-survey the general warp literature. Settled there:
- **D1 = `preempted-but-MF-composition-open`**. Learned warping is *the*
  primitive of a 2026 neural PDE solver (Flowers, https://arxiv.org/html/2603.04430
  — STN-style bilinear sampling at `x + rho(x)`, single-fidelity, no LF->HF
  correction, no zero-init, no smoothness penalty). Warp + appearance is
  published as **metamorphosis** (MetaRegNet, https://arxiv.org/pdf/2303.09088).
  Transport geometry for MF diffuse-interface correction is published (Khamlich,
  https://arxiv.org/html/2603.04232v2 — classical OT on *residual* fields,
  conservative Allen-Cahn, 128^2->512^2, no NN).
- Claimable slice: a *neural* displacement predicted **from the LF PDE field**
  and applied to that field before a learned correction, inside an MF operator
  surrogate at N_hf small.
- Displacement parameterization at small N: free-form fields dominate but drop
  diffeomorphic guarantees, and *global* smoothness penalties are documented as
  locally insufficient (https://arxiv.org/html/2412.17982v1); low-parameter
  parents are B-spline control grids and velocity-field integration
  (https://arxiv.org/html/2405.18684v1).

## Cross-stream boundary (question (c))

`experiment_cards/s6_local/batch_2/B2.json` (status `running`) is a **local
intensity-space defect corrector**: banded local pixel gate + a scored
zero-trained-parameter `lsi_ctrl` FFT filter, circular padding by a data-driven
wrap-continuity test, out-of-fold trust head. B1 F14 showed 87-98 % of that
filter's energy IS the half-cell phase ramp — i.e. s6 already owns the LSI /
low-mode amplitude part of the residual, and on cahn_hilliard it saturates at
skill 0.44. So the warp arm's honest territory is exactly the 85 % that the LSI
filter cannot reach. **What this batch must search**: whether the literature
reports a per-term attribution for the warp-vs-intensity split, and whether
joint or sequential training is the published answer.

## Floors / anchors

`state/noise_floor.json`: `min_claimable_effect` cahn_hilliard **0.553**,
allen_cahn 1.633, pfc 1.151, fisher_kpp 0.418, ifc_poisson 0.240,
helmholtz 9.695 (report-only). No `state/anchors/s3_warp.json` exists — B1 was a
diagnostic and wrote none; the anchor is the champion's certified panel geomean
per section 12.3.

## Open questions this batch must answer

1. Which displacement-**prediction** architecture fits a 0.64-0.74-cell,
   spatially varying, 5-parameter-conditioned residual at N_hf small?
2. Is the **single-interpolation composition** (compose the warp with the LF->HF
   upsample so only one resample happens — e.g. Fourier-shift / band-limited
   resample at warped nodes) published, and where?
3. Does the metamorphosis literature report **per-term attribution** (how much
   error the appearance channel owns vs the diffeomorphism)?
4. Joint vs sequential warp+correction training; ground-truth-free displacement
   validation (cycle/inverse consistency) at small N.
