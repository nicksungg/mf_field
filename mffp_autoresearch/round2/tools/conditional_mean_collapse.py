#!/usr/bin/env python
"""Has this condition→field model COLLAPSED to a constant field, and is its
condition-driven variation worth its amplitude?

In the round-2 regime (condition vector in, HF field out) the dominant
degenerate solution is the conditional mean: the model emits nearly the same
field for every sample and scores at the `train_mean` floor while looking like a
trained model. This tool separates that case from a real conditional predictor,
and — the load-bearing part — from the *worse* case where the model emits plenty
of condition-driven variation that points in the wrong direction and therefore
costs it score.

What it computes (per dataset, per prediction file)
---------------------------------------------------
* `skill` and `skill_of_own_mean_field_broadcast` — the model, and the model with
  its condition-dependence surgically removed (its own mean field broadcast to
  every test sample), both scored through `round2/eval/nrmse.py`. **This pair is
  the decisive, metric-consistent test.**
* `R` = pooled fluctuation-energy ratio ‖P−P̄‖²/‖Y−Ȳ‖², `A` = fluctuation
  alignment, `useful = 2A√R − R` (share of the truth's fluctuation energy
  removed; NEGATIVE means the variation adds error).
* `shrinkage` — skill of `P̄ + λ(P − P̄)` on a λ grid and the arg-min λ*.
  **TEST-FITTED oracle, labelled**: a diagnostic of whether the variation is
  worth its amplitude, not a claimable arm. λ* ≪ 1 ⇒ the model should be shrunk
  toward its own mean; λ* > 1 ⇒ it under-amplifies.
* per-sample: rel-L2 quantiles, cosine(pred, hf), amplitude ratio ‖P_i‖/‖Y_i‖,
  Spearman ρ of rel-L2 against ‖hf‖ / the amplitude ratio / the distance to the
  nearest TRAIN condition, the top-10 share of the summed rel-L2, and the count
  of samples with per-sample skill < 1.
* with ≥ 2 prediction files for the same dataset (different seeds): pairwise
  `‖P_a−P_b‖/‖P_a‖`, the fluctuation cosine, and the worst-10 overlap —
  "same function" vs "same score", which is what a seed-spread noise constant
  actually measures.

READ IT AS
----------
* `skill ≈ skill_of_own_mean_field_broadcast` and `R ≪ 1` → COLLAPSED. Check the
  aleatoric ceiling (`tools/condition_predictability_ceiling.py`) before calling
  it a failure: on `sharp__fisher_kpp_2d` the collapse is the correct answer.
* `useful < 0`, `λ* ≈ 0`, low per-sample cosine → the model is a noise generator
  whose only contribution to the error is its own amplitude. Post-hoc shrinkage
  calibrated on a held-out TRAIN fold is a mandatory guardrail for such a model.
* seed-pair `fluct_cosine ≈ 1` → the seeds found the same function, so a small
  certified seed spread is reproducibility of one solution, not resolving power.

Invocation
----------
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/conditional_mean_collapse.py \
        --preds "sharp__fisher_kpp_2d=/path/s0.npy:/path/s1.npy:/path/s2.npy" \
        --out /path/to/collapse.json
    # several datasets: repeat --preds, or comma-separate the ds=... groups.

Each `.npy` is `(n_test, n_cells)` (or `(n_test, H, W)`) in the loader's test
order. Provenance: card `experiment_cards/r2s4_diag/batch_1/B1.json` part 6
(findings T1-F1 … T1-F5, T3-F1 … T3-F5); source probes
`worktrees/r2s4_diag/B1/scratchpad/reanalysis_turn_{1,3}.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml


def _resolve_roots():
    here = Path(__file__).resolve()
    project_root = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
        check=True, cwd=here.parent).stdout.strip())
    round_root = here.parents[1]
    cfg = yaml.safe_load(open(round_root / "project.yaml"))
    paths = {k: (Path(v) if os.path.isabs(v) else (project_root / v).resolve())
             for k, v in cfg["paths"].items()}
    return project_root, round_root, cfg, paths


PROJECT_ROOT, ROUND_ROOT, CFG, PATHS = _resolve_roots()
sys.path.insert(0, str(PATHS["eval_dir"]))
sys.path.insert(0, str(PATHS["factory_root"]))
import nrmse as NR                                    # noqa: E402
from data_adapters.loaders import load_mf_dataset      # noqa: E402

LAMS = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.5]


def frob(a):
    return float(np.sqrt((a ** 2).sum()))


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / (np.linalg.norm(ra) * np.linalg.norm(rb)))


def load_split(name: str, data_root: Path):
    train = load_mf_dataset(data_root / name, "train")
    test = load_mf_dataset(data_root / name, "test")
    hf = train["hf_fid"]
    if hf not in test["fids"]:
        hf = test["hf_fid"]
    c_tr = np.asarray(train["cond_by_fid"][hf], dtype=np.float64)
    c_te = np.asarray(test["cond_by_fid"][hf], dtype=np.float64)
    mu, sd = c_tr.mean(0), c_tr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    Y_tr = np.asarray(train["field_by_fid"][hf], dtype=np.float64).reshape(
        c_tr.shape[0], -1)
    Y_te = np.asarray(test["field_by_fid"][hf], dtype=np.float64).reshape(
        c_te.shape[0], -1)
    return (c_tr - mu) / sd, (c_te - mu) / sd, Y_tr, Y_te


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", action="append", required=True,
                    help="ds=path[:path2:...]  (repeatable, or comma-separated)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--data_root", default=str(PATHS["stripped_data_root"]))
    args = ap.parse_args()

    groups = {}
    for chunk in args.preds:
        for item in chunk.split(","):
            if not item:
                continue
            k, v = item.split("=", 1)
            groups.setdefault(k, []).extend(v.split(":"))

    baselines = json.load(open(PATHS["eval_dir"] / "copylf_baselines.json"))
    data_root = Path(args.data_root)
    res = {"_tool": "conditional_mean_collapse",
           "_nrmse_def_hash": NR.NRMSE_DEF_HASH,
           "_copylf_def_hash": baselines["_copylf_def_hash"],
           "_shrinkage_is_test_fitted_oracle": True,
           "_data_root": str(data_root), "datasets": {}}

    for name, paths in groups.items():
        C_tr, C_te, Y_tr, Y_te = load_split(name, data_root)
        ref = float(baselines[name]["test_nrmse"])
        Y = Y_te
        ybar = Y.mean(0, keepdims=True)
        ytrbar = Y_tr.mean(0, keepdims=True)
        Yf = Y - ybar
        ynorm = np.linalg.norm(Y, axis=1)
        d2 = ((C_te[:, None, :] - C_tr[None, :, :]) ** 2).sum(2)
        dnn = np.sqrt(d2.min(1))
        d = {"copylf_ref_nrmse": ref,
             "reference_type": baselines[name]["reference_type"],
             "truth_fluct_share_of_energy": float((Yf ** 2).sum() / (Y ** 2).sum()),
             "const_arms_skill": {
                 "train_mean_floor": NR.nrmse(np.broadcast_to(ytrbar, Y.shape), Y) / ref,
                 "test_mean_ORACLE": NR.nrmse(np.broadcast_to(ybar, Y.shape), Y) / ref},
             "arms": {}}
        P_all, worst = {}, {}
        for path in paths:
            P = np.load(path).reshape(Y.shape[0], -1).astype(np.float64)
            P_all[path] = P
            pbar = P.mean(0, keepdims=True)
            Pf = P - pbar
            R = float((Pf ** 2).sum() / max((Yf ** 2).sum(), 1e-300))
            A = float((Pf * Yf).sum() / max(frob(Pf) * frob(Yf), 1e-300))
            rel = np.linalg.norm(P - Y, axis=1) / ynorm
            amp = np.linalg.norm(P, axis=1) / ynorm
            cos = (P * Y).sum(1) / (np.linalg.norm(P, axis=1) * ynorm)
            worst[path] = set(np.argsort(rel)[::-1][:10].tolist())
            sk = {f"{lam}": NR.nrmse(pbar + lam * (P - pbar), Y) / ref for lam in LAMS}
            lam_star = float(min(sk, key=lambda t: sk[t]))
            d["arms"][path] = {
                "skill": rel.mean() / ref,
                "skill_of_own_mean_field_broadcast":
                    NR.nrmse(np.broadcast_to(pbar, Y.shape), Y) / ref,
                "fluct_energy_ratio_R": R, "fluct_alignment_A": A,
                "useful_fluct_share": float(2 * A * np.sqrt(R) - R),
                "mean_field_vs_train_mean_reldist":
                    float(frob(pbar - ytrbar) / max(frob(ytrbar), 1e-300)),
                "shrinkage_TEST_FITTED_ORACLE": {
                    "skill_by_lambda": sk, "lambda_star": lam_star,
                    "skill_at_lambda_star": sk[f"{lam_star}"],
                    "skill_at_lambda_1": sk["1.0"]},
                "per_sample": {
                    "rel_l2_p50": float(np.percentile(rel, 50)),
                    "rel_l2_p90": float(np.percentile(rel, 90)),
                    "rel_l2_max": float(rel.max()),
                    "top10_share_of_summed_rel":
                        float(np.sort(rel)[::-1][:10].sum() / rel.sum()),
                    "n_samples_skill_lt_1": int((rel / ref < 1).sum()),
                    "median_sample_skill": float(np.median(rel) / ref),
                    "cosine_median": float(np.median(cos)),
                    "cosine_p10": float(np.percentile(cos, 10)),
                    "amplitude_ratio_median": float(np.median(amp)),
                    "amplitude_ratio_max": float(amp.max()),
                    "spearman_rel_vs_ynorm": spearman(rel, ynorm),
                    "spearman_rel_vs_amplitude_ratio": spearman(rel, amp),
                    "spearman_rel_vs_dist_to_nearest_train_cond": spearman(rel, dnn)},
            }
            a = d["arms"][path]
            print(f"[{name}] {Path(path).name}: skill {a['skill']:.4f} | own-mean "
                  f"{a['skill_of_own_mean_field_broadcast']:.4f} | R={R:.4f} A={A:.4f}"
                  f" useful={a['useful_fluct_share']:.4f} lam*={lam_star}", flush=True)
        if len(paths) > 1:
            pair = {}
            for i, a in enumerate(paths):
                for b in paths[i + 1:]:
                    Pa, Pb = P_all[a], P_all[b]
                    fa = Pa - Pa.mean(0, keepdims=True)
                    fb = Pb - Pb.mean(0, keepdims=True)
                    pair[f"{Path(a).name}|{Path(b).name}"] = {
                        "rel_dist_full": float(frob(Pa - Pb) / frob(Pa)),
                        "fluct_cosine":
                            float((fa * fb).sum() / max(frob(fa) * frob(fb), 1e-300)),
                        "worst10_overlap": len(worst[a] & worst[b])}
            d["arm_agreement"] = pair
        res["datasets"][name] = d
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=1))
    print("[wrote]", args.out)


if __name__ == "__main__":
    main()
