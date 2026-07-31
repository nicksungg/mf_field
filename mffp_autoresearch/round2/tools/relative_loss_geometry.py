#!/usr/bin/env python
"""relative_loss_geometry.py — is a per-sample-normalized training objective
safe on this dataset, and does it have a low-amplitude trap?

Any objective of the family

    L_lambda(p, y) = (1 - cos^2) + lambda (g - cos)^2 ,
        g = ||p||/||y|| ,  cos = <p,y>/(||p|| ||y||)

reduces EXACTLY to two scalars per sample, and at lambda = 1 it is exactly the
scored metric rel-L2 squared (s7_loss-B1 F1, verified to 4.3e-14). This tool
takes any saved `(pred, target)` pair and reports, for each requested lambda:

  * where the trained endpoint sits in the reduced (alpha, beta) plane,
    alpha = <p, yhat>/||y||  (1 = correct),  beta = ||p_perp||/||y||;
  * `frac_perverse` — the fraction of samples with alpha < 1 whose target-aligned
    component gradient DESCENT would SHRINK. At lambda = 1 this is 0 by algebra
    (L = (alpha-1)^2 + beta^2), so a non-zero value is entirely the lambda > 1
    gain term. Non-zero here means the objective is pushing predictions away
    from their targets on that fraction of the data;
  * `escape_drive` — |dL/dr| along the low-amplitude valley c* = lambda/(lambda-1) r,
    which is 2*lambda/(lambda-1) * r for lambda > 1 (vanishes as r -> 0) but the
    finite constant 2(1-r) at lambda = 1. This is the drive that has to take an
    untrained network (r ~ 0, c ~ 0) away from the zero output;
  * `sample_weight_concentration` — a relative objective silently replaces
    uniform sample weighting by w_i ~ 1/||y_i||^2. Reports the top-decile weight
    share (MSE-equivalent 0.10), max/median, and the effective sample fraction
    1/sum(w^2)/n. s7_loss-B1 F13: the two panel datasets that collapsed had
    hf_norm_spread 22.7 / 5017 and effective fraction 0.16 / 0.45; the four that
    did not had spread <= 2.55 and effective fraction 0.55-0.99.

Read it as. `frac_perverse` > 0 at your chosen lambda => the objective has a
region where it de-aligns predictions; lower lambda toward 1. `escape_drive` at
the dataset's own g_median much below 1 => a network that ever reaches a small
output cannot get back out. Weight concentration far from 0.10 => you are
changing WHICH samples the model fits, not just how it is scored.

Usage
-----
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/relative_loss_geometry.py \
        --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
        [--lambdas 1.0 4.0] [--pred_key pred --target_key target] \
        [--plot out.png] [--out out.json]

Provenance: worktrees/s7_loss/B1/scratchpad/reanalysis_turn_1{,b}.py;
card experiment_cards/s7_loss/batch_1/B1.json part 6, findings F1-F5, F13.
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
import torch

_SQ_EPS = 1e-12          # sqrt(sum p^2 + eps): finite gradient at p == 0
NORM_FLOOR = 1e-4        # clamp on ||y||, the transolver_residual precedent


def shape_gain(p: torch.Tensor, y: torch.Tensor):
    """Per-sample (shape, gain); shape + gain == rel^2 exactly."""
    p = p.reshape(p.shape[0], -1)
    y = y.reshape(y.shape[0], -1)
    a = torch.sqrt((p * p).sum(1) + _SQ_EPS)
    b = torch.clamp(torch.sqrt((y * y).sum(1)), min=NORM_FLOOR)
    cos = (p * y).sum(1) / (a * b)
    return 1.0 - cos * cos, (a / b - cos) ** 2


def _loss_ab(alpha: torch.Tensor, beta: torch.Tensor, lam: float):
    """L on the reduced 2-vector realisation p = (alpha, beta), y = (1, 0)."""
    p = torch.stack([alpha, beta], dim=1)
    y = torch.zeros_like(p)
    y[:, 0] = 1.0
    s, g = shape_gain(p, y)
    return s + lam * g


def aligned_drive(alpha: np.ndarray, beta: np.ndarray, lam: float) -> np.ndarray:
    """-dL/dalpha: the descent drive on the target-aligned component."""
    a = torch.tensor(np.asarray(alpha, float), requires_grad=True)
    b = torch.tensor(np.asarray(beta, float))
    (grad,) = torch.autograd.grad(_loss_ab(a, b, lam).sum(), a)
    return -grad.numpy()


def analyse(pred: np.ndarray, target: np.ndarray, lambdas) -> dict:
    p = np.asarray(pred, np.float64).reshape(pred.shape[0], -1)
    y = np.asarray(target, np.float64).reshape(target.shape[0], -1)
    if p.shape != y.shape:
        raise ValueError(f"pred {p.shape} != target {y.shape}")
    yn = np.linalg.norm(y, axis=1)
    if (yn == 0).any():
        raise ValueError("zero-norm target sample")
    r = np.linalg.norm(p, axis=1) / yn
    alpha = (p * y).sum(1) / yn ** 2
    beta = np.sqrt(np.maximum(r ** 2 - alpha ** 2, 0.0))
    c = np.divide(alpha, r, out=np.zeros_like(alpha), where=r > 0)
    rel = np.linalg.norm(p - y, axis=1) / yn

    w = 1.0 / yn ** 2
    w = w / w.sum()
    n = len(yn)
    out = {
        "n_samples": int(n),
        "rel_l2_mean_SEAM": float(rel.mean()),
        "identity_max_absdiff_rel2_vs_shape_plus_gain": float(np.max(np.abs(
            rel ** 2 - ((1 - c ** 2) + (r - c) ** 2)))),
        "g_median": float(np.median(r)),
        "cos_median": float(np.median(c)),
        "alpha_median": float(np.median(alpha)),
        "beta_median": float(np.median(beta)),
        "frac_alpha_below_1": float((alpha < 1).mean()),
        "frac_amplitude_collapse_g_below_0.5": float((r < 0.5).mean()),
        "sample_weight_concentration": {
            "hf_norm_spread_max_over_min": float(yn.max() / yn.min()),
            "top10pct_weight_share_MSE_equivalent_0.10":
                float(np.sort(w)[-max(1, n // 10):].sum()),
            "weight_max_over_median": float(w.max() / np.median(w)),
            "effective_sample_fraction_1_over_sumw2_over_n":
                float(1.0 / (w ** 2).sum() / n),
        },
        "per_lambda": {},
    }
    for lam in lambdas:
        d = aligned_drive(alpha, beta, float(lam))
        under = alpha < 1.0
        k = float(lam) / (float(lam) - 1.0) if lam > 1 else None
        gm = out["g_median"]
        out["per_lambda"][f"lambda={float(lam)}"] = {
            "frac_perverse_alpha_lt_1_and_drive_lt_0": float((under & (d < 0)).mean()),
            "aligned_drive_median": float(np.median(d)),
            "aligned_drive_p10": float(np.percentile(d, 10)),
            "low_amplitude_valley_cos_over_g": k,
            "escape_drive_at_this_arms_g_median":
                float(2 * float(lam) / (float(lam) - 1) * gm) if lam > 1
                else float(2 * (1 - gm)),
            "frac_samples_above_the_valley_cos_gt_k_times_g":
                float((c > k * r).mean()) if k else None,
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pred_npz", nargs="+", required=True)
    ap.add_argument("--labels", nargs="*", default=None)
    ap.add_argument("--lambdas", nargs="+", type=float, default=[1.0, 4.0])
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    ap.add_argument("--plot", default=None,
                    help="write the (alpha,beta) plane with the perverse region "
                         "of the LARGEST lambda shaded")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    labels = a.labels or [os.path.basename(os.path.dirname(p)) or p
                          for p in a.pred_npz]
    if len(labels) != len(a.pred_npz):
        raise SystemExit("--labels must match --pred_npz in length")

    rep = {"lambdas": a.lambdas, "arms": {}}
    pts = {}
    for lab, path in zip(labels, a.pred_npz):
        z = np.load(path)
        pr, tg = z[a.pred_key], z[a.target_key]
        rep["arms"][lab] = analyse(pr, tg, a.lambdas)
        rep["arms"][lab]["path"] = path
        yn = np.linalg.norm(tg.reshape(tg.shape[0], -1).astype(np.float64), axis=1)
        pp = pr.reshape(pr.shape[0], -1).astype(np.float64)
        al = (pp * tg.reshape(tg.shape[0], -1)).sum(1) / yn ** 2
        rr = np.linalg.norm(pp, axis=1) / yn
        pts[lab] = (al, np.sqrt(np.maximum(rr ** 2 - al ** 2, 0)))

    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        lam = max(a.lambdas)
        gr = 300
        A = np.linspace(-0.05, 1.3, gr)
        B = np.linspace(1e-4, 1.3, gr)
        AA, BB = np.meshgrid(A, B)
        D = aligned_drive(AA.ravel(), BB.ravel(), lam).reshape(gr, gr)
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        ax.contourf(AA, BB, (D < 0).astype(float), levels=[0.5, 1.5],
                    colors=["#ffcccc"])
        ax.contour(AA, BB, D, levels=[0.0], colors="r", linewidths=1.5)
        for lab, (al, be) in pts.items():
            ax.scatter(al, be, s=12, alpha=0.7, label=lab, edgecolors="none")
        ax.scatter([1], [0], marker="*", s=250, c="gold", edgecolors="k", zorder=5)
        ax.set_xlabel(r"$\alpha=\langle p,\hat y\rangle/\|y\|$ (1 = correct)")
        ax.set_ylabel(r"$\beta=\|p_\perp\|/\|y\|$")
        ax.set_title(f"red = gradient descent on L(lambda={lam}) SHRINKS the "
                     "aligned component\n(empty at lambda=1)")
        ax.legend(fontsize=8)
        ax.set_xlim(-0.05, 1.3)
        ax.set_ylim(0, 1.3)
        fig.tight_layout()
        fig.savefig(a.plot)
        rep["plot"] = a.plot

    txt = json.dumps(rep, indent=1)
    print(txt)
    if a.out:
        with open(a.out, "w") as f:
            f.write(txt)
        print(f"[wrote] {a.out}")


if __name__ == "__main__":
    main()
