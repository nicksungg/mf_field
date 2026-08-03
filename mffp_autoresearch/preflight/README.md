# Autoresearch preflight + stop-the-line

Two enforcement tools that turn round-2's post-hoc audit findings into pre-launch and in-flight gates.
Both are standalone (numpy only) and round-agnostic; every future round's harness is REQUIRED to wire them in as described below.

## Why these exist

Round 2 discovered four instrument/panel defects *during* the round, when the frozen panel could no longer respond:

1. Condition vectors incomplete on 3 of 6 datasets (pfc / fisher_kpp / allen_cahn — ADR r2-0003).
2. helmholtz trivially re-solvable from `x` (rel-L2 2.2e-13).
3. ifc_poisson's fidelity ladder unpaired (LF row i ≠ HF row i; `attribution.valid=false`).
4. pfc with no fidelity gap (LF ≈ HF; nothing for MF to add).

Every one of these is detectable from the data alone in under a minute.
In this harness, batch N+1 was the error-detector for batch N; these tools move detection to *before batch 1* and give any agent a way to stop the line the moment a defect is found.

## `preflight.py` — run before batch 1, and after any regeneration

```bash
python preflight.py --root <benchmark_root> --datasets <a> <b> ... --out preflight_report.json
python preflight.py --selftest     # instruments must detect all four synthetic defect classes
```

Checks per dataset (factory npz layout): `completeness` (nearest-pair witness + the generator gate's `condition_completeness` meta record), `pairing` (per-row diagonal-cosine-above-p95-of-off-diagonal — robust to look-alike samples), `fidelity_gap` (NO_GAP / SATURATED warnings), `nn_baseline` (1-NN-in-condition-space floor; a weak triviality screen — the decisive triviality test is the generator gate's reconstruction certificate, which lives in `mffp_sharp.common.completeness`).

Exit 0 = launch may proceed. Exit 1 = hard fail (completeness or pairing): set a HOLD, then repair or explicitly `--waive <dataset>:<check>` (waivers are recorded in the report and belong in the round's launch ADR).

**Demonstration** (`preflight_round2_panel_demo.json`, run 2026-08-03 against `benchmark_42/sharp` as round 2 shipped): flags pfc / fisher_kpp / allen_cahn INCOMPLETE, pfc NO_GAP + TRIVIAL_NN, helmholtz SATURATED, cahn_hilliard PASS — i.e., it catches the audit's data-side findings before a single batch is spent. (The ifc pairing class is covered by `--selftest`; ifc's data lives on the cluster.)

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
3. call `hold.py check` before *every* batch dispatch;
4. re-run preflight after any dataset regeneration mid-round (panel mutation is allowed only under an explicit ADR).
