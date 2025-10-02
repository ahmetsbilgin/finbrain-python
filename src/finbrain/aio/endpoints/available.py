from __future__ import annotations
import pandas as pd
from typing import TYPE_CHECKING, Literal, List, Dict, Any

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient

_PType = Literal["daily", "monthly"]
_ALLOWED: set[str] = {"daily", "monthly"}


class AsyncAvailableAPI:
    """Async wrapper for /available endpoints."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    async def markets(self) -> List[str]:
        """Return every market index string FinBrain supports."""
        data = await self._c._request("GET", "available/markets")

        if isinstance(data, List):
            return data

        return data.get("availableMarkets", [])

    async def tickers(
        self,
        prediction_type: _PType,
        *,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """List all tickers for which FinBrain has predictions of the given type."""
        prediction_type = prediction_type.lower()
        if prediction_type not in _ALLOWED:
            raise ValueError("prediction_type must be 'daily' or 'monthly'")

        path = f"available/tickers/{prediction_type}"
        data: List[Dict[str, Any]] = await self._c._request("GET", path)

        return pd.DataFrame(data) if as_dataframe else data
