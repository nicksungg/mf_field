# Iteration 4 — refutation turn 2: the decisive E1/E2 hit

## Search rationale

Iteration 3 surfaced a data-poor projection-based MF *linear regression* paper
by title only (PDF fetch failed). Because that title covers E1 almost exactly,
turn 4 spends a term retrieving a readable version. Term 2 re-attacks the one
measurement batch 1 declared unclaimed (matched with/without-LF value of LF) —
if it exists anywhere, round-2 criterion 1 must be reframed. Term 3 attacks
B1's "architecture tax" observation (a 4.8M-parameter decoder loses to OLS on
an exactly linear problem), which B2 may want to claim.

## Search terms used

1. `Sella Pham Chaudhuri Willcox projection-based multifidelity linear regression data-poor abstract`
2. `how much does low-fidelity data help ablation quantify value of low-fidelity training data multi-fidelity surrogate matched budget with without`
3. `neural network fails to recover exactly linear solution map worse than ordinary least squares operator learning overparameterized small sample`

## Findings

### Term 1 — DECISIVE for E1 and E2

The paper is **Sella, Pham, Chaudhuri & Willcox, "Projection-based
multifidelity linear regression for data-scarce applications"**, AIAA SciTech
2023-0916, journal version in *Machine Learning for Computational Science and
Engineering* (2025), DOI 10.1007/s44379-025-00049-5, preprint
**arXiv:2508.08517** [search returns:
https://dx.doi.org/10.2514/6.2023-0916,
https://link.springer.com/article/10.1007/s44379-025-00049-5,
https://arxiv.org/pdf/2508.08517].

**Fetched — arXiv:2508.08517** [cite: https://arxiv.org/pdf/2508.08517]
(quotes below are the fetcher's rendering of the PDF, marked as such):
- Three multifidelity **linear regression** methods, all with **POD projection
  of high-dimensional outputs**: (i) additive **Kennedy-O'Hagan** discrepancy
  ("the HF response is modeled as the LF response plus a discrepancy term"),
  (ii) **direct data augmentation** with LF data, (iii) **regression-mapping
  data augmentation** (map LF through a fitted LF→HF regression, then augment).
- Outputs are **high-dimensional QoIs / fields**; POD "projects high-dimensional
  outputs onto a low-dimensional subspace".
- **"LF data can be evaluated at parameter values where no HF data exists"** —
  LF and HF samples "need not be at identical parameter values", and exploiting
  cheap simulations at unexplored parameter regions is stated as the point.
- The paper **compares against HF-only regression**, concluding "when LF data
  quality is high, multifidelity approaches provide benefits; conversely, poor
  LF data can degrade predictions" relative to HF-only.
- Regime: **data-scarce**, very limited HF samples.

→ This is E1 **and** E2 **and** the with/without-LF contrast, in one paper:
linear MF regression, field-valued outputs, LF at parameter values with no HF
data, few HF samples, HF-only baseline, and the finding that LF can *hurt*.
Batch 1's `novel` verdict for D3 ("LF-as-parameter-coverage") does not survive
this retrieval and is **superseded** (batch 1's searches used PDE/neural-operator
vocabulary; this literature is AIAA/UQ surrogate vocabulary).

### Term 2 — the value-of-LF ablation

Returns: arXiv:2404.14456 (MF surrogates: a data-fusion perspective)
[search return: https://arxiv.org/abs/2404.14456];
PRICAI 2025 "Efficient Selection of Low-Fidelity Data for Multi-fidelity
Surrogate Models" [https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32];
"A novel low-fidelity-guided design of experiments"
[https://www.sciencedirect.com/science/article/abs/pii/S1474034625009693];
non-hierarchical LF fusion [S1270963824000610]. Engine synthesis: "Not all
low-fidelity data necessarily improves model performance ... choosing
low-fidelity data that is 'more similar' to high-fidelity data will result in
better performance"; the value of LF is "conditional".
→ The *qualitative* statement "LF does not always help, and can hurt" is
established (and now also directly evidenced by arXiv:2508.08517's HF-only
comparison). What still returned **nothing** is a matched-architecture,
matched-budget, **per-dataset** with/without-LF accounting for **neural**
field surrogates at N_hf ≈ 5 with a certified noise floor — the specific shape
of round-2 criterion 1. Two independent search framings (batch 1 iteration 3
term 3; here) have now missed it.

### Term 3 — neural nets vs OLS on linear problems

Returns: arXiv:2209.15265 [search return: https://arxiv.org/pdf/2209.15265]
"Overparameterized ReLU Neural Networks Learn the
Simplest Models: Neural Isometry and Exact Recovery" (**FETCH FAILED** —
binary PDF unparseable; nothing claimed from the text beyond the
search-returned synthesis); arXiv:2406.18035 (local linear recovery guarantee
at overparameterization); arXiv:1905.10826; arXiv:2605.27097. Engine synthesis
of 2209.15265: "when the ratio of samples to dimension (n/d) is below a
critical threshold, the linear solution is not the unique optimal solution, and
neural networks overfit ... when n < 2d for Gaussian data, the theory predicts
failure to recover linear models uniquely."
→ **"An overparameterized network fails to recover a linear ground-truth map
below a sample threshold" is published theory** (regularized ReLU networks,
Gaussian data). B1's ifc_poisson observation (n=5 HF rows, d=6 coefficients,
network 60x worse than OLS) is a *field-surrogate instance* of that regime, not
a new phenomenon. It should be cited, not claimed.

## Interpretation

The refutation turn found the paper that preempts the stream's most attractive
B2 direction end-to-end. What remains genuinely unretrieved after four turns is
narrow and specific: (1) a **training-free, per-dataset decision rule** for
whether to use the LF channel at all (turn 2 term 3: explicit engine miss);
(2) the **matched with/without-LF measurement for neural condition→field
surrogates at N_hf ≈ 5 against a certified seed-noise floor** (two independent
misses); (3) any instance of the LF-signal question where the LF rungs are
**fully condition-aligned** (the five sharp datasets) so that LF can only carry
spectral truncation — the nested-ladder degeneracy, which the MF literature
never treats because it always assumes LF adds coverage or cheaper samples.
One more turn is warranted to attack (1), the last surface with claimable
substance.
