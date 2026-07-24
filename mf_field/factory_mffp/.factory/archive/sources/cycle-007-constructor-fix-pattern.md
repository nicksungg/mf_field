---
name: cycle-007-constructor-fix-pattern
description: Cross-cycle pattern — cycle-007 Researcher confirms the fno_coregionalization crash is a pure wrapper-level mismatch; inner classes (SpectralConv2d, FNOBlock) already accept (modes_h, modes_w); the dirty model.py edit that aligned the outer constructor was lost in a git reset
metadata:
  type: project
tags:
  - factory
  - pattern
  - cycle-007
  - committed-tree-broken
  - git-reset-pitfall
source: factory-archivist
date: 2026-06-02
cycle: cycle-007
---

# Cycle-007 Constructor-Fix Pattern

Cycle-007's Researcher confirms the dominant cycle-007 failure
(`COMMITTED_TREE_BROKEN` on `fno_coregionalization`) is **a pure
wrapper-level mismatch**. The repair is mechanical (≤15-LOC edit), not
an architectural redesign.

## Why this is a pattern, not a one-off

This is the **second** time in the project's recent history that a dirty,
load-bearing edit to a `model.py` has been lost while sibling files
(`smoke_eval.py`, inner classes, manifest) retained their updated state.
See [[cycle-005-summary]] for the cycle-005→006 instance where the
H2 schedule landed in `smoke_eval.py` (commit `be36cba`) but the matching
`model.py` constructor signature was never committed and was subsequently
overwritten by a hard reset.

**Trigger conditions for this pattern:**

1. Multi-file change where the dirty tree had **smoke harness + inner
   classes + outer constructor** all modified.
2. Operator stages and commits only some of those files
   (`git add models/fno_coregionalization/smoke_eval.py` rather than
   `git add models/fno_coregionalization/`).
3. Later `git reset --hard` or branch-switch wipes the unstaged file.
4. Tree compiles but **crashes at construction** because the inner
   classes still accept `(modes_h, modes_w)` while the outer wrapper
   still passes scalar `modes`.

## What's already correct in the committed tree

Cycle-007 Researcher re-verified, against the current `experiment/7@be36cba` tree:

- `models/fno_coregionalization/model.py:28-79` — **`SpectralConv2d` and
  `FNOBlock` ALREADY accept `(modes_h, modes_w)`**. These inner classes
  carry the correct anisotropic signature from an earlier (committed)
  pass.
- `models/fno_coregionalization/smoke_eval.py:265-273` — the call site
  is already correct: `FNOCoregionalization(... modes_h=modes_h,
  modes_w=modes_w, grid=grid, ...)`.
- `models/fno_coregionalization/smoke_eval.py:64-411` — the full
  cycle-005 H2 two-stage schedule (LF warm-up + joint fine-tune, fresh
  `Adam` + fresh `CosineAnnealingLR` per stage) is **intact**.
- `models/fno_coregionalization/smoke_eval.py:304-318` — resume guard
  already checks `grid` tuple identity, so the constructor-fix's
  `grid_size: int → grid: tuple` swap is **resume-compatible**.

## What's broken: only the outer wrapper

- `models/fno_coregionalization/model.py:83-128` — outer
  `FNOCoregionalization.__init__` **still declares** `modes: int,
  grid_size: int, b_hidden: int` (single isotropic `modes` and scalar
  `grid_size`).
- `models/fno_coregionalization/model.py:100` — outer constructor passes
  scalar `modes, modes` into the inner `FNOBlock`, even though the inner
  block accepts split `(modes_h, modes_w)` happily.
- `forward()` (lines 143-161) — `H = W = self.grid_size` should be
  `H, W = self.grid`.

## Fix shape (≤15-LOC edit)

Mirror `mf_fno_transfer_bar/model.py:62-94` (sibling pattern, verified
correct). Outer `FNOCoregionalization.__init__` takes
`modes_h, modes_w, grid: tuple[int, int]`; build `coord_grid` from
`grid = (H, W)`; propagate `(modes_h, modes_w)` into the inner
`FNOBlock`s. The full patch:

```python
class FNOCoregionalization(nn.Module):
    def __init__(
        self,
        cond_dim: int,
        hidden_channels: int = 64,
        K: int = 10,
        n_blocks: int = 4,
        modes_h: int = 12,
        modes_w: int = 12,
        grid: tuple = (64, 64),
        b_hidden: int = 64,
    ):
        super().__init__()
        self.cond_dim = cond_dim
        self.K = K
        self.grid = (int(grid[0]), int(grid[1]))

        self.lift = nn.Conv2d(cond_dim + 2, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            FNOBlock(hidden_channels, modes_h, modes_w) for _ in range(n_blocks)
        )
        self.proj = nn.Sequential(
            nn.Conv2d(hidden_channels, hidden_channels, 1), nn.GELU(),
            nn.Conv2d(hidden_channels, K, 1),
        )
        self.B = nn.Sequential(
            nn.Linear(2, b_hidden), nn.GELU(),
            nn.Linear(b_hidden, b_hidden), nn.GELU(),
            nn.Linear(b_hidden, K),
        )

        self.register_buffer("m_keys", torch.zeros(0, dtype=torch.float32))
        self.register_buffer("scalers", torch.zeros(0, dtype=torch.float32))

        H, W = self.grid
        ys = torch.linspace(-1.0, 1.0, H)
        xs = torch.linspace(-1.0, 1.0, W)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        self.register_buffer("coord_grid", torch.stack([gy, gx], dim=0).unsqueeze(0))
```

And in `forward()`: replace `H = W = self.grid_size` with
`H, W = self.grid`. No other changes needed.

**Do not** add a `modes=` backwards-compat kwarg. All call sites live
inside `models/fno_coregionalization/`; the smoke harness is the only
consumer.

## Cache implications

- Cycle-005 cached checkpoints (hashes `9528aeef4a5a`, `9be21a0f9ce9`)
  are on disk but **no longer key-match** the current source hash.
- `SpectralConv2d` weight tensor shapes do **not** change under the fix
  (the inner classes already use `(modes_h, modes_w)`), so a
  `load_state_dict` from the stale checkpoint **may** still succeed —
  expect ~30s of fresh training on H100 smoke if state_dict keys
  mismatch. Well within budget.

## How to avoid this pattern in future cycles

[[dirty-tree-staging]] (auto-memory) already captures the lesson:
`git add <file>` commits pre-existing dirty changes too, but conversely,
`git add <subset_of_files>` **misses** dirty edits in sibling files. For
multi-file architectural changes, **always run
`git add models/<family>/` (the directory)** to stage every modified file
inside a family at once, then explicitly review `git status` for any
remaining unstaged files before resetting or switching branches.

## Strategic prioritization (CEO, cycle-007)

- **TOP-1 is the load-bearing single experiment.** Projection: composite
  `0.039578 → ~0.0304` by reinstating the cycle-005 cached heat winner
  @ 0.01551. Already at-or-near the bar `0.0274`.
- **Do NOT bundle Top-2 recipe changes with Top-1** — would confound
  the regression test against the cached 0.01551 number.
- **Defer Top-3 (LF→HF add-on / new family).** With Top-1 alone projected
  to drop composite to ~0.0304 (near the bar), the case for a brand-new
  family is weaker.
- **Hypothesis count target: 1 (Top-1 alone), or 2 (Top-1 + Top-2
  decoupled).** Three hypotheses would over-extend the cycle budget.

## Related notes

- [[anisotropic-spectral-modes-fno]] — literature backing for the
  `(modes_h, modes_w)` abstraction.
- [[lf-hf-pretrain-fraction-survey)]] — schedule survey; the cycle-005
  H2 recipe @ `pretrain_frac=0.25` is the one we are reattaching.
- [[per-dataset-recipes-mf-field]] — Top-2 dispatch (separate
  hypothesis; do not bundle).
- [[failure-analysis-cycle-007]] — failure-analyst's diagnosis
  (`COMMITTED_TREE_BROKEN`, single-fix delta `−0.0092` composite).
- [[cycle-005-summary]] / [[cycle-006-summary]] — prior cycles where
  the dirty-edit / hard-reset interaction first surfaced.
