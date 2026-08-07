# iteration_4 — `r3s1_factorised`, batch 1 (§3.3 continued)

## Search rationale

Turn 3 refuted D1's mechanism with a fetched citation (SST/ERC, arXiv:1211.6581).
Turn 4 attacks the three residues that decide what is still claimable:
(i) has SST/ERC-style target-as-input stacking already been applied to **POD /
modal coefficients of PDE fields** (which would close D1's composition too);
(ii) does a **pre-fit diagnostic for when exploiting target dependence pays**
exist (which would preempt D2); (iii) is a **trivial-baseline reporting
requirement** established for operator-learning / few-HF benchmarks
(which would preempt D3).

**Tooling note:** this box has no `pdftotext` and no `pypdf`, so `arxiv.org/pdf/*`
and publisher PDFs extract to 0 characters. All fetches this loop therefore use
HTML landing pages (`arxiv.org/abs/*`, docs pages). Publisher pages that block
scripted retrieval (MDPI `computation13020058`, Royal Society RSPA, Polimi MOX
PDF) returned 60–233 characters and are recorded as **NOT usable as citations**.

## Search terms used

1. `stacked single-target multi-target regression applied to POD modal coefficients PDE field surrogate prediction`
2. `when does exploiting target dependence help multi-target regression diagnostic input dimensionality number of training samples`
3. `nearest neighbor and mean predictor trivial baselines operator learning benchmark scarce high fidelity samples reporting requirement`

## Findings

### Term 1 — SST/ERC applied to ROM coefficients? Not returned.

Returns: the same MTR papers (Springer
<https://link.springer.com/article/10.1007/s10994-016-5546-z>), multi-fidelity
reduced-order surrogate modelling (Conti et al., RSPA 480:20230655 —
<https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate>,
MOX preprint <https://www.mate.polimi.it/biblioteca/add/qmox/83-2024.pdf>, code
<https://github.com/ContiPaolo/MultiFidelity_POD>), REALM neural-surrogate
benchmark <https://arxiv.org/html/2512.18595>, multi-output regression survey
<https://oa.upm.es/40804/1/INVE_MEM_2015_204213.pdf>.
Fetch attempts on the RSPA page (60 chars) and the MOX/UPM PDFs (0 chars, no PDF
extractor) **failed** — not citable.

The aggregated search return states the standard ROM practice — *"The task
involves learning a surrogate model that represents the mapping from parameters
to POD coefficients. **Multiple independent regression models** can be employed,
each associated with one modal coefficient."* — and returns **no** source that
feeds one modal coefficient's prediction into another's regressor. **No usable
result** connecting SST/ERC to POD/modal coefficient targets. This is the
composition residue that survives for D1.

### Term 2 — pre-fit diagnostic for target-dependence benefit? Not returned.

Returns: MTR via target-specific features
<https://www.sciencedirect.com/science/article/abs/pii/S0950705119300383>; MTR via
random linear target combinations
<https://www.researchgate.net/publication/261761352_Multi-Target_Regression_via_Random_Linear_Target_Combinations>;
self-training MTR with tree ensembles
<https://www.sciencedirect.com/science/article/abs/pii/S0950705117300813>; and
again arXiv:1211.6581. Aggregated search return, verbatim: *"regarding the
specific conditions under which exploiting target dependence helps based on
diagnostic measures like input dimensionality and number of training samples,
the search results indicate that when the discrepancy … is appropriately
mitigated, proposed methods can attain consistent improvements"* — i.e. the MTR
literature reports **average empirical improvement**, and the search returned
**no** dataset-level pre-fit diagnostic keyed on input dimensionality or row
count. **No usable result.**

The nearest published thing remains turn 2's fetched arXiv:2607.06832 (Chen, Fan
& Wang) — pre-fit *design-geometry* diagnostics (directed coverage, directed
proximity, borrowing-potential indices) and a net-benefit criterion for joint vs
separate multi-output kriging, in a **heterotopic-design** setting. That is a
different independent variable (design geometry) from M15's (condition dimension
vs fit rows), and a different predictor structure (joint GP, not a cascade on
predicted targets).

### Term 3 — trivial-baseline reporting requirement? Not returned for this field.

Returns: generic ML baseline pedagogy
<https://bait509-ubc.github.io/BAIT509/lectures/lecture3.html>; ALMANACS
benchmark <https://arxiv.org/pdf/2312.12747> (naive `PREDICTAVERAGE` and
`NEARESTNEIGHBOR` baselines); load-forecasting "are deep models worth it"
<https://arxiv.org/pdf/2501.05000>; ANN-benchmarks (unrelated sense of "nearest
neighbour"). Aggregated search return, verbatim: *"the search results **do not
contain specific information about operator learning benchmarks, requirements
for reporting results on scarce high-fidelity samples**, or detailed
benchmarking standards for operator learning specifically."*

So: train-mean and nearest-neighbour baselines are entirely standard **in
general ML** (and must be declared as such — do not claim them), while a
*mandatory floor battery for parametric-PDE surrogates at N_hf = 5, including a
fitted closed-form affine arm with its oracle-affine residual reported*, was not
returned by any search across this loop or round 2's three loops.

## Interpretation

D1's mechanism is closed (preempted, arXiv:1211.6581) but its **composition**
survives two independent searches: nobody returned SST/ERC-style corrected
target-stacking applied to PDE reduced-basis coefficients. D2's discriminator
survives as a distinct question from the one published criterion
(arXiv:2607.06832 is design-geometry, not condition-dimension). D3 is
prior-art at the level of individual baselines and open only as a **reporting
protocol**. Turn 5 runs the last refutation triplet and records the verdict.
