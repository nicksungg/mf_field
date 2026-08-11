#!/usr/bin/env python
"""Extend the certified noise floor to the pfc cell (ADR r3-0005).

`state/anchors_repaired/noise_floor.json` (certified 2026-08-08) covers the
5-cell ADR r3-0004 panel; ADR r3-0005 (2026-08-10) restored
`sharp__phase_field_crystal_2d` to the scored panel — scored cell
L1(32^2)->L3(128^2), exact spectral (FFT zero-pad) reference — so pfc has no
certified entry and batch-3 cards cannot register pfc clauses.

This script computes the pfc entry by the round's OWN certification protocol,
byte-for-byte the r3s4_audit-B1 pipeline
(`worktrees/r3s4_audit/B1/probes/certify_thresholds.py`), whose functions it
IMPORTS rather than re-implements:

  * three fresh `r3s4_cert_min` legs on the NEW pfc cell (score_panel.py,
    200 epochs, seeds {0,1,2}, R3S4B1 env verbatim), submitted via
    `mffp_autoresearch_outputs/round3_anchors/scripts/r3s4_cert_min_pfc-R3.sh`
    into `<outputs>/round3/r3s4_audit/B1_pfc_ext/` (fresh cache + ckpts —
    no stale-anchor path exists);
  * D2 seed noise — `certify_seeds` (10,000-resample IQM/stratified bootstrap +
    Du paired per-seed deltas), rng seed 0;
  * D3 row noise — `row_paired_null` (10,000-resample PAIRED row bootstrap of
    same-model seed pairs), same rng stream;
  * D0 denominator noise — the SCORED copy-LF reference cell's relative
    bootstrap width: `preflight.cell_stability_check` at
    R3S4B1_ROW_BOOTSTRAP_B=10000 resamples, seed 0, over the per-row
    `copylf_prediction` gaps (post-ADR: spectral zero-pad rung-1) —
    `mdd_scored = (ci_hi - ci_lo) / point`, the protocol's copy-LF branch.

RNG note (documented in the entry): certify_thresholds.py threads ONE
`np.random.default_rng(0)` through its 5-dataset loop, so each dataset's draws
depend on loop position. A single-cell extension necessarily restarts the
stream at seed 0 (the protocol's `bootstrap_rng_seed`), preserving the
per-dataset internal order (certify_seeds, then row_paired_null).

Sanctioned-mutation pattern (tools/recompute_pfc_reference_floors.py): archive
first, add ONLY the `sharp__phase_field_crystal_2d` key, assert every other
top-level entry byte-identical.  DEFAULT IS DRY-RUN: writes
`noise_floor_candidate_pfc_ext.json` + `pfc_extension_diagnostic.json` to
--out_dir and never touches state/.  `--apply` performs the archived in-place
extension (ORCHESTRATOR-ONLY).
"""
from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field")
ROUND3 = ROOT / "mffp_autoresearch" / "round3"
PROBES = ROUND3 / "worktrees" / "r3s4_audit" / "B1" / "probes"
EXT_OUT = (ROOT / "mffp_autoresearch_outputs" / "round3" / "r3s4_audit"
           / "B1_pfc_ext")
NAME = "sharp__phase_field_crystal_2d"
STAMP = datetime.date.today().isoformat()

sys.path.insert(0, str(PROBES))
import _probe_common as PC                      # noqa: E402  (path bootstrap)
import certify_thresholds as CT                 # noqa: E402
import preflight as PF                          # noqa: E402  (shipped instrument)
from panel_data import COPYLF_DEF_HASH, copylf_prediction  # noqa: E402


def utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def compute_entry(results_dir: Path, per_row_dir: Path, seeds: list,
                  n_boot_seed: int, n_boot_row: int, boot_seed: int) -> dict:
    # ---- the three certifier legs (stale/binding gates) ----
    runs = {}
    for s in seeds:
        p = results_dir / f"result_pfc_certmin_s{s}.json"
        assert p.exists(), f"missing seed result {p}"
        runs[s] = PC.read_json(p)
    hashes = {(r["nrmse_def_hash"], r["copylf_def_hash"], r["code_hash"])
              for r in runs.values()}
    assert len(hashes) == 1, f"seeds scored under different definitions: {hashes}"
    any_run = next(iter(runs.values()))
    assert any_run["copylf_def_hash"] == COPYLF_DEF_HASH, (
        "runs were scored under a stale copylf definition "
        f"({any_run['copylf_def_hash']} != current {COPYLF_DEF_HASH})")
    assert int(any_run["epochs"]) == 200, any_run["epochs"]
    family = any_run["family"]
    assert family == "r3s4_cert_min", family
    for s, r in runs.items():
        cell = r["per_dataset"][NAME]
        assert cell.get("cached") is False, f"seed {s} served from cache"
        assert cell.get("reference_type") == "copylf", cell.get("reference_type")

    db = results_dir / "data_binding_exit_s0.txt"
    binding_exit = int(db.read_text().strip()) if db.exists() else None
    assert binding_exit == 0, f"data_binding verify exit={binding_exit}"

    # ---- reference (post-ADR-r3-0005) ----
    # KNOWN DEFECT (found 2026-08-10 while building this extension):
    # tools/recompute_pfc_reference_floors.py rebuilds the pfc floors entry
    # copying only NON-DICT old keys, so it silently dropped the `reference`
    # sub-dict from state/anchors_repaired/floors.json — certify_thresholds /
    # cell_seam / cell_integrity would KeyError on pfc. Until the orchestrator
    # repairs floors.json, the reference is sourced from the seam-verified
    # eval/copylf_baselines.json (the same value the ADR installed; the two
    # files agreed byte-for-byte for every other dataset).
    floors = PC.read_json(
        ROUND3 / "state" / "anchors_repaired" / "floors.json")
    baselines = PC.read_json(
        ROOT / "mffp_autoresearch" / "round2" / "eval" / "copylf_baselines.json")
    assert baselines[NAME]["convention"] == "spectral_zeropad_rung1"
    ref = float(baselines[NAME]["test_nrmse"])
    floors_ref = floors[NAME].get("reference")
    floors_reference_defect = floors_ref is None
    if not floors_reference_defect:
        assert abs(float(floors_ref["test_nrmse"]) - ref) < 1e-12, (
            "floors.json / copylf_baselines.json disagree on the pfc reference")
    # cross-check against the recomputed arm skills (skill = nrmse / ref)
    z = floors[NAME]["zero"]
    assert abs(z["nrmse"] / ref - z["skill"]) / z["skill"] < 1e-9, (
        "floors.json pfc arm skills were not computed against this reference")

    # ---- D2 + D3 (fresh rng stream, protocol seed, per-dataset order) ----
    rng = np.random.default_rng(boot_seed)
    skills = np.array([runs[s]["per_dataset"][NAME]["skill"] for s in seeds])
    nrmses = [float(runs[s]["per_dataset"][NAME]["nRMSE"]) for s in seeds]
    st = CT.certify_seeds(skills, n_boot_seed, rng)

    per_row = {}
    for s in seeds:
        arr = CT.load_per_row(per_row_dir, family, NAME, 200, s)
        assert arr is not None, f"per-row array missing for seed {s}"
        per_row[s] = arr
    row = CT.row_paired_null(per_row, ref, n_boot_row, rng)
    assert row.get("status") == "OK", row

    # ---- D0: scored copy-LF reference cell, relative bootstrap width ----
    te = PC.load_original_split(NAME, "test")   # OFFLINE REFERENCE path
    hf = np.asarray(te["field_by_fid"][te["hf_fid"]], dtype=np.float64)
    gaps = PC.per_row_rel_l2(copylf_prediction(te, NAME), hf)
    assert abs(float(gaps.mean()) - ref) / ref < 1e-6, (
        f"D0 cell mean {gaps.mean():.12g} does not reproduce the frozen "
        f"reference {ref:.12g}")
    stab = PF.cell_stability_check(np.asarray(gaps, np.float64),
                                   n_boot=n_boot_row, seed=boot_seed)
    mdd = float(stab["min_detectable_delta"])
    mdd_src = "probe D0 scored cell (copylf_prediction, spectral rung-1, ADR r3-0005)"

    tau_rel = max(st["seed_mce"], row.get("row_paired_95") or 0.0)
    skill_level = st["iqm"]
    tau_abs = float(tau_rel + mdd * skill_level)

    # ---- provisional comparison (pre-certification archive) ----
    provisional = PC.read_json(
        ROUND3 / "state" / "anchors_repaired"
        / "noise_floor_provisional_pre_certify_2026-08-10.json")
    prov = provisional.get(NAME, {}).get("min_claimable_effect")
    quoted = CT.CARD_PROVISIONAL.get(NAME)

    entry = {
        "family": family,
        "reference_type": "copylf",
        "reference_test_nrmse": ref,
        "per_seed_nrmse": nrmses,
        "per_seed_skill": [float(x) for x in skills],
        "mean_skill": st["mean"],
        "spread": st["spread_maxmin"],
        **st,
        "row_noise": row,
        "row_paired_95": row.get("row_paired_95"),
        "mdd_scored": mdd,
        "mdd_scored_source": mdd_src,
        "skill_level_used_for_tau_abs": skill_level,
        "tau_rel": float(tau_rel),
        "tau_rel_licenses": "same-reference, within-era arm comparisons",
        "tau_abs": tau_abs,
        "tau_abs_licenses": "absolute-bar or cross-era claims",
        "tau_abs_over_tau_rel": (None if tau_rel == 0
                                 else float(tau_abs / tau_rel)),
        "min_claimable_effect": float(tau_rel),
        "min_claimable_effect_definition":
            "tau_rel (same-reference comparisons). Use tau_abs against an "
            "absolute bar or across eras.",
        "provisional_min_claimable_effect": prov,
        "provisional_quoted_in_card": quoted,
        "provisional_agrees_with_card": (
            None if (prov is None or quoted is None)
            else bool(abs(prov - quoted) <= 5e-4)),
        "delta_vs_provisional": (None if prov is None
                                 else float(tau_rel - prov)),
        "provisional_comparability_caveat":
            "the provisional constant priced the PRE-ADR-r3-0005 cell "
            "(bilinear finest-LF convention); skills across the convention "
            "change are not comparable on pfc, so delta_vs_provisional is "
            "recorded mechanically, not as a like-for-like movement",
        "scoring_status": "scored",
        "adr_r3_0005_note":
            "restored to the scored panel by ADR r3-0005 (scored cell "
            "L1(32^2)->L3(128^2), exact spectral zero-pad reference); this "
            "entry EXTENDS the 2026-08-08 certification to the pfc cell — "
            "same family, tier, env, protocol and bootstrap constants",
        "denominator_stability": {
            **stab,
            "note": "OUTLIER_DOMINATED expected (preflight "
                    "state/preflight_pfc_adr0005_2026-08-10.json measured MDD "
                    "0.658 at n_boot=1000); mdd_scored here is the same "
                    "statistic at the protocol's n_boot_row resamples",
        },
        "extension_provenance": {
            "extended_utc": utc(),
            "result_files": [str(EXT_OUT / "eval" / f"result_pfc_certmin_s{s}.json")
                             for s in seeds],
            "per_row_results_dir": str(per_row_dir),
            "code_hash": any_run["code_hash"],
            "nrmse_def_hash": any_run["nrmse_def_hash"],
            "copylf_def_hash": any_run["copylf_def_hash"],
            "env": any_run["env"],
            "n_boot_seed": n_boot_seed, "n_boot_row": n_boot_row,
            "bootstrap_rng_seed": boot_seed,
            "data_binding_exit": binding_exit,
            "rng_stream_note":
                "fresh np.random.default_rng(0) for this single-cell "
                "extension, same per-dataset internal draw order as "
                "certify_thresholds.py (certify_seeds, then row_paired_null); "
                "the 2026-08-08 file threaded one stream through its "
                "5-dataset loop, so cross-dataset stream positions differ by "
                "construction",
            "floors_reference_defect": (
                "state/anchors_repaired/floors.json pfc entry is MISSING its "
                "'reference' sub-dict — dropped by "
                "tools/recompute_pfc_reference_floors.py (copies only "
                "non-dict keys when rebuilding the entry); reference sourced "
                "from eval/copylf_baselines.json instead; orchestrator repair "
                "needed: floors[pfc]['reference'] = {'convention': "
                "'spectral_zeropad_rung1', 'reference_type': 'copylf', "
                "'test_nrmse': " + repr(ref) + "}"
                if floors_reference_defect else None),
            "base_file_copylf_def_hash_note":
                "the base file's _provenance.copylf_def_hash is the pre-ADR "
                "hash (its 5 cells were certified 2026-08-08); this entry "
                "carries the post-ADR hash — the pfc reference construction "
                "changed under the ratified ADR, other cells' references "
                "were verified byte-identical by "
                "tools/recompute_pfc_reference_floors.py",
        },
    }
    if prov is None:
        entry["first_certification"] = (
            "no provisional constant exists for this dataset; this is its "
            "first certified threshold and it is cited in no falsification "
            "clause (card §'vs noise floor')")
    return entry


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results_dir", default=str(EXT_OUT / "eval"))
    ap.add_argument("--per_row_dir", default=str(EXT_OUT / "training"))
    ap.add_argument("--out_dir", default=str(EXT_OUT / "eval"))
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--n_boot_seed", type=int, default=10000)
    ap.add_argument("--n_boot_row", type=int, default=10000)
    ap.add_argument("--boot_seed", type=int, default=0)
    ap.add_argument("--apply", action="store_true",
                    help="ORCHESTRATOR-ONLY: archive + mutate the real "
                         "state/anchors_repaired/noise_floor.json")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]

    entry = compute_entry(Path(args.results_dir), Path(args.per_row_dir),
                          seeds, args.n_boot_seed, args.n_boot_row,
                          args.boot_seed)

    nf_path = ROUND3 / "state" / "anchors_repaired" / "noise_floor.json"
    base_txt = nf_path.read_text()
    base = json.loads(base_txt)
    assert NAME not in base, f"{NAME} already present in {nf_path}"
    assert base.get("_provisional") is False

    merged = dict(base)
    merged[NAME] = entry
    before = {k: v for k, v in base.items() if k != NAME}
    after = {k: v for k, v in merged.items() if k != NAME}
    assert json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True), \
        "non-pfc entry drifted"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cand = out_dir / "noise_floor_candidate_pfc_ext.json"
    cand.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n")
    diag = out_dir / "pfc_extension_diagnostic.json"
    diag.write_text(json.dumps({
        "_tool": "extend_noise_floor_pfc", "_utc": utc(),
        "pfc_entry": entry,
        "mode": "apply" if args.apply else "dry_run",
        "target": str(nf_path),
    }, indent=2, sort_keys=True) + "\n")
    print(f"[wrote] {cand}\n[wrote] {diag}")
    print(f"pfc: iqm {entry['iqm']:.4f}  seed_mce {entry['seed_mce']:.4f}  "
          f"row95 {entry['row_paired_95']:.4f}  mdd {entry['mdd_scored']:.4f}  "
          f"tau_rel {entry['tau_rel']:.4f}  tau_abs {entry['tau_abs']:.4f}")

    if not args.apply:
        print("[dry-run] state/ untouched")
        return

    # ---- sanctioned mutation (archive first; pfc key added, nothing else) ----
    arch = nf_path.with_name(f"noise_floor_pre_pfc_ext_{STAMP}.json")
    assert not arch.exists(), f"archive already exists: {arch}"
    shutil.copy2(nf_path, arch)
    # preserve the installed file's serialization if it round-trips; else
    # fall back to the candidate's canonical form
    written = False
    for ind, sk in ((2, False), (2, True), (1, False), (1, True), (4, False)):
        if json.dumps(base, indent=ind, sort_keys=sk) + "\n" == base_txt:
            nf_path.write_text(json.dumps(merged, indent=ind, sort_keys=sk) + "\n")
            written = True
            break
    if not written:
        nf_path.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n")
    check = json.loads(nf_path.read_text())
    assert NAME in check
    assert json.dumps({k: v for k, v in check.items() if k != NAME},
                      sort_keys=True) == json.dumps(before, sort_keys=True)
    print(f"[applied] {nf_path} (archive: {arch})")


if __name__ == "__main__":
    main()
