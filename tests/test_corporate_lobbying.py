# tests/test_corporate_lobbying.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AAPL"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_corporate_lobbying_raw_ok(client, _activate_responses):
    path = f"lobbying/{TICKER}"
    payload = wrap_v2({
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "filings": [
            {
                "date": "2024-03-15",
                "filingUuid": "abc-123",
                "filingYear": 2024,
                "quarter": "Q1",
                "clientName": "Apple Inc.",
                "registrantName": "Lobbying Firm LLC",
                "income": 50000,
                "expenses": 75000,
                "issueCodes": ["TAX", "ITC"],
                "governmentEntities": ["Congress", "Senate"],
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.corporate_lobbying.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["filings"], list)
    assert data["filings"][0]["registrantName"] == "Lobbying Firm LLC"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_corporate_lobbying_dataframe_ok(client, _activate_responses):
    path = f"lobbying/{TICKER}"
    payload = wrap_v2({
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "filings": [
            {
                "date": "2024-03-15",
                "filingUuid": "abc-123",
                "filingYear": 2024,
                "quarter": "Q1",
                "clientName": "Apple Inc.",
                "registrantName": "Lobbying Firm LLC",
                "income": 50000,
                "expenses": 75000,
                "issueCodes": ["TAX", "ITC"],
                "governmentEntities": ["Congress", "Senate"],
            },
            {
                "date": "2024-06-20",
                "filingUuid": "def-456",
                "filingYear": 2024,
                "quarter": "Q2",
                "clientName": "Apple Inc.",
                "registrantName": "Another Firm Inc.",
                "income": 30000,
                "expenses": 45000,
                "issueCodes": ["ENV"],
                "governmentEntities": ["Congress"],
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.corporate_lobbying.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "registrantName" in df.columns
    assert "income" in df.columns
    assert "expenses" in df.columns
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-03-15") in df.index
    assert pd.Timestamp("2024-06-20") in df.index
    assert df.loc["2024-03-15", "registrantName"] == "Lobbying Firm LLC"
    assert df.loc["2024-06-20", "income"] == 30000


# ─────────── error mapping ──────────────────────────────────────────────
def test_corporate_lobbying_bad_request(client, _activate_responses):
    path = f"lobbying/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.corporate_lobbying.ticker(symbol=TICKER)
