# Websearch Report — Stream `r2s4_diag`, Batch 3

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 3
**Total iterations**: 5 (CAP HIT)
**WebSearch calls**: 15 (3 per iteration x 5; no turn exceeded 3 terms)
**WebFetch calls**: 12 (9 usable, 3 failed: `sciencedirect.com/.../S0952197625034293` HTTP 403;
`link.springer.com/article/10.1007/s10994-024-06619-7` 303 -> `idp.springer.com`;
`besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.13851` HTTP 402). <=2 fetches per
term throughout. **No `arxiv.org/pdf/` URL was fetched at any point** (process rule after this
round's two fabrication incidents; only `/abs/` and `/html/`).
**Cap hit**: YES — 5/5 iterations used. ENOUGH on field survey declared at end of iteration 3;
iterations 4-5 were pure §3.3 refutation.

## Search trace

### Turn 1 — is "project the privileged teacher onto the student's observable space" published?
Terms: (1) LUPI theory / when PI cannot be transferred; (2) projecting teacher predictions onto
student feature space; (3) recoverable share of an oracle's advantage.
- LUPI theory is **positive-result oriented and supplies no ceiling**: "encouraging agreement
  between the teacher and the student leads to reduced search space"; the fetch confirmed no
  failure condition is stated [cite: https://arxiv.org/abs/1903.03694, FETCHED].
- The *setting* exists in the LM domain: privileged info available only at training, absent at
  inference; "the abstract does not explicitly state an upper bound on how much of the
  teacher's advantage is recoverable" [cite: https://arxiv.org/abs/2602.04942, FETCHED].
- Closest published relative of B3-D1 anywhere in the loop: "the expected oracle decomposes as
  O^exp = O^repro + Delta, into reproducible single-commit headroom O^repro and a non-negative
  single-commit selection floor Delta", with a **recoverability asymmetry** and an explicit
  warning about "non-identifiability at k=1" [cite: https://arxiv.org/abs/2607.03436, FETCHED].
- The snippet claiming https://arxiv.org/abs/2606.01292 lower-bounds teacher risk by its
  projection onto the student space was **refuted by the fetch** — do-not-cite.
-> `iteration_1.md`

### Turn 2 — Option B (coverage-greedy support repair) and the training-free regime rule
Terms: (1) coverage/space-filling subset selection from a fixed pool for surrogates;
(2) training-free "will more data help?" predictor; (3) learning-curve extrapolation.
- Option B's mechanism is **published**: a method that "selects those dynamic data points that
  fill the input space of the nonlinear model more homogeneously", evaluated "against two
  baselines: random subset sampling and using all available data points", beating random
  [cite: https://arxiv.org/abs/2012.03541, FETCHED].
- Term 2: **No usable results** (first dedicated failure for the training-free predictor).
- Viering & Loog: scepticism "towards the idea that it has been proven that power laws often
  provide accurate learning curve models", plus "learning curves that are ill-behaved, showing
  worse learning performance with more training data"
  [cite: https://arxiv.org/abs/2103.10948, FETCHED].
-> `iteration_2.md`

### Turn 3 — metric artifact, input-side distillation channel, complexity measures (ENOUGH declared)
Terms: (1) mean-of-ratios vs energy-pooled rel-L2; (2) LF-teacher -> condition-only student for
PDE fields; (3) training-free dataset-complexity predictors.
- Term 1: **No usable results** for a *critique* of the two conventions — only papers that
  report one of them.
- The dangerous preemption surfaced: "Learning from more to predict with less:
  Representation-level multimodal distillation to address training-inference data asymmetry in
  surrogate modeling" [cite: https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293
  — FETCH 403, title/venue only; all numbers do-not-cite].
- Training-free geometric predictors of learning difficulty exist generally: "low dimensional
  datasets are easier for neural networks to learn, and models solving these tasks generalize
  better from training to test data" [cite: https://arxiv.org/abs/2104.08894, FETCHED].
-> `iteration_3.md`

### Turn 4 — refutation pass 1 (D1 setting, D1 predicted outcome, D2 diagnostic framing)
- No fetchable mirror of the ScienceDirect paper exists; the design is published but only
  citable at title level.
- **Counter-hypothesis found for D1's predicted outcome**: a factorial 50 IC x 50 parameter
  test design with a 50x50 error matrix concludes "approximation difficulty varies primarily
  with the conditioning vector (i.e., the induced PDE regime), rather than with the initial
  conditions" [cite: https://arxiv.org/html/2601.22654v1, FETCHED] — opposite polarity to
  ADR r2-0003's grounding.
- Stochastic-surrogate evaluation: "the forcing realization is not observed at forecast time, a
  surrogate cannot track a single reference trajectory indefinitely"; "pointwise-trained neural
  surrogates fail" [cite: https://arxiv.org/html/2607.00196v1 (TRIE), FETCHED].
- D2-as-diagnostic: search engine stated outright it found nothing distinguishing
  "sample-limited" from "information-limited" regimes with such tools. **No usable result.**
-> `iteration_4.md`

### Turn 5 — refutation pass 2 (CAP)
- D1 operation in generic vocabulary: **No usable results** (third independent framing to fail).
- d_min-style coverage diagnostics exist in **spatial statistics**, not SciML: NNDM
  [cite: https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.13851 — FETCH 402,
  title/venue only]. Second dedicated failure in-domain for D3.
- Metric artifact: **No usable results**, second independent failure.
-> `iteration_5.md` (contains the full verdict text)

## Prior-art verdict

| Candidate direction | Verdict | Citations (this loop) | What remains open |
|---|---|---|---|
| **D1** — teacher-projection diagnostic (B2 Option A): matched T0/I1 legs with per-arm test predictions dumped, then out-of-fold condition -> prediction map fitted to I1's predictions, scoring `proj(I1)` vs `T0` | `preempted-but-MF-composition-open (cite)` | training-inference data asymmetry — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 (403, title only) ; pi-Distill/OPSD — https://arxiv.org/abs/2602.04942 (FETCHED) ; multi-view LUPI theory — https://arxiv.org/abs/1903.03694 (FETCHED) ; oracle-gap decomposition — https://arxiv.org/abs/2607.03436 (FETCHED) ; counter-hypothesis — https://arxiv.org/html/2601.22654v1 (FETCHED) ; batch-1 Yang et al. — https://arxiv.org/abs/2209.08754 ; batch-2 DOPD — https://arxiv.org/html/2606.30626v1 | No fetched source computes the **condition-measurable projection of an LF-consuming field teacher** as a transferability ceiling — three independent framings failed to find the operation. 2607.03436's recoverable/irreducible split has never been instantiated for a **field-valued** output whose irreducible part is an **unrecorded random IC**, scored in copy-LF skill. Adoptable by citation: 2607.03436's `O^repro + Delta` vocabulary and its k=1 non-identifiability warning; 2601.22654's factorial IC x parameter error matrix. |
| **D2** — coverage-greedy fit-fold selection at fixed N_fit on `sharp__cahn_hilliard` (B2 Option B) | `preempted (cite)` at mechanism level; composition open as a **diagnostic** | space-filling subset selection from a fixed pool — https://arxiv.org/abs/2012.03541 (FETCHED) ; active-learning contrast (forbidden by §5.11) — https://arxiv.org/pdf/2606.09949 , https://www.sciencedirect.com/science/article/pii/S004578252030760X (search results only) | Selecting a maximally space-filling subset from an existing pool and beating random subsampling is **done**. Open: using it as the *discriminator* between support-limited and information-limited datasets, gated by a training-free d_min/identifiability go/no-go — explicit search-engine non-result. |
| **D3** — training-free regime rule (identifiability x d_min predicts the learning-curve regime; B2 cross-stream item (a), needs a second card to reproduce) | `preempted-but-MF-composition-open (cite)` | intrinsic dimension predicts learnability — https://arxiv.org/abs/2104.08894 (FETCHED) ; learning-curve shapes + ill-behaved curves — https://arxiv.org/abs/2103.10948 (FETCHED) ; LC decision survey — https://link.springer.com/article/10.1007/s10994-024-06619-7 (303 blocked) ; NNDM — https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.13851 (402) | Training-free NN-geometry predictors of learning difficulty are published in general ML; nearest-neighbour-distance-matched validation is published in spatial statistics. NOT found in two dedicated searches: the **conditional pre-training go/no-go** form (low identifiability + small d_min = adding rows cannot help; real identifiability + d_min >> 1 = coverage-limited) in a PDE condition space. Viering & Loog also **constrain** B2's own 3-point power-law asymptote fit. |
| **D4** — energy-pooled restatement of the mean-of-ratios metric (B2 cross-stream item (b)) | `novel` (weak sense: two independent framings found nothing close) — but it is a **reporting** item, not an experiment | nearest neighbours: in-repo `docs/reports/MF_Sharp_HighFreq_Report.md` §0.3 ; TRIE — https://arxiv.org/html/2607.00196v1 (FETCHED) | No source found measures how much of a reported seed spread or ranking is an artifact of per-sample-ratio vs pooled normalisation. TRIE supplies the stronger, citable adjacent claim that pointwise metrics are inappropriate for stochastic PDE surrogates at all. §5.4 keeps nRMSE immutable in-round, so this stays interpretive. |

## Citations summary

- [Wang 2019] "Everything old is new again: A multi-view learning approach to LUPI and distillation" — https://arxiv.org/abs/1903.03694 — FETCHED — used in: `iteration_1.md` term 1
- [Anon. 2026] "Privileged Information Distillation for Language Models" (pi-Distill / OPSD) — https://arxiv.org/abs/2602.04942 — FETCHED — used in: `iteration_1.md` term 1
- [Anon. 2026] "What Makes a Strong Model? A Unified Spectral Analysis of Knowledge Transfer over High-dimensional Linear Regression" — https://arxiv.org/abs/2606.01292 — FETCHED (projection claim **refuted** by the fetch) — used in: `iteration_1.md` term 2
- [Anon. 2026] "How Much of the Routing Gap Is Real? Decomposing the Router-to-Oracle Gap into Reproducible Specialist Advantage and Single-Draw Label Noise" — https://arxiv.org/abs/2607.03436 — FETCHED — used in: `iteration_1.md` term 3
- [Rothenberger et al. 2020] "Space-Filling Subset Selection for an Electric Battery Model" — https://arxiv.org/abs/2012.03541 — FETCHED — used in: `iteration_2.md` term 1
- [Viering & Loog] "The Shape of Learning Curves: a Review" — https://arxiv.org/abs/2103.10948 — FETCHED — used in: `iteration_2.md` term 3
- ["Learning curves for decision making in supervised machine learning: a survey"] — https://link.springer.com/article/10.1007/s10994-024-06619-7 — FETCH BLOCKED (303) — used in: `iteration_2.md` term 3
- [Pope et al. 2021] "The Intrinsic Dimension of Images and Its Impact on Learning" — https://arxiv.org/abs/2104.08894 — FETCHED — used in: `iteration_3.md` term 3
- [Anon. 2025] "Learning from more to predict with less: Representation-level multimodal distillation to address training-inference data asymmetry in surrogate modeling", Eng. Appl. of AI — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 — FETCH 403, search result only — used in: `iteration_3.md` term 2, `iteration_4.md` term 1
- [Anon. 2026] "Parameter conditioned interpretable U-Net surrogate model for data-driven predictions of convection-diffusion-reaction processes" — https://arxiv.org/html/2601.22654v1 — FETCHED — used in: `iteration_4.md` term 2
- [Anon. 2026] "TRIE: An Evaluation Framework for Stochastic PDE Surrogates" — https://arxiv.org/html/2607.00196v1 — FETCHED — used in: `iteration_4.md` term 2
- [Mila et al. 2022] "Nearest neighbour distance matching Leave-One-Out Cross-Validation for map validation", Methods Ecol. Evol. — https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.13851 — FETCH 402, search result only — used in: `iteration_5.md` term 2
- ["Learning Where to Simulate: Generative Active Sampling for Online PDE Surrogate Training"] — https://arxiv.org/pdf/2606.09949 — search result only (NOT fetched: /pdf/ URL, process rule) — used in: `iteration_2.md` term 1
- [ISMO] "Iterative surrogate model optimization: an active learning algorithm for PDE constrained optimization" — https://www.sciencedirect.com/science/article/pii/S004578252030760X — search result only — used in: `iteration_2.md` term 1
- ["Multi-fidelity reduced-order surrogate modelling"] — https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate — search result only — used in: `iteration_3.md` term 2

**Still binding from earlier batches** (do not re-derive): Agarwal et al. IQM/stratified
bootstrap https://ar5iv.labs.arxiv.org/html/2108.13264 ; Du paired protocol
https://arxiv.org/abs/2511.19794 ; Yang et al. LUPI non-monotone law
https://arxiv.org/abs/2209.08754 ; McGreivy & Hakim https://arxiv.org/abs/2407.07218 ;
Lipschitz-operator sample complexity https://arxiv.org/abs/2410.23440 ; DOPD advantage gap
https://arxiv.org/html/2606.30626v1 ; MSE -> conditional-mean collapse
https://arxiv.org/html/2604.20061v1 . In-repo prior websearch:
`docs/reports/MF_Sharp_HighFreq_Report.md` §0.3.

**Do-not-cite list (new this loop)** — surfaced only as search-engine synthesis and never
verified in a fetch: the claim that arXiv:2606.01292 lower-bounds teacher risk by its
projection onto the student's space (**explicitly contradicted by the fetch**); the "two
necessary conditions for successful privileged learning based on information theory"
formulation; every quantitative claim about the ScienceDirect training-inference-asymmetry
paper (the "up to 30% error reduction", the benchmark list, the mechanism description); the
"sample complexity depends exponentially on intrinsic dimension" statement; the k-center /
farthest-point greedy wording; the claim that coverage-based selection and gradient-based data
valuation are "the two technical families most relevant to training subset selection".
Batch-1 and batch-2 do-not-cite lists remain in force.

## Dead ends

- `predict whether more training data will help without training dataset diagnostic learning curve regime nearest neighbor coverage` -> kNN tutorials, two 2000s ML patents, a bias/variance blog. Search engine stated the combination is not covered.
- `regress oracle predictions on available features to find achievable ceiling feature ablation upper bound predictable component` -> entirely off-domain (LLM accuracy prediction, neuro-predictivity, mutation analysis). Third failed framing for D1's operation.
- `relative L2 error mean of per-sample ratios versus norm-pooled aggregate ...` and `averaging per-sample normalized error overweights low-energy samples benchmark ranking artifact ...` -> both returned papers that *use* one convention; no critique of the choice. Two independent failures.
- `greedy maxmin distance subset selection ... sample-limited from information-limited regime` -> generic diverse-summarization/coreset work; search engine explicitly reported no hit on the regime-diagnostic framing.
- Fetch failures to avoid repeating: `sciencedirect.com/science/article/abs/*` (403), `link.springer.com/article/*` **and** `/chapter/*` (303 -> `idp.springer.com`), `besjournals.onlinelibrary.wiley.com/doi/*` (402). Process rule: `arxiv.org/pdf/*` was never fetched — use `/abs/` or `/html/`.

## For the brainstormer

The brainstormer MUST quote the applicable verdict row above for whatever it proposes.

1. **D1 (B2's Option A) is the batch's strongest card, and its verdict is
   `preempted-but-MF-composition-open`.** Quote the row. Sell the *composition*: the
   condition-measurable projection of an LF-consuming **field** teacher, scored in copy-LF
   skill units, where the irreducible remainder is an unrecorded random IC. Do NOT claim the
   setting is new — "training-inference data asymmetry" is a published surrogate-modelling
   term (https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293, title-level
   citation only; its numbers are on the do-not-cite list).
2. **Adopt arXiv:2607.03436's vocabulary and its warning rather than inventing either.** Write
   the split as `O^exp = O^repro + Delta` (recoverable headroom + irreducible floor), and quote
   its "non-identifiability at k=1" caution as the reason the projection must be fitted
   **out-of-fold with k >= 2 repeats**, not on a single draw. This is fetched and citable.
3. **Pre-register against a citable counter-hypothesis, not against a hunch.**
   https://arxiv.org/html/2601.22654v1 built a factorial 50-IC x 50-parameter error matrix and
   found difficulty tracked the *parameters*, not the ICs — the opposite of ADR r2-0003's
   grounding for our panel. B2 predicts `proj(I1) ~ T0` on 4/5 datasets; 2601.22654 is the
   published reason that prediction could fail, and naming it converts the card from a
   confirmation into a test.
4. **If Option B is chosen instead, its mechanism is `preempted` — lead with the diagnostic.**
   Space-filling subset selection from a fixed pool beating random subsampling is done
   (https://arxiv.org/abs/2012.03541, fetched). What is open is using coverage-greedy
   re-selection to *discriminate* support-limited from information-limited datasets, with the
   training-free d_min/identifiability check as the go/no-go before any GPU is spent. Also note
   the immutable that makes this necessary: the PDE-surrogate literature's standard answer is
   **active learning** (generate new solves), which §5.11 forbids.
5. **Two constraints on the round-level rule (D3).** (a) Viering & Loog
   (https://arxiv.org/abs/2103.10948) express scepticism that power laws reliably model
   learning curves — B2's 3-point `c + a N^-b` asymptote fits must be reported with that
   caveat, especially the cahn_hilliard fit that returned an unphysical negative asymptote on
   1 of 3 seeds. (b) The same review's "learning curves that are ill-behaved, showing worse
   learning performance with more training data" is the citation for B2's helmholtz kNN
   degradation (8.69 -> 20.59 skill as N goes 20 -> 320) — quote it instead of calling the
   curve anomalous.
6. **n_eff is STILL uncited after three batches.** Nothing this loop moved it. Any card using
   effective sample counts must define the statistic in its own recipe and label it a project
   convention.
7. **Two binding carry-overs.** (i) Batch 2's instruction stands: **do not propose "build a
   ceiling estimator"**. (ii) Re-certification is still owed — the installed noise-floor
   constants were measured on a conditional-mean-collapsed model, so they **under-state** a
   less-collapsed successor's noise; any B3 claim against them must re-certify on the compared
   arm or state the bias direction. Also carry B2's three binding build constraints: helmholtz
   report-only, no ifc_poisson LF-paired arm on the `lf[:n_hf]` rule (run
   `tools/ladder_pair_alignment_audit.py --fail-on mispaired`), and **dump per-arm test
   predictions and checkpoints** — B2's missing artefacts are precisely why D1 cannot be run as
   re-analysis.
8. **If the card touches the metric (D4), it is a reporting item with no external critique to
   cite** — verdict `novel` only in the sense that two independent searches found nothing. The
   defensible citation is TRIE (https://arxiv.org/html/2607.00196v1): pointwise metrics are
   inappropriate for stochastic PDE surrogates because "the forcing realization is not observed
   at forecast time". §5.4 keeps nRMSE immutable, so this can only change the *interpretation*.
