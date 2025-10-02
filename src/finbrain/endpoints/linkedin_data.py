from __future__ import annotations
import pandas as pd
from urllib.parse import quote
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by static type-checkers
    from ..client import FinBrainClient


class LinkedInDataAPI:
    """
    Endpoint
    --------
    ``/linkedindata/<MARKET>/<TICKER>`` - LinkedIn follower / employee-count
    metrics for a single ticker.
    """

    # ------------------------------------------------------------------ #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client  # reference to the parent client

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
        LinkedIn follower- and employee-count metrics for a single ticker.

        Market names may contain spaces (“S&P 500”, “Germany DAX”, “HK Hang Seng”);
        they are URL-encoded automatically.

        Parameters
        ----------
        market :
            Market name **exactly as FinBrain lists it**
            (e.g. ``"S&P 500"``, ``"Germany DAX"``, ``"HK Hang Seng"``).
            Spaces and special characters are accepted; they are URL-encoded
            automatically.
        symbol :
            Stock symbol; auto-upper-cased.
        date_from, date_to :
            Optional ``YYYY-MM-DD`` bounds.
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
        path = f"linkedindata/{market_slug}/{symbol.upper()}"

        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("linkedinData", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
