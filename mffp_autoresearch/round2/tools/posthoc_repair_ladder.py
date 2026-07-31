#!/usr/bin/env python
"""How much of a trained arm's error is LEGITIMATELY repairable after the fact --
and where its implicit affine law sits relative to what its training rows could see.

Provenance: promoted from `r2s3_lf_train_signal-B1` mechanism turn 3 (parts C, D, E),
`worktrees/r2s3_lf_train_signal/B1/scratchpad/reanalysis_turn_3.py` and
`.../reanalysis_turn_3b.py`.

WHY THIS EXISTS
---------------
A card that ships a bad number needs to know which of four things it bought:
a mis-scaled prediction, a spectrally contaminated one, a mis-fitted low-band
law, or a genuinely uninformed model. Those have completely different B(N+1)
levers, and three of the four are visible WITHOUT retraining. This tool applies,
in order, the repairs a next batch could bake in, each fitted on the HF TRAINING
rows only, and prices each in skill units:

  L0  raw                                   (the shipped number, rebuilt)
  L1  + one global scale fitted on HF train rows
  L2  + an ideal radial low-pass, cutoff selected on HF train rows
  L3  + an affine residual correction on HF train rows (ridge alpha by exact LOO)
  L4  L2 then L3

Each rung also reports its ORACLE twin (scale/cutoff chosen on test). A large
ORACLE-vs-LEGIT gap is itself the finding: it means the defect is INVISIBLE from
the training rows, so no gate, early-stopping rule or calibration fitted on them
can catch it (that is how r2s3-B1 found a 647-skill arm whose legitimate 5-row
scale was 0.956).

THE AFFINE-ISATION HALF (optional, `--cond_probe/--pred_probe`)
---------------------------------------------------------------
A condition->field net is a deterministic map, so it has a best affine surrogate.
Evaluate the net at a design of RANDOM conditions (no field data is read to build
it -- use `--gen_probe_conds` to emit the design, feed it to your family, feed the
predictions back), and the tool reports:
  * the net's NON-AFFINITY: rel-L2 of (net - its own affine surrogate) on held-out
    probe conditions, and what deleting the non-affine part is worth in skill;
  * the net's implicit 6-coefficient law against the ORACLE law (per-coefficient
    cosines, overall rel-L2);
  * the NULL-DIRECTION diagnostic: the component of the law living in the null
    space of the HF training design -- the direction the training rows cannot
    constrain. `cos ~ -1` there means the network is confidently extrapolating
    the WRONG way in a direction its data never saw (r2s3-B1 found exactly that
    in a no-LF control: 27.7% of its law energy, cos -0.99, against a min-norm
    least-squares solution that puts zero there);
  * coefficient-space SURGERY (ORACLE, diagnostic): row-space and null parts
    swapped against the true law, so "is the model wrong where it could have
    known, or where it could not?" gets a number instead of an opinion.

Pair with `tools/affine_ladder_voi.py`, which computes the same rank/null geometry
training-free and prices the LF rungs that can fill the null direction. This tool
is the model-facing half: run VOI first to learn the ceiling, this one to see
where your arm sits against it.

LEGITIMACY DISCIPLINE
---------------------
Every key WITHOUT an `_ORACLE` suffix is fitted on the HF training rows only.
Every key WITH it is fitted on test and is a diagnostic; it may never be quoted
as an arm score.

USAGE
-----
  source "$PROJECT_ROOT/.venv/bin/activate"
  # 1. emit a probe condition design (optional half)
  python tools/posthoc_repair_ladder.py --dataset ifc_poisson \
      --gen_probe_conds 320 --probe_box 0.10,0.90 --probe_out probe_conds.npy
  #    ... run your family's forward pass on probe_conds.npy -> probe_preds.npy ...
  # 2. the ladder
  python tools/posthoc_repair_ladder.py --dataset ifc_poisson \
      --pred_test preds_test.npz:pred --pred_hf_train preds_train.npy \
      --cond_probe probe_conds.npy --pred_probe probe_preds.npy \
      --out repair_ladder.json

`--pred_*` accept `path.npy` or `path.npz:key`. Shapes (N, H, W) or (N, n_cells).
Pure numpy on the login node.
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
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROUND_ROOT / "eval"))
from nrmse import nrmse, NRMSE_DEF_HASH  # noqa: E402
from affine_ladder_voi import (  # noqa: E402
    load_rungs, skill_denominator, ridge_fit, ridge_apply, loo_rel_residual,
    scale_fit, select_alpha, RESID_ALPHAS,
)

DEFAULT_CUTOFFS = "2,3,4,6,8,12,16,24,32,64"


def load_pred(spec, n_expect, n_cells):
    if spec is None:
        return None
    if ":" in spec and not Path(spec).exists():
        path, key = spec.rsplit(":", 1)
        arr = np.load(path)[key]
    else:
        p = Path(spec)
        if p.suffix == ".npz":
            z = np.load(p)
            arr = z[z.files[0]]
        else:
            arr = np.load(p)
    arr = np.asarray(arr, dtype=np.float64).reshape(arr.shape[0], -1)
    if arr.shape[0] != n_expect or arr.shape[1] != n_cells:
        raise SystemExit(f"{spec}: got {arr.shape}, expected ({n_expect}, {n_cells})")
    return arr


def lowpass(P_flat, grid, kc):
    """Ideal radial low-pass |k| <= kc. P_flat (N, H*W)."""
    H, W = int(grid[0]), int(grid[1])
    P = P_flat.reshape(-1, H, W)
    F = np.fft.rfft2(P)
    ky = np.fft.fftfreq(H) * H
    kx = np.fft.rfftfreq(W) * W
    K = np.sqrt(ky[:, None] ** 2 + kx[None, :] ** 2)
    F = F * (K <= kc)[None]
    return np.fft.irfft2(F, s=(H, W)).reshape(P_flat.shape)


def residual_repair(base_hf, Y_hf, X_hf, base_te, X_te, Y_te, bar):
    sweep = {}
    for a in RESID_ALPHAS:
        Wr = ridge_fit(X_hf, Y_hf - base_hf, a)
        P = base_te + ridge_apply(Wr, X_te)
        sweep[f"{a:g}"] = {"skill": nrmse(P, Y_te) / bar,
                           "loo_on_hf_train_rows": loo_rel_residual(
                               X_hf, Y_hf - base_hf, a)}
    a_sel = min(sweep, key=lambda k: sweep[k]["loo_on_hf_train_rows"])
    return {"alpha_selected_by_LOO_on_hf_train_rows": a_sel,
            "skill_at_LOO_selected_alpha": sweep[a_sel]["skill"],
            "best_skill_over_sweep_ORACLE": min(v["skill"] for v in sweep.values()),
            "worst_skill_over_sweep": max(v["skill"] for v in sweep.values()),
            "sweep": sweep}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--pred_test", default=None, help="path.npy | path.npz:key")
    ap.add_argument("--pred_hf_train", default=None,
                    help="the arm's predictions AT THE HF TRAIN CONDITIONS")
    ap.add_argument("--cond_probe", default=None)
    ap.add_argument("--pred_probe", default=None)
    ap.add_argument("--gen_probe_conds", type=int, default=0,
                    help="emit a random condition design of this size and exit")
    ap.add_argument("--probe_box", default=None,
                    help="lo,hi for the probe design; default = the LF rungs' own box")
    ap.add_argument("--probe_out", default="probe_conds.npy")
    ap.add_argument("--probe_fit_frac", type=float, default=0.6)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--cutoffs", default=DEFAULT_CUTOFFS)
    ap.add_argument("--data_root", default="stripped", choices=["stripped", "orig"])
    ap.add_argument("--max_test", type=int, default=None)
    ap.add_argument("--rank_tol", type=float, default=1e-10)
    ap.add_argument("--skill_denominator", type=float, default=None)
    ap.add_argument("--arm_name", default="arm")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    t0 = time.time()
    data_root_key = "stripped_data_root" if args.data_root == "stripped" else "data_root"
    data = load_rungs(args.dataset, data_root_key, args.max_test)
    hf, grid = data["hf"], data["hf_grid"]
    X_te, Y_te = data["X_te"], data["Y_te"]
    X_hf, Y_hf = data["rung"][hf]["X"], data["rung"][hf]["Y_up"]
    n_cells = Y_te.shape[1]

    if args.gen_probe_conds:
        if args.probe_box:
            lo, hi = [float(x) for x in args.probe_box.split(",")]
            lo = np.full(X_hf.shape[1], lo); hi = np.full(X_hf.shape[1], hi)
        else:
            allX = np.concatenate([r["X"] for r in data["rung"].values()])
            lo, hi = allX.min(0), allX.max(0)
        rng = np.random.default_rng(args.seed)
        Xr = rng.uniform(lo, hi, size=(args.gen_probe_conds, X_hf.shape[1]))
        np.save(args.probe_out, Xr)
        print(f"wrote {args.probe_out} shape={Xr.shape} box={lo.tolist()}..{hi.tolist()}\n"
              f"NOTE: conditions only -- no field data was read to build this design.",
              flush=True)
        return

    if not (args.pred_test and args.pred_hf_train):
        raise SystemExit("--pred_test and --pred_hf_train are required "
                         "(or use --gen_probe_conds)")
    bar, bar_src = skill_denominator(args.dataset, args.skill_denominator)
    P_te = load_pred(args.pred_test, X_te.shape[0], n_cells)
    P_hf = load_pred(args.pred_hf_train, X_hf.shape[0], n_cells)

    def sk(P):
        return nrmse(P, Y_te) / bar

    out = {"_tool": "posthoc_repair_ladder.py", "_nrmse_def_hash": NRMSE_DEF_HASH,
           "dataset": args.dataset, "arm": args.arm_name,
           "skill_denominator": bar, "skill_denominator_source": bar_src,
           "n_test": int(X_te.shape[0]), "n_hf_train": int(X_hf.shape[0]),
           "hf_grid": grid, "cond_dim": int(X_te.shape[1])}

    # ---- L0 raw / L1 global scale --------------------------------------
    c_legit = scale_fit(P_hf, Y_hf)
    c_oracle = scale_fit(P_te, Y_te)
    out["L0_raw"] = {"skill": sk(P_te), "train_row_nrmse": nrmse(P_hf, Y_hf)}
    out["L1_global_scale"] = {
        "c_LEGIT_from_hf_train_rows": c_legit, "skill": sk(c_legit * P_te),
        "c_ORACLE_from_test": c_oracle, "skill_ORACLE": sk(c_oracle * P_te),
        "note": "a large LEGIT-vs-ORACLE gap means the miscalibration is INVISIBLE "
                "from the training rows -- no train-row gate can catch it"}

    # ---- L2 low-pass -----------------------------------------------------
    cutoffs = [int(x) for x in args.cutoffs.split(",")]
    per = {}
    for kc in cutoffs:
        Pk, Pktr = lowpass(P_te, grid, kc), lowpass(P_hf, grid, kc)
        per[str(kc)] = {"test_skill": sk(Pk), "train_row_nrmse": nrmse(Pktr, Y_hf),
                        "target_truncation_ceiling_skill": sk(lowpass(Y_te, grid, kc))}
    kc_legit = min(per, key=lambda k: per[k]["train_row_nrmse"])
    kc_oracle = min(per, key=lambda k: per[k]["test_skill"])
    out["L2_lowpass"] = {
        "per_cutoff": per,
        "cutoff_selected_on_hf_train_rows": int(kc_legit),
        "skill": per[kc_legit]["test_skill"],
        "gain_skill_units": out["L0_raw"]["skill"] - per[kc_legit]["test_skill"],
        "cutoff_ORACLE": int(kc_oracle),
        "skill_ORACLE": per[kc_oracle]["test_skill"],
        "gain_skill_units_ORACLE": out["L0_raw"]["skill"] - per[kc_oracle]["test_skill"]}

    # ---- L3 / L4 affine residual on the HF train rows --------------------
    out["L3_affine_residual"] = residual_repair(
        c_legit * P_hf, Y_hf, X_hf, c_legit * P_te, X_te, Y_te, bar)
    Pk_te, Pk_hf = lowpass(P_te, grid, int(kc_legit)), lowpass(P_hf, grid, int(kc_legit))
    ck = scale_fit(Pk_hf, Y_hf)
    out["L4_lowpass_then_residual"] = residual_repair(
        ck * Pk_hf, Y_hf, X_hf, ck * Pk_te, X_te, Y_te, bar)

    best = min([("L0_raw", out["L0_raw"]["skill"]),
                ("L1_global_scale", out["L1_global_scale"]["skill"]),
                ("L2_lowpass", out["L2_lowpass"]["skill"]),
                ("L3_affine_residual", out["L3_affine_residual"]["skill_at_LOO_selected_alpha"]),
                ("L4_lowpass_then_residual",
                 out["L4_lowpass_then_residual"]["skill_at_LOO_selected_alpha"])],
               key=lambda kv: kv[1])
    out["best_legitimate_repair"] = {"rung": best[0], "skill": best[1],
                                     "total_gain_skill_units": out["L0_raw"]["skill"] - best[1]}

    # ---- affine-isation + null-direction (optional) -----------------------
    if args.cond_probe and args.pred_probe:
        Xr = np.asarray(np.load(args.cond_probe), dtype=np.float64)
        Pr = load_pred(args.pred_probe, Xr.shape[0], n_cells)
        n_fit = int(round(args.probe_fit_frac * Xr.shape[0]))
        if n_fit <= Xr.shape[1] + 1 or n_fit >= Xr.shape[0]:
            raise SystemExit("probe design too small for --probe_fit_frac")
        Wn = ridge_fit(Xr[:n_fit], Pr[:n_fit], 0.0)
        nonaff = float(np.linalg.norm(ridge_apply(Wn, Xr[n_fit:]) - Pr[n_fit:])
                       / max(np.linalg.norm(Pr[n_fit:]), 1e-300))
        cN = scale_fit(ridge_apply(Wn, X_hf), Y_hf)
        Wl = Wn * cN

        alpha_or, _ = select_alpha(X_te, Y_te)
        W_or = ridge_fit(X_te, Y_te, alpha_or)
        Xd_hf = np.concatenate([X_hf, np.ones((X_hf.shape[0], 1))], axis=1)
        U, S, Vt = np.linalg.svd(Xd_hf, full_matrices=True)
        n_res = int(np.sum(S > args.rank_tol * max(S.max(), 1e-300)))
        null_dirs, row_dirs = Vt[n_res:], Vt[:n_res]

        cosc = ((Wl * W_or).sum(1) / np.maximum(
            np.linalg.norm(Wl, axis=1) * np.linalg.norm(W_or, axis=1), 1e-300))
        aff = {"n_probe": int(Xr.shape[0]), "n_fit": n_fit,
               "nonaffinity_rel_l2_on_holdout_probe_conds": nonaff,
               "c_LEGIT_from_hf_train_rows": cN,
               "affine_surrogate_skill_raw": sk(ridge_apply(Wn, X_te)),
               "affine_surrogate_skill_legit_scaled": sk(ridge_apply(Wl, X_te)),
               "overall_law_rel_l2_vs_ORACLE": float(
                   np.linalg.norm(Wl - W_or) / max(np.linalg.norm(W_or), 1e-300)),
               "cos_per_coefficient_field_vs_ORACLE": dict(zip(
                   [f"w{i}" for i in range(X_te.shape[1])] + ["intercept"],
                   cosc.tolist())),
               "hf_design_numerical_rank": n_res,
               "hf_design_singular_values": S.tolist()}
        if null_dirs.shape[0] > 0:
            v_net = (null_dirs @ Wl).ravel()
            v_or = (null_dirs @ W_or).ravel()
            aff["null_direction"] = {
                "vec": null_dirs.tolist(),
                "frac_of_ORACLE_law_energy_in_null": float(
                    (v_or ** 2).sum() / max((W_or ** 2).sum(), 1e-300)),
                "frac_of_ARM_law_energy_in_null": float(
                    (v_net ** 2).sum() / max((Wl ** 2).sum(), 1e-300)),
                "cos_vs_ORACLE": float(v_net @ v_or / max(
                    np.linalg.norm(v_net) * np.linalg.norm(v_or), 1e-300)),
                "recovery_ratio": float((v_net @ v_or) / max(v_or @ v_or, 1e-300)),
                "read_as": "cos ~ +1 & ratio ~ 1: the arm learned the unconstrained "
                           "direction. cos ~ -1: it extrapolates the WRONG way there "
                           "(worse than a min-norm fit, which puts 0). |ratio| >> 1: "
                           "right direction, wrong gain -- a calibration lever."}
            # ORACLE coefficient-space surgery
            def law_skill(W):
                return sk(ridge_apply(W, X_te))
            W_row_net = row_dirs.T @ (row_dirs @ Wl)
            W_null_net = null_dirs.T @ (null_dirs @ Wl)
            W_row_or = row_dirs.T @ (row_dirs @ W_or)
            W_null_or = null_dirs.T @ (null_dirs @ W_or)
            aff["surgery_ORACLE"] = {
                "arm_law": law_skill(Wl),
                "arm_row_only": law_skill(W_row_net),
                "arm_row_plus_oracle_null": law_skill(W_row_net + W_null_or),
                "oracle_row_plus_arm_null": law_skill(W_row_or + W_null_net),
                "oracle_row_only_INFORMATION_LIMIT": law_skill(W_row_or),
                "oracle_law": law_skill(W_or),
                "arm_row_rel_l2_vs_ORACLE": float(
                    np.linalg.norm(W_row_net - W_row_or)
                    / max(np.linalg.norm(W_row_or), 1e-300)),
                "arm_null_rel_l2_vs_ORACLE": float(
                    np.linalg.norm(W_null_net - W_null_or)
                    / max(np.linalg.norm(W_null_or), 1e-300)),
                "note": "ORACLE diagnostic (uses the test-fitted law) -- locates the "
                        "arm's error in coefficient space; never an arm score"}
        out["affine_isation"] = aff

    out["_wall_seconds"] = round(time.time() - t0, 1)
    print(f"[{args.arm_name}/{args.dataset}] L0={out['L0_raw']['skill']:.4f} "
          f"L1={out['L1_global_scale']['skill']:.4f} "
          f"L2(kc={out['L2_lowpass']['cutoff_selected_on_hf_train_rows']})"
          f"={out['L2_lowpass']['skill']:.4f} "
          f"L3={out['L3_affine_residual']['skill_at_LOO_selected_alpha']:.4f} "
          f"L4={out['L4_lowpass_then_residual']['skill_at_LOO_selected_alpha']:.4f} "
          f"-> best {out['best_legitimate_repair']['rung']} "
          f"{out['best_legitimate_repair']['skill']:.4f}", flush=True)
    if "affine_isation" in out:
        a = out["affine_isation"]
        nd = a.get("null_direction", {})
        print(f"    nonaffinity={a['nonaffinity_rel_l2_on_holdout_probe_conds']:.4f} "
              f"law_rel_l2={a['overall_law_rel_l2_vs_ORACLE']:.4f} "
              f"null_cos={nd.get('cos_vs_ORACLE')} "
              f"null_ratio={nd.get('recovery_ratio')}", flush=True)
    txt = json.dumps(out, indent=1)
    if args.out:
        Path(args.out).write_text(txt)
        print(f"wrote {args.out}", flush=True)
    else:
        print(txt)


if __name__ == "__main__":
    main()
