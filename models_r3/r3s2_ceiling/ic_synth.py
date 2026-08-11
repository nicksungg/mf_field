# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/ic_synth.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : 44620cbf9a48add5263737f49c42beaad6302d58eb8fde078d3c4bd94172381f
# STATUS : byte-identical below this header.
#          Copied, never imported: score_panel.py::code_hash hashes only
#          family_dir/**/*.py, so logic outside the family dir is invisible to
#          the eval cache key.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector stays a FROZEN test-time sub-component behind a
#          condition->pseudo-LF front end. The B2 contribution is the ROUTE
#          SWITCH + budget accountant, not this code.
# ============================================================================
"""Exact, ZERO-PARAMETER analytic synthesis of the band-limited initial condition
from the condition vector (round-3 card `r3s2_field_reach-B1`, front end **E1**).

WHY THIS EXISTS
---------------
Round 2's terminal conditional was: *"if the missing variable really is the
realised random initial condition (ADR r2-0003), then no architecture, capacity
or budget can move this panel further."* Round 3's repaired panel EXPORTS that
variable — the IC is built deterministically from a handful of low Fourier-mode
coefficients and those coefficients ship in the condition vector as
`ic_c0..ic_c{n-1}`. This module turns them back into the IC FIELD analytically,
with no learned parameters and no PDE solve, so the emulator receives the actual
realised initial state as an input channel rather than 16-48 opaque scalars.

PROVENANCE (read-only surfaces; NEVER imported, NEVER edited)
-------------------------------------------------------------
The math below is re-implemented from the generator, with the source lines
quoted in comments:

  `mf_field_eloise_data/SURF_2026-main/mffp_sharp/src/mffp_sharp/common/
   ic_encoding.py::ic_2d`
      m   = int(round(np.sqrt(len(coeffs) / 2.0 + 1.0)))
      xs  = 2 * np.pi * np.arange(res) / res ;  X, Y = meshgrid(xs, xs, "ij")
      modes = [(a, b) for a in range(m) for b in range(m) if not (a == 0 and b == 0)]
      f  += coeffs[i] * cos(kx X + ky Y) + coeffs[i+1] * sin(kx X + ky Y)
      return f / (max|f| + 1e-12) * scale

  `.../common/spectral.py::spectral_interp`
      exact band-limited (zero-pad) interpolation of a periodic field to n_fine

  and the solver call sites (e.g. `pdes/allen_cahn.py:74-78`,
  `pdes/cahn_hilliard.py:95-99`, `pdes/fisher_kpp.py:83-86`,
  `pdes/phase_field_crystal.py:72-77`), all of which do

      res_min  = min(resolutions)
      ic_coarse = <offset> + build_ic(coeffs, res_min, <scale>, 2)
      per rung: _solve(spectral_interp(ic_coarse, res), ...)

THE TWO THINGS THAT MAKE THIS *EXACT*
-------------------------------------
1. The normalising constant is `max|f|` computed on the **res_min** grid, not on
   the rung's grid — because the generator normalises the coarse field and THEN
   zero-pads it (knob `R3S2_IC_SYNTH_NORM=res_min_maxabs`). Normalising on the
   fine grid would be a different (slightly larger) constant.
2. The trig sum is band-limited to |k| <= m-1 <= 4 while res_min >= 32, so
   evaluating the sum analytically on the rung's node grid and zero-padding the
   res_min field to that grid are the SAME field. `equivalence_check` asserts it
   at <= 1e-12 in-job (knob `R3S2_IC_EQUIV_CHECK=1`); measured deviation at build
   time was 1.2e-15 - 3.6e-15 over the panel's (n_coeff, res_min, res) triples.

The generator's per-dataset amplitude (`0.1` for allen_cahn/cahn_hilliard, `0.5`
for fisher_kpp, `spec["ic_amplitude"]` for pfc) and the additive mean offset
(`mean_composition` / `mean_density` / `0.5`) are NOT reproduced: `scale` is 1.0
(knob `R3S2_IC_SYNTH_SCALE`) and the offset is dropped. Both are a known global
constant / affine shift on an INPUT channel of a network whose first layer is a
1x1 conv, so they are absorbable and their omission is recorded rather than
guessed at (the offset is in any case already in the condition vector, and it
reaches the emulator through FiLM).
"""
from __future__ import annotations

import numpy as np

IC_PREFIX = "ic_c"
EQUIV_TOL = 1e-12


class ICSynthError(RuntimeError):
    """A seam in the IC-synthesis path violated its contract."""


# ── condition-vector layout ──────────────────────────────────────────────


def resolve_ic_indices(param_names, cond_dim: int) -> dict:
    """Which columns of the condition vector are the IC coefficients?

    `R3S2_IC_NAMES_FROM=meta_param_names_ic_prefix`: the dataset's OWN
    `meta.json::param_names` is the authority; a positional guess is never made.
    Returns a record (never raises on "no IC dims" — that is the recorded
    `film_only_recorded` fallback, card part 3).
    """
    if not param_names:
        return {"applicable": False, "reason": "dataset meta.json has no param_names",
                "ic_indices": [], "other_indices": list(range(cond_dim)),
                "n_ic_coeffs": 0, "param_names": None}
    names = [str(s) for s in param_names]
    if len(names) != int(cond_dim):
        return {"applicable": False,
                "reason": (f"param_names has {len(names)} entries but the loaded "
                           f"condition vector has {cond_dim} columns"),
                "ic_indices": [], "other_indices": list(range(cond_dim)),
                "n_ic_coeffs": 0, "param_names": names}
    ic = [i for i, s in enumerate(names) if s.startswith(IC_PREFIX)]
    other = [i for i in range(cond_dim) if i not in set(ic)]
    if not ic:
        return {"applicable": False,
                "reason": f"no {IC_PREFIX}* columns in param_names",
                "ic_indices": [], "other_indices": other,
                "n_ic_coeffs": 0, "param_names": names}
    # export order must be ic_c0, ic_c1, ... contiguous and ascending, else the
    # (kx, ky) pairing below would be silently permuted.
    want = [f"{IC_PREFIX}{j}" for j in range(len(ic))]
    got = [names[i] for i in ic]
    if got != want:
        raise ICSynthError(
            f"IC columns are not the contiguous ascending export order: {got} != {want}")
    if ic != list(range(ic[0], ic[0] + len(ic))):
        raise ICSynthError(f"IC columns are not contiguous in the condition vector: {ic}")
    n = len(ic)
    m = int(round(np.sqrt(n / 2.0 + 1.0)))
    if 2 * (m * m - 1) != n:
        raise ICSynthError(
            f"{n} ic_c* columns is not 2*(m^2-1) for any integer m (got m={m}); the "
            "generator's 2-D encoding cannot be inverted")
    return {"applicable": True, "reason": None, "ic_indices": ic,
            "other_indices": other, "n_ic_coeffs": n, "mode_square_m": m,
            "param_names": names}


# ── the synthesis itself ─────────────────────────────────────────────────


def modes_of(m: int):
    """`[(a, b) for a in range(m) for b in range(m) if not (a == 0 and b == 0)]`
    — verbatim ordering from `ic_encoding.ic_2d`."""
    return [(a, b) for a in range(m) for b in range(m) if not (a == 0 and b == 0)]


def trig_sum(coeffs: np.ndarray, res: int) -> np.ndarray:
    """UNNORMALISED `sum_j c_2j cos(kx X + ky Y) + c_{2j+1} sin(kx X + ky Y)`.

    Batched over rows: `coeffs` (N, n) -> (N, res, res). Node grid
    `xs = 2*pi*arange(res)/res`, `meshgrid(..., indexing="ij")` — the generator's.
    """
    c = np.asarray(coeffs, dtype=np.float64)
    if c.ndim == 1:
        c = c[None, :]
    n = c.shape[1]
    m = int(round(np.sqrt(n / 2.0 + 1.0)))
    if 2 * (m * m - 1) != n:
        raise ICSynthError(f"{n} coefficients is not 2*(m^2-1); m={m}")
    xs = 2 * np.pi * np.arange(int(res)) / float(res)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    out = np.zeros((c.shape[0], int(res), int(res)), dtype=np.float64)
    for j, (kx, ky) in enumerate(modes_of(m)):
        phase = kx * X + ky * Y
        out += c[:, 2 * j, None, None] * np.cos(phase)[None, :, :]
        out += c[:, 2 * j + 1, None, None] * np.sin(phase)[None, :, :]
    return out


def ic_fields(coeffs: np.ndarray, res: int, res_min: int, scale: float = 1.0) -> np.ndarray:
    """The synthesised IC channel on the `res` node grid, generator-faithful.

    Normalisation constant is `max|f| + 1e-12` evaluated on the **res_min** grid
    (`R3S2_IC_SYNTH_NORM=res_min_maxabs`), matching the generator's
    build-at-res_min-then-zero-pad order. Returns (N, res, res).
    """
    coarse = trig_sum(coeffs, int(res_min))
    norm = np.abs(coarse).reshape(coarse.shape[0], -1).max(axis=1) + 1e-12
    fine = trig_sum(coeffs, int(res)) if int(res) != int(res_min) else coarse
    return fine / norm[:, None, None] * float(scale)


# ── the in-job exactness certificate ─────────────────────────────────────


def _spectral_interp_2d(field: np.ndarray, n_fine: int) -> np.ndarray:
    """Re-implementation of `common/spectral.py::spectral_interp` (2-D branch),
    used ONLY as the independent reference in `equivalence_check`."""
    n_c = int(field.shape[0])
    if int(n_fine) == n_c:
        return field.astype(np.float64).copy()
    if (int(n_fine) - n_c) % 2 != 0:
        raise ICSynthError(f"spectral_interp needs (n_fine - n) even; {n_fine} vs {n_c}")
    F = np.fft.fftshift(np.fft.fft2(field))
    pad = (int(n_fine) - n_c) // 2
    Fp = np.zeros((int(n_fine), int(n_fine)), dtype=complex)
    Fp[pad:pad + n_c, pad:pad + n_c] = F
    return np.real(np.fft.ifft2(np.fft.ifftshift(Fp)) * (int(n_fine) / n_c) ** 2)


def equivalence_check(coeffs: np.ndarray, res: int, res_min: int, scale: float = 1.0,
                      n_probe: int = 4, tol: float = EQUIV_TOL) -> dict:
    """Assert analytic-on-the-rung-grid == build-at-res_min-then-zero-pad.

    This is the certificate that the front end is EXACT rather than merely
    plausible: if it ever fails, the synthesised channel is not the field the
    solver actually integrated and the card's claim is void. Raises on failure
    (`R3S2_IC_EQUIV_CHECK=1`); tolerance 1e-12 from card part 3.
    """
    c = np.asarray(coeffs, dtype=np.float64)
    rows = list(range(min(int(n_probe), c.shape[0])))
    analytic = ic_fields(c[rows], res, res_min, scale)
    dev = 0.0
    for i, r in enumerate(rows):
        coarse = trig_sum(c[r], res_min)[0]
        coarse = coarse / (np.abs(coarse).max() + 1e-12) * float(scale)
        ref = _spectral_interp_2d(coarse, res)
        dev = max(dev, float(np.abs(analytic[i] - ref).max()))
    if not np.isfinite(dev) or dev > float(tol):
        raise ICSynthError(
            f"IC synthesis is NOT the generator's field: analytic evaluation on the "
            f"{res}x{res} node grid deviates from spectral_interp(build_ic(coeffs, "
            f"{res_min}), {res}) by max|delta| = {dev!r} > {tol}")
    return {"max_abs_dev": dev, "tol": float(tol), "n_probe_rows": len(rows),
            "res": int(res), "res_min": int(res_min), "pass": True,
            "reference": ("common/spectral.py::spectral_interp of "
                          "common/ic_encoding.py::ic_2d built at res_min")}


# ── the zero-information null (E1n) ──────────────────────────────────────


def shuffle_rows(coeffs: np.ndarray, seed: int) -> tuple:
    """Row-shuffle the IC coefficient block: sample i is handed sample perm[i]'s IC.

    The ZERO-INFORMATION NULL for the channel (card `_arms`, `E1n_emul_only`).
    The permutation is derandomised by `seed` and is a DERANGEMENT where one
    exists, so no row keeps its own coefficients (a fixed point would leak real
    information into the null). Returns (shuffled, perm).
    """
    n = int(np.asarray(coeffs).shape[0])
    rng = np.random.default_rng(int(seed))
    if n < 2:
        return np.asarray(coeffs).copy(), np.arange(n)
    perm = rng.permutation(n)
    for _ in range(64):
        if not np.any(perm == np.arange(n)):
            break
        perm = rng.permutation(n)
    else:  # pragma: no cover - astronomically unlikely for n >= 2
        perm = np.roll(np.arange(n), 1)
    return np.asarray(coeffs)[perm], perm
