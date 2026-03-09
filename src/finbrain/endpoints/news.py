from __future__ import annotations
import pandas as pd
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:
    from ..client import FinBrainClient


class NewsAPI:
    """
    Endpoint: ``/news/<SYMBOL>`` (v2)

    Recent news articles with sentiment analysis for a single ticker.
    """

    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client

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
        Get recent news articles with sentiment for *symbol*.

        Parameters
        ----------
        symbol :
            Ticker symbol; auto-upper-cased.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``).
        limit :
            Maximum number of articles to return.
        as_dataframe :
            If *True*, return a **pandas.DataFrame** indexed by ``date``.

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

        path = f"news/{symbol.upper()}"
        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("articles", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
