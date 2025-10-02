from __future__ import annotations
import pandas as pd
from urllib.parse import quote
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


class AsyncOptionsAPI:
    """Async wrapper for options data endpoints."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    async def put_call(
        self,
        market: str,
        symbol: str,
        *,
        date_from: _dt.date | str | None = None,
        date_to: _dt.date | str | None = None,
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """Put/Call ratio data for symbol in market (async)."""
        params: Dict[str, str] = {}
        if date_from:
            params["dateFrom"] = to_datestr(date_from)
        if date_to:
            params["dateTo"] = to_datestr(date_to)

        market_slug = quote(market, safe="")
        path = f"putcalldata/{market_slug}/{symbol.upper()}"

        data: Dict[str, Any] = await self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("putCallData", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
