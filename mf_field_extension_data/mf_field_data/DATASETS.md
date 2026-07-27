# Multi-fidelity field-prediction datasets

Each `.npz` in `data/` has: `params (N,d)`, `lf (N,...)`, `hf (N,...)`, `param_names (d,)`.

Fidelities are **aligned/nested**: `lf[i]` and `hf[i]` are the *same* parameter vector solved on a coarse vs. fine grid (genuine discretization-error fidelity gap). LF→HF upsampling is one line (`scipy.ndimage.zoom`).

All PDEs here are chosen to **not overlap** with the existing collection (Poisson, heat, Darcy, advection-diffusion, Allen-Cahn, Burgers, lid-cavity, fluid, ERA5).

![overview](figures/overview.png)

| # | Dataset | PDE | Params (input) | N | LF grid | HF grid | Size |
|---|---------|-----|----------------|---|---------|---------|------|
| 1 | **01_helmholtz_2d** | Δu + k²u = f, Dirichlet 0 (real part) | `wavenumber_k` ∈ [4.1, 12]<br>`source_x` ∈ [0.3, 0.7]<br>`source_y` ∈ [0.3, 0.7] | 200 | (24, 24) | (96, 96) | 7.219 MB |
| 2 | **02_rayleigh_benard_2d** | Boussinesq convection (vorticity-streamfunction-temperature) | `log10_rayleigh` ∈ [3, 4.3] | 80 | (24, 24) | (64, 64) | 1.24 MB |
| 3 | **03_gray_scott_2d** | Gray-Scott reaction-diffusion (u,v), periodic | `feed_F` ∈ [0.026, 0.057]<br>`kill_k` ∈ [0.055, 0.065] | 100 | (24, 24) | (72, 72) | 0.442 MB |
| 4 | **04_wave_2d** | u_tt = c²Δu, Dirichlet 0 (reflecting) | `wave_speed` ∈ [0.6, 1.8]<br>`source_x` ∈ [0.3, 0.7]<br>`source_y` ∈ [0.3, 0.7] | 150 | (24, 24) | (80, 80) | 3.718 MB |
| 5 | **05_eikonal_2d** | |∇T| = 1/speed(x), T(source)=0 (Hamilton-Jacobi) | `source_x` ∈ [0.2, 0.8]<br>`source_y` ∈ [0.21, 0.79]<br>`log10_inclusion_speed` ∈ [-0.68, 0.7] | 150 | (24, 24) | (64, 64) | 2.497 MB |
| 6 | **06_cahn_hilliard_2d** | c_t = M∇²(c³-c-γ∇²c), periodic (spectral) | `log10_gamma` ∈ [-3.7, -2.7]<br>`mean_composition` ∈ [-0.099, 0.096] | 100 | (24, 24) | (64, 64) | 1.687 MB |
| 7 | **07_kuramoto_sivashinsky_1d** | u_t + u u_x + u_xx + u_xxxx = 0, periodic (space×time field) | `domain_L` ∈ [22, 44]<br>`ic_amplitude` ∈ [0.61, 1]<br>`ic_phase` ∈ [0.023, 6.3] | 120 | (40, 64) | (120, 256) | 14.804 MB |

**Total: 7 datasets, 31.6 MB.**


### 01_helmholtz_2d

- **PDE:** Δu + k²u = f, Dirichlet 0 (real part)
- **What it adds:** 2D Helmholtz cavity field; indefinite operator, wavenumber + source as params.
- **Domain:** unit square [0,1]^2
- **Parameters (input):** `wavenumber_k` ∈ [4.07, 12], `source_x` ∈ [0.301, 0.698], `source_y` ∈ [0.301, 0.699]
- **Samples:** 200  | **LF:** (24, 24)  **HF:** (96, 96)

![01_helmholtz_2d](figures/01_helmholtz_2d.png)

### 02_rayleigh_benard_2d

- **PDE:** Boussinesq convection (vorticity-streamfunction-temperature)
- **What it adds:** 2D Rayleigh-Benard temperature field vs Rayleigh number (hot bottom).
- **Domain:** unit square, hot bottom T=1 / cold top T=0
- **Parameters (input):** `log10_rayleigh` ∈ [3.03, 4.27]
- **Samples:** 80  | **LF:** (24, 24)  **HF:** (64, 64)

![02_rayleigh_benard_2d](figures/02_rayleigh_benard_2d.png)

### 03_gray_scott_2d

- **PDE:** Gray-Scott reaction-diffusion (u,v), periodic
- **What it adds:** 2D Gray-Scott Turing patterns; output is v-species concentration field.
- **Domain:** unit square [0,1]^2
- **Parameters (input):** `feed_F` ∈ [0.026, 0.0572], `kill_k` ∈ [0.055, 0.065]
- **Samples:** 100  | **LF:** (24, 24)  **HF:** (72, 72)

![03_gray_scott_2d](figures/03_gray_scott_2d.png)

### 04_wave_2d

- **PDE:** u_tt = c²Δu, Dirichlet 0 (reflecting)
- **What it adds:** 2D wave field snapshot at t=0.4 from a Gaussian pulse; hyperbolic.
- **Domain:** unit square [0,1]^2
- **Parameters (input):** `wave_speed` ∈ [0.601, 1.8], `source_x` ∈ [0.3, 0.7], `source_y` ∈ [0.302, 0.699]
- **Samples:** 150  | **LF:** (24, 24)  **HF:** (80, 80)

![04_wave_2d](figures/04_wave_2d.png)

### 05_eikonal_2d

- **PDE:** |∇T| = 1/speed(x), T(source)=0 (Hamilton-Jacobi)
- **What it adds:** 2D first-arrival travel-time field through a circular speed inclusion.
- **Domain:** unit square [0,1]^2
- **Parameters (input):** `source_x` ∈ [0.203, 0.798], `source_y` ∈ [0.206, 0.792], `log10_inclusion_speed` ∈ [-0.678, 0.697]
- **Samples:** 150  | **LF:** (24, 24)  **HF:** (64, 64)

![05_eikonal_2d](figures/05_eikonal_2d.png)

### 06_cahn_hilliard_2d

- **PDE:** c_t = M∇²(c³-c-γ∇²c), periodic (spectral)
- **What it adds:** 2D Cahn-Hilliard spinodal decomposition; 4th-order conservative phase field.
- **Domain:** unit square [0,1]^2
- **Parameters (input):** `log10_gamma` ∈ [-3.7, -2.7], `mean_composition` ∈ [-0.099, 0.0961]
- **Samples:** 100  | **LF:** (24, 24)  **HF:** (64, 64)

![06_cahn_hilliard_2d](figures/06_cahn_hilliard_2d.png)

### 07_kuramoto_sivashinsky_1d

- **PDE:** u_t + u u_x + u_xx + u_xxxx = 0, periodic (space×time field)
- **What it adds:** 1D Kuramoto-Sivashinsky spatiotemporal chaos; output is the x-t field.
- **Domain:** x in [0,L), t in [0,60]
- **Parameters (input):** `domain_L` ∈ [22.3, 43.8], `ic_amplitude` ∈ [0.606, 1], `ic_phase` ∈ [0.0233, 6.27]
- **Samples:** 120  | **LF:** (40, 64)  **HF:** (120, 256)

![07_kuramoto_sivashinsky_1d](figures/07_kuramoto_sivashinsky_1d.png)