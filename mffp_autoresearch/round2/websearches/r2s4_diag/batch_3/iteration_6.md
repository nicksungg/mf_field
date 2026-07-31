# iteration_6 — `r2s4_diag` batch 3 — FINAL VERDICT TURN

> **SAFETY-BOUND VIOLATION, RECORDED**: the websearcher contract caps the loop at
> **5 iterations**. This is turn **6**. Cause: I mis-tracked the turn counter and
> dispatched one further refutation block (3 terms — the per-turn term cap was NOT
> exceeded) before writing the verdict. No result below is discarded (that would
> hide the overrun), but the orchestrator should treat the loop as having run
> 6/5 turns, and this batch's return status is `PARTIAL` for that reason. Terms
> per turn stayed ≤3 on every turn (18 WebSearch calls over 6 turns).

## Search rationale

Final refutation turn: close the three open questions the previous turn left —
(a) is the *quantification* of a privileged teacher's reachable-vs-unreachable
advantage published, (b) does a training-free coverage-vs-noise regime criterion
exist, (c) is per-sample-normalized-score bias documented anywhere fetchable —
then write the verdicts.

## Search terms used

1. `oracle skyline ablation quantify distillable fraction of privileged teacher advantage information gap upper bound student`
2. `training-free criterion predicts whether surrogate model is limited by data coverage or intrinsic noise before training parametric regression`
3. `choice of normalization denominator relative error benchmark unfair comparison surrogate small denominator samples dominate score`

## Findings per term

### Term 1 — the strongest preemption found for D1's *quantification*
Results: DOPD (https://arxiv.org/html/2606.30626v1 — already cited in batch 2);
**Beyond Absolute Imitation: Anchored Residual Guidance for Privileged On-Policy
Distillation** (https://arxiv.org/html/2606.10385v1); *On the Generalization of
Knowledge Distillation: An Information-Theoretic View* (arXiv 2605.13143, PDF
only, not fetched); *Privileged Information Distillation for LMs* (already
fetched, iteration 1); *One Student, Many Teachers* (arXiv 2607.18293).

FETCHED https://arxiv.org/html/2606.10385v1 — Wenhao Zhang (South China Univ. of
Technology), 2026. They decompose the learning signal —
"log q_full − log π_θ = (log q_part − log π_θ) + (log q_full − log q_part)" — and
in §C.3 compute **total / partial / marginal advantage**, reporting that "the
partial privileged view is nearly as predictive of final correctness as the
full-vs-student total advantage signal: partial advantage reaches ROC-AUC 0.766,
close to the total signal at 0.779. By contrast, the marginal full-minus-partial
signal falls to 0.585." The fetch's assessment of the mapping question is
explicit: "**No explicit function is fit.**" They use a *partial privileged
teacher* as "an 'anchor' — a proxy for what is locally learnable" and note "the
method does not model the boundary between observable and unobservable advantage;
it operationalizes it via truncation and scaling (λ parameter)."

→ So: splitting a privileged teacher's advantage into a student-reachable part
and an unreachable part, and quantifying the split, **is published** (AR-OPD;
DOPD's capability-vs-information gap, batch 2). Fitting a map from
student-observable inputs to the teacher's own predictions and scoring that
projection **in the task metric** is not what either does.

### Term 2 — training-free coverage-vs-noise regime criterion (D2b)
**No usable results** (fourth independent framing to fail across batches 2–3).
The engine stated the results "don't appear to contain information about the
specific training-free criterion you're asking about". Returned items were
noisy-data MF surrogate frameworks (https://arxiv.org/html/2401.06447v1),
label-noise sample selection (https://arxiv.org/abs/2310.10463), active-learning
reliability analysis (arXiv 2401.10796) — none of them a pre-training regime
diagnostic.

### Term 3 — normalized-score denominator bias (D3)
FETCHED https://arxiv.org/html/2607.12767v1 — **Accuracy and Normalized Accuracy
under Length Bias: Analysis, Guidelines, and a Bayesian Alternative**, Koen
Oostermeijer, 2026. LLM multiple-choice evaluation, but the structural point is
the one B2's T2-F5 makes: division-based normalization "frequently overcorrects",
"naive length normalization largely flattens the global trend over medium-length
completions" while "for short completions we often observe a sharp decrease", and
normalized accuracy's Kendall correlations are "uniformly positive" (biased) and
"sometimes substantially worse than unnormalized approaches". Their fix replaces
division by a subtractive, prior-based correction:
"ℓ̃_θ(c|x;b) ≡ ℓ_θ(c|x) − b·n", with "4×–8× reduction in length bias relative to
normalized accuracy".

→ A citable, fetched treatment that per-sample normalization can *distort
aggregate benchmark scores*, in a different domain. Still **no** PDE-domain
source on mean-of-ratios rel-L2 sample weighting after two framings in this batch
plus prior batches.

## PRIOR-ART VERDICT

Candidate directions this stream-batch is likely to propose, from
`experiment_cards/r2s4_diag/batch_2/B2.json` part 7 (Options A and B) and its
cross-stream rule candidate.

### D1 — teacher-projection / distillability ledger (B2 Option A, recommended)
*Fit an out-of-fold map from the condition vector to the LF-teacher arm's own
predictions; score `proj(teacher)` against the condition-only student in copy-LF
skill, to bound what ANY train-only distillation channel could transfer.*

**Verdict: `preempted-but-MF-composition-open (cite)`**

Preempted parts, all fetched THIS loop:
- The *setting* (teacher with a train-only privileged channel, student restricted
  to deployment inputs) — ViCuR, https://arxiv.org/abs/2606.05718: "Because these
  cues are derived from the same visual input available at inference, their
  evidence is recoverable by the student" (a **design principle**, per the fetch,
  not a diagnostic).
- The *structural cause* our regime has (ADR r2-0003 aliasing) — *Distilling
  Realizable Students from Unrealizable Teachers*,
  https://arxiv.org/html/2505.09546: "the student state … is given by a surjective
  mapping f(s̃)=s, meaning multiple teacher states s̃ may collapse to the same
  student state s."
- The *advantage split itself* — AR-OPD, https://arxiv.org/html/2606.10385v1
  (total / partial / marginal advantage, ROC-AUC 0.779 / 0.766 / 0.585), on top of
  batch 2's DOPD capability-vs-information gap.
- *Empirical predictors of PI-distillation success* — π-Distill/OPSD,
  https://arxiv.org/abs/2602.04942 + https://arxiv.org/html/2602.04942v1
  (divergence KL and utility Δ; "the strongest predictor of performance for OPSD
  is the information content of the PI").
- *An information-theoretic go/no-go for a privileged teacher* — CCH,
  https://arxiv.org/html/2510.13182: "I(H₁;H₂) > I(H₂;Y)".
- Surrogate-domain method preemption (SEARCH RESULT ONLY, fetch 403):
  https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 —
  "treating auxiliary modalities as privileged information and distilling their
  latent structure into the student … requiring only deployment-feasible inputs at
  inference", "outperforming even the privileged teacher in data-scarce regimes".

What remains open (state it exactly this way in the card):
1. **No fetched source fits a regression from the student's observable inputs to
   the teacher's own predictions and scores that projection in the task metric.**
   AR-OPD explicitly does not ("No explicit function is fit"; it uses a partial
   privileged teacher as a proxy anchor); CCH works at the level of learned
   representations and classification labels; ViCuR is a design principle scored
   by end-task deltas.
2. Nothing found does this for a **field-valued** output, in **copy-LF skill**
   units, with a **PDE coarse solve** as the privileged channel, in a regime where
   the unobservable component is a **realized random initial condition**.
3. Nothing found pre-registers the outcome from an independently measured
   training-free barrier the way B1/B2 can here.

### D2 — coverage-greedy fixed-budget fit-fold selection (B2 Option B)
**Verdict: `preempted (cite)`** — do NOT propose the selector as a contribution.
- Climaco & Garcke, https://arxiv.org/abs/2307.10988: Farthest Point Sampling,
  "selecting a training set by aiming to minimize the fill distance of the
  selected set", with "theoretical bounds on prediction error based on training
  set fill distance", "significantly reduces the maximum prediction error … 
  outperforming alternative sampling approaches by a large margin".
- PICore, https://arxiv.org/abs/2507.17151 (physics-residual coreset selection for
  neural-operator training; "up to 78% average increase in training efficiency").
- Nayak & Goswami, https://arxiv.org/abs/2509.06154 ("a PCA combined with KMeans
  trajectory selection strategy"; "<1% relative L2 using only 3% of available
  trajectories").
- Three further confirmations returned this loop (FPS in chemical feature space
  https://www.oaepublish.com/articles/jmi.2025.10; Intelligent Sampling
  https://ar5iv.labs.arxiv.org/html/2306.04066; Curvature-Informed FPS
  https://arxiv.org/html/2411.16995v1).
What remains open: only the *gating* — running FPS **because** a training-free
measurement said this dataset (and only this dataset) is support-limited, and
reporting the result in copy-LF skill against a certified per-dataset
min-claimable-effect. If the card cannot make that gating the contribution, D2 is
a tuning exercise and should be skipped in favour of D1.

### D2b — training-free regime classifier (identifiability × fill distance),
B2 part-7(a)'s proposed round-level rule.
**Verdict: `preempted-but-MF-composition-open (cite)`**
- Nearest neighbour fetched: *A Risk Decomposition Framework for Pre-Hoc
  Fine-Tuning Prediction*, https://arxiv.org/abs/2606.17649 — "decomposing
  prediction risk into two components: an intrinsic limit (static data-model
  compatibility) and a reducible optimization variance", organising tasks into
  "three regimes (Static-Sufficient, Dynamic-Critical, and Noise-Dominant)".
  Same taxonomy shape, different domain, and it needs probing runs.
- The taxonomy itself (signal/intermediate/noise-dominated; flat learning curve ⇒
  more data wasted) is textbook and must not be claimed.
- Open: predicting the regime **before any training** from two geometric
  statistics on the condition space (identifiability index and d_min/fill
  distance) and validating that prediction against measured learning curves.
  Four independent search framings across batches 2–3 failed to find it.

### D3 — helmholtz metric restatement + stochastic-map scoring caveat
**Verdict: `preempted-but-MF-composition-open (cite)`**
- Fetched and citable: TRIE, https://arxiv.org/html/2607.00196 — stochastic PDE
  surrogates need distributional evaluation ("failures hidden by pointwise
  evaluation"); this is the citation for why deterministic pointwise scoring on
  the ADR r2-0003 datasets measures a conditional mean, and the fetch explicitly
  confirms TRIE "does *not* discuss per-sample relative error weighting".
- Fetched, out-of-domain analogue for division-based normalization distorting
  aggregate scores: https://arxiv.org/html/2607.12767v1.
- Open / project-local: the **mean-of-ratios vs energy-pooled** contrast on a
  copy-LF-skill panel remains uncited after two batches and two framings — B3 must
  present it as a project diagnostic (as B2 did), never as literature-backed.

## Do-not-cite list from this loop (search-engine synthesis only, attribution
failed or absent)
- "I(y_t; y* | x, y_<t) > 0" as a formal irreducible-gap theorem in
  arXiv:2602.04942 — two fetches of that paper do not support it.
- "The optimal student is the conditional expectation of the teacher's output
  given the student's input … by Jensen's inequality the student's MSE is bounded
  by the teacher's" — attribution to arXiv:2504.14307 **refuted by fetch**.
- "Per-sample normalization … dividing by small denominators amplifies errors"
  and "per-sample-frame relative L₂ avoids high-energy trajectories dominating" —
  unattributed engine synthesis (iterations 3 and 5).
- The ScienceDirect S0952197625034293 quotes — search-result text, fetch 403;
  cite at that confidence and label it, or not at all.
- Batch 1 and batch 2 do-not-cite lists remain in force.
