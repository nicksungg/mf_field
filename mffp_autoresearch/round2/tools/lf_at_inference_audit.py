#!/usr/bin/env python
"""LF-at-inference audit — does a model family actually consume the low-fidelity
field at test time, or only during training?

Provenance: s2_beyond_copy-B1 mechanism analysis, turn 3 (finding F14 in card
`experiment_cards/s2_beyond_copy/batch_1/B1.json` part 6), generalizing the card's
own runtime M1 forward-hook audit
(`worktrees/s2_beyond_copy/B1/models_r1/s2_copylf_forensics/base_reload.py`).

Why it matters
--------------
`skill = nRMSE(model) / nRMSE(copy-LF)` compares a model against a baseline that
receives the per-sample coarse solve. If the model does NOT receive it at
inference, the comparison is LF-blind-model vs LF-using-baseline and the "fusion
failure" it reports is an input gap, not a mechanism gap. In round 1 this audit
returned 0 of 27 factory families reading the test split's LF field.

What it does (static, cheap, no training)
-----------------------------------------
For each family directory with a `smoke_eval.py`, it reports every source line
that indexes a TEST-split field (`test[...]["field_by_fid"][...]`) together with
the fidelity key used, plus:
  * `mf_mechanism`   — the family's own declared MF mechanism string, if any
  * `reads_test_lf`  — True only if some test-split field read uses a fidelity key
                       that is not the HF one
  * `surrogate_lf`   — True if the family builds its "LF" at test time from the
                       condition vector (a `*_lf*.summaries(X_te...)`-style call)
  * `lf_fidelity_used` — whether the family trains on `min(lf_fids)` or
                       `max(lf_fids)`; copy-LF always uses `max(lf_fids)`, so a
                       family on `min` is scored against a STRONGER LF than it saw.

`reads_test_lf` is the load-bearing field and is robust (it needs a literal
test-split field read with a non-HF fidelity key). `surrogate_lf_at_test` and
`lf_fidelity_used_in_training` are HEURISTICS: they depend on which shared
`_common` modules the import-graph resolution folds in, so treat them as leads.
Static analysis is deliberately conservative: it flags candidates, it does not
prove consumption. For a definitive answer on one family, run it under the
runtime forward-hook audit in `base_reload.capture()` (see the B1 family), which
records the shape of every tensor entering the network in eval mode.

Invocation
----------
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/lf_at_inference_audit.py --models_dir "$FACTORY_ROOT/models" \
      --out /path/to/lf_audit.json [--families a,b,c] [--verbose]

Cost: < 2 s, pure file reads.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

TEST_FIELD = re.compile(r'test\w*\s*\[\s*["\']field_by_fid["\']\s*\]\s*\[\s*([^\]]+)\]')
HF_KEYS = {"hf", "hf_fid", "test_hf", "hfid", "hf_f"}
SURROGATE = re.compile(r'\.summaries\s*\(\s*X_te|\.predict\w*\s*\(\s*X_te')
MECH = re.compile(r'["\']mf_mechanism["\']\s*:\s*(.+)')


def audit_family(fam_dir: Path, shared_dirs):
    own = sorted(fam_dir.glob("*.py"))
    own_src = "\n".join(f.read_text() for f in own)
    files = list(own)
    for d in shared_dirs:
        # fold in only the shared MODULES this family actually imports by name
        files += [p for p in sorted(d.glob("*.py"))
                  if re.search(rf"\b{re.escape(p.stem)}\b", own_src)]
    reads, surrogate_hits, mech = [], [], None
    lf_choice = None
    for f in files:
        try:
            lines = f.read_text().splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            m = TEST_FIELD.search(line)
            if m:
                key = m.group(1).strip()
                reads.append({
                    "file": str(f.relative_to(fam_dir.parent)), "line": i,
                    "fidelity_key": key,
                    "is_hf_key": any(h == key or key.endswith(h) for h in HF_KEYS),
                    "text": line.strip()[:160],
                })
            if SURROGATE.search(line):
                surrogate_hits.append(f"{f.relative_to(fam_dir.parent)}:{i}: "
                                      f"{line.strip()[:120]}")
            if mech is None and f.parent == fam_dir:
                mm = MECH.search(line)
                if mm:
                    mech = mm.group(1).split('",')[0].strip().strip('",')[:140]
            if lf_choice is None and 'lf_fids' in line and 'lf =' in line.replace(' ', ' '):
                if "min(" in line:
                    lf_choice = "min(lf_fids)  [WEAKER than copy-LF's max(lf_fids)]"
                elif "max(" in line:
                    lf_choice = "max(lf_fids)  [same as copy-LF]"
    return {
        "family": fam_dir.name,
        "mf_mechanism": mech,
        "test_field_reads": reads,
        "reads_test_lf": any(not r["is_hf_key"] for r in reads),
        "surrogate_lf_at_test": bool(surrogate_hits),
        "surrogate_evidence": surrogate_hits[:3],
        "lf_fidelity_used_in_training": lf_choice,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models_dir", required=True,
                    help="directory of model families (each with smoke_eval.py)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--families", default=None, help="comma-separated subset")
    ap.add_argument("--shared", default="_common",
                    help="comma-separated shared subdirs to include (default _common)")
    ap.add_argument("--verbose", action="store_true", help="print every read line")
    args = ap.parse_args()

    models = Path(args.models_dir).resolve()
    shared = [models / s for s in args.shared.split(",") if s and (models / s).is_dir()]
    want = set(args.families.split(",")) if args.families else None
    fams = [p for p in sorted(models.iterdir())
            if (p / "smoke_eval.py").exists() and (want is None or p.name in want)]
    if not fams:
        raise SystemExit(f"no families with smoke_eval.py under {models}")

    rows = [audit_family(p, shared) for p in fams]
    n_lf = sum(r["reads_test_lf"] for r in rows)
    n_sur = sum(r["surrogate_lf_at_test"] for r in rows)
    print(f"{n_lf} of {len(rows)} families read the TEST split's LF field at inference; "
          f"{n_sur} build a surrogate LF from X at test time.\n")
    for r in rows:
        flag = "LF-USING" if r["reads_test_lf"] else "LF-BLIND"
        extra = " (surrogate-LF)" if r["surrogate_lf_at_test"] else ""
        print(f"  {r['family']:30s} {flag}{extra}  "
              f"[{r['lf_fidelity_used_in_training'] or 'lf choice unknown'}]")
        if r["mf_mechanism"]:
            print(f"      declared: {r['mf_mechanism']}")
        if args.verbose:
            for x in r["test_field_reads"]:
                print(f"      {x['file']}:{x['line']}  key={x['fidelity_key']} "
                      f"hf={x['is_hf_key']}")
    out = {"models_dir": str(models), "n_families": len(rows),
           "n_reads_test_lf": n_lf, "n_surrogate_lf": n_sur, "families": rows}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
