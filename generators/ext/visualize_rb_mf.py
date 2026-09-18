"""Sanity-check + visualization of rayleigh_benard_mf.npz."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from numpy.polynomial.legendre import legval

d = np.load("data/rayleigh_benard_mf.npz")
NE, NM = 7, 5

def reconstruct(coeffs, n):
    """Rebuild T(n,n) from (49,25) Legendre coeffs on the same uniform grid."""
    xs = np.linspace(0, 1, n)
    T = np.zeros((n, n))
    for I in range(NE):
        xmask = (xs >= I / NE - 1e-9) & (xs <= (I + 1) / NE + 1e-9)
        xi = (xs[xmask] - (I + 0.5) / NE) * (2 * NE)            # local [-1,1]
        for J in range(NE):
            ymask = (xs >= J / NE - 1e-9) & (xs <= (J + 1) / NE + 1e-9)
            eta = (xs[ymask] - (J + 0.5) / NE) * (2 * NE)
            c = coeffs[I * NE + J].reshape(NM, NM)             # (p,q)
            Px = np.stack([legval(xi, np.eye(NM)[p]) for p in range(NM)])   # (p, nx)
            Py = np.stack([legval(eta, np.eye(NM)[q]) for q in range(NM)])  # (q, ny)
            block = np.einsum("pq,px,qy->xy", c, Px, Py)
            ii = np.where(ymask)[0][:, None]; jj = np.where(xmask)[0][None, :]
            T[ii, jj] = block.T   # T is [y,x]
    return T

# reconstruction error per level
print("Legendre (49x25) reconstruction error vs field:")
for lvl in ["LF", "MF", "HF"]:
    n = len(d[f"x_{lvl}"]); T = d[f"T_{lvl}"]; L = d[f"Tleg_{lvl}"]
    errs = [np.abs(reconstruct(L[i], n) - T[i]).max() for i in range(len(T))]
    print(f"  {lvl}: max|recon-T| = {max(errs):.4f}")

# ---- Fig: temperature fields (HF) across Ra ----
T = d["T_HF"]; ra = d["ra_HF"]
fig, ax = plt.subplots(2, len(ra), figsize=(3 * len(ra), 6))
for i in range(len(ra)):
    im = ax[0, i].imshow(T[i], origin="lower", extent=[0, 1, 0, 1],
                         cmap="jet", vmin=0, vmax=1, aspect="equal")
    ax[0, i].set_title(f"T,  Ra={ra[i]:.0f}")
    ax[0, i].set_xticks([]); ax[0, i].set_yticks([])
    psi = d["psi_HF"][i]
    ax[1, i].imshow(psi, origin="lower", extent=[0, 1, 0, 1], cmap="RdBu", aspect="equal")
    ax[1, i].contour(np.linspace(0, 1, psi.shape[1]), np.linspace(0, 1, psi.shape[0]),
                     psi, 10, colors="k", linewidths=0.4)
    ax[1, i].set_title(r"$\psi$"); ax[1, i].set_xticks([]); ax[1, i].set_yticks([])
fig.colorbar(im, ax=ax[0, :], shrink=0.7, label="T")
fig.suptitle("Rayleigh-Benard HF: temperature (top) & streamfunction (bottom)")
fig.savefig("viz/rb_mf_fields.png", dpi=110, bbox_inches="tight")

# ---- Fig: a_12^(loc) of element 25 vs Ra, all three fidelities (cf. Fig 11) ----
# element "25" (1-based) in Fig 9b = center element -> I=J=3 -> idx 24; coeff a12 -> mode 11 (0-based)
ELEM, MODE = 24, 11
fig2, ax2 = plt.subplots(1, 1, figsize=(6, 4.5))
for lvl, mk in [("LF", "o-"), ("MF", "s-"), ("HF", "^-")]:
    ax2.plot(d[f"ra_{lvl}"], d[f"Tleg_{lvl}"][:, ELEM, MODE], mk, label=lvl, ms=5)
ax2.set_xlabel("Ra"); ax2.set_ylabel(r"$a_{12}^{(loc)}$ (element 25)")
ax2.set_title("Local-temperature Legendre coeff vs Ra (cf. Fig. 11)")
ax2.legend(); ax2.grid(alpha=0.3)
fig2.savefig("viz/rb_mf_coeff_vs_ra.png", dpi=110, bbox_inches="tight")
print("wrote viz/rb_mf_fields.png and viz/rb_mf_coeff_vs_ra.png")
