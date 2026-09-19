# PDEBench + PDEArena — one dataset per PDE (visualization preview)

Composite figure: `figures/all_benchmarks.png` (1D PDEs shown as x–t space-time
images; 2D as a snapshot; 3D as a mid-plane slice; sample index 0 each).

Provenance: **✓ upstream** = produced by the real benchmark solver (cloned repos);
**≈ reimpl** = my own numpy solver of the *same governing equations* (used only
where the upstream solver couldn't run here — PhiFlow is incompatible with
numpy 2.x, and PDEArena's shallow-water needs Julia/SpeedyWeather).

## PDEBench (11 — 10 canonical + 1 bonus)

| PDE | Solver | Provenance | Shape shown |
|-----|--------|-----------|-------------|
| Advection 1D (β) | JAX FV/MUSCL | ✓ upstream | 21×256 (x-t) |
| Burgers 1D (ν) | JAX FV/MUSCL | ✓ upstream | 21×256 (x-t) |
| Reaction-Diffusion 1D (ρ,ν) | JAX FD | ✓ upstream | 21×256 (x-t) |
| Diffusion-Sorption 1D | SciPy RK45 | ✓ upstream | 51×256 (x-t) |
| Compressible NS 1D (M0,η,ζ) | JAX FV HLLC | ✓ upstream | 21×256 (x-t) |
| Compressible NS 2D (M0,η,ζ) | JAX FV HLLC | ✓ upstream | 64×64 |
| Compressible NS 3D (M0,η,ζ) | JAX FV HLLC | ✓ upstream | 16³ (z-slice) |
| Darcy 2D (β) | JAX FD | ✓ upstream | 64×64 |
| Diffusion-Reaction 2D | SciPy RK45 | ✓ upstream | 64×64 |
| Shallow Water 2D (dam break) | PyClaw | ✓ upstream | 128×128 *(bonus)* |
| Incompressible NS 2D | spectral vorticity | ≈ reimpl | 64×64 |

## PDEArena (4)

| PDE | Solver | Provenance | Shape shown |
|-----|--------|-----------|-------------|
| NS smoke 'standard' | spectral buoyant NS+scalar | ≈ reimpl | 64×64 |
| NS smoke 'conditioned' (buoyancy) | spectral buoyant NS+scalar | ≈ reimpl | 64×64 |
| Shallow Water 'weather' | finite-difference SW | ≈ reimpl | 96×96 |
| Maxwell 3D | `fdtd` FDTD | ✓ upstream | 16³ (z-slice) |

**Totals: 12 upstream, 3 reimpl → 15 fields shown (10 PDEBench canonical + 4 PDEArena + 1 bonus).**

## Upstream patches applied (version rot, for reproducibility)
The cloned generators needed small fixes to run on a modern stack:
- `data_gen_NLE/utils.py`: deprecated JAX index-update `.loc[...]` → `.at[...]` (65 sites).
- `gen_diff_react.py`, `gen_radial_dam_break.py`: `output_path.mkdir(output_path, ...)` /
  `.with_suffix` path bugs corrected.
- `gen_radial_dam_break.py`: removed unsupported `plot=` kwarg from `scenario.run(...)`.
- Sample counts (`num_samples_final`) reduced to 3 for quick previews.
- PhiFlow generators (PDEBench incomp-NS, PDEArena smoke) NOT run: PhiFlow 2.x imports
  `numpy.math` (removed in numpy ≥2) and PhiFlow 3.x changed the API — reimplemented instead.

## Where the data is
- PDEBench JAX `.npy`: `PDEBench/pdebench/data_gen/data_gen_NLE/save/{advection,burgers,ReacDiff,CFD}/`
- PDEBench `.h5`: `PDEBench/pdebench/data*/{1D_diff-sorp,2D_diff-react,2D_rdb}_NA_NA/`
- PDEArena Maxwell `.h5`: `pdearena/out_maxwell/`
- Reimplemented `.npz`: `reimpl_out/`

All are tiny previews (2–8 samples). To scale up: re-run each generator with larger
`numbers`/`samples` and grid; for aligned multi-fidelity, re-run at two `nx` values with
the same `init_key`/seed (see earlier analysis).
