#!/usr/bin/env python3
"""Fit released statistical/pointwise baselines without opening query answers.

Production hyperparameters are the released run_st.py defaults. The only data
protocol change is using the frozen ERA5 split, with six internal validation
rows for neural arms. --smoke is explicitly separated from production outputs.
The released neural routines do not serialize optimizer state and cannot resume.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace


CLASSICAL = ("st_koh_pod", "st_nargp_pod", "st_lf_affine_pod", "st_knn")
NEURAL = ("st_mfdnn", "st_mfdeeponet", "st_dmfal")
MODELS = CLASSICAL + NEURAL
ROOT = Path(__file__).resolve().parent


def training_arguments(model: str, smoke: bool = False) -> SimpleNamespace:
    """Preserve the release recipe; no arbitrary production budget CLI exists."""
    if model not in MODELS:
        raise ValueError(f"Unsupported model: {model}")
    args = SimpleNamespace(
        arm=model, dataset="core/era5", seed=42, pod_modes=64,
        pod_energy=0.999, gp_restarts=2, nargp_samples=32,
        nargp_lf_modes=16, steps=100000, batch=16, points=512,
        hidden=[128, 128, 128, 128], latent=32 if model == "st_dmfal" else 128,
        sensors=256, lr=1e-3, wd=1e-4, eval_every=500,
    )
    if model in CLASSICAL:
        args.latent = 32  # Same classical runner convention, unused by these arms.
    if smoke:
        args.steps, args.eval_every = 2, 1
        args.batch, args.points = 2, 32
        args.gp_restarts, args.nargp_samples = 1, 2
    return args


def import_released():
    vendor = ROOT / "vendor" / "st_bench"
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(vendor))
    common = importlib.import_module("st_common")
    common.FACTORY_DATA = ROOT / "flat_data"
    # load_unpaired prepends these import roots. Keep both within this campaign.
    common.FAMILY = vendor
    return common, importlib.import_module("st_classical"), importlib.import_module("st_neural")


def discard_query_targets(data: dict) -> None:
    """Fail closed if staged answers are present, then eliminate scoring access."""
    import torch

    target = data.pop("Ytest")
    if not bool(torch.isfinite(target).all()) or bool(torch.count_nonzero(target)):
        raise ValueError("Staged query fields must contain only zero placeholders")
    if data.get("Ytest_lf_up") is not None:
        raise ValueError("Query low fidelity answers must not be supplied")
    data.pop("Ytest_lf_up", None)


def smoke_classical_data(data: dict) -> dict:
    """Limit CPU smoke cost, retaining original field grid and all query inputs."""
    import numpy as np

    result = dict(data)
    for prefix, maximum in (("hf", 12), ("lf", 16)):
        rows = np.asarray(data[f"{prefix}_tr"][:maximum])
        result[f"X_{prefix}"] = data[f"X_{prefix}"][rows]
        result[f"Y_{prefix}"] = data[f"Y_{prefix}"][rows]
        if prefix == "lf":
            result["Y_lf_up"] = data["Y_lf_up"][rows]
        result[f"{prefix}_tr"] = np.arange(len(rows))
        result[f"{prefix}_va"] = np.empty(0, dtype=np.int64)
    return result


@contextlib.contextmanager
def smoke_gp_iterations(common, classical, enabled: bool):
    """Patch both imported aliases only inside an explicitly marked smoke run."""
    original_common, original_classical = common.fit_gp, classical.fit_gp
    if enabled:
        def short_fit(*args, **kwargs):
            kwargs["maxiter"] = 2
            return original_common(*args, **kwargs)
        common.fit_gp = short_fit
        classical.fit_gp = short_fit
    try:
        yield
    finally:
        common.fit_gp = original_common
        classical.fit_gp = original_classical


def fit_arm(data: dict, args, device, smoke: bool = False):
    common, classical, neural = import_released()
    with smoke_gp_iterations(common, classical, smoke):
        if args.arm in CLASSICAL:
            working = smoke_classical_data(data) if smoke else data
            if args.arm == "st_knn":
                pred, extra = classical.ARMS[args.arm](working, args)
            else:
                cache = classical._lf_emulator(working, args)
                pred, extra = classical.ARMS[args.arm](working, args, cache)
            n_params = 0
        else:
            working = data
            pred, extra, _, n_params = neural.ARMS[args.arm](working, args, device)
    if "plugin_test_rel_l2" in extra:
        raise RuntimeError("Forbidden NARGP query metric was computed")
    extra["actual_fit_rows"] = {
        "hf_train": int(len(working["hf_tr"])),
        "hf_validation": int(len(working["hf_va"])),
        "lf_train": int(len(working["lf_tr"])),
        "lf_validation": int(len(working["lf_va"])),
    }
    return pred, extra, n_params


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=MODELS, required=True)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--threads", type=int, default=8)
    return parser.parse_args(argv)


def run_worker(cli):
    import numpy as np
    import torch
    from baseline_common import (
        completed, export_prediction, load_plan, protected_numpy_load,
        verify_inputs, verify_source,
    )

    torch.set_num_threads(cli.threads)
    verify_source()
    input_audit = verify_inputs()
    if completed(cli.model, smoke=cli.smoke):
        print(f"{cli.model}: verified output already complete; skipping", flush=True)
        return
    plan = load_plan()["datasets"]["era5"]
    args = training_arguments(cli.model, cli.smoke)
    classical = cli.model in CLASSICAL
    if classical:
        device = torch.device("cpu")
    elif cli.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(cli.device)
    if not classical and device.type != "cuda" and not cli.smoke:
        raise RuntimeError("Production neural training requires a scheduled CUDA device")
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    started = time.monotonic()
    with protected_numpy_load() as loaded_paths:
        query_path = ROOT / "data" / "core" / "era5" / "test_l9.npz"
        with np.load(query_path, allow_pickle=False) as query:
            theta = np.asarray(query["x"], dtype=np.float32).copy()
        common, _, _ = import_released()
        data = common.load_unpaired(
            "core/era5", args.seed, val_frac=0.0 if classical else 0.1,
            device=device, min_val=0 if classical else 6, cap=256,
        )
        if tuple(data["grid"]) != tuple(plan["work_grid"]):
            raise ValueError(f"Working grid mismatch: {data['grid']}")
        if len(data["X_hf"]) != 55 or len(theta) != 17 or len(data["Xtest"]) != 17:
            raise ValueError("Expected 55 base training rows and 17 query rows")
        if data["paired"] or data["n_levels"] != 9:
            raise ValueError("Expected the unpaired nine level ERA5 loader")
        expected_split = (55, 0) if classical else (49, 6)
        if (len(data["hf_tr"]), len(data["hf_va"])) != expected_split:
            raise ValueError("Unexpected internal fine training/validation split")
        discard_query_targets(data)
        print(
            f"{cli.model}: grid={data['grid']} HF={expected_split} "
            f"LF={len(data['lf_tr'])}+{len(data['lf_va'])} device={device} smoke={cli.smoke}",
            flush=True,
        )
        pred, extra, n_params = fit_arm(data, args, device, smoke=cli.smoke)
        pred = pred.detach().cpu().numpy().astype(np.float32) * float(data["scale"])
        if pred.shape != (17, *plan["work_grid"]) or not np.isfinite(pred).all():
            raise ValueError(f"Invalid prediction array: {pred.shape}")
    metadata = {
        "worker": "worker_st.py", "seed": args.seed,
        "train_seconds": time.monotonic() - started, "n_params": n_params,
        "device": str(device), "training_arguments": vars(args),
        "input_audit": input_audit,
        "numpy_paths_read": [str(path) for path in loaded_paths],
        "query_answers_read": False, "query_targets_removed_before_fit": True,
        "inputs_at_inference": ["theta"], "loader_manifest": data["manifest"],
        "normalization_scale": float(data["scale"]),
        "hf_fit_rows": data["hf_tr"].tolist(), "hf_validation_rows": data["hf_va"].tolist(),
        "resume_supported": False,
        "resume_note": "Released arm routines do not serialize optimizer state. Restart refits the arm.",
        "adaptations": [
            "Frozen reserved inputs excluded from every fidelity by preparation",
            "Six fine validation rows for neural checkpoint selection",
            "NARGP query-error diagnostic removed without changing predictions",
        ],
        "fit": extra,
    }
    export_prediction(cli.model, pred, theta, data["grid"], metadata, smoke=cli.smoke)
    print(f"{cli.model}: exported predictions in {metadata['train_seconds']:.1f}s", flush=True)


def main(argv=None):
    cli = parse_args(argv)
    if cli.threads < 1:
        raise ValueError("--threads must be positive")
    # Set BLAS limits before baseline_common imports NumPy.
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[name] = str(cli.threads)
    from baseline_common import task_claim
    with task_claim(cli.model, smoke=cli.smoke):
        run_worker(cli)


if __name__ == "__main__":
    main()
