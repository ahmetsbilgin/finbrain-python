# tests/test_patent_filings.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AAPL"


def _sample_patents():
    return [
        {
            "patentId": "12345678",
            "patentDate": "2025-06-01",
            "title": "Method and apparatus for on-device machine learning",
            "type": "utility",
            "kind": "B2",
            "numClaims": 20,
            "numCitedBy": 5,
            "assigneeOrganization": "Apple Inc.",
            "assigneeType": "2",
            "applicationFilingDate": "2022-03-15",
            "filingToGrantDays": 808,
            "inventors": ["Jane Doe", "John Roe"],
            "numInventors": 2,
            "cpcSections": ["G", "H"],
            "cpcSubsections": ["G06", "H04"],
            "primaryCpcSection": "G",
        },
        {
            "patentId": "12345679",
            "patentDate": "2025-03-15",
            "title": "Display panel with adaptive refresh",
            "type": "utility",
            "kind": "B2",
            "numClaims": 15,
            "numCitedBy": 2,
            "assigneeOrganization": "Apple Inc.",
            "assigneeType": "2",
            "applicationFilingDate": "2021-11-01",
            "filingToGrantDays": 865,
            "inventors": ["Alice Smith"],
            "numInventors": 1,
            "cpcSections": ["G"],
            "cpcSubsections": ["G09"],
            "primaryCpcSection": "G",
        },
    ]


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_patent_filings_raw_ok(client, _activate_responses):
    path = f"patent-filings/{TICKER}"
    payload = wrap_v2({
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "patents": _sample_patents(),
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.patent_filings.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["patents"], list)
    assert len(data["patents"]) == 2
    assert data["patents"][0]["patentId"] == "12345678"
    assert data["patents"][0]["numClaims"] == 20
    assert data["patents"][0]["primaryCpcSection"] == "G"


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_patent_filings_dataframe_ok(client, _activate_responses):
    path = f"patent-filings/{TICKER}"
    payload = wrap_v2({
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "patents": _sample_patents(),
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.patent_filings.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "numClaims" in df.columns
    assert "title" in df.columns
    assert df.index.name == "patentDate"
    assert pd.api.types.is_datetime64_any_dtype(df.index)


# ─────────── with query params ──────────────────────────────────────────
def test_patent_filings_with_params(client, _activate_responses):
    path = f"patent-filings/{TICKER}"
    payload = wrap_v2({
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "patents": [],
    })
    stub_json(
        _activate_responses,
        "GET",
        path,
        payload,
        params={"startDate": "2025-01-01", "endDate": "2025-12-31", "limit": "10"},
    )

    data = client.patent_filings.ticker(
        symbol=TICKER,
        date_from="2025-01-01",
        date_to="2025-12-31",
        limit=10,
    )
    assert data["symbol"] == TICKER


# ─────────── error mapping ──────────────────────────────────────────────
def test_patent_filings_bad_request(client, _activate_responses):
    path = f"patent-filings/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.patent_filings.ticker(symbol=TICKER)


# ─────────── screener raw JSON ──────────────────────────────────────────
def test_patent_filings_screener_raw_ok(client, _activate_responses):
    path = "screener/patent-filings"
    payload = wrap_v2({
        "data": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "patentId": "12345678",
                "patentDate": "2025-06-01",
                "title": "On-device machine learning",
                "type": "utility",
                "assigneeOrganization": "Apple Inc.",
                "primaryCpcSection": "G",
                "numClaims": 20,
            },
        ],
        "summary": {
            "totalPatents": 1,
            "totalTickers": 1,
            "topCpcSections": ["G"],
        },
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.screener.patent_filings()
    assert isinstance(data, list)
    assert data[0]["symbol"] == "AAPL"
    assert data[0]["numClaims"] == 20


# ─────────── screener DataFrame ─────────────────────────────────────────
def test_patent_filings_screener_dataframe_ok(client, _activate_responses):
    path = "screener/patent-filings"
    payload = wrap_v2({
        "data": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "patentId": "12345678",
                "patentDate": "2025-06-01",
                "title": "On-device machine learning",
                "type": "utility",
                "assigneeOrganization": "Apple Inc.",
                "primaryCpcSection": "G",
                "numClaims": 20,
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "patentId": "12345699",
                "patentDate": "2025-05-20",
                "title": "Distributed training scheduler",
                "type": "utility",
                "assigneeOrganization": "Microsoft Technology Licensing, LLC",
                "primaryCpcSection": "G",
                "numClaims": 18,
            },
        ],
        "summary": {
            "totalPatents": 2,
            "totalTickers": 2,
            "topCpcSections": ["G"],
        },
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.screener.patent_filings(as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert df.index.name == "symbol"
    assert "numClaims" in df.columns
