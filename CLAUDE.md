# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

MFFP (Multi-Fidelity Field Prediction) is an **autonomous research project** driven by the
`remote-factory` CEO agent (config in `factory.md`). The goal: invent new multi-fidelity
field-prediction model *families* that beat the published paper nRMSE numbers in
`baselines/paper_baselines.json` across the 17 benchmark datasets in `data/`.

"Multi-fidelity" here means each task gives abundant cheap **low-fidelity (LF)** data and scarce
expensive **high-fidelity (HF)** data; a model must fuse them to predict the HF field. Families
differ almost entirely in *how* they fuse — the backbone (a Fourier Neural Operator) is held
roughly constant so the comparison isolates the MF mechanism. See `model/README.md` for the
full model-zoo leaderboard and per-family TL;DRs.

## Where the research writing lives

All reports, proposals, plans, and raw notes are filed under `docs/` — start at `docs/README.md`,
which indexes every document with its date and status. In short: `docs/reports/` (finished
deliverables + their figure directories), `docs/proposals/` (model ideas under consideration),
`docs/planning/` (autoresearch loop design), `docs/notes/` (raw question lists and idea seeds),
`docs/external/` (papers and decks from outside this repo). None of it is read by the eval or
factory pipeline. Only `README.md`, `CLAUDE.md`, `factory.md`, and `HOWTO.md` stay at the root.

## The one rule that governs everything: mutable vs fixed surfaces

`factory.md` declares what may change. **Only `models/**` is modifiable.** Treat everything
else as read-only unless the user explicitly overrides:

- **Do not** modify `data/`, `baselines/`, `eval/`, `references/`, `scripts/`, `factory.md`, `README.md`.
- **Do not** edit `baselines/paper_baselines.json` — these are fixed published reference numbers (the actual bar).
- **Do not** delete or rename existing model families. Add new work as `models/<new_family>/`.
- New families must be implemented **from scratch from the source paper(s)**, not copied from
  `references/v9_baseline/` (which is one worked example, not a template).
- Each new family needs `models/<family>/INSPIRATION.md` citing the paper(s) (bibtex keys from
  `../papers_summary.csv`; append rows there if a cited paper is missing).
- No external API calls or weight downloads at eval time. Smoke eval must stay **≤ ~30 min on one H100**.

## The model-family contract (`eval/MODEL_CONTRACT.md`)

Every family at `models/<family>/` must expose exactly:

- `manifest.json` — `{ "name", "description", "supports": ["ifc_raw"|"npz_l"...], "external": false, "paper": ... }`.
  `"frozen": true` means the orchestrator runs it but nothing inside may be edited (`v9_baseline` is frozen).
- `smoke_eval.py` — fixed CLI: `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`.
  Exit 0 on success; writes a results JSON with `model`, `dataset`, and `splits` (each split has `nRMSE`).
- **Checkpoint resume is mandatory** — read/write `ckpt_dir/last.pt`; SLURM `mit_preemptable` jobs get
  preempted and requeued, so without resume every preemption wastes the run.

### Critical import convention (the main gotcha)

`smoke_eval.py` puts its own directory **and** the repo root on `sys.path`, then does:

```python
from model import FNO2d, FNO2dAug, param_count   # the family's OWN model.py (vendored backbone)
from data_adapters import load_mf_dataset          # SHARED repo-root package (fixed surface)
from data_adapters.geometry import resolve_grid
from data_adapters.metrics import finalize_and_write
```

So `model` is **per-family** (each family vendors its own `model.py` backbone), while
`data_adapters` is the **shared** data-loader / geometry / metrics layer that all families import
and must not reimplement. Use `resolve_grid` for fidelity→grid mapping and `finalize_and_write`
to emit the contract JSON (it computes per-sample relative-L2 with bootstrap CIs).

> **Note on this git checkout:** only `data_adapters/npz_compat.py` and `model/README.md` are
> tracked here. The runnable shared internals (`data_adapters/__init__.py`, `geometry.py`,
> `metrics.py`) and the symlinked `data/` contents live in the cluster working tree at the path in
> `scripts/env.sh` (`/orcd/data/faez/001/nick/mf_field/factory_mffp`). `smoke_eval.py` therefore
> runs there, not from a bare clone.

## Shared code

- `models/_common/` — shared core for the FIRE-family UQ ablation. `fire_core.py` holds the
  geometry-general FNO backbone + the shared residual runner; `fire_methods.py` holds one class
  per uncertainty source (snapshot / SWAG / batch-ensemble / quantile / IQN / MDN / Laplace / DKL-GP).
  Every FIRE family produces the same per-pixel LF summary fields `[mu, sigma, q10, q50, q90]`,
  conditions a residual FNO on them, and predicts `HF = mu_LF + delta`; families differ only in
  *how* the LF distribution is obtained.
- `data_adapters/npz_compat.py` — compatibility shim letting legacy `ifc_raw` loaders read newer
  `npz_l` datasets without on-disk conversion.

## Eval / scoring flow

`eval/score.py` is the orchestrator: discovers all `models/*` families (plus frozen
`references/*`), runs each family × each smoke dataset as a subprocess, and aggregates into
`composite_nRMSE` = **geomean over datasets of the best-model-per-dataset nRMSE** (geomean is
scale-invariant so one bad dataset can't dominate). It also emits `vs_paper` (per-dataset
comparison vs `baselines/paper_baselines.json`) — the optimization metric does *not* use paper
numbers, but `vs_paper`/`n_datasets_beating_paper` tells you whether SOTA was reached.

**Caching:** results are keyed by `(family, dataset, epochs, seed, code_hash)` where `code_hash`
is a sha256 over all `*.py` in the family dir. Changing any `.py` invalidates the cached result.
Cached results live in `results/raw/<tag>.json` (gitignored).

## Common commands

Run from the project root, after `source scripts/env.sh` (sets `$MFFP_PY` = project venv python,
loads the cluster module, etc.). Substitute `$MFFP_PY` for `python` on the cluster.

```bash
# Smoke-test ONE family end-to-end (this is the Builder's required pre-flight check):
python models/<family>/smoke_eval.py \
    --dataset_dir data/ifc_heat --dataset_name ifc_heat \
    --epochs 2 --out /tmp/x.json --ckpt_dir /tmp/c --seed 0

# Run the orchestrator on a subset, bypassing cache:
python eval/score.py --no_cache --families <family>            # or comma-separated list

# One factory cycle's eval (cache-first local pass, else submits eval/run_smoke.sbatch --wait):
bash scripts/cycle_eval.sh

# Full benchmark across all 17 datasets (SLURM array):
./scripts/launch_full_benchmark.sh "v9_baseline,<family1>,<family2>"

# Drive the autonomous research loop (factory CEO):
factory ceo . --mode research                                   # one cycle
factory tmux . --mode research --loop                           # continuous

# Reporting helpers:
python bench/status.py            # current run status
python bench/summary_report.py    # leaderboard summary
```

Smoke config (datasets, epochs, seed, per-call timeout, primary metric) lives in
`eval/smoke_config.json`; the full 17-dataset config in `eval/full_config.json`. Per-cycle
defaults: datasets `ifc_heat` + `ifc_poisson`, 200 epochs, seed 42, geomean `composite_nRMSE`
(lower is better).

## Environment

- Two virtualenvs: the **factory** venv runs the `factory` CLI; the **project** `.venv`
  (`$MFFP_PY`) has torch/numpy/pandas for model code. Both are sourced via `scripts/env.sh`.
- SLURM partitions are selected via `MFFP_PARTITION` (default `mit_preemptable`) and
  `MFFP_FALLBACK_PARTITION` (default `mit_normal_gpu`).
- Gitignored runtime dirs: `results/raw/`, `results/raw_full/`, `results/smoke_latest.json`,
  `results/history.jsonl`, `checkpoints/`, `logs/`, `.venv/`.
