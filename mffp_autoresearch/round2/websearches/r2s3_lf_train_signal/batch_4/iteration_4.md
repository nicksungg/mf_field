# Iteration 4 — dedicated refutation pass on directions (a) and (b)

## Search rationale

Turns 1–3 left (a) "is the gain channel LF-free recoverable?" and (b)
"budget-matched no-LF ensemble vs LF arm" alive only because they had been
searched from the *calibration* and *variance* vocabularies. This turn tries
to kill them from the **multi-fidelity-methodology** side: (1) has any MF
paper controlled its ±LF ablation for output scaling/normalization (which
would preempt (a)'s framing as an MF question)? (2) has anyone compared an
ensemble of single-fidelity models against an MF surrogate at equal cost
((b) exactly)? (3) has anyone factorized a PDE surrogate into
"predict the solution norm from parameters × predict the normalized field"
((a)'s mechanism in its most literal form)?

## Search terms used

1. `multi-fidelity benefit ablation controlled for output scaling normalization fair baseline single-fidelity properly normalized`
2. `ensemble of single-fidelity models outperforms multi-fidelity surrogate equal computational budget comparison`
3. `learned per-sample normalization predict solution norm from PDE parameters then predict normalized field operator learning`

## Findings

### Term 1 — MF ablations controlled for output scaling

- **"A general multi-fidelity metamodeling framework for models with various
  output correlation"** —
  https://link.springer.com/article/10.1007/s00158-023-03537-5 [search return].
  Engine synthesis: "A general multi-fidelity metamodeling framework called
  **output scaling multi-fidelity (OS-MF)** method has been proposed to better
  integrate information from multi-fidelity models with various correlation."
  Output scaling is thus a *named MF construct* — but it scales the **LF model
  toward the HF model**, i.e. it is a fusion device that consumes LF, not an
  LF-free recovery of the amplitude channel.
- **"Assessing the performance of correlation-based multi-fidelity neural
  emulators"** — https://arxiv.org/html/2512.02868v1 [search return]. Engine
  synthesis: "Test MSEs can be normalized using the squared ℓ₂ norm of each
  function over its corresponding input domain"; and MF vs "equivalent
  single-fidelity networks trained solely on high-fidelity data" shows
  "normalized MSE values consistently 1–4 orders of magnitude higher" for
  single-fidelity. Same genre as batch 3's P1 preemptors; still no arm in
  which the single-fidelity baseline is given an output-scale correction.
- **No retrieved MF ablation controls its single-fidelity baseline for output
  scale.** This is the negative result direction (a) needs.

### Term 2 — ensemble-of-single-fidelity vs MF at equal budget

- **"An ensemble-based approach for multi-fidelity emulation and adaptive
  sampling"** — https://arxiv.org/abs/2604.18045 **[curl-fetched: abstract;
  https://arxiv.org/html/2604.18045 body also fetched]**. Verbatim: "The base
  learners of the ensemble are **hierarchical kriging emulators that
  systematically incorporate information from lower-fidelity models** into HF
  predictions… Results show that our multi-fidelity emulator **outperforms
  single-model alternatives** in terms of accuracy and robustness."
  **Wrong direction for (b)**: the ensemble members are themselves
  LF-consuming; the comparison is ensemble-MF vs single-model-MF, not
  no-LF-ensemble vs LF-single. Body search for "fixed computational budget" /
  "equal budget" / "fair" returned **0 hits** — no budget-matching statement
  in that paper.
- **"Balancing Accuracy and Speed: A Multi-Fidelity Ensemble Kalman Filter
  with a Machine Learning Surrogate Model"** — https://arxiv.org/abs/2512.12276
  (also https://arxiv.org/html/2512.12276) [search return, not fetched]. The
  engine's sentence "the comparison needs to assume a **fixed computational
  budget** to be fair, since multi-fidelity methods can use information from
  extra surrogate runs" is an **engine synthesis whose source I did not
  confirm by fetch** — recorded as a search return only, not usable as a
  citation of record.
- **Turbomachinery MF comparison under extreme cost imbalance** —
  https://link.springer.com/article/10.1186/s40323-025-00316-3 [search return]:
  cost-imbalance-aware MF comparison exists in aerodynamic optimization; still
  MF-vs-MF, not ensemble-vs-LF.
- **No retrieved work prices a no-auxiliary-data ensemble against an
  LF-trained model at matched compute.**

### Term 3 — predict the norm, then the normalized field (**the decisive hit for (a)**)

- **"Discrete Solution Operator Learning for Geometry-Dependent PDEs"
  (DiSOL)** — https://arxiv.org/abs/2601.09143 **[curl-fetched: abstract;
  body via https://arxiv.org/html/2601.09143v1 and
  https://ar5iv.labs.arxiv.org/html/2601.09143]**. Methods §4.1, verbatim:
  "We define a **per-sample amplitude** u_lim (Supplementary Information D,
  e.g., u_lim = max_x |U_h(x)|) and the **dimensionless solution pattern**
  u_h := U_h / u_lim, so that max_x |u_h(x)| = 1. **All models (DiSOL and all
  baselines) are trained to predict the normalized pattern û_h. If an
  absolute-amplitude prediction is required, it can be reconstructed as
  Û_h = û_lim · û_h using an optional amplitude regressor** (Supplementary
  Sec. D)."
  Their arms are ≈0.13 M parameters each, "trained under the same
  optimizer/schedule and have comparable parameter counts", over
  geometry-dependent Poisson, advection-diffusion, linear elasticity and
  spatiotemporal heat conduction, ID and OOD.
  **Consequence**: the mechanism of direction (a) — factorize the field into
  a per-sample amplitude predicted by a small regressor × a normalized pattern
  — is **published, verbatim, in the PDE-operator-learning setting**. What
  DiSOL does *not* do: it uses the factorization to make its benchmark
  well-posed (it normalizes **every** arm and treats the amplitude regressor
  as optional post-processing), it has **no low-fidelity data anywhere**, and
  it never asks how much of any auxiliary-data benefit the amplitude regressor
  absorbs.
- Related normalization convention [search return, same engine synthesis]:
  "normalizing training examples by their **source norm** relative to a
  reference value (the median source norm over the training dataset)" — again
  a preprocessing convention, not a measurement.
- **Foundation-model scaling/transfer for SciML** —
  https://arxiv.org/pdf/2306.00258 [search return]: pretraining/transfer for
  PDE surrogates; the LF-pretrain genre again (§12.3 declared baseline).

## Interpretation

Direction (a)'s **mechanism is now preempted at the exact level of
description** (DiSOL's per-sample amplitude + optional amplitude regressor for
PDE operator learning, https://arxiv.org/abs/2601.09143), and generically twice
over from turn 2 (FiLM-as-hypernetwork scale; LCC/Tweedie de-shrinkage on a
small held-out split). What no retrieved work does is use that head as a
**substitution test for the value of low-fidelity training data** — every MF
ablation retrieved leaves its single-fidelity baseline un-scale-corrected, and
no one prices an LF-free variance/calibration alternative against an LF arm at
matched budget. Turn 5 spends its last calls confirming that gap has not been
closed under the "is the improvement real or an artifact of the baseline"
framing, then writes the verdict.
