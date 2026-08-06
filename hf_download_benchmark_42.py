#!/usr/bin/env python3
"""Resumable, content-verified mirror of benchmark_42/ from the gated HF dataset.

Default source is eloisezeng/mf_field (the corrected release); override with
MFFP_HF_REPO. Mirrors HF `benchmark_42/**` 1:1 into $MFFP_ROOT/benchmark_42/.

Supersedes nicksung/mf_field (2026-07-28), which still carries the
grid-registration, condition-incompleteness, and ifc-pairing defects. Seven
datasets differ between the two releases -- see benchmark_42/README.md
Revision history. Do not mix them.

WHY THIS VERIFIES BY HASH, NOT SIZE
-----------------------------------
An earlier version skipped any file already present at the identical byte size.
That is unsafe for exactly the update this script exists to deliver: re-pairing
the ifc fidelity ladders changed *which* samples sit at each level, not the array
shapes, so all 22 ifc arrays have byte-identical sizes across the two releases
with completely different contents. A size-only check silently keeps the
defective data and reports success.

So: skip only when the local sha256 matches the remote LFS sha256. Small
non-LFS files (json/csv/md) carry no LFS hash and are simply re-fetched.

Does NOT use snapshot_download(allow_patterns=...) (broken on huggingface_hub 1.x).

Usage:
    python hf_download_benchmark_42.py              # sync, report orphans
    python hf_download_benchmark_42.py --prune      # also delete local orphans
    python hf_download_benchmark_42.py --trust-size # old size-only behaviour (unsafe)
"""
import argparse
import hashlib
import os
import sys

from huggingface_hub import HfApi, hf_hub_download

REPO = os.environ.get("MFFP_HF_REPO", "eloisezeng/mf_field")
ROOT = os.environ.get("MFFP_ROOT", os.path.dirname(os.path.abspath(__file__)))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def up_to_date(dest, sib, trust_size):
    """True only when we can positively confirm the local file matches the remote."""
    if not os.path.exists(dest):
        return False
    if sib.size is not None and os.path.getsize(dest) != sib.size:
        return False            # size differs -> definitely stale, no need to hash
    if trust_size:
        return True
    remote_hash = sib.lfs.sha256 if sib.lfs else None
    if remote_hash is None:
        return False            # no hash to verify against -> re-fetch (these are tiny)
    return sha256(dest) == remote_hash


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prune", action="store_true",
                    help="delete local files under benchmark_42/ that are absent from the remote")
    ap.add_argument("--trust-size", action="store_true",
                    help="skip on equal size without hashing (UNSAFE across releases)")
    args = ap.parse_args()

    if args.trust_size:
        print("WARNING: --trust-size cannot detect the ifc re-pairing update "
              "(same sizes, different contents).", flush=True)

    api = HfApi()
    info = api.repo_info(repo_id=REPO, repo_type="dataset", files_metadata=True)
    sibs = sorted((s for s in info.siblings if s.rfilename.startswith("benchmark_42/")),
                  key=lambda s: s.rfilename)
    print(f"source repo: {REPO}", flush=True)
    print(f"benchmark_42 files on HF: {len(sibs)}", flush=True)

    downloaded = skipped = 0
    failed = []
    for i, s in enumerate(sibs):
        dest = os.path.join(ROOT, s.rfilename)
        if up_to_date(dest, s, args.trust_size):
            skipped += 1
        else:
            try:
                hf_hub_download(repo_id=REPO, repo_type="dataset",
                                filename=s.rfilename, local_dir=ROOT)
                downloaded += 1
            except Exception as e:  # noqa: BLE001
                failed.append((s.rfilename, f"{type(e).__name__}: {str(e)[:200]}"))
        if (i + 1) % 25 == 0 or (i + 1) == len(sibs):
            print(f"[{i+1}/{len(sibs)}] downloaded={downloaded} "
                  f"skipped={skipped} failed={len(failed)}", flush=True)

    # orphans: files the previous release shipped that this one does not.
    remote = {s.rfilename for s in sibs}
    base = os.path.join(ROOT, "benchmark_42")
    orphans = []
    for dp, dn, fn in os.walk(base):
        # never treat local pre-repair snapshots as orphans -- --prune would delete them
        dn[:] = [d for d in dn if not d.startswith(".") and "backup" not in d]
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), ROOT)
            if rel not in remote:
                orphans.append(rel)
    if orphans:
        print(f"\n{len(orphans)} local file(s) not present in {REPO}:", flush=True)
        for o in sorted(orphans)[:40]:
            print("   ", o, flush=True)
        if args.prune:
            for o in orphans:
                os.remove(os.path.join(ROOT, o))
            print(f"pruned {len(orphans)} orphan(s)", flush=True)
        else:
            print("re-run with --prune to delete them "
                  "(the ifc scalers/ from the old release belong here)", flush=True)

    print(f"\nDONE downloaded={downloaded} skipped={skipped} failed={len(failed)}",
          flush=True)
    for fn, e in failed:
        print("FAIL", fn, e, flush=True)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
