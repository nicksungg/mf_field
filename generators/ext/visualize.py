"""
Visualize each multi-fidelity dataset and emit a human-readable DATASETS.md.
Produces:
  figures/<name>.png   -- per dataset: a few samples, LF (upsampled) | HF | abs diff
  figures/overview.png -- one HF sample per dataset in a grid
  DATASETS.md          -- table of parameters / sizes / fidelity from manifest.json
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import zoom

ROOT = "/archive/workspace/mf_field_data"
DATA = os.path.join(ROOT, "data")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

manifest = json.load(open(os.path.join(DATA, "manifest.json")))


def upsample(a, shape):
    if a.shape == tuple(shape):
        return a
    return zoom(a, (shape[0] / a.shape[0], shape[1] / a.shape[1]), order=1)


def panel(name):
    d = np.load(os.path.join(DATA, name + ".npz"))
    lf, hf, P = d["lf"], d["hf"], d["params"]
    pn = [str(x) for x in d["param_names"]]
    nrow = min(3, lf.shape[0])
    fig, ax = plt.subplots(nrow, 3, figsize=(9, 3 * nrow))
    ax = np.atleast_2d(ax)
    for r in range(nrow):
        i = r * (lf.shape[0] // nrow)
        lo = upsample(lf[i], hf[i].shape)
        hi = hf[i]
        vmin, vmax = hi.min(), hi.max()
        ax[r, 0].imshow(lo, origin="lower", vmin=vmin, vmax=vmax, cmap="viridis")
        ax[r, 1].imshow(hi, origin="lower", vmin=vmin, vmax=vmax, cmap="viridis")
        im = ax[r, 2].imshow(np.abs(hi - lo), origin="lower", cmap="magma")
        plt.colorbar(im, ax=ax[r, 2], fraction=0.046)
        ptxt = ", ".join(f"{n}={v:.2g}" for n, v in zip(pn, P[i]))
        ax[r, 0].set_ylabel(ptxt, fontsize=7)
        if r == 0:
            ax[r, 0].set_title(f"LF {tuple(lf.shape[1:])}→up")
            ax[r, 1].set_title(f"HF {tuple(hf.shape[1:])}")
            ax[r, 2].set_title("|HF - LF↑|")
        for c in range(3):
            ax[r, c].set_xticks([]); ax[r, c].set_yticks([])
    fig.suptitle(name, fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=90)
    plt.close(fig)


def overview():
    n = len(manifest)
    cols = 4; rows = (n + cols - 1) // cols
    fig, ax = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
    ax = ax.ravel()
    for j, m in enumerate(manifest):
        d = np.load(os.path.join(DATA, m["name"] + ".npz"))
        ax[j].imshow(d["hf"][0], origin="lower", cmap="viridis", aspect="auto")
        ax[j].set_title(m["name"].replace("_", " "), fontsize=8)
        ax[j].set_xticks([]); ax[j].set_yticks([])
    for j in range(n, len(ax)):
        ax[j].axis("off")
    fig.suptitle("Multi-fidelity field datasets — one HF sample each", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "overview.png"), dpi=100)
    plt.close(fig)


def write_md():
    lines = ["# Multi-fidelity field-prediction datasets\n",
             "Each `.npz` in `data/` has: `params (N,d)`, `lf (N,...)`, `hf (N,...)`, "
             "`param_names (d,)`.\n",
             "Fidelities are **aligned/nested**: `lf[i]` and `hf[i]` are the *same* "
             "parameter vector solved on a coarse vs. fine grid (genuine "
             "discretization-error fidelity gap). LF→HF upsampling is one line "
             "(`scipy.ndimage.zoom`).\n",
             "All PDEs here are chosen to **not overlap** with the existing "
             "collection (Poisson, heat, Darcy, advection-diffusion, Allen-Cahn, "
             "Burgers, lid-cavity, fluid, ERA5).\n",
             "![overview](figures/overview.png)\n",
             "| # | Dataset | PDE | Params (input) | N | LF grid | HF grid | Size |",
             "|---|---------|-----|----------------|---|---------|---------|------|"]
    total = 0.0
    for j, m in enumerate(manifest, 1):
        total += m["file_mb"]
        prs = "<br>".join(f"`{n}` ∈ [{lo:.2g}, {hi:.2g}]"
                          for n, (lo, hi) in zip(m["param_names"], m["param_ranges"]))
        lines.append(
            f"| {j} | **{m['name']}** | {m['pde']} | {prs} | {m['n_samples']} "
            f"| {tuple(m['lf_shape'])} | {tuple(m['hf_shape'])} | {m['file_mb']} MB |")
    lines.append(f"\n**Total: {len(manifest)} datasets, {total:.1f} MB.**\n")
    for m in manifest:
        lines.append(f"\n### {m['name']}\n")
        lines.append(f"- **PDE:** {m['pde']}")
        lines.append(f"- **What it adds:** {m['description']}")
        lines.append(f"- **Domain:** {m['domain']}")
        lines.append(f"- **Parameters (input):** " +
                     ", ".join(f"`{n}` ∈ [{lo:.3g}, {hi:.3g}]"
                               for n, (lo, hi) in zip(m["param_names"], m["param_ranges"])))
        lines.append(f"- **Samples:** {m['n_samples']}  | "
                     f"**LF:** {tuple(m['lf_shape'])}  **HF:** {tuple(m['hf_shape'])}")
        lines.append(f"\n![{m['name']}](figures/{m['name']}.png)")
    open(os.path.join(ROOT, "DATASETS.md"), "w").write("\n".join(lines))


if __name__ == "__main__":
    for m in manifest:
        print("plotting", m["name"])
        panel(m["name"])
    overview()
    write_md()
    print("wrote figures/ and DATASETS.md")
