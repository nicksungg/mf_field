# Iteration 3 — refutation turn 1: E1's estimator, the affine-benchmark claim, E3(c)

## Search rationale

Turn 1 found LR-MFS (scalar responses). The refutation question for E1 is
sharper: has anyone done multi-fidelity **linear** regression for **field**
outputs in the **data-poor** regime? Second, B1's headline surprise —
"ifc_poisson is exactly affine in its 5-dim condition" — is presented as a
benchmark-integrity finding, so it must be checked against the reduced-basis /
affine-parameter-dependence literature before being called a discovery. Third,
E3(c) (penalize/calibrate the null-direction component) needs its own
refutation pass beyond turn 2's implicit-bias theory.

## Search terms used

1. `multi-fidelity surrogate full field prediction pixelwise linear regression low-fidelity coarse solution basis coefficient field few high-fidelity snapshots`
2. `reduced basis affine parameter dependence solution linear in parameters superposition parametric Poisson benchmark trivially linear surrogate`
3. `null space regularization neural operator penalize component unconstrained by training data min-norm prior small data surrogate`

## Findings

### Term 1 — MF linear regression for fields / data-poor

Returns re-confirm LR-MFS [https://arxiv.org/abs/1705.02956, AIAA
10.2514/1.J057299, OSTI 1571620 application paper] and add:
**"Projection-based multifidelity linear regression for data-poor
applications"** (Sella, Pham, Chaudhuri, Willcox)
[search return: https://kiwi.oden.utexas.edu/papers/multifidelity-regression-data-poor-Sella-Pham-Chaudhuri-Willcox.pdf
— **FETCH FAILED**: the PDF returned binary/compressed content the fetcher
could not parse, so nothing beyond the title/authors is claimed from it];
non-hierarchical multi-LF fusion with locally-weighted correlations
[search return: https://www.sciencedirect.com/science/article/abs/pii/S1270963824000610,
https://www.sciencedirect.com/science/article/abs/pii/S1474034621001828].
Engine synthesis (attributed to the LR-MFS abstract, consistent with the
iteration-1 fetch): "Because the proposed LR-MFS is obtained from standard
linear regression, it can take advantage of established regression techniques
such as prediction variance, D-optimal design, and inference ... particularly
useful when only a few high-fidelity simulations or experiments are
affordable."
→ **The exact selling point of E1 — a linear MF surrogate because HF samples
are few — is the LR-MFS selling point verbatim.** Plus a data-poor
projection-based MF *linear regression* paper exists by title. Field-valued
output remains unconfirmed either way (no fetchable evidence).

### Term 2 — affine parameter dependence / reduced basis

Returns: Springer "Generalized Reduced Basis Methods and n-Width Estimates ..."
[https://link.springer.com/chapter/10.1007/978-88-470-2592-9_16];
arXiv:1911.08954 [search return: https://arxiv.org/pdf/1911.08954]
"Basic Ideas and Tools for Projection-Based Model Reduction of
Parametric PDEs"; Certified RB review
[https://mathematicsinindustry.springeropen.com/articles/10.1186/2190-5983-1-3];
RB for non-affine parametrized BCs [https://arxiv.org/pdf/1705.08349].
Engine synthesis: RB methods "rely on affine parameter dependency" — the
bilinear form expands as `sum_q Theta_q(mu) A_q` with parameter-independent
operators — and this is the standard enabler of offline/online splitting; a
whole sub-literature exists for the **non-affine** case (EIM-style), which
only exists because affine dependence is the assumed-normal case.
→ **"This parametric elliptic benchmark is affine in its parameters" is not a
discovery in the PDE community — it is the textbook regime that reduced-basis
methods are built on.** B1's finding retains full force as a *benchmark
integrity* statement about `ifc_poisson`'s role in this project's success
criteria (a 6-coefficient exact law means criterion-2 there is rank recovery,
not operator learning), but it must NOT be presented as a novel mathematical
observation. No source retrieved here states the specific form "solution field
is an exactly affine function of the 5 condition scalars"; that follows from
linear superposition and is verified on disk by `tools/affine_ladder_voi.py`.

### Term 3 — null-space regularization

Returns: **NPN** [fetched: https://arxiv.org/html/2510.01608] — regularizes the
null space of a **measurement operator** H in imaging inverse problems, learning
a network to predict the null-space projection `S x*` from measurements y,
because "conventional methods leave the null-space uncontrolled"; **deep null
space learning** for inverse problems with convergence rates
[search return: https://iopscience.iop.org/article/10.1088/1361-6420/aaf14a];
**Safe Regularization in the Null Space of Batch Activations**
[search return: https://link.springer.com/chapter/10.1007/978-3-030-61616-8_18]
— a side objective optimized only in the null space of batch activations so it
cannot disturb the main objective.
→ "Control what the model does in the direction the data cannot see" is a
**named, populated idea** in inverse problems and in multi-objective network
training. What is NOT retrieved is its use for the null space of a **parametric
design matrix at N=5** with the missing direction supplied by **coarse-solve
data at other parameter values**.

## Interpretation

E1's estimator is preempted at the mechanism level twice over (LR-MFS; the
data-poor projection-based MF linear regression by title), and the "exactly
affine benchmark" observation is standard RB-regime knowledge rather than a
finding. E3(c) is preempted in spirit by null-space-controlled learning in
inverse problems, but not in this composition. The one surface that has
survived two independent refutation attempts is the **training-free
per-dataset gate** (turn 2, term 3: explicit engine miss) and the **matched
with/without-LF value-of-information measurement at N_hf = 5** (batch 1,
iteration 3, term 3: explicit engine miss).
