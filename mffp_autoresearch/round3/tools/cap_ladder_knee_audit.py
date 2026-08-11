#!/usr/bin/env python
"""cap_ladder_knee_audit.py — audit a trained cap/coverage ladder's step-max knee.

WHAT IT MEASURES
    Given a directory of the round's `result_*.json` files and a cap ladder
    {r1,r2,r3,r4}, this rebuilds the recovery curve

        R(c) = (nRMSE(A0) - nRMSE(arm@c)) / (nRMSE(A0) - nRMSE(A1))

    per HF draw, fold-averages it, and reports FOUR things a bare "the knee is
    at X" cannot tell you:

      * knee / steps / margin          — the registered step-max statistic;
      * the ALGEBRAIC HIT CONDITION    — for a nominated rung (--c-pred), the
                                         value R(r3) must clear for the knee to
                                         land there,
                                             R(r3) > max((1+R(r2))/2, 2R(r2)-R(r1)),
                                         and the signed deficit. Turns "it
                                         missed" into "it missed by 0.33 R";
      * the SPACING-INVARIANT knee     — the same step-max after dividing each
                                         step by its log-width (R gained per nat
                                         of cap). A geometric ladder is neutral;
                                         a ladder whose top step spans most of
                                         the pool is not, and this says by how
                                         much the verdict depends on that;
      * c50                            — the log-interpolated cap at which R
                                         crosses 0.5 (a scale-free "how many
                                         rows does half the value cost").

    nRMSE is READ from the result JSONs (`per_dataset[ds].nRMSE`); nothing is
    recomputed, so the audit inherits the run's own metric definition.

PROVENANCE
    r3s3_lf_value-B3 mechanism turns 1 and 3. On that card it reproduced part
    5's knees on 5/5 cells from the raw JSONs, quantified the falsified cells'
    deficits (allen_cahn +0.14..+0.16 R, fisher_kpp +0.31..+0.46 R) and showed
    the registered verdict flips on 2 of 5 cells under log-width normalisation
    (allen_cahn -> 20 at seed 1, phase_field_crystal -> FULL at seeds 1-2).

CAVEATS
    * The knee statistic is only defined for a 4-rung ladder (3 steps).
    * `R` is undefined when nRMSE(A0) == nRMSE(A1); such cells are reported
      `degenerate` rather than silently dropped.
    * The spacing-invariant knee is a DIAGNOSTIC, never a re-adjudication: a
      pre-registered card is adjudicated on the statistic it sealed.

INVOCATION
    python tools/cap_ladder_knee_audit.py \
        --eval-root <outputs>/<stream>/<batch>/eval \
        --dataset sharp__allen_cahn_2d --ladder 1,5,20,395 \
        --seeds 0,1,2 --draws 0,1,2 --epochs 200 --n-hf 5 --c-pred 20 \
        --out /tmp/ac_knee_audit.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

DEFAULT_TEMPLATE = "result_{arm}__{ds}__d{draw}__n{nhf}__c{cap}__e{epochs}__s{seed}.json"


def read_nrmse(path: Path, ds: str) -> float:
    d = json.loads(path.read_text())
    return float(d["per_dataset"][ds]["nRMSE"])


def c50(caps, Rs):
    caps = np.asarray(caps, dtype=float)
    Rs = np.asarray(Rs, dtype=float)
    for i in range(len(caps) - 1):
        if Rs[i] < 0.5 <= Rs[i + 1]:
            t = (0.5 - Rs[i]) / (Rs[i + 1] - Rs[i])
            return float(np.exp(np.log(caps[i]) + t * (np.log(caps[i + 1]) - np.log(caps[i]))))
    return None


def audit_seed(root, tmpl, ds, ladder, draws, seed, arms, nhf, epochs, c_pred):
    r1, r2, r3, r4 = ladder
    R = {}
    per_draw = {}
    for c in ladder:
        vals = []
        for dw in draws:
            def p(arm, cap):
                return root / tmpl.format(arm=arm, ds=ds, draw=dw, nhf=nhf,
                                          cap=cap, epochs=epochs, seed=seed)
            a0 = read_nrmse(p(arms["a0"], 0), ds)
            a1 = read_nrmse(p(arms["a1"], 0), ds)
            arm = a1 if c == r4 else read_nrmse(p(arms["cap"], c), ds)
            if abs(a0 - a1) < 1e-15:
                return {"degenerate": True, "reason": "nRMSE(A0) == nRMSE(A1)"}
            vals.append((a0 - arm) / (a0 - a1))
            per_draw.setdefault(dw, {})[c] = {"nrmse_arm": arm, "nrmse_a0": a0, "nrmse_a1": a1}
        R[c] = float(np.mean(vals))

    steps = [R[ladder[i + 1]] - R[ladder[i]] for i in range(3)]
    srt = sorted(steps, reverse=True)
    K = ladder[int(np.argmax(steps)) + 1]
    widths = [float(np.log(ladder[i + 1]) - np.log(ladder[i])) for i in range(3)]
    dens = [steps[i] / widths[i] for i in range(3)]
    dsrt = sorted(dens, reverse=True)
    K_log = ladder[int(np.argmax(dens)) + 1]

    out = {
        "R_foldmean": {str(c): round(R[c], 6) for c in ladder},
        "steps": [round(x, 6) for x in steps],
        "K": K,
        "margin_R": round(srt[0] - srt[1], 6),
        "log_widths": [round(w, 4) for w in widths],
        "step_density_R_per_nat": [round(x, 6) for x in dens],
        "K_log_width_normalised": K_log,
        "margin_density": round(dsrt[0] - dsrt[1], 6),
        "spacing_invariant": bool(K_log == K),
        "c50": c50(ladder, [R[c] for c in ladder]),
        "per_draw_nrmse": {dw: {str(c): v for c, v in d.items()} for dw, d in per_draw.items()},
    }
    if c_pred is not None:
        k = ladder.index(c_pred)
        if k == 0:
            out["hit_condition"] = {"note": "c_pred is the bottom rung; the knee can never land there"}
        else:
            # Solve for the smallest x = R(c_pred) that makes the step INTO c_pred
            # the strict maximum. Steps that do not touch c_pred are constants in x;
            # the step OUT of c_pred (if any) shrinks as x grows.
            reqs = []
            for j in range(3):
                if j == k - 1:
                    continue
                if j == k:                       # x - R[k-1] > R[k+1] - x
                    reqs.append((R[ladder[k - 1]] + R[ladder[k + 1]]) / 2.0)
                else:                            # x - R[k-1] > s_j (constant in x)
                    reqs.append(R[ladder[k - 1]] + steps[j])
            need = max(reqs)
            out["hit_condition"] = {
                "c_pred": c_pred,
                "R_required_at_c_pred": round(need, 6),
                "R_achieved_at_c_pred": round(R[c_pred], 6),
                "deficit_R": round(need - R[c_pred], 6),
                "hit": bool(K == c_pred),
                "_form": ("smallest R(c_pred) making the step into c_pred the strict max; "
                          "for the third rung of a 4-rung ladder this is "
                          "max((1+R(r2))/2, 2R(r2)-R(r1))"),
            }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--eval-root", required=True, type=Path, help="directory holding result_*.json")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--ladder", required=True, help="4 comma-separated caps, ascending, e.g. 1,5,20,395")
    ap.add_argument("--seeds", default="0", help="comma-separated training seeds")
    ap.add_argument("--draws", default="0", help="comma-separated HF draws, or 'native'")
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--n-hf", type=int, default=5)
    ap.add_argument("--arm-a0", default="A0_nolf")
    ap.add_argument("--arm-a1", default="A1_lf_all")
    ap.add_argument("--arm-cap", default="A3c_lf_uncov_cap")
    ap.add_argument("--c-pred", type=int, default=None, help="rung the prediction nominated")
    ap.add_argument("--name-template", default=DEFAULT_TEMPLATE)
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()

    ladder = [int(x) for x in a.ladder.split(",")]
    if len(ladder) != 4 or sorted(ladder) != ladder or len(set(ladder)) != 4:
        raise SystemExit("--ladder must be 4 strictly ascending caps")
    seeds = [int(s) for s in a.seeds.split(",")]
    draws = a.draws.split(",")
    arms = {"a0": a.arm_a0, "a1": a.arm_a1, "cap": a.arm_cap}

    res = {"dataset": a.dataset, "ladder": ladder, "seeds": seeds, "draws": draws,
           "eval_root": str(a.eval_root), "arms": arms, "per_seed": {}}
    for sd in seeds:
        res["per_seed"][sd] = audit_seed(a.eval_root, a.name_template, a.dataset, ladder,
                                         draws, sd, arms, a.n_hf, a.epochs, a.c_pred)

    ks = [res["per_seed"][s].get("K") for s in seeds]
    kl = [res["per_seed"][s].get("K_log_width_normalised") for s in seeds]
    res["K_per_seed"] = ks
    res["K_unanimous"] = len(set(ks)) == 1
    res["K_log_per_seed"] = kl
    res["verdict_spacing_robust"] = ks == kl

    print(f"dataset            {a.dataset}")
    print(f"ladder             {ladder}")
    print(f"K per seed         {ks}  (unanimous={res['K_unanimous']})")
    print(f"K log-normalised   {kl}  (spacing-robust={res['verdict_spacing_robust']})")
    for sd in seeds:
        p = res["per_seed"][sd]
        if p.get("degenerate"):
            print(f"  seed {sd}: DEGENERATE ({p['reason']})")
            continue
        line = (f"  seed {sd}: R {list(p['R_foldmean'].values())} steps {p['steps']} "
                f"margin_R {p['margin_R']} c50 {p['c50']}")
        if "hit_condition" in p and "deficit_R" in p["hit_condition"]:
            h = p["hit_condition"]
            line += (f"\n           hit@{h['c_pred']}: need {h['R_required_at_c_pred']} "
                     f"got {h['R_achieved_at_c_pred']} deficit {h['deficit_R']} hit={h['hit']}")
        print(line)

    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(res, indent=1, default=float))
        print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
