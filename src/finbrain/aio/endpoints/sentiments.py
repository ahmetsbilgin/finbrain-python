from __future__ import annotations
import pandas as pd
import datetime as _dt
from urllib.parse import quote
from typing import TYPE_CHECKING, Dict, Any

from ._utils import to_datestr

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


class AsyncSentimentsAPI:
    """Async wrapper for /sentiments endpoints."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    async def ticker(
        self,
        market: str,
        symbol: str,
        *,
        date_from: _dt.date | str | None = None,
        date_to: _dt.date | str | None = None,
        days: int | None = None,
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """Retrieve sentiment scores for a single ticker (async)."""
        params: Dict[str, str] = {}

        if date_from:
            params["dateFrom"] = to_datestr(date_from)
        if date_to:
            params["dateTo"] = to_datestr(date_to)
        if days is not None and "dateFrom" not in params and "dateTo" not in params:
            params["days"] = str(days)

        market_slug = quote(market, safe="")
        path = f"sentiments/{market_slug}/{symbol.upper()}"

        data: Dict[str, Any] = await self._c._request("GET", path, params=params)

        if as_dataframe:
            sa: Dict[str, str] = data.get("sentimentAnalysis", {})
            df = (
                pd.Series(sa, name="sentiment")
                .astype(float)
                .rename_axis("date")
                .to_frame()
            )
            df.index = pd.to_datetime(df.index)
            return df

        return data
