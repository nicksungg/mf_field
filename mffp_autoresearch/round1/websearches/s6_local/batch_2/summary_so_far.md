# Summary so far — stream `s6_local`, batch 2

## Where the stream stands

`experiment_cards/s6_local/batch_1/B1.json` (status complete) delivered the
round's best panel number: geomean **0.2346** vs the certified champion anchor
**6.703**. The mechanism-analyzer's verdict (part 6, M1) is blunt about what
produced it: **not** the card's advertised per-pixel trust gate over the LF
field, but *"machine-learned Richardson-style defect correction"* — base = the
real coarse solve interpolated to the HF grid (= the scored copy-LF
construction), plus a **local additive corrector of the LF field** that learns
the nested ladder's leading truncation defect, plus a **held-out scalar on/off
switch**.

Three B1 facts set batch 2's agenda (part 7 `next_direction`):

1. **A zero-parameter closed-form filter beats the trained 72k ConvNeXt on 3
   of the 4 datasets it wins** (F6): one shift-invariant transfer function
   `T(k) = sum_n R_hat LF_hat* / sum_n |LF_hat|^2` fitted on 320 train samples
   scores pfc 2.19x, allen_cahn 1.56x, cahn_hilliard 1.07x better than the
   network; the network wins only on `sharp__fisher_kpp_2d` (the one panel
   dataset whose PDE defect involves a local nonlinearity, `u(1-u)`). F7:
   `|T(k)|` rises monotonically to ~1 by band — *the fitted filter is the
   inverse of the bilinear interpolation blur*. F8: it drives pfc's
   beyond-LF-Nyquist band error energy to 5.0e-12 of copy-LF's.
2. **Zero padding holds 45–81% of the trained arm's remaining squared error**
   inside a 12-cell boundary band on periodic datasets (F10), while the
   implicitly-periodic FFT filter shows no such excess.
3. **The trust axis is per-sample, not per-pixel** (F2/F3): an oracle
   per-pixel map is worth <= 4.1% and is *harmful* on cahn_hilliard (+17%),
   whereas an oracle **per-sample** scalar gives helmholtz 0.1623 vs copy-LF
   0.3295 (skill 0.49, on the dataset B1 had to report as a no-op) and pfc
   -22.8%. And B1's stage-2 pixel gate was **structurally blind**: it
   minimized MSE over the *same* `fit_idx` that stage 1 fitted `Delta` on, so
   `g->1` was the correct answer, not a training failure (F4/F5).

## What batch 1's search already covered (do not re-cover)

`websearches/s6_local/batch_1/report.md`: NO-LIDK (ICML 2024) and U-FNO /
LOGLO-FNO establish "parallel local kernels in an FNO" as peer-reviewed prior
art; SpecB-FNO on parameterization bias; The Well's CNextU-Net vs FNO tables;
F-Adapter's opposing prediction (scarce fine-tuning capacity belongs in LOW
bands); Kochkov 2021 learned coarse-grid correction `u = u* + LC(u*)`;
MF-DeepONet fidelity-split subnets; Spectral-Inspired NO at 5 trajectories.
Its D3 verdict was **preempted-but-MF-composition-open**. Batch 2 must not
re-litigate the local-branch mechanism.

Also relevant, already-fetched by siblings (cite, don't re-derive):
`websearches/s1_poisson/batch_2/report.md` verdict (ii) established
Gauss–Richardson Extrapolation as **preempted** for `h^p`-aware scaling, and
`docs/reports/MF_Sharp_HighFreq_Report.md:260` already names *unrolled
deconvolution with a learned prior* (arXiv:2211.01567) — "fit the actual LF<->HF
transfer kernel from training pairs (one FFT pass)". **That in-repo line is the
single biggest novelty threat to the LSI arm and this loop must resolve it.**

## Open questions for this loop

- (a) Is a **data-estimated LSI/Wiener defect filter between nested grids**
  published as a *method or scored baseline* for MF operator benchmarks?
- (b) Is zero-vs-circular padding in CNN PDE surrogates on periodic domains a
  **documented pitfall** (=> hygiene) or an unreported effect (=> reportable)?
- (c) Are **per-sample trust scalars / selective prediction / reject-option
  regression** applied to residual correctors?
- (d) Is **in-sample gate training** ("generalization blindness") a documented
  failure mode in gated-fusion / stacking literature?

## Thresholds this loop must respect

`state/noise_floor.json` per-dataset `min_claimable_effect`: helmholtz
**9.695** (no numeric claim possible), allen_cahn 1.633, pfc 1.151,
cahn_hilliard 0.553, fisher_kpp 0.418, ifc_poisson 0.240. ADR 0009 (no physics
at test time) and ADR 0007 (propose-many/screen-cheap) both bind. Note the
LSI filter uses only paired LF/HF *training* solves and the given LF field at
test time — no governing equations — so it is ADR-0009-clean.
