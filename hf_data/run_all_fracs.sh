#!/bin/bash
# Sequential training for 4 data fractions.
# Logs: logs/train_frac<X>.log

set -e
cd "$(dirname "$0")"
mkdir -p logs

PYTHON="$(which python3) -u"
COMMON="--epochs 5000 --batch_size 16 --n_points 8192"

echo "====== [$(date)] Starting 100% run ======"
$PYTHON train_car_3d.py $COMMON --train_frac 1.00 --run_name frac100 \
    > logs/train_frac100.log 2>&1
echo "====== [$(date)] 100% run DONE ======"

echo "====== [$(date)] Starting 20% run ======"
$PYTHON train_car_3d.py $COMMON --train_frac 0.20 --run_name frac020 \
    > logs/train_frac020.log 2>&1
echo "====== [$(date)] 20% run DONE ======"

echo "====== [$(date)] Starting 10% run ======"
$PYTHON train_car_3d.py $COMMON --train_frac 0.10 --run_name frac010 \
    > logs/train_frac010.log 2>&1
echo "====== [$(date)] 10% run DONE ======"

echo "====== [$(date)] Starting 5% run ======"
$PYTHON train_car_3d.py $COMMON --train_frac 0.05 --run_name frac005 \
    > logs/train_frac005.log 2>&1
echo "====== [$(date)] 5% run DONE ======"

echo "====== [$(date)] ALL RUNS COMPLETE ======"
