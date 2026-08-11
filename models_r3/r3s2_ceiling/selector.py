"""`A6_ifc_loo_selector` — the ifc HEADLINE of card `r3s2_field_reach-B2`.

WHY THIS ARM EXISTS (and why the raw ifc route delta is NOT the headline)
-------------------------------------------------------------------------
B1's mechanism analysis, part 7 item 4, verbatim: *"If any ifc claim is wanted
at all, the honest route is a selector that CHOOSES between the affine closed
form and the LF route on a held-out split (part 6 M12), not a larger network."*
M12 itself: *"a stack that CHOOSES between the affine closed form and the LF
route on a held-out split dominates both."* Round-3 program.md §2's affine-floor
rule is the same instruction from the other side: on the ifc cells an arm that
does not beat `affine_on_hf_train` *"has learned nothing beyond linearity"*.

So: `R3S2B2_IFC_LOO_SELECTOR=affine_on_hf_train,A1_stack_ic_reg,A3_direct_ic`,
`optimizer_epochs: 0`, ifc cells only, selection on TRAIN ROWS ONLY — the test
split is never read by the selection (only by the reporting of the winner).

THE PROTOCOL, AND ITS ONE ASYMMETRY (recorded, never hidden)
------------------------------------------------------------
With N_train_HF = 5 the only held-out split that exists is leave-one-out. For
each held-out row i:

  * `affine_on_hf_train` is REFIT on the other rows and predicts row i. This is
    an exact, strictly out-of-sample LOO — it costs one `lstsq` per row.
  * `A1` and `A3` are NOT refit: the card budgets this arm at ZERO optimizer
    epochs, and five retrains of a 300-epoch arm is a different card. Their LOO
    column is the already-fitted arm's prediction on row i, with that arm's
    exposure to row i recorded per row (`exposure` below): rows in a trained
    arm's own fit fold are IN SAMPLE for it.

That asymmetry has a DIRECTION, and the direction is what makes the arm usable:
the closed form is scored strictly out of sample while the trained arms are
scored (partly) in sample, so

    a selection of `affine_on_hf_train` is CONSERVATIVE  — it survived a
      handicap, and it is a lower bound on the closed form's advantage;
    a selection of `A1` or `A3` is OPTIMISTIC — it must be read as an UPPER
      bound on the trained route's value, never as a certified win.

Both readings are emitted in the result (`read_as`), together with the
`heldout_only` sub-score, which restricts each candidate's score to the rows it
did not fit on (this is empty for a candidate that fitted every row — on the ifc
cells `A3_direct_ic` trains on all 5 rows by `R3S2B2_DIRECT_TRAIN_ROWS=
hf_train_all`, which is itself part of the `n_train_route` disclosure).

The affine estimator is byte-for-byte the certified floor's estimator
(`[C, 1] B ~ Y` via `lstsq`; `round3/tools/task_linearity_audit.py::
affine_fit_predict`, cited, never imported), so the selector's affine candidate
and program.md §2's `affine_on_hf_train` floor are the same object.
"""
from __future__ import annotations

import numpy as np


class SelectorError(RuntimeError):
    """The selector's contract was violated."""


def affine_fit_predict(C_fit: np.ndarray, Y_fit: np.ndarray,
                       C_eval: np.ndarray) -> np.ndarray:
    """`[C, 1] B ~ Y` via lstsq, fitted on `C_fit/Y_fit`, applied to `C_eval`."""
    A = np.concatenate([np.asarray(C_fit, dtype=np.float64),
                        np.ones((C_fit.shape[0], 1))], axis=1)
    B, *_ = np.linalg.lstsq(A, np.asarray(Y_fit, dtype=np.float64), rcond=None)
    E = np.concatenate([np.asarray(C_eval, dtype=np.float64),
                        np.ones((C_eval.shape[0], 1))], axis=1)
    return E @ B


def affine_loo_predictions(C: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Exact leave-one-out predictions of the affine floor on the train rows."""
    C = np.asarray(C, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    n = int(C.shape[0])
    if n < 2:
        raise SelectorError("affine LOO needs at least 2 rows")
    out = np.empty_like(Y)
    for i in range(n):
        keep = np.array([j for j in range(n) if j != i], dtype=np.int64)
        out[i] = affine_fit_predict(C[keep], Y[keep], C[i:i + 1])[0]
    return out


def run(Y_tr: np.ndarray, X_tr: np.ndarray, X_te: np.ndarray, Y_te: np.ndarray,
        trained: dict, nrmse_fn, candidate_order) -> dict:
    """Score the candidates by LOO on the HF train rows and pick the winner.

    trained : {tag: {"train_pred": (Ntr, HW), "test_pred": (Nte, HW),
                     "fit_rows": array of train-row indices this arm FITTED on}}
              for the two trained candidates. The affine candidate is built here.
    candidate_order : `R3S2B2_IFC_LOO_SELECTOR` csv, verbatim (defines both the
              candidate set and the deterministic tie-break order).
    """
    Y_tr = np.asarray(Y_tr, dtype=np.float64)
    X_tr = np.asarray(X_tr, dtype=np.float64)
    n_tr = int(Y_tr.shape[0])
    order = [s.strip() for s in str(candidate_order).split(",") if s.strip()]
    if not order:
        raise SelectorError(f"empty candidate list {candidate_order!r}")

    cands = {}
    for tag in order:
        if tag == "affine_on_hf_train":
            loo_pred = affine_loo_predictions(X_tr, Y_tr)
            test_pred = affine_fit_predict(X_tr, Y_tr, np.asarray(X_te, np.float64))
            fit_rows = np.zeros(0, dtype=np.int64)      # refit per fold: none held
            exact = True
        else:
            if tag not in trained:
                raise SelectorError(
                    f"selector candidate {tag!r} has no trained predictions supplied")
            loo_pred = np.asarray(trained[tag]["train_pred"], dtype=np.float64)
            test_pred = np.asarray(trained[tag]["test_pred"], dtype=np.float64)
            fit_rows = np.asarray(trained[tag]["fit_rows"], dtype=np.int64)
            exact = False
        if loo_pred.shape != Y_tr.shape:
            raise SelectorError(
                f"{tag}: train-row prediction {loo_pred.shape} != targets {Y_tr.shape}")
        seen = set(int(v) for v in fit_rows.ravel())
        heldout = np.array([i for i in range(n_tr) if i not in seen], dtype=np.int64)
        cands[tag] = {
            "loo_nrmse_all_train_rows": float(nrmse_fn(loo_pred, Y_tr)),
            "loo_is_exact_out_of_sample": bool(exact),
            "n_rows_fitted_by_this_candidate": int(len(seen)),
            "rows_fitted_by_this_candidate": sorted(seen),
            "heldout_only_rows": [int(v) for v in heldout],
            "heldout_only_nrmse": (float(nrmse_fn(loo_pred[heldout], Y_tr[heldout]))
                                   if heldout.size else None),
            "test_nrmse_reported_after_selection": float(nrmse_fn(test_pred, Y_te)),
        }
        cands[tag]["_test_pred"] = test_pred

    scores = [cands[t]["loo_nrmse_all_train_rows"] for t in order]
    finite = [s for s in scores if np.isfinite(s)]
    if not finite:
        raise SelectorError(f"every candidate scored non-finite: {dict(zip(order, scores))}")
    winner = order[int(np.argmin([s if np.isfinite(s) else np.inf for s in scores]))]
    win_exact = cands[winner]["loo_is_exact_out_of_sample"]

    out = {
        "candidates": order,
        "selection_split": ("leave-one-out over the HF TRAIN rows only; the test split "
                            "is never read by the selection"),
        "n_train_hf_rows": n_tr,
        "scores": {t: {k: v for k, v in cands[t].items() if not k.startswith("_")}
                   for t in order},
        "selected": winner,
        "selected_test_nrmse": cands[winner]["test_nrmse_reported_after_selection"],
        "optimizer_epochs": 0,
        "asymmetry": (
            "the affine candidate is REFIT per fold (exact out-of-sample LOO); the "
            "trained candidates are not refit (this arm is budgeted at zero optimizer "
            "epochs) and are scored on rows they may have fitted — see "
            "rows_fitted_by_this_candidate per candidate"),
        "read_as": (
            "a selection of `affine_on_hf_train` is CONSERVATIVE (it won under a "
            "handicap) and lower-bounds the closed form's advantage; a selection of a "
            "trained arm is OPTIMISTIC and upper-bounds the trained route's value — it "
            "is NOT a certified win. Read `heldout_only_nrmse` beside every score."
            if not win_exact else
            "the winner is the strictly out-of-sample candidate, so the selection is "
            "conservative: the trained arms were scored partly in sample and still lost."),
        "affine_estimator": ("[C, 1] B ~ Y via lstsq — byte-for-byte the estimator behind "
                            "the certified `affine_on_hf_train` floor (round-3 program.md "
                            "§2 affine-floor rule)"),
    }
    return out, cands[winner]["_test_pred"]
