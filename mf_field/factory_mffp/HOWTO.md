# How to drive this project

## 0. One-time setup checks

```bash
# Source the activation snippets (factory CLI + claude CLI on PATH)
source /orcd/data/faez/001/nick/mf_field/akash/remote-factory-main/activate-env.sh

# Authenticate Claude Code (one time, stores creds in ~/.config/claude-code/)
#   Option A — interactive browser flow:
claude
#   Option B — API key in the env (works headless):
export ANTHROPIC_API_KEY=sk-ant-...
```

## 1. Sanity check the eval contract on a GPU

Run a tiny 2-epoch v9 smoke just to confirm the chain works:

```bash
cd /orcd/data/faez/001/nick/mf_field/factory_mffp
sbatch scripts/contract_smoke_test.sbatch
# wait for it to finish, then:
cat results/contract_test.json
```

Should look like:
```json
{
  "model": "v9_baseline",
  "dataset": "ifc_heat",
  "splits": {
    "test": { "nRMSE": 0.xxx, "n_samples": 128 },
    ...
  },
  ...
}
```

## 2. Establish the baseline number for v9

Run the smoke score once to get a `composite_nRMSE` for v9 — the floor the factory is trying to beat:

```bash
sbatch scripts/contract_smoke_test.sbatch    # already ran above? skip
sbatch eval/run_smoke.sbatch                 # full smoke (ifc_heat + ifc_poisson, 200 epochs)
# wait, then:
cat results/smoke_latest.json | head -40
```

This caches per-(family, dataset) results in `results/raw/<tag>.json` and `checkpoints/<family>/<dataset>/`. Subsequent score.py runs skip already-computed (family, dataset) pairs unless `--no_cache`.

## 3. Kick off one factory cycle (interactive)

```bash
factory ceo /orcd/data/faez/001/nick/mf_field/factory_mffp --mode research
```

The CEO will:
1. Read `factory.md` and detect research mode (because `## Research Target` is present).
2. **Observe** — Researcher reads `papers_summary.csv`, `references/v9_baseline/model_v9.py`, the dataset README, prior `results/history.jsonl`.
3. **Hypothesize** — Strategist proposes 1–2 hypotheses (each = a new model family in `models/<family>/`).
4. **Build** — Builder implements `models/<family>/manifest.json` + `smoke_eval.py`.
5. **Eval** — runs `bash scripts/cycle_eval.sh` → submits `eval/run_smoke.sbatch` → blocks until done → reads `results/smoke_latest.json`.
6. **Decide** — keep if `composite_nRMSE` improved, revert otherwise.

Per-cycle wall time = SLURM queue + ~20 min compute + factory agent overhead. Plan for 30 min – several hours per cycle depending on partition load.

## 4. Continuous loop in tmux

```bash
factory tmux /orcd/data/faez/001/nick/mf_field/factory_mffp --mode research --loop
factory tmux-ls
factory tmux-stop --path /orcd/data/faez/001/nick/mf_field/factory_mffp
```

## 5. Full benchmark on demand

After several cycles you'll have a few model families. Bench all of them across all 17 datasets (parallel SLURM array):

```bash
./scripts/launch_full_benchmark.sh "v9_baseline,$(ls models | grep -v v9_baseline | tr '\n' ',' | sed 's/,$//')"
```

Results land in `results/raw_full/<tag>.json`. Aggregate them yourself or write a follow-up script.

## 6. Debugging

- `tail -f logs/smoke_*.out` — live SLURM stdout
- `factory history /orcd/data/faez/001/nick/mf_field/factory_mffp` — experiment history table
- `factory dashboard` — web dashboard on :8420 with live agent activity
- `cat results/history.jsonl | jq .metric_value` — track composite_nRMSE over time
- Bad eval result? Check `results/raw/<family>__<dataset>__*.json` for the raw contract output.

## 7. Knobs

| Knob | Where | Default | Note |
|---|---|---|---|
| `MFFP_PARTITION` | env | `mit_preemptable` | Partition for the smoke eval. |
| `MFFP_FALLBACK_PARTITION` | env | `mit_normal_gpu` | Used if primary fails. |
| smoke epochs | `eval/smoke_config.json` | 200 | Lower for faster cycles. |
| smoke datasets | `eval/smoke_config.json` | ifc_heat, ifc_poisson | Add more if you want broader coverage per cycle. |
| primary metric | `eval/smoke_config.json` | composite_nRMSE | Lower is better. |
