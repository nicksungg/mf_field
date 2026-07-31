#!/usr/bin/env python
"""LF-conditioned headroom ladder — how much of a dataset's copy-LF error is
removable by a mechanism that reads the per-sample LF field, with zero training?

Provenance: s2_beyond_copy-B1 mechanism analysis, turn 2
(`worktrees/s2_beyond_copy/B1/scratchpad/reanalysis_turn_2.py`, findings F6-F9 in
card `experiment_cards/s2_beyond_copy/batch_1/B1.json` part 6).

What it measures
----------------
A ladder of training-free predictors, all scored with the round's own metric
(`round1/eval/nrmse.py`) against the round's own copy-LF baseline
(`round1/eval/panel_data.py::copylf_prediction`):

  L0  copylf                          the bar (1.000 by construction)
  L1  alpha * copylf                  one scalar, least-squares on TRAIN
  L2  copylf + mean(hf-lf) over TRAIN
  L3  copylf + kNN-in-X residual      residual keyed on the condition vector
  L4  y_train[NN-in-LF]               field lookup keyed on the LF field
  L5  copylf + kNN-in-LF residual     residual keyed on the LF FIELD  <-- the lever
  L6  L5 with the correction low-passed at 0.25*k_nyq
  Lx  knnX{k} field lookup            the X-only reference rungs
  O2  per-sample optimal scalar rescale of copylf  (ORACLE: uses HF, upper bound)

Reading the output
------------------
* `L5 << 1` -> Class A, residual-learnable: the residual hf-lf is a function of
  the LF field, and an LF-input residual architecture has real headroom.
* `L5 ~ 1` and `L1 ~ 1` -> Class B: copy-LF is already near-optimal for what
  (X, LF) determine at this N_train; the honest target is matching copy-LF.
* `L3 >> L5` -> the lever is the QUERY KEY (LF-conditioning), not the additive
  residual form.

The "LF key" is the copy-LF field block-mean-coarsened to `--sig` cells per side
and z-scored on train: a cheap shape descriptor, not cell-level memorization.
Test HF is used only for scoring and by the labelled oracle.

Invocation
----------
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/lf_conditioned_headroom.py \
      --datasets sharp__phase_field_crystal_2d,sharp__cahn_hilliard \
      --out /path/to/headroom.json [--sig 16] [--ks 1,5,10]

  # whole panel, from project.yaml:
  python tools/lf_conditioned_headroom.py --datasets PANEL --out headroom.json

Cost: pure numpy on the login node; ~1-3 min per 256x256 dataset (400 train +
100 test). No GPU, no SLURM, no model checkpoints.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml


def _round_root() -> Path:
    root = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
        check=True, cwd=Path(__file__).resolve().parent).stdout.strip())
    return root / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
import panel_data  # noqa: E402
from nrmse import NRMSE_DEF_HASH, nrmse  # noqa: E402


def signature(fields, grid, s):
    """Block-mean coarsening of flat fields to (s, s), flattened."""
    h, w = int(grid[0]), int(grid[1])
    f = np.asarray(fields, dtype=np.float64).reshape(-1, h, w)
    bh, bw = h // s, w // s
    if bh < 1 or bw < 1:
        raise ValueError(f"--sig {s} too large for grid {grid}")
    f = f[:, : bh * s, : bw * s].reshape(-1, s, bh, s, bw).mean(axis=(2, 4))
    return f.reshape(len(f), -1)


def _zorder(query, ref, ks):
    """Stable-sorted k-NN indices of `query` into `ref`, both already z-scored."""
    d = ((query[:, None, :] - ref[None, :, :]) ** 2).sum(axis=2)
    order = np.argsort(d, axis=1, kind="stable")
    return {int(k): order[:, :k] for k in ks}, np.sqrt(d.min(axis=1))


def _zscore(train, *others):
    mu = train.mean(axis=0)
    sd = np.where(train.std(axis=0) < 1e-12, 1.0, train.std(axis=0))
    return [(a - mu) / sd for a in (train,) + others]


def lowpass(fields, grid, frac):
    h, w = int(grid[0]), int(grid[1])
    f = np.asarray(fields).reshape(-1, h, w)
    F = np.fft.rfft2(f, axes=(1, 2))
    kx = np.fft.fftfreq(h) * h
    ky = np.arange(w // 2 + 1, dtype=np.float64)
    kr = np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)
    F = F * (kr <= frac * (min(h, w) / 2.0))[None, :, :]
    return np.fft.irfft2(F, s=(h, w), axes=(1, 2)).reshape(len(f), -1)


def resolve_grid_for(ds, n_cells):
    cfg = panel_data.load_config()
    sys.path.insert(0, str(panel_data.repo_root() / cfg["paths"]["factory_root"]))
    from data_adapters.geometry import resolve_grid
    return resolve_grid(ds, int(n_cells))


def run_dataset(ds, sig, ks, lp_frac=0.25):
    tr, te = panel_data.load_split(ds, "train"), panel_data.load_split(ds, "test")
    if not te["lf_fids"]:
        raise ValueError(f"{ds}: test split ships no LF fidelity; copy-LF undefined")
    y_tr = np.asarray(tr["field_by_fid"][tr["hf_fid"]], dtype=np.float64)
    y_te = np.asarray(te["field_by_fid"][te["hf_fid"]], dtype=np.float64)
    x_tr = np.asarray(tr["cond_by_fid"][tr["hf_fid"]], dtype=np.float64)
    x_te = np.asarray(te["cond_by_fid"][te["hf_fid"]], dtype=np.float64)
    lf_tr = panel_data.copylf_prediction(tr)
    lf_te = panel_data.copylf_prediction(te)
    grid = resolve_grid_for(ds, te["n_cells_by_fid"][te["hf_fid"]])
    r_tr = y_tr - lf_tr
    base = nrmse(lf_te, y_te)

    preds = {"L0_copylf": lf_te}
    a = float((lf_tr * y_tr).sum() / (lf_tr * lf_tr).sum())
    preds["L1_copylf_x_alpha"] = a * lf_te
    preds["L2_lf_plus_meanresid"] = lf_te + r_tr.mean(axis=0)[None, :]

    zx_tr, zx_te = _zscore(x_tr, x_te)
    ix_x, _ = _zorder(zx_te, zx_tr, ks)
    for k, ix in ix_x.items():
        preds[f"L3_lf_plus_knnX{k}_resid"] = lf_te + r_tr[ix].mean(axis=1)
        preds[f"Lx_knnX{k}_field"] = y_tr[ix].mean(axis=1)

    zs_tr, zs_te = _zscore(signature(lf_tr, grid, sig), signature(lf_te, grid, sig))
    ix_lf, dmin_te = _zorder(zs_te, zs_tr, ks)
    _, dmin_tr = _zorder(zs_tr, zs_tr, [2])  # includes self at distance 0
    dtt = ((zs_tr[:, None, :] - zs_tr[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(dtt, np.inf)
    kmax = max(ix_lf)
    preds["L4_knnLF1_field"] = y_tr[ix_lf[min(ks)][:, 0]]
    for k, ix in ix_lf.items():
        preds[f"L5_lf_plus_knnLF{k}_resid"] = lf_te + r_tr[ix].mean(axis=1)
    preds[f"L6_lf_plus_lowpass_knnLF{kmax}_resid"] = (
        lf_te + lowpass(r_tr[ix_lf[kmax]].mean(axis=1), grid, lp_frac))

    num = (lf_te * y_te).sum(axis=1)
    den = (lf_te * lf_te).sum(axis=1)
    preds["O2_ORACLE_copylf_persample_rescale"] = np.where(
        den > 0, num / den, 1.0)[:, None] * lf_te

    skill = {k: float(nrmse(v, y_te) / base) for k, v in preds.items()}
    lf_rungs = {k: v for k, v in skill.items() if k[:2] in ("L0", "L1", "L2", "L4", "L5", "L6")}
    best_lf = min((k for k in skill if k.startswith(("L1", "L2", "L4", "L5", "L6"))),
                  key=lambda k: skill[k])
    return {
        "dataset": ds, "grid": [int(g) for g in grid], "sig": sig, "ks": list(ks),
        "cond_dim": int(x_tr.shape[1]), "n_train": int(len(y_tr)), "n_test": int(len(y_te)),
        "copylf_nrmse": float(base), "alpha_global_train": a,
        "nrmse": {k: float(nrmse(v, y_te)) for k, v in preds.items()},
        "skill": skill,
        "best_lf_conditioned": best_lf,
        "best_lf_conditioned_skill": skill[best_lf],
        "class": "A_residual_learnable" if skill[best_lf] < 0.95 else "B_residual_unlearnable",
        "leak_control_test_over_train_nn_dist": float(
            np.median(dmin_te) / max(np.median(np.sqrt(dtt.min(axis=1))), 1e-12)),
        "nrmse_def_hash": NRMSE_DEF_HASH,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", required=True,
                    help="comma-separated dataset names, or PANEL for project.yaml's panel")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--sig", type=int, default=16, help="LF signature side length (default 16)")
    ap.add_argument("--ks", default="1,5,10", help="k values for both keys (default 1,5,10)")
    ap.add_argument("--lowpass_frac", type=float, default=0.25)
    args = ap.parse_args()

    if args.datasets.strip().upper() == "PANEL":
        cfg = yaml.safe_load(open(ROUND / "project.yaml"))
        dss = list(cfg["panel"])
    else:
        dss = [d for d in args.datasets.split(",") if d]
    ks = tuple(int(k) for k in args.ks.split(",") if k)

    out = {}
    for ds in dss:
        try:
            out[ds] = run_dataset(ds, args.sig, ks, args.lowpass_frac)
        except Exception as exc:  # e.g. ifc_poisson has no test LF
            out[ds] = {"dataset": ds, "error": f"{type(exc).__name__}: {exc}"}
            print(f"[skip] {ds}: {exc}", flush=True)
            continue
        r = out[ds]
        print(f"\n=== {ds}  copy-LF nRMSE {r['copylf_nrmse']:.6f}  [{r['class']}] ===")
        for k, v in sorted(r["skill"].items(), key=lambda kv: kv[1]):
            print(f"   {v:9.4f}  {k}")
        print(f"   best LF-conditioned rung: {r['best_lf_conditioned']} "
              f"= {r['best_lf_conditioned_skill']:.4f}; "
              f"leak control (test/train NN dist) = "
              f"{r['leak_control_test_over_train_nn_dist']:.2f}")

    ok = [d for d in out if "skill" in out[d]]
    if ok:
        keys = set.intersection(*[set(out[d]["skill"]) for d in ok])
        geo = {k: float(np.exp(np.mean([np.log(out[d]["skill"][k]) for d in ok])))
               for k in keys}
        out["_panel_geomean"] = geo
        out["_panel_geomean_best_lf_envelope"] = float(np.exp(np.mean(
            [np.log(out[d]["best_lf_conditioned_skill"]) for d in ok])))
        print("\n=== panel geomean over", len(ok), "datasets ===")
        for k, v in sorted(geo.items(), key=lambda kv: kv[1]):
            print(f"   {v:9.4f}  {k}")
        print(f"   {out['_panel_geomean_best_lf_envelope']:9.4f}  "
              f"<best LF-conditioned envelope>")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
