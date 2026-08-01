# Iteration 4 — REFUTATION pass on direction (i): "has the fitted LSI/Wiener stage been done?"

## Search rationale

Per §3.3 the goal of this turn is to REFUTE novelty for the direction the brainstormer is most likely to
propose: **direction (i)** — promote `k-NN average of the train LF pool at calib-selected k* -> one closed-form
LSI (Fourier-diagonal) Wiener filter fitted on the fit fold` to a first-class SCORED panel arm. Three angles of
attack: the object by its signal-processing name; the object by its effect ("amplify the attenuated high
wavenumbers post hoc"); the object by its stage-1 partner ("retrieval of nearest training simulations plus a
learned/fitted correction").

## Search terms used

1. `linear shift-invariant Wiener filter fitted on training pairs corrects emulator field prediction multi-fidelity spectral transfer`
2. `spectral bias post-hoc correction fitted linear operator amplify attenuated high wavenumbers emulator climate model output`
3. `retrieval of nearest training simulations plus learned correction surrogate parametric PDE analog method`

## Findings

### Term 1 — the object by name

**No usable results.** The search engine explicitly reported: *"The search results do not contain any
information specifically about a 'linear shift-invariant Wiener filter fitted on training pairs that corrects
emulator field prediction multi-fidelity spectral transfer.'"* Returned instead: generic Wiener-filter tutorials
(https://www.salimwireless.com/2025/09/wiener-filter.html, https://fiveable.me/advanced-signal-processing/unit-4/wiener-filtering/study-guide/3vYp5KdCY6d8FzSQ,
https://www.researchgate.net/publication/8355680_Wiener_filter_estimation_of_transfer_functions — RG 403),
and the **cosmology multi-fidelity power-spectrum emulator line**: MF-Box https://arxiv.org/pdf/2306.03144,
Lyman-alpha MF emulator https://arxiv.org/pdf/2207.06445, PRIYA https://arxiv.org/pdf/2306.05471.
Note the cosmology line is the closest genuine relative found in this loop: those emulators are
multi-fidelity **in wavenumber space** (LF/HF simulation pairs, per-k correction), but the target is a 1-D
summary statistic P(k), not a 2-D field, and the correction is a GP over k, not an LSI filter applied to a
retrieval intermediate. Also returned: correlation-based MF neural emulators https://arxiv.org/html/2512.02868
(already indexed in-repo as [LF-13] in `docs/reports/MF_Leaderboard_Beaters_2026_Report.md`).

### Term 2 — the object by its effect

**FETCHED via the arXiv API (title query) this loop** — "Mitigating Spectral Bias in Neural Operators via
High-Frequency Scaling for Physical Systems" http://arxiv.org/abs/2503.13695: *"we introduce a new approach
named high-frequency scaling (HFS) to mitigate spectral bias in convolutional-based neural operators... Unlike
Fourier-based techniques, HFS is directly applied to the latent space, thus eliminating the computational cost
associated with the Fourier transform."*
Reading: the nearest published relative of "scale up the attenuated bands", and it is explicitly **latent-space,
inside the network, trained** — not a closed-form transfer fitted on output pairs. It does not preempt
direction (i)'s object; it does preempt any claim that "amplifying attenuated high-frequency content in a
surrogate" is a new idea.

**FETCHED** — "Spectral bias in physics-informed and operator learning: Analysis and mitigation guidelines"
https://arxiv.org/abs/2602.19265: *"predictions exhibit systematic high-frequency attenuation... we provide a
systematic investigation of spectral bias in physics-informed and operator learning frameworks... we quantify
spectral bias through frequency-resolved error metrics, Barron-norm diagnostics, and higher-order statistical
moments"*, concluding spectral bias is *"not simply representational but fundamentally dynamical"* (optimizer-
dependent). Establishes the diagnostic vocabulary; contains no post-hoc fitted filter.

Other returned (snippet-level, not fetched): FreqNO-DPS https://arxiv.org/html/2606.03936 (batch-2, verified
there); diffusion-based downscaling of a climate emulator https://arxiv.org/html/2602.13416; regional ocean
emulators https://arxiv.org/pdf/2501.05058; ocean wave spectrum bias correction through energy conservation
https://os.copernicus.org/articles/21/767/2025/; "Learning bias corrections for climate models using deep
neural operators" https://arxiv.org/pdf/2302.03173; hybrid operator-diffusion MHD https://arxiv.org/pdf/2507.02106
(batch-2). The climate/ocean line does post-process emulator output for bias, but with learned or
energy-conservation constructions, not a least-squares LSI transfer between fidelities.

### Term 3 — retrieval intermediate + correction

**No usable results for the composition.** Returns repeat PhysicsCorrect https://arxiv.org/abs/2507.02227
(iteration 1) and unrelated surrogate-training work: unitary neural operators for CG solvers
https://arxiv.org/pdf/2508.02681; multiscale neural operator https://arxiv.org/pdf/2207.11417; Learning Where
to Simulate https://arxiv.org/abs/2606.09949 (batch-2); HyPER https://arxiv.org/pdf/2503.10048; latent
model-correction + UQ for PDEs https://arxiv.org/html/2603.24948v1.
Reading: "retrieve the nearest training solves, average them, then fit one filter" has no PDE-surrogate
literature under any of the three vocabularies tried across iterations 2 and 4 (the closest is the analogue
downscaling family from iteration 2, which resamples rather than filters).

## Interpretation

Three refutation-directed terms failed to find the composition, while each ingredient has a clear published
relative (LS-MFS/projection-based MF linear regression for closed-form MF correction; HFS and FreqNO-DPS for
band-wise amplification of attenuated content; analogue downscaling for the k-NN intermediate; Operator
Boosting for the shrinkage-gated residual stage). That pattern is the classic
`preempted-but-MF-composition-open` shape, not `novel` — and it means the brainstormer's claimable content
for direction (i) is the *measured attribution* (a zero-gradient stage carrying 33-100 % of a trained stack's
out-of-fold gain on a copy-LF-skill panel), never the filter.
