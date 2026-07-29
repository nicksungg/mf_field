# Iteration 5 — adversarial refutation of the candidate directions (PRIOR-ART VERDICT)

*(Iteration cap 5 reached. This is the final iteration.)*

## Search rationale

Everything here is refutation-directed. I first fixed the 3 directions this
stream-batch is likely to propose, then searched to KILL each one:

- **D1 `mf_warp_correct`** — a model family: a smooth displacement field
  predicted from the up-sampled LF field (+ condition vector) by a small FNO
  head, zero-initialized and smoothness-penalized, applied by differentiable
  `grid_sample`, followed by a FiLM-conditioned residual correction net on the
  warped field (NEW_MODELS.md §8.2).
- **D2 warp-oracle diagnostic** — no training: decompose the LF→HF gap (and
  the certified champion's error) into displacement vs amplitude on the panel
  via optical flow, and compute the **oracle-warp upper bound**: the best
  nRMSE reachable by warping copy-LF alone. Plus a topology check (connected
  -component count of LF vs HF phase indicators).
- **D3 transport-flavored objective / metamorphosis regularization** — an
  OT/soft-warp auxiliary training loss, or a warp + *parsimonious* appearance
  term, in place of (or around) an architecture change.

## Search terms used

1. `learn deformation field morph low-fidelity coarse solution onto high-fidelity solution surrogate model warp before residual correction operator learning` (kills D1?)
2. `quantify fraction of error due to feature displacement optical flow decomposition coarse versus fine grid simulation upper bound alignment` (kills D2?)
3. `optimal transport Wasserstein loss training neural operator shock position error alignment auxiliary loss PDE surrogate sharp interface` (kills D3?)

## Findings

### Term 1 (against D1) — no cross-fidelity warp found

Results are the same additive/latent MF families already logged: MF-ROM with
MF-LSTM coefficient mapping (https://arxiv.org/abs/2309.00325, previously
fetched and confirmed HF-to-HF registration only), MF-LSTM surrogates
(ResearchGate 366177112), MFFM (https://arxiv.org/pdf/2605.16118),
multifidelity deep learning of lung mechanics
(https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12504473/), crashworthiness GNN
surrogate (https://www.sciencedirect.com/science/article/pii/S2590123026019572)
— where "mesh morphing" appears it is a **dataset-construction** device
(node-level deformation fields for geometry variation), not an inter-fidelity
alignment. **No usable refutation of D1.**

Supporting fetched evidence that the MF field explicitly does something else:
**MFFM, https://arxiv.org/html/2605.16118v1 — fetched.** "purely additive
refinement in value space, not spatial displacement"; cascade
`u_{ℓ+1} = I_{ℓ→ℓ+1}(u_ℓ) + δ_ℓ` where `I` is "**bilinear prolongation
(spatial upsampling only, not warping)**"; learns `δ = u_HF − u_LF`
conditioned on `u_LF`; 8 benchmarks (Darcy/Burgers 768 samples; PDEBench, The
Well, NS); and, decisively for our framing, it "does not prominently discuss
sharp interfaces, discontinuities, or feature misalignment between fidelities"
and assumes "for typical parametric PDEs the LF and HF solutions are strongly
correlated across most of the domain." That assumption is exactly what the
panel violates.

### Term 2 (against D2) — the measurement is unmade

No result quantifies the displacement-vs-amplitude split between a coarse and
a fine solve, nor an oracle-alignment upper bound. Hits are generic
coarse-to-fine optical-flow estimation (PatchMatch CVPR 2016,
https://www.cv-foundation.org/openaccess/content_cvpr_2016/papers/Hu_Efficient_Coarse-To-Fine_PatchMatch_CVPR_2016_paper.pdf ;
coarse-to-over-fine flow, ResearchGate 222814863) where "coarse/fine" refers to
image pyramids, not solver fidelity. **No usable refutation of D2**; the tool
it would use (Keil & Craig DAS, iteration 3,
https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf) is
published, its multi-fidelity application is not.

### Term 3 (against D3) — OT objectives exist in ROM, not in MF operator training

- **OT-inspired deep learning for slow-decaying Kolmogorov n-width problems:
  Sinkhorn loss + Wasserstein kernel**, https://arxiv.org/abs/2308.13840 —
  kPOD with a Wasserstein kernel, network trained with Sinkhorn; "efficient
  ... for one-dimensional conservative PDEs where the underlying metric space
  can be chosen to be the L²-Wasserstein space". This **partially preempts**
  "use OT geometry as the learning objective for transport-dominated PDE
  surrogates" — but it is single-fidelity ROM, 1-D conservative, and not a
  fusion loss.
- Nothing found applying an OT/soft-warp auxiliary loss to **multi-fidelity**
  neural-operator training on 2-D sharp interfaces.

## PRIOR-ART VERDICT

| Direction | Verdict | Load-bearing fetched citations | What remains open |
|---|---|---|---|
| **D1** `mf_warp_correct` (learned inter-fidelity displacement + correction) | **preempted-but-MF-composition-open** | Flowers, https://arxiv.org/html/2603.04430 (fetched: learned per-head warp IS the primitive of a 2026 neural PDE solver, `x + ϱ^(h)(x)` via STN-style bilinear sampling, but "**perform no coarse-to-fine solution mapping or low-to-high-fidelity correction**", no smoothness penalty, no zero-init); MetaRegNet, https://arxiv.org/pdf/2303.09088 (fetched: warp + appearance/source term = metamorphosis, the generic "warp-then-correct" formulation, in imaging); Khamlich et al., https://arxiv.org/html/2603.04232v2 (fetched: **MF, LF→HF, transport-based, on conservative Allen–Cahn diffuse interfaces at 128²→512²** — but OT displacement-*interpolation of residual fields across time/parameters*, `u ≈ u_LF + r_interp`, **no neural network**, no warp of the LF field); MFFM, https://arxiv.org/html/2605.16118v1 (fetched: MF refinement is additive in value space with bilinear prolongation, assumes strong LF-HF correlation) | Open: predicting a displacement field **from an LF PDE solution field** and warping **that field** into HF alignment before a learned correction, inside an operator-learning MF surrogate, in the few-HF-sample regime. NOT open, and must not be claimed: "learned warping in neural PDE models" (Flowers), "align-then-correct as a formulation" (metamorphosis), "transport geometry for MF diffuse-interface correction" (Khamlich). |
| **D2** warp-oracle / displacement-amplitude diagnostic on the panel | **preempted-but-MF-composition-open** | Keil & Craig 2009 DAS, https://journals.ametsoc.org/view/journals/wefo/24/5/2009waf2222247_1.pdf (the optical-flow morph + displacement/amplitude split, verified primary source); registration ROM scope limit, https://arxiv.org/html/2501.01299v1 (fetched: applies only "where the structures of the transported features remain consistent") | The metric is 17 years old; **no fetched source measures it between two fidelities of the same PDE solve**, and none reports an oracle-warp upper bound on MF fusion error. This is the cheapest defensible batch-1 card and it also *gates* D1: if the LF→HF gap is thickness/amplitude-dominated rather than displacement-dominated (iteration 4's two-regime finding), D1's premise dies before any GPU is spent. |
| **D3** OT / soft-warp auxiliary objective, or metamorphosis-style parsimony penalty | **preempted-but-MF-composition-open** (weakest confidence) | OT-inspired Sinkhorn/Wasserstein-kernel ROM, https://arxiv.org/abs/2308.13840 (single-fidelity, 1-D conservative); MetaRegNet, https://arxiv.org/pdf/2303.09088 (appearance-term parsimony is the published regularization pattern) | Open: an OT/soft-warp term in a **multi-fidelity 2-D operator** training loss. Caveat from program.md §5: the training loss is free but the SCORED metric is fixed nRMSE — an OT-flavored loss must be justified as improving nRMSE, not as changing the target. |

### Adversarial ruling on NEW_MODELS.md §8.4

The literal claim — "**No published multi-fidelity operator method predicts an
inter-fidelity displacement field and warps before correcting**" — **survives**
this loop's refutation attempts (5 dedicated searches across MF operators, MF
ROMs, registration ROMs, learned warps in PDE nets, and MF surrogate morphing;
no counterexample fetched).

The surrounding claim — "**the registration-based framing 'align, then
correct' is a documented gap**" — **does NOT survive**. Align-then-correct is
the metamorphosis formulation in registration (MetaRegNet), and the
transport-geometry-for-MF-diffuse-interface territory is already occupied by
Khamlich et al. 2603.04232 on conservative Allen–Cahn at our exact resolution
ladder. The stream's honest novelty surface is **narrow**: the *neural,
cross-fidelity, field-level* instantiation, in the few-HF-sample operator-
learning regime. Any card claiming more than that is overclaiming, and this
project is 0-for-4 on exactly that failure mode (program.md §13.3).
