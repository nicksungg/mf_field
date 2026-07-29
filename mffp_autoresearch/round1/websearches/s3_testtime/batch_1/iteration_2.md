# Iteration 2 — the two gaps iteration 1 exposed

## Search rationale

Iteration 1 produced one refutation-shaped fact ("minimizing the PDE residual
can be an unreliable proxy for reconstruction accuracy in ill-conditioned
systems", ENS) and one open door (IRNO is frozen-base, **learned**-residual,
**single-fidelity**). Iteration 2 therefore probes:

- **Term 1**: is the ill-conditioning hazard real *specifically for Helmholtz*?
  Helmholtz is the ONLY panel dataset with a computable true residual
  (`summary_so_far.md` table); if residual descent is known-bad there, the
  stream's headline design is dead on its one clean target.
- **Term 2**: what replaces a PDE residual for the FOUR time-snapshot
  phase-field/reaction panel datasets (Allen-Cahn, Cahn-Hilliard, Fisher-KPP,
  PFC), where a single snapshot carries no du/dt? Gradient-flow free-energy
  functionals are the obvious candidate — are they usable and are they taken?
- **Term 3**: the direct prior-art probe on the MF composition IRNO leaves
  open — does anyone already refine a coarse/LF solve at inference?

## Search terms used

1. `Helmholtz equation physics-informed residual minimization fails indefinite ill-conditioned neural network high wavenumber`
2. `energy functional free energy correction neural operator phase field Allen-Cahn Cahn-Hilliard post-processing sharpen interface prediction`
3. `multi-fidelity test-time refinement low-fidelity coarse solve initialization neural operator correction inference`

## Findings

### Term 1 — Helmholtz: the hazard is real, but the diagnosis is spectral bias

- **PE-PINN**, "Physics-Informed Neural Networks with Architectural Physics
  Embedding for Large-Scale Wave Field Reconstruction",
  https://arxiv.org/html/2603.02231 — **FETCHED**. Confirms the failure but
  attributes it to spectral bias, not (in this paper) to indefiniteness:
  neural networks "prioritize learning low-frequency components ... while
  systematically underrepresenting the rapid oscillations of high-wavenumber
  fields"; "PINNs frequently encounter severe optimization instabilities when
  modeling **singular sources** or sharp material discontinuities" — note
  `ext__helmholtz_2d`'s `x` is literally a point source at
  `(source_x, source_y)`, i.e. the singular-source case named here. Their fix
  is architectural (envelope transformation demodulating the oscillation into
  a smooth envelope + physics-guided plane/spherical-wave kernels + domain
  decomposition), giving 10x convergence speedup "where baseline PINNs fail
  entirely". The paper explicitly does **not** advance the nonconvex-landscape
  / locally-admissible-solutions explanation (I asked; the fetch says so).
- Search summary also surfaced the standard numerical fact that the
  discretized Helmholtz operator is "very large, complex-valued, sparse, and
  **indefinite**" needing many iterations at high wavenumber (search-snippet
  level, not fetched, NOT used as a citation).

### Term 2 — phase-field: energy functionals are a published operator objective

- **Phase-Field DeepONet** (Li, Bazant et al.), https://arxiv.org/abs/2302.13368
  — **FETCHED (abstract only; the PDF fetch returned corrupted binary)**. The
  citable statement: the method works "by incorporating the **minimizing
  movement scheme** into the framework, which **optimizes and controls how the
  total free energy of a system evolves, instead of solving the governing
  equations directly**", for "pattern formation governed by gradient flows of
  free-energy functionals", validated on Allen-Cahn and Cahn-Hilliard. So the
  free-energy-as-objective substitution for phase-field operators is
  **published prior art at training time**. The abstract does not settle
  whether the scheme is single-snapshot-evaluable or requires time-stepping —
  that stayed unresolved (flagged as a limitation, see Dead ends).
- Adjacent, search-snippet level only (NOT citations): DeepRitzSplit energy
  splitting https://arxiv.org/pdf/2604.18261 ; extended pseudo-spectral PINNs
  for phase-field https://arxiv.org/html/2606.24660v1 ; energy-dissipation-
  preserving PINN https://arxiv.org/pdf/2411.08760 ; the standard framing that
  Allen-Cahn is the **L2** gradient flow and Cahn-Hilliard the **H^-1**
  gradient flow of a free energy.

### Term 3 — the MF composition is NOT open in its plain form

- **Multi-Fidelity Flow Matching (MFFM)**, "Cascaded Refinement of PDE
  Solutions", https://arxiv.org/pdf/2605.16118 — **FETCHED**. Devastating for
  the naive framing: "A **frozen base operator** is trained on low-fidelity
  samples, then a refinement network learns to map from low to high-fidelity
  solutions"; the base operator's output "serves as conditioning for the
  refinement stage" and refinement "learns residual corrections **without
  modifying the frozen base weights**". Its stated primary contribution is
  exactly "the **cascaded composition of a frozen base operator plus a learned
  refinement stage** ... through hierarchical data exploitation". Benchmarks
  Burgers / Navier-Stokes.
  **The one thing MFFM does NOT do**: "The paper does **not** explicitly
  employ the true governing PDE residual as a training signal. Instead, it
  relies on direct supervision using paired low- and high-fidelity solution
  data." Also: refinement is at **training** time (cascade), not a test-time
  optimization loop.
- Search summary also named a multi-fidelity PINN with adaptive residual
  learning, https://arxiv.org/html/2602.01176v1 (not fetched, not cited).

## Interpretation

Both gaps closed, both against the stream's naive design: "frozen base + LF
input + learned refinement" is MFFM's own contribution claim, and
"free-energy functional instead of the governing equation" is Phase-Field
DeepONet's. What no fetched source combines is **a real physics objective
(governing residual or free energy) driving a test-time correction of a
multi-fidelity prediction** — MFFM is data-supervised and train-time, IRNO is
learned and single-fidelity, Phase-Field DeepONet is train-time and
single-fidelity. Iteration 3 must therefore (a) attack that specific
intersection to see if it is also taken, and (b) find whether anyone offers a
*guarantee* that refinement cannot make the output worse — the s2 "skill > 1"
pathology is the standing risk for anything this stream ships.
