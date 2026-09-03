from __future__ import annotations

import datetime as _dt
import pandas as pd
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by static-type tools
    from ..client import FinBrainClient


def _flatten_app_ratings(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flatten nested app-rating records.

    Input format per record::

        {
            "date": "2024-02-02",
            "ios": {"score": 4.07, "ratingsCount": 88533},
            "android": {"score": 3.75, "ratingsCount": 567996, "installCount": 1000000}
        }

    Output format per record::

        {
            "date": "2024-02-02",
            "ios_score": 4.07,
            "ios_ratingsCount": 88533,
            "android_score": 3.75,
            "android_ratingsCount": 567996,
            "android_installCount": 1000000,
        }
    """
    flat: List[Dict[str, Any]] = []
    for row in rows:
        rec: Dict[str, Any] = {"date": row.get("date")}
        for platform in ("ios", "android"):
            sub = row.get(platform, {}) or {}
            for key, value in sub.items():
                rec[f"{platform}_{key}"] = value
        flat.append(rec)
    return flat


def _flatten_apps(apps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flatten the per-app series into one row per app per observation.

    A company can publish many apps — Apple has 140 on iOS — so the blended
    ``data`` view necessarily reports one per platform. This is the granular
    alternative: no blending and no derived company score, one row per
    (app, date), so callers weight or filter for themselves.

    ``app_id`` is ``None`` for observations predating the API keying rows per
    app: the platform is known, the app is not.

    Input format per app::

        {
            "platform": "ios",
            "appId": "1108187390",
            "appName": "Apple Music",
            "observations": [
                {"date": "2026-09-01", "score": 4.86,
                 "ratingsCount": 3074796, "installCount": None},
                ...
            ],
        }
    """
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


class AppRatingsAPI:
    """
    Mobile-app rating analytics for a single ticker.

    Example
    -------
    >>> fb.app_ratings.ticker(
    ...     symbol="AMZN",
    ...     date_from="2024-01-01",
    ...     date_to="2024-02-02",
    ... )["data"][:1]
    [
        {
            "date": "2024-02-02",
            "ios": {"score": 4.07, "ratingsCount": 88533},
            "android": {"score": 3.75, "ratingsCount": 567996, "installCount": null}
        }
    ]
    """

    # ------------------------------------------------------------------ #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client

    # ------------------------------------------------------------------ #
    def ticker(
        self,
        symbol: str,
        *,
        date_from: _dt.date | str | None = None,
        date_to: _dt.date | str | None = None,
        limit: int | None = None,
        as_dataframe: bool = False,
        per_app: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """
        Fetch mobile-app ratings for *symbol*.

        Parameters
        ----------
        symbol :
            Ticker symbol, upper-cased before the request.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) to bound the range.
        limit :
            Maximum number of records to return.
        as_dataframe :
            If *True*, return a **pandas.DataFrame**; otherwise the raw JSON
            dict, which carries both views.
        per_app :
            Only meaningful with ``as_dataframe``. If *True*, return the
            granular frame — one row per app per observation, with
            ``platform``, ``app_id``, ``app_name``, ``score``,
            ``ratings_count`` and ``install_count``, **not** indexed by date
            since a date repeats across apps. If *False* (default), return the
            blended per-date frame indexed by ``date``, which reports the
            company's biggest app on each platform.

            Prefer ``per_app=True`` for anything quantitative: a company can
            publish many apps (Apple has 140 on iOS) and which of them matters
            is your judgement, not ours.

        Returns
        -------
        dict | pandas.DataFrame
        """
        params: Dict[str, str] = {}

        if date_from:
            params["startDate"] = to_datestr(date_from)
        if date_to:
            params["endDate"] = to_datestr(date_to)
        if limit is not None:
            params["limit"] = str(limit)

        path = f"app-ratings/{symbol.upper()}"
        data = self._c._request("GET", path, params=params)

        if as_dataframe:
            if per_app:
                flat = _flatten_apps(data.get("apps") or [])
                df = pd.DataFrame(flat)
                if not df.empty and "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                    # Deliberately NOT indexed by date: one date carries one
                    # row per app, so a date index would not be unique.
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
