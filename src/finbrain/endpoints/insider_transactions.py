from __future__ import annotations
import pandas as pd
from urllib.parse import quote
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:  # imported only by static-type tools
    from ..client import FinBrainClient


class InsiderTransactionsAPI:
    """
    Endpoint
    --------
    ``/insidertransactions/<MARKET>/<TICKER>`` - recent Form-4 insider trades
    for the requested ticker.
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
        as_dataframe: bool = False,
    ) -> Dict[str, Any] | pd.DataFrame:
        """
        Insider transactions for *symbol* in *market*.

        Parameters
        ----------
        market :
            Market name **exactly as FinBrain lists it**
            (e.g. ``"S&P 500"``, ``"Germany DAX"``, ``"HK Hang Seng"``).
            Spaces and special characters are accepted; they are URL-encoded
            automatically.
        symbol :
            Ticker symbol; converted to upper-case.
        as_dataframe :
            If *True*, return a **pandas.DataFrame** indexed by ``date``;
            otherwise return the raw JSON dict.

        Returns
        -------
        dict | pandas.DataFrame
        """
        market_slug = quote(market, safe="")
        path = f"insidertransactions/{market_slug}/{symbol.upper()}"
        data: Dict[str, Any] = self._c._request("GET", path)

        # --- DataFrame conversion ---
        if as_dataframe:
            rows = data.get("insiderTransactions", [])
            df = pd.DataFrame(rows)
            if not df.empty and "date" in df.columns:
                # examples show dates like "Mar 08 '24" – let pandas parse flexibly
                _fmt = "%b %d '%y"  # e.g. Mar 08 '24
                dt = pd.to_datetime(df["date"], format=_fmt, errors="coerce")
                if dt.isna().any():  # fallback if format ever changes
                    dt = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)
                df["date"] = dt
                df.set_index("date", inplace=True)
            return df

        return data
