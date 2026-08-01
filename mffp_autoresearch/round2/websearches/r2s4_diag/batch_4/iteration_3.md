# Iteration 3 — the close-now half: criterion retirement, futility stopping, attainability

**Tooling**: `WebFetch` disabled; all quotations `[bash-fetched]` via urllib
(`scratchpad/abs.py`, plus one NCBI **eutils** API call for a PubMed-only item).
No `/pdf/` URLs.

## Search rationale

B3 part 7 puts two decisions on the brainstormer: run the ifc card, or close. The
close-now half needs its own prior-art grounding, and I have not searched it at all in
three batches. Three framings, chosen to be independent: benchmark/criterion
**retirement** methodology (does the field have a rule for retiring a target?), the
**futility-stopping** literature (the statistically formal version of "close unless
still reachable"), and **attainability estimation** (can you decide a target is out of
reach before spending the run?).

## Search terms used

1. `machine learning benchmark design when to retire a task saturated or unattainable target metric methodology`
2. `futility analysis stopping rule conditional power abandon arm interim analysis underpowered experiment`
3. `deciding whether target accuracy is attainable given dataset size irreducible error estimate before further experiments`

## Findings

### Term 1 — benchmark/criterion retirement

Results: https://arxiv.org/html/2602.16763v1 , https://arxiv.org/html/2606.26158 ,
https://arxiv.org/html/2503.05551v1 , https://arxiv.org/pdf/2602.18029 ,
https://mbrenndoerfer.com/writing/benchmark-saturation-ai-evaluation-metrics (tertiary),
https://www.statsig.com/perspectives/slug-benchmark-saturation-metrics-stop (tertiary).

**Fetched 1** — https://arxiv.org/abs/2602.16763 , "When AI Benchmarks Plateau: A
Systematic Study of Benchmark Saturation" [bash-fetched]: "benchmarks quickly
'saturate', making it difficult to differentiate models and diminishing their long-term
value. In this study, we define benchmark saturation and analyze it across 60 language
model benchmarks using 14 properties that relate to saturation. We find that nearly half
of our benchmarks exhibit saturation, with rates increasing with age."

**Fetched 2** — https://arxiv.org/abs/2606.26158 , "Life After Benchmark Saturation: A
Case Study of CORE-Bench" [bash-fetched]: "**When a benchmark's accuracy saturates, it
is often retired and replaced with a more challenging version. We show that this
approach privileges accuracy and misses the opportunity to study six other key
dimensions** … construct validity issues such as shortcuts, out-of-distribution
generalizability, efficiency, reliability, the relative importance of the model versus
the scaffold, and uplift from human-agent collaboration … **despite accuracy saturation,
CORE-Bench v1.1 remains useful for measuring efficiency, reliability, model performance,
and scaffold performance** … Together, our contributions present a more rigorous
alternative to the dominant accuracy-centric evaluation paradigm."

*Critical reading*: both are about **saturation** (target reached / no longer
discriminative). Our situation is the **mirror image** — the target (ifc_poisson at the
paper bar, nRMSE 0.036) is *un*reached and possibly unreachable at N_hf = 5. Neither
fetched source addresses retiring a criterion for **infeasibility**. But 2606.26158's
argument transfers directly and is the strongest citation for the close-now debate: when
the headline accuracy number stops being informative, the answer is to **keep measuring
the other dimensions** rather than retire — which in our terms is exactly B3 part 7's
"the stream's remaining value is the instrument suite and the standing sentence".

### Term 2 — futility stopping (the formal version of "close unless reachable")

Results: https://www.semanticscholar.org/paper/...Lachin/7d4c09dd... (page fetched
**empty**, JS-only), https://www.researchgate.net/publication/7627254_... (bot-blocked),
https://arxiv.org/pdf/2007.15935 , several clinicaltrials.gov SAP PDFs,
http://onbiostatistics.blogspot.com/2022/01/... (tertiary).
Semantic Scholar's **API also failed (HTTP 429)**.

**Fetched 3** — PubMed record **16134130** via NCBI eutils
(https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=16134130 ),
Lachin, "A review of methods for futility stopping based on conditional power",
*Stat Med* 24(18):2747–2764, 2005, doi 10.1002/sim.2151 [bash-fetched]: "Conditional
power (CP) is the probability that the final study result will be statistically
significant, given the data observed thus far and a specific assumption about the
pattern of the data to be observed in the remainder of the study … a CP computation at a
pre-specified point in the study … is used as the basis for **early termination for
futility when there is little evidence of a beneficial effect** … **As the probability
of stopping increases, the probability of a type I error alpha decreases from the
nominal desired level … while the probability of a type II error beta increases from the
level specified in the study design.** Thus a stopping boundary … can be determined such
that the **inflation in type II error probability is controlled at a desired level**."

*Reading*: this is the citable spine of the close-now decision, and it cuts **both**
ways. Futility stopping is a legitimate, formalised decision — but its cost is a
quantified **type II error inflation**, i.e. closing a stream that would have found
something. The honest form of B3 part 7's recommendation is therefore not "close because
the answer is probably unclaimable" but "close **with a pre-stated conditional-power
argument**" — and note that the CP here is computable in the round's own units: a
per-dataset `min_claimable_effect` of 0.93770 against an ifc skill of ~8.26 with a
single seed.

### Term 3 — attainability / irreducible error before spending the run

Results were tertiary or off-domain: a USPTO patent PDF, a ResearchGate Q&A,
machinelearningmastery.com, a course page, https://arxiv.org/pdf/2511.12698 (hold-out
size), https://arxiv.org/pdf/2202.03856 , https://arxiv.org/pdf/2207.14529 . None fetched
— none is a primary source for "decide attainability of a target error at a given N
before running". **No usable results.** This is the third independent failure across
batches for a *pre-training* feasibility/regime criterion (batch 3's D2b row recorded two
earlier framings, batch 2 one) — the negative is now robust enough to state as such.

## Interpretation

The close-now decision is **not** a novelty question but a methodology question, and the
methodology exists and is citable: futility stopping with controlled type-II inflation
(Lachin 2005), plus the benchmark-lifecycle argument that a criterion which has stopped
being informative should be replaced by measurement along other dimensions rather than
simply retired (arXiv:2606.26158). Nothing found retires a criterion for
**infeasibility**, and nothing supports declaring the ifc target unattainable
*a priori* — so "close because it's probably unclaimable" is not retrieval-supported,
while "close with a pre-registered futility argument" is.
