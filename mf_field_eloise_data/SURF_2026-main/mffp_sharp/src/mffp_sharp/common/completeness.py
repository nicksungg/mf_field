"""Condition-completeness certificate as a generation gate.

Two training-free tests (the round-2 audit instruments, ADR r2-0003, made
first-class so every generated dataset carries a checkable verdict instead of an
asserted claim):

1. NEAREST-PAIR WITNESS — standardize the condition vectors, find the closest
   pair, compare their fields. Near-zero condition distance with O(1) field
   difference proves a driver of the solution is missing from the vector.
2. RECONSTRUCTION CERTIFICATE — rebuild the spec STRICTLY from the exported
   cond/names plus the dataset's config constants, re-run the module's
   generate_sample, and compare to the stored field. Solver-precision agreement
   proves the field is a deterministic function of the condition vector.

`certify` raises CompletenessError on an INCOMPLETE verdict unless the dataset
deliberately keeps a stochastic map and declares it (then the verdict is
recorded as STOCHASTIC_DECLARED and generation may proceed; such datasets are
benchmarks for distributional prediction, judged against the conditional-mean
floor rather than skill 1.0).
"""
from __future__ import annotations

import numpy as np

# Reconstruction must reproduce the stored field at solver precision; the identical
# code path is bitwise-deterministic, so 1e-9 is generous.
REL_L2_TOL = 1e-9

# Witness thresholds (from the round-2 certificate): near-identical conditions with
# an O(1) field difference.
WITNESS_DIST_MAX = 0.5
WITNESS_REL_MIN = 0.1


class CompletenessError(RuntimeError):
    """The dataset's condition vector does not determine its fields."""

    def __init__(self, message: str, record: dict):
        super().__init__(message)
        self.record = record


def nearest_pair_witness(x: np.ndarray, y: np.ndarray) -> dict:
    """Closest pair in standardized condition space vs their relative field difference."""
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64).reshape(len(x), -1)
    mu, sd = x.mean(0), x.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    z = (x - mu) / sd
    d2 = ((z[:, None, :] - z[None, :, :]) ** 2).sum(-1)   # N is small; full pairwise is cheap
    np.fill_diagonal(d2, np.inf)
    i, j = np.unravel_index(np.argmin(d2), d2.shape)
    dist = float(np.sqrt(d2[i, j]))
    scale = 0.5 * (np.linalg.norm(y[i]) + np.linalg.norm(y[j]))
    rel = float(np.linalg.norm(y[i] - y[j]) / (scale + 1e-300))
    return {"closest_pair": [int(i), int(j)],
            "standardized_condition_distance": dist,
            "relative_field_difference": rel,
            "median_pair_distance": float(np.sqrt(np.median(d2[np.isfinite(d2)])))}


def reconstruction_check(mod, cond: np.ndarray, names: list[str], const: dict,
                         resolutions: list[int], hf_res: int, output_time: float,
                         stored_hf: np.ndarray) -> dict:
    """Re-generate one sample from its exported cond alone; compare to the stored HF field."""
    spec = {**const, **dict(zip(names, np.asarray(cond, dtype=np.float64).tolist()))}
    fields, cond2, names2 = mod.generate_sample(spec, list(resolutions), hf_res, output_time)
    pred = np.asarray(fields[hf_res], dtype=np.float64).ravel()
    truth = np.asarray(stored_hf, dtype=np.float64).ravel()
    rel = float(np.linalg.norm(pred - truth) / (np.linalg.norm(truth) + 1e-300))
    roundtrip = (list(names2) == list(names)
                 and np.allclose(np.asarray(cond2, dtype=np.float64),
                                 np.asarray(cond, dtype=np.float64), rtol=0, atol=0))
    verdict = "COMPLETE" if (rel < REL_L2_TOL and roundtrip) else "NOT_REPRODUCED"
    return {"rel_L2": rel, "cond_roundtrip": bool(roundtrip), "verdict": verdict}


def certify(mod, x: np.ndarray, y_hf: np.ndarray, names: list[str], const: dict,
            resolutions: list[int], hf_res: int, output_time: float,
            n_reconstruct: int = 2, declared_stochastic: bool = False) -> dict:
    """Certify a dataset; return the record for meta.json's `condition_completeness`.

    Raises CompletenessError on INCOMPLETE unless `declared_stochastic`.
    """
    x = np.asarray(x, dtype=np.float64)
    record = {"witness": nearest_pair_witness(x, y_hf)}
    if mod is not None:
        n = min(int(n_reconstruct), len(x))
        rels, verdicts = [], []
        for i in range(n):
            rec_i = reconstruction_check(mod, x[i], names, const, resolutions,
                                         hf_res, output_time, np.asarray(y_hf)[i])
            rels.append(rec_i["rel_L2"])
            verdicts.append(rec_i["verdict"])
        record["reconstruction"] = {
            "n_samples": n, "rel_L2_per_sample": rels, "rel_L2_max": max(rels),
            "verdict": "COMPLETE" if all(v == "COMPLETE" for v in verdicts)
                       else "NOT_REPRODUCED"}
        complete = record["reconstruction"]["verdict"] == "COMPLETE"
    else:
        record["reconstruction"] = {
            "verdict": "NOT_POSSIBLE", "reason": "no generator module supplied"}
        w = record["witness"]
        complete = not (w["relative_field_difference"] > WITNESS_REL_MIN
                        and w["standardized_condition_distance"] < WITNESS_DIST_MAX)

    if declared_stochastic:
        record["verdict"] = "STOCHASTIC_DECLARED"
        return record
    if complete and mod is not None:
        record["verdict"] = "COMPLETE"
        return record
    if complete:
        record["verdict"] = "UNDECIDED"          # witness alone cannot PROVE completeness
        return record
    record["verdict"] = "INCOMPLETE"
    raise CompletenessError(
        "condition vector does not determine the field "
        f"(reconstruction: {record['reconstruction'].get('verdict')}, "
        f"witness rel diff {record['witness']['relative_field_difference']:.3f} at "
        f"distance {record['witness']['standardized_condition_distance']:.4f}); "
        "declare stochastic_map semantics if this is deliberate", record)
