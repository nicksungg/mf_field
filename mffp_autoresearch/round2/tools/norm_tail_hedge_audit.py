#!/usr/bin/env python
"""norm_tail_hedge_audit.py — is this arm's score bought by ABSTAINING on the
samples it cannot fit, and would a per-sample-normalized objective take that
hedge away?

The round scores `nRMSE = mean_i ||p_i - y_i|| / ||y_i||` (round1/eval/nrmse.py).
Write g = ||p||/||y|| and cos = <p,y>/(||p|| ||y||); then

    rel^2 = 1 + g^2 - 2 g cos      =>   rel < 1  IFF  g < 2 cos .

Two consequences this tool measures, neither of which is visible in an nRMSE:

  1. THE ADMISSION RULE. The zero field scores exactly 1 on every sample. On a
     sample whose shape the model cannot get (cos small), SHRINKING the output
     is strictly better than predicting it. A squared-error objective does this
     automatically (regression to the mean); a per-sample-normalized objective
     does not. `frac_g_ge_2cos` is the fraction of samples the arm is scored
     WORSE THAN NOTHING on; `hedge_share_of_score` is how much of the arm's
     nRMSE would vanish under an oracle per-sample rescale (= 1 - mean
     sqrt(1-cos^2) / nRMSE), i.e. how much of the score is amplitude rather
     than shape.

  2. THE LOW-NORM TAIL GATE. A per-sample-normalized loss silently reweights
     the training set by w ~ 1/||y||^2. If (i) the weight concentrates
     (effective sample fraction low / hf_norm_spread >~ 10), (ii) the low-norm
     decile is much harder than the rest, and (iii) the reference (MSE-trained)
     arm SHRINKS amplitude there (`g_ratio_lownorm_over_all` <~ 0.8), then
     normalizing removes the hedge, the tail crosses g >= 2cos and its rel-L2
     goes above 1. Measured cost when all three held (s7_loss-B2,
     sharp__allen_cahn_2d, lambda=1): +1.818 certified floors, 52% of it in 5
     samples. `--floors` prints the denominator-floor counterfactual: what a
     floor on ||y|| does to the weighting, before any training.

Read it as. `gate_verdict = RISK` on the reference arm => do not adopt a
per-sample-normalized objective on this dataset without a denominator floor and
an inference-time amplitude calibration. `hedge_share_of_score` large (> ~0.3)
=> most of the arm's score is the amplitude channel, so any comparison of two
arms on this dataset is mostly a comparison of their gains. `frac_g_ge_2cos`
large => the arm is scored worse than the zero field on that fraction of the
split; quote it next to the nRMSE.

Usage
-----
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/norm_tail_hedge_audit.py \
        --preds mse=<a/preds_test.npz> [rel=<b/preds_test.npz> ...] \
        [--reference-arm mse] [--decile-frac 0.1] [--floors 0.1 0.25 0.5] \
        [--pred-key pred --target-key target] [--out audit.json] [--plot p.png]

With two or more arms it also prints the pairwise gap decomposition (how much
of `arm - reference` is the amplitude channel, and how concentrated the gap is
in the worst samples). Arms must share a test split; the target arrays are
compared and the tool refuses to proceed if they differ.

Provenance: worktrees/s7_loss/B2/scratchpad/reanalysis_turn_{2,3}.py;
card experiment_cards/s7_loss/batch_2/B2.json part 6, findings F6-F11.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROUND, "eval"))
import nrmse as N  # noqa: E402


def _geometry(pred: np.ndarray, target: np.ndarray) -> dict:
    p = np.asarray(pred, np.float64).reshape(pred.shape[0], -1)
    y = np.asarray(target, np.float64).reshape(target.shape[0], -1)
    if p.shape != y.shape:
        raise ValueError(f"pred {p.shape} != target {y.shape}")
    yn = np.linalg.norm(y, axis=1)
    if (yn == 0).any():
        raise ValueError("zero-norm target sample")
    g = np.linalg.norm(p, axis=1) / yn
    alpha = (p * y).sum(1) / yn ** 2
    cos = np.divide(alpha, g, out=np.zeros_like(alpha), where=g > 0)
    rel = np.linalg.norm(p - y, axis=1) / yn
    return {"g": g, "cos": cos, "rel": rel, "yn": yn}


def _weights(yn: np.ndarray, floor_q=None) -> np.ndarray:
    d = np.maximum(yn, np.quantile(yn, floor_q)) if floor_q is not None else yn
    w = 1.0 / d ** 2
    return w / w.sum()


def _conc(w: np.ndarray) -> dict:
    n = len(w)
    return {"top10pct_weight_share_MSE_equivalent_0.10":
            float(np.sort(w)[-max(1, n // 10):].sum()),
            "effective_sample_fraction_1_over_sumw2_over_n":
            float(1.0 / (w ** 2).sum() / n),
            "weight_max_over_median": float(w.max() / np.median(w))}


def audit_arm(pred, target, decile_frac=0.10, floors=(0.10, 0.25, 0.50)) -> dict:
    G = _geometry(pred, target)
    g, cos, rel, yn = G["g"], G["cos"], G["rel"], G["yn"]
    n = len(yn)
    k = max(1, int(round(decile_frac * n)))
    lo = np.argsort(yn)[:k]
    rest = np.setdiff1d(np.arange(n), lo)
    oracle = float(np.mean(np.sqrt(np.clip(1 - cos ** 2, 0, None))))
    measured = float(rel.mean())
    g_ratio = float(np.median(g[lo]) / np.median(g))
    hard_ratio = float(rel[lo].mean() / rel[rest].mean())
    eff = _conc(_weights(yn))["effective_sample_fraction_1_over_sumw2_over_n"]
    out = {
        "n_samples": int(n),
        "nrmse_measured_SEAM": measured,
        "nrmse_after_oracle_per_sample_rescale": oracle,
        "hedge_share_of_score": float(1.0 - oracle / measured) if measured > 0 else None,
        "hf_norm_spread_max_over_min": float(yn.max() / yn.min()),
        "weight_concentration_no_floor": _conc(_weights(yn)),
        "denominator_floor_counterfactual": {
            f"floor_at_q{q}": _conc(_weights(yn, q)) for q in floors},
        "g_median": float(np.median(g)),
        "cos_median": float(np.median(cos)),
        "admission_rule_rel_lt_1_iff_g_lt_2cos": {
            "frac_g_ge_2cos_all": float((g >= 2 * cos).mean()),
            "frac_g_ge_2cos_lownorm_tail": float((g[lo] >= 2 * cos[lo]).mean()),
            "median_margin_2cos_minus_g_all": float(np.median(2 * cos - g)),
            "median_margin_2cos_minus_g_lownorm_tail": float(np.median((2 * cos - g)[lo])),
        },
        "lownorm_tail": {
            "tail_size": int(k),
            "g_median_tail": float(np.median(g[lo])),
            "cos_median_tail": float(np.median(cos[lo])),
            "g_ratio_lownorm_over_all": g_ratio,
            "mean_rel_l2_tail": float(rel[lo].mean()),
            "mean_rel_l2_rest": float(rel[rest].mean()),
            "tail_hardness_ratio": hard_ratio,
            "tail_indices": lo.tolist(),
        },
        "amplitude_law_slope_log_prednorm_on_log_targetnorm": float(
            np.polyfit(np.log(yn), np.log(np.maximum(g * yn, 1e-30)), 1)[0]),
        "gate": {
            "concentration": bool(eff <= 0.20 or (yn.max() / yn.min()) >= 10.0),
            "tail_is_hard": bool(hard_ratio >= 2.0),
            "reference_arm_hedges_on_tail": bool(g_ratio <= 0.8),
        },
    }
    out["gate_verdict"] = ("RISK" if all(out["gate"].values()) else
                           "WATCH" if sum(out["gate"].values()) >= 2 else "OK")
    out["_gate_meaning"] = ("RISK = all three sub-conditions hold; a per-sample-"
                            "normalized objective is predicted to sacrifice the "
                            "low-norm tail even at lambda=1 (s7_loss-B2: +1.818 "
                            "certified floors). WATCH = two of three. OK = at most one.")
    return out, G


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preds", nargs="+", required=True,
                    help="label=path/preds_test.npz (one or more)")
    ap.add_argument("--reference-arm", default=None,
                    help="label of the MSE-trained arm the gate is read from "
                         "(default: the first)")
    ap.add_argument("--decile-frac", type=float, default=0.10)
    ap.add_argument("--floors", nargs="*", type=float, default=[0.10, 0.25, 0.50])
    ap.add_argument("--pred-key", default="pred")
    ap.add_argument("--target-key", default="target")
    ap.add_argument("--out", default=None)
    ap.add_argument("--plot", default=None,
                    help="(g, cos) plane per arm, coloured by log10 ||HF||, with "
                         "the g = 2cos admission line")
    a = ap.parse_args()

    arms, geoms, targets = {}, {}, {}
    for spec in a.preds:
        if "=" not in spec:
            raise SystemExit(f"--preds entries must be label=path, got {spec!r}")
        lab, path = spec.split("=", 1)
        z = np.load(path)
        rep, G = audit_arm(z[a.pred_key], z[a.target_key], a.decile_frac, a.floors)
        rep["path"] = path
        arms[lab], geoms[lab], targets[lab] = rep, G, np.asarray(z[a.target_key], np.float64)

    ref = a.reference_arm or list(arms)[0]
    if ref not in arms:
        raise SystemExit(f"--reference-arm {ref!r} not among {list(arms)}")

    pairing = {}
    for lab, t in targets.items():
        d = float(np.abs(t - targets[ref]).max())
        pairing[lab] = d
        if d != 0.0:
            raise SystemExit(f"arm {lab!r} is not on the same test split as "
                             f"{ref!r} (target max abs diff {d}); refusing.")

    rep = {"_nrmse_def_hash": N.NRMSE_DEF_HASH,
           "reference_arm": ref,
           "pairing_target_maxabsdiff_vs_reference": pairing,
           "per_arm": arms,
           "gate_read_from_reference_arm": arms[ref]["gate_verdict"]}

    if len(arms) > 1:
        rep["pairwise_vs_reference"] = {}
        for lab in arms:
            if lab == ref:
                continue
            d = geoms[lab]["rel"] - geoms[ref]["rel"]
            o = np.argsort(-np.abs(d))
            cum = np.cumsum(d[o]) / len(d)
            gap = float(d.mean())
            gap_oracle = (arms[lab]["nrmse_after_oracle_per_sample_rescale"]
                          - arms[ref]["nrmse_after_oracle_per_sample_rescale"])
            rep["pairwise_vs_reference"][lab] = {
                "gap_nrmse": gap,
                "gap_after_oracle_per_sample_rescale": float(gap_oracle),
                "amplitude_share_of_gap": (float(1 - gap_oracle / gap) if gap != 0 else None),
                "gap_share_from_top5_samples": float(cum[min(4, len(cum) - 1)] / gap) if gap else None,
                "gap_share_from_top10_samples": float(cum[min(9, len(cum) - 1)] / gap) if gap else None,
                "worst_sample_indices": o[:5].tolist(),
                "n_samples_worse_than_reference": int((d > 0).sum()),
                "median_per_sample_delta": float(np.median(d)),
            }

    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        labs = list(arms)
        fig, axs = plt.subplots(1, len(labs), figsize=(10, 6), dpi=100, squeeze=False)
        yn = geoms[ref]["yn"]
        for ax, lab in zip(axs[0], labs):
            G = geoms[lab]
            sc = ax.scatter(G["g"], G["cos"], c=np.log10(yn), s=26, cmap="viridis")
            lo = arms[lab]["lownorm_tail"]["tail_indices"]
            ax.scatter(G["g"][lo], G["cos"][lo], s=110, facecolors="none",
                       edgecolors="red", linewidths=1.4, label="low-norm tail")
            gg = np.linspace(0, max(2.5, float(G["g"].max()) * 1.05), 50)
            ax.plot(gg, gg / 2.0, "r--", lw=1, label="admission line g = 2cos")
            ax.scatter([1], [1], marker="*", s=200, c="gold", edgecolors="k")
            ax.set_xlabel("g = ||p||/||y||"); ax.set_ylabel("cos(p,y)")
            ax.set_title(f"{lab}  (nRMSE {arms[lab]['nrmse_measured_SEAM']:.4f}, "
                         f"{arms[lab]['gate_verdict']})", fontsize=9)
            ax.set_ylim(-0.1, 1.05); ax.legend(fontsize=7, loc="lower right")
        fig.colorbar(sc, ax=axs[0].tolist(), label="log10 ||HF||")
        fig.savefig(a.plot, bbox_inches="tight")
        rep["plot"] = a.plot

    print(json.dumps(rep, indent=1))
    if a.out:
        with open(a.out, "w") as f:
            json.dump(rep, f, indent=1)
        print(f"[wrote] {a.out}")


if __name__ == "__main__":
    main()
