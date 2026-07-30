# iteration_5 — MANDATORY adversarial prior-art verdicts (cap: 5/5 iterations used)

**Cap note**: this is iteration 5 of 5. No further iterations are permitted.

## Search rationale

One refutation search per candidate direction, each written to try to KILL the
direction rather than support it: (i) the narrow cahn_hilliard warp-then-correct
model, (ii) the single-interpolation warp composition, (iii) the
warp-vs-defect-correction boundary / per-term attribution.

## Search terms used

1. `2026 learned displacement field maps low-fidelity simulation field into alignment with high-fidelity solution neural operator few high-fidelity samples`  (attacks (i))
2. `flow-based warping coarse simulation to fine grid scientific super-resolution single resampling directly from coarse field`  (attacks (i) and (ii) from the SR side)
3. `error decomposition displacement component versus amplitude component learned correction division of labor alignment module ablation contribution`  (attacks (iii))

## Findings

### Term 1 — no counterexample; MF operator learning stays value-space

Everything returned maps LF values to HF values or transfers weights: neural
operator "super-fidelity" warm starts [cite: https://arxiv.org/pdf/2312.11842],
multifidelity DeepONet for tunnel-lining **displacement fields** — note this is
displacement as the PDE's *solution variable* (structural mechanics), not a
coordinate warp of a field [cite:
https://iopscience.iop.org/article/10.1088/1755-1315/1333/1/012045], FNO
transfer-learning MF for flow/temperature [cite:
https://arxiv.org/pdf/2304.06972], residual-augmented flow-matching operators
[cite: https://arxiv.org/pdf/2512.12749]. All search-result level; none is a
counterexample and none needed fetching to see that.

### Term 2 — the closest 2026 work is explicitly value-space, and its LF is a downsample

**Super-Resolving Coarse-Resolution Weather Forecasts with Flow Matching**
(fetched) is the sharpest recent LF→HF paper and it refutes itself as a
preemption: the formulation is exactly `x_HR = up(x_LR) + r`, learning
`p(r | up(x_LR))` by flow matching; it *"does not address displacement errors,
feature misalignment, or registration between resolutions"*, and it trains on
~60 000 paired states built by **regridding 0.25° ERA5 down to 1.5°**
[cite: https://arxiv.org/html/2604.00897 — fetched]. Two adversarial notes for
the brainstormer: (a) this is the value-space default the whole field keeps
choosing, so D1's premise is at least not crowded; (b) its LF is a *downsample*,
which our repo law forbids — a downsampled LF has no coarse-solve transport
error, so that literature would not see a displacement even if one existed. Fluid
SR is the same story (patch-wise value-space GNN/CNN, survey level) [cite:
https://arxiv.org/pdf/2301.10937 , https://arxiv.org/pdf/2108.07667 ,
https://www.alcf.anl.gov/science/case-studies/mesh-based-super-resolution-fluid-flows-multiscale-graph-neural-networks].
The one optical-flow-plus-resampling hit is video SR with a "resampling
deformable convolution module" [cite:
https://www.sciencedirect.com/science/article/abs/pii/S0045790625001193 — search
result, paywalled, not fetched].

### Term 3 — phase/amplitude splitting exists as a LOSS, single-fidelity, with no attribution

**MI2A** (arXiv:2504.11433, fetched abstract) introduces *"a novel loss
decomposition strategy that explicitly separates the training loss function into
distinct phase and amplitude components"* for autoregressive latent ROMs
(denoising CAE + LSTM-attention) on 1-D convection, viscous Burgers and 2-D
Saint-Venant. Fetched verdict on the two things that matter: it is
**single-fidelity**, it involves **no spatial warping**, and it *"does not
explicitly attribute error sources to phase versus amplitude"* — it mitigates
both without quantifying their shares [cite: https://arxiv.org/abs/2504.11433 —
fetched]. Combined with iteration 2's finding that the metamorphosis literature
acknowledges appearance-vs-geometry balancing as an OPEN problem and reports no
per-term attribution, and with batch 1's Keil & Craig DAS (a verification score,
not a model decomposition) [cite:
https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf], the
conclusion is that **no fetched source reports a quantitative per-term
attribution of a displacement-vs-intensity error split**, in any fidelity
setting.

## PRIOR-ART VERDICTS

### (i) The narrow cahn_hilliard warp-then-correct instance — `preempted-but-MF-composition-open`

Every *component* is published; the composition and the setting are not.
- Published and NOT claimable: learned warping as a neural-PDE primitive
  (Flowers, single-fidelity, no LF→HF map) [cite:
  https://arxiv.org/html/2603.04430 — fetched in batch 1]; warp+intensity as
  metamorphosis [cite: https://arxiv.org/pdf/2303.09088 — fetched in batch 1];
  transport geometry for MF diffuse-interface correction on conservative
  Allen-Cahn at 128²-512², classical OT on residual fields [cite:
  https://arxiv.org/html/2603.04232v2 — fetched in batch 1]; band-limited
  Fourier displacement heads with a parameter-free zero-pad+iFFT decoder
  [cite: https://arxiv.org/abs/2211.16342 — fetched]; subvoxel-precise
  displacement estimation with direct warp supervision and in-network feature
  warping [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC9645132/ — fetched];
  learned coordinate relocation driven by a coarse solution's monitor function
  [cite: https://arxiv.org/abs/2204.11188 , https://arxiv.org/abs/2407.00382 —
  both fetched].
- **What remains open, stated as narrowly as the evidence supports**: a
  **one-sided** displacement — predicted from the LF PDE field plus the condition
  vector ALONE, with no target field at inference — applied to that LF field
  before a learned correction, inside a multi-fidelity operator surrogate at
  small N_hf. Registration (Quicksilver, SuperWarp, MetaRegNet, CycleMorph) is
  pairwise by construction [cite: https://arxiv.org/pdf/1703.10908 ,
  https://pmc.ncbi.nlm.nih.gov/articles/PMC9645132/ ,
  https://arxiv.org/pdf/2008.05772]; learned mesh movement has no target field
  but outputs **nodes, not a warped solution field** (fetched, both papers); MF
  operator learning and 2026 coarse→fine generative SR are value-space
  (fetched: https://arxiv.org/html/2604.00897 , https://arxiv.org/html/2605.16118v1).
- **Adversarial caveats the card must carry**: the claim is a *composition +
  measurement*, not a new primitive, and the honest phrasing is "first
  measurement of one-sided cross-fidelity field warping", not "new mechanism";
  it is licensed on ONE dataset (cahn_hilliard, floor `min_claimable_effect`
  0.553), and single-dataset composition claims are how this project went
  0-for-4 (program.md §13.3).

### (ii) Single-interpolation warp composition — `preempted (cite)`

**Fully preempted, with the same motivating argument as B1 F17.**
`JUBW` (Joint Upsampling and Backward Warping) in Makansi, Ilg & Brox,
*End-to-End Learning of Video Super-Resolution with Motion Compensation* (2017):
fetched abstract states *"common off-the-shelf image warping does not allow video
super-resolution to benefit much from optical flow"* and proposes *"an operation
for motion compensation that performs warping from low to high resolution
directly"* [cite: https://arxiv.org/abs/1707.00471 — fetched]. Snippet-level
(flagged, iteration 2): JUBW rounds to the nearest LF source pixel with **no
interpolation** and emits sub-pixel offsets as extra channels, motivated by
*"first upsampling and then warping ... both operations involve interpolation
during which image information is lost"*. Later relatives: SRWarp
(warp-with-enlargement := spatially varying SR) [cite:
https://openaccess.thecvf.com/content/CVPR2021/papers/Son_SRWarp_Generalized_Image_Super-Resolution_under_Arbitrary_Transformation_CVPR_2021_paper.pdf]
and LTEW (Jacobian-modulated local implicit Fourier warping) [cite:
https://arxiv.org/abs/2207.01831 — fetched]. The periodic band-limited
resampling machinery is textbook signal processing [cite:
https://ieeexplore.ieee.org/document/7076647/ , https://arxiv.org/pdf/1605.05231].
**Nothing remains open.** Use it, cite JUBW, and never present it as a
contribution — it is the *implementation obligation* B1 F17 imposes.

### (iii) The warp-vs-defect-correction boundary (what s3 owns vs delegates to s6) — `preempted-but-MF-composition-open`, weak novelty, strong measurement value

- Published: the displacement/amplitude error split as a verification score
  (Keil & Craig DAS, batch 1); phase-vs-amplitude **loss** decomposition in a
  single-fidelity autoregressive ROM with no warping [cite:
  https://arxiv.org/abs/2504.11433 — fetched]; geometry-vs-appearance splitting
  as metamorphosis, with the balance acknowledged as an open problem and the
  published remedy being a spatial weight on the intensity term (Weighted
  Metamorphosis — snippet-level, iteration 2, NOT citation-grade); two-stage vs
  joint training ablated in both directions in video/HDR/RGB-D pipelines [cite:
  https://arxiv.org/pdf/2510.24734 (joint degrades),
  https://arxiv.org/pdf/1909.07623 (joint helps),
  https://arxiv.org/html/2603.14920v2 (two-stage with a flow adapter),
  https://arxiv.org/pdf/1905.02716 (implicit alignment, no flow)].
- **Open**: no fetched source, in any field, reports a **quantitative per-term
  attribution** of how much error the displacement term owns vs the
  intensity/appearance term — and none does it across two fidelities of one PDE
  solve. In our setting the attribution is already half-measured in-repo (B1 F14
  + F18: the s6 LSI filter's ceiling on cahn_hilliard is skill 0.44, the oracle
  warp's residual ceiling is 83-85 %), which makes the *measurement* cheap and
  the *claim* modest.
- **Boundary recommendation, decided from the evidence**: s3 owns the
  **coordinate** term (a smooth, low-mode, one-sided displacement); s6 owns the
  **intensity** term (local/LSI amplitude repair). Do not add a metamorphosis
  intensity channel to the warp arm — the literature's own verdict is that the
  intensity channel steals work from the diffeomorphism, and B1's leg-C numbers
  (5-6 % topology mismatch) mean scoping is sufficient. Joint vs sequential
  cannot be settled by citation (the ablations point both ways), so it must be a
  control arm; the cheapest published pattern is a differentiable single-
  interpolation warp trained jointly with a small corrector, with the
  displacement head additionally given a **direct displacement target** from an
  oracle fit on the TRAIN split (SuperWarp's supervised-warp result, fetched).

## Interpretation

Two of the three directions are honestly preempted at the mechanism level and one
(the one-sided cross-fidelity warp) survives as a composition-plus-measurement
claim. The strongest, least-preempted deliverable in this batch is therefore not
"a new warp mechanism" but a **measured attribution** — how much of
cahn_hilliard's registration-corrected residual a one-sided predicted
displacement can actually remove, versus the oracle ceiling (83-85 %), the
constant-displacement arm (48.9 %), and the LSI/intensity arm (skill 0.44).
