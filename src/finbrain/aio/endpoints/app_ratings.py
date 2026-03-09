from __future__ import annotations

import datetime as _dt
import pandas as pd
from typing import TYPE_CHECKING, Dict, Any, List
from ._utils import to_datestr


if TYPE_CHECKING:
    from ..client import AsyncFinBrainClient


def _flatten_app_ratings(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten nested iOS/Android rating objects into flat column dicts."""
    flat: List[Dict[str, Any]] = []
    for row in rows:
        entry: Dict[str, Any] = {"date": row.get("date")}
        ios = row.get("ios", {}) or {}
        entry["ios_score"] = ios.get("score")
        entry["ios_ratingsCount"] = ios.get("ratingsCount")
        android = row.get("android", {}) or {}
        entry["android_score"] = android.get("score")
        entry["android_ratingsCount"] = android.get("ratingsCount")
        entry["android_installCount"] = android.get("installCount")
        flat.append(entry)
    return flat


class AsyncAppRatingsAPI:
    """Async wrapper for mobile-app rating analytics."""

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
        """Fetch mobile-app ratings for a symbol (async)."""
        params: Dict[str, str] = {}

        if date_from:
            params["startDate"] = to_datestr(date_from)
        if date_to:
            params["endDate"] = to_datestr(date_to)
        if limit is not None:
            params["limit"] = str(limit)

        path = f"app-ratings/{symbol.upper()}"
        data = await self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("data", [])
            flat = _flatten_app_ratings(rows)
            df = pd.DataFrame(flat)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
