# Autoresearch preflight + stop-the-line

Three enforcement tools that turn round-2's post-hoc audit findings and round-3's red-team findings into pre-launch and in-flight gates.
All are standalone (numpy / stdlib only) and round-agnostic; every future round's harness is REQUIRED to wire them in as described below.

## Why these exist

Round 2 discovered four instrument/panel defects *during* the round, when the frozen panel could no longer respond:

1. Condition vectors incomplete on 3 of 6 datasets (pfc / fisher_kpp / allen_cahn — ADR r2-0003).
2. helmholtz trivially re-solvable from `x` (rel-L2 2.2e-13).
3. ifc_poisson's fidelity ladder unpaired (LF row i ≠ HF row i; `attribution.valid=false`).
4. pfc with no fidelity gap (LF ≈ HF; nothing for MF to add).

Every one of these is detectable from the data alone in under a minute.
In this harness, batch N+1 was the error-detector for batch N; these tools move detection to *before batch 1* and give any agent a way to stop the line the moment a defect is found.

Round 3's red-team (`defect_class_redteam/REDTEAM_REPORT.md`) then named a **fifth defect class — per-cell estimator integrity**: the panel cell is a mean of per-sample ratios, and nothing checked that this estimator is fed task-valid rows, is not outlier-dominated, is fed rungs on one physical amplitude scale, or still describes the current data bytes.
ADR r3-0003 D4 lands four instruments for it: three new `preflight.py` checks (`degenerate_rows`, `cell_stability`, `rung_scale_coherence`) plus the standalone `data_binding.py`.

## `preflight.py` — run before batch 1, and after any regeneration

```bash
python preflight.py --root <benchmark_root> --datasets <a> <b> ... --out preflight_report.json
python preflight.py --selftest     # instruments must detect every synthetic defect class (round-2 four + fifth-class)
```

Checks per dataset (factory npz layout): `completeness` (nearest-pair witness + the generator gate's `condition_completeness` meta record), `pairing` (per-row diagonal-cosine-above-p95-of-off-diagonal — robust to look-alike samples), `fidelity_gap` (NO_GAP / SATURATED warnings), `nn_baseline` (1-NN-in-condition-space floor; a weak triviality screen — the decisive triviality test is the generator gate's reconstruction certificate, which lives in `mffp_sharp.common.completeness`).

Fifth-class checks (ADR r3-0003 D4), all on the canonical per-row copy-LF construction (LF spectrally interpolated to the HF grid, per-row rel-L2, test split):

- `degenerate_rows` — rows with per-row gap below `max(1e-6, 1% of the median row gap)` are task-void (LF≈HF: nothing to predict; they deflate the copy-LF reference and inflate every skill).
  **HARD FAIL** `DEGENERATE_ROWS` at ≥ 5% void rows; `TASK_VOID_ROWS` warning below.
  Records count, fraction, threshold, and the first 10 void indices; this is the certification instrument for any test-split regeneration (e.g. the pfc r3-0002 swap).
- `cell_stability` — seeded 1000-resample bootstrap of the copy-LF reference cell: top-5 rows' share of the per-row ratio sum and the CI95 half-width relative to the point value.
  Share > 0.4 or relative half-width > 0.25 → `OUTLIER_DOMINATED` **warning** (never a hard fail — it prices the cell's discriminative power, not its validity).
  `min_detectable_delta` is always recorded: a claimed model delta on that cell below it is not claimable (ADR r3-0003 D2).
- `rung_scale_coherence` — per LF rung, `RMS(LF upsampled) / RMS(HF)` on test rows (train fallback) must lie in `[0.5, 2.0]`.
  Outside the band → **HARD FAIL** `RUNG_SCALE`, unless the dataset has a declared convention in `CONVENTION_ALLOWANCES` (currently `ifc_poisson`: the h² amplitude convention, round-2 report / ADR r3-0003 D3), in which case the measured ratios + the allowance string are recorded as a warning.

Exit 0 = launch may proceed. Exit 1 = hard fail (completeness, pairing, degenerate_rows, or rung_scale_coherence): set a HOLD, then repair or explicitly `--waive <dataset>:<check>` (waivers are recorded in the report and belong in the round's launch ADR).

**Demonstration** (`preflight_round2_panel_demo.json`, run 2026-08-03 against `benchmark_42/sharp` as round 2 shipped): flags pfc / fisher_kpp / allen_cahn INCOMPLETE, pfc NO_GAP + TRIVIAL_NN, helmholtz SATURATED, cahn_hilliard PASS — i.e., it catches the audit's data-side findings before a single batch is spent. (The ifc pairing class is covered by `--selftest`; ifc's data lives on the cluster.)

## `data_binding.py` — launch-time data↔artifact binding

```bash
python data_binding.py record --root <data_root> --datasets a b c --out manifest.json
python data_binding.py verify --manifest manifest.json      # exit 0 match / exit 3 mismatch
```

Closes the redteam L1/C05 hole: the score cache keys on `(code_hash | dataset | epochs | seed)` and the copy-LF baselines JSON carries no hash of the data bytes it was computed from, so after a dataset swap every cached cell and recorded reference remains silently valid-looking — the exact artifact-staleness pattern that let defect classes 1–4 survive.
The binding is a per-dataset sha256 over the sorted concatenation of the dataset's array files (`*.npz`/`*.npy`, recursive, symlinks followed), each prefixed by relative path + byte size; streamed, no array parsing, ~disk speed.
`verify` prints a per-dataset diff on mismatch (files added / removed / resized, or "content changed" when the file census is identical) and exits 3.

Wiring requirement:

- The round **launch script** runs `record` over the scored panel and archives the manifest at `round3/state/data_hashes.json` (future rounds: `<round>/state/data_hashes.json`), alongside the preflight report.
- **Every dispatch path** (batch launcher, cron/poll loops, anchor re-scores) runs `verify` against that manifest *before* leaning on cached cells or recorded references, and refuses to dispatch on exit 3 — a mismatch means the caches/baselines describe bytes that no longer exist; set a HOLD and re-baseline via the sanctioned mutation path, then `record` again.
- After any ADR-sanctioned regeneration (e.g. the pfc r3-0002 swap): re-run preflight, re-baseline, then re-`record` — in that order.

## `hold.py` — stop-the-line sentinel

```bash
python hold.py set   --state <round>/state --reason "what broke" --by <agent-or-person>
python hold.py check --state <round>/state    # exit 0 free / exit 3 held
python hold.py clear --state <round>/state --by eloise
```

Contract:

- Any agent that finds a defect on a mentor-owned surface (generator code, dataset arrays, scoring instruments) sets a HOLD **immediately** — before writing the finding up.
- Every batch-dispatch path (including cron/poll loops) runs `check` first and refuses to launch on exit 3, so a held round also stops its pollers.
- Only the operator clears a hold, choosing: repair + preflight re-run, waive with rationale, or close the round. Cleared holds are archived to `HOLD_history.jsonl`.

## Round-harness wiring requirement

A round launch script MUST:
1. run `preflight.py` over the panel and archive the report into the round's `state/`;
2. refuse to launch on exit 1 unless every hard fail carries a waiver recorded in the launch ADR;
3. run `data_binding.py record` over the panel into the round's `state/data_hashes.json`;
4. call `hold.py check` AND `data_binding.py verify` before *every* batch dispatch, refusing on exit 3 from either;
5. re-run preflight (and re-record the binding manifest) after any dataset regeneration mid-round (panel mutation is allowed only under an explicit ADR).
