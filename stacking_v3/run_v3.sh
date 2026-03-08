#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run_v3.sh  —  stacking_v3 MFTransolver training pipeline
#
# Single end-to-end phase: the Multi-Fidelity Transolver is trained directly
# with both the 2-D LF surface pressure (physics-context) and 3-D HF surface
# pressure (targets) in each batch.  No separate pre-training stage is needed.
#
# The norm stats are computed once and shared across all runs
# (saved to checkpoints/global_norm_stats.json).
#
# Pause/Resume
# ─────────────
#   Kill the process at any time.  Re-run the same command: each run saves
#   a resume_state.pth every 50 epochs and auto-resumes from it.
#
# Usage
# ─────
#   bash run_v3.sh                          # full pipeline (all fractions)
#   bash run_v3.sh frac010                  # single run
#   bash run_v3.sh frac010 frac020          # multiple runs
#
# Logs
# ────
#   logs/train_<run>.log     logs/eval_all.log
# ─────────────────────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")"
mkdir -p logs checkpoints

PYTHON="$(which python3) -u"
EVAL_LOG="logs/eval_all.log"

# ── Training hyper-parameters ─────────────────────────────────────────────────
TRAIN_COMMON="--epochs 2500 --batch_size 8 --lr 3e-4 \
              --n_lf 2048 --n_hf 8192 \
              --hidden_dim 256 --n_slices 32 --num_heads 8 \
              --encoder_layers 3 --residual_layers 3 \
              --pos_enc_freqs 6"

# ── Fraction map ──────────────────────────────────────────────────────────────
declare -A FRAC
FRAC[frac0001]="0.001"
FRAC[frac001]="0.01"
FRAC[frac005]="0.05"
FRAC[frac010]="0.10"
FRAC[frac020]="0.20"

ALL_RUNS=(frac0001 frac001 frac005 frac010 frac020)

# ── Parse arguments ───────────────────────────────────────────────────────────
RUN_LIST=()

if [ $# -eq 0 ]; then
    RUN_LIST=("${ALL_RUNS[@]}")
else
    for arg in "$@"; do
        if [ -n "${FRAC[$arg]}" ]; then
            RUN_LIST+=("$arg")
        else
            echo "[WARN] Unknown argument '$arg' — skipping."
        fi
    done
fi

# ─────────────────────────────────────────────────────────────────────────────
# Training — one run per fraction
# ─────────────────────────────────────────────────────────────────────────────
for RUN in "${RUN_LIST[@]}"; do
    F="${FRAC[$RUN]}"
    if [ -z "$F" ]; then
        echo "[WARN] Unknown run '$RUN', skipping."
        continue
    fi

    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Training MFTransolver — ${RUN}  (frac=${F})"
    echo "  Resume-state saved every 50 epochs → checkpoints/${RUN}/resume_state.pth"
    echo "══════════════════════════════════════════════════════════════"

    $PYTHON train_v3.py $TRAIN_COMMON \
        --run_name "$RUN" --train_frac "$F" \
        >> "logs/train_${RUN}.log" 2>&1

    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  ${RUN} DONE"
done

# ─────────────────────────────────────────────────────────────────────────────
# Evaluation — all completed runs
# ─────────────────────────────────────────────────────────────────────────────
if [ ${#RUN_LIST[@]} -gt 0 ]; then
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Evaluating runs"
    echo "══════════════════════════════════════════════════════════════"

    for RUN in "${RUN_LIST[@]}"; do
        CKPT="checkpoints/${RUN}"
        if [ ! -d "$CKPT" ]; then
            echo "  [SKIP] $RUN — checkpoint dir not found"
            continue
        fi

        for W in film_best film_final; do
            if [ ! -f "${CKPT}/${W}.pth" ]; then
                echo "  [SKIP] ${RUN}/${W}.pth not found"
                continue
            fi
            echo "  Evaluating ${RUN}  weights=${W} ..."
            $PYTHON eval_v3.py \
                --run_name "$RUN" --weights "${W}.pth" --split test \
                >> "$EVAL_LOG" 2>&1
        done
    done

    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Evaluation DONE"
    echo "  Results → ${EVAL_LOG}"
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  All requested runs complete."
echo "══════════════════════════════════════════════════════════════"
