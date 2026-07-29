# Iteration 1 — s2_beyond_copy / batch 1

## Search rationale

`summary_so_far.md` opens with four questions. Iteration 1 attacks the three that
must be answered before any diagnostic is designed:
(Q2) is "the fused model loses to its own LF input" a *named* published phenomenon?
(Q1) what is the citable methodology for decomposing field error per frequency band,
so the batch-1 diagnostic can be built on a published metric rather than an invented
one? and (Q3) does published work already guarantee "never worse than the input"
(identity/zero init), because if so the natural batch-2 mechanism is preempted and
the diagnostic must be designed to discriminate *variants* rather than to motivate
the idea from scratch. Terms chosen to be adversarial: each is phrased to find the
work that would REFUTE the project's framing.

## Search terms used

1. `multi-fidelity neural operator worse than low-fidelity baseline negative transfer surrogate underperforms its own input`
2. `per-wavenumber band error decomposition diagnostic neural operator PDE spectral error metric evaluation`
3. `identity initialization zero-initialized residual branch guarantee network no worse than input skip-to-output`

## Findings

### Term 1 — MF surrogate worse than its LF input

Top results: plasma-edge neural-operator surrogates
(https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb); MF-FNO for geological
carbon storage (https://arxiv.org/pdf/2308.09113 — the MFFP baseline's namesake, Tang
et al.); MF scaling laws for CFD surrogates (https://arxiv.org/pdf/2511.01830); MF
wavelet NO (ScienceDirect S0266892024000948); pretrain-finetune NO for structural
dynamics (ScienceDirect S0141029625016098); MF residual neural processes
(https://arxiv.org/pdf/2402.18846).

- The search-engine synthesis surfaces *negative-transfer* results (MF transfer helps
  at small data / short rollouts, "effectiveness diminished with longer rollouts and
  larger dataset sizes, especially when applied to datasets with significantly
  different dynamics"; transfer to unseen variables "unsuccessful"). That is
  degradation of the *transfer benefit*, not the specific claim we need.
- **WebFetch https://arxiv.org/pdf/2511.01830 → no usable results.** The fetch
  returned PDF structure/metadata only; the model could not locate a results section
  with LF-baseline comparisons. Recorded as a dead end, not as evidence.
- Interim reading: no source in this turn reports a learned MF surrogate scoring
  *worse than copying its own low-fidelity input field*. The MF literature almost
  universally reports against a single-fidelity-HF baseline or against an
  HF-data-budget curve — the copy-LF reference is not a standard baseline. That is
  itself the finding, and it is why the stream's premise may be under-documented
  rather than novel-in-mechanism.

### Term 2 — per-wavenumber diagnostic methodology

Top results: FreqNO-DPS "Correcting Neural Operator Spectral Bias via Diffusion
Posterior Sampling with Sparse Observations" (https://arxiv.org/html/2606.03936);
PDE-Refiner (NeurIPS 2023 proceedings PDF); "Frequency Bias and OOD Generalization in
Neural Operators under a Variable-Coefficient Wave Equation"
(https://arxiv.org/pdf/2605.12997); a practical NO introduction
(https://arxiv.org/html/2503.05598); reduced-order NO (https://arxiv.org/pdf/2409.05508).

- **FreqNO-DPS [cite: https://arxiv.org/html/2606.03936] (FETCHED).** Gives a
  ready-made, published diagnostic triple computed per Fourier mode k:
  (i) **frequency-banded relative FFT bias `rFFT`** over three bands
  (low/mid/high), where *negative values indicate systematic attenuation* — they
  measure −0.075 / −0.137 / −0.239 for low/mid/high, i.e. monotone worsening with k,
  "high-frequency content is systematically attenuated";
  (ii) a **transfer function `H(k)`** = expected ratio of surrogate to ground-truth
  amplitude at mode k, with the reported signature `H(k) ≈ 1` at low k and
  `|H(k)| << 1` in the spectral-bias regime;
  (iii) **mode-dependent residual variance `σ²_no(k)`** against the true power
  spectrum `P_u(k)`.
  They further assume the residual field is wide-sense stationary so **residual
  covariance is diagonal in the Fourier basis**, and *validate that assumption
  empirically with off-diagonal cross-spectral coherence diagnostics* (their
  Appendix B.6), explicitly offered as "a verification tool for applying the method
  to new surrogates."
- **Frequency Bias / OOD wave equation [cite: https://arxiv.org/pdf/2605.12997]
  (FETCHED).** Decomposes error per wavenumber and per band, specifically
  investigating whether error grows beyond the training truncation mode. Two
  reported pathologies: severe degradation on frequencies beyond the truncation
  mode, and — directly relevant — **"in certain frequency bands, particularly
  high-frequency regimes, the neural operator performs worse than trivial
  baselines (such as zero-padding or simple projection methods)."**
  (Caveat: this came from the fetch summary of the PDF, not from a table I read
  directly; treated as a qualitative claim, not a number.)

### Term 3 — identity / never-worse-than-input guarantees

Top results: ZerO Initialization (https://openreview.net/pdf?id=EYCm0AFjaSS);
Fixup (https://arxiv.org/pdf/1901.09321); IDInit (https://arxiv.org/html/2503.04626);
robust residual-block init (https://arxiv.org/pdf/2112.12299); BatchNorm biases
residual blocks toward identity (https://arxiv.org/pdf/2002.10444).

- **Fixup [cite: https://arxiv.org/pdf/1901.09321] (FETCHED).** Confirms verbatim the
  rule: zeroing the residual branch's weights means *"At initialization, the network
  computes the identity, since the residual branch contributes zero."* The
  learned-branch-starts-at-zero device is thoroughly published generic ML
  (Fixup 2019, ZerO ICLR'22, IDInit 2025; also the α-scalar-zero convention).
- Implication for this stream: **"initialize so the model starts by copying the LF
  field" is NOT a novel mechanism** — it is standard practice. Whatever batch 2
  proposes must therefore be about the *multi-fidelity composition* (what exactly is
  the identity path — up(LF)? which band of it? gated where?) and must be justified
  by the diagnostic, not by the init trick.

## Interpretation

The published diagnostic machinery this batch needs already exists and is citable:
per-band `rFFT` bias, the amplitude transfer function `H(k)`, and LF/HF
cross-spectral coherence [https://arxiv.org/html/2606.03936], plus the precedent of
reporting "worse than a trivial baseline" per band [https://arxiv.org/pdf/2605.12997].
Conversely, identity-at-init is generic published practice, so it cannot carry
novelty on its own. The remaining unknown after this turn is whether anyone has
published the *copy-the-input* reference specifically for multi-fidelity operator
learning, and whether the interface-localized (spatial, not spectral) half of the
diagnostic has an equally citable form — iteration 2.
