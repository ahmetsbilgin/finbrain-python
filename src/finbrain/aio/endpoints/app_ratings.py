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


def _flatten_apps(apps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """One row per app per observation — see the sync endpoint for the rationale."""
    flat: List[Dict[str, Any]] = []
    for app in apps or []:
        for obs in app.get("observations") or []:
            flat.append(
                {
                    "date": obs.get("date"),
                    "platform": app.get("platform"),
                    "app_id": app.get("appId"),
                    "app_name": app.get("appName"),
                    "score": obs.get("score"),
                    "ratings_count": obs.get("ratingsCount"),
                    "install_count": obs.get("installCount"),
                }
            )
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
        per_app: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """Fetch mobile-app ratings for a symbol (async).

        ``per_app=True`` returns the granular frame — one row per app per
        observation — instead of the blended per-date view. A company can
        publish many apps, so the blended view necessarily reports only its
        biggest on each platform.
        """
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
            if per_app:
                flat = _flatten_apps(data.get("apps") or [])
                df = pd.DataFrame(flat)
                if not df.empty and "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                    # Not indexed by date: a date repeats across apps.
                    df.sort_values(["app_id", "date"], inplace=True)
                    df.reset_index(drop=True, inplace=True)
                return df

            rows: List[Dict[str, Any]] = data.get("data", [])
            flat = _flatten_app_ratings(rows)
            df = pd.DataFrame(flat)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
