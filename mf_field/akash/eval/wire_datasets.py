"""Wire the 43-dataset benchmark into the factory harness (idempotent).

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

ROOT = Path("/orcd/data/faez/001/nick")
MF = ROOT / "mf_field"
FACTORY = MF / "factory_mffp"
DATA = FACTORY / "data"
MANIFEST = ROOT / "mffp_bench_combined.csv"


def real_dir(coll, name):
    if coll == "core":
        c = DATA / name
        return c if c.exists() else (MF / name if (MF / name).exists() else None)
    if coll == "ext":
        b = ROOT / "mf_field_extension_data/data_400_100"
        for c in (b / f"{name}_generated", b / name):
            if c.exists():
                return c
    else:
        b = MF / "sharp_generated"
        for c in (b / f"{name}_generated", b / name, b / f"{name.replace('_2d','')}_generated"):
            if c.exists():
                return c
    return None


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
    for r in rows:
        coll, name = r["collection"], r["dataset"]
        d = real_dir(coll, name)
        if d is None:
            missing.append(f"{coll}/{name}"); continue
        sn = safe_name(coll, name)
        names.append(sn)
        link = DATA / sn
        if not link.exists():
            link.symlink_to(d)
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

    print(f"\nwired {len(names)} datasets ({len(extra)} ext/sharp grid entries). missing: {missing or 'none'}")
    print("dataset list -> akash/eval/bench_datasets.txt")


if __name__ == "__main__":
    main()
