from __future__ import annotations
import pandas as pd
import datetime as _dt
from typing import TYPE_CHECKING, Dict, Any, List

from ._utils import to_datestr

if TYPE_CHECKING:  # imported only by type-checkers
    from ..client import FinBrainClient


class SenateTradesAPI:
    """
    Endpoint
    --------
    ``/congress/senate/<TICKER>`` - trading activity of U.S. Senators
    for the selected ticker.
    """

    # ------------------------------------------------------------------ #
    def __init__(self, client: "FinBrainClient") -> None:
        self._c = client  # reference to the parent client

    # ------------------------------------------------------------------ #
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
        Fetch Senate-member trades for *symbol*.

        Parameters
        ----------
        symbol :
            Ticker symbol; auto-upper-cased.
        date_from, date_to :
            Optional ISO dates (``YYYY-MM-DD``) bounding the returned rows.
        limit :
            Maximum number of records to return.
        as_dataframe :
            If *True*, return a **pandas.DataFrame** indexed by ``date``;
            otherwise return the raw JSON dict.

        Returns
        -------
        dict | pandas.DataFrame
            The raw dict has a ``trades`` list whose rows carry ``date``
            (the transaction date), ``politician``, ``transactionType``,
            ``amount`` and ``disclosureDate`` — the date the trade was
            publicly disclosed in the member's periodic transaction report.
            The gap between the two dates is the reporting lag.

            ``disclosureDate`` is ``None`` for historical rows collected
            before the field was captured upstream. In the DataFrame branch
            ``date`` becomes the index and ``disclosureDate`` is a column
            whose missing values read as ``None`` or ``NaN`` depending on the
            pandas version — test them with :func:`pandas.isna`.

        Notes
        -----
        ``date_from`` and ``date_to`` bound the **transaction** date, not the
        disclosure date. A trade executed inside the window is returned even
        if it was disclosed after ``date_to``.

        Example row::

            {"date": "2026-06-10", "politician": "Jane Doe",
             "transactionType": "Purchase", "amount": "$1,001 - $15,000",
             "disclosureDate": "2026-06-25"}

        """
        params: Dict[str, str] = {}
        if date_from:
            params["startDate"] = to_datestr(date_from)
        if date_to:
            params["endDate"] = to_datestr(date_to)
        if limit is not None:
            params["limit"] = str(limit)

        path = f"congress/senate/{symbol.upper()}"

        data: Dict[str, Any] = self._c._request("GET", path, params=params)

        if as_dataframe:
            rows: List[Dict[str, Any]] = data.get("trades", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)
            return df

        return data
