"""HDF5 dataset writer, matching the deck's MF-dataset layout.

One file per PDE dataset. Layout:

    /fields/res_<R>        float32 [N, R, R]   native-grid field per fidelity R
    /fields_hf/res_<R>     float32 [N, H, H]   same field interpolated up to HF grid
    /condition             float32 [N, D]      condition vector per sample
    /fidelity_index        int32   [n_levels]  the resolutions, ascending
    /standardization       group: mean,std per HF field over the TRAIN split
    attrs: pde, hf_res, output_time, n_samples, condition_names, seed

Standardization stats are computed on the TRAIN split only (stored as attrs/
datasets) so they can be applied consistently and never leak test info.
"""
from __future__ import annotations

import numpy as np


def write_dataset(
    path: str,
    pde: str,
    samples: list[dict],
    condition: np.ndarray,
    condition_names: list[str],
    resolutions: list[int],
    hf_res: int,
    output_time: float,
    seed: int,
    train_frac: float = 0.8,
) -> None:
    """Write one PDE dataset to `path` (HDF5).

    `samples[i]` is the dict from ladder.assemble_sample: has "raw" and "aligned"
    (both {res: field}). `condition[i]` is that sample's condition vector.
    """
    import h5py

    n = len(samples)
    assert condition.shape[0] == n, "condition rows must match sample count"
    n_train = int(round(train_frac * n))

    with h5py.File(path, "w") as f:
        f.attrs["pde"] = pde
        f.attrs["hf_res"] = hf_res
        f.attrs["output_time"] = output_time
        f.attrs["n_samples"] = n
        f.attrs["n_train"] = n_train
        f.attrs["seed"] = seed
        f.attrs["condition_names"] = [s.encode() for s in condition_names]
        hf0 = np.asarray(samples[0]["aligned"][hf_res])
        f.attrs["ndim"] = int(hf0.ndim)
        f.attrs["spatial_shape"] = list(hf0.shape)

        f.create_dataset("fidelity_index", data=np.asarray(resolutions, dtype=np.int32))
        f.create_dataset("condition", data=condition.astype(np.float32))

        graw = f.create_group("fields")
        galn = f.create_group("fields_hf")
        for res in resolutions:
            raw = np.stack([s["raw"][res] for s in samples]).astype(np.float32)
            aln = np.stack([s["aligned"][res] for s in samples]).astype(np.float32)
            graw.create_dataset(f"res_{res}", data=raw, compression="gzip")
            galn.create_dataset(f"res_{res}", data=aln, compression="gzip")

        # Standardization on the HF field over the TRAIN split only.
        hf_train = np.stack([s["aligned"][hf_res] for s in samples[:n_train]])
        gstd = f.create_group("standardization")
        gstd.create_dataset("mean", data=np.float32(hf_train.mean()))
        gstd.create_dataset("std", data=np.float32(hf_train.std() + 1e-12))


def read_dataset(path: str) -> dict:
    """Load a dataset written by write_dataset back into memory.

    Returns {resolutions, hf_res, condition_names, bundles} where each bundle is the
    same {"raw", "aligned", "hf_res"} shape ladder.assemble_sample produces — so
    figures can be re-rendered from saved data without re-solving.
    """
    import h5py

    with h5py.File(path, "r") as f:
        resolutions = [int(r) for r in f["fidelity_index"][:]]
        hf_res = int(f.attrs["hf_res"])
        ndim = int(f.attrs.get("ndim", 2))
        spatial_shape = list(f.attrs.get("spatial_shape", [hf_res, hf_res]))
        names = [s.decode() if isinstance(s, bytes) else str(s)
                 for s in f.attrs.get("condition_names", [])]
        n = int(f.attrs["n_samples"])
        condition = f["condition"][:] if "condition" in f else None
        graw, galn = f["fields"], f["fields_hf"]
        bundles = []
        for i in range(n):
            raw = {r: graw[f"res_{r}"][i] for r in resolutions}
            aligned = {r: galn[f"res_{r}"][i] for r in resolutions}
            bundles.append({"raw": raw, "aligned": aligned, "hf_res": hf_res})
    return {"resolutions": resolutions, "hf_res": hf_res, "condition_names": names,
            "condition": condition, "bundles": bundles,
            "ndim": ndim, "spatial_shape": spatial_shape}
