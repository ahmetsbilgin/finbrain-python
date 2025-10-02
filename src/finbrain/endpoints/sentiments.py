from __future__ import annotations
import pandas as pd
import datetime as _dt
from urllib.parse import quote
from typing import TYPE_CHECKING, Dict, Any

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by static type-checkers
    from ..client import FinBrainClient


class SentimentsAPI:
    """
    Wrapper for **/sentiments/<MARKET>/<TICKER>** endpoints.

    Example
    -------
    >>> fb.sentiments.ticker(
    ...     market="S&P 500",
    ...     symbol="AMZN",
    ...     date_from="2024-01-01",
    ...     date_to="2024-02-02",
    ... )
    {
        "ticker": "AMZN",
        "name": "Amazon.com Inc.",
        "sentimentAnalysis": {
            "2024-01-15": "0.123",
            ...
        }
    }
    """

    # --------------------------------------------------------------------- #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client

    # --------------------------------------------------------------------- #
    def ticker(
        self,
        market: str,
        symbol: str,
        *,
        date_from: _dt.date | str | None = None,
        date_to: _dt.date | str | None = None,
        days: int | None = None,
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """
        Retrieve sentiment scores for a *single* ticker.

        Parameters
        ----------
        market :
            Market name **exactly as FinBrain lists it**
            (e.g. ``"S&P 500"``, ``"Germany DAX"``, ``"HK Hang Seng"``).
            Spaces and special characters are accepted; they are URL-encoded
            automatically.
        symbol :
            Stock/crypto symbol (``AAPL``, ``AMZN`` …) *uppercase recommended*.
        date_from, date_to :
            Optional start / end dates (``YYYY-MM-DD``).  If omitted, FinBrain
            defaults to its internal window or to ``days``.
        days :
            Alternative to explicit dates - integer 1…120 for "past *n* days".
            Ignored if either ``date_from`` or ``date_to`` is supplied.
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
            params["dateFrom"] = to_datestr(date_from)
        if date_to:
            params["dateTo"] = to_datestr(date_to)
        if days is not None and "dateFrom" not in params and "dateTo" not in params:
            params["days"] = str(days)

        market_slug = quote(market, safe="")
        path = f"sentiments/{market_slug}/{symbol.upper()}"

        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        if as_dataframe:
            sa: Dict[str, str] = data.get("sentimentAnalysis", {})
            df = (
                pd.Series(sa, name="sentiment")
                .astype(float)
                .rename_axis("date")
                .to_frame()
            )
            df.index = pd.to_datetime(df.index)
            return df

        return data
