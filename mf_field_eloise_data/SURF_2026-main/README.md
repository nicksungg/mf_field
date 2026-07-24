# SURF 2026 — sharp-field PDE datasets for the MFFP benchmark

Adding **high-frequency (shock / sharp-interface) 2D PDE datasets** to the Multi-Fidelity Field
Prediction (MFFP) benchmark, to test whether its "FNO-finetuning beats multi-fidelity fusion"
result — measured on a mostly-smooth suite — still holds when the solution is sharp.

## Where to start
- **Latest status (for the mentor): [`docs/sample-round-report.md`](docs/sample-round-report.md)** —
  the 8 implementation plans, the 3 → 24 dataset expansion, the 72-figure screened menu, and the
  open decisions for Nicholas.
- **Solver legitimacy + verification: [`PDE_SOLVERS.md`](PDE_SOLVERS.md)** — each PDE's citation and
  exact code file, plus how to verify the solvers run correctly (`mffp_sharp/scripts/verify.sh`).
- **New here? Read [`docs/design-rationale.md`](docs/design-rationale.md)** — a plain-language
  walkthrough of the whole reasoning, with all the plots (covers the original 3 PDEs).
- **Quick reference:** [`docs/pde-summary.md`](docs/pde-summary.md) — the 3 PDEs, their condition
  vectors, and the open decisions.
- **Docs index:** [`docs/README.md`](docs/README.md).

## Repo map
```
README.md                  this file
CLAUDE.md                  project instructions for Claude Code
TO-DO.md                   active plan / sample-round design + approval gate
PDE_SOLVERS.md             per-PDE citations + code pointers + how to verify the solvers
docs/                      all notes & writeups (+ committed figures in docs/figures/)
mffp_sharp/                the Python package (solvers, generation, figures)
  src/mffp_sharp/          code; configs/ ; scripts/
  data/                    ALL generated output (datasets + figures) — GIT-IGNORED, regenerable
mf_field_prediction.pptx   the original MFFP deck (git-ignored)
```

## Figures live in two buckets (by design)
- **Generated** — under `mffp_sharp/data/` (e.g. `data/explain/`, `data/sample/figures/`). Produced
  by scripts, **git-ignored and regenerable**; they also live on the compute box. Not in the repo.
- **Committed** — `docs/figures/`. The curated subset that the markdown docs embed (so they render on
  GitHub). When a generated figure is worth publishing, it's copied here.

## Running it
The package (solvers, dataset generation, review figures) is documented in
[`mffp_sharp/README.md`](mffp_sharp/README.md). Heavy generation runs on the GPU box; light figure
work runs in a local venv (see that README).

## Resources
- **Compute box (4090 GPU):** `ssh eloise@10.80.6.224` — runs heavy generation/training (see
  `CLAUDE.md` for the box workflow).
- **Papers:** [Google Drive folder](https://drive.google.com/drive/folders/1TK5iz9mij3o9YA12ZQs9pSxmHpymtIa6?usp=drive_link).
- **Original MFFP deck:** `mf_field_prediction.pptx` (git-ignored, in the repo root).
