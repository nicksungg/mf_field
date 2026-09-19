"""Post-process saved sample HDF5s into a sharpness screen_report.json (+ printed summary).

Run where the sample data lives (the box):
    python scripts/screen_samples.py --sample-dir data/sample --k-cs 12 16 20 24
"""
from __future__ import annotations
import argparse, glob, json, os
import numpy as np
from mffp_sharp.common import io, screen

def _hf_fields(d):
    hf = d["hf_res"]
    return [b["aligned"][hf] for b in d["bundles"]], hf

def _mean_curve(fields, k_cs):
    curves = [screen.cumulative_curve(f, k_cs) for f in fields]
    return {kc: float(np.mean([c[kc] for c in curves])) for kc in [int(x) for x in k_cs]}

def build_report(sample_dir, k_cs=(12, 16, 20, 24)):
    paths = sorted(glob.glob(os.path.join(sample_dir, "*_sample.h5")))
    data = {os.path.basename(p).replace("_sample.h5", ""): io.read_dataset(p) for p in paths}
    # dimension-matched KS anchors + Euler anchor
    curves, ndims = {}, {}
    for name, d in data.items():
        fields, _ = _hf_fields(d)
        curves[name] = _mean_curve(fields, k_cs)
        ndims[name] = d["ndim"]
    ks_anchor = {nd: next((curves[n] for n in curves
                           if "kuramoto" in n and ndims[n] == nd), None)
                 for nd in set(ndims.values())}
    euler_curve = next((curves[n] for n in curves if "euler" in n), None)
    report = {}
    for name, d in data.items():
        fields, hf = _hf_fields(d)
        ksc = ks_anchor.get(ndims[name])
        row = {"ndim": ndims[name], "f_curve": curves[name]}
        for kc in [int(x) for x in k_cs]:
            f_cand = curves[name][kc]
            f_ks = ksc[kc] if ksc else None
            f_eu = euler_curve[kc] if euler_curve else None
            row.setdefault("floor_pass", {})[kc] = (
                None if f_ks is None else bool(f_cand >= f_ks))
            row.setdefault("s", {})[kc] = (
                None if (f_ks is None or f_eu is None)
                else screen.sharpness_coordinate(f_cand, f_ks, f_eu))
        # mean LF-HF gap at the smallest cutoff (coarsest LF vs HF)
        res = d["resolutions"]; res_min = min(res)
        gaps = [screen.lf_hf_gap(b["aligned"][res_min], b["aligned"][hf], int(k_cs[0]))
                for b in d["bundles"]]
        row["lf_hf_gap"] = float(np.mean(gaps))
        report[name] = row
    return report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-dir", required=True)
    ap.add_argument("--k-cs", type=int, nargs="+", default=[12, 16, 20, 24])
    args = ap.parse_args()
    report = build_report(args.sample_dir, args.k_cs)
    out = os.path.join(args.sample_dir, "screen_report.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"wrote {out}\n")
    for name, row in report.items():
        kc0 = args.k_cs[1] if len(args.k_cs) > 1 else args.k_cs[0]
        fp = row["floor_pass"].get(kc0)
        s = row["s"].get(kc0)
        tag = "PASS" if fp else ("FAIL-floor" if fp is False else "??")
        print(f"  {name:28} floor@{kc0}={tag:11} "
              f"s={'n/a' if s is None else round(s,3)}  lf_hf_gap={row['lf_hf_gap']:.3g}")

if __name__ == "__main__":
    main()
