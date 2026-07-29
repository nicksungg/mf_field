# Iteration 2 — resolving the "multi-fidelity registration" thread; learned-shift operators

## Search rationale

Iteration 1 left exactly one live preemption thread: registration ROMs that
also say "multi-fidelity". Term 1 chases it into the Taddei registration-ROM
line. Term 2 tests the other heavily-published preemption vector named in
program.md §12.3 — deformable registration / coarse-to-fine displacement
prediction in medical imaging and weather downscaling — to establish how close
the *nearest published warp-predictor* is to a PDE-fusion setting. Term 3
verifies (rather than recalls) the shift-mechanism operator-learning anchor
that `MF_Sharp_HighFreq_Report.md` cites unverified as arXiv:2210.01074,
because a learned shift inside an operator is the mechanism closest to a warp.

## Search terms used

1. `Taddei registration model reduction multi-fidelity mapping low-fidelity snapshots construct registration parameterized mapping`
2. `deformable registration deep learning coarse-to-fine simulation upscaling weather forecast field alignment neural network displacement correction`
3. `arXiv 2210.01074 shift-DeepONet transport operator learning discontinuous shock shifting neural operator`

## Findings

### Term 1 — MF inside registration ROM

- **Multi-fidelity reduced-order surrogate modelling**, arXiv:2309.00325 /
  Proc. R. Soc. A 480:20230655, https://arxiv.org/abs/2309.00325 —
  **fetched**. Verdict from the fetch: "Registration is **only applied among
  high-fidelity snapshots** ... no warping between fidelity levels occurs";
  the MF part is "a **coefficient-space mapping via LSTM**, not a spatial
  warping/registration between solution fields" (POD basis from HF snapshots;
  LF and HF both projected; MF-LSTM maps LF coefficients → HF coefficients).
  **This clears the biggest single threat**: the best-named "MF +
  registration" paper does NOT register LF to HF.
- Registration-based MOR of 2-D conservation laws,
  https://www.sciencedirect.com/science/article/abs/pii/S0021999122001309 and
  spatio-parameter-adaptive version,
  https://www.sciencedirect.com/science/article/abs/pii/S0021999123008227 —
  the "multi-fidelity" phrase in these is about using cheap solves to reduce
  the **offline cost of building the mapping Φ**, i.e. MF-for-registration.
  Abstract pages are paywalled (no fetch); treated as unresolved-but-adjacent
  rather than as a citation.
- `klein2025multifidelitylearningreducedorder` (the lead pulled from the
  transport-ROM review's bibliography) resolves to **Multi-fidelity Learning
  of Reduced Order Models for Parabolic PDE Constrained Optimization**,
  https://arxiv.org/abs/2503.21252 — hierarchical ROM/trust-region with a
  posteriori error estimators. **No registration, no warping.** Thread closed.
- New lead surfaced, and it is the sharpest one yet: **A Multi-Fidelity and
  Parametric Reduced-Order Modeling Framework with Optimal Transport-based
  Interpolation: Applications to Diffused-Interface Two-Phase Flows**,
  https://arxiv.org/html/2603.04232v2 — MF + OT + *diffuse-interface* (the
  Cahn–Hilliard-adjacent setting). Deferred to iteration 3 for a full fetch.

### Term 2 — the heavily-published warp literature (preemption vector)

Confirms program.md §12.3's warning that this vector is crowded, and shows it
is crowded **outside** MF PDE fusion:

- Correlation-aware coarse-to-fine MLPs for deformable medical registration,
  CVPR 2024, https://openaccess.thecvf.com/content/CVPR2024/papers/Meng_Correlation-aware_Coarse-to-fine_MLPs_for_Deformable_Medical_Image_Registration_CVPR_2024_paper.pdf
- Successive-next-network regularization for deformable brain MR registration,
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10058981/ ; cascaded fetal
  brain MRI registration, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11732682/
  — the standard cascade is "affine, then several CNNs predicting coarse then
  fine B-spline deformation fields", i.e. coarse-to-fine in *deformation
  resolution*, not in *solver fidelity*.
- Weather side: SR-Weather super-resolution downscaling to 1 km,
  https://www.nature.com/articles/s41612-026-01328-5 — value-space SR from
  coarse 0.25° forecasts, **no displacement field**; deformable-convolution
  weather-regime forecasting,
  https://www.nature.com/articles/s41598-022-12167-8 — deformable *kernels*
  (learned sampling offsets inside a conv layer), not a field-level warp of a
  low-fidelity solution.
  No usable result applying deformable registration between two *fidelities of
  the same PDE solve*.

### Term 3 — learned shifts inside operators

- **Nonlinear Reconstruction for Operator Learning of PDEs with
  Discontinuities**, https://arxiv.org/pdf/2210.01074 (OpenReview
  https://openreview.net/forum?id=CrfhZAsJDsZ) — proves linear-reconstruction
  operators (DeepONet, PCA-Net) cannot efficiently approximate discontinuous
  solution operators, while nonlinear reconstruction (FNO, **shift-DeepONet**)
  can; shift-DeepONet is "significantly more accurate than DeepONet, with at
  least a two-fold gain". **Fetch attempt on the PDF returned only PDF
  structural metadata — the shift-DeepONet definition could NOT be read**, so
  the precise question (spatially-varying displacement applied by warping vs
  per-basis-function shift/scale parameters) is unresolved and is carried into
  the verdict as a caveat. What IS established from the abstract-level result:
  the shift mechanism there maps an *input function* (e.g. initial condition)
  to the solution — **not** a low-fidelity solution field to a high-fidelity
  one; there is no MF component.
- Adjacent discontinuity-capturing operators found but not fetched:
  φ-DeepONet https://arxiv.org/abs/2604.08076 ; Shearlet neural operators
  https://arxiv.org/html/2604.25181 ; shock-aware Fusion-DeepONet
  https://arxiv.org/html/2510.17887v1 — all single-fidelity representation
  fixes, useful as "nearest neighbor" context.

## Interpretation

The "MF + registration" threat collapses on inspection: the one paper that
names both registers HF-to-HF and fuses fidelities in POD-coefficient space
(arXiv:2309.00325), and the ROM line's MF usage is about cheapening the
offline mapping construction. The learned-warp literature is dense but lives
in imaging/weather SR where the two fields are not two fidelities of one
solve. One unresolved sharp threat remains — arXiv:2603.04232 (MF + OT +
diffuse interface) — plus one unread definition (shift-DeepONet).
