# Iteration 2 — subspace decomposition, negative transfer, penalty calibration

## Search rationale

Iteration 1 left three of B3's likely claims unpriced. (a) B2 part 7's
**three-channel taxonomy** (direction supply / row-space fit / level) is a
*decomposition of the transfer gain* — if such a decomposition is published as
a diagnostic, the taxonomy is preempted as vocabulary and only the PDE-field
measurement survives. (b) B2's M1/M5 report LF **hurting** (the null penalty;
the paired-LF arm) — the negative-transfer literature is where "LF can hurt"
would already be named. (c) part 7's optional leg is an **amplitude-corrected**
penalty (multiply the target law by the measured 0.5510075 gain), so the
scaling-factor / penalty-calibration MF literature is the refutation surface
for it.

## Search terms used

1. `decomposing transfer learning gain into row space and null space components auxiliary source data regression subspace diagnostic`
2. `negative transfer low-fidelity data hurts neural surrogate when multi-fidelity fails diagnostic taxonomy of what low-fidelity contributes`
3. `calibrating regularization strength toward biased surrogate target amplitude mismatch penalty low-fidelity estimated coefficients`

## Findings

### Term 1 — row-space / null-space decomposition of transfer gain
Search returns (no new fetch; the decisive item was already fetched in batch 2):
- https://arxiv.org/html/2510.15337 (Transfer Learning for Benign Overfitting
  in High-Dimensional Linear Regression) reappears as the top structural hit;
  engine synthesis: "an interpretable decomposition structure that involves
  orthogonal projections onto the design row space and the null space …
  transferring source information only into the null space". This is the
  citation batch 2's E2 row already carries.
- Adjacent instances of the same decomposition in other domains:
  https://arxiv.org/pdf/2506.04244 (PEFT adapters projected onto column/row
  spaces of source weights and their null spaces),
  https://arxiv.org/pdf/2507.02248 and https://arxiv.org/html/2503.00174v1
  (transfer for matrix completion).

Reading: the **two-way** split (row space vs null space) is published and
generic across domains. What iteration searches have NOT returned is a
**three-way** split adding a *level/amplitude* channel, nor any instance where
the shares are measured empirically for a PDE field surrogate.

### Term 2 — negative transfer with low-fidelity data
- **"On transfer learning of neural networks using bi-fidelity data"** —
  https://arxiv.org/abs/2002.04495 — FETCHED (abstract only; thin): they
  "focus on accuracy improvement achieved by transfer learning over standard
  training approaches"; abstract does not disclose HF-only baselines, sample
  counts, or negative results. Engine synthesis attached to this result is
  stronger and is recorded as a **search return, not a fetched quote**: "when
  transfer learning relies on lower-fidelity datasets, the resulting network
  may lead to less accurate surrogates compared to when the network is trained
  based only on large high-fidelity datasets".
- **"Towards Multi-Fidelity Scaling Laws of Neural Surrogates in CFD"** —
  https://arxiv.org/abs/2511.01830 — FETCHED (abstract): "We investigate this
  trade-off between data fidelity and cost in neural surrogates using low- and
  high-fidelity Reynolds-Averaged Navier-Stokes (RANS) simulations";
  "compute-performance scaling behavior"; "budget-dependent optimal fidelity
  mixes". Methodological detail absent from the abstract → follow-up fetch of
  the HTML deferred to iteration 3 (this is the single most dangerous
  preemption for a panel-scale value-of-LF accounting).
- Negative-transfer remedies named by the engine (search returns):
  https://www.sciencedirect.com/science/article/pii/S0021999124002018
  (multi-channel fusion), https://hal.science/hal-04602579/document (LOL-GP,
  per-location ReLU gate deciding whether to borrow from LF — already in batch
  2 iteration 5), Ada2MF-style gated residual learning
  (https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X),
  https://arxiv.org/pdf/2204.11138, https://arxiv.org/pdf/2410.12241.

Reading: "LF can hurt" is a **named, well-populated** phenomenon
(negative transfer) with a standard remedy family (gating / adaptive
weighting). B2's M1/M5 findings are instances, not discoveries.

### Term 3 — calibrating a penalty toward a biased LF-estimated target
- **"Bi-fidelity surrogate modeling via scaled correlation construction and
  penalty minimization"** —
  https://link.springer.com/article/10.1007/s00158-024-03887-8 —
  search return: a scale factor "integrated into the construction of the
  discrepancy function to represent variations between low-fidelity and
  high-fidelity samples", inside a penalty-minimization objective, motivated
  by limited data.
- Other returns are generic Tikhonov / bias-variance material
  (https://www.sciencedirect.com/science/article/abs/pii/S0888327022000668)
  and MF fusion with non-hierarchical LF
  (https://www.sciencedirect.com/science/article/abs/pii/S1270963824000610).

Reading: fitting a **scale factor between LF and HF** inside a penalized
objective is standard bi-fidelity practice; an "amplitude-corrected null
penalty" is that idea composed with the already-preempted null-space
regularization family (batch 2, E3c). No route to a novelty claim.

## Interpretation

Two of the three probes land on established literatures (subspace
decomposition of transfer gain; negative transfer; LF/HF scale calibration),
so B3 must not claim any of them as mechanism-level contributions. The
outstanding risk to the stream's one `novel` row is arXiv:2511.01830, whose
abstract promises budget-dependent fidelity-mix scaling laws — iteration 3
must read its body before the E5 verdict can be restated.
