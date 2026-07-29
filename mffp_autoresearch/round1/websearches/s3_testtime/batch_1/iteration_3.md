# Iteration 3 — the intersection, the safety guarantee, and the solver route

## Search rationale

Iteration 2 left exactly one un-refuted intersection (*real physics objective*
x *test-time* x *multi-fidelity*) and one unanswered design question (can a
refinement be made **provably no worse** than what it started from — the
standing "skill > 1" risk from program.md 2.3, where every zoo model already
loses to its own LF input). Iteration 3 attacks both, plus the third seed
direction implicit in the stream: the in-repo report's proposal **N3**
(`mf_fno_solve`, predict-then-solve with a fixed Krylov budget), which is the
strongest form of "the residual is real" and the only route with a *bounded*
error.

## Search terms used

1. `physics residual test-time correction of multi-fidelity surrogate prediction few high-fidelity samples governing equation refinement`
2. `guarantee refinement never worse than baseline safeguard line search trust region test-time adaptation neural PDE surrogate`
3. `learned preconditioner Krylov conjugate gradient correction of neural operator prediction bounded by solver iterations known PDE`

## Findings

### Term 1 — MF + physics, but never at test time

No usable *test-time* result. Everything returned is train-time multi-fidelity
residual learning: MF Residual Neural Processes https://arxiv.org/pdf/2402.18846
(surrogate on the residual between aggregated lower-fidelity prediction and HF
truth — note this is the MFRNP whose npz convention this repo already uses),
physics-guided bi-fidelity operator learning https://arxiv.org/pdf/2311.03639 ,
data-efficient MF DeepONet with physics-guided subsampling
https://arxiv.org/pdf/2503.17941 . All search-snippet level, none fetched,
none used as citations. **No usable results for the specific query** (physics
residual applied as a *test-time* correction to a *multi-fidelity* prediction).

### Term 2 — no clean "cannot be worse" guarantee in the learned-refinement literature

- PDE-Refiner (NeurIPS 2023), https://papers.neurips.cc/paper_files/paper/2023/file/d529b943af3dba734f8a7d49efcb6d09-Paper-Conference.pdf
  and https://dl.acm.org/doi/10.5555/3666122.3669068 — "a novel model class
  that enables more accurate modeling of all frequency components via a
  multistep refinement process". Learned, no guarantee. (snippet level, not
  fetched.)
- Trust-region framing appeared only as a generic "dynamic trust radius ...
  intelligent guardrail" in a rare-event surrogate paper
  https://arxiv.org/abs/2605.15356 — not a refinement guarantee.
- **Read-out: the learned-refinement family offers no monotonicity guarantee.**
  The only monotone-by-construction option is a classical solver (term 3).

### Term 3 — the solver route is real, guaranteed, and ALREADY PUBLISHED

- **NOWS — "Neural Operator Warm Starts for Accelerating Iterative Solvers"**,
  https://arxiv.org/abs/2511.02481 — **FETCHED (abstract; the PDF fetch failed
  with `maxContentLength size of 10485760 exceeded`)**. This is proposal N3's
  mechanism, verbatim: learned solution operators "producing **high-quality
  initial guesses for Krylov methods such as conjugate gradient and GMRES**",
  while "**preserv[ing] the stability and convergence guarantees of the
  underlying numerical algorithms**" — i.e. the classical solver keeps
  iterating from the neural initialization so the final answer inherits the
  solver's guarantee, not the network's. Reported up to **90%** runtime
  reduction; integrates with FD/FEM/IGA/FVM. (Surfaced in iteration 1's term-2
  result list; fetched here.)
- **FCG-NO**, "Neural operators meet conjugate gradients",
  https://arxiv.org/pdf/2402.05598 — **FETCHED**. The complementary form: a
  **frozen** trained neural operator used as a *nonlinear preconditioner*
  inside flexible CG, with FCG convergence guarantees, 2-8x acceleration on
  elliptic/Poisson-type and parametric PDEs. Explicitly "**No multi-fidelity**:
  the document does not describe coarse-grid or low-fidelity data strategies".
- Adjacent (snippet level, not cited): GNN preconditioner design
  https://arxiv.org/abs/2405.15557 ; learning preconditioners for CG
  https://arxiv.org/abs/2305.16432 ; neural incomplete factorization
  https://arxiv.org/pdf/2305.16368 ; neural preconditioning via Krylov
  subspace geometry https://arxiv.org/html/2507.15452 .

## Interpretation

The solver route (N3 / "predict-then-solve") is the only mechanism with a
**monotone, provable** guarantee that refinement cannot end below its own
starting point — and it is squarely published (NOWS, FCG-NO), both
single-fidelity and both about *speed*, not about accuracy-under-scarce-HF.
Meanwhile the exact triple (real physics objective + test time + multi-fidelity
input) returned **nothing**. Field context is sufficient; iteration 4 spends
itself entirely on 3.3, running refutation-shaped searches against the three
concrete directions this batch can propose.

**ENOUGH** — three iterations have produced a fetched source for every branch
of the design space (learned refinement: IRNO; MF cascade: MFFM; physics
objective for phase-field: Phase-Field DeepONet; solver route: NOWS/FCG-NO;
the hazard: ENS). Remaining iterations go to the prior-art verdict.
