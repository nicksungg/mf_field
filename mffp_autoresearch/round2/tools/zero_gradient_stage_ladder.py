#!/usr/bin/env python
"""How much of a TRAINED stack's test-side value is reachable with ZERO gradient steps.

WHAT THIS ANSWERS
-----------------
A stacked design ships `intermediate -> closed-form stage -> trained corrector ->
blend`. The leaderboard reports one number for the whole stack, so "the trained
corrector works" is never actually tested against "a closed-form stage over the
same intermediate would have done it". This tool builds the ladder that separates
them, every rung selected OUT OF FOLD on a calibration split and read on TEST:

  S0  raw          X_k, the intermediate itself                 0 parameters
  S1  gain         a* . X_k, a* on calib                        1 selection
  S2  lsi          X_k + alpha . (T (*) X_k); T closed-form on  closed form,
                   the fit fold, alpha out of fold on calib     0 GRADIENT STEPS
  S3  blend_raw    lam . X_k  + (1-lam) . base   on calib       2 selections
  S4  blend_lsi    lam . S2   + (1-lam) . base   on calib       2 selections
  S5  free_joint   joint (k, base, lam) on calib                3 selections, 0 fitted
  --- read from the shipped diagnostics, NOT rebuilt ---
  S6  arm          the trained stack at the scored rung
  S7  scored       the shipped blend that was actually scored

and then ATTRIBUTES the scored arm's test-side improvement over S0 to
{closed-form stage, gradient stage, blend stage} in percent and in the round's
SKILL units (nRMSE / copy-LF reference), against the certified
`min_claimable_effect`. Geometry (mean cosine / amplitude ratio / per-sample-gain
oracle = structure-only error) is recorded for every rung this tool builds, so a
gain can be read as AMPLITUDE or as STRUCTURE, and the fitted transfer's dyadic
band gains |1 + alpha.T(k)| say what the spatially-invariant stage does
spectrally.

READ IT AS
----------
`attribution.closed_form_pct` near 100 -> the "trained" arm is a closed-form
filter with a decorative network; the design's expensive variable buys nothing
and the reportable finding is the filter, not the architecture. A large
`S5_free_joint` gap in the other direction -> the fitted stages are real. A
`gradient_pct` that is large on one dataset only -> the corrector is a
dataset-specific rescue, not a class property. Amplitude-only improvements with
falling cosine -> the stage is exploiting the relative-error metric's amplitude
channel (pair with `field_error_decomposition.py`).
Neighbours: `posthoc_repair_ladder.py` asks how much of a SHIPPED arm's error a
next batch could remove post hoc (predictions only, no folds); this asks the
complementary question INSIDE a stack that has already been trained — which of
its own stages earned the number. `surrogate_coherence_eligibility.py` gives the
training-free CEILING for the S2 class; this gives the realised, out-of-fold
value of that class against the trained alternative.
`relative_gain_units_audit.py` converts this tool's output into the decision
statement (skill units vs mce).

FAMILY INTERFACE REQUIRED (`--family_dir`)
------------------------------------------
This tool rebuilds the stack's own intermediates, so it needs the family's
modules rather than a prediction dump. `--family_dir` must expose:
  `folds.make_folds(N, seed, fracs, loo_min_n) -> {"fit","calib","ladder_eval"}`
  `ladders.cond_scaler / neighbour_order / effective_ks / ladder_b_fields`
  `floors.build(Y, X, Xq, arms=..., pool_rows=..., exclude_self=...)`, `floors.FLOOR_ARMS`
  `lsi_filter.fit_transfer(X, R, grid, ridge) / apply_transfer(X, T, grid)`
  `local_corrector.fit_alpha(R, C_raw, X, Y, include_zero=True)`
  `bands.band_masks(grid, bands)`, `bands.N_BANDS`
  `upsample.upsample_fields(F, src_grid, dst_grid, name)`
(the `r2s2_correctability` family of round 2 and any descendant of it). The
shipped diagnostics JSON must carry `M3.kstar.raw_calib_nrmse`,
`M3.scored_rung`, `M3.arm_test_nrmse`, `M3.scored_test_nrmse`,
`M3.reference_splits`, `M3.blend`, `M1[rung].verdict.label` and
`M1c[rung].nrmse_after_lsi`. All four of those are SEAM-CHECKED, not assumed:
the tool asserts nothing and reports every |dev| so a mismatch is visible.

Nothing is fitted on the test split, and no test-side LF array is constructed
(the test rung is built from the TRAIN LF pool + test conditions).

PROVENANCE
----------
`worktrees/r2s2_stacked/B2/scratchpad/reanalysis_turn_3.py`; card
`experiment_cards/r2s2_stacked/batch_2/B2.json` part 6, findings T3/F3.1-F3.6
and interpretation H-STAGE.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

TOOLS = Path(__file__).resolve().parent
ROUND = TOOLS.parent
PROJECT_ROOT = ROUND.parent.parent


def geometry(X, Y, round_nrmse):
    """Per-sample geometry: what part of the error is amplitude, what is structure."""
    nx = np.sqrt((X ** 2).sum(1))
    ny = np.sqrt((Y ** 2).sum(1))
    cos = (X * Y).sum(1) / np.maximum(nx * ny, 1e-300)
    return {
        "nrmse_round": float(round_nrmse(X, Y)),
        "mean_cos": float(cos.mean()),
        "mean_amp_ratio": float((nx / np.maximum(ny, 1e-300)).mean()),
        "structure_only_nrmse": float(np.sqrt(np.clip(1 - cos ** 2, 0, None)).mean()),
    }


def build_parser():
    ap = argparse.ArgumentParser(
        description="zero-gradient stage ladder vs a trained stack (CLI args only)")
    ap.add_argument("--family_dir", required=True,
                    help="model family directory exposing the module interface "
                         "documented in this file's docstring")
    ap.add_argument("--diag_dir", required=True,
                    help="directory holding the shipped per-dataset diagnostics JSONs")
    ap.add_argument("--datasets", required=True,
                    help="comma-separated dataset names (one leg per dataset; a "
                         "4-dataset invocation can exceed a 20-min cap)")
    ap.add_argument("--out", required=True, help="output JSON path")
    ap.add_argument("--rungs", default="1,kstar",
                    help="ladder-B rung labels to build; 'kstar' resolves to the "
                         "shipped scored rung (default: 1,kstar)")
    ap.add_argument("--ks", default="1,2,4,8,16,64,256,all",
                    help="k grid for the intermediate and for S5 (default: the "
                         "r2s2 recipe grid)")
    ap.add_argument("--epochs", type=int, default=200,
                    help="epochs tag used in --diag_pattern")
    ap.add_argument("--seed", type=int, default=0,
                    help="seed tag used in --diag_pattern")
    ap.add_argument("--fold_seed", type=int, default=0)
    ap.add_argument("--fracs", default="0.70,0.15,0.15",
                    help="fit,calib,ladder_eval fractions (must match the job's)")
    ap.add_argument("--loo_min_n", type=int, default=20)
    ap.add_argument("--bases", default="zero,train_mean,nn_condition",
                    help="floor arms available to the blend stages")
    ap.add_argument("--n_lambda", type=int, default=21)
    ap.add_argument("--gain_max", type=float, default=1.5)
    ap.add_argument("--gain_step", type=float, default=0.005)
    ap.add_argument("--diag_pattern",
                    default="diagnostic_{dataset}_e{epochs}_s{seed}.json")
    ap.add_argument("--factory_root", default=str(PROJECT_ROOT / "mf_field" / "factory_mffp"),
                    help="root providing data_adapters (default: repo factory_mffp)")
    ap.add_argument("--eval_dir", default=str(ROUND / "eval"),
                    help="round eval dir providing nrmse.py (metric definition)")
    ap.add_argument("--stripped_data", default=str(ROUND / "stripped_data"))
    ap.add_argument("--floors_json", default=str(ROUND / "state" / "anchors" / "floors.json"))
    ap.add_argument("--copylf_json", default=str(ROUND / "eval" / "copylf_baselines.json"))
    ap.add_argument("--noise_floor_json", default=str(ROUND / "state" / "noise_floor.json"))
    return ap


def main():
    args = build_parser().parse_args()

    fam = Path(args.family_dir).resolve()
    sys.path.insert(0, str(fam))
    sys.path.insert(0, str(Path(args.factory_root).resolve()))
    sys.path.insert(0, str(Path(args.eval_dir).resolve()))

    import bands as bandlib                      # noqa: E402
    import floors as floorlib                    # noqa: E402
    import folds as foldlib                      # noqa: E402
    import ladders as ladlib                     # noqa: E402
    import lsi_filter as lsilib                  # noqa: E402
    import upsample as uplib                     # noqa: E402
    from local_corrector import fit_alpha        # noqa: E402
    from data_adapters import load_mf_dataset    # noqa: E402
    from data_adapters.geometry import resolve_grid   # noqa: E402
    from nrmse import nrmse as round_nrmse       # noqa: E402

    FRACS = tuple(float(x) for x in args.fracs.split(","))
    LAMBDAS = np.linspace(0.0, 1.0, args.n_lambda)
    GAINS = np.round(np.arange(0.0, args.gain_max + args.gain_step / 2, args.gain_step), 6)
    BASES = tuple(b.strip() for b in args.bases.split(",") if b.strip())
    STRIPPED = Path(args.stripped_data)
    DIAG = Path(args.diag_dir)

    frozen = json.loads(Path(args.floors_json).read_text())
    copylf = json.loads(Path(args.copylf_json).read_text())
    nf = {}
    if Path(args.noise_floor_json).exists():
        nf = json.loads(Path(args.noise_floor_json).read_text())

    out = {"_what": "zero-gradient stage ladder vs the trained stack",
           "_tool": "tools/zero_gradient_stage_ladder.py",
           "_args": vars(args),
           "_protocol": {"fracs": list(FRACS), "fold_seed": args.fold_seed,
                         "selection_fold": "calib", "readout": "test",
                         "lambda_grid": args.n_lambda,
                         "gain_grid": [0.0, args.gain_max, args.gain_step]},
           "datasets": {}}

    for name in [d.strip() for d in args.datasets.split(",") if d.strip()]:
        print(f"\n===== {name}", flush=True)
        dg = json.loads((DIAG / args.diag_pattern.format(
            dataset=name, epochs=args.epochs, seed=args.seed)).read_text())
        train = load_mf_dataset(STRIPPED / name, "train")
        test = load_mf_dataset(STRIPPED / name, "test")
        hf = train["hf_fid"]
        lf_rung = max(train["lf_fids"])
        grid = resolve_grid(name, int(train["n_cells_by_fid"][hf]))
        lf_grid = resolve_grid(name, int(train["n_cells_by_fid"][lf_rung]))
        Ytr = np.asarray(train["field_by_fid"][hf], np.float64)
        Xtr = np.asarray(train["cond_by_fid"][hf], np.float64)
        LF_nat = np.asarray(train["field_by_fid"][lf_rung], np.float64)
        Xlf = np.asarray(train["cond_by_fid"][lf_rung], np.float64)
        Yte = np.asarray(test["field_by_fid"][hf], np.float64)
        Cte = np.asarray(test["cond_by_fid"][hf], np.float64)
        LF_up = uplib.upsample_fields(LF_nat, lf_grid, grid, name)
        Ntr, n_pool = Ytr.shape[0], LF_up.shape[0]

        F0 = foldlib.make_folds(Ntr, args.fold_seed, FRACS, args.loo_min_n)
        fit, cal, ev = F0["fit"], F0["calib"], F0["ladder_eval"]
        mu, sd = ladlib.cond_scaler(Xtr)
        self_row = np.arange(Ntr, dtype=np.int64) if n_pool >= Ntr else None
        order_tr = ladlib.neighbour_order(Xtr, Xlf, mu, sd, exclude_self_row=self_row)
        order_te = ladlib.neighbour_order(Cte, Xlf, mu, sd)
        ks = ladlib.effective_ks(args.ks, int(order_tr.shape[1]))
        pool_sum = LF_up.sum(axis=0)
        B_tr = ladlib.ladder_b_fields(LF_up, order_tr, [k for _, k in ks],
                                      pool_sum=pool_sum, self_row=self_row)
        ks_te = ladlib.effective_ks(args.ks, int(order_te.shape[1]))
        B_te = ladlib.ladder_b_fields(LF_up, order_te, [k for _, k in ks_te],
                                      pool_sum=pool_sum, self_row=None)
        k_of = dict(ks)
        k_of_te = dict(ks_te)

        # ── floors: calib-side from the FIT fold only; test-side full train ──
        fit_pos = {int(r): i for i, r in enumerate(fit)}
        base_cal = floorlib.build(Ytr, Xtr, Xtr[cal], arms=BASES, pool_rows=fit,
                                  exclude_self=np.array([fit_pos.get(int(r), -1)
                                                         for r in cal], dtype=np.int64))
        floor_te = floorlib.build(Ytr, Xtr, Cte, arms=floorlib.FLOOR_ARMS)
        floor_seam = {a: {"in_job": float(round_nrmse(floor_te[a], Yte)),
                          "frozen": float(frozen[name][a]["nrmse"])}
                      for a in floorlib.FLOOR_ARMS if a in frozen.get(name, {})}
        for a, r in floor_seam.items():
            r["abs_dev"] = abs(r["in_job"] - r["frozen"])

        masks, _, _ = bandlib.band_masks(grid, bandlib.N_BANDS)

        kstar_label = dg["M3"]["kstar"]["kstar_label"]
        scored_rung = dg["M3"]["scored_rung"]
        ds = {"n_train": Ntr, "n_test": int(Yte.shape[0]), "n_pool": n_pool,
              "grid": [int(grid[0]), int(grid[1])],
              "fold_sizes": [len(fit), len(cal), len(ev)],
              "floor_seam": floor_seam,
              "shipped": {
                  "scored_test_nrmse": dg["M3"]["scored_test_nrmse"],
                  "arm_test_nrmse": dg["M3"]["arm_test_nrmse"],
                  "scored_rung": scored_rung,
                  "lambda_star": dg["M3"]["blend"]["lambda_star"],
                  "base_star": dg["M3"]["blend"]["base"],
                  "ref": {k: v.get("round_nrmse")
                          for k, v in dg["M3"]["reference_splits"].items()},
                  "rule_label_kstar": dg["M1"][scored_rung]["verdict"]["label"],
              },
              "seams": {}, "rungs": {}}

        # ── seam 1: the calib-side raw k-sweep ───────────────────────────
        raw_cal = {lab: float(round_nrmse(B_tr[k][cal], Ytr[cal])) for lab, k in ks}
        shipped_cal = dg["M3"]["kstar"]["raw_calib_nrmse"]
        ds["seams"]["raw_calib_max_abs_dev"] = max(
            abs(raw_cal[lab] - shipped_cal[lab]) for lab in raw_cal if lab in shipped_cal)

        want_rungs = []
        for tok in [t.strip() for t in args.rungs.split(",") if t.strip()]:
            lab = kstar_label if tok == "kstar" else tok
            if lab in k_of and lab not in want_rungs:
                want_rungs.append(lab)

        # ── the per-rung stage ladder ────────────────────────────────────
        for lab in want_rungs:
            k_tr, k_te = k_of[lab], k_of_te[lab]
            Xc, Xt = B_tr[k_tr][cal], B_te[k_te]
            rec = {"k_train": int(k_tr), "k_test": int(k_te)}

            rec["S0_raw"] = geometry(Xt, Yte, round_nrmse)
            rec["S0_raw"]["calib_nrmse"] = raw_cal[lab]

            gc = [float(round_nrmse(a * Xc, Ytr[cal])) for a in GAINS]
            a_star = float(GAINS[int(np.argmin(gc))])
            rec["S1_gain"] = geometry(a_star * Xt, Yte, round_nrmse)
            rec["S1_gain"].update({"a_star": a_star, "calib_nrmse": float(min(gc))})

            # S2 closed-form LSI: T on the FIT fold, alpha out of fold on calib
            X_full = B_tr[k_tr]
            R = Ytr - X_full
            T = lsilib.fit_transfer(X_full[fit], R[fit], grid, ridge=0.0)
            C_raw = lsilib.apply_transfer(X_full, T, grid)
            alpha, a_ls, base_r, gated_r = fit_alpha(R[cal], C_raw[cal], Xc, Ytr[cal],
                                                     include_zero=True)
            lsi_te = Xt + alpha * lsilib.apply_transfer(Xt, T, grid)
            rec["S2_lsi"] = geometry(lsi_te, Yte, round_nrmse)
            rec["S2_lsi"].update({"alpha_lsi": float(alpha), "alpha_ls": float(a_ls),
                                  "calib_nrmse": float(gated_r)})
            lsi_ev = X_full[ev] + alpha * C_raw[ev]
            got = float(round_nrmse(lsi_ev, Ytr[ev]))
            want = dg.get("M1c", {}).get(f"B:{lab}", {}).get("nrmse_after_lsi")
            rec["S2_lsi"]["seam_ladder_eval"] = {
                "recomputed": got, "shipped": want,
                "abs_dev": (abs(got - want) if want is not None else None)}
            G = np.abs(1.0 + alpha * T)
            rec["S2_lsi"]["band_gain_1_plus_alphaT"] = [float(G[m].mean()) for m in masks]

            for tag, cal_arm, te_arm in (("S3_blend_raw", Xc, Xt),
                                         ("S4_blend_lsi", Xc + alpha * C_raw[cal], lsi_te)):
                best = (None, None, np.inf)
                for b in BASES:
                    for lam in LAMBDAS:
                        v = float(round_nrmse(lam * cal_arm + (1 - lam) * base_cal[b],
                                              Ytr[cal]))
                        if v < best[2]:
                            best = (b, float(lam), v)
                b, lam, cv = best
                pred = lam * te_arm + (1 - lam) * floor_te[b]
                rec[tag] = geometry(pred, Yte, round_nrmse)
                rec[tag].update({"base": b, "lambda": lam, "calib_nrmse": cv})

            ds["rungs"][f"B:{lab}"] = rec
            print(f"  B:{lab:4s} raw {rec['S0_raw']['nrmse_round']:.5f}  "
                  f"gain {rec['S1_gain']['nrmse_round']:.5f} (a*={a_star:.3f})  "
                  f"lsi {rec['S2_lsi']['nrmse_round']:.5f} (alpha={alpha:.3f})  "
                  f"blend_raw {rec['S3_blend_raw']['nrmse_round']:.5f}  "
                  f"blend_lsi {rec['S4_blend_lsi']['nrmse_round']:.5f}", flush=True)

        # ── S5: joint training-free (k, base, lambda) selected on calib ──
        best = (None, None, None, np.inf)
        surface = {}
        for lab, k in ks:
            for b in BASES:
                for lam in LAMBDAS:
                    v = float(round_nrmse(lam * B_tr[k][cal] + (1 - lam) * base_cal[b],
                                          Ytr[cal]))
                    surface.setdefault(lab, {}).setdefault(b, {})[f"{lam:.2f}"] = v
                    if v < best[3]:
                        best = (lab, b, float(lam), v)
        lab5, b5, lam5, cv5 = best
        pred5 = lam5 * B_te[k_of_te[lab5]] + (1 - lam5) * floor_te[b5]
        ds["S5_free_joint"] = geometry(pred5, Yte, round_nrmse)
        ds["S5_free_joint"].update({"k": lab5, "base": b5, "lambda": lam5,
                                    "calib_nrmse": cv5, "n_selections": 3,
                                    "n_fitted_parameters": 0})

        # ── attribution of the scored arm's value, in % and in skill units ──
        ref_nrmse = float(copylf[name]["test_nrmse"])
        scored = float(dg["M3"]["scored_test_nrmse"])
        arm = float(dg["M3"]["arm_test_nrmse"])
        free = ds["S5_free_joint"]["nrmse_round"]
        if scored_rung in ds["rungs"]:
            r = ds["rungs"][scored_rung]
            raw = r["S0_raw"]["nrmse_round"]
            lsi = r["S2_lsi"]["nrmse_round"]
            total = raw - scored
            parts = {"closed_form_lsi": raw - lsi, "gradient_stage": lsi - arm,
                     "blend_stage": arm - scored}
            ds["attribution"] = {
                "scored_rung": scored_rung,
                "test_nrmse": {"raw": raw, "gain": r["S1_gain"]["nrmse_round"],
                               "lsi": lsi, "arm": arm, "scored": scored,
                               "training_free_joint": free},
                "skill_units": {k: v / ref_nrmse for k, v in parts.items()},
                "pct_of_total": ({k: 100.0 * v / total for k, v in parts.items()}
                                 if abs(total) > 0 else None),
                "total_skill_units_over_raw": total / ref_nrmse,
                "training_free_joint_skill_units_over_raw": (raw - free) / ref_nrmse,
                "trained_minus_training_free_skill_units": (free - scored) / ref_nrmse,
                "min_claimable_effect": (float(nf[name]["min_claimable_effect"])
                                         if name in nf else None),
                "note": ("skill = nRMSE / copy-LF reference, LOWER is better; a "
                         "POSITIVE trained_minus_training_free means the trained "
                         "stack beats the zero-gradient selection"),
            }
            mce = ds["attribution"]["min_claimable_effect"]
            if mce:
                ds["attribution"]["over_mce"] = {
                    k: (v / ref_nrmse) / mce for k, v in parts.items()}
                ds["attribution"]["trained_minus_training_free_over_mce"] = \
                    ((free - scored) / ref_nrmse) / mce
            print(f"  attribution @ {scored_rung}: closed-form "
                  f"{ds['attribution']['pct_of_total']['closed_form_lsi']:.1f}% / "
                  f"gradient {ds['attribution']['pct_of_total']['gradient_stage']:.1f}% / "
                  f"blend {ds['attribution']['pct_of_total']['blend_stage']:.1f}%",
                  flush=True)

        ds["verdict"] = {
            "copylf_ref_nrmse": ref_nrmse,
            "scored_skill": scored / ref_nrmse,
            "free_joint_skill": free / ref_nrmse,
            "delta_skill_free_minus_scored": (free - scored) / ref_nrmse,
            "delta_nrmse_free_minus_scored": free - scored,
            "note": ("a NEGATIVE delta means the TRAINING-FREE ladder beats the "
                     "trained scored arm"),
        }
        print(f"  S5 free_joint k={lab5} base={b5} lam={lam5:.2f} -> {free:.5f} "
              f"vs scored {scored:.5f}  (delta skill "
              f"{ds['verdict']['delta_skill_free_minus_scored']:+.4f})", flush=True)
        seam_floor = (max(v['abs_dev'] for v in floor_seam.values())
                      if floor_seam else float('nan'))
        print(f"  seams: raw_calib {ds['seams']['raw_calib_max_abs_dev']:.2e}  "
              f"floors {seam_floor:.2e}", flush=True)
        ds["S5_selection_surface_calib"] = surface
        out["datasets"][name] = ds
        del LF_up, B_tr, B_te, Ytr, Yte

    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
