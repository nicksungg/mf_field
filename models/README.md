# Model Families

Each model family is a self-contained directory under `models/` that satisfies the contract in `eval/MODEL_CONTRACT.md`:

```
models/<family>/
├── manifest.json
├── smoke_eval.py
└── (anything else: model.py, train.py, configs, etc.)
```

## Conventions

- **Family name** = directory name (snake_case).
- **`manifest.json` `frozen: true`** → the orchestrator runs the family but the factory must not edit any file inside. `v9_baseline` is frozen.
- **Cache** — `eval/score.py` keys results by `(family_name, dataset, epochs, seed, code_hash)`. If you change any `.py` under the family the hash changes and the cached result is invalidated.
- **Resume** — every smoke_eval.py must check `--ckpt_dir/last.pt` and resume. SLURM preemption on `mit_preemptable` is the default expectation.

## Adding a new family

1. `mkdir models/<family>` and write `manifest.json` + `smoke_eval.py`.
2. Make sure `python smoke_eval.py --dataset_dir ../../data/ifc_heat --dataset_name ifc_heat --epochs 5 --out /tmp/x.json --ckpt_dir /tmp/ckpt --seed 0` produces a valid contract JSON.
3. Run `python eval/score.py --no_cache --families <family>` to confirm the orchestrator picks it up.
4. Open a PR (or let the factory's Builder open it) — the next research cycle will benchmark you.

## Inspiration sources (read but do NOT copy/clone — Builder must implement from scratch)

The factory's Researcher should consult:

- `papers_summary.csv` — the literature catalog (li2022ifc, niu2024mfrnp, taghizadeh2024mfgnn, gladstone2024mfgunet, songia2026mfgraphns, kent2026noisemf, etc.)
- `paper_baselines.json` — what to beat per dataset
- `models/v9_baseline/model_v9.py` — current SOTA-on-our-bench architecture (point-wise gated fusion + transolver-style slicing)

Promising directions worth exploring (non-exhaustive — the Strategist will pick):

- Multi-fidelity Fourier neural operators (FNO/UNO/F-FNO) with cross-fidelity transfer
- Multi-fidelity DeepONet variants (MF-DeepONet, MF-PIDeepONet)
- Coregionalization-style latent priors (li2022ifc IFC)
- Graph-based mesh operators (MFGNN, MF-GUNet, MFGraphNS) for irregular geometries
- Operator-Transformer hybrids (Transolver, OFormer) with explicit fidelity tokens
- Residual-stack / boosting style (MFRNP, stacked GP-as-prior)
- Latent diffusion / score-matching priors over the residual
- Implicit neural representations (SIREN/ FilmNet) conditioned on fidelity index
