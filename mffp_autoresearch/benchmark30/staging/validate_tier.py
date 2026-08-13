"""G3/G4 validators (r1 fix F6; spec D6).

The launcher refuses full tiers until these record their gates; nothing else
may write G3/G4.  Validation is completion- and coverage-based, never
metric-based (spec D6: "completion, not metric quality").

G3 (after the smoke tier): every (family, dataset) cell has either a
2-epoch score JSON or an exclusion-ledger entry, and every smoke job in the
submissions record reached a terminal sacct state.
G4 (after full seed 0): every non-ledgered (family, dataset) cell has a
200-epoch seed-0 score JSON, and both seed-0 jobs are sacct COMPLETED.

Each gate entry is bound to the sealed manifest hash (r1 fix F4).
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def sacct_states(job_ids: list) -> dict:
    out = subprocess.run(
        ["sacct", "-j", ",".join(job_ids), "--format=JobID,State", "-n", "-P"],
        capture_output=True, text=True, check=True).stdout
    states = {}
    for line in out.strip().splitlines():
        jid, state = line.split("|")[:2]
        if "." not in jid:  # top-level job line only
            states[jid] = state.split()[0]
    return states


def _load(path, default):
    return json.load(open(path)) if Path(path).exists() else default


def _cells(cfg: dict, ledger: dict, family: str) -> list:
    ids = [d["id"] for g in cfg["datasets"].values() for d in g]
    return [ds for ds in ids if ds not in ledger.get(family, {})]


def validate_tier(cfg: dict, tier: str, state_dir: Path = None,
                  sacct_fn=sacct_states) -> dict:
    state_dir = Path(state_dir or CAMPAIGN / "state")
    manifest = json.load(open(state_dir / "staging_manifest.json"))
    if not manifest.get("sealed"):
        raise RuntimeError("unsealed manifest (spec D12)")
    rev_root = Path(cfg["output_root"]) / f"rev-{manifest['manifest_hash'][:8]}"
    all_subs = [s for s in _load(state_dir / "submissions.json", [])
                if s["tier"] == tier and s["manifest_hash"] == manifest["manifest_hash"]]
    ledger = _load(state_dir / "exclusion_ledger.json", {})
    epochs = cfg["epochs"]["smoke"] if tier == "smoke" else cfg["epochs"]["full"]
    tier_seeds = [0] if tier in ("smoke", "full-seed0") else [1, 2]

    # micro-fix M1: the EXPECTED cell set comes from the tier definition, never
    # from whatever happened to be submitted; every cell needs a submission.
    # micro-fix M2: submissions are append-only history — validate the LATEST
    # attempt per (family, seed) cell so a failed earlier attempt can be retried.
    latest = {}
    for sub in all_subs:  # file order is submission order
        latest[(sub["family"], sub["seed"])] = sub
    missing_cells = [(f, sd) for f in cfg["families"] for sd in tier_seeds
                     if (f, sd) not in latest]
    if missing_cells:
        raise RuntimeError(f"no {tier} submission recorded for cells {missing_cells} "
                           f"under the active manifest")
    subs = list(latest.values())

    states = sacct_fn([s["job_id"] for s in subs])
    # micro-fix M1: a job sacct cannot see is NOT terminal — refuse loudly.
    unseen = [s["job_id"] for s in subs if s["job_id"] not in states]
    if unseen:
        raise RuntimeError(f"sacct returned no state for submitted jobs {unseen} — "
                           f"cannot certify the tier")
    terminal = {"COMPLETED", "FAILED", "TIMEOUT", "CANCELLED", "OUT_OF_MEMORY"}
    pending = {j: st for j, st in states.items() if st not in terminal}
    if pending:
        raise RuntimeError(f"jobs not terminal yet: {pending}")
    if tier != "smoke":
        not_completed = {j: st for j, st in states.items() if st != "COMPLETED"}
        if not_completed:
            raise RuntimeError(
                f"full-tier latest attempts not COMPLETED (honest-exit: failures "
                f"occurred): {not_completed} — triage into the exclusion ledger or "
                f"retry (a NEW submission supersedes this attempt) first")

    problems = []
    seeds = tier_seeds
    for fam in cfg["families"]:
        for ds in _cells(cfg, ledger, fam):
            for seed in seeds:
                score = rev_root / "results/scores" / f"{fam}_s{seed}_e{epochs}_{ds}.json"
                if not score.exists():
                    problems.append(f"{fam}/{ds}/s{seed}: no score JSON and no ledger entry")
    if problems:
        raise RuntimeError(
            f"{tier} coverage incomplete ({len(problems)} cells): "
            + "; ".join(problems[:8])
            + (" …" if len(problems) > 8 else "")
            + " — every failure must be ledgered with evidence before the gate records")

    gate = "G3" if tier == "smoke" else "G4"
    gates = _load(state_dir / "gates.json", {})
    gates[gate] = {
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "manifest_hash": manifest["manifest_hash"],
        "evidence": f"{tier}: {len(subs)} jobs terminal, all cells scored or ledgered",
        "jobs": {s["job_id"]: states.get(s["job_id"]) for s in subs},
        "ledgered": {f: sorted(ledger.get(f, {})) for f in cfg["families"]},
    }
    with open(state_dir / "gates.json", "w") as f:
        json.dump(gates, f, indent=1, sort_keys=True)
    print(f"[{gate}] recorded (bound to {manifest['manifest_hash'][:12]})")
    return gates[gate]


def main() -> None:
    import argparse
    import yaml
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tier", required=True, choices=["smoke", "full-seed0"])
    args = ap.parse_args()
    cfg = yaml.safe_load(open(CAMPAIGN / "config.yaml"))
    validate_tier(cfg, args.tier)


if __name__ == "__main__":
    main()
