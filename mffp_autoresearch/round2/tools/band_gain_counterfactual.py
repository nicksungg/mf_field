#!/usr/bin/env python
"""band_gain_counterfactual.py -- IS THAT ARCHITECTURE ADVANTAGE JUST BAND CALIBRATION?

Fit ONE SCALAR PER RADIAL FOURIER BAND on a train-side calibration fold, apply it
to the arm's test prediction, and re-score through `round2/eval/nrmse.py`.  If a
6-number out-of-fold rescaling of arm B closes B's gap to arm A, the gap was
never representation -- it was amplitude CALIBRATION, and no amount of decoder
capacity is being measured.

WHY THIS EXISTS
---------------
`r2s1_direct-B1`: a 13.7-15.9 M-parameter FiLM-spectral condition->HF decoder beat
a ~150-parameter closed-form POD/ridge head by +6.9 % on
`sharp__phase_field_crystal_2d`.  A per-band amplitude/phase decomposition showed
BOTH arms had ring phase cosine ~ 0 (neither carries any phase information); the
decoder simply emitted 100x LESS energy in the band whose phase is unpredictable.
Six band gains fitted on the SAME 40-sample calibration fold the shipped blend
uses took the tiny head from 0.41455 to 0.38425 against the shipped 0.38403 --
residual gap 0.06 %, where the uncalibrated comparison said 6.9 %.  The same
calibration closed the gap on `ext__helmholtz_2d` (a uniform ~4x global shrink),
`sharp__allen_cahn_2d` and `sharp__fisher_kpp_2d`; only `sharp__cahn_hilliard`
survived it (+4.6 %).  Under a per-sample RELATIVE metric with an
unidentifiable component, the scored quantity rewards predicting LESS -- so any
capacity claim must be made against a band-calibrated competitor, not a raw one.

RELATION TO `band_weight_counterfactual.py` (round 1, s3_warp-B2)
----------------------------------------------------------------
That tool answers "which band OWNS an existing A-vs-B gap?" -- it swaps arm A's
Fourier error in one band for arm B's and re-scores, weighting every band ratio
by the error mass it can possibly be worth.  This tool answers the next question:
"does the gap SURVIVE if B is allowed to rescale its own bands out of fold?"
Use `band_weight_counterfactual.py` to locate a gap, this one to decide whether
the gap is calibration or representation.  They share no code and can be run in
either order (locate first is usually cheaper).

WHAT IT REPORTS
---------------
  hf_band_energy_share[b]   share of TEST HF energy in band b (what is at stake)
  fit.gains[b]              the fitted scalar per band (1.0 = untouched, 0 = band
                            deleted, <1 = shrinkage); fitted on the CAL fold only
  fit.cal_nrmse_before/after  the objective actually minimised (no test quantity)
  test.nrmse_raw / _gained  the scored effect of the calibration
  test.nrmse_gained_blended (with --blend) after re-selecting the floor blend
                            (lambda, base) on the same calibration fold
  gap (with a second arm)   A-vs-B nRMSE gap before and after B's calibration,
                            and `frac_of_gap_closed`

READ IT AS
----------
* `frac_of_gap_closed >= ~0.9` -> the A-vs-B difference is band calibration.  Any
  mechanism story about capacity/architecture on that dataset is unsupported
  until the competitor is re-run calibrated.
* gains that are a near-uniform s < 1 -> a pure GLOBAL amplitude shrink; the arm
  is mis-scaled, not mis-structured (r2s1-B1 helmholtz: 0.20-0.30 uniform,
  1.52895 -> 0.92769, i.e. parity with a 15.9 M-parameter network).
* gains that ZERO every non-DC band -> the only scoreable content is the spatial
  mean; check `condition_identifiable_rank.py` / `dc_pattern_split.py` next.
* gains that are non-monotone and include a value > 1 -> the arm is genuinely
  under-predicting some band; this is the one signature that does NOT reduce to
  shrinkage (r2s1-B1 `sharp__cahn_hilliard`: 0, 0.85, 0, 1.3, 0.2, 0).

HONESTY / SCOREABILITY
----------------------
Gains are fitted on a TRAIN-side fold only (`--fold_seed/--model_frac/--blend_frac`
reproduce `common.make_folds`, or pass `--cal_idx`), so the calibrated arm is a
legitimately scoreable predictor, not an oracle.  `--fit_on test` exists for
ceiling questions ONLY: it consults test HF, is labelled `ORACLE` in the output
JSON, and its numbers may never enter a card as an arm score.

COST CONTROL (why --gains / --passes exist)
-------------------------------------------
The calibration set is Fourier-decomposed into per-band spatial components ONCE,
so a coordinate-descent trial is a weighted sum, not an FFT.  Memory is
n_bands x n_cal x n_cells x 8 B (256^2 grid, 400 cal samples -> 1.3 GB): use
`--max_cal` to subsample.  `--gains` (grid points) and `--passes` (sweeps) trade
calibration quality for wall time; the r2s1-B1 default 31 x 2 finishes a 128^2
panel dataset in well under a minute with the decomposition, where the
FFT-in-the-loop scratchpad version blew the 20-minute cap on 256^2.

INVOCATION
----------
    source "$PROJECT_ROOT/.venv/bin/activate"
    # arm predictions: (n_train, n_cells) and (n_test, n_cells), loader order
    python tools/band_gain_counterfactual.py \
        --dataset sharp__phase_field_crystal_2d \
        --pred_train tiny_train.npy --pred_test tiny_test.npy \
        --blend --out /path/bandgain_pfc.json
    # ... with a reference arm to attribute a gap (npz needs path:key)
    python tools/band_gain_counterfactual.py \
        --dataset sharp__cahn_hilliard \
        --pred_train tiny_tr.npz:pred --pred_test tiny_te.npz:pred \
        --ref_test decoder_te.npy --gains 11 --passes 1 --max_cal 200 \
        --blend --out /path/bandgain_ch.json

Provenance: card `experiment_cards/r2s1_direct/batch_1/B1.json` part 6
(findings T3-F3/T3-F4/T3-F8); source probe
`worktrees/r2s1_direct/B1/scratchpad/turn3_followup.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import yaml


def _resolve_roots():
    here = Path(__file__).resolve()
    project_root = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
        check=True, cwd=here.parent).stdout.strip())
    round_root = here.parents[1]
    cfg = yaml.safe_load(open(round_root / "project.yaml"))
    paths = {k: (Path(v) if os.path.isabs(v) else (project_root / v).resolve())
             for k, v in cfg["paths"].items()}
    return project_root, round_root, cfg, paths


PROJECT_ROOT, ROUND_ROOT, CFG, PATHS = _resolve_roots()
sys.path.insert(0, str(PATHS["eval_dir"]))
sys.path.insert(0, str(PATHS["factory_root"]))
from nrmse import NRMSE_DEF_HASH, nrmse                # noqa: E402
from data_adapters.loaders import load_mf_dataset      # noqa: E402

LAMBDAS = np.linspace(0.0, 1.0, 21)
BLEND_BASES = ("zero", "train_mean", "nn_condition")


# ── data (stripped view; conditions + HF only, never LF) ────────────


def load_panel(name: str, data_root: Path):
    tr = load_mf_dataset(data_root / name, "train")
    te = load_mf_dataset(data_root / name, "test")
    hf = tr["hf_fid"]
    if hf not in te["fids"]:
        hf = te["hf_fid"]
    if te["lf_fids"]:
        raise RuntimeError(f"LEAKAGE TRIPWIRE: test split exposes LF fids {te['lf_fids']}")
    n_tr = np.asarray(tr["cond_by_fid"][hf]).shape[0]
    n_te = np.asarray(te["cond_by_fid"][hf]).shape[0]
    grid = tr["grid_shape_by_fid"].get(hf)
    return {
        "cond_train": np.asarray(tr["cond_by_fid"][hf], dtype=np.float64),
        "cond_test": np.asarray(te["cond_by_fid"][hf], dtype=np.float64),
        "hf_train": np.asarray(tr["field_by_fid"][hf], dtype=np.float64).reshape(n_tr, -1),
        "hf_test": np.asarray(te["field_by_fid"][hf], dtype=np.float64).reshape(n_te, -1),
        "grid": tuple(int(g) for g in grid) if grid is not None else None,
    }


def load_pred(spec: str, n_cells: int) -> np.ndarray:
    """`path.npy` or `path.npz:key` -> (N, n_cells) float64."""
    path, _, key = spec.partition(":")
    arr = np.load(path)
    if key or path.endswith(".npz"):
        arr = arr[key] if key else arr[list(arr.keys())[0]]
    arr = np.asarray(arr, dtype=np.float64).reshape(np.shape(arr)[0], -1)
    if arr.shape[1] != n_cells:
        raise SystemExit(f"{spec}: {arr.shape[1]} cells != dataset's {n_cells}")
    return arr


def make_folds(n: int, model_frac: float, blend_frac: float, seed: int):
    """Transcribed from the round-2 family convention (`common.make_folds`)."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_model = max(1, int(round(model_frac * n)))
    n_blend = max(1, int(round(blend_frac * n)))
    if n_model + n_blend >= n:
        raise ValueError(f"folds do not fit: n={n}, model={n_model}, blend={n_blend}")
    model_idx = np.sort(perm[:n_model])
    blend_idx = np.sort(perm[n_model:n_model + n_blend])
    fit_idx = np.sort(perm[n_model + n_blend:])
    return fit_idx, model_idx, blend_idx


# ── floors (for the optional blend re-selection) ────────────────────


def floor_fields(base: str, cond_q, cond_fit, hf_fit):
    if base == "zero":
        return np.zeros((cond_q.shape[0], hf_fit.shape[1]))
    if base == "train_mean":
        return np.broadcast_to(hf_fit.mean(axis=0), (cond_q.shape[0], hf_fit.shape[1])).copy()
    if base == "nn_condition":
        mu, sd = cond_fit.mean(0), cond_fit.std(0)
        sd = np.where(sd > 0, sd, 1.0)
        a, b = (cond_q - mu) / sd, (cond_fit - mu) / sd
        idx = np.argmin(((a[:, None, :] - b[None, :, :]) ** 2).sum(2), axis=1)
        return hf_fit[idx]
    raise ValueError(f"unknown floor base {base}")


def blend_select(y_cal, pred_cal, base_cal):
    best = None
    for name, b in base_cal.items():
        for lam in LAMBDAS:
            v = nrmse(lam * pred_cal + (1.0 - lam) * b, y_cal)
            if best is None or v < best["cal"]:
                best = {"base": name, "lambda": float(lam), "cal": v}
    return best


# ── radial bands ────────────────────────────────────────────────────


def radial_index(grid):
    ny, nx = grid
    ky = np.fft.fftfreq(ny) * ny
    kx = np.fft.fftfreq(nx) * nx
    KY, KX = np.meshgrid(ky, kx, indexing="ij")
    return np.sqrt(KY ** 2 + KX ** 2)


def band_masks(grid, inner_edges):
    kr = radial_index(grid)
    edges = [-0.5, 0.5] + list(inner_edges) + [float(kr.max()) + 1.0]
    labels = ["DC(k=0)"] + [f"{edges[i]:g}<k<={edges[i + 1]:g}"
                            for i in range(1, len(edges) - 2)]
    labels.append(f"k>{edges[-2]:g}")
    masks = [((kr > edges[i]) & (kr <= edges[i + 1])) for i in range(len(edges) - 1)]
    return masks, labels


def band_decompose(fields, grid, masks):
    """(n, cells) -> list of per-band spatial components summing back to `fields`."""
    n = fields.shape[0]
    F = np.fft.fft2(fields.reshape(n, *grid), axes=(1, 2))
    return [np.real(np.fft.ifft2(F * m, axes=(1, 2))).reshape(n, -1) for m in masks]


def apply_gains(fields, grid, masks, gains):
    n = fields.shape[0]
    F = np.fft.fft2(fields.reshape(n, *grid), axes=(1, 2))
    G = np.ones(grid)
    for m, g in zip(masks, gains):
        G[m] = g
    return np.real(np.fft.ifft2(F * G, axes=(1, 2))).reshape(n, -1)


def fit_band_gains(comps, y_cal, grid_pts, passes):
    """Coordinate descent over `grid_pts` gains, on the decomposed cal predictions."""
    nb = len(comps)
    gains = np.ones(nb)

    def score(g):
        p = comps[0] * g[0]
        for b in range(1, nb):
            if g[b] != 0.0:
                p = p + comps[b] * g[b]
        return nrmse(p, y_cal)

    best = score(gains)
    before = best
    for _ in range(int(passes)):
        for b in range(nb):
            cur = gains[b]
            for g in grid_pts:
                trial = gains.copy()
                trial[b] = g
                v = score(trial)
                if v < best - 1e-12:
                    best, cur = v, float(g)
            gains[b] = cur
    return gains, before, best


# ── main ────────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data_root", default=str(PATHS["stripped_data_root"]))
    ap.add_argument("--pred_test", required=True,
                    help="arm B test predictions, `path.npy` or `path.npz:key`")
    ap.add_argument("--pred_train", default=None,
                    help="arm B TRAIN predictions (n_train, n_cells); required "
                         "unless --fit_on test (ORACLE)")
    ap.add_argument("--ref_test", default=None,
                    help="optional arm A test predictions for gap attribution")
    ap.add_argument("--fit_on", choices=("cal", "test"), default="cal",
                    help="'cal' = train-side fold (scoreable); 'test' = ORACLE")
    ap.add_argument("--cal_idx", default=None,
                    help="npy of train indices to calibrate on (overrides folds)")
    ap.add_argument("--fold_seed", type=int, default=0)
    ap.add_argument("--model_frac", type=float, default=0.10)
    ap.add_argument("--blend_frac", type=float, default=0.10)
    ap.add_argument("--bands", default="4,8,16,32",
                    help="inner radial edges; DC and k>last are added")
    ap.add_argument("--gains", type=int, default=31,
                    help="gain grid points (>=2); grid = 0 plus linspace(gmin,gmax)")
    ap.add_argument("--gain_min", type=float, default=0.05)
    ap.add_argument("--gain_max", type=float, default=1.5)
    ap.add_argument("--passes", type=int, default=2)
    ap.add_argument("--max_cal", type=int, default=0,
                    help="subsample the calibration set to this many samples (0=all)")
    ap.add_argument("--blend", action="store_true",
                    help="re-select (base, lambda) over the floors on the same fold")
    args = ap.parse_args()

    t0 = time.time()
    P = load_panel(args.dataset, Path(args.data_root))
    if P["grid"] is None or len(P["grid"]) != 2:
        raise SystemExit(f"{args.dataset}: needs a 2-D grid_shape for radial bands")
    grid, hf_te, hf_tr = P["grid"], P["hf_test"], P["hf_train"]
    n_cells = hf_te.shape[1]
    masks, labels = band_masks(grid, [float(x) for x in args.bands.split(",") if x])

    pred_te = load_pred(args.pred_test, n_cells)
    if pred_te.shape != hf_te.shape:
        raise SystemExit(f"--pred_test {pred_te.shape} != test HF {hf_te.shape}")

    # ── the calibration set ──
    if args.fit_on == "test":
        cal_pred, y_cal, cal_desc = pred_te, hf_te, "ORACLE(test)"
        fit_idx = np.arange(hf_tr.shape[0])
        cond_cal = P["cond_test"]
    else:
        if args.pred_train is None:
            raise SystemExit("--pred_train is required unless --fit_on test")
        pred_tr = load_pred(args.pred_train, n_cells)
        if pred_tr.shape != hf_tr.shape:
            raise SystemExit(f"--pred_train {pred_tr.shape} != train HF {hf_tr.shape}")
        if args.cal_idx:
            cal_idx = np.asarray(np.load(args.cal_idx), dtype=int)
            fit_idx = np.setdiff1d(np.arange(hf_tr.shape[0]), cal_idx)
            cal_desc = f"cal_idx({args.cal_idx})"
        else:
            fit_idx, _, cal_idx = make_folds(hf_tr.shape[0], args.model_frac,
                                             args.blend_frac, args.fold_seed)
            cal_desc = (f"make_folds(seed={args.fold_seed}, model={args.model_frac}, "
                        f"blend={args.blend_frac})")
        if args.max_cal and len(cal_idx) > args.max_cal:
            cal_idx = cal_idx[np.linspace(0, len(cal_idx) - 1, args.max_cal).astype(int)]
            cal_desc += f" subsampled to {args.max_cal}"
        cal_pred, y_cal = pred_tr[cal_idx], hf_tr[cal_idx]
        cond_cal = P["cond_train"][cal_idx]

    # ── band energy shares of the TEST HF (what is at stake) ──
    H = np.fft.fft2(hf_te.reshape(hf_te.shape[0], *grid), axes=(1, 2))
    eH = np.abs(H) ** 2
    tot = eH.sum(axis=(1, 2))
    shares = [float(np.mean(eH[:, m].sum(axis=1) / tot)) for m in masks]

    # ── fit the gains ──
    gpts = np.concatenate([[0.0], np.linspace(args.gain_min, args.gain_max,
                                              max(1, args.gains - 1))])
    comps = band_decompose(cal_pred, grid, masks)
    gains, cal_before, cal_after = fit_band_gains(comps, y_cal, gpts, args.passes)
    del comps

    gained_te = apply_gains(pred_te, grid, masks, gains)
    out = {
        "_tool": "band_gain_counterfactual",
        "_nrmse_def_hash": NRMSE_DEF_HASH,
        "dataset": args.dataset, "grid": list(grid), "band_labels": labels,
        "hf_band_energy_share": shares,
        "calibration": {"source": cal_desc, "n_cal": int(y_cal.shape[0]),
                        "oracle": args.fit_on == "test",
                        "gain_grid": [float(gpts.min()), float(gpts.max()), len(gpts)],
                        "passes": int(args.passes)},
        "fit": {"gains": gains.tolist(), "cal_nrmse_before": cal_before,
                "cal_nrmse_after": cal_after},
        "test": {"nrmse_raw": nrmse(pred_te, hf_te),
                 "nrmse_gained": nrmse(gained_te, hf_te)},
    }

    # ── optional blend re-selection on the same fold ──
    if args.blend:
        if args.fit_on == "test":
            out["test"]["nrmse_gained_blended"] = None
            out["blend"] = {"skipped": "ORACLE calibration; blend would be oracle too"}
        else:
            base_cal = {b: floor_fields(b, cond_cal, P["cond_train"][fit_idx],
                                        hf_tr[fit_idx]) for b in BLEND_BASES}
            base_te = {b: floor_fields(b, P["cond_test"], P["cond_train"], hf_tr)
                       for b in BLEND_BASES}
            comps_cal = band_decompose(cal_pred, grid, masks)
            gcal = sum(c * g for c, g in zip(comps_cal, gains))
            del comps_cal
            sel = blend_select(y_cal, gcal, base_cal)
            blended = sel["lambda"] * gained_te + (1 - sel["lambda"]) * base_te[sel["base"]]
            sel0 = blend_select(y_cal, cal_pred, base_cal)
            blended0 = sel0["lambda"] * pred_te + (1 - sel0["lambda"]) * base_te[sel0["base"]]
            out["blend"] = {"after_gains": sel, "before_gains": sel0}
            out["test"]["nrmse_gained_blended"] = nrmse(blended, hf_te)
            out["test"]["nrmse_raw_blended"] = nrmse(blended0, hf_te)

    # ── optional gap attribution against a reference arm ──
    if args.ref_test:
        ref = load_pred(args.ref_test, n_cells)
        if ref.shape != hf_te.shape:
            raise SystemExit(f"--ref_test {ref.shape} != test HF {hf_te.shape}")
        key = ("nrmse_gained_blended" if args.blend
               and out["test"].get("nrmse_gained_blended") is not None else "nrmse_gained")
        raw_key = ("nrmse_raw_blended" if key == "nrmse_gained_blended"
                   else "nrmse_raw")
        v_ref = nrmse(ref, hf_te)
        gap0 = out["test"][raw_key] - v_ref
        gap1 = out["test"][key] - v_ref
        out["gap"] = {
            "ref_nrmse": v_ref, "arm_before": out["test"][raw_key],
            "arm_after": out["test"][key], "gap_before": gap0, "gap_after": gap1,
            "frac_of_gap_closed": (float((gap0 - gap1) / gap0) if abs(gap0) > 0 else None),
            "compared_on": key,
        }

    out["seconds"] = time.time() - t0
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "hf_band_energy_share"},
                     indent=1))
    print("band labels     :", labels)
    print("HF energy share :", [round(s, 5) for s in shares])
    print("wrote", args.out)


if __name__ == "__main__":
    main()
