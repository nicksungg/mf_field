# iteration_3 — the nearest PDE-side neighbour (learned mesh movement), the
# one-sided-input problem, and GT-free displacement validation

## Search rationale

Two gaps left. (1) Everything batch 1 found on the PDE side was value-space; but
"a neural net predicts a coordinate displacement from a PDE field" has a whole
literature under a different name — **learned r-adaptivity / mesh movement**.
That is the highest-probability un-searched preemption for D1, so it goes first.
(2) A structural asymmetry nobody has priced: all registration methods take a
**pair** (moving + fixed). At test time our model has only the LF field and the
condition vector — no HF target. Is one-sided displacement prediction a thing?
(3) Task item (d): validating a predicted displacement with no displacement
ground truth at small N.

## Search terms used

1. `neural network predicts mesh movement from coarse PDE solution r-adaptivity learned coordinate transformation operator`
2. `predict deformation field from single input image without target template registration one-sided displacement prediction`
3. `inverse consistency cycle consistency metric evaluating displacement field without ground truth registration validation`

## Findings

### Term 1 — learned mesh movement is the nearest PDE-side neighbour, and it stops one step short of D1

- **M2N** (NeurIPS 2022) is *"the first learning-based end-to-end mesh movement
  framework for PDE solvers"*, with a neural-spline variant for large
  deformations and a GAT variant for delicate local deformation; it explicitly
  addresses **mesh tangling, boundary consistency, and generalization to meshes
  of different resolutions**, and claims a large speedup over the classical
  **Monge-Ampère** mesh-movement solver at comparable numerical error reduction
  [cite: https://arxiv.org/abs/2204.11188 — fetched;
  https://neurips.cc/virtual/2022/poster/53649]. Fetched verdict on the decisive
  question: **it moves mesh nodes, it does not warp a solution field.**
- **UM2N** (2024) generalizes this zero-shot across PDE types and geometries
  (Graph-Transformer encoder, GAT decoder, outputs node relocations), again with
  **no** solution-field warping and **no** multi-fidelity content in the fetched
  abstract [cite: https://arxiv.org/abs/2407.00382 — fetched].
- The pattern that matters for the *input* side: one line of this work *"learns a
  mapping from monitor function values to the potential field describing the mesh
  movement instead of the PDE solution directly"* — i.e. displacement is
  predicted from a **scalar roughness/monitor field derived from the current
  (coarse) solution**, which is precisely the signal a D1 head would have
  [cite: search-result summary over https://arxiv.org/pdf/2407.00382 ;
  parametric r-adaptivity via residual minimization
  https://arxiv.org/html/2607.21753 ; r-adaptive FEM with NNs for parametric
  self-adjoint elliptic problems https://arxiv.org/pdf/2504.21160 (search
  results)]. Note ADR 0009: residual-minimization variants of this are
  physics-requiring and thus disqualified for us; the monitor-function variant is
  physics-agnostic if the monitor is a data statistic.

### Term 2 — displacement prediction is pairwise almost everywhere

- Canonical predictive registration (**Quicksilver**) takes *"entire 3D moving
  and target images as input to directly predict the displacement field"*, in
  patches for memory reasons [cite: https://arxiv.org/pdf/1703.10908 (search
  result) and https://pmc.ncbi.nlm.nih.gov/articles/PMC5731783/ (search result)].
- Unsupervised registration *"learns the deformation field from the
  to-be-registered image PAIR automatically ... by maximizing the image
  similarity metric between the pair"* — pairwise by construction.
- The only one-sided constructions found are **template/canonical-model**
  settings: predict the deformation that warps a *fixed canonical* shape into the
  instance seen in a single image [cite: https://arxiv.org/pdf/2008.07203
  (search result)], and pseudo-mean/atlas symmetric registration
  [cite: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8087477/ (search result)].
  There the "other image" is a learned constant, not an observed target.
- **Structural read**: D1's head must predict `phi` from the LF field + condition
  vector alone, with the HF target available only through the training loss. That
  is not the registration setting (pairwise), and it is not the mesh-movement
  setting either (which is a monitor-field → mesh map with no target field at
  all, and whose output is nodes, not a warped field). It IS the setting closest
  to a *sharp-interface-aware learned error estimator*, and it is the part of D1
  the accumulated literature does not cover.
- Consequence for the design: B1's part-7 open question ("is the displacement
  predictable from the LF field the model actually receives, or only visible to
  an HF-fitted oracle?") is not answerable by citation — the literature never
  poses it, because it always has the target image.

### Term 3 — GT-free validation: inverse-consistency error is the published instrument

- **Inverse-consistency error (E_IC)**: forward composed with backward should be
  the identity; deviation is *"a metric that can evaluate registration quality
  without requiring ground truth data"*, reported over the whole image and over
  regions [cite: https://pmc.ncbi.nlm.nih.gov/articles/PMC3915046/ (search
  result); inversion machinery
  https://link.springer.com/content/pdf/10.1007/978-3-540-75757-3_109.pdf].
- **CycleMorph** makes cycle consistency the training objective for unsupervised
  registration [cite: https://arxiv.org/pdf/2008.05772 (search result)], and
  cycle-consistency has been used as an **uncertainty-quantification** signal for
  networks solving inverse problems, reported to outperform existing UQ methods
  [cite: https://spj.science.org/doi/10.34133/icomputing.0071 (search result)].
- Caveat surfaced and worth carrying: cycle-consistent training is known to fail
  on **many-to-one mappings** [cite:
  http://proceedings.mlr.press/v130/guo21b/guo21b.pdf (search result)] — and an
  LF→HF map that has lost information (5-6 % topology mismatch on cahn_hilliard)
  is exactly many-to-one, so E_IC should be used as a DIAGNOSTIC on the predicted
  displacement, not as a training objective.

## Interpretation

Learned mesh movement (M2N/UM2N) is the true nearest neighbour on the PDE side
and it is one step short of D1 in exactly the way that matters: it relocates
nodes to help a solver, never warps a coarse solution field toward a fine one.
The genuinely uncovered piece of D1 is the **one-sided** displacement prediction
(LF + condition in, displacement out, no target at inference) — registration is
pairwise, mesh movement has no target field. GT-free validation of the predicted
displacement has a published instrument (inverse-consistency error, cycle
consistency) that is cheap to add as a diagnostic, with a documented reason
(many-to-one) not to promote it to a loss here.
