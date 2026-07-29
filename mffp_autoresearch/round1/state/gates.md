# Launch gate ledger — Round 1

## G1 — eval-layer smoke + assertion drill: **PASS** (2026-07-28)

- Real family end-to-end, contract tier:
  `python eval/score_panel.py --family_dir .../models/mf_fno_transfer_film
  --datasets ext__helmholtz_2d,ifc_poisson --epochs 2 --seed 0
  --out eval/results/g1_contract.json` → exit 0; both datasets scored
  (`metric_source: per_sample_mean`, `split: test_hf`); identical rerun hit
  the cache (`cached: true` both).
- **Seam catch (the gate working as designed):** the first G1 run raised
  `ScoreContractError: result JSON missing splits.test.nRMSE` — factory
  families emit `splits.test_hf` via `data_adapters/metrics.py::
  finalize_and_write`, with both an aggregate ratio-of-sums `nRMSE` and
  `rel_l2_per_sample`. Fix (committed): select the test split by contract
  naming and prefer the per-sample array (the round's one definition),
  recording `metric_source` per dataset. Eval suite: 27/27 green.
- Assertion drill (fake family): `FAKE_BREAK=wrong_dataset` →
  `ScoreContractError: result JSON reports dataset 'some_other_dataset',
  requested 'ext__helmholtz_2d'`; unknown dataset →
  `ScoreContractError: dataset 'not_a_dataset' has no entry in
  copylf_baselines.json`. Both fired with specific messages.

## G2 — copy-LF baselines: **PASS** (2026-07-28)

- `eval/copylf_baselines.json` generated; all panel ratios vs the
  characterization reference within [0.25, 4].
- Two documented divergences (in the JSON `_notes`): `ifc_poisson` uses the
  paper bar 0.036 (test split ships no LF — ADR 0002); `heat_local` ratio
  0.028 (highest-LF convention vs the characterization's coarser fidelity).



## G4 — dry-run card s5_tuning-B1: PENDING

## G3 — batch 0 (anchors + noise floor): **PASS** (2026-07-29)

- Array 65956106: 36/36 COMPLETED, 0 failed (after excluding bad node hpc-93-36;
  one wholesale INFRA failure on job 65955389 documented above).
- `state/noise_floor.json` + 5 anchors written by `eval/make_batch0_state.py`.
- Champion: `mf_fno_transfer_film`, panel geomean skill **6.703 [6.219, 7.102]**
  (200-epoch smoke tier; per-seed [6.5, 6.6, 7.0]-ish, see JSON).
- Per-dataset best-family mean skills (smoke tier): helmholtz 13.82,
  pfc 11.51, allen_cahn_2d 16.33, fisher_kpp 4.18, cahn_hilliard 5.53,
  **ifc_poisson 1.566** (best nRMSE ≈ 0.056 vs bar 0.036 at this tier).
- **Noise-floor alert**: `ext__helmholtz_2d` seed spread = 9.695 skill units
  (a diverging seed at 200 epochs) → min claimable effect there is 9.695.
  Brainstormers must treat helmholtz claims as unfalsifiable at smoke tier
  unless the design addresses the instability itself; the other five floors
  are tight (0.24-1.63).

## G4 — split per ADR 0006 (2026-07-29)

- **G4a (build-path): PASS** — starter/builder/code-review mechanics validated
  end-to-end on s5_tuning-B1 (card transcribed verbatim, build commit ad29239
  with bit-identical default-equivalence + mid-stage resume + exact knob audit,
  reviewer verdict SUGGEST/submit-as-is). s1-s4 starters+builders unblocked.
- **G4b (submit-path): PENDING** — recorded when s5-B1 seed 0 (job 65988184,
  H100 per ADR 0005) is RUNNING and score_panel has written its first valid
  per-dataset result. s1-s4 SLURM submits gate on G4b.

## G4b + G4 overall: **PASS** (2026-07-29)

- Guard-contract job 65988185 (s5-B1 build, H100) COMPLETED in 46 s with a
  valid seam-checked score_panel JSON (guard_contract_s0.json: code_hash,
  nrmse_def_hash, metric_source per_sample_mean, split test_hf, env knob
  recorded) at the analyzer-visible path. Seed-0 panel job 65988184 RUNNING on
  hpc-33-16. Submit path validated end-to-end: sbatch → H100 → venv → family
  on GPU → score_panel → correct output layout. With G4a (build path) this
  completes G4. s1-s4 SLURM submissions unblocked (submit on each
  reviewed_pass/suggest).
