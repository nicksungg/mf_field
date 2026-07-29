# Iteration 4 — Stream `s5_tuning`, Batch 1

## Search rationale

Iterations 1-3 converged on one unresolved design question that decides whether this
card can produce an interpretable result at all: **the 12 -> 32 bump is a 7.1x spectral
parameter increase** (summary_so_far.md), and the benchmark literature (iteration 1,
arXiv:2510.05995) compares operators at **capacity-aligned budgets**. So if cap 32 wins,
the honest reading is ambiguous between "the spectral bottleneck was real" and "the
champion was simply under-parameterized". Two probes, aimed at instruments that
*decouple mode count from parameter count*:

1. Tensorized / low-rank factorized FNO (TFNO, MG-TFNO) — the field's standard way to
   raise the mode budget without raising parameters, and its claimed regularization
   effect under scarce data (our N_hf=5 / ntrain=400 regime).
2. Whether anyone has run a **fixed-parameter-budget** width-vs-modes ablation, which
   would give the card a capacity-matched control arm.

Two terms this turn (under the 3 cap; no truncation — no third term was worth running
once these two were chosen).

## Search terms used
1. "tensorized Fourier neural operator TFNO Tucker low-rank factorization more modes fewer parameters"
2. "FNO ablation number of Fourier modes matched parameter count capacity controlled comparison width"

## Findings

### Term 1: "tensorized Fourier neural operator TFNO Tucker low-rank factorization more modes fewer parameters"

- [Kossaifi, Kovachki, Azizzadenesheli, Anandkumar 2023] **"Multi-Grid Tensorized
  Fourier Neural Operator for High-Resolution PDEs" (MG-TFNO)**. URL:
  https://arxiv.org/html/2310.00120 (fetched below)
- [neuraloperator docs] `neuralop.models.TFNO` — TFNO is "an FNO with Tucker
  factorization enabled by default"; default `rank=0.1` gives roughly **10% of the
  parameters of a dense FNO**, contracting directly with the decomposition factors.
  Reported: superior performance at low compression (up to 200x) and very little
  degradation past 450x. URL:
  https://neuraloperator.github.io/dev/modules/generated/neuralop.models.TFNO.html
- [2025] "Tensor-GaLore: Memory-Efficient Training via Gradient Tensor Decomposition" —
  same low-rank-in-Fourier-space family, applied to gradients. URL:
  https://arxiv.org/html/2501.02379v1

**WebFetch (arXiv:2310.00120, MG-TFNO).** Confirms both halves of the hypothesis.
Parameters are represented in a high-order latent subspace of the Fourier domain via a
**global Tucker factorization**, so cost grows linearly rather than exponentially with
problem size: **>100x parameter compression at equal-or-better accuracy vs full FNO**,
**400x** on turbulent Navier-Stokes still beating baseline FNO, and "less than half the
error with over 150x compression". Crucially for scarce-HF: their Fig. 8 shows **TFNO
reaching FNO's test error using only 50% of the training samples**, with a visibly
smaller train-test gap — the low-rank constraint is described as "low-rank
regularization on the model", "invaluable in the PDE setting where very few training
samples are typically available".

### Term 2: "FNO ablation number of Fourier modes matched parameter count capacity controlled comparison width"

- Search snippet reports a **fixed-parameter-budget width-vs-modes study**: "parameter
  count scales as O(d_c^2 K^2) for 2D problems, [so] the relationship **d_c K = C** is
  used as a proxy to control model sizes", with widths tested at 16 / 32 / 48 / 64.
  **Attribution UNVERIFIED**: the snippet is an aggregation across the result set and I
  could not confirm which paper it belongs to — the WebFetch of the most likely
  candidate, [Mohan et al.-style] "Fourier neural operators for spatiotemporal dynamics
  in two-dimensional turbulence" (https://arxiv.org/pdf/2409.14660), returned
  undecodable binary and did **not** contain evidence of the study. Recorded as an
  unattributed field convention, **not citable as a paper claim**.
- [2606.08448] "Multiscale Fourier Neural Operator for Inverse Wave Scattering in Highly
  Oscillatory Media" — reports setting modes to the **maximum allowable value (50 for a
  101x101 training resolution, the Nyquist limit) specifically to rule out insufficient
  spectral resolution as the cause of poor performance**. This is the exact control this
  card needs, used as a negative control in published work. URL:
  https://arxiv.org/pdf/2606.08448
- Cross-check re-hit: "An ablation study on FNO varying the number of active Fourier
  modes reveals a clear trade-off between model capacity and implicit regularization" —
  consistent with iteration 1's plateau/divergence results.
- [AFNO, Guibas et al.] "Adaptive Fourier Neural Operators" — soft-thresholding /
  shrinkage sparsification of modes (already flagged as crowded prior art in
  `docs/proposals/MODELS_TO_TRY.md`). URL: https://openreview.net/pdf?id=EXHG-A3jlM

**Arithmetic this implies for the champion (mine, from the code, not from a paper).**
`mf_fno_transfer_film` spectral weights are two `(C, C, mh, mw)` complex tensors per
block, so params ∝ C^2·mh·mw and the `d_c·K = const` proxy holds. Current point:
C=64, K=12 → d_c·K = 768. The **capacity-matched** cap-32 point is therefore
**C=24, K=32** (24·32 = 768); the naive cap-32 point (C=64, K=32) is 7.1x larger.

## Interpretation (1-3 sentences)

There is a clean, in-scope way to make this card interpretable rather than confounded:
run cap 32 both at the champion's width (capacity-inflated) and at the capacity-matched
width C=24, so that "modes" and "capacity" are separable — and both are pure
hyperparameter knobs, which keeps the card inside program.md §12.5's no-architecture
constraint. The *published* safe way to buy modes — Tucker/low-rank factorization of the
spectral weights, which MG-TFNO shows also halves the data requirement — is an
architectural change and therefore belongs to a different stream, but it is the natural
follow-up if the mode bump wins only at inflated capacity.

## ENOUGH

**Decision: ENOUGH — stop the loop at 4 iterations (cap not reached).** The field
context now covers the direction (does raising modes help), the mechanism for why it may
not (Fourier parameterization bias, aliasing fold-back), the fairness confounds (optimal
LR shifts with K; parameter-count inflation) with a concrete capacity-matched control,
the panel-specific comparator (E-UNO's per-level mode schedule on our own Cahn-Hilliard
source paper), and a verified prior-art verdict (iFNO) — which is everything the
brainstormer needs to write a falsifiable slot; a fifth turn would add breadth, not
decisions.
