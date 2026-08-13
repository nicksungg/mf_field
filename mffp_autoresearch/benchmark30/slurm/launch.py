"""SLURM launcher with gate→tier enforcement (spec D6, D10, D12).

One job per {family, seed} iterating its dataset list SEQUENTIALLY, one
`score_panel.py` invocation per dataset so a deterministic failure on one
dataset (e.g. era5's predeclared WORK_CAP raise) cannot mask the rest.
Every mutable path — results, cache, checkpoints (score_panel derives them
from ROUND2_EVAL_RESULTS), logs — lives under the D12 revision root.

Gate matrix (spec D6): smoke needs G0–G2; full seed 0 needs G3; full
seeds 1–2 need G4.  Gates are recorded in `state/gates.json` by the
preflight/validation steps; this launcher only ever READS them.
"""
from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]

TIER_GATES = {
    "smoke": ["G0", "G1", "G2"],
    "full-seed0": ["G0", "G1", "G2", "G3"],
    "full-seeds12": ["G0", "G1", "G2", "G3", "G4"],
}
TIER_SEEDS = {"smoke": [0], "full-seed0": [0], "full-seeds12": [1, 2]}


class GateError(RuntimeError):
    """A tier was requested before its required gates were recorded (spec D6)."""


def _require_gates(tier: str, state_dir: Path) -> None:
    gates_file = state_dir / "gates.json"
    recorded = json.load(open(gates_file)) if gates_file.exists() else {}
    missing = [g for g in TIER_GATES[tier] if g not in recorded]
    if missing:
        raise GateError(
            f"tier {tier!r} requires gates {TIER_GATES[tier]}; missing {missing} "
            f"in {gates_file} — run the corresponding preflight/validation step "
            f"first (spec D6; the gate evidence is written by Phase B, never by hand)")


def _rev_root(cfg: dict, state_dir: Path) -> str:
    manifest = json.load(open(state_dir / "staging_manifest.json"))
    if not manifest.get("sealed") or not manifest.get("manifest_hash"):
        raise GateError("unsealed staging manifest — run staging/preflight.py (spec D12)")
    return f"{cfg['output_root']}/rev-{manifest['manifest_hash'][:8]}"


def _ledger(state_dir: Path) -> dict:
    p = state_dir / "exclusion_ledger.json"
    return json.load(open(p)) if p.exists() else {}


SBATCH_TEMPLATE = """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --gres={gres}
#SBATCH --time={time}
#SBATCH --mail-user={mail_user}
#SBATCH --mail-type={mail_type}
#SBATCH --output={rev_root}/logs/%x_%j.out
#SBATCH --error={rev_root}/logs/%x_%j.err

set -u
mkdir -p {rev_root}/logs {rev_root}/results {rev_root}/cache
export ROUND2_EVAL_RESULTS={rev_root}/results
export ROUND2_EVAL_CACHE={rev_root}/cache
export PYTHONHASHSEED={seed}
FAILED=""
{invocations}
if [ -n "$FAILED" ]; then
  echo "[b30] per-dataset failures (exclusion-ledger candidates):$FAILED"
  printf '%s\\n' "$FAILED" > {rev_root}/results/{family}_s{seed}_e{epochs}_failures.txt
fi
exit 0
"""


def render_jobs(cfg: dict, tier: str, state_dir: Path = None) -> list:
    state_dir = Path(state_dir or CAMPAIGN / "state")
    _require_gates(tier, state_dir)
    rev_root = _rev_root(cfg, state_dir)
    epochs = cfg["epochs"]["smoke"] if tier == "smoke" else cfg["epochs"]["full"]
    all_ids = [d["id"] for g in cfg["datasets"].values() for d in g]
    ledger = _ledger(state_dir) if tier != "smoke" else {}
    scorer = CAMPAIGN / "eval/score_panel.py"
    venv_py = "/resnick/groups/Hippo/ezeng/mf_field/.venv/bin/python"
    s = cfg["slurm"]

    jobs = []
    for family, fam_rel in cfg["families"].items():
        fam_dir = (CAMPAIGN / "family/r3s2_route_b30" if family == "r3s2_route_b30"
                   else Path("/resnick/groups/Hippo/ezeng/mf_field") / fam_rel)
        datasets = [d for d in all_ids if d not in ledger.get(family, {})]
        env_args = ""
        if family == "r3s2_route_b30":
            env_args = " --env " + " ".join(
                shlex.quote(f"{k}={v}") for k, v in cfg["recipe_env"].items())
        for seed in TIER_SEEDS[tier]:
            lines = []
            for ds in datasets:
                cmd = (f"{venv_py} {scorer} --family_dir {fam_dir} --datasets {ds} "
                       f"--epochs {epochs} --seed {seed}{env_args}")
                lines.append(f'{cmd} || FAILED="$FAILED {ds}"')
            script = SBATCH_TEMPLATE.format(
                job_name=f"b30-{family}-s{seed}-{tier}",
                partition=s["partition"], gres=s["gres"],
                time=s["time_smoke"] if tier == "smoke" else s["time_full"],
                mail_user=s["mail_user"], mail_type=s["mail_type"],
                rev_root=rev_root, seed=seed, epochs=epochs, family=family,
                invocations="\n".join(lines),
            )
            jobs.append({"family": family, "seed": seed, "epochs": epochs,
                         "tier": tier, "datasets": datasets, "script": script,
                         "job_name": f"b30-{family}-s{seed}-{tier}"})
    return jobs


def submit(jobs: list, rev_root_dir: Path) -> list:
    ids = []
    scripts_dir = rev_root_dir / "sbatch"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    for j in jobs:
        p = scripts_dir / f"{j['job_name']}.sbatch"
        p.write_text(j["script"])
        out = subprocess.run(["sbatch", str(p)], capture_output=True, text=True, check=True)
        job_id = out.stdout.strip().split()[-1]
        ids.append({"job_name": j["job_name"], "job_id": job_id})
        print(f"submitted {j['job_name']} -> {job_id}")
    return ids


def main() -> None:
    import argparse
    import yaml
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tier", required=True, choices=list(TIER_GATES))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    with open(CAMPAIGN / "config.yaml") as f:
        cfg = yaml.safe_load(f)
    jobs = render_jobs(cfg, args.tier)
    if args.dry_run:
        for j in jobs:
            print(f"-- {j['job_name']}: {len(j['datasets'])} datasets, epochs {j['epochs']}")
        return
    rev_root = Path(_rev_root(cfg, CAMPAIGN / "state"))
    ids = submit(jobs, rev_root)
    sub_file = CAMPAIGN / "state/submissions.json"
    hist = json.load(open(sub_file)) if sub_file.exists() else []
    hist.append({"tier": args.tier, "jobs": ids})
    json.dump(hist, open(sub_file, "w"), indent=1)


if __name__ == "__main__":
    main()
