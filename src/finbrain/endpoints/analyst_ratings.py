from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:  # imported only by type-checkers
    from ..client import FinBrainClient


class AnalystRatingsAPI:
    """
    Endpoint: ``/analystratings/<MARKET>/<TICKER>``

    Fetches broker/analyst rating actions (upgrade/downgrade, target-price
    changes, etc.) for a single ticker.
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
    ) -> Dict[str, Any]:
        """
        Analyst ratings for *symbol* in *market*.

        Parameters
        ----------
        market :
            Path segment such as ``sp500``, ``nasdaq`` — must match your FinBrain
            subscription.
        symbol :
            Ticker symbol (case-insensitive; converted to upper-case).
        date_from, date_to :
            Optional ISO dates ``YYYY-MM-DD`` limiting the range.

        Returns
        -------
        dict
            Keys:

            * ``ticker``           - symbol
            * ``name``             - company name
            * ``analystRatings``   - list[dict] of rating actions
        """
        params: Dict[str, str] = {}

        if date_from:
            params["dateFrom"] = _to_datestr(date_from)
        if date_to:
            params["dateTo"] = _to_datestr(date_to)

        path = f"analystratings/{market}/{symbol.upper()}"
        return self._c._request("GET", path, params=params)


# ---------------------------------------------------------------------- #
# helper                                                                 #
# ---------------------------------------------------------------------- #
def _to_datestr(value: _dt.date | str) -> str:
    """Convert ``datetime.date`` → ``YYYY-MM-DD``; pass strings through untouched."""
    if isinstance(value, _dt.date):
        return value.isoformat()
    return value
