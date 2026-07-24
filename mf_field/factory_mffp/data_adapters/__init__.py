"""Unified multi-fidelity dataset adapters for factory_mffp.

Drop-in loaders that handle every dataset layout under data/ — both the existing
`ifc_raw` layout (used by ifc_heat, ifc_poisson, chin_chun_*) and the
`npz_l*` layout (used by the other 13 datasets). Auto-detects format.

Public API:
    load_mf_dataset(dataset_dir, split) -> dict   # raw arrays
    MFDataset(dataset_dir, split)                  # torch.utils.data.Dataset

A family wanting to replace its hardcoded `IFCRawMultiStreamDataset` with this
adapter only needs to swap the import and (if its model expects 2-D fields)
reshape via the `grid_shape_by_fid` metadata returned by load_mf_dataset.
"""

from .loaders import load_mf_dataset, MFDataset, detect_layout

__all__ = ["load_mf_dataset", "MFDataset", "detect_layout"]
