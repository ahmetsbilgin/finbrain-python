from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:  # imported only by static type-checkers
    from ..client import FinBrainClient


class SentimentsAPI:
    """
    Wrapper for **/sentiments/<MARKET>/<TICKER>** endpoints.

    Example
    -------
    >>> fb.sentiments.ticker(
    ...     market="sp500",
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
    ) -> Dict[str, Any]:
        """
        Retrieve sentiment scores for a *single* ticker.

        Parameters
        ----------
        market :
            The market segment as used in the path (e.g. ``sp500``, ``nasdaq``).
        symbol :
            Stock/crypto symbol (``AAPL``, ``AMZN`` …) *uppercase recommended*.
        date_from, date_to :
            Optional start / end dates (``YYYY-MM-DD``).  If omitted, FinBrain
            defaults to its internal window or to ``days``.
        days :
            Alternative to explicit dates - integer 1…120 for "past *n* days".
            Ignored if either ``date_from`` or ``date_to`` is supplied.

        Returns
        -------
        dict
            The raw JSON FinBrain returns, keys:

            - ``ticker`` - symbol
            - ``name``   - company name
            - ``sentimentAnalysis`` - mapping of ``YYYY-MM-DD`` → score string
        """
        # Build query parameters
        params: Dict[str, str] = {}

        if date_from:
            params["dateFrom"] = _to_datestr(date_from)
        if date_to:
            params["dateTo"] = _to_datestr(date_to)
        if days is not None and "dateFrom" not in params and "dateTo" not in params:
            params["days"] = str(days)

        path = f"sentiments/{market}/{symbol.upper()}"

        return self._c._request("GET", path, params=params)


# ------------------------------------------------------------------------- #
# Helpers                                                                   #
# ------------------------------------------------------------------------- #
def _to_datestr(value: _dt.date | str) -> str:
    """Convert ``datetime.date`` → 'YYYY-MM-DD' but pass strings through."""
    if isinstance(value, _dt.date):
        return value.isoformat()
    return value
