# Websearch Report — Stream `r2s4_diag`, Batch 1

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 1
**Total iterations**: 5 (cap)
**WebSearch calls**: 15 (3 per iteration × 5)
**WebFetch calls**: 17 (14 succeeded, 3 failed on undecodable PDFs: arxiv.org/pdf/2407.07218, arxiv.org/pdf/2504.03503, the NeurIPS PFD proceedings PDF); ≤2 fetches per search term every turn
**Cap hit**: YES — 5/5 iterations used; ≤3 terms every turn, no truncations.

## Search trace

### Turn 1 — floors and seed variance (are they published hygiene or open methodology?)
Terms: (1) trivial baselines for PDE surrogates; (2) seed-variance/significance
reporting for neural operators; (3) SciML benchmark pitfalls / weak baselines.
- Weak-baseline prevalence is quantified: "79% (60/76) compare to a weak
  baseline" [cite: https://arxiv.org/abs/2407.07218 ; journal
  https://www.nature.com/articles/s42256-024-00897-5].
- The interpolation-diagnostic is stated in near-r2s4 terms: "The key diagnostic
  is whether classical reduced-order methods with comparable offline cost achieve
  similar accuracy; if so, the benchmark tests interpolation…"
  [cite: https://arxiv.org/html/2604.20061v1].
- The empirical mean predictor is already an algorithmic floor/starting point
  [cite: https://arxiv.org/abs/2606.17460].
- A current neural-operator UQ paper explicitly has "no formal protocol for
  statistical significance testing" between models
  [cite: https://arxiv.org/html/2603.11052].
→ `iteration_1.md`

### Turn 2 — value of the LF/privileged signal
Terms: (1) value of LF data in MF surrogates; (2) learning using privileged
information; (3) MF negative transfer / when LF hurts.
- Round 2's regime has an exact published name: **LUPI**, with two mechanism
  families (distillation-based; auxiliary-feature/multi-task)
  [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC8596492/].
- MAGPI works at 10/16/45 HF samples but "lacks explicit ablation studies
  quantifying low-fidelity contributions in isolation"
  [cite: https://arxiv.org/html/2603.22050].
- MF force-field study: log–log linear pretrain↔finetune accuracy relation;
  matched-budget arms not confirmable from the abstract
  [cite: https://arxiv.org/abs/2506.14963].
→ `iteration_2.md`

### Turn 3 — tiny-N overfitting anatomy
Terms: (1) neural-operator generalization gap at few samples; (2) operator
learning data-scaling laws; (3) effective sample size for correlated data.
- The literature is remedy-oriented (physics losses, reduced bases, multi-level
  training), not diagnostic; **no** train/test gap decomposition protocol found.
- Scaling-law framing exists [cite: https://arxiv.org/abs/2203.13181 ;
  https://arxiv.org/pdf/2410.00357] but the specific rates surfaced in search
  snippets could NOT be verified from fetched text — flagged do-not-quote.
- No PDE-domain effective-sample-size diagnostic. "No usable results" for term 3.
→ `iteration_3.md`

### Turn 4 — refutation pass 1 (ENOUGH declared on field survey)
Terms aimed at D1-spread, D1-floors, D2.
- Few-run statistics is a solved, published protocol: stratified bootstrap CIs,
  IQM, performance profiles, probability of improvement, explicitly for "3–10
  runs per task" [cite: https://ar5iv.labs.arxiv.org/html/2108.13264].
- With three seeds, a conservative paired protocol (BCa bootstrap + sign-flip
  permutation on per-seed deltas) "never declares significance" for 0.6–2.0-point
  effects that single runs call significant [cite: https://arxiv.org/abs/2511.19794].
- Dedicated search for a mandatory trivial-predictor floor panel in parametric-PDE
  benchmarking: **no usable results**.
→ `iteration_4.md`

### Turn 5 — refutation pass 2 (cap)
Terms aimed at D2 (arXiv version of the PFD paper), D3, D1-floors (reworded).
- PFD runs the matched with/without-privileged-information design explicitly
  ("includes a no-distillation baseline… enabling direct comparison of
  distillation's impact") and reports the **non-monotone law**: student
  performance rises then falls as the privileged feature becomes more predictive,
  via teacher-variance [cite: https://arxiv.org/abs/2209.08754].
- Simple beats neural in the low-data smooth regime: "polynomial surrogates
  achieve substantially better data efficiency for smooth input fields"
  [cite: https://arxiv.org/abs/2604.00689].
- MF-DeepONet's N_hf sweep / HF-only control arm not confirmable from the abstract
  [cite: https://arxiv.org/abs/2204.06684].
→ `iteration_5.md` (contains the full verdict text)

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1a** — certify a minimum-claimable-effect from a 3-seed condition→HF spread (replaces provisional `noise_floor.json`) | `preempted (cite)` | Agarwal et al., *Deep RL at the Edge of the Statistical Precipice* — https://ar5iv.labs.arxiv.org/html/2108.13264 ; Du, *When +1% Is Not Enough* — https://arxiv.org/abs/2511.19794 | Nothing methodological. Open item is the **empirical constant** for this panel/regime. Adopt IQM + stratified/paired BCa bootstrap CIs + per-seed deltas instead of a bare max−min spread; expect 3 seeds to license only LARGE effects. |
| **D1b** — training-free floor panel (NN-in-condition / train-mean / zero) as mandatory reported arms | `preempted-but-MF-composition-open (cite)` | McGreivy & Hakim — https://arxiv.org/abs/2407.07218 (79% weak baselines) ; *Predictivity and Utility…* — https://arxiv.org/html/2604.20061v1 (interpolation diagnostic) ; Westermann et al. — https://arxiv.org/abs/2604.00689 (polynomial beats neural, low data) ; Operator Boosting — https://arxiv.org/abs/2606.17460 (mean predictor as floor) | All published floors are **fitted** (ROM, polynomial, GP, kriging). Two dedicated searches found no *training-free* trivial-predictor panel reported as mandatory columns, and none expressed in **copy-LF skill units** for a no-solver-at-test regime. That composition is open. |
| **D2** — value-of-LF accounting: matched architecture/budget ± LF-training-signal arms | `preempted-but-MF-composition-open (cite)` | Yang et al., *Toward Understanding Privileged Features Distillation in LTR* — https://arxiv.org/abs/2209.08754 (matched no-distillation arm; non-monotone law) ; LUPI framing — https://pmc.ncbi.nlm.nih.gov/articles/PMC8596492/ ; MAGPI — https://arxiv.org/html/2603.22050 | Three fetched sources independently report **no standard protocol for isolating marginal PI/LF value**. Open: LUPI instantiated with coarse-grid PDE *fields* as privileged info for a *field-valued* output, scored in copy-LF skill; and the **nested-ladder degeneracy** as a domain-specific reason the value may be zero. |
| **D3** — overfitting anatomy at N_hf ∈ {5,20,50} / N=400: train/test gap decomposition + n_eff | `preempted-but-MF-composition-open (cite)` — LOW confidence (one dedicated search) | MAGPI — https://arxiv.org/html/2603.22050 (10/16/45 HF samples, single-fidelity arm) ; MF-DeepONet — https://arxiv.org/abs/2204.06684 ; scaling-law frame — https://arxiv.org/abs/2203.13181 | HF-sample sweeps are routine; **gap decomposition** and a **domain n_eff estimator** were not found. Re-search before a B2/B3 card leans on this. |

## Citations summary

- [McGreivy & Hakim 2024] "Weak baselines and reporting biases lead to overoptimism in machine learning for fluid-related partial differential equations" — https://arxiv.org/abs/2407.07218 (journal: https://www.nature.com/articles/s42256-024-00897-5) — used in: iteration_1.md term 3
- [anon. 2026] "Predictivity and Utility of Neural Surrogates of Multiscale PDEs" — https://arxiv.org/html/2604.20061v1 — used in: iteration_1.md term 1
- [Operator Boosting 2026] "Operator Boosting Produces Pareto-Efficient PDE Surrogates" — https://arxiv.org/abs/2606.17460 — used in: iteration_1.md term 1
- [Structure-Aware EUQ 2026] "Structure-Aware Epistemic Uncertainty Quantification for Neural Operator PDE Surrogates" — https://arxiv.org/html/2603.11052 — used in: iteration_1.md term 2
- [MAGPI 2026] "MAGPI: Multifidelity-Augmented Gaussian Process Inputs for Surrogate Modeling from Scarce Data" — https://arxiv.org/html/2603.22050 — used in: iteration_2.md term 1
- [Retaining PI for MTL] "Retaining Privileged Information for Multi-Task Learning" — https://pmc.ncbi.nlm.nih.gov/articles/PMC8596492/ — used in: iteration_2.md term 2
- [MF-MLFF 2025] "Understanding multi-fidelity training of machine-learned force-fields" — https://arxiv.org/abs/2506.14963 — used in: iteration_2.md term 3 (abstract only)
- [de Hoop, Huang, Qian & Stuart] "The Cost-Accuracy Trade-Off In Operator Learning With Neural Networks" — https://arxiv.org/abs/2203.13181 — used in: iteration_3.md term 2 (abstract only; rates NOT verified)
- [Subedi & Tewari] "Operator Learning: A Statistical Perspective" — https://arxiv.org/abs/2504.03503 — used in: iteration_3.md term 2 (abstract only)
- [Agarwal et al. 2021] "Deep Reinforcement Learning at the Edge of the Statistical Precipice" — https://ar5iv.labs.arxiv.org/html/2108.13264 — used in: iteration_4.md term 1
- [Du] "When +1% Is Not Enough: A Paired Bootstrap Protocol for Evaluating Small Improvements" — https://arxiv.org/abs/2511.19794 — used in: iteration_4.md term 1
- [Yang, Sanghavi, Rahmanian, Bakus & Vishwanathan 2022] "Toward Understanding Privileged Features Distillation in Learning-to-Rank" — https://arxiv.org/abs/2209.08754 — used in: iteration_5.md term 1
- [Westermann, Huber, O'Leary-Roseberry & Zech] "Performance of Neural and Polynomial Operator Surrogates" — https://arxiv.org/abs/2604.00689 — used in: iteration_5.md term 3
- [Lu, Pestourie, Johnson & Romano 2022] "Multifidelity deep neural operators…" — https://arxiv.org/abs/2204.06684 — used in: iteration_5.md term 2 (abstract only)

**Do-not-cite list** (surfaced in search snippets, never verified in a fetch):
the FNO Navier–Stokes scaling rate `r = 0.28` / "60.1K samples for 1% error";
SPDEBench's "less than a factor of two from 1K→10K samples"; the sparse-HF
"20 samples" MF-beats-HF-only anecdote; gradient-enhanced MF NNs' "10 vs 12 HF
samples". Re-verify before any card quotes these.

## Dead ends

- `nearest neighbor in parameter space baseline parametric PDE surrogate benchmark trivial predictor mandatory reporting` → returns kNN as a *modelling ingredient* and GP/BNN as baselines; the concept "training-free floor panel as mandatory columns" appears to have no keyword handle in this literature.
- `relative L2 error benchmark neural operator worse than predicting zero mean field normalization critique` → the critique literature is about weak *numerical* baselines and about normalization/resolution-invariance, not about trivial predictors. No hit.
- `effective sample size correlated training samples deep learning diagnostic redundancy dataset` → only applied-domain saturating learning curves and MCMC-style ESS; nothing in the PDE-surrogate domain.
- PDF fetches of https://arxiv.org/pdf/2407.07218, https://arxiv.org/pdf/2504.03503, and the NeurIPS PFD proceedings PDF returned undecoded binary — use `arxiv.org/abs/…` or `ar5iv.labs.arxiv.org/html/…` instead.

## For the brainstormer

The brainstormer MUST quote the applicable verdict row above for whatever it proposes.

1. **Reframe B1's spread half honestly.** D1a is `preempted` — do NOT propose
   "invent a noise-floor certification". Propose "apply Agarwal et al.'s few-run
   protocol (IQM + stratified bootstrap CI) and Du's paired per-seed-delta
   sign-flip test to certify the condition→HF effect threshold on this panel".
   Cite both. The deliverable is a *number*, not a method — which is exactly what
   a `diag` stream is for, so this costs the card nothing.
2. **Budget for the 3-seed reality.** Du reports a conservative paired protocol
   with **three seeds never declaring significance** for sub-2-point effects. The
   card should say up front what effect size 3 seeds CAN license here, and should
   report paired per-seed deltas (aligning with round 2's drift-class rule)
   rather than max−min spread, so downstream falsification clauses are testable.
3. **The floor panel's novelty is the composition, not the arms.** D1b: lead with
   "training-free floors expressed in copy-LF skill units for a no-solver-at-test
   regime", and cite McGreivy & Hakim for *why* mandatory floor columns matter and
   Westermann et al. for *simple beats neural in the low-data regime*. Do not claim
   NN/mean/zero baselines are novel — they are not. Note the existing
   `floors.json` artifact already shows ifc_poisson's NN floor is a **5-atom
   dictionary** (all 128 test points map onto 5 train fields); B1's reproduction
   should report that as a caveat rather than as a floor.
4. **D2 has a citable, falsifiable prediction waiting for it.** Yang et al.'s
   non-monotone law says a *highly predictive* privileged feature can make the
   student WORSE via teacher variance. On our panel the LF field is extremely
   predictive (copy-LF is the reference), so the LUPI prior predicts LF-as-teacher
   may hurt. Write that into the card's `expected_falsification` — it converts a
   preempted design into a genuine test, and it pairs with the **nested-ladder
   degeneracy** (LF is a spectral truncation of HF; it may add nothing).
5. **Do not quote unverified numbers.** The do-not-cite list above (scaling-rate
   r=0.28, the 60.1K figure, SPDEBench's factor-of-two, the 20-sample anecdote)
   came from search snippets only. Any card quoting them fails the citation rule.
6. **D3 is under-searched.** If B2/B3 proposes overfitting anatomy with n_eff, ask
   for a fresh websearch batch first — it got one dedicated refutation search and
   the verdict is low-confidence.
