# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/periodicity.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : 085541c7563705fc13edacbca1ca80cf92358c16c0a5671c1cb8da42f09c1453
# STATUS : byte-identical below this header.
#          Copied, never imported: score_panel.py::code_hash hashes only
#          family_dir/**/*.py, so logic outside the family dir is invisible to
#          the eval cache key.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector stays a FROZEN test-time sub-component behind a
#          condition->pseudo-LF front end. The B2 contribution is the ROUTE
#          SWITCH + budget accountant, not this code.
# ============================================================================
# == RE-VENDORED (round-3 card r3s2_field_reach-B1) ============================
# SOURCE : round2/worktrees/r2s2_stacked/B1/models_r2/r2s2_stack/periodicity.py
# COMMIT : 6b4e1d4825666e037a43675c83d9bda6289ec9d0  (recipe.env._vendor_source)
# SHA256 : 8f6796ffb909a0f9e511bd25843f8c516d9b02543f83a6c84c9e644939798257
# STATUS : byte-identical below this header (the round-2 header block and the
#          body are unchanged). Copied, never imported: score_panel.py::code_hash
#          hashes only family_dir/**/*.py.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector is a frozen test-time sub-component behind a NEW
#          condition->pseudo-LF front end. The reuse IS the experiment.
# ==============================================================================
# ══ VENDORED (round-2 card r2s2_stacked-B1) ═════════════════════════════
# SOURCE : round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router/periodicity.py
# COMMIT : b90d4662cd12820b6926730d39bdb5af70bba276  (recipe.base_commit)
# SHA256 : 5c3c88c3d4a0a1bb3265b9036741c098654186bec0079d7a57d8f21363be3c0d
# STATUS : byte-identical below this header. Round-1 branches are immutable
#          (program.md §5.13); the file is COPIED, never imported, because
#          `score_panel.py::code_hash` hashes only `family_dir/**/*.py` and
#          logic living outside the family dir is invisible to the cache key.
# ROLE   : declared frozen test-time sub-component (program.md §5.10a) behind a
#          new condition->pseudo-LF front end. The reuse IS the experiment.
# ══════════════════════════════════════════════════════════════════════════
"""The DATA-DRIVEN periodicity switch for card `s6_local-B2` (recipe knobs
`S6_PAD_MODE=circular_if_periodic`, `S6_PERIODIC_TEST=wrap_continuity_ratio_hf_train`,
`S6_PERIODIC_TOL=1.25`).

WHY a switch at all, and why it carries NO physics (ADR 0009). The base
prediction this family corrects is `eval/panel_data.py::copylf_prediction`, which
upsamples with `scipy.ndimage.zoom(..., order=1, grid_mode=True, mode="nearest")`
-- an extension that is **not** periodic. So copy-LF itself carries a wrap seam
(the brainstormer measured LF_up wrap ratios 3.89-4.18 against HF's 0.99-1.02),
and B1's zero-padded corrector was forbidden from looking across it while 45-81%
of its remaining squared error sat in a 12-cell boundary band (B1 F10). The eval
layer is immutable (program.md section 5.3), so the MODEL fixes the seam; it is
never "fixed" by touching `panel_data.py`.

But circular padding is only correct where the data actually wraps. Asserting
"these four datasets are periodic because they are spectral solves" would be a
physics assumption at test time. Instead we MEASURE it on the HF **train** split
only (never test, never the condition vector, no PDE operator, no residual):

    ratio_axis = RMS_over_samples_and_lines( f[0]  - f[-1] )        # the wrap jump
                 / RMS_over_samples_and_lines( f[1] - f[0]  )        # the first interior jump

and use `padding_mode="circular"` iff `max(ratio_y, ratio_x) <= S6_PERIODIC_TOL`.
A genuinely periodic field's wrap jump is statistically an ordinary interior
jump, so the ratio sits at 1; a Dirichlet/wall boundary makes it explode.

This is the brainstormer's probe (`brainstormer/s6_local/batch_2/iteration_1.md`
section 2.2), re-derived here and verified at build time to reproduce all 14 of
its pre-registered HF numbers to 4 decimals over `N_PROBE = 32` train samples:

    pfc 1.0152 / 0.9908   allen_cahn 0.9906 / 1.0210   fisher_kpp 0.9988 / 0.9871
    cahn_hilliard 0.9998 / 1.0003   helmholtz 0.3478 / 0.8585
    heat_local 10.6358 / 16.5482    fluid 2.5563 / 1.2146

=> circular on the five panel datasets that have LF at test, zeros on both
2-D guard datasets. `N_PROBE = 32` and the ratio definition are fixed by that
pre-registration, NOT chosen here.

DEGENERATE CASE, made explicit rather than silent: `sharp__sod_1d` has H == 1
(no y axis) and a constant left plateau, so its first interior jump along x is
exactly 0 and the ratio is undefined on both axes. Undefined => `zeros` (the
conservative branch, which is also B1's behaviour), recorded with
`decision_reason="degenerate_denominator"`.
"""
from __future__ import annotations

import numpy as np

N_PROBE = 32       # brainstormer probe protocol (iteration_1.md section 2.2); not a free choice
PAD_MODES = ("zeros", "circular_if_periodic")
RESOLVED_MODES = ("zeros", "circular")


def _rms(a) -> float:
    a = np.asarray(a, dtype=np.float64)
    return float(np.sqrt((a ** 2).mean())) if a.size else 0.0


def wrap_continuity_ratio(fields: np.ndarray, grid, axis: int):
    """`RMS(f[0] - f[-1]) / RMS(f[1] - f[0])` along `axis` (1 = y, 2 = x).

    Returns None when the axis has extent < 2 or the first interior jump is
    identically zero (the denominator would be degenerate).
    """
    H, W = int(grid[0]), int(grid[1])
    f = np.asarray(fields, dtype=np.float64).reshape(-1, H, W)
    g = np.moveaxis(f, axis, 1)
    if g.shape[1] < 2:
        return None
    den = _rms(g[:, 1, :] - g[:, 0, :])
    if den <= 0.0:
        return None
    return _rms(g[:, 0, :] - g[:, -1, :]) / den


def decide_padding(pad_mode_knob: str, hf_train_fields: np.ndarray, grid,
                   tol: float, n_probe: int = N_PROBE) -> dict:
    """Resolve `S6_PAD_MODE` into a concrete torch `padding_mode`.

    `hf_train_fields` must be the HF **train** split on the working grid. The
    decision is seed-independent and arm-independent by construction (it reads
    only the first `n_probe` train HF fields), so `circ_repair` and
    `trust_head_circ` cannot disagree about it.
    """
    if pad_mode_knob not in PAD_MODES:
        raise ValueError(f"S6_PAD_MODE={pad_mode_knob!r} not one of {PAD_MODES}")
    probe = np.asarray(hf_train_fields, dtype=np.float64)[:int(n_probe)]
    ry = wrap_continuity_ratio(probe, grid, axis=1)
    rx = wrap_continuity_ratio(probe, grid, axis=2)
    finite = [r for r in (ry, rx) if r is not None and np.isfinite(r)]
    worst = max(finite) if finite else None

    if pad_mode_knob == "zeros":
        resolved, reason = "zeros", "S6_PAD_MODE=zeros (no probe consulted)"
    elif worst is None:
        resolved, reason = "zeros", "degenerate_denominator"
    elif worst <= float(tol):
        resolved, reason = "circular", f"max_wrap_ratio {worst:.4f} <= tol {float(tol):.4f}"
    else:
        resolved, reason = "zeros", f"max_wrap_ratio {worst:.4f} > tol {float(tol):.4f}"

    if resolved not in RESOLVED_MODES:
        raise ValueError(f"internal: resolved padding {resolved!r}")
    return {
        "padding_decision": resolved,
        "padding_decision_reason": reason,
        "pad_mode_knob": pad_mode_knob,
        "periodic_tol": float(tol),
        "n_probe_samples": int(min(int(n_probe), probe.shape[0])),
        "wrap_ratio_hf": {"y": ry, "x": rx},
        "wrap_ratio_hf_max": worst,
        "test": "wrap_continuity_ratio_hf_train",
    }
