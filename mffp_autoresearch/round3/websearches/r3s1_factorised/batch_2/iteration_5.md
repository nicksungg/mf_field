# Iteration 5 — §3.3 refutation pass 2 + PRIOR-ART VERDICT (iteration cap reached)

**Cap note: this is iteration 5 of 5. The loop stops here per the websearcher contract §3.2.**

## Search rationale

Three last refutation queries, one per surviving direction, each phrased to *find* the preemption rather than to confirm novelty: (1) the exact D1 criterion stated in PCA vocabulary ("keep only modes learnable from the inputs"); (2) the exact D3 instrument ("oracle nearest-neighbour in target space separates irreducible from model error"); (3) the D1 theory side ("truncation error dominates at few samples — so raise the latent dimension"), which is where a preemption would live if someone had already made the fisher_kpp argument.

## Search terms used

1. `discard unpredictable principal components keep only modes learnable from inputs surrogate regression skill based basis selection` (D1)
2. `separate irreducible error from model error using nearest neighbor in target space oracle retrieval diagnostic dataset` (D3)
3. `operator learning error decomposition truncation of latent basis dominates few-shot parametric PDE increase latent dimension` (D1 theory)

## Findings

### Term 1 (D1) — closest returns select components by *output variance*, not by input-predictability

Returns: PCA+Kriging global surrogates that retain "principal components that account for nearly all the **uncertainty of the dynamic output**" [https://www.sciencedirect.com/science/article/abs/pii/S0951832020308541]; UQLab ultrahigh-dimensional surrogate extension [https://ethz.ch/content/dam/ethz/special-interest/baug/ibk/risk-safety-and-uncertainty-dam/publications/reports/RSUQ-2018-008A.pdf]; dimensionality reduction in model **inputs** [https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=928052]; sparse basis-function selection (SSR) for interpretable surrogates [https://www.osti.gov/servlets/purl/1642435]; shrinkage/variable selection notes [https://tommasorigon.github.io/datamining/slides/un_C.html].
All snippet-level; none fetched, because all select on the **output side by variance/energy** or on the **input side by dimension reduction** — neither is "drop an output direction because the input cannot predict it".
**No usable preemption of the D1 criterion.**

### Term 2 (D3) — no published instrument of this exact shape

Three successive rephrasings by the search backend returned bias–variance-decomposition tutorials, aleatoric/epistemic decomposition (e.g. [https://proceedings.mlr.press/v80/depeweg18a/depeweg18a.pdf]), and nearest-neighbour uncertainty estimation [https://arxiv.org/html/2407.02138v1].
Verbatim from the turn's own summary: "The specific methodology of using **'oracle retrieval in target space' to diagnose model error from irreducible error does not appear in these results**."
Note the honest reading: this is a *null from one query family*, and the phenomenon (omitted variable → unserviceable subpopulation) is classical (iteration 2, term 2). Not fetched.

### Term 3 (D1 theory) — reduced-basis error separation and closed-form latent readouts are both published (two fetches)

**FETCHED** — Wang & Lin, *Reduced-Basis Deep Operator Learning for Parametric PDEs with Independently Varying Boundary and Source Data* (RB-DeepONet), arXiv:2511.18260, 23 Nov 2025 — [cite: https://arxiv.org/abs/2511.18260].
Verbatim: "The trunk is fixed to a rigorously constructed **RB space generated offline via Greedy selection**, granting physical interpretability, stability, and **certified error control**"; "The branch network **predicts only RB coefficients**"; "We provide convergence guarantees **separating RB approximation error from statistical learning error**."
This is the strongest structural neighbour of the whole r3s1 family: parameters → reduced-basis coefficients, with the basis chosen by a certified (greedy, error-driven — *not* energy) criterion and the truncation/statistical error split proved.

**FETCHED** — Deng, Sun, Meng & Wang, *Randomized neural operator for parametric PDEs with fast training and conformal uncertainty quantification* (PCA-RaNN), arXiv:2606.29440, 28 Jun 2026 — [cite: https://arxiv.org/abs/2606.29440].
Verbatim: "a randomized latent neural operator that combines **PCA-based dimensionality reduction with fixed random features and a closed-form least-squares readout**. It recasts latent operator learning as **fixed-feature linear regression**"; plus "an **energy-matched scaling rule**", ensemble averaging, split-conformal intervals, and "rapid online adaptation via **recursive least squares**".
Implication for this stream: "closed-form least-squares readout on PCA coefficients of a parametric-PDE field" is published as of June 2026 — the r3s1 family's *architecture class* carries no novelty at all, only its composition and its selection rule can.
Also returned, snippet only: SFO Hilbert spectral basis where "the only approximation being **truncation to the top modes**" [https://arxiv.org/html/2601.17090]; MOFS few-shot multi-operator [https://arxiv.org/abs/2508.01211].

## PRIOR-ART VERDICT

### D1 — adaptive / predictability-criterion basis selection replacing the `SELECT_MAX = 32` clip

**Verdict: `preempted-but-MF-composition-open (cite)`.**
Published and therefore unclaimable: the critique that "**energy-based truncation can discard low-energy modes needed to capture small-scale features**" and task-driven mode selection (arXiv:2605.27756); certified **greedy** (error-driven, non-energy) reduced-basis selection with the RB-approximation / statistical-learning error split proved (arXiv:2511.18260); truncation-vs-regression **error decomposition identifying a truncation error floor** (par.nsf.gov/biblio/10684905); mode-count as a CV hyperparameter tuned against downstream predictability (arXiv:1907.12239; doi 10.3390/en19102387 snippet); and closed-form least-squares readout on PCA coefficients for parametric PDEs (arXiv:2606.29440).
**What remains open**: admitting a basis direction on a **per-direction out-of-fold predictability-from-the-condition** criterion (rather than energy, reconstruction error, or a certified residual bound), with the retained set then feeding an OOF-corrected second stage, in the **no-LF-at-test** regime at N_hf 5–400, scored on a copy-LF-skill panel. Five refutation queries across iterations 1/4/5 returned no per-direction predictability screen.
**Hard caveat**: merely raising the numeric cap `SELECT_MAX` is a hyperparameter repair of an arbitrary clip — an instrument/bug-fix, exactly like batch 1's affine floor, and it must be shipped as such. Only the *criterion* is a candidate claim.

### D2 — replacement discriminator `n_SET` / `E_rem` x reachability (training-free, pre-unlock)

**Verdict: `preempted-but-MF-composition-open (cite)`.**
Published: the bias–variance account of when target-as-input stacking helps and the rule that unrelated targets should be modelled independently (arXiv:1211.6581, already the batch-1 citation of record; corroborated by arXiv:2406.07991).
**What remains open**: the **estimator** — a pre-fit statistic computed from the reduced basis' *unexplained residual energy* and its condition-reachability, evaluated before the test tensor unlocks, as a predictor of the cascade's payoff on PDE reduced-basis coefficients. No returned work computes one.
**Standing risk the brainstormer must price**: batch 1 pre-registered `cond_dim` as the discriminator and its own controlled pair falsified it (ac vs ch, both cond_dim 19, margins 0.0148 vs 0.6945). A second discriminator pre-registered at n = 5 cells, with the mechanism stage having already *fit* the new statistic on those same cells, is at real risk of being a post-hoc rationalisation dressed as a pre-registration.

### D3 — two-population certification (a scored cell certified condition-incomplete on identified rows)

**Verdict: `preempted-but-MF-composition-open (cite)`.**
Published: automatic **slice discovery** — "slice detection models (SDM), which automatically identify **underperforming groups of datapoints**" with a benchmark and quantitative metrics (arXiv:2211.04476, TACL), plus the 2025–26 cluster (arXiv:2501.19032, 2501.16751, 2605.29836, 2306.08167); post-hoc **diagnostic-panel auditing** of learned PDE models (arXiv:2606.18200); and, classically, omitted-variable subpopulation failure (iteration 2).
**What remains open**: the *inversion* — a slice that is **indistinguishable in input (condition) space** yet separated in **target (field)** space, used to certify the **benchmark's** conditioning as incomplete rather than to blame the model, with an oracle field-retrieval arm bounding the reducible part. Every fetched SDM discovers slices in an embedding/semantic feature space and concludes about the model.
**Scope warning**: `B1.json:7_gap_and_future.next_direction` says explicitly "Do NOT spend a batch on cahn_hilliard's hard 27%: it is a condition-completeness limit, not an architecture limit", and the orchestrator routed the 27-row mask to `r3s3_lf_value`. Treat D3 as an instrument + cross-stream handoff, not as this batch's scored object.

### D4 — feeding stage 2 `[predicted SET coefficients, condition]`

**Verdict: `preempted (cite)`.**
Spyromitros-Xioufis et al., *Multi-Target Regression via **Input Space Expansion**: Treating Targets as Inputs*, arXiv:1211.6581 — the method's definition is augmenting the **original input space** with (OOF-corrected) predicted targets; feeding stage 2 the condition alongside the predicted coefficients *is* SST, not a variant of it (re-surfaced and re-confirmed in iteration 4, term 2).
Ship it as the minimal repair of the batch-1 information loss, named as SST; it cannot be a claim.

## Interpretation

The batch's strongest available position is D1's *criterion* (with the cap-raise shipped separately as a bug-fix), D2 is a repeat bet on an already-once-falsified claim shape, D3 belongs to r3s3 as an instrument, and D4 is a named repair.
Note also that arXiv:2606.29440 removes any residual novelty from the family's architecture class, so no batch-2 card should describe the closed-form PCA-coefficient readout as new.
