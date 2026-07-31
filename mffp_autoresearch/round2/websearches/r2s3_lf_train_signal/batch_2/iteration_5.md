# Iteration 5 — refutation turn 3 + PRIOR-ART VERDICT (iteration cap 5 HIT)

**Cap note**: this is iteration 5 of a maximum 5. The loop stops here whether or
not further threads remain (two remain and are named at the end).

## Search rationale

Iteration 4 left exactly one direction with claimable substance: E1's mandatory
guard — a **training-free, per-dataset decision** about whether to use the LF
channel at all. This turn attacks it directly from two angles (the classical
"is the LF model correlated enough?" criterion, and the "LF data is harmful,
detect it" framing), then records the verdict for every candidate direction.
Only 2 terms were used; the third slot was not needed once term 2 returned a
direct hit.

## Search terms used

1. `criterion to decide whether multi-fidelity modeling will help correlation between low and high fidelity a priori indicator when not to use low-fidelity data`
2. `per-dataset automatic switch fallback single-fidelity model when low-fidelity data harmful multi-fidelity surrogate safeguard test`

## Findings

### Term 1 — the classical decision criterion

Returns: "Review of multi-fidelity models" [https://arxiv.org/html/1609.07196v5,
https://www.aimsciences.org/article/doi/10.3934/acse.2023015]; PRICAI 2025 LF
selection [https://link.springer.com/chapter/10.1007/978-981-95-7072-0_32];
non-hierarchical LF fusion [S1474034621001828]. Engine synthesis: success "depends
on strong correlation between fidelities"; "when correlation is weak or
qualitatively different behavior occurs (e.g. missing modes), multi-fidelity
corrections may be insufficient"; cost-ratio (LFA/HFA vs MFO/HFO) analyses decide
whether MF pays at all.
→ "Check LF–HF correlation before trusting a multi-fidelity model" is textbook
review material. A gate is expected practice, not a contribution.

### Term 2 — harmful LF sources, detected from available data (DIRECT HIT)

**Fetched — arXiv:2403.08118 "Characterising harmful data sources when
constructing multi-fidelity surrogate models"** (also Artificial Intelligence,
S0004370224001437) [cite: https://arxiv.org/abs/2403.08118]: identifies harmful
LF sources "analyzing only the limited data available to train a surrogate
model", without extra HF evaluations; frames it as **algorithm selection** with
**Instance Space Analysis**, giving "an intuitive visualisation of when a
low-fidelity source should be used"; uses benchmark-filtering for a bias-free
assessment; targets industrial design problems.
→ **E1's guard is preempted**: deciding per-instance whether an LF source helps,
using only the data at hand, is a named published methodology.

Other returns: local transfer learning with ReLU-gated latent GPs that learns
**per location** whether to borrow from LF or rely on HF alone (negative-transfer
control) [search return, HAL: https://hal.science/hal-04602579/document — not
fetched]; a survey/benchmark of MF surrogates for simulators with **functional
(field) outputs** with a unified framework and benchmark
[https://arxiv.org/pdf/2408.17075 — **FETCH FAILED**, binary PDF; title/venue
recorded only, nothing claimed from its text]. The existence of that survey is
itself a warning that MF-for-field-outputs is a consolidated area.

## PRIOR-ART VERDICT (§3.3)

Candidate directions are B1 part 7's `next_direction` items, split so each is
separately falsifiable.

**E1 — ship the linear/affine LF channel `c·A(cond) + R(cond)` as a family
(A fitted on the best LF rung, c and residual ridge on the 5 HF rows).**
**VERDICT: preempted.**
- arXiv:1705.02956 / AIAA J. 10.2514/1.J057299 — LR-MFS: LF prediction as a
  basis function plus a polynomial discrepancy, **both coefficient sets fitted
  in a single least-squares**, motivated by "only a few high-fidelity
  simulations ... are affordable" (iteration 1, fetched).
- arXiv:2508.08517 (AIAA 2023-0916; ML for Comp. Sci. & Eng. 2025,
  DOI 10.1007/s44379-025-00049-5) — projection-based MF **linear** regression
  for **data-scarce** applications with **POD-projected high-dimensional field
  outputs**; three variants (additive KO, direct data augmentation,
  regression-mapping augmentation) (iteration 4, fetched).
Nearest-neighbour gap: nothing more than the specific rung-selection-by-in-rung-
LOO detail and the exact panel. **No novelty claim is available for E1's
estimator.** It remains a legitimate, strong *baseline* to ship — but it must be
introduced as an implementation of published MF linear regression, cited.

**E2 — LF rows at conditions disjoint from the HF rows supply the null direction
of the HF design matrix (rank completion at N_hf = 5).**
**VERDICT: preempted-but-MF-composition-open.**
- arXiv:2510.15337 — retain-plus-transfer: fine-tuning "retains target-learned
  signal in the span of n_0 target samples ... while transferring source
  information only into the null space S_0^perp where the target samples provide
  no information" (iteration 1, fetched). The mechanism sentence is published.
- arXiv:2508.08517 — "LF data can be evaluated at parameter values where no HF
  data exists"; compares to **HF-only** regression and finds LF can help or
  degrade depending on LF quality (iteration 4, fetched).
- arXiv:2511.20183 — non-nested (LF/HF at different parameter values) MF GP
  regression; classical KO/recursive formulations assume nested designs
  (iteration 1, fetched).
What remains open: the *field-valued, neural, certified-floor* instance — the
null direction of a **condition design matrix** filled by **coarse consistent
PDE solves**, priced in skill units against a **3-seed certified
min_claimable_effect**, on a panel where five of six datasets have
**condition-aligned (nested) rungs** so LF can only carry spectral truncation.
**This supersedes batch 1's `novel` verdict for D3** (batch 1 searched
PDE/neural-operator vocabulary; the preempting work is AIAA/UQ vocabulary).

**E3a — per-rung (resolution-dependent) output scaler.**
**VERDICT: novel, but weak — and in tension with the retrieved literature.**
Nearest neighbour: arXiv:2310.00120 (MG-TFNO) requires normalization to be
global/function-wise and **not spatially dependent**, to preserve discretization
invariance (iteration 2, fetched). A per-resolution scale is exactly the kind of
resolution dependence that literature avoids. Defensible only as a
dataset-specific fix for `ifc_poisson`'s h² amplitude convention, and it should
be presented as a bug fix, never as a contribution.

**E3b — mode clipping pinned at the HF Nyquist for every rung.**
**VERDICT: preempted.** arXiv:2310.00120 keeps "the first α modes in each
direction, where α is independent of the discretization" — identical truncation
at every resolution is the standard convention (iteration 2, fetched). B1's
grid-dependent clipping was the deviation; restoring it is a bug fix.

**E3c — explicit null-direction gain calibration / min-norm penalty on the
component the HF rows cannot constrain.**
**VERDICT: preempted-but-MF-composition-open.**
- arXiv:2510.01608 (NPN) — regularizes the **measurement operator's** null space
  because "conventional methods leave the null-space uncontrolled" (iteration 3,
  fetched); deep null space learning
  [https://iopscience.iop.org/article/10.1088/1361-6420/aaf14a] and Safe
  Regularization in the null space of batch activations
  [https://link.springer.com/chapter/10.1007/978-3-030-61616-8_18] (iteration 3,
  search-returned).
- Theory side: min-norm implicit bias in underdetermined regression
  (arXiv:2006.07356, iteration 2, fetched — the *extrapolation* sentence there is
  fetch prose, not a verbatim quote, and is used only as a lead);
  arXiv:2209.15265 (search-returned synthesis: below an n/d threshold an
  overparameterized network fails to uniquely recover a linear ground truth).
Open: the null space of a **low-dimensional parametric design matrix** (5 rows,
6 unknowns) inside a **neural field operator**, and the empirical observation
that a FiLM-FNO puts 27.7% of its implicit law energy there **anti-aligned**
(cos −0.99) — the opposite of the min-norm prediction. That *measurement* is the
open part; the *fix* is not.

**E4 — training-free per-dataset gate (affinity test → LF channel vs no-LF
control).**
**VERDICT: preempted.** arXiv:2403.08118 characterises harmful LF sources from
"only the limited data available to train a surrogate model", as an algorithm-
selection / Instance Space Analysis problem yielding "when a low-fidelity source
should be used" (this iteration, fetched); MF reviews make LF–HF correlation the
standard admissibility check (term 1). A ReLU-gated latent-GP method even learns
per-location LF-vs-HF-only borrowing [https://hal.science/hal-04602579/document,
search-returned]. Using an **affine-LOO-residual structural test on the
condition→field map** as the gate feature is an unretrieved *feature choice*
inside a preempted framework — not a claim.

**E5 — the measurement itself: matched, budget-equal with/without-LF-training
contrast for a NEURAL condition→field surrogate at N_hf ≈ 5 (and N = 400 with
condition-aligned rungs), priced against a certified 3-seed noise floor, per
dataset.**
**VERDICT: novel (nearest neighbours named).** Nearest: arXiv:2508.08517's
HF-only-vs-MF comparison (linear POD regression, scalar/POD-coefficient error,
no seed-noise floor, no neural arm) and arXiv:2403.08118 (harmful-source
characterisation, algorithm-selection framing, not a matched-architecture
training ablation). Three independent search framings across batches 1–2 have
failed to retrieve a matched with/without-LF accounting for neural field
surrogates at this sample count. **This is where the stream's remaining
publishable content sits**, and it is precisely round-2 success criterion 1.

## Threads left unexplored at the cap

1. The functional-output MF survey/benchmark arXiv:2408.17075 (fetch failed) —
   likely contains the closest baseline suite for E1/E5; a batch-3 loop should
   retrieve the HTML/journal version.
2. Whether the **condition-aligned nested-ladder** case (LF adds only spectral
   truncation, no coverage) has any MF-literature treatment at all — two turns
   touched it obliquely; it was never the primary term.
