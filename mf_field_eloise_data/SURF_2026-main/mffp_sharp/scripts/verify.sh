#!/usr/bin/env bash
# Verify the PDE solver suite: run the unit tests and print a one-line summary.
#
#   bash scripts/verify.sh
#
# Pure-numpy solvers verify on ANY machine (the Mac .venv or the box conda env 'mffp').
# PyClaw solvers (euler, burgers, sod, shallow_water) only run where clawpack is installed
# (the box); without it they SKIP — that is EXPECTED off-box, not a failure.
# See ../PDE_SOLVERS.md ("Verifying the solvers work") for the full guide.
set -euo pipefail

cd "$(dirname "$0")/.."          # -> mffp_sharp/

if python -c "import clawpack" 2>/dev/null; then
  echo ">> clawpack present — PyClaw solvers (euler/burgers/sod/shallow_water) will RUN."
else
  echo ">> clawpack NOT present — PyClaw solvers (euler/burgers/sod/shallow_water) will SKIP (expected off-box)."
fi

echo ">> running solver test suite (pytest)…"
python -m pytest -q -rs
