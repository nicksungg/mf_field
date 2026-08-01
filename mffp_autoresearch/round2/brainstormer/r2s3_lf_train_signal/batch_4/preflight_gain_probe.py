"""Pre-flight grounding for r2s3-B4 brainstorm: can a train-fitted LF-free
global gain head absorb any of the +-LF effect?  READ-ONLY, dumps only."""
import sys, json, numpy as np
from pathlib import Path

R2 = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2")
sys.path.insert(0, str(R2 / "eval"))
import panel_data
from nrmse import nrmse as NRMSE

OUT = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B3/eval")
FAM = "r2s3_coverage_panel"

REF = {  # corrected copy-LF denominators (program.md 2.3)
    "ifc_poisson": 0.036,
    "sharp__cahn_hilliard": 0.041803,
    "sharp__allen_cahn_2d": 0.001781,
    "sharp__fisher_kpp_2d": 0.021450,
    "sharp__phase_field_crystal_2d": 0.007381,
    "ext__helmholtz_2d": 0.299033,
}

CASES = {
    "sharp__cahn_hilliard": [("ch_A0_d0", "ch_A1_d0"), ("ch_A0_d1", "ch_A1_d1"), ("ch_A0_d2", "ch_A1_d2")],
    "sharp__allen_cahn_2d": [("ac_A0_d0", "ac_A1_d0"), ("ac_A0_d1", "ac_A1_d1"), ("ac_A0_d2", "ac_A1_d2")],
    "ifc_poisson": [("ifc_A0", "ifc_A1")],
    "sharp__fisher_kpp_2d": [("fk_A0_d0", "fk_A1_d0")],
    "sharp__phase_field_crystal_2d": [("pfc_A0_d0", "pfc_A1_d0")],
}


def load(tag, ds):
    p = OUT / f"results_{tag}" / FAM / f"{ds}_e200_s0_preds.npz"
    return np.load(p)


def targets(ds):
    d = panel_data.load_split(ds, "test")
    y = np.asarray(d["field_by_fid"][d["hf_fid"]], dtype=np.float64)
    return y.reshape(y.shape[0], -1)


def per_sample_scale(p, y):
    # oracle per-sample multiplier minimising ||c p - y||
    return (p * y).sum(1) / np.maximum((p * p).sum(1), 1e-300)


for ds, pairs in CASES.items():
    y = targets(ds)
    print(f"\n===== {ds}  (ref {REF[ds]}, n_test={y.shape[0]}) =====")
    for a0tag, a1tag in pairs:
        z0, z1 = load(a0tag, ds), load(a1tag, ds)
        p0 = z0["pred_test"].astype(np.float64).reshape(y.shape[0], -1)
        p1 = z1["pred_test"].astype(np.float64).reshape(y.shape[0], -1)
        pt, yt = z0["pred_hf_train"].astype(np.float64), z0["target_hf_train"].astype(np.float64)
        pt = pt.reshape(pt.shape[0], -1); yt = yt.reshape(yt.shape[0], -1)

        c_train = per_sample_scale(pt, yt)             # 5 train rows, LF-FREE supervision
        c_test = per_sample_scale(p0, y)               # oracle (test-fitted ceiling)
        c_hat_global = float(np.median(c_train))       # H1: achievable global head

        s0 = NRMSE(p0, y) / REF[ds]
        s1 = NRMSE(p1, y) / REF[ds]
        s0_h1 = NRMSE(c_hat_global * p0, y) / REF[ds]
        s0_oracle = NRMSE(c_test[:, None] * p0, y) / REF[ds]
        # ceiling 1: single global gain fitted ON TEST
        c_glob_test = float((p0 * y).sum() / (p0 * p0).sum())
        s0_globtest = NRMSE(c_glob_test * p0, y) / REF[ds]

        eff = s0 - s1
        print(f"  {a0tag:>10} vs {a1tag:>10} | A0 {s0:10.4f}  A1 {s1:10.4f}  effect {eff:10.4f}")
        print(f"      train-row scale c: {np.round(c_train,4).tolist()}  median {c_hat_global:.4f}"
              f"  | train-row rel-l2 {float(np.mean(np.linalg.norm(pt-yt,axis=1)/np.linalg.norm(yt,axis=1))):.4f}")
        print(f"      test oracle scale: median {float(np.median(c_test)):.4f} "
              f"iqr [{float(np.percentile(c_test,25)):.4f},{float(np.percentile(c_test,75)):.4f}]")
        print(f"      A0+H1(train-global) {s0_h1:10.4f}  absorbed {(s0-s0_h1):10.4f} "
              f"= {100*(s0-s0_h1)/eff if eff else float('nan'):7.2f}% of effect")
        print(f"      A0+globalgain[TEST-FIT ceiling] {s0_globtest:10.4f}  "
              f"A0+per-sample ORACLE {s0_oracle:10.4f} = {100*(s0-s0_oracle)/eff if eff else float('nan'):7.2f}% of effect")
