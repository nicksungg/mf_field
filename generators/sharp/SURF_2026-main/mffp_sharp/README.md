# Sharp-field solver package

`src/mffp_sharp/pdes/` contains the PDE solvers. `common/` supplies sampling, initial-condition encoding, fidelity ladders, metrics and output utilities. `configs/sample.yaml` defines an exploratory sample recipe. The finalized benchmark uses the parent directory's standardized generation driver and per-variant configuration files.

From the AutoMF review directory:

```bash
python -m pip install -r requirements-generators.txt
export PYTHONPATH="$PWD/generators/sharp/SURF_2026-main/mffp_sharp/src:$PYTHONPATH"
python -m mffp_sharp.generate --help
```

Hyperbolic solvers require Clawpack/PyClaw and a working Fortran toolchain. The solver source and [verification report](../../VERIFICATION_REPORT.md) describe the checks actually performed; including a solver does not establish validation over every parameter setting. See the [benchmark dataset guide](../../../../docs/DATASETS.md) for the exact archive locations and generation scope.
