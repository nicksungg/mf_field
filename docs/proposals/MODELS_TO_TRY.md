# Models To Try — Candidate Catalog

**Status:** catalog for a build/no-build decision. Nothing implemented.
**Date:** 2026-07-22.
**Reference model:** `mf_fno_transfer_film` (#1 by Elo) — transfer schedule + per-block FiLM on the condition vector X.

## TL;DR

**Two hypotheses explain why MF neural operators struggle on high-frequency PDEs, and eight training runs can decide between them.**

**H1 — the bottleneck is spectral capacity.** Every FNO family in the zoo hardcodes `modes_cap=12`, which on a 256×256 grid keeps **12 of 128 available modes** and discards the rest. Nobody has ever tuned it per dataset, so every architectural result in the zoo was measured through the same spectral bottleneck.

**H2 — the bottleneck is missing local representation.** Global spectral mixing may simply be unable to express localized structure, and the fix is a convolutional branch. The question is not whether a CNN helps but **when it should exist**: during LF pretraining, only at HF fine-tuning, or both.

**HF-data proportion is not a third study.** It is an axis crossing both, asking the question the leaderboard cannot: everything was ranked at full HF data, but scarce HF is the project's premise, so does the ranking *reorder* as HF shrinks?

### The four things worth knowing before reading further

1. **Do the free measurement first.** D1 (§2.1) is an FFT over stored fields — zero training — giving the radial spectrum of the HF field, the LF field, and the **HF−LF residual**, which has never been measured on these datasets. It says whether `modes_cap=12` is absurd, where to place every subsequent experiment, and whether M2's core premise holds at all.
2. **The mode-count question is already solved — use the solution.** **iFNO** ([arXiv:2211.15188](https://arxiv.org/abs/2211.15188), from the FNO authors' own group) progressively grows the mode count during training and reports 10% lower error at 20% *fewer* modes. It returns the per-dataset answer in one run, replacing a 4-point sweep. Cite it, don't reinvent it (§2.1b).
3. **A is already run.** The A/B/C transfer study's baseline leg *is* `mf_fno_transfer_film` at #1, so the decisive H2 experiment costs 2 new configs (§3.1).
4. **Three prerequisites can invalidate everything.** The CLI is fixed at six args so sweeps need an env-var knob; that knob is invisible to the eval `code_hash`, so **two sweep points would silently collide in the cache**; and there is no CUDA seeding despite the `seed=42` contract, so ablation deltas may be smaller than run-to-run noise. All three are cheap to fix and are covered in §5.

### Priority order

**D1 (free) → fix determinism → M3 (iFNO) and M5 (A/B/C) in parallel → the surviving hypothesis' follow-ups → HF axis.**
Roughly **8 training configs**, versus several dozen for a naive full-factorial sweep.

### The strategic finding

Six proposals across this project have now hit the same verdict — Candidates A, B and C in `NEW_MODELS.md`, plus M2, M3 and a group-lasso idea here: **the mechanism was already published, and the multi-fidelity composition was what survived.**
At six for six that is not bad luck, it is information. The mechanisms are covered by large, well-resourced groups; what is not covered is how they behave under scarce-HF transfer across 17 benchmark datasets.
Treat published mechanisms as instruments to cite and use, and make the MF composition the thesis (§6).

## 0. What this doc is, and what it is not

This is a **menu of candidate models to build**, organized under the two-hypothesis framing from [`NEW_MODELS_2.md`](NEW_MODELS_2.md).
Each entry gives the mechanism, what changes relative to the reference model, the expected payoff, and an explicit novelty-risk line.

It supersedes [`NEW_MODELS_2.md`](NEW_MODELS_2.md) as the live candidate list.
It does **not** supersede the other proposal docs, which stay where they are and are not re-catalogued here:

- [`NEW_MODELS.md`](NEW_MODELS.md) — Candidates A–D (diffusion refiner, FNO↔WNO hybrid, cycle-consistency, warp-then-correct).
- [`MODEL_TWEAKS.md`](MODEL_TWEAKS.md) — cross-family fixes, a different axis entirely (correctness of the existing zoo, not new families).
- The P-proposals in `../reports/MF_Sharp_HighFreq_Report.md` and N1–N7 in `../reports/MF_Leaderboard_Beaters_2026_Report.md`.

**PINN is excluded as a reference model.**
`mf_fno_pinn_transfer` sits at #2 with the best median relL2 in the zoo, but its PDE-residual term requires recovering the governing equation in closed form — it only does this on the Poisson datasets and falls back to plain FiLM-transfer elsewhere.
Building on it would contradict the standing decision not to embed physics we do not know.

### Novelty handling

Every candidate carries a `NOVELTY-RISK` line stating what it most likely collides with, a confidence, and the search terms to run.
**Assume `UNVERIFIED` unless the line says otherwise.**

One exception: **§2.1b was verified against primary sources on 2026-07-22**, because the question it covers — can the backbone learn its own mode count — turned out to be closed literature, and that materially changed the H1 plan (see §2.4 and §6).
Everything else still needs its search run before any `INSPIRATION.md` claims novelty.

This is deliberate. The recurring failure in this project has not been wasted candidates — Candidates A, B and C were all still recommended for build after their prior-art passes — it has been *writing the novelty claim before running the search*, then walking it back.
Run the searches below before any `INSPIRATION.md` claims novelty.

---

## 1. The two hypotheses

`NEW_MODELS_2.md` reduces the whole project to two competing explanations for why MF neural operators struggle on high-frequency PDEs:

| | Hypothesis | Tests |
| --- | --- | --- |
| **H1** | The bottleneck is **spectral capacity** — the model literally cannot represent the frequencies present in the target. | Mode count, adaptive modes, learned frequency masks, frequency-aware losses. |
| **H2** | The bottleneck is **local representation** — global spectral mixing cannot express localized structure, and the fix is local (convolutional / attentional) features. | The A/B/C transfer study, residual-aware Transolver. |

**HF-data proportion is not a third hypothesis.** It is an axis crossing both: it asks whether whatever wins at full HF data still wins when HF is scarce, which is the regime the project premise actually assumes.

The ordering is a dependency, not a preference.
H1's diagnostic (§2.1) is free and re-scopes H1's sweep; H1's outcome determines whether H2 is even worth running at full breadth; the HF axis is only meaningful once there is a winner per hypothesis to apply it to.

---

## 2. H1 — Is the bottleneck spectral truncation?

### Why this is the first thing to test

Every FNO family in the zoo hardcodes `modes_cap=12`, and the mode allocation is
`modes(grid, c) = (min(c, H//2), min(c, W//2 + 1))` (`models/_common/fire_core.py:147`).
Grids are capped at `WORK_CAP = 256`, so on a 256×256 dataset the model retains **12 of 128 available modes along H** and discards everything above.

Nobody has ever tuned this per-dataset.
The two exceptions in the zoo are incidental, not investigations: `fno_coregionalization` uses 16, and `fno_coreg_residual` uses a per-level schedule `(4, 8, 12, 12)`.

If 12 is far below where the target's energy actually lives, every architectural result in the zoo was measured through the same spectral bottleneck.

### 2.1 D1 — Residual spectrum diagnostic *(not a model; run this first)*

**What it is.** Per dataset, compute the radial power spectrum of three fields: the HF field, the LF field, and the **HF − LF residual**.
Report cumulative energy fraction against radial mode index k, and define `k*(τ)` = the smallest k retaining a fraction τ of residual energy, for τ ∈ {0.95, 0.99}.

**Why the residual and not just the HF field.** The model is not asked to produce the HF field from nothing — it is asked to produce what LF is missing.
The residual spectrum is therefore the quantity that determines the required mode budget, and `../reports/MF_FNO_CNN_Hybrid_Report.md` (line 166) records that it has never been measured on these datasets.
The LF spectrum is worth computing alongside it because the point where LF energy dies is the boundary above which HF detail cannot be recovered from LF at all, only inferred from X.

**Cost: zero training.** This is an FFT over already-stored fields.

**Payoff.** Three things at once: whether `modes_cap=12` is absurd or roughly right; where to place the training points in §2.2 instead of guessing; and a per-dataset predicted-optimal mode count that §2.2 can then falsify.

**The actual deliverable** is the correlation between `k*` predicted from the free diagnostic and the empirically optimal mode count from §2.2.
If they track, you have a rule that sets modes per dataset for free, forever, and that rule is a publishable result on its own.

### 2.1b Prior art on learned mode count — **VERIFIED 2026-07-22**

Unlike the rest of this doc, this subsection was checked against primary sources.
The question "can the backbone learn how many modes to use?" is **already answered in the literature, by the FNO authors' own group.**

| Work | Mechanism | Consequence here |
| --- | --- | --- |
| **iFNO** — Incremental Spatial and Spectral Learning, [arXiv:2211.15188](https://arxiv.org/abs/2211.15188) (George, Zhao, Kossaifi, Li, Anandkumar) | **Progressively increases the number of frequency modes** during training, alongside training-data resolution. States our exact problem: "too many modes can lead to overfitting, while too few can lead to underfitting." Reports 10% lower test error with **20% fewer modes** and 30% faster training. | The instrument for H1. Do not reinvent it. |
| **AFNO**, [arXiv:2111.13587](https://arxiv.org/abs/2111.13587) (Guibas, Mardani, Li, Tao, Anandkumar, Catanzaro) | Sparsifies frequency modes via **soft-thresholding and shrinkage** (LASSO-like), plus block-diagonal channel mixing. Vision token-mixing context. | Makes any "sparsify to discover the cutoff" proposal crowded. Claim nothing there. |
| **SirenFNO**, [arXiv:2606.11518](https://arxiv.org/abs/2606.11518) | SIREN-based **mode-wise kernel parameterization** learning a full-grid spectrum at constant, discretization-independent parameter count — "eliminating the need for frequency truncation." 4–15× parameter reduction, up to 73× with tensor decompositions. | Removes the mode-count hyperparameter entirely rather than tuning it. A structural alternative to this whole section. |
| **AdaptFNO** (Dang, Nguyen, Nguyen & Hy; NeurIPS 2025 ML4PS workshop) | Abstract and conclusion claim it "dynamically adjusts spectral modes based on input frequency content." **The methodology describes no such mechanism.** Read in full 2026-07-22 — see the assessment below. | **Does not pre-empt M2.** Its real overlap is with H2, not H1. |

**AdaptFNO, read in full (2026-07-22).** This was flagged as the biggest threat to M2. It is not one, and the gap between its claims and its method is worth recording.

What the methodology actually contains: patch embedding with positional encoding; **AFNO [Guibas et al.] applied essentially verbatim**, extended to multi-frame input, whose only described spectral machinery is AFNO's block-diagonal kernel `W ∈ C^(N_B×B×B)`; a global operator on downsampled low-resolution data; a local operator on high-resolution data; and a frequency-domain cross-attention that "selects relevant global modes for local forecasts."

There is **no mechanism that conditions mode selection on input frequency content**. The title's "dynamic spectral modes" is carried entirely by AFNO's inherited soft-thresholding — which the paper does not describe — and by the cross-attention selecting global modes for the local branch. Neither predicts a per-mode gate from a spectrum.

Weigh it accordingly: it is a 7-page workshop paper describing its own results as preliminary, evaluated on a **single case study** (Typhoon Yagi) with **no baseline comparison** — the paper states that "future benchmarks and comparisons will be made against well-known baseline such as CNNs and FNOs" — while its conclusion nonetheless asserts "state-of-the-art accuracy." That claim is unsupported by the paper's own account of what it has run.

**Where it does matter, and it is not H1.** A low-resolution global operator pretrained as a "context provider" for a high-resolution local operator, coupled in the frequency domain, is structurally close to this project's setup — pretrain on cheap/coarse, transfer to expensive/fine. They frame it as multiscale rather than multi-fidelity, and both branches receive abundant data so there is no scarce-HF premise. It is nonetheless a genuine architectural precedent for the coupling idea in **§3.1 (M5)** and should be cited there.
Note also a direct overlap of evaluation data: AdaptFNO is evaluated on ERA5, and `era5` is one of this benchmark's 17 datasets.

**What this means for H1.** The mechanism question is closed; the measurement question is not.
Nobody has reported the right mode count for *these 17 datasets*, and no published result tells you whether mode budget interacts with a *multi-fidelity transfer schedule*.
Run iFNO as an instrument, claim the MF composition, not the mechanism.

### 2.2 M1 — Higher-mode transfer-FiLM *(the control)*

**TL;DR.** `mf_fno_transfer_film` with nothing changed but `modes_cap`, swept over ~4 points bracketing the `k*` predicted by D1.

**Largely superseded by M3 (§2.4).** iFNO returns a per-dataset mode count from a single run, which is what this sweep is trying to approximate with four.
Keep M1 only as a cheap confirmation at whatever count iFNO discovers — and only if that number is surprising enough to be worth checking by hand.

**Why only 4 points.** A blind ladder is wasteful once D1 exists — the diagnostic says where the knee should be, so the sweep only has to confirm or refute it.
There is also a hard cost reason: spectral weights scale as `modes_h × modes_w`, so 12 → 48 is roughly **16× the spectral parameters**.
A blind high-mode sweep hits OOM before it hits diminishing returns.

**Expected payoff.** This is the cleanest possible test of H1 and it is nearly free to implement.
If error falls monotonically with modes up to `k*` and flattens after, H1 is confirmed and the zoo's whole architectural ranking is suspect.
If error is flat from 12 upward, H1 is dead and everything moves to H2.

**NOVELTY-RISK.** None claimed — this is a control, not a contribution.

### 2.3 M2 — LF-conditioned learned frequency mask *(survives prior-art check; run after M3)*

**TL;DR.** Keep a generous mode budget, but learn a per-mode gate `g(k) ∈ [0,1]` predicted **from the LF field's own spectrum**, and apply it to the spectral weights.
Instead of one global mode cutoff chosen by a human, each sample gets its capacity spent on the bands that sample actually needs.

**What changes vs. the reference.** The FiLM conditioning path stays; a small encoder on the LF spectrum is added, emitting a gate vector over retained modes per block.

**Why it would be the strongest H1 candidate, if it survives §2.1b.** It is the only one that is multi-fidelity by construction — the LF field is exactly the cheap, abundant signal that reveals where a given sample's energy sits, so the MF setting hands you the mask predictor for free.
A fixed high mode count pays the full parameter cost on every sample; this pays it only where it helps.

**Two limitations to state plainly.**

1. **A gate can only suppress, never extend.** It operates on a fixed `mh × mw` block, so if the ceiling is 32 and a sample needs mode 40, M2 cannot get there.
   M2 does not remove the hyperparameter — it changes it from "pick the right cutoff" to "pick a generous ceiling and prune inside it."
   Fix by composing with iFNO (§2.4), which raises the ceiling, while the gate allocates beneath it.
2. **Under task loss alone, the optimal gate is all-ones.** Suppressing any band can only worsen the training fit, so the sparsity penalty is not a safeguard against collapse — it is the entire reason the gate does anything.
   The required control is therefore **gated-32 vs. ungated-32**, never gated-32 vs. the current 12, which would credit the gate for a win that came from the larger budget.

**NOVELTY-RISK — the blocking question is resolved; M2 survives.**
AdaptFNO was the named threat and it was read in full on 2026-07-22 (§2.1b): despite its title and abstract, it contains **no mechanism that selects modes from input frequency content**, and nothing that predicts a per-mode gate from a low-fidelity view of the sample.
The specific idea here — a gate over retained modes, predicted from the LF field's spectrum — is **not pre-empted by the nearest candidate.**

Residual risk remains moderate and unverified: AFNO's soft-thresholding is a different route to sample-adaptive sparsity, and the general area is active.
Remaining searches before any novelty claim: `input-conditioned spectral gating PDE`, `factorized FNO F-FNO`, `frequency domain adaptation operator learning`, `hypernetwork spectral weights neural operator`.

**Sequencing note.** M2 is unblocked but should still run *after* M3 (§2.4). iFNO gives the per-dataset mode count, which sets the ceiling M2's gate then allocates beneath — and D1's per-sample correlation check (§2.1) says whether the gate's input carries signal at all. Building M2 first means guessing both.

### 2.4 M3 — iFNO under a multi-fidelity transfer schedule

**Revised 2026-07-22.** This entry previously proposed "mode-annealed transfer" as a new mechanism.
It is not new — **iFNO** (§2.1b) is progressive mode growth, published in 2022 by the FNO group. Use it rather than reinvent it.

**TL;DR.** Adopt iFNO as the H1 instrument, and ask the one question it does not answer: **how does progressive mode growth interact with a two-stage LF→HF transfer schedule?**

**The MF-specific question.** iFNO grows modes on a schedule driven by training progress, in a single-fidelity setting.
Here there are two data distributions with *different spectral content* — LF fields are band-limited, HF fields are not — and a discrete moment when the model switches between them.
That suggests the growth schedule should be tied to the **fidelity transition**, not to wall-clock training progress: hold a narrow budget during LF pretraining (spending high-mode capacity on LF fits noise at frequencies the LF data does not carry), then grow once the HF target arrives.

This is a thin delta on iFNO, and it should be described as one.
But it is a real one: no result found ties spectral growth to a fidelity transition, and the "correct" schedule under transfer is an open question that this benchmark is unusually well set up to answer.

**Expected payoff.** Moderate, and unusually cheap — iFNO likely has a reference implementation in the `neuraloperator` library, so this is closer to an integration than a build.
It also subsumes M1: iFNO returns a per-dataset mode count directly, replacing the 4-point sweep with a single run.

**NOVELTY-RISK — verified for the mechanism, open for the composition.**
The mechanism is iFNO and must be cited as such; `INSPIRATION.md` must not claim progressive mode growth.
The contribution to claim, if any, is the transfer-schedule coupling.
Remaining search: `incremental spectral learning transfer learning`, `progressive mode growth fine-tuning operator`.

### 2.5 M4 — Frequency-aware objectives

**TL;DR.** Direction 3 from `NEW_MODELS_2.md`: replace or augment relative-L2 with a frequency-weighted L2, a gradient loss, a multiscale loss, or a wavelet loss.
Very cheap to implement — no architecture change at all.

**The caveat that decides whether this is worth doing.** The leaderboard metric is per-sample relative-L2, and it is not changing.
So a frequency-weighted objective only wins if caring about high modes *also* improves relL2.
Where the high-frequency content is genuinely uncertain, it will not: the relL2-optimal prediction of an uncertain sharp feature is the blurred conditional mean, which is precisely the perception–distortion tradeoff already documented in `NEW_MODELS.md` §5.5 and `../reports/MF_Sharp_HighFreq_Report.md` §0.3.

**Recommendation.** Run it as a cheap ablation, not as a headline candidate, and read the result as a diagnostic: if a frequency-weighted loss improves relL2, the model was under-fitting high modes; if it degrades relL2 while looking sharper, you have re-derived the tradeoff rather than beaten it.

**NOVELTY-RISK — `UNVERIFIED`, high collision probability.** Frequency-weighted and wavelet losses for PDE surrogates are well covered. Treat as engineering, claim nothing.
Search: `frequency weighted loss neural operator`, `wavelet loss PDE surrogate`, `spectral bias training operator learning`.

---

## 3. H2 — Is the bottleneck missing local representation?

### 3.1 M5 — The A/B/C transfer study *(one experiment, not three projects)*

This is the hybrid study.
`NEW_MODELS_2.md` makes the key observation that a transfer study over architectures already **contains** the separate "parallel FNO+CNN" and "CNN refinement" proposals, so they should not be listed as independent projects:

| Variant | LF pretrain stage | HF fine-tune stage | Contains |
| --- | --- | --- | --- |
| **A** | FNO | FNO | the current reference model — **already run** (`mf_fno_transfer_film`, #1) |
| **B** | FNO + CNN | FNO + CNN | the parallel hybrid architecture |
| **C** | FNO | FNO + CNN | the residual-CNN refinement architecture |

The question is not "is a CNN good" but **when should the CNN exist**.

**How to read the outcome:**

| Result | Conclusion |
| --- | --- |
| B ≈ C ≈ A | Local representation is not the bottleneck. H2 dies, everything returns to H1. |
| B > A and C > A | Local representation matters; both placements work. |
| **C > B** | The CNN should exist *only* at HF — local detail is HF-specific and learning it on LF actively wastes or misdirects capacity. |
| **B > C** | Local features must be learned on abundant LF data and transferred; the scarce HF set cannot train them from scratch. |

**A confound to fix before running.** As written, B and C differ in *both* where the CNN sits and when it is trained.
To isolate "when should the CNN exist," B and C should be the **same architecture**, differing only in whether the CNN branch is trained during the LF stage or frozen/absent until HF.
Otherwise a C > B result cannot distinguish "the CNN belongs at HF" from "the parallel placement is worse than the residual placement."

**Expected payoff.** Highest of any entry here. A is free, so this is 2 new training configs for a decisive answer to half the project's scientific question.

**NOVELTY-RISK — `UNVERIFIED`, high for the architectures, lower for the study.**
Both FNO+CNN placements are established — see `../reports/MF_FNO_CNN_Hybrid_Report.md`, which found Park 2507.06133 and SINO pre-empt the hybrid itself and concluded only the MF composition survives.
The contribution to claim is therefore the **transfer-schedule study** — the systematic when-should-the-CNN-exist result — not any of the three architectures.

**Add AdaptFNO to this candidate's prior art** (verified 2026-07-22, §2.1b). It pairs a global operator pretrained on **downsampled low-resolution** data, acting as a "context provider," with a lightweight **high-resolution** local operator, coupled by frequency-domain cross-attention.
That is a direct precedent for the coarse-pretrain / fine-predict coupling M5 is built on, even though it is framed as multiscale rather than multi-fidelity and assumes abundant data in both branches.
It also evaluates on ERA5, which overlaps this benchmark's `era5` dataset — so it is a possible point of direct comparison, not merely a citation.

Search: `multi-fidelity transfer neural operator CNN hybrid`, `staged fine-tuning spectral local operator`, `when to add convolutional branch operator learning`, `global local operator coupling cross-attention forecasting`.

### 3.2 M6 — Residual-aware Transolver

**TL;DR.** Direction 4 from `NEW_MODELS_2.md`, and the one architectural idea there that is genuinely different in kind: stop trying to build a better predictor and instead build a **better allocation of computation**, using LF information, predicted difficulty, and residual estimates to guide attention.

**Two honest warnings, both of which should be resolved before this gets priority.**

1. Transolver families are currently the weakest non-reference entries in the zoo — `transolver_residual` is #23 (Elo 1392, median relL2 0.116) and `transolver_attention_fusion` is #26 (0.322), against 0.0154 for the reference.
   This candidate is asking a family that is losing by an order of magnitude to win by being smarter about where it spends attention.
2. That deficit is partly a **protocol artifact, not an architectural verdict** — and the asymmetry is larger than it first looks.
   The Transolver families and `v9_baseline` all sample point clouds at `n_lf=1024, n_hf=2048` (identical settings in all three `smoke_eval.py` files).
   The FNO families they are ranked against consume the **full capped grid** — up to 256×256 = 65,536 points.
   So the point-cloud families are being scored against dense-grid families while seeing roughly 3% as many points per sample.
   The leaderboard is consistent with this: the four bottom-ranked families (#23 `transolver_residual`, #26 `transolver_attention_fusion`, #29 `mf_deeponet`, #30 `v9_baseline`) are exactly the non-FNO, non-dense-grid ones.

**Recommendation.** Resolve warning 2 first — it is a `MODEL_TWEAKS.md`-class fix and it is cheap.
Until a Transolver is trained at comparable point density, its position in the zoo says more about sampling than about attention, and any M6 result inherits that ambiguity.
If Transolver is still an order of magnitude behind on a fair protocol, do not build M6.

**NOVELTY-RISK — `UNVERIFIED`, moderate.** Adaptive-computation and difficulty-guided attention are established in vision and language; the residual-guided MF framing is the possibly-new part.
Search: `adaptive computation neural operator`, `residual guided attention PDE`, `difficulty aware token allocation operator learning`, `Transolver physics attention`.

---

## 4. The HF-proportion axis

**What it asks.** Every number on the current leaderboard was measured at full HF data.
Scarce HF is the entire premise of the project, so the question that matters is not "what wins" but **"does the ranking reorder as HF shrinks."**

**Design.** Subsample the HF training set to a fixed fraction ρ with a fixed seed, leaving LF untouched.
Use **ρ ∈ {1.0, 0.25, 0.0625}** — three points, of which ρ=1.0 is free because the existing leaderboard already is ρ=1.
Apply it to the winner of H1 and the winner of H2, not to all 30 families.

A curve is not needed. Two additional points per model are enough to detect reordering, which is the result; a fine-grained data-efficiency curve is a follow-up only if reordering actually occurs.

**M7 — FiLM-only fine-tuning** is the one candidate this axis motivates on its own.
Freeze the FNO spectral weights after LF pretraining and fine-tune **only** the FiLM γ/β generators on HF.
The rationale is the zoo's own headline finding — conditioning mechanism mattered more than added architecture — combined with the observation that scarce HF and a large trainable parameter count is the classic overfitting setup.
Restricting HF adaptation to the conditioning path is the natural low-ρ play, and it should show up as a flatter error-vs-ρ curve rather than a better ρ=1 number.

**How hard to lean on that finding.** Not very, and this is worth stating before M7 is built on top of it.
`mf_fno_transfer_film` beats plain `mf_fno_transfer` **on Elo** (1820 vs 1616), but their median relL2 is effectively tied and marginally favours the plain model (0.0154 vs 0.0151).
So the FiLM result is a consistency win across datasets in pairwise comparisons, not a magnitude win — which is a fine reason to prefer FiLM as the conditioning path, but a weak reason to assume conditioning carries most of the model's capability.
M7 tests that assumption directly: if FiLM-only fine-tuning holds up as ρ falls, conditioning really is doing the work.

**NOVELTY-RISK — `UNVERIFIED`, high.** This is the operator-learning analogue of parameter-efficient fine-tuning (adapters, LoRA, BitFit), which is heavily published in other modalities.
Search: `parameter efficient fine-tuning neural operator`, `LoRA operator learning`, `adapter fine-tuning PDE surrogate`, `FiLM-only adaptation transfer`.

---

## 5. Constraints every candidate must satisfy

**The CLI is fixed.** `eval/MODEL_CONTRACT.md` pins `smoke_eval.py` to exactly `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`.
Neither `modes_cap` nor ρ can be passed as a flag without changing a fixed surface.

Recommended: an **environment-variable knob** (`MFFP_MODES_CAP`, `MFFP_HF_FRAC`) read inside each family, defaulting to current behaviour so existing cached results stay valid.
The fallback — one family directory per sweep point — is contract-clean but pollutes `models/` with a dozen near-duplicates and should be avoided.
This needs explicit sign-off because it changes how every sweep is run.

**Caching.** `eval/score.py` keys results on `(family, dataset, epochs, seed, code_hash)` where `code_hash` covers all `*.py` in the family directory.
An env-var knob is invisible to that hash, so **two sweep points would collide in the cache**.
Either include the knob value in the result tag or run sweeps with `--no_cache`. This is a correctness issue, not a convenience one.

**Determinism — this one can invalidate the whole exercise.**
These are ablations measuring small deltas, and the repo currently has no CUDA seeding or determinism guards despite the `seed=42` contract.
A 4-point mode sweep whose differences are smaller than run-to-run variance produces a confident-looking curve made of noise.
Before trusting any ablation here, either fix determinism or run ≥2 seeds per point and report the spread.
Treat this as a prerequisite for §2.2, §3.1 and §4, not as a nice-to-have.

**Build prerequisite.** `mf_fno_transfer_film` is not in this checkout — only `mf_fno_pinn_transfer` and `mf_fno_transfer_bar` are here, and the runnable shared internals live in the cluster tree.
Every candidate that forks the reference model has to be built there.

**Budget.** Smoke eval must stay ≤ ~30 min on one H100, over `ifc_heat` + `ifc_poisson` at 200 epochs.

---

## 6. Summary and recommended order

| ID | Candidate | Hyp. | New runs | Novelty risk | Notes |
| --- | --- | --- | --- | --- | --- |
| **D1** | Residual spectrum diagnostic | H1 | **0** | n/a | Free. Gates M1 and M2. Run first. |
| **M1** | Higher-mode transfer-FiLM | H1 | ~4 | none (control) | Sweep placed by D1. Largely **subsumed by M3** — iFNO returns the mode count in one run. |
| **M2** | LF-conditioned frequency mask | H1 | 1 | moderate (**unblocked**) | AdaptFNO checked and does not pre-empt it. Run after M3 sets the ceiling. |
| **M3** | iFNO under MF transfer | H1 | 1 | mechanism = prior art | Integration, not a build. Subsumes M1. Best H1 value. |
| **M4** | Frequency-aware objectives | H1 | 1–2 | high | Run as diagnostic, claim nothing. |
| **M5** | A/B/C transfer study | H2 | **2** (A is free) | high arch. / low study | Highest payoff here. |
| **M6** | Residual-aware Transolver | H2 | 1 | moderate | Gated on fixing the point-sampling confound. |
| **M7** | FiLM-only fine-tuning | axis | 1 | high | Judge on the ρ curve, not on ρ=1. |
| — | HF-proportion axis | axis | 4 | n/a | 2 extra ρ points × 2 hypothesis winners. |

**Recommended order:**

1. **D1** — free, and it re-scopes everything in H1 before a single GPU-hour is spent.
2. **Determinism prerequisite** (§5) — otherwise everything below is unfalsifiable.
3. ~~Read AdaptFNO~~ — **done 2026-07-22** (§2.1b). M2 is unblocked; AdaptFNO's real overlap is with M5, where it is now cited.
4. **M3 (iFNO) and M5 (A/B/C) in parallel** — the two decisive experiments, one per hypothesis, ~3 new configs between them.
   M3 replaces M1's sweep; run M1 only as a confirmation at the mode count iFNO discovers, and only if that number is surprising.
5. Then whichever hypothesis survives: **M2** if H1 (after M3 sets the ceiling), **M6** if H2 and the sampling confound clears.
6. **HF axis + M7** applied to the two winners.

Roughly **8 training configs** to answer both scientific questions, down from ~11 before the prior-art pass and several dozen for a naive full-factorial sweep.
The saving comes from D1 replacing blind mode search, iFNO replacing the mode sweep outright, A already being run, and the HF axis testing for reordering rather than measuring a curve.

### A note on the pattern

Six proposals have now hit the same verdict: Candidates A, B and C in `NEW_MODELS.md`, and M2, M3 and the group-lasso idea here.
In every case the *mechanism* was already published and the **multi-fidelity composition was what survived**.

At six for six, that is not a run of bad luck — it is information about where the contribution actually lies.
The mechanisms in this space are well covered by large, well-resourced groups; what is not covered is how they behave under scarce-HF transfer across 17 benchmark datasets.
The project should stop treating "mechanism is prior art" as a disappointing result and start treating the MF composition as the thesis, with published mechanisms as instruments to be cited and used rather than reinvented.
That reframing is also what makes iFNO an *asset* in §2.4 rather than a setback.

## 7. Open questions

1. Env-var knob vs. one-family-per-sweep-point (§5) — needs a decision before any sweep is built.
2. Does the determinism fix belong here or in `MODEL_TWEAKS.md`? It is a cross-family correctness issue, but these ablations are what make it urgent.
3. Should D1 run on all 17 datasets or only the smoke pair? It is cheap enough for all 17, and per-dataset `k*` across the full suite is more useful than two points.
4. M5's B/C confound (§3.1) — confirm the same-architecture framing before building, or accept a weaker conclusion.
