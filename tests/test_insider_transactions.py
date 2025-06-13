# tests/test_insider_transactions.py
import pandas as pd
import pytest
from urllib.parse import quote

from .conftest import stub_json
from finbrain.exceptions import BadRequest

MARKET = "S&P 500"  # market names may contain spaces/&
ENC_MARKET = quote(MARKET, safe="")  # → 'S%26P%20500'
TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_insider_tx_raw_ok(client, _activate_responses):
    path = f"insidertransactions/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "insiderTransactions": [
            {
                "date": "Mar 08 '24",
                "insiderTradings": "Selipsky Adam",
                "relationship": "CEO Amazon Web Services",
                "transaction": "Sale",
                "cost": 176.31,
                "shares": 500,
            }
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    data = client.insider_transactions.ticker(MARKET, TICKER)
    assert data["ticker"] == TICKER
    assert isinstance(data["insiderTransactions"], list)
    assert data["insiderTransactions"][0]["insiderTradings"] == "Selipsky Adam"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_insider_tx_dataframe_ok(client, _activate_responses):
    path = f"insidertransactions/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "insiderTransactions": [
            {
                "date": "Mar 08 '24",
                "insiderTradings": "Selipsky Adam",
                "relationship": "CEO Amazon Web Services",
                "transaction": "Sale",
                "cost": 176.31,
                "shares": 500,
            },
            {
                "date": "Feb 15 '24",
                "insiderTradings": "Jassy Andrew",
                "relationship": "Chief Executive Officer",
                "transaction": "Purchase",
                "cost": 160.00,
                "shares": 1000,
            },
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    df = client.insider_transactions.ticker(MARKET, TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert pd.Timestamp("2024-03-08") in df.index  # parsed date
    assert df.loc["2024-02-15", "insiderTradings"] == "Jassy Andrew"


# ─────────── error mapping ──────────────────────────────────────────────
def test_insider_tx_bad_request(client, _activate_responses):
    path = f"insidertransactions/{ENC_MARKET}/{TICKER}"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)

    with pytest.raises(BadRequest):
        client.insider_transactions.ticker(MARKET, TICKER)
