#!/usr/bin/env python3
"""Frozen baseline recipes on a PLAN-defined, answer-isolated dataset.

Outputs are FP32 raw-unit fields and query inputs. --smoke changes training
budgets and writes only under smoke/. Production recipe budgets are fixed.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import fcntl
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import time
import types

ROOT = Path(__file__).resolve().parent
CLASSICAL = ("st_koh_pod", "st_nargp_pod", "st_lf_affine_pod", "st_knn", "st_mean")
NEURAL = ("st_mfdnn", "st_mfdeeponet", "st_dmfal")
PAPER = ("nomad_mf", "mfrnp", "fno_coregionalization", "mf_fno_transfer")
ALIAS = "mf_fno_transfer_bar"
MODELS = CLASSICAL + NEURAL + PAPER + (ALIAS,)


def sha(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 22), b""):
            result.update(block)
    return result.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    os.replace(temporary, path)


def output_paths(dataset, model, smoke=False):
    base = ROOT / "smoke" if smoke else ROOT
    return base / "predictions" / dataset / f"{model}.npz", base / "metadata" / dataset / f"{model}.json"


def dataset_info(dataset):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", dataset):
        raise ValueError("Invalid dataset identifier")
    plan = json.loads((ROOT / "PLAN.json").read_text())
    info = plan["datasets"][dataset]
    directory = (ROOT / info.get("data_dir", f"data/{dataset}")).resolve()
    if not directory.is_relative_to((ROOT / "data").resolve()):
        raise ValueError("Dataset directory must be in the staged data tree")
    return plan, info, directory


@contextlib.contextmanager
def protected_numpy_load(paths):
    """Allow only explicit staged arrays; reject symlink escapes and file objects."""
    import numpy as np
    original = np.load
    permitted = {Path(path).resolve() for path in paths}
    loaded = []

    def guarded(path, *args, **kwargs):
        if not isinstance(path, (str, os.PathLike)):
            raise PermissionError("Training NumPy loads require an audited path")
        resolved = Path(path).resolve()
        if "answers" in resolved.parts or resolved not in permitted:
            raise PermissionError(f"Unaudited training data read: {resolved}")
        if kwargs.get("allow_pickle", False) or (len(args) > 1 and args[1]):
            raise PermissionError("Pickled arrays are not permitted")
        loaded.append(str(resolved))
        return original(path, *args, **kwargs)

    np.load = guarded
    try:
        yield loaded
    finally:
        np.load = original


def staged_paths(info, directory):
    return [directory / f"{split}_l{level}.npz"
            for level in sorted(info["levels"], key=int) for split in ("train", "test")]


def load_staged(info, directory):
    """Read all training fields, validate and discard every query placeholder."""
    import numpy as np
    train, query = {}, None
    hashes = {}
    for level in sorted(map(int, info["levels"])):
        detail = info["levels"][str(level)]
        grid = tuple(map(int, detail["grid"]))
        if len(grid) != 2 or min(grid) < 1:
            raise ValueError(f"Invalid native grid for level {level}")
        for split in ("train", "test"):
            path = directory / f"{split}_l{level}.npz"
            actual = sha(path)
            expected = detail["prepared_sha256" if split == "train" else "query_sha256"]
            if actual != expected:
                raise ValueError(f"Staged file hash changed: {path}")
            hashes[path.name] = actual
            with np.load(path, allow_pickle=False) as archive:
                x = np.asarray(archive["x"], np.float32).copy()
                y = np.asarray(archive["y"], np.float32).copy()
            if x.ndim != 2 or y.size != len(x) * int(np.prod(grid)):
                raise ValueError(f"Invalid staged array dimensions: {path}")
            y = y.reshape(len(x), -1)
            if not np.isfinite(x).all() or not np.isfinite(y).all():
                raise ValueError(f"Nonfinite staged data: {path}")
            if split == "train":
                if len(x) != detail["kept_train_count"] or len(x) < 2:
                    raise ValueError(f"Invalid training count: {path}")
                train[level] = dict(x=x, y=y, grid=grid)
            else:
                if np.count_nonzero(y):
                    raise ValueError(f"Query answers must be zero placeholders: {path}")
                if len(x) != info["n_query"]:
                    raise ValueError(f"Query count mismatch: {path}")
                if query is not None and not np.array_equal(query, x):
                    raise ValueError("Query input order differs across fidelity levels")
                query = x
    hf = int(info["hf_level"])
    if hf != max(train) or len(train[hf]["x"]) != info["n_base_hf_train"]:
        raise ValueError("Highest fidelity/count differs from PLAN")
    if len(train) < 2:
        raise ValueError("Multi-fidelity baselines require at least two training levels")
    reserved = {tuple(row) for row in query}
    for level, data in train.items():
        if data["x"].shape[1] != query.shape[1]:
            raise ValueError("Condition dimension differs across levels")
        if any(tuple(row) in reserved for row in data["x"]):
            raise ValueError(f"Reserved query input appears in training level {level}")
    return train, query, hashes


@contextlib.contextmanager
def isolated_imports(names, paths):
    """Restore vendor module names and import roots after every recipe."""
    def selected(name):
        return any(name == prefix or name.startswith(prefix + ".") for prefix in names)
    previous_path = sys.path.copy()
    previous = {name: module for name, module in list(sys.modules.items()) if selected(name)}
    for name in previous:
        del sys.modules[name]
    sys.path[:0] = list(map(str, paths))
    try:
        yield
    finally:
        for name in list(sys.modules):
            if selected(name):
                del sys.modules[name]
        sys.modules.update(previous)
        sys.path[:] = previous_path


def training_arguments(model, dataset, smoke=False):
    args = argparse.Namespace(arm=model, dataset=dataset, seed=42, pod_modes=64,
        pod_energy=.999, gp_restarts=2, nargp_samples=32, nargp_lf_modes=16,
        steps=100000, batch=16, points=512, hidden=[128] * 4,
        latent=32 if model == "st_dmfal" or model in CLASSICAL else 128,
        sensors=256, lr=1e-3, wd=1e-4, eval_every=500)
    if smoke:
        args.steps, args.eval_every = 2, 1
        args.batch, args.points = 2, 32
        args.gp_restarts, args.nargp_samples = 1, 2
    return args


def prepare_statistical(train, query, info, dataset, common, device, classical):
    """Match paired/unpaired released normalization using training rows only."""
    import numpy as np
    import torch
    hf = int(info["hf_level"])
    lf = max(level for level in train if level != hf)
    paired = all(np.array_equal(level["x"], train[hf]["x"]) for level in train.values())
    grids = [level["grid"] for level in train.values()]
    paired = paired and all(a[0] * a[1] < b[0] * b[1] for a, b in zip(grids, grids[1:]))
    minimum = int(info.get("baseline_min_validation", 6 if dataset == "era5" else 4))
    def split(n, seed):
        nval = 0 if classical else min(n - 1, max(minimum, round(.1 * n)))
        perm = np.random.default_rng(seed).permutation(n)
        return np.sort(perm[nval:]), np.sort(perm[:nval])
    hf_tr, hf_va = split(len(train[hf]["x"]), 42)
    lf_tr, lf_va = (hf_tr, hf_va) if paired else split(len(train[lf]["x"]), 43)
    mean = train[hf]["x"][hf_tr].mean(0)
    std = np.maximum(train[hf]["x"][hf_tr].std(0), 1e-6)
    tensor = lambda value: torch.as_tensor(value, dtype=torch.float32, device=device)
    native = {level: tensor(data["y"]).reshape(-1, *data["grid"])
              for level, data in train.items()}
    scale = float(native[lf][lf_tr].square().mean().sqrt())
    if scale <= 1e-12:
        raise ValueError("Degenerate low-fidelity training scale")
    grid = tuple(info["work_grid"])
    reg, reg_errors = "generic", {}
    if paired:
        from ct_common import choose_registration
        reg, reg_errors = choose_registration(native[lf][lf_tr], native[hf][hf_tr], train[hf]["grid"])
    field_hf = common.prolong(native[hf], grid, reg) / scale
    field_lf = native[lf] / scale
    levels = [dict(X=tensor((train[level]["x"] - mean) / std),
                   Y=(field_hf if level == hf else native[level] / scale),
                   grid=(grid if level == hf else train[level]["grid"])) for level in train]
    return dict(rel=dataset, name=dataset, paired=paired, cond_dim=query.shape[1], scale=scale,
        registration=reg, grid=grid, grid_lf=train[lf]["grid"], n_levels=len(train),
        X_hf=tensor((train[hf]["x"] - mean) / std), Y_hf=field_hf, hf_tr=hf_tr, hf_va=hf_va,
        X_lf=tensor((train[lf]["x"] - mean) / std), Y_lf=field_lf,
        Y_lf_up=common.prolong(field_lf, grid, reg), lf_tr=lf_tr, lf_va=lf_va,
        levels=levels, Xtest=tensor((query - mean) / std),
        manifest=dict(paired_exactly=paired, registration=reg, registration_errors=reg_errors,
                      hf_fid=hf, lf_fid=lf, work_grid=list(grid),
                      test_lf_used_at_inference=False, normalization_from_training_only=True))


def run_statistical(model, dataset, info, train, query, device, smoke):
    import numpy as np
    import torch
    args = training_arguments(model, dataset, smoke)
    names = ("st_common", "st_classical", "st_neural", "ct_common")
    with isolated_imports(names, [ROOT / "vendor" / "st_bench"]):
        common = importlib.import_module("st_common")
        classical = importlib.import_module("st_classical")
        # The release computes one NARGP diagnostic against held-out answers.
        # Remove only that reporting expression; the predicted field is unchanged.
        old = 'plugin_test_rel_l2=float(rel_l2_per_sample(pred_plug, data["Ytest"]).mean())'
        source = Path(classical.__file__).read_text()
        if old in source:
            if source.count(old) != 1:
                raise ValueError("Unexpected NARGP diagnostic source")
            source = source.replace(old, 'plugin_test_diagnostic_omitted="answers withheld"')
            exec(compile(source, classical.__file__, "exec"), classical.__dict__)
        neural = importlib.import_module("st_neural")
        common.seed_all(args.seed)
        data = prepare_statistical(train, query, info, dataset, common, device, model in CLASSICAL)
        if smoke and model in CLASSICAL:
            # Independent subsets lose paired indexing; emulate LF at HF rows.
            data["paired"] = False
            for prefix, maximum in (("hf", 12), ("lf", 16)):
                rows = data[f"{prefix}_tr"][:maximum]
                for key in (f"X_{prefix}", f"Y_{prefix}"):
                    data[key] = data[key][rows]
                if prefix == "lf":
                    data["Y_lf_up"] = data["Y_lf_up"][rows]
                data[f"{prefix}_tr"] = np.arange(len(rows))
                data[f"{prefix}_va"] = np.empty(0, dtype=np.int64)
            original = common.fit_gp
            def short_fit(*a, **kw):
                return original(*a, **dict(kw, maxiter=2))
            common.fit_gp = classical.fit_gp = short_fit
        if model in CLASSICAL:
            if model in ("st_knn", "st_mean"):
                pred, extra = classical.ARMS[model](data, args)
            else:
                pred, extra = classical.ARMS[model](data, args, classical._lf_emulator(data, args))
            params = 0
        else:
            pred, extra, _, params = neural.ARMS[model](data, args, device)
        if "plugin_test_rel_l2" in extra or "lf_emulator_test_rel_l2" in extra:
            raise RuntimeError("A forbidden query diagnostic was computed")
        result = pred.detach().cpu().numpy().astype(np.float32) * data["scale"]
        metadata = dict(training_arguments=vars(args), n_params=int(params),
            loader_manifest=data["manifest"], normalization_scale=data["scale"],
            hf_fit_rows=data["hf_tr"].tolist(), hf_validation_rows=data["hf_va"].tolist(),
            lf_fit_rows=data["lf_tr"].tolist(), lf_validation_rows=data["lf_va"].tolist(),
            actual_hf_fit_count=len(data["hf_tr"]), actual_lf_fit_count=len(data["lf_tr"]),
            query_targets_removed_before_fit=True, resume_supported=False,
            resume_note="Released statistical/neural arms restart their fit after interruption.", fit=extra)
    return result, metadata


def paper_adapter(train, query, info, directory):
    import numpy as np
    hf = int(info["hf_level"])
    def load(path, split="train", *args, **kwargs):
        if Path(path).resolve() != directory.resolve():
            raise PermissionError("Paper recipe attempted to use a different dataset")
        if split == "ood":
            raise FileNotFoundError("No OOD answers belong to this campaign")
        if split not in ("train", "test"):
            raise PermissionError(f"Unexpected dataset split: {split}")
        # Query placeholders are newly allocated; no held-out fields are retained.
        return dict(fids=list(train), hf_fid=hf, lf_fids=[level for level in train if level != hf],
            cond_by_fid={level: data["x"] if split == "train" else query for level, data in train.items()},
            field_by_fid={level: data["y"] if split == "train" else np.zeros((len(query), data["y"].shape[1]), np.float32)
                          for level, data in train.items()},
            n_cells_by_fid={level: data["y"].shape[1] for level, data in train.items()},
            cond_dim=query.shape[1], loader="audited_staged_npz")
    grids = {}
    for data in train.values():
        cells = int(np.prod(data["grid"]))
        if cells in grids and grids[cells] != data["grid"]:
            raise ValueError("Ambiguous grid dimensions with identical cell counts")
        grids[cells] = data["grid"]
    def resolve(name, cells):
        return grids[int(cells)]
    return load, resolve


@contextlib.contextmanager
def import_paper(model, identity):
    names = ("model", "lib", "torchvision", "_common", "common", "data_adapters",
             "paper_resume", "stage_train", "baseline_common", "_campaign_recipe")
    paths = [ROOT, ROOT / "vendor" / "paper", ROOT / "vendor" / "baseline_runtime"]
    with isolated_imports(names, paths):
        shim = types.ModuleType("baseline_common")
        shim.write_json = write_json
        sys.modules["baseline_common"] = shim
        resume = importlib.import_module("paper_resume")
        stage = importlib.import_module("stage_train")
        source = ROOT / "vendor" / "paper" / model / "smoke_eval.py"
        code = source.read_text()
        if model == "mfrnp":
            for package in ("model", "lib"):
                namespace = types.ModuleType(package)
                namespace.__path__ = [str(source.parent / "upstream" / package)]
                sys.modules[package] = namespace
            code = resume.adapt_mfrnp(code)
        else:
            spec = importlib.util.spec_from_file_location("model", source.parent / "model.py")
            module = importlib.util.module_from_spec(spec)
            sys.modules["model"] = module
            spec.loader.exec_module(module)
            if model == "fno_coregionalization":
                code = resume.adapt_coregionalization(code)
        spec = importlib.util.spec_from_file_location("_campaign_recipe", source)
        recipe = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = recipe
        recipe.__dict__.update(_RUN_IDENTITY=identity, atomic_save=resume.atomic_save,
                              capture_rng=resume.capture_rng, restore_rng=resume.restore_rng)
        exec(compile(code, str(source), "exec"), recipe.__dict__)
        if model == "mfrnp":
            recipe.MFLoader = resume.resumable_mf_loader(recipe.MFLoader)
        yield recipe, stage.StageTrainer


def run_paper(model, dataset, info, train, query, directory, identity, smoke):
    import numpy as np
    epochs = (4 if model == "fno_coregionalization" else 1) if smoke else 2500
    base = ROOT / "smoke" if smoke else ROOT
    ckpt = base / "checkpoints" / dataset / model
    ckpt.mkdir(parents=True, exist_ok=True)
    record = ckpt / "IDENTITY.json"
    identity = dict(identity, epochs=epochs)
    if record.exists() and json.loads(record.read_text()) != identity:
        raise ValueError("Checkpoint identity changed; refusing incompatible resume")
    write_json(record, identity)
    captured = {}
    load, resolve = paper_adapter(train, query, info, directory)
    with import_paper(model, identity) as (recipe, StageTrainer):
        recipe.load_mf_dataset, recipe.resolve_grid = load, resolve
        def capture(**kw):
            if captured or np.count_nonzero(kw["target"]):
                raise ValueError("Finalizer received real query fields or repeated predictions")
            captured.update(pred=np.asarray(kw["pred"], np.float32), work_grid=list(kw["work_grid"]),
                train_seconds=float(kw["train_seconds"]), eval_seconds=float(kw["eval_seconds"]),
                n_params=int(kw["n_params"]), fit=kw.get("extra", {}))
            return {"captured": True}
        recipe.finalize_and_write = capture
        if model in ("nomad_mf", "mf_fno_transfer"):
            trainer = StageTrainer(ckpt / "stages", identity)
            if model == "nomad_mf":
                recipe.train_loop = trainer
            else:
                recipe._train = trainer
        args = argparse.Namespace(dataset_dir=str(directory), dataset_name=dataset,
            seed=42, epochs=epochs, ckpt_dir=str(ckpt), out=str(ckpt / "unused.json"), decoder="nonlinear")
        if model in ("nomad_mf", "mf_fno_transfer"):
            recipe.run(args, Path(args.out))
        else:
            recipe.run(args)
    if not captured or captured["work_grid"] != list(info["work_grid"]):
        raise ValueError("Paper recipe did not produce the planned working grid")
    pred = captured.pop("pred")
    if model in ("nomad_mf", "mf_fno_transfer"):
        stages = [json.loads(path.read_text()) for path in (ckpt / "stages").glob("*.json")]
        if len(stages) != 2 or any(row["epoch"] != epochs for row in stages):
            raise ValueError("Incomplete transfer stage checkpoints")
        captured["train_seconds"] = sum(row["seconds"] for row in stages)
    captured.update(epochs=epochs, resume_supported=True,
                    architecture_and_hyperparameters="Frozen release recipe; optimizer/RNG checkpoint adaptations only")
    return pred, captured


def source_fingerprint():
    files = [Path(__file__).resolve()]
    for folder in (ROOT / "vendor" / "st_bench", ROOT / "vendor" / "paper",
                   ROOT / "vendor" / "baseline_runtime", ROOT / "common", ROOT / "data_adapters"):
        files.extend(sorted(folder.rglob("*.py")))
    entries = {str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else "baseline_worker.py": sha(path)
               for path in files}
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()


def export(dataset, model, pred, query, info, metadata, smoke=False):
    import numpy as np
    pred = np.asarray(pred, np.float32).reshape(len(query), -1)
    if pred.shape != (info["n_query"], int(np.prod(info["work_grid"]))) or not np.isfinite(pred).all():
        raise ValueError(f"Invalid output prediction: {pred.shape}")
    path, meta_path = output_paths(dataset, model, smoke)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    with temporary.open("wb") as stream:
        np.savez_compressed(stream, X=np.asarray(query, np.float32), pred=pred,
                            work_grid=np.asarray(info["work_grid"], np.int32))
    os.replace(temporary, path)
    metadata = dict(metadata, dataset=dataset, model=model, smoke=smoke,
        work_grid=list(info["work_grid"]), n_query=len(query), dtype="float32",
        scientific_result=not smoke, query_sha256=info.get("query_sha256"),
        prediction_sha256=sha(path), prediction_path=str(path.relative_to(ROOT)))
    write_json(meta_path, metadata)


def alias_evidence():
    folder = ROOT / "vendor" / "paper"
    first, second = folder / "mf_fno_transfer", folder / ALIAS
    if (first / "model.py").read_bytes() != (second / "model.py").read_bytes():
        raise ValueError("B9/B10 architectures differ")
    def normalized(path):
        tree = ast.parse(path.read_text())
        tree.body = [node for node in tree.body if not (isinstance(node, ast.Assign) and
            any(isinstance(target, ast.Name) and target.id == "REPO_ROOT" for target in node.targets))]
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == ALIAS:
                node.value = "mf_fno_transfer"
        return ast.dump(tree, include_attributes=False)
    if normalized(first / "smoke_eval.py") != normalized(second / "smoke_eval.py"):
        raise ValueError("B9/B10 executable recipes differ")
    return dict(alias_of="mf_fno_transfer", independent_training=False,
                alias_evidence="Architecture bytes and normalized executable recipe AST match",
                architecture_sha256=sha(first / "model.py"))


def export_alias(dataset, info, smoke=False):
    import numpy as np
    source, meta_path = output_paths(dataset, "mf_fno_transfer", smoke)
    metadata = json.loads(meta_path.read_text())
    if metadata["prediction_sha256"] != sha(source):
        raise ValueError("B9 source prediction changed")
    metadata.update(alias_evidence(), source_prediction_sha256=sha(source),
                    source_metadata_sha256=sha(meta_path), additional_training_seconds=0.)
    with np.load(source, allow_pickle=False) as archive:
        pred, query = archive["pred"], archive["X"]
    export(dataset, ALIAS, pred, query, info, metadata, smoke)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return parser.parse_args(argv)


def run(cli):
    import numpy as np
    import torch
    plan, info, directory = dataset_info(cli.dataset)
    base = ROOT / "smoke" if cli.smoke else ROOT
    claim_model = "mf_fno_transfer" if cli.model == ALIAS else cli.model
    claim = base / "claims" / cli.dataset / f"{claim_model}.lock"
    claim.parent.mkdir(parents=True, exist_ok=True)
    with claim.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if cli.model == ALIAS:
            export_alias(cli.dataset, info, cli.smoke)
            return
        if cli.dataset == "era5" and not cli.smoke:
            raise ValueError("ERA5 production outputs must be reused from the existing 55-row campaign")
        classical = cli.model in CLASSICAL
        device = torch.device("cpu" if classical else (
            "cuda" if torch.cuda.is_available() else "cpu") if cli.device == "auto" else cli.device)
        if not classical and not cli.smoke and device.type != "cuda":
            raise RuntimeError("Production neural baselines require a scheduled CUDA device")
        if device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but unavailable")
        if cli.model in PAPER and device.type == "cpu" and torch.cuda.is_available():
            raise ValueError("Paper recipes choose CUDA automatically; hide GPUs for CPU smoke runs")
        torch.set_num_threads(cli.threads)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        torch.set_float32_matmul_precision("highest")
        os.environ["DDE_BACKEND"] = "pytorch"
        os.environ.pop("SAVE_PRED_DIR", None)
        start = time.monotonic()
        with protected_numpy_load(staged_paths(info, directory)) as loaded:
            train, query, input_hashes = load_staged(info, directory)
            identity = dict(model=cli.model, dataset=cli.dataset, seed=42, smoke=cli.smoke,
                plan_sha256=sha(ROOT / "PLAN.json"), source_sha256=source_fingerprint(), input_sha256=input_hashes)
            path, meta_path = output_paths(cli.dataset, cli.model, cli.smoke)
            if path.exists() and meta_path.exists():
                previous = json.loads(meta_path.read_text())
                if previous.get("identity") == identity and previous.get("prediction_sha256") == sha(path):
                    print("VERIFIED COMPLETE", cli.dataset, cli.model, flush=True)
                    return
                raise ValueError("Existing output has a different scientific identity")
            print("TRAIN", cli.dataset, cli.model, "grid", info["work_grid"], "device", device, flush=True)
            if cli.model in PAPER:
                pred, extra = run_paper(cli.model, cli.dataset, info, train, query, directory, identity, cli.smoke)
            else:
                pred, extra = run_statistical(cli.model, cli.dataset, info, train, query, device, cli.smoke)
        elapsed = time.monotonic() - start
        extra = dict(extra, identity=identity, seed=42, elapsed_seconds=elapsed,
            train_seconds=extra.get("train_seconds", elapsed), device=str(device),
            device_name=torch.cuda.get_device_name() if device.type == "cuda" else "cpu",
            query_answers_read=False, calibration_answers_loaded=False, raw_test_answers_loaded=False,
            loaded_data_paths=sorted(set(loaded)), independent_training=True,
            inputs_at_inference=["theta"], n_base_hf_train=info["n_base_hf_train"],
            matmul_tf32=False, cudnn_tf32=False,
            cost=dict(wall_seconds=elapsed, train_seconds=extra.get("train_seconds", elapsed),
                      eval_seconds=extra.get("eval_seconds"), n_params=extra.get("n_params"),
                      peak_gpu_allocated_bytes=torch.cuda.max_memory_allocated() if device.type == "cuda" else None))
        export(cli.dataset, cli.model, pred, query, info, extra, cli.smoke)
        if cli.model == "mf_fno_transfer":
            export_alias(cli.dataset, info, cli.smoke)
        print("EXPORTED", cli.dataset, cli.model, f"{elapsed:.1f}s", flush=True)


def main(argv=None):
    args = parse_args(argv)
    if args.threads < 1:
        raise ValueError("--threads must be positive")
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[name] = str(args.threads)
    run(args)


if __name__ == "__main__":
    main()
