#!/usr/bin/env python
"""Model-library DOMINANCE audit — is a router/super-learner licensed at all?

Provenance: `s4_hybrid_routing-B3` mechanism analysis, turn 3
(`worktrees/s4_hybrid_routing/B3/scratchpad/reanalysis_turn_3.py`, findings F10 /
F11 in card `experiment_cards/s4_hybrid_routing/batch_3/B3.json` part 6).

WHAT IT MEASURES
----------------
A discrete super learner / router / mixture-of-experts over a library of K
predictors can only pay if **no single member weakly dominates the rest**. s4-B3
built a 2-element library and then, in the same card, changed one member's
training target so that it became `other_member + gated_correction` — i.e. a
strict SUPERSET of the other. Over a nested library no-harm is a theorem and
routing gain is impossible, so the router scored *bit-identically* to its own
donor arm and to a deliberately rule-inverted control. Nobody noticed until the
mechanism turn.

Given each library member's scored result JSON, this tool reports:

  * the per-dataset nRMSE / skill table;
  * the WEAK-DOMINANCE matrix at each dataset's certified relative floor —
    "does member A beat member B everywhere?";
  * `DEGENERATE_TIES`: datasets where two members are numerically IDENTICAL
    (a held-out gain line search containing 0 collapsing one member onto
    another), which masquerade as measurement ties in a rule table;
  * the panel geomean of every CONSTANT router ("always member m"), of the
    per-dataset ORACLE, and of any shipped selector you pass in;
  * `routing_headroom_pct` = best constant router vs the oracle. If that is
    inside the geomean floor, **the router is not licensed** and the lever is
    what the members CONTAIN, not how they are mixed.

Complements `routing_headroom.py` (s4-B1: the ceiling of a richer *gate* over one
scalar alpha, within a single `base + alpha*correction` model) and
`persample_gate_audit.py` (s6-B2: what a SHIPPED per-sample gate realised). This
tool works one level up — between whole arms — and needs nothing but their result
JSONs.

INPUT FORMAT
------------
`--arm NAME=PATH` (repeatable). PATH is any JSON with
`per_dataset.<dataset>.{nRMSE, skill}` — i.e. the round's
`score_panel.py` output `result_{panel,guard}_<arm>_s<seed>.json`.

USAGE
-----
    python tools/library_dominance_audit.py \
        --arm lsi=$OUT/result_panel_lsi_alone_s0.json \
        --arm dc=$OUT/result_panel_dc_cleaned_s0.json \
        --arm shipped=$OUT/result_panel_router_s0.json \
        --selector shipped
"""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _round_root() -> Path:
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True, cwd=Path(__file__).resolve().parent
                         ).stdout.strip()
    return Path(top) / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
from nrmse import panel_geomean                              # noqa: E402

IDENTICAL_REL = 1e-12     # below this relative gap two members are the SAME object


def load_floors(path: Path) -> dict:
    """dataset -> certified relative floor (min_claimable_effect / mean_skill)."""
    if not path.exists():
        return {}
    d = json.load(open(path))
    out = {}
    for k, v in d.items():
        if k.startswith("_") or not isinstance(v, dict):
            continue
        mce, ms = v.get("min_claimable_effect"), v.get("mean_skill")
        if mce is not None and ms:
            out[k] = float(mce) / float(ms)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--arm", action="append", required=True, metavar="NAME=PATH",
                    help="library member; repeat once per member (>=2)")
    ap.add_argument("--selector", default=None,
                    help="name of an arm that is a SHIPPED selector, not a library "
                         "member (excluded from the constant-router comparison)")
    ap.add_argument("--floors", default=str(ROUND / "state" / "noise_floor.json"))
    ap.add_argument("--default-floor", type=float, default=0.0,
                    help="relative floor for datasets with no certified entry "
                         "(guard sets have none; 0.0 = any non-zero gap resolves)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    arms = {}
    for spec in a.arm:
        if "=" not in spec:
            raise SystemExit(f"--arm expects NAME=PATH, got {spec!r}")
        nm, pth = spec.split("=", 1)
        j = json.load(open(pth))
        arms[nm] = {ds: float(v["nRMSE"]) for ds, v in j["per_dataset"].items()}
        arms[nm + "__skill"] = {ds: float(v["skill"]) for ds, v in j["per_dataset"].items()}
    names = [n for n in arms if not n.endswith("__skill")]
    members = [n for n in names if n != a.selector]
    if len(members) < 2:
        raise SystemExit("need >= 2 library members (excluding --selector)")
    datasets = sorted(set(arms[names[0]]))
    for n in names:
        if sorted(arms[n]) != datasets:
            raise SystemExit(f"arm {n} covers a different dataset set")

    floors = load_floors(Path(a.floors))
    fl = {ds: floors.get(ds, a.default_floor) for ds in datasets}
    res = {"arms": names, "members": members, "selector": a.selector,
           "datasets": datasets, "floors": fl}

    print("=== per-dataset nRMSE ===")
    print(f"{'dataset':32s} {'floor':>7s} " + " ".join(f"{n:>13s}" for n in names))
    for ds in datasets:
        print(f"{ds:32s} {fl[ds]:7.3f} " + " ".join(f"{arms[n][ds]:13.6e}" for n in names))

    # ── weak dominance at the floor ────────────────────────────────────────
    print("\n=== weak dominance (A beats B on every dataset, at that dataset's floor) ===")
    dom = {}
    for x, y in itertools.permutations(members, 2):
        ok = all(arms[x][ds] <= arms[y][ds] * (1.0 + fl[ds]) for ds in datasets)
        strict = sum(arms[x][ds] < arms[y][ds] * (1.0 - fl[ds]) for ds in datasets)
        dom[f"{x}>{y}"] = {"weakly_dominates": bool(ok), "strictly_better_on": int(strict)}
        print(f"  {x:>13s} >= {y:<13s} weak_dominance={str(ok):5s} "
              f"strictly better on {strict}/{len(datasets)}")
    res["dominance"] = dom
    dominators = [m for m in members
                  if all(dom[f"{m}>{o}"]["weakly_dominates"] for o in members if o != m)]
    res["dominating_members"] = dominators

    # ── degenerate ties (members that are the SAME object) ─────────────────
    print("\n=== degenerate ties (two members numerically IDENTICAL) ===")
    deg = {}
    for x, y in itertools.combinations(members, 2):
        hits = [ds for ds in datasets
                if abs(arms[x][ds] - arms[y][ds]) <= IDENTICAL_REL * max(arms[y][ds], 1e-300)]
        if hits:
            deg[f"{x}=={y}"] = hits
            print(f"  {x} == {y} on: {', '.join(hits)}")
    if not deg:
        print("  none")
    res["degenerate_ties"] = deg

    # ── constant routers, oracle, shipped selector ─────────────────────────
    print("\n=== geomean of every constant router vs the per-dataset oracle ===")
    sk = lambda n: {ds: arms[n + "__skill"][ds] for ds in datasets}          # noqa: E731
    geo = {n: panel_geomean(sk(n)) for n in names}
    oracle_sk = {ds: min(arms[m + "__skill"][ds] for m in members) for ds in datasets}
    g_oracle = panel_geomean(oracle_sk)
    best_const = min(members, key=lambda m: geo[m])
    for n in names:
        tag = ("  <- SHIPPED SELECTOR" if n == a.selector
               else ("  <- best constant router" if n == best_const else ""))
        print(f"  always_{n:<16s} {geo[n]:.6f}{tag}")
    print(f"  {'per-dataset ORACLE':<24s} {g_oracle:.6f}")
    head = 100.0 * (geo[best_const] - g_oracle) / g_oracle
    res["geomeans"] = geo
    res["oracle_geomean"] = g_oracle
    res["best_constant_router"] = best_const
    res["routing_headroom_pct"] = head
    print(f"\n  routing_headroom_pct (best constant vs oracle) = {head:+.3f} %")
    if a.selector:
        cap = 100.0 * (geo[a.selector] - g_oracle) / g_oracle
        res["selector_vs_oracle_pct"] = cap
        res["selector_vs_best_constant_pct"] = 100.0 * (geo[a.selector] - geo[best_const]) / geo[best_const]
        print(f"  shipped selector vs oracle           = {cap:+.3f} %")
        print(f"  shipped selector vs best constant    = "
              f"{res['selector_vs_best_constant_pct']:+.3f} %")

    verdict = ("NOT LICENSED: one member weakly dominates the whole library "
               f"({dominators}); a selector cannot pay more than the floor. The lever is "
               "what the members CONTAIN, not how they are mixed."
               if dominators else
               "LICENSED: no member weakly dominates; routing_headroom_pct is the prize a "
               "perfect selector would win over the best constant router. Compare it to the "
               "geomean floor before building the selector.")
    res["verdict"] = verdict
    print("\n  VERDICT: " + verdict)

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        with open(a.out, "w") as f:
            json.dump(res, f, indent=1, default=float)
        print("  wrote", a.out)


if __name__ == "__main__":
    main()
