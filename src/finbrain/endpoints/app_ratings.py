from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:  # imported only by static-type tools
    from ..client import FinBrainClient


class AppRatingsAPI:
    """
    Mobile-app rating analytics for a single ticker.

    Example
    -------
    >>> fb.app_ratings.ticker(
    ...     market="sp500",
    ...     symbol="AMZN",
    ...     date_from="2024-01-01",
    ...     date_to="2024-02-02",
    ... )["appRatings"][:2]
    [
        {
            "playStoreScore": 3.75,
            "playStoreRatingsCount": 567996,
            "appStoreScore": 4.07,
            "appStoreRatingsCount": 88533,
            "playStoreInstallCount": null,
            "date": "2024-02-02"
        },
        ...
    ]
    """

    # ------------------------------------------------------------------ #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client

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
        Fetch mobile-app ratings for *symbol* in *market*.

        Parameters
        ----------
        market :
            Path segment after ``/appratings/`` (e.g. ``sp500``, ``nasdaq``).
        symbol :
            Ticker symbol, upper-cased before the request.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) to bound the range.

        Returns
        -------
        dict
            Keys: ``ticker``, ``name``, ``appRatings`` (list of dicts).
        """
        params: Dict[str, str] = {}

        if date_from:
            params["dateFrom"] = _to_datestr(date_from)
        if date_to:
            params["dateTo"] = _to_datestr(date_to)

        path = f"appratings/{market}/{symbol.upper()}"
        return self._c._request("GET", path, params=params)


# ---------------------------------------------------------------------- #
# helper                                                                 #
# ---------------------------------------------------------------------- #
def _to_datestr(value: _dt.date | str) -> str:
    """Convert :pyclass:`~datetime.date` → ``YYYY-MM-DD`` but pass strings."""
    if isinstance(value, _dt.date):
        return value.isoformat()
    return value
