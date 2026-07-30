# Iteration 2 — `s7_loss` batch 2

## Search rationale

Iteration 1 left two of the five open questions unresolved: (3) whether a
**jointly trained loss-level gain/amplitude term** is preempted (distinct from
s1-B3's post-hoc ridge head), and (5) whether **loss-level residual/LF-referenced
supervision** is separable in the literature from residual *prediction*
(s2's mechanism). This turn attacks both, plus a generic "two-term shape +
magnitude objective" probe to find the construction under any name.

## Search terms used

1. `learned output scaling head amplitude calibration jointly trained neural operator surrogate predict magnitude and normalized shape separately`
2. `two-term loss normalized shape term plus magnitude term deep learning regression scale decomposition training objective`
3. `multi-fidelity training loss weighted by low-fidelity residual magnitude supervise correction term objective neural network`

## Findings

### Term 1 — jointly trained amplitude/scale heads for PDE surrogates

Top results: `https://arxiv.org/html/2602.11090` (Direct Learning of
Calibration-Aware Uncertainty for Neural PDE Surrogates),
`https://arxiv.org/html/2412.12069` (Accurate Surrogate Amplitudes with
Calibrated Uncertainties), `https://arxiv.org/pdf/2512.11036` (Amplitude
Surrogates for Multi-Jet Processes), `https://arxiv.org/html/2502.09692v3`
(AB-UPT), `https://arxiv.org/html/2605.00330`.

**The word "amplitude" collides.** Every hit is either (a) *uncertainty*
calibration — learning noise/uncertainty parameters jointly with the mean
prediction at an output head (2602.11090, 2412.12069, 2512.11036) — or (b)
particle-physics scattering "amplitudes", a scalar target, not a field gain.
This reproduces batch 1's dead end ("amplitude calibration → returns
conformal-prediction/UQ 'calibration', a different sense of the word"). **No
result trains a per-sample output *gain* jointly with a normalized-shape
objective for a PDE field.**

### Term 2 — two-term shape + magnitude objectives

No usable results for the specific construction. Returned the same
`https://www.emergentmind.com/topics/normalized-loss-function` page,
`https://arxiv.org/pdf/2006.13554` (Normalized Loss Functions for Deep Learning
with Noisy Labels — classification, not regression), and a loss survey
`https://arxiv.org/html/2307.02694v3`.

**Fetched**: `https://arxiv.org/html/2307.02694v3` ("Loss Functions and Metrics
in Deep Learning"). Directly useful as a *negative* result: the survey does NOT
define relative-error / relative-MSE / MAPE-style losses with a denominator
floor, lists MAPE/SMAPE only in a metrics table, acknowledges only that "the
value of MSE depends on the scale of the target variable, making it difficult
to compare the performance of models across different problems or target
variable scales", recommends "scale-invariant metrics such as MAPE or NMAE"
without formulas, and **does not discuss instability for small-magnitude
targets**. It contains no Eigen-style scale-invariant loss. So the field's own
survey treats scale-normalized objectives as a metrics footnote, not a design
axis — consistent with iteration 1's reading that flooring is an idiom, not a
contribution, and that the failure mode is undocumented.

### Term 3 — loss-level LF-referenced / residual supervision in MF

Top results: `https://arxiv.org/abs/2310.03572` and its BIT version
`https://link.springer.com/article/10.1007/s10543-025-01058-9` (Residual
Multi-Fidelity Neural Network Computing), `https://arxiv.org/pdf/2402.18846`
(Multi-Fidelity Residual Neural Processes), `https://onlinelibrary.wiley.com/doi/10.1111/mice.13312`
(Multifidelity GNNs for mesh-based PDE surrogates),
`https://arxiv.org/html/2602.01176` (MF-PINNs with adaptive residual learning).

Every hit puts the LF field in as an **input / output parameterization**
(architecture), matching batch 1's C-LFANCHOR verdict for 2310.03572. The only
*loss-side* MF construction the search surfaced is **scalar per-fidelity loss
weights** ("setting the highest fidelity weight to 2 and lower fidelities to 1")
— i.e. weighting by fidelity level, never by the **per-sample copy-LF residual
magnitude**. That is the same conclusion batch 1 reached from
`https://arxiv.org/abs/2204.06684`, now with a second independent pass.
No fetch attempted this turn (the abstracts as returned already separate the
two mechanisms; a targeted refutation fetch is scheduled for §3.3).

## In-repo check made this turn (not a web finding)

Reading `worktrees/s7_loss/B1/models_r1/mf_fno_transfer_film_s7loss/s7_losses.py`
resolves open question 1 *without* the literature: `MFFP_S7_LOSS=rel` is
`mean_i rel_i²` and its denominator is **already floored** —
`b = clamp(sqrt(sum(y²)), min=1e-4)` (`NORM_FLOOR = 1e-4`), an idiom vendored
from `factory_mffp/models/transolver_residual/smoke_eval.py:68`. So "add a
denominator floor" is **already built and shipped** in the B1 family; it is not
a proposable direction, and — because the floor is absolute (1e-4) rather than
spread-relative — it did **not** prevent the allen_cahn collapse. Any B2 arm
claiming a floor must state which samples the floor actually binds on.

## Interpretation

The gain/amplitude direction survives a second refutation pass at the
*mechanism* level for PDE fields (the literature's "amplitude calibration" is
uncertainty calibration), and the MF literature keeps LF on the architecture
side, leaving **per-sample loss weighting by the copy-LF residual** unoccupied
so far. The floored-relative-loss direction is dead as a proposal — it is
already in the codebase.
