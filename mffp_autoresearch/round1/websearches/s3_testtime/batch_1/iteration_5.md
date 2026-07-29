# Iteration 5 — FINAL (iteration cap = 5, reached): the prior-art verdict

**Cap note**: this is iteration 5 of the 5 allowed by the websearcher contract
3.2. No further searching is possible in this batch; anything still unresolved
below is recorded as unresolved rather than guessed.

## Search rationale

`iteration_4.md` left three things to settle before the verdict table:
(a) the one unresolved threat to **D1** — whether PIC-Flow (2605.06929) uses
its Helmholtz residual at training or at inference (the PDF fetch had failed);
(b) whether PINO's instance-wise test-time optimization + anchor loss is
established enough to preempt D1's *mechanism* (as opposed to its application);
(c) whether **D3** (predict-then-solve / warm start) has a *multi-fidelity*
instance, which NOWS and FCG-NO both explicitly lacked.

## Search terms used

1. `Quaratiello Rizzo physics-based flow matching silicon photonic Helmholtz residual training loss inference`
2. `PINO instance-wise test-time optimization anchor loss frozen operator solve PDE residual gains reported`
3. `neural operator prediction warm start conjugate gradient fixed iteration budget multi-fidelity few high-fidelity samples elliptic`

## Findings

### Term 1 — D1 threat RESOLVED (in D1's favour), and a transferable trick

**PIC-Flow**, Quaratiello & Rizzo (Dartmouth), "Physics-Based Flow Matching for
Full-Field Prediction of Silicon Photonic Devices",
https://arxiv.org/abs/2605.06929 (2026-05-07). The search result states the
Helmholtz residual is used for "**physics-constrained training** through a
Helmholtz residual loss enforcing `grad^2 Ez + k0^2 eps Ez = 0`" — a
**training-time** loss inside a conditional-flow-matching U-Net, not an
inference-time correction. So it does **not** preempt D1.
**Transferable and directly actionable**: PIC-Flow "introduced an
**interface-aware masking scheme for the Helmholtz residual that excludes
dielectric boundary pixels where finite-difference stencil errors dominate**,
yielding a physically meaningful compliance metric." `ext__helmholtz_2d` has a
**point source** in its condition vector — precisely the location where a
finite-difference Helmholtz residual is singular and where an unmasked
residual term would dominate and corrupt the descent. Any D1 build must mask.
(Search-summary level; the PDF fetch failed again in iteration 4 with
metadata-only content. Cited as a search-returned source with URL, not as a
fetched quotation.)

### Term 2 — D1's MECHANISM is preempted, at search-summary level only

Consistent statements across the returned set (PINO, https://arxiv.org/pdf/2111.03794 ;
OpenReview https://openreview.net/pdf/599f6baa8b522af9cb7b4d8a1d220aca987db406.pdf ;
official code https://github.com/neuraloperator/physics_informed ):
"**Instance-wise fine-tuning (or test-time optimization)** allows the
pretrained neural operator to be further refined to solve a single PDE
instance using **only the PDE loss** to minimize residual errors", with "an
additional **anchor loss** ... expressed as the L2 distance between the
fine-tuned and pretrained operators" to "prevent the optimization from
deviating too much".

**HONESTY FLAG — this is NOT a fetched citation.** I attempted the PINO source
three times across iterations 1 and 5 and all three failed: the arXiv PDF
returned corrupted binary (twice), and the OpenReview PDF returned a browser
verification page. The emergentmind PINO topic page
https://www.emergentmind.com/topics/physics-informed-neural-operator-pino was
**FETCHED** and explicitly says the opposite — it "does not contain specific
details about instance-wise or test-time optimization", describing only
offline fine-tuning. So the strongest defensible statement is: *PINO-style
instance-wise test-time optimization with an anchor loss is repeatedly
described in search results as established prior art, but this loop could not
fetch a primary source confirming it.* The brainstormer must treat D1's
mechanism as **presumed preempted** and, if it proposes D1, verify PINO
directly (the ONE difference that is separately grounded: `mf_fno_ptr` and
this batch would optimize the **output field**, whereas PINO optimizes the
**operator weights**).

### Term 3 — D3 is PREEMPTED, including its multi-fidelity form

- **NOWS**, https://arxiv.org/abs/2511.02481 (fetched in iteration 3;
  journal version https://www.sciencedirect.com/science/article/pii/S0045782526002628 ):
  now confirmed to include "the **canonical Poisson equation, a second-order
  elliptic PDE**" — i.e. the exact class of `ifc_poisson` / Helmholtz. Up to
  90% runtime reduction "while preserving the stability and convergence
  guarantees of the underlying numerical algorithms."
- **NEW and decisive: "Neural operator-based super-fidelity: A warm-start
  approach for accelerating steady-state simulations"**,
  https://arxiv.org/abs/2312.11842 — **FETCHED**. "It uses a neural operator
  to **map low-fidelity solutions to high-fidelity targets**, then employs
  this as a **warm-start initialization for classical steady-state PDE
  solvers**", via a vector-cloud neural network with equivariance (VCNN-e);
  at-least-**two-fold** acceleration "without sacrificing accuracy" on three
  flow cases. The search summary adds it is "capable of learning with just a
  few solutions by decomposing the whole solution field into patches". This is
  D3, multi-fidelity and all.
- Also returned (snippet level, not fetched, not cited): Pretrained Finite
  Element Method with an optional warm-start stage
  https://www.sciencedirect.com/science/article/abs/pii/S0022509626001833 ;
  "Spectrally Safe Neural Operator Warm-Starts for Large-Scale Newton Solvers"
  https://arxiv.org/pdf/2606.21828 (the safeguarding question from iteration 3
  term 2 evidently has its own paper — unfetched, cap reached).

## THE PRIOR-ART VERDICT

| # | Candidate direction | Verdict | Fetched/returned citations | What remains open |
|---|---|---|---|---|
| **D1** | Replace `mf_fno_ptr`'s placeholder Laplacian with the **exact** governing residual (`du + k^2 u = f`, source located by `x`) and descend on the **output field** with an anchor, starting from an MF prediction. | **preempted-but-MF-composition-open (cite)** — with an honesty caveat | PINO instance-wise fine-tuning + anchor loss https://arxiv.org/pdf/2111.03794 (**search-summary only; three fetch attempts failed** — see Term 2 flag); ENS https://arxiv.org/abs/2606.27354 (fetched); PIC-Flow https://arxiv.org/abs/2605.06929 (training-time residual, does NOT preempt); PE-PINN https://arxiv.org/html/2603.02231 (fetched) | The mechanism (test-time residual descent + anchor) is prior art. Open: (i) field-space vs weight-space optimization; (ii) doing it **from a multi-fidelity prediction under N_hf = 5** — no fetched source combines a real physics objective, test time, and MF; (iii) whether it beats **copy-LF** rather than beating the base model, which is the round's actual bar (program.md 2.2) and which nobody in this literature measures. **Standing threat**: ENS (fetched) — "numerically minimizing the PDE residual can be an unreliable proxy for reconstruction accuracy in ill-conditioned systems", and Helmholtz is the canonical indefinite operator. Mandatory mitigation: PIC-Flow's interface/source masking. |
| **D2** | IRNO-style frozen-base weight-tied fixed-point refinement `h_{k+1} = h_k + alpha*Phi(x, h_k, u_LF)` under a progressive spectral loss, initialized from / conditioned on the LF field. | **preempted (cite)** in its plain form | IRNO https://arxiv.org/html/2605.24041 (fetched); MFFM https://arxiv.org/pdf/2605.16118 (fetched); SINO https://arxiv.org/html/2606.18305 (fetched) | Three independent 2026 papers build "coarse initialization + learned residual refinement", and **MFFM explicitly claims "the cascaded composition of a frozen base operator plus a learned refinement stage"** with LF input as its primary contribution. Genuinely open only if the refinement is driven by a **real physics objective** rather than data supervision (all three are verified purely learned: IRNO "no true PDE residuals are computed at test time"; SINO "purely learned. It does not use true PDE residuals"; MFFM "does not explicitly employ the true governing PDE residual"). Also open, and cheap: IRNO's *cross-operator transferability* (58.53% on TR-2D without retraining) has never been tested **across fidelities**. Do NOT propose plain LF-conditioned learned refinement — it is MFFM. |
| **D3** | MF prediction as warm start for a fixed Krylov/CG budget on the assembled discrete operator (in-repo proposal N3, `mf_fno_solve`). | **preempted (cite)** | NOWS https://arxiv.org/abs/2511.02481 (fetched) incl. the Poisson/elliptic case; super-fidelity https://arxiv.org/abs/2312.11842 (fetched) — LF->HF map used as warm start for a classical steady-state solver; FCG-NO https://arxiv.org/pdf/2402.05598 (fetched) | The mechanism, the elliptic application, AND the multi-fidelity variant are all published. What no source does is use it as an **accuracy** method under HF scarcity rather than a **speed** method — every cited work reports runtime (90%, 2x, 2-8x), none reports accuracy at N_hf = 5. That reframing is thin novelty and, worse, D3 needs the discrete operator + source term, which `summary_so_far.md` shows is **unavailable for `ifc_poisson`** (source decode not shipped) — leaving Helmholtz alone. Not recommended as a batch-1 card. |
| **D4** | Free-energy / equilibrium projection as a test-time correction for the four time-snapshot phase-field panel datasets (no du/dt available). | **novel** (weakly — absence of evidence) | Nearest neighbours, all **training-time**: Phase-Field DeepONet https://arxiv.org/abs/2302.13368 (fetched abstract: minimizing-movement scheme "optimizes and controls how the total free energy of a system evolves, instead of solving the governing equations directly"); PINNs-MPF https://arxiv.org/pdf/2407.02230 (a "denoising loss functioning as a corrector", in training); Sharp-PINNs https://arxiv.org/html/2502.11942 | Three result pages produced **no** paper that applies a free-energy or equilibrium projection as a post-hoc correction to an already-predicted phase-field snapshot. This is the only `novel` slot — but it is novelty by absence, and it inherits the ENS hazard in a worse form (a free-energy functional is an even weaker proxy for pointwise accuracy than a true residual, and its minimizer at fixed mean composition is NOT the snapshot at t=0.5). Any D4 card must state up front what stops it from collapsing the field to a bulk equilibrium. Note the 5 sharp-2D datasets are exactly where every zoo model already loses to copy-LF. |

## Interpretation

The stream's own two named levers land differently than program.md 12.3
assumes: the "true governing residual" lever (D1) is mechanically preempted but
its multi-fidelity + copy-LF-bar composition is open, while the IRNO lever (D2)
is preempted precisely in the LF-conditioned form the stream wants. The
cleanest genuine experiments are (a) D1 restricted to Helmholtz with source
masking, scored against **copy-LF**, and (b) D4, the one thing nobody has done
— both of which are cheap and both of which teach something whether they win
or lose.
