"""Independent shock-solver check: PyClaw Sod output vs the EXACT Riemann solution.

The Sod shock tube (Sod 1978) has a closed-form solution (Toro, Riemann Solvers, ch.4):
a left rarefaction + contact discontinuity + right shock. We solve the exact Riemann
problem here from scratch and compare the solver's density profile, checking the error
DECREASES with resolution (a finite-volume shock smears over a few cells, so pointwise
equality is not expected, but it must converge).
"""
import numpy as np
from mffp_sharp.pdes import sod

g = 1.4
rhoL, uL, pL = 1.0, 0.0, 1.0          # classic Sod left state
rhoR, uR, pR = 0.125, 0.0, 0.1        # classic Sod right state (matches sod.py defaults)
T = 0.2
x0 = 0.5

aL = np.sqrt(g * pL / rhoL)
aR = np.sqrt(g * pR / rhoR)

def f_K(p, rhoK, pK, aK):
    if p > pK:  # shock
        A = 2.0 / ((g + 1) * rhoK); B = (g - 1) / (g + 1) * pK
        return (p - pK) * np.sqrt(A / (p + B))
    else:       # rarefaction
        return 2 * aK / (g - 1) * ((p / pK) ** ((g - 1) / (2 * g)) - 1)

def f(p):
    return f_K(p, rhoL, pL, aL) + f_K(p, rhoR, pR, aR) + (uR - uL)

# bisection for p_star
lo, hi = 1e-8, 10.0
for _ in range(200):
    mid = 0.5 * (lo + hi)
    if f(mid) > 0: hi = mid
    else: lo = mid
p_star = 0.5 * (lo + hi)
u_star = 0.5 * (uL + uR) + 0.5 * (f_K(p_star, rhoR, pR, aR) - f_K(p_star, rhoL, pL, aL))

def sample(xi):
    """Exact (rho,u,p) at self-similar coordinate xi=(x-x0)/t."""
    if xi < u_star:   # left of contact
        if p_star > pL:  # left shock (not for Sod, but general)
            rho_sL = rhoL * ((p_star / pL + (g - 1) / (g + 1)) /
                             ((g - 1) / (g + 1) * p_star / pL + 1))
            S = uL - aL * np.sqrt((g + 1) / (2 * g) * p_star / pL + (g - 1) / (2 * g))
            return (rhoL, uL, pL) if xi < S else (rho_sL, u_star, p_star)
        else:            # left rarefaction (Sod case)
            rho_sL = rhoL * (p_star / pL) ** (1 / g)
            a_sL = aL * (p_star / pL) ** ((g - 1) / (2 * g))
            SHL = uL - aL                     # head
            STL = u_star - a_sL               # tail
            if xi < SHL: return rhoL, uL, pL
            if xi > STL: return rho_sL, u_star, p_star
            u = 2 / (g + 1) * (aL + (g - 1) / 2 * uL + xi)
            a = 2 / (g + 1) * (aL + (g - 1) / 2 * (uL - xi))
            rho = rhoL * (a / aL) ** (2 / (g - 1))
            p = pL * (a / aL) ** (2 * g / (g - 1))
            return rho, u, p
    else:             # right of contact -> right shock (Sod case)
        rho_sR = rhoR * ((p_star / pR + (g - 1) / (g + 1)) /
                         ((g - 1) / (g + 1) * p_star / pR + 1))
        S = uR + aR * np.sqrt((g + 1) / (2 * g) * p_star / pR + (g - 1) / (2 * g))
        return (rho_sR, u_star, p_star) if xi < S else (rhoR, uR, pR)

print(f"exact: p*={p_star:.5f}, u*={u_star:.5f}  (Toro reference p*=0.30313, u*=0.92745)")

errs = {}
for res in (256, 512, 1024):
    rho_num = sod._solve(res, rhoL, pL, g, T, high_fidelity=True)   # SharpClaw WENO
    x = (np.arange(res) + 0.5) / res
    rho_exact = np.array([sample((xi - x0) / T)[0] for xi in x])
    errs[res] = float(np.linalg.norm(rho_num - rho_exact) / np.linalg.norm(rho_exact))

print(f"density relL2 vs exact @256/512/1024 = "
      f"{errs[256]:.3e}/{errs[512]:.3e}/{errs[1024]:.3e}")
converging = errs[1024] < errs[512] < errs[256]
ok = converging and errs[1024] < 0.03
print(f"[{'PASS' if ok else 'FAIL'}] Sod exact-Riemann: converging↓={converging}, "
      f"finest relL2={errs[1024]:.3e}")
