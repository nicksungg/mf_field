# Iteration 2 — `r2s2_stacked` / batch 1

## Search rationale

Iteration 1 established that published "two-stage" pipelines keep a **real** LF/coarse solve
online. Three follow-ups: (1) has anyone *replaced* the coarse solver in a solver+corrector
hybrid with a learned emulator and measured the cost; (2) is the **frozen vs fine-tuned vs
end-to-end** arm set for a stacked surrogate already settled in the literature (that is
literally the pre-directed B1 ablation, program.md §12.2); (3) is "a coarse/LF field as an
intermediate bottleneck representation, predicted rather than solved" a published design.

## Search terms used

1. `surrogate replaces coarse solver in hybrid solver-corrector pipeline error accumulation emulated coarse field`
2. `end-to-end training versus frozen pretrained downstream module two-stage neural PDE surrogate ablation fine-tuning`
3. `intermediate coarse solution as bottleneck representation neural surrogate parametric PDE intermediate supervision hierarchical coarse-to-fine`

## Findings

### Term 1 — surrogate substituted for the coarse solver

- **INC: An Indirect Neural Corrector for Auto-Regressive Hybrid PDE Solvers**,
  https://openreview.net/forum?id=s3Uk3lrfjy — search snippet: "Directly applying learned
  corrections to solver outputs leads to significant autoregressive errors, which originate
  from amplified perturbations". Snippet-level only (not fetched); the setting is
  autoregressive time-marching with a *real* solver in the loop.
- **ANCHOR**, https://arxiv.org/pdf/2512.19643 — neural operator + HF solver invoked
  selectively when an error estimator trips. Solver-in-the-loop; the opposite of our
  no-solver-at-test constraint.
- **Predictivity and Utility of Neural Surrogates of Multiscale PDEs**,
  https://arxiv.org/pdf/2604.20061 — snippet: "use the surrogate where it is fast and
  accurate … and return to the full solver to regenerate the high-frequency content that
  spectral bias suppresses"; periodic resets to a full-order solver. Same solver-in-the-loop
  premise.
- Adjacent hybrids surfaced but not fetched: XRePIT https://arxiv.org/html/2510.21804,
  DNS+neural-operator blending https://arxiv.org/pdf/2312.05410, hybrid adaptive FNO for
  phase-field https://arxiv.org/pdf/2406.17119.
- **No usable result** for "corrector trained on real coarse solves, then fed an emulated
  coarse field, with the loss attributed to distribution shift" in a *parametric,
  single-shot* (non-autoregressive) setting.

### Term 2 — frozen vs end-to-end for a stacked surrogate

- **CALM-PDE** (Hagnberger, Musekamp, Niepert, NeurIPS 2025), https://arxiv.org/abs/2505.12944
  (full text fetched at https://arxiv.org/html/2505.12944v2), **VERIFIED BY HTML FETCH** of §4.3: the authors "opt for an end-to-end training procedure
  because we found it to be more stable compared to a two-stage training procedure that first
  trains the encoder-decoder using a self-reconstruction loss and, after that, trains the
  processor to learn the latent dynamics", citing Yin et al. (2023) and Serrano et al. (2024)
  as users of the two-stage variant. This is a **directional prior on the exact frozen-vs-
  end-to-end axis** — but for a latent encoder/processor of time-dependent PDEs, not for an
  emulated-LF front end + independently trained field corrector, and with no attribution of
  the gap to input distribution shift.
- The rest of the hits are generic pretrain/finetune transfer (Pretraining a Neural Operator
  in Lower Dimensions https://arxiv.org/pdf/2407.17616; MoE operator transformer
  https://arxiv.org/pdf/2510.25803; PI-JEPA https://arxiv.org/html/2604.01349v3) — r2s3
  territory, not this stream's.

### Term 3 — coarse field as a predicted bottleneck

- **PANIS — Physics-Aware Neural Implicit Solvers for multiscale, parametric PDEs**
  (Chatzopoulos & Koutsourelakis, arXiv:2405.19019 — https://arxiv.org/abs/2405.19019), **VERIFIED via arXiv API fetch** (http://export.arxiv.org/api/query?search_query=ti:%22Physics-Aware%20Neural%20Implicit%20Solvers%22):
  surrogate for parametrized PDEs using weighted residuals to produce "virtual data",
  combined with "a physics-aware implicit solver — essentially a coarser discretized version
  of the original PDE — to address high-dimensional challenges". The coarse discretization is
  an **explicit solver embedded in the model** (physics known), not a learned emulator of a
  coarse solve. Round 2 is physics-agnostic at test (program.md §12.1 cites ADR 0009), so this
  is a different mechanism, though it is the nearest "coarse-solution-as-bottleneck" neighbor.
- Other hits (numerical homogenization surrogates https://arxiv.org/pdf/2209.02624; Latent
  Neural PDE Solver https://arxiv.org/pdf/2402.17853; coarse-to-fine PINN collocation
  refinement https://arxiv.org/html/2607.14665) use coarse *grids/points*, not an emulated LF
  field consumed by a separately trained corrector.

## Interpretation

The mechanism "learned emulator stands in for the coarse solve, feeding a corrector trained
on real coarse solves" has not surfaced in either iteration; what is published is (a)
solver-in-the-loop hybrids and (b) a general end-to-end-beats-two-stage prior (CALM-PDE) in a
different architecture. Iteration 3 should spend its budget on the targeted refutation
searches for the concrete B1 candidate directions (§3.3), including a search phrased in
statistics/UQ vocabulary ("emulator of the low-fidelity code") where this idea would most
plausibly already exist.
