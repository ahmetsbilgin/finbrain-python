from __future__ import annotations

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
    def ticker(self, market: str, symbol: str) -> Dict[str, Any]:
        """
        Insider transactions for *symbol* in *market*.

        Parameters
        ----------
        market :
            Path segment such as ``sp500``, ``nasdaq`` - must match your
            FinBrain subscription.
        symbol :
            Ticker symbol; converted to upper-case.

        Returns
        -------
        dict
            Keys:

            * ``ticker``               - symbol
            * ``name``                 - company name
            * ``insiderTransactions``  - list[dict] of trade records
        """
        path = f"insidertransactions/{market}/{symbol.upper()}"
        return self._c._request("GET", path)
