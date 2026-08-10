#!/usr/bin/env python
"""Matched-fit-set audit for training-free reference floors.

**What it answers.** A scored arm is fit on `n_scored` rows; the reference floor
it is compared against is fit on ALL the training rows. Is that a fair
comparison, and how much of the difference is a *systematic* n-effect versus
*estimator variance of the reference itself*?

A single deterministic refit at `n_scored` (e.g. "the first 320 rows") cannot
tell those apart, and for a SELECTION arm such as `nn_condition` — a discrete
argmin over the fit set — it is one draw from a wide distribution: removing rows
flips the neighbour for a fraction of test rows and each flip moves that row's
error by O(1). This tool reports, per cell per arm:

  * `systematic_correction`  E[skill @ matched fit] - skill @ full fit, an
    EXPECTATION over fit sets, with a standard error — the honest matched-n
    correction, and the only part of the seam that is a bias;
  * `selection_noise_sd`     the reference arm's own sd over fit sets — a
    property of the arm that no choice of subset removes;
  * `frac_folds_breaching_tau`  the fraction of fit sets on which the shift
    exceeds the cell's certified `tau_rel`, i.e. the POWER of a single-draw gate;
  * the per-test-row re-selection anatomy (how many rows change neighbour, and
    how concentrated the net shift is), because a net shift that is the residual
    of a cancelling sum must not be read as an n-scaling law;
  * optionally, a comparand re-pricing: a model skill per cell re-read against
    both the full-fit and the matched-fit floor, with a `verdict_sign_unchanged`
    flag.

When `n_train <= n_scored` the matched-n question is undefined; the tool then
runs the ANSWERABLE analogue instead — exhaustive leave-one-out over all
`C(n, n-1)` folds — so few-row reference floors (the ifc cells: a 6-dof affine
fit on 5 HF train rows) are audited rather than skipped.

**Run it** before pricing any claim against a training-free floor whose fit-set
size differs from the scored arm's, and on any few-row reference floor before
quoting it in a rule.

Exactness: the round's nRMSE is the MEAN of per-row rel-L2, so the whole
`nn_condition` fold population is evaluated from ONE precomputed
`(n_train x n_test)` rel-L2 matrix; the matrix is asserted against the frozen
`nrmse()` at 1e-12 before use. Arm constructions are byte-identical to
`tools/make_round3_anchors.py` / `r3s4_audit-B2 probes/d4_fitset.py`.

REPORT-ONLY: never writes `state/`, never re-freezes a floor.

Provenance: `r3s4_audit-B2` turns 1-2 (card
`experiment_cards/r3s4_audit/batch_2/B2.json` part 6).
"""
from __future__ import annotations

import argparse
import datetime
import itertools
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _project_root() -> Path:
    here = Path(__file__).resolve()
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             cwd=str(here.parent), capture_output=True,
                             text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:                                              # noqa: BLE001
        return here.parents[3]


ROOT = _project_root()
sys.path.insert(0, str(ROOT / "mffp_autoresearch" / "round2" / "eval"))
sys.path.insert(0, str(ROOT / "mf_field" / "factory_mffp"))

from nrmse import NRMSE_DEF_HASH, nrmse                            # noqa: E402

ARMS_DEFAULT = "nn_condition,train_mean,affine_on_hf_train"


# ── arm constructions (verbatim: make_round3_anchors / d4_fitset) ──

def standardize_cond(c_tr, c_te):
    mu, sd = c_tr.mean(axis=0), c_tr.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    return (c_tr - mu) / sd, (c_te - mu) / sd


def affine_fit(X, Y):
    A = np.hstack([X, np.ones((len(X), 1))])
    W, *_ = np.linalg.lstsq(A, Y, rcond=None)
    return lambda Xq: np.hstack([Xq, np.ones((len(Xq), 1))]) @ W


def arm_value(arm, c_tr, y_tr, c_te, y_te):
    if arm == "train_mean":
        return float(nrmse(np.broadcast_to(y_tr.mean(axis=0), y_te.shape), y_te))
    if arm == "nn_condition":
        z_tr, z_te = standardize_cond(c_tr, c_te)
        d2 = ((z_te[:, None, :] - z_tr[None, :, :]) ** 2).sum(axis=2)
        return float(nrmse(y_tr[np.argmin(d2, axis=1)], y_te))
    if arm == "affine_on_hf_train":
        return float(nrmse(affine_fit(c_tr, y_tr)(c_te), y_te))
    if arm == "zero":
        return float(nrmse(np.zeros_like(y_te), y_te))
    raise SystemExit(f"unknown arm {arm!r}")


def nn_index(c_tr, c_te):
    z_tr, z_te = standardize_cond(c_tr, c_te)
    d2 = ((z_te[:, None, :] - z_tr[None, :, :]) ** 2).sum(axis=2)
    return np.argmin(d2, axis=1)


def rel_l2_matrix(y_tr, y_te):
    """M[j, i] = ||y_tr[j] - y_te[i]|| / ||y_te[i]|| via the Gram identity."""
    tn = (y_tr ** 2).sum(axis=1)[:, None]
    en = (y_te ** 2).sum(axis=1)[None, :]
    d2 = np.maximum(tn + en - 2.0 * (y_tr @ y_te.T), 0.0)
    return np.sqrt(d2) / np.sqrt(en)


def load_split(root: Path, dataset: str):
    from data_adapters.loaders import load_mf_dataset
    tr = load_mf_dataset(Path(root) / dataset, "train")
    te = load_mf_dataset(Path(root) / dataset, "test")
    hf = tr["hf_fid"] if tr["hf_fid"] in te["fids"] else te["hf_fid"]
    f64 = lambda a: np.asarray(a, dtype=np.float64)                # noqa: E731
    return (f64(tr["cond_by_fid"][hf]), f64(tr["field_by_fid"][hf]),
            f64(te["cond_by_fid"][hf]), f64(te["field_by_fid"][hf]))


def kv(spec: str, cast=float) -> dict:
    out = {}
    for part in (spec or "").split(","):
        if not part.strip():
            continue
        k, v = part.split("=", 1)
        out[k.strip()] = cast(v.strip())
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--datasets", required=True, help="comma list")
    ap.add_argument("--arms", default=ARMS_DEFAULT)
    ap.add_argument("--n-scored", type=int, default=320,
                    help="the SCORED arm's fit-set size")
    ap.add_argument("--draws", type=int, default=2000,
                    help="random fit sets for the cheap arms")
    ap.add_argument("--draws-affine", type=int, default=50,
                    help="random fit sets for affine_on_hf_train (a full lstsq "
                         "per draw; keep it small)")
    ap.add_argument("--seed", type=int, default=20260810)
    ap.add_argument("--stripped-root", default=str(
        ROOT / "mffp_autoresearch/round2/stripped_data"))
    ap.add_argument("--floors-json", default=str(
        ROOT / "mffp_autoresearch/round3/state/anchors_repaired/floors.json"),
        help="supplies each cell's reference nRMSE (the skill denominator)")
    ap.add_argument("--noise-floor-json", default=str(
        ROOT / "mffp_autoresearch/round3/state/anchors_repaired/noise_floor.json"),
        help="supplies certified tau_rel per cell")
    ap.add_argument("--anchors-json", default=str(
        ROOT / "mffp_autoresearch/round3/state/anchors/launch_anchors.json"),
        help="supplies best_floor.per_dataset[ds].arm (the gating arm)")
    ap.add_argument("--tau-rel", default="", help="ds=v,... overrides")
    ap.add_argument("--best-arm", default="", help="ds=arm,... overrides")
    ap.add_argument("--reference-nrmse", default="", help="ds=v,... overrides")
    ap.add_argument("--compare-skill", default="",
                    help="ds=skill,... a model comparand to re-price")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    arms = [x for x in a.arms.split(",") if x]
    tau_over, arm_over = kv(a.tau_rel), kv(a.best_arm, str)
    ref_over, cmp_over = kv(a.reference_nrmse), kv(a.compare_skill)
    floors = json.loads(Path(a.floors_json).read_text()) if Path(a.floors_json).exists() else {}
    nf = json.loads(Path(a.noise_floor_json).read_text()) if Path(a.noise_floor_json).exists() else {}
    anch = json.loads(Path(a.anchors_json).read_text()) if Path(a.anchors_json).exists() else {}
    best = (anch.get("best_floor", {}) or {}).get("per_dataset", {})

    rng = np.random.default_rng(a.seed)
    out = {"_tool": "fitset_matched_n_audit", "_nrmse_def_hash": NRMSE_DEF_HASH,
           "_utc": datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
           "_report_only": "never writes state/; re-freezes nothing",
           "n_scored": a.n_scored, "arms": arms, "seed": a.seed, "cells": {}}

    for ds in [x for x in a.datasets.split(",") if x]:
        c_tr, y_tr, c_te, y_te = load_split(Path(a.stripped_root), ds)
        n_full, n_te = len(c_tr), len(y_te)
        ref = ref_over.get(ds) or float(
            (floors.get(ds, {}).get("reference", {}) or {}).get("test_nrmse", 1.0))
        tau = tau_over.get(ds, (nf.get(ds, {}) or {}).get("tau_rel"))
        tau = float(tau) if tau else None
        gate_arm = arm_over.get(ds) or (best.get(ds, {}) or {}).get("arm")
        M = rel_l2_matrix(y_tr, y_te)
        ar = np.arange(n_te)

        nn_full = nn_index(c_tr, c_te)
        v_ref = float(nrmse(y_tr[nn_full], y_te))
        assert abs(float(M[nn_full, ar].mean()) - v_ref) <= 1e-12 * max(1.0, v_ref), \
            "metric seam: rel-L2 matrix does not reproduce nrmse()"

        full = {arm: arm_value(arm, c_tr, y_tr, c_te, y_te) / ref for arm in arms}
        cell = {"n_train": n_full, "n_test": n_te, "reference_nrmse": ref,
                "certified_tau_rel": tau, "gating_arm": gate_arm,
                "skill_at_full_fit": full}

        if n_full > a.n_scored:
            mode, n_fit = "random_subsets", a.n_scored
            folds = None
        else:
            mode = f"exhaustive_leave_one_out_C({n_full},{n_full - 1})"
            n_fit = n_full - 1
            folds = [np.array(f) for f in
                     itertools.combinations(range(n_full), n_full - 1)]
            cell["matched_n_undefined_note"] = (
                f"n_train ({n_full}) <= --n-scored ({a.n_scored}): the matched-n "
                "question is undefined here; the answerable analogue "
                "(exhaustive leave-one-out) is reported instead")
        cell["mode"], cell["n_fit"] = mode, n_fit

        Ysum, ten = y_tr.sum(axis=0), (y_te ** 2).sum(axis=1)
        per_arm = {}
        for arm in arms:
            B = (len(folds) if folds is not None
                 else (a.draws_affine if arm == "affine_on_hf_train" else a.draws))
            v = np.empty(B)
            for b in range(B):
                sel = folds[b] if folds is not None else rng.choice(
                    n_full, n_fit, replace=False)
                if arm == "nn_condition":
                    v[b] = M[sel[nn_index(c_tr[sel], c_te)], ar].mean() / ref
                elif arm == "train_mean" and folds is None:
                    keep = np.zeros(n_full, dtype=bool)
                    keep[sel] = True
                    m = (Ysum - y_tr[~keep].sum(axis=0)) / n_fit
                    d2 = np.maximum(float(m @ m) - 2.0 * (y_te @ m) + ten, 0.0)
                    v[b] = float(np.mean(np.sqrt(d2) / np.sqrt(ten))) / ref
                else:
                    v[b] = arm_value(arm, c_tr[sel], y_tr[sel], c_te, y_te) / ref
            d = v - full[arm]
            se = float(v.std(ddof=1) / np.sqrt(B))
            per_arm[arm] = {
                "n_draws": int(B),
                "skill_matched_mean": float(v.mean()),
                "skill_matched_sd": float(v.std(ddof=1)),
                "skill_matched_p2.5": float(np.percentile(v, 2.5)),
                "skill_matched_p97.5": float(np.percentile(v, 97.5)),
                "systematic_correction": float(d.mean()),
                "systematic_correction_se": se,
                "systematic_correction_over_tau": (float(d.mean() / tau) if tau else None),
                "systematic_correction_se_over_tau": (float(se / tau) if tau else None),
                "selection_noise_sd_over_tau": (float(v.std(ddof=1) / tau) if tau else None),
                "abs_shift_over_tau_p50": (float(np.percentile(np.abs(d), 50) / tau)
                                           if tau else None),
                "abs_shift_over_tau_p95": (float(np.percentile(np.abs(d), 95) / tau)
                                           if tau else None),
                "frac_folds_breaching_tau": (float((np.abs(d) > tau).mean())
                                             if tau else None),
            }
        cell["per_arm"] = per_arm

        # re-selection anatomy at one deterministic matched fit (first n_fit rows)
        if "nn_condition" in arms:
            i_s = nn_index(c_tr[:n_fit], c_te)
            r_s, r_f = M[np.arange(n_fit)[i_s], ar], M[nn_full, ar]
            drow = (r_s - r_f) / ref
            tot = float(drow.sum())
            order = np.argsort(-np.abs(drow))
            cell["reselection_anatomy_first_n_fit"] = {
                "n_rows_changing_neighbour": int((i_s != nn_full).sum()),
                "frac_rows_changing": float((i_s != nn_full).mean()),
                "skill_shift": float(drow.mean()),
                "skill_shift_over_tau": (float(drow.mean() / tau) if tau else None),
                "top1_row_share_of_shift": (float(drow[order[0]] / tot) if tot else None),
                "n_rows_for_50pct_of_shift": (
                    int(np.searchsorted(np.cumsum(drow[order]) / tot, 0.5) + 1)
                    if tot else None),
                "reading": "a |share| > 1 or a tiny row count means the net shift is "
                           "the RESIDUAL of a cancelling sum, not an n-scaling law",
            }

        if ds in cmp_over and gate_arm in per_arm:
            m = cmp_over[ds]
            mf, mm = full[gate_arm] - m, per_arm[gate_arm]["skill_matched_mean"] - m
            cell["comparand_repricing"] = {
                "arm": gate_arm, "model_skill": m,
                "margin_vs_full_fit": mf, "margin_vs_matched_fit": mm,
                "margin_vs_full_fit_over_tau": (mf / tau if tau else None),
                "margin_vs_matched_fit_over_tau": (mm / tau if tau else None),
                "direction": ("matched fit WIDENS the model's margin" if mm > mf
                              else "matched fit NARROWS the model's margin"),
                "verdict_sign_unchanged": bool((mf > 0) == (mm > 0)),
            }
        out["cells"][ds] = cell
        g = per_arm.get(gate_arm, {})
        print(f"{ds:28s} mode={mode:34s} arm={str(gate_arm):18s} "
              f"full={full.get(gate_arm, float('nan')):11.4f} "
              f"matched={g.get('skill_matched_mean', float('nan')):11.4f} "
              f"sys={g.get('systematic_correction_over_tau') or float('nan'):+7.3f}tau "
              f"sd={g.get('selection_noise_sd_over_tau') or float('nan'):6.3f}tau "
              f"breach={g.get('frac_folds_breaching_tau')}")

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, indent=2, sort_keys=True))
        print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
