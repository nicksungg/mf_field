#!/usr/bin/env python
"""Per-dataset floating-point precision band of the frozen training-free floor arms.

Provenance: promoted from `r3s4_audit-B1` mechanism turns 2 (+2b)
(`worktrees/r3s4_audit/B1/scratchpad/reanalysis_turn_2.py`,
`reanalysis_turn_2b.py`, results file sections 1-3).

Why it exists
-------------
Round-3's F1-class clauses compare a recomputed floor arm against a frozen value
at a HARD tolerance (1e-9 relative). That tolerance was written before anyone had
measured the arithmetic's own precision, and `r3s4_audit-B1`'s F1 fired at
1.1056e-9 on a cell whose round-off band is 7.85e-9 -- a tolerance below the
instrument's precision, not a floor-reproduction failure.

This tool measures that band per dataset, with two estimators:

  E1  PATH DIFFERENCE  |arm(native on-disk dtype) - arm(loader float32 view)| / arm
      The literal "float64 -> float32 loader seam". Defined only where a float64
      native copy exists, and identically 0 where the arrays ship float32 -- so
      it UNDER-measures exactly where no control exists (measured: `fluid` E1 = 0
      while its true band is 1.005e-8, 10x the carded tolerance).

  E2  ULP DITHER BAND  max over B random +/-1-ULP dithers of the float32 view of
      |arm(dithered) - arm(float32)| / arm.
      Defined for every dataset; measured >= E1 on 10/10 datasets and 20/20
      non-trivial arm cells. USE THIS ONE for tolerance setting.

Recommended F1-class tolerance per dataset: `max(--floor-tol, max_arm max(E1,E2))`.

E2 is a STOCHASTIC upper-bound estimate: a max over B random dithers, so it drifts
with B and with the RNG stream. This tool reseeds per dataset (`--seed`), while
the provenance run used one shared stream across datasets; the two agree to the
same order (ifc_heat 6.61e-9 here vs 7.85e-9 there). E1 is deterministic and
reproduces exactly (ifc_heat 1.106e-9, sod_1d 7.740e-8, fluid 0.0). Quote E1 for
exact provenance and E2 for tolerance setting, and raise `--b-dither` if you need
a tighter bound.

It is also a DEFECT DETECTOR, not just a tolerance calculator. A band that is
orders of magnitude above the others means the arm is DISCONTINUOUS in the data,
not merely imprecise. That is how `sharp__sod_1d` was found: band 3.078e-1
(31 % relative!), because it is the only panel/guard dataset with a degenerate
condition dimension (`std == 0` exactly) and `standardize_cond`'s guard
`sd = where(sd > 0, sd, 1.0)` is exact-equality-gated -- one ULP of dither moves
the measured std to ~1.2e-7, amplifying a pure-noise coordinate by ~8.4e6 and
re-selecting the nearest train atom on 53 % of test rows. `--nn-stability`
reports that directly.

Metric definitions are imported read-only from the round's own `nrmse.py`; the
arm constructions are byte-for-byte `eval/make_floor_anchors.py` /
`tools/make_round3_anchors.py`.

Usage
-----
  python tools/floor_precision_seam.py [--datasets a,b,c] [--floors-json PATH]
      [--arms nn_condition,train_mean,zero] [--b-dither 8] [--seed 0]
      [--nn-stability] [--floor-tol 1e-9] [--out seam.json]

Exit code 1 with --fail-on-discontinuity when any arm's band exceeds
--discontinuity-tol (default 1e-3), i.e. when a frozen floor is not continuous
in its own data.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


def _project_root() -> Path:
    here = Path(__file__).resolve()
    try:
        out = subprocess.run(["git", "-C", str(here.parent), "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:                                              # noqa: BLE001
        return here.parents[3]


ROOT = _project_root()
sys.path.insert(0, str(ROOT / "mffp_autoresearch" / "round2" / "eval"))
sys.path.insert(0, str(ROOT / "mf_field" / "factory_mffp"))

from nrmse import NRMSE_DEF_HASH, nrmse                            # noqa: E402

FROZEN_ARMS = ("nn_condition", "train_mean", "zero")


# ── data access (mirrors r3s4-B1 probes/_probe_common.py) ──

def load_view(root: Path, dataset: str, split: str):
    """Load a split through the round's loader (returns the float32 view)."""
    from data_adapters.loaders import load_mf_dataset
    d = load_mf_dataset(Path(root) / dataset, split)
    return (np.asarray(d["cond_by_fid"][d["hf_fid"]]),
            np.asarray(d["field_by_fid"][d["hf_fid"]]))


def native_arrays(root: Path, dataset: str, split: str):
    """Read the split's HF condition/field arrays in their NATIVE on-disk dtype."""
    d = Path(root) / dataset
    lv = sorted(int(p.stem.split("_l")[1]) for p in d.glob(f"{split}_l*.npz"))
    if lv:
        z = np.load(d / f"{split}_l{lv[-1]}.npz")
        return np.asarray(z["x"]), np.asarray(z["y"]).reshape(len(z["x"]), -1)
    fids = sorted(int(p.name.split("_")[1]) for p in (d / split).glob("fidelity_*")
                  if (d / split / p.name / "Xs.npy").exists())
    if fids:
        f = fids[-1]
        x = np.load(d / split / f"fidelity_{f}" / "Xs.npy")
        y = np.load(d / split / f"fidelity_{f}" / "ys.npy").reshape(len(x), -1)
        return np.asarray(x), np.asarray(y)
    return None, None


# ── arms ──

def standardize_cond(c_tr, c_te):
    mu, sd = c_tr.mean(axis=0), c_tr.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    return (c_tr - mu) / sd, (c_te - mu) / sd


def arms_from(c_tr, y_tr, c_te, y_te, arms):
    z_tr, z_te = standardize_cond(c_tr, c_te)
    d2 = ((z_te[:, None, :] - z_tr[None, :, :]) ** 2).sum(axis=2)
    nn = np.argmin(d2, axis=1)
    out = {}
    for a in arms:
        if a == "nn_condition":
            out[a] = float(nrmse(y_tr[nn], y_te))
        elif a == "train_mean":
            out[a] = float(nrmse(np.broadcast_to(y_tr.mean(axis=0), y_te.shape), y_te))
        elif a == "zero":
            out[a] = float(nrmse(np.zeros_like(y_te), y_te))
        else:
            raise SystemExit(f"unknown arm {a!r}")
    return out, nn, d2


def ulp_dither(a32, rng):
    a = np.asarray(a32, dtype=np.float32)
    up = np.nextafter(a, np.float32(np.inf))
    dn = np.nextafter(a, np.float32(-np.inf))
    return np.where(rng.integers(0, 2, size=a.shape).astype(bool), up, dn).astype(np.float64)


def rel(a, b):
    d = max(abs(a), abs(b))
    return abs(a - b) / d if d > 0 else 0.0


def analyse(ds, stripped_root, data_root, arms, b_dither, seed, nn_stability):
    t0 = time.time()
    rng = np.random.default_rng(seed)
    c_tr32, y_tr32 = load_view(stripped_root, ds, "train")
    c_te32, y_te32 = load_view(stripped_root, ds, "test")
    f64 = lambda a: np.asarray(a, dtype=np.float64)                # noqa: E731
    base, nn0, d2 = arms_from(f64(c_tr32), f64(y_tr32), f64(c_te32), f64(y_te32), arms)

    e1, native_dtype = {}, None
    nx_tr, ny_tr = native_arrays(data_root, ds, "train")
    nx_te, ny_te = native_arrays(data_root, ds, "test")
    if nx_tr is not None and nx_te is not None:
        native_dtype = str(ny_tr.dtype)
        nv, _, _ = arms_from(f64(nx_tr), f64(ny_tr), f64(nx_te), f64(ny_te), arms)
        e1 = {a: rel(base[a], nv[a]) for a in arms}

    dev = {a: [] for a in arms}
    flips = []
    for _ in range(b_dither):
        v, nn1, _ = arms_from(ulp_dither(c_tr32, rng), ulp_dither(y_tr32, rng),
                              ulp_dither(c_te32, rng), ulp_dither(y_te32, rng), arms)
        for a in arms:
            dev[a].append(rel(base[a], v[a]))
        if nn_stability:
            flips.append(float(np.mean(nn1 != nn0)))
    e2 = {a: float(max(dev[a])) for a in arms}
    per_arm = {a: max(e1.get(a, 0.0), e2[a]) for a in arms}

    rec = {"dataset": ds, "native_dtype": native_dtype,
           "stripped_dtype": str(y_tr32.dtype),
           "n_train": int(y_tr32.shape[0]), "n_test": int(y_te32.shape[0]),
           "cond_dim": int(c_tr32.shape[1]),
           "arm_values_float32_view": base,
           "E1_path_difference": e1, "E2_ulp_band_max": e2,
           "E2_ulp_band_median": {a: float(np.median(dev[a])) for a in arms},
           "per_arm_band": per_arm, "measured_band": float(max(per_arm.values())),
           "seconds": time.time() - t0}
    if nn_stability:
        srt = np.sort(d2, axis=1)
        margin = ((srt[:, 1] - srt[:, 0]) / np.maximum(srt[:, 1], 1e-300)
                  if srt.shape[1] > 1 else np.zeros(len(srt)))
        sd = f64(c_tr32).std(axis=0)
        rec["nn_stability"] = {
            "max_flip_frac_under_ulp_dither": float(max(flips)) if flips else None,
            "argmin_margin_q0": float(np.quantile(margin, 0.0)),
            "argmin_margin_q50": float(np.quantile(margin, 0.5)),
            "n_zero_margin_rows": int((margin == 0).sum()),
            "degenerate_cond_dims_std_exactly_zero": [int(j) for j in np.where(sd == 0)[0]],
        }
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", default=None, help="comma list; default = keys of --floors-json")
    ap.add_argument("--floors-json", default=str(
        ROOT / "mffp_autoresearch/round3/state/anchors_repaired/floors.json"))
    ap.add_argument("--stripped-root", default=str(
        ROOT / "mffp_autoresearch/round2/stripped_data"))
    ap.add_argument("--data-root", default=str(ROOT / "mf_field/factory_mffp/data"))
    ap.add_argument("--arms", default=",".join(FROZEN_ARMS))
    ap.add_argument("--b-dither", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--floor-tol", type=float, default=1e-9)
    ap.add_argument("--nn-stability", action="store_true",
                    help="also report NN-index flip fraction, argmin margins and "
                         "degenerate (std==0) condition dims")
    ap.add_argument("--discontinuity-tol", type=float, default=1e-3)
    ap.add_argument("--fail-on-discontinuity", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    arms = [a for a in args.arms.split(",") if a]
    if args.datasets:
        datasets = [d for d in args.datasets.split(",") if d]
    else:
        datasets = [d for d in json.load(open(args.floors_json)) if not d.startswith("_")]

    print(f"# floor precision seam | nrmse_def_hash {NRMSE_DEF_HASH[:12]} | "
          f"B={args.b_dither} seed={args.seed} arms={arms}")
    rows, bad = [], []
    for ds in datasets:
        try:
            r = analyse(ds, Path(args.stripped_root), Path(args.data_root), arms,
                        args.b_dither, args.seed, args.nn_stability)
        except Exception as e:                                     # noqa: BLE001
            print(f"  {ds:32s} ERROR {e!r}")
            continue
        r["recommended_tolerance"] = max(args.floor_tol, r["measured_band"])
        r["discontinuous"] = bool(r["measured_band"] > args.discontinuity_tol)
        if r["discontinuous"]:
            bad.append(ds)
        rows.append(r)
        print(f"  {ds:32s} native={str(r['native_dtype']):>8s} "
              f"E1={max(r['E1_path_difference'].values(), default=0.0):.3e} "
              f"E2={max(r['E2_ulp_band_max'].values()):.3e} "
              f"band={r['measured_band']:.3e}"
              f"{'  <-- DISCONTINUOUS' if r['discontinuous'] else ''}  ({r['seconds']:.1f}s)")

    print(f"\n{'dataset':32s}{'measured band':>16s}{'recommended tol':>18s}{'x floor-tol':>13s}")
    for r in sorted(rows, key=lambda x: -x["measured_band"]):
        print(f"{r['dataset']:32s}{r['measured_band']:>16.3e}"
              f"{r['recommended_tolerance']:>18.3e}"
              f"{r['recommended_tolerance'] / args.floor_tol:>13.1f}x")

    if args.nn_stability:
        print(f"\n{'dataset':32s}{'NN flip% @1ULP':>16s}{'margin p0':>12s}"
              f"{'degenerate cond dims':>24s}")
        for r in rows:
            s = r.get("nn_stability", {})
            fl = s.get("max_flip_frac_under_ulp_dither")
            print(f"{r['dataset']:32s}{(100*fl if fl is not None else float('nan')):>15.1f}%"
                  f"{s.get('argmin_margin_q0', float('nan')):>12.3e}"
                  f"{str(s.get('degenerate_cond_dims_std_exactly_zero')):>24s}")

    if bad:
        print(f"\nDISCONTINUOUS ARMS on {len(bad)} dataset(s): {bad}")
        print("  -> the frozen floor is not continuous in its own data; a regeneration, "
              "dtype change or loader change can move it silently. Investigate before "
              "quoting the value as a reference.")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump({"_nrmse_def_hash": NRMSE_DEF_HASH, "_b_dither": args.b_dither,
                   "_seed": args.seed, "_arms": arms, "_floor_tol": args.floor_tol,
                   "_discontinuity_tol": args.discontinuity_tol,
                   "n_datasets": len(rows), "discontinuous": bad, "rows": rows},
                  open(args.out, "w"), indent=1)
        print(f"wrote {args.out}")
    return 1 if (args.fail_on_discontinuity and bad) else 0


if __name__ == "__main__":
    raise SystemExit(main())
