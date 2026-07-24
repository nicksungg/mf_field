# Box Sample Generation + Auto-Screen + Survivor Menu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Checkbox steps.

**Goal:** Build the sharpness **auto-screen** (the pre-filter that ranks candidates before Nicholas sees them) and wire it into the sample pipeline, so that — once the sample batch is generated **on the box** — each candidate gets a one-line PASS/FAIL + sharpness ranking and Nicholas receives a ranked menu of one-pagers.

**Architecture:** A pure-numpy `common/screen.py` implements the spec's **energy-above-cutoff** metric (the form-agnostic high-k content measure), the **sharpness coordinate** `s` against the KS/Euler anchors, the **LF–HF high-k gap**, and the **dimension-matched KS floor**. A report builder consumes the saved sample HDF5s + computes the screen, emitting `screen_report.json`. The screen code and its tests run **locally** on synthetic/saved fields; the **generation run itself is box-only and Nicholas-gated** (see below).

**⚠️ WORKFLOW GATE — READ THIS:** Per `TO-DO.md`/`CLAUDE.md`: generate a small SAMPLE batch → **Nicholas approves** → only then full counts; **do NOT generate full datasets before Nicholas signs off.** This plan builds the *machinery*. Task 3 (the actual box generation run + handing Nicholas the menu) is a **box + mentor-gated** step that is NOT executed by an agent — it is run on the box and reviewed by Nicholas. Tasks 1–2 (the screen + its wiring) are light and run locally.

## Global Constraints

- **Screen metric is energy-above-cutoff** `f(k_c) = Σ_{|k|>k_c}|û|² / Σ_{|k|>0}|û|²` (DC excluded), form-agnostic (works for power-laws, knees, exponentials, spectral peaks). **Slope is descriptor-only, never the gate.**
- **Floor (the only binary):** drop a candidate only if `f_cand(k_c) < f_smooth-control(k_c)`, dimension-matched (1D vs 1D-KS, 2D vs 2D-KS). Otherwise **rank** by `s` + LF–HF gap; never hard-drop on a hand-picked `f` threshold.
- **k_c is the model's to set:** report the whole `f(k_c)` curve over `k_c ∈ {12,16,20,24}` until FNO's `k_max` is known; then it collapses to one point. (Same open blocker as the CH study.)
- Pure numpy; Python 3.9; `from __future__ import annotations`; no new deps.
- Git: branch `feat/sharpness-screen`; commit per task; trailer `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Prefix python cmds with `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate &&`.

**Depends on:** Plans 1–7 (the solvers + dimension-agnostic `common/` + `io.read_dataset`).

---

## File Structure
| File | Action |
|---|---|
| `common/screen.py` | Create — energy-above-cutoff, sharpness coordinate, LF–HF gap, floor, report builder |
| `tests/test_screen.py` | Create — synthetic-field validation of the metrics |
| `scripts/screen_samples.py` | Create — post-process saved sample HDF5s → `screen_report.json` (box/CLI) |
| `scripts/run_sample.sh` | Modify (optional) — call the screen after generation |

---

## Task 1: `common/screen.py` — sharpness metrics

**Files:** Create `common/screen.py`, `tests/test_screen.py`.

**Interfaces:**
- `radial_power(field) -> (kr_int, power)` — integer-binned radial power spectrum (1D or 2D), DC at index 0.
- `energy_above_cutoff(field, k_c) -> float` — `f(k_c)` (DC excluded).
- `cumulative_curve(field, k_cs) -> dict[int, float]` — `f` over several cutoffs.
- `sharpness_coordinate(f_cand, f_ks, f_euler) -> float` — `s=(f_cand-f_ks)/(f_euler-f_ks)` (clamped to ≥0; returns nan if anchors coincide).
- `lf_hf_gap(lf_up, hf, k_c) -> float` — `energy_above_cutoff(hf - lf_up, k_c)` (both on the HF grid).
- `passes_floor(f_cand, f_ks_dimmatched) -> bool` — `f_cand >= f_ks`.

- [ ] **Step 1: Write tests** — `tests/test_screen.py`:

```python
import numpy as np

from mffp_sharp.common import screen


def _mode_2d(n, kx, ky):
    x = np.arange(n) / n
    return np.sin(2 * np.pi * kx * x)[:, None] * np.sin(2 * np.pi * ky * x)[None, :]


def test_energy_above_cutoff_monotone_decreasing():
    f = _mode_2d(64, 10, 10) + 0.5 * _mode_2d(64, 2, 2)
    vals = [screen.energy_above_cutoff(f, kc) for kc in [0, 4, 8, 16]]
    assert all(vals[i] >= vals[i + 1] - 1e-12 for i in range(len(vals) - 1))


def test_f_at_zero_is_one():
    f = _mode_2d(64, 5, 5)
    assert abs(screen.energy_above_cutoff(f, 0) - 1.0) < 1e-9   # all non-DC energy is >0


def test_high_mode_sharper_than_low_mode():
    lo = _mode_2d(64, 2, 2)
    hi = _mode_2d(64, 20, 20)
    kc = 8
    assert screen.energy_above_cutoff(hi, kc) > screen.energy_above_cutoff(lo, kc)


def test_dc_excluded():
    f = 5.0 + _mode_2d(64, 6, 6)            # large DC offset must not change f(k_c)
    g = _mode_2d(64, 6, 6)
    assert abs(screen.energy_above_cutoff(f, 4) - screen.energy_above_cutoff(g, 4)) < 1e-9


def test_sharpness_coordinate_endpoints():
    assert abs(screen.sharpness_coordinate(0.2, 0.2, 0.8) - 0.0) < 1e-12
    assert abs(screen.sharpness_coordinate(0.8, 0.2, 0.8) - 1.0) < 1e-12
    assert np.isnan(screen.sharpness_coordinate(0.5, 0.3, 0.3))   # coincident anchors


def test_floor_and_1d():
    ks = np.sin(2 * np.pi * 3 * np.arange(128) / 128)            # smooth-ish 1D control
    cand = np.sin(2 * np.pi * 30 * np.arange(128) / 128)         # sharp 1D candidate
    kc = 8
    assert screen.passes_floor(screen.energy_above_cutoff(cand, kc),
                               screen.energy_above_cutoff(ks, kc))
    assert screen.energy_above_cutoff(cand, kc) > screen.energy_above_cutoff(ks, kc)


def test_lf_hf_gap_nonnegative():
    hf = _mode_2d(64, 12, 12)
    lf_up = _mode_2d(64, 3, 3)                                   # blurry LF (low modes only)
    assert screen.lf_hf_gap(lf_up, hf, 8) >= 0.0
```

- [ ] **Step 2: Run → fail (module missing).**

- [ ] **Step 3: Create `common/screen.py`:**

```python
"""Sharpness auto-screen: energy-above-cutoff + sharpness coordinate + LF-HF gap.

The single metric is energy-above-cutoff
    f(k_c) = sum_{|k|>k_c} |u_hat|^2 / sum_{|k|>0} |u_hat|^2      (DC excluded),
the complementary cumulative radial spectrum. Form-agnostic (power-law, knee,
exponential, or spectral-peak spectra all handled). Spectral SLOPE is a descriptor
only -- never the gate. Works for 1D and 2D fields.

Gating: the only binary is the dimension-matched KS FLOOR (drop a candidate smoother
than the smooth control). Otherwise candidates are RANKED by the sharpness coordinate
    s = (f_cand - f_ks) / (f_euler - f_ks)
and by the LF-HF high-k gap (the quantity MF fusion rides on). No hand-picked f cut.
"""
from __future__ import annotations

import numpy as np


def radial_power(field: np.ndarray):
    """Integer-binned radial power spectrum. Returns (kr_int, power) with DC at index 0."""
    field = np.asarray(field)
    F = np.fft.fftn(field)
    psd = np.abs(F) ** 2
    n = field.shape[0]
    freqs = [np.fft.fftfreq(n) * n for _ in range(field.ndim)]
    grids = np.meshgrid(*freqs, indexing="ij")
    kr = np.sqrt(sum(g ** 2 for g in grids))
    kr_int = np.rint(kr).astype(int).ravel()
    power = np.bincount(kr_int, weights=psd.ravel())
    return np.arange(len(power)), power


def energy_above_cutoff(field: np.ndarray, k_c: float) -> float:
    """f(k_c) = energy at radial wavenumber > k_c, normalized by total non-DC energy."""
    kr, power = radial_power(field)
    nondc = power.copy()
    nondc[0] = 0.0
    total = nondc.sum()
    if total <= 0.0:
        return 0.0
    above = nondc[kr > k_c].sum()
    return float(above / total)


def cumulative_curve(field: np.ndarray, k_cs) -> dict:
    """f(k_c) over several cutoffs (the curve reported until FNO k_max is known)."""
    return {int(kc): energy_above_cutoff(field, kc) for kc in k_cs}


def sharpness_coordinate(f_cand: float, f_ks: float, f_euler: float) -> float:
    """s = (f_cand - f_ks)/(f_euler - f_ks); clamp to >= 0; nan if anchors coincide."""
    denom = f_euler - f_ks
    if abs(denom) < 1e-30:
        return float("nan")
    return float(max(0.0, (f_cand - f_ks) / denom))


def lf_hf_gap(lf_up: np.ndarray, hf: np.ndarray, k_c: float) -> float:
    """High-k content of the residual (hf - lf_up), both on the HF grid."""
    return energy_above_cutoff(np.asarray(hf) - np.asarray(lf_up), k_c)


def passes_floor(f_cand: float, f_ks_dimmatched: float) -> bool:
    """Floor: a candidate must be at least as sharp as the dimension-matched KS control."""
    return f_cand >= f_ks_dimmatched
```

- [ ] **Step 4: Run tests + full suite.** `... python -m pytest tests/test_screen.py -q` (all pass) then `... python -m pytest tests/ -q`.

- [ ] **Step 5: Commit** (`feat(screen): energy-above-cutoff sharpness metrics + coordinate + LF-HF gap`).

---

## Task 2: `scripts/screen_samples.py` — report builder

**Files:** Create `scripts/screen_samples.py`; modify `scripts/run_sample.sh` (optional hook).

**Interfaces:** a CLI that reads every `*_sample.h5` in a sample dir via `io.read_dataset`, computes per-candidate `f(k_c)` curves (mean over the HF fields), the dimension-matched KS floor, the sharpness coordinate `s` vs the KS / Euler anchors, the mean LF–HF gap, and the bottom-rung rel-L2, then writes `screen_report.json` and prints a one-line PASS/FAIL + `s` per candidate. Pure post-processing — runs anywhere the saved HDF5s are (the box).

- [ ] **Step 1: Write `tests/test_screen_report.py`** — build two tiny in-memory datasets (a smooth one and a sharp one) via the existing solvers at low res, write with `io.write_dataset`, then call `screen_samples.build_report(dir)` and assert: the report has one entry per file, the sharp candidate's `s` > the smooth one's, and floor PASS/FAIL is set. (Uses `kuramoto_sivashinsky` as the smooth anchor and, e.g., `allen_cahn` as a sharper candidate — both pure-numpy, local.)

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Create `scripts/screen_samples.py`** with:
```python
"""Post-process saved sample HDF5s into a sharpness screen_report.json (+ printed summary).

Run where the sample data lives (the box):
    python scripts/screen_samples.py --sample-dir data/sample --k-cs 12 16 20 24
"""
from __future__ import annotations
import argparse, glob, json, os
import numpy as np
from mffp_sharp.common import io, screen

def _hf_fields(d):
    hf = d["hf_res"]
    return [b["aligned"][hf] for b in d["bundles"]], hf

def _mean_curve(fields, k_cs):
    curves = [screen.cumulative_curve(f, k_cs) for f in fields]
    return {kc: float(np.mean([c[kc] for c in curves])) for kc in [int(x) for x in k_cs]}

def build_report(sample_dir, k_cs=(12, 16, 20, 24)):
    paths = sorted(glob.glob(os.path.join(sample_dir, "*_sample.h5")))
    data = {os.path.basename(p).replace("_sample.h5", ""): io.read_dataset(p) for p in paths}
    # dimension-matched KS anchors + Euler anchor
    curves, ndims = {}, {}
    for name, d in data.items():
        fields, _ = _hf_fields(d)
        curves[name] = _mean_curve(fields, k_cs)
        ndims[name] = d["ndim"]
    ks_anchor = {nd: next((curves[n] for n in curves
                           if "kuramoto" in n and ndims[n] == nd), None)
                 for nd in set(ndims.values())}
    euler_curve = next((curves[n] for n in curves if "euler" in n), None)
    report = {}
    for name, d in data.items():
        fields, hf = _hf_fields(d)
        ksc = ks_anchor.get(ndims[name])
        row = {"ndim": ndims[name], "f_curve": curves[name]}
        for kc in [int(x) for x in k_cs]:
            f_cand = curves[name][kc]
            f_ks = ksc[kc] if ksc else None
            f_eu = euler_curve[kc] if euler_curve else None
            row.setdefault("floor_pass", {})[kc] = (
                None if f_ks is None else bool(f_cand >= f_ks))
            row.setdefault("s", {})[kc] = (
                None if (f_ks is None or f_eu is None)
                else screen.sharpness_coordinate(f_cand, f_ks, f_eu))
        # mean LF-HF gap at the smallest cutoff (coarsest LF vs HF)
        res = d["resolutions"]; res_min = min(res)
        gaps = [screen.lf_hf_gap(b["aligned"][res_min], b["aligned"][hf], int(k_cs[0]))
                for b in d["bundles"]]
        row["lf_hf_gap"] = float(np.mean(gaps))
        report[name] = row
    return report

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-dir", required=True)
    ap.add_argument("--k-cs", type=int, nargs="+", default=[12, 16, 20, 24])
    args = ap.parse_args()
    report = build_report(args.sample_dir, args.k_cs)
    out = os.path.join(args.sample_dir, "screen_report.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"wrote {out}\n")
    for name, row in report.items():
        kc0 = args.k_cs[1] if len(args.k_cs) > 1 else args.k_cs[0]
        fp = row["floor_pass"].get(kc0)
        s = row["s"].get(kc0)
        tag = "PASS" if fp else ("FAIL-floor" if fp is False else "??")
        print(f"  {name:28} floor@{kc0}={tag:11} "
              f"s={'n/a' if s is None else round(s,3)}  lf_hf_gap={row['lf_hf_gap']:.3g}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the report test + full suite.**

- [ ] **Step 5: Commit + push.**

---

## Task 3: Box generation + survivor menu — ⚠️ BOX + NICHOLAS-GATED (not agent-executed)

This task is **run on the box, then reviewed by Nicholas** — it is NOT executed by an agent (compute policy + the approval gate). Recorded here as the operating procedure:

1. On the box: `git pull && cd SURF_2026/mffp_sharp && bash scripts/setup_env.sh` (once; clawpack/gfortran for the PyClaw solvers).
2. Generate the **sample** batch (small counts, `configs/sample.yaml`): `python -m mffp_sharp.generate --config configs/sample.yaml --pde all`. (PyClaw + 2D 128² solves are heavy → box only.)
3. `python scripts/screen_samples.py --sample-dir data/sample` → `screen_report.json` + printed PASS/FAIL + `s`.
4. Auto-drop floor-failures (and bottom-rung / repro failures); keep their one-pagers for the record.
5. Bring back only the small artifacts (`sample_summary.json`, `screen_report.json`, `data/sample/figures/*.png`) for review.
6. **Hand Nicholas the ranked survivor menu** — one-pagers + mechanism tags + `s` + `f(k_c)` curve + LF–HF gap. He picks which go to full counts.
7. **Only after Nicholas signs off** → regenerate at full counts. **Do not generate full datasets before then.**

---

## Self-Review

**Spec coverage:** the Sharpness-screen section of the design — energy-above-cutoff (Task 1), the `f(k_c)` sweep over `{12,16,20,24}`, the dimension-matched KS floor, the sharpness coordinate `s`, the LF–HF gap (Tasks 1–2), and the survivor-menu hand-off (Task 3, gated). ✓

**What runs where:** Tasks 1–2 (the screen + report builder) are pure-numpy and **run locally** with synthetic/saved data. Task 3 (the actual sample generation + menu) is **box + Nicholas-gated** and is procedure, not agent-executed — this is the project's hard workflow gate.

**Open dependency (unchanged):** FNO `k_max` is unknown, so the screen reports the whole `f(k_c)` curve rather than collapsing to one cutoff; Nicholas's `k_max` selects the operative point. The stronger "smooth-suite envelope" baseline (vs the KS floor) is gated on locating the deck's smooth datasets on the box.

**Follow-on:** once Nicholas picks survivors, full-count generation + the downstream model comparison (which lives in the separate MFFP codebase) — out of scope for this dataset-building project.
