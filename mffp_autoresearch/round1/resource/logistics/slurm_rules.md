# SLURM rules — MFFP Round 1 (Caltech HPC)

Single source of truth for job submission. Builders write scripts from the
templates in `example_scripts/`; the ORCHESTRATOR submits, never the builder.

## 1. Header conventions

```bash
#SBATCH --job-name=r1-{stream}-B{N}-s{seed}     # the maintainer matches on this
#SBATCH --partition=gpu                          # from project.yaml sbatch.partition
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:p100:1                        # typed gres MANDATORY; see §3
#SBATCH --mem=32G
#SBATCH --time=04:00:00                          # from the timing ledger; see §4
#SBATCH --output=<outputs_root>/{stream}/B{N}/slurm/%x_%j.out
#SBATCH --error=<outputs_root>/{stream}/B{N}/slurm/%x_%j.err
```

`set -euo pipefail` at the top of every script body. `mkdir -p` the slurm/
and eval/ output dirs before use. Activate `${PROJECT_ROOT}/.venv`.

## 2. What a job runs

One `score_panel.py` invocation per (dataset-set, seed) — train+eval is one
command in this project (program.md §9). No train→eval dependency chains.
`submit.sh` submits seed 0 only; `submit_seeds_2_3.sh` submits seeds 1 and 2
in parallel (orchestrator calls it only after the seed-0 gate).

## 3. GPU selection

Typed gres is mandatory (`gpu:<token>:1`); bare `gpu:1` is not allowed.
Check live availability before choosing:

```bash
sinfo -p gpu -t idle,mix -o "%D %G %T"
```

- **Default: `p100`** — most abundant (46 nodes × 4), fine for 200-epoch
  smoke-tier runs of FNO-scale models (verified: contract smoke ran on P100,
  torch 2.6 cu124). 16 GB memory — keep batch sizes modest.
- **Fast tier when free: `nvidia_h200` ≥ `h100` ≥ `nvidia_l40s`** — use for
  batch-0-style arrays or when the timing ledger shows a p100 run would
  exceed 6 h. Note some h200 nodes sit in reservations; if a job pends with
  `ReqNodeNotAvail`/reservation reasons, fall back to p100.
- **Never `v100`** (old driver stack; round-5 lesson kept).
- Do NOT use `--constraint=<gpu>` or invented partitions.

## 4. Walltime

`--time` from `${ROUND_ROOT}/state/timing_ledger.json`: closest prior entry
(same datasets/epochs, same gpu_type; p100 runs ~2–4× fast-tier) + ~50%
headroom. No analog → 04:00:00 (panel × 200 epochs) / 00:30:00 (contract
tier). Oversized `--time` blocks backfill and pends forever at low priority —
right-size (round-5 lesson).

## 5. Preemption / resume

The partition can preempt or nodes can drain. Every family MUST resume from
`<ckpt_dir>/last.pt` (contract requirement, program.md §5.8). A job that
restarts from epoch 0 after requeue is an ALGO bug. Scripts should be
idempotent — safe to resubmit.

## 6. Hygiene

- Logs stay under `<outputs_root>/{stream}/B{N}/slurm/` — never the worktree.
- One job name = one card+seed; never reuse names across cards.
- Before declaring a job vanished: empty `squeue` can be transient — confirm
  with `sacct -j <id>`.
- `scancel` only your own `r1-*` jobs, and only the orchestrator does it.
