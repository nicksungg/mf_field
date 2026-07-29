# Iteration 3 — `s4_hybrid_routing` batch 1

## Search rationale

Two negatives from iteration 2 need to become verdicts, and one uncitable
result needs a citable source:
1. **Routing conditioned on the LF field** (the §12.4 "which fidelity feeds
   which expert" novelty) — attack it directly with MF-fusion + spatially-varying
   gating language.
2. **The MF mixture-of-experts framework** whose OpenReview PDF refused to fetch
   — find an arXiv/other mirror so it can be cited (or confirm it can't be).
3. **Band cutoff chosen from LF/HF cross-spectral coherence** (the P4 mechanism
   in `docs/reports/MF_Sharp_HighFreq_Report.md`) — the last unexamined axis.

## Search terms used

1. `gate conditioned on low-fidelity solution field local disagreement route between operator experts multi-fidelity fusion spatially varying`
2. `"multi-fidelity mixture of experts" framework physics-aware gating network neural operator solver arxiv`
3. `cross-spectral coherence low-fidelity high-fidelity cutoff wavenumber decide which fidelity resolves which band operator learning`

## Findings

### Term 1 — LF-conditioned spatially-varying routing

Top results:
- **LGFNet**, "Local-Global Fusion Network with Fidelity Gap Delta Learning for
  Multi-Source Aerodynamics" — https://arxiv.org/abs/2603.29303 / https://arxiv.org/pdf/2603.29303
- AGMF-Net, "Ensemble adaptive gated multi-fidelity neural network for Bayesian
  optimization: hydrofoil design" —
  https://www.sciencedirect.com/science/article/abs/pii/S002980182502997X
- LCWF-MFS, "multi-fidelity surrogate modeling in the presence of
  non-hierarchical low-fidelity data" —
  https://www.sciencedirect.com/science/article/abs/pii/S1270963824000610
  (local-correlation-weighted fusion: **variable weights per low-fidelity model
  depending on its LOCAL correlation with the HF model**)
- GAR: Generalized Autoregression for Multi-Fidelity Fusion (NeurIPS 2022) —
  https://proceedings.neurips.cc/paper_files/paper/2022/file/37e9e62294ff6607f6f7c170cc993f2c-Paper-Conference.pdf
- "Multi-Fidelity Flow Matching: Cascaded Refinement of PDE Solutions" —
  https://arxiv.org/pdf/2605.16118
- "A new framework for non-stationary spatio-temporal data fusion of
  multi-fidelity models" — https://arxiv.org/pdf/2605.03693
- Gated Fusion Mechanisms (topic page) — https://www.emergentmind.com/topics/gated-fusion-mechanism

**Fetched twice** (PDF then abstract page) — and the second fetch **corrected the
first**, which had over-fitted to my leading prompt. Honest record:

- First fetch (https://arxiv.org/pdf/2603.29303, PDF via summarizer) claimed
  "spectral operator + attention operator experts with spatially-varying gating".
- Second fetch (https://arxiv.org/abs/2603.29303) returned the **verbatim
  abstract**, which says something different: LGFNet (Zhu, Xiang, Zhang, Wang,
  submitted 31 Mar 2026) combines *"a spatial perception layer that integrates a
  sliding window mechanism with a relational reasoning layer based on
  self-attention"* — a **local sliding-window branch + a global self-attention
  branch**, NOT a Fourier/spectral expert; and the abstract claims **no explicit
  routing/gating mechanism**, only multi-scale feature decomposition.
  **Fidelity Gap Delta Learning (FGDL)** treats the LF CFD data as a
  *"low-frequency carrier"* and explicitly approximates the nonlinear
  discrepancy, *"prevent[ing] unphysical smoothing while inheriting the
  foundational physical trends from the simulation baseline."*
  Caveat: the fidelity axis is CFD vs wind-tunnel/flight-test, **not coarse-grid
  vs fine-grid solves** — so it is a fidelity-gap paper, not an MFFP-shaped one.

**I am recording the first summary as unreliable and using only the abstract.**
Net: LGFNet preempts the *framing* "treat LF as a low-frequency carrier and learn
only the nonlinear delta with a local+global two-branch net", but does **not**
preempt LF-conditioned routing (it has no router).

The LCWF-MFS hit (local-correlation-weighted fusion, variable weights by *local*
correlation with HF) is the closest thing found to LF-conditioned spatial
weighting, but it is classical surrogate modelling over LF *models*, not
per-pixel routing between operator experts — and it was **not fetched**, so it is
listed as a lead only, not a citation.

### Term 2 — recovering the MF mixture-of-experts framework

Top results: 2508.21249 again (already fetched, iteration 2), HyPINO
(https://arxiv.org/pdf/2509.05117), Multi-Stepsize MoE Neural Operator
(https://arxiv.org/pdf/2604.12794), SPAMoE (already fetched), MoE-POT (already
fetched), "Knowledge-Constrained Shape Optimization with a Mixture-of-Experts
Neural Operator" (https://arxiv.org/html/2607.09763), AGMF-Net (ScienceDirect).

**No arXiv mirror of the OpenReview "A MULTI-FIDELITY MIXTURE-OF-EXPERT
FRAMEWORK" surfaced.** It therefore stays **uncitable** for this round; the
brainstormer must not lean on it. The search synthesis did describe AGMF-Net as
using *"a deep Mixture-of-Experts (DMoE) gating sub-network to assign
context-aware weights to specialized experts"* in a multi-fidelity setting —
again a synthesis, not a fetch, and ScienceDirect is paywalled, so **AGMF-Net is
also uncitable here**. Both are recorded as *known-to-exist leads that could not
be verified*, which is the honest state; a brainstormer claiming novelty for
"MoE gating in a multi-fidelity network" should treat that claim as **at risk**.

### Term 3 — band cutoff from LF/HF coherence

Top results:
- "Discretization-independent multifidelity operator learning for PDEs" —
  https://arxiv.org/pdf/2507.07292
- "Spectral bias in physics-informed and operator learning: analysis and
  mitigation guidelines" — https://arxiv.org/html/2602.19265v1
- "A Physics-Guided Bi-Fidelity Fourier-Featured Operator Learning Framework" —
  https://arxiv.org/pdf/2311.03639
- "Multi-fidelity prediction of fluid flow and temperature field based on
  transfer learning using FNO" — https://arxiv.org/pdf/2304.06972
- Graph-Laplacian spectral multi-fidelity — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10547726/

**Fetched** https://arxiv.org/pdf/2507.07292 (discretization-independent
multifidelity operator learning): coarse-to-fine discretization ladder in a
single unified model, "significantly fewer high-fidelity samples"; explicitly
**"does not employ routing, gating, or mixture-of-experts mechanisms between
different operator architectures."** So the leading MF-operator-learning paper in
this space is *not* a routing paper — confirming the routing x multi-fidelity
cell is genuinely sparse.

**No usable results** for the specific mechanism "estimate `k_c` from LF/HF
cross-spectral coherence and hard-constrain the sub-`k_c` output band to the LF
spectrum". Two independent negative queries now (iteration 2 term 3, this term).

## Interpretation

The routing x multi-fidelity cell is real but narrower than hoped: LF-as-
low-frequency-carrier delta learning with a local+global two-branch net is
published (LGFNet, arXiv:2603.29303) though without a router; per-region and
per-band routing over operator experts are published single-fidelity
(arXiv:2508.21249, arXiv:2604.07421, arXiv:2605.12965); and the strongest MF
operator-learning paper explicitly has no routing (arXiv:2507.07292). What
remains unpreempted by any *fetched* source: **a router whose input is the LF
field / the LF-HF disagreement**, and **a band cutoff derived from LF-HF
coherence**. Iteration 4 runs the final targeted refutation on the three concrete
candidate directions and writes the verdicts.
