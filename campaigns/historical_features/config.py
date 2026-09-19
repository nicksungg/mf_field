"""Frozen scope for a field-conditioned ensemble pilot."""
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parent
MF = Path('/archive/mf_field')
ST = MF / 'experiments/st_bench'
PYTHON = MF / 'factory_mffp/.venv/bin/python'
PAPER_MODELS = ['mf_fno_transfer_film', 'mf_fno_allpairs', 'convnext_unet_film',
                'fno_fire_distcond', 'wno_transfer_film', 'mf_deeponet']
MODELS = PAPER_MODELS + ['st_hf_pod_gp']
CLASSES = {
    'elliptic': ['poisson_generated', 'poisson_generated_v2', 'poisson_local',
                 'darcy_generated', 'ext__helmholtz_2d', 'sharp__helmholtz_2d',
                 'ext__eikonal_2d', 'ext__pressure_poisson_poiseuille'],
    'diffusion': ['heat_generated', 'heat_local'],
    'shocks': ['sharp__burgers_2d', 'sharp__euler'],
    'convection': ['fluid', 'lid_driven_cavity_generated', 'lid_driven_cavity_v2',
                   'ext__rayleigh_benard_2d'],
    'porous': ['sharp__porous_medium_2d'],
    'reaction_diffusion': ['sharp__allen_cahn_2d', 'sharp__cahn_hilliard',
                           'ext__cahn_hilliard_2d', 'sharp__fisher_kpp_2d',
                           'sharp__phase_field_crystal_2d'],
    'waves': ['ext__wave_2d', 'sharp__shallow_water_2d'],
    'climate': ['era5'],
}
CLASS_OF = {d:c for c, ds in CLASSES.items() for d in ds}
EXCLUDE = 'node2900,node4200,node4002,node1702,node2119,node2809,node2810,node4004,node4007,node4008,node5003,node5004,node5005,node5101,node5103,node5104,node5106,node5202,node5203,node5204'

def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda:f.read(4*1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def write_json(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f'.tmp.{os.getpid()}')
    tmp.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')
    os.replace(tmp, path)

def atomic_npz(path, **arrays):
    import numpy as np
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f'.tmp.{os.getpid()}')
    with open(tmp, 'wb') as f:
        np.savez_compressed(f, **arrays)
    os.replace(tmp, path)

def specimen_group(dataset):
    # Old/fixed versions share generator inputs; never split their matching rows.
    if dataset in ('poisson_generated', 'poisson_generated_v2'):
        return 'poisson_generated_versions'
    if dataset in ('lid_driven_cavity_generated', 'lid_driven_cavity_v2'):
        return 'cavity_versions'
    return dataset

