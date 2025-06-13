# tests/test_house_trades.py
import pandas as pd
import pytest
from urllib.parse import quote

from .conftest import stub_json
from finbrain.exceptions import BadRequest

MARKET = "S&P 500"  # contains space and &
ENC_MARKET = quote(MARKET, safe="")  # → 'S%26P%20500'
TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_house_trades_raw_ok(client, _activate_responses):
    path = f"housetrades/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "houseTrades": [
            {
                "date": "2024-03-19",
                "amount": "$360.00",
                "representative": "Pete Sessions",
                "type": "Purchase",
            }
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    data = client.house_trades.ticker(MARKET, TICKER)
    assert data["ticker"] == TICKER
    assert isinstance(data["houseTrades"], list)
    assert data["houseTrades"][0]["representative"] == "Pete Sessions"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_house_trades_dataframe_ok(client, _activate_responses):
    path = f"housetrades/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "houseTrades": [
            {
                "date": "2024-02-29",
                "amount": "$15,001 - $50,000",
                "representative": "Shri Thanedar",
                "type": "Sale",
            },
            {
                "date": "2024-01-25",
                "amount": "$360.00",
                "representative": "Pete Sessions",
                "type": "Purchase",
            },
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    df = client.house_trades.ticker(MARKET, TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert pd.Timestamp("2024-02-29") in df.index
    assert df.loc["2024-01-25", "representative"] == "Pete Sessions"


# ─────────── error mapping ──────────────────────────────────────────────
def test_house_trades_bad_request(client, _activate_responses):
    path = f"housetrades/{ENC_MARKET}/{TICKER}"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)

    with pytest.raises(BadRequest):
        client.house_trades.ticker(MARKET, TICKER)
