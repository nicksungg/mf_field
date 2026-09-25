"""Array-based datasets, independent of the paper's dataset registry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


def real_array(value, name):
    array = np.asarray(value)
    if array.dtype.kind not in "fiu" or not np.isfinite(array).all():
        raise ValueError(f"{name} must contain finite real numeric values")
    return np.array(array, dtype=np.float64, order="C", copy=True)


def parameters(value, dimension=None, name="X", allow_empty=False):
    array = real_array(value, name)
    if array.ndim != 2 or array.shape[1] == 0 or (not allow_empty and len(array) == 0):
        raise ValueError(f"{name} must have shape (N, d), with nonempty parameter dimension")
    if dimension is not None and array.shape[1] != dimension:
        raise ValueError(f"{name} has {array.shape[1]} parameters, expected {dimension}")
    return array


def field_pair(value, name="data", dimension=None, field_shape=None):
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError(f"{name} must be an (X, Y) pair")
    x = parameters(value[0], dimension, name + ".X")
    y = real_array(value[1], name + ".Y")
    if y.ndim != 3 or len(y) != len(x) or min(y.shape[1:]) < 1:
        raise ValueError(f"{name}.Y must have shape (N, H, W), matching the rows of X. "
                         "For 1D fields use (N, 1, W). For flattened fields supply grid_shape in dataset.json.")
    if field_shape is not None and y.shape[1:] != tuple(field_shape):
        raise ValueError(f"{name}.Y has grid {y.shape[1:]}, expected {tuple(field_shape)}")
    return x, y


def row_keys(x):
    """Stable exact parameter identities, independent of array layout and signed zero."""
    canonical = np.array(x, dtype="<f8", order="C", copy=True)
    canonical[canonical == 0] = 0
    return [hashlib.sha256(row.tobytes()).hexdigest() for row in canonical]


class FieldDataset:
    """Training arrays at one or more coarse fidelities and one fine fidelity.

    ``low_fidelity`` is an (X, Y) pair or a list of pairs ordered from cheapest
    to finest. Rows need not be paired across fidelities. Y contains scalar
    fields with shape (N, H, W). Empty low_fidelity is allowed for M7 alone.
    Fitting/evaluation answers are not part of a separate test table here.
    """

    def __init__(self, *, low_fidelity, high_fidelity, name="custom"):
        self.high_fidelity = field_pair(high_fidelity, "high_fidelity")
        self.parameter_dimension = self.high_fidelity[0].shape[1]
        self.field_shape = self.high_fidelity[1].shape[1:]
        is_pair = False
        if isinstance(low_fidelity, (tuple, list)) and len(low_fidelity) == 2:
            try:
                candidate_x = np.asarray(low_fidelity[0])
                is_pair = candidate_x.ndim == 2 and candidate_x.dtype.kind in "fiu"
            except (TypeError, ValueError):
                pass  # Two fidelity pairs form a ragged array, unlike one X table.
        if is_pair:
            levels = [low_fidelity]
        elif isinstance(low_fidelity, (tuple, list)):
            levels = list(low_fidelity)
        else:
            raise ValueError("low_fidelity must be an (X, Y) pair or a list of pairs")
        self.low_fidelity = tuple(field_pair(level, f"low_fidelity[{i}]", self.parameter_dimension)
                                  for i, level in enumerate(levels))
        self.name = str(name)

    @classmethod
    def from_directory(cls, path):
        """Load dataset.json and NPZ files (keys x and y), without a dataset registry.

        Example manifest: {"low_fidelity": [{"path": "low.npz"}],
        "high_fidelity": {"path": "high.npz"}}. Each level may additionally
        supply grid_shape: [H, W] to reshape flattened fields.
        """
        root = Path(path)
        manifest = json.loads((root / "dataset.json").read_text())

        def read(entry):
            if isinstance(entry, str):
                entry = {"path": entry}
            if not isinstance(entry, dict) or "path" not in entry:
                raise ValueError("Each fidelity must specify a path to an NPZ file")
            source = root / entry["path"]
            with source.open("rb") as stream:
                is_pointer = stream.read(42).startswith(b"version https://git-lfs.github.com/spec/v1")
            if is_pointer:
                raise ValueError(f"{source} is a Git LFS pointer. Download the array file first.")
            with np.load(source, allow_pickle=False) as archive:
                x, y = archive["x"], archive["y"]
            if "grid_shape" in entry:
                shape = entry["grid_shape"]
                if (not isinstance(shape, list) or len(shape) != 2
                        or any(not isinstance(n, int) or isinstance(n, bool) or n < 1 for n in shape)):
                    raise ValueError("grid_shape must be two positive integers [H, W]")
                if y.shape[0] != len(x) or np.prod(y.shape[1:]) != np.prod(shape):
                    raise ValueError(f"grid_shape does not match the fields in {source}")
                y = y.reshape(len(x), *shape)
            return x, y

        low = manifest.get("low_fidelity", [])
        if isinstance(low, (str, dict)):
            low = [low]
        return cls(low_fidelity=[read(level) for level in low],
                   high_fidelity=read(manifest["high_fidelity"]), name=manifest.get("name", root.name))

    def describe(self):
        return {"name": self.name, "parameter_dimension": self.parameter_dimension,
                "low_fidelity": [{"rows": len(x), "grid": list(y.shape[1:])}
                                 for x, y in self.low_fidelity],
                "high_fidelity": {"rows": len(self.high_fidelity[0]), "grid": list(self.field_shape)}}
