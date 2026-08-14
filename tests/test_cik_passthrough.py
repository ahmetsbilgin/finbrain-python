# tests/test_cik_passthrough.py
"""The four CIK-carrying datasets pass `cik` through untouched.

The SDK deliberately does not pin row fields, so `cik` (added to the v2 API
2026-08-14) must appear in both the raw-dict and DataFrame branches with no
SDK code changes. These tests pin that passthrough so a future refactor that
starts whitelisting columns fails loudly. `cik` is a 10-digit zero-padded
STRING (leading zeros are data); rows without an entity resolution carry null.
"""
import pandas as pd

from .conftest import stub_json, wrap_v2

CIK_AAPL = "0000320193"


def _one_row_payload(kind):
    if kind == "insider":
        return "insider-trading/AAPL", wrap_v2({
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "transactions": [
                {
                    "date": "2026-06-15",
                    "insider": "Jane Doe",
                    "relationship": "CFO",
                    "transactionType": "Sale",
                    "shares": 100,
                    "pricePerShare": 200.0,
                    "totalValue": 20000,
                    "sharesOwned": 5000,
                    "filingDate": "2026-06-17",
                    "filingUrl": "https://www.sec.gov/x",
                    "cik": CIK_AAPL,
                },
                {
                    "date": "2015-02-02",
                    "insider": "Old Filer",
                    "relationship": "Director",
                    "transactionType": "Sale",
                    "shares": 10,
                    "pricePerShare": 100.0,
                    "totalValue": 1000,
                    "sharesOwned": 50,
                    "filingDate": "2015-02-04",
                    "filingUrl": "https://www.sec.gov/y",
                    "cik": None,
                },
            ],
        }), "transactions"
    if kind == "contracts":
        return "government-contracts/AAPL", wrap_v2({
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "contracts": [
                {
                    "awardId": "AWD1",
                    "awardAmount": 1.0,
                    "awardType": "A",
                    "awardingAgency": "GSA",
                    "awardingSubAgency": "",
                    "recipientName": "APPLE INC",
                    "startDate": "2024-01-01",
                    "endDate": "2024-12-31",
                    "description": "",
                    "naicsCode": "",
                    "naicsDescription": "",
                    "contractAwardType": "",
                    "cik": CIK_AAPL,
                }
            ],
        }), "contracts"
    if kind == "lobbying":
        return "lobbying/AAPL", wrap_v2({
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "filings": [
                {
                    "date": "2026-01-21",
                    "filingUuid": "00000000-0000-0000-0000-000000000001",
                    "filingYear": 2025,
                    "quarter": "Q4",
                    "clientName": "Apple Inc.",
                    "registrantName": "Firm LLP",
                    "income": 0,
                    "expenses": 100000,
                    "issueCodes": ["TEC"],
                    "governmentEntities": ["SENATE"],
                    "cik": CIK_AAPL,
                }
            ],
        }), "filings"
    return "patent-filings/AAPL", wrap_v2({
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "patents": [
            {
                "patentId": "12345678",
                "patentDate": "2026-08-11",
                "title": "Widget",
                "type": "utility",
                "kind": "B2",
                "numClaims": 20,
                "numCitedBy": 0,
                "assigneeOrganization": "Apple Inc.",
                "assigneeType": "2",
                "applicationFilingDate": "2024-01-01",
                "filingToGrantDays": 953,
                "inventors": ["A B"],
                "numInventors": 1,
                "cpcSections": ["G"],
                "cpcSubsections": ["G06"],
                "primaryCpcSection": "G",
                "cik": CIK_AAPL,
            }
        ],
    }), "patents"


def test_insider_cik_raw_and_null(client, _activate_responses):
    path, payload, key = _one_row_payload("insider")
    stub_json(_activate_responses, "GET", path, payload)
    data = client.insider_transactions.ticker(symbol="AAPL")
    rows = data[key]
    assert rows[0]["cik"] == CIK_AAPL  # string, leading zeros intact
    assert rows[1]["cik"] is None  # honest blank passes through as null


def test_insider_cik_dataframe(client, _activate_responses):
    path, payload, key = _one_row_payload("insider")
    stub_json(_activate_responses, "GET", path, payload)
    df = client.insider_transactions.ticker(symbol="AAPL", as_dataframe=True)
    assert "cik" in df.columns
    assert df["cik"].iloc[0] == CIK_AAPL


def test_contracts_cik_raw(client, _activate_responses):
    path, payload, key = _one_row_payload("contracts")
    stub_json(_activate_responses, "GET", path, payload)
    data = client.government_contracts.ticker(symbol="AAPL")
    assert data[key][0]["cik"] == CIK_AAPL


def test_lobbying_cik_raw(client, _activate_responses):
    path, payload, key = _one_row_payload("lobbying")
    stub_json(_activate_responses, "GET", path, payload)
    data = client.corporate_lobbying.ticker(symbol="AAPL")
    assert data[key][0]["cik"] == CIK_AAPL


def test_patents_cik_dataframe(client, _activate_responses):
    path, payload, key = _one_row_payload("patents")
    stub_json(_activate_responses, "GET", path, payload)
    df = client.patent_filings.ticker(symbol="AAPL", as_dataframe=True)
    assert "cik" in df.columns
    assert df["cik"].iloc[0] == CIK_AAPL
    assert pd.api.types.is_object_dtype(df["cik"])  # stays a string column
