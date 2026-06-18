from __future__ import annotations
import pandas as pd
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by type-checkers
    from ..client import FinBrainClient


class PatentFilingsAPI:
    """
    Endpoints
    ---------
    ``/patent-filings/<TICKER>`` - USPTO granted patents mapped to a ticker.
    ``/screener/patent-filings`` - cross-ticker patent filings screener.
    """

    # ------------------------------------------------------------------ #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client  # reference to the parent client

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
        Fetch USPTO granted patents for *symbol*.

        Parameters
        ----------
        symbol :
            Ticker symbol; auto-upper-cased.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) bounding the returned rows by
            grant date (``patentDate``).
        limit :
            Maximum number of records to return (1-500).
        as_dataframe :
            If *True*, return a **pandas.DataFrame** indexed by ``patentDate``;
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

        path = f"patent-filings/{symbol.upper()}"

        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("patents", [])
            df = pd.DataFrame(rows)
            if not df.empty and "patentDate" in df.columns:
                df["patentDate"] = pd.to_datetime(df["patentDate"])
                df.set_index("patentDate", inplace=True)
            return df

        return data
