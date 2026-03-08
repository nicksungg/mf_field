#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run_v2.sh  —  Full stacking_v2 training pipeline
#
# Stages
# ──────
#   Phase 1  LF pre-training on 2-D car-wall surface data (z = 0)
#   Phase 3  HF fine-tuning for each data fraction with frozen middle layers
#   Eval     Evaluation of each Phase-3 run (film_best + film_final)
#
# Pause/Resume
# ─────────────
#   Kill the process at any time.  Re-run with the same arguments.
#   Each phase saves a resume_state.pth every 50 epochs and resumes
#   automatically from the last checkpoint.
#
# Usage
# ─────
#   bash run_v2.sh                          # full pipeline (all fractions)
#   bash run_v2.sh phase1                   # Phase 1 only
#   bash run_v2.sh frac010                  # Phase 3 frac010 only (phase1 must exist)
#   bash run_v2.sh frac010 frac020          # multiple Phase-3 fractions
#   bash run_v2.sh phase1 frac010 frac020   # phase1 + subset of fine-tunes
#
# Logs
# ───
#   logs/phase1.log          logs/train_<run>.log     logs/eval_all.log
# ─────────────────────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")"
mkdir -p logs

PYTHON="$(which python3) -u"
PHASE1_DIR="checkpoints/phase1"
EVAL_LOG="logs/eval_all.log"

# ── Phase 1 hyper-parameters ──────────────────────────────────────────────────
P1_COMMON="--epochs 5000 --batch_size 32 --lr 5e-4 --n_points 4096 \
           --hidden_dim 512 --num_layers 8 --extra_layers 5 \
           --z_noise_std 0.05"

# ── Phase 3 hyper-parameters ──────────────────────────────────────────────────
P3_COMMON="--epochs 2500 --batch_size 16 --lr 1e-4 --n_points 8192 \
           --freeze_start 2 --freeze_end 5 \
           --phase1_dir ${PHASE1_DIR} --phase1_weights film_best.pth"

# ── Fraction map ──────────────────────────────────────────────────────────────
declare -A FRAC
FRAC[frac0001]="0.001"
FRAC[frac001]="0.01"
FRAC[frac005]="0.05"
FRAC[frac010]="0.10"
FRAC[frac020]="0.20"

ALL_P3_RUNS=(frac0001 frac001 frac005 frac010 frac020)

# ── Parse arguments ──────────────────────────────────────────────────────────
RUN_PHASE1=false
RUN_P3_RUNS=()

if [ $# -eq 0 ]; then
    # Default: full pipeline
    RUN_PHASE1=true
    RUN_P3_RUNS=("${ALL_P3_RUNS[@]}")
else
    for arg in "$@"; do
        if [ "$arg" = "phase1" ]; then
            RUN_PHASE1=true
        elif [ -n "${FRAC[$arg]}" ]; then
            RUN_P3_RUNS+=("$arg")
        else
            echo "[WARN] Unknown argument '$arg' — skipping."
        fi
    done
fi

# ─────────────────────────────────────────────────────────────────────────────
# Phase 1 — LF Pre-training
# ─────────────────────────────────────────────────────────────────────────────
if [ "$RUN_PHASE1" = true ]; then
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Phase 1 — LF Pre-training"
    echo "  Resume-state saved every 50 epochs → ${PHASE1_DIR}/resume_state.pth"
    echo "══════════════════════════════════════════════════════════════"
    $PYTHON train_phase1.py $P1_COMMON >> logs/phase1.log 2>&1
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Phase 1 DONE"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Phase 3 — HF Fine-tuning (one run per fraction)
# ─────────────────────────────────────────────────────────────────────────────
for RUN in "${RUN_P3_RUNS[@]}"; do
    F="${FRAC[$RUN]}"
    if [ -z "$F" ]; then
        echo "[WARN] Unknown run '$RUN', skipping."
        continue
    fi

    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Phase 3 — ${RUN}  (frac=${F})"
    echo "  Resume-state saved every 50 epochs → checkpoints/${RUN}/resume_state.pth"
    echo "══════════════════════════════════════════════════════════════"
    $PYTHON train_phase3.py $P3_COMMON \
        --run_name "$RUN" --train_frac "$F" \
        >> "logs/train_${RUN}.log" 2>&1
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  ${RUN} DONE"
done

# ─────────────────────────────────────────────────────────────────────────────
# Evaluation — all completed Phase-3 runs
# ─────────────────────────────────────────────────────────────────────────────
if [ ${#RUN_P3_RUNS[@]} -gt 0 ]; then
    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Evaluating Phase-3 runs"
    echo "══════════════════════════════════════════════════════════════"

    for RUN in "${RUN_P3_RUNS[@]}"; do
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
            $PYTHON eval_v2.py \
                --run_name "$RUN" --weights "${W}.pth" --split test \
                >> "$EVAL_LOG" 2>&1
        done
    done
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Evaluation DONE"
    echo "  Results appended to ${EVAL_LOG}"
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  All requested stages complete."
echo "══════════════════════════════════════════════════════════════"
