"""FinBrain Python SDK."""

from importlib import metadata as _meta

try:  # installed from a wheel / sdist
    __version__: str = _meta.version(__name__)
except _meta.PackageNotFoundError:  # running from a Git checkout
    __version__ = "0.0.0.dev0"

from .client import FinBrainClient

__all__ = ["FinBrainClient", "__version__"]
