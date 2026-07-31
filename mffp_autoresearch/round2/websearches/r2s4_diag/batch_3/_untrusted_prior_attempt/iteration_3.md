# Iteration 3 — the metric artifact, the input-side distillation channel, and a second framing of the training-free regime rule

## Search rationale

Three loose ends. (1) B2 cross-stream item (b) asks the round report to restate helmholtz
under an energy-pooled convention (3-seed spread 1.6363 mean-of-ratios vs 0.0656
energy-pooled, 24.9x; spearman(rel-L2, ||y||) = -0.673): is that discrepancy a documented
artifact of the benchmark metric, or a project observation? (2) B3-D1's actual experiment
is an LF-consuming teacher at train, condition-only student at test — the sharpest
possible refutation query is whether that exact train/inference input asymmetry is
published for PDE surrogates. (3) Iteration 2 term 2 failed to find any training-free
"will more data help?" predictor; the second independent framing goes through
dataset-complexity / intrinsic-dimension measures.

## Search terms used

1. `relative L2 error mean of per-sample ratios versus norm-pooled aggregate error neural operator benchmark sensitive to sample norm`
2. `distill low-fidelity-consuming teacher into parameter-only student PDE field surrogate no low fidelity solve at inference`
3. `dataset complexity measure predicts sample efficiency before training intrinsic dimension nearest neighbour distance high dimensional design coverage`

## Findings

### Term 1 — mean-of-ratios vs energy-pooled relative L2

**No usable results** for the *critique*. Both conventions are in routine use and the
search engine could articulate the difference ("The per-sample ratio approach normalizes
each sample by its own norm individually, while the norm-pooled aggregate approach
normalizes by the global norm") but every returned paper (e.g.
https://arxiv.org/pdf/2510.16816, https://arxiv.org/pdf/2406.06486,
https://arxiv.org/pdf/2307.02494) merely *reports* one of them; none was found that
measures how much of a reported seed spread or model ranking is an artifact of the choice.
No fetch was spent — nothing to fetch. Note the in-repo report
`docs/reports/MF_Sharp_HighFreq_Report.md` §0.3 already establishes the adjacent, stronger
statement (MSE + rel-L2 structurally prefer blur; "the SURF metric panel matters as much
as any architecture change") — cite that rather than re-deriving.

### Term 2 — LF-consuming teacher -> condition-only student (the input-side channel)

- https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 — "Learning from
  more to predict with less: Representation-level multimodal distillation to address
  training-inference data asymmetry in surrogate modeling" (Engineering Applications of AI).
  **FETCH FAILED (HTTP 403)** — title + search-engine snippet only. The title alone names
  B3-D1's setting exactly ("training-inference data asymmetry in surrogate modeling",
  "learn from more, predict with less"); snippet: "A lightweight student model designed to
  operate solely on primary, deployment-feasible inputs can inherit the teacher's deeper
  understanding... through feature-level distillation" (SNIPPET — the quantitative claims
  are **do-not-cite** until a fetchable version is found).
- https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate
  (also https://www.mate.polimi.it/biblioteca/add/qmox/83-2024.pdf) — "Multi-fidelity
  reduced-order surrogate modelling": "By mapping low-fidelity reduced states to their
  high-fidelity counterpart, reduced-order surrogate models enable efficient recovery of
  full solution fields" — this is an LF-*consuming* test-time map (round-1 regime), not the
  round-2 stripped view. Search result only.
- https://arxiv.org/pdf/2512.13336 (KD-PINN, teacher PINN -> reduced student) and
  https://arxiv.org/html/2505.22391v1 (physics-informed distillation of diffusion models)
  are *capacity/latency* distillation — same architecture family, same inputs — not
  privileged-input distillation. Search results only.

### Term 3 — training-free complexity measures as sample-efficiency predictors

- https://arxiv.org/abs/2104.08894 — "The Intrinsic Dimension of Images and Its Impact on
  Learning" — **FETCHED**. Establishes the general form of B2's proposed rule: a
  training-free, nearest-neighbour-distance-based geometric statistic predicts learning
  difficulty — "low dimensional datasets are easier for neural networks to learn, and
  models solving these tasks generalize better from training to test data". The fetched
  abstract does **not** give an explicit sample-complexity formula (do-not-cite any
  numeric rate).
- Search-engine synthesis added two snippet-level claims — that "sample complexity to
  learn the data manifold depends exponentially on the intrinsic dimension", and the
  caveat that intrinsic dimensionality "is not the only feature of data that influences
  sample complexity". Both **SNIPPET-ONLY, do-not-cite**.
- https://arxiv.org/html/2406.03537v1 (local intrinsic dimension via diffusion models),
  https://arxiv.org/pdf/2101.01441 (data-quality measures for high-dimensional data) —
  search results only, adjacent but not about forecasting a learning-curve regime.

## Interpretation

The metric-artifact item has no external critique to cite and should be carried as a
project observation backed by the in-repo sharp-field report, not as a literature claim.
The input-side privileged-teacher setting **is** published for surrogate modelling under
the name "training-inference data asymmetry", which materially raises the prior-art bar
for B3-D1 — but the one source found is paywalled, so the refutation pass must find a
fetchable version or an equivalent. Training-free geometric predictors of learning
difficulty exist in general ML (intrinsic dimension), so B2's rule (a) is a domain
instantiation, not a new idea.
