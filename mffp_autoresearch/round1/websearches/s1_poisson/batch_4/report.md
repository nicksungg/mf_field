# Websearch Report — Stream `s1_poisson`, Batch 4

**Stream**: s1_poisson (gap) · **Batch**: 4 (narrow disambiguation slot) ·
**Total iterations**: 4 · **WebSearch calls**: 12 (3 + 3 + 3 + 3, cap-respecting) ·
**WebFetch calls**: 12 attempted / **11 returned content**, of which **10 usable**
(1 hard failure: `arxiv.org/html/2405.19101v3` HTTP 404; 1 informative negative:
`arxiv.org/abs/2512.04863` contained no "fixed optimization budget" statement —
the search summariser had invented it) ·
**Cap hit**: NO (stopped at 4 of 5 — see iteration_4 "Interpretation")

**Headline**: this batch is measurement hygiene, and the literature confirms it.
Directions 1-3 are cleanly preempted, with an unusually good citation for the
step-count confound (a 2026 paper that states "this comparison conflates
algorithmic quality with compute: GRPO performs 8x more gradient updates per
epoch" and then runs *both* of the matched controls B4 plans). Direction 4 —
the nested-ladder all-pairs degeneracy — **survived three independent
refutation attempts and appears to be unreported**, and iteration 3 found the
structural reason first-hand in POSEIDON, the very paper the `allpairs` family
cites as its inspiration.

## Search trace

### Turn 1 — directions 1 & 3: duplication-as-reweighting, dedup effects
Terms: `exact duplicate training examples equivalent to loss reweighting SGD
importance weighting duplication`; `deduplicating training data language models
duplicates memorization effect on training distribution weighting`;
`"importance duplication" weighted empirical risk duplicating data points
approximation weights`. Chosen to get the *formal* statement first, the
empirical dedup literature second, and the term of art third.
- The construction is published and **named "importance duplication"**:
  "We can obtain an approximation to this method by including ⌈1/M(x_i)⌉
  duplicates of data point x_i in our training set", with named caveats
  (discretization error; U-statistic bias when duplicates co-occur in a
  minibatch) [cite: https://ar5iv.labs.arxiv.org/html/1806.02512 (fetched)]
  → iteration_1.md
- Dedup changes required train steps: deduplicated models "require fewer train
  steps to achieve the same or better accuracy"
  [cite: https://arxiv.org/abs/2107.06499 (fetched)]; SoftDedup separates the
  two operations — "Hard deduplication identifies and removes duplicate
  samples. Soft deduplication ... decreas[es] their sampling weight during
  training" — and reports "a reduction of 26% to 39% in the number of required
  training steps" [cite: https://arxiv.org/html/2407.06654 (fetched)]
  → iteration_1.md
- Engine negative: **no source states duplication == loss weighting as an exact
  identity**; the published claim is an approximation with caveats
  → iteration_1.md

### Turn 2 — direction 2: step-count vs epoch-count confound
Terms: `compute-matched versus epoch-matched comparison confound number of
gradient steps data selection ablation fair comparison`; `data pruning subset
selection baseline must control for number of training steps equal iterations
not equal epochs`; `neural operator training ablation matched number of
optimization steps rather than epochs when dataset size differs`.
- **The best citation of the batch**: "However, this comparison conflates
  algorithmic quality with compute: GRPO performs 8x more gradient updates per
  epoch than REINFORCE and POMO", with both matched controls constructed —
  train the short arms for 800 epochs to match 312K updates, AND read the long
  arm off at epoch 12 to match 39K [cite: https://arxiv.org/html/2606.10321v1
  (fetched); abstract corroboration at https://arxiv.org/abs/2606.10321
  (fetched)] → iteration_2.md
- Data-pruning literature makes the same point but only as search-return; no
  quotable fetched sentence (all top hits on dead routes) → iteration_2.md
- **No usable results** for a scientific-ML/neural-operator statement of the
  step-matching rule; PENCO's claimed "fixed optimization budget" safeguard did
  not exist in the fetched page [https://arxiv.org/abs/2512.04863 (fetched,
  negative)] → iteration_2.md

### Turn 3 — direction 4: is the nested-ladder degeneracy reported?
Terms: `POSEIDON foundation model PDE all2all training strategy time pairs data
amplification trajectory`; `multi-fidelity training all pairs of fidelity levels
nested aligned samples duplicate targets redundant cross-level supervision`;
`all-pairs fidelity augmentation degenerate identical inputs low and high
fidelity same parameters duplicate training rows operator learning`.
Grounded first in `mf_field/akash/models/mf_fno_allpairs/manifest.json` (read
directly), which declares `"inspired_by": ["herde2024poseidon", ...]` and
"POSEIDON all2all recast onto a fidelity ladder ... amplifies the data O(L^2)".
- POSEIDON's amplification rests on the **semi-group property**, with the input
  being "any initial condition" at t_k and the target the solution at t_kbar,
  yielding "quadratic O(K^2) samples per trajectory, when compared to the
  linear K samples" [cite: https://ar5iv.labs.arxiv.org/html/2405.19101
  (fetched)] — i.e. the input VARIES with the source index. The fidelity recast
  with `cond_from = target` has a source-invariant input, so the premise is
  absent. → iteration_3.md
- MF literature's concern about aligned data is **flexibility, not degeneracy**:
  "removing the requirement for low-fidelity and high-fidelity datasets to share
  identical function inputs or spatio-temporal query points"
  [cite: https://arxiv.org/html/2503.17941v1 (fetched)] → iteration_3.md
- **No usable results** for the degeneracy claim itself → iteration_3.md

### Turn 4 — targeted refutation of the three B4 candidate directions
Terms: `multi-fidelity neural network per-level loss weighting weight high
fidelity samples more few high-fidelity data upweighting`; `reported gain
attributed to confound rather than proposed mechanism revisiting ablation deep
learning attribution of improvement`; `fidelity embedding single network trained
on all fidelity levels same design points effective sample size replication
nested experimental design`.
- Per-fidelity loss weights are standard: "L_total = L_LF + λ_HF L_HF + ...",
  "especially important in multi-fidelity settings, where the model must
  reconcile abundant low-fidelity supervision with scarce high-fidelity labels"
  [cite: https://arxiv.org/html/2602.01176v1 (fetched)] → iteration_4.md
- Attribution-of-gains is a named duty: "Too frequently, authors propose many
  tweaks absent proper ablation studies, obscuring the source of empirical
  gains"; the Melis LSTM precedent [cite:
  https://ar5iv.labs.arxiv.org/html/1807.03341 (fetched)] → iteration_4.md
- Second degeneracy refutation attempt: **no usable results** → iteration_4.md

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched in THIS loop) | What remains open |
|---|---|---|---|
| **D-A** — B4's core A/B: allpairs-dedup arm (duplicates removed → self_only's data at allpairs' 18 steps/epoch) + step-matched self_only (epoch scaling) + frozen controls, to split effective-N/weighting from optimization budget | **`preempted` (ML-general methodology) — open only as an in-repo measurement** | Epoch-matched comparisons "conflate algorithmic quality with compute" (8x updates/epoch), with BOTH matched controls constructed — https://arxiv.org/html/2606.10321v1 · https://arxiv.org/abs/2606.10321 · "obscuring the source of empirical gains" + the Melis precedent — https://ar5iv.labs.arxiv.org/html/1807.03341 · dedup changes required train steps — https://arxiv.org/abs/2107.06499 , https://arxiv.org/html/2407.06654 | Nothing methodologically. What is open is the **answer on `ifc_poisson` at N_hf=5**: does the 0.021913 vs 0.034264 gap survive step-matching? No fetched source reports MF effect sizes at N_hf=5 (fourth consecutive batch of this negative). The card must claim the *measurement*, never the *method*. Note the documented failure mode: in https://arxiv.org/html/2606.10321v1 the epoch-matched ranking **reversed** under step-matching. |
| **D-B** — make an explicit per-level row-WEIGHT knob the mechanism under test (`allpairs` = 1+#levels-below control, `self_only` = natural, weight-matched arm) | **`preempted` (MF-general)** | Per-fidelity loss weights, incl. upweighting the scarce HF level: "L_total = L_LF + λ_HF L_HF + ...", "reconcile abundant low-fidelity supervision with scarce high-fidelity labels" — https://arxiv.org/html/2602.01176v1 · duplication-as-weighting is named and published ("importance duplication", with discretization / minibatch-co-occurrence caveats) — https://ar5iv.labs.arxiv.org/html/1806.02512 · hard-dedup vs soft-reweight framed as alternatives — https://arxiv.org/html/2407.06654 | The knob is old. Open is only: **which** implicit weight schedule the ladder construction imposes, and whether it is the cause of the s1 result. Also open (and worth pre-registering): the fetched search-return caution that HF upweighting "showed some improvements ... though results were not consistently better than with equal penalties across different network weight initializations" — a seed-sensitivity warning that lands hard at ADR-0004 single-seed. |
| **D-C** — report B3-T1-F1/T1-F2 (all-pairs on an aligned/nested ladder is pure replication; ×1/×2/×3/×4 schedule; 0.625×/2.5× effective weights) as a round-level observation | **`novel` (narrow) — "not previously reported", never "novel method"** | Nearest neighbours, in order: POSEIDON's all2all, whose O(K²) amplification is explicitly grounded in the semi-group property with a source-varying input — https://ar5iv.labs.arxiv.org/html/2405.19101 (this is the family's own cited inspiration, per `mf_fno_allpairs/manifest.json`) · MF-DeepONet, which treats LF-HF alignment as a *requirement to be removed* for flexibility, not a source of degeneracy — https://arxiv.org/html/2503.17941v1 · "importance duplication" as the general form of what the construction reduces to — https://ar5iv.labs.arxiv.org/html/1806.02512 | Three independently worded searches (iter-3 terms 2 & 3, iter-4 term 3) found **no source stating that all-pairs / cross-level fidelity supervision on an aligned nested ladder degenerates into pure replication**. The claim is about a *construction*, not a method, so it is reportable as an unreported observation + a warning to anyone recasting all2all onto fidelity — but it is a one-line remark, not a contribution. Weak-novelty discipline (program.md §13.3, 0-for-4) applies: state it as "we could not find this reported", and cite POSEIDON's semi-group premise as the reason it should have been expected. |

## Citations summary

- [Diesendruck et al.] "Importance Weighted Generative Networks" — https://ar5iv.labs.arxiv.org/html/1806.02512 — used in: iteration_1 (term 1, fetched)
- [Lee et al. 2021] "Deduplicating Training Data Makes Language Models Better" — https://arxiv.org/abs/2107.06499 — used in: iteration_1 (term 2, fetched)
- [SoftDedup 2024] "SoftDedup: an Efficient Data Reweighting Method for Speeding Up Language Model Pre-training" — https://arxiv.org/html/2407.06654 — used in: iteration_1 (term 2, fetched)
- [2026] "Baseline-Free Policy Optimization for Neural Combinatorial Optimization" — https://arxiv.org/html/2606.10321v1 (body) and https://arxiv.org/abs/2606.10321 (abstract) — used in: iteration_2 (term 1, both fetched)
- [Lipton & Steinhardt 2018] "Troubling Trends in Machine Learning Scholarship" — https://ar5iv.labs.arxiv.org/html/1807.03341 — used in: iteration_4 (term 2, fetched)
- [Herde et al. 2024] "Poseidon: Efficient Foundation Models for PDEs" — https://ar5iv.labs.arxiv.org/html/2405.19101 — used in: iteration_3 (term 1, fetched); abs page https://arxiv.org/abs/2405.19101 also fetched (insufficient)
- [2025] "Physics-Guided Multi-Fidelity DeepONet for Data-Efficient Flow Field Prediction" — https://arxiv.org/html/2503.17941v1 — used in: iteration_3 (term 3, fetched)
- [2026] "Multi-Fidelity Physics-Informed Neural Networks with Bayesian UQ and Adaptive Residual Learning" — https://arxiv.org/html/2602.01176v1 — used in: iteration_4 (term 1, fetched)

Search-return only (NOT citable, recorded as such in the iteration files):
Weighted ERM https://arxiv.org/abs/2002.05145; data-pruning iteration-matching
synthesis (iteration_2 term 2); the HF-upweighting seed-sensitivity caution
(iteration_4 term 1); "Bilevel Graph Structure Learning, Revisited"
https://arxiv.org/pdf/2605.07577.

## Dead ends

- `arxiv.org/html/2405.19101v3` → **HTTP 404**. ar5iv recovered it. Batch 3's
  rule holds and extends: **ar5iv is the route for 2024 papers too**, not just
  pre-2024.
- `arxiv.org/abs/2512.04863` (PENCO) → the search summariser claimed a "Fixed
  optimization budget" fair-comparison safeguard; **the fetch found no such
  sentence**. Second independent confirmation of batch 3's warning that search
  summariser content must be fetch-verified before citation.
- `arxiv.org/pdf`, ScienceDirect, Springer, OpenReview, IOPscience,
  publica.fraunhofer.de → not attempted (batch-1/2/3 dead-route rules); this
  cost real coverage on term 2 of iteration 2 and term 3 of iteration 4, both
  of which recorded search-return-only findings as a result.
- Term `"...revisiting ablation deep learning..."` → collides hard with medical
  **ablation therapy** literature. Use "source of empirical gains" /
  "matched compute" instead.
- **Nothing at N_hf = 5, again** (fourth consecutive batch). The literature
  supplies mechanisms and no effect sizes for this regime.

## For the brainstormer

The brainstormer MUST quote the verdict for whatever it proposes.

1. **Propose D-A, and frame it as a measurement, not a method.** Verdict:
   `preempted (ML-general) — open only as an in-repo measurement`. Quote
   https://arxiv.org/html/2606.10321v1 ("this comparison conflates algorithmic
   quality with compute") as the *justification for the design*. Any card text
   implying the step-matched control is an innovation contradicts this loop.

2. **Run BOTH matched controls, not one.** The fetched precedent runs both
   directions: scale the short arm's epochs UP to the long arm's update count,
   AND read the long arm off at the short arm's update count. B4's plan
   (dedup arm at allpairs' step count + self_only at 280/175 x epochs) matches
   this; keeping both is what makes the answer non-ambiguous whichever way it
   falls. The precedent also documents a **rank reversal** under step-matching —
   so pre-register both readings.

3. **Expect and pre-register the "it was the steps" outcome.** self_only is
   0.021913 vs the control's 0.034264 = 1.43x the `ifc_poisson` noise floor
   (0.23990756 skill, `state/noise_floor.json`). If step-matching closes the
   gap to below the floor, that is a *result* — it retires the round's best
   claimable ifc_poisson number as a compute artifact, which the end-of-round
   confirmation slate must know before it spends 3 seeds on it.

4. **Do NOT propose the per-level weight knob as the contribution.** Verdict:
   `preempted (MF-general)` — https://arxiv.org/html/2602.01176v1 shows
   per-fidelity loss weights (including HF upweighting) as standard practice
   with published weight values. It is fine as the *instrument*; it is not the
   claim.

5. **The duplication==weighting equivalence is an approximation, and its
   published caveat bites here.** "Importance duplication" carries a named
   failure mode when "two or more copies of the data point x_i appear in a
   minibatch" (https://ar5iv.labs.arxiv.org/html/1806.02512). With bs=16 and 5
   HF rows replicated x4, duplicate co-occurrence within a minibatch is
   frequent — so `allpairs` is not *exactly* `self_only`-with-weights even at
   matched steps; it also changes gradient-noise structure. If the card wants a
   clean weighting arm, prefer an explicit per-sample loss weight over
   replication, and say why (this is a third arm worth one line, not a fourth
   training run if budget is tight).

6. **D-C is the one thing that can be stated as unreported — carefully.**
   Verdict: `novel (narrow)`. Three independent refutation searches found
   nothing. Say "we could not find this reported", cite POSEIDON's semi-group
   premise (https://ar5iv.labs.arxiv.org/html/2405.19101) as the reason the
   recast should have been expected to degenerate, and note that
   `mf_fno_allpairs/manifest.json` itself advertises "amplifies the data
   O(L^2)" — the manifest, not the paper, is what B3 falsified. Cross-stream:
   `tools/ladder_pair_row_audit.py` shows the same REPLICATION_ONLY verdict on
   `heat_local`, so this is a warning to **every** stream, not just s1.
