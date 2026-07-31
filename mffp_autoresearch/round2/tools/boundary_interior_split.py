#!/usr/bin/env python
"""Is a predictor's error — or a CONTRAST between two predictors — BOUNDARY-BORNE?

Provenance: promoted from `s6_local-B2` mechanism analysis turns 1-2
(`worktrees/s6_local/B2/scratchpad/reanalysis_turn_{1,2}.py`). There it decided two
questions the card could not settle from scores alone:

  * the guard-set INVERSION (a trained local corrector beat a zero-parameter LSI
    filter by -88.3 % geomean on non-periodic data, the opposite of the panel).
    Crop 16 cells off every edge and the advantage SURVIVES (`fluid` 0.321 -> 0.344,
    `sharp__sod_1d` 0.058 -> 0.057, `heat_local` 0.086 -> 0.111), so it is an
    operator-class effect, not the FFT control tripping over its own wrap.
  * the `sharp__allen_cahn_2d` C2 sign flip (predicted NN/LSI 0.948, observed 1.126).
    The same crop moves the ratio to 0.986 — the flip is a ONE-CELL RIM defect in the
    trained arm, not a whole-field loss.

Round 1 keeps producing wins and losses that turn out to live in a few cells at the
domain edge (zero padding, circular padding on a non-periodic upsample, an FFT
control on a Dirichlet domain, `zoom(..., mode="nearest")`'s wrap seam). This is the
one-pass test. It is the EDGE-DISTANCE complement to
`tools/interface_locality_profile.py`, which bins by |grad HF| instead.

WHAT IT REPORTS, per prediction file
  nrmse_full                round nRMSE (eval/nrmse.py) on the whole field
  interior_nrmse[m]         the same metric recomputed on the interior crop at each
                            margin m (cells removed from every edge)
  strip[s].frac_sq_err      share of the file's total squared error inside the strip
                            `distance-to-edge < s cells`
  strip[s].frac_pixels      that strip's pixel share (the null)
  strip[s].concentration    frac_sq_err / frac_pixels. 1.0 = spatially neutral
  verdict                   BOUNDARY_BORNE (innermost-strip concentration >= 3) /
                            MILD (>= 1.5) / NEUTRAL / INTERIOR_BORNE (<= 0.67)

AND, when more than one file is given, per contrast vs the FIRST file
  ratio_by_margin[m]        nrmse(other, crop m) / nrmse(first, crop m)
  crop_sign_flip            True when the ratio crosses 1.0 between the full field
                            and the largest margin — i.e. the comparison's VERDICT is
                            decided by the boundary strip and should not be reported
                            without this table

READ IT AS
  A contrast whose `crop_sign_flip` is True is a boundary-handling result, not an
  operator-class result; say which one you mean. A contrast whose `ratio_by_margin`
  is flat is boundary-independent and can be attributed to representation. A single
  arm with `verdict = BOUNDARY_BORNE` has an unfixed padding / extension / seam bug
  worth more than any capacity knob: on `s6_local-B2` the circular-padding repair
  still left concentration 7.1x (pfc) and 7.4x (allen_cahn) in the outermost ring.

USAGE
  python tools/boundary_interior_split.py \
      --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
      [--pred_key pred --target_key target] [--grid H W] \
      [--strips 1 2 4 8 12 16] [--margins 0 4 8 12 16] \
      [--out split.json] [--plot split.png]

Each npz must carry a prediction array and a target array of shape (N, H*W) (or
(N, H, W)); every file must share the same target. 1-D layouts (H == 1) are handled
(distance is measured along the single axis).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
                         capture_output=True, text=True,
                         cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip())


sys.path.insert(0, str(_repo_root() / "mffp_autoresearch" / "round1" / "eval"))
from nrmse import nrmse as round_nrmse  # noqa: E402


def infer_grid(n_cells: int, grid_arg) -> tuple:
    if grid_arg:
        H, W = int(grid_arg[0]), int(grid_arg[1])
        if H * W != n_cells:
            raise ValueError(f"--grid {H}x{W} != {n_cells} cells")
        return (H, W)
    r = int(round(np.sqrt(n_cells)))
    if r * r == n_cells:
        return (r, r)
    return (1, n_cells)


def boundary_distance(grid) -> np.ndarray:
    """(H, W) distance to the nearest domain edge in cells (an edge cell is 0)."""
    H, W = int(grid[0]), int(grid[1])
    ix = np.minimum(np.arange(W), W - 1 - np.arange(W))
    if H == 1:
        return ix[None, :]
    iy = np.minimum(np.arange(H), H - 1 - np.arange(H))
    return np.minimum(iy[:, None], ix[None, :])


def load(path: str, pred_key: str, target_key: str):
    z = np.load(path, allow_pickle=False)
    if pred_key not in z:
        raise KeyError(f"{path}: no key {pred_key!r} (has {list(z.keys())})")
    if target_key not in z:
        raise KeyError(f"{path}: no key {target_key!r} (has {list(z.keys())})")
    p = np.asarray(z[pred_key], dtype=np.float64)
    t = np.asarray(z[target_key], dtype=np.float64)
    p = p.reshape(p.shape[0], -1)
    t = t.reshape(t.shape[0], -1)
    if p.shape != t.shape:
        raise ValueError(f"{path}: pred {p.shape} vs target {t.shape}")
    return p, t


def analyse(pred, target, grid, strips, margins) -> dict:
    d = boundary_distance(grid).reshape(-1)
    err = pred - target
    e2 = (err ** 2).sum(axis=0)
    tot = float(e2.sum())
    out = {"nrmse_full": round_nrmse(pred, target), "strip": {}, "interior_nrmse": {}}
    for s in strips:
        m = d < s
        fp = float(m.mean())
        fe = float(e2[m].sum() / tot) if tot > 0 else float("nan")
        out["strip"][str(s)] = {"frac_sq_err": fe, "frac_pixels": fp,
                                "concentration": (fe / fp) if fp > 0 else None}
    for m in margins:
        keep = d >= m
        out["interior_nrmse"][str(m)] = (round_nrmse(pred[:, keep], target[:, keep])
                                         if keep.sum() >= 16 else None)
    c = out["strip"][str(min(strips))]["concentration"]
    out["innermost_strip_concentration"] = c
    out["verdict"] = ("BOUNDARY_BORNE" if c is not None and c >= 3.0 else
                      "MILD" if c is not None and c >= 1.5 else
                      "INTERIOR_BORNE" if c is not None and c <= 0.67 else "NEUTRAL")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred_npz", nargs="+", required=True)
    ap.add_argument("--labels", nargs="*", default=None)
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    ap.add_argument("--grid", nargs=2, type=int, default=None)
    ap.add_argument("--strips", nargs="+", type=int, default=[1, 2, 4, 8, 12, 16])
    ap.add_argument("--margins", nargs="+", type=int, default=[0, 4, 8, 12, 16])
    ap.add_argument("--out", default=None)
    ap.add_argument("--plot", default=None)
    a = ap.parse_args()

    labels = a.labels or [Path(p).stem for p in a.pred_npz]
    if len(labels) != len(a.pred_npz):
        raise SystemExit("--labels must match --pred_npz in length")

    res = {"files": {}, "contrasts": {}, "strips": a.strips, "margins": a.margins}
    ref_target, grid = None, None
    for lab, path in zip(labels, a.pred_npz):
        p, t = load(path, a.pred_key, a.target_key)
        if ref_target is None:
            ref_target = t
            grid = infer_grid(t.shape[1], a.grid)
            res["grid"] = list(grid)
        elif t.shape != ref_target.shape or not np.allclose(t, ref_target, rtol=0, atol=0):
            raise SystemExit(f"{path}: target differs from {labels[0]}'s — refusing to compare")
        res["files"][lab] = analyse(p, ref_target, grid, a.strips, a.margins)
        res["files"][lab]["path"] = str(path)

    base = labels[0]
    for lab in labels[1:]:
        rb, rl = res["files"][base]["interior_nrmse"], res["files"][lab]["interior_nrmse"]
        ratio = {m: (rl[m] / rb[m]) if (rl[m] and rb[m]) else None for m in rb}
        vals = [v for v in ratio.values() if v is not None]
        flip = bool(vals and ((vals[0] - 1.0) * (vals[-1] - 1.0) < 0))
        res["contrasts"][f"{lab}_over_{base}"] = {
            "ratio_by_margin": ratio, "crop_sign_flip": flip,
            "ratio_full": ratio.get(str(a.margins[0])),
            "ratio_max_margin": ratio.get(str(a.margins[-1]))}

    print(f"grid {res['grid']}  strips {a.strips}  margins {a.margins}")
    for lab in labels:
        f = res["files"][lab]
        print(f"\n== {lab}   nrmse_full {f['nrmse_full']:.6e}   verdict {f['verdict']}")
        print("   strip  frac_sq_err  frac_pixels  concentration")
        for s in a.strips:
            v = f["strip"][str(s)]
            print(f"   d<{s:<4d} {v['frac_sq_err']:11.4f}  {v['frac_pixels']:11.4f}  "
                  f"{(v['concentration'] if v['concentration'] else float('nan')):13.3f}")
        print("   margin  interior_nrmse")
        for m in a.margins:
            v = f["interior_nrmse"][str(m)]
            print(f"   {m:<7d} {(v if v else float('nan')):.6e}")
    for k, c in res["contrasts"].items():
        print(f"\n== contrast {k}: ratio by margin " +
              " ".join(f"{m}:{(v if v else float('nan')):.4f}"
                       for m, v in c["ratio_by_margin"].items()) +
              f"  crop_sign_flip={c['crop_sign_flip']}")

    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(10, 6), dpi=100)
        for lab in labels:
            f = res["files"][lab]
            ax[0].plot(a.strips, [f["strip"][str(s)]["concentration"] for s in a.strips],
                       marker="o", label=lab)
            ax[1].plot(a.margins, [f["interior_nrmse"][str(m)] for m in a.margins],
                       marker="o", label=lab)
        ax[0].axhline(1.0, color="k", lw=0.8, ls="--")
        ax[0].set_xlabel("boundary strip width (cells)")
        ax[0].set_ylabel("sq-error concentration vs pixel share")
        ax[0].set_yscale("log"); ax[0].legend(); ax[0].set_title("boundary concentration")
        ax[1].set_xlabel("interior crop margin (cells)"); ax[1].set_ylabel("nRMSE")
        ax[1].set_yscale("log"); ax[1].legend(); ax[1].set_title("nRMSE vs crop")
        fig.tight_layout(); fig.savefig(a.plot); print(f"\nwrote {a.plot}")

    if a.out:
        with open(a.out, "w") as fh:
            json.dump(res, fh, indent=1)
        print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
