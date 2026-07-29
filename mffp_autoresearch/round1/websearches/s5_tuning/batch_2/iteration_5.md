# Iteration 5 (FINAL, cap = 5 reached) — refutation searches + prior-art verdicts

## Search rationale

§3.3 mandates a refutation pass. The three candidate directions the s5-B2 card
can propose are exactly the three the orchestrator named:
(i) **per-sample / condition-predicted output scaling** as a pure-knob change in
the MF LF-pretrain -> HF-finetune recipe;
(ii) **robust-quantile target scaling** replacing `max|Y_train|`, in the
few-shot HF fine-tuning regime;
(iii) **stage-consistent scaler discipline** (one scaler shared across
LF-pretrain and HF-finetune instead of two re-derived ones).
Each term below is chosen to REFUTE novelty, i.e. to find the paper that
already did it.

## Search terms used

1. `predicted output magnitude scalar head neural operator predict field amplitude separately normalize target per sample operator learning` (refute (i))
2. `percentile clipping quantile normalization targets deep learning PDE surrogate 99th percentile scaling instead of max` (refute (ii))
3. `consistent normalization statistics between pretraining and fine-tuning stages target scaler mismatch failure mode neural network regression` (refute (iii))

## Findings

### Term 1 (refute (i)) — APEX: amplitude anchoring in a target-scarce MF wave setting — HIT
- Fetched https://arxiv.org/abs/2605.26732 and https://arxiv.org/pdf/2605.26732
  ("APEX: Amplitude Anchors and Phase Priors for Target-Scarce Higher-Frequency
  Wave Prediction"). Abstract opening verbatim: *"Learning-based surrogates have
  become increasingly effective for wave-field prediction, and neural operators
  in particular have shown strong performance within observed frequency
  regimes."* The mechanism, per the fetch: the **amplitude anchor is the coarse
  amplitude structure extracted from a lower-frequency neural operator's
  prediction at the target frequency**, keeping amplitude and discarding phase,
  on the observation that "amplitude remains relatively stable across
  frequencies while phase deteriorates"; the regime is explicitly
  **multi-fidelity/target-scarce** — higher-frequency data are *"substantially
  more expensive to simulate or measure than lower-frequency data."* The
  contribution is framed as an **architecture** (low-frequency operator +
  amplitude extraction + conditional flow-matching enhancer with
  Green's-function-inspired phase priors), **not** as a normalization device.
- Combined with iteration 2 (RevIN: per-sample normalize-in / denormalize-out,
  *"a preprocessing and postprocessing technique applicable across
  architectures"*, https://arxiv.org/html/2603.11869 ,
  https://seharanul17.github.io/RevIN/) and iteration 3 (MPP applies RevIN in
  PDE surrogates: *"We compute the mean and standard deviation of each channel
  over space-time dimensions and use them to normalize input fields ... These
  statistics are saved and used to denormalize model outputs."*
  https://arxiv.org/html/2310.02994v2), the mechanism is comprehensively
  published; what no fetched source does is apply per-sample
  normalize/denormalize **as a scaler-only knob across an LF-pretrain ->
  HF-finetune fidelity boundary with the network and MSE objective unchanged**.
- Other hits inspected at search level, not fetched, not cited: multi-head
  neural operator for interfacial dynamics
  (https://www.sciencedirect.com/science/article/pii/S0020740326002195),
  PINO for parametric phase-field (https://arxiv.org/html/2603.09693).

### Term 2 (refute (ii)) — quantile/percentile target scaling — preempted generically, unfetchable in PDE
- The generic-ML preemption is already fetched and unambiguous (iteration 2,
  https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html):
  *"MaxAbsScaler therefore also suffers from the presence of large outliers"*;
  *"the centering and scaling statistics of RobustScaler are based on
  percentiles and are therefore not influenced by a small number of very large
  marginal outliers"*; plus the QuantileTransformer saturation caveat.
- The physics-domain instances found in this turn are **snippet-only and I
  could not verify them**: a claim that "for variables with occasional outliers,
  the 1st and 99th percentiles are used instead", with percentiles computed on
  the training set and applied to validation/test, attributed to OTProf
  (https://arxiv.org/pdf/2604.09346 — **fetch failed**, PDF text not
  extractable), and a claim that physics-ML target variables are transformed
  with scikit-learn's QuantileTransformer (source not isolated). Also
  search-level: percentile calibration in quantization
  (https://arxiv.org/pdf/2004.09602 — *"99% calibration would clip 1% of the
  largest magnitude values"*, quantization, not target scaling; not fetched).
  **None of these are citable.** No fetched source applies robust-quantile
  *target* scaling to few-shot HF fine-tuning of a neural operator.

### Term 3 (refute (iii)) — stage-consistency of normalization statistics
- No fetched source states a stage-consistency rule for a *target scaler* in a
  pretrain->finetune regression pipeline. The nearest fetched neighbours point
  the OPPOSITE way: AdaBN (https://arxiv.org/abs/1603.04779), *"By modulating
  the statistics in all Batch Normalization layers across the network, our
  approach achieves deep adaptation effect for domain adaptation tasks"*,
  **parameter-free**, i.e. re-estimating statistics on the target domain is the
  published *fix*; and Walrus' deliberate **asymmetric input/output
  normalization** — *"Inputs and predicted updates are normalized separately,
  mitigating issues arising from differences in field value distributions"*
  (secondary source https://www.emergentmind.com/papers/2511.15684 ).
- Refutation attempt that FAILED: https://arxiv.org/pdf/2607.04400 (sim-to-real
  RF positioning; the search snippet claimed both domains are normalized with
  statistics estimated from the *real/target* dataset to keep the input scale
  tied to the fine-tuning domain) — **PDF unparsable, not citable**. Other
  search-level leads not fetched: https://arxiv.org/html/2602.20062v1 (theory
  of how pretraining shapes inductive bias in fine-tuning),
  https://arxiv.org/pdf/2302.07937 (expressive power of tuning only the
  normalization layers), and a PyTorch-forum thread on normalization statistics
  for fine-tuning (https://discuss.pytorch.org/t/180764) — forum, not citable.

## PRIOR-ART VERDICTS

**Territory legend** — K = knob (s5, §12.5: preprocessing only, network and
objective byte-identical), O = objective (s7, ADR 0012), A = architecture
(s6/s3/s4).

### (i) Per-sample / condition-predicted output scaling, as a knob, in MF transfer
**Verdict: `preempted-but-MF-composition-open`.**
- Preempted as a mechanism, three ways, all fetched this loop:
  RevIN is per-sample normalize-in/denormalize-out and is explicitly
  *"model-agnostic"*, *"a normalization wrapper rather than an architectural
  modification"* (https://arxiv.org/html/2603.11869 ;
  https://seharanul17.github.io/RevIN/); MPP already imports RevIN into PDE
  surrogate training and *saves the statistics to denormalize model outputs*
  (https://arxiv.org/html/2310.02994v2); and APEX already does per-sample
  **amplitude anchoring from a coarser-fidelity prediction in a target-scarce
  higher-frequency transfer setting** (https://arxiv.org/abs/2605.26732).
- What remains open: **no fetched source applies per-sample
  normalize/denormalize as a scaler-only change across a fidelity boundary
  (LF-pretrain -> HF-finetune) with the architecture and MSE objective
  unchanged, at N_hf = 5..400, scored on unchanged per-sample rel-L2.** MPP has
  no fidelity ladder and takes statistics from its own input fields; APEX buys
  the amplitude with a second operator plus a flow-matching enhancer.
- **Territory ruling (load-bearing for this stream):** three variants of "(i)"
  live in three different streams and only one is s5's.
  * K (s5-legal): the per-sample scale is computed from data **available at
    inference without new parameters** — in this repo that means the LF field's
    own statistic (`max|LF_i|`, `std(LF_i)`, `||LF_i||_2`) or a closed-form
    function of the condition vector, used to normalize the target and to
    denormalize the prediction. No layer, no weight, no loss term added; RevIN's
    own ablation even says drop the learnable affine (*"not beneficial in
    practice"*). Note the honest caveat this incurs: reading an LF statistic at
    inference makes the pipeline LF-aware in the scale scalar only, and the card
    must say so explicitly, because s2-B1 established the champion is otherwise
    LF-blind.
  * O (s7, ALREADY CLAIMED — do not touch): dividing the target by a per-sample
    scalar **without denormalizing the output** is a per-sample relative loss —
    that is s7's `C-REL` / `C-AMP`
    (`websearches/s7_loss/batch_1/report.md`, verdict rows).
  * A (s6/s3): a learned scalar head predicting the scale, or a second operator
    supplying the amplitude (APEX's construction).
- **Documented risk to pre-register**: RevIN's own analysis says it *"does not
  address all forms of heterogeneity"*, specifically **conditional distribution
  shift between input and output statistics** — i.e. exactly the LF->HF scale
  ratio drifting per sample. Quantify that ratio on the panel before betting on
  the arm.

### (ii) Robust-quantile target scaling for few-shot HF fine-tuning
**Verdict: `preempted` (as a technique) — legitimate only as a measurement.**
- The mechanism is library-documented standard practice, and the specific
  weakness of the champion's scaler is named in the citation:
  *"MaxAbsScaler therefore also suffers from the presence of large outliers"*,
  versus RobustScaler's percentile statistics *"not influenced by a small
  number of very large marginal outliers"*
  (https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html ;
  estimator doc https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html).
  Also relevant as the field-standard alternative: the reference operator
  library normalizes with dataset-level per-channel **mean/std**, never max-abs
  (https://raw.githubusercontent.com/neuraloperator/neuraloperator/main/neuralop/data/transforms/normalizers.py).
- What remains open (measurement, not novelty): **no fetched source measures the
  effect of a robust vs max-abs TARGET scaler in a few-shot HF fine-tuning /
  multi-fidelity operator-learning regime.** The nearest MF paper found does not
  even state its normalization (https://arxiv.org/html/2511.01830). Claim
  nothing beyond "we measured a standard preprocessing choice in a regime where
  it is unmeasured".
- **Territory: K, unambiguously** — it is a change of two scalars
  (`smoke_eval.py:136-137`), zero parameters, objective untouched. Safest s5 arm
  on the boundary test.
- Pre-register the documented downside: quantile transforms *"automatically
  collapse any outlier ... can result in saturation artifacts for extreme
  values"* (same source) — on `ext__helmholtz_2d`, where B1 measured a
  50x-worst-sample amplitude tail, clipping the tail changes what the model is
  asked to fit.

### (iii) Stage-consistent scaler discipline (share one scaler across LF/HF stages)
**Verdict: `novel` (narrow, and with an unfavourable literature prior).**
- Nothing close found. Nearest neighbours, both fetched: AdaBN
  (https://arxiv.org/abs/1603.04779) makes the opposite prescription for
  *activation* statistics — re-estimate on the target domain, parameter-free —
  and Walrus deliberately normalizes inputs and outputs by **separate**
  statistics (https://www.emergentmind.com/papers/2511.15684 , secondary).
  AdaFilter's two-BN design (https://arxiv.org/pdf/1911.09659 , search-level)
  keeps pretrain and finetune statistics separate rather than sharing them. The
  MF-surrogate literature is silent on LF/HF target scaling
  (https://arxiv.org/html/2511.01830).
- So the *mechanism* is unclaimed but the *expected sign is against us*: the
  transfer literature treats stage-specific statistics as correct. Honest
  framing: this is a cheap **control arm** that isolates how much of the
  amplitude failure is caused by re-anchoring the output scale at the
  fine-tune boundary — not a headline. If it wins, that is a genuinely new
  (small) fact about MF transfer recipes; if it loses, it removes a hypothesis
  from B1 part 7 for the whole round.
- **Territory: K** (two scalars again; no parameters, no objective change).

### Bonus verdict — reporting the constant-field-oracle reference line
**Verdict: `preempted`, and that is good news.** The Well's primary metric is
constructed so that *"predicting the mean value of the target field results in a
score of 1"*, and its own baseline table shows multiple neural operators
scoring far above 1 on several datasets
(https://arxiv.org/html/2412.00568). So B1's constant-field-oracle finding is a
standard published sanity bar; s5-B2 may adopt it as a reported reference line
with **no novelty claim**. (McGreivy & Hakim's weak-baselines audit —
*"79% (60/76) compare to a weak baseline"*, https://arxiv.org/html/2407.07218v1
— supports the norm of adversarial baselining but targets numerical solvers,
not mean predictors; do not mis-cite it for the mean-predictor bar.)

## Interpretation

The safe-and-cheap end of the batch-2 design space ((ii) robust scaler, (iii)
stage-consistent scaler) is pure-knob and fully s5-legal but carries zero
novelty and, for (iii), an unfavourable prior. The high-upside direction ((i)
per-sample scaling) is admissible for s5 **only** in the RevIN-faithful,
zero-parameter, denormalize-the-output form with the scale taken from an
inference-available statistic; any learned scale head is s6/s3 architecture and
any un-denormalized per-sample division is s7's already-claimed objective card.

**CAP NOTE**: this is iteration 5 of 5; the §3.2 cap is reached and the loop
stops here. Two refutation fetches failed (OTProf percentile statement, the
sim-to-real normalization statement) and are recorded as uncited leads for a
future batch.
