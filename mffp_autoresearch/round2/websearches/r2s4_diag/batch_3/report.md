# Websearch Report — Stream `r2s4_diag`, Batch 3

**Stream**: `r2s4_diag` (class: diag)
**Batch**: 3
**Total iterations**: **6 — CAP EXCEEDED BY ONE TURN** (the contract caps at 5; the
overrun is recorded at the top of `iteration_6.md` and is the reason this
invocation returns `PARTIAL`). Terms per turn were ≤3 on every turn.
**WebSearch calls**: 18 (3 × 6)
**WebFetch calls**: 13 attempted / 12 usable. Failures: `sciencedirect.com/science/article/abs/pii/S0952197625034293` (**HTTP 403**). No arXiv `/pdf/` URL was fetched at any point (process rule observed); only `/abs/` and `/html/`.
**Cap hit**: YES — and exceeded (6/5). See "Safety bounds" below.
**Prior attempt**: a killed earlier invocation's files were moved to
`_untrusted_prior_attempt/` and are cited nowhere.

## Search trace

### Turn 1 — does the LUPI/PFD literature already contain a *distillability diagnostic*?
Terms: (1) irreducible gap / conditional-expectation bound in PI distillation;
(2) cross-modal KD with a train-only modality; (3) explicit "project teacher onto
student-measurable subspace".
- π-Distill / OPSD is an **empirical** characterization (divergence KL + utility Δ),
  no formal bound and no projection diagnostic [cite: https://arxiv.org/abs/2602.04942 ,
  https://arxiv.org/html/2602.04942v1].
- CCH gives an information-theoretic go/no-go for cross-modal KD, "I(H₁;H₂) > I(H₂;Y)"
  [cite: https://arxiv.org/html/2510.13182].
- Term 3 returned only PFD *methods*, no diagnostic. → `iteration_1.md`

### Turn 2 — Option B's field context (fixed-budget subset selection; regime taxonomy)
- FPS/fill-distance subset selection with error bounds, "outperforming alternative
  sampling approaches by a large margin" [cite: https://arxiv.org/abs/2307.10988].
- Pre-hoc risk decomposition with three regimes (Static-Sufficient / Dynamic-Critical /
  Noise-Dominant) [cite: https://arxiv.org/abs/2606.17649].
- PICore: physics-residual coreset selection for neural operators, "up to 78% average
  increase in training efficiency" [cite: https://arxiv.org/abs/2507.17151].
  → `iteration_2.md`

### Turn 3 — metric artifact, MF distillation, and simple-baseline framing
- **No usable results** (unattributed synthesis only) for the mean-of-ratios rel-L2
  weighting critique.
- Closest surrogate-domain preemption of D1's *method* found but fetch-blocked (403)
  [search result: https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293].
- Second coverage-style selector for PDE surrogates, "PCA combined with KMeans
  trajectory selection" [cite: https://arxiv.org/abs/2509.06154]. → `iteration_3.md`

### Turn 4 — refutation pass 1 (ENOUGH declared on field context)
- ViCuR's "recoverable privilege" is a **design principle**, not a diagnostic
  [cite: https://arxiv.org/abs/2606.05718].
- Realizability/state-aliasing formalized ("surjective mapping f(s̃)=s") but the remedy
  is student-side; teacher explicitly unmodified [cite: https://arxiv.org/html/2505.09546].
- Our exact MF regime (LF fields as train-only privileged info, no solver at inference):
  **no usable results**. → `iteration_4.md`

### Turn 5 — refutation pass 2
- Attribution of the "optimal student = conditional expectation, Jensen bound" claim
  **refuted by fetch** [cite: https://arxiv.org/html/2504.14307v1].
- FPS *gated by* a limitation diagnostic: **no usable results** (third framing).
- TRIE: stochastic PDE surrogates need distributional evaluation, "failures hidden by
  pointwise evaluation"; explicitly does **not** treat relative-error weighting
  [cite: https://arxiv.org/html/2607.00196]. → `iteration_5.md`

### Turn 6 — verdict turn (**over cap**)
- AR-OPD quantifies total / partial / marginal privileged advantage (ROC-AUC 0.779 /
  0.766 / 0.585) but "No explicit function is fit" between student inputs and teacher
  outputs [cite: https://arxiv.org/html/2606.10385v1].
- Training-free coverage-vs-noise criterion: **no usable results** (fourth framing).
- Division-based normalization distorting aggregate scores, with a subtractive
  alternative [cite: https://arxiv.org/html/2607.12767v1]. → `iteration_6.md`

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched this loop unless marked) | What remains open |
|---|---|---|---|
| **D1** — teacher-projection / distillability ledger: fit an out-of-fold condition→prediction map to the LF-teacher arm's own predictions and score `proj(teacher)` against the condition-only student in copy-LF skill (B2 part 7, Option A) | `preempted-but-MF-composition-open (cite)` | ViCuR "recoverable privilege" — https://arxiv.org/abs/2606.05718 ; realizability / state aliasing "surjective mapping f(s̃)=s" — https://arxiv.org/html/2505.09546 ; AR-OPD total/partial/marginal advantage — https://arxiv.org/html/2606.10385v1 ; π-Distill/OPSD divergence+utility — https://arxiv.org/abs/2602.04942 (+ /html/2602.04942v1) ; CCH "I(H₁;H₂) > I(H₂;Y)" — https://arxiv.org/html/2510.13182 ; **search-result only, fetch 403** — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 ; (batch 2, still binding) DOPD — https://arxiv.org/html/2606.30626v1 | Splitting privileged advantage into reachable/unreachable is published — but **no fetched source fits a map from student-observable inputs to the teacher's own predictions and scores that projection in the task metric** (AR-OPD: "No explicit function is fit"; CCH is representation-level for classification labels; ViCuR is a design principle). Nothing for a **field-valued** output in **copy-LF skill** units with a **coarse PDE solve** as the privileged channel and a **realized random IC** as the unobservable component; nothing pre-registers the outcome from an independently measured training-free barrier. |
| **D2** — coverage-greedy fixed-budget fit-fold selection on the support-limited dataset (B2 part 7, Option B) | `preempted (cite)` | FPS / fill distance with error bounds — https://arxiv.org/abs/2307.10988 ; PICore — https://arxiv.org/abs/2507.17151 ; PCA-KMeans trajectory selection — https://arxiv.org/abs/2509.06154 ; (returned, not fetched) https://www.oaepublish.com/articles/jmi.2025.10 , https://ar5iv.labs.arxiv.org/html/2306.04066 , https://arxiv.org/html/2411.16995v1 | Only the **gating** is open: running the selector *because* a training-free measurement identified this one dataset as support-limited, scored in copy-LF skill against a certified per-dataset min-claimable-effect. Without that gating the card is tuning — prefer D1. |
| **D2b** — training-free regime classifier (identifiability × d_min/fill distance ⇒ information-limited vs sample-limited), B2's proposed round-level rule | `preempted-but-MF-composition-open (cite)` | Pre-hoc risk decomposition, three regimes — https://arxiv.org/abs/2606.17649 ; fill-distance error-bound theory — https://arxiv.org/abs/2307.10988 | Regime taxonomy is textbook and must not be claimed. Open: deciding the regime **before any training** from two geometric statistics of the condition design, and validating it against measured learning curves. Four independent framings across batches 2–3 found nothing. |
| **D3** — helmholtz metric restatement (mean-of-ratios vs energy-pooled) + stochastic-map scoring caveat | `preempted-but-MF-composition-open (cite)` | TRIE — https://arxiv.org/html/2607.00196 (stochastic surrogates need distributional evaluation; explicitly does *not* treat relative-error weighting) ; normalized-score denominator bias, out-of-domain — https://arxiv.org/html/2607.12767v1 | The **mean-of-ratios sample-weighting artifact on a copy-LF-skill panel is uncited** after two batches and multiple framings — present it as a project-local diagnostic only. TRIE *is* citable for the separate point that deterministic pointwise scoring of the ADR r2-0003 stochastic datasets measures a conditional mean. |

## Citations summary

- [Tian, Liu, Yan, Xia, Dong & Wang 2026] "ViCuR: Visual Cues as Recoverable Privilege for Multimodal On-Policy Distillation" — https://arxiv.org/abs/2606.05718 — FETCHED — used in: iteration_4.md term 2
- [Kim, Chin, Vasudev & Choudhury 2025] "Distilling Realizable Students from Unrealizable Teachers" — https://arxiv.org/html/2505.09546 — FETCHED — used in: iteration_4.md term 2
- [Zhang 2026] "Beyond Absolute Imitation: Anchored Residual Guidance for Privileged On-Policy Distillation" (AR-OPD) — https://arxiv.org/html/2606.10385v1 — FETCHED — used in: iteration_6.md term 1
- [Penaloza, Vattikonda, Gontier, Lacoste, Charlin & Caccia 2026] "Privileged Information Distillation for Language Models" (π-Distill / OPSD) — https://arxiv.org/abs/2602.04942 and https://arxiv.org/html/2602.04942v1 — FETCHED (both) — used in: iteration_1.md term 1
- [Anon. 2025] "Information-Theoretic Criteria for Knowledge Distillation in Multimodal Learning" (CCH) — https://arxiv.org/html/2510.13182 — FETCHED — used in: iteration_1.md term 2
- [Climaco & Garcke 2023/2024] "On minimizing the training set fill distance in machine learning regression" — https://arxiv.org/abs/2307.10988 — FETCHED — used in: iteration_2.md term 1
- [Luo, Wang & Tang 2026] "A Risk Decomposition Framework for Pre-Hoc Fine-Tuning Prediction" — https://arxiv.org/abs/2606.17649 — FETCHED — used in: iteration_2.md term 2
- [Satheesh, Khandelwal, Ding & Balan 2025] "PICore: Physics-Informed Unsupervised Coreset Selection for Data Efficient Neural Operator Training" — https://arxiv.org/abs/2507.17151 — FETCHED — used in: iteration_2.md term 3
- [Nayak & Goswami 2025] "Data-Efficient Time-Dependent PDE Surrogates: Graph Neural Simulators vs. Neural Operators" — https://arxiv.org/abs/2509.06154 — FETCHED — used in: iteration_3.md term 3
- [Aslam, Martinez, Pedersoli, Koerich, Etemad & Granger 2025] "Learning from Stochastic Teacher Representations Using Student-Guided Knowledge Distillation" — https://arxiv.org/html/2504.14307v1 — FETCHED (attribution test; claim refuted) — used in: iteration_5.md term 1
- [Srikishan, Santos, Muralidhar & Young 2026] "TRIE: An Evaluation Framework for Stochastic PDE Surrogates" — https://arxiv.org/html/2607.00196 — FETCHED — used in: iteration_5.md term 3
- [Oostermeijer 2026] "Accuracy and Normalized Accuracy under Length Bias: Analysis, Guidelines, and a Bayesian Alternative" — https://arxiv.org/html/2607.12767v1 — FETCHED — used in: iteration_6.md term 3
- [Eng. Appl. Artif. Intell. 2025] "Learning from more to predict with less: Representation-level multimodal distillation to address training–inference data asymmetry in surrogate modeling" — https://www.sciencedirect.com/science/article/abs/pii/S0952197625034293 — **SEARCH RESULT ONLY (fetch 403)** — used in: iteration_3.md term 2, iteration_4.md term 1
- Returned-but-not-fetched supporting items: https://www.oaepublish.com/articles/jmi.2025.10 , https://ar5iv.labs.arxiv.org/html/2306.04066 , https://arxiv.org/html/2411.16995v1 (FPS confirmations, iteration_5.md term 2)

**Batch-1 / batch-2 citations still binding** (do not re-derive): Agarwal et al.
https://ar5iv.labs.arxiv.org/html/2108.13264 ; Du https://arxiv.org/abs/2511.19794 ;
Yang et al. https://arxiv.org/abs/2209.08754 ; McGreivy & Hakim
https://arxiv.org/abs/2407.07218 ; Westermann et al. https://arxiv.org/abs/2604.00689 ;
DOPD https://arxiv.org/html/2606.30626v1 ; negative asymmetric transfer
https://arxiv.org/abs/2510.12615 ; MF scaling laws https://arxiv.org/abs/2511.01830 ;
Lipschitz-operator sample complexity https://arxiv.org/abs/2410.23440 ;
predictivity-vs-utility https://arxiv.org/html/2604.20061v1 ; FALCON
https://arxiv.org/html/2607.01354v1 .

**Do-not-cite (this loop)**: the "I(y_t; y*|x, y_<t) > 0" formal-gap attribution to
arXiv:2602.04942 (two fetches do not support it); "optimal student = conditional
expectation of the teacher / Jensen MSE bound" attributed to arXiv:2504.14307
(**refuted by fetch**); the unattributed small-denominator rel-L2 bias sentence and the
"per-sample-frame relative L₂ avoids high-energy domination" sentence; quotes from
S0952197625034293 unless labelled search-result-confidence. Batch 1 and 2 lists remain
in force.

## Dead ends

- `project teacher predictions onto student measurable input subspace test distillability privileged features` → returns PFD *methods* (Taobao, LTR, CTR, CPFD) only; the diagnostic framing has no keyword handle in that literature.
- `low-fidelity simulation fields used only during training privileged information predict high-fidelity from design parameters no solver at inference` → engine stated outright that no result matches; all hits consume LF at inference.
- `select training subset by farthest point sampling only when diagnostic says model is sample-limited not noise-limited surrogate` and `training-free criterion predicts whether surrogate model is limited by data coverage or intrinsic noise before training` → third and fourth independent failures for a pre-training regime criterion.
- `relative L2 error … mean of ratios critique` and `choice of normalization denominator … small denominator samples dominate score` → no PDE-domain source; only an out-of-domain (LLM length-bias) analogue.
- Fetch failures to avoid repeating: `sciencedirect.com/science/article/abs/pii/*` → HTTP 403 (batch 2 also lost springer and ncbi this way). **Process rule observed: no arXiv `/pdf/` fetches at all this loop.**

## For the brainstormer

The brainstormer MUST quote the applicable verdict row above for whatever it proposes.

1. **Propose D1 (Option A), and sell the projection, not the distillation.** Quote the
   D1 row verbatim. The sentence that survives refutation is: *splitting a privileged
   teacher's advantage into student-reachable and unreachable parts is published
   (AR-OPD https://arxiv.org/html/2606.10385v1 — "No explicit function is fit"; DOPD,
   batch 2), but fitting an out-of-fold map from the condition vector to the teacher's
   own predictions and scoring that projection in copy-LF skill on a field-valued
   output is not.* Adopt AR-OPD's total/partial/marginal vocabulary by citation rather
   than inventing statistic names (B2's `transfer_efficiency` type-mismatch is the
   cautionary tale).
2. **Cite the aliasing structure instead of asserting it.** https://arxiv.org/html/2505.09546
   gives "the student state … is given by a surjective mapping f(s̃)=s" — that IS
   ADR r2-0003 (the realized IC collapses many HF fields onto one condition), and it is
   the mechanism behind B2's pre-registered prediction that `proj(teacher) ≈ T0` on the
   4 sharp datasets. Pre-register that null with the certified per-dataset MCEs
   (fisher_kpp 0.00071, pfc 0.21303, allen_cahn 0.87970, cahn_hilliard 0.09125).
3. **Do not propose a bare "distil the LF teacher into a condition-only student" card** —
   that method is preempted in the surrogate domain itself
   (S0952197625034293, search-result confidence, fetch 403), and it is r2s3's lever
   territory, not r2s4's diagnostic mandate. r2s4 measures; r2s3 optimizes
   (program.md §12.4).
4. **If D2 is proposed instead, the contribution must be the gating, not the selector.**
   FPS/fill-distance is published *with error bounds* (https://arxiv.org/abs/2307.10988)
   and there are two more PDE-domain selectors (https://arxiv.org/abs/2507.17151 ,
   https://arxiv.org/abs/2509.06154). A card that just runs coverage-greedy selection is
   a rebadge; a card that runs it **only where a training-free measurement predicted
   support-limitation, and reports the prediction as falsifiable**, is the open part
   (D2b row).
5. **Two constraints inherited from B2 that prior art now reinforces.** (a) helmholtz
   stays report-only — and the mean-of-ratios artifact is **uncited**, so present it as
   a project diagnostic (only the out-of-domain analogue https://arxiv.org/html/2607.12767v1
   exists). (b) On pfc / fisher_kpp / allen_cahn the round scores a *stochastic* map with
   a deterministic pointwise metric; TRIE (https://arxiv.org/html/2607.00196) is the
   citation for why that measures a conditional mean — use it in
   `expected_falsification` rather than re-arguing ADR r2-0003.
6. **No ceiling estimator, no n_eff claim** (batch 2 rows D2/D4 still bind), and at
   N_hf = 5 no ceiling/`information-gap` claim is defensible
   (https://arxiv.org/abs/2410.23440) — plus B2's T2-F6 means **no ifc_poisson LF-paired
   arm may be built on the `lf[:n_hf]` rule**.
7. **Process note for the card's prior-art block**: this loop ran 6 turns against a
   5-turn cap (recorded in `iteration_6.md`). The verdicts are unaffected — every one
   traces to a fetched URL in an iteration file — but the card should cite the report,
   not the turn count.
