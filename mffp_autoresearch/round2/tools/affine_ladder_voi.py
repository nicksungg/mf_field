#!/usr/bin/env python
"""Training-free value-of-LF certificate for a condition->HF task, via the affine ladder.

Provenance: promoted from `r2s3_lf_train_signal-B1` mechanism turn 2 (part B) +
turn 3 (part E), `worktrees/r2s3_lf_train_signal/B1/scratchpad/reanalysis_turn_2.py`
and `.../reanalysis_turn_3b.py`.

WHY THIS EXISTS
---------------
When a card reports "the LF rows did not help", that sentence conflates two
different measurements: whether the LF rows CARRY information about the HF field,
and whether the trained architecture DELIVERED it. This tool measures the first
one, training-free and in the round's own metric, before any model is built.

The mechanism it was built for: with N_hf_train small, the affine design
`[X_hf, 1]` (N_hf x (d+1)) can be RANK DEFICIENT. Every direction in its null
space is a component of the true condition->field law that NO estimator can see
from the HF rows alone, whatever its capacity. LF rows at DIFFERENT conditions
span those directions. The tool quantifies:

  1. how affine the task is at each rung (exact-LOO ridge; on `ifc_poisson` the
     answer was 3.2e-08, i.e. the benchmark is a closed-form linear map);
  2. how many affine directions the HF training rows cannot determine, and what
     fraction of the true law's coefficient energy lives there;
  3. the resulting HARD FLOOR for any HF-only estimator (the min-norm pinv fit,
     which attains the analytic row-space projection of the true law);
  4. what an LF rung + one scalar fitted on the HF train rows actually scores,
     and what a rung-affine base + an HF-row affine residual scores (the
     value-of-LF certificate, in skill units);
  5. whether the LF rungs recover the unidentifiable direction (cosine and gain
     against the ORACLE law), which is the diagnostic that says WHY they help.

RELATION TO `condition_identifiable_rank.py` (r2s1-B1)
-----------------------------------------------------
Different axis; run both. That tool asks whether the CONDITION can predict the
coefficient of each POD mode of the field (out-of-fold R^2 per mode, on the train
split) -- an information ceiling in FIELD-basis coordinates, with no LF rungs in
it. This tool asks whether the FEW HF TRAINING ROWS span the condition-side
design at all, and prices the LF rungs at other conditions as the fix -- an
information ceiling in CONDITION-side coordinates. `condition_identifiable_rank`
answers "is the answer predictable from cond?"; this answers "do my 5 rows let me
FIT the predictor, and do the LF rows complete it?". A dataset can be
COEFFICIENT_UNIDENTIFIABLE there and rank-deficient here for unrelated reasons.

LEGITIMACY DISCIPLINE (the reason the numbers are usable)
---------------------------------------------------------
Every claimable estimator here is fitted on LF rungs + the HF TRAIN rows only.
Test HF fields are touched in exactly two ways: to score, and to build quantities
whose keys are suffixed `_ORACLE` (the oracle affine law, used only to say WHERE
in coefficient space an estimator is wrong). Never quote an `_ORACLE` key as an
arm score. Exact condition-overlap counts are computed and reported so a
"disjoint conditions" claim is verified rather than assumed.

USAGE
-----
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/affine_ladder_voi.py --datasets ifc_poisson --out voi_ifc.json
  # affinity scan only (cheap; no ladder / no rank work), several datasets:
  python tools/affine_ladder_voi.py \
      --datasets ifc_poisson,sharp__allen_cahn_2d,ext__helmholtz_2d \
      --affinity_only --quadratic --out panel_affinity.json

Pure numpy (+ torch only for the bilinear rung upsample) on the login node.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROUND_ROOT = HERE.parent
sys.path.insert(0, str(ROUND_ROOT / "eval"))
from nrmse import nrmse, NRMSE_DEF_HASH  # noqa: E402
from panel_data import load_config, repo_root  # noqa: E402

CFG = load_config()
ROOT = repo_root()

ALPHAS = [0.0, 1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1.0]
RESID_ALPHAS = [1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0]


# ── data ────────────────────────────────────────────────────────────

def _factory_import():
    factory_root = ROOT / CFG["paths"]["factory_root"]
    if str(factory_root) not in sys.path:
        sys.path.insert(0, str(factory_root))
    from data_adapters.loaders import load_mf_dataset  # noqa: E402
    from data_adapters.geometry import resolve_grid  # noqa: E402
    return load_mf_dataset, resolve_grid


def _to_grid(y_flat, src_grid, dst_grid):
    """(N, prod(src)) flat -> (N, Hd*Wd) flat, bilinear.

    Byte-equivalent to the round-1/zoo `_to_grid` upsample convention
    (`mf_fno_transfer_film._to_grid`): torch bilinear, align_corners=False.
    """
    import torch
    import torch.nn.functional as F
    Hs, Ws = int(src_grid[0]), int(src_grid[1])
    Hd, Wd = int(dst_grid[0]), int(dst_grid[1])
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32)).view(-1, 1, Hs, Ws)
    if (Hs, Ws) != (Hd, Wd):
        t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float64).reshape(t.shape[0], -1)


def load_rungs(dataset, data_root_key, max_test=None):
    load_mf_dataset, resolve_grid = _factory_import()
    ddir = ROOT / CFG["paths"][data_root_key] / dataset
    if not ddir.exists():
        raise SystemExit(f"dataset dir not found: {ddir}")
    train = load_mf_dataset(ddir, "train")
    test = load_mf_dataset(ddir, "test")
    hf = int(train["hf_fid"])
    if hf not in test["fids"]:
        hf = int(test["hf_fid"])
    grids = {int(f): resolve_grid(dataset, int(train["n_cells_by_fid"][f]))
             for f in train["fids"]}
    hf_grid = grids[hf]
    if data_root_key == "stripped_data_root" and len(test["fids"]) != 1:
        print(f"[warn] stripped test split for {dataset} carries fids {test['fids']}",
              file=sys.stderr)

    rung = {}
    for f in sorted(int(x) for x in train["fids"]):
        Xf = np.asarray(train["cond_by_fid"][f], dtype=np.float64)
        Yn = np.asarray(train["field_by_fid"][f], dtype=np.float64)
        rung[f] = dict(X=Xf, Y_native=Yn.reshape(Xf.shape[0], -1),
                       Y_up=_to_grid(Yn, grids[f], hf_grid),
                       grid=[int(grids[f][0]), int(grids[f][1])], n=int(Xf.shape[0]))
    X_te = np.asarray(test["cond_by_fid"][hf], dtype=np.float64)
    Y_te = np.asarray(test["field_by_fid"][hf], dtype=np.float64).reshape(X_te.shape[0], -1)
    if max_test is not None and X_te.shape[0] > max_test:
        X_te, Y_te = X_te[:max_test], Y_te[:max_test]
    return dict(rung=rung, hf=hf, hf_grid=[int(hf_grid[0]), int(hf_grid[1])],
                X_te=X_te, Y_te=Y_te)


def skill_denominator(dataset, override=None):
    if override is not None:
        return float(override), "cli_override"
    fl = ROUND_ROOT / "state" / "anchors" / "floors.json"
    d = json.loads(fl.read_text())
    if dataset not in d or "reference" not in d[dataset]:
        raise SystemExit(f"no reference floor for {dataset} in {fl}; pass --skill_denominator")
    return float(d[dataset]["reference"]["test_nrmse"]), str(fl)


# ── linear algebra (the turn-2 definitions, unchanged) ───────────────

def ridge_fit(X, Y, alpha):
    Xd = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1).astype(np.float64)
    d = Xd.shape[1]
    A = Xd.T @ Xd + alpha * np.eye(d)
    A[-1, -1] -= alpha              # never penalise the intercept
    return np.linalg.solve(A, Xd.T @ Y.astype(np.float64))


def ridge_apply(W, X):
    Xd = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1).astype(np.float64)
    return Xd @ W


def loo_rel_residual(X, Y, alpha):
    """Exact LOO for ridge with a shared design: mean_i ||r_i|| / ||y_i||."""
    Xd = np.concatenate([X, np.ones((X.shape[0], 1))], axis=1).astype(np.float64)
    d = Xd.shape[1]
    A = Xd.T @ Xd + alpha * np.eye(d)
    A[-1, -1] -= alpha
    Ai = np.linalg.inv(A)
    Hd = np.einsum("ij,jk,ik->i", Xd, Ai, Xd)
    Yf = Y.astype(np.float64)
    R = Yf - Xd @ (Ai @ (Xd.T @ Yf))
    R = R / np.maximum(1.0 - Hd, 1e-12)[:, None]
    return float(np.mean(np.linalg.norm(R, axis=1) / np.linalg.norm(Yf, axis=1)))


def select_alpha(X, Y, alphas=ALPHAS):
    best, ba = np.inf, alphas[0]
    for a in alphas:
        try:
            v = loo_rel_residual(X, Y, a)
        except np.linalg.LinAlgError:
            continue
        if np.isfinite(v) and v < best:
            best, ba = v, a
    return ba, best


def scale_fit(P, Y):
    return float((P * Y).sum() / max((P * P).sum(), 1e-300))


def quad_lift(X):
    cols = [X]
    d = X.shape[1]
    for i in range(d):
        for j in range(i, d):
            cols.append((X[:, i] * X[:, j])[:, None])
    return np.concatenate(cols, axis=1)


# ── the probe ───────────────────────────────────────────────────────

def affinity_block(data, quadratic=False):
    """A1: how affine is the map cond->field, per rung and (ORACLE) on test."""
    out = {}
    for f, r in sorted(data["rung"].items()):
        if r["n"] <= r["X"].shape[1] + 2:
            out[str(f)] = {"n": r["n"], "note": "n <= cond_dim+2, LOO undefined"}
            continue
        a, v = select_alpha(r["X"], r["Y_native"])
        rec = {"n": r["n"], "grid": r["grid"], "alpha": a,
               "affine_loo_rel_residual_native_grid": v}
        if quadratic:
            Xq = quad_lift(r["X"])
            if r["n"] > Xq.shape[1] + 2:
                aq, vq = select_alpha(Xq, r["Y_native"])
                rec["quadratic_loo_rel_residual"] = vq
        out[str(f)] = rec
    X_te, Y_te = data["X_te"], data["Y_te"]
    a, v = select_alpha(X_te, Y_te)
    rec = {"n": int(X_te.shape[0]), "alpha": a, "affine_loo_rel_residual": v,
           "note": "fitted on TEST rows -- ORACLE characterisation of how affine "
                   "the HF map is; never a scored prediction"}
    if quadratic:
        Xq = quad_lift(X_te)
        if X_te.shape[0] > Xq.shape[1] + 2:
            _, vq = select_alpha(Xq, Y_te)
            rec["quadratic_loo_rel_residual"] = vq
    out["test_hf_ORACLE"] = rec
    return out


def run_dataset(dataset, args):
    t0 = time.time()
    data = load_rungs(dataset, args.data_root_key, args.max_test)
    bar, bar_src = skill_denominator(dataset, args.skill_denominator)
    hf = data["hf"]
    rung, X_te, Y_te = data["rung"], data["X_te"], data["Y_te"]
    X_hf, Y_hf = rung[hf]["X"], rung[hf]["Y_up"]
    d = X_te.shape[1]

    def sk(P):
        return nrmse(P, Y_te) / bar

    out = {"dataset": dataset, "_nrmse_def_hash": NRMSE_DEF_HASH,
           "skill_denominator": bar, "skill_denominator_source": bar_src,
           "cond_dim": d, "hf_fid": hf, "hf_grid": data["hf_grid"],
           "n_hf_train": int(X_hf.shape[0]), "n_test": int(X_te.shape[0]),
           "rungs": {str(f): {"n": r["n"], "grid": r["grid"]} for f, r in rung.items()}}

    out["A1_affinity_loo"] = affinity_block(data, quadratic=args.quadratic)
    if args.affinity_only:
        out["_wall_seconds"] = round(time.time() - t0, 1)
        return out

    # ---- A2 rank / null space of the HF training design ---------------
    Xd_hf = np.concatenate([X_hf, np.ones((X_hf.shape[0], 1))], axis=1)
    U, S, Vt = np.linalg.svd(Xd_hf, full_matrices=True)
    n_res = int(np.sum(S > args.rank_tol * max(S.max(), 1e-300)))
    null_dirs = Vt[n_res:]                      # (d+1-n_res, d+1)
    alpha_or, _ = select_alpha(X_te, Y_te)
    W_or = ridge_fit(X_te, Y_te, alpha_or)      # ORACLE affine law
    proj_null = null_dirs @ W_or
    W_rowspace = Vt[:n_res].T @ (Vt[:n_res] @ W_or)
    a2 = {
        "design_shape": list(Xd_hf.shape),
        "singular_values": S.tolist(),
        "numerical_rank": n_res,
        "n_unresolved_affine_directions": int(null_dirs.shape[0]),
        "null_directions": null_dirs.tolist(),
        "frac_of_ORACLE_law_energy_in_null": float(
            (proj_null ** 2).sum() / max((W_or ** 2).sum(), 1e-300)),
        "skill_of_ORACLE_law_projected_to_hf_rowspace": sk(ridge_apply(W_rowspace, X_te)),
        "oracle_law_insample_nrmse_ORACLE": nrmse(ridge_apply(W_or, X_te), Y_te),
    }
    out["A2_hf_design_rank"] = a2

    # ---- A3 HF-only controls, incl. the min-norm information limit ----
    a3 = {}
    for a in ALPHAS:
        try:
            W5 = ridge_fit(X_hf, Y_hf, a)
        except np.linalg.LinAlgError:
            continue
        a3[f"ridge_alpha_{a:g}"] = {"skill": sk(ridge_apply(W5, X_te)),
                                    "train_nrmse": nrmse(ridge_apply(W5, X_hf), Y_hf)}
    W_mn = np.linalg.pinv(Xd_hf) @ Y_hf     # the honest alpha->0 limit
    a3["min_norm_pinv"] = {"skill": sk(ridge_apply(W_mn, X_te)),
                           "train_nrmse": nrmse(ridge_apply(W_mn, X_hf), Y_hf),
                           "note": "HF-only INFORMATION LIMIT: with a rank-deficient "
                                   "design this equals the row-space projection of the "
                                   "true law (compare A2)"}
    mu = Y_hf.mean(0, keepdims=True)
    a3["train_mean"] = {"skill": sk(np.repeat(mu, Y_te.shape[0], 0))}
    a3["zero"] = {"skill": sk(np.zeros_like(Y_te))}
    out["A3_hf_only_controls"] = a3

    # ---- A4 per-LF-rung affine transfer, scale from HF TRAIN rows -----
    a4, a5, a6 = {}, {}, {}
    lf_fids = [f for f in sorted(rung) if f != hf]
    for f in lf_fids:
        r = rung[f]
        a_f = (out["A1_affinity_loo"].get(str(f), {}) or {}).get("alpha", 0.0)
        W = ridge_fit(r["X"], r["Y_up"], a_f)
        P_te, P_hf = ridge_apply(W, X_te), ridge_apply(W, X_hf)
        c_legit = scale_fit(P_hf, Y_hf)
        c_theory = (r["grid"][0] / data["hf_grid"][0]) ** 2
        a4[str(f)] = {
            "alpha": a_f, "n_rows": r["n"], "grid": r["grid"],
            "skill_no_scale": sk(P_te),
            "c_LEGIT_from_hf_train_rows": c_legit,
            "skill_LEGIT_scaled": sk(c_legit * P_te),
            "c_ORACLE_from_test": scale_fit(P_te, Y_te),
            "skill_ORACLE_scaled_ORACLE": sk(scale_fit(P_te, Y_te) * P_te),
            "c_predicted_by_grid_ratio_squared": c_theory,
            "c_legit_over_grid_ratio_squared": c_legit / max(c_theory, 1e-300),
        }
        # ---- A5 rung-affine base + HF-row affine residual (the certificate)
        base_hf, base_te = c_legit * P_hf, c_legit * P_te
        sweep = {}
        for a2r in RESID_ALPHAS:
            Wr = ridge_fit(X_hf, Y_hf - base_hf, a2r)
            sweep[f"{a2r:g}"] = {
                "skill": sk(base_te + ridge_apply(Wr, X_te)),
                "loo_on_hf_train_rows": loo_rel_residual(X_hf, Y_hf - base_hf, a2r)}
        a_sel = min(sweep, key=lambda k: sweep[k]["loo_on_hf_train_rows"])
        a5[str(f)] = {"base_skill": sk(base_te),
                      "alpha_selected_by_LOO_on_hf_train_rows": a_sel,
                      "skill_at_LOO_selected_alpha": sweep[a_sel]["skill"],
                      "best_skill_over_sweep": min(v["skill"] for v in sweep.values()),
                      "worst_skill_over_sweep": max(v["skill"] for v in sweep.values()),
                      "sweep": sweep}
        # ---- A6 does this rung recover the unidentifiable direction? ---
        Wl = W * c_legit
        cos_c = ((Wl * W_or).sum(1) / np.maximum(
            np.linalg.norm(Wl, axis=1) * np.linalg.norm(W_or, axis=1), 1e-300))
        rec = {"overall_law_rel_l2_vs_ORACLE": float(
                   np.linalg.norm(Wl - W_or) / max(np.linalg.norm(W_or), 1e-300)),
               "cos_per_coefficient_field_vs_ORACLE": dict(zip(
                   [f"w{i}" for i in range(d)] + ["intercept"], cos_c.tolist()))}
        if null_dirs.shape[0] > 0:
            v_net = (null_dirs @ Wl).ravel()
            v_or = proj_null.ravel()
            rec["null_direction_cos_vs_ORACLE"] = float(
                v_net @ v_or / max(np.linalg.norm(v_net) * np.linalg.norm(v_or), 1e-300))
            rec["null_direction_recovery_ratio"] = float(
                (v_net @ v_or) / max(v_or @ v_or, 1e-300))
            rec["frac_of_law_energy_in_null_direction"] = float(
                (v_net ** 2).sum() / max((Wl ** 2).sum(), 1e-300))
        a6[str(f)] = rec

    # ---- A4b all LF rungs jointly, grid-ratio normalised --------------
    if lf_fids:
        Xs = [rung[f]["X"] for f in lf_fids]
        Ys = [rung[f]["Y_up"] * ((rung[f]["grid"][0] / data["hf_grid"][0]) ** 2)
              for f in lf_fids]
        Xj, Yj = np.concatenate(Xs), np.concatenate(Ys)
        aj, vj = select_alpha(Xj, Yj)
        Wj = ridge_fit(Xj, Yj, aj)
        Pj_te, Pj_hf = ridge_apply(Wj, X_te), ridge_apply(Wj, X_hf)
        cj = scale_fit(Pj_hf, Y_hf)
        a4["joint_all_lf_rungs_grid_normalised"] = {
            "alpha": aj, "affine_loo_rel_residual": vj, "n_rows": int(Xj.shape[0]),
            "c_LEGIT_from_hf_train_rows": cj, "skill_LEGIT_scaled": sk(cj * Pj_te)}
    out["A4_lf_rung_affine_transfer"] = a4
    out["A5_rung_affine_plus_hf_row_residual"] = a5
    out["A6_coefficient_agreement_vs_ORACLE"] = a6

    # ---- A7 exact condition-overlap integrity -------------------------
    def key(A):
        return {tuple(np.round(r, 12)) for r in A}
    kt, kh = key(X_te), key(X_hf)
    a7 = {"n_test_conds": len(kt), "n_hf_train_conds": len(kh),
          "test_cap_hf_train": len(kt & kh)}
    for f in lf_fids:
        kf = key(rung[f]["X"])
        a7[f"rung{f}_cap_test"] = len(kf & kt)
        a7[f"rung{f}_cap_hf_train"] = len(kf & kh)
    out["A7_exact_condition_overlap"] = a7

    # ---- verdict ------------------------------------------------------
    limit = a3["min_norm_pinv"]["skill"]
    best_lf = min((a5[k]["skill_at_LOO_selected_alpha"] for k in a5), default=None)
    best_rung = (min(a5, key=lambda k: a5[k]["skill_at_LOO_selected_alpha"])
                 if a5 else None)
    aff = out["A1_affinity_loo"]["test_hf_ORACLE"]["affine_loo_rel_residual"]
    out["verdict"] = {
        "hf_only_information_limit_skill": limit,
        "best_lf_assisted_skill_LEGIT": best_lf,
        "best_rung": best_rung,
        "value_of_lf_skill_units": (None if best_lf is None else limit - best_lf),
        "hf_design_rank_deficient": bool(null_dirs.shape[0] > 0),
        "affine_task": bool(aff < 1e-3),
        "label": ("RANK_LIMITED_LF_COMPLETES" if (null_dirs.shape[0] > 0 and best_lf is not None
                                                  and best_lf < limit)
                  else "RANK_LIMITED_LF_DOES_NOT_COMPLETE" if null_dirs.shape[0] > 0
                  else "HF_DESIGN_FULL_RANK"),
    }
    out["_wall_seconds"] = round(time.time() - t0, 1)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--datasets", required=True, help="comma-separated dataset names")
    ap.add_argument("--out", default=None, help="output JSON path")
    ap.add_argument("--data_root", default="stripped",
                    choices=["stripped", "orig"],
                    help="stripped (default; models' view) or orig")
    ap.add_argument("--affinity_only", action="store_true",
                    help="A1 only: cheap per-dataset affinity scan")
    ap.add_argument("--quadratic", action="store_true",
                    help="also report a quadratic-lift LOO residual in A1")
    ap.add_argument("--max_test", type=int, default=None)
    ap.add_argument("--rank_tol", type=float, default=1e-10,
                    help="relative singular-value tolerance for the design rank")
    ap.add_argument("--skill_denominator", type=float, default=None,
                    help="override; default = floors.json <ds>.reference.test_nrmse")
    args = ap.parse_args()
    args.data_root_key = ("stripped_data_root" if args.data_root == "stripped"
                          else "data_root")

    res = {"_tool": "affine_ladder_voi.py", "_nrmse_def_hash": NRMSE_DEF_HASH,
           "_data_root": args.data_root, "datasets": {}}
    for ds in [s.strip() for s in args.datasets.split(",") if s.strip()]:
        r = run_dataset(ds, args)
        res["datasets"][ds] = r
        if args.affinity_only:
            print(f"[{ds}] affine LOO (test, ORACLE) = "
                  f"{r['A1_affinity_loo']['test_hf_ORACLE']['affine_loo_rel_residual']:.4g}",
                  flush=True)
        else:
            v = r["verdict"]
            print(f"[{ds}] rank={r['A2_hf_design_rank']['numerical_rank']}"
                  f"/{r['A2_hf_design_rank']['design_shape'][1]} "
                  f"null_energy={r['A2_hf_design_rank']['frac_of_ORACLE_law_energy_in_null']:.4f} "
                  f"limit={v['hf_only_information_limit_skill']:.4f} "
                  f"best_lf={v['best_lf_assisted_skill_LEGIT']} "
                  f"voi={v['value_of_lf_skill_units']} {v['label']}", flush=True)
    txt = json.dumps(res, indent=1)
    if args.out:
        Path(args.out).write_text(txt)
        print(f"wrote {args.out}", flush=True)
    else:
        print(txt)


if __name__ == "__main__":
    main()
