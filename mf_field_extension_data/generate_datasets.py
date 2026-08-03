"""
Multi-fidelity field-prediction dataset generator (NON-REPLICA suite).

Every dataset:
    params : (N, d)  float32   -- PDE parameter vector (the INPUT)
    lf     : (N, ...)          -- low-fidelity field  (COARSE solve of the SAME params)
    hf     : (N, ...)          -- high-fidelity field (FINE  solve of the SAME params)
    param_names : (d,) str

Fidelities are ALIGNED/NESTED: lf[i] and hf[i] are the same parameter mu[i]
solved on a coarse vs. fine grid -> genuine discretization-error fidelity gap.

These PDEs were chosen to AVOID overlap with an existing collection that already
covers: Poisson, heat, Darcy, advection-diffusion, Allen-Cahn, Burgers,
lid-driven cavity, generic fluid, ERA5.  New operator types here:
  Helmholtz (indefinite), Rayleigh-Benard (thermal convection),
  Gray-Scott (two-species reaction-diffusion / Turing), Wave (hyperbolic),
  Eikonal (Hamilton-Jacobi), Cahn-Hilliard (4th-order conservative),
  Kuramoto-Sivashinsky (chaotic 4th-order, space-time).

Run:  python3 generate_datasets.py
"""
import os, json, time, traceback
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

OUT = "/home/nicksung/Downloads/mf_field_data/data"
os.makedirs(OUT, exist_ok=True)
MANIFEST = []


# ---- shared variable-coefficient elliptic operator -div(a grad u), Dirichlet 0
def assemble_elliptic(n, a):
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


def save(name, pde, params, param_names, lf, hf, desc, domain="unit square [0,1]^2"):
    path = os.path.join(OUT, name + ".npz")
    np.savez_compressed(path, params=params.astype(np.float32),
                        lf=lf.astype(np.float32), hf=hf.astype(np.float32),
                        param_names=np.array(param_names))
    size_mb = os.path.getsize(path) / 1e6
    MANIFEST.append({
        "name": name, "pde": pde, "description": desc, "domain": domain,
        "n_samples": int(params.shape[0]), "param_dim": int(params.shape[1]),
        "param_names": param_names,
        "param_ranges": [[float(params[:, k].min()), float(params[:, k].max())]
                         for k in range(params.shape[1])],
        "lf_shape": list(lf.shape[1:]), "hf_shape": list(hf.shape[1:]),
        "fidelity": "aligned/nested: lf[i],hf[i] same params, coarse vs fine grid",
        "file": name + ".npz", "file_mb": round(size_mb, 3),
    })
    print(f"  saved {name:26s} N={params.shape[0]:4d}  "
          f"LF{tuple(lf.shape[1:])} HF{tuple(hf.shape[1:])}  {size_mb:6.2f} MB")


# =============================================================================
# 1. HELMHOLTZ 2D :  Delta u + k^2 u = f  (indefinite).  params: k, src_x, src_y
# =============================================================================
def gen_helmholtz(N=200, n_lf=24, n_hf=96, seed=4):
    rng = np.random.default_rng(seed)
    P = np.column_stack([rng.uniform(4.0, 12.0, N),
                         rng.uniform(0.3, 0.7, N), rng.uniform(0.3, 0.7, N)])
    def solve(n):
        X, Y = grid_xy(n)
        L = assemble_elliptic(n, np.ones((n, n)))     # = -Delta
        I = sp.identity(n * n)
        out = np.empty((N, n, n))
        for i, (k, sx, sy) in enumerate(P):
            A = (-L + (k**2) * I).tocsc()
            f = np.exp(-((X - sx)**2 + (Y - sy)**2) / (2 * 0.04**2))
            out[i] = np.real(spla.spsolve(A, f.ravel())).reshape(n, n)
        return out
    save("01_helmholtz_2d", "Δu + k²u = f, Dirichlet 0 (real part)",
         P, ["wavenumber_k", "source_x", "source_y"], solve(n_lf), solve(n_hf),
         "2D Helmholtz cavity field; indefinite operator, wavenumber + source as params.")


# =============================================================================
# 2. RAYLEIGH-BENARD CONVECTION 2D (Boussinesq, stream-vorticity-temperature).
#    params: log10(Rayleigh).  Output: steady-ish temperature field.
# =============================================================================
def gen_rayleigh_benard(N=80, n_lf=24, n_hf=64, seed=2):
    rng = np.random.default_rng(seed)
    P = rng.uniform(3.0, 4.3, (N, 1))            # log10 Ra  (1e3 .. ~2e4)
    Pr = 1.0
    def solve(n):
        h = 1.0 / (n - 1)
        m = n - 2
        Apsi = assemble_elliptic(m, np.ones((m, m))).tocsc()   # (-Delta) interior
        lu = spla.splu(Apsi)
        xs = np.linspace(0, 1, n)
        X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
        out = np.empty((N, n, n))
        for s, (lRa,) in enumerate(P):
            Ra = 10**lRa
            T = (1.0 - Y) + 0.05 * np.sin(2 * np.pi * X) * np.sin(np.pi * Y)
            T[0, :] = 1.0; T[-1, :] = 0.0
            w = np.zeros((n, n))
            dt = 0.15 * h**2 / Pr
            t_end = 0.06
            nsteps = int(t_end / dt)
            for _ in range(nsteps):
                psi = np.zeros((n, n))
                psi[1:-1, 1:-1] = lu.solve(w[1:-1, 1:-1].ravel()).reshape(m, m)
                u = np.zeros((n, n)); v = np.zeros((n, n))
                u[1:-1, 1:-1] = (psi[2:, 1:-1] - psi[:-2, 1:-1]) / (2 * h)
                v[1:-1, 1:-1] = -(psi[1:-1, 2:] - psi[1:-1, :-2]) / (2 * h)
                def ddx(a): return (a[1:-1, 2:] - a[1:-1, :-2]) / (2 * h)
                def ddy(a): return (a[2:, 1:-1] - a[:-2, 1:-1]) / (2 * h)
                def lap(a): return (a[1:-1, 2:] + a[1:-1, :-2] + a[2:, 1:-1]
                                    + a[:-2, 1:-1] - 4 * a[1:-1, 1:-1]) / h**2
                ui, vi = u[1:-1, 1:-1], v[1:-1, 1:-1]
                wn = w.copy()
                wn[1:-1, 1:-1] = w[1:-1, 1:-1] + dt * (
                    -ui * ddx(w) - vi * ddy(w) + Pr * lap(w) + Ra * Pr * ddx(T))
                Tn = T.copy()
                Tn[1:-1, 1:-1] = T[1:-1, 1:-1] + dt * (
                    -ui * ddx(T) - vi * ddy(T) + lap(T))
                # BCs: T fixed top/bottom, insulated sides
                Tn[0, :] = 1.0; Tn[-1, :] = 0.0
                Tn[:, 0] = Tn[:, 1]; Tn[:, -1] = Tn[:, -2]
                # vorticity walls (Thom, no-slip)
                wn[0, :] = -2 * psi[1, :] / h**2
                wn[-1, :] = -2 * psi[-2, :] / h**2
                wn[:, 0] = -2 * psi[:, 1] / h**2
                wn[:, -1] = -2 * psi[:, -2] / h**2
                w, T = wn, Tn
                if not np.isfinite(w).all(): break
            out[s] = T
        return out
    save("02_rayleigh_benard_2d",
         "Boussinesq convection (vorticity-streamfunction-temperature)",
         P, ["log10_rayleigh"], solve(n_lf), solve(n_hf),
         "2D Rayleigh-Benard temperature field vs Rayleigh number (hot bottom).",
         domain="unit square, hot bottom T=1 / cold top T=0")


# =============================================================================
# 3. GRAY-SCOTT 2D : two-species reaction-diffusion (Turing patterns).
#    params: feed F, kill k.  Output: v-species field at final time. Periodic.
# =============================================================================
def gen_gray_scott(N=100, n_lf=24, n_hf=72, seed=3):
    rng = np.random.default_rng(seed)
    P = np.column_stack([rng.uniform(0.026, 0.058, N),   # feed F
                         rng.uniform(0.055, 0.065, N)])  # kill k
    Du, Dv = 0.16, 0.08
    def lap(a): return (np.roll(a, 1, 0) + np.roll(a, -1, 0)
                        + np.roll(a, 1, 1) + np.roll(a, -1, 1) - 4 * a)
    def solve(n):
        out = np.empty((N, n, n))
        for s, (F, k) in enumerate(P):
            U = np.ones((n, n)); V = np.zeros((n, n))
            c = n // 2; r = max(2, n // 12)
            U[c - r:c + r, c - r:c + r] = 0.50
            V[c - r:c + r, c - r:c + r] = 0.25
            dt = 1.0
            for _ in range(6000):
                uvv = U * V * V
                U += dt * (Du * lap(U) - uvv + F * (1 - U))
                V += dt * (Dv * lap(V) + uvv - (F + k) * V)
            out[s] = V
        return out
    save("03_gray_scott_2d", "Gray-Scott reaction-diffusion (u,v), periodic",
         P, ["feed_F", "kill_k"], solve(n_lf), solve(n_hf),
         "2D Gray-Scott Turing patterns; output is v-species concentration field.")


# =============================================================================
# 4. WAVE EQUATION 2D : u_tt = c^2 Delta u, Dirichlet 0 (reflecting).
#    params: speed c, source x, source y.  Output: snapshot at t_end.
# =============================================================================
def gen_wave(N=150, n_lf=24, n_hf=80, seed=5):
    rng = np.random.default_rng(seed)
    P = np.column_stack([rng.uniform(0.6, 1.8, N),
                         rng.uniform(0.3, 0.7, N), rng.uniform(0.3, 0.7, N)])
    t_end = 0.4
    def solve(n):
        h = 1.0 / (n - 1)
        xs = np.linspace(0, 1, n)
        X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
        out = np.empty((N, n, n))
        for s, (c, bx, by) in enumerate(P):
            dt = 0.35 * h / c
            nsteps = int(t_end / dt)
            u0 = np.exp(-((X - bx)**2 + (Y - by)**2) / (2 * 0.05**2))
            up = u0.copy(); cur = u0.copy()
            lam = (c * dt / h)**2
            for _ in range(nsteps):
                lap = np.zeros_like(cur)
                lap[1:-1, 1:-1] = (cur[1:-1, 2:] + cur[1:-1, :-2]
                                   + cur[2:, 1:-1] + cur[:-2, 1:-1] - 4 * cur[1:-1, 1:-1])
                nxt = 2 * cur - up + lam * lap
                nxt[0, :] = nxt[-1, :] = nxt[:, 0] = nxt[:, -1] = 0.0
                up, cur = cur, nxt
            out[s] = cur
        return out
    save("04_wave_2d", "u_tt = c²Δu, Dirichlet 0 (reflecting)",
         P, ["wave_speed", "source_x", "source_y"], solve(n_lf), solve(n_hf),
         "2D wave field snapshot at t=0.4 from a Gaussian pulse; hyperbolic.")


# =============================================================================
# 5. EIKONAL 2D : |grad T| = slowness(x), T(source)=0  (Hamilton-Jacobi).
#    params: source x, source y, log10(inclusion speed).  Output: travel time.
# =============================================================================
def gen_eikonal(N=150, n_lf=24, n_hf=64, seed=6):
    rng = np.random.default_rng(seed)
    P = np.column_stack([rng.uniform(0.2, 0.8, N), rng.uniform(0.2, 0.8, N),
                         rng.uniform(-0.7, 0.7, N)])   # log10 speed in inclusion
    def solve(n):
        h = 1.0 / (n - 1)
        xs = np.linspace(0, 1, n)
        X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
        out = np.empty((N, n, n))
        for s, (sx, sy, lsp) in enumerate(P):
            speed = np.ones((n, n))
            speed[(X - 0.5)**2 + (Y - 0.5)**2 < 0.15**2] = 10**lsp
            f = 1.0 / speed                                   # slowness
            T = np.full((n, n), 1e6)
            si = int(round(sy * (n - 1))); sj = int(round(sx * (n - 1)))
            T[si, sj] = 0.0
            for _ in range(4 * n):                            # Jacobi-Godunov sweeps
                Tx = np.minimum(np.roll(T, 1, 1), np.roll(T, -1, 1))
                Ty = np.minimum(np.roll(T, 1, 0), np.roll(T, -1, 0))
                a = np.minimum(Tx, Ty); b = np.maximum(Tx, Ty)
                fh = f * h
                cand = a + fh
                mask = (b - a) < fh
                disc = 2 * fh**2 - (b - a)**2
                cand2 = 0.5 * (a + b + np.sqrt(np.clip(disc, 0, None)))
                cand = np.where(mask, cand2, cand)
                Tnew = np.minimum(T, cand)
                Tnew[si, sj] = 0.0
                if np.max(np.abs(Tnew - T)) < 1e-7:
                    T = Tnew; break
                T = Tnew
            out[s] = T
        return out
    save("05_eikonal_2d", "|∇T| = 1/speed(x), T(source)=0 (Hamilton-Jacobi)",
         P, ["source_x", "source_y", "log10_inclusion_speed"],
         solve(n_lf), solve(n_hf),
         "2D first-arrival travel-time field through a circular speed inclusion.")


# =============================================================================
# 6. CAHN-HILLIARD 2D : 4th-order conservative phase field (spinodal), periodic.
#    params: log10(gamma) interface energy, IC mean composition.  Spectral.
# =============================================================================
def gen_cahn_hilliard(N=100, n_lf=24, n_hf=64, seed=7):
    rng = np.random.default_rng(seed)
    P = np.column_stack([rng.uniform(-3.7, -2.7, N),    # log10 gamma
                         rng.uniform(-0.1, 0.1, N)])    # mean composition
    M = 1.0
    def ic_field(n, mean, seed=5000):
        # identical continuous IC on any grid: sum of fixed low Fourier modes.
        # FIXED seed (not the row index): a per-sample seed here hides ~48 IC dof
        # from the 2-param condition vector (the round-2 incompleteness defect
        # class) — export the drawn values into params if per-sample ICs are
        # ever wanted.
        r = np.random.default_rng(seed)
        xs = np.linspace(0, 2 * np.pi, n, endpoint=False)
        Xg, Yg = np.meshgrid(xs, xs)
        c = np.zeros((n, n))
        for _ in range(12):
            kx, ky = r.integers(1, 5), r.integers(1, 5)
            ph = r.uniform(0, 2 * np.pi)
            c += r.uniform(-1, 1) * np.cos(kx * Xg + ky * Yg + ph)
        c = 0.1 * c / np.max(np.abs(c)) + mean
        return c
    def solve(n):
        kx = np.fft.fftfreq(n, d=1.0 / n)
        KX, KY = np.meshgrid(kx, kx)
        k2 = KX**2 + KY**2; k4 = k2**2
        out = np.empty((N, n, n))
        for s in range(N):
            lg, mean = P[s]
            gamma = 10**lg
            c = ic_field(n, mean)
            dt = 1e-5
            for _ in range(4000):
                ch = np.fft.fft2(c**3 - c)
                chat = np.fft.fft2(c)
                chat = (chat - dt * M * k2 * ch) / (1 + dt * M * gamma * k4)
                c = np.real(np.fft.ifft2(chat))
            out[s] = c
        return out
    save("06_cahn_hilliard_2d", "c_t = M∇²(c³-c-γ∇²c), periodic (spectral)",
         P, ["log10_gamma", "mean_composition"], solve(n_lf), solve(n_hf),
         "2D Cahn-Hilliard spinodal decomposition; 4th-order conservative phase field.")


# =============================================================================
# 7. KURAMOTO-SIVASHINSKY 1D (space-time, chaotic 4th-order), periodic.
#    params: domain length L, IC amplitude, IC phase.  Output: u(x,t) field.
# =============================================================================
def gen_kuramoto_sivashinsky(N=120, nx_lf=64, nt_lf=40, nx_hf=256, nt_hf=120, seed=8):
    rng = np.random.default_rng(seed)
    P = np.column_stack([rng.uniform(22.0, 44.0, N),     # domain length L
                         rng.uniform(0.6, 1.0, N),       # IC amplitude
                         rng.uniform(0, 2 * np.pi, N)])   # IC phase
    t_end = 60.0
    def solve(nx, nt):
        out = np.empty((N, nt, nx))
        for s, (L, amp, ph) in enumerate(P):
            x = L * np.arange(nx) / nx
            k = 2 * np.pi * np.fft.fftfreq(nx, d=L / nx)
            Lk = k**2 - k**4                               # linear operator
            u = amp * np.cos(2 * np.pi * x / L + ph) * (1 + np.sin(2 * np.pi * x / L))
            dt = t_end / (nt * 50)
            E = 1.0 / (1 - dt * Lk)                        # implicit linear
            rec = np.empty((nt, nx)); rec[0] = u
            uh = np.fft.fft(u)
            for t in range(1, nt):
                for _ in range(50):
                    nl = -0.5 * 1j * k * np.fft.fft(np.real(np.fft.ifft(uh))**2)
                    uh = E * (uh + dt * nl)
                rec[t] = np.real(np.fft.ifft(uh))
            out[s] = rec
        return out
    save("07_kuramoto_sivashinsky_1d",
         "u_t + u u_x + u_xx + u_xxxx = 0, periodic (space×time field)",
         P, ["domain_L", "ic_amplitude", "ic_phase"],
         solve(nx_lf, nt_lf), solve(nx_hf, nt_hf),
         "1D Kuramoto-Sivashinsky spatiotemporal chaos; output is the x-t field.",
         domain="x in [0,L), t in [0,60]")


# =============================================================================
if __name__ == "__main__":
    t0 = time.time()
    gens = [gen_helmholtz, gen_rayleigh_benard, gen_gray_scott, gen_wave,
            gen_eikonal, gen_cahn_hilliard, gen_kuramoto_sivashinsky]
    for g in gens:
        print(f"[{g.__name__}] ...", flush=True)
        ts = time.time()
        try:
            g()
            print(f"    done in {time.time()-ts:.1f}s", flush=True)
        except Exception:
            print(f"    FAILED:\n{traceback.format_exc()}", flush=True)
    with open(os.path.join(OUT, "manifest.json"), "w") as fh:
        json.dump(MANIFEST, fh, indent=2)
    print(f"\nDONE in {time.time()-t0:.1f}s. {len(MANIFEST)} datasets -> {OUT}")
