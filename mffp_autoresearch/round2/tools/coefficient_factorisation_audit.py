#!/usr/bin/env python
"""coefficient_factorisation_audit.py -- WHEN A CONDITION->FIELD MODE COEFFICIENT
LOOKS "UNIDENTIFIABLE", IS IT THE INFORMATION OR THE FACTORISATION?

The standard closed-form control for a condition->HF task is a per-mode head:
build a basis (DC + POD of the train residual), score each direction's
out-of-fold R^2 of `condition -> coefficient`, keep the directions that clear a
threshold, fit a map on each.  Every card that uses that control -- and every
card that reads a low per-mode OOF R^2 as "the condition does not determine this
mode" -- is making a hidden assumption: that a PER-DIRECTION function of the
CONDITION is the right factorisation of the law.

This tool tests that assumption.  For each direction of the same basis it
measures, out of fold and training-free:

  A. `oof_r2_from_condition`   the usual statistic (the head's own selector);
  B. `oof_r2_from_set_coeffs`  the SAME coefficient predicted from the SELECTED
                               directions' coefficients -- cross-coefficient
                               (field-internal) structure that (A) cannot see;
  C. `test_r2_arm`             optional: what a supplied trained arm's own
                               output achieves on that coefficient, i.e. what a
                               big model actually learned.

and then SCORES, through the round's `eval/nrmse.py`, a deployable two-stage
head `condition -> SET coefficients -> remaining coefficients` against the
one-stage head, with the stage-2 gate computed two ways:

  * `true_input`         stage 2 selected/fitted on the TRUE stage-1
                         coefficients (optimistic; the usual mistake), and
  * `propagation_aware`  stage 2 selected/fitted on OUT-OF-FOLD stage-1
                         PREDICTIONS, so the selector sees the error it will be
                         fed at test time.  Use this one.

VERDICTS
--------
  CONDITION_LIMITED     (A) low and (B) low: no factorisation reaches those
                        coefficients; the lever is the condition vector or the
                        sampling design, not the model.
  FACTORISATION_LIMITED (A) low but (B) high: the information IS there and a
                        per-direction condition map cannot express it.  A
                        two-stage / shared-representation estimator is the
                        lever -- and a large decoder will appear to "win on
                        capacity" when it is really winning on factorisation.
  BASIS_LIMITED         most of the centered test energy lies OFF the train
                        basis: neither statistic is the binding constraint.

WHY THIS EXISTS
---------------
`r2s1_direct-B3` turn 3.  On `sharp__cahn_hilliard` the head's selector scored
`pod_5` / `pod_6` at OOF R^2 -0.006 / -0.017 (i.e. "noise"), a 15 853 057-
parameter FiLM-FNO decoder predicted those same coefficients at TEST R^2
+0.606 / +0.565, and they turned out to be 0.92 / 0.94 predictable from the
head's OWN three selected coefficients.  A ~3.5e3-parameter closed-form
two-stage head then scored 11.4148 against the head's 12.6601 and the decoder's
12.0478 (13.6x that dataset's certified mce).  The same probe on
`sharp__allen_cahn_2d` found max stage-2 OOF R^2 = +0.0054 and correctly
returned a no-op, matching the decoder's zero off-subspace gain there.
Relaxing the head's selection threshold to admit ALL directions, by contrast,
made every panel cell flat or worse -- so this is not "widen the basis", it is
"change the factorisation".

RELATION TO NEIGHBOURING TOOLS
------------------------------
* `condition_identifiable_rank.py` (r2s1_direct-B1) computes statistic (A) and
  the ORACLE truncation.  Read its `COEFFICIENT_UNIDENTIFIABLE` verdict as
  "unidentifiable BY THIS FAMILY at this cond_dim / row count" until this tool
  has ruled out (B).
* `head_subspace_surgery.py` (r2s1_direct-B3 turn 2) asks the same question from
  the OUTPUT side: whether a big arm's content outside a small arm's subspace is
  useful at all.  A positive `cos` there and a high (B) here are the same
  phenomenon seen from two directions.
* `reachable_set_rank_audit.py` (r2s2_stacked-B1) measures how many knobs a
  TRAINED model turns; this measures how many knobs a CLOSED-FORM control can
  turn under two different factorisations.

USAGE
-----
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/coefficient_factorisation_audit.py \
      --datasets sharp__cahn_hilliard,sharp__allen_cahn_2d \
      --out factorisation.json
  # with a trained arm's test predictions for column (C):
  python tools/coefficient_factorisation_audit.py \
      --datasets sharp__cahn_hilliard --arm_preds <...>/preds_test_ref_decoder_big_*.npz \
      --out factorisation_ch.json

Defaults reproduce `r2s1_direct-B3`'s head: 50 POD modes + DC, disjoint
80/10/10 folds at seed 0, 5-fold selection, tau = 0.1, map bank
{affine, quadratic, knn, rbf_kernel_ridge}, `add`/`fact` centering by the
||mean field|| / geomean||y|| rule at tau = 1.0.

Provenance: promoted from `r2s1_direct-B3` mechanism turn 3
(`worktrees/r2s1_direct/B3/scratchpad/reanalysis_turn_3{,c,d}.py`).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import subprocess
import sys

import numpy as np
import yaml

ROUND_ROOT = pathlib.Path(__file__).resolve().parents[1]
EVAL_DIR = ROUND_ROOT / "eval"


def _repo_root() -> pathlib.Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True,
                         cwd=str(pathlib.Path(__file__).resolve().parent)).stdout.strip()
    return pathlib.Path(out)


def _load_nrmse():
    spec = importlib.util.spec_from_file_location("round_eval_nrmse",
                                                  EVAL_DIR / "nrmse.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


NR = _load_nrmse()


def load_dataset(dataset: str, data_root: pathlib.Path) -> dict:
    """Condition/HF arrays for a dataset, through the factory adapter (read-only)."""
    root = _repo_root()
    cfg = yaml.safe_load((ROUND_ROOT / "project.yaml").read_text())
    factory_root = root / cfg["paths"]["factory_root"]
    if str(factory_root) not in sys.path:
        sys.path.insert(0, str(factory_root))
    from data_adapters.loaders import load_mf_dataset  # noqa: E402

    dd = data_root / dataset
    tr = load_mf_dataset(dd, "train")
    te = load_mf_dataset(dd, "test")
    hf = tr["hf_fid"]
    ctr = np.asarray(tr["cond_by_fid"][hf], dtype=np.float64)
    ytr = np.asarray(tr["field_by_fid"][hf], dtype=np.float64)
    cte = np.asarray(te["cond_by_fid"][te["hf_fid"]], dtype=np.float64)
    yte = np.asarray(te["field_by_fid"][te["hf_fid"]], dtype=np.float64)
    return {"cond_train": ctr, "hf_train": ytr.reshape(ytr.shape[0], -1),
            "cond_test": cte, "hf_test": yte.reshape(yte.shape[0], -1)}


# ── centering + basis (the round's own construction) ────────────────

class Centering:
    def __init__(self, hf_fit: np.ndarray, form: str):
        self.form = form
        if form == "add":
            self.center, self.amp = hf_fit.mean(axis=0), None
        else:
            nn = np.linalg.norm(hf_fit, axis=1)
            self.center = (hf_fit / nn[:, None]).mean(axis=0)
            self.amp = float(np.exp(np.mean(np.log(nn))))

    def encode(self, y):
        y = np.asarray(y, dtype=np.float64)
        if self.form == "add":
            return y - self.center
        return y / np.linalg.norm(y, axis=1, keepdims=True) - self.center

    def decode(self, resid):
        f = self.center[None, :] + np.asarray(resid, dtype=np.float64)
        if self.form == "fact":
            f = f / np.maximum(np.linalg.norm(f, axis=1, keepdims=True), 1e-300) * self.amp
        return f


def centering_form(hf: np.ndarray, tau: float) -> tuple[str, float]:
    ratio = float(np.linalg.norm(hf.mean(axis=0))
                  / np.exp(np.mean(np.log(np.linalg.norm(hf, axis=1)))))
    return ("fact" if ratio >= tau else "add"), ratio


def pod_basis(target: np.ndarray, n_modes: int):
    """Leading POD modes by the method of snapshots, with a self-validating screen."""
    G = target @ target.T
    w, V = np.linalg.eigh(G)
    order = np.argsort(w)[::-1]
    w, V = w[order], V[:, order]
    s = np.sqrt(np.maximum(w, 0.0))
    if s.size == 0 or s[0] <= 0:
        return np.zeros((0, target.shape[1])), np.zeros(0)
    keep = int(np.sum(s > np.sqrt(np.finfo(float).eps) * s[0]))
    keep = max(1, min(keep, n_modes))
    Vt = (V[:, :keep] / s[:keep]).T @ target
    r = keep
    while r > 1:
        g = Vt[:r] @ Vt[:r].T
        if np.abs(g - np.eye(r)).max() <= 1e-9:
            break
        r -= 1
    return Vt[:r], s[:r]


def direction_bank(target_fit: np.ndarray, n_pod: int):
    cells = target_fit.shape[1]
    d0 = np.full(cells, 1.0 / np.sqrt(float(cells)))
    resid = target_fit - np.outer(target_fit @ d0, d0)
    Vt, _ = pod_basis(resid, n_pod)
    D = np.concatenate([d0[None, :], Vt], axis=0)
    off = float(np.abs(D @ D.T - np.eye(D.shape[0])).max())
    if off > 1e-8:
        raise RuntimeError(f"direction bank not orthonormal: {off:.3e}")
    return D, ["dc_meanfield"] + [f"pod_{j}" for j in range(Vt.shape[0])]


# ── the map bank ────────────────────────────────────────────────────

def standardizer(X):
    mu = X.mean(0)
    sd = X.std(0)
    sd[sd < 1e-12] = 1.0
    return mu, sd


def quad_features(Z):
    n, d = Z.shape
    cols = [np.ones((n, 1)), Z]
    for i in range(d):
        cols.append(Z[:, i:i + 1] * Z[:, i:])
    return np.concatenate(cols, axis=1)


class _Ridge:
    def __init__(self, feat, alphas):
        self.feat, self.alphas = feat, alphas

    def fit(self, Z, Y):
        A = self.feat(Z)
        best, self.W = None, None
        AtA, AtY = A.T @ A, A.T @ Y
        I = np.eye(A.shape[1])
        H0 = A @ np.linalg.solve(AtA + 1e-12 * I, A.T) if A.shape[0] <= 800 else None
        for al in self.alphas:
            W = np.linalg.solve(AtA + al * I, AtY)
            if H0 is not None:
                H = A @ np.linalg.solve(AtA + al * I, A.T)
                h = np.clip(np.diag(H), None, 1 - 1e-8)
                res = (Y - A @ W) / (1 - h)[:, None]
                sc = float((res ** 2).sum())
            else:
                sc = float(((Y - A @ W) ** 2).sum())
            if best is None or sc < best:
                best, self.W, self.alpha = sc, W, al
        self.n_params_per_column = A.shape[1]
        return self

    def predict(self, Z):
        return self.feat(Z) @ self.W


class _KNN:
    def __init__(self, ks):
        self.ks = ks

    def fit(self, Z, Y):
        self.Z, self.Y = Z, Y
        n = Z.shape[0]
        d2 = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1)
        np.fill_diagonal(d2, np.inf)
        best = None
        for k in self.ks:
            k = min(k, n - 1)
            idx = np.argsort(d2, axis=1)[:, :k]
            pred = Y[idx].mean(1)
            sc = float(((Y - pred) ** 2).sum())
            if best is None or sc < best:
                best, self.k = sc, k
        self.n_params_per_column = 1
        return self

    def predict(self, Z):
        d2 = ((Z[:, None, :] - self.Z[None, :, :]) ** 2).sum(-1)
        idx = np.argsort(d2, axis=1)[:, : self.k]
        return self.Y[idx].mean(1)


class _KRR:
    def __init__(self, alphas):
        self.alphas = alphas

    @staticmethod
    def _k(A, B, g):
        d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(-1)
        return np.exp(-g * d2)

    def fit(self, Z, Y):
        d2 = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(-1)
        med = float(np.median(d2[d2 > 0])) if np.any(d2 > 0) else 1.0
        self.gamma = 1.0 / max(med, 1e-12)
        self.Z = Z
        K = np.exp(-self.gamma * d2)
        n = K.shape[0]
        best = None
        for al in self.alphas:
            M = np.linalg.solve(K + al * np.eye(n), Y)
            H = K @ np.linalg.solve(K + al * np.eye(n), np.eye(n))
            h = np.clip(np.diag(H), None, 1 - 1e-8)
            res = (Y - K @ M) / (1 - h)[:, None]
            sc = float((res ** 2).sum())
            if best is None or sc < best:
                best, self.M = sc, M
        self.n_params_per_column = n
        return self

    def predict(self, Z):
        return self._k(Z, self.Z, self.gamma) @ self.M


def make_family(name, cfg):
    al = cfg["ridge_alphas"]
    if name == "affine":
        return _Ridge(lambda Z: np.concatenate([np.ones((Z.shape[0], 1)), Z], 1), al)
    if name == "quadratic":
        return _Ridge(quad_features, al)
    if name == "knn":
        return _KNN(cfg["knn_k"])
    if name == "rbf_kernel_ridge":
        return _KRR(al)
    raise ValueError(name)


def r2_columns(pred, C):
    ss = ((C - pred) ** 2).sum(0)
    tot = ((C - C.mean(0)) ** 2).sum(0)
    return 1.0 - ss / np.maximum(tot, 1e-300)


def kfold(n, k, seed):
    return np.array_split(np.random.default_rng(seed).permutation(n), max(1, min(k, n)))


def oof_table(Z, C, folds, cfg):
    fams = cfg["map_bank"]
    r2 = np.zeros((C.shape[1], len(fams)))
    for fi, fam in enumerate(fams):
        pred = np.zeros_like(C)
        for f in folds:
            tr = np.setdiff1d(np.arange(C.shape[0]), f)
            if tr.size < 2 or f.size == 0:
                continue
            pred[f] = make_family(fam, cfg).fit(Z[tr], C[tr]).predict(Z[f])
        r2[:, fi] = r2_columns(pred, C)
    bi = np.argmax(r2, axis=1)
    return {"r2": r2, "best_r2": r2[np.arange(r2.shape[0]), bi],
            "best_family": [fams[i] for i in bi]}


def fit_group(Z, Y, fams, cfg):
    models = []
    for fam in dict.fromkeys(fams):
        cols = np.array([i for i, f in enumerate(fams) if f == fam], dtype=int)
        models.append((cols, make_family(fam, cfg).fit(Z, Y[:, cols])))
    return models


def predict_group(models, Z, m):
    out = np.zeros((Z.shape[0], m))
    for cols, mod in models:
        pr = mod.predict(Z)
        for c, col in enumerate(cols):
            out[:, col] = pr[:, c]
    return out


# ── the audit ───────────────────────────────────────────────────────

def run(ds: str, args, cfg) -> dict:
    data = load_dataset(ds, pathlib.Path(args.data_root))
    ctr, ytr = data["cond_train"], data["hf_train"]
    n_train = ytr.shape[0]
    rng = np.random.default_rng(args.seed)
    perm = rng.permutation(n_train)
    n_model = max(1, int(round(args.model_frac * n_train)))
    n_calib = max(1, int(round(args.calib_frac * n_train)))
    if n_train < args.small_n_threshold:
        fit_idx = np.arange(n_train)
        S_idx = np.arange(n_train)
    else:
        fit_idx = np.sort(perm[n_model + n_calib:])
        S_idx = np.sort(np.concatenate([fit_idx, np.sort(perm[:n_model])]))

    form, ratio = centering_form(ytr[S_idx], args.center_tau)
    cen = Centering(ytr[fit_idx], form)
    D, labels = direction_bank(cen.encode(ytr[fit_idx]), args.n_modes)
    m = D.shape[0]
    C_S = cen.encode(ytr[S_idx]) @ D.T
    mu, sd = standardizer(ctr[fit_idx])
    Z_S = (ctr[S_idx] - mu) / sd
    folds_S = kfold(len(S_idx), args.kfold, args.seed + 9973)
    tabA = oof_table(Z_S, C_S, folds_S, cfg)
    SET = np.flatnonzero(tabA["best_r2"] > args.tau)
    if SET.size < 1:
        SET = np.argsort(-tabA["best_r2"])[:1]
    SET = np.sort(SET[: args.max_set])
    rest = np.array([j for j in range(m) if j not in set(SET.tolist())], dtype=int)

    y = data["hf_test"]
    Z_fit = (ctr[fit_idx] - mu) / sd
    C_fit = cen.encode(ytr[fit_idx]) @ D.T
    stage1 = fit_group(Z_fit, C_fit[:, SET], [tabA["best_family"][j] for j in SET], cfg)
    Z_te = (data["cond_test"] - mu) / sd
    coef_te = predict_group(stage1, Z_te, SET.size)
    add = np.zeros((y.shape[0], m))
    add[:, SET] = coef_te
    p_head = cen.decode(add @ D)
    ref = None
    cl = json.loads(pathlib.Path(args.copylf).read_text())
    if ds in cl and "test_nrmse" in cl[ds]:
        ref = float(cl[ds]["test_nrmse"])
    n_head = float(NR.nrmse(p_head, y))

    C_true_te = cen.encode(y) @ D.T
    e_total = float((cen.encode(y) ** 2).sum())
    out = {"dataset": ds, "centering_form": form, "centering_ratio": ratio,
           "n_directions": int(m), "set_indices": [int(j) for j in SET],
           "set_labels": [labels[j] for j in SET],
           "n_fit": int(fit_idx.size), "n_select": int(S_idx.size),
           "one_stage_head": {"nrmse": n_head,
                              "skill": (NR.skill(n_head, ref) if ref else None)},
           "nrmse_def_hash": NR.NRMSE_DEF_HASH}

    # optional column C: a trained arm's own coefficients
    arm_r2 = None
    if args.arm_preds:
        z = np.load(args.arm_preds)
        arm = np.asarray(z["pred"] if "pred" in getattr(z, "files", []) else z,
                         dtype=np.float64).reshape(y.shape[0], -1)
        C_arm = cen.encode(arm) @ D.T
        arm_r2 = r2_columns(C_arm, C_true_te)
        n_arm = float(NR.nrmse(arm, y))
        out["arm"] = {"path": args.arm_preds, "nrmse": n_arm,
                      "skill": (NR.skill(n_arm, ref) if ref else None)}

    # stage-2 gates
    folds_f = kfold(fit_idx.size, args.kfold, args.seed + 9973)
    X_oof = np.zeros((fit_idx.size, SET.size))
    for f in folds_f:
        tr = np.setdiff1d(np.arange(fit_idx.size), f)
        mods = fit_group(Z_fit[tr], C_fit[tr][:, SET],
                         [tabA["best_family"][j] for j in SET], cfg)
        X_oof[f] = predict_group(mods, Z_fit[f], SET.size)
    Y_rest = C_fit[:, rest]
    for tag, Xsrc in (("true_input", C_fit[:, SET]), ("propagation_aware", X_oof)):
        mu2, sd2 = standardizer(Xsrc)
        Z2 = (Xsrc - mu2) / sd2
        tabB = oof_table(Z2, Y_rest, folds_f, cfg)
        keep = np.flatnonzero(tabB["best_r2"] > args.tau2)
        rec = {"n_kept": int(keep.size),
               "max_oof_r2": float(tabB["best_r2"].max()) if tabB["best_r2"].size else None,
               "kept_labels": [labels[j] for j in rest[keep]]}
        if keep.size == 0:
            rec.update({"nrmse": n_head, "skill": out["one_stage_head"]["skill"],
                        "note": "no-op"})
        else:
            mods = fit_group(Z2, Y_rest[:, keep], [tabB["best_family"][i] for i in keep],
                             cfg)
            pr = predict_group(mods, (coef_te - mu2) / sd2, keep.size)
            add2 = add.copy()
            add2[:, rest[keep]] = pr
            nn = float(NR.nrmse(cen.decode(add2 @ D), y))
            rec.update({"nrmse": nn, "skill": (NR.skill(nn, ref) if ref else None)})
        out[f"two_stage_{tag}"] = rec
        if tag == "propagation_aware":
            best_r2B = tabB["best_r2"]

    per = []
    for i, j in enumerate(rest):
        row = {"index": int(j), "label": labels[j],
               "oof_r2_from_condition": float(tabA["best_r2"][j]),
               "oof_r2_from_set_coeffs": float(best_r2B[i]),
               "test_energy_share": float((C_true_te[:, j] ** 2).sum() / e_total)}
        if arm_r2 is not None:
            row["test_r2_arm"] = float(arm_r2[j])
        per.append(row)
    out["per_direction"] = per
    out["ledger"] = {
        "energy_off_bank_share": float(
            ((cen.encode(y) - C_true_te @ D) ** 2).sum() / e_total),
        "energy_in_discarded_share": float(
            sum(r["test_energy_share"] for r in per)),
        "max_oof_r2_from_condition_on_discarded": float(
            max((r["oof_r2_from_condition"] for r in per), default=float("nan"))),
        "max_oof_r2_from_set_coeffs_on_discarded": float(
            max((r["oof_r2_from_set_coeffs"] for r in per), default=float("nan"))),
    }
    L = out["ledger"]
    if L["energy_off_bank_share"] > 0.5:
        out["verdict"] = "BASIS_LIMITED"
    elif L["max_oof_r2_from_set_coeffs_on_discarded"] > max(
            args.tau2, L["max_oof_r2_from_condition_on_discarded"] + 0.1):
        out["verdict"] = "FACTORISATION_LIMITED"
    else:
        out["verdict"] = "CONDITION_LIMITED"
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--datasets", required=True, help="comma-separated dataset names")
    ap.add_argument("--out", required=True)
    ap.add_argument("--data_root", default=str(ROUND_ROOT / "stripped_data"))
    ap.add_argument("--copylf", default=str(EVAL_DIR / "copylf_baselines.json"))
    ap.add_argument("--arm_preds", default=None,
                    help="optional test-prediction npz of a trained arm (single dataset)")
    ap.add_argument("--n_modes", type=int, default=50)
    ap.add_argument("--tau", type=float, default=0.1, help="stage-1 SET threshold")
    ap.add_argument("--tau2", type=float, default=0.1, help="stage-2 threshold")
    ap.add_argument("--max_set", type=int, default=32)
    ap.add_argument("--kfold", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--model_frac", type=float, default=0.10)
    ap.add_argument("--calib_frac", type=float, default=0.10)
    ap.add_argument("--small_n_threshold", type=int, default=20)
    ap.add_argument("--center_tau", type=float, default=1.0)
    args = ap.parse_args()
    cfg = {"map_bank": ["affine", "quadratic", "knn", "rbf_kernel_ridge"],
           "ridge_alphas": list(np.logspace(-6, 2, 13)), "knn_k": [1, 2, 4, 8]}

    rep = {"nrmse_def_hash": NR.NRMSE_DEF_HASH, "config": {
        k: getattr(args, k) for k in ("n_modes", "tau", "tau2", "kfold", "seed",
                                      "model_frac", "calib_frac", "center_tau")},
        "datasets": {}}
    for ds in [s for s in args.datasets.split(",") if s]:
        d = run(ds, args, cfg)
        rep["datasets"][ds] = d
        print(f"[{ds}] {d['verdict']} | 1-stage head nRMSE "
              f"{d['one_stage_head']['nrmse']:.6f} | 2-stage prop-aware "
              f"{d['two_stage_propagation_aware']['nrmse']:.6f} "
              f"(kept {d['two_stage_propagation_aware']['n_kept']}) | max OOF R^2 on "
              f"discarded: cond {d['ledger']['max_oof_r2_from_condition_on_discarded']:+.4f}"
              f" vs set-coeffs {d['ledger']['max_oof_r2_from_set_coeffs_on_discarded']:+.4f}",
              flush=True)
    pathlib.Path(args.out).write_text(json.dumps(rep, indent=1))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
