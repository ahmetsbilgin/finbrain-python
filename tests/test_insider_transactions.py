# tests/test_insider_transactions.py
from .conftest import stub_json


def test_insider_tx_ok(client, _activate_responses):
    path = "insidertransactions/sp500/AMZN"
    stub_json(
        _activate_responses, "GET", path, {"ticker": "AMZN", "insiderTransactions": []}
    )
    assert "insiderTransactions" in client.insider_transactions.ticker("sp500", "AMZN")
