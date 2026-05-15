# MFFP — Multi-Fidelity Field Prediction Research Project

## Goal
Invent new multi-fidelity field-prediction model families that beat the published paper nRMSE numbers in `baselines/paper_baselines.json` on as many of the 17 benchmark datasets in `data/` as possible. The bar is the **paper numbers**, not v9 — v9_baseline is one worked example of incorporating multi-fidelity ideas into a SOTA architecture, kept in-tree as a reference implementation only.

## Scope
### Modifiable
- models/**
- !models/v9_baseline/**

## Guards
- Do not modify anything under `data/`, `baselines/`, `eval/`, or `models/v9_baseline/`.
- Do not edit `baselines/paper_baselines.json` — these are fixed reference numbers from the published papers.
- Do not delete or rename existing model families. Add new ones in `models/<new_family>/`.
- Every new model family MUST satisfy `eval/MODEL_CONTRACT.md` (manifest.json + smoke_eval.py with the specified signature and JSON schema).
- New family code must implement architectures from scratch from the source paper(s), not from `models/v9_baseline/`. v9 is one of many references, not the template.

## Research Target
- objective: minimize composite_nRMSE across all smoke datasets, eventually all 17 benchmark datasets
- metric: metric_value
- target: 0.0
- run_command: bash scripts/cycle_eval.sh
- result_path: results/smoke_latest.json
- result_parser: json
- timeout: 14400

## Mutable Surfaces
- models/*/manifest.json
- models/*/smoke_eval.py
- models/*/**/*.py

## Fixed Surfaces
- data/**
- baselines/**
- eval/**
- models/v9_baseline/**
- factory.md
- README.md

## Research Constraints
- Each new model family must cite the paper(s) that inspired it in `models/<family>/INSPIRATION.md` (one paragraph + bibtex_keys from `papers_summary.csv` and any other papers found by the Researcher). If the inspiration paper is missing from `papers_summary.csv`, append a row.
- Researcher should actively expand the literature beyond `papers_summary.csv` — search for current MF surrogate / multi-fidelity field prediction work (graph operators, neural operators, in-context regression, foundation models for tabular/scientific data, hierarchical Gaussian processes, residual stacking, autoencoder fusion, etc.). Cite findings in `models/<family>/INSPIRATION.md`.
- Per-cycle smoke eval wall time must remain under ~30 minutes on a single H100. If a hypothesis needs more, reduce model size for the smoke pass and document the full-config in `models/<family>/full_config.json`.
- New families must support at least the `ifc_raw` dataset loader (smoke datasets are `ifc_heat` and `ifc_poisson`).
- The Builder MUST verify a fresh `models/<family>/smoke_eval.py` runs end-to-end with `--epochs 2 --dataset_dir data/ifc_heat --out /tmp/x.json --ckpt_dir /tmp/c --seed 0` before declaring the experiment ready for the orchestrator.
- Do not call out to any external API or download weights from the internet at eval time.

## Hypothesis Budget
- min_growth: 1
- max_new: 2

## Eval Weights
- hygiene: 0.10
- growth: 0.10
- project: 0.80

## Project Eval
- name: composite_nRMSE
  command: bash scripts/cycle_eval.sh
  parse: json
  weight: 1.0
  timeout: 14400
  description: Submit smoke eval to SLURM via sbatch --wait, return composite_nRMSE (lower is better).

## Smoke Test
```bash
.venv/bin/python -c "import json; d = json.loads(open('results/smoke_latest.json').read()); assert 'metric_value' in d; print('OK', d['metric_value'])"
```
