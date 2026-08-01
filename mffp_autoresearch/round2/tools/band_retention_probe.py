#!/usr/bin/env python
"""What part of the spectrum does this predictor actually PRODUCE?

ROUND-2 tool, promoted from `r2s4_diag-B3` mechanism turn 3.

A field predictor can post a finite nRMSE while contributing literally nothing
above the spatial mean. The round metric cannot see that; a radial-band energy
audit can. For each log-spaced radial wavenumber band `b` this reports

  * `hf_energy_share[b]`      - where the TRUTH's energy actually lives;
  * `retained_energy_ratio[b] = E_arm(b) / E_truth(b)` - does the arm produce
    energy in this band at all (a conditional-mean estimator averages
    realisation structure away and is DEPLETED where the condition does not
    determine the field);
  * `band_relative_error[b]  = E_{truth-arm}(b) / E_truth(b)` - the decisive
    number. **1.00 means the arm contributes EXACTLY ZERO useful energy in that
    band** (identical to predicting zero there); > 1 means it injects wrong
    energy; « 1 means the band is genuinely reconstructed.

With `--advantage A:B` it also localises WHERE an arm-vs-arm advantage lives:
the per-band share of `E_{truth-A}(b) - E_{truth-B}(b)`. A band-localised
advantage is a design target; a uniform one is not.

On r2s4-B3 this turned "the condition-only arm scores 11-148x copy-LF" into
"the condition-only arm's band relative error is ~1.00 in every band above the
lowest on 3 of 4 sharp datasets" -- i.e. not a model doing poorly, a model
contributing nothing above DC. The same probe located the LF teacher's
advantage to 1-2 bands (83-100% of it) and explained a primary arm losing to
its own zero-field floor (it retained 0.5% of the truth's energy in EVERY band).

Numerical guard: bands whose `hf_energy_share` falls below `--min_energy_share`
are round-off and are flagged `meaningless`; ratios there routinely reach 1e9
and must not be read. Verdicts ignore them.

Read-only; skills go through `round2/eval/nrmse.py`. Real `rfft2` with the
Hermitian double-count correction on interior columns (energies are exact).

CAVEAT: prediction dumps are not always in dataset row order (r2s4-B3's
`preds_oof_*.npz` carry an `oof_row_index` permutation). Band energies here are
means over samples and are therefore permutation-invariant, but the per-arm
SKILL column is not -- pass arrays from the same dump, or permute first.

Invocation
----------
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/band_retention_probe.py \
        --truth <outputs>/preds_oof_sharp__cahn_hilliard_e200_s0.npz:hf_true \
        --arm T0=<same npz>:T0_cond_only --arm I1=<same npz>:I1_lf_teacher \
        --dataset sharp__cahn_hilliard --advantage T0:I1 --out bands.json

`NAME=path.npz[:key]` (key defaults to `pred`), so one-npz-per-arm layouts work
too. Grid from `data_adapters.geometry.resolve_grid` when available, else
`--grid HxW`.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROUND_ROOT = HERE.parent
sys.path.insert(0, str(ROUND_ROOT / "eval"))
import nrmse as R                                             # noqa: E402


def parse_ref(spec: str, default_key: str = "pred"):
    name, body = (spec.split("=", 1) if "=" in spec
                  and not spec.split("=", 1)[0].endswith(".npz") else (None, spec))
    if ":" in body and not body.rsplit(":", 1)[1].endswith(".npz"):
        path, key = body.rsplit(":", 1)
    else:
        path, key = body, default_key
    return (name or pathlib.Path(path).stem), path, key


def load_ref(spec: str, default_key: str = "pred"):
    name, path, key = parse_ref(spec, default_key)
    z = np.load(path)
    if key not in z.files:
        raise SystemExit(f"{path}: key {key!r} not present; has {list(z.files)}")
    arr = np.asarray(z[key])
    if arr.ndim != 2:
        arr = arr.reshape(arr.shape[0], -1)
    return name, arr.astype(np.float32)


def resolve_hw(dataset, n_cells, override):
    if override:
        h, w = override.lower().split("x")
        return int(h), int(w)
    try:
        factory = ROUND_ROOT.parent.parent / "mf_field" / "factory_mffp"
        sys.path.insert(0, str(factory))
        from data_adapters.geometry import resolve_grid       # noqa: PLC0415
        return tuple(int(v) for v in resolve_grid(dataset, int(n_cells)))
    except Exception:                                          # noqa: BLE001
        s = int(round(np.sqrt(n_cells)))
        if s * s == int(n_cells):
            return s, s
        raise SystemExit("cannot infer the grid; pass --grid HxW")


def radial_bands(H, W, n_bands):
    ky = np.fft.fftfreq(H) * H
    kx = np.fft.rfftfreq(W) * W
    kk = np.sqrt(ky[:, None] ** 2 + kx[None, :] ** 2)
    edges = np.concatenate([[0.0], np.geomspace(1.0, kk.max() + 1e-9, n_bands)])
    return np.digitize(kk, edges[1:-1], right=False), edges


def band_energy(F, idx, W, n_bands):
    """Mean-over-samples energy per band; interior rfft columns count twice."""
    w = np.full(F.shape[-1], 2.0)
    w[0] = 1.0
    if W % 2 == 0:
        w[-1] = 1.0
    p = (np.abs(F) ** 2).astype(np.float64) * w[None, None, :]
    return np.array([p[:, idx == b].sum(axis=1).mean() for b in range(n_bands)])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--truth", required=True, help="NAME=path.npz[:key]")
    ap.add_argument("--arm", action="append", required=True,
                    help="repeatable NAME=path.npz[:key]")
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--grid", default=None, help="HxW override")
    ap.add_argument("--bands", type=int, default=8)
    ap.add_argument("--advantage", default=None, help="A:B — locate skill(A)-skill(B)")
    ap.add_argument("--min_energy_share", type=float, default=1e-9)
    ap.add_argument("--dc_tol", type=float, default=0.05,
                    help="|band_relative_error - 1| <= tol counts as 'contributes nothing'")
    ap.add_argument("--skill_denominator", type=float, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    _, y = load_ref(a.truth, "hf_true")
    H, W = resolve_hw(a.dataset, y.shape[1], a.grid)
    if H * W != y.shape[1]:
        raise SystemExit(f"grid {H}x{W} != n_cells {y.shape[1]}")

    denom = a.skill_denominator
    if denom is None and a.dataset:
        cl = json.loads((ROUND_ROOT / "eval" / "copylf_baselines.json").read_text())
        denom = cl.get(a.dataset, {}).get("test_nrmse")
    denom = denom or 1.0

    idx, edges = radial_bands(H, W, a.bands)
    F_y = np.fft.rfft2(y.reshape(-1, H, W))
    E_y = band_energy(F_y, idx, W, a.bands)
    share = E_y / E_y.sum()
    meaningless = (share < a.min_energy_share)

    arms, E_arm, E_err, skills = {}, {}, {}, {}
    for spec in a.arm:
        name, arr = load_ref(spec)
        if arr.shape != y.shape:
            raise SystemExit(f"{name}: shape {arr.shape} != truth {y.shape}")
        arms[name] = arr
        Fa = np.fft.rfft2(arr.reshape(-1, H, W))
        E_arm[name] = band_energy(Fa, idx, W, a.bands)
        E_err[name] = band_energy(F_y - Fa, idx, W, a.bands)
        skills[name] = R.skill(R.nrmse(arr.astype(np.float64),
                                       y.astype(np.float64)), denom)
        del Fa
    del F_y

    safe = np.maximum(E_y, 1e-300)
    out = {
        "_tool": "band_retention_probe.py",
        "_nrmse_def_hash": R.NRMSE_DEF_HASH,
        "dataset": a.dataset, "grid": [H, W],
        "n_rows": int(y.shape[0]), "n_bands": a.bands,
        "band_edges_k": [float(x) for x in edges],
        "skill_denominator": denom, "skill": skills,
        "hf_energy_share": share.tolist(),
        "band_meaningless": meaningless.tolist(),
        "min_energy_share": a.min_energy_share,
        "retained_energy_ratio": {n: (E_arm[n] / safe).tolist() for n in arms},
        "band_relative_error": {n: (E_err[n] / safe).tolist() for n in arms},
    }

    # per-arm verdict: does it contribute anything above the lowest band?
    verdicts = {}
    for n in arms:
        bre = E_err[n] / safe
        live = [b for b in range(1, a.bands) if not meaningless[b]]
        null_bands = [b for b in live if abs(bre[b] - 1.0) <= a.dc_tol]
        verdicts[n] = {
            "live_bands_above_lowest": live,
            "bands_contributing_nothing": null_bands,
            "contributes_nothing_above_lowest_band":
                bool(live) and len(null_bands) == len(live),
            "energy_share_of_null_bands": float(share[null_bands].sum())
            if null_bands else 0.0,
        }
    out["verdict_per_arm"] = verdicts

    if a.advantage:
        A, B = a.advantage.split(":")
        for nm in (A, B):
            if nm not in arms:
                raise SystemExit(f"--advantage names unknown arm {nm!r}")
        adv = E_err[A] - E_err[B]
        tot = adv.sum()
        sh = (adv / tot) if tot else np.zeros_like(adv)
        order = np.argsort(-np.abs(sh))
        out["advantage"] = {
            "pair": f"{A}-{B}",
            "skill_delta": skills[A] - skills[B],
            "energy_per_band": adv.tolist(),
            "share_per_band": sh.tolist(),
            "total_energy": float(tot),
            "top_band": int(order[0]), "top_band_share": float(sh[order[0]]),
            "n_bands_for_80pct": int(
                1 + np.argmax(np.cumsum(np.abs(sh[order])) >= 0.8)),
            "localised": bool(np.cumsum(np.abs(sh[order]))[
                min(1, a.bands - 1)] >= 0.8),
        }

    # ---- console
    fmt = lambda v, w: " ".join(f"{x:{w}}" for x in v)          # noqa: E731
    print(f"dataset={a.dataset} grid={H}x{W} rows={y.shape[0]} "
          f"bands(upper |k|)={['%.0f' % x for x in edges[1:]]}")
    print(f"  {'hf energy share':26s}", fmt(share, "9.2e"))
    print(f"  {'band meaningless':26s}",
          " ".join(f"{('y' if m else '.'):>9s}" for m in meaningless))
    for n in arms:
        print(f"  {'retained ' + n:26s}", fmt(E_arm[n] / safe, "9.3f"))
    for n in arms:
        print(f"  {'band rel err ' + n:26s}", fmt(E_err[n] / safe, "9.3f"))
    for n, v in verdicts.items():
        if v["contributes_nothing_above_lowest_band"]:
            print(f"  [!] {n}: CONTRIBUTES NOTHING above the lowest band — band "
                  f"relative error is 1.00 +/- {a.dc_tol} in all "
                  f"{len(v['live_bands_above_lowest'])} live bands "
                  f"({100*v['energy_share_of_null_bands']:.1f}% of truth energy)")
    if a.advantage:
        adv = out["advantage"]
        print(f"  {'advantage share ' + adv['pair']:26s}",
              fmt(np.array(adv["share_per_band"]), "9.3f"))
        print(f"  [i] {adv['pair']}: skill delta {adv['skill_delta']:.6g}; "
              f"{'BAND-LOCALISED' if adv['localised'] else 'spread'} — top band "
              f"{adv['top_band']} carries {100*adv['top_band_share']:.1f}%, "
              f"{adv['n_bands_for_80pct']} band(s) carry 80%")

    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
