#!/bin/bash
cd /orcd/data/faez/001/nick/mf_field/factory_mffp
CAP=63
for iter in $(seq 1 300); do
  q=$(squeue -u nicksung -h | wc -l)
  qnames=$(squeue -u nicksung -h -o "%j" | grep '^b_' | sed 's/^b_//')
  room=$((CAP - q))
  rem=0
  while read f d; do
    [ -z "$f" ] && continue
    cell="${f}__${d}"
    [ -f "results/raw_bench/${cell}__e2500__s42.json" ] && continue
    echo "$qnames" | grep -qx "$cell" && continue
    rem=$((rem+1))
    [ "$room" -lt 1 ] && continue
    sbatch -J b_${cell} --partition=pi_faez --time=23:59:00 --exclude=node2901 \
      --export=ALL,PYTHONUNBUFFERED=1 bench/bench_one.sbatch $f $d 2500 42 >/dev/null 2>&1 \
      && { room=$((room-1)); rem=$((rem-1)); }
  done < /tmp/need_cells.txt
  echo "[drip iter $iter] queued=$q remaining=$rem"
  [ "$rem" -eq 0 ] && { echo "[drip] all needed cells done or queued"; break; }
  sleep 150
done
echo "[drip] exit"
