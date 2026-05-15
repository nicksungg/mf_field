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

## What "the bar" is

The optimization target (`composite_nRMSE` in `eval/score.py`) only ranks model families against each other on our smoke datasets. The **published paper numbers** in `baselines/paper_baselines.json` are the actual yardstick — a family is "interesting" once it matches or beats the source paper on the same dataset. The leaderboard appended to each cycle's results JSON shows both ours and the paper number side-by-side.

`models/v9_baseline/` is **not** the baseline to beat — it's a worked example of how multi-fidelity fusion can be plugged into a SOTA point-cloud transformer (gated fusion + Transolver-style slicing). It runs every cycle for direct comparison, but its presence is purely for reference.

## Inspiration sources (read but do NOT copy/clone — Builder must implement from scratch)

The factory's Researcher should consult:

- `../papers_summary.csv` — local literature catalog (li2022ifc, niu2024mfrnp, taghizadeh2024mfgnn, gladstone2024mfgunet, songia2026mfgraphns, kent2026noisemf, …) — and **expand it** with new papers found via WebSearch.
- `../baselines/paper_baselines.json` — published numbers per dataset (the bar).
- `models/v9_baseline/model_v9.py` — one worked example, not the template.

Promising directions worth exploring (non-exhaustive — the Strategist will pick):

- **Multi-fidelity neural operators** — FNO/UNO/F-FNO with cross-fidelity transfer, transfer-learning across fidelities (lyu2023fno).
- **Multi-fidelity DeepONet variants** — MF-DeepONet, MF-PIDeepONet (yang2025mfdeeponet).
- **Coregionalization-style latent priors** — li2022ifc Infinite-Fidelity Coregionalization.
- **Graph-based mesh operators** for irregular geometries — MFGNN (taghizadeh2024mfgnn), MF-GUNet (gladstone2024mfgunet), MFGraphNS (songia2026mfgraphns).
- **Operator-Transformer hybrids** — Transolver, OFormer with explicit fidelity tokens.
- **Residual-stack / boosting** — MFRNP (niu2024mfrnp), stacked-GP-as-prior.
- **In-context regression with tabular foundation models** — **FIRE: Multi-fidelity Regression with Distribution-conditioned In-context Learning using Tabular Foundation Models** — Nick's prior work on framing MF regression as in-context learning over a foundation model. Cite as `sung2026fire` (or whatever bibtex key gets added to `papers_summary.csv` once Researcher expands it). Strong candidate to adapt to field prediction by tokenizing patches/coordinates.
- **Latent diffusion / score-matching priors** over the residual field.
- **Implicit neural representations** (SIREN, FilmNet) conditioned on fidelity index.
- **Generative / probabilistic surrogates** — zeng2026genmf transfer-learning, kent2026noisemf noise-robust MF surrogates.
- **Bayesian/PINN MF hybrids** — imanov2026mfbpinn, penwarden2022mfpinns, perdikaris2017nonlinear nonlinear information fusion.

The Researcher is encouraged to use WebSearch / WebFetch to find papers beyond this list and add bibtex rows to `../papers_summary.csv` when citing them.
