# Iteration 1 — is warp-before-correct already published for MF PDE fusion?

## Search rationale

The stream's whole premise is Candidate D's claim (NEW_MODELS.md §8.4): "No
published multi-fidelity *operator* method predicts an inter-fidelity
displacement field and warps before correcting." Program.md §13.3 says the
project is 0-for-4 on such claims, so iteration 1 goes straight at the two
places the mechanism most plausibly already lives: (i) the MF neural-operator
literature itself, (ii) the registration/transport model-order-reduction (ROM)
line, which is where "align then correct" is a mature, named idea. A third
term probes the learned-warp super-resolution angle (coarse→fine CFD), the
nearest ML-side neighbor.

## Search terms used

1. `multi-fidelity neural operator displacement field warping low-fidelity to high-fidelity alignment PDE`
2. `registration-based multi-fidelity model order reduction transport map discontinuous solutions warp then correct`
3. `neural network predicts warping field align coarse simulation to fine simulation optical flow grid_sample super-resolution fluid`

## Findings

### Term 1 — MF neural operators

Top results are all **additive / generative residual** MF methods, none
geometric:

- Multi-Fidelity Flow Matching (MFFM), https://arxiv.org/html/2605.16118v1 —
  "consumes ... any low-fidelity solver's output on a finer grid and produces
  a high-fidelity refinement through a flow-matching cascade". Refinement in
  value space, not a displacement.
- Flow-matching operators for residual-augmented probabilistic learning,
  https://arxiv.org/pdf/2512.12749 — "the flow model learns the correction
  (residual) between a low-fidelity surrogate and the high-fidelity solution".
- GAR generalized autoregression, https://arxiv.org/pdf/2301.05729;
  MF-FNO for geological carbon storage,
  https://www.sciencedirect.com/science/article/abs/pii/S0022169424000350;
  MF transfer-learning FNO, https://arxiv.org/pdf/2304.06972; composite MF
  network, https://arxiv.org/abs/1903.00104 — all additive/autoregressive.
- Neural-operator "super-fidelity" warm start,
  https://www.sciencedirect.com/science/article/abs/pii/S0021999125001548 —
  LF solution used to warm-start a HF steady solve; still value-space.
- Feature-adjacent MF PIML,
  https://www.sciencedirect.com/science/article/abs/pii/S0021999123007787 —
  "a feature space shared by the low- and high-fidelity solutions ...
  constraining their relative distance". This is *latent* alignment, NOT a
  spatial displacement field. Nearest conceptual neighbor so far, but a
  different mechanism (no warp of the field, no grid_sample).

No result predicts a spatial displacement field between fidelities.

### Term 2 — registration / transport ROM

This is where "align then correct" is mature — and it is **classical ROM, not
learned operators**:

- Registration-based MOR of parameterized 2-D conservation laws,
  https://www.sciencedirect.com/science/article/abs/pii/S0021999122001309 —
  computes a mapping Φ tracking moving features, then a hyper-reduced LSPG ROM
  for the coefficients. **Critically, the search snippet states: "A
  multi-fidelity approach reduces the offline costs associated with the
  construction of the parameterized mapping and the reduced-order model."**
  This is MF used to build the registration cheaply — a real preemption threat
  that iteration 2 must pin down (MF-for-registration vs registration-for-MF).
- Registration-based MOR with spatio-parameter adaptivity (ResearchGate
  376872409); registration-based nonlinear MOR for transonic Euler/RANS,
  https://www.sciencedirect.com/science/article/pii/S0021999124008246 —
  "localized spline-based parametrized transformations which warp the domain
  to align discontinuities" + hyperreduction.
- Calibration-based ALE MOR for self-similar travelling discontinuities,
  https://arxiv.org/pdf/2403.11664; transport-map n-width paper,
  https://arxiv.org/pdf/1911.06598.
- Review: Nonlinear model reduction for transport-dominated problems
  (Hesthaven, Peherstorfer, Unger), https://arxiv.org/pdf/2602.01397 —
  **fetched**; the PDF returned mostly structural metadata so no passages
  could be read, but the bibliography exposes two leads worth chasing:
  `iollo2026mathematicalaspectsregistrationmethods` and
  **`klein2025multifidelitylearningreducedorder`** (MF + ROM learning).
- Cross-correlation snapshot registration, https://arxiv.org/html/2501.01299v1
  — **fetched**: registers each snapshot to a *reference snapshot*, shifts
  computed by cross-correlation and mapped from parameters by RBF/linear
  interpolation, "**No neural network is used**", "**No multi-fidelity
  approach is present**" (HF snapshots only). 1-D 256 nodes; 2-D 28,800
  points. Explicitly limited to problems "where the structures of the
  transported features remain consistent" — i.e. **the topology-preservation
  assumption is acknowledged as a scope limit in this literature**, with no
  handling offered.

### Term 3 — learned warp for coarse→fine

- Mesh-based super-resolution with multiscale GNNs,
  https://www.sciencedirect.com/science/article/abs/pii/S0045782525003445 —
  coarse→fine interpolation, message passing; no displacement field.
- Super-resolution with dynamics in the loss, https://arxiv.org/pdf/2410.20884;
  pore-flow SR, https://arxiv.org/pdf/2109.09863 — value-space SR.
- WAFT: Warping-Alone Field Transforms for Optical Flow,
  https://arxiv.org/html/2506.21526v1 — warping is central, but the task is
  optical flow on images, not fidelity fusion.
  No usable *PDE-fusion* warp result on this term.

## Interpretation

Two literatures are adjacent and neither is the proposed mechanism: MF neural
operators correct **additively/generatively in value space**, and registration
ROMs warp **classically, snapshot-to-reference, with no neural displacement
predictor and (in the one fetched case) explicitly no multi-fidelity**. The
one live preemption thread is the multi-fidelity variant inside the
registration-ROM line (S0021999122001309 and the `klein2025` reference),
which must be resolved before any novelty verdict.
