#!/usr/bin/env python
"""persample_norm_eligibility.py -- should this dataset's regression target be
normalised PER SAMPLE? A pre-flight, model-free GO / NO-GO with a reason.

Promoted from `s2_beyond_copy-B3` mechanism turns 2-3
(`worktrees/s2_beyond_copy/B3/scratchpad/reanalysis_turn_2.py` +
`reanalysis_turn_2b.py`); provenance card
`experiment_cards/s2_beyond_copy/batch_3/B3.json` part 6, findings F5-F8, F13.

WHY THIS EXISTS
---------------
Round 1 ran three normalisation cards (s5_tuning-B2 per-dataset affine,
s7_loss-B1/B2 per-sample RELATIVE loss, s2_beyond_copy-B3 per-sample RESIDUAL
target) and the panel's residual/field SPREAD -- the statistic every one of them
selected on -- got the sign WRONG on `sharp__phase_field_crystal_2d`: largest
spread in the panel (7.9e04), healthiest effective N (140/400), and per-sample
normalisation made it 4.2x worse. The statistic that ordered all five outcomes
is the effective N of the loss, gated by whether the samples the re-weighting
PROMOTES carry signal at all.

WHAT IT MEASURES (per dataset, train split, no model, no GPU)
-------------------------------------------------------------
Every normalisation is a re-weighting of the loss by `1/den_i^2`. Three checks:

| key | check | reading |
|---|---|---|
| `R1_need.effective_sample_fraction` | effN of the MSE target energy under the CURRENT (global) scaler, / N | `< r1_threshold` (default 0.05) => a per-sample denominator is the only thing that can de-concentrate the loss (a per-DATASET scaler provably cannot: s5-B2) |
| `R2_signal.min_relative_residual` | `min_i \|\|r_i\|\|/\|\|y_i\|\|` and the in-band energy fraction of the smallest-scale decile | if the promoted samples are numerical roundoff (`< noise_floor`, default 1e-06; in-band fraction near the white-noise reference) the re-weighting trains on noise. A denominator FLOOR does not rescue this when the floor quantile is itself inside the noise -- reported as `floor_inside_noise` |
| `R3_metric.spearman_log_scale_vs_log_fieldnorm` | does the proposed denominator track the SCORED metric's own denominator `\|\|y_i\|\|`? | the round scores per-sample rel-L2; a normaliser uncorrelated with `\|\|y_i\|\|` moves loss weight away from what the metric measures. `kl_*` quantify it |

`verdict` is `GO` only when R1 fires AND R2 passes; `NO_GO_NO_NEED`,
`NO_GO_PROMOTES_NOISE` (the s2-B3 pfc case) and `GO_WITH_METRIC_CAVEAT`
otherwise. `--target residual|field` selects `r_i = y_i - copyLF_i` (residual
correctors, s2/s6 substrates) or `y_i` itself (field regressors, s5/s7).

COST NOTE. Pure numpy on the login node; ~10-60 s per 256^2 dataset (the
in-band probe FFTs one decile of train samples). Nothing it prints is a score.

INVOKE
------
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/persample_norm_eligibility.py \
      --datasets sharp__phase_field_crystal_2d,ext__helmholtz_2d \
      --out /path/elig.json [--target residual] [--r1_threshold 0.05]
      [--noise_floor 1e-6] [--floor_q 0.25] [--modes_cap 12]
  python tools/persample_norm_eligibility.py --datasets PANEL --out elig.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
R1DIR = HERE.parent
sys.path.insert(0, str(R1DIR / "eval"))
from panel_data import load_config, load_split, copylf_prediction  # noqa: E402


def _resolve(names: str):
    if names in ("PANEL", "GUARD"):
        cfg = load_config()
        return list(cfg["panel"] if names == "PANEL" else cfg["guard_set"])
    return [d for d in names.split(",") if d]


def _spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    d = np.sqrt((ra * ra).sum() * (rb * rb).sum())
    return float((ra * rb).sum() / d) if d > 0 else float("nan")


def _inband(field2d, cap):
    F = np.fft.rfft2(field2d)
    e = np.abs(F) ** 2
    H, W = field2d.shape
    ky = np.fft.fftfreq(H, 1.0 / H)[:, None]
    kx = np.fft.rfftfreq(W, 1.0 / W)[None, :]
    m = (np.abs(ky) < cap) & (np.abs(kx) < cap)
    return float(e[m].sum() / max(e.sum(), 1e-300)), float(m.sum() / m.size)


def _grid(n_cells):
    s = int(round(np.sqrt(n_cells)))
    return (s, s) if s * s == n_cells else None


def one(ds, target, r1_threshold, noise_floor, floor_q, cap):
    tr = load_split(ds, "train")
    hf = max(tr["field_by_fid"])
    y = np.asarray(tr["field_by_fid"][hf], dtype=np.float64)
    if y.ndim != 2:
        y = y.reshape(y.shape[0], -1)
    if target == "residual":
        lf = copylf_prediction(tr)
        if lf.shape != y.shape:
            return {"dataset": ds, "error": f"LF shape {lf.shape} != HF {y.shape}"}
        r = y - lf
    else:
        r = y
    n = y.shape[0]
    s = np.abs(r).max(axis=1)                      # the usual per-sample scale stat
    rn = np.sqrt((r ** 2).sum(axis=1))
    yn = np.sqrt((y ** 2).sum(axis=1))
    rel = rn / np.maximum(yn, 1e-300)

    e_glob = rn ** 2                                # loss weight under a global scaler
    floor = float(np.quantile(s, floor_q))
    s_fl = np.maximum(s, floor)
    e_ps = (rn / s_fl) ** 2                         # ... under per-sample + floor
    effN = lambda e: float(e.sum() ** 2 / max((e ** 2).sum(), 1e-300))
    frac_glob = effN(e_glob) / n

    # R2: are the promoted (smallest-scale) samples signal or roundoff?
    order = np.argsort(s)
    bottom = order[: max(1, n // 10)]
    g = _grid(y.shape[1])
    inband, white = (float("nan"), float("nan"))
    if g is not None:
        vals = [_inband(r[i].reshape(g), cap) for i in bottom]
        inband = float(np.median([v[0] for v in vals]))
        white = float(vals[0][1])

    w_ps = 1.0 / np.maximum(s_fl, 1e-300) ** 2
    w_gl = np.ones(n)
    w_me = 1.0 / np.maximum(yn, 1e-300) ** 2
    nrm = lambda w: w / w.sum()
    kl = lambda a, b: float((nrm(a) * np.log(nrm(a) / nrm(b))).sum())

    need = frac_glob < r1_threshold
    # PRIMARY noise test: the promoted samples' residual is at/below the fields'
    # numerical noise floor. The spectral test is only corroborating, and only
    # where the relative residual is already tiny -- a broadband residual
    # (fisher_kpp: in-band 0.14 at relative residual 2.9e-02) is real physics.
    tiny = float(rel.min()) < noise_floor
    whiteish = bool(np.isfinite(inband) and np.isfinite(white)
                    and inband < 10.0 * white and float(rel.min()) < 1e-4)
    promotes_noise = bool(tiny or whiteish)
    metric_aligned = _spearman(np.log(s + 1e-300), np.log(yn + 1e-300)) > 0.3
    reasons = []
    if not need:
        reasons.append("NO_NEED")
    if promotes_noise:
        reasons.append("PROMOTES_NOISE")
    if not metric_aligned:
        reasons.append("METRIC_MISALIGNED")
    if promotes_noise:
        verdict = "NO_GO_PROMOTES_NOISE"
    elif not need:
        verdict = "NO_GO_NO_NEED"
    elif not metric_aligned:
        verdict = "GO_WITH_METRIC_CAVEAT"
    else:
        verdict = "GO"
    return {
        "dataset": ds, "target": target, "n_train": int(n),
        "verdict": verdict, "reasons": reasons,
        "R1_need": {
            "effective_sample_fraction": frac_glob,
            "effN_global": effN(e_glob),
            "effN_persample_floored": effN(e_ps),
            "energy_share_top1": float(np.max(e_glob) / e_glob.sum()),
            "threshold": r1_threshold, "fires": bool(need),
            "note": "a per-DATASET scaler cannot change this (s5_tuning-B2)",
        },
        "R2_signal": {
            "min_relative_residual": float(rel.min()),
            "q25_relative_residual": float(np.quantile(rel, 0.25)),
            "median_relative_residual": float(np.median(rel)),
            "inband_fraction_bottom_decile": inband,
            "white_noise_reference": white,
            "scale_floor_value": floor,
            "scale_raw_min": float(s.min()),
            "floor_inside_noise": bool(floor <= 2.0 * float(s.min())),
            "noise_floor": noise_floor,
            "passes": bool(not promotes_noise),
        },
        "R3_metric": {
            "spearman_log_scale_vs_log_fieldnorm":
                _spearman(np.log(s + 1e-300), np.log(yn + 1e-300)),
            "field_norm_p90_over_p10":
                float(np.quantile(yn, .9) / max(np.quantile(yn, .1), 1e-300)),
            "kl_persample_vs_metric": kl(w_ps, w_me),
            "kl_global_vs_metric": kl(w_gl, w_me),
            "aligned": bool(metric_aligned),
        },
        "legacy_spread_statistic": {
            "scale_max_over_median": float(s.max() / max(np.median(s), 1e-300)),
            "warning": "SPREAD IS NOT THE DECIDER -- s2-B3 pfc had the panel's "
                       "largest spread (7.9e04) and NO_GO_PROMOTES_NOISE",
        },
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", required=True, help="PANEL | GUARD | comma list")
    ap.add_argument("--out", required=True)
    ap.add_argument("--target", default="residual", choices=("residual", "field"))
    ap.add_argument("--r1_threshold", type=float, default=0.05)
    ap.add_argument("--noise_floor", type=float, default=1e-6)
    ap.add_argument("--floor_q", type=float, default=0.25)
    ap.add_argument("--modes_cap", type=int, default=12)
    a = ap.parse_args()
    out = {"_args": vars(a)}
    for ds in _resolve(a.datasets):
        try:
            out[ds] = one(ds, a.target, a.r1_threshold, a.noise_floor,
                          a.floor_q, a.modes_cap)
        except Exception as exc:                                  # noqa: BLE001
            out[ds] = {"dataset": ds, "error": repr(exc)}
        r = out[ds]
        print(f"{ds[:34]:34s} {r.get('verdict', r.get('error'))!s:24s} "
              f"effFrac {r.get('R1_need', {}).get('effective_sample_fraction', float('nan')):.4f} "
              f"minRelResid {r.get('R2_signal', {}).get('min_relative_residual', float('nan')):.3e} "
              f"inband {r.get('R2_signal', {}).get('inband_fraction_bottom_decile', float('nan')):.3f}",
              flush=True)
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
