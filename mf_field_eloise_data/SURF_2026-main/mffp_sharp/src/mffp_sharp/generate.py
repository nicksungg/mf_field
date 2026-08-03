"""Sample-round generator CLI.

For each PDE: draw condition vectors, solve across the fidelity ladder, align to
the HF grid, write an HDF5 dataset, and emit a LF-vs-HF metric summary (the
bottom-rung check: is LF measurably blurrier than HF?).

Usage (on Nicholas's box, per the compute policy):
    python -m mffp_sharp.generate --config configs/sample.yaml --pde all
    python -m mffp_sharp.generate --config configs/sample.yaml --pde euler

Edit code locally; RUN here:  ssh eloise@10.80.6.224
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
import yaml

from .common import completeness, ladder, io, metrics, visualize
from .pdes import euler, cahn_hilliard, kuramoto_sivashinsky, allen_cahn, fisher_kpp, swift_hohenberg, kdv, nls, sine_gordon, gray_scott, phase_field_crystal, burgers, sod, shallow_water, helmholtz, porous_medium

_MODULES = {
    "euler": euler,
    "cahn_hilliard": cahn_hilliard,
    "kuramoto_sivashinsky": kuramoto_sivashinsky,
    "allen_cahn": allen_cahn,
    "fisher_kpp": fisher_kpp,
    "swift_hohenberg": swift_hohenberg,
    "kdv": kdv,
    "nls": nls,
    "sine_gordon": sine_gordon,
    "gray_scott": gray_scott,
    "phase_field_crystal": phase_field_crystal,
    "burgers": burgers,
    "sod": sod,
    "shallow_water": shallow_water,
    "helmholtz": helmholtz,
    "porous_medium": porous_medium,
}


def generate_dataset(name: str, block: dict, top: dict) -> dict:
    """Generate one dataset's sample batch; return a metric summary for review.

    `name` is the dataset name (output filename + figure label). `block` is its
    config: {module, ndim, output_time, sampling}.
    """
    mod = _MODULES[block["module"]]
    resolutions = top["ladder"]["resolutions"]
    hf_res = resolutions[top["ladder"]["hf_index"]]
    n = top["n_samples_per_pde"]
    seed = top["seed"]
    T = block["output_time"]
    ndim = int(block.get("ndim", 2))

    specs = mod.sample_configs(n, block["sampling"], ndim, seed)
    samples, conds, names = [], [], None
    hf_raw = []
    per_lf_metrics = {res: [] for res in resolutions if res != hf_res}

    for i, spec in enumerate(specs):
        raw, cond, names = mod.generate_sample(spec, resolutions, hf_res, T)
        bundle = ladder.assemble_sample(raw, hf_res)
        samples.append(bundle)
        conds.append(cond)
        hf_raw.append(np.asarray(raw[hf_res], dtype=np.float64).ravel())
        hf = bundle["aligned"][hf_res]
        for res in per_lf_metrics:
            per_lf_metrics[res].append(
                metrics.evaluate(bundle["aligned"][res], hf, top["metrics"]))
        print(f"  [{name}] sample {i+1}/{n} done", flush=True)

    # Completeness gate (ADR r2-0003): the condition vector must determine the field,
    # verified against the just-generated arrays, unless the block declares itself a
    # deliberate stochastic map.
    const = {k: v for k, v in block["sampling"].items() if not k.endswith("_range")}
    const["ndim"] = ndim
    try:
        cc = completeness.certify(mod, np.array(conds), np.stack(hf_raw), names, const,
                                  resolutions, hf_res, T,
                                  declared_stochastic=bool(block.get("stochastic_map")))
    except completeness.CompletenessError as e:
        raise SystemExit(f"[{name}] condition_completeness INCOMPLETE — {e}")
    print(f"  [{name}] condition_completeness: {cc['verdict']}", flush=True)

    os.makedirs(top["out_dir"], exist_ok=True)
    out_path = os.path.join(top["out_dir"], f"{name}_sample.h5")
    io.write_dataset(out_path, name, samples, np.array(conds), names,
                     resolutions, hf_res, T, seed)

    n_figs = min(int(top.get("n_figures", 3)), n)
    if n_figs > 0:
        fig_dir = os.path.join(top["out_dir"], "figures")
        os.makedirs(fig_dir, exist_ok=True)
        for i in range(n_figs):
            try:
                visualize.one_pager(samples[i], resolutions, hf_res, top["metrics"],
                                    block["module"], i,
                                    os.path.join(fig_dir, f"{name}_sample{i}.png"),
                                    condition=conds[i], condition_names=names)
            except Exception as e:
                print(f"  [{name}] figure {i} failed: {e}", flush=True)

    summary = {"pde": name, "out_path": out_path, "hf_res": hf_res, "n": n,
               "condition_completeness": cc,
               "lf_vs_hf": {res: {m: float(np.mean([d[m] for d in rows]))
                                  for m in top["metrics"]}
                            for res, rows in per_lf_metrics.items()}}
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--pde", default="all")
    args = ap.parse_args()
    with open(args.config) as f:
        top = yaml.safe_load(f)
    names = list(top["pdes"]) if args.pde == "all" else [args.pde]
    unknown = [nm for nm in names if nm not in top["pdes"]]
    if unknown:
        raise SystemExit(f"unknown pde(s) {unknown}; choices: {list(top['pdes'])}")
    summaries = []
    for name in names:
        print(f"=== generating {name} ===", flush=True)
        summaries.append(generate_dataset(name, top["pdes"][name], top))
    sum_path = os.path.join(top["out_dir"], "sample_summary.json")
    with open(sum_path, "w") as f:
        json.dump(summaries, f, indent=2)
    print(f"\nwrote {sum_path}")
    for s in summaries:
        print(f"  {s['pde']}:")
        for res, m in s["lf_vs_hf"].items():
            parts = [f"{key}={m[key]:.4f}" for key in ("rel_l2", "linf", "spectral_band")
                     if m.get(key) is not None]
            print(f"    res {res:>3} vs HF: " + "  ".join(parts))


if __name__ == "__main__":
    main()
