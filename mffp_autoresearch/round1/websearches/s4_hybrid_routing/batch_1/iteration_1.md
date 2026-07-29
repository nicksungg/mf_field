# Iteration 1 — `s4_hybrid_routing` batch 1

## Search rationale

program.md §12.4 says the base hybrids are published and *"the surviving novelty
is the MF composition (routing, per-band/per-region gating, which fidelity feeds
which expert)"*. So iteration 1 maps the field along exactly the three axes the
stream would propose on: (a) MoE/routing over neural-operator experts in general,
(b) per-frequency-band routing between a spectral and an attention operator
(the §12.4 "per-band gating" phrase + P4 band-split from
`docs/reports/MF_Sharp_HighFreq_Report.md`), (c) whether anyone has done this
routing in a **multi-fidelity** setting (the claimed surviving novelty).

## Search terms used

1. `mixture of experts neural operator PDE routing gating Fourier neural operator`
2. `frequency band routing spectral operator attention operator hybrid PDE surrogate`
3. `multi-fidelity mixture of experts operator learning fidelity-aware routing gating low-fidelity high-fidelity`

## Findings

### Term 1 — MoE over neural operators

Top results:
- MoE-POT, "Mixture-of-Experts Operator Transformer for Large-Scale PDE
  Pre-Training" — https://arxiv.org/abs/2510.25803 (NeurIPS 2025 poster
  https://neurips.cc/virtual/2025/loc/san-diego/poster/118221)
- NESTOR, "A Nested MOE-based Neural Operator for Large-Scale PDE Pre-Training" —
  https://arxiv.org/html/2602.22059
- "A Greedy PDE Router for Blending Neural Operators and Classical Methods" —
  https://arxiv.org/html/2509.24814
- "Mixture of neural operator experts for learning boundary conditions and model
  selection" — https://arxiv.org/html/2502.04562
- "Eradicating Negative Transfer in Multi-Physics Foundation Models via Sparse
  Mixture-of-Experts Routing" (Shodh-MoE) — https://arxiv.org/pdf/2605.15179

**Fetched** MoE-POT abstract page (https://arxiv.org/abs/2510.25803):
sparse-activated operator transformer; 16 routed + 2 shared experts, 4 routed
experts activated per layer by a **layer-wise router-gating network**; each block
pairs a Fourier layer (AFNO token mixer) with an MoE layer; 90M activated params
beat 120M dense models by up to 40% zero-shot error. Interpretability analysis
shows **dataset/equation type is recoverable from the router decisions**, i.e.
the routing specializes by PDE family, not by frequency band or fidelity. The
abstract page gives no indication of multi-fidelity input; that question needs
the full text (flagged for iteration 2 if it becomes load-bearing).

So: **MoE routing over operator experts inside a Fourier-layer backbone is
published and mainstream as of NeurIPS 2025.** A card proposing "MoE over
operators" as a bare mechanism is dead on arrival.

### Term 2 — per-band spectral routing between spectral and attention operators

Top results:
- SPAMoE, "Spectrum-Aware Hybrid Operator Framework for Full-Waveform Inversion"
  — https://arxiv.org/html/2604.07421
- U-HNO, "A U-shaped Hybrid Neural Operator with Sparse-Point Adaptive Routing
  for Non-stationary PDE Dynamics" — https://arxiv.org/pdf/2605.12965
- "Hybrid operator learning of wave scattering maps in high-contrast media" —
  https://arxiv.org/html/2602.11197 (FNO for the smooth background field + a
  ViT-based high-contrast scattering corrector — structurally the same
  "spectral base + attention corrector" as `fno_transolver_seq`)
- SAOT, "Enhanced Locality-Aware Spectral Transformer for Solving PDEs" —
  https://arxiv.org/html/2511.18777
- "A Physics-Informed Fourier-Wavelet Transformer for Multiscale CFD Surrogate
  Modeling" — https://arxiv.org/pdf/2606.24696

**Fetched** SPAMoE (https://arxiv.org/html/2604.07421): a
**Spectral-Preserving DINO encoder + Adaptive Spectral Mixture-of-Experts** over
three complementary operator experts — FNO (low-frequency global background),
MNO (mid-frequency multiscale), LNO (high-frequency faults / sharp interfaces).
Routing: concentric **soft frequency-band decomposition** (Gaussian masks, K
overlapping bands), a learnable per-expert **frequency-preference parameter**, and
a **spectral-energy attention router** (self-attention over the power spectrum)
with Top-k=2 experts per sample. Explicitly: **no multi-fidelity / coarse-solve
component** — single forward pass, single input fidelity.

**Fetched** U-HNO (https://arxiv.org/pdf/2605.12965): U-shaped hybrid with a
**spectral (FNO) branch and a local/attention branch**; **Sparse-Point Adaptive
Routing (SPAR)** emits a **per-location hard choice** between branch outputs (not
a soft blend), with the dominant output-gradient masked to the chosen branch in
the backward pass; gating weights zero-initialized so branches start balanced.
Benchmarks: Burgers, Darcy, Navier-Stokes, shallow water. **No multi-fidelity /
coarse-grid low-fidelity input.**

This is the single most important result of the iteration: **both per-band
routing (SPAMoE) and per-region routing (U-HNO) over spectral-vs-local/attention
operator experts are published, and neither is multi-fidelity.**

### Term 3 — multi-fidelity MoE / fidelity-aware routing

Top results (none is MF-routing):
- "Stable Fine-Time-Step Long-Horizon Turbulence Prediction with a Multi-Stepsize
  Mixture-of-Experts Neural Operator" — https://arxiv.org/pdf/2604.12794
  (shared expert + routed experts for *time-step scale*, not fidelity)
- Shodh-MoE, sparse MoE routing against negative transfer in multi-physics
  foundation models — https://arxiv.org/pdf/2605.15179 (routes by physics domain)
- SA-EMO, "Structure-Aligned Encoder Mixture of Operators for Generalizable
  Full-waveform Inversion" — https://arxiv.org/pdf/2511.11627
- Non-PDE MoE routing hits (malware GNN MoE, MoME, SAME navigation, multi-path
  routing) — irrelevant.

The search engine's own summary states it plainly: *"a specific paper dedicated
exclusively to 'multi-fidelity' MoE with explicit fidelity-aware routing wasn't
in these top results."* Nothing found that routes **by fidelity** or that decides
**which fidelity feeds which expert**. Recorded as a first (weak, one-query)
negative — a targeted refutation query is still owed in §3.3.

## Interpretation

The stream's two obvious mechanisms are already published in single-fidelity
form: per-band routing over operator experts (SPAMoE) and per-region hard gating
between a spectral and a local/attention branch (U-HNO), plus generic MoE-over-
operators at foundation-model scale (MoE-POT). The one axis that has produced no
hits so far is **fidelity-aware routing** — routing that conditions on, or
allocates, the LF field. Iteration 2 must (a) confirm the MF gap with targeted
queries and (b) check whether the *sequential residual FNO->attention hybrid*
itself (the cheap `fno_transolver_seq` benchmark card) is preempted — the
high-contrast-scattering paper above suggests it is.
