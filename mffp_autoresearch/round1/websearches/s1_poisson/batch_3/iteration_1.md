# Iteration 1 — task (a): post-hoc per-sample output calibration heads

## Search rationale
The B3 card class is "freeze the operator, add one head that predicts a per-sample
scalar gain g(X) and multiply the output by it". Before anything MF-specific, I
must know whether that object — a post-hoc multiplicative output-calibration head
on a frozen regression/operator model — is generic published machinery. s5-B2
already mapped the RevIN/APEX territory from the *knob* side; my job is the *head*
side, and to fetch APEX first-hand so it can be cited here (recall and another
stream's report are not citations for my verdict).

## Search terms used
1. `post-hoc multiplicative bias correction head frozen surrogate model per-sample scalar gain predicted from input parameters`
2. `neural operator output amplitude calibration head predict per-sample scaling factor from PDE parameters`
3. `learned output rescaling head trained on auxiliary cheap data applied to expensive target regression calibration transfer`

## Findings per term

### Term 1
Top returns: CHRep post-hoc calibration for gene expression
(https://arxiv.org/pdf/2604.21573); a USPTO patent on post-hoc improvement of
instance-level prediction metrics
(https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11734585);
"Mean-Model Bias Correction Method"
(https://link.springer.com/chapter/10.1007/978-3-031-99155-4_11); frozen surrogate
variable analysis (https://arxiv.org/abs/1301.3947,
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4179553/).
Engine-synthesised statements worth recording (search-return grade, NOT fetched):
- **multiplicative vs additive bias correction is a named choice in surrogate
  modelling**, and "additive bias correction is sometimes preferred as it is more
  robust in cases of small values of the objective function"
  (search return over the Springer chapter — *cross-host/auth wall expected per
  batch-2 dead-ends, not fetched*).
- **fSVA** "borrows strength from a training set for individual sample batch
  correction" (https://arxiv.org/abs/1301.3947) — the *borrow-strength-for-
  per-sample-correction* idiom exists outside PDEs, in genomics.
No PDE/operator source. Verdict for this term: the generic machinery exists in
other fields; nothing on operator outputs.

### Term 2
Returns were architecture papers, not calibration:
https://arxiv.org/html/2507.18067v1 (multiscale neural PDE surrogates /
downscaling), https://arxiv.org/html/2406.03923 (Latent Neural Operator),
https://arxiv.org/pdf/2605.15793 (AOT-POT), https://arxiv.org/html/2505.20721
(Recurrent Neural Operators), https://arxiv.org/pdf/2605.25353 (PDEInvBench).
One engine-synthesised statement (search-return grade): "an MLP generates
parameter-dependent scaling factors that modulate the base spectral filters …
low-frequency modes for high-viscosity flows" — i.e. parameter-conditioned
scaling **inside** the spectral layers (this is FiLM-family conditioning, which
the base already has), not an **output** gain. The engine explicitly reported
that "the specific concept of an 'output amplitude calibration head' that
predicts per-sample scaling factors directly from PDE parameters wasn't
explicitly detailed in these particular results."

### Term 3
Returns: https://arxiv.org/pdf/2506.14963 (Understanding multi-fidelity training
of machine-learned force-fields — **per-fidelity heads**, "how the accuracy of
auxiliary labels relates to target task performance"); Oxford/JRSSB transfer
learning for high-dimensional linear regression
(https://academic.oup.com/jrsssb/article/84/1/149/7056104);
https://arxiv.org/pdf/1612.01020 (**Hypothesis Transfer Learning via
Transformation Functions** — "constructs auxiliary regression functions trained
on target domain data to transform source domain predictions"); post-hoc
calibration topic page (https://www.emergentmind.com/topics/post-hoc-calibration-methods);
https://arxiv.org/html/2402.12736v1 (Calibration Side-Tuning);
https://arxiv.org/pdf/2011.05493 (auxiliary outcomes: "pooled estimator using all
outcomes to borrow information from auxiliary outcomes, followed by a calibration
procedure to reduce bias").
Two of these are directly on the card's mechanism class and are carried into
iteration 2 for fetching: **1612.01020** (learned transformation of a frozen
model's output) and **2506.14963** (MF heads with auxiliary-fidelity labels).

### Fetch — APEX (the strongest known threat, from s5-B2's report)
https://arxiv.org/abs/2605.26732 (**fetched**). Definitions obtained first-hand:
"A lower-frequency neural operator first provides a coarse prediction in the
target-frequency regime, from which we retain only the amplitude as a
transferable structural anchor." Setting: "higher-frequency prediction under
scarce target supervision" where "higher-frequency data are substantially more
expensive to simulate or measure than lower-frequency data". Mechanism rationale:
"coarse amplitude structure remains relatively stable across frequencies, whereas
phase-sensitive oscillatory structure deteriorates much more rapidly as frequency
increases." The fetch states the anchor is **a spatial field retained from the
coarse prediction**, not a per-sample scalar, and the fidelity axis is
**frequency**, not grid resolution.

## Interpretation
Post-hoc multiplicative output calibration is generic, published machinery in
other fields (surrogate bias correction, fSVA, hypothesis-transfer transformation
functions) and *is not* documented as an output head for neural operators in
anything returned here. APEX is the nearest MF neighbour but differs on two
axes that matter for the verdict: its anchor is a **field**, taken from a coarser
model's **prediction**, whereas the card's g(X) is a **scalar fitted against
targets on pooled lower-fidelity rows**. The exposed risk is not APEX but the
generic-machinery argument: "learn a multiplicative correction from cheap data,
apply it to the expensive regime" has named prior art outside PDE ML, so the
novelty claim must be the MF composition, never the head.
