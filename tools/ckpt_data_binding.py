#!/usr/bin/env python
"""Role-resolved checkpoint<->data content binding (card `r3s4_audit-B2`, D1).

WHAT THIS ADDS (and what it deliberately does NOT touch)
--------------------------------------------------------
`mffp_autoresearch/preflight/data_binding.py` records ONE sha256 per dataset,
over every array file. That is the right launch-time instrument and it is NOT
edited here — this module *imports* it read-only and reuses its `hash_dataset`
so that `union_sha256` reproduces the recorded manifest digest byte-exactly.

`round3/tools/zero_work_resume_scan.py` reports the NECESSARY condition for the
stale-checkpoint defect (`executed_steps == 0`) and already looks for a
`data_binding` block in `last.pt` (its `BINDING_KEYS`). That tool is NOT edited
either — this module supplies the block it reads, and the ACTION PREDICATE that
turns "zero work" into a remedy.

Why a whole-dataset hash is not enough in THIS regime
-----------------------------------------------------
Round 3 is LF-at-train-only. A change confined to the TRAIN LF arrays
invalidates an LF-consuming arm and is a no-op for a condition-only arm on the
*identical* dataset; a change confined to the TEST arrays invalidates the score
but not the weights (the 18 `sharp__allen_cahn_2d` test-trim legs), while a
change to the TRAIN arrays invalidates the weights (the 18
`sharp__phase_field_crystal_2d` box-swap legs). A single digest cannot express
any of that, so the binding is resolved into SIX ROLES:

    train_cond  train_hf  train_lf  test_cond  test_hf  test_lf

ACTION PREDICATE (card part 3, verbatim)
----------------------------------------
    RETRAIN      iff executed_steps == 0 and any role in
                 roles_read intersect {train_*} mismatches
    else RESCORE if test_cond / test_hf mismatch
    else REREFERENCE if test_lf mismatch     (copy-LF denominator only)
    else NONE

`roles_read` is what the leg's own family declares it consumed; it is written
into `last.pt` beside the role hashes by `models_r3/_common/ckpt_binding.py`.

CENSUS CONTRACT (card falsification G2)
---------------------------------------
Every array file under a dataset dir is classified by an explicit declared rule.
The six roles cover exactly the set of files the round's loader
(`mf_field/factory_mffp/data_adapters/loaders.py`) opens for the `train` and
`test` splits; anything else (an `ood/` split, a `shards/` provenance dir, a
`_pretrim_backup_*/` archive) lands in `_unconsumed` WITH the rule that placed
it there. An array file matching no rule makes the census FAIL — it is never
silently dropped. Exhaustive: roles ∪ `_unconsumed` == all array files.
Disjoint: no file (or npz member) carries two roles.

Sub-commands
------------
  census        classify a dataset's array files into roles (structure only, fast)
  record        census + per-role sha256 + union_sha256 (the block written to last.pt)
  verify-legs   evaluate the R1..R6 rules over a leg corpus, emit a confusion matrix
  price-rules   alias of verify-legs kept for the card's naming

Exit codes: 0 ok / 2 usage or missing input / 3 census failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "ckpt_data_binding/1.0"

ROLES = ("train_cond", "train_hf", "train_lf",
         "test_cond", "test_hf", "test_lf")
TRAIN_ROLES = ("train_cond", "train_hf", "train_lf")
RESCORE_ROLES = ("test_cond", "test_hf")
REREFERENCE_ROLES = ("test_lf",)

ARRAY_SUFFIXES = (".npz", ".npy")
_NPZ_FILE_RE = re.compile(r"^(train|test)_l(\d+)\.npz$")   # loaders.py, verbatim


# ── read-only import of the SHIPPED launch-time instrument ──────────────────

def _preflight_dir() -> Path:
    """`mffp_autoresearch/preflight` in the MAIN checkout.

    A worktree copy would defeat the purpose: the whole point of
    `union_sha256` is that it reproduces the digest the SHIPPED tool recorded.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "mffp_autoresearch" / "preflight" / "data_binding.py"
        if cand.exists():
            return cand.parent
    raise SystemExit("could not locate mffp_autoresearch/preflight/data_binding.py")


sys.path.insert(0, str(_preflight_dir()))
import data_binding as _shipped_binding            # noqa: E402  (READ-ONLY import)

hash_dataset = _shipped_binding.hash_dataset        # the exact recorded digest


# ── layout + role classification ────────────────────────────────────────────

def _array_files(ds_dir: Path) -> list[Path]:
    """Same file set as data_binding.py's `_array_files` (sorted, symlinks followed)."""
    out: list[Path] = []
    for base, _dirs, files in os.walk(ds_dir, followlinks=True):
        for f in files:
            if f.endswith(ARRAY_SUFFIXES):
                out.append(Path(base) / f)
    return sorted(out, key=lambda p: p.relative_to(ds_dir).as_posix())


def detect_layout(ds_dir: Path) -> str:
    """'ifc_raw' | 'npz_l' — the two on-disk layouts loaders.py supports."""
    ds_dir = Path(ds_dir)
    train = ds_dir / "train"
    if train.is_dir() and any(p.is_dir() and p.name.startswith("fidelity_")
                              for p in train.iterdir()):
        return "ifc_raw"
    if _npz_root(ds_dir) is not None:
        return "npz_l"
    raise SystemExit(f"unknown dataset layout under {ds_dir}")


def _npz_root(ds_dir: Path) -> Path | None:
    """loaders.py::_find_npz_root — the dir holding {train,test}_l<k>.npz."""
    ds_dir = Path(ds_dir)
    if not ds_dir.is_dir():
        return None
    if any(_NPZ_FILE_RE.match(p.name) for p in ds_dir.iterdir() if p.is_file()):
        return ds_dir
    for sub in sorted(ds_dir.iterdir()):
        if sub.is_dir() and any(_NPZ_FILE_RE.match(p.name)
                                for p in sub.iterdir() if p.is_file()):
            return sub
    return None


def _npz_members(path: Path) -> list[str]:
    """Member names inside an .npz (without the `.npy` suffix), sorted."""
    with zipfile.ZipFile(path) as z:
        return sorted(n[:-4] if n.endswith(".npy") else n for n in z.namelist())


def _unit(rel: str, member, role: str, rule: str, nbytes: int) -> dict:
    return {"path": rel, "member": member, "role": role, "rule": rule,
            "nbytes": int(nbytes)}


def census(ds_dir) -> dict:
    """Classify every array file (npz: every member) into a role or `_unconsumed`.

    Raises SystemExit(3) only through `census_ok=False` in the caller; here an
    unclassifiable file is recorded in `unclassified` rather than dropped.
    """
    ds_dir = Path(ds_dir)
    layout = detect_layout(ds_dir)
    units: list[dict] = []
    unclassified: list[str] = []
    files = _array_files(ds_dir)

    if layout == "npz_l":
        root = _npz_root(ds_dir)
        consumed = {}          # rel -> (split, fid)
        for p in files:
            if p.parent != root:
                continue
            m = _NPZ_FILE_RE.match(p.name)
            if m:
                consumed[p.relative_to(ds_dir).as_posix()] = (m.group(1), int(m.group(2)))
        hf_fid = {}
        for split in ("train", "test"):
            fids = [f for (s, f) in consumed.values() if s == split]
            hf_fid[split] = max(fids) if fids else None

        for p in files:
            rel = p.relative_to(ds_dir).as_posix()
            if rel in consumed:
                split, fid = consumed[rel]
                is_hf = (fid == hf_fid[split])
                members = _npz_members(p)
                for mem in members:
                    if is_hf and mem == "x":
                        role, rule = f"{split}_cond", "npz_l:HF rung, member x -> condition"
                    elif is_hf and mem == "y":
                        role, rule = f"{split}_hf", "npz_l:HF rung, member y -> HF field"
                    elif not is_hf:
                        role, rule = f"{split}_lf", "npz_l:sub-HF rung -> LF (cond+field)"
                    else:
                        unclassified.append(f"{rel}#{mem}")
                        continue
                    units.append(_unit(rel, mem, role, rule, p.stat().st_size))
            elif "/ood/" in f"/{rel}" or rel.startswith("ood/"):
                units.append(_unit(rel, None, "_unconsumed",
                                   "npz_l:ood/ split is never scored by this round",
                                   p.stat().st_size))
            elif "shards/" in rel:
                units.append(_unit(rel, None, "_unconsumed",
                                   "npz_l:shards/ provenance dir, not the loader's npz root",
                                   p.stat().st_size))
            elif re.search(r"(^|/)_[a-z0-9_]*backup[a-z0-9_-]*/", rel):
                units.append(_unit(rel, None, "_unconsumed",
                                   "npz_l:_*backup*/ archive dir, not the loader's npz root",
                                   p.stat().st_size))
            else:
                unclassified.append(rel)

    else:  # ifc_raw
        fid_re = re.compile(r"^(train|test)/fidelity_(\d+)/(Xs|ys)\.npy$")
        hf_fid = {}
        for split in ("train", "test"):
            d = ds_dir / split
            fids = []
            if d.is_dir():
                for p in d.iterdir():
                    if p.is_dir() and p.name.startswith("fidelity_") and \
                            (p / "Xs.npy").exists():
                        fids.append(int(p.name.split("_")[1]))
            hf_fid[split] = max(fids) if fids else None
        for p in files:
            rel = p.relative_to(ds_dir).as_posix()
            m = fid_re.match(rel)
            if not m:
                if "/ood/" in f"/{rel}" or rel.startswith("ood/"):
                    units.append(_unit(rel, None, "_unconsumed",
                                       "ifc_raw:ood/ split is never scored by this round",
                                       p.stat().st_size))
                elif re.search(r"(^|/)_[a-z0-9_]*backup[a-z0-9_-]*/", rel):
                    units.append(_unit(rel, None, "_unconsumed",
                                       "ifc_raw:_*backup*/ archive dir", p.stat().st_size))
                else:
                    unclassified.append(rel)
                continue
            split, fid, which = m.group(1), int(m.group(2)), m.group(3)
            if fid == hf_fid[split]:
                role = f"{split}_cond" if which == "Xs" else f"{split}_hf"
                rule = f"ifc_raw:HF fidelity_{fid}, {which}.npy -> {role}"
            else:
                role = f"{split}_lf"
                rule = f"ifc_raw:sub-HF fidelity_{fid} -> {split}_lf"
            units.append(_unit(rel, None, role, rule, p.stat().st_size))

    by_role = {r: [] for r in ROLES}
    by_role["_unconsumed"] = []
    seen = {}
    duplicates = []
    for u in units:
        key = (u["path"], u["member"])
        if key in seen and seen[key] != u["role"]:
            duplicates.append(f"{u['path']}#{u['member']} -> {seen[key]} & {u['role']}")
        seen[key] = u["role"]
        by_role[u["role"]].append(u)

    n_files_covered = len({u["path"] for u in units})
    exhaustive = (not unclassified) and n_files_covered == len(files)
    disjoint = not duplicates
    return {
        "dataset_dir": str(ds_dir),
        "layout": layout,
        "hf_fid_by_split": hf_fid,
        "n_array_files": len(files),
        "n_units": len(units),
        "roles": {r: sorted(f"{u['path']}" + (f"#{u['member']}" if u["member"] else "")
                            for u in by_role[r]) for r in ROLES},
        "unconsumed": sorted(u["path"] for u in by_role["_unconsumed"]),
        "unconsumed_rules": sorted({u["rule"] for u in by_role["_unconsumed"]}),
        "role_rules": sorted({u["rule"] for u in units if u["role"] in ROLES}),
        "unclassified": sorted(unclassified),
        "duplicates": sorted(duplicates),
        "census_exhaustive": bool(exhaustive),
        "census_disjoint": bool(disjoint),
        "census_ok": bool(exhaustive and disjoint),
        "_units": units,
    }


# ── hashing ─────────────────────────────────────────────────────────────────

def _unit_bytes(ds_dir: Path, u: dict) -> bytes:
    p = ds_dir / u["path"]
    if u["member"] is None:
        return p.read_bytes()
    with zipfile.ZipFile(p) as z:                 # the stored .npy member, verbatim
        name = f"{u['member']}.npy"
        if name not in z.namelist():
            name = u["member"]
        return z.read(name)


def role_hashes(ds_dir, cen: dict = None) -> dict:
    """{role: sha256} over the role's units, sorted by (path, member).

    Prefix per unit: `path[#member]\\0nbytes\\0`, then the raw bytes — the same
    shape as data_binding.py's per-file prefix, extended to npz members so that
    a condition-only change and a field-only change inside ONE npz are
    distinguishable (the M1-vs-M5 discriminator the round needs).
    """
    ds_dir = Path(ds_dir)
    cen = cen or census(ds_dir)
    out = {}
    for role in ROLES:
        units = sorted((u for u in cen["_units"] if u["role"] == role),
                       key=lambda u: (u["path"], u["member"] or ""))
        h = hashlib.sha256()
        n_units = 0
        for u in units:
            b = _unit_bytes(ds_dir, u)
            key = u["path"] + (f"#{u['member']}" if u["member"] else "")
            h.update(f"{key}\0{len(b)}\0".encode())
            h.update(b)
            n_units += 1
        out[role] = {"sha256": h.hexdigest(), "n_units": n_units}
    return out


def record(ds_dir, dataset_name: str, roles_read=None) -> dict:
    """The block a family writes into `<ckpt_dir>/last.pt`."""
    ds_dir = Path(ds_dir)
    cen = census(ds_dir)
    if not cen["census_ok"]:
        raise SystemExit(
            f"[record] census FAILED for {ds_dir}: "
            f"unclassified={cen['unclassified']} duplicates={cen['duplicates']}")
    rh = role_hashes(ds_dir, cen)
    return {
        "dataset": dataset_name,
        "dataset_dir": str(ds_dir),
        "layout": cen["layout"],
        "roles": {r: rh[r]["sha256"] for r in ROLES},
        "role_n_units": {r: rh[r]["n_units"] for r in ROLES},
        "union_sha256": hash_dataset(ds_dir)["sha256"],
        "roles_read": sorted(roles_read or []),
        "tool_version": TOOL_VERSION,
        "recorded_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


# ── the action predicate + the priced ablations ─────────────────────────────

def mismatched_roles(recorded: dict, current: dict) -> list:
    return [r for r in ROLES if recorded["roles"].get(r) != current["roles"].get(r)]


def predicate_r1(recorded: dict, current: dict, roles_read, executed_steps) -> dict:
    """R1 — the card's role binding predicate, verbatim."""
    mism = mismatched_roles(recorded, current)
    read = set(roles_read or [])
    train_hits = [r for r in mism if r in TRAIN_ROLES and r in read]
    if executed_steps == 0 and train_hits:
        action, why = "RETRAIN", f"roles_read∩train mismatched: {train_hits}"
    elif [r for r in mism if r in RESCORE_ROLES]:
        action, why = "RESCORE", f"test cond/hf mismatched: {[r for r in mism if r in RESCORE_ROLES]}"
    elif [r for r in mism if r in REREFERENCE_ROLES]:
        action, why = "REREFERENCE", "test_lf mismatched (copy-LF denominator only)"
    else:
        action, why = "NONE", "no consumed role mismatched"
    return {"action": action, "why": why, "mismatched_roles": mism}


def predicate_r2(recorded: dict, current: dict, **_) -> dict:
    """R2 — round-2's WHOLE-DATASET certificate. One digest, one verdict."""
    changed = recorded.get("union_sha256") != current.get("union_sha256")
    return {"action": "RETRAIN" if changed else "NONE",
            "why": "whole-dataset sha256 changed" if changed else "whole-dataset sha256 identical",
            "mismatched_roles": None}


def predicate_r3(recorded: dict, current: dict, **_) -> dict:
    """R3 — train/test split WITHOUT `roles_read` (the MF role increment, ablated)."""
    mism = mismatched_roles(recorded, current)
    train_side = [r for r in mism if r.startswith("train_")]
    test_side = [r for r in mism if r.startswith("test_")]
    if train_side:
        return {"action": "RETRAIN", "why": f"train-side mismatch {train_side}",
                "mismatched_roles": mism}
    if test_side:
        return {"action": "RESCORE", "why": f"test-side mismatch {test_side}",
                "mismatched_roles": mism}
    return {"action": "NONE", "why": "neither side changed", "mismatched_roles": mism}


def predicate_r4(leg: dict, **_) -> dict:
    """R4 — `ckpt_older_than_result` (stale_checkpoint_audit.py's wall-clock rule)."""
    d = leg.get("ckpt_minus_result_seconds")
    stale = (d is not None) and (d < -float(leg.get("mtime_slack_seconds", 60.0)))
    return {"action": "RETRAIN" if stale else "NONE",
            "why": f"ckpt_mtime - result_mtime = {d}", "mismatched_roles": None}


def predicate_r5(leg: dict, floor_seconds: float = 5.0, **_) -> dict:
    """R5 — `train_seconds_collapsed`: the rule B1 priced at 62/62 false alarms."""
    ts = leg.get("train_seconds")
    collapsed = (ts is not None) and (float(ts) < floor_seconds)
    return {"action": "RETRAIN" if collapsed else "NONE",
            "why": f"train_seconds={ts} < floor {floor_seconds}", "mismatched_roles": None}


def predicate_r6(leg: dict, cutoff_epoch: float = None, **_) -> dict:
    """R6 — the blunt global `--data-changed-after <cutoff>` instrument.

    SHIPPED semantics, verbatim from `round3/tools/stale_checkpoint_audit.py`:
        if cutoff and ck.exists() and os.path.getmtime(ck) < cutoff: -> suspect
    i.e. "the data was repaired by time T, so every checkpoint older than T is
    suspect" — content-blind by construction, which is exactly what is being
    priced here.
    """
    ck = leg.get("ckpt_mtime_epoch")
    if cutoff_epoch is None or ck is None:
        return {"action": "NONE", "why": "no cutoff or no checkpoint mtime",
                "mismatched_roles": None}
    older = ck < cutoff_epoch
    return {"action": "RETRAIN" if older else "NONE",
            "why": f"ckpt mtime {ck} vs global data-changed-after cutoff "
                   f"{cutoff_epoch}",
            "mismatched_roles": None}


RULES = {
    "R1_role_binding": "binding",
    "R2_whole_hash": "binding",
    "R3_traintest_split": "binding",
    "R4_ckpt_older_than_result": "leg",
    "R5_train_seconds_collapsed": "leg",
    "R6_global_cutoff": "leg",
}


def apply_rule(rule: str, leg: dict, cutoff_epoch: float = None,
               train_seconds_floor: float = 5.0) -> dict:
    rec, cur = leg.get("recorded_binding"), leg.get("current_binding")
    if RULES[rule] == "binding" and (rec is None or cur is None):
        return {"action": "UNAVAILABLE", "why": "leg carries no binding",
                "mismatched_roles": None}
    if rule == "R1_role_binding":
        return predicate_r1(rec, cur, leg.get("roles_read"), leg.get("executed_steps"))
    if rule == "R2_whole_hash":
        return predicate_r2(rec, cur)
    if rule == "R3_traintest_split":
        return predicate_r3(rec, cur)
    if rule == "R4_ckpt_older_than_result":
        return predicate_r4(leg)
    if rule == "R5_train_seconds_collapsed":
        return predicate_r5(leg, train_seconds_floor)
    if rule == "R6_global_cutoff":
        return predicate_r6(leg, cutoff_epoch)
    raise SystemExit(f"unknown rule {rule!r}")


# ── Wilson score interval ───────────────────────────────────────────────────

def wilson(k: int, n: int, alpha: float = 0.05) -> list:
    """Wilson score interval (Wilson 1927). k successes of n; two-sided 1-alpha."""
    if n == 0:
        return [0.0, 1.0]
    z = _z_for(alpha)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [max(0.0, (c - half) / d), min(1.0, (c + half) / d)]


def _z_for(alpha: float) -> float:
    """Two-sided normal quantile via the inverse error function."""
    from statistics import NormalDist
    return NormalDist().inv_cdf(1.0 - alpha / 2.0)


ACTIONS = ("RETRAIN", "RESCORE", "REREFERENCE", "NONE")


def price_rules(legs: list, rules: list, blindspot_classes=(), alpha: float = 0.05,
                cutoff_epoch: float = None, train_seconds_floor: float = 5.0) -> dict:
    """4-class confusion matrix + Wilson intervals per rule, on the IDENTICAL legs.

    `blindspot_classes` are mutation classes pre-registered as a CONSERVATIVE
    BLIND SPOT (content-identical row permutations): they are reported in full
    but excluded from the false-positive denominator, exactly as pre-registered
    on the card. They are never excluded from recall.
    """
    blind = set(blindspot_classes or ())
    out = {"n_legs": len(legs), "alpha": alpha,
           "blindspot_classes": sorted(blind), "rules": {}}
    for rule in rules:
        conf = {t: {p: 0 for p in list(ACTIONS) + ["UNAVAILABLE"]} for t in ACTIONS}
        recall_num = {a: 0 for a in ACTIONS}
        recall_den = {a: 0 for a in ACTIONS}
        fp_num = fp_den = 0
        # SECOND false-positive reading, reported beside the first because the
        # card quotes both: "0/27 false RETRAIN" uses the NONE class as the
        # denominator, while "45 false RETRAIN calls out of 90 mutated legs"
        # counts every RETRAIN call on a leg whose truth is not RETRAIN.
        wr_num = wr_den = 0
        wr_num_all = wr_den_all = 0
        blind_calls = {p: 0 for p in list(ACTIONS) + ["UNAVAILABLE"]}
        per_leg = []
        for leg in legs:
            truth = leg["truth"]
            got = apply_rule(rule, leg, cutoff_epoch, train_seconds_floor)
            pred = got["action"]
            is_blind = leg.get("mutation") in blind
            wr_den_all += 1
            if pred == "RETRAIN" and truth != "RETRAIN":
                wr_num_all += 1
            if is_blind:
                blind_calls[pred] += 1
            else:
                conf[truth][pred] += 1
                recall_den[truth] += 1
                if pred == truth:
                    recall_num[truth] += 1
                if truth == "NONE":
                    fp_den += 1
                    if pred == "RETRAIN":
                        fp_num += 1
                wr_den += 1
                if pred == "RETRAIN" and truth != "RETRAIN":
                    wr_num += 1
            per_leg.append({"leg": leg["leg_id"], "mutation": leg.get("mutation"),
                            "arm": leg.get("arm"), "truth": truth,
                            "predicted": pred, "why": got["why"],
                            "blindspot": is_blind})
        out["rules"][rule] = {
            "confusion_excl_blindspot": conf,
            "recall": {a: {"k": recall_num[a], "n": recall_den[a],
                           "rate": (recall_num[a] / recall_den[a]) if recall_den[a] else None,
                           "wilson95": wilson(recall_num[a], recall_den[a], alpha)}
                       for a in ACTIONS},
            "false_retrain": {"k": fp_num, "n": fp_den,
                              "rate": (fp_num / fp_den) if fp_den else None,
                              "wilson95": wilson(fp_num, fp_den, alpha),
                              "denominator": "legs whose truth is NONE, blind spot excluded"},
            "wrong_retrain_calls_excl_blindspot": {
                "k": wr_num, "n": wr_den,
                "rate": (wr_num / wr_den) if wr_den else None,
                "wilson95": wilson(wr_num, wr_den, alpha),
                "denominator": "every priced leg whose truth is not RETRAIN, "
                               "blind spot excluded"},
            "wrong_retrain_calls_all_legs": {
                "k": wr_num_all, "n": wr_den_all,
                "rate": (wr_num_all / wr_den_all) if wr_den_all else None,
                "wilson95": wilson(wr_num_all, wr_den_all, alpha),
                "denominator": "every priced leg, blind spot INCLUDED"},
            "blindspot_calls": blind_calls,
            "per_leg": per_leg,
        }
    return out


# ── CLI ─────────────────────────────────────────────────────────────────────

def _json(obj) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, default=str)


def cmd_census(a) -> int:
    bad = []
    rows = {}
    for ds in a.datasets:
        cen = census(Path(a.root) / ds)
        cen.pop("_units", None)
        rows[ds] = cen
        flag = "OK  " if cen["census_ok"] else "FAIL"
        print(f"[census] {flag} {ds:34s} layout={cen['layout']:8s} "
              f"files={cen['n_array_files']:3d} units={cen['n_units']:3d} "
              f"unconsumed={len(cen['unconsumed'])}")
        for r in ROLES:
            print(f"           {r:11s} {len(cen['roles'][r]):3d} unit(s)")
        if not cen["census_ok"]:
            bad.append(ds)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(_json({"root": str(a.root), "datasets": rows,
                                      "census_failures": bad}))
        print(f"wrote {a.out}")
    if bad:
        print(f"[census] FAIL on {len(bad)} dataset(s): {bad}")
        return 3
    return 0


def cmd_record(a) -> int:
    blk = record(Path(a.dataset_dir), a.dataset_name,
                 roles_read=[r for r in (a.roles_read or "").split(",") if r])
    text = _json(blk)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text)
    print(text)
    return 0


def cmd_verify_legs(a) -> int:
    legs = json.loads(Path(a.legs).read_text())
    legs = legs["legs"] if isinstance(legs, dict) else legs
    res = price_rules(legs, [r for r in a.rules.split(",") if r],
                      blindspot_classes=[c for c in (a.blindspot or "").split(",") if c],
                      alpha=a.alpha, cutoff_epoch=a.cutoff_epoch,
                      train_seconds_floor=a.train_seconds_floor)
    for rule, r in res["rules"].items():
        fr = r["false_retrain"]
        print(f"[{rule:26s}] false RETRAIN {fr['k']}/{fr['n']} "
              f"wilson95={[round(x, 4) for x in fr['wilson95']]}  "
              + " ".join(f"{a_}:{r['recall'][a_]['k']}/{r['recall'][a_]['n']}"
                         for a_ in ACTIONS))
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(_json(res))
        print(f"wrote {a.out}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("census", help="classify a dataset's array files into roles")
    c.add_argument("--root", required=True)
    c.add_argument("--datasets", nargs="+", required=True)
    c.add_argument("--out", default=None)
    c.set_defaults(fn=cmd_census)

    r = sub.add_parser("record", help="census + role hashes + union_sha256")
    r.add_argument("--dataset_dir", required=True)
    r.add_argument("--dataset_name", required=True)
    r.add_argument("--roles_read", default="")
    r.add_argument("--out", default=None)
    r.set_defaults(fn=cmd_record)

    for name in ("verify-legs", "price-rules"):
        v = sub.add_parser(name, help="price the R1..R6 rules over a leg corpus")
        v.add_argument("--legs", required=True)
        v.add_argument("--rules", default=",".join(RULES))
        v.add_argument("--blindspot", default="")
        v.add_argument("--alpha", type=float, default=0.05)
        v.add_argument("--cutoff_epoch", type=float, default=None)
        v.add_argument("--train_seconds_floor", type=float, default=5.0)
        v.add_argument("--out", default=None)
        v.set_defaults(fn=cmd_verify_legs)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
