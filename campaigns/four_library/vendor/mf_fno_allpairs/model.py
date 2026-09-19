"""All-pairs fidelity FiLM-FNO (POSEIDON all2all -> fidelity ladder).

ONE FNO is trained over EVERY ordered fidelity pair (src < tgt) drawn from the
train fidelities. For a pair (s, t) the input is the sample's condition vector X
and the target is that sample's field at fidelity t resampled to the common
working grid; the network is FiLM-conditioned on

    cond = [X, f_src, f_tgt]            (cond_dim = d + 2)

where f_src, f_tgt are normalized fidelity scalars in [0,1]. Training over all
ordered pairs amplifies the data O(L^2) and teaches the cross-fidelity trend
(herde2024poseidon's all2all transfer, recast onto a fidelity ladder). At eval
we query (f_src = lf_norm, f_tgt = hf_norm) to predict the HF field.

The model is just common.backbone.FNO2d with a widened cond dim — FiLMNorm is
agnostic to the conditioning source, so the all-pairs scalars ride in exactly
where the winner put raw X. We re-export it here so the family is self-contained.

References: herde2024poseidon (all2all multi-operator training), perez2018film
(FiLM), li2020fno (FNO backbone, imported from common.backbone).
"""
from __future__ import annotations

import sys
from pathlib import Path

MODEL_LIBRARY = Path(__file__).resolve().parents[2]
if str(MODEL_LIBRARY) not in sys.path:
    sys.path.insert(0, str(MODEL_LIBRARY))

from common.backbone import FNO2d, param_count  # noqa: E402,F401

# The all-pairs model IS the shared FiLM-FNO with cond_dim = d + 2.
# forward(cond) where cond = concat([X, f_src, f_tgt], dim=-1).
AllPairsFNO2d = FNO2d
