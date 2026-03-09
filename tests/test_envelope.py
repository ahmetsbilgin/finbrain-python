import pytest
import responses
from urllib.parse import urljoin
from finbrain import FinBrainClient
from finbrain.exceptions import (
    BadRequest, AuthenticationError, NotFound, RateLimitError
)

BASE = "https://api.finbrain.tech/v2/"


@pytest.fixture()
def client():
    return FinBrainClient(api_key="dummy", retries=0)


@pytest.fixture(autouse=True)
def _activate_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_envelope_unwraps_data(client, _activate_responses):
    """_request auto-unwraps the v2 envelope, returning just 'data'."""
    url = urljoin(BASE, "markets")
    _activate_responses.add("GET", url, json={
        "success": True,
        "data": [{"name": "S&P 500", "region": "US"}],
        "meta": {"timestamp": "2025-01-17T12:00:00.000Z"}
    })
    result = client._request("GET", "markets")
    assert result == [{"name": "S&P 500", "region": "US"}]


def test_envelope_stores_meta(client, _activate_responses):
    """_request stores meta on client.last_meta."""
    url = urljoin(BASE, "markets")
    _activate_responses.add("GET", url, json={
        "success": True,
        "data": [],
        "meta": {"timestamp": "2025-01-17T12:00:00.000Z"}
    })
    client._request("GET", "markets")
    assert client.last_meta == {"timestamp": "2025-01-17T12:00:00.000Z"}


def test_envelope_error_format_400(client, _activate_responses):
    """v2 error envelope with error.code and error.message."""
    url = urljoin(BASE, "sentiment/INVALID")
    _activate_responses.add("GET", url, json={
        "success": False,
        "error": {"code": "VALIDATION_ERROR", "message": "Invalid ticker symbol", "details": {"field": "symbol"}}
    }, status=400)
    with pytest.raises(BadRequest) as exc_info:
        client._request("GET", "sentiment/INVALID")
    assert "Invalid ticker symbol" in str(exc_info.value)
    assert exc_info.value.error_code == "VALIDATION_ERROR"
    assert exc_info.value.error_details == {"field": "symbol"}


def test_envelope_error_401(client, _activate_responses):
    url = urljoin(BASE, "markets")
    _activate_responses.add("GET", url, json={
        "success": False,
        "error": {"code": "UNAUTHORIZED", "message": "Authentication required"}
    }, status=401)
    with pytest.raises(AuthenticationError):
        client._request("GET", "markets")


def test_envelope_error_404(client, _activate_responses):
    url = urljoin(BASE, "sentiment/XYZ")
    _activate_responses.add("GET", url, json={
        "success": False,
        "error": {"code": "NOT_FOUND", "message": "Ticker not found"}
    }, status=404)
    with pytest.raises(NotFound):
        client._request("GET", "sentiment/XYZ")


def test_envelope_error_429(client, _activate_responses):
    url = urljoin(BASE, "markets")
    _activate_responses.add("GET", url, json={
        "success": False,
        "error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Too many requests"}
    }, status=429)
    with pytest.raises(RateLimitError):
        client._request("GET", "markets")


def test_bearer_auth_header(client, _activate_responses):
    """Client sends Authorization: Bearer header."""
    url = urljoin(BASE, "markets")
    _activate_responses.add("GET", url, json={"success": True, "data": [], "meta": {}})
    client._request("GET", "markets")
    assert _activate_responses.calls[0].request.headers["Authorization"] == "Bearer dummy"


def test_no_token_in_query_params(client, _activate_responses):
    """v2 client should NOT send token as query parameter."""
    url = urljoin(BASE, "markets")
    _activate_responses.add("GET", url, json={"success": True, "data": [], "meta": {}})
    client._request("GET", "markets")
    assert "token=" not in _activate_responses.calls[0].request.url


def test_last_meta_initially_none(client):
    """last_meta starts as None."""
    assert client.last_meta is None
