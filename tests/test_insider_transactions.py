# tests/test_insider_transactions.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_insider_tx_raw_ok(client, _activate_responses):
    path = f"insider-trading/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "transactions": [
            {
                "date": "2024-01-15",
                "insider": "John Doe",
                "relationship": "CFO",
                "transactionType": "Sale",
                "shares": 5000,
                "pricePerShare": 155.0,
                "totalValue": 775000,
                "sharesOwned": 50000,
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.insider_transactions.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["transactions"], list)
    assert data["transactions"][0]["insider"] == "John Doe"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_insider_tx_dataframe_ok(client, _activate_responses):
    path = f"insider-trading/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "transactions": [
            {
                "date": "2024-01-15",
                "insider": "John Doe",
                "relationship": "CFO",
                "transactionType": "Sale",
                "shares": 5000,
                "pricePerShare": 155.0,
                "totalValue": 775000,
                "sharesOwned": 50000,
            },
            {
                "date": "2024-01-10",
                "insider": "Jane Smith",
                "relationship": "CTO",
                "transactionType": "Purchase",
                "shares": 2000,
                "pricePerShare": 150.0,
                "totalValue": 300000,
                "sharesOwned": 30000,
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.insider_transactions.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"insider", "relationship", "transactionType", "shares", "pricePerShare", "totalValue", "sharesOwned"}
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert pd.Timestamp("2024-01-10") in df.index
    assert df.loc["2024-01-10", "insider"] == "Jane Smith"
    assert df.loc["2024-01-15", "transactionType"] == "Sale"
    assert df.loc["2024-01-15", "shares"] == 5000


# ─────────── error mapping ──────────────────────────────────────────────
def test_insider_tx_bad_request(client, _activate_responses):
    path = f"insider-trading/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.insider_transactions.ticker(symbol=TICKER)
