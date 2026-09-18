"""Isolate the frozen direct and unpaired-corrector recipes per dataset.

Only this adapter, copied recipe sources and training/query-placeholder files are
visible to training entry points. Evaluation answers never enter a workspace.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parent
DIRECT = ["mf_fno_transfer_film", "mf_fno_allpairs", "convnext_unet_film",
          "fno_fire_distcond", "wno_transfer_film", "mf_deeponet", "st_hf_pod_gp"]
CORRECTORS = ["uqcorr_transolver_pred", "uqcorr_convnext_pred"]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def save_npz(path, **arrays):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    with temporary.open("wb") as stream:
        np.savez_compressed(stream, **arrays)
    os.replace(temporary, path)


def input_keys(x):
    x = np.asarray(x, np.float32).copy()
    x[x == 0] = 0
    return [np.ascontiguousarray(row).tobytes() for row in x]


def identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", value) or value in (".", ".."):
        raise ValueError(f"Invalid dataset identifier: {value!r}")
    return value


@contextlib.contextmanager
def training_loads(allowed):
    """Reject unexpected paths, including aliases to answer files."""
    original = np.load
    allowed = {Path(path).resolve() for path in allowed}
    if any({"answers", "reserved_answers", "readonly_answers"}.intersection(path.parts) for path in allowed):
        raise PermissionError("Training input resolves to a reserved answer store")

    def guarded(path, *args, **kwargs):
        if not isinstance(path, (str, os.PathLike)):
            raise PermissionError("Untracked NumPy input stream")
        resolved = Path(path).resolve()
        if resolved not in allowed or {"answers", "reserved_answers", "readonly_answers"}.intersection(resolved.parts):
            raise PermissionError(f"Training data access is not authorized: {resolved}")
        return original(path, *args, **kwargs)

    np.load = guarded
    try:
        yield
    finally:
        np.load = original


def grouped_folds(x_lf, x_hf):
    hf, lf = input_keys(x_hf), input_keys(x_lf)
    groups = list(dict.fromkeys(hf))
    if len(groups) < 5:
        raise ValueError("Five-fold OOF training needs at least five unique HF inputs")
    order = np.random.default_rng(1234).permutation(len(groups))
    folds = []
    for fold, indices in enumerate(np.array_split(order, 5)):
        held = {groups[i] for i in indices}
        hold = [i for i, key in enumerate(hf) if key in held]
        train = [i for i, key in enumerate(lf) if key not in held]
        if not hold or not train:
            raise ValueError("Each OOF fold needs held HF inputs and retained LF examples")
        folds.append(dict(fold=fold, hold_hf_rows=hold, train_lf_rows=train))
    return folds


def grouped_split(x, seed=42):
    keys = input_keys(x)
    groups = list(dict.fromkeys(keys))
    if len(groups) < 2:
        raise ValueError("Corrector validation needs two distinct training input identities")
    order = np.random.default_rng(seed).permutation(len(groups))
    count = min(len(groups) - 1, max(4, int(round(.1 * len(groups)))))
    held = {groups[i] for i in order[:count]}
    return dict(train_rows=[i for i, key in enumerate(keys) if key not in held],
                val_rows=[i for i, key in enumerate(keys) if key in held])


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"Frozen recipe changed; expected one occurrence of {old!r}")
    return source.replace(old, new)


def direct_source(source):
    """Change paths/grid dispatch only; model and optimizer recipes stay frozen."""
    source = replace_once(source, "    import data_adapters\n", """    import data_adapters
    import data_adapters.geometry as geometry
    geometry.KNOWN_GRIDS[a.dataset] = [tuple(v['grid']) for v in info['levels'].values()]
""")
    source = replace_once(source,
        "data=st_common.load_any(rel(a.dataset),str(ROOT/'data'),42,val_frac=0.,device='cpu',min_val=0)",
        "data=st_common.load_unpaired(rel(a.dataset),42,val_frac=0.,device='cpu',min_val=0)")
    source = replace_once(source, "        mod.load_mf_dataset=guarded_adapter\n", """        mod.load_mf_dataset=guarded_adapter
        if hasattr(mod, '_cap_grid'):
            mod._cap_grid = lambda *args, **kwargs: tuple(info['work_grid'])
""")
    return source


def corrector_source(source):
    """Generalize ERA5 constants, preserving loss, optimizer and checkpoint logic."""
    source = source.replace("(55,)", '(len(data["x_hf"]),)')
    source = source.replace("(55, *grid)", '(len(data["x_hf"]), *grid)')
    source = source.replace("(17, *grid)", '(len(data["x_query"]), *grid)')
    old = '''    if grid != (128, 256) or data["y_hf"].shape != (len(data["x_hf"]), *grid):
        raise ValueError("This campaign requires 55 fine training fields on the 128 by 256 grid")
    if data["x_hf"].shape != (55, 12) or data["x_query"].shape != (17, 12):
        raise ValueError("This campaign requires 55 HF and 17 reserved inputs with 12 parameters")'''
    new = '''    if len(grid) != 2 or min(grid) < 2 or data["y_hf"].shape != (len(data["x_hf"]), *grid):
        raise ValueError("Fine training fields do not match the frozen working grid")
    if data["x_hf"].ndim != 2 or data["x_query"].ndim != 2 or data["x_hf"].shape[1] != data["x_query"].shape[1]:
        raise ValueError("Training and query parameter dimensions do not match")
    cond_dim = data["x_hf"].shape[1]
    registration = plan["corrector_registration"]'''
    source = replace_once(source, old, new)
    changes = [
        ('bb.coordinates(grid, "periodic_node", device)', 'bb.coordinates(grid, registration, device)'),
        ('bb.build(args.backbone, 12, coords, 0, width=32, base=48)', 'bb.build(args.backbone, cond_dim, coords, 0, width=32, base=48)'),
        ('"registration": "periodic_node", "prolongation": "identity"', '"registration": registration, "prolongation": "identity"'),
        ('tag = f"{model_name}__era5"', 'tag = f"{model_name}__{plan[\'dataset\']}"'),
        ('"dataset": "era5", "smoke": args.smoke', '"dataset": plan["dataset"], "smoke": args.smoke'),
        ('query=17 grid={grid}', 'query={len(data[\'x_query\'])} grid={grid}'),
        ('.reshape(17, -1)', '.reshape(len(data["x_query"]), -1)'),
        ('pred.shape != (17, 32768)', 'pred.shape != (len(data["x_query"]), int(np.prod(grid)))'),
        ('"n_query": 17, "n_params"', '"n_query": len(data["x_query"]), "n_params"'),
    ]
    for old, new in changes:
        source = replace_once(source, old, new)
    return source


ANSWER_GUARD = '''"""Loaded automatically in every isolated training subprocess."""
import os
from pathlib import Path
import sys
def _deny_answers(event, args):
    if event == 'open' and args and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).expanduser().resolve()
        if {'answers', 'reserved_answers', 'readonly_answers'}.intersection(path.parts):
            raise PermissionError('Training cannot open reserved answers: ' + str(path))
sys.addaudithook(_deny_answers)
'''


def source_files(root):
    era5, repair = root / "vendor/era5", root / "vendor/repair"
    files = {}
    for name in ("run_coarse.py", "run_corrector.py", "era5_common.py"):
        files[name] = era5 / name
    for name in ("run_base.py", "repair_common.py", "stage_train.py"):
        files[name] = repair / name
    for folder in ("vendor", "data_adapters", "common", "uqcorr"):
        for path in (era5 / folder).rglob("*"):
            if path.is_file() and path.suffix in (".py", ".json") and "__pycache__" not in path.parts:
                files[str(path.relative_to(era5))] = path
    for path in files.values():
        if not path.is_file():
            raise FileNotFoundError(f"Missing frozen trainer source: {path}")
    for name in ("vendor/st_classical.py", "vendor/mf_fno_transfer_film/model.py", "uqcorr/corr_backbones.py"):
        if name not in files:
            raise FileNotFoundError(f"Missing frozen trainer dependency: {name}")
    return files


def read_dataset(root, dataset, info):
    folder = root / "data" / dataset
    levels = sorted(map(int, info["levels"]))
    if len(levels) < 2:
        raise ValueError("Multi-fidelity expert training requires at least two fidelity levels")
    hf = int(info["hf_level"])
    lf = int(info.get("lf_level", levels[-2]))
    if hf != levels[-1] or lf not in levels or lf >= hf:
        raise ValueError("Fidelity labels must increase from LF to HF")
    permitted = [folder / f"{split}_l{level}.npz" for level in levels for split in ("train", "test")]
    records, arrays, query = {}, {}, None
    with training_loads(permitted):
        for level in levels:
            entry = info["levels"][str(level)]
            grid = tuple(map(int, entry["grid"]))
            if len(grid) != 2 or min(grid) < 2:
                raise ValueError(f"Unsupported field grid at level {level}: {grid}")
            train_path, query_path = folder / f"train_l{level}.npz", folder / f"test_l{level}.npz"
            train_sha, query_sha = sha(train_path), sha(query_path)
            if train_sha != entry["prepared_sha256"] or query_sha != entry["query_sha256"]:
                raise ValueError(f"Prepared data changed at level {level}")
            with np.load(train_path, allow_pickle=False) as data:
                x, y = data["x"].astype(np.float32), data["y"].astype(np.float32)
            with np.load(query_path, allow_pickle=False) as data:
                qx, qy = data["x"].astype(np.float32), data["y"]
                if np.any(qy) or qy.shape[0] != len(qx) or qy.size != len(qx) * int(np.prod(grid)):
                    raise ValueError("Query fields must be zero placeholders on the native grid")
            if x.ndim != 2 or qx.ndim != 2 or x.shape[1] != qx.shape[1] or not len(x) or not len(qx):
                raise ValueError("Invalid training/query input dimensions")
            if y.size != len(x) * int(np.prod(grid)) or not np.isfinite(x).all() or not np.isfinite(qx).all() or not np.isfinite(y).all():
                raise ValueError("Invalid training field dimensions or nonfinite inputs")
            if query is None:
                query = qx
            if not np.array_equal(query, qx):
                raise ValueError("Query identity and order must match at every fidelity")
            if set(input_keys(x)) & set(input_keys(qx)):
                raise ValueError("Reserved query inputs occur in training")
            if len(set(input_keys(qx))) != len(qx):
                raise ValueError("Reserved query inputs must have unique identities")
            records[str(level)] = dict(entry, prepared_sha256=train_sha, query_sha256=query_sha)
            if level in (hf, lf):
                arrays[level] = (x, y, grid)
    return records, arrays, query, hf, lf


def resized(y, native, grid):
    import torch
    import torch.nn.functional as functional
    tensor = torch.from_numpy(np.ascontiguousarray(y, dtype=np.float32)).reshape(-1, 1, *native)
    if tuple(native) != tuple(grid):
        tensor = functional.interpolate(tensor, size=grid, mode="bilinear", align_corners=False)
    return tensor[:, 0].numpy().copy()


def prepare_workspace(root, dataset):
    """Input-only deterministic preparation; safe for concurrent array workers."""
    root = Path(root).resolve()
    dataset = identifier(dataset)
    plan = json.loads((root / "PLAN.json").read_text())
    info = plan["datasets"][dataset]
    files = source_files(root)
    source_hashes = {name: sha(path) for name, path in files.items()}
    identity = dict(plan_sha256=sha(root / "PLAN.json"), adapter_sha256=sha(Path(__file__)),
                    recipe_sources=source_hashes, dataset=dataset)
    workroot = root / "expert_work"
    workroot.mkdir(parents=True, exist_ok=True)
    workspace = workroot / dataset
    with (workroot / f".{dataset}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if (workspace / "PREPARED.json").exists():
            if json.loads((workspace / "PREPARED.json").read_text())["identity"] != identity:
                raise ValueError("Existing expert workspace differs from frozen plan, source or adapter")
            return workspace
        records, arrays, query, hf, lf = read_dataset(root, dataset, info)
        grid = tuple(map(int, info["work_grid"]))
        x_lf, y_lf, lf_grid = arrays[lf]
        x_hf, y_hf, hf_grid = arrays[hf]
        if x_lf.shape[1] != x_hf.shape[1]:
            raise ValueError("LF and HF parameter dimensions differ")
        temporary = Path(tempfile.mkdtemp(prefix=f".{dataset}.", dir=workroot))
        try:
            for name, path in files.items():
                dest = temporary / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, dest)
            (temporary / "run_base.py").write_text(direct_source((temporary / "run_base.py").read_text()))
            (temporary / "run_corrector.py").write_text(corrector_source((temporary / "run_corrector.py").read_text()))
            common = (temporary / "repair_common.py").read_text()
            common += f"\n# Explicit dataset-local adapter overrides.\nDATASETS = [{dataset!r}]\ndef rel(ds):\n    assert ds in DATASETS\n    return ds\n"
            (temporary / "repair_common.py").write_text(common)
            (temporary / "sitecustomize.py").write_text(ANSWER_GUARD)
            # The native table layout is reused by direct recipes; no answers are copied.
            (temporary / "data").mkdir(exist_ok=True)
            (temporary / "data" / dataset).symlink_to(root / "data" / dataset, target_is_directory=True)
            (temporary / "flat_data").mkdir()
            (temporary / "flat_data" / dataset).symlink_to(root / "data" / dataset, target_is_directory=True)
            info = dict(info, levels=records, n_base_hf_train=len(x_hf), n_query=len(query))
            local_plan = dict(plan, datasets={dataset: info})
            write_json(temporary / "PLAN.json", local_plan)
            save_npz(temporary / "data/training.npz", x_lf=x_lf, y_lf=resized(y_lf, lf_grid, grid),
                     x_hf=x_hf, y_hf=resized(y_hf, hf_grid, grid), x_query=query)
            folds = grouped_folds(x_lf, x_hf)
            tasks = [dict(fold=f["fold"], variant=v, seed=s, tag=f"{v}__F{f['fold']}of5__s{s}")
                     for f in folds for v in ("plain", "hetero") for s in (42, 123)]
            write_json(temporary / "COARSE_PLAN.json", dict(folds=folds, tasks=tasks))
            registration = info.get("corrector_registration", "generic")
            if registration not in ("generic", "interior_dirichlet", "periodic_cell", "periodic_node"):
                raise ValueError("Unrecognized predeclared corrector coordinate convention")
            experiment = dict(dataset=dataset, grid=list(grid), coarse_grid=list(grid),
                base_seed=plan.get("base_seed", 42), coarse_steps=plan.get("coarse_steps", 30000),
                corrector_steps=plan.get("corrector_steps", 6000), corrector_K=plan.get("corrector_K", 6),
                alpha=.2, corrector_registration=registration, corrector_split=grouped_split(x_hf),
                training_sha256=sha(temporary / "data/training.npz"),
                parent_plan_sha256=identity["plan_sha256"], lf_level=lf, hf_level=hf,
                n_lf_train=len(x_lf), n_hf_train=len(x_hf), n_query=len(query), cond_dim=x_hf.shape[1],
                preprocessing="Bilinear LF/HF to frozen working grid; align_corners=False; corrector identity prolongation",
                input_identity_rule="Exact float32 parameter bytes, with signed zero normalized")
            write_json(temporary / "EXPERIMENT.json", experiment)
            manifest = {name: sha(temporary / name) for name in files}
            manifest["sitecustomize.py"] = sha(temporary / "sitecustomize.py")
            write_json(temporary / "SOURCE.json", manifest)
            write_json(temporary / "PREPARED.json", dict(identity=identity, reserved_answers_loaded=False,
                reserved_input_training_overlap=0, query_placeholders_verified=True,
                source_manifest_sha256=sha(temporary / "SOURCE.json")))
            os.replace(temporary, workspace)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    return workspace


def export_prediction(root, workspace, dataset, model, smoke):
    local = workspace / "smoke" if smoke else workspace
    destination = root / "smoke" if smoke else root
    tag = f"{model}__{dataset}"
    source = local / "predictions" / f"{tag}.npz"
    metadata = json.loads((local / "metadata" / f"{tag}.json").read_text())
    if metadata["prediction_sha256"] != sha(source) or metadata["smoke"] != smoke:
        raise ValueError("Recipe prediction metadata does not match output bytes or mode")
    with np.load(source, allow_pickle=False) as data:
        x, pred, grid = data["theta"], data["pred"], data["work_grid"]
    expected = json.loads((workspace / "EXPERIMENT.json").read_text())
    if pred.shape != (expected["n_query"], int(np.prod(expected["grid"]))) or not np.isfinite(pred).all():
        raise ValueError("Invalid flattened query predictions")
    with np.load(workspace / "data/training.npz", allow_pickle=False) as data:
        np.testing.assert_array_equal(x, data["x_query"])
    output = destination / "predictions" / dataset / f"{model}.npz"
    save_npz(output, X=np.asarray(x, np.float32), theta=np.asarray(x, np.float32),
             pred=np.asarray(pred, np.float32), work_grid=np.asarray(grid, np.int64))
    metadata.update(dataset=dataset, model=model, prediction_sha256=sha(output),
        prediction_file=str(output.relative_to(root)), isolated_workspace=str(workspace.relative_to(root)),
        original_recipe_prediction_sha256=sha(source), parent_plan_sha256=sha(root / "PLAN.json"),
        adapter_sha256=sha(Path(__file__)), reserved_answers_loaded=False, scientific_result=not smoke)
    write_json(destination / "metadata" / dataset / f"{model}.json", metadata)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--kind", required=True, choices=("direct", "coarse", "assemble", "corrector"))
    parser.add_argument("--model")
    parser.add_argument("--index", type=int)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if args.kind == "direct" and args.model not in DIRECT:
        parser.error("direct requires one of the seven direct --model names")
    if args.kind == "corrector" and args.model not in CORRECTORS:
        parser.error("corrector requires uqcorr_transolver_pred or uqcorr_convnext_pred")
    if args.kind == "coarse" and (args.index is None or not 0 <= args.index < 20):
        parser.error("coarse requires --index 0 through 19")
    workspace = prepare_workspace(ROOT, args.dataset)
    if args.prepare_only:
        print(workspace)
        return
    if args.kind == "direct":
        command = ["run_base.py", "--dataset", args.dataset, "--model", args.model]
    elif args.kind == "corrector":
        command = ["run_corrector.py", "--backbone", args.model.removeprefix("uqcorr_").removesuffix("_pred")]
    else:
        command = ["run_coarse.py", "--assemble"] if args.kind == "assemble" else ["run_coarse.py", "--task", str(args.index)]
    if args.smoke:
        command.append("--smoke")
    environment = dict(os.environ, PYTHONPATH=str(workspace), OMP_NUM_THREADS=os.environ.get("OMP_NUM_THREADS", "4"))
    subprocess.run([sys.executable, *command], cwd=workspace, env=environment, check=True)
    if args.kind in ("direct", "corrector"):
        print("EXPORTED", export_prediction(ROOT, workspace, args.dataset, args.model, args.smoke), flush=True)


if __name__ == "__main__":
    main()
