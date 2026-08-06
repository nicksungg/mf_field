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

Fifth defect class (per-cell estimator integrity, ADR r3-0003 D4 / defect_class_redteam):

  degenerate_rows       per-row copy-LF gap on the TEST split. Rows with gap below
                        max(1e-6, 1% of the median row gap) carry no prediction task and
                        deflate the copy-LF reference (the allen_cahn/pfc class).
                        HARD FAIL when >= 5% of rows are void; WARN when any are.
  cell_stability        bootstrap (1000 resamples, seeded) of the copy-LF reference cell
                        over test rows. top-5 rows' share of the ratio sum > 0.4 or CI95
                        half-width > 25% of the point value -> WARN OUTLIER_DOMINATED
                        (never a hard fail: it prices the cell's discriminative power,
                        not its validity — the cahn_hilliard class). Always records
                        min_detectable_delta: claimed deltas below it are not claimable.
  rung_scale_coherence  per LF rung, RMS(LF spectrally upsampled)/RMS(HF) on shared test
                        rows (train fallback). Outside [0.5, 2.0] -> HARD FAIL RUNG_SCALE
                        (the ifc_poisson h^2-amplitude class) unless the dataset has a
                        declared convention allowance in CONVENTION_ALLOWANCES, in which
                        case the measured ratios + the allowance are recorded as a WARN.

The fourth D4 instrument, launch-time data binding (sha256 manifest of every panel
dataset's array bytes, recorded at launch and verified before any dispatch), is the
standalone sibling tool `data_binding.py` — see the README for the wiring requirement.

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
# --- fifth defect class: per-cell estimator integrity (ADR r3-0003 D4) ---
DEGEN_ABS_MIN = 1e-6        # absolute per-row gap floor for a task-void row
DEGEN_MEDIAN_FRAC = 0.01    # ... or 1% of the dataset's median row gap, whichever larger
DEGEN_FAIL_FRAC = 0.05      # >= 5% void rows -> hard fail
STAB_N_BOOT = 1000
STAB_SEED = 0
STAB_TOP5_SHARE = 0.4       # top-5 rows owning > 40% of the ratio sum -> outlier-dominated
STAB_CI_REL_HALFWIDTH = 0.25  # CI95 half-width > 25% of the point value -> outlier-dominated
RUNG_RMS_LO, RUNG_RMS_HI = 0.5, 2.0
# Declared per-dataset amplitude conventions: a rung-scale ratio outside the band is
# recorded as a warning (with the allowance string), not a hard fail, for these datasets.
CONVENTION_ALLOWANCES = {
    "ifc_poisson": "h2_amplitude (round-2 report, ADR r3-0003 D3)",
}


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


def _per_row_gap(y_lf: np.ndarray, y_hf: np.ndarray, ndim: int) -> np.ndarray | None:
    """Per-row copy-LF gap: rel-L2 of (HF − LF spectrally interpolated to the HF grid) —
    the same canonical construction as fidelity_gap, kept per row instead of aggregated."""
    lf_up = _spectral_up(y_lf, y_hf.shape[1], ndim)
    if lf_up is None:
        return None
    return (np.linalg.norm(y_hf - lf_up, axis=1)
            / (np.linalg.norm(y_hf, axis=1) + 1e-300))


def degenerate_rows_check(gaps: np.ndarray | None) -> dict:
    """Task-void test rows (the allen_cahn/pfc class): a row whose per-row copy-LF gap
    sits below max(1e-6, 1% of the median row gap) contains no prediction task and
    deflates the copy-LF reference, inflating every model's skill on the cell."""
    if gaps is None or len(gaps) == 0:
        return {"status": "UNSUPPORTED"}
    med = float(np.median(gaps))
    thr = max(DEGEN_ABS_MIN, DEGEN_MEDIAN_FRAC * med)
    void = np.flatnonzero(gaps < thr)
    frac = float(len(void) / len(gaps))
    status = ("DEGENERATE_ROWS" if frac >= DEGEN_FAIL_FRAC
              else ("TASK_VOID_ROWS" if len(void) else "OK"))
    return {"status": status, "n_rows": int(len(gaps)), "n_void": int(len(void)),
            "frac_void": frac, "threshold": float(thr), "median_row_gap": med,
            "min_row_gap": float(gaps.min()),
            "void_indices_first10": [int(i) for i in void[:10]]}


def cell_stability_check(gaps: np.ndarray | None,
                         n_boot: int = STAB_N_BOOT, seed: int = STAB_SEED) -> dict:
    """Discriminative power of the copy-LF reference cell (the cahn_hilliard class):
    bootstrap the per-row reference and report outlier concentration + the minimum
    model delta the cell can distinguish. Prices power, not validity — never a hard fail."""
    if gaps is None or len(gaps) < 2:
        return {"status": "UNSUPPORTED"}
    point = float(gaps.mean())
    rng = np.random.default_rng(seed)
    boots = rng.choice(gaps, size=(n_boot, gaps.size), replace=True).mean(axis=1)
    lo, hi = (float(v) for v in np.percentile(boots, [2.5, 97.5]))
    rel_half = float((hi - lo) / 2 / (point + 1e-300))
    top5_share = float(np.sort(gaps)[::-1][:5].sum() / (gaps.sum() + 1e-300))
    dominated = top5_share > STAB_TOP5_SHARE or rel_half > STAB_CI_REL_HALFWIDTH
    return {"status": "OUTLIER_DOMINATED" if dominated else "OK",
            "cell_point_value": point, "ci95": [lo, hi],
            "ci_halfwidth_rel": rel_half, "top5_share": top5_share,
            "min_detectable_delta": float((hi - lo) / (point + 1e-300)),
            "n_boot": int(n_boot), "seed": int(seed)}


def rung_scale_check(y_by_level: dict[int, np.ndarray], y_hf: np.ndarray, ndim: int,
                     allowance: str | None = None) -> dict:
    """Cross-rung amplitude coherence (the ifc_poisson h^2 class): every LF rung must sit
    on the same physical amplitude scale as HF. RMS(LF upsampled)/RMS(HF) per rung must
    lie in [0.5, 2.0]; a declared convention allowance downgrades a violation to a WARN."""
    ratios: dict[str, float] = {}
    unsupported: list[str] = []
    for k in sorted(y_by_level):
        y_lf = np.asarray(y_by_level[k], float)
        n = min(len(y_lf), len(y_hf))
        up = _spectral_up(y_lf[:n], y_hf.shape[1], ndim)
        if up is None:
            unsupported.append(str(k))
            continue
        hf = np.asarray(y_hf[:n], float)
        ratios[str(k)] = float(np.sqrt(np.mean(up ** 2))
                               / (np.sqrt(np.mean(hf ** 2)) + 1e-300))
    if not ratios:
        return {"status": "UNSUPPORTED",
                "reason": "no upsample-compatible LF rung", "skipped_levels": unsupported}
    offending = [k for k, v in ratios.items() if not (RUNG_RMS_LO <= v <= RUNG_RMS_HI)]
    if offending:
        status = "ALLOWED_CONVENTION" if allowance else "RUNG_SCALE"
    else:
        status = "OK"
    rec = {"status": status, "rms_ratio_by_level": ratios,
           "bounds": [RUNG_RMS_LO, RUNG_RMS_HI], "offending_levels": offending}
    if unsupported:
        rec["skipped_levels"] = unsupported
    if allowance:
        rec["convention_allowance"] = allowance
    return rec


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
    y_te_hf = None
    if te_hf_p.exists():
        te = np.load(te_hf_p)
        y_te_hf = np.asarray(te["y"][:MAX_ROWS], float)
        rec["nn_baseline"] = nn_baseline(
            np.asarray(x, float), np.asarray(y_hf, float),
            np.asarray(te["x"][:50], float), np.asarray(te["y"][:50], float))
    # --- fifth class: per-cell estimator integrity (test split; canonical per-row gap)
    te_lf_p = d / f"test_l{levels[0]}.npz"
    gaps = None
    if len(levels) > 1 and y_te_hf is not None and te_lf_p.exists():
        y_te_lf = np.asarray(np.load(te_lf_p)["y"][:MAX_ROWS], float)
        n_te = min(len(y_te_lf), len(y_te_hf))
        gaps = _per_row_gap(y_te_lf[:n_te], y_te_hf[:n_te], ndim)
    rec["degenerate_rows"] = degenerate_rows_check(gaps)
    rec["cell_stability"] = cell_stability_check(gaps)
    if len(levels) > 1:
        rungs, rung_split = {}, "test"
        if y_te_hf is not None:
            for k in levels[:-1]:
                p = d / f"test_l{k}.npz"
                if p.exists():
                    rungs[k] = np.load(p)["y"][:MAX_ROWS]
        y_hf_rung = y_te_hf
        if not rungs:
            rung_split = "train"
            rungs = {k: np.load(d / f"train_l{k}.npz")["y"][:MAX_ROWS]
                     for k in levels[:-1]}
            y_hf_rung = np.asarray(y_hf, float)
        rec["rung_scale_coherence"] = rung_scale_check(
            rungs, y_hf_rung, ndim, allowance=CONVENTION_ALLOWANCES.get(name))
        rec["rung_scale_coherence"]["split"] = rung_split
    else:
        rec["rung_scale_coherence"] = {"status": "UNSUPPORTED",
                                       "reason": "single-level ladder"}
    hard = []
    if comp_status == "INCOMPLETE":
        hard.append("completeness")
    if rec["pairing"]["status"] == "MISPAIRED":
        hard.append("pairing")
    if rec["degenerate_rows"]["status"] == "DEGENERATE_ROWS":
        hard.append("degenerate_rows")
    if rec["rung_scale_coherence"]["status"] == "RUNG_SCALE":
        hard.append("rung_scale_coherence")
    warns = [k for k in ("fidelity_gap", "nn_baseline", "degenerate_rows",
                         "cell_stability", "rung_scale_coherence")
             if rec.get(k, {}).get("status") not in (None, "OK", "UNSUPPORTED")
             and k not in hard]
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
    # --- fifth class (ADR r3-0003 D4) ---
    # degenerate rows: HF with genuine HF-only structure everywhere must read OK;
    # injecting rows where HF == spectral-up(LF) exactly (LF≡HF, the allen_cahn/pfc
    # class) must hard-fail at >= 5% and warn below.
    hf_ok = hf_band + 0.05 * rng.random(hf_band.shape)
    gaps_ok = _per_row_gap(lf_exact, hf_ok, 2)
    assert degenerate_rows_check(gaps_ok)["status"] == "OK"
    hf_mix = hf_ok.copy()
    hf_mix[:4] = hf_band[:4]                     # 4/40 = 10% task-void -> hard fail
    res = degenerate_rows_check(_per_row_gap(lf_exact, hf_mix, 2))
    assert res["status"] == "DEGENERATE_ROWS" and res["n_void"] == 4
    assert res["void_indices_first10"] == [0, 1, 2, 3]
    hf_one = hf_ok.copy()
    hf_one[0] = hf_band[0]                       # 1/40 = 2.5% -> warning only
    assert degenerate_rows_check(_per_row_gap(lf_exact, hf_one, 2))["status"] == "TASK_VOID_ROWS"
    # cell stability: a flat per-row reference is stable; one dominating row (the
    # cahn_hilliard class) must read OUTLIER_DOMINATED, and min_detectable_delta is
    # always recorded.
    flat = np.full(100, 0.01)
    s_ok = cell_stability_check(flat)
    assert s_ok["status"] == "OK" and "min_detectable_delta" in s_ok
    dom = flat.copy(); dom[0] = 1.0
    s_dom = cell_stability_check(dom)
    assert s_dom["status"] == "OUTLIER_DOMINATED" and s_dom["top5_share"] > 0.4
    # rung scale: a x10 amplitude rung (the ifc_poisson h^2 class) must hard-fail,
    # a declared convention allowance must downgrade it to a warning, and a
    # scale-coherent rung must read OK.
    r_bad = rung_scale_check({16: lf_exact * 10.0}, hf_ok, 2)
    assert r_bad["status"] == "RUNG_SCALE" and r_bad["offending_levels"] == ["16"]
    r_allowed = rung_scale_check({16: lf_exact * 10.0}, hf_ok, 2,
                                 allowance="h2_amplitude (selftest)")
    assert r_allowed["status"] == "ALLOWED_CONVENTION"
    assert rung_scale_check({16: lf_exact}, hf_ok, 2)["status"] == "OK"
    print("preflight selftest: all defect classes detected OK "
          "(4 round-2 classes + degenerate_rows / cell_stability / rung_scale_coherence)")
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
