# Websearch Report — SCOUTING gap-mine for an 8th stream (2026-07-29)

**Stream**: `_scouting` (not tied to a stream) / **Batch**: n/a
**Total iterations**: 5 (CAP HIT) / **WebSearch calls**: 15 /
**WebFetch calls**: 11 (2 failed: arXiv 2304.06972 size limit; ScienceDirect
AGMF-Net HTTP 403) / **Cap hit**: YES (5/5)

Files: `summary_so_far.md`, `iteration_1.md` .. `iteration_5.md`, this report,
all under
`${ROUND_ROOT}/websearches/_scouting/2026-07-29_stream_gap_mining/`.

## Search trace

### Turn 1 — angles (a) cross-dataset pretraining, (c) retrieval, (d) in-context
Terms chosen to open the three highest-prior brief angles, (c) first because
the in-round `pfc` result (training-free knn10 beats the 200-epoch champion by
3.045 skill units, above the 1.151 floor) is direct evidence an instance-based
component carries signal the FNO does not.
- `retrieval-augmented neural operator ...` -> **no named method exists**;
  nearest is sequential residual boosting, explicitly not multi-fidelity
  [cite: https://arxiv.org/pdf/2606.17460].
- `in-context operator learning few-shot ...` -> MOFS: memory-augmented
  multimodal prompting, self-supervised FNO pretraining, **no LF/HF notion**
  [cite: https://arxiv.org/abs/2508.01211].
- `multi-fidelity ... cross-dataset pretraining ...` -> LF-pretrain ->
  HF-finetune is the textbook recipe; `negative transfer` is its named failure
  mode. -> `iteration_1.md`

### Turn 2 — angles (b) trust-region fusion, (e) recurring mechanisms
- `uncertainty-weighted multi-fidelity fusion trust region ...` -> **MAST**,
  spatial trust-weighting, but a **GP for scalar QoI** with no field capability
  and **no guarantee** (worst case ~2.04x HF-only)
  [cite: https://arxiv.org/html/2602.20974].
- `neural network fusion worse than low-fidelity baseline ...` -> correlation
  strength governs whether MF fusion beats single-fidelity; normalization
  matters [cite: https://arxiv.org/pdf/2512.02868]. No never-worse guarantee
  in the literature.
- `multi-fidelity neural operator 2026 survey ...` -> zero-shot
  super-resolution in learned operators is a **false promise**; aliasing is the
  mechanism [cite: https://arxiv.org/pdf/2510.06646]. -> `iteration_2.md`

### Turn 3 — the two live candidates vs their neighbouring literatures
- `learned confidence gate ... never worse ... super-resolution` -> per-pixel
  gating and interpolate-and-concatenate are CV-standard
  [cite: https://www.emergentmind.com/topics/learnable-skip-and-gate-fusion];
  the never-worse *guarantee* has no hit.
- `exemplar-based reference-guided super-resolution ...` -> RASR, retrieval
  bank + LR query, beats non-retrieval baselines, **image-domain only**
  [cite: https://arxiv.org/pdf/2508.09449].
- `delta learning residual correction of coarse solution ...` -> IRNO
  [cite: https://arxiv.org/html/2605.24041]; Deep Delta Learning
  [cite: https://huggingface.co/papers/2601.00417]; no identity-initialization
  guarantee found. -> `iteration_3.md`

### Turn 4 — refutation pass in MF / operator vocabulary
- `multi-fidelity neural operator learned gating ...` -> the standard
  composition is additive `G_theta(v) + G_psi(v, u_theta)`, **"without gating
  or trust weighting"**, **"no formal guarantee exists"**, and its prior is a
  physics model (ADR-0009-excluded)
  [cite: https://arxiv.org/html/2606.03469]. Unresolved paywalled threat:
  AGMF-Net [https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X,
  HTTP 403].
- `nearest-neighbor retrieval ... PDE surrogate ...` -> no hit; nearest is
  self-conditioning on the PDE residual field
  [cite: https://arxiv.org/pdf/2606.27354], physics-coupled.
- `pretraining neural operator on multiple unrelated PDE datasets ...` ->
  comprehensively preempted; multi-difficulty pre-generation gets ~96% of
  hard-only performance from 10% hard data at 8.9x less compute
  [cite: https://arxiv.org/html/2512.00564v1]. -> `iteration_4.md`

### Turn 5 — closing sweep + verdicts (CAP)
- `simple baselines outperform neural operators ...` -> "nonlinearity in the
  system does not guarantee that nonlinear neural network models outperform
  linear ones" [cite: https://arxiv.org/html/2508.05831].
- `per-sample amplitude scale calibration neural operator ...` -> no
  operator-specific method; nearest is classifier-probability rho-norm scaling
  [cite: https://arxiv.org/html/2412.15301].
- `"never worse" guarantee ... safe improvement ...` -> the framing exists in
  RL as **safe policy improvement**
  [cite: https://media.nips.cc/nipsbooks/nipspapers/paper_files/nips29/reviews/1193.html];
  in supervised ensembling it explicitly does not hold
  [cite: https://arxiv.org/pdf/2011.03395]. -> `iteration_5.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched unless noted) | What remains open / where it goes |
|---|---|---|---|
| **C1 Guaranteed-fallback, trust-gated MF fusion** — `y = LF_up + g ⊙ Δ(LF,X)`, `g∈[0,1]` per-pixel/per-band, `g≡0` at init reproduces copy-LF exactly | **preempted-but-MF-composition-open** | MAST https://arxiv.org/html/2602.20974 (GP, **scalar QoI**, no guarantee, ~2.04x worst case); physics-guided correction https://arxiv.org/html/2606.03469 (additive, **explicitly ungated**, **"no formal guarantee exists"**, physics prior); CV gating https://www.emergentmind.com/topics/learnable-skip-and-gate-fusion (hit); safe policy improvement https://media.nips.cc/nipsbooks/nipspapers/paper_files/nips29/reviews/1193.html (hit) | OPEN: a **field-valued per-pixel/per-band trust gate over the interpolated LF field inside a neural operator, parameterized so the scored copy-LF reference is exactly recoverable and is the initialization**. -> **NEW STREAM (rank 1)**. Unresolved threat to re-check: AGMF-Net (403) |
| **C2 LF-field-keyed retrieval / exemplar residual transfer** | **preempted-but-MF-composition-open** | RASR https://arxiv.org/pdf/2508.09449 (**image-domain only**); CrossNet https://arxiv.org/pdf/1807.10547 (hit); retrieval-compensated sparse SR https://dl.acm.org/doi/10.1109/TMM.2016.2614427 (hit); nearest PDE relative is residual-field self-conditioning https://arxiv.org/pdf/2606.27354 (hit) | OPEN: a bank **keyed on the LF field** returning `HF-LF` residuals, blended onto copy-LF under a confidence weight. No retrieval-augmented neural operator found in **two independent framings**. -> **batch 2 of the same new stream** |
| **C3 Cross-dataset / foundation pretraining (deferred `s8_data`)** | **preempted (cite)** | https://arxiv.org/html/2512.00564v1; https://arxiv.org/abs/2508.01211; https://arxiv.org/pdf/2403.03542 (hit); https://arxiv.org/pdf/2507.15409 (hit); NeurIPS 2024 unsupervised pretraining (hit) | Nothing open as a novelty claim; our champion is already LF-pretrain->HF-finetune. -> **batch-2 seed for `s5_tuning`** (SSL aux tasks on the LF corpus) and **`s1_poisson`** (the only true N_hf=5 setting). **Needs an operator fairness ruling** under immutable 1 |
| **C4 Meta-learning / in-context operator learning** | **preempted (cite)** | https://arxiv.org/abs/2508.01211; https://arxiv.org/pdf/2603.12725 (hit); https://arxiv.org/pdf/2401.07364 (hit) | Aimed at **unseen-PDE-family** generalization, not our per-dataset problem; budget-hostile. -> **not worth it** |
| **C5 Boosting / cascaded residual operator ensembles** | **preempted (cite)** | https://arxiv.org/pdf/2606.17460 ("residual boosting ... **rather than multi-fidelity data**"); https://arxiv.org/pdf/2605.16118 (hit); IRNO https://arxiv.org/html/2605.24041 | -> **batch-2 seed for `s4_hybrid_routing`** |
| **C6 Per-sample amplitude / scale calibration head** | **novel** (no near neighbor; nearest is classifier calibration https://arxiv.org/html/2412.15301, hit) | — | Thin: no literature support either. Single-dataset-dominant (helmholtz 86.5% amplitude). -> **batch-2 seed for `s5_tuning`** (normalization is §12.5 territory), secondarily `s7_loss` |
| **C7 "Training-free baselines beat trained surrogates"** | not a mechanism — external corroboration | https://arxiv.org/html/2508.05831; https://www.nature.com/articles/s41592-025-02772-6 (hit); https://www.ijcai.org/proceedings/2025/0640.pdf (hit) | -> **not a stream**; cite it when reporting the knn10 result |
| **C0 Make the model consume LF at test time** (precondition, not a literature mechanism) | n/a | in-round: `experiment_cards/s2_beyond_copy/batch_1/B1.json` M1 | -> **batch-2 seed for `s2_beyond_copy`**: audit which zoo families ingest a field-shaped LF tensor at eval. **Gates C1 and C2** |

## Citations summary

- MAST, "A Multi-fidelity Augmented Surrogate model via Spatial
  Trust-weighting" — https://arxiv.org/html/2602.20974 — FETCHED — iteration_2
- Villatoro, Geraci & Schiavazzi, "Assessing the performance of
  correlation-based multi-fidelity neural emulators" —
  https://arxiv.org/pdf/2512.02868 — FETCHED (partial) — iteration_2
- "The False Promise of Zero-Shot Super-Resolution in Machine-Learned
  Operators" — https://arxiv.org/pdf/2510.06646 — FETCHED — iteration_2
- "Physics-guided correction for operator learning under model
  misspecification" — https://arxiv.org/html/2606.03469 — FETCHED — iteration_4
- "Operator Boosting Produces Pareto-Efficient PDE Surrogates" —
  https://arxiv.org/pdf/2606.17460 — FETCHED — iteration_1
- Li & Zhe, "MOFS: Multi-Operator Few-Shot Learning for Generalization Across
  PDE Families" — https://arxiv.org/abs/2508.01211 (OpenReview
  https://openreview.net/forum?id=x46qJUo38Q) — FETCHED — iteration_1
- "RASR: Retrieval-Augmented Super Resolution for Practical Reference-based
  Image Restoration" — https://arxiv.org/pdf/2508.09449 — FETCHED — iteration_3
- "Pre-Generating Multi-Difficulty PDE Data for Few-Shot Neural PDE Solvers" —
  https://arxiv.org/html/2512.00564v1 — FETCHED — iteration_4
- "Optimal Linear Baseline Models for Scientific Machine Learning" —
  https://arxiv.org/html/2508.05831 — FETCHED — iteration_5
- IRNO, "Iterative Refinement Neural Operators are Learned Fixed-Point
  Solvers" — https://arxiv.org/html/2605.24041 — hit — iteration_3
- "Deep Delta Learning" — https://huggingface.co/papers/2601.00417 — hit —
  iteration_3
- "Error-Conditioned Neural Solvers" — https://arxiv.org/pdf/2606.27354 — hit
  — iteration_4
- "Learnable Skip-and-Gate Fusion" —
  https://www.emergentmind.com/topics/learnable-skip-and-gate-fusion — hit —
  iteration_3
- CrossNet — https://arxiv.org/pdf/1807.10547 — hit — iteration_3
- Retrieval-Compensated Group Structured Sparsity for Image SR —
  https://dl.acm.org/doi/10.1109/TMM.2016.2614427 — hit — iteration_3
- Graph In-Context Operator Networks — https://arxiv.org/pdf/2603.12725 — hit
  — iteration_1
- ICON on 1-D scalar conservation laws — https://arxiv.org/pdf/2401.07364 —
  hit — iteration_1
- PDEformer-2 — https://arxiv.org/pdf/2507.15409 — hit — iteration_4
- DPOT — https://arxiv.org/pdf/2403.03542 — hit — iteration_4
- Multiphysics Pretraining (NeurIPS ML4PS 2025) —
  https://ml4physicalsciences.github.io/2025/files/NeurIPS_ML4PS_2025_157.pdf
  — hit — iteration_4
- Data-Efficient Operator Learning via Unsupervised Pretraining (NeurIPS 2024)
  — https://proceedings.neurips.cc/paper_files/paper/2024/file/0bac492172db3311c7e116098cfcf521-Paper-Conference.pdf
  — hit — iteration_4
- Multi-Fidelity Flow Matching: Cascaded Refinement —
  https://arxiv.org/pdf/2605.16118 — hit — iteration_2
- Multifidelity DeepONets (Phys. Rev. Research) —
  https://link.aps.org/doi/10.1103/PhysRevResearch.4.023210 — hit — iteration_4
- AGMF-Net (ensemble adaptive gated multi-fidelity NN) —
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X —
  **FETCH FAILED (HTTP 403)** — iteration_4 — recorded as an unresolved threat
- MF-FNO transfer learning for flow/temperature —
  https://arxiv.org/pdf/2304.06972 — **FETCH FAILED (size limit)** —
  iteration_1 — search-hit only, no content claim
- Parametric rho-Norm Scaling Calibration — https://arxiv.org/html/2412.15301
  — hit — iteration_5
- Underspecification Presents Challenges for Credibility —
  https://arxiv.org/pdf/2011.03395 — hit — iteration_5
- Safe policy improvement (NeurIPS 29 review page) —
  https://media.nips.cc/nipsbooks/nipspapers/paper_files/nips29/reviews/1193.html
  — hit — iteration_5
- "Deep-learning-based gene perturbation effect prediction does not yet
  outperform simple linear baselines" —
  https://www.nature.com/articles/s41592-025-02772-6 — hit — iteration_5
- CFDONEval — https://www.ijcai.org/proceedings/2025/0640.pdf — hit —
  iteration_5

## Dead ends

- `retrieval-augmented neural operator PDE nearest-neighbor prior 2025` -> the
  named method does not exist; returned IR/vector-search papers. Useful as a
  negative result, useless as literature support.
- `per-sample amplitude scale calibration neural operator ...` -> the word
  "calibration" collapses to classifier-confidence calibration in every hit.
- `"never worse" guarantee ensemble ... surrogate` -> collapses to LLM
  ensembling and conformal prediction; the concept lives in RL under a
  different name (safe policy improvement).
- ScienceDirect AGMF-Net -> HTTP 403; must be checked by a human or via an
  institutional route before C1's novelty claim is final.
- arXiv 2304.06972 PDF -> exceeds the fetch size limit; use the abs page next
  time.

## For the brainstormer / operator

The brainstormer MUST quote the prior-art verdict for whatever it proposes.

1. **Recommend ONE 8th stream, not several.** Proposed question: *"can
   multi-fidelity fusion be constructed so it cannot lose to its own LF input,
   and does the learned correction then add anything?"* Batch 1 = **C1**
   (identity-initialized per-pixel/per-band trust gate over copy-LF, verdict
   **preempted-but-MF-composition-open**); batch 2 = **C2** (LF-field-keyed
   retrieval residual bank, same verdict). This is the only gap where the
   literature's silence is *structural*: in most MF applications the LF
   baseline is not also the scored reference, so nobody needed a never-worse
   fusion rule. In this benchmark it is the reference — that is why the gap
   exists here and not there.
2. **Pre-register the gaming risk.** An identity-initialized gate makes
   `skill <= 1` reachable at initialization. The card must be framed as a
   measurement — the trained gate's magnitude and per-band profile ARE the
   readout of how much learned fusion adds over copy-LF — and must state that
   a gate collapsing to zero is a *finding*, not a win. Falsification must be
   stated on the *correction's* contribution, not on the raw skill.
3. **C0 gates everything.** s2-B1 measured `lf_at_inference = false` on 5/5
   datasets x 3/3 seeds for the certified champion: it consumes only the
   `[batch, cond_dim]` vector. Any C1/C2 card must first verify its base family
   actually ingests a field-shaped LF tensor at eval, or it will silently
   inherit the same defect. Route the audit itself to `s2_beyond_copy` batch 2.
4. **Do not open `s8_data`.** C3 is **preempted** by five fetched/hit sources
   and by our own champion's architecture, and the literature's own caveat
   (transfer helps when target resembles pretraining) cuts against a panel of
   6 unrelated PDE families. Route its two salvageable fragments to `s5_tuning`
   (SSL aux tasks on the LF corpus) and `s1_poisson` (the only real N_hf=5
   setting). **Operator ruling required** before any card pretrains on
   non-panel datasets — it changes the comparison basis for every other card.
5. **Correct the brief's sample-count premise.** `n_train_hf = 400` on all five
   beyond-copy panel datasets (s2-B1 part 5); only `ifc_poisson` is N_hf=5.
   Candidates were assessed under both regimes; retrieval banks and in-context
   prompting are feasible on 5/6 panel datasets precisely because of this.
6. **Reject C4 (in-context) and C5 (boosting) as streams**, both
   **preempted (cite)**; C5 is a cheap batch-2 seed for `s4_hybrid_routing`,
   C6 (amplitude calibration, verdict **novel** but thin) is a batch-2 seed for
   `s5_tuning`.
7. **When reporting the knn10 result, cite C7's corroboration**
   (https://arxiv.org/html/2508.05831): "nonlinearity in the system does not
   guarantee that nonlinear neural network models outperform linear ones" —
   the training-free-baseline-wins signature is literature-recognized, not an
   artefact of our harness.
