#!/usr/bin/env python
"""registration_skill_split.py -- how much of a model's beyond-copy win is REGISTRATION?

Promoted from `worktrees/s2_beyond_copy/B2/scratchpad/reanalysis_turn_1.py`; provenance
card `experiment_cards/s2_beyond_copy/batch_2/B2.json` part 6, findings F1-F3, F12.

WHY THIS EXISTS
---------------
`tools/registration_audit.py` (s3_warp-B1) showed the round's skill DENOMINATOR is
misregistered by `(r-1)/2` HF cells on the sharp panel: `eval/panel_data.py::
copylf_prediction` upsamples with the CELL-CENTRED convention while the solvers store
NODE samples. A zero-parameter re-sampling of the same LF field removes 54-100 % of
copy-LF's error there. Any card that reports `skill < 1` on those datasets is therefore
reporting a number whose denominator is part artifact, and the first question a
mechanism analyst must answer is:

    is this model beating copy-LF, or beating a resampling convention?

This tool answers it for ANY predictor, in one call, without touching the eval layer:
it rebuilds `registration_audit`'s zero-parameter variants (A eval-copy-LF / A2 wrap /
B constant shift / C node-aligned bilinear / D node-aligned band-limited / E Dirichlet
node-aligned) per sample, and re-expresses the predictor's score against the corrected
denominator.

WHAT IT REPORTS (per dataset)
-----------------------------
| key | meaning |
|---|---|
| `variant_skill_vs_copylf` | what each zero-parameter fix scores (the free win) |
| `pct_copylf_error_removed_best_fix` | how much of copy-LF's error is REGISTRATION |
| `pct_copylf_error_removed_model` | how much the trained predictor removed |
| `model_skill_vs_best_fix` | **the load-bearing number**: `> 1` means the predictor is worse than a `scipy.ndimage.map_coordinates` one-liner |
| `per_sample_model_beats_best_fix_frac` | the same question per sample (needs `rel_l2_per_sample`) |
| `no_harm_gate_oracle_skill` | what a per-sample fallback to copy-LF would score; `damage_share` = the fraction of the predictor's error that is damage inflicted ON TOP of copy-LF |
| `_geomeans` | the panel geomean under BOTH denominators |

HOW TO READ IT
--------------
* `model_skill_vs_best_fix >= 1` on most datasets -> the card's win is a learned
  re-derivation of the resampling fix, not physics. Report the corrected geomean.
* `pct_copylf_error_removed_model` tracking `pct_copylf_error_removed_best_fix` across
  datasets (rank correlation) is the signature of a registration-driven mechanism.
* `best_fix_skill_vs_copylf ~ 1e-5` -> the ladder is DEGENERATE (no fidelity gap at
  all); any skill reported there is measuring the convention plus the model's own
  output noise.
* `damage_share > 0.5` -> most of the predictor's error is harm it does to samples
  copy-LF already had right; a trust gate is worth more than the mechanism.

INVOKE
------
  source "$PROJECT_ROOT/.venv/bin/activate"
  # per-run result JSONs written by round1/eval/score_panel.py (recommended: gives the
  # per-sample columns and the gate oracle)
  python tools/registration_skill_split.py \
      --datasets sharp__phase_field_crystal_2d,sharp__cahn_hilliard \
      --result_glob '<results_dir>/{dataset}_e200_s0.json' --out split.json
  # or supply scores directly (per-sample columns are then omitted)
  python tools/registration_skill_split.py --datasets PANEL \
      --model_nrmse 'sharp__cahn_hilliard=0.03973,ext__helmholtz_2d=1.3626' --out split.json

`--datasets` accepts `PANEL` / `GUARD` (from `project.yaml`) or a comma list.
`--split` (default `test_hf`) and `--metric_key` (default `rel_l2_mean`, the round's
per-sample-mean convention -- NEVER the legacy ratio-of-sums `nRMSE` key) select what is
read from the result JSON. Pure numpy/scipy on the login node, ~10-40 s per 256^2
dataset. Nothing it prints may become a card score: the eval layer stays the source of
truth, and the corrected variants exist for interpretation and for control arms.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
R1 = HERE.parent
sys.path.insert(0, str(R1 / "eval"))
sys.path.insert(0, str(HERE))
from nrmse import nrmse                                    # noqa: E402
from panel_data import load_config, load_split, copylf_prediction  # noqa: E402
import registration_audit as RA                            # noqa: E402


def _resolve(names: str):
    if names in ("PANEL", "GUARD"):
        cfg = load_config()
        return list(cfg["panel"] if names == "PANEL" else cfg["guard_set"])
    return [d for d in names.split(",") if d]


def _per_sample(pred, hf):
    return np.linalg.norm(pred - hf, axis=1) / np.linalg.norm(hf, axis=1)


def one(ds, model_nrmse, model_ps, copylf_ps_official, n_test):
    d = load_split(ds, "test")
    if not d["lf_fids"]:
        return {"error": "test split ships no LF fidelity (copy-LF undefined)"}
    hf_fid, lf_fid = d["hf_fid"], max(d["lf_fids"])
    hg = d["grid_shape_by_fid"].get(hf_fid)
    lg = d["grid_shape_by_fid"].get(lf_fid)
    if hg is None or lg is None:
        return {"error": "non-square / 1-D layout: this audit is 2-D only"}
    hg, lg = tuple(hg), tuple(lg)
    hf = np.asarray(d["field_by_fid"][hf_fid], dtype=np.float64)[:n_test]
    n = hf.shape[0]
    lf2d = np.asarray(d["field_by_fid"][lf_fid], dtype=np.float64)[:n].reshape(n, *lg)
    ec = copylf_prediction(d)[:n]
    periodic = ds != "ext__helmholtz_2d" and hg[0] % lg[0] == 0

    variants = RA.build_variants(lf2d, hg, ec, periodic)
    vn = {k: nrmse(v, hf) for k, v in variants.items()}
    vps = {k: _per_sample(v, hf) for k, v in variants.items()}
    a = vn["A_eval_copylf"]

    fixes = {k: v for k, v in vn.items() if not k.startswith(("A_", "A2_"))}
    best = min(fixes, key=fixes.get)

    e = {
        "n_test_used": int(n), "grid_hf": list(hg), "grid_lf": list(lg),
        "copylf_A_nrmse": a,
        "variant_nrmse": vn,
        "variant_skill_vs_copylf": {k: v / a for k, v in vn.items()},
        "best_zero_param_fix": best,
        "best_fix_skill_vs_copylf": vn[best] / a,
        "pct_copylf_error_removed_best_fix": 100.0 * (1 - vn[best] / a),
    }
    if copylf_ps_official is not None:
        m = min(len(copylf_ps_official), n)
        e["copylf_seam_vs_result_json_abs"] = float(
            abs(float(np.mean(copylf_ps_official[:m])) - float(np.mean(vps["A_eval_copylf"][:m]))))
    if model_nrmse is None:
        return e
    e.update({
        "model_nrmse": float(model_nrmse),
        "model_skill_vs_copylf": float(model_nrmse) / a,
        "model_skill_vs_best_fix": float(model_nrmse) / vn[best],
        "pct_copylf_error_removed_model": 100.0 * (1 - float(model_nrmse) / a),
    })
    if model_ps is not None:
        mp = np.asarray(model_ps, dtype=np.float64)[:n]
        cp = (np.asarray(copylf_ps_official, dtype=np.float64)[:len(mp)]
              if copylf_ps_official is not None else vps["A_eval_copylf"][:len(mp)])
        e["per_sample_model_beats_best_fix_frac"] = float(np.mean(mp < vps[best][:len(mp)]))
        e["per_sample_model_beats_copylf_frac"] = float(np.mean(mp < cp))
        e["no_harm_gate_oracle_skill"] = float(np.minimum(mp, cp).mean() / cp.mean())
        e["n_samples_gate_would_reject"] = int((mp > cp).sum())
        e["damage_share_of_model_error"] = float(
            np.where(mp > cp, mp - cp, 0.0).sum() / max(mp.sum(), 1e-300))
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", required=True, help="PANEL | GUARD | comma list")
    ap.add_argument("--out", required=True)
    ap.add_argument("--result_glob", default=None,
                    help="path template with {dataset}, e.g. '<dir>/{dataset}_e200_s0.json'")
    ap.add_argument("--model_nrmse", default=None,
                    help="comma list 'dataset=value' (used when no result JSON exists)")
    ap.add_argument("--split", default="test_hf")
    ap.add_argument("--metric_key", default="rel_l2_mean",
                    help="per-sample-mean by convention; never the ratio-of-sums 'nRMSE'")
    ap.add_argument("--copylf_split", default="ref_copylf_identity",
                    help="split in the result JSON holding copy-LF's per-sample column")
    ap.add_argument("--n_test", type=int, default=10 ** 9)
    a = ap.parse_args()

    direct = {}
    if a.model_nrmse:
        for kv in a.model_nrmse.split(","):
            k, v = kv.split("=")
            direct[k.strip()] = float(v)

    out = {"_args": vars(a)}
    for ds in _resolve(a.datasets):
        mn, mps, cps = direct.get(ds), None, None
        if a.result_glob:
            p = pathlib.Path(a.result_glob.format(dataset=ds))
            if p.exists():
                j = json.load(open(p))
                sp = j["splits"][a.split]
                mn = float(sp[a.metric_key])
                mps = sp.get("rel_l2_per_sample")
                cs = j["splits"].get(a.copylf_split)
                cps = np.asarray(cs["rel_l2_per_sample"], float) if cs else None
            else:
                out[ds] = {"error": f"result JSON not found: {p}"}
                print(f"[{ds}] MISSING {p}")
                continue
        try:
            e = one(ds, mn, mps, cps, a.n_test)
        except Exception as exc:                                  # noqa: BLE001
            e = {"error": f"{type(exc).__name__}: {exc}"}
        out[ds] = e
        if "error" in e:
            print(f"[{ds}] {e['error']}")
            continue
        msg = (f"[{ds}] free fix {e['best_zero_param_fix']} skill "
               f"{e['best_fix_skill_vs_copylf']:.4g} "
               f"({e['pct_copylf_error_removed_best_fix']:.1f}% of copy-LF error is registration)")
        if "model_skill_vs_copylf" in e:
            msg += (f" | model skill {e['model_skill_vs_copylf']:.4f} -> "
                    f"MODEL/FIX {e['model_skill_vs_best_fix']:.3f}")
        if "no_harm_gate_oracle_skill" in e:
            msg += (f" | gate oracle {e['no_harm_gate_oracle_skill']:.4f} "
                    f"(rejects {e['n_samples_gate_would_reject']})")
        print(msg, flush=True)

    def gm(key):
        v = [out[d][key] for d in out
             if not d.startswith("_") and isinstance(out[d], dict) and key in out[d]
             and out[d][key] > 0]
        return float(np.exp(np.mean(np.log(v)))) if v else None

    out["_geomeans"] = {
        "model_vs_copylf": gm("model_skill_vs_copylf"),
        "best_free_fix_vs_copylf": gm("best_fix_skill_vs_copylf"),
        "model_vs_registration_fixed_denominator": gm("model_skill_vs_best_fix"),
        "no_harm_gate_oracle": gm("no_harm_gate_oracle_skill"),
        "note": "geomean over the datasets supplied on the command line, not necessarily "
                "the round panel",
    }
    print("\ngeomeans:", json.dumps(out["_geomeans"]))
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
