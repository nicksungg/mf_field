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

### Round 2 — pending
