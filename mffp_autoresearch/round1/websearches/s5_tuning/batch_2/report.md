# Websearch Report — Stream `s5_tuning`, Batch 2

**Stream**: s5_tuning (tuning class, program.md §12.5 — knobs only)
**Batch**: 2
**Total iterations**: 5 (**cap hit: YES**, noted in `iteration_5.md`; an ENOUGH
on field context was recorded at the end of `iteration_4.md` and iteration 5 was
spent entirely on §3.3 refutation)
**WebSearch calls**: 15 (3 per iteration)
**WebFetch calls**: 23 attempted / 15 usable (8 non-yielding: The Well PDF, The
Well OpenReview, the_well GitHub README, Walrus PDF (>10 MB), doi.org ->
cross-host redirect notice, MDPI airfoil paper (HTTP 403), OTProf PDF,
sim-to-real RF PDF — each recorded inline and in Dead ends; none of their
contents are cited. Two of the 15 "usable" are weak: the QuadNorm PDF fetch and
the APEX PDF fetch returned summarizer paraphrase, so both are backed by their
`/abs/` fetches instead)

**Scope note**: this batch's candidate is the OUTPUT/TARGET SCALER
(B1 part 7 `next_direction`). The s5/s7 boundary is adjudicated explicitly in
every verdict below, because `websearches/s7_loss/batch_1/report.md` has already
claimed the per-sample *objective* forms (`C-REL`, `C-AMP`).

## Search trace

### Turn 1 — what the reference codebases/benchmarks actually normalize (Q1)
Terms: `PDEBench normalization ... UnitGaussianNormalizer per-channel mean std`;
`"the Well" dataset ... normalization strategy per-field statistics`;
`neuraloperator library UnitGaussianNormalizer transform output denormalize`.
Chosen to establish field-standard practice first-hand before touching the
champion's non-standard `max|Y|` scaler.
- **The reference FNO implementation is dataset-level, per-channel, Gaussian**:
  `UnitGaussianNormalizer` "normalizes data to be zero mean and unit std", with
  reduction dims that must "include the batch-size (typically 0)", giving
  `(1, C, 1, 1)` statistics; `fit()` = `torch.mean(..., dim=self.dim)` /
  `torch.std(...)`. Per-sample statistics are structurally impossible there.
  [cite: https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/data/transforms/normalizers.py]
- Normalization-statistic choice is an actively published axis for this model
  class: *"Normalization layers in neural operators usually compute statistics
  by uniformly averaging discrete grid values, making the normalization itself
  discretization-dependent and thereby a source of transfer error across
  different resolutions or meshes."* [cite: https://arxiv.org/abs/2605.07375]
- PDEBench yielded no first-hand normalization prescription; The Well fetches
  all failed this turn. → `iteration_1.md`

### Turn 2 — per-sample scaling and robust scalers (Q2, Q3)
Terms: `per-sample normalization neural operator instance normalization ...`;
`robust quantile scaler versus max-abs normalization scientific machine
learning outliers target scaling regression`; `reversible instance normalization
RevIN per-sample denormalization output model-agnostic distribution shift`.
Chosen because the §12.5 admissibility of per-sample scaling turns on whether it
is published as a wrapper or as a head.
- **Decisive for the boundary**: RevIN normalizes per instance and
  **denormalizes the output with the same statistics**
  (`x_tilde = alpha(x-mu_x)/sigma_x + beta`,
  `y_hat = sigma_x(f(x_tilde)-beta)/alpha + mu_x`), described as *"a
  preprocessing and postprocessing technique applicable across architectures"*,
  a *"normalization wrapper rather than an architectural modification"*; its
  ablations find the learnable affine *"not beneficial in practice"*, that
  training in normalized space beats denormalized training, and that RevIN
  *"does not address all forms of heterogeneity"*, notably conditional shift
  between input and output statistics.
  [cite: https://arxiv.org/html/2603.11869 ; https://seharanul17.github.io/RevIN/]
- **Max-abs is the documented-fragile choice**: *"MaxAbsScaler therefore also
  suffers from the presence of large outliers"* vs RobustScaler statistics
  *"based on percentiles and ... therefore not influenced by a small number of
  very large marginal outliers"*, with the quantile caveat that outliers are
  *"collapse[d] ... to the a priori defined range boundaries"* causing
  *"saturation artifacts"*.
  [cite: https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html]
  → `iteration_2.md`

### Turn 3 — stage consistency across pretrain -> finetune (Q4)
Terms: `pretraining fine-tuning normalization statistics mismatch ... AdaBN`;
`multiple physics pretraining PDE foundation model normalization across datasets
... per-sample scaling`; `Walrus ... normalization per-trajectory finetuning
full dataset statistics`.
- **PDE-domain precedent for per-sample denormalization**: MPP uses RevIN —
  *"We compute the mean and standard deviation of each channel over space-time
  dimensions and use them to normalize input fields ... These statistics are
  saved and used to denormalize model outputs"*, motivated by fields that
  *"operate on entirely different scales in terms of both magnitude and
  resolution"*. [cite: https://arxiv.org/html/2310.02994v2]
- **The transfer literature's prior is AGAINST stage-consistency**: AdaBN
  *"modulat[es] the statistics in all Batch Normalization layers"* to the target
  domain and is **parameter-free**, i.e. re-estimating on the target is the fix.
  [cite: https://arxiv.org/abs/1603.04779]
- Walrus deliberately uses **asymmetric input/output normalization**: *"Inputs
  and predicted updates are normalized separately, mitigating issues arising
  from differences in field value distributions"* (secondary source).
  [cite: https://www.emergentmind.com/papers/2511.15684] → `iteration_3.md`

### Turn 4 — the constant-predictor bar + MF-specific scaler practice (Q5), then ENOUGH
Terms: `VRMSE ... "the Well" ... predicting the mean baseline value 1`;
`trivial baseline constant predictor mean field sanity check neural operator
PDE benchmark`; `multi-fidelity neural network normalization low-fidelity
high-fidelity data same scaling factor`.
- **"Beat the mean predictor" is a published bar**: The Well's VRMSE is scaled so
  that *"predicting the mean value of the target field results in a score of
  1"*, chosen over NRMSE because *"the centered normalization is more
  appropriate for non-negative fields"*; its baseline table shows multiple
  operators at *">>>10"* (worse than the mean) on e.g.
  `rayleigh_taylor_instability` and `active_matter`.
  [cite: https://arxiv.org/html/2412.00568]
- Adversarial-baselining norm (different target — numerical solvers, not mean
  predictors): *"Of articles that use ML to solve a fluid-related PDE and claim
  to outperform a standard numerical method, we determine that 79% (60/76)
  compare to a weak baseline."* [cite: https://arxiv.org/html/2407.07218v1]
- The MF-surrogate literature **does not state its LF/HF normalization**: the
  closest scaling-law paper has *"no explicit discussion of normalization
  procedures"*. [cite: https://arxiv.org/html/2511.01830]
- **ENOUGH** recorded (all five open questions answered from fetched sources).
  → `iteration_4.md`

### Turn 5 — refutation pass + verdicts (CAP)
Terms: `predicted output magnitude scalar head neural operator predict field
amplitude separately normalize target per sample`; `percentile clipping quantile
normalization targets deep learning PDE surrogate 99th percentile scaling
instead of max`; `consistent normalization statistics between pretraining and
fine-tuning stages target scaler mismatch failure mode`.
- **The strongest preemption found all run**: APEX extracts a per-sample
  **amplitude anchor** from *a lower-frequency neural operator's prediction* in
  an explicitly target-scarce MF regime (higher-frequency data *"substantially
  more expensive to simulate or measure than lower-frequency data"*), keeping
  amplitude and discarding phase — but frames it as an **architecture** (coarse
  operator + amplitude extraction + flow-matching enhancer with phase priors).
  [cite: https://arxiv.org/abs/2605.26732]
- Physics-domain percentile-target-scaling instances were **snippet-only and
  unverifiable** (OTProf fetch failed); the generic preemption stands on the
  scikit-learn source from turn 2.
- No fetched source prescribes stage-consistency for a *target scaler*.
  → `iteration_5.md`

## Prior-art verdict

Territory: **K** = knob (s5-legal under §12.5), **O** = objective (s7, ADR 0012),
**A** = architecture (s6/s3/s4).

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **(i) Per-sample / condition-predicted output scaling** (normalize target per sample, denormalize prediction) in the MF LF-pretrain -> HF-finetune recipe | **`preempted-but-MF-composition-open`** | https://arxiv.org/html/2603.11869 ; https://seharanul17.github.io/RevIN/ (RevIN = model-agnostic normalize/denormalize wrapper; affine "not beneficial"; conditional-shift limitation) ; https://arxiv.org/html/2310.02994v2 (MPP: RevIN in PDE surrogates, statistics saved to denormalize outputs) ; https://arxiv.org/abs/2605.26732 (APEX: per-sample amplitude anchor from a coarser-fidelity operator, target-scarce MF, framed as architecture) | Applying per-sample normalize/denormalize as a **scaler-only** change **across a fidelity boundary** (LF-pretrain -> HF-finetune), network and MSE byte-identical, N_hf = 5..400, scored on unchanged per-sample rel-L2. **Territory ruling**: K only if the scale comes from an inference-available statistic with zero new parameters (LF-field statistic or closed-form function of the condition vector). A learned scale head = **A** (s6/s3). Per-sample target division **without** output denormalization = **O** = s7's already-claimed `C-REL`/`C-AMP`. |
| **(ii) Robust-quantile target scaling** (99.5th percentile / median-IQR) replacing `max|Y_train|`, incl. the few-shot HF stage | **`preempted`** (technique; zero novelty) | https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html ("MaxAbsScaler therefore also suffers from the presence of large outliers"; RobustScaler percentile statistics; QuantileTransformer saturation artifacts) ; https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html ; https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/data/transforms/normalizers.py (field-standard is per-channel mean/std, not max-abs) | Nothing novel — defensible ONLY as a measurement. Open as measurement: no fetched source quantifies robust-vs-max-abs **target** scaling in a **multi-fidelity few-shot** operator-learning regime; the nearest MF paper does not state its normalization at all (https://arxiv.org/html/2511.01830). Territory: **K**, unambiguously (two scalars, `smoke_eval.py:136-137`). |
| **(iii) Stage-consistent scaler discipline** (one scaler shared by LF-pretrain and HF-finetune, vs two re-derived) | **`novel`** (narrow) — with an **unfavourable literature prior** | Nearest neighbours: https://arxiv.org/abs/1603.04779 (AdaBN: re-estimate statistics on the target domain, parameter-free — the OPPOSITE prescription, for activation statistics) ; https://www.emergentmind.com/papers/2511.15684 (Walrus: inputs and predicted updates normalized separately, by design; secondary source) ; https://arxiv.org/html/2511.01830 (MF surrogate literature silent on LF/HF scaling) | The mechanism is unclaimed for a *target scaler* across a fidelity boundary, but the transfer literature treats stage-specific statistics as correct, so expect a null-or-negative sign. Value is as a **control arm** that removes a B1-part-7 hypothesis round-wide. Territory: **K**. |
| **(bonus) Reporting the constant-field-oracle reference line** alongside every panel number | **`preempted`** (and that is the desired answer) | https://arxiv.org/html/2412.00568 (The Well: "predicting the mean value of the target field results in a score of 1"; several operators at ">>>10") | Nothing — adopt as a standard reported bar with **no** novelty claim. Do NOT cite https://arxiv.org/html/2407.07218v1 for this: its weak-baseline audit targets numerical solvers, not mean predictors. |

## Citations summary

- [neuraloperator maintainers] `neuralop/data/transforms/normalizers.py` (`UnitGaussianNormalizer`) — https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/data/transforms/normalizers.py — used in: iteration_1, verdict (ii)
- [2026] "QuadNorm: Resolution-Robust Normalization for Neural Operators" — https://arxiv.org/abs/2605.07375 (PDF https://arxiv.org/pdf/2605.07375) — used in: iteration_1
- [Kossaifi et al. 2024] "A Library for Learning Neural Operators" — https://arxiv.org/html/2412.10354v1 — used in: iteration_1 (DataProcessor statement only)
- [2026] "On the Role of Reversible Instance Normalization" — https://arxiv.org/html/2603.11869 — used in: iteration_2, iteration_5, verdict (i)
- [Kim et al. 2022] "Reversible Instance Normalization for Accurate Time-Series Forecasting against Distribution Shift" (RevIN) — https://seharanul17.github.io/RevIN/ (other endpoints located, not fetched: https://openreview.net/forum?id=cGDAkQo1C0p , https://iclr.cc/virtual/2022/poster/6034 , https://github.com/ts-kim/RevIN) — used in: iteration_2, verdict (i)
- [scikit-learn docs] "Compare the effect of different scalers on data with outliers" — https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html — used in: iteration_2, iteration_5, verdict (ii)
- [scikit-learn docs] `RobustScaler` — https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html (search-returned; not fetched separately) — used in: iteration_2, verdict (ii)
- [Li et al. 2016] "Revisiting Batch Normalization For Practical Domain Adaptation" (AdaBN) — https://arxiv.org/abs/1603.04779 — used in: iteration_3, iteration_5, verdict (iii)
- [McCabe et al. 2023/24] "Multiple Physics Pretraining for Spatiotemporal Surrogate Models" — https://arxiv.org/html/2310.02994v2 — used in: iteration_3, verdict (i)
- [Walrus team 2025] "Walrus: A Cross-Domain Foundation Model for Continuum Dynamics" — https://www.emergentmind.com/papers/2511.15684 (**secondary source**; primary PDF https://arxiv.org/pdf/2511.15684 exceeded the fetch size cap) — used in: iteration_3, verdict (iii)
- [Ohana et al. 2024] "The Well: a Large-Scale Collection of Diverse Physics Simulations for Machine Learning" — https://arxiv.org/html/2412.00568 — used in: iteration_4, bonus verdict
- [McGreivy & Hakim 2024] "Weak baselines and reporting biases lead to overoptimism in machine learning for fluid-related partial differential equations" — https://arxiv.org/html/2407.07218v1 — used in: iteration_4 (79%/weak-baseline statistic only)
- [2025] "Towards Multi-Fidelity Scaling Laws of Neural Surrogates in CFD" — https://arxiv.org/html/2511.01830 — used in: iteration_4, verdicts (ii)/(iii) (as evidence of silence on normalization)
- [2026] "APEX: Amplitude Anchors and Phase Priors for Target-Scarce Higher-Frequency Wave Prediction" — https://arxiv.org/abs/2605.26732 (PDF https://arxiv.org/pdf/2605.26732) — used in: iteration_5, verdict (i)

**Unverified leads — MUST NOT be cited**: the claim that The Well normalizes
per-field from training-split statistics (snippet only; the fetched paper does
not state its training normalization); the claim that pretraining uses
per-trajectory normalization while finetuning switches to full-dataset
statistics (snippet only; Walrus PDF over the size cap); OTProf's
1st/99th-percentile normalization (https://arxiv.org/pdf/2604.09346 — fetch
failed); the MDPI airfoil paper's "logarithmic-exponential normalization" for MF
transfer (HTTP 403); the sim-to-real claim that both domains are normalized with
target-domain statistics (https://arxiv.org/pdf/2607.04400 — fetch failed);
scikit-learn `QuantileTransformer` use for physics-ML *targets* (source not
isolated); the "normalization must be global or function-wise to preserve
discretization invariance" snippet; AdaFilter's two-BN design
(https://arxiv.org/pdf/1911.09659 — search-level only).

## Dead ends

- **PDEBench normalization prescription** — three primary endpoints located
  (https://arxiv.org/pdf/2210.07182 , the NeurIPS paper + supplement); the
  returned material covers data format and metrics, not a training
  normalization rule. PDEBench appears not to prescribe one.
- **The Well, three failed routes** — PDF (https://danfortunato.com/papers/TheWell.pdf)
  undecodable binary; OpenReview (https://openreview.net/forum?id=00Sx577BT3)
  served a browser-verification page; GitHub README
  (https://github.com/PolymathicAI/the_well) has no normalization text. The
  arXiv HTML endpoint (https://arxiv.org/html/2412.00568) worked in turn 4 —
  **lesson: go to `arxiv.org/html/` first**.
- **Walrus primary PDF** — exceeded the 10 MB WebFetch cap; the one on-target
  sentence about pretrain-vs-finetune normalization statistics remains
  unverified and uncited.
- **MDPI** (https://www.mdpi.com/2076-3417/15/19/10820) — HTTP 403 after a
  cross-host redirect from doi.org. Its bespoke MF normalization claim is lost.
- **`per-sample normalization neural operator instance normalization ...`** — the
  operator-learning-framed query returned style-transfer/AdaIN patents; the
  productive route to the same content was the time-series term (RevIN).
- **`percentile clipping ... PDE surrogate`** — every physics instance was
  snippet-level and its PDF unparsable; only the generic scikit-learn
  documentation survived as a citation.
- **arXiv PDF endpoints** — 4 of 6 `arxiv.org/pdf/*` fetches returned
  unparsable binary or exceeded the size cap (2604.09346, 2607.04400,
  2511.15684, plus partial value from 2605.07375 and 2605.26732).
  `arxiv.org/abs` and `arxiv.org/html` worked 7/7.

## For the brainstormer

The brainstormer MUST quote the verdict row for whatever it proposes.

1. **The stream-boundary test is now a hard, citable rule — apply it before
   anything else.** A per-sample scale is **s5-legal only if it is computed from
   data available at inference with zero new parameters and the prediction is
   DENORMALIZED with the same scalar** (RevIN's construction,
   https://arxiv.org/html/2603.11869). Predict the scale with a learned head and
   the card belongs to s6/s3; divide the target per-sample without
   denormalizing and you have written s7's `C-REL`/`C-AMP`, which
   `websearches/s7_loss/batch_1/report.md` has already claimed. Say in the card
   which of the three you are doing.
2. **Rank (ii) first for defensibility, (i) first for upside.** (ii) robust
   scaler is a two-scalar edit at `smoke_eval.py:136-137`, verdict `preempted`
   (claim nothing), and it attacks exactly the documented weakness of the
   current scheme: *"MaxAbsScaler therefore also suffers from the presence of
   large outliers"*
   (https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html).
   (i) has the larger measured headroom (B1: amplitude is 70–87% of the
   helmholtz error, fitted alpha 0.05–0.07; per-sample HF norms span 408x) but
   carries the `preempted-but-MF-composition-open` verdict, so its write-up must
   cite RevIN + MPP + APEX and claim only the MF-scaler composition.
   ADR 0007 applies (propose 3–5, screen at contract tier): a natural pool is
   {global max-abs (control), robust 99.5th-percentile, dataset z-score
   (per-channel mean/std = the neuraloperator default,
   https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/data/transforms/normalizers.py),
   LF-statistic per-sample RevIN-style, shared LF/HF scaler}.
3. **Pre-register RevIN's own two documented failure modes.** Its ablation says
   the learnable affine is *"not beneficial in practice"* (so do not add one —
   it would also cost you the knob status), and RevIN *"does not address all
   forms of heterogeneity"*, specifically **conditional distribution shift
   between input and output statistics** — for us, the per-sample LF->HF scale
   ratio. If that ratio has heavy spread on the panel, the arm cannot work; that
   is a one-line pre-check on data the round already has, and it belongs in the
   falsification clause.
4. **Expect stage-consistency (iii) to lose, and say so up front.** AdaBN's
   published prescription is the opposite — re-estimate statistics on the target
   domain, parameter-free (https://arxiv.org/abs/1603.04779) — and Walrus
   normalizes inputs and outputs separately by design
   (https://www.emergentmind.com/papers/2511.15684). Keep (iii) as the cheap
   control arm that retires a B1-part-7 hypothesis round-wide, not as the
   headline.
5. **Adopt the constant-field-oracle reference line for free.** The Well scales
   its primary metric so *"predicting the mean value of the target field results
   in a score of 1"* and reports operators far above it
   (https://arxiv.org/html/2412.00568). Report every panel number against
   `tools/dc_pattern_split.py`'s oracle (B1 part 7's SECONDARY recommendation)
   and cite The Well — a published bar, no novelty claimed.
6. **Thresholds, unchanged from the round's arithmetic.** Anchor 6.703 panel
   geomean (`state/anchors/s5_tuning.json`), geomean floor 0.884, and the
   dataset that motivates the whole amplitude story — `ext__helmholtz_2d` —
   has `min_claimable_effect` 9.695 (`state/noise_floor.json`), i.e. **it cannot
   carry the verdict**. State falsification on `sharp__allen_cahn_2d` (1.633),
   `sharp__phase_field_crystal_2d` (1.151), `sharp__cahn_hilliard` (0.553),
   `sharp__fisher_kpp_2d` (0.418), or the geomean; report helmholtz
   qualitatively. Note also the quantile-saturation caveat from the same
   scikit-learn source: clipping helmholtz's 50x worst-sample tail changes what
   the model is asked to fit.
