# Iteration 3 — Q4: the deferred overfitting-anatomy direction (batch 1 rated it LOW confidence and demanded a fresh pass)

## Search rationale

`websearches/r2s4_diag/batch_1/report.md` closed with "D3 is under-searched … ask
for a fresh websearch batch first". Program.md 12.4 names the components:
train/test gap decomposition at N_hf in {5,20,50} (ifc ladder) and N=400 (sharp),
plus **effective sample counts** and the drift-class rule (n_eff/N < 1% => only
in-job paired controls are controls). Three terms, one per component: the
decomposition, the n_eff estimator, and the HF-sample learning curve for
operator learning.

## Search terms used

1. `generalization gap decomposition train test error diagnosis small sample deep learning bias variance noise decomposition`
2. `effective number of independent training samples redundancy dataset deep learning estimate`
3. `how many high-fidelity samples needed neural operator learning curve sample complexity sweep 5 20 50 samples`

## Findings

### Term 1 — gap decomposition

Confirms batch 1's read: the decomposition itself is textbook and generic
("Test Error = Train Error + Generalization gap"; bias-variance-**noise**, the
third term being "irreducible error resulting from noise in the problem
itself"), with variance further attributed to sampling / optimization /
label noise. Nothing PDE- or operator-specific; nothing that would make a
decomposition protocol novel. Results (none fetched, all generic references):
https://arxiv.org/pdf/2011.03321 (fine-grained bias-variance decomposition for
double descent), https://arxiv.org/pdf/2010.08127 (Deep Bootstrap),
https://arxiv.org/pdf/2203.10036, https://arxiv.org/html/2604.12827,
https://www.emergentmind.com/topics/generalization-error-in-deep-learning.
Note for us: the *noise* term of that decomposition is exactly the aleatoric
barrier B1 already measured — i.e. the decomposition and the ceiling estimator
are the same instrument seen from two sides, which is a useful unifying framing
but not a new one.

### Term 2 — effective sample size / redundancy

Still **no PDE-domain n_eff estimator**, matching batch 1's dead end. The
nearest published handle is dataset-redundancy pruning:

- "Less is More: An Exploration of Data Redundancy with Active Dataset
  Subsampling" — https://arxiv.org/abs/1905.12737v1 — **FETCHED**: redundancy is
  identified by "ensemble based uncertainty estimation"; removable subsets are
  "up to 50% of the full dataset"; the abstract does **not** define an effective
  sample size statistic. Demonstrated on CIFAR/ImageNet, not on PDE fields.
- Also surfaced, unfetched:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC10659445/ (entropy-based semantic
  redundancy scoring; snippet defines a point as redundant if removing it
  degrades test accuracy by <10%),
  https://www.sciencedirect.com/science/article/pii/S0895611124000569.

### Term 3 — HF sample complexity for operator learning

- "The Sample Complexity of Learning Lipschitz Operators with respect to
  Gaussian Measures" — https://arxiv.org/abs/2410.23440 — **FETCHED**, and the
  strongest theoretical anchor found this batch: "No method to approximate
  Lipschitz operators based on m linear samples can achieve algebraic
  convergence rates in m"; the paper "tightly characterize[s] the … smallest
  achievable worst-case error among all possible choices of (adaptive) sampling
  and reconstruction strategies"; convergence "arbitrarily close to any
  algebraic rate" is recovered only under "sufficiently fast spectral decay of
  the covariance operator of the underlying Gaussian measure"; it "confirms the
  intrinsic difficulty of learning Lipschitz operators, regardless of the data
  or learning technique".
- The specific 5/20/50 sweep granularity has **no published counterpart** in
  these results (search engine said so explicitly). Other results, unfetched:
  https://www.sciencedirect.com/science/article/abs/pii/S0045782525009478
  (optimal experimental design for operator-learning data generation),
  https://arxiv.org/pdf/2605.22724 (multi-task operator rates).

## Interpretation

The overfitting-anatomy direction is now searched twice and the picture is
stable: the decomposition machinery is generic textbook material (not novel, but
also not contested), no PDE-domain n_eff estimator exists in either batch's
searches, and the one genuinely load-bearing citation is arXiv:2410.23440's
**negative** result — worst-case operator learning admits no algebraic rate in m
unless the input measure's covariance decays fast, which is a principled reason
to expect the N_hf = 5 ifc_poisson column to be information-starved rather than
architecture-starved. A B2/B3 card can now lean on D3, but only if it frames the
contribution as *measurement on this panel* (with the ceiling as the noise term
of the decomposition), never as a new diagnostic method.
