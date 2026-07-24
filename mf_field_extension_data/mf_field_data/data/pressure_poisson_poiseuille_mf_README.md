# pressure_poisson_poiseuille_mf

Multi-fidelity **pressure-Poisson / Hagen–Poiseuille** CFD benchmark — a
*recreate-only* reproduction of the dense-regression (§2.2) and low-to-high (§2.3)
test cases in

> L. Partin, G. Geraci, A. Rushdi, M.S. Eldred, D.E. Schiavazzi,
> "Multifidelity data fusion in convolutional encoder/decoder networks,"
> *J. Comput. Phys.* (2022) / arXiv:2205.05187.

The paper specifies the PDE, flow case, parameterization, image sizes, fidelity
construction and sample counts but releases **no dataset and no solver**. See
`pressure_poisson_poiseuille_mf.json` for the machine-readable manifest.

## Physics
Hagen–Poiseuille flow in an axisymmetric cylindrical domain; a 2D slice through
the axis fully describes it. Pressure obeys the incompressible pressure-Poisson
equation `Δp = ∇·f` (Eq. 5). For fully-developed flow the exact solution is a
**parabolic axial velocity** and a **pressure that is linear along the axis** and
uniform across the cross-section — generated here analytically (what the FEM
Poisson solver produces for this idealized case).

64×64 image: columns = axial direction (pressure decreases linearly in x), rows =
transverse; fluid band `|y−0.5| ≤ r`. Parameters: radius `r`, max velocity `v_max`
(pressure gradient ∝ `v_max/r²`).

## Two prediction tasks (same pressure outputs)
- **Dense regression** (§2.2): `x_dense (N,3,64,64)` = [noisy concentration mask, u_x, u_y] → pressure.
- **Low-to-high** (§2.3): `params (N,2)` = [r, v_max] → pressure 64×64.

## Multi-fidelity output (coarsest → finest)
`LF1 8×8 → LF2 16×16 → LF3 32×32 → HF 64×64`. Each LF = HF block-mean downsampled
+ uniform noise `U(0, 0.05·(max−min))` (App. C.4.2).

## Splits
Per-sample 60/20/20 → train/val/test (probabilistic, exact ratios not preserved,
as in the paper). `hf32_idx` = random 32-subset of training (the "HF 32/0" set).
Combine 32 HF + 116-per-LF for the "MF 32/116" configuration.

## Contents of `pressure_poisson_poiseuille_mf.npz` (N=200)
| array | shape | meaning |
|---|---|---|
| `params`     | `(200,2)`        | `[radius_r, v_max]` — low-to-high input |
| `x_dense`    | `(200,3,64,64)`  | `[concentration, u_x, u_y]` — dense input |
| `p_hf`       | `(200,64,64)`    | HF pressure (0.5 outside fluid) |
| `p_lf3/2/1`  | `(200,32/16/8,·)`| LF pressure targets (downsampled + noise) |
| `mask_64`    | `(200,64,64)`    | binary fluid mask — score R² inside this |
| `split`      | `(200,)`         | 0=train, 1=val, 2=test |
| `hf32_idx`   | `(32,)`          | HF-32 subset (indices into all 200) |

## Assumptions (not numerically fixed by the paper)
- `r ∈ [0.15, 0.33]`, `v_max ∈ [0.6, 1.6]`.
- Axial pressure gradient ∝ `v_max/r²` (Hagen–Poiseuille), mapped monotonically
  (via log) to a visible half-amplitude band `0.02–0.08` about 0.5 — a global
  affine rescaling that keeps pressure a clean increasing function of `v_max/r²`.
- Constant 0.5 outside the fluid (R² scored only inside `mask_64`).
- Concentration measurement noise `N(0, 0.10)` on the {0,1} mask.
- Coarsening by block-mean restriction (paper says "subsampling").

## Reproduce / inspect
```
python3 generate_pressure_poisson_mf.py   # regenerate the .npz (seconds)
python3 visualize_pressure_mf.py          # figures in viz/
```
