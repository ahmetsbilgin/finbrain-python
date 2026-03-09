from __future__ import annotations
import pandas as pd
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any

from ._utils import to_datestr

if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


class AsyncSentimentsAPI:
    """Async wrapper for /sentiment endpoints."""

    def __init__(self, client: "AsyncFinBrainClient") -> None:
        self._c = client

    async def ticker(
        self,
        symbol: str,
        *,
        date_from: _dt.date | str | None = None,
        date_to: _dt.date | str | None = None,
        limit: int | None = None,
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """Retrieve sentiment scores for a single ticker (async)."""
        params: Dict[str, str] = {}

        if date_from:
            params["startDate"] = to_datestr(date_from)
        if date_to:
            params["endDate"] = to_datestr(date_to)
        if limit is not None:
            params["limit"] = str(limit)

        path = f"sentiment/{symbol.upper()}"

        data: Dict[str, Any] = await self._c._request("GET", path, params=params)

        if as_dataframe:
            rows = data.get("data", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            if "score" in df.columns:
                df.rename(columns={"score": "sentiment"}, inplace=True)
            return df

        return data
