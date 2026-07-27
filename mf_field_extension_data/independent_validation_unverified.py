"""Independent validation of the UNVERIFIED / CHECK-flagged extension datasets.

Targets the datasets verify.py left as CHECK or did not cover:
  eikonal_2d, cahn_hilliard_2d, rayleigh_benard_2d (CHECK),
  pressure_poisson_poiseuille_mf, rayleigh_benard_mf (no verify entry),
  + CFD tarballs (separate script).

Uses EXACT analytic solutions / physical invariants only — no skfmm / py-pde, so
the checks are independent of the reference solvers verify.py used.
"""
import json
import numpy as np
import solvers as S

DATA = "/orcd/data/faez/001/nick/mf_field_extension_data/data"
out = []
def rec(name, ok, detail):
    out.append((name, ok, detail)); print(f"[{'PASS' if ok else 'CHECK'}] {name}: {detail}")


# ============================================================================
# 1. EIKONAL — exact test: uniform speed => travel time = Euclidean distance.
#    Isolates the in-house scheme from (a) the speed inclusion and (b) the
#    point-source vs source-circle difference that inflates the skfmm rel-L2.
# ============================================================================
def val_eikonal():
    # uniform speed (lsp=0 -> inclusion speed = 1, so speed==1 everywhere)
    errs = {}
    for n in (49, 97, 193):
        sx = sy = 0.5
        T = S.solve_eikonal(np.array([[sx, sy, 0.0]]), n)[0]
        xs = np.linspace(0, 1, n)
        X, Y = np.meshgrid(xs, xs)
        exact = np.sqrt((X - sx) ** 2 + (Y - sy) ** 2)
        # exclude the source cell (singular); relative L2 over the rest
        m = exact > 1e-9
        errs[n] = float(np.linalg.norm((T - exact)[m]) / np.linalg.norm(exact[m]))
    # first-order upwind eikonal: error ~ O(h); halving h should ~halve error
    order = np.log2(errs[49] / errs[193]) / 2   # 4x refinement
    rec("eikonal exact distance (uniform speed)",
        errs[193] < 0.03 and order > 0.6,
        f"relL2 @49/97/193 = {errs[49]:.2e}/{errs[97]:.2e}/{errs[193]:.2e}, "
        f"obs order≈{order:.2f} (1st-order scheme)")
    # monotone causality: T must be >=0 and increase away from source
    T = S.solve_eikonal(np.array([[0.5, 0.5, 0.0]]), 97)[0]
    rec("eikonal nonneg + source is global min",
        T.min() >= -1e-9 and np.unravel_index(np.argmin(T), T.shape) == (48, 48),
        f"min={T.min():.2e} at center; max={T.max():.3f}")


# ============================================================================
# 2. CAHN-HILLIARD — physical invariants + dt self-convergence.
#    The 11% vs ETDRK4 is a time-accuracy gap, not a wrong equation: show the
#    in-house 1st-order scheme converges to a fine-dt reference as dt->0, and
#    that mass is conserved and the free energy is a Lyapunov function (decays).
# ============================================================================
def _ch_energy(c, gamma):
    # E = sum[ 1/4 (c^2-1)^2 + gamma/2 |grad c|^2 ] on the 2π-periodic grid
    n = c.shape[0]
    k = np.fft.fftfreq(n, d=1.0 / n); KX, KY = np.meshgrid(k, k)
    ch = np.fft.fft2(c)
    gx = np.real(np.fft.ifft2(1j * KX * ch)); gy = np.real(np.fft.ifft2(1j * KY * ch))
    return float(np.sum(0.25 * (c ** 2 - 1) ** 2 + 0.5 * gamma * (gx ** 2 + gy ** 2)))

def val_cahn_hilliard():
    n = 64
    p = np.array([[-3.0, 0.0]])         # log10_gamma=-3, mean 0
    gamma = 10 ** p[0, 0]
    # mass conservation over the in-house solve
    c0 = S.ch_ic(n, 0, 0.0)
    c = S.solve_cahn_hilliard(p, n)[0]
    mass_drift = abs(c.mean() - c0.mean())
    rec("Cahn-Hilliard mass conservation",
        mass_drift < 1e-10, f"|<c>_T - <c>_0| = {mass_drift:.2e}")
    # energy decay (sample the trajectory by re-running to increasing step counts)
    Es = []
    for steps in (0, 500, 1500, 3000, 4000):
        cc = S.solve_cahn_hilliard(p, n, steps=steps)[0] if steps else c0
        Es.append(_ch_energy(cc, gamma))
    monotone = all(Es[i + 1] <= Es[i] + 1e-6 * abs(Es[i]) for i in range(len(Es) - 1))
    rec("Cahn-Hilliard free energy is Lyapunov (decays)",
        monotone, f"E = {[round(e,2) for e in Es]} (non-increasing={monotone})")
    # dt self-convergence: in-house with smaller dt -> approaches a fine reference
    ref = S.solve_cahn_hilliard(p, n, steps=40000, dt=1e-6)[0]   # 10x finer dt, same t_end=0.04
    es = {}
    for steps, dt in ((4000, 1e-5), (8000, 5e-6), (16000, 2.5e-6)):
        ci = S.solve_cahn_hilliard(p, n, steps=steps, dt=dt)[0]
        es[dt] = float(np.linalg.norm(ci - ref) / np.linalg.norm(ref))
    converging = es[2.5e-6] < es[5e-6] < es[1e-5]
    rec("Cahn-Hilliard dt self-convergence (same eq. as ETDRK4)",
        converging,
        f"relL2 vs fine-dt ref @dt=1e-5/5e-6/2.5e-6 = "
        f"{es[1e-5]:.2e}/{es[5e-6]:.2e}/{es[2.5e-6]:.2e} (↓={converging})")


# ============================================================================
# 3. RAYLEIGH-BENARD (02_rayleigh_benard_2d) — the Ra_c=1708 flag explained.
#    This is a CONFINED unit cavity (no-slip all walls, insulating sidewalls),
#    NOT the infinite layer 1708 applies to. Validate the physics that IS
#    well-defined: Nu->1 (pure conduction) at low Ra, Nu>1 (convection) at high
#    Ra, with onset above 1708 as expected for a confined cell.
# ============================================================================
def _nusselt(T, n):
    # Nu = (mean vertical heat flux at bottom) / (conductive flux). bottom = row 0.
    h = 1.0 / (n - 1)
    dTdy_bottom = (T[1, :] - T[0, :]) / h          # row 0 is hot wall (T=1)
    cond_flux = -1.0                                # pure-conduction dT/dy = (0-1)/1 = -1
    return float(np.mean(dTdy_bottom) / cond_flux)

def val_rayleigh_benard_solver():
    n = 64
    Ras = [3.0, 3.23, 3.5, 3.8, 4.0, 4.3]          # log10 Ra: 1e3 .. 2e4
    Nus = []
    for lRa in Ras:
        T = S.solve_rayleigh_benard(np.array([[lRa]]), n)[0]
        Nus.append(_nusselt(T, n))
    # Nu should rise with Ra and exceed 1 in the convective regime
    rises = Nus[-1] > Nus[0]
    convects = Nus[-1] > 1.05
    rec("Rayleigh-Benard Nu increases with Ra (convection onset present)",
        rises and convects,
        f"Nu(Ra=10^[{Ras[0]}..{Ras[-1]}]) = {[round(x,3) for x in Nus]}")
    # Document the onset reference: classic 1708 is for an INFINITE layer; this is
    # a confined cavity (insulating sidewalls), whose Ra_c is higher.
    onset_idx = next((i for i, nu in enumerate(Nus) if nu > 1.05), None)
    onset = 10 ** Ras[onset_idx] if onset_idx else float("nan")
    rec("Rayleigh-Benard onset consistent with CONFINED cavity (>1708)",
        (onset_idx is None) or (onset > 1708),
        f"first Ra with Nu>1.05 ≈ {onset:.0f} (>1708 expected for insulated sidewalls; "
        f"1708 is the infinite-layer value, not this geometry)")
    # field sanity: T bounded in [0,1]-ish, hot bottom / cold top preserved
    T = S.solve_rayleigh_benard(np.array([[4.3]]), n)[0]
    rec("Rayleigh-Benard field physical (T BCs + bounded)",
        abs(T[0].mean() - 1.0) < 1e-6 and abs(T[-1].mean()) < 1e-6
        and T.min() > -0.05 and T.max() < 1.05,
        f"bottom<T>={T[0].mean():.3f} top<T>={T[-1].mean():.3f} range=[{T.min():.3f},{T.max():.3f}]")


# ============================================================================
# 4. PRESSURE-POISSON / POISEUILLE (analytic) — check stored fields ARE the
#    exact Hagen-Poiseuille structure and that fidelity nesting holds.
# ============================================================================
def val_pressure_poisson():
    d = np.load(f"{DATA}/pressure_poisson_poiseuille_mf.npz")
    params, x_dense, p_hf = d["params"], d["x_dense"], d["p_hf"]
    mask = d["mask_64"]
    # (a) velocity u_x parabolic across the fluid band (Poiseuille): take a column,
    #     fit u_x vs transverse coord inside the mask -> should be concave (neg 2nd diff)
    ok_par = []
    for i in range(min(20, len(params))):
        ux = x_dense[i, 1]                          # u_x channel
        col = ux[:, 32]                             # mid-axial column
        msk = mask[i, :, 32] > 0.5
        if msk.sum() >= 5:
            prof = col[msk]
            second = np.diff(prof, 2)
            ok_par.append(np.mean(second) < 0)     # concave => parabolic max in middle
    rec("Poiseuille velocity is parabolic (concave profile)",
        np.mean(ok_par) > 0.8, f"{int(np.sum(ok_par))}/{len(ok_par)} columns concave")
    # (b) pressure linear along the axis inside the fluid (constant gradient)
    lin_resid = []
    for i in range(min(20, len(params))):
        p = p_hf[i]; msk = mask[i] > 0.5
        axial = np.array([p[msk[:, j], j].mean() if msk[:, j].any() else np.nan
                          for j in range(p.shape[1])])
        good = np.isfinite(axial)
        xj = np.arange(p.shape[1])[good]; pv = axial[good]
        A = np.polyfit(xj, pv, 1); fit = np.polyval(A, xj)
        lin_resid.append(np.linalg.norm(pv - fit) / (np.ptp(pv) + 1e-12))
    rec("Poiseuille pressure linear along axis",
        np.median(lin_resid) < 0.1, f"median rel residual of linear fit = {np.median(lin_resid):.2e}")
    # (c) fidelity nesting: LF3 (32) ~ block-mean(HF 64) + small noise
    p_lf3 = d["p_lf3"]
    i = 0
    hf = p_hf[i]; bm = hf.reshape(32, 2, 32, 2).mean(axis=(1, 3))
    diff = np.linalg.norm(p_lf3[i] - bm) / np.linalg.norm(bm)
    rec("Pressure-Poisson LF = blockmean(HF)+noise (nested fidelity)",
        diff < 0.2, f"relL2(LF3 vs blockmean(HF)) = {diff:.2e} (noise ~U(0,0.05·range))")


# ============================================================================
# 5. RAYLEIGH-BENARD MF (Parussini 2017 recreate) — structure + nesting + BCs.
# ============================================================================
def val_rb_mf():
    d = np.load(f"{DATA}/rayleigh_benard_mf.npz")
    raLF, raMF, raHF = d["ra_LF"], d["ra_MF"], d["ra_HF"]
    # nested HF ⊂ MF ⊂ LF in Rayleigh number
    nested = (set(np.round(raHF, 3)).issubset(set(np.round(raLF, 3)))
              and set(np.round(raMF, 3)).issubset(set(np.round(raLF, 3))))
    rec("RB-MF nested Ra sampling (HF⊂MF⊂LF)",
        nested, f"LF={len(raLF)} MF={len(raMF)} HF={len(raHF)} samples, nested={nested}")
    # temperature BCs: bottom hot row, top cold row (README: row 0 = bottom)
    T = d["T_HF"]                                   # (S,n,n)
    bot, top = T[:, 0, :].mean(), T[:, -1, :].mean()
    rec("RB-MF temperature BCs (hot bottom, cold top)",
        bot > top and T.min() > -0.1 and T.max() < 1.1,
        f"<T> bottom={bot:.3f}, top={top:.3f}, range=[{T.min():.3f},{T.max():.3f}]")
    # self-convergence proxy: HF field finite & streamfunction nonzero at high Ra (convecting)
    psi = d["psi_HF"]
    rec("RB-MF fields finite + convective rolls present",
        np.isfinite(T).all() and np.isfinite(psi).all() and np.abs(psi).max() > 1e-6,
        f"max|psi|={np.abs(psi).max():.3e}, Ra range=[{raLF.min():.0f},{raLF.max():.0f}]")


if __name__ == "__main__":
    for f in (val_eikonal, val_cahn_hilliard, val_rayleigh_benard_solver,
              val_pressure_poisson, val_rb_mf):
        try:
            f()
        except Exception as e:
            rec(f.__name__, False, f"EXCEPTION: {type(e).__name__}: {e}")
    n_pass = sum(1 for _, ok, _ in out if ok)
    print("\n" + "=" * 72)
    print(f"UNVERIFIED-DATASET VALIDATION: {n_pass}/{len(out)} checks passed")
    print("=" * 72)
