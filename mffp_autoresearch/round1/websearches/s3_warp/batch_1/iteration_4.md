# Iteration 4 — learned warps inside PDE nets, the physical premise, and small-data parameterization

## Search rationale

Iteration 3 left the composition unpreempted but every ingredient parented. So
iteration 4 attacks the last two ways the claim can die and one way the
*premise* can die. (i) Is there now a neural-PDE architecture whose primitive
IS warping? (this is the fastest-moving area and the one where 2026 papers
could preempt outright). (ii) Does coarse-grid phase-field solving actually
produce interface **position** error — if the LF error is amplitude/width only,
the whole warp mechanism is misdirected and the stream should know that before
the brainstormer designs anything. (iii) Assigned coverage (d): diffeomorphic
vs free-form displacement parameterization in a small-data regime.

## Search terms used

1. `spatial transformer network inside neural PDE surrogate learned warping module advection displacement prediction video prediction fluid`
2. `coarse grid phase-field simulation interface position error spurious velocity Allen-Cahn Cahn-Hilliard grid resolution shifts front location`
3. `diffeomorphic versus free-form displacement parameterization few training pairs registration network overfitting smoothness regularization small dataset`

## Findings

### Term 1 — **Flowers: A Warp Drive for Neural PDE Solvers** (the big one)

https://arxiv.org/html/2603.04430 — **fetched**, and it is the strongest
architectural preemption found in this whole loop:

- "warping is made the main and only adaptive nonlocal mixing primitive, with
  each layer predicting a single per-head displacement".
- Mechanics from the fetch: input `u` → pointwise value map `v = f[u]` → split
  into H heads → **each head warped at displaced coordinates `x + ϱ^(h)(x)`**,
  with `(ϱ^(1),…,ϱ^(H)) := g[u]` computed **pointwise** (depends only on
  `u(x)`), realized by "bilinear interpolation; this is the same
  differentiable sampling function used by spatial transformer networks".
- Residual block: `u ↦ ϕ ∘ Norm ∘ (SelfWarp_{V,g}[u] + IdProj)[u]` — warp
  output **plus** a skip, i.e. warp-and-add inside the block.
- **No smoothness penalty, no identity/zero initialization** reported.
- **Single-fidelity only**: 18 benchmarks across The Well, PDEBench, PDEGym,
  WaveBench, all "single-resolution/single-fidelity autoregressive
  forecasting"; the fetch is explicit that "Flowers perform no coarse-to-fine
  solution mapping or low-to-high-fidelity correction ... not a learned
  residual correction to an external coarse solution."

So: learned warping inside a neural PDE architecture **is now published**
(2026). What is *not* is warping an external LF solution field into HF
alignment across fidelities.

Also seen on this term (not fetched): parameter-conditioned interpretable
U-Net for convection–diffusion–reaction, https://arxiv.org/html/2601.22654v1 ;
P3D scalable 3-D surrogates, https://arxiv.org/html/2509.10186 . The search
result also notes advection-augmented CNNs as an existing thread in neural PDE
surrogate modeling.

### Term 2 — does a coarse solve DISPLACE interfaces? (premise check)

Yes, and the effect has a name.

- Frictionless motion of diffuse interfaces by sharp phase-field modeling,
  https://doi.org/10.3390/cryst12101496 (MDPI Crystals 12(10):1496) — fetch
  **blocked (HTTP 403 via the mdpi.com redirect target)**; the search-result
  summary reports: "numerical representation of moving diffuse interfaces on
  discrete numerical grids involves **spurious grid friction**", overcome by a
  sharp phase-field method that "restores the discretization-induced broken
  translational invariance", which "allows choosing substantially **coarser**
  numerical resolutions of the diffuse interface **without the appearance of
  pinning**". Recorded as search-snippet-level evidence only (not a fetched
  citation) because the fetch failed.
- Search-level statement of the two error regimes: for phase-field problems
  there is "a regime dominated by **shape error** and a regime dominated by
  **interfacial thickness error**"; at coarse resolutions "advection of an
  interface will result in **deformation** which contributes the majority of
  the phase-field shape error", improving with grid refinement.
- Related, unfetched: spurious currents / interface regularization,
  https://arxiv.org/pdf/2602.18024 ; robust phase-field method for two-phase
  flows, https://arxiv.org/pdf/2310.10795 ; grid-adapting interface thickness,
  https://arxiv.org/pdf/2411.18770 .

Premise verdict: coarse-grid phase-field error is **not** purely amplitude —
pinning/grid friction and shape deformation are position-type errors. But the
same literature says the OTHER regime is interfacial-thickness error, which a
warp cannot fix (a warp preserves the profile it transports; it can stretch it
but only via non-uniform displacement). **The mechanism's payoff therefore
depends on which regime our LF grids sit in — that is a measurable quantity
and the obvious batch-1 diagnostic.**

### Term 3 — diffeomorphic vs free-form, small data

- Most CNN registration nets "parameterize the registration problem with
  **displacement vector fields and ignore desirable diffeomorphic properties**
  (topology preservation, invertibility)"; "although some methods enforce
  smoothness of the displacement field with **global** regularization, it is
  not sufficient to guarantee smooth and consistent displacement vectors in
  **local** regions" — https://arxiv.org/html/2412.17982v1 (unsupervised
  learning of **spatially varying** regularization).
- Diffeomorphic route: stationary/time-continuous velocity fields with
  semigroup regularization, https://arxiv.org/html/2405.18684v1 ; fast
  symmetric diffeomorphic registration CNN (Mok & Chung, CVPR 2020),
  https://openaccess.thecvf.com/content_CVPR_2020/papers/Mok_Fast_Symmetric_Diffeomorphic_Image_Registration_with_Convolutional_Neural_Networks_CVPR_2020_paper.pdf ;
  Laplacian-pyramid large-deformation registration; explicit B-spline
  regularization in diffeomorphic registration,
  https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2013.00039/full ;
  learned regularization prediction, https://arxiv.org/pdf/2011.14229 .
- Design read-across for N_hf = 5–25: a **B-spline / low-mode free-form
  displacement with few control points** is the low-capacity option (few
  parameters, inherently smooth), and **spatially varying** regularization is
  the published response to global smoothness being too blunt. No fetched
  source gives few-shot (N≈5) registration-training evidence — that gap should
  be stated honestly rather than papered over.

## Interpretation

Learned warping in neural PDE solvers is published as of 2026 (Flowers) but
strictly single-fidelity and without the smoothness/zero-init discipline
Candidate D specifies; the cross-fidelity warp remains unoccupied. The
mechanism's physical premise partially survives — coarse phase-field solves do
suffer position-type errors (grid friction/pinning, shape deformation) — but
the competing thickness-error regime means the premise must be *measured on
our own LF fields*, not assumed.
