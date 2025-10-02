from __future__ import annotations
import pandas as pd
from urllib.parse import quote
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any

from ._utils import to_datestr

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


class AsyncHouseTradesAPI:
    """Async wrapper for /housetrades endpoints."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    async def ticker(
        self,
        market: str,
        symbol: str,
        *,
        date_from: _dt.date | str | None = None,
        date_to: _dt.date | str | None = None,
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """Fetch House-member trades for symbol in market (async)."""
        params: Dict[str, str] = {}
        if date_from:
            params["dateFrom"] = to_datestr(date_from)
        if date_to:
            params["dateTo"] = to_datestr(date_to)

        market_slug = quote(market, safe="")
        path = f"housetrades/{market_slug}/{symbol.upper()}"

        data: Dict[str, Any] = await self._c._request("GET", path, params=params)

        if as_dataframe:
            rows = data.get("houseTrades", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
