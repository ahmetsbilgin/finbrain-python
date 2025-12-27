# tests/test_senate_trades.py
import pandas as pd
import pytest
from urllib.parse import quote

from .conftest import stub_json
from finbrain.exceptions import BadRequest

MARKET = "NASDAQ"
ENC_MARKET = quote(MARKET, safe="")
TICKER = "META"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_senate_trades_raw_ok(client, _activate_responses):
    path = f"senatetrades/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Meta Platforms Inc.",
        "senateTrades": [
            {
                "date": "2025-11-13",
                "amount": "$1,001 - $15,000",
                "senator": "Shelley Moore Capito",
                "type": "Purchase",
            }
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    data = client.senate_trades.ticker(MARKET, TICKER)
    assert data["ticker"] == TICKER
    assert isinstance(data["senateTrades"], list)
    assert data["senateTrades"][0]["senator"] == "Shelley Moore Capito"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_senate_trades_dataframe_ok(client, _activate_responses):
    path = f"senatetrades/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Meta Platforms Inc.",
        "senateTrades": [
            {
                "date": "2025-11-13",
                "amount": "$1,001 - $15,000",
                "senator": "Shelley Moore Capito",
                "type": "Purchase",
            },
            {
                "date": "2025-10-31",
                "amount": "$1,001 - $15,000",
                "senator": "John Boozman",
                "type": "Purchase",
            },
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    df = client.senate_trades.ticker(MARKET, TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert pd.Timestamp("2025-11-13") in df.index
    assert df.loc["2025-10-31", "senator"] == "John Boozman"


# ─────────── error mapping ──────────────────────────────────────────────
def test_senate_trades_bad_request(client, _activate_responses):
    path = f"senatetrades/{ENC_MARKET}/{TICKER}"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)

    with pytest.raises(BadRequest):
        client.senate_trades.ticker(MARKET, TICKER)