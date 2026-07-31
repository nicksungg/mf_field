#!/usr/bin/env python
"""Spectral pre-stage BOUNDARY-CONDITION audit — training-free.

Provenance: `s4_hybrid_routing-B3` mechanism analysis, turns 1-2
(`worktrees/s4_hybrid_routing/B3/scratchpad/reanalysis_turn_{1,2}.py`, findings
F5 / F7 / F8 in card `experiment_cards/s4_hybrid_routing/batch_3/B3.json` part 6).

WHAT IT MEASURES
----------------
Any MF stage of the form `C = irfft2( rfft2(LF) * T(k) )` — a fitted LSI defect
filter, a Wiener transfer function, a spectral pre-stage, a global FNO-style
convolution — **silently imposes a PERIODIC boundary condition on the domain**.
Where the dataset is genuinely periodic that is free and correct. Where it is
not, the stage injects an error that is concentrated in the outermost pixel
ring, and a LOCAL corrector downstream (finite receptive field, zeros padding)
cannot represent it, let alone remove it. s4-B3 measured a +92.8 % scored
regression from exactly this on `heat_local`, of which the single outermost ring
carried 49 % of the total error energy.

This tool answers, before any GPU is spent:

  1. Is this dataset periodic?  `wrap_continuity_ratio` on the HF TRAIN split
     (re-derived from `s6_local-B2 models_r1/s6_local_repair/periodicity.py`,
     cited not imported; the model's own data-driven switch, no physics — ADR 0009).
  2. How much does the BC choice cost?  Fit the SAME closed-form transfer
     function twice — once with the periodic (plain `rfft2`) extension, once on
     MIRROR-EXTENDED (even-symmetric ⇒ non-periodic) fields — select the scalar
     gain on a held-out slice with a line search that contains 0, and score both
     on test with the round's own metric.
  3. WHERE does each one fail?  Residual energy left by each pre-stage, binned by
     distance to the domain boundary, so a rim-localized failure is visible
     rather than averaged away.

ZERO gradient steps, zero novelty claimed. `fit_transfer` is classical local
Fourier analysis of coarse-grid defect operators (multigrid LFA); the only thing
this tool contributes is *scoring the BC choice as a decision*.

HOW TO READ IT
--------------
* `verdict == "periodic"` and `mirror_delta_pct` strongly positive
    -> a plain `rfft2` pre-stage is correct here; do not "fix" the boundary.
* `verdict == "non-periodic"` and `mirror_delta_pct` strongly negative
    -> the periodic pre-stage is leaking at the rim; apply the pre-stage with the
       same extension the downstream convolution uses. Expect the gain to be
       rim-localized (`ring_profile`).
* `verdict == "non-periodic"` and `mirror_delta_pct` ~ 0
    -> the pre-stage's problem is genuine FIT QUALITY, not the BC: one linear
       shift-invariant filter cannot represent this fidelity gap
       (`resid_frac_*` stays large under both extensions). Gate the pre-stage off.

The `resid_frac` numbers double as the `1 - rho_LSI` eligibility statistic:
s4-B3 F1 found `Spearman(1-rho, pre-stage benefit) = +0.857` over 7 datasets with
the sign separated perfectly at ~0.15.

USAGE
-----
    python tools/spectral_prestage_bc_audit.py --dataset heat_local
    python tools/spectral_prestage_bc_audit.py --dataset sharp__allen_cahn_2d \
        --seed 0 --holdout-frac 0.2 --out /tmp/bc_audit.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RING_EDGES = [0, 1, 2, 4, 8, 16, 10 ** 9]   # distance-to-boundary, in cells


def _round_root() -> Path:
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True, cwd=Path(__file__).resolve().parent
                         ).stdout.strip()
    return Path(top) / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
from nrmse import nrmse as round_nrmse                      # noqa: E402
from panel_data import copylf_prediction, load_split        # noqa: E402


# ── the model's own data-driven periodicity test (cited, re-derived) ─────────
def _rms(a) -> float:
    a = np.asarray(a, dtype=np.float64)
    return float(np.sqrt((a ** 2).mean())) if a.size else 0.0


def wrap_continuity_ratio(fields, grid, axis: int):
    """`RMS(f[0]-f[-1]) / RMS(f[1]-f[0])` along `axis` (1 = y, 2 = x); None if degenerate.

    Verbatim semantics of `s6_local-B2 periodicity.py::wrap_continuity_ratio`.
    """
    H, W = int(grid[0]), int(grid[1])
    f = np.asarray(fields, dtype=np.float64).reshape(-1, H, W)
    g = np.moveaxis(f, axis, 1)
    if g.shape[1] < 2:
        return None
    den = _rms(g[:, 1, :] - g[:, 0, :])
    if den <= 0.0:
        return None
    return _rms(g[:, 0, :] - g[:, -1, :]) / den


# ── the closed form (classical multigrid LFA; zero novelty) ─────────────────
def fit_transfer(LF, R, grid, ridge=0.0, bs=16):
    H, W = int(grid[0]), int(grid[1])
    num = np.zeros((H, W // 2 + 1), dtype=np.complex128)
    den = np.zeros((H, W // 2 + 1), dtype=np.float64)
    for i in range(0, LF.shape[0], bs):
        sl = slice(i, min(i + bs, LF.shape[0]))
        fl = np.fft.rfft2(np.asarray(LF[sl], dtype=np.float64).reshape(-1, H, W))
        fr = np.fft.rfft2(np.asarray(R[sl], dtype=np.float64).reshape(-1, H, W))
        num += (fr * np.conj(fl)).sum(axis=0)
        den += (np.abs(fl) ** 2).sum(axis=0)
    if float(ridge) != 0.0:
        den = den + float(ridge) * float(den.max() if den.size else 0.0)
    return np.where(den > 1e-20, num / np.maximum(den, 1e-20), 0.0)


def apply_transfer(LF, T, grid, bs=16):
    H, W = int(grid[0]), int(grid[1])
    out = np.empty((LF.shape[0], H * W), dtype=np.float64)
    for i in range(0, LF.shape[0], bs):
        sl = slice(i, min(i + bs, LF.shape[0]))
        fl = np.fft.rfft2(np.asarray(LF[sl], dtype=np.float64).reshape(-1, H, W))
        out[sl] = np.fft.irfft2(fl * T[None, :, :], s=(H, W)).reshape(-1, H * W)
    return out


def mirror_ext(a, H, W):
    """Even-symmetric (whole-sample) extension to (2H, 2W): a NON-periodic BC."""
    f = np.asarray(a, dtype=np.float64).reshape(-1, H, W)
    f = np.concatenate([f, f[:, :, ::-1]], axis=2)
    f = np.concatenate([f, f[:, ::-1, :]], axis=1)
    return f.reshape(f.shape[0], -1)


# ── held-out scalar gain: least squares + line search CONTAINING 0 ──────────
# Semantics of `s6_local-B1/B2 local_corrector.py::fit_alpha` (cited, re-derived).
MIN_GAIN = 1e-3


def _rel_l2(pred, target) -> float:
    p = np.asarray(pred, dtype=np.float64).reshape(pred.shape[0], -1)
    t = np.asarray(target, dtype=np.float64).reshape(target.shape[0], -1)
    den = np.maximum(np.sqrt((t ** 2).sum(axis=1)), 1e-8)
    return float(np.mean(np.sqrt(((p - t) ** 2).sum(axis=1)) / den))


def fit_alpha(R_val, C_val, base_val, Y_val):
    denom = float((C_val * C_val).sum())
    a_ls = float(np.clip((R_val * C_val).sum() / denom, 0.0, 1.5)) if denom > 1e-20 else 0.0
    cands = {float(np.clip(f * a_ls, 0.0, 1.5)) for f in (0.25, 0.5, 0.75, 1.0, 1.25)}
    cands |= {0.0, 0.25, 0.5, 1.0}
    base_r = _rel_l2(base_val, Y_val)
    best, best_r = 0.0, base_r
    for a in sorted(cands):
        r = _rel_l2(base_val + a * C_val, Y_val)
        if r < min(best_r, base_r * (1.0 - MIN_GAIN)):
            best, best_r = a, r
    return float(best)


def ring_labels(H, W):
    yy, xx = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    d = np.minimum(np.minimum(yy, H - 1 - yy), np.minimum(xx, W - 1 - xx))
    lab = np.zeros((H, W), dtype=int)
    for i in range(len(RING_EDGES) - 1):
        lab[(d >= RING_EDGES[i]) & (d < RING_EDGES[i + 1])] = i
    return lab.reshape(-1)


def audit(dataset: str, seed: int = 0, holdout_frac: float = 0.2,
          ridge: float = 0.0, tol: float = 1.25, n_probe: int = 32) -> dict:
    tr, te = load_split(dataset, "train"), load_split(dataset, "test")
    LF_tr, LF_te = copylf_prediction(tr), copylf_prediction(te)
    Y_tr = np.asarray(tr["field_by_fid"][tr["hf_fid"]], dtype=np.float64)[:LF_tr.shape[0]]
    Y_te = np.asarray(te["field_by_fid"][te["hf_fid"]], dtype=np.float64)
    hf_grid = te["grid_shape_by_fid"].get(te["hf_fid"])
    if hf_grid is None or int(hf_grid[0]) < 2 or int(hf_grid[1]) < 2:
        raise SystemExit(f"{dataset}: no 2-D HF grid ({hf_grid}); this audit is 2-D only")
    H, W = int(hf_grid[0]), int(hf_grid[1])

    # 1. the data-driven periodicity test, on HF TRAIN only
    probe = Y_tr[:int(n_probe)]
    ry = wrap_continuity_ratio(probe, (H, W), axis=1)
    rx = wrap_continuity_ratio(probe, (H, W), axis=2)
    finite = [r for r in (ry, rx) if r is not None and np.isfinite(r)]
    worst = max(finite) if finite else None
    verdict = ("non-periodic (degenerate denominator)" if worst is None
               else ("periodic" if worst <= float(tol) else "non-periodic"))

    # 2. the fit / holdout split (same construction the s6/s4 families use)
    Ntr = LF_tr.shape[0]
    rng = np.random.default_rng(int(seed))
    n_val = min(int(max(1, round(float(holdout_frac) * Ntr))), max(Ntr - 1, 0))
    perm = rng.permutation(Ntr)
    val_idx, fit_idx = perm[:n_val], perm[n_val:]
    R_tr, R_te = Y_tr - LF_tr, Y_te - LF_te

    out = {"dataset": dataset, "grid": [H, W], "seed": int(seed),
           "n_fit": int(len(fit_idx)), "n_val": int(len(val_idx)),
           "n_test": int(Y_te.shape[0]), "ridge": float(ridge),
           "periodicity": {"wrap_ratio_hf_train": {"y": ry, "x": rx},
                           "wrap_ratio_max": worst, "tol": float(tol),
                           "n_probe": int(min(int(n_probe), Y_tr.shape[0])),
                           "verdict": verdict,
                           "test": "wrap_continuity_ratio_hf_train"},
           "nrmse_copylf": round_nrmse(LF_te, Y_te), "branches": {}}

    lab = ring_labels(H, W)
    nb = len(RING_EDGES) - 1
    den_ring = np.array([float((R_te[:, lab == b] ** 2).mean()) for b in range(nb)])

    for name in ("periodic", "mirror"):
        if name == "periodic":
            T = fit_transfer(LF_tr[fit_idx], R_tr[fit_idx], (H, W), ridge)
            C_tr = apply_transfer(LF_tr, T, (H, W))
            C_te = apply_transfer(LF_te, T, (H, W))
        else:
            He, We = 2 * H, 2 * W
            T = fit_transfer(mirror_ext(LF_tr[fit_idx], H, W),
                             mirror_ext(R_tr[fit_idx], H, W), (He, We), ridge)
            C_tr = apply_transfer(mirror_ext(LF_tr, H, W), T, (He, We)
                                  ).reshape(-1, He, We)[:, :H, :W].reshape(Ntr, -1)
            C_te = apply_transfer(mirror_ext(LF_te, H, W), T, (He, We)
                                  ).reshape(-1, He, We)[:, :H, :W].reshape(Y_te.shape[0], -1)
        a = fit_alpha(R_tr[val_idx], C_tr[val_idx], LF_tr[val_idx], Y_tr[val_idx])
        res = R_te - a * C_te
        prof = [float((res[:, lab == b] ** 2).mean()) for b in range(nb)]
        out["branches"][name] = {
            "alpha": a,
            "nrmse_prestage": round_nrmse(LF_te + a * C_te, Y_te),
            "resid_frac": float((res ** 2).sum() / (R_te ** 2).sum()),
            "ring_profile_resid_frac": [p / d if d > 0 else float("nan")
                                        for p, d in zip(prof, den_ring)],
        }
    p, m = out["branches"]["periodic"], out["branches"]["mirror"]
    out["mirror_delta_pct"] = 100.0 * (m["nrmse_prestage"] - p["nrmse_prestage"]) / p["nrmse_prestage"]
    out["ring_edges"] = RING_EDGES[:-1] + ["inf"]
    out["ring_npix"] = [int((lab == b).sum()) for b in range(nb)]
    out["reading"] = (
        "mirror_delta_pct < 0 => the periodic pre-stage is leaking at the boundary and the "
        "matching extension is worth that much, training-free. mirror_delta_pct > 0 => the "
        "periodic BC was correct; do not repair it. |mirror_delta_pct| ~ 0 with a large "
        "resid_frac under BOTH extensions => the pre-stage's problem is fit quality, not the "
        "BC: gate the pre-stage off on this dataset.")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--holdout-frac", type=float, default=0.2)
    ap.add_argument("--ridge", type=float, default=0.0)
    ap.add_argument("--tol", type=float, default=1.25,
                    help="wrap-continuity tolerance (s6-B2 pre-registered 1.25)")
    ap.add_argument("--n-probe", type=int, default=32)
    ap.add_argument("--out", default=None, help="write the full result JSON here")
    a = ap.parse_args()
    r = audit(a.dataset, a.seed, a.holdout_frac, a.ridge, a.tol, a.n_probe)

    per = r["periodicity"]
    print(f"=== spectral pre-stage BC audit: {r['dataset']} grid={r['grid']}")
    print(f"  wrap-continuity ratio (HF train, n={per['n_probe']}): "
          f"y={per['wrap_ratio_hf_train']['y']} x={per['wrap_ratio_hf_train']['x']} "
          f"max={per['wrap_ratio_max']} tol={per['tol']} -> {per['verdict'].upper()}")
    print(f"  copy-LF nRMSE = {r['nrmse_copylf']:.6e}")
    print(f"  {'extension':10s} {'alpha':>7s} {'nRMSE':>13s} {'resid frac':>11s}")
    for k in ("periodic", "mirror"):
        b = r["branches"][k]
        print(f"  {k:10s} {b['alpha']:7.4f} {b['nrmse_prestage']:13.6e} {b['resid_frac']:11.5f}")
    print(f"  mirror vs periodic: {r['mirror_delta_pct']:+.2f} %")
    print("  residual-energy fraction left, by distance-to-boundary ring "
          f"({', '.join(str(e) for e in r['ring_edges'])}):")
    for k in ("periodic", "mirror"):
        print(f"    {k:10s} " + " ".join(
            f"{x:8.4f}" for x in r["branches"][k]["ring_profile_resid_frac"]))
    print("  " + r["reading"])
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        with open(a.out, "w") as f:
            json.dump(r, f, indent=1, default=float)
        print("  wrote", a.out)


if __name__ == "__main__":
    main()
