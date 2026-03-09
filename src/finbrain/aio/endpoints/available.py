from __future__ import annotations
import pandas as pd
from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


class AsyncAvailableAPI:
    """Async wrapper for discovery endpoints."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    async def markets(
        self,
        *,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Return every market FinBrain supports."""
        data = await self._c._request("GET", "markets")

        markets_list: List[Dict[str, Any]] = (
            data if isinstance(data, list) else data.get("markets", [])
        )

        return pd.DataFrame(markets_list) if as_dataframe else markets_list

    async def tickers(
        self,
        prediction_type: str = "daily",
        *,
        limit: int | None = None,
        market: str | None = None,
        region: str | None = None,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """List all tickers for which FinBrain has predictions of the given type."""
        prediction_type = prediction_type.lower()
        if prediction_type not in ("daily", "monthly"):
            raise ValueError("prediction_type must be 'daily' or 'monthly'")

        params: Dict[str, str] = {"type": prediction_type}
        if limit is not None:
            params["limit"] = str(limit)
        if market:
            params["market"] = market
        if region:
            params["region"] = region

        data = await self._c._request("GET", "tickers", params=params)

        # v2 API wraps the list in {"tickers": [...]}
        if isinstance(data, dict):
            rows = data.get("tickers", [])
        else:
            rows = data

        return pd.DataFrame(rows) if as_dataframe else rows

    async def regions(
        self,
        *,
        as_dataframe: bool = False,
    ) -> List[Dict[str, Any]] | pd.DataFrame:
        """Return markets grouped by region."""
        data = await self._c._request("GET", "regions")

        regions_list: List[Dict[str, Any]] = (
            data if isinstance(data, list) else data.get("regions", [])
        )

        return pd.DataFrame(regions_list) if as_dataframe else regions_list
