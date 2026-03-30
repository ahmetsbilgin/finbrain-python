# tests/test_government_contracts.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "LMT"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_government_contracts_raw_ok(client, _activate_responses):
    path = f"government-contracts/{TICKER}"
    payload = wrap_v2({
        "symbol": "LMT",
        "name": "Lockheed Martin Corporation",
        "contracts": [
            {
                "awardId": "CONT_AWD_0001",
                "awardAmount": 50000000,
                "awardType": "",
                "awardingAgency": "Department of Defense",
                "awardingSubAgency": "Department of the Army",
                "recipientName": "Lockheed Martin Corporation",
                "startDate": "2025-06-01",
                "endDate": "2026-06-01",
                "description": "Aircraft maintenance services",
                "naicsCode": "336411",
                "naicsDescription": "Aircraft Manufacturing",
                "contractAwardType": "",
            },
            {
                "awardId": "CONT_AWD_0002",
                "awardAmount": 12000000,
                "awardType": "",
                "awardingAgency": "NASA",
                "awardingSubAgency": "NASA Headquarters",
                "recipientName": "Lockheed Martin Corporation",
                "startDate": "2025-03-15",
                "endDate": "2027-03-15",
                "description": "Space systems development",
                "naicsCode": "336414",
                "naicsDescription": "Guided Missile and Space Vehicle Manufacturing",
                "contractAwardType": "",
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.government_contracts.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["contracts"], list)
    assert len(data["contracts"]) == 2
    assert data["contracts"][0]["awardingAgency"] == "Department of Defense"
    assert data["contracts"][0]["awardAmount"] == 50000000


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_government_contracts_dataframe_ok(client, _activate_responses):
    path = f"government-contracts/{TICKER}"
    payload = wrap_v2({
        "symbol": "LMT",
        "name": "Lockheed Martin Corporation",
        "contracts": [
            {
                "awardId": "CONT_AWD_0001",
                "awardAmount": 50000000,
                "awardingAgency": "Department of Defense",
                "recipientName": "Lockheed Martin Corporation",
                "startDate": "2025-06-01",
                "endDate": "2026-06-01",
                "description": "Aircraft maintenance services",
                "naicsCode": "336411",
                "naicsDescription": "Aircraft Manufacturing",
            },
            {
                "awardId": "CONT_AWD_0002",
                "awardAmount": 12000000,
                "awardingAgency": "NASA",
                "recipientName": "Lockheed Martin Corporation",
                "startDate": "2025-03-15",
                "endDate": "2027-03-15",
                "description": "Space systems development",
                "naicsCode": "336414",
                "naicsDescription": "Guided Missile and Space Vehicle Manufacturing",
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.government_contracts.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "awardAmount" in df.columns
    assert "awardingAgency" in df.columns
    assert df.index.name == "startDate"
    assert pd.api.types.is_datetime64_any_dtype(df.index)


# ─────────── with query params ──────────────────────────────────────────
def test_government_contracts_with_params(client, _activate_responses):
    path = f"government-contracts/{TICKER}"
    payload = wrap_v2({
        "symbol": "LMT",
        "name": "Lockheed Martin Corporation",
        "contracts": [],
    })
    stub_json(
        _activate_responses,
        "GET",
        path,
        payload,
        params={"startDate": "2025-01-01", "endDate": "2025-12-31", "limit": "10"},
    )

    data = client.government_contracts.ticker(
        symbol=TICKER,
        date_from="2025-01-01",
        date_to="2025-12-31",
        limit=10,
    )
    assert data["symbol"] == TICKER


# ─────────── error mapping ──────────────────────────────────────────────
def test_government_contracts_bad_request(client, _activate_responses):
    path = f"government-contracts/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.government_contracts.ticker(symbol=TICKER)


# ─────────── screener raw JSON ──────────────────────────────────────────
def test_government_contracts_screener_raw_ok(client, _activate_responses):
    path = "screener/government-contracts"
    payload = wrap_v2({
        "data": [
            {
                "symbol": "LMT",
                "name": "Lockheed Martin Corporation",
                "awardId": "CONT_AWD_0001",
                "awardAmount": 50000000,
                "recipientName": "Lockheed Martin Corporation",
                "startDate": "2025-06-01",
                "awardingAgency": "Department of Defense",
                "naicsDescription": "Aircraft Manufacturing",
            },
        ],
        "summary": {
            "totalContracts": 1,
            "totalTickers": 1,
            "totalValue": 50000000,
        },
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.screener.government_contracts()
    assert isinstance(data, list)
    assert data[0]["symbol"] == "LMT"
    assert data[0]["awardAmount"] == 50000000


# ─────────── screener DataFrame ─────────────────────────────────────────
def test_government_contracts_screener_dataframe_ok(client, _activate_responses):
    path = "screener/government-contracts"
    payload = wrap_v2({
        "data": [
            {
                "symbol": "LMT",
                "name": "Lockheed Martin Corporation",
                "awardId": "CONT_AWD_0001",
                "awardAmount": 50000000,
                "recipientName": "Lockheed Martin Corporation",
                "startDate": "2025-06-01",
                "awardingAgency": "Department of Defense",
                "naicsDescription": "Aircraft Manufacturing",
            },
            {
                "symbol": "BA",
                "name": "The Boeing Company",
                "awardId": "CONT_AWD_0003",
                "awardAmount": 80000000,
                "recipientName": "The Boeing Company",
                "startDate": "2025-05-20",
                "awardingAgency": "Department of Defense",
                "naicsDescription": "Aircraft Manufacturing",
            },
        ],
        "summary": {
            "totalContracts": 2,
            "totalTickers": 2,
            "totalValue": 130000000,
        },
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.screener.government_contracts(as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert "awardAmount" in df.columns
