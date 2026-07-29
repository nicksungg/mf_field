# iteration_1 — s7_loss / batch 1

## Search rationale

Open question (a): what published objectives beyond plain L2 exist for neural
PDE surrogates, and what is the evidence on sharp/discontinuous fields? I split
this into the three families the task names: derivative-domain (Sobolev/H1),
frequency-domain (spectral / band-weighted), and the relative-vs-absolute
normalization axis (which is F19's axis and the one the s2-B1 amplitude finding
points at). Starting broad because the stream is new and has no prior batch.

## Search terms used

1. `Sobolev H1 loss training neural operator PDE surrogate sharp discontinuous fields`
2. `frequency-weighted spectral loss training Fourier neural operator high frequency band`
3. `loss function comparison neural PDE surrogate relative L2 vs MSE normalization ablation`

## Findings

### Term 1 — Sobolev / H1 losses on sharp fields

- **Cho, Ryu, Hwang (2024), "Sobolev Training for Operator Learning"** —
  https://arxiv.org/abs/2402.09084 (fetched abs page; the PDF fetch returned
  unparsable binary). Confirmed: integrating derivative information into the
  operator-learning loss, plus a framework to approximate derivatives on
  irregular meshes; effectiveness argued experimentally and theoretically. The
  abs page does NOT give benchmarks or quantitative gains, and says nothing
  about discontinuous fields or few-sample/multi-fidelity regimes. **Verdict
  input: Sobolev training for operator learning is unambiguously published.**
- **Dang, Schmidt, Hesser (2026), "Smooth Piecewise Cutting for Neural Operator
  to Handle Discontinuities and Sharp Transitions" (Cut-DeepONet)** —
  https://arxiv.org/html/2605.19823 (fetched). Two-stage: a "Cutting Net"
  predicts discontinuity locations, then the problem is lifted to a space where
  the discontinuity is a boundary. Two loss-relevant statements, both directly
  useful to s7: (i) they train with **L1 rather than L2** because L2
  underestimates the value of true discontinuities; (ii) explicit
  double-counting argument — "Cut-DeepONet generates a true discontinuity
  parallel to the ground truth, the error is evaluated on both sides of the
  jump, effectively doubling the contribution". They also add a localized
  "Dis loss" metric near discontinuities and admit it is imperfect.
- Search-page context (not fetched, recorded as leads only): WHNO /
  Walsh-Hadamard operators for discontinuous coefficients
  (https://arxiv.org/html/2511.07347); the general claim that neural operators
  have a smoothing bias that degrades when the ground truth has large Sobolev
  norms (shocks/discontinuities).

### Term 2 — frequency-weighted / spectral losses

- **Khodakarami, Oommen, Bora, Karniadakis (2025), "Mitigating Spectral Bias in
  Neural Operators via High-Frequency Scaling for Physical Systems"** —
  https://arxiv.org/abs/2503.13695 (fetched). Important for us: this is an
  **architecture change, not a loss change** — high-frequency scaling applied in
  the latent space of conv-based (UNet) operators, explicitly to avoid FFT cost.
  So it does not preempt a loss-only intervention.
- Leads seen on the results page but NOT fetched: DRIFT-Net (2509.24868) uses a
  frequency-weighted auxiliary Fourier-domain term with a radial weight ~ r^alpha
  (explicitly described as moving from an L_p toward a Sobolev-like metric);
  WHFL wavelet-domain high-frequency loss (WACV 2023); "Weighted FNO" mode
  rebalancing; Kong 2025 on reducing FNO frequency bias in 3D seismic
  wavefields. Recorded as leads for iteration 2.
- **Direction-critical note**: every one of these upweights HIGH frequencies.
  s2-B1's M3 says our excess error is in the LOWEST band on 5/5 datasets, so
  the published direction of travel is the *opposite* of what our evidence
  supports. That is a novelty opening and a design warning simultaneously.

### Term 3 — relative-vs-absolute normalization of the training loss

Weak: no single authoritative ablation paper surfaced. The results page
asserted (a) relative-L2 training has a normalization/regularization effect and
can roughly halve test error vs MSE training, and (b) nRMSE as a training loss
unifies scales across channels/PDEs (attributed to OmniArch, arXiv:2402.16014).
I fetched the OmniArch PDF (https://arxiv.org/pdf/2402.16014) and the extracted
text did NOT contain the loss-function methodology, so **I cannot cite either
claim** — treat as unverified. Also surfaced: "a model performs best when
trained and tested under the same loss criterion". Needs a targeted re-search
in iteration 2 with a citable source (PDEBench / PDEArena style benchmarks).

## Interpretation

Sobolev/H1 training and high-frequency-weighted spectral losses are both
published for operator learning, so neither is novel on its own; the
Cut-DeepONet paper independently documents the L2 double-counting penalty that
punishes correctly-sharp-but-displaced predictions (a fetched source for s7's
pre-registered risk). The unexploited asymmetry is directional: the published
frequency-loss literature exists to *add* high-frequency energy, while our
diagnostic says the champion already injects spurious high-k energy and fails
in the lowest band.
