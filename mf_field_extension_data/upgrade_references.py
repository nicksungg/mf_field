"""Regenerate the datasets that benefit from reference-grade solvers, in place,
preserving the numbered filenames and (params, lf, hf, param_names) schema.

  eikonal_2d           -> scikit-fmm Fast Marching (both tiers)
  cahn_hilliard_2d     -> ETDRK4 spectral (both tiers)
  kuramoto_sivashinsky -> ETDRK4 spectral (both tiers)

Gray-Scott already matches py-pde to ~0%; Helmholtz/Wave are exact-grade
(2nd-order, verified); Rayleigh-Benard kept as documented developing-convection.
"""
import os, json, warnings
import numpy as np
warnings.filterwarnings("ignore")
from solvers import REGISTRY, sample_params

DATA = "/home/nicksung/Downloads/mf_field_data/data"
JOBS = [  # (numbered file, registry name, N, [lf_grid, hf_grid], seed, solver label)
    ("05_eikonal_2d", "eikonal_2d", 150, [24, 64], 6, "reference: scikit-fmm FMM"),
    ("06_cahn_hilliard_2d", "cahn_hilliard_2d", 100, [24, 64], 7, "reference: ETDRK4 spectral"),
    ("07_kuramoto_sivashinsky_1d", "kuramoto_sivashinsky_1d", 120,
     [(64, 40), (256, 120)], 8, "reference: ETDRK4 spectral"),
]

man_path = os.path.join(DATA, "manifest.json")
manifest = json.load(open(man_path))
mi = {m["name"]: m for m in manifest}

for fname, name, N, grids, seed, label in JOBS:
    reg = REGISTRY[name]; ref = reg["reference"]
    P = sample_params(name, N, seed=seed)
    lf = ref(P, grids[0]).astype(np.float32)
    hf = ref(P, grids[1]).astype(np.float32)
    path = os.path.join(DATA, fname + ".npz")
    np.savez_compressed(path, params=P.astype(np.float32), lf=lf, hf=hf,
                        param_names=np.array(reg["param_names"]))
    # refresh manifest entry for this file
    key = fname  # manifest 'name' equals numbered file stem
    if key in mi:
        mi[key]["solver"] = label
        mi[key]["lf_shape"] = list(lf.shape[1:]); mi[key]["hf_shape"] = list(hf.shape[1:])
        mi[key]["file_mb"] = round(os.path.getsize(path) / 1e6, 3)
    print(f"upgraded {fname:28s} via {label}  LF{tuple(lf.shape[1:])} HF{tuple(hf.shape[1:])}")

# tag the others with their solver provenance for completeness
prov = {
    "01_helmholtz_2d": "exact-grade: 2nd-order FD direct solve (MMS-verified, p=2.02)",
    "02_rayleigh_benard_2d": "in-house FD vorticity-streamfunction (Nu grid-converged)",
    "03_gray_scott_2d": "in-house FD (matches py-pde to <0.01%)",
    "04_wave_2d": "exact-grade: 2nd-order leapfrog (standing-wave-verified, p=2.04)",
}
for k, v in prov.items():
    if k in mi:
        mi[k].setdefault("solver", v)

json.dump(manifest, open(man_path, "w"), indent=2)
print("manifest.json updated with solver provenance.")
