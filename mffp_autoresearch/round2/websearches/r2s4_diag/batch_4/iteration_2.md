# Iteration 2 — unpaired/non-nested MF ladders, and whether a 3-point learning curve supports any claim

**Tooling**: `WebFetch` still disabled; all quotations `[bash-fetched]` via
`scratchpad/fetch.py` / `scratchpad/abs.py` (urllib GET, HTML→text). No `/pdf/` URLs.

## Search rationale

Two decisive framings for the candidate card. (1) The ifc ladder is **unpaired**:
independent condition draws per rung, min condition distance 0.08–0.30, never 0 (B2;
r2s2-B1 builder + reviewer). Statistics has a name for this — **non-nested experimental
design** — and if the literature already states which MF claims survive non-nestedness,
that is either a preemption or a citation the card must carry. (2) The card would read
a **3-point learning curve** (N_hf = 5, 20, 50). Before proposing it I need the
learning-curve literature's own view of what a 3-point curve at single-digit N can
support — that is exactly the risk in B3 part 7's "unclaimable" counter-argument.

## Search terms used

1. `multi-fidelity dataset unpaired samples independent parameter draws per fidelity level non-nested design what claims are valid`
2. `nested versus non-nested experimental design multi-fidelity surrogate cokriging requires shared inputs correlation estimation`
3. `learning curve extrapolation unreliable few data points estimating sample complexity from small training set sizes`

## Findings

### Term 1 — unpaired / non-nested MF data

Results: https://arxiv.org/html/2511.20183 , https://iopscience.iop.org/article/10.1088/2632-2153/ad7f25 ,
https://arxiv.org/html/2601.22371 (FIRE), https://dl.acm.org/doi/10.1007/s00158-020-02583-7 (GCK),
https://arxiv.org/html/1609.07196v5 (review of MF models), https://arxiv.org/pdf/2503.23158 .

The engine's synthesis (unattributed, recorded but NOT citable) claimed: "baseline
methods degrade when inputs are unpaired"; "Nested designs, and in particular the
Coupled Nested design, offer better parameter estimation for multi-fidelity surrogate
models"; "although the nested design assumption simplifies model construction and can
yield superior performance, it is often violated in practice".

**Fetched 1** — https://arxiv.org/abs/2511.20183 , Baillie, Kerleguer, Feau & Garnier,
"Multi-fidelity Gaussian process regression for noisy outputs and non-nested
experimental designs: a comparison between the recursive and non-recursive
formulations" (v2, 20 May 2026) [bash-fetched]: "This paper investigates a recursive
formulation of auto-regressive multi-fidelity Gaussian process regression in **the
challenging setting of noisy and non-nested high- and low-fidelity data**. We propose a
decoupled optimization strategy based on the expectation-maximization algorithm, which
exploits the structure of the recursive model … This approach is compared with the fully
coupled likelihood maximization of the classical non-recursive formulation introduced by
Kenned[y and O'Hagan]".
*Reading*: non-nestedness is a **named, actively-methodologised difficulty**, not a
project-local defect — the card may (and should) call the ifc ladder "non-nested" and
cite this rather than inventing "unpairable". Crucially it is a *method* paper (make
AR(1) MF-GP work without nesting); it does not certify which *diagnostic* claims a
non-nested ladder supports.

**Fetch failure** — https://iopscience.iop.org/article/10.1088/2632-2153/ad7f25
("Assessing non-nested configurations of multifidelity machine learning for
quantum-chemical properties") returned a **Radware Bot Manager captcha page**, not
content. Recorded as search-result-confidence only; add `iopscience.iop.org` to the
blocked-fetch list alongside `sciencedirect`, `springer`, `ncbi`. Its *title* is the
single most on-point item found ("assessing non-nested configurations"), and I could
not read it — this is an honest gap in the verdict below.

### Term 2 — nested vs non-nested, the pairing requirement stated explicitly

Results: https://arxiv.org/html/2511.20183 (again),
https://www.researchgate.net/publication/341404887_... (improved co-Kriging for
non-nested sampling data), https://www.sciencedirect.com/science/article/abs/pii/S2352012425024324 ,
https://link.springer.com/article/10.1007/s00158-020-02583-7 ,
https://arxiv.org/pdf/1909.01836 .

The engine stated the definition plainly: "A nested design of experiment (DOE) assumes
that the high-fidelity (HF) sample set is a **strict subset** of the low-fidelity (LF)
data. In contrast, non-nested data occurs when partial LF data are missing, violating
the nested assumption", and that prevalent methods "rely on estimates for correlation
hyperparameters obtained via maximum likelihood estimation … which can introduce
**estimation bias and additional uncertainty**". Attempted fetches on the springer,
sciencedirect and researchgate items were **not made** — all three domains are on the
batch-2/3 blocked-fetch list (403) and researchgate hard-blocks bots; nothing new is
citable from this term beyond the already-fetched 2511.20183.

### Term 3 — what a 3-point curve at tiny N supports

Results: https://arxiv.org/pdf/2103.10948 , https://arxiv.org/pdf/2211.14061 ,
https://www.jmlr.org/papers/volume26/23-0292/23-0292.pdf ,
https://ada.liacs.nl/papers/KieEtAl24.pdf , https://arxiv.org/pdf/2307.00374 ,
https://arxiv.org/pdf/2606.24903 .

**Fetched 2** — https://arxiv.org/abs/2211.14061 , Loog & Viering, "A Survey of Learning
Curves with Bad Behavior: or How More Data Need Not Lead to Better Performance" (25 Nov
2022) [bash-fetched]: "The larger part of this survey's focus … is on learning curves
that show that **more data does not necessarily lead to better generalization
performance**. A result that seems surprising to many researchers in the field of
artificial intelligence."

**Fetched 3** — https://arxiv.org/abs/2103.10948 , Viering & Loog, "The Shape of Learning
Curves: a Review" [bash-fetched]: "We discuss empirical and theoretical evidence that
supports well-behaved curves that often have the shape of a power law or an exponential
… We draw specific attention to examples of learning curves that are **ill-behaved,
showing worse learning performance with more training data**. … our review underscores
that learning curves are surprisingly diverse and **no universal model can be
identified**."

The engine also surfaced (unattributed, recorded not cited): "Evaluation of extrapolation
performance is extremely difficult in practice because the region targeted by
extrapolation has by definition few data points, and therefore classical
cross-validation is not applicable."

## Interpretation

Two hard constraints land on the candidate card, both now retrieval-grounded. (a) The
ifc ladder's defect has a published name — **non-nested design** — with an active
methods literature (arXiv:2511.20183) but no fetched source certifying which diagnostic
claims survive it; the one paper that appears to ask exactly that question is
captcha-blocked. (b) A 3-point learning curve cannot be extrapolated or fitted to a
functional form: Viering & Loog say directly that "no universal model can be identified"
and that curves can be ill-behaved (worse with more data). So an ifc card must be
framed as **three independent point measurements of the train/test gap**, never as a
"scaling law" or a "sample-complexity estimate" — and its non-monotone outcome
(N_hf = 50 worse than 20) would be a *published phenomenon*, not a bug.
