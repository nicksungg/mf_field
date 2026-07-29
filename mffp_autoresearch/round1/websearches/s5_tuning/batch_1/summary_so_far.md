# Summary so far — Stream `s5_tuning`, Batch 1

## Current state relevant to this stream

**Stream question** (project.yaml): *"how much of the gap is knobs, not architecture?"*
Card class `tuning`. Constraint from program.md §12.5: **no new losses-as-mechanisms,
no new paradigms, no architectural changes — knobs on existing recipes only.**

**Anchor status: NOT YET CERTIFIED.** `state/anchors/` exists but is empty and
`state/noise_floor.json` does not exist — batch 0 is still running on SLURM
(`state/gates.md`: "G3 - batch 0 (anchors + noise floor): PENDING"; G1 and G2 are
PASS). Per program.md §4.5, until `state/anchors/s5_tuning.json` lands, the numeric
threshold for this stream is unavailable and the brainstormer must judge against the
falsification clause rather than a number. When it lands, the anchor is *the certified
champion's panel geomean skill* at smoke tier (200 epochs), seeds {0,1,2}, mean +/-
stratified percentile-bootstrap 95% CI (§2.3). **Any claim inside that CI is seed
noise, not an improvement**, and every falsification threshold must additionally clear
`state/noise_floor.json` per-dataset spread (§4.5).

**No prior experiment cards for this stream** - `experiment_cards/` contains only
`SCHEMA.md`. This is the first batch of the round; there is no dominant failure
mechanism yet from parts 6-7 of any card.

**Provisional priors only** (program.md §2.3, explicitly flagged as pre-round, from
the akash 2500-epoch bench): best zoo skill is > 1 on all six panel datasets -
helmholtz 1.45, cahn_hilliard 2.1, fisher_kpp 3.9, PFC 7.8, allen_cahn 15.1,
ifc_poisson 1.17. Every fusion model currently *loses to copy-LF*.

**The pre-directed knob for this batch** (program.md §12.5, and the G4 dry-run card):
**`modes_cap` 12 -> 32 on the champion recipe `mf_fno_transfer_film`.** Finding **F22**
(`docs/proposals/MODEL_TWEAKS.md:125`): "`modes_cap = 12` never scales with
resolution". Candidate **M1** (`docs/proposals/MODELS_TO_TRY.md:11,84-107`) proposes 32.
Verified in the code this batch touches:

- `mf_field/factory_mffp/models/mf_fno_transfer_film/smoke_eval.py:47-48` -
  `WORK_CAP = 256`; `SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, ...)`.
  `modes_cap` is **hardcoded, with no env-var knob** - the recipe will need one, and
  §5 immutable 5 requires it be recorded in the card `recipe` (it enters the cache key).
- Mode allocation `_modes(grid, cap)` = `(min(cap, H//2), min(cap, W//2+1))`.

Panel HF grids (read from each dataset's `meta.json` / `.npy` shapes) and what the
knob actually changes:

| panel dataset | HF grid | modes available (H//2) | at cap 12 | at cap 32 |
|---|---|---|---|---|
| `ext__helmholtz_2d` | 96^2 | 48 | 12 (25%) | 32 (67%) |
| `sharp__phase_field_crystal_2d` | 128^2 | 64 | 12 (19%) | 32 (50%) |
| `sharp__allen_cahn_2d` | 256^2 | 128 | 12 (9.4%) | 32 (25%) |
| `sharp__fisher_kpp_2d` | 256^2 | 128 | 12 (9.4%) | 32 (25%) |
| `sharp__cahn_hilliard` | 256^2 | 128 | 12 (9.4%) | 32 (25%) |
| `ifc_poisson` | 64^2 (ladder 8/16/32/64) | 32 | 12 (38%) | **32 (100%, full spectrum)** |

Spectral-weight cost implied by the champion's `SpectralConv2d` (two
`(in,out,mh,mw)` complex tensors, `hidden_channels=64`, `n_blocks=4`): cap 12 ~ 9.4M
real params in spectral weights; cap 32 ~ **67M - a 7.1x jump**, against `ntrain=400`
per sharp dataset and **N_hf = 5 on ifc_poisson** (`train/fidelity_64/ys.npy` shape
`(5,64,64)`). The knob is therefore not capacity-neutral, and on `ifc_poisson` cap 32
means a full-rank spectral operator fit from 5 HF samples.

## Relevant prior websearch reports

None - this is batch 1 of `s5_tuning`; `websearches/` was empty before this run.

## Known open questions

1. Does raising FNO mode count monotonically help, or is there a documented
   non-monotone / overfitting regime? (M1 assumes more modes ~ better; F22 only
   asserts the cap doesn't *scale*, not that raising it wins.)
2. Is 12->32 confounded by the 7.1x parameter increase - i.e. would any measured win be
   "modes" or just "capacity"? What do published ablations do to disentangle these?
3. Does FNO **spectral bias** mean the added high-frequency modes go unlearned even
   when allocated, making the knob a no-op rather than a win?
4. How does mode count interact with **LF-pretrain -> HF-finetune transfer** (the
   champion is a transfer-FiLM recipe) and with **scarce HF data** (N_hf=5)?
5. Prior art: `iFNO` (arXiv:2211.15188) already solves "choose the mode count" by
   growing modes during training - does that make a flat 12->32 bump uninteresting,
   or is the flat bump the right *tuning-stream* instrument since iFNO would be a new
   mechanism (out of scope under §12.5)?
