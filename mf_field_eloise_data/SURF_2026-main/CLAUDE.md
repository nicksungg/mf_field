# CLAUDE.md — SURF 2026

Guidance for Claude Code sessions in this repo.

## What this project is
A SURF research project extending the **Multi-Fidelity Field Prediction (MFFP)** benchmark
(`mf_field_prediction.pptx`). MFFP predicts a high-fidelity (HF, fine-grid) 2D PDE solution field
from cheap low-fidelity (LF, coarse-grid) fields + a small condition vector, with few HF samples.

**Research question.** The benchmark's headline result is *"FNO HF-finetuning beats fancier MF
fusion"* — but that was measured on a **mostly-smooth** dataset suite (FNO's comfort zone). We are
adding the **sharp / high-frequency datasets the suite lacks**, along a single frequency axis
(**shock → sharp interface → smooth control**), to test whether that conclusion survives when
FNO's spectral truncation actually bites. We are building the *datasets*; whether/which models win
is downstream.

## The plan lives in `TO-DO.md` — read it first
`TO-DO.md` is the authoritative design + approval gate. Key locked decisions:
- **Portfolio (all 2D):** 2D Euler Riemann (shock) · Cahn–Hilliard (sharp interface) ·
  Kuramoto–Sivashinsky (smooth **control**).
- **Workflow gate:** generate a *small SAMPLE batch* → **Nicholas (mentor) approves** → only then
  generate at full counts. **Do not generate full datasets before Nicholas signs off.**

## Methodology conventions (don't violate these)
- **LF = a real coarse *consistent* solve.** NEVER downsampled or noised HF (that injects
  Gibbs/aliasing artifacts and invalidates the benchmark). This is the single most important rule.
- **Fidelity ladder:** dyadic **32² → 64² → 128²** (HF = 128²); all levels interpolated up onto
  the HF grid so residuals (HF − LF) are well-defined. Keep raw native-grid LF too (provenance).
- **Condition vector** must be **complete** (those scalars + solver + snapshot time T determine the
  field) and small (≤ ~10). If snapshot time T varies per sample, it must be *in* the vector.
- **Metric panel, not rel-L2 alone:** rel-L2 averages over the smooth bulk and hides blur in the
  thin sharp region. Use the panel in `common/metrics.py` (L∞, Wasserstein-1, interface/shock
  position, high-wavenumber spectral band, conservation, SSIM).
- **Bottom-rung check:** LF must be measurably blurrier than HF for Euler/Cahn–Hilliard, and
  ≈ HF for KS (control). For Cahn–Hilliard, ε is **coupled to the ladder** — 32² must under-resolve
  ε while 128² resolves it.

## Compute policy (RULE)
**Editing happens on either machine; computationally intensive RUNS happen on the box.**
- *Heavy → box only* (`ssh eloise@10.80.6.224`, 4090 GPU): full dataset generation, training,
  large/long/high-resolution solves, anything GPU-bound.
- *Light → either machine*: editing, syntax checks, the explanatory figures, a 1–2 sample smoke
  test. (Note: running anything locally needs a local Python env — the bare system `python3` has
  no numpy; see "Local env" below.)

## Dev workflow — TWO machines, git is the single source of truth
Edit on **either** the Mac or the box, but follow this sync discipline so the two copies never
diverge into a merge conflict:
1. **Pull before you edit or run** on a machine: `git pull` (absorb the other machine's commits).
2. **Commit + push immediately after editing**, on whichever machine you edited:
   `git add -A && git commit -m "…" && git push`.
3. **Never leave uncommitted edits** on one machine while switching to the other.
4. **Don't edit the same file on both machines** before pushing/pulling.

- GitHub: **https://github.com/eloisezeng/SURF_2026** (private). `origin/main` is the truth.
- Claude (this session) edits on the Mac: it pulls at the start of an editing turn and pushes after.
- On the box: `cd SURF_2026/mffp_sharp && bash scripts/setup_env.sh` (once), then
  `git pull && bash scripts/run_sample.sh all`.
- **Data stays on the box**, git-ignored (`data/`, `*.h5`). Only small summaries/figures
  (`data/sample/sample_summary.json`, `data/sample/figures/*.png`) come back for review.
- `gh` CLI lives at `~/.claude/bin/gh` (not on PATH by default); git credential helper is wired to it.

## Local env (for light runs on the Mac)
`.venv/` at the repo root (Python 3.9, git-ignored) has the non-clawpack deps + an editable install
of `mffp_sharp`. `source .venv/bin/activate` then run figures / CH / KS locally. Euler (PyClaw) and
all full generation/training stay on the box.

## The package: `mffp_sharp/`
- `common/` — PDE-agnostic, real implementations: `ladder` (dyadic up-interp), `metrics` (panel),
  `io` (HDF5 in the deck's layout), `sampling` (Latin-hypercube + Schulz-Rinne Riemann configs),
  `visualize` (one-pager review figures).
- `pdes/` — `euler` (PyClaw: Classic vs SharpClaw, **box-only, not yet executed**),
  `cahn_hilliard` & `kuramoto_sivashinsky` (custom **pure-numpy** semi-implicit Fourier solvers,
  validated). py-pde was dropped — its explicit integrator blew up on these stiff 4th-order PDEs.
- `generate.py` — CLI: sample across the ladder → write HDF5 → print bottom-rung check → emit
  figures. Config: `configs/sample.yaml` (every provisional value flagged `(TBD)`).

## Working norms
- This project used the superpowers **brainstorming** flow to design `TO-DO.md`: prefer
  design-then-approve over jumping to code; the sample round exists to de-risk before full compute.
- Be explicit about what is grounded (in the deck / literature) vs. an assumption — the mentor
  relationship depends on not overstating.
