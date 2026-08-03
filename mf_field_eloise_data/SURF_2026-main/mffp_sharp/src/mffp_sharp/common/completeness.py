"""Condition-completeness certificate as a generation gate.

Three training-free tests (the round-2 audit instruments, ADR r2-0003, made
first-class so every generated dataset carries a checkable verdict instead of an
asserted claim; hardened 2026-08-03 per CONDITION_COMPLETENESS_BRIEFING §8.1):

1. NEAREST-PAIR WITNESS — standardize the condition vectors, find the closest
   pair, compare their fields. Near-zero condition distance with O(1) field
   difference proves a driver of the solution is missing from the vector.
   The witness is a VETO: when it fires, the verdict is INCOMPLETE even if
   reconstruction succeeds, and its distance threshold scales with the
   dataset's own median pair distance so dimension inflation cannot disarm it.
2. RECONSTRUCTION CERTIFICATE — rebuild the spec STRICTLY from the exported
   cond/names plus the dataset's config constants, re-run the module's
   generate_sample, and compare to the stored field. Solver-precision agreement
   proves the field is a deterministic function of the condition vector.
3. CONTINUITY PROBE — reconstruction alone cannot distinguish a genuine
   coefficient from an opaque RNG seed: both re-solve to machine precision, but
   only the first is learnable. The probe perturbs each exported dimension at
   two step sizes (eps and eps/2, at the coarsest rung): a smooth map's
   response shrinks with the step (chaotic amplification included — the
   finite-time map is still differentiable), a hash/seed dimension responds
   with a step function (large at both scales, or a jump at one scale and
   nothing at the other), and a dimension with spread but exactly zero
   influence is dead weight. NONSMOOTH and DEAD dimensions are fatal.

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
# an O(1) field difference. The absolute distance bound is kept for low-dimension
# datasets; the relative bound (fraction of the dataset's own median pair distance)
# keeps the witness armed at any condition dimension.
WITNESS_DIST_MAX = 0.5
WITNESS_REL_MIN = 0.1
WITNESS_DIST_MEDIAN_FRAC = 0.1

# Continuity-probe thresholds. eps is PROBE_EPS_FRAC of each dimension's spread.
# The discriminator is SHRINKAGE, not magnitude: a smooth map's response at eps/2
# is ~half its response at eps (chaotic amplification included), while a hash
# dimension's response is step-like — the same O(1) size at both scales, or a
# jump at one scale and exactly nothing at the other. PROBE_MEANINGFUL is only a
# noise floor so solver-precision jitter can't be misread as a non-shrinking
# response; a response of exactly ~0 at both steps from a dimension with spread
# is dead weight (e.g. an int-cast seed between integer boundaries).
PROBE_EPS_FRAC = 0.01
PROBE_TINY = 1e-12
PROBE_MEANINGFUL = 0.05
PROBE_SHRINK = 0.75


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


def _witness_fires(w: dict) -> bool:
    """The witness veto: a close pair (absolutely, or relative to the dataset's own
    pair-distance scale) whose fields differ at O(1)."""
    close = (w["standardized_condition_distance"] < WITNESS_DIST_MAX
             or w["standardized_condition_distance"]
             < WITNESS_DIST_MEDIAN_FRAC * w["median_pair_distance"])
    return bool(close and w["relative_field_difference"] > WITNESS_REL_MIN)


def continuity_probe(mod, cond: np.ndarray, names: list[str], const: dict,
                     coarse_res: int, output_time: float,
                     x_std: np.ndarray) -> dict:
    """Two-scale smoothness probe of the map cond -> field, one dimension at a time.

    Solves at the coarsest rung only. For each exported dimension k with spread,
    perturb by eps_k = PROBE_EPS_FRAC * std_k and by eps_k/2:

      SMOOTH    response shrinks with the step (or is small at both) — includes
                chaotic amplification, whose finite-time map is differentiable;
      NONSMOOTH step-function response: large at both scales without shrinking,
                or a jump at one scale and exactly nothing at the other — the
                signature of a hash/seed/nominal dimension;
      DEAD      spread but exactly zero response at both scales — an exported
                number the field does not depend on locally (int-cast seeds
                between integer boundaries, padding columns).
    """
    def solve(c):
        spec = {**const, **dict(zip(names, np.asarray(c, dtype=np.float64).tolist()))}
        fields, _, _ = mod.generate_sample(spec, [coarse_res], coarse_res, output_time)
        return np.asarray(fields[coarse_res], dtype=np.float64).ravel()

    base = solve(cond)
    base_norm = float(np.linalg.norm(base))
    record = {"eps_frac": PROBE_EPS_FRAC, "coarse_res": int(coarse_res), "per_dim": []}
    if base_norm < 1e-300:
        record["verdict"] = "NOT_POSSIBLE"
        record["reason"] = "base field has zero norm"
        return record
    worst = "SMOOTH"
    for k, name in enumerate(names):
        sd = float(x_std[k])
        if sd == 0.0:
            record["per_dim"].append({"name": name, "class": "CONSTANT"})
            continue
        eps = PROBE_EPS_FRAC * sd
        r = []
        for e in (eps, eps / 2.0):
            c = np.asarray(cond, dtype=np.float64).copy()
            c[k] += e
            r.append(float(np.linalg.norm(solve(c) - base) / base_norm))
        r1, r2 = r
        if r1 < PROBE_TINY and r2 < PROBE_TINY:
            cls = "DEAD"
        elif max(r1, r2) > PROBE_MEANINGFUL and min(r1, r2) < PROBE_TINY:
            cls = "NONSMOOTH"          # step function: a jump at one scale, nothing at the other
        elif r1 > PROBE_MEANINGFUL and r2 > PROBE_SHRINK * r1:
            cls = "NONSMOOTH"          # meaningful response that does not shrink with the step
        else:
            cls = "SMOOTH"
        record["per_dim"].append({"name": name, "r_eps": r1, "r_half_eps": r2, "class": cls})
        if cls in ("DEAD", "NONSMOOTH"):
            worst = "NONSMOOTH" if cls == "NONSMOOTH" or worst == "NONSMOOTH" else "DEAD"
    record["verdict"] = worst if worst != "SMOOTH" else "SMOOTH"
    return record


def certify(mod, x: np.ndarray, y_hf: np.ndarray, names: list[str], const: dict,
            resolutions: list[int], hf_res: int, output_time: float,
            n_reconstruct: int = 2, declared_stochastic: bool = False,
            probe_continuity: bool = True) -> dict:
    """Certify a dataset; return the record for meta.json's `condition_completeness`.

    Raises CompletenessError on INCOMPLETE unless `declared_stochastic`.
    """
    x = np.asarray(x, dtype=np.float64)
    record = {"witness": nearest_pair_witness(x, y_hf)}
    reconstruction_failure = None
    if mod is not None:
        n = min(int(n_reconstruct), len(x))
        rels, verdicts = [], []
        try:
            for i in range(n):
                rec_i = reconstruction_check(mod, x[i], names, const, resolutions,
                                             hf_res, output_time, np.asarray(y_hf)[i])
                rels.append(rec_i["rel_L2"])
                verdicts.append(rec_i["verdict"])
        except Exception as e:      # spec not reconstructible from flat cond (e.g. euler)
            reconstruction_failure = repr(e)
    witness_veto = _witness_fires(record["witness"])
    if mod is not None and reconstruction_failure is None:
        record["reconstruction"] = {
            "n_samples": n, "rel_L2_per_sample": rels, "rel_L2_max": max(rels),
            "verdict": "COMPLETE" if all(v == "COMPLETE" for v in verdicts)
                       else "NOT_REPRODUCED"}
        complete = record["reconstruction"]["verdict"] == "COMPLETE"
        witness_only = False
        if probe_continuity and complete:
            probe = continuity_probe(mod, x[0], names, const, min(resolutions),
                                     output_time, x.std(0))
            record["continuity_probe"] = probe
            if probe["verdict"] in ("NONSMOOTH", "DEAD"):
                complete = False
    else:
        record["reconstruction"] = {
            "verdict": "NOT_POSSIBLE",
            "reason": reconstruction_failure or "no generator module supplied"}
        complete = not witness_veto
        witness_only = True
    # The witness is a veto, not a note: dimension inflation cannot disarm it,
    # and reconstruction success cannot override it.
    if witness_veto:
        complete = False

    if declared_stochastic:
        record["verdict"] = "STOCHASTIC_DECLARED"
        return record
    if complete and not witness_only:
        record["verdict"] = "COMPLETE"
        return record
    if complete:
        record["verdict"] = "UNDECIDED"          # witness alone cannot PROVE completeness
        return record
    record["verdict"] = "INCOMPLETE"
    probe_note = ""
    if record.get("continuity_probe", {}).get("verdict") in ("NONSMOOTH", "DEAD"):
        bad = [d["name"] for d in record["continuity_probe"]["per_dim"]
               if d.get("class") in ("NONSMOOTH", "DEAD")]
        probe_note = (f"; continuity probe flags {record['continuity_probe']['verdict']}"
                      f" dimension(s) {bad} — reconstruction succeeds but the map is not"
                      " learnable through them (seed/nominal export?)")
    raise CompletenessError(
        "condition vector does not determine the field "
        f"(reconstruction: {record['reconstruction'].get('verdict')}, "
        f"witness rel diff {record['witness']['relative_field_difference']:.3f} at "
        f"distance {record['witness']['standardized_condition_distance']:.4f}"
        f"{probe_note}); "
        "declare stochastic_map semantics if this is deliberate", record)
