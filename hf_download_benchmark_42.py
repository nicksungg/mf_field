#!/usr/bin/env python3
"""Resumable download of benchmark_42/ from the gated HF dataset eloisezeng/mf_field.

Mirrors HF `benchmark_42/**` 1:1 into $MFFP_ROOT/benchmark_42/.
Skips files already present at the identical byte size. Does NOT use
snapshot_download(allow_patterns=...) (broken on huggingface_hub 1.x).

Supersedes nicksung/mf_field (2026-07-28), which still carries the grid-registration,
condition-incompleteness, and ifc-pairing defects. Seven datasets differ between the
two releases — see benchmark_42/README.md § Revision history. Do not mix them.
"""
import os
import sys
from huggingface_hub import HfApi, hf_hub_download

REPO = os.environ.get("MFFP_HF_REPO", "eloisezeng/mf_field")
ROOT = os.environ.get("MFFP_ROOT", os.path.dirname(os.path.abspath(__file__)))

api = HfApi()
info = api.repo_info(repo_id=REPO, repo_type="dataset", files_metadata=True)
sibs = [s for s in info.siblings if s.rfilename.startswith("benchmark_42/")]
sibs.sort(key=lambda s: s.rfilename)
print(f"benchmark_42 files on HF: {len(sibs)}", flush=True)

downloaded = skipped = 0
failed = []
for i, s in enumerate(sibs):
    fn = s.rfilename
    size = s.size
    dest = os.path.join(ROOT, fn)
    if os.path.exists(dest) and size is not None and os.path.getsize(dest) == size:
        skipped += 1
        continue
    try:
        hf_hub_download(repo_id=REPO, repo_type="dataset", filename=fn,
                        local_dir=ROOT)
        downloaded += 1
    except Exception as e:  # noqa: BLE001
        failed.append((fn, f"{type(e).__name__}: {str(e)[:200]}"))
    if (i + 1) % 25 == 0 or (i + 1) == len(sibs):
        print(f"[{i+1}/{len(sibs)}] downloaded={downloaded} "
              f"skipped={skipped} failed={len(failed)}", flush=True)

print(f"\nDONE downloaded={downloaded} skipped={skipped} failed={len(failed)}",
      flush=True)
for fn, e in failed:
    print("FAIL", fn, e, flush=True)
sys.exit(1 if failed else 0)
