# iteration_5 — s1_poisson batch 2 (CAP: k = 5 of 5, loop stops here)

## Search rationale

Final iteration = the mandatory §3.3 refutation pass. Three targeted "has this
been done?" searches, one per candidate direction the batch-2 card will contain:
(i) per-level target normalization in MF ladder training, (ii) h^p-aware
residual/target scaling as an inductive bias, (iii) the factorial
normalization × composition design. Adversarial bias as instructed: I went
looking for the *preprocessing paragraph* in the papers most likely to hide one
(the newest discretization-independent MF operator-learning paper, and the
nonlinear-autoregressive MF family that owns the per-level scale factor).

## Search terms used

1. `discretization-independent multifidelity operator learning normalization each fidelity level separately scaled data preprocessing`
2. `nonlinear autoregressive multi-fidelity deep learning NARGP learn per-level scale factor output rescaling before network training`
3. `factorial ablation interaction between normalization scheme and training data composition multi-level neural PDE surrogate 2x2 design`

## Findings

### Term 1 — refutation attempt for (i)

- **"Discretization-independent multifidelity operator learning for PDEs"**
  [https://arxiv.org/abs/2507.07292] (fetched, abs). Encode–approximate–
  reconstruct operator model with neural function-basis representations;
  "multifidelity training can reduce errors caused by low-fidelity training
  data". Fetch verdict, explicit: the abstract "does not discuss: whether
  normalization is shared or per-fidelity; how different fidelity levels' data
  are normalized; any ablation studies on normalization strategies; data scaling
  procedures across fidelities." **A fourth independent explicit negative** on
  the same question (after MF-PINN 2602.01176, Frontiers MF-ANN, SMT MFK docs).
- Search-return only, not fetched: MF-FNO transfer learning for flow/temperature
  [https://arxiv.org/pdf/2304.06972] uses "relative loss normalization" with LF
  from coarse discretization and HF from refined discretization — the closest
  phrase seen to a loss-side scale-invariance in an MF-FNO, but snippet-grade
  and NOT a target-normalization statement; do not cite as one.

### Term 2 — refutation attempt for (i) and (ii) from the NARGP side

- **NARGP (Perdikaris et al. 2017), as characterized in the returned MF-emulation
  literature** [https://arxiv.org/pdf/2306.03144 (MF-Box),
  https://arxiv.org/pdf/2105.01081] (search-return, not fetched): the nonlinear
  MF model "drops the assumption that the scale factor is independent of input
  parameters, allowing the scale factor ρ_t(·) to be a function of both input
  ... and output from the previous fidelity"; f_q(x) = z_{q-1}(f_{q-1}(x)) +
  δ_q(x). So the amplitude relation between levels is a **first-class learned
  object** in the classical nonlinear-MF family. Also noted: because NARGP is
  recursive and each level trains independently, "no information flows backward
  from higher to lower fidelities" — the exact deficiency B1's single shared
  pooled-row network was supposed to avoid.
- The engine's closing negative: the results "don't contain specific details
  about 'per-level scale factor output rescaling before network training' as a
  specific technique."

### Term 3 — refutation attempt for (iii)

**No usable result.** Engine's closing statement, verbatim: "I did not find a
specific paper directly addressing a 2x2 factorial ablation study examining the
interaction between normalization scheme and training data composition for
multi-level neural PDE surrogates." The generic practice statement returned
("Data fields are typically normalized by subtracting the mean and dividing by
the standard deviation in neural PDE surrogate training", with some models
forgoing normalization because e.g. the Hamiltonian is not scale/shift
invariant, over [https://arxiv.org/html/2405.17260v2,
https://arxiv.org/pdf/2506.05513]) confirms only that normalization is a
routine, rarely-ablated preprocessing choice.

## PRIOR-ART VERDICTS (§3.3)

### (i) Per-level / per-fidelity **target** normalization in MF ladder training
**Verdict: `preempted-but-MF-composition-open`.**
Published, in a different setting: multi-level residual-correction neural
networks for BVPs are reported to *require* per-level normalization because
"the size of the residual becomes increasingly smaller at each level, which
requires normalization of the solution error at each level"
[https://www.sciencedirect.com/science/article/abs/pii/S0045782523007892 —
**snippet-grade, fetch returned HTTP 403**, iteration_2]. Adjacent published
mechanism: QuadNorm shows *internal* neural-operator normalization is
discretization-dependent and fixes it with quadrature weights
[https://arxiv.org/html/2605.07375 — fetched, iteration_1]. Classical MF instead
*models* the level amplitude ratio as ρ rather than normalizing it away
[https://smt.readthedocs.io/en/latest/_src_docs/applications/mfk.html — fetched,
iteration_3; NARGP's input-dependent ρ_t(·), iteration_5].
**What remains open**: per-level standardization of **targets pooled into one
shared fidelity-conditioned operator** — five fetched MF sources
(https://arxiv.org/html/2602.01176v1, the Frontiers MF-ANN framework,
https://smt.readthedocs.io/.../mfk.html, https://arxiv.org/abs/2507.07292, plus
the iteration-3 engine negative) each **fail to state their cross-fidelity
normalization at all**, so there is no published effect size for the choice, and
none at N_hf = 5 on an elliptic ladder.
**Directive**: this is a **hygiene fix measured as an ablation**, not a new
mechanism. Do not write it up as an invention.

### (ii) h^p-aware residual/target scaling as an inductive bias
**Verdict: `preempted (cite)`.**
Gauss–Richardson Extrapolation encodes the convergence order directly:
the error bound "typically takes the form b(x) = x^r, where r represents the
convergence order", entering the kernel as
`k(x,x') := σ²[k₀² + b(x)b(x')k_e(x,x')]`, a design that "ensures the
**normalized error (f(x)−f(0))/b(x) behaves regularly**", with r estimated by
maximum quasi-likelihood when unknown
[https://pmc.ncbi.nlm.nih.gov/articles/PMC11985099/ — **fetched**, iteration_2].
That *is* dividing level differences by h^p, in a GP that explicitly "unifies
classical extrapolation methods with modern multi-fidelity modelling". Also,
NN-approximated local truncation error is already positioned as a replacement
for Richardson extrapolation [https://arxiv.org/pdf/2504.05493 — search-return,
iteration_2].
**Narrow residue**: GRE is GP-based extrapolation of (functionals of) solutions,
not a field-valued neural operator, and no fetched source rescales *training
targets* by h^p inside a learned operator.
**Directive**: do NOT hard-code an h² scaler as a contribution. The
**empirical** per-level scaler is strictly safer (it needs no known rate) and is
the same fix; B1 already measured the empirical ratios 4.379/4.196/4.120, within
≈5 % of 2² — that agreement is a *result to report*, not a mechanism to claim.

### (iii) The factorial **normalization × composition** design itself
**Verdict: `novel` (design-level only; weak-claim).**
Nothing close found: term 3 this turn returned an explicit negative for a 2×2
factorial of normalization scheme × training-data composition in multi-level
neural PDE surrogates; term 2 of iteration_3 returned an explicit negative for
fidelity-conditioned operators with output-scale conditioning + normalization
ablations. Nearest neighbors are (a) routine hyperparameter ablations in neural
PDE surrogates [https://arxiv.org/html/2405.17260v2], and (b) MFRNP's
aggregation ablation [https://arxiv.org/html/2402.18846v1, batch 1].
**Directive**: the value of the design is **internal validity** — separating the
two contrasts B1 conflated — not novelty. Claim "not previously ablated", never
"novel method".

### (iv) Training-free level-matched nearest-condition lookup as a floor
**Verdict: `novel` (not found published for elliptic MF); report, don't claim.**
Three searches (iteration_4) produced only generic kNN-competitiveness snippets
[https://www.mdpi.com/2076-3417/11/20/9411,
https://www.sciencedirect.com/science/article/abs/pii/S0306454925006863], none
multi-fidelity, none field-valued elliptic. The weak-baseline critique
[https://arxiv.org/abs/2407.07218 — fetched; **79 % (60/76)** of ML-beats-solver
claims use a weak baseline] licenses *reporting* the floor beside every skill
number, but its abstract explicitly does not discuss interpolation/NN baselines,
so it cannot be cited *for* the construct.

## Cap note

k = 5 reached; the loop stops here per §3.2. Unfetched leads deliberately left
on the table: Multi-Grid Tensorized FNO (2310.00120), Physics-informed
Multi-resolution Neural Operator (2510.23810), Multigrade NN Approximation
(2601.16884), Neural Emulator Superiority (2510.23111).
