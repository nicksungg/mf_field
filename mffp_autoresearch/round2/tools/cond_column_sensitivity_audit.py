#!/usr/bin/env python
"""Which columns of the condition vector does a trained model actually USE?

Provenance: promoted from `s1_poisson-B4` mechanism turn 3
(`worktrees/s1_poisson/B4/scratchpad/reanalysis_turn_3.py`). There it refuted the card's
pre-registered `f_src`-exposure mechanism: the arms that cratered turned out to be the
ones that had learned to IGNORE the fidelity-source tag (0.5-0.8 % of their conditioning
sensitivity, score varying 1.09-1.13x over the whole tag range), while the winning arms
carried 5.2-5.5 % there and were 4.9-5.4x worse if queried at a different tag value --
a fragility nothing in the round had tested.

WHAT IT MEASURES, for each checkpoint
  R1  column sensitivity: normalised central finite difference
      ||d output / d cond_j|| / ||output||, for every condition column, plus each
      column's share of the total. Answers "where did the conditioning capacity go?"
  R2  tag sweep: re-score the model with ONE column swept over a list of values,
      everything else at the eval query. Answers "is the score robust to this column,
      or does it sit on one untested value?"
  R3  (optional, auto-skipped if absent) FiLM probe: for every submodule whose name
      ends in `film`, the across-condition std of its output and its own per-column
      finite-difference sensitivity. Localises R1 in the conditioner rather than the
      backbone. Works for any family built on the round's shared FiLM-FNO backbone.

INFERENCE ONLY -- never trains, never writes to the outputs tree, and any nRMSE it
prints goes through `${ROUND_ROOT}/eval/nrmse.py`. CPU by default.

USAGE (all paths absolute; nothing about a stream or batch is hardcoded)
  python tools/cond_column_sensitivity_audit.py \
      --family_dir  <worktree>/models_r1/<family> \
      --model_class LadderFNO2d \
      --model_kwargs '{"hidden_channels":64,"n_blocks":4,"modes_h":12,"modes_w":12,
                       "grid":[64,64],"cond_feat_dim":64}' \
      --ckpt <A>/last.pt <B>/last.pt --labels A B \
      --dataset_dir "$FACTORY_ROOT/data/ifc_poisson" --split test \
      --tags 0.0 1.0 --col_names X1 X2 X3 X4 X5 f_src f_tgt \
      --output_scaler 1.8356895307e-03 \
      --sweep_col f_src --sweep_values 0 0.3333 0.6667 1 \
      [--n_samples 32] [--eps 0.01] [--device cpu] [--out audit.json]

`--model_kwargs` is passed to `--model_class` verbatim, with `cond_dim` inserted
automatically (it is determined by the data + `--tags`). `--tags` are the constant
trailing columns of the eval query (pass none if the family conditions on X alone).
`--output_scaler` is whatever constant the family multiplies its raw output by at eval
(read it off the family result JSON); it cancels out of the R1 shares but is needed for
the R2 nRMSE column.

COST NOTE. R1 costs 2 x n_columns forward passes per checkpoint and R2 costs
n_sweep_values; on a 1-core login node a 128-sample 64^2 FNO audit of six checkpoints
took ~19 min. Use `--n_samples 32` when the node is contended.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
import torch

ROUND_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROUND_ROOT / "eval"))
import nrmse as NR  # noqa: E402


def build_cond(dataset_dir, split, fidelity, tags, n_samples):
    """Rebuild the family's eval-query condition matrix from the dataset itself."""
    import importlib
    # `data/<ds>` is usually a SYMLINK into a sibling tree, so search the
    # un-resolved parents first (that is where `data_adapters/` lives).
    raw = pathlib.Path(dataset_dir)
    for cand in list(raw.absolute().parents) + list(raw.resolve().parents):
        if (cand / "data_adapters").is_dir():
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
            break
    loaders = importlib.import_module("data_adapters")
    d = loaders.load_mf_dataset(str(dataset_dir), split)
    fids = list(d["fids"])
    f = int(fidelity) if fidelity is not None else max(fids)
    X = np.asarray(d["cond_by_fid"][f], dtype=np.float32)
    Y = np.asarray(d["field_by_fid"][f], dtype=np.float64)
    Y = Y.reshape(Y.shape[0], -1)
    n = X.shape[0] if not n_samples else min(n_samples, X.shape[0])
    X, Y = X[:n], Y[:n]
    if tags:
        X = np.concatenate(
            [X] + [np.full((n, 1), float(t), np.float32) for t in tags], axis=1
        ).astype(np.float32)
    return X, Y, fids, f


def load_model(family_dir, model_class, model_kwargs, cond_dim, ckpt, state_key, device):
    if str(family_dir) not in sys.path:
        sys.path.insert(0, str(family_dir))
    import importlib
    mod = importlib.import_module("model")
    cls = getattr(mod, model_class)
    kw = dict(model_kwargs)
    kw.setdefault("cond_dim", int(cond_dim))
    if "grid" in kw:
        kw["grid"] = tuple(int(g) for g in kw["grid"])
    m = cls(**kw)
    sd = torch.load(ckpt, map_location="cpu", weights_only=False)
    m.load_state_dict(sd[state_key] if state_key in sd else sd)
    return m.to(device).eval()


@torch.no_grad()
def forward(m, X, scaler, bs, device):
    o = []
    for i in range(0, X.shape[0], bs):
        xb = torch.from_numpy(X[i:i + bs]).float().to(device)
        out = m(xb)
        o.append(out.reshape(out.shape[0], -1).cpu().numpy())
    return np.concatenate(o, 0).astype(np.float64) * float(scaler)


def film_modules(m):
    return [(n, mod) for n, mod in m.named_modules() if n.split(".")[-1] == "film"]


@torch.no_grad()
def film_probe(m, X, eps, device):
    mods = film_modules(m)
    if not mods:
        return None
    xt = torch.from_numpy(X).float().to(device)
    disp = [float(mod(xt).cpu().numpy().std(axis=0).mean()) for _, mod in mods]
    sens = []
    for j in range(X.shape[1]):
        Xp, Xm = X.copy(), X.copy()
        Xp[:, j] += eps
        Xm[:, j] -= eps
        tp = torch.from_numpy(Xp).float().to(device)
        tm = torch.from_numpy(Xm).float().to(device)
        v = [float(np.linalg.norm((mod(tp) - mod(tm)).cpu().numpy(), axis=1).mean()
                   / (2 * eps)) for _, mod in mods]
        sens.append(float(np.mean(v)))
    return {"module_names": [n for n, _ in mods],
            "across_cond_std_per_module": disp,
            "per_column_sensitivity": sens}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family_dir", required=True)
    ap.add_argument("--model_class", required=True)
    ap.add_argument("--model_kwargs", default="{}")
    ap.add_argument("--state_key", default="model")
    ap.add_argument("--ckpt", nargs="+", required=True)
    ap.add_argument("--labels", nargs="*", default=None)
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", default=None, help="informational only")
    ap.add_argument("--split", default="test")
    ap.add_argument("--fidelity", type=int, default=None, help="default: the HF level")
    ap.add_argument("--tags", nargs="*", type=float, default=[],
                    help="constant trailing condition columns of the eval query")
    ap.add_argument("--col_names", nargs="*", default=None)
    ap.add_argument("--output_scaler", type=float, default=1.0)
    ap.add_argument("--sweep_col", default=None, help="column NAME or 0-based index")
    ap.add_argument("--sweep_values", nargs="*", type=float, default=[])
    ap.add_argument("--n_samples", type=int, default=0, help="0 = all")
    ap.add_argument("--eps", type=float, default=0.01)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--skip_film", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    torch.manual_seed(0)
    dev = torch.device(a.device)
    kwargs = json.loads(a.model_kwargs)
    X, Y, fids, fid = build_cond(a.dataset_dir, a.split, a.fidelity, a.tags, a.n_samples)
    cond_dim = X.shape[1]
    names = a.col_names or ([f"X{j+1}" for j in range(cond_dim - len(a.tags))]
                            + [f"tag{k+1}" for k in range(len(a.tags))])
    if len(names) != cond_dim:
        raise SystemExit(f"--col_names has {len(names)} entries, cond_dim is {cond_dim}")
    labels = a.labels or [pathlib.Path(c).parent.name for c in a.ckpt]
    if len(labels) != len(a.ckpt):
        raise SystemExit("--labels must match --ckpt in length")
    print(f"dataset {a.dataset_dir} split={a.split} fids={fids} fidelity={fid}; "
          f"n={X.shape[0]} cond_dim={cond_dim} tags={a.tags}")
    print(f"nrmse_def_hash {NR.NRMSE_DEF_HASH}\n")

    sweep_j = None
    if a.sweep_col is not None:
        sweep_j = (names.index(a.sweep_col) if a.sweep_col in names else int(a.sweep_col))

    res = {}
    w = max(len(l) for l in labels) + 1
    print("R1  normalised column sensitivity  ||d out / d cond_j|| / ||out||")
    print(f"{'arm':<{w}}" + "".join(f"{n:>10s}" for n in names) + f"{'  (shares)':>12s}")
    for lab, ck in zip(labels, a.ckpt):
        m = load_model(a.family_dir, a.model_class, kwargs, cond_dim, ck,
                       a.state_key, dev)
        base = forward(m, X, a.output_scaler, a.bs, dev)
        brms = float(np.sqrt((base ** 2).mean()))
        sens = []
        for j in range(cond_dim):
            Xp, Xm = X.copy(), X.copy()
            Xp[:, j] += a.eps
            Xm[:, j] -= a.eps
            dp = (forward(m, Xp, a.output_scaler, a.bs, dev)
                  - forward(m, Xm, a.output_scaler, a.bs, dev)) / (2 * a.eps)
            sens.append(float(np.sqrt((dp ** 2).mean()) / brms))
        tot = float(sum(sens))
        r = {"ckpt": str(ck), "column_sensitivity": sens,
             "column_share": [s / tot for s in sens],
             "nRMSE_at_eval_query": (NR.nrmse(base, Y) if base.shape == Y.shape else None)}
        print(f"{lab:<{w}}" + "".join(f"{s:10.4f}" for s in sens)
              + "   " + " ".join(f"{n}={s/tot:.3f}" for n, s in zip(names, sens)))
        if sweep_j is not None and a.sweep_values:
            row_n, row_r = [], []
            for v in a.sweep_values:
                Xv = X.copy()
                Xv[:, sweep_j] = v
                pv = forward(m, Xv, a.output_scaler, a.bs, dev)
                row_n.append(NR.nrmse(pv, Y) if pv.shape == Y.shape else float("nan"))
                row_r.append(float(np.sqrt((pv ** 2).mean())))
            r["sweep"] = {"column": names[sweep_j], "values": a.sweep_values,
                          "nRMSE": row_n, "out_rms": row_r,
                          "nRMSE_range": float(max(row_n) / min(row_n)),
                          "out_rms_range": float(max(row_r) / min(row_r))}
        if not a.skip_film:
            fp = film_probe(m, X, a.eps, dev)
            if fp is not None:
                r["film"] = fp
        res[lab] = r
        del m

    if sweep_j is not None and a.sweep_values:
        print(f"\nR2  sweep of `{names[sweep_j]}` (everything else at the eval query)")
        print(f"{'arm':<{w}}" + "".join(f"{'nRMSE@%.3f' % v:>13s}" for v in a.sweep_values)
              + f"{'range':>9s}")
        for lab in labels:
            s = res[lab]["sweep"]
            print(f"{lab:<{w}}" + "".join(f"{v:13.6f}" for v in s["nRMSE"])
                  + f"{s['nRMSE_range']:9.3f}x")

    if not a.skip_film and any("film" in res[l] for l in labels):
        print("\nR3  FiLM probe (across-condition modulation std; per-column "
              "sensitivity share)")
        for lab in labels:
            f = res[lab].get("film")
            if not f:
                continue
            tot = sum(f["per_column_sensitivity"])
            print(f"  {lab:<{w}} std/module "
                  f"{' '.join('%.5f' % d for d in f['across_cond_std_per_module'])}"
                  f" | shares "
                  + " ".join(f"{n}={s/tot:.3f}"
                             for n, s in zip(names, f["per_column_sensitivity"])))

    res["_meta"] = {"nrmse_def_hash": NR.NRMSE_DEF_HASH, "col_names": names,
                    "cond_dim": cond_dim, "tags": a.tags, "eps": a.eps,
                    "n_samples": int(X.shape[0]), "fidelity": fid,
                    "family_dir": str(a.family_dir), "model_class": a.model_class}
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
        print(f"\n[wrote] {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
