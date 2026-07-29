# iteration_1 — s4_hybrid_routing batch 2 slot design

## 1. Design context considered

- `summary_so_far.md` §6 unknowns #1–#4 (gate-protocol two-sided bias; context density vs wrong target;
  attention-vs-local; the unknowable deployed-base residual scale) and §6.5 (what NOT to re-measure).
- The batch-2 prior-art verdict, all three rows, verbatim (quoted in §3.3 below).
- The **immutables block** (program.md §5, distilled in the brainstormer prompt §4.5) held in view throughout;
  self-check in §5.
- Anchor `state/anchors/s4_hybrid_routing.json` = **6.703016262587087** [6.21853605194748, 7.102239525443188]
  (3-seed, certified, `provisional: false`); geomean floor 0.8836555 = 13.183% relative; cratered 1.5x = **10.0545**.
- `state/noise_floor.json` `min_claimable_effect` (skill units): allen_cahn **1.633407079448426**,
  pfc **1.1511001428346894**, fisher_kpp **0.41773549950819566**, cahn_hilliard **0.5533465853654416**,
  helmholtz **9.694961194291832** (70.2% relative -> report-only), ifc_poisson **0.23990756041925798**.
  Certified 3-seed *relative* spreads (spread/mean_skill): allen_cahn 0.087%, pfc 0.718%, fisher_kpp **2.197%**,
  cahn_hilliard **3.467%** — these matter because two of this card's contrasts live at a skill scale far below the
  anchor's, where the absolute floor is vacuous (s6-B2 hit the same problem and used the relative form).
- Pre-falsified levers (program.md §5): WNO backbone swap, LF low-mode freezing, diffusion prior. Plus the two
  **in-round** refusals I must honour: spatially-resolved routing (B1 F11, priced under every floor) and
  "drop the line search, use `alpha_ls`" (B1 F13, 8.47x regression on pfc).
- Cost reality: B1's panel was **122.93 GPU-min** on H100 (per dataset 31.28 / 30.73 / 28.88 / 15.47 / 15.47 / 1.10);
  the Transolver corrector is the round's slowest artifact. ADR 0004 (seed 0 only), ADR 0005 (h100), ADR 0007
  (propose-many/screen-cheap — reconciled in §2.6), ADR 0009 (no physics at test time — satisfied: nothing here reads
  a governing equation).
- Code read line-by-line: `worktrees/s4_hybrid_routing/B1/models_r1/fno_transolver_seq/smoke_eval.py`
  (stage 1 `:349-356`, OOF folds `:358-377`, residual/ctx `:379-386`, split `:388-393`, corrector `:395-401`,
  gate `:403-416`, stage 3 `:420-446`, eval `:457-479`, `_fit_alpha` `:216-240`, `_corr_full_field` `:157-171`),
  `model.py` (`soft_interp` `:89-101`, cross/self slice attention `:203-226`, `gamma_init_for` `:265-276`),
  and `eval/score_panel.py` (`_run_one` `:75-113`: out JSON and ckpt paths derive from
  `(family_dir.name, dataset, epochs, seed)` **only** -> per-arm `ROUND1_EVAL_RESULTS` is mandatory;
  `code_hash(family_dir, env)` `:51-73` includes the env knobs, so arms get distinct cache keys).

## 2. Proposal reasoning

### 2.1 What this batch must be

B1 answered the stream's founding question in the negative for routing (F11: per-sample oracle <= 5.33%, honest
per-pixel <= 1.31% and negative on 2/3 — all inside every floor) and diagnosed the artifact instead: the gate is
internally inconsistent (F1/F2), and the correction is a lossy re-derivation of copy-LF (F6/F7/F10). The verdict rows
say the two licensed repairs are `preempted (cite)` and `preempted-but-MF-composition-open`, and that the ONE `novel`
thing s4 still owns is *"matched-parameter cross-attention corrector vs local/LSI corrector on the same `hf - base`
(or `hf - copylf`) target, on regular grids with sharp interfaces"*. So the batch is: **repair + densify the same
substrate (measurement, zero novelty claimed) and run the head-to-head that decides the attention class**. That is
one card because all three contrasts share one family, one substrate and one SLURM chain (program.md §4.2).

### 2.2 The gate repair: which repair, and the free paired control

B1 part 7 prescribes "hold `val_idx` out of the stage-1 HF fine-tune, keep the full-data FNO for prediction (one extra
FNO fine-tune)". Reading the code, there is a **strictly cheaper and strictly cleaner** version: `base_oof` already
holds a leave-one-fold-out prediction for **every** HF sample, including `val_idx` (`:358-377`), and `_fit_alpha`'s
least-squares half *already* uses `R_val = Y[val_idx] - base_oof[val_idx]`. Only the line-search half
(`:231-239`) swaps in `base_val_final`, the full-data FNO evaluated on samples it memorised. So the minimal,
internally-consistent repair is: **score the line search against `base_oof[val_idx]`** — Wolpert-clean (both halves
now see out-of-sample base predictions), ~3 lines, **zero extra GPU cost**, and equivalent in spirit to part 7's
recipe (fold bases see 75% of HF, a held-out refit would see 80%).

That choice buys the paired control for free too. If I leave the split draw exactly where it is (`:391-392`, consuming
`gen` after the stage-1/1b trainings), the repaired arm's RNG stream, corrector weights and correction field are
**bit-identical to B1's**; the only difference is which scalar multiplies the correction. So one run can emit the test
nRMSE at BOTH fitted alphas — `alpha_b1_insample` (B1's protocol) and `alpha_oof` (the repair) — computed
pre-stage-3, both fitted with **no test data**. That is a perfectly paired protocol contrast and it makes a separate
200-epoch `b1_replica` arm unnecessary (~123 GPU-min saved); the b1-style leg doubles as the continuity/validity gate
against B1's shipped numbers.

### 2.3 The honest reason this repair may LOSE on pfc, and why that is the finding

The repair's bias is one-sided in the opposite direction to the defect's: alpha is fitted against a base that is
*weaker* than the deployed full-data base, so the correction it wants is *larger* than the deployed base needs.
B1 measured both ends of exactly this axis: the memorised-base protocol forfeited 43.2% on cahn_hilliard (F2), while
`alpha_ls` — which IS the base-OOF-consistent estimate — costs **8.47x** on pfc (F13: 0.125893 -> 1.066448, skill
3.28 -> ~27.8). The shrinkage line search is KEPT (candidate set `{0} U {0.25,0.5,0.75,1.0,1.25}*a_ls U {0.25,0.5,1.0}`,
clip [0,1.5], MIN_GAIN 1e-3), so shrinkage remains reachable — the open question is whether a val split scored on an
out-of-sample base still selects it. I therefore pre-register **both** prices and make C1 a per-dataset clause
(B1 F12 already showed the repaired-gate panel move, -0.5275, is inside the 0.884 geomean floor). Worst case check:
even with pfc at skill 27.8 the panel geomean is **7.35**, below the 10.0545 cratered threshold, so the card cannot
crater on this axis. This two-sided pricing is the card's actual contribution and it is exactly what the verdict asks
for: *"a protocol-defect measurement with a quantified cost"*, with 2606.17460 cited as the published method that
shares the hazard.

Rejected alternative: a "both-sided" acceptance rule (accept alpha only if it also improves val error under the
deployed base). Under the memorised base ANY alpha>0 raises val error (MECHANISM 1), so the rule collapses to B1's
defect. There is no third estimator available at N_hf=400 with an 80-sample val split (unknown #4); the bias is
structural, not a bug, and saying so is more honest than inventing a knob.

### 2.4 Dense LF context: the density arm, its ceiling, and its free controls

Coverage measured from B1's own family JSONs: n_ctx=1024 of 16384 ctx points = **6.25%** on allen_cahn /
cahn_hilliard / fisher_kpp, 1024/4096 = **25%** on pfc, and **100%** already on helmholtz (576) and ifc_poisson (1024).
"Dense" therefore means `n_ctx = Hc*Wc` (the whole finest-LF grid, still the real coarse solve — never downsampled HF).
Cost: `soft_interp` is a `cdist` of (queries x ctx); at eval queries = 65536 and ctx = 16384 that is 1.07e9 entries,
so the recipe fixes a query-chunk knob (4096) — training uses n_query=2048 so it is unaffected. Two properties make
this arm cheap to interpret: (a) on helmholtz and ifc_poisson dense is a **no-op**, so the dense arm must reproduce the
sparse arm bit-exactly there (free validity gate V3); (b) the mechanism it strengthens has a **ceiling of skill 1.0**
(F6: correction ⟂ `hf - copylf`, cosine <= 0.023), which the verdict requires me to pre-register together with the free
scalar control `base + a*(copylf - base)` — B1 F13 measured pfc 0.114384 (skill 2.554) and fisher_kpp 0.202549
(skill 3.234) for that control. I therefore make the control an in-run sidecar (`ref_nrmse_scalar_blend`, one scalar
fitted on HF-train only) and require the dense arm to beat **it**, not just the base. That is the difference between
"the attention corrector adds something" and "a denser input made a better interpolator".

### 2.5 The head-to-head (verdict iii) — designed to lose, with a mechanism read either way

Definition, on `sharp__fisher_kpp_2d` only (B1's single pro-attention datapoint, -12.20% with alpha 0.7408, and the
one dataset where s2's Class-B verdict says the fidelity gap is *not* LF-predictable — so it is the hardest honest
place to claim attention pays): base = **copy-LF** (`eval/panel_data.py::copylf_prediction`, asserted bit-equal to
`eval/copylf_baselines.json` 0.06263229669603956 within 1e-9, s6 precedent), target = **`hf - copylf`** on the HF-train
split, corrector = the same `TransolverCorrector` with dense LF context, gate = the same 0-containing line search on
the 80-sample val split (Wolpert-clean by construction, because copy-LF is training-free), and the **reference** =
the zero-parameter closed-form LSI filter computed in-run (vendored from `tools/defect_correction_learnability.py`,
validity-gated to reproduce s6-B1 F6's 0.007695081137159533 within 2%). "Matched" here means matched information,
target and base; the attention arm additionally gets ~5.47M trained parameters against the reference's **zero**, so
the comparison is deliberately generous to attention and a loss is decisive.

Prediction and its mechanism (pre-registered so a null is interpretable): a Transolver query's entire view of the LF
field is (i) the base value at the query point and (ii) ONE soft-interpolated LF scalar with a learnable bandwidth
`gamma`, plus 32 global slice tokens (`model.py:194-226`). Two scalars can realise at most a 2-tap radial stencil,
while the defect is a compact multi-tap filter (`tools/index.md`: 94% of the LSI stencil energy within 12 cells on
pfc, `rho_val` 0.9998). So I expect **nRMSE 0.010-0.045 (skill 0.16-0.72), worse than the LSI floor 0.0076951
(skill 0.122861) and worse than s6-B1's trained local corrector 0.0059583 (skill 0.0951)** — the outcome
arXiv:2511.06294 predicts, for the reason it names (gains come from slice/deslice interpolation, not attention).
To separate "nonlocality does not pay" from "this architecture never sees local structure", the run emits four free
score-neutral diagnostics: `gamma_init`/`gamma_final`, an inference-time branch ablation
(`nrmse_no_cross_branch`, `nrmse_no_self_branch` — attribution of a trained model, not a matched arm, and labelled so),
`cosine(corr_attn, corr_LSI)`, and per-band energy fractions of both corrections on the s6 band edges
(0, 0.125, 0.25, 0.5, 1.0).

**What would justify KEEPING attention in the round** (stated in advance, honestly): fisher_kpp nRMSE
**<= 0.0069256** (skill <= 0.110575, i.e. beating the zero-parameter floor by more than 10% relative = 4.5x that
dataset's certified 2.197% relative seed spread) **and** a correction that actually models the gap
(`cosine(corr, hf - copylf) >= 0.3`, RMS ratio within [0.5, 2.0]). Anything less and the recommendation this card
writes is: retire the attention corrector class in s4; the local/closed-form class (s6) owns the defect.

### 2.6 Arms rejected, and the ADR 0007 reconciliation

- **Any routing/gating arm** (per-band, per-region, per-sample head): REFUSED by B1 F11 and by verdict §5
  (*"Do not resurrect routing, in any spatial form"*). Not proposed.
- **`alpha_ls` without the line search**: falsified (F13, 8.47x on pfc). Not proposed; the shrinkage is kept and the
  card says why.
- **A trained conv/local arm inside s4**: that is s6's territory (s6-B2's `circ_repair`/`pointwise_ctrl_circ` are in
  build). I use only the **zero-parameter** closed-form filter as a reference value, so nothing is duplicated.
- **C5 boosting/cascades (deferred branch)**: its own gate condition ("stage 1 lands below skill 1.0 on a Class-A
  dataset") is not met by B1 and cannot be met by arms A/B by construction (ceiling skill 1.0). Arm C is what decides
  whether a cascade would even be in the right class. Deferred again, with that reason.
- **A separate 200-epoch `b1_replica` arm**: replaced by the within-run `alpha_b1_insample` leg (§2.2) — same contrast,
  perfectly paired, 123 GPU-min cheaper.
- **ADR 0007**: this is a **sweep, not screen-and-promote** — the same reconciliation s6-B2 recorded. The three arms
  are not competing variants for one slot; each is the primary evidence for a distinct pre-registered clause
  (C1 gate, C2 density, C3 attention-vs-local), so discarding one destroys a measurement. The cheap contract-tier
  screen is retained as the plumbing / no-harm gate only, and screen numbers stay in `build_notes` (never quoted).
- **Cost**: arm A panel ~125 min + arm B panel ~155 min (dense corrector stage) + arm C fisher_kpp ~35 min + screen
  ~15 min + 2 guard-contract legs ~4 min ~= **335 GPU-min ~= 5.6 GPU-h**, run as a 13-task array (max task ~45 min).
  2.7x B1's cost for three clauses, one continuity gate and four free reference values.

## 3. Proposal

### 3.1 Category / card type

- **category**: `mf_composition_repair_and_class_test` (gate-protocol repair + LF-context density + the
  attention-vs-closed-form head-to-head, on one substrate)
- **card_type**: `model` (three trained arms at smoke tier; the reference values are computed in-run and cost seconds)

### 3.2 Anchor reference

`"s4_hybrid_routing-B1"` — batch >= 2 re-targets the stream's current (provisional-single-seed) champion card, and
every contrast on this card is paired against B1's substrate. The **numeric** anchor for any panel-geomean statement
remains the certified `state/anchors/s4_hybrid_routing.json` value 6.703016262587087 (B1's 5.664889 is
single-seed and was explicitly NOT promoted, part 5 `anchor_action.updated: false`).

### 3.3 Motivation (verdict quoted verbatim)

Row (iii), the only `novel` surface: *"**(iii) The attention-vs-local head-to-head for the fidelity-gap defect on
regular sharp-interface grids (matched budget, same residual target)** | **`novel`** — as a measurement; and the prior
art is **hostile to attention** ... Nobody has run it: matched-parameter cross-attention corrector vs local/LSI
corrector on the same `hf - base` (or `hf - copylf`) target, on regular grids with sharp interfaces, at N_hf ≈ tens.
The prior predicts attention **loses**, and 2511.06294 supplies the mechanism (the nonlocal content-adaptive part is
not what works; slice/deslice pooling is). B1's fisher_kpp band-1 result is the only pro-attention datapoint in this
loop ... Either outcome closes the stream's class — the definition of genuine under program.md §1."*

Row (i), for the gate arm: *"**`preempted (cite)`** — the estimator is published for neural operators; only the
*diagnosis* is open ... **Claim ZERO mechanism novelty. The card is a protocol-defect measurement with a quantified
cost, and it should cite 2606.17460 as the published method that shares the hazard.**"* Row (ii), for the density arm:
*"**`preempted-but-MF-composition-open (cite)`** ... **A card must pre-register the skill-1.0 ceiling and the free
control that already reaches it** (`base + a*(copylf - base)`: 0.114384 vs 0.125893 on pfc, 0.202549 vs 0.226409 on
fisher_kpp, B1 F13) ... s4's version is defensible only as the **attention arm of the (iii) comparison**."*

### 3.4 Concrete config

Vendor `models_r1/fno_transolver_seq` from B1's build commit `4691d1fbaaa4dc9e0e6fbaf3bf607afef203404c`
(branch `round1/exp-s4_hybrid_routing-B1`; verify each file's sha256 against `git show <commit>:<path>`) into
`models_r1/fno_transolver_seq_b2`. `model.py` and `manifest.json` stay byte-identical except the manifest `name`.
All new behaviour is env-gated and **defaults to B1 semantics** (so the b1-style leg is bit-comparable). Edits:

1. **Gate base (arm A/B).** `_fit_alpha` gains a `base_score` argument. With `S4_GATE_BASE=oof` the line search scores
   `base_oof[val_idx] + a*corr` against `Y[val_idx]`; with `b1_insample` it scores `base_val_final + a*corr` (B1). The
   run always computes **both** alphas on the same split/correction and emits `alpha_oof`, `alpha_b1_insample`,
   `alpha_least_squares`, plus pre-stage-3 test nRMSE at `{0, alpha_b1_insample, alpha_oof, alpha_least_squares}`
   (`nrmse_at_alpha_*`; all four alphas fitted with **no test data**). The **scored** prediction uses the arm's
   `S4_GATE_BASE` alpha; stage 3 is triggered by that alpha exactly as in B1.
2. **Dense context.** `S4_CTX_POINTS=full|1024`; `full` sets `n_ctx = Hc*Wc` (and `gamma_init_for` follows
   automatically). `_corr_full_field` and `soft_interp` call sites chunk queries at `S4_CTX_QUERY_CHUNK=4096`
   when `n_ctx > 4096` (bit-neutral: chunking is a loop over disjoint query blocks).
3. **Arm C.** `S4_BASE_MODE=copylf` + `S4_TARGET=hf_minus_copylf`: base = `copylf_prediction(train|test)` imported
   read-only from `eval/panel_data.py` (record `panel_data_sha256`), asserted bit-equal to
   `eval/copylf_baselines.json` within 1e-9; target = `Y_hf - copylf_train` (no OOF folds needed — copy-LF is
   training-free, so stages 1/1b are skipped and only the corrector + gate train); FNO stages disabled.
4. **Sidecars (all arms; score-neutral).** `S4_LSI_SIDECAR=1` closed-form LSI reference (vendored with citation from
   `tools/defect_correction_learnability.py`, never imported, so the family `code_hash` stays complete);
   `S4_SCALAR_BLEND_SIDECAR=1` -> `ref_nrmse_scalar_blend` (`base + a*(copylf-base)`, `a` fitted on HF-train only);
   `S4_ANATOMY_SIDECAR=1` -> the B1 part-7 reporting requirement (correction RMS / residual RMS, `cosine(corr, hf-base)`,
   `cosine(corr, copylf-base)`, `cosine(corr, hf-copylf)`, and for arm C `cosine(corr, corr_LSI)` + 4-band energy
   fractions on edges 0,0.125,0.25,0.5,1.0); `gamma_init`/`gamma_final`; arm C also emits
   `nrmse_no_cross_branch` / `nrmse_no_self_branch` (inference-time branch ablation of the trained model).
   **Every sidecar nRMSE is computed by importing `round1/eval/nrmse.py`** (read-only, sha256 recorded) — no
   hand-rolled metric anywhere; the SCORED number remains `score_panel.py`'s.
5. **Resume.** `last.pt` key extended to `(epochs_target, grid, recipe_hash, arm)`; per-arm
   `ROUND1_EVAL_RESULTS` (exported, not via `--env`) so `score_panel._run_one`'s
   `(family_dir.name, dataset, epochs, seed)`-derived paths cannot collide across arms.

**Arms** (seed 0, 200 epochs): **A `gate_repair`** = panel, `S4_GATE_BASE=oof`, `S4_CTX_POINTS=1024`;
**B `gate_repair_dense`** = panel, `S4_GATE_BASE=oof`, `S4_CTX_POINTS=full`;
**C `attn_gap_fkpp`** = `sharp__fisher_kpp_2d`, `S4_BASE_MODE=copylf`, `S4_TARGET=hf_minus_copylf`,
`S4_CTX_POINTS=full`. Guard set at contract tier for A and B (program.md §2.3). One contract-tier screen
(2 epochs, all arms, panel+guard) as the plumbing/no-harm gate.

**Validity gates.** V1: arm A's `nrmse_at_alpha_b1_insample` (pre-stage-3) must reproduce B1's shipped seed-0 test
nRMSE within 2% on the four alpha=0 datasets (helmholtz 6.543507222018085, ifc_poisson 0.05563486139090377,
allen_cahn 0.26355002277981737, cahn_hilliard 0.48762843911552667) — a miss is ALGO, fix before reading any contrast.
V2: the in-run LSI reference reproduces s6-B1 F6 within 2% (fisher_kpp 0.007695081137159533, pfc 0.0006124684737243416,
allen_cahn 0.0008319633678339519, cahn_hilliard 0.03856875162347986). V3: arm B == arm A bit-exactly on
`ext__helmholtz_2d` and `ifc_poisson` (dense is a no-op at 100% coverage). V4: arm C with alpha=0 is copy-LF exactly
(0.06263229669603956, delta <= 1e-9).

### 3.5 Recipe

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

### 3.6 Expected outcome (all `provisional-single-seed`, ADR 0004)

**Floor convention, stated once**: where an arm sits at the anchor's skill scale I use the **absolute** certified
`min_claimable_effect`; where the absolute floor exceeds the arm's whole skill (arm C at skill ~0.12 vs a 0.4177
floor) it is vacuous, so I use the **relative** form (10%), justified by the certified 3-seed *relative* spreads
(fisher_kpp 2.197%, cahn_hilliard 3.467%, pfc 0.718%, allen_cahn 0.087%) — 10% relative is 4.5x the relevant one.

- **C1, arm A vs its own b1-style leg (`sharp__cahn_hilliard`)**: `alpha_oof` in [0.75, 1.25] (F2's test optimum
  1.1027 to 0.9%); test nRMSE 0.48762844 -> **<= 0.30681 (skill <= 3.5)**, predicted ~0.27720 (skill 3.1622, F12).
  Claim bar = 10% relative = 0.43886560 nRMSE / 0.5562725 skill units, which **exceeds** the certified floor
  0.5533466 (1.005x); the predicted move is 2.40 skill units = **4.3x the floor**.
- **C1 pre-registered downside (`pfc`)**: alpha may rise from 0.2509 toward `alpha_ls` 0.9944 and cost up to
  **8.47x** (skill 3.2817 -> ~27.8, F13). Reported as the second price of the two-sided bias, not hidden. Even then the
  panel geomean is **7.35 < 10.0545** (not cratered). No panel-geomean claim is made for arm A (F12: -0.5275 is inside
  the 0.884 floor). fisher_kpp expected 3.6145 -> ~3.5685 (-1.3%, inside its floor -> report-only); allen_cahn and
  helmholtz have collapsed correctors (RMS ratios 0.00063 / 0.0076) so alpha stays ~0 and they are unchanged;
  ifc_poisson unchanged (correction orthogonal, cosine 0.138) -> watch item.
- **C2, arm B vs arm A**: coverage 6.25% -> 100% (pfc 25% -> 100%). Mechanism prediction: `cosine(corr, copylf-base)`
  rises to >= 0.9 with R^2 >= 0.9 on all four, and skills move **toward but not through 1.0**. Claim bar per dataset =
  the absolute floor: pfc >= 1.1511 skill units (skill <= 2.13), fisher_kpp >= 0.41774 (skill <= 3.197),
  cahn_hilliard >= 0.55335 — required on **>= 2 of 3** — **and** the arm must beat `ref_nrmse_scalar_blend`
  (B1 F13: pfc 0.114384 / skill 2.554, fisher_kpp 0.202549 / skill 3.234). Panel geomean predicted **2.5-4.5**
  (vs anchor 6.703, floor 0.884 = 13.2% relative), but explicitly labelled *attainment toward the skill-1.0 ceiling*,
  i.e. a better copy-LF re-derivation, **not** fidelity-gap information: `cosine(corr, hf-copylf)` is predicted to stay
  <= 0.1. **No arm here is predicted to reach skill < 1 on any dataset.** allen_cahn is wide open (its corrector may
  un-collapse: if RMS ratio > 0.1, skill should fall below 10) -> reported, not claimed.
- **C3, arm C vs the in-run LSI reference (`sharp__fisher_kpp_2d`)**: predicted attention **loses** —
  nRMSE **0.010-0.045** (skill 0.16-0.72) against the reference 0.0076951 (skill 0.122861) and s6-B1's trained local
  corrector 0.0059583 (skill 0.0951, cross-stream reference, not re-run). Keep-attention bar:
  nRMSE **<= 0.0069256** (skill <= 0.110575, 10% relative = 4.5x the 2.197% seed spread) **and**
  `cosine(corr, hf-copylf) >= 0.3` with RMS ratio in [0.5, 2.0]. No-harm floor by construction: alpha=0 gives copy-LF
  exactly (0.06263230, skill 1.0), so arm C cannot regress past copy-LF. Mechanism diagnostics decide the
  interpretation of a loss: if `gamma_final` >> `gamma_init` and `nrmse_no_cross_branch` ~= the scored value, the
  nonlocal content-adaptive path is inert (arXiv:2511.06294's prediction); if instead the correction is band-limited
  relative to `corr_LSI`, the diagnosis is an input-path defect (one interpolated scalar cannot carry a compact
  stencil), and the recommendation to the round differs accordingly.
- Guard set: expected clean (B1's contract-tier guard had 2/3 below copy-LF and was 2-7x better than the only peer);
  any ratio > 2x vs the recorded reference is flagged, not auto-rejected.

### 3.7 Expected falsification (one sentence)

If (C1) the base-out-of-sample gate fails to improve `sharp__cahn_hilliard` by more than 10% relative
(nRMSE 0.48762844 -> <= 0.43886560, i.e. >= 0.5562725 skill units, above the certified floor 0.5533466) against the
paired in-sample-gate leg of the same run, AND (C2) the dense-LF arm fails to beat the sparse arm by at least each
dataset's `min_claimable_effect` on >= 2 of {pfc 1.1511, fisher_kpp 0.41774, cahn_hilliard 0.55335} skill units or
fails to beat the in-run one-scalar `base + a*(copylf - base)` control, AND (C3) the attention corrector on the
`hf - copylf` target fails to beat the in-run zero-parameter LSI reference on `sharp__fisher_kpp_2d` by more than 10%
relative (0.00769508 -> <= 0.00692557), then no remaining lever of the alpha-gated **attention**-corrector class —
not the gate protocol, not context density, not the residual target — clears this round's noise floor on the sharp
panel, and s4's recommendation is to retire the attention corrector in favour of the local/closed-form class that s6
owns.

## 4. Reopen candidates resolved

| candidate | verdict | reason |
|---|---|---|
| (none formally: `s4_hybrid_routing-B1` is `complete`, `reopen_candidate: false`) | n/a | verified by reading the card's `status` / `reopen_candidate` fields and `ls experiment_cards/s4_hybrid_routing/` (batch_1 only) |
| parked branch: LF-conditioned spatially-resolved routing (B1 part 7 REFUSED, websearch D2) | **DROP** | priced on this exact artifact: per-sample oracle <= 5.33%, honest per-pixel -1.31%/+6.18%/+3.54%, in-sample pixel upper bound <= 4.40% — all inside every sharp floor (F11); s6's `trust_gate_headroom.py` agrees from the opposite base; verdict §5 forbids resurrecting it. No eased condition could make it claimable, so it is dropped, not deferred. |
| parked branch: C5 boosting/cascades (B1 part 7 DEFERRED) | **DEFER again** | its own gate ("stage 1 below skill 1.0 on a Class-A dataset") is unmet and unmeetable by arms A/B (ceiling skill 1.0, F6). Arm C tests whether a cascade of *attention* stages is even in the right class; if C3 fails, C5 should be dropped rather than deferred, and this card's part 7 should say so. |
| B1 reporting requirement (RMS ratio + cosines beside every gate value) | **CARRIED IN** | `S4_ANATOMY_SIDECAR=1` on all three arms, per verdict §6. |

## 5. Immutables self-check (positive evidence, 10/10)

1. **Data read-only.** No arm writes under `factory_root/data/**` or any dataset dir; all reads go through
   `common.mffp.load_mf_dataset` (arms A/B, as B1) and `eval/panel_data.py::load_split`/`copylf_prediction`
   (arm C, read-only import). N_hf is untouched (400 on the sharp sets, 5 on ifc_poisson — measured, not assumed).
   "Dense context" enlarges only the *subsample* of the dataset's own finest **real coarse-solve** LF field
   (`ctx_fid = max(lf_fids)`, `S4_CTX_POINTS=full` -> `n_ctx = Hc*Wc`); no HF field is ever downsampled to make LF,
   and arm C's base is the eval layer's own copy-LF, asserted equal to `eval/copylf_baselines.json` within 1e-9.
2. **Panel + guard fixed.** Arms A/B run `--datasets panel` (the 6 names from `project.yaml`); guard legs run
   `--datasets guard` (`heat_local`, `fluid`, `sharp__sod_1d`). Arm C runs one panel member as a per-dataset
   contrast and makes no geomean claim — a subset, not a redefinition.
3. **Eval layer / spec untouched.** All code lives in `worktrees/s4_hybrid_routing/B2/models_r1/fno_transolver_seq_b2/`
   plus `scripts/`; `round1/eval/`, `project.yaml`, `program.md`, `docs/adr/`, `subagents/` and `tools/` are read-only
   (`eval/panel_data.py` and `eval/nrmse.py` are *imported* and their sha256 recorded — the same pattern
   `s6_local-B1` shipped through code review).
4. **One nRMSE definition.** Every scored number comes from `eval/score_panel.py` -> `eval/nrmse.py`
   (`nrmse_def_hash` d3d0ade9...c035850 must match B1's, which the analyzer checks). Every sidecar/reference value
   (`ref_nrmse_LSI`, `ref_nrmse_scalar_blend`, `nrmse_at_alpha_*`, `nrmse_no_*_branch`) is computed by importing that
   same module — the recipe mandates it — so no metric is hand-rolled and none is compared across hashes.
5. **Contract CLI fixed.** `smoke_eval.py` keeps exactly the six args (`--dataset_dir --dataset_name --epochs --out
   --ckpt_dir --seed`); every new knob is an `S4_*` env var listed in the recipe `env` and therefore inside
   `code_hash(family_dir, env)` (`score_panel.py:51-73`) — the same mechanism B1's `MFFP_CTX_SOURCE` used and the
   reviewer accepted.
6. **Seeds / tier epochs fixed.** `seeds: [0]` (ADR 0004), 200 epochs for all three scored arms, 2 epochs for the
   screen and the guard legs; `scripts/01_train_eval.sh` stays seed-parameterized and `submit_seeds_2_3.sh` is written
   but not submitted (end-of-round top-3 pass only). No full-tier run is proposed.
7. **Guarded factory surfaces untouched.** `mf_field/akash/**` is only *imported* (`_find_akash()` upward search,
   byte-unchanged from B1, verified in `state/s4_hybrid_routing/review_B1.md` §3.4); no file under
   `factory_root/{eval,baselines,references,scripts,data}/` or `factory.md` is read-written. The vendored family is a
   NEW directory under the worktree's `models_r1/`, so nothing existing is renamed or deleted.
8. **Checkpoint resume.** B1's `last.pt` save/load (`smoke_eval.py:321-337`, `:448-454`) is kept and its key extended
   to `(epochs_target, grid, recipe_hash, arm)`; per-arm `ROUND1_EVAL_RESULTS` gives each arm its own
   `ckpt_<dataset>_e200_s0/last.pt`, so a preempted arm resumes into its own state and cannot load another arm's.
   Resume was empirically exercised in B1 (reviewer §3.6: "resume implemented AND empirically verified").
9. **Thresholds vs the noise floor** (numbers quoted): C1 bar 0.5562725 skill units **> floor 0.5533466**
   (cahn_hilliard); C2 bars are the floors themselves (pfc **1.1511001**, fisher_kpp **0.4177355**,
   cahn_hilliard **0.5533466** skill units); C3 bar is 10% relative on a dataset whose certified 3-seed relative
   spread is **2.197%** (0.09178909/4.17735500), i.e. 4.5x — the absolute floor 0.4177355 is vacuous there because
   the arm's whole skill is ~0.12, and this substitution is stated in the card (s6-B2 precedent).
   `ext__helmholtz_2d` (floor 9.694961 = 70.2% relative) is **report-only, never claimed**; `ifc_poisson`
   (floor 0.2399076) is a watch item with no claim.
10. **Not a pre-falsified lever.** None of the three §5 levers appears: no WNO backbone (the backbones are the same
    FNO-FiLM + Transolver as B1), no LF low-mode freezing (no spectral mask anywhere), no diffusion prior. Nearest
    *in-round* falsifications and the differences: (a) B1 F13 falsified "use `alpha_ls`, drop the line search" — this
    card **keeps** the shrinkage line search (`S4_KEEP_LINESEARCH_SHRINKAGE=1`, candidate set including 0 unchanged)
    and changes only the base the search scores against; (b) B1 F11 refuted spatially-resolved routing — no arm here
    has any gate finer than one global scalar; (c) verdict (i) says the *estimator* is published (2606.17460) —
    the card claims **zero** mechanism novelty for arms A/B and is written as a measurement, exactly as instructed.

## 6. Status

- Slot **covered** (one proposal, three arms, three pre-registered contrasts, four validity gates).
- Reopen candidates: none formal; two parked branches resolved (routing DROP, C5 DEFER-again).
- Immutables self-check: **pass (10/10)**; two items needed design decisions taken during this pass rather than
  after it — item 4 (all sidecar metrics must import `eval/nrmse.py`) and item 9 (the absolute-vs-relative floor
  convention for arm C) — both are written into the recipe and the expected-outcome section, not asserted post hoc.
- No second iteration required.
