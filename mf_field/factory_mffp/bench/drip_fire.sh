#!/bin/bash
cd /orcd/data/faez/001/nick/mf_field/factory_mffp
FAMS="fno_fire_snapshot fno_fire_swag fno_fire_batchens fno_fire_quantile fno_fire_iqn fno_fire_mdn fno_fire_laplace fno_fire_dkl fno_fire_cqr"
DSS="ifc_heat ifc_poisson poisson_local heat_local fluid era5 pm_test advection_diffusion_generated allen_cahn_generated burgers_generated burgers_param_generated darcy_generated heat_generated lid_driven_cavity_generated poisson_generated"
CAP=63
for iter in $(seq 1 400); do
  q=$(squeue -u nicksung -h | wc -l)
  qnames=$(squeue -u nicksung -h -o "%j" | grep '^b_' | sed 's/^b_//')
  room=$((CAP - q)); [ "$room" -lt 1 ] && { sleep 120; continue; }
  miss=0
  for f in $FAMS; do for d in $DSS; do
    cell="${f}__${d}"
    [ -f "results/raw_bench/${cell}__e2500__s42.json" ] && continue
    echo "$qnames" | grep -qx "$cell" && continue
    [ "$room" -lt 1 ] && break 2
    sbatch -J b_${cell} --partition=pi_faez --time=23:59:00 --exclude=node2901 \
      --export=ALL,PYTHONUNBUFFERED=1 bench/bench_one.sbatch $f $d 2500 42 >/dev/null 2>&1 \
      && { room=$((room-1)); miss=$((miss+1)); }
  done; done
  # count remaining missing
  rem=0
  for f in $FAMS; do for d in $DSS; do
    cell="${f}__${d}"
    [ -f "results/raw_bench/${cell}__e2500__s42.json" ] && continue
    echo "$qnames" | grep -qx "$cell" && continue
    rem=$((rem+1))
  done; done
  echo "[drip iter $iter] submitted=$miss queued=$q"
  [ "$rem" -eq 0 ] && { echo "[drip] all cells done or queued"; break; }
  sleep 150
done
echo "[drip] exit"
