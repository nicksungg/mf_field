"""Materialize the round-2 stripped test view (spec §5, gate G1).

For every panel + guard dataset, build `stripped_data_root/<dataset>/` as a
symlink mirror of the original dataset dir in which every test split keeps
ONLY its highest fidelity level — test LF field files are physically absent,
so "no LF at test" is enforced structurally: a model cannot read what is not
there. Train files (all fidelities) remain complete; the top-level test file
keeps its `x` (the complete condition vector — the model's only test input)
and `y` (the HF target the family's smoke_eval scores against).

Layout rules, applied recursively (ood/* sub-ladders included):
  - a directory containing `test_l<i>.npz` files links all of them EXCEPT
    those with i < max(i);
  - a directory named `test` containing `fidelity_<F>` subdirs (ifc_raw
    layout) links only the max-F subdir;
  - every other file/dir is symlinked as-is.

Run:  python make_stripped_view.py [--force]
Idempotent; --force rebuilds from scratch. Ends with a verification pass that
raises if any LF test file is reachable in the view.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from panel_data import load_config, repo_root

TEST_NPZ = re.compile(r"^test_l(\d+)\.npz$")
FID_DIR = re.compile(r"^fidelity_(\d+)$")


def _mirror(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    test_levels = {
        int(TEST_NPZ.match(p.name).group(1)): p
        for p in src.iterdir() if TEST_NPZ.match(p.name)
    }
    keep_level = max(test_levels) if test_levels else None
    for p in sorted(src.iterdir()):
        m = TEST_NPZ.match(p.name)
        if m and int(m.group(1)) != keep_level:
            continue  # stripped: LF test field file absent from the view
        if p.is_dir():
            if p.name == "test" and any(FID_DIR.match(q.name) for q in p.iterdir()):
                fids = {int(FID_DIR.match(q.name).group(1)): q
                        for q in p.iterdir() if FID_DIR.match(q.name)}
                keep = fids[max(fids)]
                (dst / p.name).mkdir(exist_ok=True)
                (dst / p.name / keep.name).symlink_to(keep)
                for q in sorted(p.iterdir()):
                    if not FID_DIR.match(q.name):
                        (dst / p.name / q.name).symlink_to(q)
            else:
                _mirror(p, dst / p.name)
        else:
            (dst / p.name).symlink_to(p)


def _verify(view: Path) -> None:
    for d in [view, *[p for p in view.rglob("*") if p.is_dir()]]:
        levels = sorted(int(TEST_NPZ.match(p.name).group(1))
                        for p in d.iterdir() if TEST_NPZ.match(p.name))
        if len(levels) > 1:
            raise SystemExit(f"STRIPPING FAILED: {d} exposes test levels {levels}")
        if d.name == "test":
            fids = [q.name for q in d.iterdir() if FID_DIR.match(q.name)]
            if len(fids) > 1:
                raise SystemExit(f"STRIPPING FAILED: {d} exposes fidelities {fids}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    root = repo_root()
    cfg = load_config()
    data_root = root / cfg["paths"]["data_root"]
    out_root = root / cfg["paths"]["stripped_data_root"]
    datasets = list(cfg["panel"]) + list(cfg["guard_set"])

    for ds in datasets:
        src = (data_root / ds).resolve()
        if not src.exists():
            raise SystemExit(f"dataset dir not found: {src}")
        dst = out_root / ds
        if dst.exists():
            if not args.force:
                print(f"{ds}: exists, skipping (use --force to rebuild)")
                _verify(dst)
                continue
            shutil.rmtree(dst)
        _mirror(src, dst)
        _verify(dst)
        n_test = len(list(dst.rglob("test_l*.npz")))
        print(f"{ds}: stripped view built ({n_test} test npz kept)")
    print(f"stripped view root: {out_root}")


if __name__ == "__main__":
    main()
