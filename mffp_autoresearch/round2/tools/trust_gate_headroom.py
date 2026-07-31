"""How much is a trust gate worth, and at which granularity?

For any model whose prediction is (or can be written as) `base + correction` with
`base` = the round's copy-LF field, this tool measures the VALUE CEILING of a
trust gate at three granularities, so a card does not spend a batch building the
wrong one:

| key | meaning |
|---|---|
| `nrmse_pred` / `nrmse_base_copylf` | the model as shipped, and the copy-LF base |
| `nrmse_ORACLE_pixel_gate` | best possible FIELD-VALUED gate `g(x) in [0,1]`, one map shared by all samples, fitted on the TEST set itself (labelled oracle) |
| `nrmse_ORACLE_per_sample_scalar` | best possible per-sample scalar gate, fitted on the TEST set (labelled oracle) |
| `nrmse_ACHIEVABLE_pixel_gate` | the same pixel map fitted on a held-out slice supplied via `--val_pred` (a real, leak-free estimate) |
| `pixel_gate_ceiling_frac`, `per_sample_gate_ceiling_frac` | fractional nRMSE reduction each ceiling offers over `g == 1` |
| `granularity_verdict` | which axis (if any) is worth building |
| `corr_absC_gradbase` | is the correction concentrated where the base field has structure (interfaces)? |

**Read it as.** Both ceilings < ~5 % -> a trust gate cannot pay for itself; the
model's own correction is already as good as any reweighting of it (s6_local-B1:
oracle pixel ceiling 0.6-4.1 %, and NEGATIVE on `sharp__cahn_hilliard`). Per-sample
ceiling >> pixel ceiling -> build a per-SAMPLE trust head, not a field-valued gate
(s6_local-B1: helmholtz 50.7 % per-sample vs 0 % per-pixel). An oracle ceiling that
is *negative* means a single shared pixel map cannot describe the dataset's
sample-to-sample spread at all.

Inputs are npz files holding a 2-D `(N, n_cells)` prediction array on the dataset's
TEST split (key `pred` by default), paired with the dataset name so the base and
target come from `round1/eval/panel_data.py`. Scoring is `round1/eval/nrmse.py`
only. `--corr_key` lets you pass the correction directly instead of a prediction
(then `pred = copylf + corr`).

Invoke:
```bash
source "$PROJECT_ROOT/.venv/bin/activate"
python tools/trust_gate_headroom.py \
    --dataset sharp__phase_field_crystal_2d \
    --pred_npz <run>/preds_test.npz [--pred_key pred | --corr_key corr] \
    [--val_pred <run>/preds_val.npz --val_idx_npz <run>/val_idx.npz] \
    [--n_samples 100] --out /path/to/gate_headroom.json
```
Seconds; pure numpy. The `--val_pred` arm needs the model's corrections on
TRAIN-split samples it did not fit (indices in `--val_idx_npz`, key `val_idx`);
without it only the oracle ceilings are reported, which is usually enough to kill
or license a gate design.

Provenance: `worktrees/s6_local/B1/scratchpad/reanalysis_turn_1.py`;
card `experiment_cards/s6_local/batch_1/B1.json` part 6, findings F1-F3.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
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


def pixel_gate(Rs, Cs, hi=1.0):
    num = (Rs * Cs).sum(axis=0)
    den = (Cs * Cs).sum(axis=0)
    return np.clip(np.where(den > 1e-30, num / np.maximum(den, 1e-30), 0.0), 0.0, hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--pred_npz", required=True)
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--corr_key", default=None,
                    help="if set, the npz holds the CORRECTION, not the prediction")
    ap.add_argument("--val_pred", default=None)
    ap.add_argument("--val_idx_npz", default=None)
    ap.add_argument("--val_key", default="corr")
    ap.add_argument("--n_samples", type=int, default=100000)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    test = panel_data.load_split(a.dataset, "test")
    base = panel_data.copylf_prediction(test)
    Y = np.asarray(test["field_by_fid"][test["hf_fid"]], dtype=np.float64)
    z = np.load(a.pred_npz)
    if a.corr_key:
        C = np.asarray(z[a.corr_key], dtype=np.float64)
        C = C.reshape(C.shape[0], -1)
        pred = base[:C.shape[0]] + C
    else:
        pred = np.asarray(z[a.pred_key], dtype=np.float64)
        pred = pred.reshape(pred.shape[0], -1)
        C = pred - base[:pred.shape[0]]
    n = min(a.n_samples, pred.shape[0], Y.shape[0])
    base, Y, pred, C = base[:n], Y[:n], pred[:n], C[:n]
    R = Y - base
    nr = nrmse_mod.nrmse

    g_pix = pixel_gate(R, C)
    num = (R * C).sum(axis=1)
    den = (C * C).sum(axis=1)
    a_s = np.clip(np.where(den > 1e-30, num / np.maximum(den, 1e-30), 0.0), 0.0, 1.5)
    n_g1 = nr(base + C, Y)
    n_pix = nr(base + g_pix[None, :] * C, Y)
    n_smp = nr(base + a_s[:, None] * C, Y)

    ref = BASELINES.get(a.dataset, {})
    out = {
        "dataset": a.dataset, "n_samples": int(n),
        "nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
        "pred_npz": a.pred_npz,
        "nrmse_base_copylf": nr(base, Y),
        "frozen_copylf_baseline": ref.get("test_nrmse"),
        "base_matches_frozen_baseline": bool(
            ref.get("reference_type") == "copylf" and ref.get("test_nrmse")
            and abs(nr(base, Y) - ref["test_nrmse"]) < 1e-9),
        "nrmse_pred": nr(pred, Y),
        "nrmse_correction_ungated_g_eq_1": n_g1,
        "nrmse_ORACLE_pixel_gate": n_pix,
        "nrmse_ORACLE_per_sample_scalar": n_smp,
        "pixel_gate_ceiling_frac": (n_g1 - n_pix) / max(n_g1, 1e-30),
        "per_sample_gate_ceiling_frac": (n_g1 - n_smp) / max(n_g1, 1e-30),
        "oracle_pixel_gate_stats": {
            "mean": float(g_pix.mean()), "std": float(g_pix.std()),
            "p05": float(np.percentile(g_pix, 5)),
            "frac_lt_0.9": float((g_pix < 0.9).mean())},
        "oracle_per_sample_alpha_stats": {
            "mean": float(a_s.mean()), "std": float(a_s.std()),
            "min": float(a_s.min()), "max": float(a_s.max()),
            "frac_lt_0.5": float((a_s < 0.5).mean())},
        "correction_norm_over_residual_norm": float(
            np.linalg.norm(C) / max(np.linalg.norm(R), 1e-30)),
    }
    # is the correction interface-concentrated?
    grid = test["grid_shape_by_fid"].get(test["hf_fid"])
    if grid is not None:
        H, W = int(grid[0]), int(grid[1])
        b2 = base.reshape(-1, H, W)
        gmag = np.sqrt(np.gradient(b2, axis=1) ** 2 +
                       np.gradient(b2, axis=2) ** 2).reshape(base.shape)
        out["corr_absC_gradbase"] = float(np.corrcoef(np.abs(C).ravel(), gmag.ravel())[0, 1])
        out["corr_absR_gradbase"] = float(np.corrcoef(np.abs(R).ravel(), gmag.ravel())[0, 1])

    if a.val_pred and a.val_idx_npz:
        zv = np.load(a.val_pred)
        Cv = np.asarray(zv[a.val_key], dtype=np.float64)
        Cv = Cv.reshape(Cv.shape[0], -1)
        vi = np.load(a.val_idx_npz)["val_idx"]
        tr = panel_data.load_split(a.dataset, "train")
        base_tr = panel_data.copylf_prediction(tr)
        Y_tr = np.asarray(tr["field_by_fid"][tr["hf_fid"]],
                          dtype=np.float64)[:base_tr.shape[0]]
        m = min(len(vi), Cv.shape[0])
        Rv = (Y_tr - base_tr)[vi[:m]]
        g_ach = pixel_gate(Rv, Cv[:m])
        out["nrmse_ACHIEVABLE_pixel_gate"] = nr(base + g_ach[None, :] * C, Y)
        out["achievable_pixel_gate_worse_than_ungated"] = bool(
            out["nrmse_ACHIEVABLE_pixel_gate"] > n_g1)
        out["corr_achievable_vs_oracle_pixel_map"] = float(
            np.corrcoef(g_ach, g_pix)[0, 1])

    pc, sc = out["pixel_gate_ceiling_frac"], out["per_sample_gate_ceiling_frac"]
    out["granularity_verdict"] = (
        "NO trust gate is worth building (both ceilings < 5 %)"
        if max(pc, sc) < 0.05 else
        "PER-SAMPLE trust only (pixel ceiling < 1/3 of the per-sample ceiling)"
        if sc > 3 * max(pc, 1e-9) else
        "PER-PIXEL trust has real headroom" if pc >= 0.05 else
        "both axes marginal")
    Path(a.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
