# Websearch Report — Stream `s3_warp`, Batch 2

**Stream**: `s3_warp`
**Batch**: 2
**Total iterations**: 5 (cap hit — noted in `iteration_5.md`)
**WebSearch calls**: 15 (3 per iteration; a 16th call was rejected by the tool
for a malformed parameter and never executed, noted in `iteration_1.md`)
**WebFetch calls**: 13, of which **8 usable**. Failures, all flagged in-line
where used: `arxiv.org/pdf/2211.16342` (undecodable PDF binary),
`arxiv.org/pdf/2207.01831` and the ECVA PDF (exceeded fetch size limit),
`openreview.net/forum?id=rAfgDXR35CY` (browser-verification page),
`asset.library.wisc.edu/.../file-c2af0.pdf` (unparseable binary, 4.2 MB),
`ncbi.nlm.nih.gov/pmc/articles/PMC9645132/` (cross-host redirect; refetched
successfully at `pmc.ncbi.nlm.nih.gov`).
**Scope**: FOCUSED follow-up. The general warp / MF-fusion landscape was
adjudicated in `websearches/s3_warp/batch_1/report.md` and is not re-surveyed.

## Search trace

### Turn 1 — displacement PARAMETERIZATION and the double-resample fix
Terms: band-limited/Fourier displacement warping; low-dimensional deformation
spaces at few samples; SRWarp/joint upsample+warp. Chosen because B1 F13 (only
the 16×16 rung pays on cahn_hilliard) points at a low-mode parameterization, and
B1 F17 forbids the double resample.
- **Fourier-Net** predicts only a *band-limited Fourier* displacement and decodes
  it with a **parameter-free zero-pad + inverse-DFT decoder**, at 2.2 % of
  TransMorph's parameters and +0.5 % Dice [cite: https://arxiv.org/abs/2211.16342 —
  fetched]. The "low-Fourier-mode displacement head" batch 1 recommended is
  therefore published prior art, usable but not claimable.
- Registration's few-sample answer is a learned low-dimensional deformation
  subspace (PCA/autoencoder SDMs) [cite: https://pubmed.ncbi.nlm.nih.gov/25720017/],
  and there is a dedicated DOF-of-gridded-control-points study [cite:
  https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12919706/].
- **SRWarp** (warp-with-enlargement := spatially varying SR) and **LTEW**
  (Jacobian-modulated local implicit Fourier warping) are the published
  warp⊗upsample compositions [cite:
  https://openaccess.thecvf.com/content/CVPR2021/papers/Son_SRWarp_Generalized_Image_Super-Resolution_under_Arbitrary_Transformation_CVPR_2021_paper.pdf ,
  https://arxiv.org/abs/2207.01831 — fetched]. → `iteration_1.md`

### Turn 2 — pin JUBW; the appearance term; joint vs sequential
- **JUBW pinned** to Makansi, Ilg & Brox 2017: *"common off-the-shelf image
  warping does not allow video super-resolution to benefit much from optical
  flow"* → *"an operation for motion compensation that performs warping from low
  to high resolution directly"* [cite: https://arxiv.org/abs/1707.00471 —
  fetched]. B1 F17's remedy is published, named, and ablated.
- Metamorphosis = geometric deformation + deformation **of the intensity values**
  (which is what lets new structure appear); the known failure is that methods
  *"struggle with balancing appearance vs geometric changes"*; the published
  remedy is Weighted Metamorphosis' time-varying spatial weight on intensity
  additions [cite: https://arxiv.org/pdf/2303.04849 , https://arxiv.org/pdf/2303.09088 ,
  https://arxiv.org/abs/1806.01225 ; Weighted Metamorphosis **snippet-level only**,
  fetch failed]. **No per-term attribution is reported anywhere.**
- Joint vs sequential is ablated in both directions: joint degrades
  [https://arxiv.org/pdf/2510.24734], joint helps [https://arxiv.org/pdf/1909.07623],
  two-stage-with-flow-adapter [https://arxiv.org/html/2603.14920v2], implicit
  alignment [https://arxiv.org/pdf/1905.02716]. → `iteration_2.md`

### Turn 3 — the nearest PDE-side neighbour, the one-sided problem, GT-free validation
- **M2N / UM2N** (learned mesh movement) are the true nearest neighbours on the
  PDE side and both **relocate mesh nodes, never warp a solution field**; M2N
  handles tangling/boundary consistency and beats Monge-Ampère on speed [cite:
  https://arxiv.org/abs/2204.11188 , https://arxiv.org/abs/2407.00382 — both
  fetched]. One variant maps a **monitor function of the coarse solution** to the
  mesh-movement potential — the closest published analogue of D1's input.
- All learned registration is **pairwise** (moving + fixed) [cite:
  https://arxiv.org/pdf/1703.10908 , https://pmc.ncbi.nlm.nih.gov/articles/PMC5731783/];
  one-sided prediction exists only against a *learned template*
  [https://arxiv.org/pdf/2008.07203]. → this is the uncovered slice of D1.
- GT-free validation: **inverse-consistency error** is the published instrument
  [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC3915046/], cycle consistency as
  training objective (CycleMorph) [https://arxiv.org/pdf/2008.05772] and as a UQ
  signal [https://spj.science.org/doi/10.34133/icomputing.0071], with a documented
  failure on **many-to-one** maps [http://proceedings.mlr.press/v130/guo21b/guo21b.pdf]
  — so diagnostic, not loss. → `iteration_3.md`

### Turn 4 — is 0.64 cells even estimable? spectral warp primitive; phase-field metric
- **SuperWarp** (fetched): plain U-Nets are *"jointly tasked with feature
  extraction and matching in addition to deformation estimation, which is not
  handled well by a fully convolutional network"*, worst in **untextured
  regions**; the optical-flow equation *"holds only when displacement magnitudes
  remain less than one voxel"*, hence in-network multi-scale feature warping; and
  **direct supervision on target warps beats self-supervised** (Dice 0.954 vs
  0.906, endpoint error −80 %) [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC9645132/].
  Our 0.64–0.74-cell residual sits **inside** the single-scale validity regime.
- Band-limited resampling at non-grid coordinates is textbook (NUFFT; FFT
  interpolation of periodic band-limited signals from nonuniform samples in a
  regular grid) [cite: https://arxiv.org/pdf/1605.05231 ,
  https://ieeexplore.ieee.org/document/7076647/].
- The phase-field interface-displacement metric (`dphi ≈ |∇phi|·delta`) appeared
  only as an **unsourced snippet** (fetch failed) — must be re-derived in-repo,
  not cited. → `iteration_4.md`

### Turn 5 — adversarial refutation, one search per candidate direction
- MF operator learning: still value-space/weight-transfer; no counterexample
  [https://arxiv.org/pdf/2312.11842 , https://arxiv.org/pdf/2304.06972 ,
  https://iopscience.iop.org/article/10.1088/1755-1315/1333/1/012045].
- The sharpest 2026 coarse→fine paper is `x_HR = up(x_LR) + r` flow matching and
  *"does not address displacement errors, feature misalignment, or registration
  between resolutions"* — and its LF is a **downsample** of HF (60 k pairs), so it
  structurally cannot see a coarse-solve displacement [cite:
  https://arxiv.org/html/2604.00897 — fetched].
- Phase/amplitude **loss** splitting exists (MI2A) but is single-fidelity, has no
  warping, and does **not** attribute the shares [cite:
  https://arxiv.org/abs/2504.11433 — fetched]. → `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **(i)** Narrow **cahn_hilliard-only warp-then-correct** model: a one-sided displacement head predicts a smooth low-mode `phi` from LF + condition, single-interpolation warp of the RAW LF onto the HF node grid, then a small learned correction; comparators = warp-off control, constant-displacement arm, registration-corrected copy-LF sidecar | **preempted-but-MF-composition-open** | Flowers https://arxiv.org/html/2603.04430 (b1) · MetaRegNet https://arxiv.org/pdf/2303.09088 (b1) · Khamlich https://arxiv.org/html/2603.04232v2 (b1) · Fourier-Net https://arxiv.org/abs/2211.16342 · SuperWarp https://pmc.ncbi.nlm.nih.gov/articles/PMC9645132/ · M2N https://arxiv.org/abs/2204.11188 · UM2N https://arxiv.org/abs/2407.00382 · weather-SR flow matching https://arxiv.org/html/2604.00897 | The **one-sided** instance: displacement predicted from the LF PDE field + condition vector with **no target field at inference**, applied to that field before a learned correction, inside an MF operator surrogate at small N_hf. Registration is pairwise; mesh-movement nets output nodes not fields; MF/SR fusion is value-space. Every *component* (band-limited Fourier displacement head, supervised warp targets, single-interpolation warp) is published — the claim is composition + measurement, on ONE dataset (floor 0.553). |
| **(ii)** Single-interpolation warp composition (fuse the warp with the LF→HF upsample; never `grid_sample` an already-interpolated LF) | **preempted (cite)** | JUBW: Makansi/Ilg/Brox https://arxiv.org/abs/1707.00471 (fetched) · SRWarp https://openaccess.thecvf.com/content/CVPR2021/papers/Son_SRWarp_Generalized_Image_Super-Resolution_under_Arbitrary_Transformation_CVPR_2021_paper.pdf · LTEW https://arxiv.org/abs/2207.01831 (fetched) · NUFFT/periodic band-limited resampling https://arxiv.org/pdf/1605.05231 , https://ieeexplore.ieee.org/document/7076647/ | **Nothing.** The 2017 motivation is verbatim B1 F17 ("both operations involve interpolation during which image information is lost"). It is an implementation obligation to cite, never a contribution. |
| **(iii)** The **warp-vs-defect-correction boundary** — what a warp arm owns vs what it delegates to s6's intensity corrector, measured as a per-term attribution | **preempted-but-MF-composition-open** (weak novelty, strong measurement value) | MI2A https://arxiv.org/abs/2504.11433 (fetched; single-fidelity, no warping, no attribution) · Keil & Craig DAS https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf (b1) · MetaRegNet https://arxiv.org/pdf/2303.09088 (b1) · joint-vs-two-stage ablations https://arxiv.org/pdf/2510.24734 , https://arxiv.org/pdf/1909.07623 , https://arxiv.org/html/2603.14920v2 | **No fetched source, in any field, reports a quantitative per-term attribution of a displacement-vs-intensity error split** — and none does it across two fidelities of one PDE solve. Joint-vs-sequential cannot be settled by citation (ablations point both ways) → must be a control arm. |

## Citations summary

- Makansi, Ilg & Brox, "End-to-End Learning of Video Super-Resolution with Motion Compensation" (JUBW) — https://arxiv.org/abs/1707.00471 — **fetched**; used in: iteration_2.md, iteration_5.md
- "Fourier-Net: Fast Image Registration with Band-limited Deformation" — https://arxiv.org/abs/2211.16342 — **fetched** (abs; PDF fetch failed) — used in: iteration_1.md, iteration_5.md
- "Fourier-Net+: Band-Limited Spatial Representation for Efficient 3D Medical Image Registration" — https://arxiv.org/pdf/2307.02997 , https://research.manchester.ac.uk/en/publications/fourier-net-band-limited-spatial-representation-for-efficient-med/ — search result; iteration_1.md
- "Learning Local Implicit Fourier Representation for Image Warping" (LTEW) — https://arxiv.org/abs/2207.01831 — **fetched** (abs; PDF over size limit) — iteration_1.md, iteration_5.md
- Son & Lee, "SRWarp: Generalized Image SR under Arbitrary Transformation" (CVPR 2021) — https://openaccess.thecvf.com/content/CVPR2021/papers/Son_SRWarp_Generalized_Image_Super-Resolution_under_Arbitrary_Transformation_CVPR_2021_paper.pdf , https://arxiv.org/abs/2104.10325v1 — search result; iteration_1.md, iteration_5.md
- "SuperWarp: Supervised Learning and Warping on U-Net for Invariant Subvoxel-Precise Registration" — https://pmc.ncbi.nlm.nih.gov/articles/PMC9645132/ (**fetched**), https://arxiv.org/abs/2205.07399 — iteration_4.md, iteration_5.md
- "M2N: Mesh Movement Networks for PDE Solvers" — https://arxiv.org/abs/2204.11188 — **fetched**; iteration_3.md, iteration_5.md
- "Towards Universal Mesh Movement Networks" (UM2N) — https://arxiv.org/abs/2407.00382 — **fetched**; iteration_3.md, iteration_5.md
- "Super-Resolving Coarse-Resolution Weather Forecasts with Flow Matching" — https://arxiv.org/html/2604.00897 — **fetched**; iteration_5.md
- "MI2A: Predicting Wave Dynamics ... with Physics-Based Loss Decomposition" — https://arxiv.org/abs/2504.11433 — **fetched**; iteration_5.md
- "MetaMorph: Learning Metamorphic Image Transformation With Appearance Changes" — https://arxiv.org/pdf/2303.04849 — search result; iteration_2.md
- "MetaRegNet" — https://arxiv.org/pdf/2303.09088 — batch-1 fetched; iteration_2.md, iteration_5.md
- "Image reconstruction through metamorphosis" — https://arxiv.org/abs/1806.01225 ; "Metamorphic registration, semi-Lagrangian scheme" — https://arxiv.org/pdf/2106.08817 — search results; iteration_2.md
- François et al., "Weighted Metamorphosis for Registration of Images with Different Topologies" — https://www.researchgate.net/publication/361870973_Weighted_Metamorphosis_for_Registration_of_Images_with_Different_Topologies , https://openreview.net/forum?id=rAfgDXR35CY — **fetch failed, snippet-level only**; iteration_2.md
- Quicksilver — https://arxiv.org/pdf/1703.10908 ; similarity-steered CNN regression — https://pmc.ncbi.nlm.nih.gov/articles/PMC5731783/ ; single-view non-rigid registration — https://arxiv.org/pdf/2008.07203 ; pseudomean symmetric registration — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8087477/ — search results; iteration_3.md
- Inverse-consistent symmetric optical flow registration — https://pmc.ncbi.nlm.nih.gov/articles/PMC3915046/ ; inverting dense displacement fields — https://link.springer.com/content/pdf/10.1007/978-3-540-75757-3_109.pdf ; CycleMorph — https://arxiv.org/pdf/2008.05772 ; cycle-consistency UQ — https://spj.science.org/doi/10.34133/icomputing.0071 ; "Fork or Fail" many-to-one failure — http://proceedings.mlr.press/v130/guo21b/guo21b.pdf — search results; iteration_3.md
- Registration regularization review — https://arxiv.org/pdf/2412.15740 ; DOF of gridded control points — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12919706/ ; statistical deformation models — https://pubmed.ncbi.nlm.nih.gov/25720017/ , https://pmc.ncbi.nlm.nih.gov/articles/PMC8802338/ , https://arxiv.org/pdf/1804.07172 — search results; iteration_1.md, iteration_4.md
- NUFFT in CT — https://arxiv.org/pdf/1605.05231 ; non-iterative type 4/5 NUFFT — https://arxiv.org/pdf/1604.06236 ; FFT interpolation from nonuniform samples in a regular grid — https://ieeexplore.ieee.org/document/7076647/ , https://dl.acm.org/doi/10.1109/TSP.2015.2419178 ; ENUFFT orography — https://arxiv.org/pdf/2606.21278 — search results; iteration_4.md
- Joint-vs-two-stage ablations: DrivingScene — https://arxiv.org/pdf/2510.24734 ; ToF alignment+refinement — https://arxiv.org/pdf/1909.07623 ; F2HDR — https://arxiv.org/html/2603.14920v2 ; Merging-ISP — https://arxiv.org/pdf/1911.04762 ; EDVR — https://arxiv.org/pdf/1905.02716 — search results; iteration_2.md, iteration_5.md
- MF operator learning refutation set: super-fidelity warm start — https://arxiv.org/pdf/2312.11842 ; MF DeepONet tunnel-lining displacement — https://iopscience.iop.org/article/10.1088/1755-1315/1333/1/012045 ; FNO MF transfer learning — https://arxiv.org/pdf/2304.06972 ; residual-augmented flow-matching operators — https://arxiv.org/pdf/2512.12749 — search results; iteration_5.md
- Fluid SR (value-space) — https://arxiv.org/pdf/2301.10937 , https://arxiv.org/pdf/2108.07667 , https://www.alcf.anl.gov/science/case-studies/mesh-based-super-resolution-fluid-flows-multiscale-graph-neural-networks ; optical-flow VSR resampling module — https://www.sciencedirect.com/science/article/abs/pii/S0045790625001193 — search results; iteration_5.md
- Coarse-interface alternatives (AMR, not ML) — https://arxiv.org/pdf/2510.21749 , https://arxiv.org/abs/2607.25142 , https://www.sciencedirect.com/science/article/pii/S0045782526001295 ; phase-field ML dynamics — https://arxiv.org/pdf/2203.16692 , https://arxiv.org/pdf/2407.20126 — search results; iteration_4.md

## Dead ends

- `machine learning correct interface position error coarse grid phase-field ... Cahn-Hilliard` → nobody corrects interface *position* on a coarse phase-field solve with ML; the field answers with adaptive mesh refinement. Nothing to cite for the mechanism.
- The phase-field interface-displacement metric (`phi=0.5` isoline displaced by `delta`, mean-squared interface displacement) → right object, **unsourceable** here (Wisconsin PDF fetch returned binary). Re-derive in-repo; do not cite.
- `Weighted Metamorphosis` per-term attribution → OpenReview served a verification page, ResearchGate not fetched. Snippet-level only; the attribution claim rests on the ABSENCE of evidence, which is stated as such.
- `low-dimensional spectral parameterization ... few training samples` → returns medical statistical deformation models (PCA/autoencoder subspaces); useful as parents, but nothing about PDE fidelity ladders.
- `error decomposition displacement vs amplitude ... division of labor` → mostly patents and signal-processing; only MI2A and Keil & Craig are on-topic.

## For the brainstormer

**You MUST quote the verdict for whatever you propose.** Usable phrasings:
for the model, *"(i) preempted-but-MF-composition-open — Flowers
(arXiv:2603.04430) publishes learned warping in a single-fidelity neural PDE
solver, MetaRegNet (arXiv:2303.09088) publishes warp+appearance, Khamlich
(arXiv:2603.04232) publishes classical-OT MF correction on Allen–Cahn,
Fourier-Net (arXiv:2211.16342) publishes the band-limited Fourier displacement
head, SuperWarp (PMC9645132) publishes supervised subvoxel warp estimation, and
M2N/UM2N (arXiv:2204.11188 / 2407.00382) publish learned coordinate relocation
from a coarse solution — what is open is the ONE-SIDED instance: displacement
predicted from the LF field + condition with no target at inference, applied to
that field before a learned correction, in an MF surrogate at small N_hf"*; for
the warp implementation, *"(ii) preempted (cite) — JUBW, arXiv:1707.00471"*.

1. **The single-interpolation warp is settled and cited: JUBW (arXiv:1707.00471).**
   B1 F17 is not a discovery to defend, it is a 2017 result to comply with. Warp
   the RAW LF once onto the HF node grid (or exact-Fourier-shift for the constant
   arm, as B1 F16 already did). JUBW's extra trick — emit the sub-cell offsets as
   input channels and let the network do the interpolation — is a free, cited
   design option worth considering over bilinear `grid_sample`.
2. **Parameterize the displacement band-limited, and cite Fourier-Net.** A low-mode
   Fourier `phi` with a zero-pad + iFFT decode is *published, parameter-free on the
   decode side, and reported accuracy-neutral at 2.2 % of the parameters*
   (arXiv:2211.16342). It also matches the FNO stack and B1 F13's finding that
   only the C16 rung pays on cahn_hilliard. Do NOT free-form the field.
3. **You are inside the sub-cell regime, so skip the pyramid — but not the
   architecture fix.** SuperWarp: the optical-flow equation is valid only below
   one voxel of displacement, and our residual is 0.64–0.74 cells (B1 F11), so a
   single-scale head is theoretically admissible; but SuperWarp also says a plain
   U-Net head entangles feature matching with deformation estimation and fails in
   **untextured regions** — which on cahn_hilliard is the bulk, i.e. most of the
   field. Constrain `phi` (band-limited + smoothness) rather than trusting a
   fully-convolutional head to behave in the bulk.
4. **Strongly consider direct displacement supervision.** SuperWarp reports
   supervised-warp training beating self-supervised similarity training
   (endpoint error −80 %). We CAN do this legally: B1's own warp fitter produces
   oracle `phi` on the TRAIN split (HF is available at train time; no physics, so
   ADR 0009-safe), giving a two-term loss = nRMSE + displacement-regression. B1
   leg D's nearest-neighbour retrieval is the zero-parameter ablation of the same
   idea and belongs in the same card as a comparator.
5. **Do not add a metamorphosis intensity channel; scope instead.** The
   metamorphosis literature's own verdict is that appearance-vs-geometry balancing
   is unsolved and the intensity channel steals work from the diffeomorphism
   (iteration 2); with 5–6 % topology mismatch on cahn_hilliard (B1 leg C), B1's
   scoping decision is the defensible one. Delegate the intensity/amplitude term
   to s6's corrector (whose measured ceiling there is skill 0.44, B1 F14/F18) and
   let the warp arm own only the coordinate term. Joint-vs-sequential has no
   citable verdict — make it a control arm, not an assumption.
6. **Add inverse-consistency error as a free diagnostic, never as a loss.**
   E_IC (PMC3915046) validates a displacement with no displacement ground truth;
   cycle-consistent *training* is documented to fail on many-to-one maps
   (Guo et al. 2021), and LF→HF with topology loss is many-to-one.
7. **Frame the deliverable as an attribution, not a mechanism.** The least-preempted
   thing available is the measured answer to "how much of cahn_hilliard's
   registration-corrected residual can a ONE-SIDED predicted displacement remove?"
   against three published-in-repo yardsticks: oracle ceiling 83–85 %, constant-DC
   arm 48.9 %, LSI/intensity arm skill 0.44 — with `min_claimable_effect` 0.553 on
   cahn_hilliard and helmholtz report-only (floor 9.695). Also note the standing
   confound: the champion never consumes LF at test time, so any win must be read
   against the warp-off control, not the champion. And: the 2026 SOTA coarse→fine
   comparator (arXiv:2604.00897) builds its LF by downsampling HF — a construction
   our repo law forbids and which structurally cannot exhibit the displacement we
   are targeting; that is a usable argument for why this gap is still open.
