"""FinBrain Python SDK."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _v

try:  # installed (wheel / sdist / -e)
    __version__ = _v("finbrain-python")  # ← distribution name on PyPI
except PackageNotFoundError:  # fresh git clone, no install
    __version__ = "0.0.0.dev0"

from .client import FinBrainClient

__all__ = ["FinBrainClient", "__version__"]
