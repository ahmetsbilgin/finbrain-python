# tests/test_linkedin_data.py
import pandas as pd
import pytest
from urllib.parse import quote

from .conftest import stub_json
from finbrain.exceptions import BadRequest

MARKET = "S&P 500"
ENC_MARKET = quote(MARKET, safe="")  # → 'S%26P%20500'
TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_linkedin_raw_ok(client, _activate_responses):
    path = f"linkedindata/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "linkedinData": [
            {"date": "2024-03-20", "employeeCount": 755461, "followersCount": 30628460}
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    data = client.linkedin_data.ticker(MARKET, TICKER)
    assert data["ticker"] == TICKER
    assert isinstance(data["linkedinData"], list)
    assert data["linkedinData"][0]["employeeCount"] == 755461


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_linkedin_dataframe_ok(client, _activate_responses):
    path = f"linkedindata/{ENC_MARKET}/{TICKER}"
    payload = {
        "ticker": TICKER,
        "name": "Amazon.com Inc.",
        "linkedinData": [
            {"date": "2024-03-20", "employeeCount": 755461, "followersCount": 30628460},
            {"date": "2024-03-19", "employeeCount": 755000, "followersCount": 30600000},
        ],
    }

    stub_json(_activate_responses, "GET", path, payload)

    df = client.linkedin_data.ticker(MARKET, TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert df.index.name == "date"
    assert pd.Timestamp("2024-03-19") in df.index
    assert df.loc["2024-03-20", "followersCount"] == 30628460


# ─────────── error mapping ──────────────────────────────────────────────
def test_linkedin_bad_request(client, _activate_responses):
    path = f"linkedindata/{ENC_MARKET}/{TICKER}"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)

    with pytest.raises(BadRequest):
        client.linkedin_data.ticker(MARKET, TICKER)
