#!/usr/bin/env python
"""Could this A-vs-B reading have fired at all, and is it contaminated?

ROUND-2 tool, promoted from `r2s4_diag-B3` mechanism turns 1-2.

Two failure modes bite any card that reads a paired arm difference
`delta = skill(baseline) - skill(arm)` against a threshold:

1. **The reading could not have fired.** Two arms fitted by the same procedure
   on nearly the same targets end up nearly the same FUNCTION, so |delta| is
   bounded by how far apart the functions are, regardless of the science. With

       D(a, b) := mean_i ||a_i - b_i||_2 / ||y_i||_2   / skill_denominator

   (the round's nRMSE kernel with the TRUTH denominator held fixed, so a
   prediction-to-prediction distance is on the same scale as either one's
   distance to the truth), the triangle inequality gives

       |skill(baseline) - skill(arm)| <= D(arm, baseline)  =: realised ceiling

   IDENTICALLY. `headroom = ceiling / threshold`. If headroom < 1 the clause was
   arithmetically incapable of firing in the positive direction and its "null
   survived" is guaranteed by construction, not evidence.

2. **The reading is contaminated by a FUNCTION-CLASS term.** When `arm` is
   produced by a different estimator than `baseline`, `delta` silently sums two
   unrelated things. With a CONTROL column -- the SAME estimator as `arm`, fitted
   on the SAME rows, but on the reference target the baseline was fitted on:

       delta = [skill(baseline) - skill(control)]   function-class term
             + [skill(control)  - skill(arm)]       target term

   Only the target term answers "what did the treatment's TARGET buy". The
   function-class term is an architecture comparison that would exist with the
   treatment removed entirely. On r2s4-B3's helmholtz the two terms were
   -21.721113 and +21.047550 skill units and nearly cancelled: the reported
   -0.673563 was the residue of two large unrelated effects.

3. **Row-count asymmetry.** If `arm` and `baseline` were fitted on different
   numbers of rows, `delta` carries a sample-size bias. Pass `--matched` (the
   arm refitted at the baseline's row count) and the tool prices it. On r2s4-B3
   this bias was 0.178303 skill units -- enough to move a falsification clause
   across its own threshold by itself.

Read-only. Every score goes through `round2/eval/nrmse.py`; the skill
denominator defaults to the frozen `round2/eval/copylf_baselines.json` entry for
`--dataset`.

CAVEAT that cost the source card a re-run: prediction dumps are NOT always in
dataset row order (r2s4-B3's `preds_oof_*.npz` carry an `oof_row_index`
permutation). This tool only ever compares arrays taken from the dumps you pass,
so it is safe by construction -- but if you join a dump to loader-ordered data
yourself, permute first and assert against a pre-registered value.

Invocation
----------
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/ledger_contamination_audit.py \
        --truth  <outputs>/preds_oof_sharp__cahn_hilliard_e200_s0.npz:hf_true \
        --baseline T0=<same npz>:T0_cond_only \
        --arm      ridge=<same npz>:proj_ridge \
        --control  ridge_on_hf=<control npz>:pred \
        --matched  ridge_n280=<matched npz>:pred \
        --dataset sharp__cahn_hilliard --threshold 0.1847460640603149 \
        --out audit.json

`NAME=path.npz[:key]` everywhere (key defaults to `pred`), so both dump layouts
work: one npz holding every arm (r2s4) or one npz per arm (r2s1).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROUND_ROOT = HERE.parent
sys.path.insert(0, str(ROUND_ROOT / "eval"))
import nrmse as R                                             # noqa: E402


def parse_ref(spec: str, default_key: str = "pred"):
    """'NAME=path.npz[:key]' or 'path.npz[:key]' -> (name, path, key)."""
    name = None
    body = spec
    if "=" in spec and not spec.split("=", 1)[0].endswith(".npz"):
        name, body = spec.split("=", 1)
    if ":" in body and not body.rsplit(":", 1)[1].endswith(".npz"):
        path, key = body.rsplit(":", 1)
    else:
        path, key = body, default_key
    return (name or pathlib.Path(path).stem), path, key


def load_ref(spec: str, default_key: str = "pred"):
    name, path, key = parse_ref(spec, default_key)
    z = np.load(path)
    if key not in z.files:
        raise SystemExit(f"{path}: key {key!r} not present; has {list(z.files)}")
    arr = np.asarray(z[key], dtype=np.float64)
    if arr.ndim != 2:
        arr = arr.reshape(arr.shape[0], -1)
    return name, arr


def D(a: np.ndarray, b: np.ndarray, y: np.ndarray, denom: float) -> float:
    """mean_i ||a_i-b_i||/||y_i||, in skill units. D(x, y) == skill(x)."""
    den = np.linalg.norm(y, axis=1)
    if (den == 0).any():
        raise SystemExit("zero-norm truth row")
    return float(np.mean(np.linalg.norm(a - b, axis=1) / den)) / denom


def cos_error_fields(a: np.ndarray, b: np.ndarray, y: np.ndarray) -> float:
    ea, eb = a - y, b - y
    num = (ea * eb).sum(axis=1)
    den = np.linalg.norm(ea, axis=1) * np.linalg.norm(eb, axis=1)
    return float(np.mean(num / np.maximum(den, 1e-30)))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--truth", required=True, help="NAME=path.npz[:key] of the target")
    ap.add_argument("--baseline", required=True, help="the reference arm")
    ap.add_argument("--arm", required=True, help="the arm being read against it")
    ap.add_argument("--control", default=None,
                    help="the ARM's estimator fitted on the BASELINE's target "
                         "(enables the function-class / target decomposition)")
    ap.add_argument("--matched", default=None,
                    help="the ARM refitted at the BASELINE's row count "
                         "(enables the row-count bias reading)")
    ap.add_argument("--dataset", default=None,
                    help="panel dataset name -> frozen copy-LF skill denominator")
    ap.add_argument("--skill_denominator", type=float, default=None,
                    help="override the denominator (default 1.0 if no --dataset)")
    ap.add_argument("--threshold", type=float, default=None,
                    help="the clause's operative threshold, in skill units")
    ap.add_argument("--noise_floor", default=None,
                    help="state/noise_floor.json; used when --threshold is absent")
    ap.add_argument("--mce_key", default="min_claimable_effect")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    _, y = load_ref(a.truth, "hf_true")
    denom = a.skill_denominator
    denom_src = "explicit"
    if denom is None and a.dataset:
        cl = json.loads((ROUND_ROOT / "eval" / "copylf_baselines.json").read_text())
        if a.dataset not in cl:
            raise SystemExit(f"unknown dataset {a.dataset!r} in copylf_baselines.json")
        denom, denom_src = cl[a.dataset]["test_nrmse"], "copylf_baselines.json"
    if denom is None:
        denom, denom_src = 1.0, "none (raw nRMSE units)"

    thr = a.threshold
    thr_src = "explicit"
    if thr is None and a.noise_floor and a.dataset:
        nf = json.loads(pathlib.Path(a.noise_floor).read_text())
        node = nf.get(a.dataset, {})
        thr = node.get(a.mce_key)
        thr_src = f"{a.noise_floor}:{a.dataset}.{a.mce_key}"

    arms = {}
    for spec, role in ((a.baseline, "baseline"), (a.arm, "arm"),
                       (a.control, "control"), (a.matched, "matched")):
        if spec is None:
            continue
        name, arr = load_ref(spec)
        if arr.shape != y.shape:
            raise SystemExit(f"{role} {name}: shape {arr.shape} != truth {y.shape}")
        arms[role] = {"name": name, "arr": arr}

    skill = {r: R.skill(R.nrmse(v["arr"], y), denom) for r, v in arms.items()}
    ceiling = D(arms["arm"]["arr"], arms["baseline"]["arr"], y, denom)
    delta = skill["baseline"] - skill["arm"]

    out = {
        "_tool": "ledger_contamination_audit.py",
        "_nrmse_def_hash": R.NRMSE_DEF_HASH,
        "dataset": a.dataset,
        "n_rows": int(y.shape[0]), "n_cells": int(y.shape[1]),
        "skill_denominator": denom, "skill_denominator_source": denom_src,
        "arm_names": {r: v["name"] for r, v in arms.items()},
        "skill": skill,
        "delta_baseline_minus_arm": delta,
        "threshold": thr, "threshold_source": thr_src if thr is not None else None,
        "ceiling_realised": ceiling,
        "cos_error_fields_arm_vs_baseline":
            cos_error_fields(arms["arm"]["arr"], arms["baseline"]["arr"], y),
    }
    if thr:
        out["headroom"] = ceiling / thr
        out["could_not_fire"] = bool(ceiling < thr)
        out["delta_exceeds_threshold"] = bool(delta > thr)
        out["abs_delta_over_ceiling"] = abs(delta) / ceiling if ceiling else None

    if "control" in arms:
        fn_class = skill["baseline"] - skill["control"]
        target = skill["control"] - skill["arm"]
        out["decomposition"] = {
            "function_class_term": fn_class,
            "target_term": target,
            "identity_residual": delta - (fn_class + target),
            "target_term_exceeds_threshold":
                (None if not thr else bool(target > thr)),
            "contaminated_fraction":
                (abs(fn_class) / (abs(fn_class) + abs(target))
                 if (abs(fn_class) + abs(target)) else None),
        }
    if "matched" in arms:
        out["row_count"] = {
            "skill_arm": skill["arm"], "skill_arm_matched": skill["matched"],
            "row_count_bias": skill["arm"] - skill["matched"],
            "delta_matched": skill["baseline"] - skill["matched"],
            "delta_matched_exceeds_threshold":
                (None if not thr else bool(skill["baseline"] - skill["matched"] > thr)),
        }

    verdict = []
    if thr and out["could_not_fire"]:
        verdict.append("COULD_NOT_FIRE: |delta| is bounded by the realised ceiling "
                       f"{ceiling:.6g} < threshold {thr:.6g}; a surviving null here "
                       "is guaranteed by construction, not evidence")
    if "decomposition" in out and out["decomposition"]["contaminated_fraction"] \
            is not None and out["decomposition"]["contaminated_fraction"] > 0.5:
        verdict.append("CONTAMINATED: the function-class term carries "
                       f"{100*out['decomposition']['contaminated_fraction']:.1f}% of "
                       "the reading; quote the target term instead")
    if "row_count" in out and thr and out["delta_exceeds_threshold"] \
            and not out["row_count"]["delta_matched_exceeds_threshold"]:
        verdict.append("ROW_COUNT_ARTIFACT: the reading clears its threshold at the "
                       "unmatched row count and does not at the matched one")
    out["verdict"] = verdict or ["no contamination flag fired"]

    print(json.dumps({k: v for k, v in out.items() if k != "arm_names"}, indent=1))
    print("\narms:", out["arm_names"])
    for v in out["verdict"]:
        print(f"  [!] {v}")
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
