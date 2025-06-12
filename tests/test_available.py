from finbrain.exceptions import BadRequest
from .conftest import stub_json
import pytest


def test_markets_ok(client, _activate_responses):
    stub_json(
        _activate_responses,
        "GET",
        "available/markets",
        {"availableMarkets": ["S&P 500", "NASDAQ"]},
    )
    assert client.available.markets() == ["S&P 500", "NASDAQ"]


def test_markets_bad_request(client, _activate_responses):
    stub_json(
        _activate_responses, "GET", "available/markets", {"message": "oops"}, status=400
    )
    with pytest.raises(BadRequest):
        client.available.markets()
