# tests/test_house_trades.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_house_trades_raw_ok(client, _activate_responses):
    path = f"congress/house/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "chamber": "house",
        "trades": [
            {
                "date": "2024-01-15",
                "politician": "Nancy Pelosi",
                "transactionType": "Purchase",
                "amount": "$15,001 - $50,000",
                "owner": "JT",
                "amountRaw": "$15,001 - $50,000 *",
                "amountFlag": None,
                "disclosureDate": "2024-02-05",
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.house_trades.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["trades"], list)
    assert data["trades"][0]["politician"] == "Nancy Pelosi"
    assert data["trades"][0]["disclosureDate"] == "2024-02-05"
    assert data["trades"][0]["owner"] == "JT"
    # The bracket was normalized, so the originally filed string survives.
    assert data["trades"][0]["amountRaw"] == "$15,001 - $50,000 *"
    assert data["trades"][0]["amountFlag"] is None


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_house_trades_dataframe_ok(client, _activate_responses):
    path = f"congress/house/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "chamber": "house",
        "trades": [
            {
                "date": "2024-01-15",
                "politician": "Nancy Pelosi",
                "transactionType": "Purchase",
                "amount": "$15,001 - $50,000",
                "owner": "SP",
                "amountRaw": None,
                "amountFlag": None,
                "disclosureDate": "2024-02-05",
            },
            {
                "date": "2024-01-10",
                "politician": "Pete Sessions",
                "transactionType": "Sale",
                "amount": "Unknown",
                "owner": None,
                "amountRaw": None,
                "amountFlag": "review",
                "disclosureDate": None,
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.house_trades.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {
        "politician",
        "transactionType",
        "amount",
        "owner",
        "amountRaw",
        "amountFlag",
        "disclosureDate",
    }
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert pd.Timestamp("2024-01-10") in df.index
    assert df.loc["2024-01-10", "politician"] == "Pete Sessions"
    assert df.loc["2024-01-15", "transactionType"] == "Purchase"
    assert df.loc["2024-01-15", "amount"] == "$15,001 - $50,000"
    assert df.loc["2024-01-15", "disclosureDate"] == "2024-02-05"
    assert df.loc["2024-01-15", "owner"] == "SP"
    # A filing with no usable amount stores the explicit "Unknown"
    # placeholder and carries a review flag.
    assert df.loc["2024-01-10", "amount"] == "Unknown"
    assert df.loc["2024-01-10", "amountFlag"] == "review"
    # Historical rows predate the disclosure-date and owner fields; JSON null
    # becomes NaN once pandas builds the column.
    assert pd.isna(df.loc["2024-01-10", "disclosureDate"])
    assert pd.isna(df.loc["2024-01-10", "owner"])
    assert pd.isna(df.loc["2024-01-15", "amountFlag"])


# ─────────── error mapping ──────────────────────────────────────────────
def test_house_trades_bad_request(client, _activate_responses):
    path = f"congress/house/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.house_trades.ticker(symbol=TICKER)
