"""
Paper-faithful multi-fidelity dataset:  STOCHASTIC RAYLEIGH-BENARD / OBERBECK-BOUSSINESQ

Reproduction of the thermal-convection benchmark in Section 4.3 of

    L. Parussini, D. Venturi, P. Perdikaris, G.E. Karniadakis,
    "Multi-fidelity Gaussian process regression for prediction of random fields,"
    Journal of Computational Physics 336 (2017) 36-50.

This is a RECREATE-ONLY reproduction: the paper specifies the PDE, geometry,
boundary conditions, fidelity definition, parameter range and sample counts, but
releases neither a dataset file nor a solver.  We reproduce the setup faithfully;
documented modelling choices (solver method, Pr) are noted under ASSUMPTIONS.

--------------------------------------------------------------------------------
GOVERNING EQUATIONS  (steady Oberbeck-Boussinesq, streamfunction psi / temp T), Eqs (44)-(45):

    psi_y (Lap psi)_x - psi_x (Lap psi)_y = -Pr Lap^2 psi + Ra*Pr*T_x      (momentum)
    psi_y T_x          - psi_x T_y         = Lap T                          (energy)

Solved here in the equivalent vorticity-streamfunction-temperature form
(w = -Lap psi = physical vorticity; u = psi_y, v = -psi_x) by pseudo-transient
marching to steady state:

    w_t + u w_x + v w_y = Pr Lap w + Ra*Pr*T_x
    T_t + u T_x + v T_y = Lap T
    Lap psi = -w

GEOMETRY / BCs (Fig. 9):  unit square [0,1]^2.
    Temperature:  bottom y=0  -> T=1 (hot),  top y=1 -> T=0 (cold),
                  sidewalls x=0,1 -> dT/dx = 0 (adiabatic).
    Velocity:     no-slip on all four walls (psi=0, dpsi/dn=0); Thom wall vorticity.

FIDELITY  =  physical-space resolution Nv = NT  (Sec 4.3):
    LF: 20 ,  MF: 50 ,  HF: 100   (grid points per direction).

PARAMETER:  Rayleigh number Ra in [2.6e3, 1.0e5]  (one-roll convection regime).

SAMPLES (equally spaced in Ra):  17 LF, 9 MF, 5 HF.
    With these counts the locations are NESTED:  D_HF subset D_MF subset D_LF
    (HF = LF[::4], MF = LF[::2]) -- consistent with the paper's nested design.

FIELD REPRESENTATION (Sec 4.3 / Fig 9b):  [0,1]^2 split into 7x7 = 49 square
    spectral elements; local temperature approximated by a 4th-order tensor-product
    Legendre expansion -> 25 local DOF per element.  We provide, per sample, the
    L2 Legendre coefficients  T_legendre[sample, element(49), mode(25)].
    Mode index = p*5+q for Legendre degrees p,q in {0..4} (x then y).  This 49x25
    representation has the SAME dimension at every fidelity (the shared GPR basis).

--------------------------------------------------------------------------------
ASSUMPTIONS (not fixed by the paper text, documented for reproducibility):
  * Solver: 2nd-order finite-difference vorticity-streamfunction (not spectral
    elements); fidelity proxied by FD grid resolution 20/50/100.  The resulting
    discretization-error gap between coarse and fine solves is the genuine
    multi-fidelity signal.
  * Prandtl number Pr = 0.71 (air); Ra_c for this rigid/adiabatic square cavity
    sits in the low-10^3..10^4 range, so the lowest Ra samples are near onset.

Run:  python3 generate_rayleigh_benard_mf.py
"""
import os, json, time
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from numpy.polynomial.legendre import leggauss, legval
from scipy.interpolate import RegularGridInterpolator

OUT = "/home/nicksung/Downloads/mf_field_data/data"
os.makedirs(OUT, exist_ok=True)

# ---- paper-defined constants -------------------------------------------------
RA_MIN, RA_MAX = 2.6e3, 1.0e5
PR = 0.71
LEVELS = {"LF": dict(n=20, nsamp=17),
          "MF": dict(n=50, nsamp=9),
          "HF": dict(n=100, nsamp=5)}
N_ELEM_1D = 7          # 7x7 = 49 spectral elements
LEG_ORDER = 4          # 4th-order -> 5 modes per direction -> 25 per element


# =============================================================================
# Solver
# =============================================================================
def assemble_neg_laplacian(m):
    """(-Laplacian) on an m x m interior grid, Dirichlet-0, 5-point, h=1/(m+1)."""
    h = 1.0 / (m + 1)
    idx = np.arange(m * m).reshape(m, m)
    rows, cols, vals = [], [], []
    def add(r, c, v):
        rows.append(np.asarray(r).ravel()); cols.append(np.asarray(c).ravel())
        vals.append(np.asarray(v).ravel())
    add(idx, idx, np.full((m, m), 4.0 / h**2))
    add(idx[:, 1:], idx[:, :-1], np.full((m, m - 1), -1.0 / h**2))
    add(idx[:, :-1], idx[:, 1:], np.full((m, m - 1), -1.0 / h**2))
    add(idx[1:, :], idx[:-1, :], np.full((m - 1, m), -1.0 / h**2))
    add(idx[:-1, :], idx[1:, :], np.full((m - 1, m), -1.0 / h**2))
    return sp.csr_matrix((np.concatenate(vals),
                          (np.concatenate(rows), np.concatenate(cols))),
                         shape=(m * m, m * m))


def solve_ob(Ra, n, Pr=PR, max_steps=200000, tol=1e-6):
    """Steady Oberbeck-Boussinesq.  Returns T (n,n), psi (n,n) incl. boundaries.

    Row index = y (row 0 -> y=0 bottom hot, row n-1 -> y=1 top cold); col = x.
    """
    h = 1.0 / (n - 1)
    m = n - 2
    lu = spla.splu(assemble_neg_laplacian(m).tocsc())

    xs = np.linspace(0.0, 1.0, n)
    X = np.broadcast_to(xs, (n, n)).copy()
    Y = np.broadcast_to(xs[:, None], (n, n)).copy()

    T = (1.0 - Y) + 0.05 * np.sin(np.pi * X) * np.sin(np.pi * Y)   # one-roll seed
    T[0, :] = 1.0; T[-1, :] = 0.0
    w = np.zeros((n, n))

    def ddx(a): return (a[1:-1, 2:] - a[1:-1, :-2]) / (2 * h)
    def ddy(a): return (a[2:, 1:-1] - a[:-2, 1:-1]) / (2 * h)
    def lap(a): return (a[1:-1, 2:] + a[1:-1, :-2] + a[2:, 1:-1]
                        + a[:-2, 1:-1] - 4 * a[1:-1, 1:-1]) / h**2

    diff_dt = 0.2 * h**2 / max(Pr, 1.0)
    resid = np.inf
    for step in range(max_steps):
        psi = np.zeros((n, n))
        psi[1:-1, 1:-1] = lu.solve(w[1:-1, 1:-1].ravel()).reshape(m, m)

        u = np.zeros((n, n)); v = np.zeros((n, n))
        u[1:-1, 1:-1] = (psi[2:, 1:-1] - psi[:-2, 1:-1]) / (2 * h)
        v[1:-1, 1:-1] = -(psi[1:-1, 2:] - psi[1:-1, :-2]) / (2 * h)

        vmax = max(np.abs(u).max(), np.abs(v).max(), 1e-12)
        dt = min(diff_dt, 0.4 * h / vmax)

        ui, vi = u[1:-1, 1:-1], v[1:-1, 1:-1]
        wn = w.copy()
        wn[1:-1, 1:-1] = w[1:-1, 1:-1] + dt * (
            -ui * ddx(w) - vi * ddy(w) + Pr * lap(w) + Ra * Pr * ddx(T))
        Tn = T.copy()
        dT_int = dt * (-ui * ddx(T) - vi * ddy(T) + lap(T))
        Tn[1:-1, 1:-1] = T[1:-1, 1:-1] + dT_int

        Tn[0, :] = 1.0; Tn[-1, :] = 0.0
        Tn[:, 0] = Tn[:, 1]; Tn[:, -1] = Tn[:, -2]            # adiabatic sides
        wn[0, :] = -2.0 * psi[1, :] / h**2                    # Thom no-slip walls
        wn[-1, :] = -2.0 * psi[-2, :] / h**2
        wn[:, 0] = -2.0 * psi[:, 1] / h**2
        wn[:, -1] = -2.0 * psi[:, -2] / h**2

        if not np.isfinite(wn).all():
            raise FloatingPointError(f"blow-up Ra={Ra:.3g} n={n} step={step}")

        resid = np.abs(dT_int).max() / dt
        w, T = wn, Tn
        if step > 50 and resid < tol:
            break
    return T, psi, step, resid


# =============================================================================
# Legendre spectral-element representation  ->  (49, 25) coefficients
# =============================================================================
_GL_NODES, _GL_W = leggauss(LEG_ORDER + 2)        # exact for our products
_NMODE = LEG_ORDER + 1                             # 5 modes per direction

def _legmat():
    """P[a, p] = Legendre_p(node_a) for p=0..LEG_ORDER at the GL nodes."""
    P = np.empty((len(_GL_NODES), _NMODE))
    for p in range(_NMODE):
        c = np.zeros(_NMODE); c[p] = 1.0
        P[:, p] = legval(_GL_NODES, c)
    return P
_PMAT = _legmat()

def legendre_coeffs(T, n):
    """L2 Legendre coefficients per element: returns (49, 25).

    Element (I,J) spans x in [I/7,(I+1)/7], y in [J/7,(J+1)/7]; local coords in
    [-1,1].  c_{pq} = (2p+1)/2 (2q+1)/2 * sum_ab wa wb Pp(a)Pq(b) T(xa,yb).
    Mode index = p*5 + q.  Element index = I*7 + J.
    """
    xs = np.linspace(0.0, 1.0, n)
    interp = RegularGridInterpolator((xs, xs), T, method="linear")  # (y,x) -> T
    norm = (2 * np.arange(_NMODE) + 1) / 2.0                          # (5,)
    coeffs = np.empty((N_ELEM_1D * N_ELEM_1D, _NMODE * _NMODE))
    half = 1.0 / (2 * N_ELEM_1D)
    for I in range(N_ELEM_1D):
        xc = (I + 0.5) / N_ELEM_1D
        xq = xc + half * _GL_NODES                                   # phys x nodes
        for J in range(N_ELEM_1D):
            yc = (J + 0.5) / N_ELEM_1D
            yq = yc + half * _GL_NODES
            XX, YY = np.meshgrid(xq, yq, indexing="ij")
            Tq = interp(np.stack([YY.ravel(), XX.ravel()], -1)).reshape(len(xq), -1)
            # c[p,q] = norm_p norm_q sum_a wa Pp(a) sum_b wb Pq(b) Tq[a,b]
            WT = (_GL_W[:, None] * Tq) * _GL_W[None, :]              # (a,b)
            c = _PMAT.T @ WT @ _PMAT                                  # (p,q)
            c *= norm[:, None] * norm[None, :]
            coeffs[I * N_ELEM_1D + J] = c.ravel()
    return coeffs


# =============================================================================
# Driver
# =============================================================================
def main():
    t0 = time.time()
    # nested, equally-spaced Ra (LF master grid; MF=LF[::2], HF=LF[::4])
    ra_lf = np.linspace(RA_MIN, RA_MAX, LEVELS["LF"]["nsamp"])
    ra = {"LF": ra_lf, "MF": ra_lf[::2], "HF": ra_lf[::4]}
    assert len(ra["MF"]) == 9 and len(ra["HF"]) == 5

    out = {}
    out["Pr"] = np.float64(PR)
    out["ra_range"] = np.array([RA_MIN, RA_MAX])
    out["n_elem"] = np.int64(N_ELEM_1D * N_ELEM_1D)
    out["leg_order"] = np.int64(LEG_ORDER)
    # nested index maps into the LF Ra array
    out["nested_idx_MF"] = np.arange(0, LEVELS["LF"]["nsamp"], 2)
    out["nested_idx_HF"] = np.arange(0, LEVELS["LF"]["nsamp"], 4)

    for lvl, cfg in LEVELS.items():
        n = cfg["n"]
        rs = ra[lvl]
        xs = np.linspace(0.0, 1.0, n)
        T_all = np.empty((len(rs), n, n), np.float32)
        psi_all = np.empty((len(rs), n, n), np.float32)
        leg_all = np.empty((len(rs), N_ELEM_1D**2, _NMODE**2), np.float32)
        print(f"[{lvl}] n={n}  {len(rs)} samples", flush=True)
        for i, Ra in enumerate(rs):
            ts = time.time()
            T, psi, step, resid = solve_ob(Ra, n)
            leg = legendre_coeffs(T, n)
            T_all[i] = T; psi_all[i] = psi; leg_all[i] = leg
            print(f"   Ra={Ra:8.0f}  steps={step:6d}  resid={resid:.1e}  "
                  f"psi_max={np.abs(psi).max():7.3f}  {time.time()-ts:5.1f}s", flush=True)
        out[f"ra_{lvl}"] = rs.astype(np.float64)
        out[f"x_{lvl}"] = xs.astype(np.float64)
        out[f"T_{lvl}"] = T_all
        out[f"psi_{lvl}"] = psi_all
        out[f"Tleg_{lvl}"] = leg_all

    path = os.path.join(OUT, "rayleigh_benard_mf.npz")
    np.savez_compressed(path, **out)
    size_mb = os.path.getsize(path) / 1e6

    manifest = {
        "name": "rayleigh_benard_mf",
        "aka": "ob_boussinesq_mf",
        "pde": "Steady 2D Oberbeck-Boussinesq natural convection (streamfunction-temperature)",
        "paper": ("Parussini, Venturi, Perdikaris, Karniadakis, "
                  "'Multi-fidelity Gaussian process regression for prediction of "
                  "random fields', J. Comput. Phys. 336 (2017) 36-50, Sec. 4.3"),
        "availability": "recreate-only (no public dataset / no released solver)",
        "domain": "unit square [0,1]^2",
        "bcs": {"T_bottom_y0": 1.0, "T_top_y1": 0.0,
                "T_sidewalls": "adiabatic dT/dx=0", "velocity": "no-slip all walls"},
        "parameter": "Rayleigh number Ra",
        "Ra_range": [RA_MIN, RA_MAX], "Pr": PR,
        "fidelity": "physical-space resolution Nv=NT (grid points per direction)",
        "levels": {lvl: {"n": cfg["n"], "n_samples": cfg["nsamp"]}
                   for lvl, cfg in LEVELS.items()},
        "ra_LF": ra["LF"].tolist(), "ra_MF": ra["MF"].tolist(), "ra_HF": ra["HF"].tolist(),
        "nested": "HF = LF[::4] subset MF = LF[::2] subset LF (equally spaced in Ra)",
        "field_representation": {
            "elements": "7x7 = 49 square spectral elements",
            "local_basis": "4th-order tensor-product Legendre, 25 modes/element",
            "array": "Tleg_<LVL> shape (n_samples, 49, 25); elem=I*7+J, mode=p*5+q"},
        "arrays": {
            "ra_<LVL>": "(n_samples,) Rayleigh numbers",
            "x_<LVL>": "(n,) uniform grid coords (same for x and y)",
            "T_<LVL>": "(n_samples, n, n) steady temperature field (row=y from y=0 bottom)",
            "psi_<LVL>": "(n_samples, n, n) steady streamfunction field",
            "Tleg_<LVL>": "(n_samples, 49, 25) Legendre coeffs of local temperature",
            "nested_idx_MF/HF": "indices of MF/HF Ra within the LF Ra array"},
        "assumptions": [
            "FD vorticity-streamfunction solver (paper used spectral elements); "
            "fidelity proxied by grid resolution -> genuine discretization-error gap",
            "Pr=0.71 (air); paper text does not fix Pr"],
        "file": "rayleigh_benard_mf.npz", "file_mb": round(size_mb, 3),
    }
    with open(os.path.join(OUT, "rayleigh_benard_mf.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"\nsaved rayleigh_benard_mf.npz  ({size_mb:.2f} MB)  "
          f"in {time.time()-t0:.1f}s -> {OUT}")


if __name__ == "__main__":
    main()
