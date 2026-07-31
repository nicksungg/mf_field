#!/usr/bin/env python
"""Correction anatomy — WHAT is a residual/corrector branch actually adding?

Provenance: s4_hybrid_routing-B1 mechanism analysis, turn 2
(`worktrees/s4_hybrid_routing/B1/scratchpad/correction_anatomy.py`, findings
F6-F9 in card `experiment_cards/s4_hybrid_routing/batch_1/B1.json` part 6).

What it measures
----------------
Given a model decomposed as `pred = base + alpha * correction` (any residual
hybrid, corrector, test-time refiner, boosting stage), and the round's own
copy-LF baseline, it decides which of three things the correction is:

  1. a re-derivation of the COARSE SOLVE the model already receives
     -> correction is collinear with `copylf - base`
  2. genuine FIDELITY-GAP information copy-LF does not have
     -> correction is collinear with `hf - copylf`
  3. neither (noise / collapsed branch)
     -> both cosines ~ 0 and the RMS is tiny

Blocks emitted (everything scored with `round1/eval/nrmse.py`, target and
copy-LF from `round1/eval/panel_data.py`):

  `cosine_correction_vs`     per-sample cosine with `hf-base` (the trained
                             target), `copylf-base`, `hf-copylf`
  `correction_in_span_...`   per-sample least squares of the correction on
                             span{copylf-base, hf-copylf}: the coefficient on the
                             LF direction, the coefficient on the gap direction,
                             and the R^2 of that 2-D fit
  `nrmse_base_plus_a_times_lfdir`  the TRIVIAL reference the correction has to
                             beat: `base + a*(copylf - base)` for a in 0.25..1
                             (a = 1 is copy-LF itself)
  `nrmse_all` / `skill_all`  copy-LF, base, base+alpha*correction, and two
                             training-free rungs computed with
                             `tools/lf_conditioned_headroom.py`'s own functions
                             (`L5` kNN-in-LF residual, `L3` kNN-in-X residual) so
                             the numbers are directly comparable to that card
  `mean_rel_l2_<regime>`     per-regime means over a spatially-CONSTANT /
                             PATTERNED split of the test set (s2_beyond_copy-B1
                             F1's bimodality; degenerate on unimodal datasets)

Reading the output
------------------
* `cosine(corr, copylf-base) >= cosine(corr, hf-base)` and
  `cosine(corr, hf-copylf) ~ 0`  ->  the correction is case 1. Its CEILING is
  skill 1.0, so no amount of tuning it will clear the copy-LF bar; compare
  `nrmse_base_plus_a_times_lfdir` and note that a single scalar blend may already
  match it. The lever is to feed the LF field to the network more directly, not
  to grow the corrector.
* `coef_hf_minus_copylf_median` materially non-zero -> case 2, the branch really
  is adding fidelity information; that is the case worth scaling.
* `alpha * coef_copylf_minus_base_median` is the EFFECTIVE FRACTION of the way
  from the base to copy-LF that the gated correction travels.

Invocation
----------
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/correction_anatomy.py --dataset sharp__phase_field_crystal_2d \
      --npz /path/to/fields.npz --base_key base_te --corr_key corr_te \
      --corr_scale 2.8695719242095947 --alpha 0.25085851550102234 \
      --out /path/to/anatomy.json [--sig 16] [--k 5]

`--npz` must hold two `(N, n_cells_hf)` arrays on the HF grid: the base
prediction and the RAW correction. `--corr_scale` multiplies the correction (use
it when the family stores the correction in scaler units, as
`fno_transolver_seq` does with `scaler_r`); `--alpha` is the gate value actually
applied at prediction time. Fewer rows than the test split is fine -- the first
N test samples are used.

Cost: pure numpy, seconds per dataset. No GPU, no SLURM, no training.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _round_root() -> Path:
    here = Path(__file__).resolve()
    for anc in here.parents:
        if (anc / "eval" / "nrmse.py").exists() and (anc / "tools").exists():
            return anc
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True, cwd=here.parent)
    return Path(out.stdout.strip()) / "mffp_autoresearch" / "round1"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--npz", required=True)
    ap.add_argument("--base_key", default="base_te")
    ap.add_argument("--corr_key", default="corr_te")
    ap.add_argument("--corr_scale", type=float, default=1.0)
    ap.add_argument("--alpha", type=float, required=True)
    ap.add_argument("--sig", type=int, default=16)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--round_root", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rr = Path(args.round_root).resolve() if args.round_root else _round_root()
    sys.path.insert(0, str(rr / "eval"))
    from nrmse import nrmse, NRMSE_DEF_HASH  # noqa
    import panel_data as PD  # noqa
    HR = _load_module(rr / "tools" / "lf_conditioned_headroom.py", "lf_conditioned_headroom")

    z = np.load(args.npz)
    base = np.asarray(z[args.base_key], dtype=np.float64)
    corr = np.asarray(z[args.corr_key], dtype=np.float64) * args.corr_scale
    if corr.shape != base.shape:
        raise ValueError(f"base {base.shape} and correction {corr.shape} disagree")
    n = base.shape[0]
    alpha = args.alpha

    tr, te = PD.load_split(args.dataset, "train"), PD.load_split(args.dataset, "test")
    if not te["lf_fids"]:
        raise ValueError(f"{args.dataset}: test split ships no LF; copy-LF undefined")
    y_tr = np.asarray(tr["field_by_fid"][tr["hf_fid"]], dtype=np.float64)
    y_te = np.asarray(te["field_by_fid"][te["hf_fid"]], dtype=np.float64)[:n]
    x_tr = np.asarray(tr["cond_by_fid"][tr["hf_fid"]], dtype=np.float64)
    x_te = np.asarray(te["cond_by_fid"][te["hf_fid"]], dtype=np.float64)[:n]
    lf_tr, lf_te = HR.panel_data.copylf_prediction(tr), HR.panel_data.copylf_prediction(te)[:n]
    grid = HR.resolve_grid_for(args.dataset, te["n_cells_by_fid"][te["hf_fid"]])
    if base.shape[1] != y_te.shape[1]:
        raise ValueError(f"fields have {base.shape[1]} cells, HF grid has {y_te.shape[1]}")
    r_tr = y_tr - lf_tr

    # training-free comparison rungs, via the s2 tool's own functions
    zs_tr, zs_te = HR._zscore(HR.signature(lf_tr, grid, args.sig),
                              HR.signature(lf_te, grid, args.sig))
    ix_lf, _ = HR._zorder(zs_te, zs_tr, [args.k])
    L5 = lf_te + r_tr[ix_lf[args.k]].mean(axis=1)
    zx_tr, zx_te = HR._zscore(x_tr, x_te)
    ix_x, _ = HR._zorder(zx_te, zx_tr, [args.k])
    L3 = lf_te + r_tr[ix_x[args.k]].mean(axis=1)

    preds = {"copylf": lf_te, "base": base, f"base_plus_alpha{alpha:.4f}_corr": base + alpha * corr,
             f"L5_knnLF{args.k}": L5, f"L3_knnX{args.k}": L3}
    copylf_n = nrmse(lf_te, y_te)

    def ps(p):
        return np.linalg.norm(p - y_te, axis=1) / np.linalg.norm(y_te, axis=1)

    hf_std = y_te.std(axis=1)
    patterned = hf_std > max(1e-3 * float(np.abs(y_te).max()), 1e-8)
    resolved = ps(lf_te) < 1e-3

    rec = {"dataset": args.dataset, "n_test_used": int(n), "grid": [int(g) for g in grid],
           "npz": str(args.npz), "base_key": args.base_key, "corr_key": args.corr_key,
           "corr_scale": args.corr_scale, "alpha": alpha,
           "nrmse_def_hash": NRMSE_DEF_HASH, "copylf_nrmse": copylf_n,
           "regime_counts": {"patterned_by_hf_std": int(patterned.sum()),
                             "constant_by_hf_std": int((~patterned).sum()),
                             "copylf_resolved_lt_1e-3": int(resolved.sum())},
           "hf_std_quantiles": [float(q) for q in np.percentile(hf_std, [0, 10, 50, 90, 100])],
           "nrmse_all": {k: nrmse(v, y_te) for k, v in preds.items()}}
    rec["skill_all"] = {k: v / copylf_n for k, v in rec["nrmse_all"].items()}
    for label, mask in (("patterned", patterned), ("constant", ~patterned),
                        ("copylf_unresolved", ~resolved), ("copylf_resolved", resolved)):
        if mask.sum():
            blk = {k: float(np.mean(ps(v)[mask])) for k, v in preds.items()}
            blk["n"] = int(mask.sum())
            rec[f"mean_rel_l2_{label}"] = blk

    resid, d_lf, d_gap = y_te - base, lf_te - base, y_te - lf_te

    def cos(a, b):
        return (a * b).sum(1) / np.maximum(np.linalg.norm(a, axis=1)
                                           * np.linalg.norm(b, axis=1), 1e-300)

    rec["cosine_correction_vs"] = {
        "hf_minus_base_TRAINED_TARGET": [float(np.mean(cos(corr, resid))),
                                         float(np.median(cos(corr, resid)))],
        "copylf_minus_base_REDERIVES_COPYLF": [float(np.mean(cos(corr, d_lf))),
                                               float(np.median(cos(corr, d_lf)))],
        "hf_minus_copylf_FIDELITY_GAP": [float(np.mean(cos(corr, d_gap))),
                                         float(np.median(cos(corr, d_gap)))],
        "note": "[mean, median] over test samples of the per-sample cosine"}

    coefs, r2 = np.zeros((n, 2)), np.zeros(n)
    for i in range(n):
        A = np.stack([d_lf[i], d_gap[i]], axis=1)
        sol, *_ = np.linalg.lstsq(A, corr[i], rcond=None)
        coefs[i] = sol
        r2[i] = 1.0 - float(((corr[i] - A @ sol) ** 2).sum()
                            / max(float((corr[i] ** 2).sum()), 1e-300))
    rec["correction_in_span_lfdir_gapdir"] = {
        "coef_copylf_minus_base_mean": float(coefs[:, 0].mean()),
        "coef_copylf_minus_base_median": float(np.median(coefs[:, 0])),
        "coef_hf_minus_copylf_mean": float(coefs[:, 1].mean()),
        "coef_hf_minus_copylf_median": float(np.median(coefs[:, 1])),
        "r2_mean": float(r2.mean()), "r2_median": float(np.median(r2)),
        "effective_fraction_toward_copylf": float(alpha * np.median(coefs[:, 0])),
        "note": "correction ~= c0*(copylf-base) + c1*(hf-copylf). c0*alpha is how far "
                "toward copy-LF the gated correction actually travels; c1 is the only "
                "part that carries information copy-LF does not already have."}
    rec["nrmse_base_plus_a_times_lfdir"] = {
        f"{a}": nrmse(base + a * d_lf, y_te) for a in (0.25, 0.5, 0.75, 1.0)}
    rec["corr_rms_over_residual_rms"] = float(
        np.sqrt(np.mean(corr ** 2)) / max(np.sqrt(np.mean(resid ** 2)), 1e-300))
    rec["per_sample"] = {k: ps(v).tolist() for k, v in preds.items()}
    rec["per_sample_patterned"] = patterned.tolist()
    rec["per_sample_span_coefs"] = coefs.tolist()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(rec, f, indent=1)
    print(json.dumps({k: v for k, v in rec.items() if not k.startswith("per_sample")}, indent=1))


if __name__ == "__main__":
    main()
