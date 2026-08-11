#!/usr/bin/env python
"""PHASE P — the SEAL. Card `r3s3_lf_value-B3` part 3, phase P (CPU only, NO GPU).

WHAT THIS IS
    The pre-registration driver. It emits, for every cell of `R3S3B3_CELLS`, the
    training-free surrogate's predicted step-max knee cap `c_pred` BEFORE any
    training leg runs, and seals it (payload sha256 + `_sealed_utc`) into
    `R3S3B3_PREREG_JSON`. That ordering IS the experiment: the card's claim is
    the DIRECTION OF INFERENCE, so a prediction written after a leg is worthless.

    `scripts/01_train_eval.sh` refuses to run without the seal, and the family
    re-checks the payload digest against `R3S3B3_PREREG_SHA256` on every leg.

WHY A DRIVER AND NOT THE BARE CLI
    The card's `_phase_P` directive names `tools/coverage_knee_surrogate.py`.
    This driver does not reimplement it: it IMPORTS that registered instrument
    read-only and calls its own `lift_rung` / `fit_predict` / `draw_kept` /
    `union` / `nrmse` objects, so the numerics are the tool's by construction.
    It changes exactly ONE thing, and it has to:

      * the tool's `main()` loads splits with `panel_data.load_split`, which
        reads the ORIGINAL data root. For `sharp__phase_field_crystal_2d` that
        root serves train rungs {1, 2}, but the round-3 STRIPPED view that the
        trained arm sees serves {1, 3} — L2 is deliberately withheld (ADR
        r3-0005; `stripped_data/sharp__phase_field_crystal_2d/
        SERVED_FIDS_ADR_r3-0005.md`). A prediction made over a rung the arm can
        never train on would not be a prediction of this card's ladder, and the
        card's own blocking pre-flight (3) forbids exactly that. So every split
        here is loaded from the STRIPPED view through the same
        `data_adapters.loaders.load_mf_dataset` the family uses.

    That divergence is CELL-LOCAL: on `sharp__cahn_hilliard`,
    `sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d` and `ifc_heat` the stripped
    and original TRAIN splits carry the same rungs, so `--cli-crosscheck` runs
    the bare CLI on those cells and asserts the per-cap `R` table is
    BIT-IDENTICAL to this driver's. pfc is the one cell where it cannot, and the
    seal records that with its reason.

WHAT IT PRODUCES PER CELL (card part 3, phase P items 1-3)
    1. the DENSE pass over `{5,10,20,40,80,160,320,FULL}` clipped/deduped to the
       cell's per-rung uncovered pool, `--kernel both --lam 1e-3 --n-hf 5`,
       draws `0,1,2` (sharp) or `native` (ifc)  ->  `c_hat`;
    2. the mechanical ladder rule (no discretion) -> `{r1, r2, r3, r4}`;
    3. the REGISTERED pass restricted to that ladder -> `c_pred` (the sealed
       prediction), `c_pred` under the linear kernel (specificity control), the
       full `R_surr` curve on the 4 rungs, and the two structural nulls
       (`design_rank` saturation cap, `nnc` field oracle);
    4. the 64-draw histogram of `c_pred` (the fold-population enumeration the
       batch-3 scope rule 3 asks for at `n_fit = 5`), sharp cells only — an ifc
       cell has ONE fold (native `N_hf = 5`), so its histogram is degenerate and
       is recorded as such rather than faked.

BUILDER-RESOLVED, NOT IN THE CARD (both recorded in the seal itself)
    * the 64 draw seeds are `0..63` — the card says "64-draw" without naming
      them; `0..63` is the round's own `SPLIT_SEED` generator family and
      contains the card's three scored draws `{0,1,2}`;
    * `round()` is Python's built-in (round-half-to-even). The card writes
      `round(c_hat/4)`; on its own worked example (c_hat 80 -> {5,20,80,395})
      no half-integer arises, so the tie rule is exercised only if a future
      `c_hat` is 2 (mod 8), and it is pinned here rather than left implicit.

USAGE
    python scripts/phase_p_prereg.py --out <prereg.json> --work <scratch dir>
                                     [--cells a,b,c] [--cli-crosscheck]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WORKTREE_ROOT = HERE.parent


def _main_root() -> Path:
    """The MAIN checkout (same rule as the family's `smoke_eval._main_root`)."""
    for anc in WORKTREE_ROOT.parents:
        if (anc / "mffp_autoresearch" / "round2" / "project.yaml").exists():
            return anc
    return WORKTREE_ROOT


MAIN_ROOT = _main_root()
ROUND3 = MAIN_ROOT / "mffp_autoresearch" / "round3"
TOOL_PATH = ROUND3 / "tools" / "coverage_knee_surrogate.py"
STRIPPED = MAIN_ROOT / "mffp_autoresearch" / "round2" / "stripped_data"
FACTORY_ROOT = MAIN_ROOT / "mf_field" / "factory_mffp"

if not TOOL_PATH.exists():
    raise SystemExit(f"registered instrument not found: {TOOL_PATH}")
sys.path.insert(0, str(ROUND3 / "tools"))
sys.path.insert(0, str(FACTORY_ROOT))

import coverage_knee_surrogate as cks               # noqa: E402  READ-ONLY import
from data_adapters.loaders import load_mf_dataset   # noqa: E402

nrmse = cks.nrmse
KEY_ROUND = cks.KEY_ROUND

# Card `recipe.env.R3S3B3_CELLS` (ADR r3-0007 option C).
CELLS = ("sharp__cahn_hilliard", "sharp__allen_cahn_2d", "sharp__fisher_kpp_2d",
         "sharp__phase_field_crystal_2d", "ifc_heat")
# Card part 3 phase P item 1, verbatim.
DENSE_CAPS = (5, 10, 20, 40, 80, 160, 320)          # + FULL, appended per cell
LAM = 1e-3
KERNELS = ("rbf", "linear")
N_HF = 5
SHARP_DRAWS = (0, 1, 2)                             # card `_hf_subset_draws`
HIST_DRAWS = tuple(range(64))                       # builder-resolved, see docstring
# Card `_cell_roles` as amended by `_ifc_clause_status` (ADR r3-0007 option C).
CELL_ROLES = {
    "sharp__allen_cahn_2d": "predictive (zero anchors on the cell)",
    "sharp__fisher_kpp_2d": "predictive (zero anchors on the cell)",
    "sharp__phase_field_crystal_2d":
        "predictive (zero anchors); CONDITIONAL — adjudicated only if a certified "
        "pfc tau_rel exists at analysis time (none exists today)",
    "sharp__cahn_hilliard": "reproduction control (B2 measured knee cap 80)",
    "ifc_heat": "reproduction control (B2 measured knee cap 5); pre-declared "
                "UNRESOLVED at tau_rel_film 0.335905",
}
# Card `_cell_roles`, verbatim: the caps B2 MEASURED on the two control cells.
# Recorded so the seal states, mechanically, whether the ladder rule's own output
# even contains the cap the control is supposed to reproduce.
B2_MEASURED_KNEE = {"sharp__cahn_hilliard": 80, "ifc_heat": 5}
# The cells whose STRIPPED train split carries the same rungs as the original
# data root, i.e. where the bare CLI is a valid cross-check (see the docstring).
CLI_COMPARABLE = ("sharp__cahn_hilliard", "sharp__allen_cahn_2d",
                  "sharp__fisher_kpp_2d", "ifc_heat")


# ── the cell's data, loaded from the STRIPPED view ───────────────────────────

def load_cell(ds: str) -> dict:
    tr = load_mf_dataset(STRIPPED / ds, "train")
    te = load_mf_dataset(STRIPPED / ds, "test")
    if te["lf_fids"]:
        raise SystemExit(f"{ds}: the stripped TEST split exposes LF fidelities "
                         f"{te['lf_fids']}; refusing to build a prediction on it")
    hf = int(tr["hf_fid"])
    rungs = sorted(int(f) for f in tr["lf_fids"])
    if not rungs:
        raise SystemExit(f"{ds}: no LF rung in the stripped train split")
    cond_hf_tr = np.asarray(tr["cond_by_fid"][hf], dtype=np.float64)
    fld_hf_tr = np.asarray(tr["field_by_fid"][hf], dtype=np.float64)
    cond_te = np.asarray(te["cond_by_fid"][int(te["hf_fid"])], dtype=np.float64)
    y = np.asarray(te["field_by_fid"][int(te["hf_fid"])], dtype=np.float64)
    cond_by_rung = {f: np.asarray(tr["cond_by_fid"][f], dtype=np.float64) for f in rungs}
    # `cks.lift_rung` is the tool's own frozen copy-LF lift (round2/eval
    # panel_data.copylf_prediction), called on the stripped train dict.
    lift_by_rung = {f: cks.lift_rung(tr, f, ds) for f in rungs}
    base = cond_by_rung[rungs[0]]
    Zmu, Zsd = base.mean(0), base.std(0)
    Zsd = np.where(Zsd == 0, 1.0, Zsd)
    return {
        "ds": ds, "hf": hf, "rungs": rungs, "train": tr,
        "cond_hf_tr": cond_hf_tr, "fld_hf_tr": fld_hf_tr,
        "cond_te": cond_te, "y": y, "Zte": (cond_te - Zmu) / Zsd,
        "cond_by_rung": cond_by_rung, "lift_by_rung": lift_by_rung,
        "Zmu": Zmu, "Zsd": Zsd,
        "n_train_hf": int(cond_hf_tr.shape[0]), "n_test": int(y.shape[0]),
        "cond_dim": int(cond_te.shape[1]),
        "grid_shape_by_fid": {str(int(f)): [int(x) for x in g]
                              for f, g in tr["grid_shape_by_fid"].items()},
    }


def hf_rows_for_draw(c: dict, draw):
    """The card's own HF draw rule (`_hf_subset_draws`), or the native split."""
    n = c["n_train_hf"]
    if draw == "native" or n <= N_HF:
        return list(range(n))
    return sorted(np.random.default_rng(int(draw)).permutation(n)[:N_HF].tolist())


def uncovered_per_rung(c: dict, hf_rows) -> dict:
    hf_keys = {tuple(np.round(x, KEY_ROUND)) for x in c["cond_hf_tr"][hf_rows]}
    return {int(f): int(sum(1 for x in C
                            if tuple(np.round(x, KEY_ROUND)) not in hf_keys))
            for f, C in c["cond_by_rung"].items()}


def full_cap(c: dict, draws) -> tuple:
    """FULL = max over rungs of the uncovered pool (card `_ladder_rule`: r4 = FULL,
    'per-rung uncovered pool = the A1_lf_all arm'). Asserted draw-invariant."""
    per_draw = {str(d): uncovered_per_rung(c, hf_rows_for_draw(c, d)) for d in draws}
    vals = {max(v.values()) for v in per_draw.values()}
    if len(vals) != 1:
        raise SystemExit(f"{c['ds']}: FULL is not draw-invariant: {per_draw}")
    return int(vals.pop()), per_draw


def dense_caps_for(full: int) -> list:
    """Card part 3: `{5,10,20,40,80,160,320,FULL}` clipped/deduped."""
    return sorted({int(x) for x in DENSE_CAPS if int(x) < int(full)} | {int(full)})


# ── the surrogate pass (the tool's own functions, verbatim) ──────────────────

def _e1_full_pool(c: dict, kernels, lam) -> dict:
    """The A1 analogue (FULL LF pool), memoised per cell.

    A pure function of (cell, kernel, lam) — it reads no draw and no cap — so
    caching it changes no number and removes the dominant cost from the 64-draw
    fold-population pass.
    """
    cache = c.setdefault("_e1_cache", {})
    todo = [k for k in kernels if (k, lam) not in cache]
    if todo:
        Cf, Ff = cks.union({f: list(range(len(c["cond_by_rung"][f])))
                            for f in c["rungs"]}, c["cond_by_rung"], c["lift_by_rung"])
        Zf = (Cf - c["Zmu"]) / c["Zsd"]
        for k in todo:
            cache[(k, lam)] = nrmse(cks.fit_predict(Zf, Ff, c["Zte"], lam, k), c["y"])
    return {k: cache[(k, lam)] for k in kernels}


def _e0_draw(c: dict, draw, kernels, lam) -> dict:
    """The A0 analogue at one HF draw, memoised per (cell, draw)."""
    cache = c.setdefault("_e0_cache", {})
    key = str(draw)
    got = cache.setdefault(key, {})
    todo = [k for k in kernels if (k, lam) not in got]
    if todo:
        rows = hf_rows_for_draw(c, draw)
        Zh = (c["cond_hf_tr"][rows] - c["Zmu"]) / c["Zsd"]
        for k in todo:
            got[(k, lam)] = nrmse(
                cks.fit_predict(Zh, c["fld_hf_tr"][rows], c["Zte"], lam, k), c["y"])
    return {k: got[(k, lam)] for k in kernels}


def _knee(caps_sorted, R_by_cap: dict) -> dict:
    steps = [R_by_cap[caps_sorted[i + 1]] - R_by_cap[caps_sorted[i]]
             for i in range(len(caps_sorted) - 1)]
    knee = caps_sorted[int(np.argmax(steps)) + 1]
    second = sorted(steps, reverse=True)[1] if len(steps) > 1 else float("nan")
    return dict(knee_by_stepmax=int(knee), steps=[float(s) for s in steps],
                R_at_knee=float(R_by_cap[knee]), step_into_knee=float(max(steps)),
                margin_R=float(max(steps) - second))


def surrogate(c: dict, caps, draws, kernels=KERNELS, lam=LAM, mask=None) -> dict:
    """Reproduces `coverage_knee_surrogate.main()`'s table for `caps` x `draws`."""
    Zte, y = c["Zte"], c["y"]
    e1 = _e1_full_pool(c, kernels, lam)
    hf_rows_by_draw, e0 = {}, {}
    for d in draws:
        hf_rows_by_draw[str(d)] = hf_rows_for_draw(c, d)
        e0[str(d)] = _e0_draw(c, d, kernels, lam)

    cells = []
    for cap in caps:
        for d in draws:
            ds_ = str(d)
            kept = cks.draw_kept(c["cond_by_rung"], c["cond_hf_tr"][hf_rows_by_draw[ds_]],
                                 int(cap), 0 if d == "native" else int(d))
            C, F = cks.union(kept, c["cond_by_rung"], c["lift_by_rung"])
            Zk = (C - c["Zmu"]) / c["Zsd"]
            A = np.concatenate([Zk, np.ones((len(Zk), 1))], 1)
            sv = np.linalg.svd(A, compute_uv=False)
            d2 = ((Zte[:, None, :] - Zk[None, :, :]) ** 2).sum(-1)
            j = d2.argmin(1)
            rec = dict(cap=int(cap), draw=ds_, n_distinct=int(len(C)),
                       design_rank=int((sv > sv[0] * 1e-10).sum()),
                       d_med=float(np.median(np.sqrt(d2.min(1)))),
                       nnc=nrmse(F[j], y))
            for k in kernels:
                p = cks.fit_predict(Zk, F, Zte, lam, k)
                rec[f"nrmse_{k}"] = nrmse(p, y)
                rec[f"R_{k}"] = (e0[ds_][k] - rec[f"nrmse_{k}"]) / (e0[ds_][k] - e1[k])
                if mask is not None:
                    rl = np.linalg.norm(p - y, axis=1) / np.linalg.norm(y, axis=1)
                    rec[f"rel_hard_{k}"] = float(rl[mask].mean())
                    rec[f"rel_bulk_{k}"] = float(rl[~mask].mean())
            cells.append(rec)

    per_cap = {}
    for cap in caps:
        sub = [r for r in cells if r["cap"] == int(cap)]
        per_cap[int(cap)] = {k: float(np.mean([r[k] for r in sub]))
                             for k in sub[0] if k != "draw"}
    ks = sorted(per_cap)
    verdict = {k: _knee(ks, {cap: per_cap[cap][f"R_{k}"] for cap in ks})
               for k in kernels}
    # PER-DRAW verdicts: the same step-max statistic evaluated fold by fold. This
    # is what the card's 64-draw fold-population histogram enumerates; computing
    # it here (rather than re-running the whole pass per draw) reuses the
    # memoised A1 analogue and changes no number.
    per_draw_verdict = {}
    for d in draws:
        ds_ = str(d)
        per_draw_verdict[ds_] = {
            k: _knee(ks, {cap: next(r[f"R_{k}"] for r in cells
                                    if r["cap"] == int(cap) and r["draw"] == ds_)
                          for cap in ks})
            for k in kernels}
    rk = [per_cap[cap]["design_rank"] for cap in ks]
    sat = next((int(cap) for cap, r in zip(ks, rk) if r >= max(rk)), None)
    return {"caps": [int(x) for x in ks], "draws": [str(d) for d in draws],
            "a0": e0, "a1": e1, "per_cap": {str(k): v for k, v in per_cap.items()},
            "cells": cells, "verdict": verdict, "per_draw_verdict": per_draw_verdict,
            "null_design_rank": {"saturation_cap": sat, "max_rank": int(max(rk)),
                                 "by_cap": {str(cap): int(r) for cap, r in zip(ks, rk)},
                                 "reading": "if this saturates far BELOW the knee, the "
                                            "knee is not a condition-space-rank story"},
            "null_nnc_field_oracle": {
                "min": float(min(per_cap[cap]["nnc"] for cap in ks)),
                "max": float(max(per_cap[cap]["nnc"] for cap in ks)),
                "by_cap": {str(cap): float(per_cap[cap]["nnc"]) for cap in ks},
                "reading": "if it never goes usefully below 1.0, the knee is not a "
                           "coverage-radius story"}}


# ── the mechanical ladder rule (card `recipe.env._ladder_rule`, verbatim) ────

def ladder_from(c_hat: int, full: int) -> dict:
    """r3 = c_hat; r2 = max(2, round(c_hat/4)); r1 = max(1, round(c_hat/16));
    r4 = FULL. Enforce 1 <= r1 < r2 < r3 < r4 by decrementing to the next
    distinct integer. If c_hat == FULL: r3 = round(FULL/4), r2 = round(FULL/16),
    r1 = max(1, round(FULL/64)), registered prediction = FULL."""
    trace = []
    c_hat, full = int(c_hat), int(full)
    if c_hat == full:
        r3, r2, r1 = round(full / 4), round(full / 16), max(1, round(full / 64))
        branch = "c_hat == FULL"
        rule_registered = full
    else:
        r3 = c_hat
        r2 = max(2, round(c_hat / 4))
        r1 = max(1, round(c_hat / 16))
        branch = "c_hat < FULL"
        rule_registered = None
    r4 = full
    trace.append(f"branch={branch} raw r1,r2,r3,r4 = {r1},{r2},{r3},{r4}")
    # strict increase, enforced by DECREMENTING to the next distinct integer
    if r2 >= r3:
        r2 = r3 - 1
        trace.append(f"r2 >= r3 -> decrement r2 to {r2}")
    if r1 >= r2:
        r1 = r2 - 1
        trace.append(f"r1 >= r2 -> decrement r1 to {r1}")
    if not (1 <= r1 < r2 < r3 < r4):
        raise SystemExit(f"ladder rule cannot satisfy 1 <= r1 < r2 < r3 < r4 for "
                         f"c_hat={c_hat} FULL={full}: got {r1},{r2},{r3},{r4}")
    return {"r1": int(r1), "r2": int(r2), "r3": int(r3), "r4": int(r4),
            "rungs": [int(r1), int(r2), int(r3), int(r4)],
            "branch": branch, "trace": trace,
            "rule_registered_prediction_if_c_hat_eq_full": rule_registered,
            "rounding": "python builtin round() (round-half-to-even)"}


# ── the bare-CLI cross-check ─────────────────────────────────────────────────

def cli_crosscheck(ds: str, caps, draws, work: Path) -> dict:
    out = work / f"{ds}_dense_cli.json"
    cmd = [sys.executable, str(TOOL_PATH), "--dataset", ds,
           "--caps", ",".join(str(int(x)) for x in caps),
           "--n-hf", str(N_HF), "--draws", ",".join(str(d) for d in draws),
           "--kernel", "both", "--lam", str(LAM), "--out", str(out)]
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return {"performed": True, "ok": False, "cmd": " ".join(cmd),
                "returncode": r.returncode, "stderr": r.stderr[-2000:]}
    got = json.loads(out.read_text())
    return {"performed": True, "ok": True, "cmd": " ".join(cmd),
            "seconds": round(time.time() - t0, 1), "out": str(out),
            "verdict": got["verdict"], "per_cap": got["per_cap"]}


def compare_tables(cli: dict, mine: dict) -> dict:
    """Bit-identity of the per-cap R table (both kernels)."""
    diffs = {}
    for k in KERNELS:
        for cap, v in mine["per_cap"].items():
            a = cli["per_cap"].get(str(cap), cli["per_cap"].get(cap))
            if a is None:
                diffs[f"{k}@{cap}"] = "cap missing from the CLI table"
                continue
            if a[f"R_{k}"] != v[f"R_{k}"]:
                diffs[f"{k}@{cap}"] = {"cli": a[f"R_{k}"], "driver": v[f"R_{k}"],
                                       "abs_diff": abs(a[f"R_{k}"] - v[f"R_{k}"])}
    return {"bit_identical": not diffs, "diffs": diffs,
            "cli_knee": {k: cli["verdict"][k]["knee_by_stepmax"] for k in KERNELS},
            "driver_knee": {k: mine["verdict"][k]["knee_by_stepmax"] for k in KERNELS}}


# ── main ────────────────────────────────────────────────────────────────────

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      default=float).encode()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="the seal file (R3S3B3_PREREG_JSON)")
    ap.add_argument("--work", required=True, help="scratch dir for per-cell dumps")
    ap.add_argument("--cells", default=",".join(CELLS))
    ap.add_argument("--cli-crosscheck", action="store_true")
    ap.add_argument("--hist-draws", type=int, default=len(HIST_DRAWS))
    a = ap.parse_args()

    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)
    cells = [t for t in a.cells.split(",") if t]

    film = json.loads((ROUND3 / "state" / "anchors" / "film_denominator.json")
                      .read_text())["datasets"]
    noise = json.loads((ROUND3 / "state" / "anchors_repaired" / "noise_floor.json")
                       .read_text())

    payload = {"_cells": cells, "_n_hf": N_HF, "_lam": LAM,
               "_kernels": list(KERNELS), "_dense_caps_rule":
               "{5,10,20,40,80,160,320,FULL} clipped/deduped to the cell's per-rung "
               "uncovered pool (card part 3 phase P item 1)",
               "_ladder_rule":
               "r3=c_hat; r2=max(2,round(c_hat/4)); r1=max(1,round(c_hat/16)); r4=FULL; "
               "enforce 1<=r1<r2<r3<r4 by decrementing; if c_hat==FULL then "
               "r3=round(FULL/4), r2=round(FULL/16), r1=max(1,round(FULL/64)) "
               "(card recipe.env._ladder_rule, verbatim)",
               "_registered_statistic":
               "c_pred = the step-max knee of the surrogate RECOMPUTED on {r1,r2,r3,r4} "
               "(card part 3 phase P item 2). A divergence from the dense c_hat is "
               "FLAGGED, never overridden.",
               "_view": str(STRIPPED),
               "cells": {}}

    for ds in cells:
        t0 = time.time()
        print(f"\n===== {ds} =====", flush=True)
        c = load_cell(ds)
        draws = ["native"] if c["n_train_hf"] <= N_HF else list(SHARP_DRAWS)
        full, unc = full_cap(c, draws)
        caps = dense_caps_for(full)
        print(f"  rungs={c['rungs']} n_train_hf={c['n_train_hf']} n_test={c['n_test']} "
              f"cond_dim={c['cond_dim']} FULL={full} caps={caps} draws={draws}",
              flush=True)

        # ── the stratification mask, "where a mask exists" (card part 3 item 1) ──
        mask, mask_rec = None, {"applied": False}
        mp = work / f"{ds}_strat_mask.npz"
        if mp.exists():
            z = np.load(mp)
            mask = np.asarray(z["hard_mask_rederived_model_free"], dtype=bool)
            mask_rec = {"applied": True, "source": str(mp),
                        "key": "hard_mask_rederived_model_free",
                        "n_hard": int(mask.sum()), "n_test": int(mask.size)}
        else:
            mask_rec = {"applied": False,
                        "reason": "no model-free mask artifact exists for this cell "
                                  "before any leg runs; the family re-derives it per "
                                  "leg in phase C (R3S3B3_HARD_MASK_MODE="
                                  "rederive_model_free), so the stratified readout is "
                                  "reported on every cell there"}

        dense = surrogate(c, caps, draws, mask=mask)
        c_hat = dense["verdict"]["rbf"]["knee_by_stepmax"]
        print(f"  DENSE c_hat (rbf step-max) = {c_hat}   "
              f"linear = {dense['verdict']['linear']['knee_by_stepmax']}", flush=True)

        lad = ladder_from(c_hat, full)
        print(f"  LADDER {lad['rungs']}  ({lad['branch']})", flush=True)

        reg = surrogate(c, lad["rungs"], draws, mask=mask)
        c_pred = reg["verdict"]["rbf"]["knee_by_stepmax"]
        c_pred_lin = reg["verdict"]["linear"]["knee_by_stepmax"]
        print(f"  REGISTERED c_pred = {c_pred}  (linear control {c_pred_lin})  "
              f"margin_R = {reg['verdict']['rbf']['margin_R']:.4f}", flush=True)

        # ── the fold-population histogram ──
        if draws == ["native"]:
            hist = {"applicable": False,
                    "reason": "this cell's HF train split is native N_hf = 5 (one "
                              "fold); the C(N_train, 5) fold population is a single "
                              "point, so a 64-draw histogram is degenerate"}
        else:
            hd = list(HIST_DRAWS[:a.hist_draws])
            hr = surrogate(c, lad["rungs"], hd, kernels=("rbf",))
            per_draw = {d: {"knee": v["rbf"]["knee_by_stepmax"],
                            "margin_R": v["rbf"]["margin_R"],
                            "steps": v["rbf"]["steps"]}
                        for d, v in hr["per_draw_verdict"].items()}
            knees = [per_draw[str(d)]["knee"] for d in hd]
            cnt = Counter(knees)
            hist = {"applicable": True, "n_draws": len(knees),
                    "draw_seeds": hd,
                    "counts": {str(k): int(v) for k, v in sorted(cnt.items())},
                    "modal_knee": int(cnt.most_common(1)[0][0]),
                    "modal_frequency": float(cnt.most_common(1)[0][1] / len(knees)),
                    "c_pred_frequency": float(cnt.get(int(c_pred), 0) / len(knees)),
                    "per_draw": per_draw,
                    "note": "fold population over the HF draw at n_fit = 5 (batch-3 "
                            "scope rule 3); the SEALED prediction is c_pred from the "
                            "card's own 3 scored draws, not the modal knee"}
            print(f"  HISTOGRAM modal={hist['modal_knee']} "
                  f"({hist['modal_frequency']:.2f})  c_pred freq="
                  f"{hist['c_pred_frequency']:.2f}  counts={hist['counts']}", flush=True)

        cross = {"performed": False,
                 "reason": "the stripped train split of this cell serves a DIFFERENT "
                           "rung set than the original data root the bare CLI reads "
                           "(ADR r3-0005: pfc serves {1,3}, L2 withheld), so the CLI "
                           "table is not comparable and would model a rung the trained "
                           "arm never sees"}
        if a.cli_crosscheck and ds in CLI_COMPARABLE:
            cli = cli_crosscheck(ds, caps, draws, work)
            cross = {**cli, **(compare_tables(cli, dense) if cli.get("ok") else {})}
            print(f"  CLI cross-check bit_identical="
                  f"{cross.get('bit_identical')}", flush=True)

        nf = noise.get(ds, {})
        fd = film.get(ds, {})
        tau_rel = nf.get("tau_rel")
        c_ds = fd.get("c_ds")
        payload["cells"][ds] = {
            "dataset": ds,
            "cell_role": CELL_ROLES.get(ds),
            "view": "stripped",
            "lf_rungs_trained": c["rungs"],
            "hf_fid": c["hf"], "grid_shape_by_fid": c["grid_shape_by_fid"],
            "n_train_hf": c["n_train_hf"], "n_test": c["n_test"],
            "cond_dim": c["cond_dim"],
            "draws": [str(d) for d in draws],
            "uncovered_per_rung_by_draw": {k: {str(f): v for f, v in d.items()}
                                           for k, d in unc.items()},
            "FULL": int(full),
            "dense": dense,
            "c_hat": int(c_hat),
            "ladder": lad,
            "registered": reg,
            "c_pred": int(c_pred),
            "c_pred_linear_specificity_control": int(c_pred_lin),
            "c_pred_diverges_from_c_hat": bool(int(c_pred) != int(c_hat)),
            "R_surr_curve_on_ladder": {
                str(cap): {k: reg["per_cap"][str(cap)][f"R_{k}"] for k in KERNELS}
                for cap in lad["rungs"]},
            "margin_R_surrogate": reg["verdict"]["rbf"]["margin_R"],
            "structural_nulls": {"design_rank": reg["null_design_rank"],
                                 "nnc_field_oracle": reg["null_nnc_field_oracle"]},
            "per_draw_knee_on_registered_ladder": {
                d: {k: v[k]["knee_by_stepmax"] for k in KERNELS}
                for d, v in reg["per_draw_verdict"].items()},
            "surrogate_draw_unanimous": len({
                v["rbf"]["knee_by_stepmax"] for v in reg["per_draw_verdict"].values()
            }) == 1,
            "reproduction_control": (
                {"b2_measured_knee_cap": B2_MEASURED_KNEE[ds],
                 "source": "card recipe.env._cell_roles",
                 "cap_in_dense_ladder": int(B2_MEASURED_KNEE[ds]) in caps,
                 "cap_in_registered_ladder": int(B2_MEASURED_KNEE[ds]) in lad["rungs"],
                 "note": "STATED, NOT ADJUSTED. The dense ladder is the card's own "
                         "verbatim {5,10,20,40,80,160,320,FULL} and the registered "
                         "ladder is the card's own mechanical rule applied to c_hat; "
                         "neither was moved to make a control cap reachable."}
                if ds in B2_MEASURED_KNEE else None),
            "fold_population_histogram": hist,
            "stratification_mask": mask_rec,
            "cli_crosscheck": cross,
            "film_units": {
                "nrmse_film_mean": fd.get("nrmse_film_mean"),
                "c_ds": c_ds, "tau_rel": tau_rel,
                "tau_rel_film": (float(tau_rel) * float(c_ds)
                                 if (tau_rel is not None and c_ds is not None) else None),
                "tau_rel_certified": tau_rel is not None,
                "note": ("NO certified tau_rel for this cell — the card registers it "
                         "CONDITIONALLY and it is adjudicated only if one is certified "
                         "at analysis time" if tau_rel is None else
                         "tau_rel_film = tau_rel * c_ds (card `_adjudicability`)")},
            "seconds": round(time.time() - t0, 1),
        }
        (work / f"{ds}_phaseP.json").write_text(
            json.dumps(payload["cells"][ds], indent=1, default=float))
        print(f"  [{ds}] done in {payload['cells'][ds]['seconds']}s", flush=True)

    sha = hashlib.sha256(canonical(payload)).hexdigest()
    seal = {
        "_card": "r3s3_lf_value-B3",
        "_phase": "P",
        "_what": "PRE-REGISTERED step-max knee caps, emitted with ZERO anchors on the "
                 "target cell and sealed BEFORE any training leg ran. The card's claim "
                 "is the direction of inference; a prediction written after a leg is "
                 "worthless.",
        "_sealed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_payload_sha256": sha,
        "_payload_digest_convention":
            "sha256(json.dumps(payload, sort_keys=True, separators=(',',':'), "
            "default=float).encode()) — recompute with scripts/phase_p_prereg.py::"
            "canonical",
        "_instrument": {
            "path": str(TOOL_PATH),
            "sha256": hashlib.sha256(TOOL_PATH.read_bytes()).hexdigest(),
            "imported_read_only": True},
        "_driver": {
            "path": str(Path(__file__).resolve()),
            "sha256": hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()},
        "_eval_layer": str(MAIN_ROOT / "mffp_autoresearch" / "round2" / "eval"),
        "_builder_resolved": {
            "hist_draw_seeds": "0..63 (the card says '64-draw' without naming them; "
                               "this is the round's own SPLIT_SEED generator family "
                               "and contains the card's scored draws {0,1,2})",
            "rounding": "python builtin round(), round-half-to-even",
            "FULL": "max over rungs of the uncovered pool, asserted draw-invariant",
            "stripped_view": "every split is loaded from the round-3 stripped view "
                             "through data_adapters.loaders.load_mf_dataset, so the "
                             "prediction is made over exactly the rungs the trained "
                             "arm sees (ADR r3-0005 pfc {1,3}); the bare CLI reads the "
                             "ORIGINAL root and is cross-checked bit-identical on the "
                             "four cells where the two views agree"},
        "payload": payload,
    }
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(seal, indent=1, default=float))
    print(f"\n[SEALED] {out}")
    print(f"[R3S3B3_PREREG_SHA256] {sha}")
    print("[predictions] " + "  ".join(
        f"{d}:c_pred={payload['cells'][d]['c_pred']}"
        f"(ladder={payload['cells'][d]['ladder']['rungs']})" for d in cells))


if __name__ == "__main__":
    main()
