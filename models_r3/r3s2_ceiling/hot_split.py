"""Held-out-TRAIN (HOT) split protocols for card `r3s2_field_reach-B3`.

WHY THIS MODULE EXISTS
----------------------
The ceiling rung `R2_oracle` needs a REAL LF field at evaluation time. Immutable
#9 makes that structurally impossible on the test split: the round-3 stripped
view physically omits the test LF files and `round2/eval/score_panel.py` refuses
any view that exposes them. The card therefore measures every rung on HELD-OUT
TRAIN rows (the project's own enforced precedent, round-2 report §7), and this
module is the ONLY place the fit/held-out partition is decided.

Two protocols, both VERBATIM from the card recipe -- nothing here is inferred:

  `R3S2B3_HOT_SPLIT_SHARP = seeded_perm_fit320_heldout80`
      one seeded permutation, T = 320 fit rows / H = 80 held-out rows. |T| = 320
      is chosen by the card so the floor comparison lands exactly on the
      certified G5 matched-fit population (`_n_scored = 320`).
      `R3S2B3_SHARP_CLOSEDFORM_FOLDS = kfold5_within_T` then cuts 5 DISJOINT
      cross-fit folds inside T; each is one leg of the statistic.

  `R3S2B3_HOT_SPLIT_IFC = enumerate_C5_3`
      all C(5,3) = 10 folds (T = 3 fit, H = 2 held out) -- the whole fold
      population, enumerated, not sampled (batch-3 clause-hygiene rule 3:
      "enumerate the C(Ntr, n_fit) fold population instead of spending seeds on
      closed-form stages at n_fit <= 5").
      `R3S2B3_IFC_LOO_DISCLOSURE = enumerate_C5_4` adds the 5 LOO folds
      (T = 4 / H = 1) as the floor-matched disclosure variant, because the
      `affine_on_hf_train` floor is a LOO quantity (program.md §2 affine-floor
      rule) and a C(5,3) number is not matched to it.

`R3S2B3_HOT_SPLIT_KEY = deterministic_from_dataset_and_seed`: the permutation is
drawn from sha256(dataset|seed), NOT from the global RNG, so the partition is
reproducible from the two identifiers alone and is invariant to how many torch
RNG draws happened before it.

A dataset that matches NEITHER protocol (the guard cells, and any contract-tier
probe) gets the proportional fallback below, which is flagged
`registered_unit_eligible = False`: it can never carry a registered clause.
"""
from __future__ import annotations

import hashlib
from itertools import combinations

import numpy as np

SHARP_N_FIT = 320          # recipe R3S2B3_HOT_SPLIT_SHARP / R3S2B3_FLOOR_MATCHED_N "sharp:320"
SHARP_N_HELDOUT = 80       # recipe R3S2B3_HOT_SPLIT_SHARP
SHARP_CLOSEDFORM_FOLDS = 5  # recipe R3S2B3_SHARP_CLOSEDFORM_FOLDS = kfold5_within_T
IFC_N_FIT = 3              # recipe R3S2B3_HOT_SPLIT_IFC = enumerate_C5_3
IFC_LOO_N_FIT = 4          # recipe R3S2B3_IFC_LOO_DISCLOSURE = enumerate_C5_4
IFC_MAX_NTR = 8            # above this, enumerating C(Ntr, Ntr-2) is not the card's protocol


class HotSplitError(RuntimeError):
    """The split protocol could not be applied without inventing something."""


def split_key(dataset: str, seed: int) -> int:
    """`R3S2B3_HOT_SPLIT_KEY = deterministic_from_dataset_and_seed`."""
    h = hashlib.sha256(f"{dataset}|{int(seed)}".encode()).digest()
    return int.from_bytes(h[:8], "big") % (2 ** 32)


def _perm(dataset: str, seed: int, n: int) -> np.ndarray:
    return np.random.default_rng(split_key(dataset, seed)).permutation(int(n))


def _kfold(rows: np.ndarray, k: int, dataset: str, seed: int) -> list:
    """k DISJOINT contiguous folds of an already-permuted `rows` (no re-shuffle:
    `rows` came out of the seeded permutation, so contiguous == random)."""
    rows = np.asarray(rows, dtype=np.int64)
    parts = np.array_split(np.arange(len(rows)), int(k))
    out = []
    for j, sel_pos in enumerate(parts):
        if not len(sel_pos):
            raise HotSplitError(f"{dataset}: k-fold {j} of {k} is empty on |T| = {len(rows)}")
        mask = np.ones(len(rows), dtype=bool)
        mask[sel_pos] = False
        out.append({"leg": j,
                    "fit_rows": rows[mask].copy(),
                    "sel_rows": rows[sel_pos].copy()})
    return out


def plan(dataset: str, n_train_hf: int, seed: int) -> dict:
    """Return the full HOT plan for one (dataset, seed).

    `legs` is the population the card's `min`-over-legs clauses are taken over.
    Each leg carries:
      `fit_rows`   rows the closed-form transfer function is fitted on
      `sel_folds`  (fit, sel) pairs INSIDE `fit_rows` used to select the D2
                   regularisation out of sample on the emulator's own output
      `heldout`    the H rows every rung is scored on (never seen by any stage)
      `train_rows` the rows the NEURAL stages may train on (= T for this leg)
    """
    n = int(n_train_hf)
    if n >= SHARP_N_FIT + SHARP_N_HELDOUT:
        perm = _perm(dataset, seed, n)
        T = np.sort(perm[:SHARP_N_FIT])
        H = np.sort(perm[SHARP_N_FIT:SHARP_N_FIT + SHARP_N_HELDOUT])
        legs = []
        for f in _kfold(perm[:SHARP_N_FIT], SHARP_CLOSEDFORM_FOLDS, dataset, seed):
            legs.append({
                "leg_id": f"kfold5_{f['leg']}",
                "fit_rows": np.sort(f["fit_rows"]),
                "sel_folds": [(np.sort(f["fit_rows"]), np.sort(f["sel_rows"]))],
                "heldout": H,
                "train_rows": T,
                "retrain_neural_stages": bool(f["leg"] == 0),
            })
        return {
            "protocol": "seeded_perm_fit320_heldout80",
            "knob": "R3S2B3_HOT_SPLIT_SHARP",
            "n_train_hf": n, "n_fit": int(len(T)), "n_heldout": int(len(H)),
            "T": T, "H": H, "legs": legs,
            "n_legs": len(legs),
            "closedform_folds": "kfold5_within_T",
            "split_key": split_key(dataset, seed),
            "registered_unit_eligible": True,
            "disclosure_legs": [],
            "note": ("|T| = 320 lands the floor comparison on the certified G5 "
                     "matched-fit population (_n_scored = 320); the 5 legs are the "
                     "disjoint cross-fit folds of the CLOSED-FORM stage inside T, so "
                     "every leg's regularisation is selected exactly out of sample."),
        }

    if n <= IFC_MAX_NTR:
        if n < IFC_N_FIT + 2:
            raise HotSplitError(
                f"{dataset}: n_train_hf = {n} cannot support the C(n,{IFC_N_FIT}) "
                "protocol (needs >= 5 rows); refusing to invent a split")
        rows = np.arange(n, dtype=np.int64)
        legs = []
        for j, fit in enumerate(combinations(range(n), IFC_N_FIT)):
            fit = np.asarray(fit, dtype=np.int64)
            H = np.asarray([i for i in rows if i not in set(fit.tolist())], dtype=np.int64)
            # LOO INSIDE T is the only exactly-out-of-sample criterion available at
            # n_fit = 3; it is what selects the D2 regularisation on this cell.
            sel_folds = [(np.asarray([r for r in fit if r != v], dtype=np.int64),
                          np.asarray([v], dtype=np.int64)) for v in fit]
            legs.append({
                "leg_id": f"C{n}_{IFC_N_FIT}_{j:02d}",
                "fit_rows": fit, "sel_folds": sel_folds,
                "heldout": H, "train_rows": fit,
                "retrain_neural_stages": True,
            })
        disclosure = []
        for j, fit in enumerate(combinations(range(n), IFC_LOO_N_FIT)):
            fit = np.asarray(fit, dtype=np.int64)
            H = np.asarray([i for i in rows if i not in set(fit.tolist())], dtype=np.int64)
            disclosure.append({"leg_id": f"C{n}_{IFC_LOO_N_FIT}_loo_{j:02d}",
                               "fit_rows": fit, "heldout": H})
        return {
            "protocol": f"enumerate_C{n}_{IFC_N_FIT}",
            "knob": "R3S2B3_HOT_SPLIT_IFC",
            "n_train_hf": n, "n_fit": IFC_N_FIT, "n_heldout": n - IFC_N_FIT,
            "T": None, "H": None, "legs": legs, "n_legs": len(legs),
            "closedform_folds": "loo_within_T",
            "split_key": split_key(dataset, seed),
            "registered_unit_eligible": True,
            "disclosure_legs": disclosure,
            "disclosure_knob": "R3S2B3_IFC_LOO_DISCLOSURE",
            "note": ("the WHOLE fold population is enumerated (clause-hygiene rule 3), "
                     "so no seed is spent on a closed-form stage at n_fit <= 5; the "
                     f"C(n,{IFC_LOO_N_FIT}) legs are the FLOOR-MATCHED disclosure "
                     "variant, because `affine_on_hf_train` is a LOO quantity."),
        }

    # Neither protocol applies (guard cells, contract-tier probes). Proportional
    # 80/20, ONE leg, and the unit can never be REGISTERED (assert-don't-default:
    # the fallback is explicit and disqualifying, not silent).
    n_h = max(1, int(round(0.2 * n)))
    if n - n_h < 3:
        raise HotSplitError(
            f"{dataset}: n_train_hf = {n} leaves < 3 fit rows after the fallback "
            "hold-out; refusing to default")
    perm = _perm(dataset, seed, n)
    H = np.sort(perm[:n_h])
    T = np.sort(perm[n_h:])
    return {
        "protocol": "proportional_fallback_80_20",
        "knob": "none (neither R3S2B3_HOT_SPLIT_SHARP nor R3S2B3_HOT_SPLIT_IFC applies)",
        "n_train_hf": n, "n_fit": int(len(T)), "n_heldout": int(len(H)),
        "T": T, "H": H,
        "legs": [{"leg_id": "fallback_0", "fit_rows": T,
                  "sel_folds": [(T[:max(1, len(T) - max(1, len(T) // 5))],
                                 T[max(1, len(T) - max(1, len(T) // 5)):])],
                  "heldout": H, "train_rows": T, "retrain_neural_stages": True}],
        "n_legs": 1,
        "closedform_folds": "single_holdout_within_T",
        "split_key": split_key(dataset, seed),
        "registered_unit_eligible": False,
        "disclosure_legs": [],
        "note": ("this cell matches NEITHER card protocol (n_train_hf is neither >= 400 "
                 "nor <= 8), so its ceiling numbers are contract/guard evidence only and "
                 "`registered_unit_eligible` is False -- it can never carry a clause."),
    }


def jsonable(p: dict) -> dict:
    """The plan minus the index arrays (which go to the leg dump separately)."""
    out = {k: v for k, v in p.items()
           if k not in ("legs", "T", "H", "disclosure_legs")}
    out["T_head"] = (None if p.get("T") is None else [int(v) for v in p["T"][:8]])
    out["H_head"] = (None if p.get("H") is None else [int(v) for v in p["H"][:8]])
    out["legs"] = [{"leg_id": lg["leg_id"],
                    "n_fit_rows": int(len(lg["fit_rows"])),
                    "n_heldout": int(len(lg["heldout"])),
                    "n_sel_folds": int(len(lg["sel_folds"])),
                    "n_train_rows": int(len(lg["train_rows"])),
                    "retrain_neural_stages": bool(lg["retrain_neural_stages"])}
                   for lg in p["legs"]]
    out["disclosure_legs"] = [{"leg_id": d["leg_id"],
                               "n_fit_rows": int(len(d["fit_rows"])),
                               "n_heldout": int(len(d["heldout"]))}
                              for d in p.get("disclosure_legs", [])]
    return out
