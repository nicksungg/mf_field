#!/usr/bin/env python
"""Defect-class red-team measurement suite (round 3, 2026-08-06).

Read-only against benchmark data; writes per-candidate JSONs into this dir.
Candidates C01..C12 — see REDTEAM_REPORT.md for the classification.

Usage: measure.py [c01 c02 ...]   (no args = run all)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import traceback
from pathlib import Path

import numpy as np

REPO = Path("/resnick/groups/Hippo/ezeng/mf_field")
OUT = REPO / "mffp_autoresearch" / "defect_class_redteam"
EVAL = REPO / "mffp_autoresearch" / "round2" / "eval"
sys.path.insert(0, str(EVAL))

import panel_data  # noqa: E402
from panel_data import (  # noqa: E402
    copylf_prediction,
    load_split,
    _node_aligned_periodic_up,
    _legacy_cell_centred_up,
)

SHARP_PANEL = [
    "sharp__phase_field_crystal_2d",
    "sharp__allen_cahn_2d",
    "sharp__fisher_kpp_2d",
    "sharp__cahn_hilliard",
]
IFC = ["ifc_poisson", "ifc_heat"]
PANEL = SHARP_PANEL + IFC

BASELINES = json.load(open(EVAL / "copylf_baselines.json"))


def per_sample_ratios(pred: np.ndarray, target: np.ndarray) -> np.ndarray:
    pred = np.asarray(pred, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    denom = np.linalg.norm(target, axis=1)
    return np.linalg.norm(pred - target, axis=1) / denom


def save(name: str, obj: dict) -> None:
    path = OUT / f"{name}.json"
    with open(path, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    print(f"[saved] {path}")


def std_cond(train_x: np.ndarray, other_x: np.ndarray):
    mu = train_x.mean(0)
    sd = train_x.std(0)
    sd[sd == 0] = 1.0
    return (train_x - mu) / sd, (other_x - mu) / sd


def all_train_conds(data_tr: dict) -> np.ndarray:
    """Union of condition rows over all train fidelities (dedup exact)."""
    rows = [np.asarray(data_tr["cond_by_fid"][f], float) for f in data_tr["fids"]]
    allx = np.vstack(rows)
    return np.unique(allx, axis=0)


# ── C01: cross-split contamination (near-duplicate rows across splits) ──
def c01():
    rec = {}
    for name in PANEL:
        try:
            tr = load_split(name, "train")
            te = load_split(name, "test")
            hf = tr["hf_fid"]
            tr_x = all_train_conds(tr)
            te_x = np.asarray(te["cond_by_fid"][te["hf_fid"]], float)
            trs, tes = std_cond(tr_x, te_x)
            # condition-space min distance per test row (normalized by sqrt(d))
            d2 = ((tes[:, None, :] - trs[None, :, :]) ** 2).sum(-1)
            dmin = np.sqrt(d2.min(1)) / np.sqrt(tr_x.shape[1])
            ent = {
                "n_train_conds": int(tr_x.shape[0]),
                "n_test": int(te_x.shape[0]),
                "cond_dmin_min": float(dmin.min()),
                "cond_dmin_median": float(np.median(dmin)),
                "frac_below_0.05": float((dmin < 0.05).mean()),
                "frac_below_0.01": float((dmin < 0.01).mean()),
                "n_exact_dupes": int((dmin == 0).sum()),
            }
            # field-space near-dup: test HF vs train HF (index-agnostic)
            y_tr = np.asarray(tr["field_by_fid"][hf], np.float64)
            y_te = np.asarray(te["field_by_fid"][te["hf_fid"]], np.float64)
            if y_tr.shape[1] == y_te.shape[1]:
                g_tr = (y_tr ** 2).sum(1)
                g_te = (y_te ** 2).sum(1)
                cross = y_te @ y_tr.T
                d2f = g_te[:, None] - 2 * cross + g_tr[None, :]
                d2f = np.maximum(d2f, 0)
                rel = np.sqrt(d2f) / np.sqrt(g_te)[:, None]
                relmin = rel.min(1)
                ent.update({
                    "field_relmin_min": float(relmin.min()),
                    "field_relmin_median": float(np.median(relmin)),
                    "frac_field_below_0.02": float((relmin < 0.02).mean()),
                })
            rec[name] = ent
        except Exception as e:
            rec[name] = {"error": repr(e), "tb": traceback.format_exc()[-800:]}
    save("c01_contamination", rec)


# ── C02: condition-distribution shift between splits ──
def c02():
    from scipy.stats import ks_2samp

    rec = {}
    for name in PANEL:
        try:
            tr = load_split(name, "train")
            te = load_split(name, "test")
            tr_x = all_train_conds(tr)
            te_x = np.asarray(te["cond_by_fid"][te["hf_fid"]], float)
            cols = []
            for j in range(tr_x.shape[1]):
                a, b = tr_x[:, j], te_x[:, j]
                lo, hi = a.min(), a.max()
                span = (hi - lo) or 1.0
                out_frac = float(((b < lo) | (b > hi)).mean())
                worst = float(max(0.0, max(lo - b.min(), b.max() - hi)) / span)
                ks = float(ks_2samp(a, b).statistic) if a.std() > 0 else 0.0
                cols.append(
                    {"col": j, "ks": ks, "test_outside_train_range_frac": out_frac,
                     "worst_overshoot_relspan": worst}
                )
            worst_ks = max(cols, key=lambda c: c["ks"])
            worst_out = max(cols, key=lambda c: c["test_outside_train_range_frac"])
            rec[name] = {
                "n_cols": len(cols),
                "worst_ks": worst_ks,
                "worst_outside": worst_out,
                "mean_outside_frac": float(np.mean([c["test_outside_train_range_frac"] for c in cols])),
                "cols_ks_gt_0.2": [c["col"] for c in cols if c["ks"] > 0.2],
            }
        except Exception as e:
            rec[name] = {"error": repr(e)}
    save("c02_split_shift", rec)


# ── C03/C04: target-norm pathologies + level-domination ──
def c03():
    rec = {}
    for name in PANEL:
        try:
            te = load_split(name, "test")
            hf = te["hf_fid"]
            y = np.asarray(te["field_by_fid"][hf], np.float64)
            norms = np.linalg.norm(y, axis=1)
            mean_removed = np.linalg.norm(y - y.mean(1, keepdims=True), axis=1)
            rho = mean_removed / norms  # fraction of the norm that is structure
            ent = {
                "n_test": int(y.shape[0]),
                "norm_min": float(norms.min()),
                "norm_median": float(np.median(norms)),
                "norm_min_over_median": float(norms.min() / np.median(norms)),
                "structure_fraction_rho_min": float(rho.min()),
                "structure_fraction_rho_median": float(np.median(rho)),
                "level_domination_factor_median": float(np.median(1.0 / rho)),
            }
            # copy-LF per-sample ratio concentration (test LF present only)
            try:
                pred = copylf_prediction(te, name)
                r = per_sample_ratios(pred, y)
                order = np.argsort(r)[::-1]
                s = r.sum()
                ent.update(
                    copylf_mean_of_ratios=float(r.mean()),
                    copylf_ratio_of_sums=float(
                        np.linalg.norm(pred - y) / np.linalg.norm(y)
                    ),
                    copylf_ratio_p95_over_p5=float(
                        np.percentile(r, 95) / np.percentile(r, 5)
                    ),
                    copylf_top1_share=float(r[order[0]] / s),
                    copylf_top5_share=float(r[order[:5]].sum() / s),
                    copylf_mean_removed_nrmse=float(
                        np.mean(
                            np.linalg.norm(pred - y, axis=1) / mean_removed
                        )
                    ),
                )
            except Exception as e:
                ent["copylf"] = f"skipped: {e!r}"
            rec[name] = ent
        except Exception as e:
            rec[name] = {"error": repr(e)}
    save("c03_denominators", rec)


# ── C05: reference/baseline-to-data binding (staleness) ──
def c05():
    rec = {"recompute_vs_baseline": {}, "file_coherence": {}, "pfc_box": {}}
    for name in SHARP_PANEL + ["ext__helmholtz_2d"]:
        try:
            te = load_split(name, "test")
            hf = te["hf_fid"]
            y = np.asarray(te["field_by_fid"][hf], np.float64)
            pred = copylf_prediction(te, name)
            val = float(per_sample_ratios(pred, y).mean())
            base = BASELINES[name]["test_nrmse"]
            rec["recompute_vs_baseline"][name] = {
                "recomputed_now": val,
                "baseline_json": base,
                "rel_diff": float(abs(val - base) / base),
            }
        except Exception as e:
            rec["recompute_vs_baseline"][name] = {"error": repr(e)}
    # file coherence across the three roots
    def md5(p: Path):
        h = hashlib.md5()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    strip_root = REPO / "mffp_autoresearch" / "round2" / "stripped_data"
    fac_root = REPO / "mf_field" / "factory_mffp" / "data"
    b42 = REPO / "benchmark_42" / "sharp"
    for name in SHARP_PANEL:
        short = name.replace("sharp__", "")
        ent = {}
        for fname in ["test_l3.npz", "train_l3.npz", "train_l1.npz"]:
            paths = {
                "benchmark_42": b42 / short / fname,
                "factory_data": fac_root / name / fname,
                "stripped": strip_root / name / fname,
            }
            hh = {}
            for k, p in paths.items():
                if p.exists():
                    hh[k] = {"md5": md5(p), "mtime": os.path.getmtime(p),
                             "symlink_target": str(p.resolve()) if p.is_symlink() or (fac_root / name).is_symlink() else None}
                else:
                    hh[k] = "ABSENT"
            vals = {v["md5"] for v in hh.values() if isinstance(v, dict)}
            ent[fname] = {"coherent": len(vals) <= 1, "detail": hh}
        rec["file_coherence"][name] = ent
    # pfc box check vs ADR r3-0002 (crystalline box r in [-0.4,-0.3], md in [-0.25,-0.2])
    tr = load_split("sharp__phase_field_crystal_2d", "train")
    x = np.asarray(tr["cond_by_fid"][tr["hf_fid"]], float)
    rec["pfc_box"] = {
        "r_range_observed": [float(x[:, 0].min()), float(x[:, 0].max())],
        "mean_density_range_observed": [float(x[:, 1].min()), float(x[:, 1].max())],
        "adr_r3_0002_crystalline_box": {"r": [-0.4, -0.3], "mean_density": [-0.25, -0.2]},
        "regeneration_landed": bool(
            x[:, 0].min() >= -0.4001 and x[:, 0].max() <= -0.2999
            and x[:, 1].min() >= -0.2501 and x[:, 1].max() <= -0.1999
        ),
    }
    save("c05_staleness", rec)


# ── C06: ladder monotonicity (is each coarser rung actually worse?) ──
def c06():
    rec = {}
    for name in PANEL:
        try:
            ent = {}
            for split in ["test", "train"]:
                try:
                    d = load_split(name, split)
                except Exception:
                    continue
                hf = d["hf_fid"]
                y = np.asarray(d["field_by_fid"][hf], np.float64)
                n = y.shape[0]
                hf_grid = d["grid_shape_by_fid"].get(hf)
                gaps = {}
                for f in d["lf_fids"]:
                    lf = np.asarray(d["field_by_fid"][f], np.float64)[:n]
                    if lf.shape[0] < n:
                        continue
                    lf_grid = d["grid_shape_by_fid"].get(f)
                    if lf_grid is None or hf_grid is None:
                        continue
                    if name in panel_data.PERIODIC_NODE_DATASETS:
                        up_fn = _node_aligned_periodic_up
                    else:
                        up_fn = _legacy_cell_centred_up
                    up = np.stack(
                        [up_fn(lf[i].reshape(lf_grid), tuple(hf_grid)).ravel() for i in range(n)]
                    )
                    gaps[str(f)] = float(per_sample_ratios(up, y).mean())
                if gaps:
                    keys = sorted(gaps, key=lambda k: int(k))
                    vals = [gaps[k] for k in keys]
                    ent[split] = {
                        "gap_by_level": gaps,
                        "monotone_decreasing_with_resolution": bool(
                            all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))
                        ),
                    }
            rec[name] = ent or {"error": "no measurable rungs"}
        except Exception as e:
            rec[name] = {"error": repr(e), "tb": traceback.format_exc()[-500:]}
    save("c06_ladder", rec)


# ── C07: condition-vector redundancy / degeneracy ──
def c07():
    rec = {}
    for name in PANEL:
        try:
            tr = load_split(name, "train")
            x = np.asarray(all_train_conds(tr), float)
            mu, sd = x.mean(0), x.std(0)
            const_cols = [int(j) for j in range(x.shape[1]) if sd[j] < 1e-12]
            xs = (x - mu) / np.where(sd < 1e-12, 1, sd)
            sv = np.linalg.svd(xs, compute_uv=False)
            corr = np.corrcoef(xs, rowvar=False)
            np.fill_diagonal(corr, 0)
            corr = np.nan_to_num(corr)
            i, j = np.unravel_index(np.abs(corr).argmax(), corr.shape)
            rec[name] = {
                "n_rows": int(x.shape[0]),
                "n_cols": int(x.shape[1]),
                "constant_cols": const_cols,
                "rank_1e-8": int((sv > sv[0] * 1e-8).sum()),
                "sv_min_over_max": float(sv[-1] / sv[0]),
                "max_abs_offdiag_corr": float(np.abs(corr).max()),
                "max_corr_pair": [int(i), int(j)],
            }
        except Exception as e:
            rec[name] = {"error": repr(e)}
    save("c07_redundancy", rec)


# ── C08: dtype/precision seam (float32 pipeline vs float64 reference) ──
def c08():
    rec = {}
    for name in SHARP_PANEL:
        try:
            te = load_split(name, "test")
            hf = te["hf_fid"]
            y64 = np.asarray(te["field_by_fid"][hf], np.float64)
            pred64 = copylf_prediction(te, name)
            v64 = float(per_sample_ratios(pred64, y64).mean())
            # float32 pipeline: cast pred+target, compute norms in float32
            p32 = pred64.astype(np.float32)
            y32 = y64.astype(np.float32)
            num = np.linalg.norm((p32 - y32).astype(np.float32), axis=1)
            den = np.linalg.norm(y32, axis=1)
            v32 = float(np.mean(num / den))
            rec[name] = {
                "nrmse_float64": v64,
                "nrmse_float32_pipeline": v32,
                "rel_diff": float(abs(v64 - v32) / v64),
                "float32_quantization_floor_est": float(
                    np.mean(np.linalg.norm(y64 - y64.astype(np.float32).astype(np.float64), axis=1)
                            / np.linalg.norm(y64, axis=1))
                ),
            }
        except Exception as e:
            rec[name] = {"error": repr(e)}
    save("c08_dtype", rec)


# ── C09: seed-noise scale vs claimed effects ──
def c09():
    rec = {"sources": [], "per_family_dataset": {}}
    cand_dirs = [
        EVAL / "results",
        REPO / "mffp_autoresearch" / "round3" / "state",
        REPO / "mffp_autoresearch" / "round3" / "state" / "anchors",
    ]
    seen = {}
    for d in cand_dirs:
        if not d.exists():
            continue
        for p in sorted(d.glob("**/*.json")):
            try:
                j = json.load(open(p))
            except Exception:
                continue
            fam = j.get("family")
            seed = j.get("seed")
            pd = j.get("per_dataset")
            if fam is None or seed is None or not isinstance(pd, dict):
                continue
            rec["sources"].append(str(p))
            for ds, cell in pd.items():
                if isinstance(cell, dict) and "nRMSE" in cell:
                    seen.setdefault((fam, ds), {})[int(seed)] = float(cell["nRMSE"])
    for (fam, ds), by_seed in seen.items():
        if len(by_seed) >= 2:
            vals = np.array(list(by_seed.values()))
            rec["per_family_dataset"][f"{fam}|{ds}"] = {
                "seeds": sorted(by_seed),
                "values": [float(v) for v in vals],
                "rel_std": float(vals.std(ddof=1) / vals.mean()) if vals.mean() else None,
                "rel_range": float((vals.max() - vals.min()) / vals.mean()) if vals.mean() else None,
            }
    # per-dataset summary: max rel_range over families with >=2 seeds
    summary = {}
    for k, v in rec["per_family_dataset"].items():
        ds = k.split("|")[1]
        summary.setdefault(ds, []).append(v["rel_range"])
    rec["per_dataset_max_rel_range"] = {
        ds: float(np.max(v)) for ds, v in summary.items()
    }
    save("c09_seed_noise", rec)


# ── C10: single-cell discrimination power (bootstrap CI of the cell) ──
def c10():
    rec = {}
    rng = np.random.default_rng(0)
    for name in SHARP_PANEL:
        try:
            te = load_split(name, "test")
            hf = te["hf_fid"]
            y = np.asarray(te["field_by_fid"][hf], np.float64)
            pred = copylf_prediction(te, name)
            r = per_sample_ratios(pred, y)
            boots = rng.choice(r, size=(10000, r.size), replace=True).mean(1)
            lo, hi = np.percentile(boots, [2.5, 97.5])
            rec[name] = {
                "cell_mean": float(r.mean()),
                "ci95": [float(lo), float(hi)],
                "ci_halfwidth_rel": float((hi - lo) / 2 / r.mean()),
                "min_detectable_model_delta_rel": float((hi - lo) / r.mean()),
                "per_sample_p95_over_p5": float(np.percentile(r, 95) / np.percentile(r, 5)),
            }
        except Exception as e:
            rec[name] = {"error": repr(e)}
    save("c10_discrimination", rec)


# ── C11: metric-extraction seam (self-reported cells; two statistics) ──
def c11():
    rec = {"statistic_divergence": {}, "result_json_audit": []}
    for name in SHARP_PANEL:
        try:
            te = load_split(name, "test")
            y = np.asarray(te["field_by_fid"][te["hf_fid"]], np.float64)
            pred = copylf_prediction(te, name)
            r = per_sample_ratios(pred, y)
            mor = float(r.mean())
            ros = float(np.linalg.norm(pred - y) / np.linalg.norm(y))
            rec["statistic_divergence"][name] = {
                "mean_of_ratios": mor,
                "ratio_of_sums": ros,
                "rel_diff": float(abs(mor - ros) / mor),
            }
        except Exception as e:
            rec["statistic_divergence"][name] = {"error": repr(e)}
    # audit existing result JSONs: per-sample array present? scalar consistent?
    roots = [EVAL / "results", REPO / "mf_field" / "factory_mffp" / "results"]
    for d in roots:
        if not d.exists():
            continue
        for p in sorted(d.glob("**/*.json"))[:200]:
            try:
                j = json.load(open(p))
            except Exception:
                continue
            splits = j.get("splits")
            if not isinstance(splits, dict):
                continue
            for sname, s in splits.items():
                if not isinstance(s, dict):
                    continue
                has_arr = any(
                    isinstance(s.get(k), list) and len(s.get(k)) > 1
                    for k in ("per_sample_rel_l2", "rel_l2_per_sample", "per_sample")
                )
                scalar = s.get("nRMSE")
                ent = {"file": str(p.relative_to(REPO)), "split": sname,
                       "has_per_sample_array": has_arr, "scalar_nRMSE": scalar}
                if has_arr:
                    for k in ("per_sample_rel_l2", "rel_l2_per_sample", "per_sample"):
                        if isinstance(s.get(k), list):
                            arr = np.asarray(s[k], float)
                            ent["mean_of_array"] = float(arr.mean())
                            if scalar:
                                ent["scalar_vs_mean_rel_diff"] = float(
                                    abs(arr.mean() - scalar) / scalar
                                )
                            break
                rec["result_json_audit"].append(ent)
    rec["n_result_splits_audited"] = len(rec["result_json_audit"])
    rec["n_without_per_sample_array"] = sum(
        1 for e in rec["result_json_audit"] if not e["has_per_sample_array"]
    )
    save("c11_metric_seam", rec)


# ── C12: stripped-view integrity + coherence with the scoring data ──
def c12():
    strip_root = REPO / "mffp_autoresearch" / "round2" / "stripped_data"
    fac_root = REPO / "mf_field" / "factory_mffp" / "data"

    def md5(p: Path):
        h = hashlib.md5()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    rec = {}
    for name in PANEL + ["ext__helmholtz_2d", "heat_local", "fluid", "sharp__sod_1d"]:
        sd = strip_root / name
        if not sd.exists():
            rec[name] = {"error": "no stripped dir"}
            continue
        files = sorted(str(p.relative_to(sd)) for p in sd.rglob("*") if p.is_file())
        test_lf_leaks = [
            f for f in files
            if ("test_l" in f and not f.endswith("_l3.npz") and f.endswith(".npz"))
            or (f.startswith("test/") and "fidelity" in f and not any(
                f.startswith(f"test/fidelity_{hi}/") for hi in (64, 128)))
        ]
        ent = {"n_files": len(files), "test_lf_leaks": test_lf_leaks}
        # coherence of the test HF file with the scoring root
        for cand in ["test_l3.npz", "test/fidelity_64/ys.npy", "test/fidelity_128/ys.npy"]:
            sp, fp = sd / cand, fac_root / name / cand
            if sp.exists() and fp.exists():
                ent["test_hf_file"] = cand
                ent["stripped_md5"] = md5(sp)
                ent["scoring_root_md5"] = md5(fp)
                ent["coherent_with_scoring_root"] = ent["stripped_md5"] == ent["scoring_root_md5"]
                break
        rec[name] = ent
    save("c12_stripped_view", rec)


ALL = {f.__name__: f for f in [c01, c02, c03, c05, c06, c07, c08, c09, c10, c11, c12]}

if __name__ == "__main__":
    which = sys.argv[1:] or list(ALL)
    for w in which:
        print(f"=== {w} ===", flush=True)
        try:
            ALL[w]()
        except Exception:
            traceback.print_exc()
            save(f"{w}_FAILED", {"tb": traceback.format_exc()})
