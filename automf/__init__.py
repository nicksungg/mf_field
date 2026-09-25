"""A fit/predict interface for scalar multifidelity field surrogates."""

from .data import FieldDataset
from .predictor import FieldPredictor

__all__ = ["FieldDataset", "FieldPredictor"]
__version__ = "0.1.0"
