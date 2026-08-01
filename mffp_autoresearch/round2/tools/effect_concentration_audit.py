"""ROUND-2: is a paired A-vs-B effect BROAD-BASED or carried by a handful of test
samples, and how much of it survives perfect per-sample amplitude calibration?

Provenance: r2s3_lf_train_signal-B4 mechanism turns 2-3
(`scratchpad/reanalysis_turn_{2,3}.py`). Complements
`tools/effect_threshold_readings.py`, which asks whether a DRAW/SPLIT-level
effect is claimable; this tool asks the orthogonal question about the SAMPLE
axis, and is usable when there is only one split.

WHY THIS EXISTS
---------------
A dataset-level effect in skill units is a MEAN over per-sample relative errors.
On r2s3-B4 that mean hid two very different situations:

  * `sharp__cahn_hilliard`: the MEDIAN per-sample effect (131-181 x mce) exceeded
    the mean (113-125 x mce), 24-30 of 100 samples were needed to reach half the
    effect, and a 10 % adversarial trim left 95-114 x mce. Broad-based.
  * `ifc_poisson`: 1.41 x mce, but only 56 % of samples improved (sign-test
    p = 0.185), the top 10 % held 53 % of the positive effect, and deleting the
    6 most favourable of 128 samples took it BELOW its own certified mce.

Both passed the card's primary reading. Only one is a typical-sample claim.

WHAT IT MEASURES
----------------
  effect        E = mean_i d_i with d_i = (rel_i(baseline) - rel_i(treatment))/denom,
                so mean_i d_i is EXACTLY the skill-unit effect; plus E/mce, the
                median per-sample effect, the win rate and an EXACT two-sided
                binomial sign test
  concentration share of the total POSITIVE effect held by the top 1 / 5 % / 10 %
                of samples, and the number of samples needed to reach half of E
  trim          E recomputed after DELETING the most favourable --trims percent
                of samples: the adversarial robustness reading. Still above mce
                after trimming == broad-based; collapsing == tail-borne
  amplitude_vs_structure
                E_struct = the effect surviving perfect per-sample amplitude
                calibration on BOTH arms (rel^struct_i = sqrt(1-cos_i^2), the
                error no gain can touch), E_amp = E - E_struct, and the per-arm
                cosine / norm-ratio / across-sample-fluctuation anatomy that says
                WHY. An effect whose E_struct falls below mce was an amplitude
                effect all along.
  verdict       see the table at the bottom of this docstring.

Scoring is `<eval_dir>/nrmse.py` per sample (its mean is `nrmse.nrmse`, asserted).
`--denominator` / `--floors_json` give skill units; `--mce` / `--noise_floor_json`
give the certified minimum claimable effect that the trim readings are judged
against. Both are optional; without them the tool reports raw nRMSE-unit numbers.

INVOCATION
----------
  python tools/effect_concentration_audit.py \
      --baseline control_preds.npz --treatment treatment_preds.npz \
      --dataset sharp__cahn_hilliard \
      --floors_json state/anchors/floors.json \
      --noise_floor_json state/noise_floor.json \
      --out /tmp/effect_audit.json

VERDICTS
--------
  NEGATIVE_EFFECT        E <= 0
  NOT_SIGN_SIGNIFICANT   sign-test p > --alpha: the median sample is not helped
  TAIL_BORNE             the top 10 % of samples hold >= --tail_share of the
                         positive effect, or the --trims trim drops E below mce
  BROAD_BASED            neither of the above and E > mce
  AMPLITUDE_ONLY         E_struct < mce (needs --mce): both arms amplitude-
                         calibrated, the effect is gone

RUNTIME / CAVEATS
-----------------
* Cheap: seconds of arithmetic; cost is the panel loader (~15-30 s per dataset).
  Use `--targets_npz` when you already have targets on disk.
* `--dataset` loads through `panel_data.load_split`, which materialises every
  fidelity; the HF field is copied out and the split dropped immediately. This is
  NOT the structural LF-poisoning of r2s3-B4's `lf_guard.py` -- use that when you
  need an auditable no-LF claim.
* The sign test is on the paired per-sample sign only; it says nothing about
  magnitude and is deliberately weaker than the card's paired bootstrap. Report
  both -- on ifc they disagree, and that disagreement IS the finding.
* `E_struct` is a MECHANISM decomposition of an arm-vs-arm contrast, not a gated
  claim: it is not priced against any LF-free control class.
* The two arms must be scored on the same test split in the same row order; the
  tool checks shapes but cannot check provenance.
"""
from __future__ import annotations

import argparse
import json
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_EVAL = HERE.parent / "eval"


def rel_l2_per_sample(P, Y):
    P, Y = np.asarray(P, float), np.asarray(Y, float)
    if P.shape != Y.shape or P.ndim != 2:
        raise SystemExit(f"shape mismatch or not 2-D: {P.shape} vs {Y.shape}")
    if not (np.isfinite(P).all() and np.isfinite(Y).all()):
        raise SystemExit("non-finite values")
    den = np.linalg.norm(Y, axis=1)
    if (den == 0).any():
        raise SystemExit("zero-norm target sample (eval/nrmse.py refuses these)")
    return np.linalg.norm(P - Y, axis=1) / den


def sign_test_p(k, n):
    if n == 0:
        return float("nan")
    k = min(k, n - k)
    return float(min(1.0, 2.0 * sum(comb(n, j) for j in range(k + 1)) / 2.0 ** n))


def arm_anatomy(P, Y):
    a, b, c = (P * P).sum(1), (P * Y).sum(1), (Y * Y).sum(1)
    cos = b / np.sqrt(np.maximum(a * c, 1e-300))
    Pc, Yc = P - P.mean(0, keepdims=True), Y - Y.mean(0, keepdims=True)
    return {
        "cos_mean": float(cos.mean()), "cos_median": float(np.median(cos)),
        "cos_p10": float(np.percentile(cos, 10)),
        "frac_cos_below_0.3": float(np.mean(cos < 0.3)),
        "norm_ratio_median": float(np.median(np.sqrt(a) / np.sqrt(c))),
        "norm_ratio_p90": float(np.percentile(np.sqrt(a) / np.sqrt(c), 90)),
        "across_sample_fluctuation_ratio": float(
            np.linalg.norm(Pc) / max(np.linalg.norm(Yc), 1e-300)),
    }, np.sqrt(np.maximum(1.0 - cos ** 2, 0.0))


def load_targets(a):
    if a.targets_npz:
        Y = np.asarray(np.load(a.targets_npz)[a.targets_key], float)
        return Y.reshape(Y.shape[0], -1), {"source": a.targets_npz}
    if not a.dataset:
        raise SystemExit("need --dataset (panel loader) or --targets_npz")
    sys.path.insert(0, str(Path(a.eval_dir).resolve()))
    import panel_data
    split = panel_data.load_split(a.dataset, a.split)
    hf = int(split["hf_fid"])
    Y = np.array(split["field_by_fid"][hf], dtype=np.float64)
    Y = Y.reshape(Y.shape[0], -1)
    meta = {"source": f"panel_data.load_split({a.dataset!r}, {a.split!r})", "hf_fid": hf,
            "panel_data_file": str(Path(panel_data.__file__).resolve())}
    del split
    return Y, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--baseline", required=True, help="control arm *_preds.npz")
    ap.add_argument("--treatment", required=True, help="treatment arm *_preds.npz")
    ap.add_argument("--key_pred", default="pred_test")
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--split", default="test")
    ap.add_argument("--targets_npz", default=None)
    ap.add_argument("--targets_key", default="y")
    ap.add_argument("--eval_dir", default=str(DEFAULT_EVAL))
    ap.add_argument("--denominator", type=float, default=None)
    ap.add_argument("--floors_json", default=None)
    ap.add_argument("--mce", type=float, default=None)
    ap.add_argument("--noise_floor_json", default=None)
    ap.add_argument("--trims", default="5,10", help="percent of most favourable samples to delete")
    ap.add_argument("--tail_share", type=float, default=0.40)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--top_k", type=int, default=10)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    sys.path.insert(0, str(Path(a.eval_dir).resolve()))
    import nrmse as NR

    denom = a.denominator
    if denom is None and a.floors_json:
        fl = json.loads(Path(a.floors_json).read_text())
        if not a.dataset or a.dataset not in fl:
            raise SystemExit(f"--floors_json needs a --dataset present in {a.floors_json}")
        denom = float(fl[a.dataset]["reference"]["test_nrmse"])
    denom = 1.0 if denom is None else float(denom)
    mce = a.mce
    if mce is None and a.noise_floor_json:
        nf = json.loads(Path(a.noise_floor_json).read_text())
        if not a.dataset or a.dataset not in nf:
            raise SystemExit(f"--noise_floor_json needs a --dataset present in {a.noise_floor_json}")
        mce = float(nf[a.dataset]["min_claimable_effect"])

    P0 = np.asarray(np.load(a.baseline)[a.key_pred], float)
    P1 = np.asarray(np.load(a.treatment)[a.key_pred], float)
    Y, tmeta = load_targets(a)
    if P0.shape != P1.shape:
        raise SystemExit(f"arms disagree: {P0.shape} vs {P1.shape}")

    r0, r1 = rel_l2_per_sample(P0, Y), rel_l2_per_sample(P1, Y)
    for r, P in ((r0, P0), (r1, P1)):
        if abs(float(r.mean()) - NR.nrmse(P, Y)) >= 1e-12:
            raise SystemExit("per-sample metric disagrees with eval/nrmse.py")
    d = (r0 - r1) / denom
    n = int(d.size)
    order = np.argsort(-d)
    pos, tot = d[d > 0].sum(), d.sum()
    unit = mce if mce else 1.0

    def share(k):
        # concentration is only interpretable for an effect that exists; a
        # negative or all-negative effect gets NaN rather than a ratio that
        # LOOKS like a share but is not one.
        if pos <= 0 or tot <= 0:
            return float("nan")
        return float(d[order[:max(1, k)]].sum() / pos)

    an0, s0 = arm_anatomy(P0, Y)
    an1, s1 = arm_anatomy(P1, Y)
    E, E_struct = float(d.mean()), float((s0 - s1).mean()) / denom

    trims = {}
    for t in [float(x) for x in a.trims.split(",")]:
        k = max(1, int(np.ceil(t / 100.0 * n)))
        trims[f"top{t:g}pct"] = {"n_deleted": k, "E": float(d[order[k:]].mean()),
                                 "E_over_mce": float(d[order[k:]].mean() / unit)}

    out = {
        "_tool": "effect_concentration_audit.py",
        "_provenance_card": "r2s3_lf_train_signal-B4 turns 2-3",
        "inputs": {"baseline": a.baseline, "treatment": a.treatment,
                   "targets": tmeta, "denominator": denom, "mce": mce,
                   "n_test": n, "mce_units": bool(mce)},
        "effect": {
            "E": E, "E_over_mce": float(E / unit),
            "median_per_sample": float(np.median(d)),
            "median_over_mce": float(np.median(d) / unit),
            "win_rate": float(np.mean(d > 0)),
            "sign_test_p": sign_test_p(int((d > 0).sum()), n)},
        "concentration": {
            "share_of_positive_top1": share(1),
            "share_of_positive_top5pct": share(int(np.ceil(0.05 * n))),
            "share_of_positive_top10pct": share(int(np.ceil(0.10 * n))),
            "n_samples_to_halve_E": int(np.searchsorted(np.cumsum(d[order]), 0.5 * tot) + 1)
            if tot > 0 else -1,
            f"top{a.top_k}_idx": [int(i) for i in order[:a.top_k]]},
        "trim": trims,
        "amplitude_vs_structure": {
            "E_raw": E, "E_struct": E_struct, "E_amp": E - E_struct,
            "amplitude_share": (E - E_struct) / E if E else float("nan"),
            "E_struct_over_mce": float(E_struct / unit),
            "skill_struct_only_baseline": float(s0.mean()) / denom,
            "skill_struct_only_treatment": float(s1.mean()) / denom,
            "_note": ("mechanism decomposition of an arm-vs-arm contrast; NOT "
                      "priced against any LF-free control class")},
        "arm_anatomy": {"baseline": an0, "treatment": an1},
    }

    v = []
    if E <= 0:
        v.append("NEGATIVE_EFFECT")
    if out["effect"]["sign_test_p"] > a.alpha:
        v.append("NOT_SIGN_SIGNIFICANT")
    tail = (out["concentration"]["share_of_positive_top10pct"] >= a.tail_share
            or (mce and any(t["E_over_mce"] < 1.0 for t in trims.values()) and E > 0))
    if E > 0 and tail:
        v.append("TAIL_BORNE")
    if E > 0 and not tail and "NOT_SIGN_SIGNIFICANT" not in v and (not mce or E > mce):
        v.append("BROAD_BASED")
    if mce and E > 0 and E_struct < mce:
        v.append("AMPLITUDE_ONLY")
    out["verdict"] = v

    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps({"verdict": v, **out["effect"],
                      "top10pct_share": out["concentration"]["share_of_positive_top10pct"],
                      "trim": {k: t["E_over_mce"] for k, t in trims.items()},
                      "amplitude_share": out["amplitude_vs_structure"]["amplitude_share"],
                      "E_struct_over_mce": out["amplitude_vs_structure"]["E_struct_over_mce"]},
                     indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
