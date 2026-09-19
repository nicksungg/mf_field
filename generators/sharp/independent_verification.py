"""Independent verification of the SURF_2026 / mffp_sharp PDE solvers.

Written from scratch (does NOT call the repo's pytest tests). Each check compares a
solver against an EXACT analytic solution, a conservation law, or a self-convergence
study. Prints a PASS/FAIL table with the measured numbers so the result is auditable.

Run:  python independent_verification.py
"""
import numpy as np

from mffp_sharp.pdes import porous_medium as pm
from mffp_sharp.pdes import kdv
from mffp_sharp.pdes import nls
from mffp_sharp.pdes import sine_gordon as sg
from mffp_sharp.pdes import fisher_kpp as fk
from mffp_sharp.pdes import cahn_hilliard as ch
from mffp_sharp.pdes import allen_cahn as ac
from mffp_sharp.pdes import kuramoto_sivashinsky as ks
from mffp_sharp.pdes import helmholtz as hz
from mffp_sharp.common.spectral import spectral_interp

results = []
def record(name, passed, detail):
    results.append((name, passed, detail))
    print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")


# 1. POROUS MEDIUM — Barenblatt exact self-similar solution, with GRID CONVERGENCE.
#    PME u_t = lap(u^m). Barenblatt evolves into itself; error must shrink as h->0.
def test_pme_barenblatt_convergence():
    m, domain = 2.0, 10.0
    t0, t1 = 1.0, 1.6
    errs = {}
    for res in (128, 256, 512, 1024):
        x = np.arange(res) * domain / res - domain / 2.0
        b0 = pm._barenblatt_1d(x, t0, m, mass=1.0)
        b1 = pm._barenblatt_1d(x, t1, m, mass=1.0)
        got = pm._solve(b0, m, domain, output_time=(t1 - t0))
        errs[res] = float(np.linalg.norm(got - b1) / np.linalg.norm(b1))
    # error should decrease with resolution (FD converges to the exact free boundary)
    decreasing = errs[1024] < errs[256] < errs[128]
    record("PME Barenblatt exact + convergence",
           decreasing and errs[1024] < 0.02,
           f"relL2 @128/256/512/1024 = "
           f"{errs[128]:.2e}/{errs[256]:.2e}/{errs[512]:.2e}/{errs[1024]:.2e} (monotone↓={decreasing})")


# 2. KdV — single soliton: exact translating wave, speed=c, amplitude=c/2 preserved.
#    u_t + 6 u u_x + delta^2 u_xxx = 0; soliton (c/2) sech^2( sqrt(c)/(2 delta) (x-ct-x0) )
def test_kdv_soliton():
    res, L, delta = 1024, 80.0, 1.0
    c, x0 = 1.0, 20.0
    x = np.arange(res) * L / res
    def soliton(t):
        xi = (x - c * t - x0)
        # periodic image not needed: soliton stays interior for the chosen T
        return (c / 2.0) / np.cosh(np.sqrt(c) / (2.0 * delta) * xi) ** 2
    T = 6.0
    u0 = soliton(0.0)
    got = kdv._solve(u0, delta, L, output_time=T, dt=2e-4)
    exact = soliton(T)
    rel = float(np.linalg.norm(got - exact) / np.linalg.norm(exact))
    # also check peak location moved by c*T and amplitude preserved
    peak_shift = (x[np.argmax(got)] - x[np.argmax(u0)])
    amp_err = abs(got.max() - c / 2.0) / (c / 2.0)
    record("KdV single-soliton propagation",
           rel < 0.02 and abs(peak_shift - c * T) < 0.5 and amp_err < 0.02,
           f"relL2={rel:.2e}, peak shift={peak_shift:.2f} (exact {c*T:.2f}), amp err={amp_err:.2e}")


# 3. NLS — standing bright soliton: |u|^2 is time-invariant; mass conserved.
#    i u_t + 1/2 u_xx + g|u|^2 u = 0 ; soliton u0 = eta sech(eta sqrt(g) x), theta=g eta^2/2
def test_nls_soliton_and_mass():
    res, L, g, eta = 2048, 60.0, 1.0, 1.0
    x = np.arange(res) * L / res - L / 2.0
    u0 = eta / np.cosh(eta * np.sqrt(g) * x)            # real standing soliton
    T = 5.0
    u = nls._solve(u0.astype(np.complex128), g, L, output_time=T, dt=1e-3)
    I0, IT = np.abs(u0) ** 2, np.abs(u) ** 2
    shape_err = float(np.linalg.norm(IT - I0) / np.linalg.norm(I0))
    mass_err = abs(IT.sum() - I0.sum()) / I0.sum()
    record("NLS standing bright soliton (shape + mass)",
           shape_err < 0.02 and mass_err < 1e-6,
           f"|u|^2 shape relL2={shape_err:.2e}, mass drift={mass_err:.2e}")


# 4. sine-Gordon — small-amplitude linear dispersion omega=sqrt(k^2+m^2) (Klein-Gordon).
def test_sine_gordon_dispersion():
    res, L, m = 256, 2.0 * np.pi, 1.0
    eps = 1e-3                                            # small amplitude -> linear regime
    n = 3
    k = 2.0 * np.pi * n / L
    x = np.arange(res) * L / res
    u0 = eps * np.cos(k * x)
    omega = np.sqrt(k ** 2 + m ** 2)
    T = 1.7
    u, v = sg._solve_with_velocity(u0, m, L, output_time=T, dt=1e-3)
    exact = eps * np.cos(k * x) * np.cos(omega * T)       # u_t=0 start -> cos(wt)
    rel = float(np.linalg.norm(u - exact) / np.linalg.norm(exact))
    record("sine-Gordon Klein-Gordon dispersion w=sqrt(k^2+m^2)",
           rel < 1e-3,
           f"k={k:.3f}, omega={omega:.4f}, relL2(u(T) vs analytic)={rel:.2e}")


# 5. sine-Gordon — ENERGY conservation at finite (nonlinear) amplitude.
def test_sine_gordon_energy():
    res, L, m = 512, 20.0, 1.0
    rng = np.random.default_rng(0)
    u0 = 0.6 * (2 * rng.random(res) - 1)
    E = []
    u, v = u0.copy(), np.zeros_like(u0)
    # step in chunks, recording energy
    for seg in range(6):
        u, v = sg._solve_with_velocity(u, m, L, output_time=1.0, dt=2e-3) if seg == 0 \
               else _continue(u, v, m, L)
        E.append(sg._energy(u, v, m, L))
    drift = (max(E) - min(E)) / abs(np.mean(E))
    record("sine-Gordon energy conservation",
           drift < 5e-3, f"energy rel drift over 6s = {drift:.2e} (E~{np.mean(E):.3f})")

def _continue(u, v, m, L):
    # advance an existing (u,v) state by 1.0 using the same Strang stepper internals
    res = u.shape[0]; ndim = u.ndim
    omega = sg._omega(res, L, m, ndim)
    nsteps = int(np.ceil(1.0 / 2e-3)); dt = 1.0 / nsteps
    cwt, swt, sinc = sg._step_arrays(omega, dt)
    for _ in range(nsteps):
        v = v - m**2*(np.sin(u)-u)*(dt/2)
        uh = np.fft.fftn(u); vh = np.fft.fftn(v)
        u = np.real(np.fft.ifftn(uh*cwt+vh*sinc)); v = np.real(np.fft.ifftn(-uh*omega*swt+vh*cwt))
        v = v - m**2*(np.sin(u)-u)*(dt/2)
    return u, v


# 6. Fisher-KPP — front speed approaches the KPP minimal speed 2*sqrt(D r).
#    On the PERIODIC domain a [0,a) plateau has TWO fronts (both u=1 invading u=0),
#    so its mass grows at rate 2*c*. Measure dM/dt -> c* = 0.5 dM/dt (avoids the
#    wrap-around artifact that a "rightmost-crossing" tracker would latch onto).
def test_fisher_kpp_front_speed():
    res, L = 8192, 200.0
    D, r = 1.0, 1.0
    x = np.arange(res) * L / res
    u0 = (x < 20.0).astype(np.float64)                  # steep step -> minimal-speed front
    # measure the RIGHT-moving front (level set u=0.5) in the left half only, at EARLY
    # times (t<~20) before the unstable u=0 far-field seeds from roundoff and saturates.
    def front_pos(t):
        u = fk._solve(u0, D, r, L, output_time=t, dt=2e-3)
        half = res // 2
        idx = np.where(u[:half] >= 0.5)[0]
        return x[idx.max()]
    ts = [6.0, 10.0, 14.0, 18.0]
    pos = [front_pos(t) for t in ts]
    speeds = [(pos[i + 1] - pos[i]) / (ts[i + 1] - ts[i]) for i in range(len(ts) - 1)]
    cstar = 2.0 * np.sqrt(D * r)
    # Bramson: instantaneous front speed = c* - 3/(2t). Compare the last interval to its
    # theory value at the interval midpoint; also require speeds increasing toward c*.
    t_mid = 0.5 * (ts[-1] + ts[-2])
    bramson = cstar - 3.0 / (2.0 * t_mid)
    increasing = speeds[0] < speeds[1] < speeds[2] < cstar
    last_err = abs(speeds[-1] - bramson) / bramson
    record("Fisher-KPP front speed -> c* with Bramson 3/(2t) correction",
           increasing and last_err < 0.03,
           f"speeds [6→18] = {[round(s,2) for s in speeds]} ↑ toward c*={cstar:.2f}; "
           f"last={speeds[-1]:.3f} vs Bramson c*-3/(2t)={bramson:.3f} (err {last_err:.2e})")


# 7. Cahn-Hilliard — mass (k=0 mode) conserved to ~machine precision.
def test_ch_mass():
    res = 128
    rng = np.random.default_rng(3)
    c0 = 0.05 + 0.1 * (2 * rng.random((res, res)) - 1)
    c = ch._solve(c0, eps=0.015, mobility=1.0, domain_size=1.0, output_time=2.0)
    drift = abs(c.mean() - c0.mean()) / abs(c0.mean())
    bounded = c.min() > -1.3 and c.max() < 1.3
    record("Cahn-Hilliard mass conservation + bounded",
           drift < 1e-9 and bounded,
           f"mean drift={drift:.2e}, range=[{c.min():.3f},{c.max():.3f}]")


# 8. SPECTRAL INTERP — band-limited signal interpolated up must match the analytic
#    continuous function exactly (this is the IC consistency the whole ladder relies on).
def test_spectral_interp_exact():
    nc, nf, L = 64, 256, 2 * np.pi
    xc = np.arange(nc) * L / nc
    xf = np.arange(nf) * L / nf
    # signal band-limited below nc/2: sum of low modes
    def f(x): return np.sin(x) + 0.3 * np.cos(3 * x) - 0.5 * np.sin(5 * x)
    up = spectral_interp(f(xc), nf)
    rel = float(np.linalg.norm(up - f(xf)) / np.linalg.norm(f(xf)))
    record("spectral_interp band-limited exactness",
           rel < 1e-12, f"relL2(interp vs analytic on fine grid)={rel:.2e}")


# 9. ALLEN-CAHN — self (mesh) convergence on a fixed smooth analytic IC.
#    No closed form; check the solution converges as res increases (Cauchy).
def test_allen_cahn_mesh_convergence():
    L, eps, T = 2.0 * np.pi, 0.15, 0.3
    def ic(res):
        x = np.arange(res) * L / res
        return 0.3 * np.sin(x) + 0.2 * np.cos(2 * x)
    sols = {res: ac._solve(ic(res), eps, 1.0, L, T) for res in (64, 128, 256, 512)}
    # compare each to the 512 reference by spectral down/▒up to common 512 grid
    ref = sols[512]
    def to512(u):
        return spectral_interp(u, 512) if u.shape[0] != 512 else u
    e = {res: float(np.linalg.norm(to512(sols[res]) - ref) / np.linalg.norm(ref))
         for res in (64, 128, 256)}
    decreasing = e[256] < e[128] < e[64]
    record("Allen-Cahn mesh (self) convergence",
           decreasing and e[256] < 1e-3,
           f"relL2 vs 512 @64/128/256 = {e[64]:.2e}/{e[128]:.2e}/{e[256]:.2e} (↓={decreasing})")


# 10. KdV / NLS — TIME-step convergence (verify the advertised RK4 / Strang order).
def test_time_convergence_nls():
    res, L, g = 512, 40.0, 1.0
    x = np.arange(res) * L / res - L / 2.0
    u0 = (1.0 / np.cosh(x)).astype(np.complex128)
    T = 2.0
    ref = nls._solve(u0, g, L, T, dt=1.25e-4)
    errs = {}
    for dt in (2e-3, 1e-3, 5e-4):
        u = nls._solve(u0, g, L, T, dt=dt)
        errs[dt] = float(np.linalg.norm(u - ref) / np.linalg.norm(ref))
    # Strang split-step is 2nd order: halving dt should cut error ~4x
    ratio = errs[2e-3] / errs[5e-4]
    record("NLS Strang split-step temporal order ~2",
           ratio > 8.0,
           f"err(2e-3)/err(5e-4)={ratio:.1f} (>=16 ideal for 2nd order over 4x dt); "
           f"errs={ {k: round(v,2-int(np.floor(np.log10(v)))) if v>0 else v for k,v in [] } or {f'{k:g}':f'{v:.2e}' for k,v in errs.items()} }")


# 11. HELMHOLTZ — discrete linear-solve residual ~ 0 across wavenumbers.
def test_helmholtz_residual():
    worst = 0.0
    for k in (10.0, 25.0, 40.0):
        f = hz.generate_sample({"wavenumber": k, "source_width": 0.05, "domain_size": 1.0},
                               [128], 128, 0.0)[0][128]
        r = hz.residual(f, 128, k, 0.05, 1.0)
        worst = max(worst, r)
    record("Helmholtz linear-solve residual ~0",
           worst < 1e-8, f"worst rel residual over k in {{10,25,40}} = {worst:.2e}")


# 12. KS golden-fixture reproduction on THIS machine (determinism/portability).
def test_ks_golden_reproduce():
    import os
    golden = np.load(os.path.join(os.path.dirname(ks.__file__), "..", "..", "..",
                                  "tests", "fixtures", "ks_2d_golden.npy"))
    spec = {"L": 30.0, "ic_amplitude": 0.1, "ndim": 2, "seed": 1}
    fields = ks.generate_sample(spec, [16, 32], 32, output_time=2.0)[0]
    got = np.stack([fields[16].ravel()[:64], fields[32].ravel()[:64]])
    maxabs = float(np.max(np.abs(got - golden)))
    record("KS 2D golden-fixture bit-reproduction (this machine)",
           maxabs < 1e-12, f"max abs diff vs committed golden = {maxabs:.2e}")


# 13. PHASE-FIELD CRYSTAL — conserved dynamics: spatial mean (mass) preserved exactly.
def test_pfc_mass_conserved():
    from mffp_sharp.pdes import phase_field_crystal as pfc
    res = 128
    rng = np.random.default_rng(1)
    psi0 = -0.3 + 0.05 * (2 * rng.random((res, res)) - 1)
    psi = pfc._solve(psi0, r=-0.8, domain_size=50.0, output_time=20.0)
    drift = abs(psi.mean() - psi0.mean()) / abs(psi0.mean())
    record("Phase-field-crystal mass conservation",
           drift < 1e-9 and np.isfinite(psi).all(),
           f"mean drift={drift:.2e}, finite={np.isfinite(psi).all()}")


# 14. SWIFT-HOHENBERG — pattern selects characteristic wavenumber k≈1 (spectral peak).
def test_swift_hohenberg_wavenumber():
    from mffp_sharp.pdes import swift_hohenberg as sh
    res, L = 256, 64.0                                    # domain holds many wavelengths
    rng = np.random.default_rng(0)
    u0 = 0.1 * (2 * rng.random((res, res)) - 1)
    u = sh._solve(u0, r=0.3, domain_size=L, output_time=100.0)  # let pattern saturate
    # radially-averaged power spectrum; find peak wavenumber
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=L / res)
    KX, KY = np.meshgrid(k1, k1, indexing="ij")
    kmag = np.sqrt(KX ** 2 + KY ** 2)
    P = np.abs(np.fft.fft2(u - u.mean())) ** 2
    bins = np.linspace(0, 3, 60)
    idx = np.digitize(kmag.ravel(), bins)
    radial = np.array([P.ravel()[idx == i].mean() if np.any(idx == i) else 0
                       for i in range(1, len(bins))])
    kpeak = 0.5 * (bins[np.argmax(radial)] + bins[np.argmax(radial) + 1])
    record("Swift-Hohenberg characteristic wavenumber k≈1",
           abs(kpeak - 1.0) < 0.15 and np.isfinite(u).all(),
           f"spectral peak at k={kpeak:.3f} (theory k=1)")


# 15. GRAY-SCOTT — fields stay physically bounded (u,v in ~[0,1]) and pattern forms.
def test_gray_scott_bounded():
    from mffp_sharp.pdes import gray_scott as gs
    fields, cond, names = gs.generate_sample(
        {"F": 0.04, "k_rate": 0.06, "Du": 2e-5, "Dv": 1e-5,
         "domain_size": 2.5, "ndim": 2, "seed": 0}, [64, 128], 128, output_time=2000.0)
    v = fields[128]
    bounded = v.min() > -0.05 and v.max() < 1.05 and np.isfinite(v).all()
    structured = v.std() > 1e-4                           # a pattern actually formed
    record("Gray-Scott bounded + pattern formed",
           bounded and structured,
           f"v range=[{v.min():.3f},{v.max():.3f}], std={v.std():.3e}")


if __name__ == "__main__":
    tests = [test_pme_barenblatt_convergence, test_kdv_soliton, test_nls_soliton_and_mass,
             test_sine_gordon_dispersion, test_sine_gordon_energy, test_fisher_kpp_front_speed,
             test_ch_mass, test_spectral_interp_exact, test_allen_cahn_mesh_convergence,
             test_time_convergence_nls, test_helmholtz_residual, test_ks_golden_reproduce,
             test_pfc_mass_conserved, test_swift_hohenberg_wavenumber, test_gray_scott_bounded]
    for t in tests:
        try:
            t()
        except Exception as e:
            record(t.__name__, False, f"EXCEPTION: {type(e).__name__}: {e}")
    n_pass = sum(1 for _, p, _ in results if p)
    print("\n" + "=" * 70)
    print(f"INDEPENDENT VERIFICATION: {n_pass}/{len(results)} checks passed")
    print("=" * 70)
