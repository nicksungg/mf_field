"""Overview montage: one representative HF field per dataset across all 3 collections."""
import json, glob, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/orcd/data/faez/001/nick"
CORE = f"{ROOT}/mf_field"
ELO = f"{ROOT}/mf_field/sharp_generated"
EXT = f"{ROOT}/mf_field_extension_data/data_400_100"

# (label, group) -> loader returning (array2d_or_1d, kind)  kind in {"2d","1d","st"}
def from_xy(path, grid, kind="2d"):
    def _():
        y = np.load(path)["y"][0]
        if kind == "1d":
            return y, "1d"
        return y.reshape(grid), "2d"
    return _

def meta_grid(d):
    m = json.load(open(os.path.join(d, "meta.json")))
    lad = m["ladder"][-1]
    return (lad[0],) if len(lad) == 1 else (lad[0], lad[1])

def eloise_loader(name):
    d = f"{ELO}/{name}_generated"
    fs = sorted(glob.glob(d + "/train_l*.npz"))
    g = meta_grid(d)
    kind = "1d" if len(g) == 1 else "2d"
    return from_xy(fs[-1], g if kind == "2d" else None, kind)

def ext_loader(name):
    d = f"{EXT}/{name}_generated"
    fs = sorted(glob.glob(d + "/train_l*.npz"))
    g = meta_grid(d)
    if name == "kuramoto_sivashinsky_1d":   # space-time field
        return (lambda: (np.load(fs[-1])["y"][0].reshape(g), "st"))
    kind = "1d" if len(g) == 1 else "2d"
    return from_xy(fs[-1], g if kind == "2d" else None, kind)

panels = []  # (label, loader)

# ---- A. core (regenerated + local + ifc) ----
core_specs = [
    ("poisson", "poisson_generated/train_l3.npz", (64, 64), "2d"),
    ("heat", "heat_generated/train_l3.npz", (64, 64), "2d"),
    ("burgers", "burgers_generated/train_l3.npz", None, "1d"),
    ("burgers_param", "burgers_param_generated/train_l3.npz", None, "1d"),
    ("advection_diff", "advection_diffusion_generated/train_l2.npz", (64, 64), "2d"),
    ("allen_cahn", "allen_cahn_generated/train_l3.npz", None, "1d"),
    ("darcy", "darcy_generated/train_l3.npz", (128, 128), "2d"),
    ("lid_cavity", "lid_driven_cavity_generated/train_l3.npz", (128, 128), "2d"),
    ("poisson_local", "poisson_local/train_l5.npz", (128, 128), "2d"),
    ("heat_local", "heat_local/train_l5.npz", (128, 128), "2d"),
    ("fluid", "fluid/train_l2.npz", (64, 64), "2d"),
]
for lab, rel, g, k in core_specs:
    panels.append((f"[core] {lab}", from_xy(f"{CORE}/{rel}", g, k)))

# ifc_heat / ifc_poisson HF ys.npy (N,64,64)
for nm in ("ifc_heat", "ifc_poisson"):
    p = f"{CORE}/{nm}/train/fidelity_64/ys.npy"
    if os.path.exists(p):
        panels.append((f"[core] {nm}", (lambda pp=p: (np.load(pp)[0], "2d"))))

# era5 (l1 = 144x192, channel-flattened reanalysis) + pm_test (alias)
for nm, p in (("era5", f"{CORE}/era5/era5_train_test/train_l1.npz"),
              ("pm_test", f"{CORE}/pm_test/data/train_l1.npz")):
    if os.path.exists(p):
        panels.append((f"[core] {nm} (l1 144x192)",
                       (lambda pp=p: (np.load(pp)["y"][0].reshape(144, 192), "2d"))))

# ---- B. extension (8 parametric, excl 2 CFD) + rb_mf ----
for nm in ["helmholtz_2d", "rayleigh_benard_2d", "gray_scott_2d", "wave_2d",
           "eikonal_2d", "cahn_hilliard_2d", "kuramoto_sivashinsky_1d",
           "pressure_poisson_poiseuille"]:
    if os.path.isdir(f"{EXT}/{nm}_generated"):
        panels.append((f"[ext] {nm}", ext_loader(nm)))
rbmf = f"{ROOT}/mf_field_extension_data/data/rayleigh_benard_mf.npz"
if os.path.exists(rbmf):
    panels.append(("[ext] rayleigh_benard_mf", (lambda: (np.load(rbmf)["T_HF"][0], "2d"))))

# ---- C. eloise (23) ----
elo_names = [os.path.basename(d).replace("_generated", "")
             for d in sorted(glob.glob(ELO + "/*_generated"))]
for nm in elo_names:
    panels.append((f"[sharp] {nm}", eloise_loader(nm)))

# ---- render montage ----
n = len(panels)
ncols = 7
nrows = int(np.ceil(n / ncols))
fig, axes = plt.subplots(nrows, ncols, figsize=(2.4 * ncols, 2.4 * nrows))
axes = np.array(axes).reshape(-1)
ok = skip = 0
for ax, (label, loader) in zip(axes, panels):
    try:
        arr, kind = loader()
        if kind == "1d":
            ax.plot(np.asarray(arr).ravel(), lw=0.9)
            ax.set_xticks([]); ax.set_yticks([])
        else:
            im = arr
            ax.imshow(im, origin="lower", aspect="auto", cmap="viridis")
            ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(label, fontsize=7)
        ok += 1
    except Exception as e:
        ax.text(0.5, 0.5, f"{label}\nSKIP", ha="center", va="center", fontsize=6)
        ax.set_xticks([]); ax.set_yticks([]); skip += 1
        print("skip", label, e)
for ax in axes[len(panels):]:
    ax.axis("off")
fig.suptitle("MFFP-Bench combined: representative HF field per dataset "
             f"(eloise sharp + core + extension; {ok} shown)", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.98])
out = f"{ROOT}/mffp_bench_overview.png"
fig.savefig(out, dpi=110, bbox_inches="tight")
print(f"\nwrote {out}  ({ok} panels, {skip} skipped, {n} total)")
