# Brainstormer Report — Stream `s4_hybrid_routing`, Batch 2

**Stream**: `s4_hybrid_routing` · **Batch**: 2 · **Total iterations**: 1 · **Slot filled**: yes (1 proposal, 3 arms)
· **Reopen candidates resolved**: 0 formal (none exist) + 2 parked branches resolved

## Slot

- **Category**: `mf_composition_repair_and_class_test` — gate-protocol repair + LF-context density + the
  attention-vs-closed-form head-to-head, all on B1's `fno_transolver_seq` substrate.
- **Card type**: `model` (3 trained arms at smoke tier; the reference values are in-run and cost seconds)

- **Motivation**: the batch-2 verdict leaves s4 exactly one `novel` surface and two `preempted` repairs it must run as
  measurements. Quoted verbatim from `websearches/s4_hybrid_routing/batch_2/report.md`:
  *"Nobody has run it: matched-parameter cross-attention corrector vs local/LSI corrector on the same `hf - base`
  (or `hf - copylf`) target, on regular grids with sharp interfaces, at N_hf ≈ tens. The prior predicts attention
  **loses**, and 2511.06294 supplies the mechanism (the nonlocal content-adaptive part is not what works; slice/deslice
  pooling is). B1's fisher_kpp band-1 result is the only pro-attention datapoint in this loop ... Either outcome closes
  the stream's class — the definition of genuine under program.md §1."* For the gate arm:
  *"**Claim ZERO mechanism novelty. The card is a protocol-defect measurement with a quantified cost, and it should
  cite 2606.17460 as the published method that shares the hazard.**"* For the density arm:
  *"**A card must pre-register the skill-1.0 ceiling and the free control that already reaches it**
  (`base + a*(copylf - base)`: 0.114384 vs 0.125893 on pfc, 0.202549 vs 0.226409 on fisher_kpp, B1 F13) ... s4's version
  is defensible only as the **attention arm of the (iii) comparison**."* B1's own part 7 licenses exactly these two
  repairs (shrinkage KEPT) and refuses routing; its sharpest single number is the wrongly-vetoed cahn_hilliard
  correction (F2: `alpha_ls` 1.1027 is the test optimum to 0.9%, worth **-43.2%**, skill 5.5627 -> **3.1622**).

- **Concrete config**: vendor `models_r1/fno_transolver_seq` @ `4691d1f...` (B1's build commit, sha256-verified per
  file) to `models_r1/fno_transolver_seq_b2`; `model.py` byte-identical; all new behaviour env-gated and defaulting to
  B1 semantics. Four edits: (1) `_fit_alpha` gains a scoring base — `S4_GATE_BASE=oof` scores the 0-containing
  **shrinkage line search** against `base_oof[val_idx]` (already the LS half's own reference, so both halves become
  Wolpert-consistent; ~3 lines, zero extra GPU cost), while the run *always* emits `alpha_b1_insample`, `alpha_oof`,
  `alpha_least_squares` and pre-stage-3 test nRMSE at all four alphas (each fitted with **no test data**) — the B1
  replica control becomes a free, perfectly paired within-run leg; (2) `S4_CTX_POINTS=full` sets `n_ctx = Hc*Wc`
  (coverage 6.25% -> 100% on allen_cahn/cahn_hilliard/fisher_kpp, 25% -> 100% on pfc; a no-op at helmholtz 576 and
  ifc_poisson 1024) with query chunking at 4096; (3) `S4_BASE_MODE=copylf` + `S4_TARGET=hf_minus_copylf` for the
  head-to-head arm (base = `eval/panel_data.py::copylf_prediction`, asserted bit-equal to `eval/copylf_baselines.json`
  within 1e-9; FNO/OOF stages skipped); (4) score-neutral sidecars on every arm — the zero-parameter **LSI** reference
  (vendored, not imported, from `tools/defect_correction_learnability.py`), `ref_nrmse_scalar_blend`
  (`base + a*(copylf-base)`, `a` fitted on HF-train only), the B1 part-7 anatomy block (correction RMS/residual RMS and
  cosines with `hf-base`, `copylf-base`, `hf-copylf`), `gamma_init/gamma_final`, and for arm C
  `cosine(corr, corr_LSI)`, 4-band energy fractions and inference-time branch ablations
  (`nrmse_no_cross_branch/_no_self_branch`). **All sidecar metrics import `round1/eval/nrmse.py`**; the scored value is
  always `score_panel.py`'s. **Arms** (seed 0, 200 ep): **A `gate_repair`** (panel, sparse ctx), **B
  `gate_repair_dense`** (panel, dense ctx), **C `attn_gap_fkpp`** (`sharp__fisher_kpp_2d`, copy-LF base,
  `hf - copylf` target, dense ctx). Guard set at contract tier for A and B; one contract-tier screen (all arms,
  panel+guard) as the plumbing/no-harm gate. **Validity gates** V1 (b1-style leg reproduces B1 within 2% on the four
  alpha=0 datasets), V2 (LSI reference reproduces s6-B1 F6 within 2%), V3 (dense == sparse bit-exactly on helmholtz and
  ifc_poisson), V4 (arm C at alpha=0 IS copy-LF within 1e-9). Cost ~335 GPU-min as a 13-task H100 array
  (max task ~45 min), vs B1's 123.

- **Recipe**:
```json
{
  "base_family": "fno_transolver_seq",
  "base_commit": "4691d1fbaaa4dc9e0e6fbaf3bf607afef203404c",
  "family_dir": "models_r1/fno_transolver_seq_b2",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "MFFP_CTX_SOURCE": "auto",
    "S4_ARM": "gate_repair",
    "S4_GATE_BASE": "oof",
    "S4_ALPHA_DIAG_SET": "zero,b1_insample,oof,ls",
    "S4_CTX_POINTS": "1024",
    "S4_CTX_QUERY_CHUNK": "4096",
    "S4_BASE_MODE": "fno",
    "S4_TARGET": "hf_minus_base_oof",
    "S4_KEEP_LINESEARCH_SHRINKAGE": "1",
    "S4_LSI_SIDECAR": "1",
    "S4_LSI_RIDGE": "0",
    "S4_LSI_F6_TOL": "0.02",
    "S4_SCALAR_BLEND_SIDECAR": "1",
    "S4_ANATOMY_SIDECAR": "1",
    "S4_BRANCH_ABLATION_SIDECAR": "0",
    "S4_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "S4_REPLICA_ASSERT": "1",
    "S4_REPLICA_TOL": "0.02",
    "S4_COPYLF_IDENTITY_TOL": "1e-9",
    "S4_DIAG_OUT": "mffp_autoresearch_outputs/round1/s4_hybrid_routing/B2/eval",
    "_note": "keys prefixed _ are card directives, NOT passed to --env; the --env set per arm is the non-underscore keys above with the arm's deltas from _arms applied.",
    "_arms": [
      {"tag": "gate_repair", "role": "PRIMARY for C1 (gate protocol) + continuity gate V1", "datasets": "panel",
       "S4_ARM": "gate_repair", "S4_GATE_BASE": "oof", "S4_CTX_POINTS": "1024", "S4_BASE_MODE": "fno",
       "S4_TARGET": "hf_minus_base_oof", "S4_BRANCH_ABLATION_SIDECAR": "0"},
      {"tag": "gate_repair_dense", "role": "PRIMARY for C2 (LF context density); paired with gate_repair", "datasets": "panel",
       "S4_ARM": "gate_repair_dense", "S4_GATE_BASE": "oof", "S4_CTX_POINTS": "full", "S4_BASE_MODE": "fno",
       "S4_TARGET": "hf_minus_base_oof", "S4_BRANCH_ABLATION_SIDECAR": "0"},
      {"tag": "attn_gap_fkpp", "role": "PRIMARY for C3 (attention vs zero-parameter LSI on the same target/base)",
       "datasets": "sharp__fisher_kpp_2d",
       "S4_ARM": "attn_gap_fkpp", "S4_GATE_BASE": "oof", "S4_CTX_POINTS": "full", "S4_BASE_MODE": "copylf",
       "S4_TARGET": "hf_minus_copylf", "S4_BRANCH_ABLATION_SIDECAR": "1"}
    ],
    "_primary_contrasts": {
      "C1_gate": "gate_repair scored (alpha_oof) vs its own pre-stage-3 nrmse_at_alpha_b1_insample leg, per dataset",
      "C2_density": "gate_repair_dense vs gate_repair, per dataset, AND vs ref_nrmse_scalar_blend",
      "C3_attention": "attn_gap_fkpp vs its in-run ref_nrmse_LSI on sharp__fisher_kpp_2d"
    },
    "_validity_gates": "V1 b1_insample leg reproduces B1 within S4_REPLICA_TOL on the four alpha=0 datasets; V2 LSI reference reproduces s6-B1 F6 within S4_LSI_F6_TOL; V3 dense == sparse bit-exactly on ext__helmholtz_2d and ifc_poisson; V4 arm C at alpha=0 equals copy-LF within S4_COPYLF_IDENTITY_TOL. Any miss is ALGO.",
    "_source": "vendor models_r1/fno_transolver_seq from 4691d1fbaaa4dc9e0e6fbaf3bf607afef203404c (branch round1/exp-s4_hybrid_routing-B1) to models_r1/fno_transolver_seq_b2, sha256-verified per file via `git show <commit>:<path>`; upstream akash origin 967562e2a4e3493515edab36b0fcb23655fce71f. model.py byte-identical. LSI + scalar-blend + anatomy helpers VENDORED with citation from tools/defect_correction_learnability.py and tools/correction_anatomy.py (never imported, so the family code_hash stays complete); eval/panel_data.py::copylf_prediction and eval/nrmse.py imported READ-ONLY with sha256 recorded. akash/**, factory_root/{eval,baselines,references,scripts,data} and round1/{eval,tools}/ are never written.",
    "_sweep": "one array job, seed 0, one score_panel.py call per (arm, dataset): 6 + 6 + 1 = 13 tasks; export ROUND1_EVAL_RESULTS=<outputs>/eval/results_<tag> per arm (score_panel._run_one derives out/ckpt paths from (family_dir.name, dataset, epochs, seed) only); one --out result_<tag>_<dataset>_s0.json each, then one afterok aggregate per arm (--datasets panel, pure cache hit) for the geomean.",
    "_screen": "ONE contract-tier job before the sweep: --epochs 2 --seed 0, all three arms, --datasets panel and --datasets guard. Plumbing + no-harm only (arm C must score <= 1.02 skill; V4 must hold). Screen numbers stay in build_notes and are NEVER reportable (ADR 0007).",
    "_guard_spec": "--datasets guard --epochs 2 --seed 0 for gate_repair and gate_repair_dense (program.md 2.3 contract tier for a panel-win claim); B1's guard analog took 1.42 min. Note s6-B2's critique that a 2-epoch guard is weak; recorded, tier unchanged because program.md 2.3 specifies contract tier.",
    "_sbatch": "partition gpu, --gres=gpu:h100:1 (ADR 0005), job names r1-s4_hybrid_routing-B2-s0, logs under mffp_autoresearch_outputs/round1/s4_hybrid_routing/B2/slurm/. --time=02:00:00 per array task (ledger: B1 max 31.28 min/dataset on H100; dense adds ~50% on the corrector stage -> ~45 min worst case, >2x headroom), --time=01:00:00 for the screen, --time=00:30:00 for guard + aggregate. Total ~= 335 GPU-min."
  }
}
```

- **Expected outcome** (all `provisional-single-seed`, ADR 0004; floor convention: absolute
  `min_claimable_effect` where the arm sits at the anchor's scale, relative 10% where the absolute floor exceeds the
  arm's whole skill — justified by the certified 3-seed *relative* spreads fisher_kpp 2.197%, cahn_hilliard 3.467%,
  pfc 0.718%, allen_cahn 0.087%):

| contrast | metric that moves | predicted | claim bar | vs floor |
|---|---|---|---|---|
| **C1** gate repair, `sharp__cahn_hilliard` (arm A vs its paired b1-style leg) | test nRMSE / skill | 0.48762844 -> **~0.27720 (skill 3.1622)**, `alpha_oof` in [0.75,1.25] | <= 0.30681 (skill <= **3.5**) | bar 0.5562725 skill units > floor **0.5533466** (1.005x); predicted move 2.40 units = **4.3x** floor |
| **C1 downside** `pfc` (pre-registered) | test nRMSE | alpha may rise 0.2509 -> ~0.9944 and cost up to **8.47x** (skill 3.28 -> ~27.8, F13) | none — reported as the second price of the two-sided bias | even then panel geomean **7.35 < 10.0545** cratered threshold |
| **C2** density, arm B vs arm A | per-dataset skill; `cosine(corr, copylf-base)` -> >= 0.9 | pfc/fisher_kpp/cahn_hilliard move **toward but not through skill 1.0**; panel geomean **2.5-4.5** | >= floor on **2 of 3** (pfc **1.1511**, fisher_kpp **0.41774**, cahn_hilliard **0.55335** skill units) **and** beat `ref_nrmse_scalar_blend` (pfc 0.114384 / fisher_kpp 0.202549) | bars **are** the certified floors; geomean floor 0.884 (13.2% rel) |
| **C3** attention vs zero-parameter LSI, `sharp__fisher_kpp_2d` | test nRMSE | attention **loses**: **0.010-0.045** (skill 0.16-0.72) vs LSI 0.0076951 (0.122861) and s6-B1's local corrector 0.0059583 (0.0951) | keep-attention iff nRMSE <= **0.00692557** (skill <= 0.110575) **and** `cosine(corr, hf-copylf) >= 0.3`, RMS ratio in [0.5,2.0] | 10% relative = **4.5x** the certified 2.197% relative seed spread (absolute floor 0.41774 is vacuous at skill ~0.12) |

  Not claimed: **no arm reaches skill < 1** anywhere (criterion 2 stays open in this stream);
  `ext__helmholtz_2d` (floor 9.694961 = 70.2% rel) is **report-only**; `ifc_poisson` (floor 0.2399076) is a watch item;
  allen_cahn's corrector may un-collapse under dense context (RMS ratio 0.00063 -> ?) — reported, not claimed;
  no panel-geomean claim for arm A (B1 F12: the repaired-gate panel move -0.5275 is inside the 0.884 floor); arm B's
  geomean, if it moves, is labelled **attainment toward the skill-1.0 ceiling** (a better copy-LF re-derivation,
  `cosine(corr, hf-copylf)` predicted <= 0.1), not fidelity-gap information.

- **Expected falsification**: If (C1) the base-out-of-sample gate fails to improve `sharp__cahn_hilliard` by more than
  10% relative (0.48762844 -> <= 0.43886560, i.e. >= 0.5562725 skill units, above the certified floor 0.5533466)
  against the paired in-sample-gate leg of the same run, AND (C2) the dense-LF arm fails to beat the sparse arm by at
  least each dataset's `min_claimable_effect` on >= 2 of {pfc 1.1511, fisher_kpp 0.41774, cahn_hilliard 0.55335} skill
  units or fails to beat the in-run one-scalar `base + a*(copylf - base)` control, AND (C3) the attention corrector on
  the `hf - copylf` target fails to beat the in-run zero-parameter LSI reference on `sharp__fisher_kpp_2d` by more than
  10% relative (0.00769508 -> <= 0.00692557), then no remaining lever of the alpha-gated **attention**-corrector class
  — not the gate protocol, not context density, not the residual target — clears this round's noise floor on the sharp
  panel, and s4's recommendation is to retire the attention corrector in favour of the local/closed-form class that s6
  owns.

- **Prior-art verdict quoted**: `preempted (cite)` for the gate repair —
  *"the estimator is published for neural operators; only the *diagnosis* is open"*, with
  https://arxiv.org/html/2606.17460 (fetched: *"each stage validation-safe: if a trained correction does not reduce
  validation error, it can be rejected"*, base = *"the empirical mean output field"*, *"not multi-fidelity"*,
  *"does not explicitly confirm whether validation data is withheld"*, *"-202% error change"* failures) ·
  https://arxiv.org/pdf/1106.1684 (Wolpert 1992: *"the combiner must be trained on predictions from base classifiers
  applied to held-out data"*) · https://arxiv.org/html/2309.09880 (*"the solution `alpha_hat` ... satisfies
  `sum alpha_hat_k <= 1`"*) · https://arxiv.org/html/2309.14596 (two smoothers + Mallows' Cp = James-Stein,
  *"purely statistical regression"*). `preempted-but-MF-composition-open (cite)` for dense context —
  https://arxiv.org/html/2502.09692v3 (*"Increasing M enhances contextual information ... improving performance up to a
  saturation point"*) · https://arxiv.org/pdf/2605.15305 (cross-attention anchors as *"data-adaptive interpolation
  weights"*) · negatives 2507.07292 / 2204.06684 / 2512.16074 (LF-*count* ablations only).
  **`novel`** for the head-to-head — *"as a measurement; and the prior art is **hostile to attention**"*:
  https://arxiv.org/abs/2511.06294 (*"Physics-Attention can be reformulated as a special case of linear attention, and
  that the slice attention may even hurt the model performance"*; gains from *"the slice and deslice operations
  themselves"*) · https://arxiv.org/html/2411.00040 (*"does not employ attention mechanisms anywhere ... nor does it
  compare"*) · https://arxiv.org/html/2509.01293v3 (*"Both E-UNO and UNO consistently achieve errors an order of
  magnitude lower than FNO"*, no attention baseline) · https://arxiv.org/html/2511.09729v1 (winner is *"a deep FiLMed
  residual network with spectral convolutions"*) · https://arxiv.org/abs/2605.08318 (attention beats Fourier only on
  *"complex, irregular geometries"*).

- **Immutables self-check**: **pass (10/10)** — see `iteration_1.md` §5 for the positive evidence on each. Two items
  were resolved by design decisions taken inside the pass rather than post hoc: item 4 (every sidecar/reference nRMSE
  must import `round1/eval/nrmse.py`, so the one-definition rule holds for the non-scored legs too) and item 9 (the
  absolute-vs-relative floor convention for the arm-C scale, with the certified relative seed spread quoted as the
  justification). No violation was found and no revision iteration was needed.

- **Anchor reference**: `"s4_hybrid_routing-B1"` (batch >= 2 re-targets the stream's current provisional champion card;
  every contrast is paired against B1's substrate). Numeric anchor for any geomean statement remains the certified
  `state/anchors/s4_hybrid_routing.json` 6.703016262587087 — B1's 5.664889 was single-seed and explicitly not promoted.

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none formal)* — `s4_hybrid_routing-B1` is `status: complete`, `reopen_candidate: false`; `batch_1` is the stream's only prior card | n/a | n/a | [iteration_1.md](iteration_1.md) §4 |
| parked branch: LF-conditioned **spatially-resolved routing** (B1 part 7 REFUSED; websearch D2/§5) | **DROP** | none possible — F11 priced every rung under every floor (per-sample oracle <= 5.33%, honest per-pixel -1.31%/+6.18%/+3.54%, in-sample pixel UB <= 4.40%), s6's `trust_gate_headroom.py` agrees from the opposite base, and verdict §5 forbids resurrection | [iteration_1.md](iteration_1.md) §2.6, §4 |
| parked branch: **C5 boosting/cascades** (B1 part 7 DEFERRED) | **DEFER again** | its gate ("stage 1 below skill 1.0 on a Class-A dataset") is unmeetable by arms A/B (ceiling skill 1.0, F6); arm C decides whether an attention cascade is even in the right class — if C3 fails, part 7 should DROP it | [iteration_1.md](iteration_1.md) §2.6, §4 |
| B1 standing reporting requirement (RMS ratio + cosines beside every gate value) | **CARRIED IN** | `S4_ANATOMY_SIDECAR=1` on all three arms (verdict §6) | [iteration_1.md](iteration_1.md) §3.4 |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B2 | `mf_composition_repair_and_class_test` | Repair the gate on a base-out-of-sample split (shrinkage KEPT) and densify the LF context on B1's own substrate, with a paired within-run B1-protocol leg, then settle the round's attention question head-to-head against a zero-parameter closed-form filter on `sharp__fisher_kpp_2d` — designed to lose, and decisive either way. | filled |
