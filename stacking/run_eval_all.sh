#!/bin/bash
# Run eval for all available best/final checkpoints, then aggregate into one CSV.
set -e
cd "$(dirname "$0")"
mkdir -p logs

PYTHON="$(which python3) -u"

declare -A COMBOS
COMBOS[frac100]="film_best"
COMBOS[frac020]="film_best film_final"
COMBOS[frac010]="film_best film_final"
COMBOS[frac005]="film_best film_final"

for RUN in frac100 frac020 frac010 frac005; do
    for CKPT in ${COMBOS[$RUN]}; do
        WEIGHTS_PATH="checkpoints/${RUN}/${CKPT}.pth"
        if [ ! -f "$WEIGHTS_PATH" ]; then
            echo "[SKIP] $WEIGHTS_PATH not found"
            continue
        fi
        echo "---------- ${RUN} / ${CKPT} ----------"
        $PYTHON eval_stacking.py \
            --split test \
            --run_name "$RUN" \
            --weights "${CKPT}.pth" \
            --lf_weights film_best.pth \
            2>&1 | tee -a logs/eval_all.log
    done
done

# Aggregate all summary CSVs into one combined CSV
$PYTHON - <<'EOF'
import pandas as pd
from pathlib import Path

rows = []
ckpt_base = Path("checkpoints")
for run_dir in sorted(ckpt_base.iterdir()):
    if not run_dir.is_dir():
        continue
    for ckpt_stem in ["film_best", "film_final"]:
        f = run_dir / f"eval_test_{ckpt_stem}_summary.csv"
        if not f.exists():
            continue
        s = pd.read_csv(f, index_col=0)["value"]
        rows.append({
            "run":         run_dir.name,
            "checkpoint":  ckpt_stem,
            "mae_norm":    s["mae_norm"],
            "mse_norm":    s["mse_norm"],
            "rel_l1_norm": s["rel_l1_norm"],
            "rel_l2_norm": s["rel_l2_norm"],
            "mae_phys":    s["mae_phys"],
            "mse_phys":    s["mse_phys"],
            "rel_l1_phys": s["rel_l1_phys"],
            "rel_l2_phys": s["rel_l2_phys"],
        })

out = Path("results_eval_all.csv")
pd.DataFrame(rows).to_csv(out, index=False)
print(f"\nAggregated results saved to {out}")
print(pd.DataFrame(rows).to_string(index=False))
EOF
