#!/usr/bin/env python3
"""Pre-launch integrity certificates for an autoresearch round (training-free, ~seconds/dataset).

Round 2 found four instrument/panel defects DURING the round, when the frozen panel could
no longer respond: incomplete condition vectors (pfc/fisher_kpp/allen_cahn), a trivially
re-solvable dataset (helmholtz), an unpaired fidelity ladder (ifc_poisson), and a dataset
with no fidelity gap (pfc). Every one of them is detectable from the data alone in under a
minute. This runs those detections BEFORE batch 1, so a defective panel pauses the round
at launch instead of contaminating it.

Checks per dataset (factory npz layout: <root>/<name>/{train,test}_l{k}.npz + meta.json):

  completeness   nearest-pair witness (+ the meta.json condition_completeness record when
                 the generator gate wrote one). HARD FAIL when INCOMPLETE and the dataset
                 does not declare stochastic_map semantics.
  pairing        LF row i must correspond to HF row i: best-match accuracy between LF rows
                 and block-averaged HF rows. HARD FAIL below 0.9 (the ifc defect class).
  fidelity_gap   median rel-L2 between LF and block-averaged HF. WARN when < 0.02 (LF==HF:
                 nothing for MF to add — the pfc class) or > 0.8 (LF uninformative).
  nn_baseline    1-nearest-neighbour-in-condition-space prediction of the test HF field.
                 WARN when its median rel-L2 < 0.05 (the helmholtz triviality class: any
                 model must beat this training-free floor for a claim to mean anything).

Exit 0 = launch may proceed. Exit 1 = HARD FAIL present (set a HOLD, fix or waive).
Waivers: --waive <dataset>:<check> (recorded in the report; use for panel members kept
deliberately, e.g. a declared stochastic-map dataset).

Usage:
  python preflight.py --root <benchmark_root> --datasets a b c --out preflight_report.json
  python preflight.py --selftest        # synthetic-defect self-check of the instruments
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

PAIRING_MIN_FRAC = 0.5
# Fidelity gap uses the repo's CANONICAL residual: LF spectrally interpolated up to the
# HF grid (a block-average comparison has an operator-mismatch floor of ~0.02-0.05 that
# reads as a fake gap — it hid fisher_kpp's true 4e-5 gap on 2026-08-03).
GAP_NO_GAP = 1e-3
GAP_SATURATED = 0.8
NN_TRIVIAL = 0.05
WITNESS_DIST_MAX = 0.5
WITNESS_REL_MIN = 0.1
# Full production row count: ADR r2-0003's allen_cahn witness pair only appears at the
# full 400 rows (rel diff 0.118 at distance 0.0511) — a smaller subsample misses it.
MAX_ROWS = 400


# ---------------------------------------------------------------- instruments
def nearest_pair_witness(x: np.ndarray, y: np.ndarray) -> dict:
    mu, sd = x.mean(0), x.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    z = (x - mu) / sd
    d2 = ((z[:, None, :] - z[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(d2, np.inf)
    i, j = np.unravel_index(np.argmin(d2), d2.shape)
    scale = 0.5 * (np.linalg.norm(y[i]) + np.linalg.norm(y[j]))
    return {"closest_pair": [int(i), int(j)],
            "standardized_condition_distance": float(np.sqrt(d2[i, j])),
            "relative_field_difference": float(np.linalg.norm(y[i] - y[j]) / (scale + 1e-300))}


def _block_avg_to(y_hf: np.ndarray, n_lf: int, ndim: int) -> np.ndarray | None:
    """Block-average flattened HF rows down to the LF cell count (pairing only —
    fine as a projection for row matching, NOT as a fidelity measure)."""
    n_hf = y_hf.shape[1]
    if ndim == 2:
        r_hf, r_lf = int(round(np.sqrt(n_hf))), int(round(np.sqrt(n_lf)))
        if r_hf * r_hf != n_hf or r_lf * r_lf != n_lf or r_hf % r_lf:
            return None
        s = r_hf // r_lf
        f = y_hf.reshape(-1, r_lf, s, r_lf, s)
        return f.mean(axis=(2, 4)).reshape(-1, n_lf)
    if n_hf % n_lf:
        return None
    s = n_hf // n_lf
    return y_hf.reshape(-1, n_lf, s).mean(axis=2)


def _spectral_up(y_lf: np.ndarray, n_hf: int, ndim: int) -> np.ndarray | None:
    """Spectrally interpolate flattened LF rows up to the HF cell count (the repo's
    canonical alignment for residuals: zero-pad the Fourier spectrum)."""
    n_lf = y_lf.shape[1]
    if ndim == 2:
        r_lf, r_hf = int(round(np.sqrt(n_lf))), int(round(np.sqrt(n_hf)))
        if r_lf * r_lf != n_lf or r_hf * r_hf != n_hf or r_hf % r_lf:
            return None
        out = np.empty((len(y_lf), n_hf))
        for i, row in enumerate(y_lf):
            F = np.fft.fftshift(np.fft.fft2(row.reshape(r_lf, r_lf)))
            pad = (r_hf - r_lf) // 2
            Fp = np.pad(F, pad)
            out[i] = np.real(np.fft.ifft2(np.fft.ifftshift(Fp))).ravel() * (r_hf / r_lf) ** 2
        return out
    if n_hf % n_lf:
        return None
    out = np.empty((len(y_lf), n_hf))
    for i, row in enumerate(y_lf):
        F = np.fft.fftshift(np.fft.fft(row))
        pad = (n_hf - n_lf) // 2
        Fp = np.pad(F, pad)
        out[i] = np.real(np.fft.ifft(np.fft.ifftshift(Fp))) * (n_hf / n_lf)
    return out


def pairing_check(y_lf: np.ndarray, y_hf: np.ndarray, ndim: int) -> dict:
    """Row i of LF must correspond to row i of HF (the ifc defect class).

    Criterion: each row's diagonal cosine must sit above the 95th percentile of that
    row's off-diagonal cosines. Plain argmax accuracy is too strict when a dataset's
    samples are statistical look-alikes (CH labyrinths, Helmholtz bumps cross-match
    siblings at cosine ~0.98 while their own pair sits at 0.99); a genuinely shuffled
    ladder puts the diagonal INSIDE the off-diagonal distribution, which this catches.
    """
    hf_down = _block_avg_to(y_hf, y_lf.shape[1], ndim)
    if hf_down is None:
        return {"status": "UNSUPPORTED", "reason": "non-dyadic or non-square ladder"}
    a = y_lf - y_lf.mean(axis=1, keepdims=True)
    b = hf_down - hf_down.mean(axis=1, keepdims=True)
    a = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-300)
    b = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-300)
    sim = a @ b.T
    n = len(sim)
    diag = np.diag(sim).copy()
    off = sim.copy()
    np.fill_diagonal(off, -np.inf)
    p95 = np.nanpercentile(np.where(np.isfinite(off), off, np.nan), 95, axis=1)
    frac = float((diag > p95).mean())
    acc = float((sim.argmax(axis=1) == np.arange(n)).mean())
    return {"status": "OK" if frac >= PAIRING_MIN_FRAC else "MISPAIRED",
            "frac_diag_above_p95_offdiag": frac,
            "row_match_accuracy": acc,
            "mean_diag_cosine": float(diag.mean())}


def fidelity_gap(y_lf: np.ndarray, y_hf: np.ndarray, ndim: int) -> dict:
    """Canonical fidelity gap: rel-L2 of (HF − LF spectrally interpolated to HF grid)."""
    lf_up = _spectral_up(y_lf, y_hf.shape[1], ndim)
    if lf_up is None:
        return {"status": "UNSUPPORTED"}
    rel = (np.linalg.norm(y_hf - lf_up, axis=1)
           / (np.linalg.norm(y_hf, axis=1) + 1e-300))
    med = float(np.median(rel))
    status = "NO_GAP" if med < GAP_NO_GAP else ("SATURATED" if med > GAP_SATURATED else "OK")
    return {"status": status, "median_rel_l2": med}


def nn_baseline(x_tr, y_tr, x_te, y_te) -> dict:
    mu, sd = x_tr.mean(0), x_tr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    z_tr, z_te = (x_tr - mu) / sd, (x_te - mu) / sd
    d2 = ((z_te[:, None, :] - z_tr[None, :, :]) ** 2).sum(-1)
    nn = d2.argmin(axis=1)
    rel = (np.linalg.norm(y_te - y_tr[nn], axis=1)
           / (np.linalg.norm(y_te, axis=1) + 1e-300))
    med = float(np.median(rel))
    return {"status": "TRIVIAL_NN" if med < NN_TRIVIAL else "OK",
            "median_rel_l2": med}


# ---------------------------------------------------------------- driver
def check_dataset(root: Path, name: str) -> dict:
    d = root / name
    meta = json.load(open(d / "meta.json")) if (d / "meta.json").exists() else {}
    levels = sorted(int(p.stem.split("_l")[1]) for p in d.glob("train_l*.npz"))
    if not levels:
        return {"dataset": name, "status": "NO_DATA"}
    tr_lf = np.load(d / f"train_l{levels[0]}.npz")
    tr_hf = np.load(d / f"train_l{levels[-1]}.npz")
    te_hf_p = d / f"test_l{levels[-1]}.npz"
    ndim = int(meta.get("ndim", 2))
    x, y_lf, y_hf = (tr_lf["x"][:MAX_ROWS], tr_lf["y"][:MAX_ROWS],
                     tr_hf["y"][:MAX_ROWS])

    rec = {"dataset": name, "levels": levels, "n_rows_checked": int(len(x))}
    w = nearest_pair_witness(np.asarray(x, float), np.asarray(y_hf, float))
    declared = bool(meta.get("stochastic_map")) or "stochastic_map_semantics" in meta
    gate = meta.get("condition_completeness", {})
    incomplete = (w["relative_field_difference"] > WITNESS_REL_MIN
                  and w["standardized_condition_distance"] < WITNESS_DIST_MAX)
    if gate.get("verdict") == "COMPLETE" or str(gate.get("verdict", "")).startswith("COMPLETE"):
        comp_status = "OK"
    elif declared:
        comp_status = "STOCHASTIC_DECLARED"
    elif incomplete:
        comp_status = "INCOMPLETE"
    else:
        comp_status = "UNDECIDED" if not gate else str(gate.get("verdict"))
    rec["completeness"] = {"status": comp_status, "witness": w,
                           "meta_gate_verdict": gate.get("verdict")}
    rec["pairing"] = pairing_check(np.asarray(y_lf, float), np.asarray(y_hf, float), ndim)
    rec["fidelity_gap"] = fidelity_gap(np.asarray(y_lf, float), np.asarray(y_hf, float), ndim)
    if te_hf_p.exists():
        te = np.load(te_hf_p)
        rec["nn_baseline"] = nn_baseline(
            np.asarray(x, float), np.asarray(y_hf, float),
            np.asarray(te["x"][:50], float), np.asarray(te["y"][:50], float))
    hard = []
    if comp_status == "INCOMPLETE":
        hard.append("completeness")
    if rec["pairing"]["status"] == "MISPAIRED":
        hard.append("pairing")
    warns = [k for k in ("fidelity_gap", "nn_baseline")
             if rec.get(k, {}).get("status") not in (None, "OK", "UNSUPPORTED")]
    rec["hard_fails"] = hard
    rec["warnings"] = warns
    rec["status"] = "FAIL" if hard else ("WARN" if warns else "PASS")
    return rec


def selftest() -> int:
    """The instruments must detect synthetic versions of every round-2 defect class."""
    rng = np.random.default_rng(0)
    n, d, cells = 40, 3, 256
    x = rng.random((n, d))
    y = rng.random((n, cells))
    # incomplete: two near-identical conds, different fields
    x2 = x.copy(); x2[1] = x2[0] + 1e-9
    w = nearest_pair_witness(x2, y)
    assert w["standardized_condition_distance"] < 1e-6 and w["relative_field_difference"] > 0.1
    # mispaired ladder: LF rows shuffled against HF
    y_hf = rng.random((n, 1024))
    y_lf = _block_avg_to(y_hf, cells, 2) + 0.01 * rng.random((n, cells))
    perm = rng.permutation(n)
    assert pairing_check(y_lf, y_hf, 2)["status"] == "OK"
    assert pairing_check(y_lf[perm], y_hf, 2)["status"] == "MISPAIRED"
    # look-alike samples (shared background dominates): paired must still read OK,
    # shuffled must still read MISPAIRED
    bg = rng.random(1024)
    y_hf_alike = bg[None, :] + 0.05 * rng.random((n, 1024))
    y_lf_alike = _block_avg_to(y_hf_alike, cells, 2) + 0.001 * rng.random((n, cells))
    assert pairing_check(y_lf_alike, y_hf_alike, 2)["status"] == "OK"
    assert pairing_check(y_lf_alike[perm], y_hf_alike, 2)["status"] == "MISPAIRED"
    # no fidelity gap: the same band-limited function sampled on both grids — the
    # canonical measure (LF spectrally interpolated up) sees machine zero; adding
    # genuine HF-only structure (5%) must read OK
    grids = {}
    for r in (16, 32):
        xs = 2 * np.pi * np.arange(r) / r
        grids[r] = np.meshgrid(xs, xs, indexing="ij")
    hf_band, lf_exact = [], []
    for _ in range(n):
        c = rng.uniform(-1, 1, 4)
        row = {}
        for r, (X, Y) in grids.items():
            row[r] = (c[0] * np.cos(X) + c[1] * np.sin(2 * X + Y)
                      + c[2] * np.cos(3 * Y) + c[3] * np.sin(X + 2 * Y)).ravel()
        hf_band.append(row[32])
        lf_exact.append(row[16])
    hf_band, lf_exact = np.stack(hf_band), np.stack(lf_exact)
    assert fidelity_gap(lf_exact, hf_band, 2)["status"] == "NO_GAP"
    assert fidelity_gap(lf_exact, hf_band + 0.05 * rng.random(hf_band.shape), 2)["status"] == "OK"
    # NN-trivial: test conds equal train conds -> NN reproduces the field
    assert nn_baseline(x, y, x[:10], y[:10])["status"] == "TRIVIAL_NN"
    print("preflight selftest: all four defect classes detected OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path)
    ap.add_argument("--datasets", nargs="+", default=None,
                    help="dataset dir names under root (default: every dir with meta.json)")
    ap.add_argument("--out", type=Path, default=Path("preflight_report.json"))
    ap.add_argument("--waive", nargs="*", action="extend", default=[],
                    metavar="DATASET:CHECK", help="waive a hard fail (recorded)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.root:
        ap.error("--root is required (or --selftest)")
    names = args.datasets or sorted(p.parent.name for p in args.root.glob("*/meta.json"))
    waived = {tuple(wv.split(":", 1)) for wv in args.waive}
    report = {"root": str(args.root), "waivers": sorted(map(list, waived)), "datasets": {}}
    exit_code = 0
    for name in names:
        rec = check_dataset(args.root, name)
        rec["hard_fails"] = [c for c in rec.get("hard_fails", [])
                             if (name, c) not in waived]
        if rec.get("status") == "FAIL" and not rec["hard_fails"]:
            rec["status"] = "WAIVED"
        report["datasets"][name] = rec
        if rec.get("status") == "FAIL":
            exit_code = 1
        flags = ",".join(rec.get("hard_fails", []) + rec.get("warnings", []))
        print(f"{name:28s} {rec.get('status', '?'):7s} {flags}")
    report["verdict"] = "FAIL" if exit_code else "PASS"
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"\npreflight verdict: {report['verdict']}  -> {args.out}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
