"""Train the two ERA5 correctors from predicted coarse fields only.

The frozen backbones and loss match uqcorr/corr_ens.py. ERA5 adaptations are a
predeclared parameter-group split, train-only normalization of predicted inputs,
and a fixed array coordinate convention on the common 128 by 256 working grid.
Reserved fine answers are never opened, including for validation or reporting.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import signal
import sys
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint

from era5_common import ROOT, load_training, save_npz, sha, verify_source, write_json


def guard_reserved_answers():
    """Block Python file opens of answer stores for this training process."""
    forbidden = {"answers", "reserved_answers", "readonly_answers"}

    def audit(event, args):
        if event != "open" or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).expanduser().resolve()
        if forbidden.intersection(path.parts):
            raise PermissionError(f"Corrector training cannot open reserved answers: {path}")

    sys.addaudithook(audit)


def load_backbones():
    """Resolve FiLMNorm explicitly without editing the frozen original module."""
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise ImportError(path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    film = load("era5_corrector_film_source", ROOT / "vendor/mf_fno_transfer_film/model.py")
    previous = sys.modules.get("model")
    old_path = sys.path[:]
    try:
        sys.modules["model"] = film
        bb = load("era5_corrector_backbones", ROOT / "uqcorr/corr_backbones.py")
    finally:
        sys.path[:] = old_path
        if previous is None:
            sys.modules.pop("model", None)
        else:
            sys.modules["model"] = previous
    if bb.FiLMNorm is not film.FiLMNorm:
        raise RuntimeError("The corrector imported an unexpected FiLMNorm")
    return bb


def row_keys(x):
    x = np.ascontiguousarray(x, dtype=np.float32).copy()
    x[x == 0] = 0
    return [row.tobytes() for row in x]


def validate_split(x, x_query, split):
    tr = np.asarray(split["train_rows"], dtype=np.int64)
    va = np.asarray(split["val_rows"], dtype=np.int64)
    if tr.ndim != 1 or va.ndim != 1 or not len(tr) or not len(va):
        raise ValueError("Corrector training and validation need nonempty row lists")
    if sorted(np.concatenate((tr, va)).tolist()) != list(range(len(x))):
        raise ValueError("Corrector split must partition every HF training row exactly once")
    keys = row_keys(x)
    if set(keys[i] for i in tr) & set(keys[i] for i in va):
        raise ValueError("A parameter group crosses corrector training and validation")
    if set(keys) & set(row_keys(x_query)):
        raise ValueError("Reserved query inputs occur in the HF training table")
    return tr, va


def load_coarse(data, grid, smoke):
    coarse_root = (ROOT / "smoke" if smoke else ROOT) / "coarse"
    path = coarse_root / "oof.npz"
    if path.exists():
        audit_path = coarse_root / "oof_audit.json"
        audit = json.loads(audit_path.read_text())
        expected_identity = {
            "experiment_sha256": sha(ROOT / "EXPERIMENT.json"),
            "coarse_plan_sha256": sha(ROOT / "COARSE_PLAN.json"),
            "training_sha256": sha(ROOT / "data/training.npz"),
            "source_manifest_sha256": sha(ROOT / "SOURCE.json"), "smoke": bool(smoke),
        }
        if (audit.get("passed") is not True or audit.get("identity") != expected_identity
                or audit.get("oof_sha256") != sha(path)
                or audit.get("query_targets_read") is not False
                or audit.get("hf_targets_read") is not False):
            raise ValueError("The coarse ensemble lacks an assembly audit matching this run's mode")
        with np.load(path, allow_pickle=False) as z:
            arrays = {k: z[k] for k in (
                "mean_train", "mean_query", "n_members_train", "members_query", "x_hf", "x_query"
            )}
        if not np.array_equal(arrays["x_hf"], data["x_hf"]):
            raise ValueError("Coarse training predictions have different input identities or order")
        if not np.array_equal(arrays["x_query"], data["x_query"]):
            raise ValueError("Coarse query predictions have different input identities or order")
        counts = np.asarray(arrays["n_members_train"])
        if counts.shape != (55,) or not np.all(counts == 4):
            raise ValueError("Each training prediction must use exactly four coarse members")
        if np.asarray(arrays["members_query"]).size != 1 or int(arrays["members_query"].item()) != 4:
            raise ValueError("Each query prediction must use exactly four coarse members")
        coarse_train = np.asarray(arrays["mean_train"], dtype=np.float32)
        coarse_query = np.asarray(arrays["mean_query"], dtype=np.float32)
        identity = {"coarse_sha256": sha(path), "coarse_audit_sha256": sha(audit_path),
                    "coarse_file": str(path.relative_to(ROOT)),
                    "coarse_audit_file": str(audit_path.relative_to(ROOT)),
                    "synthetic_coarse_stub": False,
                    "oof_members_train": 4, "oof_members_query": 4}
    elif smoke:
        coarse_train = np.zeros((55, *grid), dtype=np.float32)
        coarse_query = np.zeros((17, *grid), dtype=np.float32)
        identity = {"coarse_sha256": None, "coarse_audit_sha256": None,
                    "coarse_file": None, "coarse_audit_file": None,
                    "synthetic_coarse_stub": True,
                    "oof_members_train": 0, "oof_members_query": 0}
    else:
        raise FileNotFoundError(f"Scientific training requires assembled coarse predictions: {path}")
    for arr, shape in ((coarse_train, (55, *grid)), (coarse_query, (17, *grid))):
        if arr.shape != shape or not np.isfinite(arr).all():
            raise ValueError(f"Invalid coarse prediction field, expected {shape}, received {arr.shape}")
    return coarse_train, coarse_query, identity


def prepare_inputs(data, coarse_train, coarse_query, tr, synthetic_stub=False):
    """Fit every normalization constant on corrector training rows only."""
    scale = float(np.sqrt(np.mean(np.square(coarse_train[tr], dtype=np.float64))))
    if not math.isfinite(scale) or scale <= 1e-12:
        if not synthetic_stub:
            raise ValueError("Predicted coarse fields have zero or invalid training RMS")
        scale = 1.0  # Explicitly artificial and confined to the nonscientific smoke test.
    target = np.asarray(data["y_hf"], dtype=np.float32)
    start = torch.from_numpy(np.ascontiguousarray(coarse_train)) / scale
    y = torch.from_numpy(np.ascontiguousarray(target)) / scale
    if synthetic_stub:
        rho = 1.0
    else:
        # Same unregularized least-squares gain and float32 arithmetic as the old recipe.
        rho = float((start[tr] * y[tr]).sum() / start[tr].square().sum().clamp_min(1e-20))
    if not math.isfinite(rho):
        raise ValueError("Invalid predicted-coarse least-squares gain")
    x = np.asarray(data["x_hf"], dtype=np.float32)
    xmean = x[tr].mean(0)
    xstd = np.maximum(x[tr].std(0), 1e-6)
    tx = lambda a: torch.from_numpy(np.ascontiguousarray(a, dtype=np.float32))
    arrays = {
        "x": tx((x - xmean) / xstd), "y": y, "h": rho * start,
        "x_query": tx((data["x_query"] - xmean) / xstd),
        "h_query": rho * tx(coarse_query) / scale,
    }
    if not all(torch.isfinite(value).all() for value in arrays.values()):
        raise ValueError("Nonfinite normalized training or query inputs")
    normalization = {"scale": scale, "rho": rho, "xmean": xmean.tolist(), "xstd": xstd.tolist(),
                     "normalization_rows": tr.tolist(), "scale_source": "predicted_coarse_train_only",
                     "rho_source": "predicted_coarse_and_fine_train_only",
                     "synthetic_normalization": bool(synthetic_stub)}
    return arrays, normalization


def relative_l2(pred, target):
    return (pred - target).flatten(1).norm(dim=1) / target.flatten(1).norm(dim=1).clamp_min(1e-8)


def radial(grid, device):
    hh, ww = grid
    ky = torch.fft.fftfreq(hh, device=device)[:, None] * hh
    kx = torch.fft.fftfreq(ww, device=device)[None, :] * ww
    radius = torch.sqrt(ky.square() + kx.square())
    return radius / radius.max()


@torch.no_grad()
def refine(model, x, initial, alpha, steps, batch):
    model.eval()
    output = []
    for offset in range(0, len(x), batch):
        c, h = x[offset:offset + batch], initial[offset:offset + batch]
        for _ in range(steps):
            h = h + alpha * model(c, h, None)
        output.append(h)
    return torch.cat(output)


def cpu_state(model):
    return {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}


def atomic_torch_save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".tmp.{os.getpid()}")
    with temp.open("wb") as file:
        torch.save(value, file)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temp, path)


def rng_state(rng):
    return {"generator": rng.bit_generator.state, "numpy": np.random.get_state(),
            "python": random.getstate(), "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}


def restore_rng(state, rng):
    rng.bit_generator.state = state["generator"]
    np.random.set_state(state["numpy"])
    random.setstate(state["python"])
    torch.set_rng_state(state["torch"].cpu())
    if state["cuda"] and torch.cuda.is_available():
        if len(state["cuda"]) != torch.cuda.device_count():
            raise RuntimeError("CUDA device count changed since checkpoint creation")
        torch.cuda.set_rng_state_all([value.cpu() for value in state["cuda"]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backbone", required=True, choices=("transolver", "convnext"))
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    guard_reserved_answers()
    verify_source()
    plan = json.loads((ROOT / "EXPERIMENT.json").read_text())
    source_hash = sha(ROOT / "SOURCE.json")
    experiment_hash = sha(ROOT / "EXPERIMENT.json")
    training_hash = sha(ROOT / "data/training.npz")
    if training_hash != plan["training_sha256"]:
        raise ValueError("Training data differ from the frozen experiment plan")
    data = load_training(keys=("x_hf", "y_hf", "x_query"))
    grid = tuple(int(value) for value in plan["grid"])
    if grid != (128, 256) or data["y_hf"].shape != (55, *grid):
        raise ValueError("This campaign requires 55 fine training fields on the 128 by 256 grid")
    if data["x_hf"].shape != (55, 12) or data["x_query"].shape != (17, 12):
        raise ValueError("This campaign requires 55 HF and 17 reserved inputs with 12 parameters")
    tr, va = validate_split(data["x_hf"], data["x_query"], plan["corrector_split"])
    coarse_train, coarse_query, coarse_identity = load_coarse(data, grid, args.smoke)
    tensors, normalization = prepare_inputs(data, coarse_train, coarse_query, tr,
                                           coarse_identity["synthetic_coarse_stub"])
    seed = int(plan["base_seed"])
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.set_float32_matmul_precision("highest")
    device = torch.device(args.device)
    bb = load_backbones()
    coords = bb.coordinates(grid, "periodic_node", device)
    model = bb.build(args.backbone, 12, coords, 0, width=32, base=48).to(device)
    tensors = {key: value.to(device) for key, value in tensors.items()}
    steps = 1 if args.smoke else int(plan["corrector_steps"])
    k_steps = int(plan["corrector_K"])
    alpha = float(plan["alpha"])
    if int(plan["corrector_steps"]) != 6000 or k_steps != 6 or alpha != 0.2:
        raise ValueError("Unexpected departure from the frozen 6000-step, K=6, alpha=0.2 recipe")
    batch = 2 if args.backbone == "transolver" else 4
    lr = 3e-4
    settings = {"steps": steps, "K": k_steps, "alpha": alpha, "batch": batch,
                "width": 32, "base": 48, "lr": lr, "weight_decay": 1e-5,
                "spectral_weight": 1.0, "fixedpoint_weight": 0.01, "grad_clip": 1.0,
                "eval_every": 250, "checkpoint_every": 500, "gradient_checkpointing": True,
                "registration": "periodic_node", "prolongation": "identity",
                "cuda_matmul_allow_tf32": False, "cudnn_allow_tf32": False,
                "float32_matmul_precision": "highest", "cudnn_deterministic": True,
                "cudnn_benchmark": False}
    model_name = f"uqcorr_{args.backbone}_pred"
    tag = f"{model_name}__era5"
    out = ROOT / "smoke" if args.smoke else ROOT
    ckdir = out / "checkpoints" / tag
    last = ckdir / "last.pt"
    key = {"model": model_name, "dataset": "era5", "smoke": args.smoke,
           "source_manifest_sha256": source_hash, "experiment_sha256": experiment_hash,
           "training_sha256": training_hash, "base_seed": seed, "grid": list(grid),
           "corrector_split": plan["corrector_split"], "normalization": normalization,
           "settings": settings, **coarse_identity}
    if (ROOT / "PLAN.json").exists():
        key["plan_sha256"] = sha(ROOT / "PLAN.json")
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=settings["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps, eta_min=lr / 100)
    rng = np.random.default_rng(seed + 1500)
    initial_val = float(relative_l2(tensors["h"][va], tensors["y"][va]).mean())
    best, best_step, best_state = initial_val, 0, cpu_state(model)
    log, recent, start_step, spent = [], [], 0, 0.0
    if last.exists():
        state = torch.load(last, map_location="cpu", weights_only=False)
        if state["key"] != key:
            raise RuntimeError("Checkpoint identity differs from source, data, normalization, or plan")
        model.load_state_dict(state["model"])
        opt.load_state_dict(state["optimizer"])
        sched.load_state_dict(state["scheduler"])
        best, best_step, best_state = state["best"], state["best_step"], state["best_state"]
        log, recent = state["log"], state["recent"]
        start_step, spent = int(state["step"]), float(state["seconds"])
        if not 0 <= start_step <= steps:
            raise ValueError("Checkpoint step is outside the planned run")
        restore_rng(state["rng_state"], rng)
        del state
        print(f"RESUME {tag} step {start_step}/{steps}", flush=True)
    radius = radial(grid, device)
    call = lambda c, h: checkpoint(model, c, h, None, use_reentrant=False)
    stopping = []
    def request_stop(signum, frame):
        stopping.append(signum)
    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGUSR1):
        signal.signal(signum, request_stop)
    clock = time.monotonic()
    def save_last(step):
        atomic_torch_save(last, {"key": key, "model": model.state_dict(),
            "optimizer": opt.state_dict(), "scheduler": sched.state_dict(),
            "best": best, "best_step": best_step, "best_state": best_state,
            "log": log, "recent": recent, "step": step,
            "seconds": spent + time.monotonic() - clock, "rng_state": rng_state(rng)})
        write_json(ckdir / "progress.json", {"model": model_name, "smoke": args.smoke,
            "step": step, "steps": steps, "selected_step": best_step,
            "best_val_rel_l2": best, "seconds": spent + time.monotonic() - clock,
            "source_manifest_sha256": source_hash, "experiment_sha256": experiment_hash})
    print(f"START {tag}: train={len(tr)} val={len(va)} query=17 grid={grid} "
          f"batch={batch} scale={normalization['scale']:.6g} rho={normalization['rho']:.6g} "
          f"smoke={args.smoke} synthetic_coarse_stub={coarse_identity['synthetic_coarse_stub']}", flush=True)
    for step in range(start_step + 1, steps + 1):
        model.train()
        indices = torch.as_tensor(rng.choice(tr, batch, replace=len(tr) < batch), device=device)
        h, y, c = tensors["h"][indices], tensors["y"][indices], tensors["x"][indices]
        target_spectrum = torch.fft.fft2(y, norm="ortho").abs()
        loss = y.new_zeros(())
        for k in range(k_steps):
            h = h + alpha * call(c, h)
            weight = 1 + radius.pow(1 + k / max(1, k_steps - 1))
            weight = weight / weight.mean()
            spectral = ((torch.fft.fft2(h, norm="ortho").abs() - target_spectrum).square() * weight).mean()
            loss = loss + (F.mse_loss(h, y) + spectral) / k_steps
        loss = loss + settings["fixedpoint_weight"] * call(c, y).square().mean()
        if not torch.isfinite(loss):
            raise RuntimeError(f"Nonfinite corrector loss at step {step}")
        opt.zero_grad(set_to_none=True)
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), settings["grad_clip"], error_if_nonfinite=True)
        opt.step()
        sched.step()
        recent.append(float(loss.detach()))
        if step % settings["eval_every"] == 0 or step == steps:
            prediction = refine(model, tensors["x"][va], tensors["h"][va], alpha, k_steps, batch)
            val = float(relative_l2(prediction, tensors["y"][va]).mean())
            if not math.isfinite(val):
                raise RuntimeError(f"Nonfinite validation error at step {step}")
            if val < best:
                best, best_step, best_state = val, step, cpu_state(model)
            log.append({"step": step, "train_loss": float(np.mean(recent)), "val_rel_l2": val,
                        "seconds": spent + time.monotonic() - clock})
            recent.clear()
            print(f"{tag} {step}/{steps} loss={log[-1]['train_loss']:.6g} "
                  f"val={val:.6g} best={best:.6g}@{best_step}", flush=True)
        if step % settings["checkpoint_every"] == 0 or step == steps or stopping:
            save_last(step)
        if stopping and step < steps:
            print(f"STOP {tag} after atomic checkpoint at step {step}", flush=True)
            raise SystemExit(75)
    train_seconds = spent + time.monotonic() - clock
    model.load_state_dict(best_state)
    # There is deliberately no query target or evaluation metric in this program.
    pred = refine(model, tensors["x_query"], tensors["h_query"], alpha, k_steps, batch)
    pred = (pred * normalization["scale"]).cpu().numpy().reshape(17, -1).astype(np.float32)
    if pred.shape != (17, 32768) or not np.isfinite(pred).all():
        raise RuntimeError("Invalid final query predictions")
    verify_source()
    if sha(ROOT / "SOURCE.json") != source_hash or sha(ROOT / "data/training.npz") != training_hash:
        raise RuntimeError("Source or training data changed during corrector training")
    if not coarse_identity["synthetic_coarse_stub"] and sha(ROOT / coarse_identity["coarse_file"]) != coarse_identity["coarse_sha256"]:
        raise RuntimeError("Coarse predictions changed during corrector training")
    if not coarse_identity["synthetic_coarse_stub"] and sha(ROOT / coarse_identity["coarse_audit_file"]) != coarse_identity["coarse_audit_sha256"]:
        raise RuntimeError("Coarse assembly audit changed during corrector training")
    atomic_torch_save(ckdir / "best.pt", {"key": key, "model": best_state,
        "selected_step": best_step, "best_val_rel_l2": best, "normalization": normalization})
    predfile = out / "predictions" / f"{tag}.npz"
    save_npz(predfile, pred=pred, theta=np.asarray(data["x_query"], dtype=np.float32),
             work_grid=np.asarray(grid, dtype=np.int64))
    metadata = {**key, "prediction_sha256": sha(predfile), "prediction_file": str(predfile.relative_to(ROOT)),
        "trained_no_reservedanswers": True, "scientific_result": not args.smoke,
        "reserved_answer_guard": True, "actual_lf_fields_used_by_corrector": False,
        "selected_step": best_step, "best_val_rel_l2": best, "initial_val_rel_l2": initial_val,
        "steps": steps, "K": k_steps, "alpha": alpha, "n_train": len(tr), "n_val": len(va),
        "n_query": 17, "n_params": sum(p.numel() for p in model.parameters()),
        "train_seconds": train_seconds, "device": str(device),
        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "cuda_matmul_allow_tf32": torch.backends.cuda.matmul.allow_tf32,
        "cudnn_allow_tf32": torch.backends.cudnn.allow_tf32,
        "float32_matmul_precision": torch.get_float32_matmul_precision(),
        "torch_version": torch.__version__, "numpy_version": np.__version__,
        "training_log": log}
    write_json(out / "metadata" / f"{tag}.json", metadata)
    print(f"DONE {tag} selected_step={best_step} val={best:.6g} "
          f"scientific_result={not args.smoke} prediction={predfile}", flush=True)


if __name__ == "__main__":
    main()
