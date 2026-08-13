# benchmark_30 campaign — r3s2_route (round-3 certified) vs mf_fno_transfer_film

Date: 2026-08-13.
Provenance: manifest `eac7b48eea76b77e`, registry `b30-0001`, certified family commit `e606a4f`, campaign branch `bench30-campaign` (base `83a547e`), revision root `rev-eac7b48e`.
Numbers below are read from `state/leaderboard.json` (rendered in `docs/report_tables.md`); nothing in this narrative is computed independently of that artifact.

## TL;DR

**The round-3 certified model is a specialist, not a generalist.**
Across the 29-dataset common eligible set, the film-transfer FNO baseline beats `r3s2_route` overall: film-relative skill geomean **0.6004** [0.5934, 0.6047] (seed_plus_run_interval; >1 would mean r3s2 wins).
Equivalently, r3s2's panel-geomean error is ~1.67× film's.
r3s2 wins on exactly 5 of 29 datasets (up to 6.4× on `sharp__fisher_kpp_2d`): three of the five certified round-3 panel members plus two out-of-panel datasets (`ext__helmholtz_2d`, `sharp__phase_field_crystal_2d`) — while the panel's other two members (`ifc_heat`, `ifc_poisson`) flip to film.
Film wins the remaining 24, often by 2–8×.

## What was run

- **Models.** `r3s2_route_b30`: the round-3 certified best (arm A1_stack_ic_reg), vendored byte-identical from commit `e606a4f` with only the three convention-registry set literals extended append-only (ADR b30-0001); recipe env is the certified B2 card verbatim, with a single documented infrastructure deviation (`R3S2_DIAG_OUT` redirected so certified round-3 diagnostics cannot be overwritten). `mf_fno_transfer_film`: the film-transfer FNO baseline family, unmodified.
- **Data.** All 30 `benchmark_30` datasets, verified **byte-identical three ways**: local arrays ≡ the corrected hub release ≡ the campaign staging copies (per-array sha256, sealed into the manifest; re-verified at collect time under spec D12). No curator action needed.
- **Protocol.** Round-3 stripped-view protocol: each family's `smoke_eval.py` runs against test views with LF physically absent; metric is per-sample rel-L2 mean; 3 seeds (0/1/2) × 200 epochs.
  Gate discipline: the launcher mechanically refuses any tier whose required gates are unrecorded or bound to a different sealed manifest.
  `gates.json` carries the latest recordings — G0–G2 were re-recorded 03:22–03:24Z (after the floors build) between a first smoke attempt (01:23Z) and the replacement smoke (03:31Z) whose scores are the ones that stand; G3 (03:46Z) preceded full seed 0 and G4 (07:12Z) preceded seeds 1–2.
- **Aggregation (spec D9).** Per seed: panel geomean of `nrmse_film / nrmse_model` over the common eligible set; then mean and [min, max] across seeds.

## Headline and group results

| scope | n | skill geomean (mean) | [min, max] over seeds |
| --- | --- | --- | --- |
| **all common** | 29 | **0.6004** | [0.5934, 0.6047] |
| core | 10 | 0.3982 | [0.3900, 0.4121] |
| ext | 6 | 0.7845 | [0.7479, 0.8461] |
| sharp | 13 | 0.7290 | [0.6921, 0.7584] |

Per-seed headline geomeans: 0.5934, 0.6047, 0.6032 — seed scatter is small (≈2%), so the conclusion is not seed luck.

### Where r3s2 wins (skill = ratio of 3-seed mean rel-L2, film/model)

| dataset | skill | r3s2 rel-L2 | film rel-L2 |
| --- | --- | --- | --- |
| sharp__fisher_kpp_2d | **6.42** | 0.0048 | 0.0306 |
| ext__helmholtz_2d | **5.16** | 0.8588 | 4.4294 |
| sharp__allen_cahn_2d | **2.63** | 0.1769 | 0.4656 |
| sharp__cahn_hilliard | **1.35** | 0.3600 | 0.4857 |
| sharp__phase_field_crystal_2d | **1.22** | 0.7719 | 0.9394 |

Three of the five (`sharp__allen_cahn_2d`, `sharp__fisher_kpp_2d`, `sharp__cahn_hilliard`) are members of the certified round-3 5-dataset panel; the other two (`ext__helmholtz_2d`, `sharp__phase_field_crystal_2d`) are out-of-panel.
The panel's remaining two members — `ifc_heat` (0.23) and `ifc_poisson` (0.37) — flip to film: round 3 certified r3s2's panel advantage in **copy-LF-relative** skill (geomean 10.09), which is a different denominator and does not imply beating film on every panel dataset.
On `ext__helmholtz_2d` film is catastrophically unstable (rel-L2 4.43 [3.13, 5.75] — worse than predicting zero), while r3s2 stays at 0.86; the win is real but both models are far from solving that dataset.

### Where r3s2 loses hardest

`poisson_generated` (0.12), `sharp__helmholtz_2d` (0.16), `ifc_heat` (0.23), `allen_cahn_generated` (0.26), `sharp__shallow_water_1d` (0.26).
A plausible mechanism — a hypothesis, not established by these artifacts — is that these are fields where LF is already informative, so film's lighter conditioning suffices and r3s2's routing/stacking machinery adds error; testing it would need the round-3 diagnostic probes (LF-informativeness / per-band error), which this campaign did not run.
Note the two Helmholtz datasets split in opposite directions — the ext variant favors r3s2 by 5×, the sharp variant favors film by 6× — so "Helmholtz" as a class does not discriminate; whatever does discriminate is dataset-level, not equation-level.

Full per-dataset table (3-seed mean [min, max] for both families): `docs/report_tables.md`.

## Coverage, exclusions, integrity

- 177/177 eligible (family, seed, dataset) cells produced score files; zero per-dataset failures; nothing was added to the exclusion ledger during the run.
- **era5** is excluded for r3s2 only, predeclared under spec D11: the frozen family's `WORK_CAP=256` raises on the 721×1440 grid (`R3S2ContractError`, deterministic across 3 attempts, jobs 552488/558642) and D2 forbids modifying the certified family.
  Film's era5 numbers (0.0451 [0.0449, 0.0453]) are informational only and are outside the common set and headline.
  `score_ledger_conflicts: ['era5']` in the leaderboard is this same fact surfaced by the aggregator (a ledgered dataset with score files from the other family), not an error.
- Strict accounting passed: every universe cell is a result or a ledger entry; the collect-time D12 re-hash re-verified all source arrays and stripped views byte-for-byte before publishing.
- Anchor cross-check: film's `ifc_heat` seed-0 rel-L2 is 0.0268262, vs the round-3 record 0.0268172 under the same per-sample-mean convention (`round3/state/adr0007_meanremoved_check_2026-08-10.json`) — an independent retraining reproducing the anchor to 0.03% (3 significant figures).

## Interpretation

The round-3 campaign optimized for a sharp-interface-heavy panel and certified r3s2_route as its winner; this campaign asks whether that winner generalizes.
It does not: on a broad 30-dataset panel the much simpler film-transfer baseline is the better default model, and r3s2's advantage survives on only 5 of 29 datasets — four phase-field / reaction-diffusion problems plus one Helmholtz variant.
Why those five (and not, e.g., the ifc datasets it was certified on) is an open question for the round-3 diagnostic toolkit, not something this campaign's artifacts answer.
For the benchmark paper this is a *useful* result — it demonstrates the panel discriminates between specialist and generalist architectures rather than rewarding one universally.
An honest leaderboard entry for r3s2 should therefore report both the headline loss (0.60) and the home-turf wins, not either alone.

## Data-methodology caveats (for interpretation, not blocking)

1. **`ext__pressure_poisson_poiseuille`**: its LF is block-mean-downsampled HF plus noise.
   The source paper (Partin et al. 2022) specifies *subsampling*; block-mean restriction is this repo's documented implementation assumption in reproducing it.
   Either way it violates this repo's "LF is always a real coarse solve, never downsampled HF" rule, so skill numbers on it (0.84, near-tie) should be read with that in mind.
2. **`heat_generated`**: the fidelity levels sample inconsistent time windows, so the LF→HF task conflates resolution transfer with time-window shift.
3. **rel-L2 is level-dominated on near-uniform fields** (round-2 finding): `benchmark_42/MANIFEST.csv` records `sharp__fisher_kpp_2d` copy-LF rel-L2 0.00062 raw vs 0.02161 mean-removed (35×, `level_dominated=1`), so on that dataset most of the raw denominator is the field's constant level; the 6.4× win is protocol-true but could shift substantially under mean-removed metrics, which this campaign did not compute for the model outputs.
4. **era5** has ragged per-rung train counts across fidelity levels (a dataset property, independent of the WORK_CAP exclusion).

## Ops summary

Six full-tier SLURM jobs, all COMPLETED clean on the first submission of each tier: seed 0 — 559434 (r3s2, 3h01), 559435 (film, 1h25); seeds 1–2 — 579107/579108 (r3s2, ~2h08 each), 579109/579110 (film, ~1h25 each).
Per-cell train/eval wall-clock is in `leaderboard.json` under `ops` (full-tier files only; a post-campaign fix excluded the smoke-tier files that had contaminated seed-0's ops telemetry — scientific numbers were never affected; the result files carry no memory fields).

## Reproduction

```bash
cd mffp_autoresearch/benchmark30
# gates + staging: staging/run_gates.py, staging/validate_tier.py
# launch: slurm/launch.py --tier {smoke,full-seed0,full-seeds12}
# aggregate: aggregate/collect.py (strict + D12 rehash)  → state/leaderboard.json
# render:    aggregate/report.py                          → docs/report_tables.md
```
