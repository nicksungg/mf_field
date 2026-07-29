# Iteration 3 — stage consistency: normalization statistics across pretrain -> finetune

## Search rationale

Open question Q4, the s5-specific one. The champion re-derives its output
scaler between the LF-pretrain and HF-finetune stages
(`smoke_eval.py:136-137`), so the network's output scale is re-anchored exactly
at the transition where only 5 (ifc_poisson) to 400 (sharp) HF samples are
available. Two literatures could document this as a failure mode: (i) the
transfer-learning normalization-statistics literature (AdaBN and descendants),
(ii) PDE foundation models, which are the only papers that must normalize
heterogeneous-amplitude fields across a pretrain->finetune boundary. Also picks
up whether per-sample normalization has a *PDE-domain* precedent (iteration 2's
RevIN evidence is time-series).

## Search terms used

1. `pretraining fine-tuning normalization statistics mismatch batch norm statistics transfer AdaBN adapting normalization to target domain`
2. `multiple physics pretraining PDE foundation model normalization across datasets different field amplitudes per-sample scaling strategy`
3. `Walrus cross-domain foundation model continuum dynamics normalization per-trajectory finetuning full dataset statistics`

## Findings

### Term 1 — AdaBN / normalization-statistics transfer — USABLE
- Fetched https://arxiv.org/abs/1603.04779 (Li et al., "Revisiting Batch
  Normalization For Practical Domain Adaptation", AdaBN). Abstract quote:
  *"By modulating the statistics in all Batch Normalization layers across the
  network, our approach achieves deep adaptation effect for domain adaptation
  tasks."* The abstract states the method **is parameter-free**. The mechanism
  is precisely: statistics learned on the source (pretrain) domain are
  *replaced* by target-domain statistics, weights untouched.
- Search-level (not fetched, recorded as leads): AdaFilter
  https://arxiv.org/pdf/1911.09659 keeps **two** BN layers, one for pretrained
  and one for fine-tuned channels, i.e. the field's answer when source and
  target statistics disagree is to separate them rather than share them;
  OpenReview mirror https://openreview.net/forum?id=BJuysoFeg ; ConvLoRA+AdaBN
  https://arxiv.org/pdf/2402.04964 .
- Bearing on our knob: this literature says re-deriving statistics on the
  target domain is *correct*, not a bug — the opposite prior to "make the
  scaler stage-consistent". It also shows the axis is well-trodden but for
  **internal activation statistics**, not for a scalar target scaler in a
  regression head.

### Term 2 — Multiple Physics Pretraining (MPP) — USABLE, PDE-domain per-sample precedent
- Fetched https://arxiv.org/html/2310.02994v2 (McCabe et al., "Multiple Physics
  Pretraining for Spatiotemporal Surrogate Models"). Verbatim:
  *"To unify magnitudes, we use Reversible Instance Normalization (Kim et al.,
  2022, RevIN). We compute the mean and standard deviation of each channel over
  space-time dimensions and use them to normalize input fields."* and
  *"These statistics are saved and used to denormalize model outputs."*
  Motivation, verbatim: *"Embedding multiple physical systems into a single
  shared representation is complicated by the fact that fields from different
  systems may operate on entirely different scales in terms of both magnitude
  and resolution."*
- So **per-sample (instance) normalize-and-denormalize is already published in
  the PDE-surrogate domain**, as a data-pipeline device for exactly our
  problem statement (fields at wildly different magnitudes sharing one
  network). Crucially the statistics come from the **input fields**, which the
  model sees; MPP is autoregressive, so input and target are the same physical
  field at adjacent times.
- The fetched HTML gives **no** pretrain-vs-finetune normalization comparison
  ("The document does not explicitly compare per-trajectory versus full-dataset
  statistics between pretraining and fine-tuning phases").

### Term 3 — Walrus (largest cross-domain PDE FM) — partially usable, secondary source
- https://arxiv.org/pdf/2511.15684 fetch **FAILED** (exceeded the 10 MB
  content-length cap). Fetched the secondary summary page instead,
  https://www.emergentmind.com/papers/2511.15684 , which reports Walrus'
  **"asymmetric input/output normalization"**: *"Inputs and predicted updates
  are normalized separately, mitigating issues arising from differences in
  field value distributions"*, together with predicting the state *change*
  rather than the next state. Flagged **secondary-source paraphrase** — usable
  to establish that separate input/output scalers are a deliberate published
  design, not usable for numbers.
- **UNVERIFIED LEAD, MUST NOT BE CITED**: a term-2 search snippet asserted
  "during pretraining, per-trajectory normalization is used ...; during
  finetuning when the model has access to a small finetuning set, it can be
  advantageous to employ normalization computed over the full dataset." This is
  the single most on-target sentence found for Q4 and I could not attach it to a
  fetched source (Walrus PDF over the size cap, no HTML endpoint). Recorded as
  a lead for a retry; not cited anywhere.
- Other primary endpoints located but not fetched:
  https://arxiv.org/abs/2511.15684 , https://www.alphaxiv.org/hi/overview/2511.15684v1 .

## Interpretation

Two opposed priors are now on the table for stage-consistency, both fetched:
AdaBN says **re-estimating statistics on the target domain is the fix** (and
AdaFilter goes further, keeping source and target statistics separate), while
Walrus' asymmetric input/output normalization says separate scalers for
different distributions are deliberate design. Neither supports "one shared
LF/HF scaler is obviously better"; a stage-consistency arm is therefore a
genuine open question rather than a known win, and its expected sign is not
established by literature — which makes it a legitimate but *low-prior* knob.
MPP supplies the PDE-domain citation that per-sample normalize/denormalize is
standard practice, closing Q2 in the PDE domain as well as the time-series one.
