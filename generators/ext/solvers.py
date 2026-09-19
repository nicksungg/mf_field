"""
Reusable parametric PDE field solvers (single source of truth).

Each solver is a PURE function:  solve(params, grid) -> fields
    params : (N, d) array of PDE parameters
    grid   : fidelity spec. int n for 2D spatial PDEs; (nx, nt) for space-time PDEs.
    return : (N, ...) field array at that resolution.

Because the SAME params can be solved at ANY grid, you get aligned multi-fidelity
data for free: call solve(params, g) for each g in your fidelity list.

REGISTRY[name] gives: solve, param_names, ranges (for sampling), kind, default grids.
Use make_dataset.py for a CLI, or import directly:

    from solvers import REGISTRY, sample_params
    P = sample_params("helmholtz_2d", 500, seed=0)
    lo = REGISTRY["helmholtz_2d"]["solve"](P, 16)
    hi = REGISTRY["helmholtz_2d"]["solve"](P, 64)
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


# ---- shared helpers ---------------------------------------------------------
def assemble_elliptic(n, a):
    """-div(a grad u), Dirichlet 0, on n x n interior nodes (h = 1/(n+1))."""
    h = 1.0 / (n + 1)
    ap = np.pad(a, 1, mode="edge")
    aC = ap[1:-1, 1:-1]
    aW = 0.5 * (aC + ap[1:-1, 0:-2]); aE = 0.5 * (aC + ap[1:-1, 2:])
    aS = 0.5 * (aC + ap[0:-2, 1:-1]); aN = 0.5 * (aC + ap[2:, 1:-1])
    idx = np.arange(n * n).reshape(n, n)
    rows, cols, vals = [], [], []
    def add(r, c, v): rows.append(r.ravel()); cols.append(c.ravel()); vals.append(v.ravel())
    add(idx, idx, (aW + aE + aS + aN) / h**2)
    add(idx[:, 1:], idx[:, :-1], -aW[:, 1:] / h**2)
    add(idx[:, :-1], idx[:, 1:], -aE[:, :-1] / h**2)
    add(idx[1:, :], idx[:-1, :], -aS[1:, :] / h**2)
    add(idx[:-1, :], idx[1:, :], -aN[:-1, :] / h**2)
    return sp.csr_matrix((np.concatenate(vals),
                          (np.concatenate(rows), np.concatenate(cols))),
                         shape=(n * n, n * n))


def grid_xy(n):
    h = 1.0 / (n + 1)
    x = np.linspace(h, 1 - h, n)
    return np.meshgrid(x, x, indexing="xy")


# ============================== SOLVERS ======================================
def solve_helmholtz(params, n):
    X, Y = grid_xy(n)
    A0 = -assemble_elliptic(n, np.ones((n, n)))      # = Delta
    I = sp.identity(n * n)
    out = np.empty((len(params), n, n))
    for i, (k, sx, sy) in enumerate(params):
        A = (A0 + (k**2) * I).tocsc()
        f = np.exp(-((X - sx)**2 + (Y - sy)**2) / (2 * 0.04**2))
        out[i] = np.real(spla.spsolve(A, f.ravel())).reshape(n, n)
    return out


def solve_rayleigh_benard(params, n, Pr=1.0, t_end=0.06):
    h = 1.0 / (n - 1); m = n - 2
    lu = spla.splu(assemble_elliptic(m, np.ones((m, m))).tocsc())
    xs = np.linspace(0, 1, n)
    X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
    out = np.empty((len(params), n, n))
    for s, (lRa,) in enumerate(np.atleast_2d(params)):
        Ra = 10**lRa
        T = (1.0 - Y) + 0.05 * np.sin(2 * np.pi * X) * np.sin(np.pi * Y)
        T[0, :] = 1.0; T[-1, :] = 0.0
        w = np.zeros((n, n))
        dt = 0.15 * h**2 / Pr
        for _ in range(int(t_end / dt)):
            psi = np.zeros((n, n))
            psi[1:-1, 1:-1] = lu.solve(w[1:-1, 1:-1].ravel()).reshape(m, m)
            u = np.zeros((n, n)); v = np.zeros((n, n))
            u[1:-1, 1:-1] = (psi[2:, 1:-1] - psi[:-2, 1:-1]) / (2 * h)
            v[1:-1, 1:-1] = -(psi[1:-1, 2:] - psi[1:-1, :-2]) / (2 * h)
            ddx = lambda a: (a[1:-1, 2:] - a[1:-1, :-2]) / (2 * h)
            ddy = lambda a: (a[2:, 1:-1] - a[:-2, 1:-1]) / (2 * h)
            lap = lambda a: (a[1:-1, 2:] + a[1:-1, :-2] + a[2:, 1:-1]
                             + a[:-2, 1:-1] - 4 * a[1:-1, 1:-1]) / h**2
            ui, vi = u[1:-1, 1:-1], v[1:-1, 1:-1]
            wn = w.copy()
            wn[1:-1, 1:-1] = w[1:-1, 1:-1] + dt * (
                -ui * ddx(w) - vi * ddy(w) + Pr * lap(w) + Ra * Pr * ddx(T))
            Tn = T.copy()
            Tn[1:-1, 1:-1] = T[1:-1, 1:-1] + dt * (-ui * ddx(T) - vi * ddy(T) + lap(T))
            Tn[0, :] = 1.0; Tn[-1, :] = 0.0; Tn[:, 0] = Tn[:, 1]; Tn[:, -1] = Tn[:, -2]
            wn[0, :] = -2 * psi[1, :] / h**2; wn[-1, :] = -2 * psi[-2, :] / h**2
            wn[:, 0] = -2 * psi[:, 1] / h**2; wn[:, -1] = -2 * psi[:, -2] / h**2
            w, T = wn, Tn
            if not np.isfinite(w).all(): break
        out[s] = T
    return out


def solve_gray_scott(params, n, Du=0.16, Dv=0.08, steps=6000):
    lap = lambda a: (np.roll(a, 1, 0) + np.roll(a, -1, 0)
                     + np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4 * a)
    out = np.empty((len(params), n, n))
    for s, (F, k) in enumerate(params):
        U = np.ones((n, n)); V = np.zeros((n, n))
        c = n // 2; r = max(2, n // 12)
        U[c - r:c + r, c - r:c + r] = 0.50; V[c - r:c + r, c - r:c + r] = 0.25
        for _ in range(steps):
            uvv = U * V * V
            U += Du * lap(U) - uvv + F * (1 - U)
            V += Dv * lap(V) + uvv - (F + k) * V
        out[s] = V
    return out


def solve_wave(params, n, t_end=0.4):
    h = 1.0 / (n - 1)
    xs = np.linspace(0, 1, n)
    X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
    out = np.empty((len(params), n, n))
    for s, (c, bx, by) in enumerate(params):
        dt = 0.35 * h / c
        lam = (c * dt / h)**2
        u0 = np.exp(-((X - bx)**2 + (Y - by)**2) / (2 * 0.05**2))
        def L(a):
            o = np.zeros_like(a)
            o[1:-1, 1:-1] = (a[1:-1, 2:] + a[1:-1, :-2]
                             + a[2:, 1:-1] + a[:-2, 1:-1] - 4 * a[1:-1, 1:-1])
            return o
        # 2nd-order first step (u_t=0): u^1 = u^0 + 0.5 λ Δu^0
        cur = u0 + 0.5 * lam * L(u0)
        cur[0, :] = cur[-1, :] = cur[:, 0] = cur[:, -1] = 0.0
        up = u0
        for _ in range(int(t_end / dt) - 1):
            nxt = 2 * cur - up + lam * L(cur)
            nxt[0, :] = nxt[-1, :] = nxt[:, 0] = nxt[:, -1] = 0.0
            up, cur = cur, nxt
        out[s] = cur
    return out


def solve_eikonal(params, n):
    h = 1.0 / (n - 1)
    xs = np.linspace(0, 1, n)
    X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
    out = np.empty((len(params), n, n))
    for s, (sx, sy, lsp) in enumerate(params):
        speed = np.ones((n, n))
        speed[(X - 0.5)**2 + (Y - 0.5)**2 < 0.15**2] = 10**lsp
        f = 1.0 / speed
        T = np.full((n, n), 1e6)
        si = int(round(sy * (n - 1))); sj = int(round(sx * (n - 1))); T[si, sj] = 0.0
        for _ in range(4 * n):
            Tx = np.minimum(np.roll(T, 1, 1), np.roll(T, -1, 1))
            Ty = np.minimum(np.roll(T, 1, 0), np.roll(T, -1, 0))
            a = np.minimum(Tx, Ty); b = np.maximum(Tx, Ty); fh = f * h
            cand = np.where((b - a) < fh,
                            0.5 * (a + b + np.sqrt(np.clip(2 * fh**2 - (b - a)**2, 0, None))),
                            a + fh)
            Tnew = np.minimum(T, cand); Tnew[si, sj] = 0.0
            if np.max(np.abs(Tnew - T)) < 1e-7: T = Tnew; break
            T = Tnew
        out[s] = T
    return out


def ch_ic(n, sd, mean):
    """Resolution-independent Cahn-Hilliard IC (same continuous field on any grid)."""
    r = np.random.default_rng(5000 + sd)
    xs = np.linspace(0, 2 * np.pi, n, endpoint=False)
    Xg, Yg = np.meshgrid(xs, xs); c = np.zeros((n, n))
    for _ in range(12):
        kx, ky = r.integers(1, 5), r.integers(1, 5); ph = r.uniform(0, 2 * np.pi)
        c += r.uniform(-1, 1) * np.cos(kx * Xg + ky * Yg + ph)
    return 0.1 * c / np.max(np.abs(c)) + mean


def solve_cahn_hilliard(params, n, M=1.0, steps=4000, dt=1e-5):
    kx = np.fft.fftfreq(n, d=1.0 / n); KX, KY = np.meshgrid(kx, kx)
    k2 = KX**2 + KY**2; k4 = k2**2
    out = np.empty((len(params), n, n))
    for s, (lg, mean) in enumerate(params):
        gamma = 10**lg; c = ch_ic(n, s, mean)
        for _ in range(steps):
            ch = np.fft.fft2(c**3 - c); chat = np.fft.fft2(c)
            chat = (chat - dt * M * k2 * ch) / (1 + dt * M * gamma * k4)
            c = np.real(np.fft.ifft2(chat))
        out[s] = c
    return out


def solve_kuramoto_sivashinsky(params, grid, t_end=60.0, substeps=50):
    nx, nt = grid
    out = np.empty((len(params), nt, nx))
    for s, (L, amp, ph) in enumerate(params):
        x = L * np.arange(nx) / nx
        k = 2 * np.pi * np.fft.fftfreq(nx, d=L / nx)
        E = 1.0 / (1 - (t_end / (nt * substeps)) * (k**2 - k**4))
        dt = t_end / (nt * substeps)
        u = amp * np.cos(2 * np.pi * x / L + ph) * (1 + np.sin(2 * np.pi * x / L))
        uh = np.fft.fft(u); rec = np.empty((nt, nx)); rec[0] = u
        for t in range(1, nt):
            for _ in range(substeps):
                nl = -0.5 * 1j * k * np.fft.fft(np.real(np.fft.ifft(uh))**2)
                uh = E * (uh + dt * nl)
            rec[t] = np.real(np.fft.ifft(uh))
        out[s] = rec
    return out


# ============================== REGISTRY =====================================
REGISTRY = {
    "helmholtz_2d": dict(
        solve=solve_helmholtz, kind="2d",
        param_names=["wavenumber_k", "source_x", "source_y"],
        ranges=[(4.0, 12.0), (0.3, 0.7), (0.3, 0.7)],
        default_grids=[24, 96], pde="Δu + k²u = f"),
    "rayleigh_benard_2d": dict(
        solve=solve_rayleigh_benard, kind="2d",
        param_names=["log10_rayleigh"], ranges=[(3.0, 4.3)],
        default_grids=[24, 64], pde="Boussinesq convection (T field)"),
    "gray_scott_2d": dict(
        solve=solve_gray_scott, kind="2d",
        param_names=["feed_F", "kill_k"], ranges=[(0.026, 0.058), (0.055, 0.065)],
        default_grids=[24, 72], pde="Gray-Scott reaction-diffusion (v field)"),
    "wave_2d": dict(
        solve=solve_wave, kind="2d",
        param_names=["wave_speed", "source_x", "source_y"],
        ranges=[(0.6, 1.8), (0.3, 0.7), (0.3, 0.7)],
        default_grids=[24, 80], pde="u_tt = c²Δu"),
    "eikonal_2d": dict(
        solve=solve_eikonal, kind="2d",
        param_names=["source_x", "source_y", "log10_inclusion_speed"],
        ranges=[(0.2, 0.8), (0.2, 0.8), (-0.7, 0.7)],
        default_grids=[24, 64], pde="|∇T| = 1/speed (travel time)"),
    "cahn_hilliard_2d": dict(
        solve=solve_cahn_hilliard, kind="2d",
        param_names=["log10_gamma", "mean_composition"],
        ranges=[(-3.7, -2.7), (-0.1, 0.1)],
        default_grids=[24, 64], pde="c_t = M∇²(c³-c-γ∇²c)"),
    "kuramoto_sivashinsky_1d": dict(
        solve=solve_kuramoto_sivashinsky, kind="spacetime",
        param_names=["domain_L", "ic_amplitude", "ic_phase"],
        ranges=[(22.0, 44.0), (0.6, 1.0), (0.0, 2 * np.pi)],
        default_grids=[(64, 40), (256, 120)], pde="KS spatiotemporal chaos"),
}


def sample_params(name, N, seed=0):
    """Latin-uniform random parameters in the registered ranges."""
    rng = np.random.default_rng(seed)
    r = REGISTRY[name]["ranges"]
    return np.column_stack([rng.uniform(lo, hi, N) for (lo, hi) in r])


# ======================= REFERENCE-GRADE BACKENDS ============================
# Same solve(params, grid) interface; higher-accuracy / third-party solvers.

def _etdrk4_coeffs(L, dt, Mc=32):
    """Kassam & Trefethen (2005) ETDRK4 coefficients via contour integral.
    L is the (Fourier-diagonal) linear operator array of any shape."""
    E = np.exp(dt * L); E2 = np.exp(dt * L / 2)
    r = np.exp(1j * np.pi * (np.arange(1, Mc + 1) - 0.5) / Mc)
    LR = dt * L[..., None] + r
    Q = dt * np.real(np.mean((np.exp(LR / 2) - 1) / LR, axis=-1))
    f1 = dt * np.real(np.mean((-4 - LR + np.exp(LR) * (4 - 3 * LR + LR**2)) / LR**3, axis=-1))
    f2 = dt * np.real(np.mean((2 + LR + np.exp(LR) * (-2 + LR)) / LR**3, axis=-1))
    f3 = dt * np.real(np.mean((-4 - 3 * LR - LR**2 + np.exp(LR) * (4 - LR)) / LR**3, axis=-1))
    return E, E2, Q, f1, f2, f3


def _etdrk4_step(v, Nf, E, E2, Q, f1, f2, f3):
    Nv = Nf(v)
    a = E2 * v + Q * Nv; Na = Nf(a)
    b = E2 * v + Q * Na; Nb = Nf(b)
    c = E2 * a + Q * (2 * Nb - Nv); Nc = Nf(c)
    return E * v + Nv * f1 + 2 * (Na + Nb) * f2 + Nc * f3


def solve_kuramoto_sivashinsky_ref(params, grid, t_end=60.0):
    """Reference KS: Fourier pseudo-spectral + ETDRK4 (Kassam-Trefethen 2005)."""
    nx, nt = grid
    out = np.empty((len(params), nt, nx))
    for s, (L, amp, ph) in enumerate(params):
        x = L * np.arange(nx) / nx
        k = 2 * np.pi * np.fft.fftfreq(nx, d=L / nx)
        Lop = k**2 - k**4
        per_frame = t_end / (nt - 1)
        sub = max(1, int(np.ceil(per_frame / 0.25)))
        dt = per_frame / sub
        E, E2, Q, f1, f2, f3 = _etdrk4_coeffs(Lop, dt)
        Nf = lambda v: -0.5j * k * np.fft.fft(np.real(np.fft.ifft(v))**2)
        u = amp * np.cos(2 * np.pi * x / L + ph) * (1 + np.sin(2 * np.pi * x / L))
        v = np.fft.fft(u); rec = np.empty((nt, nx)); rec[0] = u
        for t in range(1, nt):
            for _ in range(sub):
                v = _etdrk4_step(v, Nf, E, E2, Q, f1, f2, f3)
            rec[t] = np.real(np.fft.ifft(v))
        out[s] = rec
    return out


def solve_cahn_hilliard_ref(params, n, M=1.0, t_end=0.04, dt=1e-3):
    """Reference Cahn-Hilliard: Fourier spectral + ETDRK4 (exact eq. match)."""
    kx = np.fft.fftfreq(n, d=1.0 / n); KX, KY = np.meshgrid(kx, kx)
    k2 = KX**2 + KY**2
    Lop = M * k2 - M * (10.0**0) * k2**2   # gamma filled per-sample below
    out = np.empty((len(params), n, n))
    for s, (lg, mean) in enumerate(params):
        gamma = 10**lg
        Lop = M * k2 - M * gamma * k2**2
        E, E2, Q, f1, f2, f3 = _etdrk4_coeffs(Lop, dt)
        Nf = lambda v: -M * k2 * np.fft.fft2(np.real(np.fft.ifft2(v))**3)
        c = ch_ic(n, s, mean); v = np.fft.fft2(c)
        for _ in range(int(round(t_end / dt))):
            v = _etdrk4_step(v, Nf, E, E2, Q, f1, f2, f3)
        out[s] = np.real(np.fft.ifft2(v))
    return out


def solve_eikonal_ref(params, n):
    """Reference eikonal: Fast Marching Method (scikit-fmm)."""
    import skfmm
    h = 1.0 / (n - 1)
    xs = np.linspace(0, 1, n)
    X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
    out = np.empty((len(params), n, n))
    for s, (sx, sy, lsp) in enumerate(params):
        speed = np.ones((n, n))
        speed[(X - 0.5)**2 + (Y - 0.5)**2 < 0.15**2] = 10**lsp
        phi = np.sqrt((X - sx)**2 + (Y - sy)**2) - 1.5 * h   # tiny source circle
        out[s] = skfmm.travel_time(phi, speed, dx=h)
    return out


def solve_gray_scott_ref(params, n, Du=0.16, Dv=0.08, t_end=6000.0):
    """Reference Gray-Scott: independent third-party solver (py-pde), dx=1 to
    match the in-house discrete diffusion (unit grid spacing)."""
    import pde
    grid = pde.CartesianGrid([[0, n], [0, n]], [n, n], periodic=True)
    out = np.empty((len(params), n, n))
    c = n // 2; r = max(2, n // 12)
    for s, (F, k) in enumerate(params):
        U = pde.ScalarField(grid, 1.0); V = pde.ScalarField(grid, 0.0)
        U.data[c - r:c + r, c - r:c + r] = 0.50
        V.data[c - r:c + r, c - r:c + r] = 0.25
        state = pde.FieldCollection([U, V], labels=["u", "v"])
        eq = pde.PDE(
            {"u": f"{Du}*laplace(u) - u*v**2 + {F}*(1-u)",
             "v": f"{Dv}*laplace(v) + u*v**2 - {F + k}*v"})
        res = eq.solve(state, t_range=t_end, dt=1.0, tracker=None)
        out[s] = res[1].data
    return out


for _n, _ref in [("kuramoto_sivashinsky_1d", solve_kuramoto_sivashinsky_ref),
                 ("cahn_hilliard_2d", solve_cahn_hilliard_ref),
                 ("eikonal_2d", solve_eikonal_ref),
                 ("gray_scott_2d", solve_gray_scott_ref)]:
    REGISTRY[_n]["reference"] = _ref
