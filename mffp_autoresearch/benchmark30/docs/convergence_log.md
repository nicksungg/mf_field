# benchmark_30 campaign — convergence log

Pinned base for all reviews: `BASE=83a547e`.
Worktree: `mffp_autoresearch/benchmark30/worktree`, branch `bench30-campaign`.

## Spec convergence

### Round 1 — Codex Terra/high, 2026-08-12

Reviewed: spec.md at `329e643`.
Verdict: needs-attention. Scorecard: 3 findings (2 high, 1 medium, 0 low).

| # | Sev | Finding | Reproduction | Disposition |
| --- | --- | --- | --- | --- |
| r1-1 | high | `score_panel.py` hard-loads `round2/eval/copylf_baselines.json` and raises for unlisted datasets; env redirection does not cover it | CONFIRMED (score_panel.py:47, 198–202); also found `COPYLF_DEF_HASH` = sha256(panel_data.py) at panel_data.py:219, so in-place extension would invalidate round-2/3 state | FIXED in spec `04debf8`: D3 rewritten — vendored scorer with two named seam deltas + byte-identity guard; campaign copy-LF baseline builder added (G2, §6) |
| r1-2 | high | Scorer cache key (`code_hash\|ds\|epochs\|seed`) and film checkpoint (`epochs_target, grid`) carry no dataset-content term → stale reuse on data change | CONFIRMED (score_panel.py:203; film smoke_eval.py:156, 172–173; film writes last.pt only after both stages → whole-run resume granularity) | FIXED in spec `04debf8`: new D12 — content-addressed `rev-<manifest_hash8>/` roots for results/cache/ckpts/logs + aggregator re-hash rejection |
| r1-3 | medium | era5 batch/grad-accum accommodation (old D7/D11) contradicts D5 verbatim-knob rule | CONFIRMED as internal contradiction; measured era5 = 721x1440 and r3s2 `WORK_CAP=256` RAISES (smoke_eval.py:650–654) → no accommodation is even possible | FIXED in spec `04debf8`: D11 rewritten — no accommodations for any dataset; era5 predeclared unsupported-by-frozen-family for r3s2; film attempts it as-is |

All three dispositions are FIXED (none adjudicated-reject).

### Round 2 — Codex Terra/high, 2026-08-12

Reviewed: spec.md at `2f73b10`.
Verdict: needs-attention. Scorecard: 3 findings (0 high, 2 medium, 1 low); r1-1 and r1-3 confirmed resolved; r1-2's strategy confirmed with a coverage gap (→ r2-2).

| # | Sev | Finding | Reproduction | Disposition |
| --- | --- | --- | --- | --- |
| r2-1 | medium | Whole-registry equality guard impossible: frozen sources already diverge on pfc (family PERIODIC_NODE vs round-2 SPECTRAL_RUNG override) | CONFIRMED — divergence independently observed in this session's own reads of both files | FIXED in spec `60535a7`: guard scoped to newly classified benchmark_30 IDs; pre-existing pfc difference (ADR r3-0005) preserved and exempted via the seam manifest |
| r2-2 | medium | `manifest_hash` did not cover the stripped views the scorer actually consumes | CONFIRMED as a definition gap | FIXED in spec `60535a7`: D12 hash now covers source + stripped-view content hashes; aggregator re-hashes both; G0 wording notes the hash seals at G1 |
| r2-3 | low | "two named seam deltas" vs three listed | CONFIRMED | FIXED in spec `60535a7`: count corrected everywhere |

### Round 3 — Terra/high (spec confirm + plan review) ∥ Luna/low (traceability + contradiction), 2026-08-12

Reviewed: spec.md + plan.md at `a29098f`.
Terra: needs-attention, 4 findings (2 high, 2 medium); r2-1/r2-2/r2-3 all CONFIRMED resolved — the spec itself is clean.
Luna: needs-attention, 8 findings (4 medium, 4 low); the two Terra highs found independently (cross-validation).
All findings target the PLAN (drafted against the pre-round-2 spec).

| # | Sev | Finding | Disposition (all in plan `fd0a13c`) |
| --- | --- | --- | --- |
| r3-1 (=L1) | high | A2 restored the pre-r2-2 manifest-hash formula; nothing sealed stripped-view hashes | FIXED: A2 writes a provisional unsealed source lock; A6 seals the D12 hash after the stripped build; downstream refuses unsealed; mutation test covers both byte classes |
| r3-2 (=L2) | high | A5 asserted whole-registry equality, which spec D4 forbids | FIXED: guard scoped to newly classified IDs; pfc divergence (ADR r3-0005) exempted via seam manifest |
| r3-3 | medium | Gate→tier launch prerequisites undefined (would deadlock or under-enforce) | FIXED: explicit matrix — smoke needs G0–G2; full seed 0 needs G3; seeds 1–2 need G4; Phase B writes immutable gate evidence; per-combination refusal tests |
| r3-4 | medium | A9 didn't pin the D9 aggregation ORDER (per-seed panel geomean → mean/[min,max]) | FIXED: exact order stated; non-symmetric fixture pins it; A1-arm-only reporting test added |
| L3 | medium | D5 verbatim-recipe carried by no task | FIXED: A1 `recipe_env` copied verbatim from the B2 card + byte-equality test against the card file |
| L4 | medium | Phase B "deliver D-summary" lacked the D13 payload and notification triggers | FIXED: payload + triggers enumerated in Phase B step 4 |
| L5 | low | Atomic-commit/red-transcript process untraced to spec | FIXED by labeling: marked NON-NORMATIVE process from the governing workflow |
| L6 | low | "Who implements" section orphaned from spec | FIXED by labeling: marked NON-NORMATIVE process |
| L7 | low | config.yaml necessity unanswered | FIXED: necessity note added (round-2 project.yaml is frozen round state; cannot carry dataset_dir/campaign roots/recipe block) |
| L8 | low | run_gates.py/gates.json necessity unanswered | FIXED: necessity note added (round-3 gate machinery is round-scoped card state with a different protocol) |

### Round 4 — pending (confirming round, Terra, both docs)
