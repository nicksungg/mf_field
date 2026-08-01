# Iteration 5 — refutation pass 2 + THE PRIOR-ART VERDICT (final turn, cap 5/5)

**Cap note**: this is turn 5 of a maximum 5. Terms per turn were ≤3 on every turn. Unlike
batch 3, the cap is **respected** here.

**Tooling**: `WebFetch` disabled throughout; all quotations `[bash-fetched]` via urllib
(`scratchpad/abs.py`, `scratchpad/fetch.py`) or the NCBI **eutils** API. No `/pdf/` URLs.

## Search rationale

Two remaining refutation obligations: (i) A's non-nested/attribution component — is there a
published *assessment* of what a non-nested MF ladder supports (the iopscience item I could
not fetch in iteration 2)? (ii) B (close now) — is there methodology that makes a
pre-registered "unclaimable"/null outcome *informative*, which is the exact hinge of B3
part 7's counter-argument? Plus one last attempt at a decision rule for "MF not worth it at
tiny HF budget".

## Search terms used

1. `non-nested multi-fidelity data cannot attribute improvement to fidelity confounded comparison independent designs per level limitation`
2. `pre-registered null result "not enough power" diagnostic study reports inconclusive outcome value of stopping a research line machine learning`
3. `scientific machine learning surrogate fails at very small high fidelity budget when is multi-fidelity not worth it decision rule`

## Findings

### Term 1 — assessing non-nested MF configurations (**the iteration-2 gap, now closed**)

The search surfaced an **arXiv mirror of the captcha-blocked iopscience article**:
https://arxiv.org/html/2407.17087 (= 10.1088/2632-2153/ad7f25). Fetched successfully.

**Fetched 1** — https://arxiv.org/abs/2407.17087 , Vinod, Zaspel et al., "Assessing
Non-Nested Configurations of Multifidelity Machine Learning for Quantum-Chemical
Properties" [bash-fetched]: "**In some multifidelity models, the training data is required
to be nested, that is the same molecular geometries are included to calculate the property
across all the fidelities. In these multifidelity models, the requirement of a nested
configuration restricts the kind of sampling that can be performed** while selecting
training samples at different fidelities. This work assesses the use of **non-nested
training data** for two of these multifidelity methods, namely MFML and optimized MFML
(o-MFML) … **Results indicate that the MFML method still requires a nested structure of
training data across the fidelities. However, the o-MFML method shows promising results for
non-nested multifidelity training data with model errors comparable to the nested
configurations.**"
The engine additionally reported (search-result confidence): "The conventional MFML model
**breaks down with a non-nested multifidelity training dataset and fails to provide any
reasonable improvement** for the different baseline fidelities."
Other results: https://arxiv.org/pdf/2006.16728 , https://www.oaepublish.com/articles/jmi.2025.85 ,
plus researchgate/springer items (blocked list, not fetched).

*Reading*: **the "does non-nestedness invalidate the MF claim?" question is published and
answered method-by-method** — nested-requiring methods break down, one reformulation
survives. So an ifc card may NOT claim novelty for discovering that its unpaired ladder
limits MF claims. It CAN cite this as the reason its ladder rungs must be treated as
independent designs. Domain gap: scalar quantum-chemical properties + kernel ridge, not
field-valued PDE surrogates, and no train/test-gap anatomy anywhere in it.

### Term 2 — making a null / "unclaimable" outcome informative

Results: https://pmc.ncbi.nlm.nih.gov/articles/PMC6412612/ (PMC blocked → routed via
eutils), https://arxiv.org/pdf/2010.10513 (does preregistration improve credibility),
https://www.researchgate.net/publication/398749214_... (blocked),
https://www.sciencedirect.com/science/article/pii/S1566253525001952 (blocked),
plus tertiary blogs.

**Fetched 2** — PubMed **30873486** via NCBI eutils
(https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=30873486 ),
Harms & Lakens, "Making 'null effects' informative: statistical techniques and inferential
frameworks", *J Clin Transl Res* 3(Suppl 2):382–393, 2018 [bash-fetched]: "To draw
informative conclusions from null-effects, researchers need to **move beyond the incorrect
interpretation of a non-significant result in a null-hypothesis significance test as
evidence of the absence of an effect. We explain how to statistically evaluate null-results
using equivalence tests, Bayesian estimation, and Bayes factors** … **no statistical
approach can actually prove that the null-hypothesis is true** … demonstrating the absence
of differences is an equally important statistical question."

The engine also surfaced (search-result confidence, unattributed): "The most practical way
to detect underpowering is to look at the confidence interval; if it includes both the
minimum clinically important difference and the null, the trial is underpowered and the
result is inconclusive" — and, for ML specifically, "**no power analyses were noted in any
of the machine learning papers reviewed**".

*Reading*: this is the direct answer to B3 part 7's counter-argument. "Unclaimable" is only
uninformative if it is reported as a failed significance test. With the round's certified
`min_claimable_effect` in hand (ifc 0.93770), the SAME measurement becomes an **equivalence
test**: either the train/test gap difference across rungs is inside ±MCE (informative: the
ladder does not move the gap by an amount this round could act on) or the CI straddles both
MCE and zero (inconclusive/underpowered — and that is diagnosable *in advance*).

### Term 3 — a decision rule for "MF not worth it at tiny HF budget"

Results: https://arxiv.org/pdf/2403.08627 , https://royalsocietypublishing.org/doi/10.1098/rspa.2023.0655 ,
https://arxiv.org/pdf/2511.01830 (already binding from batch 1/2),
https://arxiv.org/pdf/2607.23404 , https://arxiv.org/pdf/2111.02960 , plus ScienceDirect
items (blocked). The engine closed with: "the specific decision rule for when multi-fidelity
becomes worthless with very small high-fidelity budgets **is not explicitly addressed** in
these results."

**Fetched 3** — https://arxiv.org/abs/2403.08627 , "Multifidelity linear regression for
scientific machine learning from scarce data" [bash-fetched]: "in many scientific and
engineering settings, generating high-fidelity data … is expensive, and the available budget
… is limited, so that **high-fidelity training data are scarce. ML models trained on scarce
data have high variance, resulting in poor expected generalization performance.** … We use
the multifidelity data within an approximate control variate framework to define new
multifidelity Monte Carlo estimators for linear regression models. We provide **bias and
variance analysis** of our new estimators … Numerical results demonstrate that our
multifidelity training approach achieves similar accuracy to the standard high-fidelity only
approach with **orders-of-magnitude reduced high-fidelity data requirements**."

*Reading*: the *diagnosis* "at scarce HF, variance dominates and generalization is poor" is
published with bias/variance theory. An ifc card must therefore not present
variance-domination at N_hf = 5 as a finding; it may cite this and measure the **magnitude**
in the round's own units. No decision rule for abandoning MF at a budget threshold exists —
fourth independent failure for a pre-training feasibility criterion across batches 2–4.

---

## PRIOR-ART VERDICT (mandatory)

### Candidate A — ifc_poisson overfitting anatomy at N_hf ∈ {5, 20, 50} (§12.4 mandate)

**Verdict: `preempted-but-MF-composition-open`.**

Preempted components, each with a fetched citation:
- *Non-nestedness limits MF claims, method-by-method* — https://arxiv.org/abs/2407.17087
  ("the MFML method still requires a nested structure of training data across the
  fidelities. However, the o-MFML method shows promising results for non-nested … data").
  The card may not claim this as a finding.
- *Paired-vs-unpaired is a standard MF-with-functional-outputs distinction* —
  https://arxiv.org/abs/2408.17075 / https://arxiv.org/html/2408.17075v2 ("either with a set
  of correspondences between some input samples from the distinct datasets, or without …
  snapshots … obtained for the same input variables values for different fidelity levels").
- *Scarce HF ⇒ high variance ⇒ poor generalization* — https://arxiv.org/abs/2403.08627
  (with bias/variance analysis). Not a finding; a citation.
- *A tiny HF budget throttles usable LF and blunts the MF advantage* —
  https://arxiv.org/html/2408.17075v2 ("a small number of high-fidelity snapshots limits the
  number of exploitable low-fidelity snapshots. Hence, the surrogate may not take full
  advantage of the multi-fidelity context").
- *3-point learning curves cannot be fitted or extrapolated; curves can be ill-behaved* —
  https://arxiv.org/abs/2103.10948 ("no universal model can be identified"; "ill-behaved,
  showing worse learning performance with more training data") and
  https://arxiv.org/abs/2211.14061 ("more data does not necessarily lead to better
  generalization performance"). The card must not call its ladder a scaling law.

What remains open (the MF composition):
**No fetched source performs a train-vs-test error decomposition for a field-valued
condition→HF surrogate at single-digit HF sample counts.** The nearest neighbour is the
CMAME MF-functional-output benchmark (2408.17075), which sweeps training-set size and
decomposes error by *source* (Appendix D: "Decomposition of the normed RMSE into normed DR
and intermediate surrogate modeling RMSE") but whose full text returned **NOT FOUND** for
"learning curve", "overfit", and "training set sizes". The operator-learning theory closest
to the ifc PDE class is asymptotic in n (https://arxiv.org/abs/2412.17582 , parametric
elliptic PDE), silent at n = 5. "Few-shot operator learning" in the literature means
few shots of a *new* PDE family after multi-family pretraining
(https://arxiv.org/abs/2508.01211), which is not this regime. Also open and uncited: doing
any of this **in copy-LF-skill units against a pre-certified per-dataset
min_claimable_effect**.

Explicitly **NOT** open: the n_eff / effective-sample-size diagnostic (iteration 4 term 2 —
**no usable results**; the literature offers redundancy *pruning* instead, which batch 3
already ruled `preempted`). Demote n_eff to a descriptive statistic, do not claim it.

### Candidate B — close the stream now

**Verdict: `preempted (cite)` — as a *methodological* act, and it is the weaker of two
published options.**

- Futility stopping is the formal name for "close unless still reachable", and it is
  standard: Lachin 2005, **PubMed 16134130**, *Stat Med* 24(18):2747–2764, doi 10.1002/sim.2151
  (https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=16134130 ) — "a CP
  computation at a pre-specified point in the study … is used as the basis for early
  termination for futility when there is little evidence of a beneficial effect", with the
  explicit price that "the probability of a type II error beta increases from the level
  specified in the study design" and must be *controlled at a desired level*. A close-now
  with no stated futility argument is an uncontrolled type-II inflation.
- The benchmark-lifecycle literature argues **against** retiring on the headline number:
  https://arxiv.org/abs/2606.26158 ("When a benchmark's accuracy saturates, it is often
  retired and replaced … We show that this approach privileges accuracy and misses the
  opportunity to study six other key dimensions"; "despite accuracy saturation, CORE-Bench
  v1.1 **remains useful** for measuring efficiency, reliability, model performance, and
  scaffold performance"). Note the mirror-image caveat: those papers treat *saturation*
  (target met), not *infeasibility* (target unmet) — **no fetched source retires a criterion
  for infeasibility**, so "close because the target is probably unreachable" is NOT
  retrieval-supported.
- The strongest published alternative to closing is to convert the feared "unclaimable"
  into an **equivalence-test** result: Harms & Lakens, PubMed 30873486 — "move beyond the
  incorrect interpretation of a non-significant result … as evidence of the absence of an
  effect … evaluate null-results using equivalence tests, Bayesian estimation, and Bayes
  factors". The round already has the ingredient an equivalence test needs (a certified
  per-dataset `min_claimable_effect`), which most ML work does not.

## Interpretation

Both candidates are grounded. A's *mechanism* is preempted in pieces but its **composition**
— train/test gap anatomy for a field-valued condition→HF surrogate at N_hf ∈ {5, 20, 50},
scored in copy-LF skill against a pre-certified MCE, on an explicitly non-nested ladder — is
not found in any fetched source. B is a legitimate, citable act, but the fetched literature
says a close-now must carry a futility argument with acknowledged type-II inflation, and
that the "unclaimable" fear that motivates it is itself remediable by pre-registering an
equivalence test rather than a significance test.
