"""Fast architecture check for the three FNO families across grid geometries.

No dataset loading, no training loop — just builds each model and runs a
forward + backward on synthetic batches for: a square ladder, a 1-D (height-1)
ladder, and a rectangular ladder (era5-like). Confirms the scalar->grid
generalisation produces finite gradients on every geometry.

Run:  .venv/bin/python models/_grid_smoketest.py
"""
import importlib.util
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent


def _load(family, symbol):
    spec = importlib.util.spec_from_file_location(f"{family}_model", HERE / family / "model.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, symbol)


LADDERS = {
    "square":      [(8, 8), (16, 16), (32, 32)],
    "1d":          [(1, 64), (1, 128), (1, 256)],
    "rectangular": [(40, 72), (80, 144), (128, 256)],
}
COND_DIM = 4
B = 3


def modes(grid, cap=12):
    H, W = grid
    return (min(cap, max(H // 2, 1)), min(cap, W // 2 + 1))


def check_mf_stack(name, grids):
    FNOMFStack = _load("fno_mf_stack", "FNOMFStack")
    m = FNOMFStack(cond_dim=COND_DIM, native_grids=grids,
                   modes_per_level=[modes(g) for g in grids],
                   hidden=8, agg_hidden=8, n_blocks=2, hf_grid=grids[-1])
    X = torch.randn(B, COND_DIM, requires_grad=True)
    mval = torch.ones(B)
    out = m.hf_predict(X, mval)
    Hh, Wh = grids[-1]
    assert out["pred"].shape == (B, Hh, Wh), out["pred"].shape
    loss = out["pred"].pow(2).mean()
    for k in range(len(grids) - 1):
        loss = loss + m.lf_predict_native(X, k).pow(2).mean()
    loss.backward()
    return float(loss)


def check_coreg(name, grids):
    FNOCoreg = _load("fno_coregionalization", "FNOCoregionalization")
    g = grids[-1]
    mh, mw = modes(g)
    m = FNOCoreg(cond_dim=COND_DIM, hidden_channels=8, K=6, n_blocks=2,
                 modes_h=mh, modes_w=mw, grid=g)
    m.set_scalers([0.0, 0.5, 1.0], [1.0, 1.0, 1.0])
    X = torch.randn(B, COND_DIM, requires_grad=True)
    mval = torch.rand(B)
    out = m(X, mval)
    assert out.shape == (B, g[0], g[1]), out.shape
    loss = out.pow(2).mean()
    loss.backward()
    return float(loss)


def check_coreg_residual(name, grids):
    FNOCR = _load("fno_coreg_residual", "FNOCoregResidual")
    m = FNOCR(cond_dim=COND_DIM, native_grids=grids,
              modes_per_level=[modes(g) for g in grids],
              hidden=8, decoder_hidden=8, K=6, n_blocks=2, hf_grid=grids[-1])
    m.set_scaler({k: 1.0 for k in range(len(grids))})
    X = torch.randn(B, COND_DIM, requires_grad=True)
    mval = torch.ones(B)
    out = m.hf_predict(X, mval)
    Hh, Wh = grids[-1]
    assert out["pred"].shape == (B, Hh, Wh), out["pred"].shape
    loss = out["pred"].pow(2).mean()
    for k in range(len(grids) - 1):
        loss = loss + m.lf_decoded_native(X, k).pow(2).mean()
    loss.backward()
    return float(loss)


def main():
    torch.manual_seed(0)
    checks = [("fno_mf_stack", check_mf_stack),
              ("fno_coregionalization", check_coreg),
              ("fno_coreg_residual", check_coreg_residual)]
    ok = True
    for fam, fn in checks:
        for ladder_name, grids in LADDERS.items():
            try:
                loss = fn(fam, grids)
                finite = loss == loss and abs(loss) < float("inf")
                status = "OK" if finite else "NON-FINITE-LOSS"
                if not finite:
                    ok = False
                print(f"[{status:15s}] {fam:24s} {ladder_name:12s} grids={grids} loss={loss:.4e}")
            except Exception as e:
                ok = False
                import traceback
                print(f"[{'FAIL':15s}] {fam:24s} {ladder_name:12s} grids={grids}")
                traceback.print_exc()
    print("\nALL PASS" if ok else "\nFAILURES ABOVE")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
