from __future__ import annotations
import pandas as pd
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by static type-checkers
    from ..client import FinBrainClient


class SentimentsAPI:
    """
    Wrapper for **/sentiment/<TICKER>** endpoint.

    Example
    -------
    >>> fb.sentiments.ticker(
    ...     symbol="AMZN",
    ...     date_from="2024-01-01",
    ...     date_to="2024-02-02",
    ... )
    {
        "data": [
            {"date": "2024-01-15", "score": 0.123},
            ...
        ]
    }
    """

    # --------------------------------------------------------------------- #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client

    # --------------------------------------------------------------------- #
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
        Retrieve sentiment scores for a *single* ticker.

        Parameters
        ----------
        symbol :
            Stock/crypto symbol (``AAPL``, ``AMZN`` …) *uppercase recommended*.
        date_from, date_to :
            Optional start / end dates (``YYYY-MM-DD``).  If omitted, FinBrain
            defaults to its internal window.
        limit :
            Maximum number of records to return.
        as_dataframe :
            If *True*, return a **DataFrame** with a ``date`` index and a single
            ``sentiment`` column.

        Returns
        -------
        dict | pandas.DataFrame
        """
        # Build query parameters
        params: Dict[str, str] = {}

        if date_from:
            params["startDate"] = to_datestr(date_from)
        if date_to:
            params["endDate"] = to_datestr(date_to)
        if limit is not None:
            params["limit"] = str(limit)

        path = f"sentiment/{symbol.upper()}"

        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("data", [])
            df = pd.DataFrame(rows)
            if not df.empty:
                df.rename(columns={"score": "sentiment"}, inplace=True)
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                    df.set_index("date", inplace=True)
            return df

        return data
