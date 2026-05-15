#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Per-cycle smoke eval. Submitted by `factory.md` -> Research Target's run_command
# via `sbatch --wait eval/run_smoke.sbatch`.
#
# Partition strategy:
#   PARTITION=pi_faez       — try first if user explicitly sets it
#   PARTITION=mit_preemptable (default) — many GPU types, 2-day walltime, may be preempted
#   PARTITION=mit_normal_gpu (fallback) — 6h walltime, less likely to be preempted
#
# Preemption resilience:
#   --requeue + checkpoint resumption inside smoke_eval.py.
#   Each model family must save checkpoints periodically (see MODEL_CONTRACT.md).
# ─────────────────────────────────────────────────────────────────────────────
#SBATCH --job-name=mffp-smoke
#SBATCH --partition=mit_preemptable
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --requeue
#SBATCH --signal=B:USR1@90
#SBATCH --output=logs/smoke_%j.out
#SBATCH --error=logs/smoke_%j.err

set -euo pipefail
cd "$(dirname "$(realpath "$0")")/.."

mkdir -p logs results checkpoints

# Load python + paths
source scripts/env.sh
PY="$MFFP_PY"

# Trap USR1 (sent ~90s before walltime kills us) so we exit cleanly with code 0
# and SLURM requeues the job. Checkpoints inside smoke_eval.py save us.
on_usr1() {
    echo "[$(date)] USR1 received — letting current iteration save its checkpoint then exiting (will requeue)"
    pkill -USR1 -P $$ || true
    sleep 30
    exit 0
}
trap on_usr1 USR1

echo "[$(date)] Starting smoke eval on $(hostname) | partition=$SLURM_JOB_PARTITION | gpu=$(nvidia-smi -L 2>/dev/null | head -1)"
"$PY" eval/score.py \
    --config eval/smoke_config.json \
    --out results/smoke_latest.json
RC=$?
echo "[$(date)] score.py exited rc=$RC"
exit $RC
