from __future__ import annotations

import datetime as _dt
import pandas as pd
from urllib.parse import quote
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by static-type tools
    from ..client import FinBrainClient


class AppRatingsAPI:
    """
    Mobile-app rating analytics for a single ticker.

    Example
    -------
    >>> fb.app_ratings.ticker(
    ...     market="S&P 500",
    ...     symbol="AMZN",
    ...     date_from="2024-01-01",
    ...     date_to="2024-02-02",
    ... )["appRatings"][:2]
    [
        {
            "playStoreScore": 3.75,
            "playStoreRatingsCount": 567996,
            "appStoreScore": 4.07,
            "appStoreRatingsCount": 88533,
            "playStoreInstallCount": null,
            "date": "2024-02-02"
        },
        ...
    ]
    """

    # ------------------------------------------------------------------ #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client

    # ------------------------------------------------------------------ #
    def ticker(
        self,
        market: str,
        symbol: str,
        *,
        date_from: _dt.date | str | None = None,
        date_to: _dt.date | str | None = None,
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """
        Fetch mobile-app ratings for *symbol* in *market*.

        Parameters
        ----------
        market :
            Market name **exactly as FinBrain lists it**
            (e.g. ``"S&P 500"``, ``"Germany DAX"``, ``"HK Hang Seng"``).
            Spaces and special characters are accepted; they are URL-encoded
            automatically.
        symbol :
            Ticker symbol, upper-cased before the request.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) to bound the range.
        as_dataframe :
            If *True*, return a **pandas.DataFrame** indexed by ``date``;
            otherwise return the raw JSON dict.

        Returns
        -------
        dict | pandas.DataFrame
        """
        params: Dict[str, str] = {}

        if date_from:
            params["dateFrom"] = to_datestr(date_from)
        if date_to:
            params["dateTo"] = to_datestr(date_to)

        market_slug = quote(market, safe="")
        path = f"appratings/{market_slug}/{symbol.upper()}"
        data = self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("appRatings", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
