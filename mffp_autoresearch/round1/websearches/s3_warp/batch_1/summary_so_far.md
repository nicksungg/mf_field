# Summary so far — stream `s3_warp`, batch 1

## Stream provenance (why this stream exists)

`s3_warp` replaced `s3_testtime` on 2026-07-29 by operator direction
(`docs/adr/0010-s3-replacement.md`), which followed
`docs/adr/0009-unknown-physics-constraint.md`: no candidate MODEL may require
the governing equations at test time. The retired stream's own B1 evidence
(true residual computable on 1/6 panel datasets; where computable the dataset
is two-FFT-solvable; the 1-dof residual rescale collapses copy-LF 0.33 →
0.996) is the recorded dead end. **There are no prior s3_warp cards, anchors,
or websearches** — this is the stream's first pipeline agent.

## The stream question (program.md §12.3)

*Does geometric alignment (warp-then-correct) beat additive correction on
sharp-interface MF fusion?* Mechanism prior: coarse LF solves *displace* sharp
interfaces; rel-L2 double-penalizes displacement (error at both the true and
predicted interface); an additive corrector must erase-and-redraw the feature,
which MSE blurs. A smooth displacement field warping LF into alignment, plus a
small correction net on the warped LF, *moves* the feature instead.

## What the numbers say (certified, batch 0)

- Anchor for this stream = champion panel geomean, carried over from
  `state/anchors/s3_testtime.json`: `mf_fno_transfer_film`, **6.703**
  (CI95 6.219–7.102), 6 panel datasets, `provisional: false`.
- `state/noise_floor.json` `min_claimable_effect`: helmholtz **9.695**
  (i.e. NO numeric claim is defensible on helmholtz — floor exceeds the
  anchor's own dataset skill), allen_cahn 1.633, pfc 1.151, cahn_hilliard
  0.553, fisher_kpp 0.418, ifc_poisson 0.240.
- Certified best skills (all ≫ 1, i.e. every family loses to copy-LF):
  allen_cahn 16.33, pfc 11.51, helmholtz 13.82, cahn_hilliard 5.53,
  fisher_kpp 4.18 (`state/anchors/s2_beyond_copy.json`).
- Context from the orchestrator: the certified champion **never consumes the
  LF field at test time** — so "warp the LF" is not merely a better corrector,
  it is a change in what information reaches the output at all. Any warp win
  must be disentangled from a plain "use LF at test time" win. That confound
  is the single biggest internal-validity threat for this stream.

## In-repo prior scans to cite rather than re-derive

- `docs/reports/MF_Sharp_HighFreq_Report.md` (2026-07-02) is the origin of the
  P3 flagship `mf_warp_correct`, and already assembles the alignment-before-
  correction arrow across meteorology (Hoffman 1995; Keil & Craig DAS 2009;
  Ravela field-alignment DA 2007), seismic FWI (Engquist & Yang W2), statistics
  (elastic Bayesian calibration, arXiv:2305.08834), registration ROMs (Nair &
  Balajewicz arXiv:1712.09144; Gowrachari arXiv:2501.01299), deep MF GP input
  warping (Raissi & Karniadakis arXiv:1604.07484), shift-mechanism operator
  learning (arXiv:2210.01074), and — the closest listed relative — OT
  displacement-interpolation MF ROMs on **diffuse-interface two-phase flow**
  (Khamlich et al. arXiv:2603.04232, 2026), i.e. near-Cahn–Hilliard.
- `docs/proposals/NEW_MODELS.md` §8 (Candidate D) claims "**No published
  multi-fidelity operator method predicts an inter-fidelity displacement field
  and warps before correcting**" but flags its own anchors as **reproduced
  unverified**. Program.md §13.3: the project is **0-for-4** on novelty claims.
  Re-verifying that claim adversarially is this batch's core job.

## Open questions this batch must answer

1. Is warp-before-correct published for **multi-fidelity PDE surrogate
   fusion** (as opposed to video SR / medical registration / ROM)?
2. Do displacement/interface-aware metrics and losses exist off-the-shelf?
3. How do published methods handle **topology mismatch** — a diffeomorphic
   warp cannot change component counts, but phase-field coarsening does?
4. Diffeomorphic vs free-form displacement parameterizations at 64²–256² with
   N_hf = 5–25: what is known to train in that data regime?
