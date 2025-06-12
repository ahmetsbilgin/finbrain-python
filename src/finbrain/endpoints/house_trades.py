from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:  # imported only by type-checkers
    from ..client import FinBrainClient


class HouseTradesAPI:
    """
    Endpoint
    --------
    ``/housetrades/<MARKET>/<TICKER>`` - trading activity of U.S. House
    Representatives for the selected ticker.
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
        Fetch House-member trades for *symbol* in *market*.

        Parameters
        ----------
        market :
            Path segment such as ``sp500``, ``nasdaq`` - must match your
            FinBrain subscription.
        symbol :
            Ticker symbol; auto-upper-cased.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) bounding the returned rows.

        Returns
        -------
        dict
            Keys:

            * ``ticker``       - symbol
            * ``name``         - company name
            * ``houseTrades``  - list[dict] (date, amount, representative, type)
        """
        params: Dict[str, str] = {}
        if date_from:
            params["dateFrom"] = _to_datestr(date_from)
        if date_to:
            params["dateTo"] = _to_datestr(date_to)

        path = f"housetrades/{market}/{symbol.upper()}"
        return self._c._request("GET", path, params=params)


# ---------------------------------------------------------------------- #
# helper                                                                  #
# ---------------------------------------------------------------------- #
def _to_datestr(value: _dt.date | str) -> str:
    """Convert ``datetime.date`` → ``YYYY-MM-DD``; leave strings untouched."""
    if isinstance(value, _dt.date):
        return value.isoformat()
    return value
