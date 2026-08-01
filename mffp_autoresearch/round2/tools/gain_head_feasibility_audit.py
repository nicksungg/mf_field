"""ROUND-2: can a post-hoc per-sample GAIN head be fitted here at all, and is a
reported gain CEILING real condition learning or just the head's own clip?

Provenance: r2s3_lf_train_signal-B4 mechanism turns 1-2
(`scratchpad/reanalysis_turn_{1,2}.py`). Head conventions (log-space fit,
unpenalised intercept, exact-LOO/PRESS lambda selection, clipping on law-keyed
heads only) are inherited from `tools/gain_calibration_ceiling.py` via B4's
`models_r2/r2s3_b4_substitution/heads.py`.

WHY THIS EXISTS
---------------
Cards keep reaching for an output-calibration head ("just rescale each sample")
and keep reporting that it does nothing, or that a test-fitted ceiling absorbs
some fraction of an effect. Both readings are routinely instrument artifacts:

  1. DEGENERATE FIT SET. A calibration head fitted on the same HF rows the arm
     was TRAINED on is the identity BY CONSTRUCTION -- the arm has already driven
     its calibration residual to zero on exactly those rows, so the head's labels
     are a constant. On r2s3-B4 `sd(log optimal-scale)` was <= 2.0e-06 on the fit
     rows against 0.028-6.52 on the test rows: a 4-9 decade gap. Nothing about the
     head class or the sample count was the binding constraint.
  2. CLIP-ARTIFACT CEILING. A law-keyed ceiling that clips `exp(law)` to
     [lo, hi] reports the CLIP, not the law, whenever the clip binds. On 6 of 16
     r2s3-B4 draws the ceiling's absorbed share was BIT-IDENTICAL to that of a
     constant gain carrying no condition information at all.

So this tool always reports the zero-information null next to the instrument.

WHAT IT MEASURES
----------------
  label_degeneracy      sd(log c) on the FIT rows vs the EVAL rows, their ratio,
                        the median log shift, and the fit rows' own rel-L2
                        (c_i = <p_i,y_i>/||p_i||^2, the per-sample optimal scale)
  train_fitted_head     the achievable head's out-of-fit R^2 against the TRUE
                        eval log-gain, the spread of the gain it emits, and the
                        score it delivers
  learning_curve        the SAME head class refitted on n RANDOM EVAL rows WITH
                        REAL LABELS, scored on the held-out remainder, for each
                        --n_fits value x --repeats random fit sets. Reported as
                        the share of the per-sample-oracle repair absorbed.
                        Separates class capacity (plateau) from sample size
                        (shape) from label degeneracy (the shipped head's 0.000).
  ceiling_reread        the law fitted BY LOO ON THE EVAL SPLIT, scored clipped
                        and unclipped, next to TWO zero-information nulls (the
                        constant gain at the clip's lower bound, and the exact
                        best constant) and the unclipped per-sample oracle.
  verdict               see the table at the bottom of this docstring.

Scoring is `<eval_dir>/nrmse.py` (the round's one metric). Set `--denominator`
(or `--floors_json`, which reads `[dataset].reference.test_nrmse`) to report in
skill units; the default 1.0 reports nRMSE.

A closed-form identity is used so no (n, n_cells) array is rebuilt per rescale:
    ||g p - y||/||y|| = sqrt(g^2 a - 2 g b + c)/sqrt(c),  (a,b,c)=(||p||^2,<p,y>,||y||^2)
It is asserted equal to `nrmse.nrmse()` at g = 1 (`gram_seam_abs`, expect <1e-10)
before any of it is used.

INVOCATION
----------
  python tools/gain_head_feasibility_audit.py \
      --preds  <arm>_preds.npz \
      --dataset ifc_poisson \
      --floors_json state/anchors/floors.json \
      --out /tmp/gain_audit.json

  # targets from a file instead of the panel loader, and custom npz keys:
  python tools/gain_head_feasibility_audit.py --preds a.npz \
      --targets_npz t.npz --targets_key y_test \
      --key_pred_test pred --key_cond_test cond --out /tmp/x.json

VERDICTS
--------
  DEGENERATE_FIT_SET     sd_log ratio (fit/eval) < --degenerate_ratio: no
                         achievable head fitted on these rows can be anything but
                         the identity, whatever its class
  CLIP_ARTIFACT_CEILING  the constant-gain null reaches >= --null_share of the
                         law's absorbed share: the ceiling number carries no
                         condition information
  LAW_LEARNABLE          held-out R^2 at the largest n_fit >= --r2_learnable and
                         the null does not reproduce the ceiling
  NO_LAW                 neither: the gain is not a function of the conditions

RUNTIME / CAVEATS
-----------------
* Cost is dominated by the panel loader, not the maths (16 legs of 100x65536 in
  ~1.6 min wall on a login node, of which the arithmetic is seconds). Use
  `--targets_npz` to skip the loader entirely when you already have targets.
* `--dataset` loads a split through `panel_data.load_split`, which materialises
  EVERY fidelity; this tool copies out the HF field and drops the rest
  immediately (the structural LF-poisoning of B4's `lf_guard.py` is NOT
  reproduced here, so if you need an auditable no-LF claim, use that instead).
* The learning curve fits on EVAL rows with real labels. That is a
  COUNTERFACTUAL, not an achievable protocol -- it prices what labels would buy,
  and must never be quoted as an attainable score.
* n_fit values >= n_eval - 5 are skipped rather than silently truncated.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_EVAL = HERE.parent / "eval"
_EPS, _LOG_FLOOR = 1e-300, 1e-6


# ── head conventions (vendored from tools/gain_calibration_ceiling.py via
#    r2s3-B4 heads.py; unpenalised intercept, exact-LOO PRESS lambda) ────────
def optimal_scale(P, Y):
    num, den = (P * Y).sum(1), (P * P).sum(1)
    return np.where(den > 0, num / np.maximum(den, _EPS), 0.0)


def _design(Z):
    return np.concatenate([np.ones((Z.shape[0], 1)), np.asarray(Z, float)], 1)


def ridge_press(A, t, lambdas):
    best, n, k = None, *A.shape
    tvar = float(np.sum((t - t.mean()) ** 2))
    for lam in lambdas:
        P = np.eye(k) * float(lam)
        P[0, 0] = 0.0
        try:
            Gi = np.linalg.inv(A.T @ A + P)
        except np.linalg.LinAlgError:
            continue
        w = Gi @ (A.T @ t)
        H = np.einsum("ij,jk,ik->i", A, Gi, A)
        r = t - A @ w
        r_loo = r / np.maximum(1e-12, 1.0 - H)
        press = float(np.sum(r_loo ** 2))
        if best is None or press < best["press"]:
            best = {"lambda": float(lam), "w": w, "press": press,
                    "loo_pred": t - r_loo,
                    "loo_r2": float(1.0 - press / tvar) if tvar > 0 else float("nan"),
                    "r2_in_fit": float(1.0 - np.sum(r ** 2) / tvar) if tvar > 0 else float("nan")}
    if best is None:
        raise SystemExit("ridge_press: every lambda produced a singular system")
    return best


def _log(c):
    return np.log(np.maximum(np.asarray(c, float), _LOG_FLOOR))


def _stats(c, clip):
    lc = _log(c)
    return {"n": int(np.size(c)), "median": float(np.median(c)),
            "sd_log": float(np.std(lc)),
            "min": float(np.min(c)), "max": float(np.max(c)),
            "frac_outside_clip": float(np.mean((c < clip[0]) | (c > clip[1])))}


def _fit_predict(X_fit, t_fit, X_new):
    mu = X_fit.mean(0)
    sd = np.where(X_fit.std(0) > 0, X_fit.std(0), 1.0)
    fit = ridge_press(_design((X_fit - mu) / sd), t_fit, LAMBDAS)
    return np.exp(_design((X_new - mu) / sd) @ fit["w"]), fit


LAMBDAS = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10, 100]


# ── targets ────────────────────────────────────────────────────────────────
def load_targets(args):
    if args.targets_npz:
        Y = np.asarray(np.load(args.targets_npz)[args.targets_key], float)
        return Y.reshape(Y.shape[0], -1), {"source": args.targets_npz}
    if not args.dataset:
        raise SystemExit("need --dataset (panel loader) or --targets_npz")
    sys.path.insert(0, str(Path(args.eval_dir).resolve()))
    import panel_data
    split = panel_data.load_split(args.dataset, args.split)
    hf = int(split["hf_fid"])
    Y = np.array(split["field_by_fid"][hf], dtype=np.float64)
    Y = Y.reshape(Y.shape[0], -1)
    meta = {"source": f"panel_data.load_split({args.dataset!r}, {args.split!r})",
            "hf_fid": hf,
            "panel_data_file": str(Path(panel_data.__file__).resolve())}
    del split
    return Y, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--preds", required=True, help="arm's *_preds.npz")
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--split", default="test")
    ap.add_argument("--targets_npz", default=None)
    ap.add_argument("--targets_key", default="y")
    ap.add_argument("--eval_dir", default=str(DEFAULT_EVAL))
    ap.add_argument("--denominator", type=float, default=None,
                    help="skill denominator; default 1.0 -> report nRMSE")
    ap.add_argument("--floors_json", default=None,
                    help="read [dataset].reference.test_nrmse as the denominator")
    ap.add_argument("--key_pred_test", default="pred_test")
    ap.add_argument("--key_cond_test", default="cond_test_raw")
    ap.add_argument("--key_pred_fit", default="pred_hf_train")
    ap.add_argument("--key_target_fit", default="target_hf_train")
    ap.add_argument("--key_cond_fit", default="cond_hf_train_raw")
    ap.add_argument("--clip", default="0.5,2.0")
    ap.add_argument("--n_fits", default="5,10,20,40")
    ap.add_argument("--repeats", type=int, default=40)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--degenerate_ratio", type=float, default=1e-3)
    ap.add_argument("--null_share", type=float, default=0.90)
    ap.add_argument("--r2_learnable", type=float, default=0.5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    sys.path.insert(0, str(Path(a.eval_dir).resolve()))
    import nrmse as NR

    clip = tuple(float(t) for t in a.clip.split(","))
    denom = a.denominator
    if denom is None and a.floors_json:
        fl = json.loads(Path(a.floors_json).read_text())
        if not a.dataset or a.dataset not in fl:
            raise SystemExit(f"--floors_json needs a --dataset present in {a.floors_json}")
        denom = float(fl[a.dataset]["reference"]["test_nrmse"])
    denom = 1.0 if denom is None else float(denom)

    z = np.load(a.preds)
    P = np.asarray(z[a.key_pred_test], float)
    X = np.asarray(z[a.key_cond_test], float)
    Pf = np.asarray(z[a.key_pred_fit], float)
    Yf = np.asarray(z[a.key_target_fit], float)
    Xf = np.asarray(z[a.key_cond_fit], float)
    Y, tmeta = load_targets(a)
    if P.shape != Y.shape:
        raise SystemExit(f"pred {P.shape} vs target {Y.shape}: shape mismatch")

    aa, bb, cc = (P * P).sum(1), (P * Y).sum(1), (Y * Y).sum(1)

    def sk(g):
        g = np.broadcast_to(np.asarray(g, float), aa.shape)
        q = np.maximum(g * g * aa - 2.0 * g * bb + cc, 0.0)
        return float(np.mean(np.sqrt(q) / np.sqrt(cc))) / denom

    seam = abs(sk(1.0) * denom - NR.nrmse(P, Y))
    if seam >= 1e-10:
        raise SystemExit(f"gram seam failed: {seam}")

    c_fit, c_eval = optimal_scale(Pf, Yf), optimal_scale(P, Y)
    lc_eval = _log(c_eval)
    sd_fit, sd_eval = float(np.std(_log(c_fit))), float(np.std(lc_eval))

    g_head, fit_head = _fit_predict(Xf, _log(c_fit), X)
    ss = float(np.sum((lc_eval - lc_eval.mean()) ** 2))
    out = {
        "_tool": "gain_head_feasibility_audit.py",
        "_provenance_card": "r2s3_lf_train_signal-B4 turns 1-2",
        "inputs": {"preds": a.preds, "targets": tmeta, "denominator": denom,
                   "clip": list(clip), "n_eval": int(P.shape[0]),
                   "n_fit_rows": int(Pf.shape[0]), "cond_dim": int(X.shape[1]),
                   "gram_seam_abs": seam},
        "label_degeneracy": {
            "fit_rows_rel_l2": float(np.mean(
                np.linalg.norm(Pf - Yf, axis=1) / np.linalg.norm(Yf, axis=1))),
            "c_fit": _stats(c_fit, clip), "c_eval": _stats(c_eval, clip),
            "sd_log_ratio_fit_over_eval": sd_fit / max(sd_eval, 1e-12),
            "median_log_shift_eval_minus_fit": float(
                np.median(lc_eval) - np.median(_log(c_fit)))},
        "train_fitted_head": {
            "lambda": fit_head["lambda"], "loo_r2_on_fit_rows": fit_head["loo_r2"],
            "R2_vs_true_eval_loggain": float(
                1.0 - np.sum((lc_eval - _log(g_head)) ** 2) / ss) if ss > 0 else float("nan"),
            "gain_spread_sd_log": float(np.std(_log(g_head))),
            "skill_raw": sk(1.0), "skill_applied_clipped": sk(np.clip(g_head, *clip))},
    }

    # learning curve on labelled held-out rows (a counterfactual, never a score)
    n = P.shape[0]
    rng_master = np.random.default_rng(a.seed)
    curve = {}
    for nf in [int(t) for t in a.n_fits.split(",")]:
        if nf >= n - 5:
            continue
        rng = np.random.default_rng(int(rng_master.integers(0, 2 ** 31 - 1)))
        rec = {"R2": [], "absorbed_of_oracle": [], "clip_fraction": []}
        for _ in range(a.repeats):
            idx = rng.permutation(n)
            f, h = idx[:nf], idx[nf:]
            g, _ = _fit_predict(X[f], lc_eval[f], X[h])
            ah, bh, ch = aa[h], bb[h], cc[h]

            def s(gg, ah=ah, bh=bh, ch=ch):
                q = np.maximum(np.broadcast_to(np.asarray(gg, float), ah.shape) ** 2 * ah
                               - 2.0 * np.asarray(gg, float) * bh + ch, 0.0)
                return float(np.mean(np.sqrt(q) / np.sqrt(ch))) / denom

            s_raw, s_or = s(1.0), s(c_eval[h])
            s_head = s(np.clip(g, *clip))
            lh = lc_eval[h]
            ssh = float(np.sum((lh - lh.mean()) ** 2))
            rec["R2"].append(1.0 - np.sum((lh - _log(g)) ** 2) / ssh if ssh > 0 else np.nan)
            rec["absorbed_of_oracle"].append(
                (s_raw - s_head) / (s_raw - s_or) if s_raw > s_or else np.nan)
            rec["clip_fraction"].append(float(np.mean((g < clip[0]) | (g > clip[1]))))
        curve[str(nf)] = {k: {"mean": float(np.nanmean(v)),
                              "p10": float(np.nanpercentile(v, 10)),
                              "p90": float(np.nanpercentile(v, 90))}
                          for k, v in rec.items()}
    out["labelled_holdout_learning_curve"] = curve
    out["_learning_curve_note"] = (
        "fitted on EVAL rows with real labels: a counterfactual price for labels, "
        "NOT an achievable score")

    # ceiling re-read + the zero-information nulls
    fit_loo = ridge_press(_design((X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1.0)),
                          lc_eval, LAMBDAS)
    g_loo = np.exp(fit_loo["loo_pred"])
    grid = np.concatenate([np.geomspace(1e-4, 1e2, 601), [1.0]])
    g_best = float(grid[int(np.argmin([sk(g) for g in grid]))])
    s_raw, s_or = sk(1.0), sk(c_eval)
    span = s_raw - s_or
    ceil = {"law_clipped": sk(np.clip(g_loo, *clip)), "law_unclipped": sk(g_loo),
            "null_constant_at_clip_lo": sk(clip[0]), "null_best_constant": sk(g_best),
            "best_constant_gain": g_best, "per_sample_oracle_unclipped": s_or,
            "raw": s_raw, "loo_r2_of_law": fit_loo["loo_r2"],
            "clip_fraction": float(np.mean((g_loo < clip[0]) | (g_loo > clip[1])))}
    ceil["absorbed_share_of_oracle_span"] = {
        k: (s_raw - ceil[k]) / span if span > 0 else float("nan")
        for k in ("law_clipped", "law_unclipped", "null_constant_at_clip_lo",
                  "null_best_constant")}
    sh = ceil["absorbed_share_of_oracle_span"]
    ceil["null_over_law"] = (sh["null_constant_at_clip_lo"] / sh["law_clipped"]
                             if abs(sh["law_clipped"]) > 1e-12 else float("nan"))
    out["ceiling_reread"] = ceil

    r2_plateau = (max((v["R2"]["mean"] for v in curve.values()), default=float("nan"))
                  if curve else float("nan"))
    out["verdict_inputs"] = {"sd_log_ratio": out["label_degeneracy"]["sd_log_ratio_fit_over_eval"],
                             "learning_curve_R2_plateau": r2_plateau,
                             "null_over_law": ceil["null_over_law"]}
    v = []
    if out["label_degeneracy"]["sd_log_ratio_fit_over_eval"] < a.degenerate_ratio:
        v.append("DEGENERATE_FIT_SET")
    if np.isfinite(ceil["null_over_law"]) and ceil["null_over_law"] >= a.null_share:
        v.append("CLIP_ARTIFACT_CEILING")
    if np.isfinite(r2_plateau) and r2_plateau >= a.r2_learnable and "CLIP_ARTIFACT_CEILING" not in v:
        v.append("LAW_LEARNABLE")
    if not any(x in v for x in ("LAW_LEARNABLE",)):
        v.append("NO_LAW")
    out["verdict"] = v

    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps({"verdict": v,
                      "sd_log_ratio_fit_over_eval": out["label_degeneracy"]["sd_log_ratio_fit_over_eval"],
                      "head_R2_vs_true_eval_loggain": out["train_fitted_head"]["R2_vs_true_eval_loggain"],
                      "learning_curve_R2_plateau": r2_plateau,
                      "null_over_law": ceil["null_over_law"],
                      "clip_fraction": ceil["clip_fraction"]}, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
