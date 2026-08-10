#!/usr/bin/env python
"""coverage_knee_surrogate.py — predict a condition-coverage ladder's KNEE without training.

WHAT IT MEASURES
    Given a dataset and a ladder of condition-budget caps, this builds a TRAINING-FREE
    surrogate recovery curve R_surr(c) and reports its knee, so you can price a
    coverage sweep (or a whole batch) before committing GPU time.

    R_surr(c) is the exact structural analogue of the round's measured recovery
    fraction R = (nRMSE(A0) - nRMSE(arm)) / (nRMSE(A0) - nRMSE(A1)):
      * the arm at cap c   = RBF kernel ridge fit on (kept standardised conditions ->
                             that row's LF field lifted to the HF grid by the FROZEN
                             round2/eval/panel_data.py::copylf_prediction convention),
                             scored against the HF test split with round2/eval/nrmse.py;
      * the A0 analogue    = the same regressor fit on n_hf HF train rows only;
      * the A1 analogue    = the same regressor fit on the FULL LF condition pool.
    Nothing here trains a network, touches a GPU, or reads a model checkpoint.

    Also reports the two structural nulls this instrument was written to kill, so a
    user can see WHY the knee is where it is rather than only that it is there:
      * design_rank   numerical rank of [Z_kept, 1] (the "we ran out of condition-space
                      directions" story). On ch it saturates 7.2x below the knee.
      * nnc           nearest-kept-condition FIELD oracle: predict each test field by
                      the nearest kept condition's field (the "coverage radius" story).
                      On ch it never beats predicting zero, at any cap.

PROVENANCE
    r3s3_lf_value-B2 mechanism turn 1. On that card it reproduced the trained
    200-epoch FNO ladder at Pearson 0.9842 (sharp__cahn_hilliard, 63 cells,
    mean |dev| 0.0386 R = 1.57 tau_rel) and 0.9774 (ifc_heat, 21 cells), put its
    step-max knee on the SAME cap as the trained ladder on both datasets
    (80 and 5), and matched the ch deciding step 40->80 to 0.0005 R
    (0.1986 vs 0.1991) = 2.0 % of one tau_rel.

CAVEATS (measured, not hypothetical)
    * It predicts the SHAPE and the KNEE, not the LEVEL: on ch its full-pool nRMSE
      0.5753 is 11 % worse than the trained arm's 0.5178. Never quote it as a baseline.
    * The reproduction needs the NONLINEAR kernel. `--kernel linear` on ch gives
      Pearson 0.622 and excursions to -2.5 R. Report `--kernel both` when in doubt.
    * Corroborated on two cells. Treat a knee prediction on a new cell as a
      pre-registered prediction to be checked, not as a measurement.
    * Cells whose condition->field map is not a function of the recorded condition on
      part of the test split (see r3s3-B2 turn 3) will have a knee for the BULK only;
      pass --strat-mask to see the stratified ladder.

INVOCATION
    python tools/coverage_knee_surrogate.py --dataset sharp__cahn_hilliard \
        --caps 5,10,20,40,80,160,395 --n-hf 5 --draws 0,1,2
    python tools/coverage_knee_surrogate.py --dataset ifc_heat \
        --caps 1,2,5,10,15,45,95 --n-hf 5 --draws native
    # replay the EXACT kept sets a shipped card used, instead of redrawing them:
    python tools/coverage_knee_surrogate.py --dataset sharp__cahn_hilliard \
        --kept-from-training-root <outputs>/r3s3_lf_value/B2/training \
        --kept-arm A3c_lf_uncov_cap
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np


def _panel_dir():
    here = Path(__file__).resolve()
    for p in here.parents:
        cand = p / "mffp_autoresearch" / "round2" / "eval"
        if cand.is_dir():
            return cand
    raise SystemExit("could not locate mffp_autoresearch/round2/eval from this file")


sys.path.insert(0, str(_panel_dir()))
import panel_data  # noqa: E402
from nrmse import nrmse  # noqa: E402

KEY_ROUND = 12


def lift_rung(data, fid, ds):
    """Lift rung `fid` to the HF grid with the frozen copy-LF convention."""
    hf_fid = data["hf_fid"]
    lf = np.asarray(data["field_by_fid"][fid], dtype=np.float64)
    n_cells_hf = int(np.prod(data["grid_shape_by_fid"][hf_fid]))
    sub = {"hf_fid": hf_fid, "lf_fids": [fid],
           "field_by_fid": {fid: lf, hf_fid: np.zeros((lf.shape[0], n_cells_hf))},
           "grid_shape_by_fid": data["grid_shape_by_fid"]}
    return np.asarray(panel_data.copylf_prediction(sub, ds), dtype=np.float64)


def fit_predict(Ztr, Ytr, Zte, lam, kernel):
    n = len(Ztr)
    if kernel == "linear":
        A = np.concatenate([Ztr, np.ones((n, 1))], 1)
        B = np.concatenate([Zte, np.ones((len(Zte), 1))], 1)
        G, K = A @ A.T, B @ A.T
    else:
        d2 = ((Ztr[:, None, :] - Ztr[None, :, :]) ** 2).sum(-1)
        med = np.median(d2[np.triu_indices(n, 1)]) if n > 1 else 1.0
        med = med if med > 0 else 1.0
        G = np.exp(-d2 / med)
        K = np.exp(-(((Zte[:, None, :] - Ztr[None, :, :]) ** 2).sum(-1)) / med)
    return K @ np.linalg.solve(G + lam * n * np.eye(n), Ytr)


def kept_from_legs(root, arm, ds, seed):
    """Read the exact kept LF row indices per (cap, draw) out of shipped leg JSONs."""
    out = {}
    for legdir in sorted(Path(root).iterdir()):
        if not legdir.is_dir() or ds not in legdir.name or arm not in legdir.name:
            continue
        js = sorted(legdir.glob("*/*_e*_s*.json"))
        if not js:
            continue
        d = json.load(open(js[0])).get("row_efficiency")
        if d is None or (seed is not None and int(d["seed"]) != seed):
            continue
        key = (int(d["arm_spec"]["cap_this_leg"]), str(d["split"]["split_seed"]))
        out[key] = {int(p["fid"]): [int(i) for i in p["selected_row_indices"]]
                    for p in d["lf_pool"]}
    return out


def draw_kept(cond_by_rung, hf_rows, cap, draw):
    """The round's own per-rung cap draw: sort(default_rng([split_seed, fid])
    .permutation(n_uncovered)[:cap]) over the rows NOT covered by the HF train rows."""
    hf_keys = {tuple(np.round(c, KEY_ROUND)) for c in hf_rows}
    kept = {}
    for fid, C in cond_by_rung.items():
        cand = [i for i, c in enumerate(C) if tuple(np.round(c, KEY_ROUND)) not in hf_keys]
        rng = np.random.default_rng([int(draw), int(fid)])
        sel = np.sort(rng.permutation(len(cand))[: min(cap, len(cand))])
        kept[fid] = [cand[i] for i in sel]
    return kept


def union(kept, cond_by_rung, lift_by_rung):
    seen = {}
    for fid in sorted(kept):
        for i in kept[fid]:
            c = cond_by_rung[fid][i]
            seen[tuple(np.round(c, KEY_ROUND))] = (c, lift_by_rung[fid][i])
    return (np.array([v[0] for v in seen.values()], dtype=np.float64),
            np.array([v[1] for v in seen.values()], dtype=np.float64))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--caps", default="5,10,20,40,80,160,395",
                    help="comma-separated per-rung condition caps")
    ap.add_argument("--n-hf", type=int, default=5, help="HF rows for the A0 analogue")
    ap.add_argument("--draws", default="0,1,2",
                    help="comma-separated HF-draw seeds; 'native' = use all HF train rows")
    ap.add_argument("--kernel", default="rbf", choices=["rbf", "linear", "both"])
    ap.add_argument("--lam", type=float, default=1e-3)
    ap.add_argument("--split", default="test")
    ap.add_argument("--strat-mask", default=None,
                    help="path to a .npz plus ::key holding a boolean/0-1 test mask, "
                         "e.g. dump.npz::hard_mask_rederived_model_free")
    ap.add_argument("--kept-from-training-root", default=None,
                    help="replay the EXACT kept sets from a card's training tree")
    ap.add_argument("--kept-arm", default="A3c_lf_uncov_cap")
    ap.add_argument("--kept-seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    caps = [int(c) for c in a.caps.split(",")]
    tr = panel_data.load_split(a.dataset, "train")
    te = panel_data.load_split(a.dataset, a.split)
    hf = tr["hf_fid"]
    cond_hf_tr = np.asarray(tr["cond_by_fid"][hf], dtype=np.float64)
    fld_hf_tr = np.asarray(tr["field_by_fid"][hf], dtype=np.float64)
    cond_te = np.asarray(te["cond_by_fid"][hf], dtype=np.float64)
    y = np.asarray(te["field_by_fid"][hf], dtype=np.float64)
    rungs = sorted(tr["lf_fids"])
    cond_by_rung = {f: np.asarray(tr["cond_by_fid"][f], dtype=np.float64) for f in rungs}
    lift_by_rung = {f: lift_rung(tr, f, a.dataset) for f in rungs}

    base = cond_by_rung[rungs[0]]
    Zmu, Zsd = base.mean(0), base.std(0)
    Zsd[Zsd == 0] = 1.0
    Zte = (cond_te - Zmu) / Zsd
    kerns = ["rbf", "linear"] if a.kernel == "both" else [a.kernel]

    mask = None
    if a.strat_mask:
        p, k = a.strat_mask.split("::")
        mask = np.asarray(np.load(p)[k], dtype=bool)

    replay = (kept_from_legs(a.kept_from_training_root, a.kept_arm, a.dataset, a.kept_seed)
              if a.kept_from_training_root else None)
    draws = ([None] if a.draws == "native"
             else [int(d) for d in a.draws.split(",")]) if not replay else \
            sorted({d for (_, d) in replay})

    # full-pool A1 analogue
    Cf, Ff = union({f: list(range(len(cond_by_rung[f]))) for f in rungs},
                   cond_by_rung, lift_by_rung)
    Zf = (Cf - Zmu) / Zsd
    e1 = {k: nrmse(fit_predict(Zf, Ff, Zte, a.lam, k), y) for k in kerns}

    # per-draw A0 analogue
    hf_rows_by_draw, e0 = {}, {}
    for d in draws:
        if d is None or a.draws == "native":
            rows = list(range(len(cond_hf_tr)))
        else:
            rng = np.random.default_rng(int(d))
            rows = sorted(rng.permutation(len(cond_hf_tr))[: a.n_hf].tolist())
        hf_rows_by_draw[str(d)] = rows
        Zh = (cond_hf_tr[rows] - Zmu) / Zsd
        e0[str(d)] = {k: nrmse(fit_predict(Zh, fld_hf_tr[rows], Zte, a.lam, k), y)
                      for k in kerns}

    print(f"dataset {a.dataset}  rungs {rungs}  cond_dim {cond_te.shape[1]}  "
          f"n_test {len(y)}  lam {a.lam}")
    print("  A1 analogue (full LF pool): " + " ".join(f"{k}={v:.4f}" for k, v in e1.items()))
    for d, v in e0.items():
        print(f"  A0 analogue (draw {d}, {len(hf_rows_by_draw[d])} HF rows): "
              + " ".join(f"{k}={x:.4f}" for k, x in v.items()))

    rows_out = []
    for c in caps:
        for d in draws:
            ds_ = str(d)
            if replay:
                kept = replay.get((c, ds_))
                if kept is None:
                    continue
            else:
                kept = draw_kept(cond_by_rung, cond_hf_tr[hf_rows_by_draw[ds_]], c, d or 0)
            C, F = union(kept, cond_by_rung, lift_by_rung)
            Zk = (C - Zmu) / Zsd
            A = np.concatenate([Zk, np.ones((len(Zk), 1))], 1)
            sv = np.linalg.svd(A, compute_uv=False)
            d2 = ((Zte[:, None, :] - Zk[None, :, :]) ** 2).sum(-1)
            j = d2.argmin(1)
            rec = dict(cap=c, draw=ds_, n_distinct=int(len(C)),
                       design_rank=int((sv > sv[0] * 1e-10).sum()),
                       d_med=float(np.median(np.sqrt(d2.min(1)))),
                       nnc=nrmse(F[j], y))
            for k in kerns:
                p = fit_predict(Zk, F, Zte, a.lam, k)
                rec[f"nrmse_{k}"] = nrmse(p, y)
                rec[f"R_{k}"] = (e0[ds_][k] - rec[f"nrmse_{k}"]) / (e0[ds_][k] - e1[k])
                if mask is not None:
                    rl = np.linalg.norm(p - y, axis=1) / np.linalg.norm(y, axis=1)
                    rec[f"rel_hard_{k}"] = float(rl[mask].mean())
                    rec[f"rel_bulk_{k}"] = float(rl[~mask].mean())
            rows_out.append(rec)

    print(f"\n  {'cap':>6}{'n_dist':>8}{'rank':>6}{'d_med':>8}{'nnc':>8}"
          + "".join(f"{'R_'+k:>10}" for k in kerns)
          + ("".join(f"{'hard_'+k:>10}{'bulk_'+k:>10}" for k in kerns) if mask is not None else ""))
    per_cap = {}
    for c in caps:
        sub = [r for r in rows_out if r["cap"] == c]
        if not sub:
            continue
        m = lambda k: float(np.mean([r[k] for r in sub]))
        per_cap[c] = {k: m(k) for k in sub[0] if k != "draw"}
        line = (f"  {c:>6}{m('n_distinct'):>8.1f}{m('design_rank'):>6.1f}"
                f"{m('d_med'):>8.4f}{m('nnc'):>8.4f}"
                + "".join(f"{m('R_'+k):>10.4f}" for k in kerns))
        if mask is not None:
            line += "".join(f"{m('rel_hard_'+k):>10.4f}{m('rel_bulk_'+k):>10.4f}" for k in kerns)
        print(line)

    verdict = {}
    ks = sorted(per_cap)
    for k in kerns:
        steps = [per_cap[ks[i + 1]][f"R_{k}"] - per_cap[ks[i]][f"R_{k}"]
                 for i in range(len(ks) - 1)]
        knee = ks[int(np.argmax(steps))+1]
        verdict[k] = dict(knee_by_stepmax=knee, steps=steps,
                          R_at_knee=per_cap[knee][f"R_{k}"],
                          step_into_knee=float(max(steps)))
        print(f"\n  [{k}] PREDICTED KNEE (step-max) = cap {knee}  "
              f"n_distinct {per_cap[knee]['n_distinct']:.1f}  "
              f"R_surr {per_cap[knee][f'R_{k}']:.4f}  step into it {max(steps):+.4f}")
    rk = [per_cap[c]["design_rank"] for c in ks]
    sat = next((c for c, r in zip(ks, rk) if r >= max(rk)), None)
    print(f"  NULL 1 design rank saturates at cap {sat} (rank {max(rk)}) -- if this is far "
          f"below the knee, the knee is NOT a condition-space-rank story")
    print(f"  NULL 2 nearest-kept-condition field oracle over the ladder: "
          f"{min(per_cap[c]['nnc'] for c in ks):.4f} .. {max(per_cap[c]['nnc'] for c in ks):.4f} "
          f"-- if it never goes usefully below 1.0, the knee is NOT a coverage-radius story")

    if a.out:
        json.dump(dict(dataset=a.dataset, caps=caps, per_cap=per_cap, cells=rows_out,
                       a0=e0, a1=e1, verdict=verdict,
                       rank_saturation_cap=sat, lam=a.lam, kernels=kerns),
                  open(a.out, "w"), indent=1, default=float)
        print(f"\n[saved] {a.out}")


if __name__ == "__main__":
    main()
