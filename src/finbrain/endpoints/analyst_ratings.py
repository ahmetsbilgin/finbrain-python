from __future__ import annotations
import pandas as pd
import datetime as _dt
from urllib.parse import quote
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by type-checkers
    from ..client import FinBrainClient


class AnalystRatingsAPI:
    """
    Endpoint: ``/analystratings/<MARKET>/<TICKER>``

    Retrieve broker/analyst rating actions for a single ticker.
    Market names may contain spaces (``"S&P 500"``, ``"HK Hang Seng"``...);
    they are URL-encoded automatically.
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
        Analyst ratings for *symbol* in *market*.

        Parameters
        ----------
        market :
            Market name **exactly as FinBrain lists it**
            (e.g. ``"S&P 500"``, ``"Germany DAX"``, ``"HK Hang Seng"``).
            Spaces and special characters are accepted; they are URL-encoded
            automatically.
        symbol :
            Ticker symbol (case-insensitive; converted to upper-case).
        date_from, date_to :
            Optional ISO dates ``YYYY-MM-DD`` limiting the range.
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
        path = f"analystratings/{market_slug}/{symbol.upper()}"
        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("analystRatings", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
