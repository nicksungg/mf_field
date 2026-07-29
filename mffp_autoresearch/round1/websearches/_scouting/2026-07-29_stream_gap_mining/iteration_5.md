# Iteration 5 — closing sweep + MANDATORY candidate verdicts

**ITERATION CAP HIT: this is iteration 5 of 5.** No further searching.

## Search rationale

Two gaps remained. (1) The in-round helmholtz measurement (86.5% of the
champion's error is a per-sample amplitude/normalization divergence; alpha_mean
0.73-0.78 on cahn_hilliard/pfc) points at a scale-calibration mechanism nobody
has assessed for prior art. (2) The knn10-beats-champion finding deserves a
check against the "simple baselines beat learned surrogates" methodological
literature, because if that is a known benchmarking pathology it changes how
the operator should read our own numbers. I also spent one term on the
strongest possible refutation framing for C1 (the "never worse" guarantee),
outside the PDE vocabulary entirely.

## Search terms used

1. `simple baselines outperform neural operators benchmark critique nearest
   neighbor interpolation beats trained surrogate`
2. `per-sample amplitude scale calibration neural operator output magnitude
   relative L2 normalization error field prediction`
3. `"never worse" guarantee ensemble model selection blend with baseline
   regression safe improvement machine learning surrogate`

## Findings per term

### T1 — weak-baseline / benchmarking critique

- **Optimal Linear Baseline Models for Scientific Machine Learning** —
  https://arxiv.org/html/2508.05831 — FETCHED. Rank-constrained linear
  encoder-decoder baselines with closed-form Bayes-risk-optimal solutions for
  forward modelling, inverse problems, autoencoding. On **shallow water
  equations** linear models "capture essential dynamics effectively without
  hyperparameter tuning", and the paper's stated lesson is that "nonlinearity
  in the system does not guarantee that nonlinear neural network models
  outperform linear ones." Targeted validation, not a broad benchmark sweep.
- Supporting hits (not fetched): CFDONEval https://www.ijcai.org/proceedings/2025/0640.pdf;
  comprehensive comparison of NOs for 3-D industry-scale designs
  https://arxiv.org/abs/2510.05995; comparative review of NO architectures
  https://www.sciencedirect.com/science/article/abs/pii/S0925231225011907;
  and the cross-domain analogue "Deep-learning-based gene perturbation effect
  prediction does not yet outperform simple linear baselines"
  https://www.nature.com/articles/s41592-025-02772-6.
- **Reading**: "a training-free baseline beats the trained model" is an
  established, publishable failure signature in SciML benchmarking. This
  *supports* the round's own diagnostic reading and argues the finding is real,
  not an artefact — but it is a methodological result, not a mechanism, so it
  cannot itself become a stream.

### T2 — amplitude / scale calibration

- No operator-learning-specific amplitude-calibration method surfaced. The
  closest is **Parametric rho-Norm Scaling Calibration**
  https://arxiv.org/html/2412.15301, which regulates "the influence of output
  amplitude on scaling calibration" — but in output-*probability* mapping
  (classifier confidence calibration), not field amplitude.
- Generic supporting hits: data scaling/normalization effects on NN
  performance https://link.springer.com/article/10.1007/s11082-022-03799-1;
  documented limitations of FNO for nonlinear structural problems
  https://engrxiv.org/preprint/download/7702/12541/10834.
- **Reading**: no preemption found, but also no literature support. Per
  program.md §12.5, normalization is explicitly `s5_tuning`'s territory, so
  this is a stream seed, not a stream.

### T3 — the "never worse than baseline" guarantee, outside PDEs

- The guarantee concept exists and is named in **reinforcement learning**:
  "the goal of safe policy improvement is to find a new policy such that it is
  guaranteed to be no worse than the baseline"
  (https://media.nips.cc/nipsbooks/nipspapers/paper_files/nips29/reviews/1193.html).
- In supervised ensembling the guarantee is explicitly known NOT to hold:
  "averaging models together does not guarantee that the ensemble average will
  out-perform the best member" (Underspecification,
  https://arxiv.org/pdf/2011.03395); statistically-validated conservative
  blending is the practical substitute. Also: when-to-ensemble gating
  https://arxiv.org/pdf/2510.15346; conformal/guaranteed prediction sets for
  functional surrogates https://arxiv.org/html/2501.18426v2.
- **Reading**: the never-worse-than-baseline *framing* is borrowed from safe
  policy improvement, and its transplant to multi-fidelity field prediction —
  where the baseline is copy-LF and copy-LF is also the scored reference — has
  no hit in any of the five framings I ran.

---

## MANDATORY: candidate mechanism-class verdicts

Every citation below appears with a URL in iterations 1-5 of this loop and was
either FETCHED or recorded as a search-returned hit (marked). Nothing here is
from model recall (program.md §13.3).

### C1 — Guaranteed-fallback, trust-gated MF fusion

*Mechanism*: predict `y_hat = LF_up + g ⊙ Δ_theta(LF, X)` with `g ∈ [0,1]` a
learned per-pixel and/or per-band trust gate, initialized at `g ≡ 0` so
copy-LF is exactly recovered; gate driven by physics-agnostic confidence
(local LF features, ensemble/MC-dropout disagreement, distance to training
support in an LF-field embedding). Physics-agnostic at test time (ADR 0009 OK).

- **Published-evidence strength at small N_hf**: MODERATE-INDIRECT. The
  trust-weighting *principle* is validated in **MAST**
  (https://arxiv.org/html/2602.20974, FETCHED) at ~5D HF-equivalent budgets
  (~115 HF samples for 23D DrivAerNet) — but as a **GP for scalar QoI**, with
  "no field-prediction or multioutput capability", and with **no guarantee**
  (worst-case ~2.04x HF-only, "a practical bound, not a theoretical
  guarantee"). Additive prior+correction at low HF count is well-validated
  (https://arxiv.org/html/2606.03469, FETCHED: hyperelasticity rel-L2
  3.75±0.20 corrected vs 25.50±0.09).
- **Novelty-for-MF-fusion verdict**: **preempted-but-MF-composition-open.**
  Preempted parts: per-pixel learned gating / confidence-map blending in CV
  (https://www.emergentmind.com/topics/learnable-skip-and-gate-fusion, hit);
  distance-based trust weighting for MF (MAST, fetched); additive
  prior-plus-correction operator learning (2606.03469, fetched — which
  explicitly has **no gating and no trust weighting**, and whose prior is a
  physics model excluded by ADR 0009). What remains open, and was not found in
  five framings: a **field-valued, per-pixel/per-band trust gate over the
  interpolated LF field inside a neural operator, parameterized so the scored
  copy-LF reference is exactly recoverable and is the initialization.**
  Unresolved threat: **AGMF-Net**
  (https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X) —
  WebFetch 403; snippet says MoE gating over three expert subnetworks for
  Bayesian-optimization hydrofoil design (scalar objective). A builder must
  re-check it before any novelty claim.
- **Stream-worthiness**: **STREAM.** This is the top recommendation. It is the
  only candidate that attacks round success criterion 2 (skill < 1 on the five
  beyond-copy datasets) *by construction* rather than by hoping a better
  architecture emerges, and it is the natural consumer of s2-B1's finding that
  the champion is LF-blind. Honest caveat the operator must rule on: an
  identity-initialized gate makes `skill <= 1` reachable at initialization, so
  the card must be framed as a **measurement of what the learned correction
  adds over copy-LF** (gate magnitude / per-band gate profile is the readout),
  with an explicit statement that a trivially-zero gate is a *finding*, not a
  win. Overlap check: `s4_hybrid_routing` owns "per-band/per-region gating"
  but between **learned operator experts**, to capture the FNO<->Transolver
  oracle; C1 gates between the **raw LF input** and a correction. Distinct
  question, but the operator should decide explicitly.

### C2 — LF-field-keyed retrieval / exemplar residual transfer

*Mechanism*: build a bank from the training split mapping an LF-field
embedding (global or per-patch) to its `HF - LF` residual; at test time
retrieve k neighbors by LF-field similarity and blend their residuals onto
copy-LF under a confidence weight. Training-free or lightly trained.

- **Published-evidence strength at small N_hf**: STRONG in the image domain,
  ZERO in PDE/operator learning. **RASR**
  (https://arxiv.org/pdf/2508.09449, FETCHED) maintains an HQ/LR reference
  bank, queries with the LR input, and beats non-retrieval baselines — but is
  "image-domain only" per the fetch. Classical exemplar/dictionary SR and
  RefSR are dense (CrossNet https://arxiv.org/pdf/1807.10547; retrieval-
  compensated group-sparse SR https://dl.acm.org/doi/10.1109/TMM.2016.2614427
  — hits). In-repo, `docs/reports/MF_Sharp_HighFreq_Report.md` §3.6 already
  proposes the VQ-codebook transplant (CodeFormer) — an independent arrival at
  the same idea, not prior art against it.
- **Novelty-for-MF-fusion verdict**: **preempted-but-MF-composition-open.**
  Two independent refutation framings (iteration 1 T1, iteration 4 T2) found
  no retrieval-augmented neural operator; the nearest PDE relatives are
  memory-over-own-rollout (ICLR 2025 memory buffers, hit) and self-conditioning
  on the PDE residual field (**Error-Conditioned Neural Solvers**
  https://arxiv.org/pdf/2606.27354, hit — physics-coupled, ADR-0009-excluded).
  Open: a retrieval bank **keyed on the LF field** returning fidelity
  residuals, composed on top of copy-LF.
- **Stream-worthiness**: **BATCH-2 CANDIDATE INSIDE THE SAME NEW STREAM AS
  C1** (they share machinery: a non-parametric source blended under a
  confidence weight). Not strong enough alone for its own stream. Sober
  caveat from our own data: knn in **X** was still 4.0-29.7x worse than
  copy-LF on 5/5 datasets — retrieval only becomes interesting when keyed on
  the LF field and applied to the *residual*, never as a replacement predictor.

### C3 — Cross-dataset / foundation-style pretraining (the deferred `s8_data`)

- **Published-evidence strength at small N_hf**: STRONG, and that is the
  problem. **Multi-difficulty pre-generation**
  (https://arxiv.org/html/2512.00564v1, FETCHED): 10% hard + 90% easy/medium
  recovers ~96% of hard-only performance at 8.9x less generation compute,
  across CNO/FFNO/three Poseidon scales, 800 training samples. **MOFS**
  (https://arxiv.org/abs/2508.01211, FETCHED) does masked-field + spectrum
  self-supervised FNO pretraining. Plus PDEformer-2
  (https://arxiv.org/pdf/2507.15409), DPOT (https://arxiv.org/pdf/2403.03542),
  Multiphysics Pretraining
  (https://ml4physicalsciences.github.io/2025/files/NeurIPS_ML4PS_2025_157.pdf),
  lower-dimensional pretraining (https://arxiv.org/pdf/2407.17616),
  unsupervised-pretraining data-efficient operator learning
  (https://proceedings.neurips.cc/paper_files/paper/2024/file/0bac492172db3311c7e116098cfcf521-Paper-Conference.pdf)
  — all hits.
- **Novelty-for-MF-fusion verdict**: **preempted (cite: 2512.00564,
  2508.01211, 2403.03542, 2507.15409).** Additionally preempted *inside this
  repo*: the certified champion `mf_fno_transfer_film` already IS an
  LF-pretrain -> HF-finetune transfer model. And the literature's own caveat
  cuts against us: transfer helps when the target resembles the pretraining
  distribution, and our 6 panel datasets are mutually unrelated PDE families.
- **Stream-worthiness**: **NOT WORTH A STREAM.** Two transplantable pieces
  survive as **batch-2 seeds**: (i) self-supervised auxiliary tasks on the
  abundant LF corpus (masked-field reconstruction + spectrum prediction) ->
  `s5_tuning` as a recipe knob; (ii) the whole idea is only genuinely
  few-shot on `ifc_poisson` (N_hf=5) -> `s1_poisson` batch 2. **Operator
  fairness ruling needed**: pretraining on the 35+ non-panel dataset dirs
  under `factory_mffp/data/` is arguably permitted (immutable 1 forbids extra
  HF samples *for the panel dataset*, and "training procedure" is on the
  CAN-change list) but it changes the comparison basis for every other card.
  Do not let a card decide this silently.

### C4 — Meta-learning / in-context operator learning (ICON-style)

- **Published-evidence strength**: STRONG and crowded. MOFS
  (https://arxiv.org/abs/2508.01211, FETCHED, ICLR 2026 submission
  https://openreview.net/forum?id=x46qJUo38Q); Graph In-Context Operator
  Networks (https://arxiv.org/pdf/2603.12725, hit); ICON on 1-D conservation
  laws (https://arxiv.org/pdf/2401.07364, hit); VICON (in-repo report only,
  not re-fetched here).
- **Novelty-for-MF-fusion verdict**: **preempted (cite: 2508.01211,
  2603.12725, 2401.07364)** — and, more damaging, **aimed at a different
  problem**: every one of these targets generalization to *unseen PDE
  families*, whereas our 6 panel datasets are each trained separately. MOFS's
  fetched abstract has no LF/HF notion at all.
- **Stream-worthiness**: **NOT WORTH IT.** Also budget-hostile: transformer
  in-context training against a 200-epoch smoke tier. The one salvageable
  fragment is MOFS's self-supervised pretraining tasks, already routed to C3's
  s5 seed.

### C5 — Boosting / cascaded residual ensembles of operators

- **Evidence**: **Operator Boosting** (https://arxiv.org/pdf/2606.17460,
  FETCHED): sequential residual boosting, each small operator corrects the
  previous one's residual, Pareto-better than one big FNO/DeepONet — and
  explicitly "residual boosting of PDE surrogates **rather than
  multi-fidelity data**". Multi-Fidelity Flow Matching cascaded refinement
  (https://arxiv.org/pdf/2605.16118, hit). IRNO
  (https://arxiv.org/html/2605.24041) already anchored the retired
  `s3_testtime`.
- **Verdict**: **preempted (cite: 2606.17460)**.
- **Stream-worthiness**: **NOT WORTH A STREAM**; a cheap batch-2 seed for
  `s4_hybrid_routing` (a boosting cascade is a composition of operators, which
  is that stream's question).

### C6 — Per-sample amplitude / scale calibration head

- **Evidence**: none operator-specific found (T2 above); rho-norm scaling
  calibration (https://arxiv.org/html/2412.15301, hit) is classifier
  confidence, not field amplitude. In-round evidence is strong though:
  helmholtz amplitude_share_of_error 0.865 (champion), alpha_mean 0.075-0.108
  with alpha_std 0.59-0.88; cahn_hilliard/pfc alpha_mean 0.73-0.78.
- **Verdict**: **novel (no near neighbor found)**, but thin — absence of
  literature here reads as "nobody thinks it is a research question", not as
  an opportunity.
- **Stream-worthiness**: **BATCH-2 SEED for `s5_tuning`** (program.md §12.5
  names normalization as its territory) and secondarily `s7_loss`
  (a scale-invariant training objective). Single-dataset-dominant, so it
  cannot carry a stream.

### C7 — "Training-free baselines beat trained surrogates" (methodological)

- **Evidence**: Optimal Linear Baseline Models
  (https://arxiv.org/html/2508.05831, FETCHED) — "nonlinearity in the system
  does not guarantee that nonlinear neural network models outperform linear
  ones"; cross-domain analogue in Nature Methods
  (https://www.nature.com/articles/s41592-025-02772-6, hit); NO benchmarking
  critiques (https://www.ijcai.org/proceedings/2025/0640.pdf,
  https://arxiv.org/abs/2510.05995, hits).
- **Verdict**: not a mechanism. **NOT A STREAM** — but it is external
  corroboration that s2-B1's knn10-beats-champion result is a real,
  literature-recognized signature and should be reported as such.

### C0 — (precondition, not a candidate) Make the model consume LF at test time

Not a literature mechanism, so no prior-art verdict applies — but it gates C1
and C2 entirely. s2-B1 M1 measured `lf_at_inference = false` on 5/5 datasets x
3/3 seeds for the certified champion. Route: **batch-2 seed for
`s2_beyond_copy`** (audit which of the 45 zoo families actually ingest a
field-shaped LF tensor at eval, and re-score the top LF-ingesting family),
because that stream owns the "why does fusion lose to copy-LF" question and
this is the direct continuation of its own diagnostic.

## Interpretation

One stream-worthy gap (C1, with C2 as its batch 2), four preempted classes
(C3, C4, C5, and C7-as-non-mechanism), one stream seed (C6), and one
precondition audit (C0). The gap is not an architecture the field has missed —
it is a **fusion-rule guarantee** the field has not asked for, because in most
MF applications the LF baseline is not also the scored reference. In this
benchmark it is, which is exactly why the gap exists here and not there.
