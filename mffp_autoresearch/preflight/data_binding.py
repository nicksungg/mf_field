#!/usr/bin/env python3
"""Launch-time data binding for an autoresearch round (ADR r3-0003 D4, redteam L1/C05).

The round-2 score cache keys on (code_hash | dataset | epochs | seed) and the baselines
JSON carries no hash of the data bytes it was computed from, so after a dataset swap
(e.g. the pfc r3-0002 regeneration) every cached cell and reference remains silently
valid-looking. This tool closes that hole WITHOUT modifying the frozen eval layer:

  record   at round launch, hash every panel dataset's array bytes into a manifest
           (the round archives it, e.g. round3/state/data_hashes.json);
  verify   before ANY dispatch that leans on cached cells or recorded references,
           recompute and compare — exit 0 on match, exit 3 on any mismatch, with a
           per-dataset diff (files added / removed / resized, or content-only change).

Per dataset the binding is sha256 over the sorted concatenation of its array files
(*.npz / *.npy, recursive, symlinks followed), each prefixed by its relative path and
byte size. Streamed in 1 MiB chunks — no array parsing, ~disk speed.

Usage:
  python data_binding.py record --root <data_root> --datasets a b c --out manifest.json
  python data_binding.py verify --manifest manifest.json [--root <override_root>]

Exit codes: 0 ok / 2 usage or missing input at record time / 3 verify mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ARRAY_SUFFIXES = (".npz", ".npy")
CHUNK = 1 << 20


def _array_files(ds_dir: Path) -> list[Path]:
    """Every array file under the dataset dir, sorted by relative POSIX path.
    Follows symlinks (factory data dirs are symlinks to sibling dataset dirs)."""
    out: list[Path] = []
    for base, _dirs, files in os.walk(ds_dir, followlinks=True):
        for f in files:
            if f.endswith(ARRAY_SUFFIXES):
                out.append(Path(base) / f)
    return sorted(out, key=lambda p: p.relative_to(ds_dir).as_posix())


def hash_dataset(ds_dir: Path) -> dict:
    """Stream-hash a dataset's array files: sha256 over 'relpath\\0size\\0' + bytes,
    in sorted order. Returns the digest plus the file census used to compute it."""
    h = hashlib.sha256()
    files: dict[str, int] = {}
    for p in _array_files(ds_dir):
        rel = p.relative_to(ds_dir).as_posix()
        size = p.stat().st_size
        files[rel] = size
        h.update(f"{rel}\0{size}\0".encode())
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(CHUNK), b""):
                h.update(chunk)
    return {"sha256": h.hexdigest(), "n_files": len(files),
            "total_bytes": sum(files.values()), "files": files}


def cmd_record(args: argparse.Namespace) -> int:
    root = args.root.resolve()
    manifest = {
        "tool": "data_binding.py",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(root),
        "datasets": {},
    }
    for name in args.datasets:
        ds_dir = root / name
        if not ds_dir.is_dir():
            print(f"[record] ERROR: {ds_dir} is not a directory", file=sys.stderr)
            return 2
        ent = hash_dataset(ds_dir)
        if ent["n_files"] == 0:
            print(f"[record] ERROR: no array files (*.npz/*.npy) under {ds_dir}",
                  file=sys.stderr)
            return 2
        manifest["datasets"][name] = ent
        print(f"[record] {name:32s} {ent['sha256'][:16]}...  "
              f"{ent['n_files']} files, {ent['total_bytes']} bytes")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"[record] manifest -> {args.out}")
    return 0


def _diff_census(old: dict[str, int], new: dict[str, int]) -> list[str]:
    lines = []
    for rel in sorted(set(old) - set(new)):
        lines.append(f"    removed: {rel} ({old[rel]} bytes)")
    for rel in sorted(set(new) - set(old)):
        lines.append(f"    added:   {rel} ({new[rel]} bytes)")
    for rel in sorted(set(old) & set(new)):
        if old[rel] != new[rel]:
            lines.append(f"    resized: {rel} ({old[rel]} -> {new[rel]} bytes)")
    if not lines:
        lines.append("    content changed (identical file names + sizes)")
    return lines


def cmd_verify(args: argparse.Namespace) -> int:
    manifest = json.loads(args.manifest.read_text())
    root = (args.root or Path(manifest["root"])).resolve()
    mismatched = []
    for name, recorded in manifest["datasets"].items():
        ds_dir = root / name
        if not ds_dir.is_dir():
            mismatched.append(name)
            print(f"[verify] {name:32s} MISSING ({ds_dir} not a directory)")
            continue
        now = hash_dataset(ds_dir)
        if now["sha256"] == recorded["sha256"]:
            print(f"[verify] {name:32s} MATCH    {now['sha256'][:16]}...")
        else:
            mismatched.append(name)
            print(f"[verify] {name:32s} MISMATCH recorded {recorded['sha256'][:16]}... "
                  f"now {now['sha256'][:16]}...")
            for line in _diff_census(recorded.get("files", {}), now["files"]):
                print(line)
    if mismatched:
        print(f"\n[verify] FAIL: {len(mismatched)} dataset(s) diverged from the recorded "
              f"binding: {', '.join(mismatched)}")
        print("[verify] The recorded references/caches no longer describe these bytes. "
              "Set a HOLD; re-baseline via the sanctioned mutation path, then re-record.")
        return 3
    print(f"\n[verify] OK: all {len(manifest['datasets'])} dataset bindings match")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    rec = sub.add_parser("record", help="hash datasets into a binding manifest")
    rec.add_argument("--root", type=Path, required=True)
    rec.add_argument("--datasets", nargs="+", required=True)
    rec.add_argument("--out", type=Path, required=True)
    rec.set_defaults(fn=cmd_record)
    ver = sub.add_parser("verify", help="re-hash and compare against a manifest")
    ver.add_argument("--manifest", type=Path, required=True)
    ver.add_argument("--root", type=Path, default=None,
                     help="override the manifest's recorded root")
    ver.set_defaults(fn=cmd_verify)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
