# summary_so_far — `r2s3_lf_train_signal`, batch 1

## Where the stream starts

No prior cards: `mffp_autoresearch/round2/experiment_cards/r2s3_lf_train_signal/`
is empty and `websearches/r2s3_lf_train_signal/` has no `batch_0`. This is the
stream's first search loop; there is no `batch_{N-1}/report.md` to inherit.

Launch anchor (`state/anchors/r2s3_lf_train_signal.json`, certified
2026-07-31, `provisional: false`): **best-floor panel geomean skill 23.06**,
per dataset — helmholtz 3.34 (zero), pfc 59.81 (mean), allen_cahn 269.20 (NN),
fisher_kpp 11.99 (mean), cahn_hilliard 23.18 (NN), ifc_poisson 10.05 (NN).
Any trained model must beat those; skill < 1 vs copy-LF is the headline claim
(program.md §1, §2.3).

`state/noise_floor.json` is PROVISIONAL (`_source: round1-batch0-rescaled`,
from LF-consuming families) — per §4.3 falsification clauses are judged
directly until r2s4-B1 certifies a condition→HF 3-seed spread. Its scale is
still informative: recorded seed spreads are 0.13–10.68 *skill units*, so
sub-unit skill deltas on the sharp panel are not distinguishable from noise yet.

## Stream-specific constraints already known (program.md §12.3)

1. **Mandatory declared baseline**: `mf_fno_transfer_film` IS
   LF-pretrain→HF-finetune from the condition vector, verified to run
   unmodified on the stripped view. Any pretrain/finetune proposal must score
   it as an arm or state precisely how it differs, else reviewer FAIL (§5.10
   rebadge check).
2. **Nested-ladder degeneracy** (r1 report §6): LF-as-signal designs must say
   what the LF rungs contain that the HF rung does not.
3. `revin_lf` two-scaler finding (r1 s5): cross-fidelity normalization
   transfer is solved — reuse, don't rediscover.
4. Existing 400 aligned samples only (§5.11); no new HF data, no LF-only pools.

## What I verified on disk about the LF signal (load-bearing)

Read directly from `${ROUND_ROOT}/stripped_data/`:

- **Sharp datasets are fully nested**: `sharp__cahn_hilliard/train_l{1,2,3}.npz`
  all have `x` of shape (400, 19) — the *same* 400 condition vectors — with `y`
  at 4096 / 16384 / 65536 cells. LF therefore adds **zero parameter-space
  coverage**; the only extra information is a spectrally-truncated / coarse view
  of the same solutions (a low-pass curriculum signal, resolution-consistency
  signal, or extra gradient samples — not new conditions).
- **ifc_poisson is NOT nested**: fidelity 8/16/32/64 hold 100/50/20/5 samples,
  and none of the 5 HF condition rows (nor any of the 20 f32 rows) appear in the
  f8 set. LF here supplies **170 additional, disjoint parameter-space samples**
  against 5 HF ones — a 35x coverage multiplier. This is the panel's one dataset
  where LF-as-training-signal has an unambiguous information argument.

That asymmetry should drive the batch-1 design: the mechanism that helps on
ifc_poisson (coverage/regularization) is not the mechanism that could help on
the sharp panel (spectral curriculum / multi-resolution consistency).

## Prior in-repo literature (cite, don't re-derive)

`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` §4.2–4.3 already surveys
this space: F-Adapter frequency-banded PEFT on a frozen LF-pretrained FNO
(arXiv:2509.23173), Multi-Level Monte Carlo training of neural operators as a
single-loop replacement for pretrain→finetune (arXiv:2505.12940), data-efficient
MF-DeepONet freezing the LF branch/trunk and training only a merge head
(arXiv:2503.17941), FilDeep joint LF+HF fidelity-aware training positioned
against pretrain-then-finetune (arXiv:2601.10031), denoising LF pretraining
(DPOT, arXiv:2403.03542), self-supervised LF pretext tasks (MOFS,
arXiv:2508.01211).
`docs/reports/MF_Sharp_HighFreq_Report.md` §2.3 notes existing MF operator work
is "essentially all transfer learning (Tang, arXiv:2308.09113) or composite
linear+nonlinear correction nets (Howard, arXiv:2204.09157)".

**Implication for this loop**: the generic pretrain→finetune and joint-MF-loss
slots look occupied. The search must therefore target (a) *distillation from an
LF-consuming teacher into a condition-only student* — the LUPI framing — and
(b) *coarse-resolution-as-auxiliary-target under a fully nested ladder*, which
is where the prior art is least obviously settled.

## Open questions entering the loop

- Is condition-only student <- LF-consuming teacher distillation published for
  neural-operator / PDE surrogates? (LUPI / privileged information framing.)
- Is multi-resolution auxiliary supervision from a *nested* ladder known to help
  or provably degenerate?
- Does anyone report matched with/without-LF ablations at N_hf ~ 5?
