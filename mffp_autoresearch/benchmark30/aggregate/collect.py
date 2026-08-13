"""Aggregator + validator + leaderboard builder (spec D8, D9, D12).

Consumes ONLY the per-dataset score JSONs the launcher writes under
`rev-<hash8>/results/scores/` (each carries arm `A1_stack_ic_reg` for the
certified family by construction — the 7-arm sidecar diagnostics in the
smoke_eval outputs are never read for metrics, spec D5).

Headline (exact D9 order): for each seed s, the panel geomean of
per-dataset skill `nrmse_film(s) / nrmse_model(s)` over the common eligible
set; reported as the mean over the three seed-level geomeans with a
[min, max] interval, labeled `seed_plus_run_interval` (round-3 finding:
same-seed cross-node drift is 0.62x seed variance — this is NOT a proper CI
over independent observations).
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

MODEL, FILM = "r3s2_route_b30", "mf_fno_transfer_film"
SCORE_RE = re.compile(r"^(?P<family>.+)_s(?P<seed>\d+)_e(?P<epochs>\d+)_(?P<ds>.+)\.json$")


def validate_score(score: dict, expected_def_hash: str, expect: dict = None) -> None:
    """Reject a result whose identity does not match the campaign (spec D12)."""
    if score.get("copylf_def_hash") != expected_def_hash:
        raise ValueError(
            f"copylf_def_hash mismatch: result carries "
            f"{str(score.get('copylf_def_hash'))[:12]}, campaign expects "
            f"{expected_def_hash[:12]} — computed under a different construction")
    for key, want in (expect or {}).items():
        if score.get(key) != want:
            raise ValueError(f"score {key}={score.get(key)!r} does not match "
                             f"expected {key}={want!r} from its filename")


def _geomean(values: list) -> float:
    return math.exp(sum(math.log(v) for v in values) / len(values))


def load_scores(rev_root: Path, expected_def_hash: str,
                expected_epochs: int) -> dict:
    """(family, seed, ds) -> per-dataset entry; every file validated.

    Only files at `expected_epochs` are admitted (r1 fix F2: the smoke tier
    shares the revision root, and a 2-epoch value must never enter a
    200-epoch leaderboard); a duplicate cell at the same epochs hard-fails
    instead of overwriting."""
    out = {}
    scores_dir = Path(rev_root) / "results/scores"
    for p in sorted(scores_dir.glob("*.json")):
        m = SCORE_RE.match(p.name)
        if not m:
            raise ValueError(f"unrecognized score filename: {p.name}")
        if int(m["epochs"]) != expected_epochs:
            continue  # other-tier file in the shared rev root
        score = json.load(open(p))
        ds = m["ds"]
        # the JSON's family field is the family-dir name, which for both
        # campaign families equals the filename prefix — checked here.
        validate_score(score, expected_def_hash,
                       expect={"family": m["family"], "seed": int(m["seed"]),
                               "epochs": int(m["epochs"])})
        if ds not in score["per_dataset"]:
            raise ValueError(f"{p.name}: JSON lacks per_dataset[{ds!r}]")
        key = (m["family"], int(m["seed"]), ds)
        if key in out:
            raise ValueError(f"duplicate score cell {key} at epochs "
                             f"{expected_epochs} — refusing to overwrite")
        out[key] = score["per_dataset"][ds]
    return out


def _load_ops(rev_root: Path) -> dict:
    """family -> ds -> s<seed> -> runtime/memory fields from the smoke_eval
    result files score_panel writes under results/<family>/ (r1 fix F8)."""
    ops = {}
    res_re = re.compile(r"^(?P<ds>.+)_e(?P<epochs>\d+)_s(?P<seed>\d+)\.json$")
    for fam_dir in sorted((Path(rev_root) / "results").iterdir()) \
            if (Path(rev_root) / "results").is_dir() else []:
        if not fam_dir.is_dir() or fam_dir.name == "scores":
            continue
        for p in sorted(fam_dir.glob("*.json")):
            m = res_re.match(p.name)
            if not m:
                continue
            try:
                r = json.load(open(p))
            except Exception:
                continue
            fields = {k: r[k] for k in ("train_seconds", "eval_seconds",
                                        "peak_mem_bytes", "param_count") if k in r}
            if fields:
                ops.setdefault(fam_dir.name, {}).setdefault(
                    m["ds"], {})[f"s{m['seed']}"] = fields
    return ops


def aggregate_scores(rev_root: Path, expected_def_hash: str, seeds: list,
                     expected_epochs: int = 200, groups: dict = None,
                     exclusion_ledger: dict = None, universe: list = None,
                     strict: bool = False) -> dict:
    cells = load_scores(rev_root, expected_def_hash, expected_epochs)
    families = (MODEL, FILM)
    observed = sorted({ds for (_, _, ds) in cells})
    datasets = sorted(set(universe) | set(observed)) if universe else observed
    ledger = exclusion_ledger or {}

    per_dataset = {}
    coverage = {}
    for ds in datasets:
        coverage[ds] = {f: sum(1 for s in seeds if (f, s, ds) in cells)
                        for f in families}
        per_dataset[ds] = {}
        for f in families:
            vals = [cells[(f, s, ds)]["nRMSE"] for s in seeds if (f, s, ds) in cells]
            if vals:
                per_dataset[ds][f] = {"per_seed": vals, "mean": sum(vals) / len(vals),
                                      "min": min(vals), "max": max(vals)}

    common = [ds for ds in datasets
              if all(coverage[ds][f] == len(seeds) for f in families)]

    # r1 fix F3: every universe cell must be a result OR a ledger entry —
    # a silently vanished dataset must never shrink the denominator unnoticed.
    unaccounted = []
    for ds in datasets:
        for f in families:
            if coverage[ds][f] < len(seeds) and ds not in ledger.get(f, {}):
                unaccounted.append(f"{f}/{ds}: {coverage[ds][f]}/{len(seeds)} seeds, not ledgered")
    if strict and unaccounted:
        raise ValueError("unaccounted cells (spec D8 — result or ledger, never "
                         "silence): " + "; ".join(unaccounted))

    def seed_geomeans(ds_list):
        out = []
        for s in seeds:
            skills = [cells[(FILM, s, ds)]["nRMSE"] / cells[(MODEL, s, ds)]["nRMSE"]
                      for ds in ds_list]
            out.append(_geomean(skills))
        return out

    headline = None
    if common:
        per_seed = seed_geomeans(common)
        headline = {"per_seed_geomean": per_seed,
                    "mean": sum(per_seed) / len(per_seed),
                    "interval": [min(per_seed), max(per_seed)],
                    "interval_kind": "seed_plus_run_interval",
                    "definition": ("per-seed panel geomean of nrmse_film/nrmse_model "
                                   "over the common eligible set, then mean/[min,max] "
                                   "across seeds (spec D9)")}

    group_geomeans = {}
    for gname, gids in (groups or {}).items():
        sub = [ds for ds in common if ds in gids]
        if sub:
            per_seed = seed_geomeans(sub)
            group_geomeans[gname] = {"datasets": sub,
                                     "per_seed_geomean": per_seed,
                                     "mean": sum(per_seed) / len(per_seed),
                                     "interval": [min(per_seed), max(per_seed)]}

    return {
        "inputs": "score_jsons_only_arm_A1",
        "seeds": seeds,
        "expected_epochs": expected_epochs,
        "per_dataset": per_dataset,
        "coverage": coverage,
        "common_eligible_set": common,
        "unaccounted_cells": unaccounted,
        "headline": headline,
        "group_geomeans": group_geomeans,
        "exclusion_ledger": ledger,
        "ops": _load_ops(rev_root),
    }


def rehash_and_check(cfg: dict, manifest: dict) -> None:
    """Collect-time D12 re-hash of source arrays AND stripped views."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from staging.manifest import verify_against
    from staging.preflight import _view_content_hash, require_sealed, stripped_root
    require_sealed(manifest)
    ok, diffs = verify_against(cfg, manifest)
    if not ok:
        raise ValueError("D12 source re-hash FAILED: " + "; ".join(diffs))
    for ds, want in manifest["stripped_view_hashes"].items():
        got = _view_content_hash(stripped_root(cfg) / ds)
        if got != want:
            raise ValueError(f"D12 stripped-view re-hash FAILED for {ds}")


def main() -> None:
    import argparse
    import importlib.util
    import sys
    import yaml
    campaign = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(campaign))
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-rehash", action="store_true",
                    help="skip the slow D12 re-hash (NEVER for the final leaderboard)")
    args = ap.parse_args()
    cfg = yaml.safe_load(open(campaign / "config.yaml"))
    manifest = json.load(open(campaign / "state/staging_manifest.json"))
    if not args.skip_rehash:
        rehash_and_check(cfg, manifest)
        print("[D12] re-hash clean (source + stripped views)")
    spec = importlib.util.spec_from_file_location("b30_pd_agg", campaign / "eval/panel_data.py")
    pd_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pd_mod)
    rev_root = Path(cfg["output_root"]) / f"rev-{manifest['manifest_hash'][:8]}"
    groups = {g: [d["id"] for d in lst] for g, lst in cfg["datasets"].items()}
    ledger_p = campaign / "state/exclusion_ledger.json"
    ledger = json.load(open(ledger_p)) if ledger_p.exists() else {}
    universe = [d["id"] for g in cfg["datasets"].values() for d in g]
    lb = aggregate_scores(rev_root, pd_mod.COPYLF_DEF_HASH, seeds=cfg["seeds"],
                          expected_epochs=cfg["epochs"]["full"], groups=groups,
                          exclusion_ledger=ledger, universe=universe, strict=True)
    lb["manifest_hash"] = manifest["manifest_hash"]
    lb["registry_revision"] = manifest["registry_revision"]
    out = campaign / "state/leaderboard.json"
    json.dump(lb, open(out, "w"), indent=1, sort_keys=True)
    print(f"leaderboard -> {out} (common set: {len(lb['common_eligible_set'])} datasets)")


if __name__ == "__main__":
    main()
