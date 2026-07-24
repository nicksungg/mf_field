#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/home/nicksung/Desktop/.venv/bin/python}"
EPOCHS="${EPOCHS:-200}"
SEEDS="${SEEDS:-1 2 3}"
DEVICE="${DEVICE:-cuda}"

cd "$ROOT_DIR"

run_task() {
	local data_path="$1"
	local tag="$2"
	local levels="$3"
	for seed in $SEEDS; do
		local run_name="${tag}_l${levels}_seed${seed}"
		echo "===== TRAIN ${run_name} ====="
		"$PYTHON_BIN" train_mfrnp_v9.py \
			--data_path "$data_path" \
			--levels "$levels" \
			--run_name "$run_name" \
			--epochs "$EPOCHS" \
			--seed "$seed"
		echo "===== EVAL ${run_name} ====="
		"$PYTHON_BIN" eval_mfrnp_v9.py --run_name "$run_name" --split test
	done
	aggregate_task "$tag" "$levels"
}

# Aggregate nRMSE mean ± std across seeds for a completed task
aggregate_task() {
	local tag="$1"
	local levels="$2"
	echo "--- AGGREGATE ${tag} l${levels} (${SEEDS}) ---"
	"$PYTHON_BIN" - <<PYEOF
import csv, numpy as np, os, sys
here = "${ROOT_DIR}/checkpoints"
tag = "${tag}"
levels = "${levels}"
seeds = [int(s) for s in "${SEEDS}".split()]
vals = []
for seed in seeds:
    run = f"{tag}_l{levels}_seed{seed}"
    f = os.path.join(here, run, "eval_test_film_best_summary.csv")
    if os.path.isfile(f):
        with open(f) as fp:
            d = {k.strip(): v.strip() for k, v in csv.reader(fp) if k.strip() and k.strip() != ''}
        key = 'nrmse_global' if 'nrmse_global' in d else 'nrmse'
        if key in d:
            v = float(d[key])
            vals.append(v)
            print(f"  seed={seed}: nRMSE={v:.6f}")
        else:
            print(f"  seed={seed}: key not found in {list(d.keys())}")
    else:
        print(f"  seed={seed}: MISSING {f}")
if vals:
    r = np.array(vals)
    print(f"  ==> {tag} l{levels}: nRMSE = {np.mean(r):.6f} +/- {np.std(r):.6f}  (n={len(vals)})")
else:
    print("  ==> No results found")
PYEOF
}

run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/full_dataset/poisson" "poisson_full" 2
run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/full_dataset/poisson" "poisson_full" 3
run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/full_dataset/poisson" "poisson_full" 5

run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/full_dataset/heat" "heat_full" 2
run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/full_dataset/heat" "heat_full" 3
run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/full_dataset/heat" "heat_full" 5

run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/full_dataset/fluid" "fluid_full" 2

run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/OOD/poisson/l2" "poisson_ood" 2
run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/OOD/poisson/l3" "poisson_ood" 3
run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/OOD/poisson/l5" "poisson_ood" 5

run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/OOD/heat/l2" "heat_ood" 2
run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/OOD/heat/l3" "heat_ood" 3
run_task "/home/nicksung/Desktop/nicksung/mf_field_v2/data/OOD/heat/l5" "heat_ood" 5