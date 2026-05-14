#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# run_v9.sh  —  stacking_v9 Point-wise Gated Fusion MFTransolver_v9
#
# Added over v7:
#   Point-wise gate MLP for per-query fusion α
#
# Usage
# ─────
#   bash run_v9.sh                   # all fractions
#   bash run_v9.sh frac010           # single run
#   bash run_v9.sh frac010 frac020   # multiple runs
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
              --pos_enc_freqs 6 \
              --rbf_gamma_init 1.0 \
              --prior_weight_init 1.0 --prior_weight_final 0.1 \
              --prior_decay_epochs 1000"

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
# Training
# ─────────────────────────────────────────────────────────────────────────────
for RUN in "${RUN_LIST[@]}"; do
    F="${FRAC[$RUN]}"

    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Training MFTransolver_v9 — ${RUN}  (frac=${F})"
    echo "══════════════════════════════════════════════════════════════"

    $PYTHON train_v9.py $TRAIN_COMMON \
        --run_name "$RUN" --train_frac "$F" \
        >> "logs/train_${RUN}.log" 2>&1

    echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  ${RUN} DONE"
done

# ─────────────────────────────────────────────────────────────────────────────
# Evaluation
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
            $PYTHON eval_v9.py \
                --run_name "$RUN" --weights "${W}.pth" --split test \
                >> "$EVAL_LOG" 2>&1
        done
    done
    echo ""
    echo "  All evaluations done. See $EVAL_LOG"
fi

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  [$(date '+%Y-%m-%d %H:%M:%S')]  Pipeline complete"
echo "══════════════════════════════════════════════════════════════"
