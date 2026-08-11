"""The coverage-partitioned LF row selector — the NEW mechanism of this card.

Card `r3s3_lf_value-B1` `recipe.base_family`, verbatim:

    NEW in this card: the coverage-partitioned LF row selector
    (R3S3B3_LF_COND_SET / _LF_COND_CAP) and the N_hf reference rung.

WHY IT EXISTS (card part 2). Information about the condition -> field map AT
UNSEEN CONDITIONS can only come from rows AT those conditions. Partitioning
each LF rung's rows by whether their condition already carries an HF train row
therefore splits the matched +/-LF effect into two channels that the base
family's single `A1_lf_cov` arm blends:

  * COVERED rows (`LF_COND_SET=covered`) sit at the very conditions the HF rows
    already supervise. They add no new condition; whatever they buy is an
    OPTIMISATION effect (multi-resolution supervision of the same map — the
    "partial variance reduction of the stochastic gradient" reading of the
    card's D2 citation).
  * UNCOVERED rows (`LF_COND_SET=uncovered`) sit at conditions with no HF row at
    all. They are the SUPERVISION/COVERAGE channel.

`LF_COND_CAP` row-count-matches the coverage channel to the optimisation
channel (`A3s_lf_uncov_n5`): without it, `A3_lf_uncovered` supplies 395 rows per
rung against `A2_lf_covered`'s 5, and any difference is confounded with the
number of LF gradients.

MEASURED PARTITION (card `recipe.env._lf_cond_set`, re-verified live on
`mffp_autoresearch/round2/stripped_data` on 2026-08-07 by this builder, at
`SPLIT_SEED=0` -> HF rows 55, 88, 133, 202, 293):

    sharp__allen_cahn_2d      rung 1: 400 rows,  5 covered, 395 uncovered
                              rung 2: 400 rows,  5 covered, 395 uncovered
    sharp__fisher_kpp_2d      idem
    sharp__cahn_hilliard      idem
    sharp__phase_field_crystal_2d  idem (report-only, ADR r3-0004)
    ifc_poisson / ifc_heat    rung  8: 100 rows, 5 covered, 95 uncovered
                              rung 16:  50 rows, 5 covered, 45 uncovered
                              rung 32:  20 rows, 5 covered, 15 uncovered

The card requires these to be RE-DERIVED per leg rather than assumed, and the
derived counts to be recorded; `smoke_eval` does that and asserts nothing about
their values.

CONDITION KEYS. Membership is exact-condition-row matching under the round's
registered convention (`tools/affine_ladder_voi.py` block A7, restated in the
base family as `_cond_key_set`): the key of a condition row is
`tuple(np.round(row, 12))`. Rounding at 1e-12 is the registered tolerance, not
a choice made here.

NO LF LEAK. Everything in this module operates on the TRAIN split of the
stripped view. The test split physically contains no LF file and no caller
passes a test-split condition array.
"""
from __future__ import annotations

import numpy as np

# The four values `R3S3B3_LF_COND_SET` may take. `none` means "this arm builds
# no LF pool at all" (A0_nolf, A4_hf20_nolf) — it is NOT "an empty selection
# from a pool", so it short-circuits before any rung is inspected.
COND_SETS = ("none", "all", "covered", "uncovered")


def cond_key_set(X: np.ndarray) -> set:
    """Exact condition-row keys (`tools/affine_ladder_voi.py` A7 convention).

    Byte-identical to `_cond_key_set` in the base family
    `models_r2/r2s3_coverage_panel/smoke_eval.py` (commit dfcd46c6).
    """
    return {tuple(np.round(r, 12)) for r in np.asarray(X, dtype=np.float64)}


def partition_rung(X_rung: np.ndarray, hf_keys: set):
    """(covered_idx, uncovered_idx) into `X_rung`, both ascending int64."""
    Xf = np.asarray(X_rung, dtype=np.float64)
    mask = np.fromiter(
        (tuple(np.round(r, 12)) in hf_keys for r in Xf), dtype=bool, count=Xf.shape[0])
    idx = np.arange(Xf.shape[0], dtype=np.int64)
    return idx[mask], idx[~mask]


def cap_draw(n_available: int, cap: int, split_seed: str, fid: int) -> np.ndarray:
    """Which `cap` of `n_available` candidate rows the capped arm keeps.

    TBD (card gap, propagated deliberately — see `build_notes`): the card fixes
    the SIZE of the capped set (`R3S3B3_LF_COND_CAP=5`, "5 uncovered
    conditions, row-count-matched twin of A2") but does NOT say WHICH five, nor
    whether the five are drawn once for the leg or once per rung. Both are
    resolved here by extending the card's OWN draw convention rather than by
    inventing a new one:

    * WHICH — `recipe.env._hf_subset_draws` defines every subset draw in this
      card as `np.sort(np.random.default_rng(s).permutation(n)[:k])`. The same
      generator call is used here, seeded by `[split_seed, fid]` so the draw is
      a pure function of the leg (reproducible, and independent of training).
    * PER RUNG, not per leg — because the card's stated purpose for the cap is
      that `A3s_lf_uncov_n5` be "the row-count-matched twin of A2". `A2` supplies
      exactly 5 covered rows AT EVERY RUNG (5 of 400 on sharp; 5 of 100 / 50 / 20
      on the nested ifc ladders). A single leg-wide draw of 5 conditions from the
      union of uncovered conditions would leave the coarse-to-fine ifc rungs with
      0-5 rows each (rung 32 carries only 15 of the 95 uncovered conditions), so
      the row counts would NOT match and the A2-vs-A3s contrast — the clause the
      `expected_falsification` block turns on — would be confounded with the
      number of LF gradients. Drawing `cap` per rung gives 5-vs-5 at every rung
      on every dataset.

    The realised selection is recorded per rung in `lf_row_manifest` so the
    choice is auditable rather than implicit.

    `split_seed` may be the literal string "native" (the ifc legs); it maps to 0
    so the ifc draw is deterministic and identical across arms.
    """
    s = 0 if str(split_seed) == "native" else int(split_seed)
    n = int(n_available)
    k = int(cap)
    if k >= n:
        return np.arange(n, dtype=np.int64)
    return np.sort(np.random.default_rng([s, int(fid)]).permutation(n)[:k]).astype(np.int64)


def select_lf_rows(X_rung: np.ndarray, hf_keys: set, cond_set: str, cap: int,
                   split_seed: str, fid: int) -> dict:
    """Rows of one LF rung this arm may train on, plus the coverage instrument.

    Returns `{"keep", "n_rows", "n_covered", "n_uncovered", "n_candidates",
    "n_kept", "cond_set", "cap", "capped", "cap_selected_candidate_positions"}`.
    `keep` is an ascending int64 index array into `X_rung` (possibly empty — the
    caller drops empty rungs and reports why).
    """
    if cond_set not in COND_SETS:
        raise SystemExit(f"unknown LF condition set {cond_set!r}, expected {COND_SETS}")
    if cond_set == "none":
        raise SystemExit(
            "select_lf_rows called with cond_set='none'; the caller must "
            "short-circuit that arm before building any pool")
    Xf = np.asarray(X_rung, dtype=np.float64)
    n_rows = int(Xf.shape[0])
    cov_idx, unc_idx = partition_rung(Xf, hf_keys)
    if cond_set == "all":
        cand = np.arange(n_rows, dtype=np.int64)
    elif cond_set == "covered":
        cand = cov_idx
    else:
        cand = unc_idx
    capped = int(cap) > 0
    if capped and cand.size:
        pick = cap_draw(int(cand.size), int(cap), split_seed, fid)
        keep = np.sort(cand[pick]).astype(np.int64)
    else:
        pick = np.arange(cand.size, dtype=np.int64)
        keep = cand
    return {
        "keep": keep,
        "n_rows": n_rows,
        "n_covered": int(cov_idx.size),
        "n_uncovered": int(unc_idx.size),
        "n_candidates": int(cand.size),
        "n_kept": int(keep.size),
        "cond_set": cond_set,
        "cap": int(cap),
        "capped": bool(capped),
        "cap_selected_candidate_positions": [int(i) for i in pick] if capped else None,
    }
