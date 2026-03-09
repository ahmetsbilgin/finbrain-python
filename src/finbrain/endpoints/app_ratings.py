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
            If *True*, return a **pandas.DataFrame** indexed by ``date``
            with flattened columns (``ios_score``, ``android_score``, etc.);
            otherwise return the raw JSON dict.

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
            rows: List[Dict[str, Any]] = data.get("data", [])
            flat = _flatten_app_ratings(rows)
            df = pd.DataFrame(flat)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
