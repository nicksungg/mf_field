#!/usr/bin/env python
"""Where does a trained arm's error live relative to what its HF training rows could constrain?

Provenance: promoted from `r2s3_lf_train_signal-B2` mechanism turn 3
(`worktrees/r2s3_lf_train_signal/B2/scratchpad/reanalysis_turn_3.py` — the
canonical functional-space ceilings — and `.../reanalysis_turn_3b.py` — the
random-subspace dimension control and the implicit-law null block), which is the
m-generalisation of turn 1's single-null-direction construction
(`.../reanalysis_turn_1d.py`).

WHY THIS EXISTS
---------------
With N_hf train rows and a d-dimensional condition, the augmented design
`[X_hf, 1]` (N_hf x (d+1)) has rank r and null dimension m = d + 1 - r. Every
affine functional in that null space vanishes at ALL the training conditions, so
an ORACLE may edit a prediction along it WITHOUT changing a single training-row
fit: that error is structurally unreachable from the HF rows, whatever the
architecture, the seed or the epoch count. This tool prices exactly that.

For each shipped arm (predictions only — training-free, no checkpoint surgery):

  raw skill
  - best ORACLE edit `P + (X_te,1) V Delta` over the m-dim NULL family   -> error_null_borne
  - best ORACLE edit over the complementary r-dim ROW family             -> error_row_borne
  - best ORACLE edit over the full (d+1)-dim AFFINE family               -> error_affine_borne

and, because an m-dim oracle edit is powerful BY DIMENSION ALONE, a mandatory
**random-subspace control**: the same ceiling over `--n_random` random m-dim
subspaces of the same (d+1)-dim affine family. `null_over_random ~ 1` means the
arm's error is spread isotropically over the affine functional space and the
honest statement is "LF coverage repairs the whole condition response, of which
m directions happen to be unreachable" — NOT "the defect is null-aligned".
That control is the reason this tool exists as a tool: without it, an m = 15
ceiling looks like a mechanism when it is arithmetic (r2s3-B2 turn 3 T3.5:
null_over_random 0.89-1.05 on cahn_hilliard, against a near-1.0 alignment on the
exactly affine ifc_poisson).

It also reports each arm's IMPLICIT AFFINE LAW (fitted on the arm's own test
predictions — no HF test field enters the fit) split into the same two blocks and
compared with the ORACLE (test-fitted) law: the null-block amplitude ratio and
Frobenius cosine separate "the model supplies the unseeable direction"
(cos ~ +1, ratio ~ 1) from "the model merely stops over-extrapolating there"
(ratio ~ 1 at cos ~ 0) from "confident wrong-way extrapolation" (ratio >> 1 at
cos < 0). With `--level` it adds the third channel: the arm's own mean field
swapped for a better constant (HF-train mean / lifted LF-rung means /
N_hf-row mean / ORACLE test mean), which is where the whole effect lives when
m = 0.

LEGITIMACY DISCIPLINE
---------------------
Every ceiling here is fitted on the TEST targets and is suffixed `_ORACLE`. They
are upper bounds on what an edit COULD buy, never arm scores: no quantity in this
file may be quoted as a model result. What is legitimate is the DIFFERENCE
between two arms' ceilings, read as an attribution of an already-measured gap.

USAGE
-----
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/null_family_ceiling_audit.py --dataset sharp__cahn_hilliard \
      --arm A0_nolf=<outputs>/results_ch_A0_s0/<family>/<ds>_e200_s0_preds.npz \
      --arm A2_lf_cov_null=<outputs>/results_ch_A2_s0/<family>/<ds>_e200_s0_preds.npz \
      --contrast A0_nolf:A2_lf_cov_null --level --out ceilings.json

`--arm NAME=path[:key]` (default key `pred_test`, also accepts `.npy`); fields
may be `(N,H,W)` or `(N,n_cells)`. The HF-train design is read from the first
arm's `cond_hf_train_raw` unless `--hf_cond path[:key]` or `--hf_rows i,j,...`
is given. Pure numpy (torch only inside the shared rung loader) on the login
node.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROUND_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROUND_ROOT / "eval"))
from nrmse import nrmse, NRMSE_DEF_HASH                      # noqa: E402
from affine_ladder_voi import load_rungs, skill_denominator  # noqa: E402


# ── io helpers ──────────────────────────────────────────────────────

def _load_array(spec, default_key=None):
    """`path.npy` | `path.npz:key` | `path.npz` (uses default_key)."""
    key = default_key
    p = spec
    if not Path(p).exists() and ":" in spec:
        p, key = spec.rsplit(":", 1)
    p = Path(p)
    if not p.exists():
        raise SystemExit(f"not found: {spec}")
    if p.suffix == ".npz":
        z = np.load(p)
        if key is None or key not in z.files:
            raise SystemExit(f"{p} has keys {list(z.files)}; pass path:key")
        return np.asarray(z[key], dtype=np.float64), str(p), key
    return np.asarray(np.load(p), dtype=np.float64), str(p), None


def _flat(A, n_rows):
    A = np.asarray(A, dtype=np.float64)
    return A.reshape(n_rows, -1)


def aug(X):
    X = np.asarray(X, dtype=np.float64)
    return np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)


# ── the construction ────────────────────────────────────────────────

def design_null_row_bases(X_hf, tol=1e-10):
    """Orthonormal NULL (m) and ROW (r) bases of the augmented design's column space."""
    A = aug(X_hf)
    U, s, Vt = np.linalg.svd(A, full_matrices=True)
    smax = float(s[0]) if s.size else 0.0
    r = int((s > tol * max(smax, 1e-300)).sum())
    V_null = Vt[r:].T                      # (d+1, m)
    V_row = Vt[:r].T                       # (d+1, r)
    return V_null, V_row, r, [float(x) for x in s[:8]], A


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--arm", action="append", required=True,
                    help="NAME=path[:key] (repeatable; key defaults to pred_test)")
    ap.add_argument("--hf_cond", default=None,
                    help="path[:key] of the HF-train condition rows "
                         "(default: cond_hf_train_raw in the first arm's npz)")
    ap.add_argument("--hf_rows", default=None,
                    help="alternative: comma-separated row indices into the HF train rung")
    ap.add_argument("--contrast", action="append", default=[],
                    help="A:B — attribute the A-minus-B skill gap to the channels")
    ap.add_argument("--level", action="store_true",
                    help="also run the LEVEL channel (own-mean swap ladder)")
    ap.add_argument("--n_random", type=int, default=5,
                    help="random m-dim subspace control draws (0 disables)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--rank_tol", type=float, default=1e-10)
    ap.add_argument("--data_root", default="stripped", choices=["stripped", "orig"])
    ap.add_argument("--max_test", type=int, default=None)
    ap.add_argument("--skill_denominator", type=float, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    t0 = time.time()
    root_key = "stripped_data_root" if args.data_root == "stripped" else "data_root"
    out = {"_tool": "null_family_ceiling_audit.py", "_nrmse_def_hash": NRMSE_DEF_HASH,
           "_data_root": args.data_root, "dataset": args.dataset,
           "_oracle_key_convention": "_ORACLE suffix = fitted on the test targets; "
                                     "a CEILING, never an arm score"}

    data = load_rungs(args.dataset, root_key, max_test=args.max_test)
    X_te, Y_te = data["X_te"], data["Y_te"]
    bar, bar_src = skill_denominator(args.dataset, args.skill_denominator)
    out["skill_denominator"] = bar
    out["skill_denominator_source"] = bar_src
    out["n_test"] = int(X_te.shape[0])
    out["cond_dim"] = int(X_te.shape[1])

    def sk(P):
        P = np.asarray(P, dtype=np.float64)
        if P.ndim == 1:
            P = np.broadcast_to(P, Y_te.shape)
        return float(nrmse(np.ascontiguousarray(P), Y_te) / bar)

    # ---- arms -------------------------------------------------------
    arms, order, srcs = {}, [], {}
    for spec in args.arm:
        if "=" not in spec:
            raise SystemExit(f"--arm needs NAME=path: {spec}")
        name, path = spec.split("=", 1)
        A, p, k = _load_array(path, "pred_test")
        arms[name] = _flat(A, X_te.shape[0])
        srcs[name] = {"path": p, "key": k}
        order.append(name)
        if arms[name].shape != Y_te.shape:
            raise SystemExit(f"arm {name}: pred shape {arms[name].shape} != "
                             f"test target shape {Y_te.shape}")
    out["arm_sources"] = srcs

    # ---- HF-train design --------------------------------------------
    if args.hf_rows:
        rows = np.array([int(v) for v in args.hf_rows.split(",")], dtype=int)
        X_hf = data["rung"][data["hf"]]["X"][rows]
        design_src = f"--hf_rows {args.hf_rows} of the HF train rung"
    else:
        spec = args.hf_cond or args.arm[0].split("=", 1)[1].split(":")[0]
        X_hf, p, k = _load_array(spec, "cond_hf_train_raw")
        design_src = f"{p}:{k}"
    V_null, V_row, rank, svals, A_hf = design_null_row_bases(X_hf, args.rank_tol)
    m = int(V_null.shape[1])
    Xd_te = aug(X_te)
    C_null, C_row, C_aff = Xd_te @ V_null, Xd_te @ V_row, Xd_te
    out["design"] = {
        "source": design_src, "n_hf_train_rows": int(X_hf.shape[0]),
        "n_cols_augmented": int(A_hf.shape[1]), "numerical_rank": rank,
        "m_null_dim": m, "singular_values_head": svals,
        "null_functionals_vanish_at_hf_train_max_abs": float(np.abs(A_hf @ V_null).max())
        if m else 0.0,
        "cond_test_max_abs_diff_vs_loader": None,
    }
    # seam: if an arm npz carries the test conditions, check them against the loader
    for spec in args.arm:
        path = spec.split("=", 1)[1].split(":")[0]
        if Path(path).suffix == ".npz":
            z = np.load(path)
            if "cond_test_raw" in z.files:
                Xc = np.asarray(z["cond_test_raw"], float)[:X_te.shape[0]]
                out["design"]["cond_test_max_abs_diff_vs_loader"] = float(
                    np.abs(Xc - X_te).max())
                break
    if m == 0:
        out["design"]["note"] = ("design is FULL RANK — the null family is empty and the "
                                 "null/random columns are identically zero; the level "
                                 "channel (--level) is where a value-of-LF effect can live")

    def best_in_family_ORACLE(P, C):
        if C.shape[1] == 0:
            return sk(P)
        E = Y_te - P
        D, *_ = np.linalg.lstsq(C, E, rcond=None)
        return sk(P + C @ D)

    # ---- ceilings + dimension control (rng shared across arms, in --arm order) --
    rng = np.random.default_rng(args.seed)
    ceil = {}
    for name in order:
        P = arms[name]
        raw = sk(P)
        bn = best_in_family_ORACLE(P, C_null)
        br = best_in_family_ORACLE(P, C_row)
        ba = best_in_family_ORACLE(P, C_aff)
        e = {"raw_skill": raw,
             f"best_in_null_family_{m}d_ORACLE": bn,
             f"best_in_row_family_{rank}d_ORACLE": br,
             f"best_in_full_affine_family_{Xd_te.shape[1]}d_ORACLE": ba,
             "error_null_borne": raw - bn, "error_row_borne": raw - br,
             "error_affine_borne": raw - ba,
             "null_share_of_affine_fixable": (raw - bn) / max(raw - ba, 1e-12),
             "share_of_own_skill_that_is_null_borne": (raw - bn) / max(raw, 1e-300)}
        if args.n_random > 0 and m > 0:
            g = []
            for _ in range(args.n_random):
                Q, _ = np.linalg.qr(rng.standard_normal((Xd_te.shape[1], m)))
                g.append(raw - best_in_family_ORACLE(P, Xd_te @ Q))
            e["random_{}d_gain_mean".format(m)] = float(np.mean(g))
            e["random_{}d_gain_min".format(m)] = float(np.min(g))
            e["random_{}d_gain_max".format(m)] = float(np.max(g))
            e["null_over_random"] = (raw - bn) / max(float(np.mean(g)), 1e-12)
        ceil[name] = e
    out["functional_ceilings"] = ceil

    # ---- implicit affine law, null block vs the ORACLE law ------------
    def law(X, Y):
        A = aug(X)
        return np.linalg.solve(A.T @ A, A.T @ np.asarray(Y, np.float64))

    W_or = law(X_te, Y_te)
    N_or = V_null.T @ W_or if m else np.zeros((0, W_or.shape[1]))
    R_or = W_or - V_null @ N_or if m else W_or
    lawblk = {"ORACLE_law_null_energy_frac":
              float((N_or ** 2).sum() / max((W_or ** 2).sum(), 1e-300)) if m else 0.0}
    for name in order:
        P = arms[name]
        W = law(X_te, P)
        N = V_null.T @ W if m else np.zeros((0, W.shape[1]))
        R = W - V_null @ N if m else W
        lawblk[name] = {
            "null_energy_frac": float((N ** 2).sum() / max((W ** 2).sum(), 1e-300)) if m else 0.0,
            "null_block_frobenius_cos_vs_ORACLE": float(
                (N * N_or).sum() / max(np.linalg.norm(N) * np.linalg.norm(N_or), 1e-300))
            if m else None,
            "null_block_recovery_ratio_vs_ORACLE": float(
                np.linalg.norm(N) / max(np.linalg.norm(N_or), 1e-300)) if m else None,
            "row_block_rel_l2_vs_ORACLE": float(
                np.linalg.norm(R - R_or) / max(np.linalg.norm(R_or), 1e-300)),
            "non_affinity_of_the_arm": float(
                np.linalg.norm(P - Xd_te @ W) / max(np.linalg.norm(P), 1e-300)),
        }
    out["implicit_law_blocks_ORACLE_reference"] = lawblk

    # ---- level channel ------------------------------------------------
    if args.level:
        hf = data["hf"]
        Y_hf_all = data["rung"][hf]["Y_native"]
        consts = {"hf_train_mean_full": Y_hf_all.mean(axis=0),
                  "oracle_test_mean_ORACLE": Y_te.mean(axis=0)}
        for f in sorted(int(x) for x in data["rung"] if int(x) != hf):
            consts[f"lf_rung{f}_mean_lifted"] = data["rung"][f]["Y_up"].mean(axis=0)
        rows_n5 = None
        if args.hf_rows:
            rows_n5 = np.array([int(v) for v in args.hf_rows.split(",")], dtype=int)
        else:
            first = args.arm[0].split("=", 1)[1].split(":")[0]
            if Path(first).suffix == ".npz":
                z = np.load(first)
                if "selected_train_rows" in z.files:
                    rows_n5 = np.asarray(z["selected_train_rows"], int)
        if rows_n5 is not None:
            consts["hf_train_mean_n_selected"] = Y_hf_all[rows_n5].mean(axis=0)
        lev = {"const_field_reference_skill": {k: sk(v) for k, v in consts.items()},
               "truth_fluct_share_of_energy_ORACLE": float(
                   ((Y_te - Y_te.mean(axis=0)) ** 2).sum() / (Y_te ** 2).sum())}
        for name in order:
            P = arms[name]
            own = P.mean(axis=0)
            lev[name] = {
                "own_mean_broadcast_skill": sk(own),
                "own_mean_rel_dist_to_hf_train_mean_full": float(
                    np.linalg.norm(own - consts["hf_train_mean_full"])
                    / max(np.linalg.norm(consts["hf_train_mean_full"]), 1e-300)),
                "swap_own_level_for": {k: sk(P - own + c) for k, c in consts.items()},
            }
        out["level_channel"] = lev

    # ---- contrasts ----------------------------------------------------
    if args.contrast:
        con = {}
        for spec in args.contrast:
            a, b = spec.split(":")
            g = ceil[a]["raw_skill"] - ceil[b]["raw_skill"]
            e = {"total_gap_skill_units": g,
                 "null_borne_difference": ceil[a]["error_null_borne"] - ceil[b]["error_null_borne"],
                 "row_borne_difference": ceil[a]["error_row_borne"] - ceil[b]["error_row_borne"]}
            e["null_share"] = e["null_borne_difference"] / g if g else None
            e["row_share"] = e["row_borne_difference"] / g if g else None
            if args.level:
                lv = out["level_channel"][a]
                gain = ceil[a]["raw_skill"] - lv["swap_own_level_for"]["hf_train_mean_full"]
                e["level_channel_upper_bound_from_arm_a"] = gain
                e["level_share"] = gain / g if g else None
            e["note"] = ("shares are NOT additive under nRMSE (a mean of per-sample "
                         "ratios, not a squared norm); read them as attributions, "
                         "not an accounting identity")
            con[spec] = e
        out["contrasts"] = con

    out["_wall_seconds"] = round(time.time() - t0, 1)
    txt = json.dumps(out, indent=1)
    if args.out:
        Path(args.out).write_text(txt)
        print(f"wrote {args.out}", flush=True)
    for name in order:
        c = ceil[name]
        nr = ("null/random {:.3f}".format(c["null_over_random"])
              if "null_over_random" in c else "null/random n/a")
        print(f"[{args.dataset}] {name}: raw {c['raw_skill']:.4f} "
              f"null-borne {c['error_null_borne']:.4f} (m={m}) "
              f"row-borne {c['error_row_borne']:.4f} {nr}", flush=True)
    if not args.out:
        print(txt)


if __name__ == "__main__":
    main()
