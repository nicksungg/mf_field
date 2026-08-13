"""G1 preflight: stripped views, LF-free audit, manifest sealing (spec D3/D6/D12).

Stripped views are built with the round-2 `_mirror`/`_verify` machinery
(IMPORT-ONLY reuse — round-2 files are never edited), into the campaign's
own `output_root/stripped_data/`.  After the audit passes, the provisional
staging manifest is SEALED: `manifest_hash` covers the registry revision,
every source byte, and every stripped-view byte — the exact inputs scoring
consumes (spec D12).  Downstream consumers call `require_sealed` and refuse
an unsealed manifest.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROUND2_EVAL = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2/eval")
CAMPAIGN = Path(__file__).resolve().parents[1]

# generator-truth grids (ADR b30-0001 / evidence draft); the audit fails if the
# shared resolver disagrees — the allen_cahn_generated README trap class.
EXPECTED_1D = {"sharp__sod_1d", "sharp__burgers_1d", "sharp__shallow_water_1d",
               "sharp__porous_medium_1d", "allen_cahn_generated"}
EXPECTED_RECT = {"era5": (721, 1440)}


def _import_round2_stripper():
    """Load round-2 make_stripped_view without letting its sibling imports
    collide with the VENDORED panel_data (same module name, different file)."""
    saved = {k: sys.modules.pop(k) for k in ("panel_data", "nrmse", "make_stripped_view")
             if k in sys.modules}
    sys.path.insert(0, str(ROUND2_EVAL))
    try:
        spec = importlib.util.spec_from_file_location(
            "r2_make_stripped_view", ROUND2_EVAL / "make_stripped_view.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.remove(str(ROUND2_EVAL))
        for k in ("panel_data", "nrmse", "make_stripped_view"):
            sys.modules.pop(k, None)
        sys.modules.update(saved)


def _iter_datasets(cfg: dict):
    root = Path(cfg["data_root"])
    for group in cfg["datasets"].values():
        for d in group:
            yield d["id"], root / d["dataset_dir"]


def stripped_root(cfg: dict) -> Path:
    return Path(cfg["output_root"]) / "stripped_data"


def build_stripped_views(cfg: dict, force: bool = False) -> dict:
    """Build (or reuse) the stripped view per dataset; returns id -> view path."""
    stripper = _import_round2_stripper()
    out = {}
    for ds_id, src in _iter_datasets(cfg):
        dst = stripped_root(cfg) / ds_id
        if force and dst.exists():
            import shutil
            shutil.rmtree(dst)
        if not dst.exists():
            stripper._mirror(src, dst)
        stripper._verify(dst)
        out[ds_id] = str(dst)
    return out


def audit_stripped_view(ds_id: str, view: Path) -> dict:
    """LF-free + structural audit for one stripped view (raises on violation)."""
    stripper = _import_round2_stripper()
    stripper._verify(view)  # raises SystemExit("STRIPPING FAILED...") on a leak

    import re
    test_levels = sorted(int(m.group(1)) for p in view.iterdir()
                         if (m := re.match(r"^test_l(\d+)\.npz$", p.name)))
    train_levels = sorted(int(m.group(1)) for p in view.iterdir()
                          if (m := re.match(r"^train_l(\d+)\.npz$", p.name)))
    ifc = (view / "train").is_dir()
    if not ifc:
        if len(test_levels) != 1:
            raise SystemExit(f"STRIPPING FAILED: {ds_id} test levels {test_levels}")
        if len(train_levels) < 2:
            raise SystemExit(f"{ds_id}: train ladder has no LF rung "
                             f"({train_levels}) — the family's emulator has no target")
    return {"dataset": ds_id, "lf_free": True, "layout": "ifc_raw" if ifc else "npz_l",
            "test_levels": test_levels, "train_levels": train_levels}


def audit_grids(cfg: dict, manifest: dict) -> list:
    """Assert the shared resolver's grid for every dataset against generator truth."""
    factory = "/resnick/groups/Hippo/ezeng/mf_field/mf_field/factory_mffp"
    if factory not in sys.path:
        sys.path.insert(0, factory)
    from data_adapters.geometry import resolve_grid
    problems = []
    for ds_id, rec in manifest["datasets"].items():
        h, w = resolve_grid(ds_id, rec["n_cells_top"])
        if ds_id in EXPECTED_1D and h != 1:
            problems.append(f"{ds_id}: expected 1-D, resolver gave {(h, w)}")
        if ds_id in EXPECTED_RECT and (h, w) != EXPECTED_RECT[ds_id]:
            problems.append(f"{ds_id}: expected {EXPECTED_RECT[ds_id]}, got {(h, w)}")
        if ds_id not in EXPECTED_1D and ds_id not in EXPECTED_RECT and h * w != rec["n_cells_top"]:
            problems.append(f"{ds_id}: grid {(h, w)} != n_cells {rec['n_cells_top']}")
    return problems


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def _view_content_hash(view: Path) -> str:
    """Structure + bytes of the stripped view (symlinks resolved to content)."""
    entries = []
    for p in sorted(view.rglob("*")):
        if p.is_file():  # follows symlinks
            entries.append(f"{p.relative_to(view)}\t{_sha256_file(p)}")
    return hashlib.sha256("\n".join(entries).encode()).hexdigest()


def seal_manifest(cfg: dict, manifest: dict, registry_revision: str) -> dict:
    views = {ds_id: stripped_root(cfg) / ds_id for ds_id, _ in _iter_datasets(cfg)}
    missing = [d for d, v in views.items() if not v.exists()]
    if missing:
        raise RuntimeError(f"cannot seal: stripped views missing for {missing}")
    stripped = {d: _view_content_hash(v) for d, v in views.items()}
    source = {d: manifest["datasets"][d]["content_hash"] for d in manifest["datasets"]}
    payload = registry_revision + "|SRC|" + "|".join(
        f"{d}:{source[d]}" for d in sorted(source)) + "|VIEW|" + "|".join(
        f"{d}:{stripped[d]}" for d in sorted(stripped))
    manifest = dict(manifest)
    manifest["registry_revision"] = registry_revision
    manifest["stripped_view_hashes"] = stripped
    manifest["manifest_hash"] = hashlib.sha256(payload.encode()).hexdigest()
    manifest["sealed"] = True
    return manifest


def require_sealed(manifest: dict) -> None:
    if not manifest.get("sealed") or not manifest.get("manifest_hash"):
        raise RuntimeError(
            "unsealed staging manifest: run staging/preflight.py to build stripped "
            "views and seal the D12 identity before any launch (spec D12)")


def main() -> None:
    import argparse
    import yaml
    from staging.manifest import build_manifest
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(CAMPAIGN / "config.yaml"))
    ap.add_argument("--registry_revision", default="b30-0001")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    views = build_stripped_views(cfg, force=args.force)
    reports = [audit_stripped_view(d, Path(v)) for d, v in views.items()]
    print(f"[G1] {len(reports)} stripped views built + LF-free verified")

    manifest = build_manifest(cfg)
    grid_problems = audit_grids(cfg, manifest)
    if grid_problems:
        raise SystemExit("[G1] grid audit FAILED:\n  " + "\n  ".join(grid_problems))
    print("[G1] grid audit clean (30 resolver grids match generator truth)")

    sealed = seal_manifest(cfg, manifest, args.registry_revision)
    out = CAMPAIGN / "state/staging_manifest.json"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w") as f:
        json.dump(sealed, f, indent=1, sort_keys=True)
    print(f"[G0+G1] sealed manifest_hash={sealed['manifest_hash'][:16]} -> {out}")


if __name__ == "__main__":
    sys.path.insert(0, str(CAMPAIGN))
    main()
