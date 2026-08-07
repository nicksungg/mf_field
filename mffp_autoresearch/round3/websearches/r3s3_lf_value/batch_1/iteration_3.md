# Iteration 3 — r3s3_lf_value, batch 1 (refutation pass, part 1)

## Search rationale

Field context is now sufficient (turn 2 `ENOUGH`: the rate-vs-information frame is
pinned to a fetched primary source and two composition-specific queries came back
empty). Remaining iterations go to §3.3 — trying to **refute** the novelty of the
directions r3s3-B1 is likely to propose. From program.md §4 (`r3s3_lf_value`: "what is
LF-at-train worth on the honest panel ... matched with/without arms at matched
procedure"), ADR r3-0001 (completeness certificates), and r2s3-B4 part 7 (identifiability
vs trainability on cahn_hilliard), the candidate directions are:

- **D1** — re-measure the matched, budget-matched +/-LF contrast on the
  **completeness-certified** panel: does LF-at-train still pay once the condition
  vector provably determines the HF field? (success criterion 2: >= 3 datasets)
- **D2** — decide **identifiability vs trainability** on cahn_hilliard (19-D complete
  condition, N_hf = 5 draws): arms in which LF can only act as an optimisation aid
  (LF-pretrain -> HF-finetune / warm start / curriculum) vs arms where LF supplies
  supervision at conditions with no HF row.
- **D3** — distil an LF-consuming teacher into a condition-only student (LF strictly a
  training-time privileged signal, absent at test).

This turn refutes D3 and the D2 "warm start" leg.

## Search terms used

1. `coarse mesh simulation as privileged information distillation parameter-to-field surrogate low-fidelity teacher not available at inference`
2. `low-fidelity pretraining benefit ablation warm start versus additional supervision optimization curriculum coarse-to-fine PDE surrogate few high-fidelity samples`
3. `"low-fidelity" data used only during training surrogate takes only parameters at inference matched ablation with and without low-fidelity arms`

## Findings

### Term 1 — privileged-information distillation, and when it stops working

- **Yang, Sanghavi, Rahmanian, Bakus & Vishwanathan, "Toward Understanding Privileged
  Features Distillation in Learning-to-Rank", NeurIPS 2022** — **fetched (PDF body
  extracted)**
  https://proceedings.neurips.cc/paper_files/paper/2022/file/aa31dc84098add7dd2ffdd20646f2043-Paper-Conference.pdf
  Verbatim (extraction loses whitespace):
  > "We show that PFD outperforms several baselines (no-distillation,
  > **pretraining-finetuning**, self-distillation, and generalized distillation) on all
  > these datasets. Next, we analyze **why and when** PFD performs well via both
  > empirical ablation studies and theoretical analysis for linear models. Both
  > investigations uncover an interesting **non-monotone behavior**: as the predictive
  > power of a privileged feature increases, the performance of the resulting student
  > model initially increases but then **decreases** ... a very predictive privileged
  > teacher produces predictions with high variance, which lead to high variance student
  > estimates and inferior testing performance."
  Their generative model is `y = x·w* + u·v* + eps` with `u` the privileged feature —
  i.e. the privileged signal carries information about `y` that is **not in x**.
  **This is precisely the assumption round 3's panel breaks**: with a completeness
  certificate, `y` is a deterministic function of the condition `x`, so there is no
  `u·v*` term for LF to supply, and the only surviving channels are variance reduction
  / rate / optimisation. The paper is nonetheless a direct preemptor of "distil an
  LF-consuming teacher into a deployment-input-only student" as a *mechanism*, and it
  already benchmarks that mechanism against pretrain-finetune.
- Search returns, not fetched: https://arxiv.org/abs/2602.04942 (Privileged Information
  Distillation for Language Models — "transferring capabilities learned with PI to
  policies that must act without it at inference time remains a fundamental
  challenge"); https://www.sciencedirect.com/science/article/pii/S0950705125003855 and
  https://bird.bcamath.org/bitstream/20.500.11824/2025/1/TPD.pdf (Teacher privileged
  distillation: how to deal with imperfect teachers?);
  https://emilianopp.github.io/Privileged-Information-Distillation-and-Self-Distillation/;
  https://www.researchgate.net/publication/301362871_Learning_using_privileged_information_Similarity_control_and_knowledge_transfer
  (Vapnik & Izmailov canon; also cited by round-2 batch 1).
  No retrieved work makes the privileged signal a **coarse consistent PDE solve on a
  nested ladder** for a **condition-vector-only field student**.

### Term 2 — is LF-pretraining a warm start or extra supervision?

- Search returns, none fetched: https://arxiv.org/html/2601.03086 (Pretrain Finite
  Element Method — a PINO produces low-fidelity solutions, then classical solvers are
  warm-started from the neural prediction; note this puts the network *inside the
  solve*, which round 3 bans at test); https://arxiv.org/abs/2111.05841 +
  https://www.nature.com/articles/s42256-023-00761-y (PEDS: a coarse "low-fidelity,
  explainable physics simulator" is **embedded in the surrogate** and trained end to
  end — LF inside the test path, so not our regime); https://arxiv.org/pdf/2304.04862
  (few-shot graph-Laplacian correction of low-fidelity data);
  https://arxiv.org/pdf/2410.12241 (transfer learning for NN surrogates).
- **No usable result** for an experiment that *separates* the warm-start/optimisation
  contribution of LF pretraining from its supervision contribution at matched budget.

### Term 3 — LF strictly train-only, parameters-only at inference, matched arms

- Search returns, fetch of the closest hit **blocked (HTTP 403 on ScienceDirect)**:
  https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 ("Learning
  from more to predict with less: **Representation-level multimodal distillation to
  address training-inference data asymmetry in surrogate modeling**", EAAI — auxiliary
  modalities treated as privileged information, latent structure distilled into a
  student "requiring only deployment-feasible inputs at inference"). This is the same
  work round-2 batch 1 flagged as the nearest neighbour for D1-style distillation; it
  remains **unfetchable** here, so it is carried as a *search-returned* pointer, not a
  fetched citation.
  Other returns: https://arxiv.org/html/2403.08901 (credible NN surrogate discovery
  under uncertainty; ablations that "change lower-fidelity model structures");
  https://arxiv.org/html/2402.18846v1 (Multi-Fidelity Residual Neural Processes);
  https://arxiv.org/pdf/1707.03916 (large-scale variable-fidelity surrogate modelling).
- **No usable result** for a matched +/-LF contrast where LF is *absent from the test
  path by construction* and the score is denominated by the cost of just running the
  coarse solver.

## Interpretation

D3's mechanism (privileged/teacher distillation into a deployment-input-only student)
is **published and studied**, including its failure mode, so it can only ship as a
cited baseline. The genuinely un-retrieved things are (i) the composition — coarse
consistent PDE solves as the privileged signal for a condition-only field student — and
(ii) the regime question: what privileged data is worth when the observed input is
**certified sufficient**, which is the exact assumption Yang et al.'s model violates.
Turn 4 must attack that second point directly, because it is the only place r3s3 can
claim anything.
