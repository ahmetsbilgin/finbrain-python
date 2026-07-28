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
            ``amount``, ``owner``, ``amountRaw``, ``amountFlag`` and
            ``disclosureDate`` — the date the trade was publicly disclosed
            in the member's periodic transaction report. The gap between the
            two dates is the reporting lag.

            ``owner`` is the beneficial owner of the traded account:
            ``"SELF"``, ``"SP"`` (spouse), ``"DC"`` (dependent child),
            ``"JT"`` (joint), an account code, or ``"UNKNOWN"`` when the
            Senate filing left the owner column blank.

            ``amount`` is normalized to the statutory STOCK Act bracket
            (e.g. ``"$1,001 - $15,000"``) whenever the filed string is an
            unambiguous formatting variant of one. On rows that were
            normalized, ``amountRaw`` preserves the string as originally
            filed. When the filed amount could not be safely normalized,
            ``amount`` keeps the raw filed string (or ``"Unknown"`` when the
            filing had no usable amount) and ``amountFlag`` is ``"review"``
            or ``"ambiguous"``; on all other rows ``amountRaw`` and
            ``amountFlag`` are ``None``.

            ``disclosureDate`` and ``owner`` are nullable; historical rows
            were backfilled in place by the upstream pipeline, so missing
            values are rare but possible. In the DataFrame branch ``date``
            becomes the index and the remaining fields are columns whose
            missing values read as ``None`` or ``NaN`` depending on the
            pandas version — test them with :func:`pandas.isna`.

        Notes
        -----
        ``date_from`` and ``date_to`` bound the **transaction** date, not the
        disclosure date. A trade executed inside the window is returned even
        if it was disclosed after ``date_to``.

        Example row::

            {"date": "2026-06-10", "politician": "Jane Doe",
             "transactionType": "Purchase", "amount": "$1,001 - $15,000",
             "owner": "SP", "amountRaw": "$1,001-$15,000",
             "amountFlag": None, "disclosureDate": "2026-06-25"}

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
