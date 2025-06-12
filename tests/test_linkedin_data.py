# tests/test_linkedin_data.py
from .conftest import stub_json


def test_linkedin_ok(client, _activate_responses):
    path = "linkedindata/sp500/AMZN"
    stub_json(_activate_responses, "GET", path, {"ticker": "AMZN", "linkedinData": []})
    assert "linkedinData" in client.linkedin_data.ticker("sp500", "AMZN")
