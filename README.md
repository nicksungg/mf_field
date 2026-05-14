# MFFP — Multi-Fidelity Field Prediction (Factory project)

Autonomous research project driven by [`remote-factory`](../akash/remote-factory-main/). The factory's CEO agent evolves new multi-fidelity field-prediction model architectures, trains them on small smoke datasets, and keeps changes that lower the composite nRMSE.

## Layout

```
factory_mffp/
├── factory.md              # research-mode config (goal, scope, guards, eval)
├── data/                   # symlinks to the 17 datasets in ../<dataset>/
├── baselines/
│   └── paper_baselines.json   # FIXED — published numbers per dataset
├── eval/
│   ├── MODEL_CONTRACT.md      # contract every model family must satisfy
│   ├── score.py               # orchestrator: runs all families × smoke datasets
│   ├── smoke_config.json      # which datasets / epochs for the per-cycle loop
│   ├── full_config.json       # all 17 datasets × full epochs for periodic benchmarks
│   ├── run_smoke.sbatch       # SLURM wrapper for the smoke eval (per cycle)
│   ├── run_full.sbatch        # SLURM array for the full benchmark
│   └── launch_full.py         # plan/dispatch helper for the array
├── models/
│   ├── README.md              # how to add a family
│   └── v9_baseline/           # FROZEN — your stacking_v9_multistream
├── scripts/
│   ├── cycle_eval.sh          # what factory.md's run_command calls
│   └── launch_full_benchmark.sh
├── results/                   # per-cycle JSON + history.jsonl (gitignored)
├── checkpoints/               # per-(family, dataset) weights (gitignored)
└── logs/                      # SLURM stdout/stderr (gitignored)
```

## Quick check (no SLURM)

```bash
source /orcd/data/faez/001/nick/mf_field/akash/remote-factory-main/activate-env.sh
cd /orcd/data/faez/001/nick/mf_field/factory_mffp

# Smoke-test the contract on v9_baseline with 2 epochs, on a node that has a GPU
salloc -p mit_normal_gpu --gres=gpu:1 -t 30 --pty bash
python models/v9_baseline/smoke_eval.py \
    --dataset_dir data/ifc_heat --dataset_name ifc_heat \
    --epochs 2 --out /tmp/x.json --ckpt_dir /tmp/c --seed 0
```

## Run one factory cycle

```bash
source /orcd/data/faez/001/nick/mf_field/akash/remote-factory-main/activate-env.sh
factory ceo /orcd/data/faez/001/nick/mf_field/factory_mffp --mode research
```

The CEO will detect research-mode (because `factory.md` has a `## Research Target`), run the loop:
Observe → Hypothesize → Build → Eval (`scripts/cycle_eval.sh`) → Decide.

## Continuous loop

```bash
factory tmux /orcd/data/faez/001/nick/mf_field/factory_mffp --mode research --loop
factory tmux-ls
factory tmux-stop --path /orcd/data/faez/001/nick/mf_field/factory_mffp
```

## Full benchmark on demand

```bash
./scripts/launch_full_benchmark.sh "v9_baseline,my_new_family"
```

## Choosing the partition

The smoke eval defaults to `mit_preemptable` (2-day walltime, many GPU types, but jobs may be preempted; smoke_eval.py resumes from `checkpoints/<family>/<dataset>/last.pt`). Override:

```bash
MFFP_PARTITION=pi_faez MFFP_FALLBACK_PARTITION=mit_normal_gpu \
    factory ceo . --mode research
```
