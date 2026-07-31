#!/usr/bin/env python
"""Pre-flight, per STAGE: which output-target scaler should this dataset be trained under?

No model, no GPU, train split only. For every stage of a multi-fidelity family (each
fidelity's train rows is one stage) and every candidate scaler, reports the two quantities
that decide a target scaler on this benchmark and the two that decide whether it is legal:

  F = median_i(sd_i / s_i)      PLACEMENT: where the TYPICAL sample's fluctuation sits
                               inside the network's output range under this scaler.
                               A global scaler places the AGGREGATE well and the typical
                               sample badly whenever one field sets sd(Y) or max|Y|.
  n_eff (target energy)        EQUALISATION: participation ratio of the per-sample MSE
                               energies, 1/sum_i alpha_i^2 with alpha_i = l_i/sum_j l_j
                               (formula https://alex.smola.org/posts/40-effective-sample-size/,
                               only the application is claimed). Forecasts the realized
                               epoch-1 loss concentration.
  proxy fidelity               a FOREIGN-FIDELITY per-sample statistic (max|LF_i| used to
                               scale an HF target) repairs only in proportion to its
                               correlation with the target's own scale; the tool prints the
                               repair it actually delivers against the oracle's.
  dc_energy_share              CENTERING: on a DC-dominated target, replacing a centered
                               global scaler by an UNCENTERED per-sample one costs the level
                               channel; the tool flags it.

Scalers scored: global_maxabs, global_zscore, per_sample_maxabs (the sample's own max|y_i|,
an ORACLE at test time), per_sample_zscore (RevIN as published, (y_i-mu_i)/sd_i, also an
oracle at test time), and per_sample_lf_proxy (max|LF_i|, inference-available) wherever a
row-aligned LF fidelity exists.

Read it as
----------
* `NEED` fires when the current global scaler leaves `n_eff/N` below `--need_neff_frac`:
  only a PER-SAMPLE denominator can move it (a global scalar divides every sample's energy
  by the same constant).
* Prefer the scaler with the largest F, subject to: the statistic must be computable at test
  time (per_sample_lf_proxy is; the two oracle rows are not), and train and test scalers must
  MATCH.
* `CENTERING_RISK` (dc_energy_share >= --dc_risk and the winner is an uncentered scaler) ->
  use per_sample_zscore, not per_sample_maxabs.
* `PROXY_WEAK` -> the LF statistic delivers only a fraction of the oracle's equalisation at
  this stage; do not pre-register a threshold on the oracle's number.
* Gate the whole thing on tools/dc_pattern_split.py: a LEVEL_ONLY dataset has no fluctuation
  to place and is inert under any affine scaler (s5_tuning-B2 F7).

Invoke
------
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/stage_scaler_placement_forecast.py --datasets PANEL --out forecast.json
    python tools/stage_scaler_placement_forecast.py \
        --datasets ext__helmholtz_2d,ifc_poisson --out forecast.json \
        [--split train] [--n_max 400] [--need_neff_frac 0.05] [--dc_risk 0.5]

Provenance: worktrees/s5_tuning/B3/scratchpad/reanalysis_turn_{2,2b,2c}.py; card
experiment_cards/s5_tuning/batch_3/B3.json part 6, findings F6-F9 and interpretation M3.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "eval"))
import nrmse as NR              # noqa: E402  (round metric definition hash)
import panel_data               # noqa: E402

FLOOR = 1e-8


def _n_eff(l: np.ndarray) -> float:
    l = np.asarray(l, dtype=np.float64)
    s = l.sum()
    if s <= 0:
        return float("nan")
    a = l / s
    return float(1.0 / np.sum(a ** 2))


def _stage_report(Y: np.ndarray, s_lf: np.ndarray | None) -> dict:
    Y = np.asarray(Y, dtype=np.float64)
    n, ncell = Y.shape
    sd_i = Y.std(axis=1)
    max_i = np.abs(Y).max(axis=1)
    mu_i = Y.mean(axis=1)
    sd_g = max(float(Y.std()), FLOOR)
    max_g = max(float(np.abs(Y).max()), FLOOR)

    cand = {
        "global_maxabs": (np.full(n, max_g), False, True),
        "global_zscore": (np.full(n, sd_g), True, True),
        "per_sample_maxabs": (np.maximum(max_i, FLOOR), False, False),
        "per_sample_zscore": (np.maximum(sd_i, FLOOR), True, False),
    }
    if s_lf is not None:
        cand["per_sample_lf_proxy"] = (np.maximum(np.asarray(s_lf, np.float64), FLOOR),
                                       False, True)

    e_l2 = np.linalg.norm(Y, axis=1)
    out = {"n_rows": int(n), "n_cells": int(ncell),
           "dc_energy_share": float((mu_i ** 2).sum() * ncell / (Y ** 2).sum()),
           "cross_sample_energy_cv": float(e_l2.std() / e_l2.mean()),
           "scale_max_over_median_true": float(max_i.max() / np.median(max_i)),
           "scalers": {}}
    for name, (s, centered, legal_at_test) in cand.items():
        Yn = (Y - mu_i[:, None]) / s[:, None] if (centered and name.startswith("per_sample")) \
            else ((Y - Y.mean()) / s[:, None] if centered else Y / s[:, None])
        energy = (Yn ** 2).mean(axis=1)
        out["scalers"][name] = {
            "F_typical_placement": float(np.median(sd_i / s)),
            "n_eff_target_energy": _n_eff(energy),
            "n_eff_fraction": _n_eff(energy) / n,
            "top1_energy_share": float(energy.max() / energy.sum()),
            "energy_cv_after_scaling": float((e_l2 / s).std() / (e_l2 / s).mean()),
            "centered": bool(centered),
            "test_time_available": bool(legal_at_test),
        }
    if s_lf is not None:
        s_lf = np.maximum(np.asarray(s_lf, np.float64), FLOOR)
        orc = out["scalers"]["per_sample_maxabs"]["n_eff_target_energy"]
        base = out["scalers"]["global_zscore"]["n_eff_target_energy"]
        prox = out["scalers"]["per_sample_lf_proxy"]["n_eff_target_energy"]
        out["proxy_fidelity"] = {
            "corr_log_proxy_vs_log_true_scale":
                float(np.corrcoef(np.log(s_lf), np.log(np.maximum(max_i, FLOOR)))[0, 1]),
            "equalisation_delivered_vs_oracle":
                float((prox - base) / (orc - base)) if orc > base else None,
            "note": "1.0 == the proxy is the target's own statistic (true at the stage whose "
                    "target IS the LF field); << 1 == a weak cross-fidelity proxy.",
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", required=True,
                    help="comma-separated names, or PANEL for project.yaml's panel")
    ap.add_argument("--out", required=True)
    ap.add_argument("--split", default="train")
    ap.add_argument("--n_max", type=int, default=400)
    ap.add_argument("--need_neff_frac", type=float, default=0.05)
    ap.add_argument("--dc_risk", type=float, default=0.5)
    a = ap.parse_args()

    names = (panel_data.load_config()["panel"] if a.datasets.strip() == "PANEL"
             else [s for s in a.datasets.split(",") if s])
    res = {"nrmse_def_hash": NR.NRMSE_DEF_HASH, "split": a.split,
           "need_neff_frac": a.need_neff_frac, "dc_risk": a.dc_risk, "datasets": {}}

    for ds in names:
        try:
            d = panel_data.load_split(ds, a.split)
        except Exception as e:                                   # noqa: BLE001
            res["datasets"][ds] = {"error": f"{type(e).__name__}: {e}"}
            continue
        fids = sorted(d["field_by_fid"].keys())
        lf_top = max(d["lf_fids"]) if d["lf_fids"] else None
        entry = {"hf_fid": d["hf_fid"], "lf_fids": d["lf_fids"], "stages": {}}
        for fid in fids:
            Y = np.asarray(d["field_by_fid"][fid], dtype=np.float64)[:a.n_max]
            stage = "HF_finetune" if fid == d["hf_fid"] else f"stage_fid{fid}"
            if lf_top is not None and fid == min(d["lf_fids"]):
                stage = "LF_pretrain"
            s_lf = None
            if lf_top is not None:
                LF = np.asarray(d["field_by_fid"][lf_top], dtype=np.float64)
                if LF.shape[0] >= Y.shape[0]:
                    s_lf = np.abs(LF[:Y.shape[0]]).max(axis=1)
            r = _stage_report(Y, s_lf)
            sc = r["scalers"]
            need = sc["global_zscore"]["n_eff_fraction"] < a.need_neff_frac
            legal = {k: v for k, v in sc.items() if v["test_time_available"]}
            best_legal = max(legal, key=lambda k: legal[k]["F_typical_placement"])
            best_any = max(sc, key=lambda k: sc[k]["F_typical_placement"])
            flags = []
            if need:
                flags.append("NEED_PER_SAMPLE")
            if (r["dc_energy_share"] >= a.dc_risk and not sc[best_any]["centered"]):
                flags.append("CENTERING_RISK")
            pf = r.get("proxy_fidelity", {}).get("equalisation_delivered_vs_oracle")
            if pf is not None and pf < 0.5:
                flags.append("PROXY_WEAK")
            r["verdict"] = {
                "best_F_any_scaler": best_any,
                "best_F_test_time_legal_scaler": best_legal,
                "F_gain_best_legal_over_global_zscore":
                    sc[best_legal]["F_typical_placement"] / sc["global_zscore"]["F_typical_placement"],
                "flags": flags,
            }
            entry["stages"][f"{stage}__fid{fid}"] = r
        res["datasets"][ds] = entry

    pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
    for ds, e in res["datasets"].items():
        if "error" in e:
            print(f"{ds}: {e['error']}")
            continue
        for st, r in e["stages"].items():
            v = r["verdict"]
            print(f"{ds:28s} {st:22s} F(zscore)={r['scalers']['global_zscore']['F_typical_placement']:.4f} "
                  f"best_legal={v['best_F_test_time_legal_scaler']:20s} "
                  f"gain={v['F_gain_best_legal_over_global_zscore']:8.3f} "
                  f"n_eff/N={r['scalers']['global_zscore']['n_eff_fraction']:.4f} "
                  f"{','.join(v['flags'])}")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
