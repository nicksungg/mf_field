#!/usr/bin/env python
"""Routing headroom — price a richer gate BEFORE building a router.

Provenance: s4_hybrid_routing-B1 mechanism analysis, turn 3
(`worktrees/s4_hybrid_routing/B1/scratchpad/routing_headroom.py`, finding F11 in
card `experiment_cards/s4_hybrid_routing/batch_1/B1.json` part 6).

What it measures
----------------
Any model of the form `pred = base + alpha * correction` (residual hybrid,
test-time corrector, boosting stage, two-expert mixture) can in principle have
its scalar `alpha` replaced by something richer: a per-SAMPLE gate, or a
spatially-resolved per-PIXEL gate (the shape "LF-conditioned routing" cards
propose to learn). This tool computes the ceiling of each, from a saved
`(base, correction, target)` triple, with the round's own metric
(`round1/eval/nrmse.py`) and the round's own test target
(`round1/eval/panel_data.py`):

  G0  alpha = 0                                   base only
  G1  alpha = the value the model actually applied
  G2  alpha = the GLOBAL ORACLE scalar            fitted on this test set
  G3  alpha_i = PER-SAMPLE ORACLE scalars         sample-level routing ceiling
  G4  alpha(x) = per-PIXEL alpha FIELD fitted on one half of the test split and
      scored on the other, both directions        honest spatial-routing estimate
  G5  the same pixel field fitted in-sample       spatial-routing upper bound

G2, G3 and G5 use the test labels and are ORACLES: no trainable router can beat
them. So `G3 - G2` bounds what per-sample routing can buy, and `G4 - G2` /
`G5 - G2` bracket what spatially-resolved routing can buy.

Reading the output
------------------
Compare `gains_pct_vs_G2` against the dataset's `min_claimable_effect`
(`state/noise_floor.json`, 10% relative on the round-1 sharp panel):

* all rungs within the floor  ->  the routing card is NOT licensed; a single
  scalar is all the gate structure this artifact supports, and the lever is
  elsewhere (what the correction *contains*, not how it is mixed in).
* `G3` far below `G2`  ->  per-sample routing has room; look at
  `per_sample_alpha_oracle_stats.cv` for how much the optimal mix really varies.
* `G4` WORSE than `G2` (positive gain) -> a pixel-wise gate cannot even be
  estimated at this N_test; treat `G5` as fantasy.

Invocation
----------
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/routing_headroom.py --dataset sharp__cahn_hilliard \
      --npz /path/to/fields.npz --base_key base_te --corr_key corr_te \
      --corr_scale 2.207066297531128 --alpha 0.0 \
      --out /path/to/routing.json

`--npz` holds two `(N, n_cells_hf)` arrays on the HF grid (base prediction, raw
correction). `--corr_scale` multiplies the correction (for families that store it
in scaler units); `--alpha` is the gate the model actually applied. Fewer rows
than the test split is fine -- the first N test samples are used.

Cost: pure numpy, seconds. No GPU, no SLURM, no training.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _round_root() -> Path:
    here = Path(__file__).resolve()
    for anc in here.parents:
        if (anc / "eval" / "nrmse.py").exists() and (anc / "tools").exists():
            return anc
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True, cwd=here.parent)
    return Path(out.stdout.strip()) / "mffp_autoresearch" / "round1"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--npz", required=True)
    ap.add_argument("--base_key", default="base_te")
    ap.add_argument("--corr_key", default="corr_te")
    ap.add_argument("--corr_scale", type=float, default=1.0)
    ap.add_argument("--alpha", type=float, required=True)
    ap.add_argument("--round_root", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rr = Path(args.round_root).resolve() if args.round_root else _round_root()
    sys.path.insert(0, str(rr / "eval"))
    from nrmse import nrmse, NRMSE_DEF_HASH  # noqa
    import panel_data as PD  # noqa

    z = np.load(args.npz)
    base = np.asarray(z[args.base_key], dtype=np.float64)
    corr = np.asarray(z[args.corr_key], dtype=np.float64) * args.corr_scale
    if corr.shape != base.shape:
        raise ValueError(f"base {base.shape} and correction {corr.shape} disagree")
    n = base.shape[0]
    te = PD.load_split(args.dataset, "test")
    tgt = np.asarray(te["field_by_fid"][te["hf_fid"]], dtype=np.float64)[:n]
    if tgt.shape != base.shape:
        raise ValueError(f"fields {base.shape} vs HF test target {tgt.shape}")
    resid = tgt - base
    a_ck = args.alpha

    rec = {"dataset": args.dataset, "n_test_used": int(n), "alpha_applied": a_ck,
           "npz": str(args.npz), "corr_scale": args.corr_scale,
           "nrmse_def_hash": NRMSE_DEF_HASH, "rungs": {}}

    def put(name, pred, note):
        rec["rungs"][name] = {"nrmse": nrmse(pred, tgt), "note": note}

    put("G0_alpha0", base, "base only")
    put("G1_alpha_applied", base + a_ck * corr, f"the gate the model applied ({a_ck:.6f})")
    a_glob = float((resid * corr).sum() / max((corr * corr).sum(), 1e-300))
    put("G2_alpha_global_oracle", base + a_glob * corr, f"global ORACLE scalar {a_glob:.6f}")
    a_ps = ((resid * corr).sum(1) / np.maximum((corr * corr).sum(1), 1e-300))[:, None]
    put("G3_alpha_per_sample_oracle", base + a_ps * corr,
        "per-sample ORACLE scalars (sample-level routing ceiling)")

    half = n // 2
    if half >= 1:
        preds = np.zeros_like(base)
        for fit, ev in ((np.arange(half), np.arange(half, n)),
                        (np.arange(half, n), np.arange(half))):
            num = (resid[fit] * corr[fit]).sum(0)
            den = (corr[fit] * corr[fit]).sum(0)
            af = np.where(den > 1e-300, num / np.maximum(den, 1e-300), 0.0)
            preds[ev] = base[ev] + af[None, :] * corr[ev]
        put("G4_alpha_field_splithalf", preds,
            "per-pixel alpha field fitted on the other half of the test split")
    num, den = (resid * corr).sum(0), (corr * corr).sum(0)
    af_all = np.where(den > 1e-300, num / np.maximum(den, 1e-300), 0.0)
    put("G5_alpha_field_insample", base + af_all[None, :] * corr,
        "per-pixel alpha field fitted on the SAME samples (upper bound)")

    r = rec["rungs"]
    g2 = r["G2_alpha_global_oracle"]["nrmse"]
    rec["gains_pct_vs_G2"] = {k: 100.0 * (r[k]["nrmse"] / g2 - 1.0) for k in r}
    rec["per_sample_alpha_oracle_stats"] = {
        "mean": float(a_ps.mean()), "std": float(a_ps.std()),
        "cv": float(a_ps.std() / max(abs(a_ps.mean()), 1e-300)),
        "min": float(a_ps.min()), "max": float(a_ps.max()),
        "p10": float(np.percentile(a_ps, 10)), "p90": float(np.percentile(a_ps, 90))}
    rec["alpha_field_stats"] = {
        "mean": float(af_all.mean()), "std": float(af_all.std()),
        "p10": float(np.percentile(af_all, 10)), "p90": float(np.percentile(af_all, 90)),
        "frac_pixels_negative": float((af_all < 0).mean())}
    rec["per_sample_alpha_oracle"] = a_ps.reshape(-1).tolist()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(rec, f, indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k != "per_sample_alpha_oracle"}, indent=1))


if __name__ == "__main__":
    main()
