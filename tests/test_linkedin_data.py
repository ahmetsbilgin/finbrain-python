# tests/test_linkedin_data.py
import pandas as pd
import pytest

from .conftest import stub_json, wrap_v2
from finbrain.exceptions import BadRequest

TICKER = "AMZN"


# ─────────── raw JSON branch ────────────────────────────────────────────
def test_linkedin_raw_ok(client, _activate_responses):
    path = f"linkedin/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "data": [
            {
                "date": "2024-01-15",
                "employeeCount": 1500000,
                "followerCount": 30000000,
                "jobCount": 5000,
            }
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    data = client.linkedin_data.ticker(symbol=TICKER)
    assert data["symbol"] == TICKER
    assert isinstance(data["data"], list)
    assert data["data"][0]["employeeCount"] == 1500000


# ─────────── DataFrame branch ───────────────────────────────────────────
def test_linkedin_dataframe_ok(client, _activate_responses):
    path = f"linkedin/{TICKER}"
    payload = wrap_v2({
        "symbol": "AMZN",
        "name": "Amazon.com Inc.",
        "data": [
            {
                "date": "2024-01-15",
                "employeeCount": 1500000,
                "followerCount": 30000000,
                "jobCount": 5000,
            },
            {
                "date": "2024-01-14",
                "employeeCount": 1499000,
                "followerCount": 29990000,
                "jobCount": 4900,
            },
        ],
    })

    stub_json(_activate_responses, "GET", path, payload)

    df = client.linkedin_data.ticker(symbol=TICKER, as_dataframe=True)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) == {"employeeCount", "followerCount", "jobCount"}
    assert df.index.name == "date"
    assert pd.api.types.is_datetime64_any_dtype(df.index)
    assert pd.Timestamp("2024-01-15") in df.index
    assert pd.Timestamp("2024-01-14") in df.index
    assert df.loc["2024-01-15", "followerCount"] == 30000000
    assert df.loc["2024-01-14", "employeeCount"] == 1499000
    assert df.loc["2024-01-14", "jobCount"] == 4900


# ─────────── error mapping ──────────────────────────────────────────────
def test_linkedin_bad_request(client, _activate_responses):
    path = f"linkedin/{TICKER}"
    stub_json(
        _activate_responses,
        "GET",
        path,
        {"success": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}},
        status=400,
    )

    with pytest.raises(BadRequest):
        client.linkedin_data.ticker(symbol=TICKER)
