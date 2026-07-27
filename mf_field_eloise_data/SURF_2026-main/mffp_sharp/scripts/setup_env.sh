#!/usr/bin/env bash
# Build the Python env. Run THIS ON Nicholas's box, after cloning the repo:
#   git clone https://github.com/eloisezeng/SURF_2026.git
#   cd SURF_2026/mffp_sharp && bash scripts/setup_env.sh
set -euo pipefail

cd "$(dirname "$0")/.."          # -> mffp_sharp/

if ! command -v conda >/dev/null; then
  echo "conda not found on this machine; install miniconda or adjust this script."; exit 1
fi

conda create -y -n mffp python=3.11 || true
# shellcheck disable=SC1091
source activate mffp 2>/dev/null || conda activate mffp

pip install -r requirements.txt
pip install -e .

python -c "import numpy, scipy, h5py, pde; print('core OK')"
python -c "from clawpack import pyclaw; print('pyclaw OK')" \
  || echo "WARN: clawpack not ready (needs a Fortran compiler, e.g. 'conda install -y gfortran' then 'pip install clawpack')"

echo ">> env 'mffp' ready. Generate with: bash scripts/run_sample.sh all"
