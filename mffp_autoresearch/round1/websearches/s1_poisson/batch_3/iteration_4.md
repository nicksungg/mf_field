# Iteration 4 — task (d): the stretch bar. What did IFC actually do, and what does the base lack?

## Search rationale
Batch 1 left the single most material fact in the stream **unresolved**: which
method owns 0.036 vs 0.018, because every route to the paper (openreview PDF,
arXiv `/pdf/`) failed. B2 is now 1.90x from 0.018, so the number governs the
stream's remaining ambition and part 7's framing. Batch-1's dead-end list says use
`/abs/` or `/html/`; the paper is from 2022 so `arxiv.org/html/` does not exist —
this iteration tries **ar5iv** (`ar5iv.labs.arxiv.org/html/<id>`), a route no prior
batch attempted, and cross-checks with the authors' GitHub.

## Search terms used
1. `Infinite-Fidelity Coregionalization IFC-GPODE Li Zhe neural ODE fidelity Poisson nRMSE results table`
2. `"Infinite-Fidelity Coregionalization" latent output basis matrix low-dimensional latent function of fidelity and input training all fidelity data jointly`
3. `"IFC-ODE2" extrapolation "2.14" 128x128 mesh higher fidelity than training nRMSE Poisson interpolation m=1`

## Findings per term

### Term 1 + FETCH (the route that finally worked)
Returns: https://arxiv.org/abs/2207.00678, https://openreview.net/pdf?id=dUYLikScE-
(the batch-1 wall), https://github.com/shib0li/Infinite-Fidelity-Coregionalization,
https://neurips.cc/virtual/2022/poster/55154,
https://proceedings.neurips.cc//paper_files/paper/2022/hash/a6fcfd15cd01e4a550808c3e01f5583d-Abstract-Conference.html,
https://deepai.org/publication/infinite-fidelity-coregionalization-for-physical-simulation.
**FETCH — https://ar5iv.labs.arxiv.org/html/2207.00678 (SUCCESS, first fetch of
this paper's body in the round).** Mechanism, verbatim:
- latent fidelity ODE: "dh(m,x)/dm = phi(m, h(m,x), x)" with "h(0,x) = beta(x)";
- **IFC-GPODE** = GP prior over each basis element across fidelity:
  "b_ij(m) ~ GP(0, kappa(m,m'))", which the fetch characterises as "enabling
  interpolation but with limited extrapolation capability";
- **IFC-ODE2** = a second neural ODE for the bases:
  "db_ij(m)/dm = gamma(b_ij, m), b_ij(0) = nu_ij", which "enables superior
  extrapolation beyond training fidelities";
- Poisson setup: "four fidelities, using 8x8, 16x16, 32x32 and 64x64 meshes" with
  "100, 50, 20, and 5" training examples per level — **the same ladder shape as
  `ifc_poisson` (B2 bookkeeping: 100/50/20/5)**;
- results: "both IFC variants achieving normalized RMSE around 0.036-0.04 across
  latent dimensions K in {5,10,15,20}".

### Term 2 + FETCH (the structural question)
Returns: same cluster as term 1 (arXiv abs, GitHub, NeurIPS poster, DeepAI).
**FETCH — ar5iv again, targeted (SUCCESS).** Three facts:
1. **The 0.018 attribution, resolved (medium-high confidence)**: "We varied
   m in [0,2.14], and examined the corresponding prediction errors", where
   "m=2.14 corresponds to a 128x128 mesh, representing extrapolation beyond the
   highest training fidelity (m=1, 64x64 mesh)"; and "nRMSE of IFC-ODE2 at m=1 and
   m=2.14 is 0.036 vs. 0.018". The fetch's explicit answer to "is any number as low
   as 0.018 reported for Poisson": "Yes, 0.018 is reported for Poisson
   **extrapolation at m=2.14 using IFC-ODE2**." It also states IFC-**GPODE** has
   "smallest error at m=1 … but performance drops when m>1".
2. **Per-sample latent, shared bases**: "we model the latent output as a continuous
   function of the input and fidelity, i.e., h(x,m)" and then "multiply the latent
   output with a basis matrix B to obtain the high-dimensional output at fidelity
   m" — i.e. the field is factorised into **input-dependent, fidelity-continuous
   coefficients** times **input-independent, fidelity-varying spatial bases**.
3. **Joint likelihood over all levels**: "p(Y|X) = prod_n N(y_n | B_n h(m_n, x_n),
   sigma^2 I)" — all fidelities enter one likelihood with their own m_n.
   *Caveat recorded*: this second fetch rendered the Poisson per-level counts as
   "256, 128, 64, and 32" whereas the first fetch of the same page rendered
   "100, 50, 20, and 5". The summariser is not reliable on table digits; the
   ladder-shape claim above is safe, the exact counts are **not** (and our own
   dataset's counts are authoritative for our numbers anyway).

### Term 3 — independent cross-check of the m=2.14 attribution
Returns were mostly off-target (CraftMesh, IMEX schemes), but the engine's synthesis
over https://arxiv.org/pdf/2207.00678 independently states: "The value **2.14
corresponds to a mesh of size 128x128**", and "IFC-ODE^2 showing better performance
when m > 1 (mesh size bigger than 64x64)". Two independent renderings therefore
agree that 2.14 = 128^2 and that ODE2, not GPODE, is the m>1 winner.
**FETCH — https://raw.githubusercontent.com/shib0li/Infinite-Fidelity-Coregionalization/main/README.md**
(fetched, low yield): confirms the two variants ("IFC-ODE^2: uses neural ODEs for
both latent outputs and basis functions"; the GP-basis variant) and the "tensor-
Gaussian variational posterior approximation … for massive outputs", but "does not
specify mesh sizes or the number of training examples per fidelity level".

## Interpretation
Two consequences, both material. (1) **The 0.018 stretch bar is, per the only
first-hand rendering the round has obtained, IFC-ODE2's error at m=2.14 = 128^2
extrapolation, not a 64^2 number, and not IFC-GPODE's** — which contradicts the
attribution sentence in `docs/adr/0002-ifc-poisson-skill-reference.md` ("the
stronger IFC-GPODE 0.018") and confirms batch 1's suspicion. The ADR's *decision*
(denominator 0.036) is untouched by this; only the stretch-reference attribution is
affected, and ADRs are immutable in-round (program.md §5.3), so the finding is a
**written note to the operator**, not an action. (2) The base's real structural gap
vs IFC is now nameable: IFC represents the field as **per-sample, fidelity-
continuous latent coefficients x shared fidelity-varying spatial bases**, trained
under one joint likelihood over all levels. The B2 base already has the joint
all-level training; what it lacks is the explicit per-sample coefficient factor —
and the card's scalar gain g(X) is exactly the **K=1, amplitude-only, post-hoc**
special case of IFC's latent coefficient vector. That is the sharpest available
motivation *and* the sharpest available preemption risk, and it is now cited.
