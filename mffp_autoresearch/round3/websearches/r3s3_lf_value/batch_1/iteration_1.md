# Iteration 1 — r3s3_lf_value, batch 1

## Search rationale

Round 2 already established (and its websearcher already priced) the *genre* of
LF-as-training-only-signal: distillation from an LF-consuming teacher, LF-pretrain
-> HF-finetune, auxiliary multi-fidelity losses, LF-as-coverage. What round 3 changes
is that the condition vector is now **complete** (ADR r3-0001 D1: HF exactly
reconstructible from the condition). That makes the stream's question a specific
theoretical one: **when the target is a deterministic function of the observed input,
what is left for privileged low-fidelity data to supply?** Under the classical LUPI
answer, the remaining channel is a *rate / optimisation* channel, not an *information*
channel — which is exactly the identifiability-vs-trainability question r2s3-B4 left
open on cahn_hilliard. So turn 1 probes three things: (t1) LUPI theory on why
privileged information helps; (t2) the current MF-neural-operator framing of LF as an
auxiliary training signal; (t3) the negative side — documented cases where LF data
hurts, which is what a certified null on the honest panel would look like.

## Search terms used

1. `learning using privileged information theory why it helps optimization rather than information deterministic target`
2. `multi-fidelity training data optimization benefit versus information gain low-fidelity auxiliary loss neural operator 2026`
3. `when does low-fidelity data hurt surrogate negative transfer multi-fidelity ablation matched budget no-benefit`

Fetch note: the WebFetch tool is intercepted in this environment and returns a
redirect error, as does `curl`/`wget`; all page fetches in this loop were done with
`python3 urllib.request` + tag-stripping (`/tmp/fetchtxt.py`). Every "fetched" tag
below means the page body was actually retrieved and read in this loop.

## Findings

### Term 1 — LUPI theory

- **Pechyony & Vapnik, "On the Theory of Learning with Privileged Information"
  (NeurIPS 2010)** — https://papers.nips.cc/paper/3960-on-the-theory-of-learnining-with-privileged-information
  and mirror http://papers.neurips.cc/paper/3960-on-the-theory-of-learnining-with-privileged-information.pdf
  (search-returned; **PDF body not readable** — no PDF extractor on this box, and both
  the paper page and the PDF are only available as PDF). Search-result summary states
  the LUPI mechanism as: privileged information available at train and **not at test**,
  entering via a *correcting function* replacing the SVM slack; the claimed benefit is
  "reduced search space" and hence "improved convergence rate ... with regularized
  empirical risk minimization", plus faster convergence / better generalisation /
  noise resilience. **Treat as search-return only, not a fetched citation.**
- https://www.sciencedirect.com/science/article/abs/pii/S0031320326004887 (kernel LUPI
  with class-wise privileged information, Pattern Recognition 2026) and
  https://www.nature.com/nature-index/topics/l4/privileged-information-learning-in-machine-learning-systems
  — returned, not fetched.

Interpretation for the stream: the canonical LUPI claim is a **rate** claim, not an
identifiability claim. That is the precise theoretical framing for "LF-at-train on a
completeness-certified panel", and it is old and well-known — so the *framing* is
preempted; only the measurement composition can be new.

### Term 2 — LF as auxiliary training signal in neural operators

- **Villatoro, Geraci & Schiavazzi, "Assessing the performance of correlation-based
  multi-fidelity neural emulators", arXiv:2512.02868 (2 Dec 2025)** — **fetched**
  https://arxiv.org/abs/2512.02868. Directly relevant: "We further analyze the added
  value of the multi-fidelity approach by **conducting equivalent single-fidelity tests
  for each case, quantifying the performance gains achieved through fusing multiple
  sources of information**", across architectures with differing spectral bias (MLP,
  SIREN, KAN), coordinate encodings, "exact or learnable low-fidelity information",
  varying training set size, discontinuities, and "potentially corrupted low-fidelity
  sources". **Caveat that preserves our composition**: their emulators map input ->
  output *by integrating* LF model solutions, i.e. LF is inside the prediction path at
  test; ours is train-only with a stripped test view.
- Search returns, not fetched: https://www.sciencedirect.com/science/article/abs/pii/S0141029625016098
  (Pretrain-Finetune Neural Operator, PF-NO, LF data from Newmark-beta integration used
  for pretraining); https://dl.acm.org/doi/10.1016/j.jcp.2023.112462 and
  https://arxiv.org/abs/2204.06684 (multifidelity DeepONet, "one order of magnitude
  smaller error when using the same amount of high-fidelity data"); https://arxiv.org/pdf/2304.06972
  (MF FNO transfer learning); https://arxiv.org/pdf/2605.21348 (data-efficient neural
  operator training via physics-based losses).

### Term 3 — when LF hurts / negative transfer

- **Wang, Mak, Miller & Wu, "Local transfer learning Gaussian process modeling"
  (LOL-GP), arXiv:2410.12690 v3, 11 Jul 2025** — **fetched** https://arxiv.org/abs/2410.12690.
  Frames negative transfer as the central risk and (per the search summary of the same
  work) states that "the use of low-fidelity data may worsen predictions on the
  high-fidelity simulator"; the remedy is *locality* — transfer only where the source
  is informative, since the same source can help at some operating conditions and hurt
  at others.
- Search returns, not fetched: https://openreview.net/forum?id=yBTDCqNcan (Transfer
  Learning in Multi-fidelity Surrogate Modeling: A Wind Farm Case — **fetch blocked by
  OpenReview browser check**, dead end); https://www.sciencedirect.com/science/article/abs/pii/S1270963824000610
  (non-hierarchical LF data); https://dl.acm.org/doi/10.1007/978-981-95-7072-0_32
  (Efficient Selection of Low-Fidelity Data, PRICAI 2025 — "not all low-fidelity data
  necessarily improves model performance"); https://arxiv.org/pdf/2204.11138 (LF
  features "can corrupt the pre-trained features" during fine-tuning).

## Interpretation

The theoretical frame the round-3 regime invites — privileged/auxiliary data on a panel
where the input *already determines* the output — is classical LUPI territory and is a
**rate**, not an information, claim; and the "does MF actually beat matched
single-fidelity?" audit genre now has a 2025 systematic instance (arXiv:2512.02868).
Both push the same way: r3s3's contribution cannot be "LF-at-train helps", it can only
be the *quantified, certified* answer on a completeness-certified panel with LF strictly
out of the test path. Next turn should (a) pin a fetchable citation for the LUPI
rate-vs-information claim, since the canonical one is PDF-only here, and (b) search the
identifiability-vs-trainability separation directly.
