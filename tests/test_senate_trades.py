# tests/test_senate_trades.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_senate_trades_raw_ok(client, _activate_responses):
    path = f"congress/senate/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "chamber": "senate",
        "trades": [
            {
                "date": "2024-01-15",
                "politician": "Shelley Moore Capito",
                "transactionType": "Purchase",
                "amount": "$1,001 - $15,000",
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.senate_trades.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["trades"], list)
    assert data["trades"][0]["politician"] == "Shelley Moore Capito"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_senate_trades_dataframe_ok(client, _activate_responses):
    path = f"congress/senate/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "chamber": "senate",
        "trades": [
            {
                "date": "2024-01-15",
                "politician": "Shelley Moore Capito",
                "transactionType": "Purchase",
                "amount": "$1,001 - $15,000",
            },
            {
                "date": "2024-01-08",
                "politician": "John Boozman",
                "transactionType": "Purchase",
                "amount": "$1,001 - $15,000",
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.senate_trades.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"politician", "transactionType", "amount"}
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert pd.Timestamp("2024-01-08") in df.index
    assert df.loc["2024-01-08", "politician"] == "John Boozman"
    assert df.loc["2024-01-15", "transactionType"] == "Purchase"
    assert df.loc["2024-01-08", "amount"] == "$1,001 - $15,000"


# ─────────── error mapping ──────────────────────────────────────────────
def test_senate_trades_bad_request(client, _activate_responses):
    path = f"congress/senate/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.senate_trades.ticker(symbol=TICKER)
