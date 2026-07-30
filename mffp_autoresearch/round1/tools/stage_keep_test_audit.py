#!/usr/bin/env python3
"""stage_keep_test_audit.py -- is a multi-STAGE model's own keep/discard test honest?

Provenance: s4_hybrid_routing-B2 mechanism turn 1 (card part 6, findings F1-F5).

Many families in this round are staged: fit a base, fit a correction, then a
LINE SEARCH / KEEP TEST decides whether to switch the new component on
(`alpha`), and sometimes a further joint fine-tune is kept only if a held-out
error improves. Every such test is only as honest as the BASE it is scored
against. If the base saw the validation samples during its own training, the
test is scored on memorised samples (Wolpert 1992) and can be sign-inverted
against the truth -- which is exactly what s4-B2's stage 3 does on 5 of 5 cells
it was kept on.

This tool reads a family's shipped result JSONs and reports, per dataset:

  * `optimism`      base error on the val slice IN-SAMPLE vs OUT-OF-SAMPLE vs on
                    TEST -- the screening statistic. >~2x means any keep test
                    scored against the in-sample base is untrustworthy.
  * `keep_claim_pct`   the gain the stage's own keep test claimed (val pre -> post)
  * `test_delivered_pct` the paired change on the TEST split (pre-stage applied
                    leg -> scored value) -- the honest-held-out proxy
  * `sign_inverted` claim positive while test negative
  * `panel_counterfactual` the panel geomean with every kept stage rolled back to
                    its pre-stage leg, next to the scored geomean and the round's
                    geomean noise floor

It computes NO metric of its own: every number is read from the family's JSONs,
which were produced through `round1/eval/nrmse.py`. Key paths are CLI arguments
(dot paths; `{other.path}` substitutes another key's VALUE), so it is not tied to one
family's schema.

Example (the s4_hybrid_routing-B2 family, both arms):

  python tools/stage_keep_test_audit.py \
      --results "$OUTPUTS_ROOT/s4_hybrid_routing/B2/eval/results_gate_repair/fno_transolver_seq_b2/*_e200_s0.json" \
      --stage_flag stage3_joint \
      --val_pre  s4_gate.val_rel_l2_hybrid_insample_base_at_applied \
      --val_post val_rel_l2_hybrid \
      --test_pre "s4_alpha_protocol_legs.legs.{s4_alpha_protocol_legs.applied_leg}.test_nrmse" \
      --test_post splits.test_hf.rel_l2_mean \
      --base_insample s4_gate.val_rel_l2_base_insample \
      --base_oof s4_gate.val_rel_l2_base_oof \
      --base_test base_only_rel_l2 \
      --out /tmp/stage_audit.json
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import subprocess
import sys
from pathlib import Path


def _round_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True, cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip()) / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
import nrmse as NR                                                    # noqa: E402


def _plain(obj, path):
    cur = obj
    for p in path.split("."):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def dig(obj, path):
    """Dot path, with `{other.dot.path}` indirection: the braced sub-path is looked
    up in the SAME document and its value is substituted as a key first.
    e.g. `legs.{applied_leg}.test_nrmse` with `applied_leg == "oof"`
         -> `legs.oof.test_nrmse`."""
    import re
    while True:
        m = re.search(r"\{([^{}]+)\}", path)
        if not m:
            break
        val = _plain(obj, m.group(1))
        if val is None:
            return None
        path = path[:m.start()] + str(val) + path[m.end():]
    return _plain(obj, path)


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True,
                    help="glob of per-dataset family result JSONs (one per dataset)")
    ap.add_argument("--dataset_key", default="dataset")
    ap.add_argument("--stage_flag", required=True)
    ap.add_argument("--val_pre", required=True)
    ap.add_argument("--val_post", required=True)
    ap.add_argument("--test_pre", required=True)
    ap.add_argument("--test_post", default="splits.test_hf.rel_l2_mean")
    ap.add_argument("--base_insample", default=None)
    ap.add_argument("--base_oof", default=None)
    ap.add_argument("--base_test", default=None)
    ap.add_argument("--min_gain", type=float, default=1e-3,
                    help="the keep rule's relative-gain threshold (for the report only)")
    ap.add_argument("--panel", default=None,
                    help="comma-separated dataset list for the geomean; default = project.yaml panel")
    ap.add_argument("--geomean_floor", type=float, default=0.884)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    baselines = json.load(open(ROUND / "eval" / "copylf_baselines.json"))
    floors = json.load(open(ROUND / "state" / "noise_floor.json"))
    if a.panel:
        panel = a.panel.split(",")
    else:
        import yaml
        panel = yaml.safe_load(open(ROUND / "project.yaml"))["panel"]

    rows, seen = [], {}
    for p in sorted(glob.glob(a.results)):
        d = json.load(open(p))
        ds = dig(d, a.dataset_key)
        if ds is None:
            continue
        kept = bool(dig(d, a.stage_flag))
        vpre, vpost = dig(d, a.val_pre), dig(d, a.val_post)
        tpre, tpost = dig(d, a.test_pre), dig(d, a.test_post)
        row = dict(dataset=ds, json=p, stage_kept=kept,
                   val_pre=vpre, val_post=vpost, test_pre=tpre, test_post=tpost)
        if vpre and vpost is not None and vpre == vpre:
            row["keep_claim_pct"] = 100.0 * (vpre - vpost) / vpre
        if tpre and tpost is not None:
            row["test_delivered_pct"] = 100.0 * (tpre - tpost) / tpre
        row["sign_inverted"] = bool(kept and row.get("keep_claim_pct", 0) > 0
                                    and row.get("test_delivered_pct", 0) < 0)
        if a.base_insample and a.base_oof:
            bi, bo = dig(d, a.base_insample), dig(d, a.base_oof)
            bt = dig(d, a.base_test) if a.base_test else None
            if bi:
                row["optimism"] = dict(val_base_insample=bi, val_base_oof=bo,
                                       base_test=bt,
                                       oof_over_insample=(bo / bi) if bo else None,
                                       test_over_insample=(bt / bi) if bt else None)
        rows.append(row); seen[ds] = row

    print("=" * 118)
    print(f"stage keep-test audit -- {len(rows)} result JSONs, stage flag `{a.stage_flag}`, "
          f"keep rule threshold {a.min_gain:g}")
    print("=" * 118)
    print("%-34s %5s %11s %11s %11s %11s %11s %6s" % (
        "dataset", "kept", "val_pre", "val_post", "claim%", "test_pre", "test_post", "flip"))
    for r in rows:
        print("%-34s %5s %11.6f %11.6f %+11.2f %11.6f %11.6f %6s" % (
            r["dataset"][:34], "YES" if r["stage_kept"] else "-",
            r["val_pre"] if r["val_pre"] is not None else float("nan"),
            r["val_post"] if r["val_post"] is not None else float("nan"),
            r.get("keep_claim_pct", float("nan")),
            r["test_pre"], r["test_post"],
            "FLIP" if r["sign_inverted"] else ""))
    kept = [r for r in rows if r["stage_kept"]]
    n_flip = sum(r["sign_inverted"] for r in kept)
    print(f"\n  stage kept on {len(kept)} of {len(rows)} datasets; keep test SIGN-INVERTED against the "
          f"test split on {n_flip} of {len(kept)}")

    if any("optimism" in r for r in rows):
        print("\n-- base optimism on the validation slice (the screening statistic) --")
        print("%-34s %13s %13s %10s %13s %10s" % (
            "dataset", "val_base_IS", "val_base_OOF", "OOF/IS", "base_test", "test/IS"))
        for r in rows:
            o = r.get("optimism")
            if not o or not o.get("val_base_insample"):
                continue
            print("%-34s %13.6f %13.6f %10.2f %13s %10s" % (
                r["dataset"][:34], o["val_base_insample"], o["val_base_oof"] or float("nan"),
                o["oof_over_insample"] or float("nan"),
                f"{o['base_test']:.6f}" if o["base_test"] else "-",
                f"{o['test_over_insample']:.2f}" if o["test_over_insample"] else "-"))

    # panel-level counterfactual: roll every kept stage back to its pre-stage leg
    cf = None
    have = [ds for ds in panel if ds in seen]
    if len(have) == len(panel):
        scored, counter = [], []
        for ds in panel:
            r = seen[ds]
            ref = baselines.get(ds, {}).get("test_nrmse")
            if ref is None:                     # paper-bar dataset: skill ratio is arm-relative
                sk_s, sk_c = 1.0, (r["test_pre"] / r["test_post"]) if r["stage_kept"] else 1.0
            else:
                sk_s, sk_c = r["test_post"] / ref, (r["test_pre"] if r["stage_kept"]
                                                    else r["test_post"]) / ref
            scored.append(sk_s); counter.append(sk_c)
        gs, gc = geomean(scored), geomean(counter)
        cf = dict(scored_geomean=gs, no_stage_geomean=gc, cost=gs - gc,
                  cost_pct=100 * (gs - gc) / gc, geomean_floor=a.geomean_floor,
                  resolvable=abs(gs - gc) > a.geomean_floor)
        print(f"\n-- panel counterfactual (relative geomean; paper-bar datasets enter as a ratio) --")
        print(f"  scored {gs:.6f} | stage rolled back {gc:.6f} | cost {gs-gc:+.4f} "
              f"({100*(gs-gc)/gc:+.2f}%) | floor {a.geomean_floor} -> "
              f"{'RESOLVABLE' if cf['resolvable'] else 'inside the floor'}")
        for ds in panel:
            r = seen[ds]
            if not r["stage_kept"]:
                continue
            ref = baselines.get(ds, {}).get("test_nrmse")
            if ref is None:
                continue
            fl = floors.get(ds, {}).get("min_claimable_effect")
            cost = (r["test_post"] - r["test_pre"]) / ref
            print(f"    {ds:<34s} per-dataset cost {cost:+.4f} skill units"
                  + (f" vs floor {fl:.4f}: " + ("RESOLVABLE" if abs(cost) > fl else "inside floor")
                     if fl else ""))
    else:
        print(f"\n-- panel counterfactual skipped: {len(have)}/{len(panel)} panel datasets in the glob")

    if a.out:
        json.dump(dict(rows=rows, n_kept=len(kept), n_sign_inverted=n_flip,
                       panel_counterfactual=cf,
                       nrmse_def_hash=NR.NRMSE_DEF_HASH), open(a.out, "w"), indent=1)
        print(f"\n[wrote] {a.out}")


if __name__ == "__main__":
    main()
