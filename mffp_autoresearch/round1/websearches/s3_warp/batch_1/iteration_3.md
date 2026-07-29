# Iteration 3 — the diffuse-interface MF-OT paper; topology mismatch; displacement metrics

## Search rationale

Three jobs, one per assigned coverage area. (a) Kill or confirm the sharpest
remaining preemption candidate found in iteration 2 — arXiv:2603.04232, the
only paper found that is simultaneously multi-fidelity, transport-geometric,
and on a **diffuse-interface** system (the Cahn–Hilliard/Allen-Cahn family
that dominates our panel). (c) The topology-mismatch problem that program.md
§12.3 demands a design answer for: what does the published warping literature
do when a warp provably *cannot* represent the change? (b) Displacement /
amplitude decomposition metrics, so the brainstormer can propose a diagnostic
whose falsification clause is measurable rather than rhetorical.

## Search terms used

1. (fetch of the iteration-2 lead) `arXiv:2603.04232` — MF + OT + diffuse interface
2. `image registration topology change component splitting merging deformable warping cannot handle appearing disappearing structures metamorphosis`
3. `displacement amplitude error decomposition metric sharp interface prediction optical flow score forecast verification neural PDE surrogate`

## Findings

### Term 1 — arXiv:2603.04232 (Khamlich et al.), FETCHED (https://arxiv.org/html/2603.04232v2)

"A Multi-Fidelity and Parametric Reduced-Order Modeling Framework with Optimal
Transport-based Interpolation: Applications to Diffused-Interface Two-Phase
Flows". The fetch establishes, precisely:

- **MF structure**: residual-based. It forms `r(t) = u_HF(t) − u_LF(t)` and
  applies **optimal-transport displacement interpolation to those residual
  fields across time / parameters**, then `u_approx(t*) = u_LF(t*) +
  r_interp(t*)`. So the correction is still **additive in value space**; OT is
  used to *interpolate residuals between snapshots*, not to warp the LF field
  onto the HF field.
- **Is a displacement map computed between LF and HF fields?** Per the fetch:
  transport maps are computed between low- and high-fidelity **residual**
  fields, with the signed residual split into `r⁺`/`r⁻` and each interpolated
  by entropic-regularized OT before recombination.
- **No neural networks at all** — "purely geometric/classical OT-based"; and
  the authors deliberately omit an optional POD correction step to evaluate
  "plain displacement interpolation".
- **Physics/resolutions**: conservative **Allen–Cahn** inside a five-equation
  compressible two-phase model; Rider–Kothe vortex and Rayleigh–Taylor; grids
  128²–512²; MF pairs (128²→256²), (256²→512²) — i.e. **the same resolution
  ladder and nearly the same equation as our panel**.
- **Topology**: "does not explicitly discuss topology change handling"; both
  benchmarks preserve interface connectivity.

Assessment: this is the true nearest neighbor. It preempts the *framing*
("transport geometry is the right tool for LF→HF correction on diffuse
interfaces") but not the *mechanism* (no learned displacement field, no warp
of the LF field itself, no correction net on a warped field, no operator
learning, no few-shot HF regime).

### Term 2 — topology change: what the literature actually does

The answer is a named family: **metamorphosis** = diffeomorphic warp **plus**
an intensity/source term.

- **MetaRegNet**, https://arxiv.org/pdf/2303.09088 — **fetched**: metamorphic
  registration decomposes the transform into (1) a diffeomorphic spatial
  deformation, parameterized by **velocity fields integrated over time** and
  regularized for smoothness/invertibility, and (2) an **appearance/source
  component** that "captures intensity changes, appearance variations, and
  topology modifications ... what cannot be explained by spatial warping
  alone". Explicit statement of why a pure warp fails: diffeomorphic warps are
  homeomorphisms and "cannot represent [appearance/vanishing/topology change]
  without violating smoothness and invertibility constraints". Regularization
  balances warp smoothness, data fidelity, and **parsimony of the appearance
  term**.
- **MetaMorph**, https://arxiv.org/pdf/2303.04849 — learning metamorphic
  transformation with appearance changes (metamorphic autoencoders /
  ResNets).
- **TopAwaRe: Topology-Aware Registration**,
  https://link.springer.com/content/pdf/10.1007/978-3-030-32245-8_41 ;
  registration of images with topological change via Riemannian embedding
  (ResearchGate 221625380); topology-preserving non-rigid registration,
  https://www.sciencedirect.com/science/article/abs/pii/S0031320310000452 ;
  learned-regularization review, https://arxiv.org/pdf/2412.15740.

**Design consequence, and it is uncomfortable for the stream's novelty
story**: "smooth warp + additive correction that absorbs what the warp cannot
express, with the correction penalized for magnitude" *is* the metamorphosis
formulation. Candidate D's architecture is structurally metamorphic
registration; what is unpublished is its use across fidelities of a PDE solve.

### Term 3 — displacement/amplitude metrics

- **Keil & Craig, "A Displacement and Amplitude Score Employing an Optical
  Flow Technique", Wea. Forecasting 24(5), 2009**,
  https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf —
  verified primary source (the repo report cited it unverified). The
  construction is exactly the diagnostic we need: an optical-flow field
  deforms the forecast onto the observation; the **displacement vector
  magnitude** is the position error and **the difference between observation
  and the morphed forecast** is the amplitude error. Directly transplantable
  as `DIS(copy-LF → HF)` vs `DIS(model → HF)` on our panel.
- Scale-aware evaluation guidance for PDE surrogates: band-limited errors,
  H¹/H² norms, https://arxiv.org/pdf/2604.20061 ; TRIE stochastic-PDE
  surrogate evaluation, https://arxiv.org/html/2607.00196v1.
- No result found that reports a displacement/amplitude split for a
  **multi-fidelity** surrogate — the measurement itself appears unmade in this
  setting, which makes it cheap, safe stream-batch-1 material.

## Interpretation

The mechanism's *ingredients* are all published — OT/transport for MF
diffuse-interface correction (2603.04232), warp-plus-appearance-term for
topology change (MetaRegNet/MetaMorph), displacement/amplitude scoring (Keil &
Craig 2009) — but no fetched source composes a **learned displacement field
predicted from an LF PDE field and applied to it before a learned residual
correction**. The honest emerging verdict is "not preempted as a composition,
but every component has a named published parent", which is materially weaker
than NEW_MODELS.md §8.4's "documented gap".
