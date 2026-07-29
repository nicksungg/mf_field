# Iteration 4 — prior-art refutation, round 1 (per 3.3)

## Search rationale

Field context was declared sufficient at the end of `iteration_3.md`
(**ENOUGH**). This iteration and the next are spent entirely on 3.3. From
program.md 12.3 plus what iterations 1-3 found, the three directions this
stream-batch can realistically propose are:

- **D1 — true-residual test-time refinement.** Replace `mf_fno_ptr`'s
  placeholder Laplacian with the **exact** governing residual on the one panel
  dataset where it is computable (`ext__helmholtz_2d`: `du + k^2 u = f`, f a
  point source located by `x`), descending on the field tensor with an anchor,
  starting from a multi-fidelity prediction. (Program.md 12.3's headline.)
- **D2 — IRNO-style frozen-base fixed-point refinement, MF-conditioned.**
  Weight-tied learned corrector `h_{k+1} = h_k + alpha*Phi(x, h_k, u_LF)`
  under a progressive spectral loss, initialized from the LF field rather than
  from a base operator's output. (Program.md 12.3's second lever + report N1.)
- **D3 — predict-then-solve.** MF prediction as the warm start for a fixed
  Krylov budget on the discrete operator (report proposal N3).

Each term below is deliberately phrased to FIND the paper that kills the
direction, not to support it.

## Search terms used

1. `gradient descent on predicted field Helmholtz exact source residual test-time refinement operator output anchor loss` (kill D1)
2. `iterative refinement operator conditioned on low-fidelity coarse field fixed-point multi-fidelity neural operator inference loop` (kill D2)
3. `free energy projection test-time correction phase field prediction sharpen diffuse interface tanh equilibrium profile neural network postprocessing` (kill the phase-field variant of D1)

## Findings

### Term 1 (kill D1) — no direct kill found

Nothing returned performs gradient descent on a *predicted field* against an
*exact* Helmholtz residual as an inference-time step. Closest neighbours, all
search-snippet level:
- Physics-Based Flow Matching for silicon photonics,
  https://arxiv.org/pdf/2605.06929 — search summary says it uses "a Helmholtz
  residual loss computed from predicted field estimates", which would be the
  nearest neighbour. **FETCH FAILED** (PDF returned metadata/binary only), so
  I cannot establish whether that residual is a training loss or a test-time
  correction. **This is the one unresolved threat to D1's verdict** and it is
  recorded as such.
- Classical Helmholtz solver work (shifted-Laplacian preconditioners
  https://homepages.cwi.nl/~barry/chapter10.pdf ; DPG multigrid) — different
  problem class, not neural refinement.
- The rest of the result page was off-domain (video-coding "prediction
  refinement" patents, transparent-object matting) — the query was too
  compound; see Dead ends.

### Term 2 (kill D2) — partial kill, and a third preemptive architecture

- Re-returned **IRNO** https://arxiv.org/html/2605.24041 and **MFFM**
  https://arxiv.org/html/2605.16118v1 , now with the search summary stating
  the pairing explicitly: "Both approaches address the spectral bias problem
  in neural operators by leveraging hierarchical refinement **conditioned on
  coarse-field initialization**", and MFFM "consumes low-fidelity solver
  output on a finer grid and produces high-fidelity refinement ... posing the
  **LF-to-HF refinement as conditional residual flow matching**".
- **NEW: SINO — "Starter-Iterator Neural Operator: A Unified Architecture for
  High-Fidelity Forward and Inverse PDE Problems"**,
  https://arxiv.org/html/2606.18305 — **FETCHED**. A third independent
  instance of the same skeleton: a learnable *starter* captures "the dominant
  low-frequency components" giving "a reliable coarse representation that
  mitigates spectral bias"; an *iterator* does unrolled learned fixed-point
  refinement `Delta u^(n) = B^(n)(f - A^(n) u^(n))` with **both** the forward
  operator and the preconditioner parameterized as neural operators. Key
  disqualifying-for-us details, verbatim from the fetch: the iteration is
  "**purely learned**. It does not use true PDE residuals"; "**No explicit
  multi-fidelity structure**"; and the starter is **not** frozen (starter and
  iterator are trained jointly end-to-end). Results: NS 3.0e-4 vs FNO 8.0e-4,
  acoustic wave 5.0e-4 vs 1.8e-3, shallow water 6.0e-4 vs 1.3e-3, stable over
  50+ autoregressive steps. (SINO is the "Park/SINO" already named in
  program.md 12.4's prior-art list — now verified first-hand.)

### Term 3 (kill the phase-field variant) — no usable results for the exact mechanism

Three successive result pages; **no paper applies a free-energy or equilibrium
projection as a post-hoc/test-time correction of an already-predicted
phase-field snapshot.** What exists is all *training-time* physics-informed
phase-field solving:
- PINNs-MPF https://arxiv.org/pdf/2407.02230 — multi-phase-field PINN;
  notable snippet: focusing on the diffuse interfacial zone "does not exclude
  random predictions away from interfaces, so a **denoising loss functioning
  as a corrector** is introduced" — a corrector, but inside training.
- Sharp-PINNs https://arxiv.org/html/2502.11942 (staggered hard-constrained
  PINN for phase-field corrosion); PF-PINNs for coupled AC/CH
  https://www.sciencedirect.com/science/article/pii/S0021999125001263 ;
  end-to-end deep learning for nonlocal AC/CH https://arxiv.org/pdf/2410.08914 .
- A perturbation-correction method with a primary tanh network plus a
  **correction network** for quasi-linear interface problems
  https://arxiv.org/pdf/2602.05800 — training-time, not test-time.
- None fetched; all snippet-level; none used as a citation.

## Interpretation

D2's plain form is comprehensively preempted — three independent 2026 papers
(IRNO, MFFM, SINO) all build "coarse/low-frequency initialization + learned
residual refinement", and MFFM specifically claims the LF-conditioned version.
What all three lack, in fetched text, is the **true governing residual at
inference**. D1 survives round 1 with one unresolved threat (2605.06929, fetch
failed). The phase-field free-energy test-time correction returned nothing at
all. Iteration 5 resolves the 2605.06929 threat and issues the verdict table.
