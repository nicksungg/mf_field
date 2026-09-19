"""
Collect one representative field from every benchmark dataset (upstream + reimpl)
and render them all in a single composite figure, with provenance labels.

1D PDEs are shown as x-t (space-time) images; 2D as a spatial snapshot (last
timestep); 3D as a mid-plane slice. One sample (index 0) per dataset.
"""
import os, glob, json
import numpy as np
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

B = "/archive/workspace/mf_field_data/benchmarks"
NLE = f"{B}/PDEBench/pdebench/data_gen/data_gen_NLE/save"


def npy(p):  # first match
    return np.load(glob.glob(p)[0])


def h5first(p, sub="data"):
    f = h5py.File(glob.glob(p)[0], "r")
    g = f[sorted(f.keys())[0]]
    return np.array(g[sub])


def last2d(a):  # (...,H,W) take last leading index until 2D
    a = np.asarray(a)
    while a.ndim > 2:
        a = a[-1] if a.shape[0] < a.shape[-1] else a[..., 0]
        a = np.squeeze(a)
    return a


# (label, provenance, group, kind, loader)
DATASETS = [
    ("Advection 1D\nβ=1.0", "upstream", "PDEBench", "x-t",
     lambda: npy(f"{NLE}/advection/1D_Advection*beta1.0.npy")[0]),
    ("Burgers 1D\nν=0.01", "upstream", "PDEBench", "x-t",
     lambda: npy(f"{NLE}/burgers/1D_Burgers*Nu0.01.npy")[0]),
    ("Reaction-Diffusion 1D\nρ=10,ν=5", "upstream", "PDEBench", "x-t",
     lambda: npy(f"{NLE}/ReacDiff/ReacDiff_Nu5.0_Rho10.0.npy")[0]),
    ("Diffusion-Sorption 1D", "upstream", "PDEBench", "x-t",
     lambda: h5first(f"{B}/PDEBench/pdebench/data/1D_diff-sorp*/*.h5")[..., 0]),
    ("Compressible NS 1D\nM0=0, density", "upstream", "PDEBench", "x-t",
     lambda: np.squeeze(npy(f"{NLE}/CFD/HD_Sols_1D_rand*_D.npy")[0])),
    ("Compressible NS 2D\nM0=0.1, density", "upstream", "PDEBench", "2D",
     lambda: last2d(npy(f"{NLE}/CFD/HD_Sols_2D_rand*_D.npy")[0])),
    ("Compressible NS 3D\nM0=1, density (z-slice)", "upstream", "PDEBench", "3D",
     lambda: npy(f"{NLE}/CFD/HD_Sols_3D_rand*_D.npy")[0, -1, :, :, 8]),
    ("Darcy 2D\nβ=1.0, pressure", "upstream", "PDEBench", "2D",
     lambda: npy(f"{NLE}/ReacDiff/2D_ReacDiff_Multi_beta1.0_key2022.npy")[0, -1]),
    ("Diffusion-Reaction 2D\nactivator", "upstream", "PDEBench", "2D",
     lambda: h5first(f"{B}/PDEBench/pdebench/data_gen/data/2D_diff-react*/*.h5")[-1, :, :, 0]),
    ("Shallow Water 2D\nradial dam break (bonus)", "upstream", "PDEBench", "2D",
     lambda: h5first(f"{B}/PDEBench/pdebench/data_gen/data/2D_rdb*/*.h5")[-1, :, :, 0]),
    ("Incompressible NS 2D\nvorticity", "reimpl", "PDEBench", "2D",
     lambda: np.load(f"{B}/reimpl_out/PDEBench_incompressible_ns_2d.npz")["field"][0]),
    ("NS smoke 'standard'\nbuoyancy=0.5", "reimpl", "PDEArena", "2D",
     lambda: np.load(f"{B}/reimpl_out/PDEArena_ns_smoke_standard.npz")["field"][0]),
    ("NS smoke 'conditioned'\nbuoyancy param", "reimpl", "PDEArena", "2D",
     lambda: np.load(f"{B}/reimpl_out/PDEArena_ns_smoke_conditioned.npz")["field"][0]),
    ("Shallow Water 'weather'\nheight h", "reimpl", "PDEArena", "2D",
     lambda: np.load(f"{B}/reimpl_out/PDEArena_shallow_water_weather.npz")["field"][0]),
    ("Maxwell 3D\n|D|-field (z-slice)", "upstream", "PDEArena", "3D",
     lambda: np.linalg.norm(h5first(f"{B}/pdearena/out_maxwell/*.h5", "d_field")[..., :], axis=-1)[-1, :, :, 8]
             if False else
             np.linalg.norm(
                 np.array(h5py.File(glob.glob(f"{B}/pdearena/out_maxwell/*.h5")[0], "r")["train"]["d_field"])[0, -1, :, :, 8, :],
                 axis=-1)),
]

GCOL = {"PDEBench": "#1b7837", "PDEArena": "#2166ac"}
PMARK = {"upstream": "✓ upstream", "reimpl": "≈ reimpl (same eqs)"}

fig, axes = plt.subplots(4, 4, figsize=(16, 16))
axes = axes.ravel()
manifest = []
for j, (label, prov, group, kind, load) in enumerate(DATASETS):
    ax = axes[j]
    try:
        F = np.asarray(load(), dtype=float)
        F = np.squeeze(F)
        if F.ndim != 2:
            F = last2d(F)
        cmap = "RdBu_r" if F.min() < 0 else "viridis"
        ax.imshow(F, origin="lower", cmap=cmap, aspect="auto")
        tag = PMARK[prov]
        ax.set_title(f"[{group}] {label}\n{tag} · {F.shape} · {kind}",
                     fontsize=9, color=GCOL[group])
        manifest.append(dict(label=label.replace("\n", " "), group=group,
                             provenance=prov, kind=kind, shape=list(F.shape)))
    except Exception as e:
        ax.text(0.5, 0.5, f"FAILED\n{label}\n{e}", ha="center", va="center", fontsize=7)
        ax.set_title(label, fontsize=8)
        manifest.append(dict(label=label.replace("\n", " "), error=str(e)))
    ax.set_xticks([]); ax.set_yticks([])
for j in range(len(DATASETS), len(axes)):
    axes[j].axis("off")
fig.suptitle("PDEBench + PDEArena — one field per PDE  "
             "(✓ upstream solver  /  ≈ same-equation reimplementation)",
             fontsize=15, y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.985])
os.makedirs(f"{B}/figures", exist_ok=True)
fig.savefig(f"{B}/figures/all_benchmarks.png", dpi=95)
print("wrote figures/all_benchmarks.png")
json.dump(manifest, open(f"{B}/figures/manifest.json", "w"), indent=2)
for m in manifest:
    print(("  OK " if "error" not in m else " ERR ") +
          f"{m['label']:42s} {m.get('shape', m.get('error',''))}")
