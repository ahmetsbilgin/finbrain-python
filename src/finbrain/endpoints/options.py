from __future__ import annotations
import pandas as pd
from urllib.parse import quote
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any, List

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
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """
        Put/Call ratio data for *symbol* in *market*.

        Parameters
        ----------
        market :
            Market name **exactly as FinBrain lists it**
            (e.g. ``"S&P 500"``, ``"Germany DAX"``, ``"HK Hang Seng"``).
            Spaces and special characters are accepted; they are URL-encoded
            automatically.
        symbol :
            Ticker symbol; converted to upper-case.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) bounding the returned rows.
        as_dataframe :
            If *True*, return a **pandas.DataFrame** indexed by ``date``;
            otherwise return the raw JSON dict.

        Returns
        -------
        dict | pandas.DataFrame
        """
        params: Dict[str, str] = {}
        if date_from:
            params["dateFrom"] = _to_datestr(date_from)
        if date_to:
            params["dateTo"] = _to_datestr(date_to)

        market_slug = quote(market, safe="")
        path = f"putcalldata/{market_slug}/{symbol.upper()}"

        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("putCallData", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data


# ────────────────────────────────────────────────────────────────────────
# helper
# ────────────────────────────────────────────────────────────────────────
def _to_datestr(value: _dt.date | str) -> str:
    """Convert :class:`datetime.date` → ``YYYY-MM-DD``; leave strings untouched."""
    return value.isoformat() if isinstance(value, _dt.date) else value
