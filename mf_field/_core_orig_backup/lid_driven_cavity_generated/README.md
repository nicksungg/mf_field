# lid_driven_cavity_generated

**Paper:** ghia1982highre (High-Re Solutions for Incompressible Flow Using the Navier-Stokes Equations and a Multigrid Method, *J. Comp. Phys.* 1982)
**Domain:** navier_stokes_pde_2d (lid-driven cavity, vorticity-streamfunction formulation)
**License:** MIT
**Availability:** regenerable
**Generator:** `mffpbench.generators.lid_driven_cavity:generate`

## Physics

2D incompressible Navier-Stokes on the unit square `[0, 1]²`:

- Top wall (lid) moves at `u = 1`, no-slip on the other three walls
- Reynolds number Re sampled **log-uniform in [100, 1000]** per sample (the standard Ghia 1982 range)
- Steady-state vorticity `ω = ∂v/∂x − ∂u/∂y` is the output

## Numerical scheme

- Vorticity-streamfunction formulation (avoids pressure-Poisson coupling)
- **First-order upwind** on convection, central differences on diffusion (stable at all cell-Re; adds numerical diffusion at coarse resolution — this is the genuine multi-fidelity signal)
- RK2 (midpoint) time stepping
- `dt = 0.125 · min(h²/ν, h/U)` (RK2 diffusive CFL of ~0.5)
- Streamfunction Poisson solved once per step by sparse LU (operator factorised once per fidelity)
- Vorticity wall BCs via Thom's formula
- Steady-state termination at `‖ω_new − ω_old‖_∞ / dt < 10⁻⁴`, MAX_STEPS = 8000

## Fidelity ladder

- L1: 32×32
- L2: 64×64
- L3: 128×128

Same `Re` realisations across all fidelities — LF and HF differ only in discretisation.

## Sample counts

- Train: **40**
- Test: **10**
- Total: 50

## Array convention (IMPORTANT for plotting)

`ω[0, :]` is the **bottom wall**, `ω[-1, :]` is the **top wall** (the moving lid). When plotting, **use `imshow(..., origin='lower')`** so the lid appears at the top of the image — otherwise the cavity appears upside-down.

## File layout

`train_l1.npz`, `train_l2.npz`, `train_l3.npz`, `test_l1.npz`, `test_l2.npz`, `test_l3.npz` — MFRNP npz convention with keys `x` and `y`.

- `x` shape: `(N, 1)` — Reynolds number per sample, **linear (not log10)**
- `y` shape: `(N, level²)` — flattened steady-state vorticity field

## Load example

```python
import numpy as np

d = np.load("train_l3.npz")
X, Y = d["x"], d["y"]
Re = X[:, 0]                   # (40,) — actual Re values in [100, 1000]
print(f"Re range: [{Re.min():.0f}, {Re.max():.0f}]")
vort = Y[0].reshape(128, 128)  # vorticity field of sample 0

import matplotlib.pyplot as plt
plt.imshow(vort, cmap="RdBu_r", origin="lower")  # ← origin='lower' is critical
plt.title(f"Re = {Re[0]:.0f}")
plt.colorbar()
```

## Regenerate from scratch

```bash
uv run python -c "from mffpbench.generators.lid_driven_cavity import generate; out = generate(fidelity_levels=[32, 64, 128], n_samples=50, seed=42)"
```
