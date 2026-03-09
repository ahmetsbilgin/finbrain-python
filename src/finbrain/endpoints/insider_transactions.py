from __future__ import annotations
import pandas as pd
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by static-type tools
    from ..client import FinBrainClient


class InsiderTransactionsAPI:
    """
    Endpoint
    --------
    ``/insider-trading/<TICKER>`` - recent Form-4 insider trades
    for the requested ticker.
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
        Insider transactions for *symbol*.

        Parameters
        ----------
        symbol :
            Ticker symbol; converted to upper-case.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) bounding the returned rows.
        limit :
            Maximum number of records to return.
        as_dataframe :
            If *True*, return a **pandas.DataFrame** indexed by ``date``;
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

        path = f"insider-trading/{symbol.upper()}"
        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        # --- DataFrame conversion ---
        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("transactions", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
