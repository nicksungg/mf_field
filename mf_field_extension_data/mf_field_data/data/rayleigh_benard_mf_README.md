# rayleigh_benard_mf  (aka ob_boussinesq_mf)

Multi-fidelity **steady 2D Oberbeck–Boussinesq / Rayleigh–Bénard natural convection**,
a *recreate-only* reproduction of Section 4.3 of

> L. Parussini, D. Venturi, P. Perdikaris, G.E. Karniadakis,
> "Multi-fidelity Gaussian process regression for prediction of random fields,"
> *J. Comput. Phys.* **336** (2017) 36–50.

The paper specifies the PDE, geometry, BCs, fidelity definition, Ra range and
sample counts but releases **no dataset and no solver**. This reproduces the setup
faithfully. See `rayleigh_benard_mf.json` for the machine-readable manifest.

## Physics
Steady streamfunction–temperature system (Eqs. 44–45), unit square `[0,1]²`:
- bottom `y=0`: `T=1` (hot), top `y=1`: `T=0` (cold), sidewalls adiabatic `∂T/∂x=0`
- no-slip velocity on all walls (`ψ=0`, `∂ψ/∂n=0`)
- parameter: Rayleigh number `Ra ∈ [2.6e3, 1e5]`; Prandtl `Pr=0.71`

Solved by a 2nd-order finite-difference vorticity–streamfunction scheme marched to
steady state. **Fidelity = physical-space grid resolution** `Nv=NT` (paper used
spectral resolution): LF=20, MF=50, HF=100. The coarse-vs-fine discretization
error is the genuine multi-fidelity signal.

## Sampling (equally spaced in Ra, **nested** `HF ⊂ MF ⊂ LF`)
- LF: 17 samples on 20×20 grid
- MF:  9 samples on 50×50 grid  (`= LF[::2]`)
- HF:  5 samples on 100×100 grid (`= LF[::4]`)

## Contents of `rayleigh_benard_mf.npz`
Per level `<LVL> ∈ {LF, MF, HF}` (grid size `n` = 20/50/100):

| array | shape | meaning |
|---|---|---|
| `ra_<LVL>`    | `(S,)`        | Rayleigh numbers |
| `x_<LVL>`     | `(n,)`        | uniform grid coords (x and y) |
| `T_<LVL>`     | `(S,n,n)`     | steady temperature field (row=y, row 0 = bottom) |
| `psi_<LVL>`   | `(S,n,n)`     | steady streamfunction field |
| `Tleg_<LVL>`  | `(S,49,25)`   | Legendre coeffs of local temperature |
| `nested_idx_MF/HF` | — | indices of MF/HF Ra within the LF Ra array |

**Field representation** (`Tleg_*`): `[0,1]²` split into 7×7 = 49 square spectral
elements; local temperature expanded in a 4th-order tensor-product Legendre basis
(25 modes/element). Element index `= I*7 + J`; mode index `= p*5 + q` (Legendre
degrees `p,q ∈ {0..4}` in x,y). This 49×25 representation has identical dimension
at every fidelity — the shared cross-fidelity GPR basis.

## Reproduce / inspect
```
python3 generate_rayleigh_benard_mf.py   # regenerate the .npz (~4 min)
python3 visualize_rb_mf.py               # fields + a_12(Ra) figures in viz/
```
