# Iteration 1 — is the oracle-vs-predicted-intermediate ablation a named practice?

## Search rationale

The batch-3 slot is fixed (emulator-ceiling card). Its instrument is: run one FROZEN downstream stage twice, once on the real (oracle) intermediate and once on the upstream model's predicted intermediate, and read the gap. Before anything else I need to know whether that instrument has a name and a home literature — because if it does, the card cannot claim the instrument, only the MF composition. Three terms: (1) the ablation itself, (2) the MF/surrogate-side error decomposition, (3) the closest ML analogue (teacher forcing vs free running).

## Search terms used

1. `oracle intermediate representation ablation frozen downstream module pipeline error attribution predicted vs ground-truth input`
2. `error decomposition emulator error versus downstream estimator error two-stage surrogate chained model propagation`
3. `teacher forcing versus free running gap analysis exposure bias non-autoregressive two-stage model predicted input distribution shift`

## Findings

### Term 1 — oracle vs predicted intermediate (STRONGEST HIT OF THE LOOP)

Search returned, among others: <https://arxiv.org/html/2604.12440> (IAD-Unify), <https://arxiv.org/pdf/2606.07718> (agents on a neuroscience data-to-discovery pipeline), <https://arxiv.org/html/2601.19337> (SETA, statistical fault attribution for compound AI systems), <https://arxiv.org/pdf/2502.08504> (MoDitector, module-directed testing for autonomous driving), <https://arxiv.org/html/2606.09071> (REFLECT).

**Fetched — IAD-Unify, arXiv:2604.12440v1 [cs.CV] 14 Apr 2026** (<https://arxiv.org/html/2604.12440>, full HTML body retrieved, 52,899 chars). This paper runs *exactly* our instrument, under an explicit name and with an explicit interpretation:

- *"Understanding is evaluated under both **oracle (ground-truth mask)** and **predicted (region-expert proposal)** settings; **the oracle–predicted gap directly quantifies deployment readiness**."*
- The upstream stage is FROZEN, like ours: *"Both converge in the unified stage (purple) with **the region expert frozen**"*; *"At inference time, the primary protocol is predicted-region understanding: the model uses proposal masks from E_seg rather than ground-truth masks, **reflecting realistic deployment conditions**."*
- A single trained model is run under four inference modes with no retraining — `Oracle 96.34 / Predicted 93.28 / Full image as region 24.63 / No region 16.71` (location accuracy) — i.e. an **oracle → predicted → degraded-input ladder**, structurally identical to the real-LF → pseudo-LF → no-LF ladder the card wants.
- And, directly on our component (b): *"**Training exclusively with ground-truth masks reaches high accuracy under oracle evaluation but collapses under predicted masks, revealing overfitting to inputs unavailable at deployment.** Gradually transitioning from ground-truth to predicted masks during training partially mitigates this but underperforms on both settings."* Their table: `GT mask only 96.82 oracle / 41.35 predicted`; `GT→predicted transition 95.47 / 87.42`; `Stage-wise 96.08 / 91.56`; `joint 96.34 / 93.28`.

**Fetched — arXiv:2606.07718** (<https://arxiv.org/pdf/2606.07718>, PDF text extracted with pypdf, 222,009 chars): *"To better understand how end-to-end failure is distributed across stages, we ran **oracle ablation experiments injecting ground truth inputs** at two points in the agent-produced E2E Maximal pipelines (Table 2)."* Table 2 caption: *"End-to-end oracle ablation experiments. Rows compare single-stage performance, E2E Maximal trial performance, and two oracle ablations: **injecting gold Body Tracking inputs** and **injecting gold inputs at all stages upstream**."* Note the framing: single-stage performance is measured independently *"and thus reflect genuine difficulty in the composed setting, rather than error"* propagation alone.

Snippet-only (recorded, not carrying a verdict): SETA <https://arxiv.org/html/2601.19337> — end-to-end testing "is unable to perform credit attribution to internal components"; MoDitector <https://arxiv.org/pdf/2502.08504> — module-specific oracles by "substituting module outputs with perfect outputs".

### Term 2 — MF / surrogate-side error decomposition

Results: <https://arxiv.org/abs/1701.03240> (Error modeling for surrogates of dynamical systems using ML), Stanford SUETRI-B ROM error-estimation theses, <https://arxiv.org/pdf/2103.11766> (Fixes That Fail: self-defeating improvements in ML systems), tandem-queue decomposition error. The engine's own summary conceded the gap: *"For more specific information about how emulator errors propagate through downstream estimators in two-stage surrogate models, you might want to search for more specialized literature."* **No usable MF-specific result**; the retrieved surrogate-error work models the error of a single surrogate, not the split between an upstream emulator and a frozen downstream estimator. Not fetched (deferred to iteration 2, where I search the MF corpus by its own vocabulary).

### Term 3 — teacher forcing vs free running

Results: <https://www.emergentmind.com/topics/exposure-bias>, <https://arxiv.org/pdf/2210.08959> (Flipped Classroom: effective teaching for time-series forecasting), <https://arxiv.org/pdf/2106.15561> (survey on neural speech synthesis), <https://link.springer.com/article/10.1007/s00521-025-11162-0> (exposure bias in LLM distillation). Snippet-level definition consistently: exposure bias = *"the discrepancy between teacher-forced training and free-running inference"*, mitigated by scheduled sampling. All snippet-only at this point; the corpus is overwhelmingly **autoregressive/sequential**, where the mechanism is *accumulation* over steps — our stack is single-shot with one intermediate, so the accumulation mechanism does not transfer even though the train/deploy input mismatch does. Fetch deferred to iteration 3 (need a source that analyses the gap itself, not a mitigation).

## Interpretation

The oracle-vs-predicted-intermediate ladder on a frozen downstream stage is **not novel as an instrument** — it is named ("oracle ablation", "oracle–predicted gap") and is standard practice in compound-AI/pipeline evaluation, with 2604.12440 supplying both the ladder and the *"overfitting to inputs unavailable at deployment"* reading of our component (b). What is still unretrieved is the same instrument inside the multi-fidelity surrogate literature, and any use of the gap as a *decision rule* about whether to keep the intermediate at all — that is what iterations 2–3 must attack.
