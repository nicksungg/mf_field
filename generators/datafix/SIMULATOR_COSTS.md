# Simulator inventory and measured cost per solve (2026-09-06, single core, CLUSTER login/compute nodes, Python solvers)

## Datasets we own a runnable simulator for
| dataset | source | grids (coarse -> fine) | seconds per solve | fine/coarse ratio | notes |
|---|---|---|---|---|---|
| poisson_generated_v2 | gen_core_v2.py (fixed) | 16 / 32 / 64 | 0.00085 / 0.0029 / 0.0139 | 16x | dx^2 bug fixed |
| heat_generated | gen_core_v2.py | 16 / 32 / 64 | 0.0005 / 0.0018 / 0.0066 | 13x | space-time field |
| darcy_generated | gen_core_v2.py | 32 / 64 / 128 | 0.009 / 0.034 / 0.132 | 15x | KL basis not bit-reproducible; paired rows = original |
| allen_cahn_generated | gen_core_v2.py | 64 / 128 / 256 pts (1-D) | (sub-ms) | ~2-4x | 1-D |
| lid_driven_cavity (converged v2 solver) | gen_cavity/lid_driven_cavity.py | 32 / 64 / 128 / 256 | 3 / 23 / 244 / 2936 | ~1000x | steady state; the only expensive one |
| ext helmholtz_2d | mf_field_extension_data/solvers.py | 24 / 96 | 0.0010 / 0.018 | 18x | resonant k range |
| ext rayleigh_benard_2d | solvers.py | 24 / 64 | 0.016 / 0.49 | 30x | |
| ext wave_2d | solvers.py | 24 / 80 | 0.0004 / 0.0032 | 8x | |
| ext eikonal_2d | solvers.py | 24 / 64 | 0.0009 / 0.0039 | 4x | |
| ext cahn_hilliard_2d | solvers.py | 24 / 64 | 0.34 / (n/a) | | shipped ICs not reconstructible from theta |
| sharp cahn_hilliard | mffp_sharp (py-pde) | 32 / 64 / 128 (timed; shipped 64/128/256) | 3.0 / 8.7 / 34.1 | ~4x per rung | 256 not timed (~2-3 min est.) |
| sharp allen_cahn_2d | mffp_sharp (spectral) | 32 / 64 / 128 | 0.049 / 0.142 / 0.535 | ~3.8x/rung | shipped 64/128/256 |
| sharp fisher_kpp_2d | mffp_sharp | 32 / 64 / 128 | 0.027 / 0.055 / 0.204 | | shipped 64/128/256 |
| sharp phase_field_crystal_2d | mffp_sharp | 32 / 64 / 128 | 0.31 / 1.0 / 3.9 | ~4x/rung | matches shipped ladder |
| sharp helmholtz_2d | mffp_sharp | 32 / 64 / 128 | 0.003 / 0.008 / 0.038 | | shipped 64/128/256 |
| sharp porous_medium_2d | mffp_sharp | 32 / 64 / 128 | 0.006 / 0.047 / 0.58 | ~10x/rung | shipped 64/128/256 |
| sharp porous_medium_1d | mffp_sharp | 32 / 64 / 128 | 0.001 / 0.004 / 0.016 | | |
| sharp euler, sod_1d, burgers_1d/2d, shallow_water_1d/2d | mffp_sharp via PyClaw | | NOT timed | | clawpack not installed in the venv |
| non-roster sharp (KS, Swift-Hohenberg, Gray-Scott, KdV, NLS, sine-Gordon, allen_cahn_1d, fisher_1d) | mffp_sharp | 32 / 64 / 128 | 0.01 - 1.7 | | candidate HOLD-OUT problems |

## Not simulators (cannot regenerate)
poisson_local, heat_local, fluid (MFRNP release files); ifc_heat, ifc_poisson (IFC release); era5 (reanalysis); ext pressure_poisson (synthetic coarse levels).

## Reading
Except for the cavity (and sharp cahn_hilliard at 256), every fine solve costs milliseconds to seconds, i.e. far less than training a
network (~0.5 GPU-h). The multi-fidelity premise (fine solves are the bottleneck) is false for these toy solvers and true for the
CFD they stand in for; cost must enter the study parametrically (cost ratio r = c_L/c_H, c_H relative to training, deployment volume Q),
with the measured numbers fixing only the scaling exponents (~cells^1.2-1.5 here; cavity ~cells^2.3 because steady-state step counts grow too).
