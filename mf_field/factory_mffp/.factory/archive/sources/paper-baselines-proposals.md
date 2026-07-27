---
name: paper-baselines-proposals
description: Human-side TODO — append proposed splits to baselines/paper_baselines.json. IFC paper m=1 numbers — Poisson 0.036, Heat 0.074. baselines/ is a fixed surface; Researcher cannot edit.
metadata:
  type: reference
tags:
  - factory
  - source
  - human-action
  - cycle-001
  - blocked
source: factory-archivist
date: 2026-05-15
cycle: "001"
project: factory_mffp
---

# Paper-Baseline Proposals — Human Action Required

`baselines/` is a **fixed surface** per `.factory/config.json` and `factory.md`. The Researcher cannot edit. The CEO/user must commit these manually.

Until this happens, `vs_paper.beats_paper` is forced to `false` for `ifc_heat` and `ifc_poisson` regardless of model quality, and `n_datasets_beating_paper` is stuck at 0.

## Proposed entries

From [[li2022ifc]] p.9 verbatim text: "The nRMSE of IFC-ODE2 at m=1 and m=2.14 is 0.036 vs. 0.018 and 0.074 vs. 0.061, for Poisson's and Heat equations, respectively."

```json
"ifc_heat": {
  "source": "li2022ifc",
  "metric": "nRMSE",
  "splits": {
    "test_l4": {
      "paper": 0.074,
      "paper_std": 0.005,
      "_method": "IFC-ODE2 at m=1, K=20",
      "_note": "From li2022ifc p.9 text. IFC-GPODE estimated ~0.04 from Fig 4(b) but explicit number not stated; use 0.074 (ODE2) as the conservative bar."
    }
  }
},
"ifc_poisson": {
  "source": "li2022ifc",
  "metric": "nRMSE",
  "splits": {
    "test_l4": {
      "paper": 0.036,
      "paper_std": 0.005,
      "_method": "IFC-ODE2 at m=1, K=20",
      "_note": "From li2022ifc p.9 text. IFC-GPODE estimated ~0.03 from Fig 4(a). Use 0.036 (ODE2) as the conservative bar."
    }
  }
}
```

## Important caveats

- **Split key may need adjustment**: `eval/score.py` and `references/v9_baseline/smoke_eval.py` likely use the key `"test"` (not `"test_l4"`). Verify by grepping `splits.get("test"` in `eval/score.py` before committing.
- **`paper_std=0.005` is estimated from Fig. 1 error bars**, not explicit text. Must be flagged "estimated from Fig. 1 error bars" in any commit message.
- A second-pass extrapolation entry (m=2.14, mesh 128×128) could be added later, but no current dataset under `data/` ships that split.

## Related

- [[li2022ifc]] — source paper for these numbers.
- [[papers-summary-csv-state]] — sibling human-side TODO (papers_summary.csv does not exist either).
- [[cycle-001-failure-diagnosis]] — F3 is the meta-blocker these numbers unblock.
