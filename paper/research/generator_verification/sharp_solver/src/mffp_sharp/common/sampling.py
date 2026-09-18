"""Condition-vector sampling.

Two things live here: a generic Latin-hypercube sampler over named ranges, and
the Schulz-Rinne canonical 2D Riemann configurations for Euler (so we sample
around genuinely-2D shock interactions instead of blindly over all 17 dims,
which mostly yields degenerate/1D configs).

Ranges here are PROVISIONAL (TBD) — the sample round validates that they produce
sharp solutions, keep the LF bottom rung under-resolved, and stay solver-stable.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import qmc


def latin_hypercube(ranges: dict[str, tuple[float, float]], n: int, seed: int) -> dict[str, np.ndarray]:
    """Latin-hypercube draw of `n` points over the named [lo, hi] ranges.

    Degenerate dims (lo == hi) are returned as the constant value; only the
    non-degenerate dims are passed to scipy's qmc.scale (which requires lo < hi).
    """
    names = list(ranges)
    lo = np.array([ranges[k][0] for k in names])
    hi = np.array([ranges[k][1] for k in names])
    active = lo < hi                               # mask of non-degenerate dims
    n_active = int(active.sum())
    result = np.empty((n, len(names)))
    # fill degenerate dims with the constant
    for j, (l, h, is_active) in enumerate(zip(lo, hi, active)):
        if not is_active:
            result[:, j] = l
    if n_active > 0:
        sampler = qmc.LatinHypercube(d=n_active, seed=seed)
        unit = sampler.random(n)                   # [n, n_active] in [0,1)
        active_idx = np.where(active)[0]
        scaled = qmc.scale(unit, lo[active], hi[active])
        for col_src, col_dst in enumerate(active_idx):
            result[:, col_dst] = scaled[:, col_src]
    return {k: result[:, i] for i, k in enumerate(names)}


# Schulz-Rinne 2D Riemann configurations: each is the four quadrant states
# (rho, u, v, p) for quadrants (top-right, top-left, bottom-left, bottom-right).
# A small representative subset of the classic 19; extend as needed (TBD).
# Source convention follows Schulz-Rinne (1993) / Kurganov-Tadmor (2002).
SCHULZ_RINNE = {
    "config_3": [  # four shocks
        (1.5,    0.0,    0.0,    1.5),
        (0.5323, 1.206,  0.0,    0.3),
        (0.138,  1.206,  1.206,  0.029),
        (0.5323, 0.0,    1.206,  0.3),
    ],
    "config_12": [  # two shocks, two contact discontinuities
        (0.5313, 0.0,    0.0,    0.4),
        (1.0,    0.7276, 0.0,    1.0),
        (0.8,    0.0,    0.0,    1.0),
        (1.0,    0.0,    0.7276, 1.0),
    ],
    "config_15": [  # mixed shock / rarefaction / contact
        (1.0,    0.1,   -0.3,    1.0),
        (0.5197, -0.6259, -0.3,  0.4),
        (0.8,    0.1,   -0.3,    0.4),
        (0.5313, 0.1,    0.4276, 0.4),
    ],
}


def sample_euler_configs(n: int, jitter_frac: float, seed: int) -> list[dict]:
    """Pick Schulz-Rinne base configs round-robin and jitter their quadrant states.

    Returns a list of `n` dicts, each with the 16 quadrant values + a `base` tag.
    Jitter is multiplicative +/- jitter_frac, applied independently per value.
    """
    rng = np.random.default_rng(seed)
    keys = list(SCHULZ_RINNE)
    out = []
    for i in range(n):
        base = keys[i % len(keys)]
        quads = SCHULZ_RINNE[base]
        jittered = []
        for (rho, u, v, p) in quads:
            f = lambda x: x * (1.0 + jitter_frac * (2 * rng.random() - 1))
            jittered.append((f(rho), f(u), f(v), f(p)))
        out.append({"base": base, "quadrants": jittered})
    return out
