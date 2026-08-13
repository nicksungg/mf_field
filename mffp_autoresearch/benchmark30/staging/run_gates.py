"""Execute gates G0-G2 and record their evidence (spec D6; plan A10).

Necessity note (spec §4): the round-3 gate machinery is the orchestrator/card
pipeline — round-scoped state with a different protocol; this is a minimal
campaign-local runner whose only consumers are `slurm/launch.py` (which READS
`state/gates.json`) and the convergence record.

G0: provisional staging manifest (source hashes + hub-identity tripwire).
G1: stripped views for all 30 + LF-free audit + grid audit + D12 seal.
G2: registry/vendor/family guard tests green + copy-LF baselines built for
    every dataset (or ledgered with evidence).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN))
VENV_PY = "/resnick/groups/Hippo/ezeng/mf_field/.venv/bin/python"


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _record_gate(gates: dict, name: str, evidence: dict, manifest_hash: str = None) -> None:
    # r1 fix F4: every gate record is bound to the sealed manifest it vouches for
    gates[name] = {"utc": _utc(), "manifest_hash": manifest_hash, **evidence}
    with open(CAMPAIGN / "state/gates.json", "w") as f:
        json.dump(gates, f, indent=1, sort_keys=True)
    print(f"[{name}] recorded")


def main() -> None:
    import yaml
    from staging.manifest import build_manifest
    from staging.preflight import (audit_grids, audit_stripped_view,
                                   build_stripped_views, seal_manifest)

    cfg = yaml.safe_load(open(CAMPAIGN / "config.yaml"))
    gates = {}

    # ---- G0: provisional manifest (recorded post-seal, bound to the hash) ----
    manifest = build_manifest(cfg)

    # ---- G1: stripped views + audits + seal ----
    views = build_stripped_views(cfg)
    reports = [audit_stripped_view(d, Path(v)) for d, v in views.items()]
    grid_problems = audit_grids(cfg, manifest)
    if grid_problems:
        raise SystemExit("[G1] grid audit FAILED:\n  " + "\n  ".join(grid_problems))
    sealed = seal_manifest(cfg, manifest, registry_revision="b30-0001")
    with open(CAMPAIGN / "state/staging_manifest.json", "w") as f:
        json.dump(sealed, f, indent=1, sort_keys=True)
    mh = sealed["manifest_hash"]
    _record_gate(gates, "G0", {
        "evidence": f"{len(manifest['datasets'])} datasets source-hashed",
        "n_datasets": len(manifest["datasets"])}, manifest_hash=mh)
    _record_gate(gates, "G1", {
        "evidence": f"{len(reports)} stripped views LF-free; grid audit clean; "
                    f"manifest sealed {mh[:16]}"}, manifest_hash=mh)

    # ---- G2: guard tests + copy-LF baselines ----
    tests = subprocess.run(
        [VENV_PY, "-m", "pytest", "tests/", "-q", "--tb=no"],
        capture_output=True, text=True, cwd=CAMPAIGN)
    tail = tests.stdout.strip().splitlines()[-1] if tests.stdout.strip() else "?"
    if tests.returncode != 0:
        raise SystemExit(f"[G2] guard tests FAILED: {tail}")

    from eval.make_floors_b30 import FLOORS_OUT, build_all as build_floors
    floors = build_floors()
    # micro-review fix: an incomplete floors rebuild must never replace the
    # committed artifact or leave G2 green (the family HARD-requires entries).
    expected_ids = {d["id"] for g in cfg["datasets"].values() for d in g}
    floor_errors = floors.get("_errors", {})
    built_ids = {k for k in floors if not k.startswith("_")}
    if floor_errors or built_ids != expected_ids:
        raise SystemExit(
            f"[G2] floors rebuild incomplete: errors={sorted(floor_errors)}, "
            f"missing={sorted(expected_ids - built_ids)} — refusing to overwrite "
            f"{FLOORS_OUT} or record G2 (ledger explicitly if intended)")
    FLOORS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(FLOORS_OUT, "w") as f:
        json.dump(floors, f, indent=1, sort_keys=True)
    n_floors = len(built_ids)

    from eval.make_copylf_baselines_b30 import build_all
    baselines = build_all()
    with open(CAMPAIGN / "state/copylf_baselines.json", "w") as f:
        json.dump(baselines, f, indent=1, sort_keys=True)
    errors = baselines.get("_errors", {})
    if errors:
        ledger_p = CAMPAIGN / "state/exclusion_ledger.json"
        ledger = json.load(open(ledger_p)) if ledger_p.exists() else {}
        for ds, msg in errors.items():
            for fam in ("r3s2_route_b30", "mf_fno_transfer_film"):
                ledger.setdefault(fam, {})[ds] = (
                    f"unscorable: copy-LF reference not constructible ({msg[:160]})")
        with open(ledger_p, "w") as f:
            json.dump(ledger, f, indent=1, sort_keys=True)
    n_ok = sum(1 for k in baselines if not k.startswith("_"))
    _record_gate(gates, "G2", {
        "evidence": f"guard tests: {tail}; copy-LF baselines: {n_ok} built, "
                    f"{len(errors)} ledgered; floors: {n_floors} built",
        "tests": tail, "baselines_built": n_ok,
        "ledgered": sorted(errors)}, manifest_hash=mh)

    print("\nG0-G2 complete.")
    for ds in sorted(errors):
        print(f"  LEDGERED (both families): {ds}")


if __name__ == "__main__":
    main()
