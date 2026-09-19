"""
Faithful same-equation reimplementations for the benchmark PDEs that can't run
upstream here (PhiFlow incompatible with numpy 2.x; SpeedyWeather needs Julia):

  - PDEBench  Incompressible Navier-Stokes 2D  (PhiFlow upstream)
  - PDEArena  Navier-Stokes smoke 'standard'   (PhiFlow upstream)
  - PDEArena  Navier-Stokes smoke 'conditioned' (PhiFlow upstream, param=buoyancy)
  - PDEArena  Shallow-water 'weather'          (SpeedyWeather.jl upstream)

These are independent numpy solvers of the SAME governing equations (spectral
2D vorticity-streamfunction NS with a buoyancy-coupled scalar; finite-difference
shallow water). They are clearly labeled 'reimpl' in the manifest.
"""
import numpy as np

TWO_PI = 2 * np.pi


# ---- spectral 2D incompressible NS (vorticity) with optional buoyant scalar --
def _ns_setup(n, L=TWO_PI):
    k = np.fft.fftfreq(n, d=L / n) * TWO_PI
    KX, KY = np.meshgrid(k, k, indexing="ij")
    K2 = KX**2 + KY**2
    K2inv = 1.0 / np.where(K2 == 0, 1.0, K2)
    kmax = np.abs(k).max()
    mask = (np.abs(KX) < (2.0 / 3.0) * kmax) & (np.abs(KY) < (2.0 / 3.0) * kmax)
    return KX, KY, K2, K2inv, mask


def _vel(wh, KX, KY, K2inv):
    psih = wh * K2inv
    u = np.real(np.fft.ifft2(1j * KY * psih))
    v = np.real(np.fft.ifft2(-1j * KX * psih))
    return u, v


def incomp_ns_2d(seed, n=64, nu=1.2e-3, T=8.0, nsteps=4000):
    """Decaying 2D turbulence: random vorticity IC -> evolve. Returns vorticity."""
    KX, KY, K2, K2inv, mask = _ns_setup(n)
    rng = np.random.default_rng(seed)
    # smooth random vorticity IC (band-limited)
    w0 = rng.standard_normal((n, n))
    wh = np.fft.fft2(w0) * np.exp(-K2 / (2 * (6.0**2))) * mask
    wh[0, 0] = 0
    dt = T / nsteps
    visc = np.exp(-nu * K2 * dt)

    def rhs(wh):
        u, v = _vel(wh, KX, KY, K2inv)
        w = np.real(np.fft.ifft2(wh))
        wx = np.real(np.fft.ifft2(1j * KX * wh)); wy = np.real(np.fft.ifft2(1j * KY * wh))
        return -np.fft.fft2(u * wx + v * wy) * mask

    for _ in range(nsteps):
        k1 = rhs(wh)
        k2 = rhs(wh + 0.5 * dt * k1)
        k3 = rhs(wh + 0.5 * dt * k2)
        k4 = rhs(wh + dt * k3)
        wh = (wh + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)) * visc
    return np.real(np.fft.ifft2(wh))


def smoke_ns_2d(buoyancy, seed, n=64, nu=1.5e-3, kappa=1.5e-3, T=10.0, nsteps=5000):
    """Buoyancy-driven incompressible NS carrying a smoke scalar.
    omega_t = -(u.grad)omega + nu*lap(omega) + buoyancy * d(smoke)/dx
    smoke_t = -(u.grad)smoke + kappa*lap(smoke).  Returns the smoke field."""
    KX, KY, K2, K2inv, mask = _ns_setup(n)
    rng = np.random.default_rng(seed)
    xs = np.linspace(0, TWO_PI, n, endpoint=False)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    # smoke source: a couple of blobs near the bottom, seeded location
    cx = TWO_PI * (0.4 + 0.2 * rng.random())
    s = np.exp(-((X - cx)**2 + (Y - 0.8)**2) / (2 * 0.45**2))
    sh = np.fft.fft2(s); wh = np.zeros((n, n), complex)
    dt = T / nsteps
    visc_w = np.exp(-nu * K2 * dt); visc_s = np.exp(-kappa * K2 * dt)

    def adv(fh, u, v):
        fx = np.real(np.fft.ifft2(1j * KX * fh)); fy = np.real(np.fft.ifft2(1j * KY * fh))
        return -np.fft.fft2(u * fx + v * fy) * mask

    for _ in range(nsteps):
        u, v = _vel(wh, KX, KY, K2inv)
        Nw = adv(wh, u, v) + buoyancy * (1j * KX * sh) * mask
        Ns = adv(sh, u, v)
        wh = (wh + dt * Nw) * visc_w
        sh = (sh + dt * Ns) * visc_s
    return np.real(np.fft.ifft2(sh))


# ---- finite-difference 2D shallow water ('weather'-like) ---------------------
def shallow_water_2d(seed, n=96, g=1.0, T=1.5, nsteps=3000, f=1.0, theta=0.04):
    """2D shallow-water (h, hu, hv) on a periodic plane with Coriolis f and a
    random smooth height IC (geostrophic-ish). Lax-Friedrichs (dissipative,
    stable) time stepping. Returns the surface-height field h."""
    rng = np.random.default_rng(seed)
    L = 1.0; h0 = 1.0
    xs = np.linspace(0, L, n, endpoint=False); dx = xs[1] - xs[0]
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    h = np.full((n, n), h0)
    for _ in range(6):
        kx, ky = rng.integers(1, 4), rng.integers(1, 4)
        h += 0.06 * rng.uniform(-1, 1) * np.sin(2 * np.pi * (kx * X + ky * Y) + rng.uniform(0, TWO_PI))
    hu = np.zeros((n, n)); hv = np.zeros((n, n))
    dt = T / nsteps

    def dxc(a): return (np.roll(a, -1, 0) - np.roll(a, 1, 0)) / (2 * dx)
    def dyc(a): return (np.roll(a, -1, 1) - np.roll(a, 1, 1)) / (2 * dx)
    def avg(a): return 0.25 * (np.roll(a, 1, 0) + np.roll(a, -1, 0)
                              + np.roll(a, 1, 1) + np.roll(a, -1, 1))
    for _ in range(nsteps):
        u = hu / h; v = hv / h
        h_t = -(dxc(hu) + dyc(hv))
        hu_t = -(dxc(hu * u + 0.5 * g * h**2) + dyc(hu * v)) + f * hv
        hv_t = -(dxc(hv * u) + dyc(hv * v + 0.5 * g * h**2)) - f * hu
        # lightly-blended Lax-Friedrichs: just enough dissipation to stay stable
        h = (1 - theta) * h + theta * avg(h) + dt * h_t
        hu = (1 - theta) * hu + theta * avg(hu) + dt * hu_t
        hv = (1 - theta) * hv + theta * avg(hv) + dt * hv_t
        h = np.clip(h, 0.3, None)
    return h


# --------------------------------------------------------------- driver -------
REIMPL = {
    "PDEBench_incompressible_ns_2d": dict(
        gen=lambda i: incomp_ns_2d(seed=i), param_name="random IC (decaying turb.)",
        param=lambda i: float("nan"), field="vorticity"),
    "PDEArena_ns_smoke_standard": dict(
        gen=lambda i: smoke_ns_2d(0.5, seed=i), param_name="buoyancy_y (fixed 0.5)",
        param=lambda i: 0.5, field="smoke"),
    "PDEArena_ns_smoke_conditioned": dict(
        gen=lambda i: smoke_ns_2d(0.2 + 0.3 * ((i % 3) / 2), seed=i),
        param_name="buoyancy_y in [0.2,0.5]",
        param=lambda i: 0.2 + 0.3 * ((i % 3) / 2), field="smoke"),
    "PDEArena_shallow_water_weather": dict(
        gen=lambda i: shallow_water_2d(seed=i), param_name="random IC (weather)",
        param=lambda i: float("nan"), field="height h"),
}

if __name__ == "__main__":
    import os, json, time
    out = os.path.join(os.path.dirname(__file__), "reimpl_out"); os.makedirs(out, exist_ok=True)
    man = {}
    for name, spec in REIMPL.items():
        t = time.time(); fields = []; params = []
        for i in range(3):
            fields.append(spec["gen"](i)); params.append(spec["param"](i))
        F = np.stack(fields).astype(np.float32)
        np.savez_compressed(os.path.join(out, name + ".npz"), field=F,
                            params=np.array(params, np.float32))
        man[name] = dict(field=spec["field"], param_name=spec["param_name"],
                         shape=list(F.shape), provenance="reimpl (same equations)")
        print(f"{name:34s} {F.shape}  {time.time()-t:.1f}s")
    json.dump(man, open(os.path.join(out, "manifest.json"), "w"), indent=2)
    print("done")
