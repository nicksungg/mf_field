# MFFP documentation index

Everything here is *research writing* — reports, proposals, plans, and raw notes.
None of it is executable and none of it is read by the factory pipeline; the code contract lives in
[`../CLAUDE.md`](../CLAUDE.md), [`../factory.md`](../factory.md), and [`../eval/MODEL_CONTRACT.md`](../eval/MODEL_CONTRACT.md).

Filenames are unique across the whole tree, so a bare mention like `NEW_MODELS.md` inside a
document still resolves unambiguously — use the tables below to find where it now lives.

## `reports/` — finished deliverables

The Markdown is the source of truth and the only kept copy.
The PDFs that were originally shared have been deleted as redundant — regenerate any of them with
`md_to_pdf.py` (see [Figures](#figures) below).
Documents whose only form is HTML or PDF are kept as-is, since there is no Markdown source for them.

| Report | Date | What it covers |
| --- | --- | --- |
| [`MF_SOTA_vs_MFFP_Report.md`](reports/MF_SOTA_vs_MFFP_Report.md) | 2026-06-27 | Multi-fidelity state of the art in industry and academia, head-to-head against the MFFP model zoo. |
| [`MF_Sharp_HighFreq_Report.md`](reports/MF_Sharp_HighFreq_Report.md) | 2026-07-02 | Sharp / high-frequency PDE solutions: the spectral wall, misalignment dipole, blur-preference arguments, and the P-proposals. |
| [`MF_Sharp_HighFreq_Report_Beginner.md`](reports/MF_Sharp_HighFreq_Report_Beginner.md) | 2026-07-02 | Plain-language companion to the above, for an intro-ML reader. Same facts, no new claims. |
| [`MF_Leaderboard_Beaters_2026_Report.md`](reports/MF_Leaderboard_Beaters_2026_Report.md) | 2026-07-13 | July 2026 literature scan for papers that could beat the MFFP leaderboard, high- and low-frequency regimes. |
| [`MF_FNO_CNN_Hybrid_Report.md`](reports/MF_FNO_CNN_Hybrid_Report.md) · [html](reports/MF_FNO_CNN_Hybrid_Report.html) | 2026-07-21 | The spectral-then-local FNO→CNN hybrid: how it works, and a prior-art verdict from a 5-angle literature sweep. |
| [`MFFP_Model_Explanations.html`](reports/MFFP_Model_Explanations.html) | 2026-07-02 | Walkthrough of the model zoo — what each family does and how it fuses LF and HF. |
| [`MFFP_Model_Explanations_Beginner.html`](reports/MFFP_Model_Explanations_Beginner.html) | 2026-07-02 | From-scratch version of the same tour (what an FNO is, what FiLM is, all 30 families). |
| [`MFFP_QUESTIONS_ANSWERED.pdf`](reports/MFFP_QUESTIONS_ANSWERED.pdf) | 2026-06-27 | Answers to the first round of open questions in [`notes/QUESTIONS.md`](notes/QUESTIONS.md). |

### Figures

Figure directories sit beside the reports so the relative image paths inside the Markdown keep working.

| Directory | Belongs to |
| --- | --- |
| `reports/report_figs/` | `MF_SOTA_vs_MFFP_Report.md` |
| `reports/report_figs_hf/` | `MF_Sharp_HighFreq_Report.md` |
| `reports/report_figs_hybrid/` | `MF_FNO_CNN_Hybrid_Report.md` — also holds `make_fig_hybrid.py` (regenerates the figures) and `md_to_pdf.py` (renders a report to PDF). |

Both scripts are run from inside their own directory and take paths like `../<report>.md`.
`md_to_pdf.py` is not specific to the hybrid report — it renders *any* of the reports above,
which is how you get a shareable PDF back:

```bash
cd docs/reports/report_figs_hybrid
python make_fig_hybrid.py                          # regenerate the hybrid figures
python md_to_pdf.py ../MF_Sharp_HighFreq_Report.md # -> ../MF_Sharp_HighFreq_Report.pdf
```

It inlines images as data URIs and renders through headless Chrome, so the output is
self-contained and matches the toolchain that produced the original deliverables.

## `proposals/` — model ideas under consideration

| Document | Date | Status |
| --- | --- | --- |
| [`MODELS_TO_TRY.md`](proposals/MODELS_TO_TRY.md) | 2026-07-22 | **The live candidate list.** Net-new models organized under two hypotheses (spectral capacity vs. local representation), with HF-data proportion as a crossing axis. Supersedes `NEW_MODELS_2.md`. |
| [`NEW_MODELS.md`](proposals/NEW_MODELS.md) | 2026-07-20 | Strategy memo: refiner mechanism + hybrid backbone, candidates A–D with prior-art findings. |
| [`NEW_MODELS_2.md`](proposals/NEW_MODELS_2.md) | 2026-07-22 | Follow-on discussion fragment arguing the candidate list should be collapsed (the transfer-learning study contains the hybrid architecture). Superseded by `MODELS_TO_TRY.md`, kept for provenance. |
| [`MODEL_TWEAKS.md`](proposals/MODEL_TWEAKS.md) | audit 2026-07-19 | Cross-family fixes, decision brief. Nothing implemented. |
| [`MODEL_TWEAKS_EVIDENCE.md`](proposals/MODEL_TWEAKS_EVIDENCE.md) | audit 2026-07-19 | Evidence register backing the decision brief. |

## `planning/` — autonomous-research loop design

| Document | Date | Status |
| --- | --- | --- |
| [`AUTORESEARCH_PLAN.md`](planning/AUTORESEARCH_PLAN.md) | 2026-07-22 | Proposal for a go/no-go decision, not a spec. |
| [`META_AUTORESEARCH.md`](planning/META_AUTORESEARCH.md) | 2026-07-22 | Analysis of whether the autoresearch loop can itself be autoresearched. For a go/no-go decision. |

## `notes/` — raw inputs, unedited

Question lists and idea seeds, in the order they were written.
These are inputs to the reports above, not conclusions.

| Document | Date |
| --- | --- |
| [`QUESTIONS.md`](notes/QUESTIONS.md) | 2026-07-01 |
| [`QUESTIONS-1.md`](notes/QUESTIONS-1.md) | 2026-07-02 |
| [`QUESTIONS-2.md`](notes/QUESTIONS-2.md) | 2026-07-21 |
| [`IDEA.md`](notes/IDEA.md) | 2026-07-15 — the forward/backward-NN idea that became Candidate C in `NEW_MODELS.md`. |

## `external/` — material from outside this repo

| File | What it is |
| --- | --- |
| [`multifidelity_shared_detail_latent_operator.pdf`](external/multifidelity_shared_detail_latent_operator.pdf) | "Shared-Detail Latent Neural Operator for Multi-Fidelity PDE Prediction" — 5-page paper, evaluated 2026-07-20. |
| [`update2.pdf`](external/update2.pdf) | 8-page project update deck. |

## What stayed at the repo root

These are the fixed-surface / entry-point documents and are deliberately not filed under `docs/`:

- `README.md` — repo entry point
- `CLAUDE.md` — Claude Code guidance
- `factory.md` — the CEO agent's config and mutable/fixed-surface declaration
- `HOWTO.md` — operating instructions

Per-directory docs also stay where they are: `eval/MODEL_CONTRACT.md`, `model/README.md`,
`models/README.md`, and each family's `models/<family>/INSPIRATION.md`.
