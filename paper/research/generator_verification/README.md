# Dataset generator sources and numerical checks

This record supports the additions to Section 4.1 and Appendix A.1. It
separates published software, adapted benchmark recipes, and our numerical
checks. It does not claim external certification of the 22 stored datasets.
No benchmark arrays, trained models, or prediction results were changed.

## Published sources

| Entry | Source and supported relationship | Implementation evidence |
| --- | --- | --- |
| Euler, Burgers, Shallow water | [Ketcheson et al., 2012](https://doi.org/10.1137/110856976) describes PyClaw, Clawpack, and SharpClaw. This is a software citation. | `sharp_solver/src/mffp_sharp/pdes/{euler,burgers,shallow_water}.py` calls Classic ClawSolver at coarse fidelities and SharpClaw at the fine fidelity. |
| Euler | [The Well, Section C.4](https://arxiv.org/html/2412.00568v1#A3.SS4) uses Euler Riemann problems with piecewise constant initial data and Clawpack. | The local generator initializes four quadrants and varies pressure/density ratios. This is a recipe influence, not imported Well data or an identical task. |
| Shallow water | [PDEBench, Section D.7](https://arxiv.org/html/2210.07182v7#A4.SS7) describes radial dam break simulations using PyClaw. | Our code varies inner height and radius on a unit square. PDEBench describes a different domain and sampling prescription. |
| Porous medium | [Vázquez, 2007](https://academic.oup.com/book/7922) provides the mathematical background for porous medium diffusion and its self similar solutions. | `_barenblatt_1d` and the verification script provide an analytical reference for the finite difference solver. This is not a released dataset attribution. |
| Phase field crystal | [Elder and Grant, 2004](https://doi.org/10.1103/PhysRevE.70.051605), with [author manuscript](https://arxiv.org/pdf/cond-mat/0306681), gives the conserved phase field crystal model. | `sharp_solver/src/mffp_sharp/pdes/phase_field_crystal.py` implements the deterministic conserved equation with a Fourier discretization. The citation concerns the governing model, not independent validation of this implementation. |

Imported MFRNP data and ERA5 retain their existing Niu et al. and Hersbach
et al. citations. IFC is outside the current 22 dataset roster.

## Numerical evidence and its limits

The [archived sharp solver report](sharp_verification_report.md) records a
June 2026 verification exercise. The present paper uses only specific checks
relevant to its current roster, not the report's broad opening verdict.
The scripts and inspected solver modules are preserved here. Their original
paths and file hashes are in [source_manifest.json](source_manifest.json).

Two existing checks were repeated for this revision. Their full output is in
[selected_checks_20260917.txt](selected_checks_20260917.txt):

* Porous medium: a one dimensional Barenblatt profile, exponent 2, evolves
  from time 1 to 1.6. Relative errors at 128, 256, 512, and 1024 points are
  `8.11e-4`, `1.87e-4`, `2.62e-5`, and `3.97e-5`. The paper gives the decline
  over 128 to 512 points. The final refinement does not improve error, so this
  does not establish monotone convergence over all four grids or an asymptotic
  convergence order. The test function's printed `monotone` flag checks only
  its stated subset of comparisons.
* Allen Cahn: a one dimensional smooth initial condition is compared against
  a 512 point numerical reference. Errors at 64, 128, and 256 points are
  `4.89e-5`, `1.16e-5`, and `2.33e-6`. This is self convergence, not comparison
  to an exact solution or an independent published implementation.

Both solvers support the one and two dimensional settings. These small tests
do not validate every two dimensional dataset sample. The archived report
also supplies the Cahn Hilliard mass, phase field crystal mean conservation,
and Helmholtz discrete residual checks described in Appendix A.1. A small
discrete residual alone does not establish continuum solution accuracy.

From this directory, repeat the two selected checks with NumPy and SciPy:

```bash
PYTHONPATH=sharp_solver/src python3 -c 'import independent_verification as v; v.test_pme_barenblatt_convergence(); v.test_allen_cahn_mesh_convergence(); assert all(r[1] for r in v.results)'
```

The [extension report](extension_verification_report.md) and its
[script](extension_verify.py) are also retained for context. Eikonal and
Cahn Hilliard reference comparisons were marked `CHECK`, with discrepancies
of 18.42% and 11.28%. They are not cited as successful external validation.
The Wave verification reimplements the stencil for a standing wave test
rather than invoking the complete generator. The extension Helmholtz test
belongs to a dataset excluded from the current roster. These distinctions
prevent transferring evidence to a different generator or task.

The cavity archive has a script comparing a centerline statistic to Ghia's
reference. No completed quantitative comparison record was located in this
review, so a successful Ghia validation claim was not added. None of the
new citations implies that the published authors checked our generated files.
