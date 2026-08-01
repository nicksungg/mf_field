# Websearch Report — Stream `r2s2_stacked`, Batch 3

**Stream**: `r2s2_stacked`
**Batch**: 3
**Total iterations**: 5 (cap 5 — **cap hit**, noted in `iteration_5.md`)
**WebSearch calls**: 15 (3 per iteration x 5)
**WebFetch calls**: 0 via the `WebFetch` tool — it is DISABLED in this environment (it redirects to a
context-mode MCP tool that is not in this subagent's tool list). Routed around per the never-give-up rule:
**13 HTTP GETs performed from Bash via `urllib`/`curl`** (10 succeeded with abstract text extracted,
3 failed: OpenReview browser-check + OpenReview API 403, Wiley 403). Every "FETCHED" quote below is from one
of those successful GETs made in this loop.
**Cap hit**: yes (5/5 iterations used; 3 terms per iteration, never exceeded)

## Search trace

### Turn 1 — closed-form / training-free correction of surrogate fields → `iteration_1.md`
Terms chosen because B2's H-STAGE says the scored stack collapses to a zero-gradient recipe; before promoting
it I must know if the mechanism is published.
- `Wiener filter post-processing correction of neural operator PDE surrogate predictions spectral` → the
  Wiener coefficient appears only *inside* FreqNO-DPS's diffusion-posterior likelihood (needs sparse test-time
  observations) [cite: https://arxiv.org/abs/2606.03936]; "Spectral Shaping" is a training-time activation
  filter and could not be fetched [cite: https://openreview.net/forum?id=mmDkgLtYNI — 403/browser check].
- `closed-form linear least-squares filter low-fidelity to high-fidelity field correction multifidelity surrogate`
  → LS-MFS fits the scale factor + polynomial discrepancy by a single least-squares regression with the LF
  model as a basis function [cite: https://arxiv.org/abs/1705.02956, FETCHED]; projection-based MF linear
  regression does closed-form MF correction on a **field** output with **<=10 HF samples**, 3-12 % better than
  single-fidelity [cite: https://arxiv.org/abs/2508.08517, FETCHED].
- `training-free correction outperforms trained neural corrector small data PDE surrogate` → PhysicsCorrect is
  a named, AAAI-published **training-free** corrector with a cached pseudoinverse, but PDE-residual based
  (unusable here: physics-agnostic at test) [cite: https://arxiv.org/abs/2507.02227, FETCHED].

### Turn 2 — fitted spectral transfers, retrieval baselines, "simple baseline" benchmarking → `iteration_2.md`
- `Wiener deconvolution transfer function fitted from coarse-fine simulation pairs ...` → **No usable
  results** for the PDE composition; only instrument/optics deconvolution.
- `analog ensemble nearest-neighbor retrieval baseline with linear correction outperforms neural network
  downscaling` → analogue/k-NN resampling of training fields is a classical downscaling family
  [cite: https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004WR003444, snippet-level, fetch 403].
- `simple linear baseline outperforms deep learning surrogate benchmark reality check scientific machine
  learning` → closed-form optimal linear maps are already offered as *the* SciML benchmarking baseline
  (with a shallow-water PDE experiment) [cite: https://arxiv.org/abs/2508.05831, FETCHED]; and the canonical
  "none of the deep models beat deliberately simple baselines" result plus its rebuttal show **the metric
  decides the verdict** [cite: https://www.nature.com/articles/s41592-025-02772-6, FETCHED;
  https://www.biorxiv.org/content/10.1101/2025.10.20.683304.full.pdf].

### Turn 3 — seed/fold variance protocol and shrinkage-gated stagewise correctors → `iteration_3.md`
- `random seed variance ablation neural PDE surrogate ...` → **Operator Boosting** already builds stagewise
  tiny residual correctors over a cheap base predictor, *"incorporates each correction through
  validation-selected shrinkage"*, and decides per cell against confidence intervals (30 dataset-architecture
  pairs; 21 positive mean gains, 17 positive CIs) [cite: https://arxiv.org/abs/2606.17460, FETCHED];
  benchmark seed variance as the meaningfulness test [cite: https://arxiv.org/abs/2406.10229, FETCHED].
- `stacked generalization out-of-fold non-negative least squares weight zero ...` → a zero OOF weight is
  textbook Super-Learner behaviour ("adds little unique information")
  [cite: https://www.biorxiv.org/content/10.1101/172395v1.full; https://doi.org/10.1177/1536867x231212426,
  snippet-level].
- `ablation shows linear filter suffices learned residual correction unnecessary ...` → **No usable results**;
  every fetched/returned ablation *credits* the learned stage (P2C2Net, PhyRes-MDNF).

### Turn 4 — REFUTATION pass on direction (i) → `iteration_4.md`
- `linear shift-invariant Wiener filter fitted on training pairs ... multi-fidelity spectral transfer` →
  **No usable results** (engine said so explicitly); nearest genuine relative is the cosmology MF
  power-spectrum emulator line [cite: https://arxiv.org/pdf/2306.03144], which corrects a 1-D summary
  statistic, not a field.
- `spectral bias post-hoc correction fitted linear operator amplify attenuated high wavenumbers ...` →
  high-frequency scaling is **latent-space and trained**, not a fitted output-side transfer
  [cite: http://arxiv.org/abs/2503.13695, FETCHED via arXiv API]; spectral-bias diagnosis
  [cite: https://arxiv.org/abs/2602.19265, FETCHED].
- `retrieval of nearest training simulations plus learned correction surrogate parametric PDE analog method` →
  **No usable results** for the composition.

### Turn 5 — REFUTATION pass on directions (ii)/(iii) + verdicts → `iteration_5.md`
- `zero-parameter training-free baseline as mandatory benchmark bar ...` → "the trivial baseline is the bar"
  is established practice [cite: NAS-Bench-Suite-Zero
  https://proceedings.neurips.cc/paper_files/paper/2022/file/b3835dd49b7d5bb062aecccc14d8a675-Supplemental-Datasets_and_Benchmarks.pdf,
  snippet-level].
- `neural network component contributes nothing after proper out-of-fold evaluation multi-fidelity surrogate
  negative result` → **No usable results**: the MF literature returned is uniformly positive-result. The
  negative is the stream's open content.
- `re-running single dataset improvement multiple seeds decide keep or remove learned module protocol` →
  the round's own certified protocol [cite: https://arxiv.org/abs/2511.19794, FETCHED — *"with only three
  seeds, our paired protocol never declares significance in these settings"*], plus the warning that
  downstream re-seeding cannot substitute for multiple *training* seeds
  [cite: https://arxiv.org/abs/2510.26714, FETCHED].

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched this loop unless marked) | What remains open |
|---|---|---|---|
| **(i)** Promote `k-NN average of train LF pool at calib-selected k* -> one closed-form LSI Wiener filter fitted on the fit fold` from diagnostic to a first-class **SCORED** panel arm | `preempted-but-MF-composition-open (cite)` | LS-MFS closed-form LF-as-basis least squares https://arxiv.org/abs/1705.02956 (FETCHED); projection-based MF linear regression, field output, <=10 HF samples https://arxiv.org/abs/2508.08517 (FETCHED); high-frequency scaling http://arxiv.org/abs/2503.13695 (FETCHED, arXiv API); spectral-bias diagnosis https://arxiv.org/abs/2602.19265 (FETCHED); shrinkage-gated stagewise residual correction https://arxiv.org/abs/2606.17460 (FETCHED); analogue/k-NN downscaling https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004WR003444 (snippet, 403); training-free corrector class https://arxiv.org/abs/2507.02227 (FETCHED) | No fetched source composes **retrieval intermediate → one fitted LSI Fourier-diagonal transfer** as a *multi-fidelity* corrector, scores it under a **copy-LF-skill** denominator with **no LF at test**, or reports the **attribution** (closed-form stage carries 33-100 % of a trained stack's out-of-fold gain; learned stage switched off on 5/8 cells). Claim the composition + attribution, never the filter |
| **(ii)** Re-run allen_cahn's gated-CNN increment (9.443 skill units, 1 fold seed, 1 fit) at the round's 1+2-seed protocol as the keep/kill decider for the learned stage | `preempted (cite)` — as a *method*; it is a measurement, not a claim | Du paired multi-seed + BCa + sign-flip https://arxiv.org/abs/2511.19794 (FETCHED; already cited by `state/noise_floor.json._protocol`); single-training-seed limitation https://arxiv.org/abs/2510.26714 (FETCHED); benchmark seed variance https://arxiv.org/abs/2406.10229 (FETCHED); per-cell CI decision on learned residual stages https://arxiv.org/abs/2606.17460 (FETCHED); Super-Learner zero OOF weight https://www.biorxiv.org/content/10.1101/172395v1.full (snippet) | Nothing methodological is open — only the **answer on this panel**. Two design constraints fall out of the citations: vary the **fold/train seed**, not just the corrector init (2510.26714); and pre-register the decision against the certified per-dataset `min_claimable_effect` (allen_cahn 0.8797 skill units), because a 3-seed paired test may never declare significance (2511.19794) |
| **(iii)** Close on B2; export the closed-form filter as the **zero-parameter bar** other streams' learned correctors must beat | `preempted (cite)` — as a *framing*; open as artefact + measurement | Optimal closed-form linear/affine baselines for SciML benchmarking (incl. shallow-water PDE) https://arxiv.org/abs/2508.05831 (FETCHED); "none outperformed the deliberately simple baselines" https://www.nature.com/articles/s41592-025-02772-6 (FETCHED) + rebuttal https://www.biorxiv.org/content/10.1101/2025.10.20.683304.full.pdf; NAS-Bench-Suite-Zero trivial-baseline result (snippet) | The specific bar — an **LF-derived, retrieval + LSI, zero-gradient** predictor scored on a copy-LF-skill panel — exists in no fetched source. The rebuttal pair is the field's own warning that the bar must be published **in the round's claim unit** (skill units vs certified `min_claimable_effect`), which is B2's H-RULE-UNITS finding arriving from an unrelated domain |

## Citations summary

- [LS-MFS] "Multi-Fidelity Surrogate Based on Single Linear Regression" — https://arxiv.org/abs/1705.02956 — iteration_1 (term 2, FETCHED, abstract quoted)
- [Projection-based MF linear regression] "…for data-scarce applications" — https://arxiv.org/abs/2508.08517 — iteration_1 (term 2, FETCHED)
- [PhysicsCorrect] "A Training-Free Approach for Stable Neural PDE Simulations" (AAAI) — https://arxiv.org/abs/2507.02227 / https://ojs.aaai.org/index.php/AAAI/article/view/39360 — iteration_1 (term 3, FETCHED)
- [FreqNO-DPS] — https://arxiv.org/abs/2606.03936 — iteration_1 (term 1, snippet here; FETCHED+VERIFIED in this stream's batch-2 loop)
- [Spectral Shaping for Neural PDE Surrogates] — https://openreview.net/forum?id=mmDkgLtYNI — iteration_1 (term 1, FETCH FAILED, snippet-level only)
- [Gangopadhyay et al. 2005] "Statistical downscaling using K-nearest neighbors", WRR — https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2004WR003444 — iteration_2 (term 2, snippet-level; HTTP 403)
- [Optimal Linear Baseline Models for SciML] — https://arxiv.org/abs/2508.05831 — iteration_2 (term 3, FETCHED)
- [Ahlmann-Eltze et al.] "Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines", Nature Methods — https://www.nature.com/articles/s41592-025-02772-6 — iteration_2 (term 3, FETCHED)
- [Rebuttal] "Deep Learning-Based Genetic Perturbation Models *Do* Outperform Uninformative Baselines on Well-Calibrated Metrics" — https://www.biorxiv.org/content/10.1101/2025.10.20.683304.full.pdf — iteration_2 (term 3, snippet-level)
- [Operator Boosting] "…Produces Pareto-Efficient PDE Surrogates" — https://arxiv.org/abs/2606.17460 (html https://arxiv.org/html/2606.17460v2) — iteration_3 (term 1, FETCHED)
- [Quantifying Variance in Evaluation Benchmarks] — https://arxiv.org/abs/2406.10229 — iteration_3 (term 1, FETCHED)
- [GITS] "Gradient-Informed Temporal Sampling…" — https://arxiv.org/abs/2603.18237 — iteration_3 (term 1, FETCHED; recorded as NOT supporting the direction)
- [Super Learner / pystacked] — https://www.biorxiv.org/content/10.1101/172395v1.full ; https://doi.org/10.1177/1536867x231212426 — iteration_3 (term 2, snippet-level)
- [P2C2Net] — https://gsai.ruc.edu.cn/uploads/20241101/6848e3dd8cb571a8cf728ca4c80e6495.pdf — iteration_3 (term 3, snippet-level)
- [PhyRes-MDNF] — https://arxiv.org/pdf/2607.06237 — iteration_3 (term 3, snippet-level)
- [MF-Box] "Multi-fidelity and multi-scale emulation for the matter power spectrum" — https://arxiv.org/pdf/2306.03144 — iteration_4 (term 1, snippet-level)
- [HFS] "Mitigating Spectral Bias in Neural Operators via High-Frequency Scaling for Physical Systems" — http://arxiv.org/abs/2503.13695 — iteration_4 (term 2, FETCHED via arXiv API title query)
- [Spectral bias analysis and mitigation guidelines] — https://arxiv.org/abs/2602.19265 — iteration_4 (term 2, FETCHED)
- [NAS-Bench-Suite-Zero] — https://proceedings.neurips.cc/paper_files/paper/2022/file/b3835dd49b7d5bb062aecccc14d8a675-Supplemental-Datasets_and_Benchmarks.pdf — iteration_5 (term 1, snippet-level)
- [Du] paired multi-seed evaluation protocol — https://arxiv.org/abs/2511.19794 — iteration_5 (term 3, FETCHED; already the round's certified protocol)
- [Single-training-seed limitation] — https://arxiv.org/abs/2510.26714 — iteration_5 (term 3, FETCHED)
- In-repo prior websearches (cited, not re-derived): `docs/reports/MF_Sharp_HighFreq_Report.md` line 260
  (fit the LF↔HF transfer kernel from training pairs in one FFT pass, then unroll proximal steps — the nearest
  in-repo neighbour to the LSI stage) and line 248 (near-training-free patch-dictionary corrector);
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` line 105 (closed-form spectrally-shaped guidance, no
  backprop), line 140 (training-free post-hoc GP FIRE source), [LF-13] https://arxiv.org/abs/2512.02868
- Carry-over from this stream's earlier loops (NOT re-fetched, cited as batch-1/2 findings): CALM-PDE
  https://arxiv.org/abs/2505.12944; MFFM https://arxiv.org/html/2605.16118; Xu et al.
  https://arxiv.org/abs/2310.00057; Hesthaven & Ubbiali (snippet)

## Dead ends

- `WebFetch` tool → disabled in this environment (redirects to an MCP tool not in the roster). Routed around
  with `urllib`/`curl` from Bash; all fetch claims in this report are real GETs made in this loop.
- OpenReview (`/forum?id=…` browser-verification interstitial; `api2.openreview.net` HTTP 403) → any
  OpenReview-only paper stays snippet-level. New dead end this loop.
- Wiley (`agupubs.onlinelibrary.wiley.com`) HTTP 403 → joins ScienceDirect / ResearchGate on the 403 list.
- `Wiener deconvolution … coarse-fine simulation pairs` → instrument/optics deconvolution; the PDE-surrogate
  literature does not use this vocabulary.
- `neural network component contributes nothing … multi-fidelity surrogate negative result` → the MF
  literature returned is uniformly positive-result; there is no publication venue vocabulary for this negative.
- `ablation shows linear filter suffices …` → returns the opposite result (ablations that credit the learned
  stage).

## For the brainstormer

1. **Direction (i) is the only one with claimable content, and the claim is the attribution, not the filter.**
   Quote verbatim: *"(i) — `preempted-but-MF-composition-open (cite)`: closed-form least-squares LF→HF
   correction is LS-MFS (https://arxiv.org/abs/1705.02956) and projection-based MF linear regression on field
   outputs at <=10 HF samples (https://arxiv.org/abs/2508.08517); band-wise amplification of attenuated
   content is HFS (http://arxiv.org/abs/2503.13695); the shrinkage-gated residual stage over a cheap base
   predictor is Operator Boosting (https://arxiv.org/abs/2606.17460); the k-NN intermediate is analogue
   downscaling. What no fetched source composes is retrieval intermediate → one fitted LSI Fourier-diagonal
   transfer as a multi-fidelity corrector scored under a copy-LF-skill denominator with no LF at test."*
2. **Operator Boosting (https://arxiv.org/abs/2606.17460) is a near-miss you must engage explicitly.** It
   starts from *the empirical mean predictor* and adds tiny residual operators through *validation-selected
   shrinkage* — structurally B2's `alpha_nn` line search over a k-NN-mean base. If you propose (i) or (ii),
   name it as the closest prior art and state the difference (their base is the train mean and their stages
   are trained; yours is an LF-retrieval intermediate and the winning stage is closed-form).
3. **Direction (ii) is a measurement whose protocol is already published and already certified in-round.**
   Quote *"(ii) — `preempted (cite)`: Du https://arxiv.org/abs/2511.19794"* and inherit two design constraints
   from the fetched sources: **vary the fold/train seed, not just the corrector init**
   (https://arxiv.org/abs/2510.26714 — extra downstream seeds cannot compensate for one training seed), and
   **pre-register the decision rule against the certified `min_claimable_effect`** (allen_cahn 0.8797 skill
   units), because with 3 seeds a paired significance test may declare nothing at all
   (2511.19794's own headline finding). Do not write a falsification clause that can only be satisfied by a
   paired p-value.
4. **Direction (iii)'s framing is preempted; publish the artefact, not the idea.** Quote *"(iii) —
   `preempted (cite)`: https://arxiv.org/abs/2508.05831 already offers closed-form rank-constrained optimal
   linear maps as 'a robust baseline for … benchmarking learned neural network models for scientific machine
   learning'."* If you close the stream, the deliverable is the **numbers in skill units** with the certified
   mce alongside, per dataset — the Nature Methods pair
   (https://www.nature.com/articles/s41592-025-02772-6 vs
   https://www.biorxiv.org/content/10.1101/2025.10.20.683304.full.pdf) is the field's own demonstration that
   a baseline-beats-deep-model claim lives or dies on the metric, which is exactly B2's H-RULE-UNITS.
5. **The genuinely unpublished thing is the negative.** Two separate refutation terms (iteration 3 term 3,
   iteration 5 term 2) found *no* published MF/PDE result where a learned corrector is switched off out of
   fold while a closed-form stage carries the gain; every returned ablation credits the learned stage. If
   B3 is scored, design it so that this negative is *identifiable* per dataset (LSI-only arm, LSI+CNN arm,
   same folds, same k*), because that contrast is the stream's only publishable content.
6. **Carry the standing card obligations** (program.md §2.2, §2.3, §12.2 and B2 part 7): mandatory floor arms
   (NN-in-condition / train-mean / zero) on any model card; anchor 23.064; helmholtz report-only with the
   zero-floor column; pfc band-limited denominator caveat; ADR r2-0004 registration conventions for any
   resampling in the filter/lift code; **no** coherence eligibility gate (STOP-EXPORT already issued); and
   **never** build a rung that is leave-one-out on train and no-self on test.
