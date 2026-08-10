"""The `direct` leg of card `r3s2_field_reach-B2`'s ROUTE SWITCH.

    stack  : cond -> pseudo-LF (LF native grid) -> corrected upsample
                  -> frozen regularised LSI + local corrector -> HF
    direct : cond -> HF                                        (this module)

WHAT IS AND IS NOT NEW HERE
---------------------------
Nothing about the TRUNK is new: `front_end.Emulator` is the vendored B1 front
end, instantiated on the HF working grid instead of the LF rung's native grid.
That is the point — the card's contrast is a ROUTE contrast at a matched trunk,
matched front end, matched folds and matched total optimizer budget, so the
direct arms are declared MATCHED CONTROLS inside the contrast, not candidate
architectures (recipe `_novelty_declaration`). `A4_direct_film` is the
pre-registered r2s1 calibration arm; if it lands far from `r2s1_direct-B2`'s
certified 23.7753 the family, not the route, is the story.

NO CODE IS VENDORED FROM `r2s1_direct` (recipe `_vendor_source`). The direct
arms additionally carry the zero-parameter analytic IC-synthesis channel, which
r2s1's FiLM-only heads do not have.

EVERY HYPERPARAMETER'S PROVENANCE
---------------------------------
  width 64, blocks 4, modes cap 12   recipe `R3S2B2_DIRECT_TRUNK=
                                     shared_film_fno_w64_b4_m12` (== the
                                     emulator's `R3S2_EMU_{WIDTH,BLOCKS,MODES}`)
  target = HF field                  recipe `R3S2B2_DIRECT_TARGET=hf`
  epochs = E_emu + 2*E_dc            recipe `R3S2B2_DIRECT_BUDGET=
                                     match_stage2_total` (300 at tier 200)
  train rows                         recipe `R3S2B2_DIRECT_TRAIN_ROWS=
                                     hf_train_all` +
                                     `R3S2B2_DIRECT_VAL=disjoint_if_n_train_hf_
                                     ge_20_else_none_recorded` (see `train_rows`)
  loss = rel_l2                      the card's `source_iteration`
                                     (brainstormer iteration_2, item 4:
                                     "the training objectives (`rel_l2` for both
                                     the emulator and the direct head) are free
                                     by rule and recorded separately in the
                                     diag")
  lr, weight decay, batch, clip,     the BASE FAMILY's `SMOKE` block, unchanged
  cosine schedule                    (`lr_pretrain` 1e-3 — the direct head is
                                     the same trunk trained from scratch, so it
                                     takes the same pre-training lr the emulator
                                     takes; no new constant is introduced)
"""
from __future__ import annotations

import numpy as np
import torch

from front_end import Emulator


class DirectHeadError(RuntimeError):
    """The direct route's contract was violated."""


def train_rows(n_train_hf: int, fit_idx: np.ndarray, val_idx: np.ndarray,
               val_threshold: int = 20) -> dict:
    """Resolve `R3S2B2_DIRECT_TRAIN_ROWS` x `R3S2B2_DIRECT_VAL`.

    The two knobs together read: the direct head's row POOL is the whole HF
    train split (`hf_train_all` — never a sub-sample, never the LF-paired
    subset), and a DISJOINT validation slice is carved out of it only when the
    split is large enough to afford one (`n_train_hf >= 20`); otherwise there is
    no validation slice and the fact is RECORDED (`..._else_none_recorded`).

    Consequence, which the card discloses on every ifc delta
    (`R3S2B2_ROUTE_DATA_DISCLOSURE=1`): on the ifc cells (N_train_HF = 5) the
    direct head trains on all 5 HF rows and holds none out, while the stack's
    stage 1 fits on 18 of 20 LF rows and its corrector on 3 HF rows.
    """
    fit_idx = np.asarray(fit_idx, dtype=np.int64)
    val_idx = np.asarray(val_idx, dtype=np.int64)
    n = int(n_train_hf)
    if n >= int(val_threshold):
        rows = np.array(sorted(int(i) for i in fit_idx), dtype=np.int64)
        rec = {
            "rows": rows, "n_train_route": int(rows.size),
            "val_slice": np.array(sorted(int(i) for i in val_idx), dtype=np.int64),
            "val_disjoint": True,
            "rule": (f"n_train_hf={n} >= {val_threshold}: a DISJOINT val slice exists, "
                     "so the direct head trains on the fit fold only — the same fold "
                     "the stack's corrector fits on (matched folds)"),
        }
    else:
        rows = np.arange(n, dtype=np.int64)
        rec = {
            "rows": rows, "n_train_route": int(rows.size),
            "val_slice": np.zeros(0, dtype=np.int64),
            "val_disjoint": False,
            "rule": (f"n_train_hf={n} < {val_threshold}: no val slice is affordable, so "
                     "the direct head trains on ALL HF train rows and holds none out "
                     "(R3S2B2_DIRECT_VAL=..._else_none_recorded). RECORDED, and the "
                     "asymmetry vs the stack is published as n_train_route."),
        }
    if rec["rows"].size == 0:
        raise DirectHeadError("the direct head resolved to an empty training row set")
    rec["knobs"] = {"R3S2B2_DIRECT_TRAIN_ROWS": "hf_train_all",
                    "R3S2B2_DIRECT_VAL":
                        "disjoint_if_n_train_hf_ge_20_else_none_recorded",
                    "val_threshold": int(val_threshold)}
    return rec


def build(front_end: str, cond_dim: int, film_idx, hf_grid, width: int,
          blocks: int, modes_h: int, modes_w: int, device) -> Emulator:
    """The direct trunk: the SAME `Emulator` class, on the HF working grid.

    `film_idx=None` -> `film_only` (FiLM on the whole condition vector);
    otherwise the non-`ic_*` columns FiLM and the analytic IC field synthesised
    AT HF RESOLUTION enters as the extra input channel.
    """
    net = Emulator(front_end, int(cond_dim), film_idx, (int(hf_grid[0]), int(hf_grid[1])),
                   int(width), int(blocks), int(modes_h), int(modes_w)).to(device)
    return net


def rel_l2_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Per-sample relative L2, mean over the batch — byte-for-byte the emulator's
    objective (`R3S2_EMU_LOSS=rel_l2`), so the two routes optimise the same thing."""
    num = (pred - target).reshape(pred.shape[0], -1).norm(dim=1)
    den = target.reshape(target.shape[0], -1).norm(dim=1).clamp_min(1e-8)
    return (num / den).mean()


def predict(net: Emulator, X: np.ndarray, ic: torch.Tensor, scaler: float,
            hf_grid, device, batch_size: int) -> np.ndarray:
    """(N, cond_dim) -> (N, H*W) HF prediction in RAW units.

    `ic` is the (N, 1, H, W) analytic IC channel for this front end, or None.
    NO LF ARRAY IS TOUCHED ANYWHERE ON THIS PATH — that is the whole point of
    the direct route, and the caller asserts it (validity gate V15).
    """
    H, W = int(hf_grid[0]), int(hf_grid[1])
    net.eval()
    Xt = torch.from_numpy(np.asarray(X, dtype=np.float32))
    n = int(Xt.shape[0])
    out = np.empty((n, H * W), dtype=np.float64)
    with torch.no_grad():
        for i in range(0, n, batch_size):
            sl = slice(i, min(i + batch_size, n))
            extra = None if ic is None else ic[sl].to(device)
            p = net(Xt[sl].to(device), extra) * float(scaler)
            out[sl] = p.reshape(p.shape[0], -1).double().cpu().numpy()
    return out
