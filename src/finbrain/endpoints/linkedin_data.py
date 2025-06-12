from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:  # imported only by static type-checkers
    from ..client import FinBrainClient


class LinkedInDataAPI:
    """
    Endpoint
    --------
    ``/linkedindata/<MARKET>/<TICKER>`` - LinkedIn follower / employee-count
    metrics for a single ticker.
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
        LinkedIn metrics for *symbol* in *market*.

        Parameters
        ----------
        market :
            Path segment such as ``sp500`` or ``nasdaq``.
        symbol :
            Stock symbol; auto-upper-cased.
        date_from, date_to :
            Optional ``YYYY-MM-DD`` bounds.

        Returns
        -------
        dict
            Keys:

            * ``ticker``        - symbol
            * ``name``          - company name
            * ``linkedinData``  - list[dict] (date, employeeCount, followersCount)
        """
        params: Dict[str, str] = {}
        if date_from:
            params["dateFrom"] = _to_datestr(date_from)
        if date_to:
            params["dateTo"] = _to_datestr(date_to)

        path = f"linkedindata/{market}/{symbol.upper()}"
        return self._c._request("GET", path, params=params)


# ---------------------------------------------------------------------- #
# helper                                                                  #
# ---------------------------------------------------------------------- #
def _to_datestr(value: _dt.date | str) -> str:
    """Convert :class:`datetime.date` → ``YYYY-MM-DD``; leave strings untouched."""
    if isinstance(value, _dt.date):
        return value.isoformat()
    return value
