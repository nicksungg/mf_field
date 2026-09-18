"""Sanity-check visualization of pressure_poisson_poiseuille_mf.npz (cf. Figs. 2,9,10)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = np.load("data/pressure_poisson_poiseuille_mf.npz")
# pick samples spanning the pressure-gradient magnitude (v_max / r^2)
g = d["params"][:, 1] / d["params"][:, 0] ** 2
order = np.argsort(g)
sel = order[[20, 90, 150, 190]]

def vlim(img):  # tight symmetric range about 0.5 for visible gradient
    a = max(abs(img.min() - 0.5), abs(img.max() - 0.5), 1e-3)
    return 0.5 - a, 0.5 + a

# ---- Fig A: input channels + HF pressure + the 4 fidelities, for one sample ----
i = order[170]   # a clearly-sloped sample
fig, ax = plt.subplots(2, 4, figsize=(14, 7))
imgs = [("concentration", d["x_dense"][i, 0], "gray"),
        ("u_x (axial vel)", d["x_dense"][i, 1], "viridis"),
        ("u_y", d["x_dense"][i, 2], "viridis"),
        ("HF pressure 64", d["p_hf"][i], "jet")]
for a, (t, im, cm) in zip(ax[0], imgs):
    h = a.imshow(im, cmap=cm); a.set_title(t); a.set_xticks([]); a.set_yticks([])
    fig.colorbar(h, ax=a, shrink=0.7)
lo, hi = vlim(d["p_hf"][i])
for a, (t, key) in zip(ax[1], [("LF1 8x8", "p_lf1"), ("LF2 16x16", "p_lf2"),
                               ("LF3 32x32", "p_lf3"), ("HF 64x64", "p_hf")]):
    h = a.imshow(d[key][i], cmap="jet", vmin=lo, vmax=hi)
    a.set_title(t); a.set_xticks([]); a.set_yticks([])
    fig.colorbar(h, ax=a, shrink=0.7)
fig.suptitle(f"Pressure-Poisson / Poiseuille  (r={d['params'][i,0]:.3f}, vmax={d['params'][i,1]:.2f})\n"
             "top: dense-regression inputs + HF pressure   bottom: multifidelity targets (LF1->HF)")
fig.savefig("viz/pressure_mf_sample.png", dpi=100, bbox_inches="tight")

# ---- Fig B: HF pressure for 4 radii + centerline slices (cf. Fig 10) ----
fig2, ax2 = plt.subplots(1, 5, figsize=(18, 3.4))
for k, i in enumerate(sel):
    ax2[k].imshow(d["p_hf"][i], cmap="jet", vmin=0.42, vmax=0.58)
    ax2[k].set_title(f"r={d['params'][i,0]:.2f}, vmax={d['params'][i,1]:.2f}")
    ax2[k].set_xticks([]); ax2[k].set_yticks([])
    ax2[k].axhline(32, color="w", ls=":", lw=0.8)
for i in sel:
    ax2[4].plot(d["p_hf"][i][32], label=f"r={d['params'][i,0]:.2f}")
ax2[4].set_title("centerline pressure vs axial location"); ax2[4].set_xlabel("location")
ax2[4].set_ylabel("pressure"); ax2[4].legend(fontsize=8); ax2[4].grid(alpha=0.3)
fig2.savefig("viz/pressure_mf_slices.png", dpi=100, bbox_inches="tight")
print("wrote viz/pressure_mf_sample.png and viz/pressure_mf_slices.png")
