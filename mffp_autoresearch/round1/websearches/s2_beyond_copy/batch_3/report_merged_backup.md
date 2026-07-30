# Websearch Report — Stream `s2_beyond_copy`, Batch 3

**Stream**: s2_beyond_copy
**Batch**: 3
**Total iterations**: 5 + 5 (TWO websearcher invocations ran concurrently against this
directory on 2026-07-30; see "Concurrency note" below — each respected the 5-iteration,
3-terms-per-turn cap independently)
**WebSearch calls**: ~15 (invocation A, recorded in `iteration_{1,3,4,5}.md`) + 12
(invocation B, recorded in `iteration_2.md` and `parallel_run_b_iterations.md`)
**WebFetch calls**: A ~12, B 12 (B: 9 usable, 3+1 dead — listed under Dead ends)
**Cap hit**: YES for both runs. `modes_cap` (lever d) was searched by neither.

## Concurrency note (honesty, read first)

Two websearcher invocations were launched for this same stream-batch and wrote to the same
directory. Invocation A's turn files survive as `iteration_1.md`, `iteration_3.md`,
`iteration_4.md`, `iteration_5.md`; invocation B's survive as `iteration_2.md` plus
`parallel_run_b_iterations.md` (B's turns 1-5 in full, written after the clobber was
detected so that **every citation below resolves to a file in this directory with its
URL**). Overlapping fetches (RMFNN arXiv:2310.03572, SR misalignment arXiv:2410.05410,
RevIN critique arXiv:2603.11869) were made **independently by both runs and agree**, which
is a useful cross-check. This report is the merge; where the two runs' verdicts differ in
strength, the stronger (more preempting) evidence is taken.

## Search trace

### A-turns 1-3 — field context → `iteration_1.md`, `iteration_3.md`
- Tail-aware training is published **and, in the one fetched PDE instance, a failed
  lever**: density-inverse cost-sensitive weighting **raised** test max error 76.63 K →
  96.72 K, and "worst-case prediction errors of the neural networks are an order of
  magnitude larger than the mean field error" [cite: https://arxiv.org/html/2605.16078].
  Heavy-tailed targets are a *named* benchmark difficulty axis in operator learning
  [cite: https://arxiv.org/abs/2606.20771].
- The MF canonical residual formulation **does not normalize the residual at all** and
  merely *assumes* ||F||_inf << ||Q_HF||_inf [cite: https://arxiv.org/html/2310.03572 —
  independently re-fetched by B via https://ar5iv.labs.arxiv.org/html/2310.03572].
- The theoretical statement B3's open question needs: "A network trained with mean-squared
  error converges to the conditional expectation ... The resulting prediction is
  over-smoothed by construction, and no architecture or training procedure can recover
  information the coarse representation discards"; "Many successful benchmarks live on
  low-dimensional solution manifolds where any competent reduced model will interpolate
  well." [cite: https://arxiv.org/html/2604.20061v1]
- Grid-alignment is a named problem in downscaling, addressed by *learned alignment*
  rather than by fixing the reference [cite: https://arxiv.org/abs/2410.03945]; half-pixel
  offset conventions are graphics folklore
  [cite: https://bartwronski.com/2021/02/15/bilinear-down-upsampling-pixel-grids-and-that-half-pixel-offset/].

### B-turns 1-2 — normalization framing + ESS → `iteration_2.md`, `parallel_run_b_iterations.md`
- Operator-learning practice retrieved is dataset-global min-max; the only instance-level
  use is adaptive instance norm as **conditioning** [cite: https://arxiv.org/html/2509.10186].
- RevIN critique **fetched**: scope "exclusively time series forecasting", not PDE/operator
  learning; "training via backpropagation in the normalized space yields better models"
  [cite: https://arxiv.org/html/2603.11869].
- Heavy-tail/ESS machinery exists only outside SciML — "MSE minimization is hypersensitive
  to these values ... forces the model to prioritize fitting the outliers at the expense of
  the structural majority" [cite: https://arxiv.org/html/2601.15360v1]; effective-number
  reweighting [cite: https://arxiv.org/pdf/1901.05555].

### A-turn 4 + B-turn 5 — refutation of the normalization lever → `iteration_4.md`, `parallel_run_b_iterations.md`
- **The strongest preemption of the whole batch**: DiSOL's "magnitude decoupling" — "We
  define a per-sample amplitude u_lim"; "the dimensionless solution pattern
  u_h := U_h / u_lim, so that max_x |u_h(x)| = 1"; "all models (DiSOL and all baselines)
  are trained to predict the normalized pattern"; amplitude restored via "an optional
  amplitude regressor" [cite: https://arxiv.org/html/2601.09143v1]. Applied to the
  **solution**, not a fidelity residual.
- QuadNorm: per-sample quadrature-weighted statistics are standard for neural-operator
  normalization **layers**, but on feature activations, "not inputs or targets", with no
  global-vs-instance ablation [cite: https://arxiv.org/html/2605.07375].

### A-turns 4-5 + B-turn 3 — refutation of the gate lever → `iteration_4.md`, `iteration_5.md`, `parallel_run_b_iterations.md`
- Routing safety defined as "|y − g(x)| − |y − f(x)| ≤ τ", decided "from features alone,
  before either model runs", thresholded by "Clopper–Pearson conformal calibration on a
  held-out set" [cite: https://arxiv.org/html/2603.14623].
- The no-harm accept-else-return-baseline rule, per-sample, test-time, no ground truth, in
  a PDE setting: "the learned reconstruction is selected only if R_learn <= R_base +
  eps_safe. If [this] fails, the method returns the baseline reconstruction"
  [cite: https://arxiv.org/html/2606.07153] — its certificate uses the **PDE residual**
  (ADR 0009 forbids that for us).
- Error-map gated solver fallback, reliability "recoverable from its forward passes alone"
  [cite: https://arxiv.org/abs/2605.28317]; MF spatial trust weighting with full fallback
  to "the corrected low-fidelity value", scalar-valued, "no explicit no-learning
  low-fidelity baseline is reported" [cite: https://arxiv.org/html/2602.20974];
  per-sample input-dependent MF gate that reads u_LF, no no-harm guarantee
  [cite: https://arxiv.org/html/2602.01176v1]; data-space Mahalanobis gate with HF-solve
  fallback at eta_sigma = 0.6 [cite: https://arxiv.org/html/2607.09763].

### A-turn 5 + B-turn 4 — refutation of the registration finding → `iteration_5.md`, `parallel_run_b_iterations.md`
- The convention mismatch itself is textbook numerics: "Unlike the vertex-centred case, in
  which a node of the coarse grid is also a node of the fine grid, the nodes on coarser
  grids do not form a subset of the fine grid nodes in the case of cell-centred
  discretization" [cite: https://ar5iv.labs.arxiv.org/html/2001.05723]; grid staggering
  "creates directional bias in interpolants due to source data nodes not being
  symmetrically placed about the target node location but offset"
  [cite: https://resources.system-analysis.cadence.com/blog/dual-grid-interpolation-for-cell-centered-overset-grid-systems].
- Misalignment invalidating full-reference metrics is published in SR: "conventional SR
  metrics (PSNR/SSIM) cannot be reliably evaluated on the real-world dataset due to
  misalignment in the testing set" [cite: https://arxiv.org/html/2410.05410].
- Five independent framings across the two runs found **no** published case of a
  misregistered no-learning *reference* inflating reported skill in an SR / downscaling /
  MF benchmark.

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched, with the iteration file that records them) | What remains open |
|---|---|---|---|
| **(D1)** Per-sample (instance-wise) normalization of the **fidelity-residual target**, replacing the family's single global `max\|HF−LF\|` scaler, on the same `lf_resid_fno` substrate | **preempted-but-MF-composition-open** | DiSOL "magnitude decoupling": "We define a per-sample amplitude u_lim"; "u_h := U_h / u_lim, so that max_x \|u_h(x)\| = 1"; "an optional amplitude regressor" — https://arxiv.org/html/2601.09143v1 (`iteration_4.md`). QuadNorm: per-sample stats standard in operator **feature** norm layers, "not inputs or targets", no global-vs-instance ablation — https://arxiv.org/html/2605.07375 (`parallel_run_b_iterations.md`). RevIN critique: instance norm/denorm standard, time series only; "training ... in the normalized space yields better models" — https://arxiv.org/html/2603.11869 (both runs). RMFNN: MF residual scale treated globally, **no** training-time scaling factor, "no discussion of per-sample or instance-wise scaling of residuals" — https://arxiv.org/html/2310.03572 + https://ar5iv.labs.arxiv.org/html/2310.03572 (`iteration_3.md`, `iteration_2.md`) | (i) instance-wise normalization of the **fidelity residual `HF−LF`** (DiSOL normalizes the solution); (ii) the **scale must be predicted from `(X, LF)` at test time** — it is not observable — for which DiSOL's amplitude regressor is the citable precedent; (iii) the **ESS diagnosis** (89.2 % of MSE energy in 1 of 400 samples, ESS 1.2; pfc max/median per-sample ‖r‖ = 8.2e4) as the stated cause, since the heavy-tail/ESS machinery exists only in classification / causal inference / RL (https://arxiv.org/pdf/1901.05555, https://arxiv.org/html/2601.15360v1); (iv) scoring it against a node-aligned no-learning reference |
| **(D2)** Per-sample **no-harm trust gate**: emit copy-LF instead of the corrected field when the corrector is predicted to hurt, decided from `(X, LF)` only | **preempted (cite)** at protocol/mechanism level; **preempted-but-MF-composition-open** only for the copy-LF-fallback binding | Proactive routing: safe iff "\|y − g(x)\| − \|y − f(x)\| ≤ τ", "from features alone, before either model runs", Clopper–Pearson conformal threshold — https://arxiv.org/html/2603.14623 (`iteration_4.md`/`iteration_2.md` of run A). No-harm Def. 3: "selected only if R_learn <= R_base + eps_safe ... otherwise ... returns the baseline reconstruction", per-sample, test-time, no ground truth, PDE — https://arxiv.org/html/2606.07153 (`parallel_run_b_iterations.md`). Error-map gated solver fallback — https://arxiv.org/abs/2605.28317 (`iteration_5.md`). MAST spatial trust weighting, fallback to "the corrected low-fidelity value", scalar outputs, "no explicit no-learning low-fidelity baseline is reported" — https://arxiv.org/html/2602.20974 (`iteration_5.md`). Per-sample MF gate reading u_LF, no no-harm guarantee — https://arxiv.org/html/2602.01176v1 (`parallel_run_b_iterations.md`). Data-space Mahalanobis gate, HF-solve fallback — https://arxiv.org/html/2607.09763 (`parallel_run_b_iterations.md`) | Only this sliver: nobody gates a **field-valued** operator against the **raw interpolated coarse solve** and reports the gated skill against that same baseline; and arXiv:2606.07153's certificate is a **PDE residual**, which ADR 0009 forbids at test time, so a physics-free `(X, LF)`-only certificate is unretrieved. **Do not claim the gate as a mechanism** — claim the measurement (oracle geomean 0.3803 → 0.2590; helmholtz 4.136 → 0.675) and cite 2603.14623 for the calibration recipe |
| **(D3)** Report the node-aligned (variant C/D/E) **registration-corrected reference** as a secondary column and pre-register falsification on it (zero GPU, `tools/registration_skill_split.py`) | **novel** as a benchmark-hygiene finding — but diagnostic/reporting only; the round-1 metric is frozen (program.md §5 immutables 2-4) | Convention mismatch is textbook: "the nodes on coarser grids do not form a subset of the fine grid nodes in the case of cell-centred discretization" — https://ar5iv.labs.arxiv.org/html/2001.05723 (`iteration_5.md`); staggering bias — https://resources.system-analysis.cadence.com/blog/dual-grid-interpolation-for-cell-centered-overset-grid-systems (`parallel_run_b_iterations.md`); misalignment invalidates full-reference SR metrics — https://arxiv.org/html/2410.05410 (both runs); learned alignment for unaligned downscaling grids — https://arxiv.org/abs/2410.03945 (`iteration_3.md`); weak-baseline discipline — https://arxiv.org/html/2508.05831 (batch-2 fetch) | Everything specific: no retrieved source reports a benchmark whose **no-learning reference** was misregistered by the cell-vs-node convention, the closed-form (r−1)/2 shift, the 2.0-8.6x skill inflation, or the consequence that trained wins are re-learned registration. These are exactly the citations the mentor note should carry as category precedent |
| **(D4)** Tail-aware / hard-sample reweighting of the residual objective (an alternative to D1 for the same defect) | **preempted (cite), with a published NEGATIVE result — treat as pre-falsified-adjacent** | "models are primarily ranked based on their prediction accuracy in the tails"; "worst-case prediction errors ... an order of magnitude larger than the mean field error"; density-inverse cost-sensitive weighting **raised** test max error 76.63 K → 96.72 K — https://arxiv.org/html/2605.16078 (`iteration_1.md`). Heavy-tailed targets a named benchmark axis — https://arxiv.org/abs/2606.20771 (`iteration_1.md`). RQA quantile-clipped reweighting — https://arxiv.org/pdf/2209.05315 (search-listed, `iteration_1.md`) | Narrow: nobody reweights a **fidelity-residual** objective by per-sample residual mass. Given the fetched negative result, any reweighting arm must carry an `expected_falsification` citing 2605.16078. **This is the reason to prefer D1 (normalize) over D4 (reweight).** |
| **(D5)** `modes_cap` raise for fisher_kpp only | **not searched (both runs hit the cap)** | — | Propose only as program.md §12.5's audited knob F22 with **no** novelty claim; defer to s5_tuning's searches |

**Cross-cutting caution for whatever B3 proposes** [cite: https://arxiv.org/html/2604.20061v1]:
"A network trained with mean-squared error converges to the conditional expectation ...
over-smoothed by construction, and no architecture or training procedure can recover
information the coarse representation discards." B2 part 7's open question ("is there ANY
dataset where a trained LF-consuming operator beats the node-aligned reference?") has a
published a-priori reason to answer NO wherever HF carries no energy outside the LF band —
already proven for pfc by the registration note. **B3 must pre-register a well-founded
negative as a legitimate outcome**, not a failure.

## Citations summary

Invocation A (recorded in `iteration_{1,3,4,5}.md`):
- DiSOL, "Discrete Solution Operator Learning for Geometry-Dependent PDEs" — https://arxiv.org/html/2601.09143v1 — FETCHED — iteration_4
- "Proactive Routing to Interpretable Surrogates" — https://arxiv.org/html/2603.14623 — FETCHED — iteration_2/4 (run A)
- "Hybrid Neural World Models" — https://arxiv.org/abs/2605.28317 — FETCHED — iteration_5
- MAST, "Multi-fidelity Augmented Surrogate via Spatial Trust-weighting" — https://arxiv.org/html/2602.20974 — FETCHED — iteration_5
- "Predictivity and Utility of Neural Surrogates of Multiscale PDEs" — https://arxiv.org/html/2604.20061v1 — FETCHED — iteration_3
- "A numerical study into NN surrogate model performance for uncertainty propagation" — https://arxiv.org/html/2605.16078 — FETCHED — iteration_1
- ELADO elliptic-PDE operator-learning datasets — https://arxiv.org/abs/2606.20771 — FETCHED (abstract) — iteration_1
- RMFNN — https://arxiv.org/html/2310.03572 — FETCHED — iteration_3
- Gmunu (cell- vs vertex-centred multigrid) — https://ar5iv.labs.arxiv.org/html/2001.05723 — FETCHED — iteration_5
- Interpolation-free DL downscaling on unaligned grids — https://arxiv.org/abs/2410.03945 — search-listed — iteration_3
- Bilinear up/downsampling half-pixel offset — https://bartwronski.com/2021/02/15/bilinear-down-upsampling-pixel-grids-and-that-half-pixel-offset/ — search-listed — iteration_1
- RQA adaptive PINN reweighting — https://arxiv.org/pdf/2209.05315 — search-listed — iteration_1
- MLSys "Accounting for Variance in ML Benchmarks" — https://proceedings.mlsys.org/paper_files/paper/2021/file/0184b0cd3cfb185989f858a1d9f5c1eb-Paper.pdf — search-listed (PDF dead) — iteration_4
- Conformal prediction for neural operators — https://arxiv.org/html/2606.09923 — search-listed — iteration_4

Invocation B (recorded in `iteration_2.md` + `parallel_run_b_iterations.md`):
- "On the Role of Reversible Instance Normalization" — https://arxiv.org/html/2603.11869 — FETCHED — B-turn 1
- RevIN (Kim et al., ICLR 2021) — https://openreview.net/forum?id=cGDAkQo1C0p — search-listed — B-turn 1
- P3D (adaptive instance norm as conditioning) — https://arxiv.org/html/2509.10186 — search-listed — B-turn 1
- RMFNN via ar5iv — https://ar5iv.labs.arxiv.org/html/2310.03572 — FETCHED — iteration_2
- Class-Balanced Loss / effective number of samples — https://arxiv.org/pdf/1901.05555 — search-listed — iteration_2
- Robust X-Learner (heavy tails vs MSE) — https://arxiv.org/html/2601.15360v1 — search-listed — iteration_2
- "FNOs Explained: A Practical Perspective" — https://arxiv.org/abs/2512.01421 — FETCHED (abstract only) — iteration_2
- "No-Harm Physics-Informed Inverse Learning" — https://arxiv.org/html/2606.07153 — FETCHED — B-turn 3
- "Causality-Inspired Safe Residual Correction" — https://arxiv.org/pdf/2512.22428 — FETCHED — B-turn 3
- MoE neural operator with uncertainty gate — https://arxiv.org/html/2607.09763 — FETCHED — B-turn 3
- "Enhanced SR Training via Mimicked Alignment" — https://arxiv.org/html/2410.05410 — FETCHED — B-turn 4
- Dual-grid interpolation, cell-centred overset grids — https://resources.system-analysis.cadence.com/blog/dual-grid-interpolation-for-cell-centered-overset-grid-systems — search-listed — B-turn 4
- Cell- vs vertex-centred AMR in numerical relativity — https://arxiv.org/pdf/2406.09139 — search-listed — B-turn 4
- QuadNorm — https://arxiv.org/html/2605.07375 — FETCHED — B-turn 5
- MF-BPINN (per-sample gate reading u_LF) — https://arxiv.org/html/2602.01176v1 — FETCHED — B-turn 5
- Multifidelity KAN (trainable convex-combination alpha) — https://arxiv.org/pdf/2410.14764 — search-listed — B-turn 5
- AGMF-Net — https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X — search-listed (HTTP 403) — B-turn 5

## Dead ends

- `https://arxiv.org/pdf/2310.03572`, `https://arxiv.org/pdf/2512.01421`,
  `https://proceedings.mlsys.org/paper_files/paper/2021/file/0184b0cd3cfb185989f858a1d9f5c1eb-Paper.pdf` → raw/undecoded PDF binary.
  **Use `/abs/` or `/html/<id>v1` or `ar5iv.labs.arxiv.org/html/<id>`.**
- `https://arxiv.org/pdf/2508.17902`, `https://arxiv.org/pdf/2601.09143`,
  `https://arxiv.org/pdf/2305.00163` → maxContentLength exceeded (>10 MB).
- `https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X` → HTTP 403.
- `https://www.emergentmind.com/topics/fourier-neural-operators-fnos` → fetched but has no
  loss/normalization content; the widely-repeated "operator losses are typically relative"
  claim could NOT be pinned to a fetched source — **do not cite it**.
- Term framings that failed: "cell-centered vs node-centered ... machine learning
  benchmark" (returns CFD/AMR numerics only) and three further framings of
  "misregistered reference inflates benchmark skill" — the absence IS the D3 finding.

## For the brainstormer

The brainstormer MUST quote the verdict for whatever it proposes.

1. **Lead with D1, per-sample normalization of the fidelity-residual target**, and quote:
   *"preempted-but-MF-composition-open — per-sample amplitude normalization of the
   SOLUTION is established practice ('magnitude decoupling': 'We define a per-sample
   amplitude u_lim', https://arxiv.org/html/2601.09143v1), instance norm is standard in
   operator feature layers but 'not inputs or targets' (https://arxiv.org/html/2605.07375),
   and the canonical MF residual formulation does not normalize the residual at all and
   assumes it is uniformly small (https://arxiv.org/html/2310.03572). Per-sample
   normalization of the fidelity residual `HF−LF`, with the scale predicted from `(X, LF)`
   at test time, is unoccupied."* Frame it as **repairing an assumption the MF literature
   makes implicitly** and that our panel violates by 4-5 orders of magnitude.
2. **Design constraint the search settles**: the per-sample residual scale is NOT observable
   at test time, so the arm needs an explicit scale predictor from `(X, LF)` (DiSOL's
   "optional amplitude regressor" is the citable precedent) or a scale surrogate computable
   from LF alone. A card that normalizes by the *true* per-sample `max|HF−LF|` at test time
   would be an oracle, not a method — state which one is being run.
3. **Make the 2x5 asymmetry the evidence design**: `tools/target_scale_spread_audit.py`
   flags exactly pfc (spread 8.24e4) and helmholtz (ESS 1.2/400) and clears the other
   three, so per-sample normalization is predicted to help on 2 and be **neutral** on 3.
   A uniform gain across all five would falsify the mechanism story even if the geomean
   improves. Floors to clear: geomean 0.884; pfc 1.151, allen_cahn 1.633, fisher_kpp 0.418,
   cahn_hilliard 0.553 (helmholtz report-only, ADR 0002).
4. **Prefer D1 (normalize) over D4 (reweight)**: tail reweighting is preempted *with a
   fetched negative result* — density-inverse weighting raised test max error 76.63 K →
   96.72 K (https://arxiv.org/html/2605.16078). If any reweighting appears in the card it
   must carry that citation in `expected_falsification`.
5. **Do not claim novelty for the trust gate (D2)** — `preempted (cite)`
   (https://arxiv.org/html/2603.14623 routing-safety condition + conformal threshold;
   https://arxiv.org/html/2606.07153 Definition 3 accept-else-return-baseline). Include it,
   if at all, as a cheap non-promotable screening arm under ADR 0007 whose contribution is
   the *measurement* (oracle 0.3803 → 0.2590), with a **physics-free** certificate because
   ADR 0009 forbids the PDE-residual certificate the published rule uses.
6. **Carry D3 as a reported secondary column, never as the scored metric** (round-1 metric
   frozen). Verdict `novel` as benchmark hygiene; the mentor note should cite
   https://ar5iv.labs.arxiv.org/html/2001.05723 (the convention mismatch, textbook) and
   https://arxiv.org/html/2410.05410 (misalignment invalidating full-reference metrics) as
   category precedent, and claim only the benchmark-internal consequence as ours.
7. **Pre-register the negative**: https://arxiv.org/html/2604.20061v1 gives the published
   reason a trained corrector may be unable to beat the node-aligned reference on datasets
   whose HF carries no out-of-band energy. A clean negative on that column is a result, not
   a failed card.
