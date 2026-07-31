#!/usr/bin/env python
"""reachable_set_rank_audit.py -- HOW MANY DIMENSIONS DOES A TRAINED MODEL'S
OUTPUT FAMILY ACTUALLY SPAN, AND IS THAT THE RIGHT NUMBER?

Given a trained model's OUTPUTS on a set of conditions (supplied as arrays; the
tool never imports a family), this measures the dimension of the reachable set
the model can emit and places it between two reference numbers computed from the
data alone:

  * `truth_r99`      -- the dimension of the TRUE field family it is imitating;
  * `n_pcs_learnable`-- how many of that family's POD coefficients are
                        predictable from the condition vector out of sample.

Three outcomes, and they call for opposite next moves:

  RANK_MATCHES_LEARNABLE  model r99 ~ n_pcs_learnable << truth r99.  The
      collapse is a CORRECT response to a target the condition cannot select.
      Capacity, epochs and richer conditioning paths all buy nothing; the lever
      is the condition parameterisation or the sampling design.
  RANK_BELOW_LEARNABLE    model r99 materially under n_pcs_learnable.  A real
      LEARNING gap: the information is in the condition and the trained weights
      do not carry it.  Optimisation / conditioning / loss are live levers.
  RANK_MATCHES_TRUTH      the reachable set is adequate; any remaining error is
      coefficient placement, not representation.

WHY THIS EXISTS
---------------
`r2s2_stacked-B1` turn 1 read the emulator's code (coordinates-only input, all
sample dependence through spatially-constant FiLM) and concluded its reachable
set had to be "a fixed spatial dictionary under a global rescale" -- the measured
symptom (rank-1, low-passed outputs on pfc / allen_cahn / fisher_kpp) fit
perfectly.  Turn 2 ran this probe and FALSIFIED that: the identical architecture,
width, blocks and modes emits a rank-22 field family on `sharp__cahn_hilliard`
matching the truth's rank 22, and a rank-6 one on `fluid` matching the truth's
rank 6, and reproduces the truth's band>=1 pattern-diversity statistic to three
decimals on both guards.  What the rank tracks is the LEARNABLE rank, dataset by
dataset (pfc 26 truth / 1 model / 1 learnable; allen_cahn 33 / 1 / 1; fisher_kpp
139 / 1 / 1; cahn_hilliard 22 / 22 / 3; fluid 6 / 6 / 25).  A correct code
reading plus a correct symptom prediction was still the wrong mechanism -- run
the measurement.

RELATION TO NEIGHBOURING TOOLS (the identifiability TRIAD)
----------------------------------------------------------
Three tools ask "is this task information-limited?" along three different axes;
they are complements, not substitutes, and a dataset can look limited on one and
healthy on another.

  1. `condition_identifiable_rank.py` (r2s1_direct-B1) -- FIELD-basis axis, no
     model.  Per-POD-mode out-of-fold R^2 of the coefficient predicted from the
     condition, on the TRUE fields: how many knobs EXIST.
  2. `affine_ladder_voi.py` (r2s3_lf_train_signal-B1) -- CONDITION-side axis, no
     model.  Whether the few HF training rows SPAN the design at all, the null
     space they cannot constrain, and what LF rows at other conditions are worth
     as the fix: whether the DESIGN can identify the knobs.
  3. this tool -- TRAINED-MODEL-OUTPUT axis.  How many knobs the trained weights
     actually turn, on real and on synthetic conditions.  It is the only one of
     the three that can say "the model is under the ceiling" as opposed to
     "the ceiling is low", because it measures the fitted object.

Order of use: (1) or (2) first for the ceiling, this third for the gap to it.
Section D of this tool overlaps (1) deliberately -- it recomputes a learnable
rank on the SAME split as the model outputs, so the model/ceiling comparison is
apples-to-apples; `condition_identifiable_rank.py` remains the better-regularised
standalone (K-fold alpha, RFF features) when no model is in hand.

WHAT IT REPORTS
---------------
  A rank_anatomy.*            participation-ratio effective rank, r90, r99 and
                              top-1 energy share (uncentered AND centered) of
                              the truth's rows and of the model's outputs on
                              (a) the fit conditions, (b) synthetic conditions
                              drawn over the train box, (c) synthetic conditions
                              3 sd around the train mean -- (c) probes the
                              trained function, not the data distribution
  B band_fixed_pattern.*      per dyadic band (s2-B1 grid, 4 bands), the mean
                              pairwise |cos| of the per-sample Fourier
                              coefficient vectors and their effective rank:
                              1.0 = ONE fixed pattern rescaled per sample.
                              Compare model vs truth band by band
  C dictionary_vs_coefficients.*
                              ORACLE projection of the held-out TRUE fields onto
                              (i) the model's own rank-r output subspace and
                              (ii) the truth's own rank-r subspace.  (i) ~ (ii)
                              -> the dictionary is fine and the coefficient map
                              is the bottleneck; (i) >> (ii) -> the dictionary is
  D pc_learnability.*         out-of-sample R^2 of each truth-PC coefficient
                              predicted from the condition (ridge and 5-NN), the
                              count above 0.5, and the nRMSE of
                              basis+LEARNED-coefficients at each rank -- the
                              training-free condition-only ceiling in the
                              model's own target space
  E cond_map_continuity.*     nearest-condition-neighbour test, band by band:
                              median relative field difference and median cosine
                              between a held-out sample and its nearest fit
                              sample in standardised condition space.  band>=1
                              cosine ~ 0 at small nn distance = the realised
                              high-band content is NOT a function of the
                              condition (ADR r2-0003's structural ceiling,
                              measured; r2s2-B1 pfc: nn distance 0.132 sd,
                              band0 cosine +1.000, band>=1 cosine -0.002)
  verdict.*                   the three-way label above + `structural_
                              discontinuity` + the model-vs-ceiling comparison

READ IT AS
----------
* `verdict.label = RANK_MATCHES_LEARNABLE` and `structural_discontinuity = true`
  -> stop tuning this stage.  The conditional mean IS the answer; only a
  realisation-aware (stochastic / IC-carrying) formulation or a different
  condition vector changes the number.
* `RANK_BELOW_LEARNABLE` -> the one shape of result that justifies more training
  work on the same data.  r2s2-B1 found exactly one panel column here
  (`ext__helmholtz_2d`: continuous map, nn band>=1 cosine +0.931, model r99 3 vs
  truth 5).
* `dictionary_vs_coefficients.emulator_dict_oracle[r]` far ABOVE
  `truth_dict_oracle[r]` at the same r -> the model's span is the problem, and a
  richer output head is worth trying.  Equal -> it is not.
* Section D's `learned_reconstruction_nrmse` WORSE than the model's own held-out
  error means the model is at or past the training-free condition-only ceiling.
  Quote that before proposing any "better condition->field" design.

LEGALITY
--------
TRAIN-split fields only; the test split is opened solely to assert it exposes no
LF fidelity (the round's stripped-view gate).  Every field score goes through the
round's own `eval/nrmse.py`.  Rows named `*_oracle` are ORACLE projections of
held-out TRUE fields onto a basis and are CEILINGS, never scoreable arm values.

INVOCATION (two steps; the tool never runs your model)
------------------------------------------------------
    source "$PROJECT_ROOT/.venv/bin/activate"

    # 1. emit the condition design (fit rows, val rows, 2 synthetic draws)
    python tools/reachable_set_rank_audit.py --dataset sharp__phase_field_crystal_2d \
        --target lf --gen_conds --conds_out conds.npz --out plan.json

    # 2. run YOUR model forward on conds.npz's X_fit / X_val / X_synth_box /
    #    X_synth_wide3sd (same row order), then feed the outputs back
    python tools/reachable_set_rank_audit.py --dataset sharp__phase_field_crystal_2d \
        --target lf --conds conds.npz \
        --pred_fit preds.npz:fit --pred_val preds.npz:val \
        --pred_synth_box preds.npz:box --pred_synth_wide preds.npz:wide \
        --out reachable.json

    # training-free half only (sections D + E; no model needed)
    python tools/reachable_set_rank_audit.py --dataset sharp__cahn_hilliard \
        --target lf --out ceiling_only.json

`--fit_idx/--val_idx` accept .npy index files when you need the audit on YOUR
family's exact split (that is how the r2s2-B1 numbers are reproduced).
`--pred_*` accept `path.npy` or `path.npz:key`; shapes (N, H, W) or (N, n_cells).

Provenance: card `experiment_cards/r2s2_stacked/batch_1/B1.json` part 6
(findings 3, 4, 5 and interpretation I2'/the ceiling taxonomy); source probe
`worktrees/r2s2_stacked/B1/scratchpad/reanalysis_turn_2.py` (P1-P4).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
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
from nrmse import NRMSE_DEF_HASH, nrmse                    # noqa: E402
from data_adapters.loaders import load_mf_dataset          # noqa: E402
from data_adapters.geometry import resolve_grid            # noqa: E402

RANKS = (1, 2, 4, 8, 16, 32, 64)
N_BANDS = 4


# ── band grid: the s2-B1 dyadic convention, copied so cross-card band
#    comparisons stay on ONE grid (source: models_r1/s2_copylf_forensics/
#    forensics.py, re-vendored in every DC-lineage family's bands.py) ──────────
def band_masks(grid, n_bands: int = N_BANDS):
    h, w_ = int(grid[0]), int(grid[1])
    kx = np.fft.fftfreq(h) * h
    ky = np.arange(w_ // 2 + 1, dtype=np.float64)
    kr = np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)
    weight = np.full((h, w_ // 2 + 1), 2.0)
    weight[:, 0] = 1.0
    if w_ % 2 == 0:
        weight[:, -1] = 1.0
    k_ny = min(h, w_) / 2.0
    edges = [0.0] + [k_ny / 2.0 ** (n_bands - 1 - b) for b in range(n_bands)]
    masks = []
    for b in range(n_bands):
        if b == n_bands - 1:
            masks.append(kr >= edges[b])
        else:
            masks.append((kr >= edges[b]) & (kr < edges[b + 1]))
    return masks, weight, edges


# ── linear algebra helpers (Gram-based: n << P here) ────────────────────────
def sv_from_gram(A):
    A = np.asarray(A, np.float64)
    ev = np.linalg.eigvalsh(A @ A.T)
    return np.sqrt(np.maximum(ev, 0.0))[::-1]


def right_basis(A, r):
    A = np.asarray(A, np.float64)
    r = int(min(r, min(A.shape)))
    G = A @ A.T
    ev, U = np.linalg.eigh(G)
    order = np.argsort(ev)[::-1][:r]
    ev, U = np.maximum(ev[order], 0.0), U[:, order]
    s = np.sqrt(np.maximum(ev, 1e-300))
    return np.ascontiguousarray(((A.T @ U) / s[None, :]).T)


def spectrum(A):
    def _anat(M):
        s = sv_from_gram(M)
        e = s ** 2
        tot = float(e.sum())
        if tot <= 0:
            return {"eff_rank_pr": 0.0, "r90": 0, "r99": 0, "top1_share": None,
                    "energy_frac": []}
        c = np.cumsum(e) / tot
        return {
            "eff_rank_pr": float(tot ** 2 / float((e ** 2).sum())),
            "r90": int(np.searchsorted(c, 0.90) + 1),
            "r99": int(np.searchsorted(c, 0.99) + 1),
            "top1_share": float(e[0] / tot),
            "energy_frac": [float(c[min(r, len(c)) - 1]) for r in RANKS if r <= len(c)],
        }
    A = np.asarray(A, np.float64)
    return {"uncentered": _anat(A), "centered": _anat(A - A.mean(0, keepdims=True)),
            "ranks_for_energy_frac": [r for r in RANKS if r <= min(A.shape)]}


def band_coeff_matrix(F, grid, mask, weight):
    H, W = int(grid[0]), int(grid[1])
    fc = np.fft.rfft2(np.asarray(F, np.float64).reshape(-1, H, W))
    wm = np.sqrt(weight[mask])[None, :]
    z = fc[:, mask] * wm
    return np.concatenate([z.real, z.imag], axis=1)


def pairwise_cos_stats(Z):
    n = np.linalg.norm(Z, axis=1, keepdims=True)
    keep = (n[:, 0] > 0)
    Zn = Z[keep] / n[keep]
    if Zn.shape[0] < 2:
        return {"mean_cos": None, "mean_abscos": None, "n": int(Zn.shape[0])}
    G = Zn @ Zn.T
    iu = np.triu_indices(G.shape[0], 1)
    v = G[iu]
    e = np.linalg.svd(Zn, compute_uv=False) ** 2
    return {"mean_cos": float(v.mean()), "mean_abscos": float(np.abs(v).mean()),
            "p10_abscos": float(np.percentile(np.abs(v), 10)),
            "eff_rank_pr": float(e.sum() ** 2 / (e ** 2).sum()),
            "n": int(Zn.shape[0])}


def ridge_fit(Xf, Yf, lam=1e-6):
    mu, sd = Xf.mean(0), Xf.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    A = np.hstack([(Xf - mu) / sd, np.ones((len(Xf), 1))])
    G = A.T @ A + lam * np.eye(A.shape[1])
    Wm = np.linalg.solve(G, A.T @ Yf)
    return lambda Xq: np.hstack([(Xq - mu) / sd, np.ones((len(Xq), 1))]) @ Wm


def knn_fit(Xf, Yf, k):
    mu, sd = Xf.mean(0), Xf.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    A = (Xf - mu) / sd

    def f(Xq):
        B = (Xq - mu) / sd
        d = ((B[:, None, :] - A[None, :, :]) ** 2).sum(-1)
        idx = np.argsort(d, axis=1)[:, :min(k, A.shape[0])]
        return Yf[idx].mean(axis=1)
    return f


def r2_cols(pred, true):
    ss_res = ((pred - true) ** 2).sum(0)
    ss_tot = ((true - true.mean(0, keepdims=True)) ** 2).sum(0)
    return np.where(ss_tot > 0, 1.0 - ss_res / np.maximum(ss_tot, 1e-300), np.nan)


def load_array(spec, n_cells):
    """`path.npy` or `path.npz:key` -> (N, n_cells) float64."""
    if spec is None:
        return None
    path, _, key = str(spec).partition(":")
    if path.endswith(".npz"):
        with np.load(path) as z:
            arr = z[key] if key else z[list(z.keys())[0]]
    else:
        arr = np.load(path)
    arr = np.asarray(arr, np.float64)
    arr = arr.reshape(arr.shape[0], -1)
    if arr.shape[1] != n_cells:
        raise ValueError(f"{spec}: {arr.shape[1]} cells, dataset has {n_cells}")
    return arr


# ── main ────────────────────────────────────────────────────────────────────
def run_dataset(name, data_root, target, rung, fit_idx, val_idx, holdout_frac,
                seed, max_fit, max_val, n_synth, preds, conds_npz, ranks):
    t0 = time.time()
    ds_dir = Path(data_root) / name
    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")
    if test["lf_fids"]:
        raise AssertionError(f"{name}: test split exposes LF {test['lf_fids']} "
                             "(stripped-view gate)")
    if target == "hf":
        fid = test["hf_fid"]
    else:
        lfs = sorted(train["lf_fids"])
        if not lfs:
            raise ValueError(f"{name}: no LF fidelity in the train split")
        fid = lfs[-1] if rung == "max" else int(rung)
    Y = np.asarray(train["field_by_fid"][fid], np.float64)
    X = np.asarray(train["cond_by_fid"][fid], np.float64)
    n_cells = Y.shape[1]
    grid = resolve_grid(name, int(n_cells))
    N = Y.shape[0]

    if fit_idx is None or val_idx is None:
        rng = np.random.default_rng(seed)
        perm = rng.permutation(N)
        n_val = max(1, min(int(round(holdout_frac * N)), N - 1))
        val_idx = np.sort(perm[:n_val])
        fit_idx = np.sort(perm[n_val:])
    fit_idx = np.asarray(fit_idx, np.int64)
    val_idx = np.asarray(val_idx, np.int64)
    n_fit_full = int(len(fit_idx))
    if len(fit_idx) > max_fit:
        fit_idx = fit_idx[:max_fit]
    if len(val_idx) > max_val:
        val_idx = val_idx[:max_val]

    Y_fit, Y_val = Y[fit_idx], Y[val_idx]
    X_fit, X_val = X[fit_idx], X[val_idx]

    # synthetic condition designs (emitted, and reused verbatim when handed back)
    if conds_npz is not None:
        X_box = np.asarray(conds_npz["X_synth_box"], np.float64)
        X_wide = np.asarray(conds_npz["X_synth_wide3sd"], np.float64)
    else:
        rng = np.random.default_rng(20260731)
        lo, hi = X_fit.min(0), X_fit.max(0)
        X_box = rng.random((n_synth, X.shape[1])) * (hi - lo) + lo
        mu_c, sd_c = X_fit.mean(0), X_fit.std(0)
        X_wide = mu_c + 3.0 * np.where(sd_c > 0, sd_c, 1.0) * \
            rng.standard_normal((n_synth, X.shape[1]))

    out = {
        "dataset": name, "target": target, "fidelity": int(fid),
        "grid": [int(grid[0]), int(grid[1])], "cond_dim": int(X.shape[1]),
        "n_fit": int(len(fit_idx)), "n_fit_full": n_fit_full,
        "n_val": int(len(val_idx)), "n_synth": int(X_box.shape[0]),
        "fit_idx_sha": int(abs(hash(fit_idx.tobytes())) % (10 ** 12)),
        "nrmse_def_hash": NRMSE_DEF_HASH,
    }
    masks, weight, edges = band_masks(grid)
    hi_mask = np.zeros_like(masks[0])
    for m in masks[1:]:
        hi_mask |= m
    band_list = [("band0", masks[0]), ("band1", masks[1]), ("band_ge1", hi_mask)]

    has_model = preds.get("fit") is not None and preds.get("val") is not None
    out["model_half"] = "present" if has_model else "skipped (no --pred_fit/--pred_val)"

    # ── A rank anatomy ──────────────────────────────────────────────────────
    rank = {"truth_fit": spectrum(Y_fit)}
    if has_model:
        rank["model_fit"] = spectrum(preds["fit"])
        if preds.get("synth_box") is not None:
            rank["model_synth_box"] = spectrum(preds["synth_box"])
        if preds.get("synth_wide") is not None:
            rank["model_synth_wide3sd"] = spectrum(preds["synth_wide"])
    out["rank_anatomy"] = rank

    # ── B fixed-pattern test ────────────────────────────────────────────────
    per_band = {}
    for label, m in band_list:
        if not m.any():
            continue
        rec = {"truth": pairwise_cos_stats(band_coeff_matrix(Y_val, grid, m, weight))}
        if has_model:
            rec["model"] = pairwise_cos_stats(
                band_coeff_matrix(preds["val"], grid, m, weight))
            if preds.get("synth_wide") is not None:
                rec["model_synth_wide3sd"] = pairwise_cos_stats(
                    band_coeff_matrix(preds["synth_wide"], grid, m, weight))
        per_band[label] = rec
    out["band_fixed_pattern"] = per_band

    # ── C dictionary vs coefficients ────────────────────────────────────────
    r_top = int(min(max(ranks), len(fit_idx), n_cells))
    Vy_all = right_basis(Y_fit, r_top)
    dict_probe = {"truth_dict_oracle": {}}
    if has_model:
        Ve_all = right_basis(preds["fit"], r_top)
        dict_probe["model_dict_oracle"] = {}
        dict_probe["model_output_in_truth_span"] = {}
    for r in ranks:
        if r > r_top:
            continue
        Vy = Vy_all[:r]
        dict_probe["truth_dict_oracle"][str(r)] = nrmse((Y_val @ Vy.T) @ Vy, Y_val)
        if has_model:
            Ve = Ve_all[:r]
            dict_probe["model_dict_oracle"][str(r)] = nrmse((Y_val @ Ve.T) @ Ve, Y_val)
            dict_probe["model_output_in_truth_span"][str(r)] = float(
                np.linalg.norm((preds["val"] @ Vy.T) @ Vy)
                / max(np.linalg.norm(preds["val"]), 1e-30))
    dict_probe["_caveat"] = ("model_dict_oracle at ranks above the model's own r99 "
                            "uses numerically degenerate directions (Gram basis); "
                            "read the low-rank columns")
    out["dictionary_vs_coefficients"] = dict_probe

    # ── D learnable rank of the TRUTH's coefficients ────────────────────────
    r_max = int(min(64, len(fit_idx) - 1, n_cells))
    Vy = Vy_all[:r_max] if r_max <= r_top else right_basis(Y_fit, r_max)
    Cf, Cq = Y_fit @ Vy.T, Y_val @ Vy.T
    f_r, f_k = ridge_fit(X_fit, Cf), knn_fit(X_fit, Cf, 5)
    Cr, Ck = f_r(X_val), f_k(X_val)
    r2_ridge, r2_knn = r2_cols(Cr, Cq), r2_cols(Ck, Cq)
    learned = {}
    for r in ranks:
        if r > r_max:
            continue
        learned[str(r)] = {"ridge_coeff": nrmse(Cr[:, :r] @ Vy[:r], Y_val),
                           "knn5_coeff": nrmse(Ck[:, :r] @ Vy[:r], Y_val)}
    _ey = sv_from_gram(Y_fit) ** 2
    best_learned = min([min(v.values()) for v in learned.values()]) if learned else None
    out["pc_learnability"] = {
        "r_max": r_max,
        "pc_energy_share_fit": [float(x) for x in (_ey[:8] / max(float(_ey.sum()), 1e-30))],
        "r2_ridge_first8": [None if np.isnan(v) else float(v) for v in r2_ridge[:8]],
        "r2_knn5_first8": [None if np.isnan(v) else float(v) for v in r2_knn[:8]],
        "n_pcs_ridge_r2_gt_0p5": int(np.nansum(r2_ridge > 0.5)),
        "n_pcs_knn_r2_gt_0p5": int(np.nansum(r2_knn > 0.5)),
        "n_pcs_best_r2_gt_0p5": int(np.nansum(np.fmax(r2_ridge, r2_knn) > 0.5)),
        "learned_reconstruction_nrmse": learned,
        "best_learned_reconstruction_nrmse": best_learned,
    }

    # ── E nearest-condition-neighbour continuity, band by band ──────────────
    mu_s, sd_s = X_fit.mean(0), np.where(X_fit.std(0) > 0, X_fit.std(0), 1.0)
    A, B = (X_fit - mu_s) / sd_s, (X_val - mu_s) / sd_s
    d = ((B[:, None, :] - A[None, :, :]) ** 2).sum(-1)
    nn = np.argmin(d, axis=1)
    nn_dist = np.sqrt(d[np.arange(len(B)), nn])
    cont = {"nn_cond_dist_median": float(np.median(nn_dist))}
    for label, m in band_list:
        if not m.any():
            continue
        Zq = band_coeff_matrix(Y_val, grid, m, weight)
        Zn = band_coeff_matrix(Y_fit[nn], grid, m, weight)
        num = np.linalg.norm(Zq - Zn, axis=1)
        den = np.maximum(np.linalg.norm(Zq, axis=1), 1e-30)
        cs = (Zq * Zn).sum(1) / np.maximum(
            np.linalg.norm(Zq, axis=1) * np.linalg.norm(Zn, axis=1), 1e-30)
        cont[label] = {"nn_rel_diff_median": float(np.median(num / den)),
                       "nn_cosine_median": float(np.median(cs))}
    out["cond_map_continuity"] = cont

    # ── verdict ─────────────────────────────────────────────────────────────
    truth_r99 = rank["truth_fit"]["uncentered"]["r99"]
    n_learn = out["pc_learnability"]["n_pcs_best_r2_gt_0p5"]
    struct = bool(cont.get("band_ge1", {}).get("nn_cosine_median", 1.0) < 0.10
                  and cont.get("band0", {}).get("nn_cosine_median", 0.0) > 0.90)
    verdict = {"truth_r99": int(truth_r99), "n_pcs_learnable": int(n_learn),
               "structural_discontinuity": struct,
               "nn_cond_dist_median": cont["nn_cond_dist_median"]}
    if has_model:
        model_r99 = rank["model_fit"]["uncentered"]["r99"]
        verdict["model_r99"] = int(model_r99)
        verdict["model_r99_synth_wide3sd"] = (
            int(rank["model_synth_wide3sd"]["uncentered"]["r99"])
            if "model_synth_wide3sd" in rank else None)
        verdict["model_heldout_nrmse"] = nrmse(preds["val"], Y_val)
        verdict["model_over_learned_ceiling"] = (
            None if best_learned is None else
            float(verdict["model_heldout_nrmse"] / max(best_learned, 1e-300)))
        if model_r99 < max(1, 0.5 * n_learn):
            label = "RANK_BELOW_LEARNABLE"
        elif model_r99 >= 0.8 * truth_r99:
            label = "RANK_MATCHES_TRUTH"
        elif model_r99 <= max(1.5 * max(n_learn, 1), n_learn + 1):
            label = "RANK_MATCHES_LEARNABLE"
        else:
            label = "MIXED"
        verdict["label"] = label
    else:
        verdict["label"] = "CEILING_ONLY (no model outputs supplied)"
    out["verdict"] = verdict
    out["seconds"] = float(time.time() - t0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--data_root", default=str(PATHS["stripped_data_root"]))
    ap.add_argument("--target", default="lf", choices=["lf", "hf"],
                    help="which train-split field family the model imitates")
    ap.add_argument("--rung", default="max", help="LF fidelity id, or 'max'")
    ap.add_argument("--fit_idx", default=None, help=".npy of train row indices")
    ap.add_argument("--val_idx", default=None, help=".npy of held-out row indices")
    ap.add_argument("--holdout_frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max_fit", type=int, default=200)
    ap.add_argument("--max_val", type=int, default=80)
    ap.add_argument("--n_synth", type=int, default=80)
    ap.add_argument("--ranks", default="1,2,4,8,16,32,64")
    ap.add_argument("--gen_conds", action="store_true",
                    help="emit the condition design and exit (step 1)")
    ap.add_argument("--conds_out", default=None)
    ap.add_argument("--conds", default=None,
                    help="the .npz emitted by --gen_conds (reuses its synth draws)")
    ap.add_argument("--pred_fit", default=None)
    ap.add_argument("--pred_val", default=None)
    ap.add_argument("--pred_synth_box", default=None)
    ap.add_argument("--pred_synth_wide", default=None)
    args = ap.parse_args()

    ranks = tuple(int(x) for x in args.ranks.split(",") if x.strip())
    fit_idx = np.load(args.fit_idx) if args.fit_idx else None
    val_idx = np.load(args.val_idx) if args.val_idx else None

    if args.gen_conds:
        if not args.conds_out:
            raise SystemExit("--gen_conds requires --conds_out")
        ds_dir = Path(args.data_root) / args.dataset
        train = load_mf_dataset(ds_dir, "train")
        test = load_mf_dataset(ds_dir, "test")
        if test["lf_fids"]:
            raise AssertionError(f"{args.dataset}: test exposes LF {test['lf_fids']}")
        if args.target == "hf":
            fid = test["hf_fid"]
        else:
            lfs = sorted(train["lf_fids"])
            fid = lfs[-1] if args.rung == "max" else int(args.rung)
        X = np.asarray(train["cond_by_fid"][fid], np.float64)
        N = X.shape[0]
        if fit_idx is None or val_idx is None:
            rng0 = np.random.default_rng(args.seed)
            perm = rng0.permutation(N)
            n_val = max(1, min(int(round(args.holdout_frac * N)), N - 1))
            val_idx = np.sort(perm[:n_val])
            fit_idx = np.sort(perm[n_val:])
        fit_idx, val_idx = np.asarray(fit_idx, np.int64), np.asarray(val_idx, np.int64)
        if len(fit_idx) > args.max_fit:
            fit_idx = fit_idx[:args.max_fit]
        if len(val_idx) > args.max_val:
            val_idx = val_idx[:args.max_val]
        X_fit = X[fit_idx]
        rng = np.random.default_rng(20260731)
        lo, hi = X_fit.min(0), X_fit.max(0)
        X_box = rng.random((args.n_synth, X.shape[1])) * (hi - lo) + lo
        mu_c, sd_c = X_fit.mean(0), X_fit.std(0)
        X_wide = mu_c + 3.0 * np.where(sd_c > 0, sd_c, 1.0) * \
            rng.standard_normal((args.n_synth, X.shape[1]))
        Path(args.conds_out).parent.mkdir(parents=True, exist_ok=True)
        np.savez(args.conds_out, X_fit=X_fit, X_val=X[val_idx],
                 X_synth_box=X_box, X_synth_wide3sd=X_wide,
                 fit_idx=fit_idx, val_idx=val_idx)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump({"_tool": "reachable_set_rank_audit", "_step": "gen_conds",
                   "dataset": args.dataset, "target": args.target,
                   "fidelity": int(fid), "conds_out": args.conds_out,
                   "n_fit": int(len(fit_idx)), "n_val": int(len(val_idx)),
                   "n_synth": int(args.n_synth), "cond_dim": int(X.shape[1])},
                  open(args.out, "w"), indent=1)
        print(f"wrote {args.conds_out} (fit {len(fit_idx)}, val {len(val_idx)}, "
              f"synth {args.n_synth} x2) and {args.out}")
        return

    conds_npz = None
    if args.conds:
        conds_npz = dict(np.load(args.conds))
        if fit_idx is None:
            fit_idx, val_idx = conds_npz["fit_idx"], conds_npz["val_idx"]

    ds_dir = Path(args.data_root) / args.dataset
    tr = load_mf_dataset(ds_dir, "train")
    te = load_mf_dataset(ds_dir, "test")
    fid = te["hf_fid"] if args.target == "hf" else (
        sorted(tr["lf_fids"])[-1] if args.rung == "max" else int(args.rung))
    n_cells = int(np.asarray(tr["field_by_fid"][fid]).shape[1])
    preds = {"fit": load_array(args.pred_fit, n_cells),
             "val": load_array(args.pred_val, n_cells),
             "synth_box": load_array(args.pred_synth_box, n_cells),
             "synth_wide": load_array(args.pred_synth_wide, n_cells)}

    r = run_dataset(args.dataset, args.data_root, args.target, args.rung,
                    fit_idx, val_idx, args.holdout_frac, args.seed,
                    args.max_fit, args.max_val, args.n_synth, preds,
                    conds_npz, ranks)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"_tool": "reachable_set_rank_audit",
               "_nrmse_def_hash": NRMSE_DEF_HASH,
               "_note": "keys containing 'oracle' project held-out TRUE fields "
                        "onto a basis; they are ceilings, never arm scores",
               "result": r}, open(args.out, "w"), indent=1)
    v = r["verdict"]
    print(f"[{args.dataset}] truth_r99={v['truth_r99']} "
          f"model_r99={v.get('model_r99')} learnable={v['n_pcs_learnable']} "
          f"nn_dist={v['nn_cond_dist_median']:.3f} "
          f"struct_discont={v['structural_discontinuity']} "
          f"verdict={v['label']} ({r['seconds']:.1f}s)")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
