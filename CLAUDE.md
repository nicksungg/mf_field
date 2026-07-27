# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Research monorepo for **Multi-Fidelity Field Prediction (MFFP)**: predicting a high-fidelity (HF, fine-grid) PDE solution field from cheap low-fidelity (LF, coarse-grid) fields plus a small condition vector, with few HF samples.
It is one git repository (currently a single initial commit) holding three parallel workstreams under three top-level directories.
Almost all heavy artifacts are git-ignored — see `.gitignore`: `*.npz *.npy *.pt *.h5 *.png *.pdf`, `data/`, `.venv/`.
What lives in git is code, configs, sbatch scripts, CSVs, and Markdown; the actual datasets, checkpoints, and figures are regenerable and stay on the compute box.

The three workstreams:

- **`mf_field/`** — the benchmark itself: the local dataset directories, the autonomous model-invention harness (`factory_mffp/`), the v9 reference model (`stacking_v9_multistream/`), and the factory engine (`akash/`).
- **`mf_field_eloise_data/`** — Eloise's dataset-generation work: standalone PDE generators + the `SURF_2026-main/` sub-project (sharp-field datasets, a real Python package with tests). **Has its own `CLAUDE.md` at `SURF_2026-main/CLAUDE.md` — read and obey it when working in that subtree.**
- **`mf_field_extension_data/`** — a further set of 7 non-overlapping PDE datasets with their own solvers, generators, and verification.

## `factory_mffp/` — the core harness (read this first)

This is the heart of the repo.
It is an autonomous "factory" (driven by `akash/remote-factory-main/`, the vendored `remote-factory` engine) whose CEO agent invents new MFFP model architectures, trains them on small smoke datasets, and keeps only changes that lower a composite error metric.
The loop is Observe → Hypothesize → Build → Eval → Decide, configured entirely by `factory.md` (the research-mode spec: goal, scope, guards, eval command, hypothesis budget).

**The bar is the published paper numbers** in `baselines/paper_baselines.json`, *not* v9.
`references/v9_baseline/` is one worked example of MF fusion in a SOTA architecture, kept frozen for side-by-side comparison only.

### Model Family Contract (the central convention)

Every model is a self-contained family directory `models/<family>/` that must expose:

- `manifest.json` — `{ "name", "description", "supports": ["ifc_raw", "npz"], "frozen": bool }`.
- `smoke_eval.py` — CLI with a fixed signature (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`), writing a results JSON whose required keys are `model`, `dataset`, and `splits` (each split has `nRMSE`).

The full contract (signature, JSON schema, checkpoint-resume requirement) is `eval/MODEL_CONTRACT.md`.
Checkpoint resume from `<ckpt_dir>/last.pt` is mandatory because the default SLURM partition (`mit_preemptable`) can preempt any run.
There are ~27 families today (FNO coregionalization/residual/transfer variants, Transolver hybrids, DINO-conditioned, and the FIRE uncertainty-source families).
The `fno_fire_*` families all share `models/_common/` (`fire_core.py`, `fire_methods.py`, `recipe_hash.py`) and differ only in how the LF predictive distribution is obtained.

### How evaluation runs

`eval/score.py` discovers every `models/<family>/` (plus frozen `references/*`), runs each family × each smoke dataset via its `smoke_eval.py`, and aggregates into a leaderboard JSON at `results/smoke_latest.json`.
Results are **cached by `(family, dataset, epochs, seed, code_hash)`** where `code_hash` is a SHA over all `.py` in the family dir — editing any `.py` under a family invalidates its cache; use `--no_cache` to force.
The composite metric (lower is better): mean over datasets of the best model's mean nRMSE on that dataset.
Data is loaded through `data_adapters/loaders.py`, which handles two on-disk layouts: **`ifc_raw`** (`train/fidelity_<F>/{Xs,ys}.npy`, 2-D fields) and **`npz_l*`** (`train_l<i>.npz`/`test_l<i>.npz` with keys `x`,`y`, flat fields, optional `ood/`).

### Guards (from `factory.md` — do not violate)

- Only `models/**` is modifiable. **Never edit** `data/`, `baselines/`, `eval/`, `references/`, `scripts/`, or `factory.md`.
- Never edit `baselines/paper_baselines.json` (fixed published numbers).
- Never delete/rename existing families; add new ones only.
- New families implement architectures **from scratch from the source paper**, not by copying `references/v9_baseline/`; each cites its source in `models/<family>/INSPIRATION.md`.

## Datasets and multi-fidelity methodology

`mf_field/datasets_summary.csv` is the canonical per-dataset table (paper, resolutions, N_train/N_test, license).
Local dataset dirs live as siblings under `mf_field/` (`era5`, `pm_test`, `fluid`, `heat_local`, `ifc_heat`, `ifc_poisson`, `poisson_local`, `sharp_generated`, …); `factory_mffp/data/` symlinks to them.
Fields are either genuine 2-D `(H, W)` (ifc_raw) or flattened `(n_cells,)` (npz); the npz generation format is `params (N,d)`, `lf (N,…)`, `hf (N,…)`, `param_names (d,)` with **aligned/nested** LF↔HF (same parameter vector, coarse vs fine grid).

Non-negotiable methodology rules (see `SURF_2026-main/CLAUDE.md` for the full statement):

- **LF is always a real coarse *consistent* solve — never downsampled or noised HF.** Downsampling injects Gibbs/aliasing artifacts and invalidates the benchmark. This is the single most important rule.
- Fidelity levels are interpolated onto the HF grid so residuals `HF − LF` are well-defined; keep raw native-grid LF for provenance.
- The condition vector must be *complete* (those scalars + solver + snapshot time fully determine the field) and small (≤ ~10).
- Prefer a **metric panel**, not rel-L2 alone: rel-L2 averages over the smooth bulk and hides blur in thin sharp regions.

## Common commands

Heavy work (generation, training, full benchmarks) runs on a SLURM GPU cluster; the factory docs assume the cluster root `/orcd/data/faez/001/nick/mf_field/` where dataset dirs are siblings of `factory_mffp/`.
Local editing/syntax/figure work happens on the Mac.

```bash
# --- Sharp-field package tests (the one place with a real test suite: 25 pytest files) ---
cd mf_field_eloise_data/SURF_2026-main/mffp_sharp
source ../.venv/bin/activate        # repo-root venv with numpy/scipy/h5py/skimage/matplotlib
pytest                              # all tests
pytest tests/test_cahn_hilliard.py # a single test file
bash scripts/verify.sh             # solver-legitimacy verification

# --- Run one model family end-to-end (contract smoke, no SLURM) ---
cd mf_field/factory_mffp
python models/<family>/smoke_eval.py \
    --dataset_dir data/ifc_heat --dataset_name ifc_heat \
    --epochs 2 --out /tmp/x.json --ckpt_dir /tmp/c --seed 0

# --- Orchestrate all families over the smoke datasets ---
python eval/score.py --no_cache --families <family>   # confirm a new family is picked up

# --- One autonomous factory cycle (needs the remote-factory env sourced) ---
source mf_field/akash/remote-factory-main/activate-env.sh
factory ceo <abs path to factory_mffp> --mode research

# --- Heavy jobs go through SLURM (examples) ---
sbatch mf_field/factory_mffp/eval/run_smoke.sbatch          # full smoke eval
sbatch mf_field_eloise_data/generate_sharp.sbatch          # dataset generation
```

Dataset generation entry points: `mf_field/generate_all_datasets.py`, the `mf_field_eloise_data/generate_*.py` + `ablation_*.json` configs, and `mf_field_extension_data/generate_datasets.py` (with `solvers.py` and `verify.py`).

## Nested guidance to defer to

Two subtrees carry their own `CLAUDE.md` that governs them and takes precedence when you are working inside them:

- `mf_field_eloise_data/SURF_2026-main/CLAUDE.md` — the sharp-field dataset project: two-machine git sync discipline, the sample-round approval gate (mentor sign-off before full generation), and the LF-methodology rules.
- `mf_field/akash/remote-factory-main/CLAUDE.md` — the `remote-factory` engine that drives the factory.

`factory_mffp/HOWTO.md` is the operational runbook for the factory (setup, cycles, tmux loop, full benchmark, knobs like `MFFP_PARTITION`).
