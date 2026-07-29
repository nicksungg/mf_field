# Summary So Far — Websearcher, Stream `s1_poisson`, Batch 1

> Persisted verbatim by the orchestrator from the websearcher's return
> (agent could not Write .md files — harness restriction; content unmodified).

## The question this stream owns

`project.yaml`: *"why is `ifc_poisson` above the paper bar (0.036), and what closes it?"* Class **gap**. Round success criterion 1 (`program.md` §1) is exactly this dataset at or below **0.036** nRMSE, stretch **0.018**.

## What the dataset actually is (verified on disk)

`mf_field/factory_mffp/data/ifc_poisson/` — shapes read with numpy:

| split | fidelity | N | field | cond dim |
|---|---|---|---|---|
| train | 8 | 100 | (8,8) | 5 |
| train | 16 | 50 | (16,16) | 5 |
| train | 32 | 20 | (32,32) | 5 |
| train | 64 | **5** | (64,64) | 5 |
| test | 64 | 128 | (64,64) | 5 |

Three facts that shaped every search term:

1. **This is not LF-field-in / HF-field-out.** `ifc_raw` maps a **5-dim parameter vector → field** at a requested fidelity (`data_adapters/loaders.py::_load_ifc_raw`). The relevant literature is multi-fidelity *parametric surrogate / fidelity-ladder* learning, not image-to-image LF→HF fusion. That is why copy-LF is undefined here (ADR 0002).
2. **The ladder is nested and pyramid-shaped** (100/50/20/5, index-aligned — `loaders.py`: "for ifc_raw, all fidelities are aligned"). Exactly the structure the IFC ODE/GPODE methods exploit and exactly what all-pairs / multi-level training needs.
3. **N_hf = 5.** §12.1: prefer designs that **reduce variance** or **add information** over designs that **add capacity**.

## Current state

- **Anchors do not exist yet.** `state/anchors/` empty, `state/noise_floor.json` absent, `state/gates.md` records **G3 PENDING**. Batch 0 is live now (`squeue`: array `65956106_[0-35]`, `r1-batch`, partition `gpu`). Per §4.5 there is no numeric threshold for this stream yet — batch-1 falsification clauses must be qualitative or gated on the anchor landing.
- **No experiment cards exist** (`experiment_cards/` holds only `SCHEMA.md`); no prior websearch for this stream. Cold start.
- **Provisional prior only** (§2.3): best zoo `ifc_poisson` **0.042** → skill **1.17**, from `mf_fno_pinn_transfer` at the akash 2500-epoch bench. Round 1 runs at **200 epochs**, so that prior is optimistic for this tier.
- **Seed direction** (§12.1): all-pairs fidelity training, `mf_field/akash/models/mf_fno_allpairs`. Its `model.py` docstring cites `herde2024poseidon` + `perez2018film`; one FNO over every ordered pair (s<t), FiLM cond `[X, f_src, f_tgt]`. `akash/results/FINDINGS.md` ranks it #1 on the hard subset (gm **0.0094** vs FiLM anchor 0.0121, wins 5/12), with its only known failure being O(L²) pair cost at L=9 (era5/pm_test 12 h timeout) — irrelevant at L=4 (6 ordered pairs).
- **Falsified in-zoo, relevant here**: `mf_fno_richardson` ("continuous-fidelity + super-fidelity") is recorded **mostly FALSIFIED** in `FINDINGS.md` (0.0160). Continuous-fidelity conditioning has already been tried in this zoo and lost.

## Prior websearch by another agent (cite, don't re-derive)

`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` §4 is the HF-scarcity half and is this stream's territory: **[LF-10] MLMC** (2505.12940), **[LF-1] multi-stage to machine precision** (2307.08934), **[LF-4] F-Adapter** (2509.23173), **[LF-2] Spectral-Refiner** (2405.17211), **[LF-14] NOWS** (2511.02481) + **[LF-16] NPO** (2502.01337), **[LF-11] frozen-trunk MF-DeepONet** (2503.17941), **[LF-6] POSEIDON** (2405.19101). Its §4.6 ranks predict-then-solve 1st, multi-stage 2nd, MLMC 5th. `docs/reports/MF_Sharp_HighFreq_Report.md` is about sharp 2-D fronts — `s2_beyond_copy`'s problem, not this one. **These are prior websearches, not fetched-this-run citations** (§13.3).

## Open questions for this batch

- **Q1** Is 0.036 still the bar on the `li2022ifc` Poisson benchmark, and has anything gone below 0.018?
- **Q2** Is all-ordered-pairs fidelity training already published as an MF method (vs POSEIDON's *time*-pair all2all)? Decides measurement vs contribution.
- **Q3** What is quantified at N_hf ≈ 5 — variance reduction, control variates, frozen-trunk heads, ensembling?
- **Q4** Does a physics-residual route beat a data-amplification route at HF budget 5, and is that comparison published?
