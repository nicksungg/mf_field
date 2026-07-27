# Docs index

### Start here
- **[design-rationale.md](design-rationale.md)** — plain-language walkthrough of the whole project:
  what "high frequency" means, why FNO struggles, how we chose the PDEs + condition vectors, what
  sample validation taught us, and the thought process to the sharpness-transition idea. With plots.

### Reference & proposals (for Nicholas)
- **[pde-summary.md](pde-summary.md)** — concise reference: the 3 PDEs, governing equations,
  condition vectors, fidelity ladders, suitability, and the open decisions.
- **[ch-sharpness-transition.md](ch-sharpness-transition.md)** — proposal: use Cahn–Hilliard's
  interface width ε as a continuous knob to map the smooth→sharp performance transition. With the
  prototype sweep results.
- **[mf-fusion-explained.md](mf-fusion-explained.md)** — what multi-fidelity *fusion* is, and how the
  benchmark's models sort into fusion vs transfer/finetuning vs baselines.

### Concept explainer
- **[answers.md](answers.md)** — detailed answers on radial wavenumber, smoothness ↔ spectral
  decay, computing decay rates, and why FNO truncates. With plots.

### Project notes
- **[prereqs.md](prereqs.md)** — initial Claude Code environment/plugin setup (historical).
- Active plan: [`../TO-DO.md`](../TO-DO.md). Resources (compute box, papers): [root README](../README.md#resources).

### Figures
`figures/` holds the **committed** figures the docs embed. Generated/regenerable figures live under
`mffp_sharp/data/` (git-ignored) — see the [root README](../README.md#figures-live-in-two-buckets-by-design).
