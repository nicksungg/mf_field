# Iteration 3 — the two mechanisms the in-round data actually points at

## Search rationale

Iteration 2 left two live candidates. This turn tests them against the
adjacent, much larger literatures they would be borrowing from — computer
vision (gated blending, exemplar/reference SR) and neural-operator residual
correction — because that is where this project's 0-for-4 novelty record has
historically been broken (program.md §13.3): the mechanism is always already
published *somewhere*, and the only defensible claim is about the
multi-fidelity composition.

## Search terms used

1. `learned confidence gate blend surrogate prediction with input baseline
   per-pixel never worse than identity skip connection super-resolution`
2. `exemplar-based reference-guided super-resolution patch dictionary
   retrieval scientific field prediction`
3. `delta learning residual correction of coarse solution neural operator
   identity initialization guarantee not worse than coarse baseline`

## Findings per term

### T1 — gated blending with the input / never-worse constructions

- No paper stating a **never-worse-than-the-input guarantee** surfaced. What
  exists is the generic CV machinery: "Learnable Skip-and-Gate Fusion"
  (https://www.emergentmind.com/topics/learnable-skip-and-gate-fusion) —
  gates that "learn when to pass, block, or blend information"; per-pixel
  fusion-weight modules; confidence-map-guided blending; U-Net SR pipelines
  that interpolate the LR input to target resolution and concatenate it.
  Also dense-skip SR (https://openaccess.thecvf.com/content_ICCV_2017/papers/Tong_Image_Super-Resolution_Using_ICCV_2017_paper.pdf).
- **Reading**: per-pixel learned gating and interpolate-and-concatenate are
  thoroughly published *as CV components*. The proposition that has no hit is
  the **fusion-rule guarantee** — parameterizing the model so that the
  copy-LF baseline is exactly recoverable and is the initialization, in the
  multi-fidelity PDE setting where copy-LF is the scored reference.

### T2 — exemplar / retrieval-based super-resolution

- **RASR: Retrieval-Augmented Super Resolution for Practical Reference-based
  Image Restoration** — https://arxiv.org/pdf/2508.09449 — FETCHED. Maintains
  a bank of HQ reference images with their LR versions; queries it with the LR
  input; retrieved references guide restoration; beats non-retrieval baselines
  on perceptual + detail metrics. **Image-domain only** per the fetch.
- The broader class is old and dense: exemplar-based SR (external patch
  database, transfer HR patches for matched LR patches), RefSR, sparse-coding
  over-complete LR/HR dictionaries, CrossNet cross-scale warping
  (https://arxiv.org/pdf/1807.10547), retrieval-compensated group-sparse SR
  (https://dl.acm.org/doi/10.1109/TMM.2016.2614427), RZSR self-exemplars.
- **Reading**: retrieval/exemplar SR is comprehensively preempted **as an
  image method**. No hit places a retrieval bank inside multi-fidelity
  operator learning, and iteration 1's T1 found no retrieval-augmented neural
  operator either. The open composition is: **bank keyed on the LF FIELD**
  (our knn measurements were keyed on X, the condition vector) returning HF-LF
  residuals.

### T3 — residual/delta correction of a coarse solution

- **IRNO — Iterative Refinement Neural Operators are Learned Fixed-Point
  Solvers** — https://arxiv.org/html/2605.24041 and
  https://arxiv.org/pdf/2605.24041. Decomposes prediction into a coarse
  initialization plus successive residual corrections at inference; a
  pretrained base operator gives an ansatz capturing dominant low-frequency
  structure, then residual correction. (Already known to this round — it was
  the anchor paper of the retired `s3_testtime` stream.)
- **Deep Delta Learning** — https://huggingface.co/papers/2601.00417 /
  https://yifanzhang-pro.github.io/deep-delta-learning/ — generalizes the
  residual connection by modulating the identity shortcut with a learnable,
  data-dependent rank-1 "Delta Operator" (reflection direction + gating
  scalar). Generic deep-learning architecture, not PDE/MF-specific.
- Also: residual-based error correction for neural-operator-accelerated
  Bayesian inverse problems
  (https://www.sciencedirect.com/science/article/abs/pii/S0021999123001997);
  PhyRes-MDNF physics-coupled residual GNN correction
  (https://arxiv.org/pdf/2607.06237) — physics-coupled, excluded by ADR 0009
  as a test-time method.
- The search engine's own summary is the load-bearing negative: the returned
  set "[does] not contain specific information about an identity
  initialization guarantee that ensures the refined solution is not worse than
  the coarse baseline."

## Interpretation

Both live candidates are *mechanism-preempted in a neighbouring field and
composition-open in ours*: gated blending is CV-standard but its use as a
**guaranteed copy-LF fallback in MF PDE fusion** has no hit; exemplar
retrieval is CV-standard but has no MF-operator instance, and the
LF-field-keyed residual bank has no hit at all. Iteration 4 runs the explicit
refutation queries in the multi-fidelity / neural-operator vocabulary, plus
the deferred `s8_data` cross-dataset-pretraining refutation.
