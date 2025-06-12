import pytest, responses
from finbrain.exceptions import BadRequest
from .conftest import stub_json


def test_ticker_predictions_ok(client, _activate_responses):
    path = "ticker/AAPL/predictions/daily"
    stub_json(_activate_responses, "GET", path, {"ticker": "AAPL", "prediction": {}})
    data = client.predictions.ticker("AAPL")
    assert data["ticker"] == "AAPL"


def test_market_predictions_invalid_type(client):
    with pytest.raises(ValueError):
        client.predictions.market("sp500", prediction_type="weekly")


def test_market_predictions_bad_request(client, _activate_responses):
    path = "market/sp500/predictions/daily"
    stub_json(_activate_responses, "GET", path, {"message": "bad"}, status=400)
    with pytest.raises(BadRequest):
        client.predictions.market("sp500")
