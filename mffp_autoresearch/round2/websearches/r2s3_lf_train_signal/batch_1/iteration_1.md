# iteration_1 — `r2s3_lf_train_signal`, batch 1

## Search rationale

program.md §12.3 names three candidate mechanisms: (a) distillation from an
LF-consuming teacher, (b) LF-pretrain→HF-finetune, (c) auxiliary MF losses.
(b) is already occupied by the mandatory declared baseline
`mf_fno_transfer_film` and is heavily covered in
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` §4.2, so turn 1 spends its
three terms on (a) and (c), plus the general "privileged information" framing
that is the theoretical home of "input available at train, absent at test".

## Search terms used

1. `knowledge distillation multi-fidelity teacher low-fidelity input student parameter-only PDE surrogate`
2. `learning using privileged information neural operator PDE surrogate low-fidelity available only at training`
3. `multi-resolution auxiliary loss coarse grid supervision neural operator few high-fidelity samples`

## Findings per term

### Term 1 — KD from an LF-consuming teacher

- **[MOST RELEVANT] "Learning from more to predict with less: Representation-level
  multimodal distillation to address training–inference data asymmetry in
  surrogate modeling"** — Engineering Applications of AI, ScienceDirect,
  https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 .
  Search-result abstract text: "a multimodal teacher-student framework distills
  knowledge from privileged modalities via representation-level learning into a
  lightweight student model designed to operate solely on primary,
  deployment-feasible inputs… feature-level distillation guides the student to
  align its internal feature representation with the teacher". This is EXACTLY
  the train-time-only-extra-input framing for *surrogate modeling*. WebFetch
  returned HTTP 403 (paywall) — no full text obtained this turn; the title +
  abstract snippet above are what the search returned. Follow-up needed to
  establish whether the privileged modality is a low-fidelity *simulation* and
  whether the student is condition-vector-only.
- KD-PINN (https://arxiv.org/pdf/2512.13336): distillation is large-PINN →
  small-PINN for latency. Same-input compression, not fidelity asymmetry. Not
  our mechanism.
- Multi-fidelity NAS with KD (https://arxiv.org/pdf/2006.08341): KD loss used to
  improve *low-fidelity evaluations of architectures* inside NAS. Different
  meaning of "multi-fidelity"; irrelevant.
- Physics-informed distillation of diffusion models
  (https://arxiv.org/pdf/2505.22391): sampler-step distillation. Irrelevant.

### Term 2 — LUPI / privileged information for operators

- **"Neural Emulator Superiority: When Machine Learning for PDEs Surpasses its
  Training Data"** — https://arxiv.org/html/2510.23111 . Search snippet:
  networks trained *purely on low-fidelity solver data* can beat those solvers
  when scored against a higher-fidelity reference, via inductive bias +
  regularized dynamics. Directly relevant to r2s3's falsification framing: an
  LF-only-trained condition→field model is a legitimate arm, and "LF training
  signal can exceed the LF solver" has precedent.
- "Transfer Learning on Multi-Dimensional Data: A Novel Approach to Neural
  Network-Based Surrogate Modeling" — https://arxiv.org/pdf/2410.12241 .
- Plasma-edge neural-operator surrogates (data efficiency):
  https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb . Search snippet
  for the transfer-learning result: "an order-of-magnitude reduction when
  transferring from low- to high-fidelity datasets" at small dataset sizes,
  diminishing with larger datasets. This is quantified prior art for the
  pretrain→finetune arm, i.e. it strengthens the rebadge risk on that arm.
- No result framed as *learning using privileged information* (Vapnik) applied
  to neural operators. Gap candidate — needs a direct LUPI-term search.

### Term 3 — multi-resolution / coarse-grid auxiliary supervision

- **"A Physics-informed Multi-resolution Neural Operator"** —
  https://arxiv.org/html/2510.23810 . FETCHED. Explicitly *distinguishes itself
  from* multi-fidelity: "we distinguish multi-resolution from multi-fidelity in
  the sense that multi-fidelity typically implies a loss of information from
  high-fidelity to low-fidelity"; all data derives from the same PDEs at
  sufficient resolution and **coarse grids are NOT used as auxiliary training
  signals**. Test-time input is a discretized input *function* projected onto
  pretrained bases — not a condition vector. 150–800 training samples. So it is
  a near neighbor that does NOT preempt coarse-as-auxiliary-target.
- Multi-Grid Tensorized FNO (https://arxiv.org/html/2310.00120): coarse→fine
  inputs as multi-grid *input* construction for high-resolution PDEs; field
  input at test. Not train-only LF.
- Search snippet (unattributed to a fetched paper): "neural operator models can
  be pre-trained with cheap coarse-grid simulation data and a small amount of
  fully-resolved data, then trained with physics-informed loss on fine grids".
  Recorded as a lead only — no URL isolated for it this turn; NOT citable.
- Coarse-graining with neural operators for chaotic systems
  (https://arxiv.org/pdf/2408.05177): learns the coarse-graining map itself,
  field-in/field-out. Not our regime.

## Interpretation

The pretrain→finetune arm is well-populated prior art (plasma-edge paper
quantifies an order-of-magnitude small-data gain), reinforcing §12.3's rebadge
warning. The genuinely promising novelty surface is the *representation-level
distillation from an LF-consuming teacher into a condition-only student* — one
paper appears to occupy exactly that slot in surrogate modeling generally, but
it is paywalled and its privileged modality may not be a coarse solve; that
must be resolved before the brainstormer can claim novelty. Coarse-grid-as-
auxiliary-target under a *nested* ladder is not yet shown preempted; the closest
multi-resolution operator paper explicitly disclaims the multi-fidelity reading.
