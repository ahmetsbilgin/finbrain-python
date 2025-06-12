# tests/test_house_trades.py
from .conftest import stub_json


def test_house_trades_ok(client, _activate_responses):
    path = "housetrades/sp500/AMZN"
    stub_json(_activate_responses, "GET", path, {"ticker": "AMZN", "houseTrades": []})
    assert "houseTrades" in client.house_trades.ticker("sp500", "AMZN")
