"""Training-free defect-correction learnability probe.

Answers, before any model is written: **is the residual `R = HF - interp(LF)` a
fixed operator of the LF field on this dataset?** — i.e. does an additive
corrector that consumes the real interpolated LF field have headroom, how much of
it a ZERO-parameter closed-form filter already gets, whether the operator is
spatially LOCAL, and whether a held-out trust switch would shut it off.

Per dataset it fits ONE ridge-regularised per-frequency transfer function
`T(k) = sum_n R_hat LF_hat* / (sum_n |LF_hat|^2 + lam)` on the HF-train split
(20 % held out), then:

| key | meaning |
|---|---|
| `nrmse_LSI_defect_correction` / `skill_LSI` | score of `LF + T*LF` on the TEST split, through `round1/eval/nrmse.py`; a zero-trained-parameter baseline any learned corrector must beat |
| `rho_fit_in_sample` / `rho_val_heldout` / `generalization_gap_rho` | residual-explained fraction in and out of sample; `rho_val` is the load-bearing number |
| `heldout_trust_switch_alpha` | the card-s6 stage-3 protocol (line search including 0, MIN_GAIN 1e-3) run on the closed-form arm — 0 means "a no-harm gate should switch the corrector off here" |
| `stencil.frac_energy_within_12_cells`, `radius_50pct_energy` | compactness of the fitted operator's impulse response — is defect correction LOCAL? |
| `band_mean_abs_T` | the defect's amplitude law by radial band (edges = `[0,.125,.25,.5,1] * k_nyquist`, the round's band convention). Rising to ~1 at the top band = "undo the interpolation low-pass"; ~0.1-0.2 in band 0 = a systematic coarse-solve truncation gain |
| `predicted_verdict` | STRONG (`rho_val > 0.9`) / MODERATE (> 0.5) / WEAK (> 0.1) / NO headroom |

**Read it as.** `rho_val > 0.9` -> a nested-ladder defect corrector will win big and
most of the win is a linear filter; check `skill_LSI` before attributing anything
to an architecture. `rho_fit` high with `rho_val` <= 0 -> the coarse solve is NOT in
its asymptotic regime (sample-dependent phase/dispersion error); a held-out trust
switch is mandatory and the corrector will shut itself off. Low
`frac_energy_within_12_cells` -> the optimal operator is NOT local and a small
convolutional receptive field is mis-sized. Datasets whose test split ships no LF
(e.g. `ifc_poisson`) return an `error` field and are skipped.

Invoke:
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/defect_correction_learnability.py \
    --datasets sharp__phase_field_crystal_2d,ext__helmholtz_2d \
    --out /path/to/defect.json [--ridge 1e-6] [--n_train 320] [--n_test 100000]
# whole panel / guard set from project.yaml:
python tools/defect_correction_learnability.py --datasets PANEL --out d.json
python tools/defect_correction_learnability.py --datasets GUARD --out g.json
```
Pure numpy + FFT on the login node; seconds to ~2 min per dataset. Use the FULL
test split (`--n_test` large) if you want the `identity_matches_frozen_baseline`
seam to be exact — a truncated test split will not match
`eval/copylf_baselines.json`.

Provenance: `worktrees/s6_local/B1/scratchpad/reanalysis_turn_3.py`;
card `experiment_cards/s6_local/batch_1/B1.json` part 6, findings F14-F16.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


def _round_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True, cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip()) / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
import nrmse as nrmse_mod          # noqa: E402
import panel_data                  # noqa: E402

BASELINES = json.loads((ROUND / "eval" / "copylf_baselines.json").read_text())
MIN_GAIN = 1e-3                    # the s6/s4 held-out line-search ceiling


def fit_transfer(LF, R, grid, ridge=0.0):
    H, W = grid
    fl = np.fft.rfft2(LF.reshape(-1, H, W))
    fr = np.fft.rfft2(R.reshape(-1, H, W))
    num = (fr * np.conj(fl)).sum(axis=0)
    den = (np.abs(fl) ** 2).sum(axis=0)
    return num / (den + ridge * float(den.mean()))


def apply_transfer(LF, T, grid):
    H, W = grid
    fl = np.fft.rfft2(LF.reshape(-1, H, W))
    return np.fft.irfft2(fl * T[None, :, :], s=(H, W)).reshape(LF.shape[0], -1)


def rho(R, C):
    den = float((R ** 2).sum())
    return float(1.0 - ((R - C) ** 2).sum() / den) if den > 0 else float("nan")


def stencil_profile(T, grid):
    H, W = grid
    h = np.fft.fftshift(np.fft.irfft2(T, s=(H, W)))
    cy, cx = H // 2, W // 2
    yy, xx = np.mgrid[0:H, 0:W]
    rr = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
    e = h ** 2
    tot = max(e.sum(), 1e-300)
    order = np.argsort(rr.ravel())
    csum = np.cumsum(e.ravel()[order]) / tot
    rs = rr.ravel()[order]
    out = {}
    for q in (0.5, 0.9, 0.99):
        i = int(np.searchsorted(csum, q))
        out[f"radius_{int(q * 100)}pct_energy"] = float(rs[min(i, len(rs) - 1)])
    out["frac_energy_within_12_cells"] = float(e[rr <= 12].sum() / tot)
    out["frac_energy_within_3_cells"] = float(e[rr <= 3].sum() / tot)
    out["h_center_value"] = float(h[cy, cx])
    return out


def band_masks(grid, n=4):
    """Round band convention: edges = [0,.125,.25,.5,1] * k_nyquist."""
    H, W = grid
    k_nyq = (max(H, W) if min(H, W) == 1 else min(H, W)) / 2.0
    ed = [f * k_nyq for f in (0.0, 0.125, 0.25, 0.5, 1.0)]
    ky = np.fft.fftfreq(H) * H
    kx = np.fft.rfftfreq(W) * W
    kk = np.sqrt(ky[:, None] ** 2 + kx[None, :] ** 2)
    masks = [(kk >= ed[i]) & (kk < ed[i + 1]) for i in range(n)]
    masks[-1] = masks[-1] | (kk >= ed[-1])
    return masks, ed


def one(ds, ridge, n_train, n_test, holdout_frac=0.2, seed=0):
    t0 = time.time()
    train = panel_data.load_split(ds, "train")
    test = panel_data.load_split(ds, "test")
    if not train["lf_fids"] or not test["lf_fids"]:
        return {"dataset": ds, "error": "no LF fidelity in one of the splits"}
    hf = train["hf_fid"]
    LF_tr = panel_data.copylf_prediction(train)
    LF_te = panel_data.copylf_prediction(test)
    Y_tr = np.asarray(train["field_by_fid"][hf], dtype=np.float64)[:LF_tr.shape[0]]
    Y_te = np.asarray(test["field_by_fid"][hf], dtype=np.float64)
    hf_grid = test["grid_shape_by_fid"].get(hf)
    lf_grid = test["grid_shape_by_fid"].get(max(test["lf_fids"]))
    grid = (1, LF_te.shape[1]) if hf_grid is None else (int(hf_grid[0]), int(hf_grid[1]))
    R_tr = Y_tr - LF_tr
    Ntr = LF_tr.shape[0]
    perm = np.random.default_rng(seed).permutation(Ntr)
    n_val = max(1, int(round(holdout_frac * Ntr)))
    val, fit = perm[:n_val], perm[n_val:][:n_train]
    T = fit_transfer(LF_tr[fit], R_tr[fit], grid, ridge=ridge)
    C_fit, C_val = apply_transfer(LF_tr[fit], T, grid), apply_transfer(LF_tr[val], T, grid)
    n_te = min(n_test, Y_te.shape[0])
    C_te = apply_transfer(LF_te[:n_te], T, grid)
    nr = nrmse_mod.nrmse
    id_nr = nr(LF_te[:n_te], Y_te[:n_te])
    lsi_nr = nr(LF_te[:n_te] + C_te, Y_te[:n_te])
    base_v = nr(LF_tr[val], Y_tr[val])
    best_a, best_r = 0.0, base_v
    for c in (0.25, 0.5, 0.75, 1.0):
        rr = nr(LF_tr[val] + c * C_val, Y_tr[val])
        if rr < min(best_r, base_v * (1 - MIN_GAIN)):
            best_a, best_r = c, rr
    masks, ed = band_masks(grid)
    ref = BASELINES.get(ds, {})
    is_copylf_ref = ref.get("reference_type") == "copylf" and ref.get("test_nrmse")
    out = {
        "dataset": ds, "grid": list(grid),
        "lf_native_grid": (list(lf_grid) if lf_grid is not None else None),
        "refinement_ratio": (float(hf_grid[0]) / float(lf_grid[0])
                             if (hf_grid and lf_grid) else None),
        "n_fit": int(len(fit)), "n_val": int(len(val)), "n_test": int(n_te),
        "ridge": ridge, "seed": seed,
        "nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
        "nrmse_identity_copylf": id_nr,
        "frozen_copylf_baseline": ref.get("test_nrmse"),
        "identity_matches_frozen_baseline": bool(
            is_copylf_ref and abs(id_nr - ref["test_nrmse"]) < 1e-9),
        "nrmse_LSI_defect_correction": lsi_nr,
        "skill_LSI": (lsi_nr / ref["test_nrmse"]) if is_copylf_ref else (lsi_nr / id_nr),
        "frac_of_copylf_error_removed": 1.0 - lsi_nr / id_nr,
        "rho_fit_in_sample": rho(R_tr[fit], C_fit),
        "rho_val_heldout": rho(R_tr[val], C_val),
        "generalization_gap_rho": rho(R_tr[fit], C_fit) - rho(R_tr[val], C_val),
        "heldout_trust_switch_alpha": best_a,
        "band_mean_abs_T": [float(np.abs(T)[m].mean()) for m in masks],
        "band_edges_wavenumber": ed,
        "stencil": stencil_profile(T, grid),
        "wall_seconds": time.time() - t0,
    }
    g = out["rho_val_heldout"]
    out["predicted_verdict"] = (
        "STRONG defect-correction headroom" if g > 0.9 else
        "MODERATE headroom" if g > 0.5 else
        "WEAK headroom" if g > 0.1 else
        "NO headroom (a held-out trust switch should shut the corrector off)")
    return out


def resolve(spec):
    cfg = panel_data.load_config()
    if spec.strip().upper() == "PANEL":
        return list(cfg["panel"])
    if spec.strip().upper() == "GUARD":
        return list(cfg["guard_set"])
    return [s.strip() for s in spec.split(",") if s.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", required=True, help="comma list, or PANEL / GUARD")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ridge", type=float, default=1e-6)
    ap.add_argument("--n_train", type=int, default=320)
    ap.add_argument("--n_test", type=int, default=100000)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    res = []
    for ds in resolve(a.datasets):
        try:
            r = one(ds, a.ridge, a.n_train, a.n_test, seed=a.seed)
        except Exception as e:                                     # noqa: BLE001
            r = {"dataset": ds, "error": f"{type(e).__name__}: {e}"}
        print(json.dumps(r, indent=1), flush=True)
        res.append(r)
    Path(a.out).write_text(json.dumps(
        {"nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH, "results": res}, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
