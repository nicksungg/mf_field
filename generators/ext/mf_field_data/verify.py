"""
Verification suite for the PDE solvers.

Checks (printed table + figures/verification/*.png + VERIFICATION.md):
  Helmholtz : Method of Manufactured Solutions -> spatial convergence order
  Wave      : exact standing-wave solution     -> space-time convergence order
  Eikonal   : exact distance (uniform speed)   -> order;  + Fast-Marching cross-check
  Cahn-Hill.: mass conservation + free-energy monotone decay + ETDRK4 cross-check
  KS        : ETDRK4 cross-check (short-time accurate, long-time chaotic decorrelation)
  Gray-Scott: independent py-pde cross-check
  Rayleigh-Benard: convective onset near Ra_c≈1708 + Nusselt trend + grid self-convergence

Run: python3 verify.py
"""
import os, warnings, json
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

import solvers as S

ROOT = "/archive/workspace/mf_field_data"
FIG = os.path.join(ROOT, "figures", "verification")
os.makedirs(FIG, exist_ok=True)
REPORT = []


def relL2(a, b):
    return np.linalg.norm(a - b) / np.linalg.norm(b)


def fit_order(hs, errs):
    hs, errs = np.array(hs, float), np.array(errs, float)
    return np.polyfit(np.log(hs), np.log(errs), 1)[0]


# ---------------------------------------------------------------- Helmholtz MMS
def verify_helmholtz():
    k = 8.0
    grids = [16, 32, 64, 128]
    errs = []
    for n in grids:
        X, Y = S.grid_xy(n)
        ue = np.sin(2 * np.pi * X) * np.sin(3 * np.pi * Y)        # Dirichlet 0
        f = (k**2 - (4 + 9) * np.pi**2) * ue                      # (Δ+k²)ue
        A = (-S.assemble_elliptic(n, np.ones((n, n))) + k**2 * sp.identity(n * n)).tocsc()
        u = spla.spsolve(A, f.ravel()).reshape(n, n)
        errs.append(relL2(u, ue))
    p = fit_order([1.0 / (n + 1) for n in grids], errs)
    REPORT.append(("helmholtz_2d", "MMS sin(2πx)sin(3πy)", f"order≈{p:.2f}",
                   f"errs={[f'{e:.1e}' for e in errs]}", "PASS" if p > 1.8 else "CHECK"))
    return grids, errs, p


# --------------------------------------------------------------------- Wave MMS
def verify_wave():
    c = 1.0
    t_end = 0.3
    grids = [17, 33, 65, 129]
    errs, hs = [], []
    for n in grids:
        h = 1.0 / (n - 1)
        xs = np.linspace(0, 1, n)
        X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
        w = c * np.pi * np.sqrt(2)
        u0 = np.sin(np.pi * X) * np.sin(np.pi * Y)
        ue = u0 * np.cos(w * t_end)
        dt = 0.35 * h / c
        lam = (c * dt / h)**2
        def L(a):
            o = np.zeros_like(a)
            o[1:-1, 1:-1] = (a[1:-1, 2:] + a[1:-1, :-2] + a[2:, 1:-1]
                             + a[:-2, 1:-1] - 4 * a[1:-1, 1:-1])
            return o
        cur = u0 + 0.5 * lam * L(u0); cur[0,:]=cur[-1,:]=cur[:,0]=cur[:,-1]=0; up = u0
        nsteps = int(round(t_end / dt))
        for _ in range(nsteps - 1):
            nxt = 2 * cur - up + lam * L(cur)
            nxt[0,:]=nxt[-1,:]=nxt[:,0]=nxt[:,-1]=0
            up, cur = cur, nxt
        # account for the fixed final time vs integer steps
        errs.append(relL2(cur, u0 * np.cos(w * (nsteps * dt)))); hs.append(h)
    p = fit_order(hs, errs)
    REPORT.append(("wave_2d", "exact standing wave", f"order≈{p:.2f}",
                   f"errs={[f'{e:.1e}' for e in errs]}", "PASS" if p > 1.7 else "CHECK"))
    return hs, errs, p


# ------------------------------------------------------------------ Eikonal
def verify_eikonal():
    # (a) uniform speed -> exact Euclidean distance; (b) FMM cross-check
    grids = [33, 65, 129]
    errs, hs = [], []
    sx, sy = 0.5, 0.5
    for n in grids:
        T = S.solve_eikonal(np.array([[sx, sy, 0.0]]), n)[0]   # lsp=0 -> speed 1
        xs = np.linspace(0, 1, n)
        X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
        Te = np.sqrt((X - sx)**2 + (Y - sy)**2)
        m = Te > 0.1                                            # exclude near-source
        errs.append(np.linalg.norm((T - Te)[m]) / np.linalg.norm(Te[m]))
        hs.append(1.0 / (n - 1))
    p = fit_order(hs, errs)
    # cross-check vs Fast Marching on random inclusion cases
    P = S.sample_params("eikonal_2d", 8, seed=3)
    mine = S.solve_eikonal(P, 96); ref = S.solve_eikonal_ref(P, 96)
    xs = np.linspace(0, 1, 96)
    X = np.broadcast_to(xs, (96, 96)); Y = np.broadcast_to(xs[:, None], (96, 96))
    rels = []
    for i, (px, py, _) in enumerate(P):
        m = np.sqrt((X - px)**2 + (Y - py)**2) > 0.08
        rels.append(np.linalg.norm((mine[i] - ref[i])[m]) / np.linalg.norm(ref[i][m]))
    REPORT.append(("eikonal_2d", "exact distance + FMM cross-check",
                   f"order≈{p:.2f}", f"vs FMM rel-L2={np.mean(rels):.2%}",
                   "PASS" if (p > 0.8 and np.mean(rels) < 0.05) else "CHECK"))
    return hs, errs, p, np.mean(rels)


# --------------------------------------------------------------- Cahn-Hilliard
def verify_cahn_hilliard():
    n = 64
    P = S.sample_params("cahn_hilliard_2d", 1, seed=2)
    lg, mean = P[0]; gamma = 10**lg
    kx = np.fft.fftfreq(n, d=1.0 / n); KX, KY = np.meshgrid(kx, kx)
    k2 = KX**2 + KY**2
    c = S.ch_ic(n, 0, mean); m0 = c.mean()
    energies, masses = [], []
    dt = 1e-5
    def energy(c):
        cx = np.real(np.fft.ifft2(1j * KX * np.fft.fft2(c)))
        cy = np.real(np.fft.ifft2(1j * KY * np.fft.fft2(c)))
        return np.sum(0.25 * (c**2 - 1)**2 + 0.5 * gamma * (cx**2 + cy**2))
    for it in range(4000):
        if it % 200 == 0:
            energies.append(energy(c)); masses.append(c.mean())
        ch = np.fft.fft2(c**3 - c); chat = np.fft.fft2(c)
        chat = (chat - dt * k2 * ch) / (1 + dt * gamma * k2**2)
        c = np.real(np.fft.ifft2(chat))
    mass_drift = abs(c.mean() - m0)
    monotone = np.all(np.diff(energies) <= 1e-9 * abs(energies[0]))
    # cross-check vs ETDRK4 reference at same params/grid/time
    mine = S.solve_cahn_hilliard(P, n)[0]
    ref = S.solve_cahn_hilliard_ref(P, n)[0]
    rel = relL2(mine, ref)
    REPORT.append(("cahn_hilliard_2d", "mass+energy invariants + ETDRK4 xcheck",
                   f"mass drift={mass_drift:.1e}, energy↓={monotone}",
                   f"vs ETDRK4 rel-L2={rel:.2%}",
                   "PASS" if (mass_drift < 1e-6 and monotone and rel < 0.10) else "CHECK"))
    return energies, masses, rel


# --------------------------------------------------------------------- KS
def verify_ks():
    nx, nt = 256, 120
    P = S.sample_params("kuramoto_sivashinsky_1d", 1, seed=1)
    mine = S.solve_kuramoto_sivashinsky(P, (nx, nt))[0]
    ref = S.solve_kuramoto_sivashinsky_ref(P, (nx, nt))[0]
    t = np.linspace(0, 60, nt)
    early = relL2(mine[t <= 10], ref[t <= 10])
    late = relL2(mine[t >= 40], ref[t >= 40])
    REPORT.append(("kuramoto_sivashinsky_1d", "ETDRK4 cross-check",
                   f"t≤10 rel-L2={early:.2%}", f"t≥40 rel-L2={late:.1%} (chaotic)",
                   "PASS" if early < 0.05 else "CHECK"))
    return mine, ref, t, early, late


# --------------------------------------------------------------- Gray-Scott
def verify_gray_scott():
    n = 48
    P = S.sample_params("gray_scott_2d", 3, seed=0)
    mine = S.solve_gray_scott(P, n, steps=2000)
    ref = S.solve_gray_scott_ref(P, n, t_end=2000.0)
    rels = [relL2(mine[i], ref[i]) for i in range(len(P))]
    REPORT.append(("gray_scott_2d", "independent py-pde cross-check",
                   f"rel-L2 mean={np.mean(rels):.2%}", f"max={np.max(rels):.2%}",
                   "PASS" if np.mean(rels) < 0.10 else "CHECK"))
    return np.mean(rels)


# --------------------------------------------------------- Rayleigh-Benard
def rb_run(Ra, n, t_end=0.06):
    h = 1.0 / (n - 1); m = n - 2
    lu = spla.splu(S.assemble_elliptic(m, np.ones((m, m))).tocsc())
    xs = np.linspace(0, 1, n)
    X = np.broadcast_to(xs, (n, n)); Y = np.broadcast_to(xs[:, None], (n, n))
    T = (1 - Y) + 0.05 * np.sin(2 * np.pi * X) * np.sin(np.pi * Y)
    T[0,:]=1; T[-1,:]=0; w = np.zeros((n, n)); Pr = 1.0
    dt = 0.15 * h**2 / Pr
    u = v = None
    for _ in range(int(t_end / dt)):
        psi = np.zeros((n, n)); psi[1:-1,1:-1] = lu.solve(w[1:-1,1:-1].ravel()).reshape(m, m)
        u = np.zeros((n,n)); v = np.zeros((n,n))
        u[1:-1,1:-1] = (psi[2:,1:-1]-psi[:-2,1:-1])/(2*h)
        v[1:-1,1:-1] = -(psi[1:-1,2:]-psi[1:-1,:-2])/(2*h)
        ddx=lambda a:(a[1:-1,2:]-a[1:-1,:-2])/(2*h); ddy=lambda a:(a[2:,1:-1]-a[:-2,1:-1])/(2*h)
        lap=lambda a:(a[1:-1,2:]+a[1:-1,:-2]+a[2:,1:-1]+a[:-2,1:-1]-4*a[1:-1,1:-1])/h**2
        ui,vi=u[1:-1,1:-1],v[1:-1,1:-1]; wn=w.copy()
        wn[1:-1,1:-1]=w[1:-1,1:-1]+dt*(-ui*ddx(w)-vi*ddy(w)+Pr*lap(w)+Ra*Pr*ddx(T))
        Tn=T.copy(); Tn[1:-1,1:-1]=T[1:-1,1:-1]+dt*(-ui*ddx(T)-vi*ddy(T)+lap(T))
        Tn[0,:]=1;Tn[-1,:]=0;Tn[:,0]=Tn[:,1];Tn[:,-1]=Tn[:,-2]
        wn[0,:]=-2*psi[1,:]/h**2;wn[-1,:]=-2*psi[-2,:]/h**2
        wn[:,0]=-2*psi[:,1]/h**2;wn[:,-1]=-2*psi[:,-2]/h**2
        w,T=wn,Tn
        if not np.isfinite(w).all(): break
    KE = float(np.sum(u**2 + v**2)) * h * h
    Nu = float(np.mean(-(T[1, :] - T[0, :]) / h))     # wall heat flux / conduction
    return T, KE, Nu


def verify_rb():
    Ras = [500, 1000, 1500, 1708, 2500, 5000, 1e4, 2e4]
    KEs, Nus = [], []
    for Ra in Ras:
        _, ke, nu = rb_run(Ra, 48)
        KEs.append(ke); Nus.append(nu)
    onset = next((Ra for Ra, nu in zip(Ras, Nus) if nu > 1.05), None)  # Nu-based
    # grid self-convergence at fixed Ra (Richardson)
    Ra = 1e4
    Ts = {n: rb_run(Ra, n)[0] for n in [33, 49, 65]}
    from scipy.ndimage import zoom
    def to(a, n): return zoom(a, (n / a.shape[0], n / a.shape[1]), order=1)
    e1 = relL2(to(Ts[33], 65), Ts[65]); e2 = relL2(to(Ts[49], 65), Ts[65])
    REPORT.append(("rayleigh_benard_2d", "Nusselt onset + self-convergence",
                   f"Nu onset Ra≈{onset} (theory 1708)",
                   f"Nu: {Nus[0]:.2f}(Ra500)→{Nus[-1]:.2f}(Ra2e4); refine {e1:.1%}→{e2:.1%}",
                   "PASS" if (onset and 1000 <= onset <= 3000 and e2 < e1) else "CHECK"))
    return Ras, KEs, Nus


# =============================================================== run + figures
if __name__ == "__main__":
    print("Running verification ...\n")
    hg, he, hp = verify_helmholtz()
    wg, we, wp = verify_wave()
    eg, ee, ep, efmm = verify_eikonal()
    ch_E, ch_m, ch_rel = verify_cahn_hilliard()
    ks_mine, ks_ref, ks_t, ks_e, ks_l = verify_ks()
    gs_rel = verify_gray_scott()
    ras, kes, nus = verify_rb()

    # ---- figures
    fig, ax = plt.subplots(1, 3, figsize=(13, 4))
    for g, e, lbl, hs in [("helmholtz", he, f"Helmholtz p={hp:.2f}", [1/(n+1) for n in hg]),
                          ("wave", we, f"Wave p={wp:.2f}", wg),
                          ("eikonal", ee, f"Eikonal p={ep:.2f}", eg)]:
        ax[0].loglog(hs, e, "o-", label=lbl)
    ax[0].set_xlabel("h"); ax[0].set_ylabel("rel L2 error"); ax[0].legend()
    ax[0].set_title("Convergence (analytical references)"); ax[0].grid(True, which="both", alpha=.3)
    ax[1].semilogy(np.arange(len(ch_E)) * 200, ch_E, "o-")
    ax[1].set_xlabel("CH step"); ax[1].set_ylabel("free energy")
    ax[1].set_title(f"Cahn-Hilliard energy decay\n(mass conserved; vs ETDRK4 {ch_rel:.1%})")
    ax[1].grid(True, alpha=.3)
    ax2 = ax[2]; ax2.semilogx(ras, kes, "o-", color="C3")
    ax2.set_xlabel("Rayleigh number"); ax2.set_ylabel("kinetic energy", color="C3")
    ax2.axvline(1708, ls="--", color="k", alpha=.6)
    ax2b = ax2.twinx(); ax2b.semilogx(ras, nus, "s-", color="C0")
    ax2b.set_ylabel("Nusselt", color="C0")
    ax2.set_title("Rayleigh-Benard onset (Ra_c≈1708)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "summary.png"), dpi=110); plt.close(fig)

    fig, ax = plt.subplots(1, 3, figsize=(12, 4))
    ax[0].imshow(ks_mine, aspect="auto", origin="lower"); ax[0].set_title("KS: in-house")
    ax[1].imshow(ks_ref, aspect="auto", origin="lower"); ax[1].set_title("KS: ETDRK4 ref")
    ax[2].plot(ks_t, [relL2(ks_mine[i], ks_ref[i]) for i in range(len(ks_t))])
    ax[2].set_xlabel("t"); ax[2].set_ylabel("rel L2"); ax[2].set_title("KS error growth (chaos)")
    ax[2].grid(True, alpha=.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "ks.png"), dpi=110); plt.close(fig)

    # ---- report
    print(f"{'dataset':26s} {'check':40s} {'metric':40s} {'detail':34s} verdict")
    print("-" * 150)
    md = ["# Solver verification report\n",
          "Generated by `verify.py`. Two kinds of evidence:\n",
          "1. **Analytical / convergence** — exact solutions (Helmholtz MMS, wave standing "
          "wave, eikonal distance) give measured convergence orders.\n",
          "2. **Reference cross-checks** — independent solvers (scikit-fmm Fast Marching, "
          "ETDRK4 spectral, py-pde) and physical invariants (CH mass/energy, RB onset).\n",
          "![summary](figures/verification/summary.png)\n",
          "![ks](figures/verification/ks.png)\n",
          "| dataset | check | metric | detail | verdict |",
          "|---|---|---|---|---|"]
    for r in REPORT:
        print(f"{r[0]:26s} {r[1]:40s} {r[2]:40s} {r[3]:34s} {r[4]}")
        md.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | **{r[4]}** |")
    open(os.path.join(ROOT, "VERIFICATION.md"), "w").write("\n".join(md))
    print("\nwrote VERIFICATION.md + figures/verification/")
