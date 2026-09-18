"""Portable recipe-hash helper. Cherry-picked from
models/transolver_residual/smoke_eval.py (canonical in-tree pattern).
"""
from __future__ import annotations
import hashlib
import json
from typing import Any, Mapping


def recipe_hash(defaults: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(defaults), sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:12]
