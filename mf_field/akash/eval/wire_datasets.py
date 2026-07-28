"""Wire the 42-dataset benchmark into the factory harness (idempotent).

Datasets are read from `<root>/benchmark_42/{core,ext,sharp}/<name>/`, indexed by
`benchmark_42/MANIFEST.csv`. Root is derived from this file's location, or taken
from $MFFP_ROOT.

1. Collision-safe symlinks into factory_mffp/data/:
     core   -> <name>            (unchanged; already present, unique names)
     ext    -> ext__<name>       (ext & sharp share helmholtz_2d, kuramoto_sivashinsky_1d)
     sharp  -> sharp__<name>
2. data_adapters/known_grids_extra.json : per (prefixed) dataset, the physical grids
   from meta.json ladder — (1,L) for 1-D so 64/256-length fields are NOT mis-squared.
3. Append a tiny loader to geometry.py (once) so KNOWN_GRIDS picks up the extra JSON.
4. Symlink akash/models/mf_fno_allpairs -> factory_mffp/models/ (harness discovers it).
5. Write akash/eval/bench_datasets.txt : the collision-safe dataset list for the sweep.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import os

# Repo root, derived from this file's location so the script works under any
# checkout path: <root>/mf_field/akash/eval/wire_datasets.py -> parents[3].
# MFFP_ROOT overrides it if set.
ROOT = Path(os.environ.get("MFFP_ROOT") or Path(__file__).resolve().parents[3])
MF = ROOT / "mf_field"
FACTORY = MF / "factory_mffp"
DATA = FACTORY / "data"

# All 42 datasets ship as one benchmark_42/ package, split by collection.
BENCH = ROOT / "benchmark_42"
MANIFEST = BENCH / "MANIFEST.csv"


def real_dir(coll, name):
    """benchmark_42/<collection>/<dataset>/, or None if absent.

    ext and sharp both contain helmholtz_2d and kuramoto_sivashinsky_1d as
    different datasets, so the collection directory is what disambiguates them.
    """
    c = BENCH / coll / name
    return c if c.is_dir() else None


def safe_name(coll, name):
    return name if coll == "core" else f"{coll}__{name}"


def grids_from_meta(d: Path):
    m = json.load(open(d / "meta.json"))
    ndim = int(m.get("ndim", 2))
    out = []
    for g in m["ladder"]:
        out.append([1, int(g[0])] if ndim == 1 else [int(g[0]), int(g[1])])
    return out


def main():
    rows = list(csv.DictReader(open(MANIFEST)))
    DATA.mkdir(parents=True, exist_ok=True)
    extra = {}
    names = []
    missing = []
    relinked = []
    conflicts = []
    for r in rows:
        coll, name = r["collection"], r["dataset"]
        d = real_dir(coll, name)
        if d is None:
            missing.append(f"{coll}/{name}"); continue
        sn = safe_name(coll, name)
        names.append(sn)
        link = DATA / sn
        # Relative target, so the checked-in symlinks stay valid in any checkout
        # (they are tracked in git; absolute paths would pin them to one machine).
        rel = Path(os.path.relpath(d, DATA))
        # Repoint existing symlinks: a link left over from an earlier layout may
        # be stale or dangling, and Path.exists() follows the link, so a broken
        # one reads as absent and symlink_to() would then raise FileExistsError.
        if link.is_symlink():
            if link.readlink() != rel:
                link.unlink()
                link.symlink_to(rel)
                relinked.append(sn)
        elif link.exists():
            # a real directory, not a link -- never clobber it
            conflicts.append(sn)
        else:
            link.symlink_to(rel)
        # extra grids for ext/sharp (core already in KNOWN_GRIDS / square-safe)
        if coll != "core" and (d / "meta.json").exists():
            extra[sn] = grids_from_meta(d)

    # 2) write extra grids json
    extra_path = FACTORY / "data_adapters" / "known_grids_extra.json"
    extra_path.write_text(json.dumps(extra, indent=1))

    # 3) append loader hook to geometry.py (once)
    geom = FACTORY / "data_adapters" / "geometry.py"
    src = geom.read_text()
    HOOK = "# --- auto: load extra known grids (ext/sharp benchmark datasets) ---"
    if HOOK not in src:
        hook = f'''

{HOOK}
def _load_extra_grids():
    import json as _json, os as _os
    p = _os.path.join(_os.path.dirname(__file__), "known_grids_extra.json")
    try:
        with open(p) as _f:
            for _k, _v in _json.load(_f).items():
                KNOWN_GRIDS[_k] = [tuple(_g) for _g in _v]
    except Exception:
        pass
_load_extra_grids()
'''
        geom.write_text(src + hook)
        print(f"[geometry.py] appended extra-grids loader hook")
    else:
        print(f"[geometry.py] hook already present")

    # 4) symlink allpairs into factory models
    ap_src = MF / "akash/models/mf_fno_allpairs"
    ap_link = FACTORY / "models/mf_fno_allpairs"
    if ap_src.exists() and not ap_link.exists():
        ap_link.symlink_to(ap_src)
        print(f"[models] symlinked mf_fno_allpairs")

    # 5) dataset list
    (MF / "akash/eval/bench_datasets.txt").write_text("\n".join(names) + "\n")

    print(f"\nwired {len(names)} datasets ({len(extra)} ext/sharp grid entries)")
    print(f"  root      : {ROOT}")
    print(f"  datasets  : {BENCH}")
    if relinked:
        print(f"  repointed : {len(relinked)} stale symlink(s) -> {', '.join(relinked[:6])}"
              + (" ..." if len(relinked) > 6 else ""))
    if conflicts:
        print(f"  SKIPPED   : {len(conflicts)} real dir(s) in data/, not replaced: {', '.join(conflicts)}")
    print(f"  missing   : {missing or 'none'}")
    print("dataset list -> akash/eval/bench_datasets.txt")


if __name__ == "__main__":
    main()
