from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:  # imported only by type-checkers
    from ..client import FinBrainClient


class OptionsAPI:
    """
    Options data endpoints
    ----------------------

    Currently implemented
    ~~~~~~~~~~~~~~~~~~~~~
    • **put_call** - ``/putcalldata/<MARKET>/<TICKER>``

    Future additions (open interest, IV, strikes, …) can live in this same class.
    """

    # ────────────────────────────────────────────────────────────────────
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client  # reference to the parent client

    # ────────────────────────────────────────────────────────────────────
    def put_call(
        self,
        market: str,
        symbol: str,
        *,
        date_from: _dt.date | str | None = None,
        date_to: _dt.date | str | None = None,
    ) -> Dict[str, Any]:
        """
        Put/Call ratio data for *symbol* in *market*.

        Parameters
        ----------
        market :
            Path segment such as ``sp500``, ``nasdaq``.
        symbol :
            Ticker symbol; converted to upper-case.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) bounding the returned rows.

        Returns
        -------
        dict
            Keys:

            * ``ticker``       - symbol
            * ``name``         - company name
            * ``putCallData``  - list[dict]  (date, ratio, callCount, putCount)
        """
        params: Dict[str, str] = {}
        if date_from:
            params["dateFrom"] = _to_datestr(date_from)
        if date_to:
            params["dateTo"] = _to_datestr(date_to)

        path = f"putcalldata/{market}/{symbol.upper()}"
        return self._c._request("GET", path, params=params)


# ────────────────────────────────────────────────────────────────────────
# helper
# ────────────────────────────────────────────────────────────────────────
def _to_datestr(value: _dt.date | str) -> str:
    """Convert :class:`datetime.date` → ``YYYY-MM-DD``; leave strings untouched."""
    if isinstance(value, _dt.date):
        return value.isoformat()
    return value
