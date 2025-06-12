# tests/test_options.py
from .conftest import stub_json


def test_put_call_ok(client, _activate_responses):
    path = "putcalldata/sp500/AMZN"
    stub_json(_activate_responses, "GET", path, {"ticker": "AMZN", "putCallData": []})
    assert "putCallData" in client.options.put_call("sp500", "AMZN")
