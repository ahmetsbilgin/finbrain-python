from __future__ import annotations

import pytest
import responses
from urllib.parse import urljoin, urlencode
from finbrain import FinBrainClient

BASE = "https://api.finbrain.tech/v2/"


# ------------------------------------------------------------------ #
@pytest.fixture()
def client():
    # Use a dummy key; _request sends it as Bearer header
    return FinBrainClient(api_key="dummy", retries=0)


# ------------------------------------------------------------------ #
@pytest.fixture(autouse=True)
def _activate_responses(request):
    """Activate responses mock for every test — except integration tests."""
    if "integration" in {m.name for m in request.node.iter_markers()}:
        yield None
        return
    with responses.RequestsMock() as rsps:
        yield rsps


# ------------------------------------------------------------------ #


def wrap_v2(data):
    """Wrap payload in v2 response envelope."""
    return {
        "success": True,
        "data": data,
        "meta": {"timestamp": "2025-01-17T12:00:00.000Z"},
    }


def stub_json(
    rsps,
    method: str,
    path: str,
    json,
    *,
    status: int = 200,
    params: dict[str, str] | None = None,
):
    url = urljoin(BASE, path)
    if params:
        url = url + "?" + urlencode(params)
    rsps.add(method, url, json=json, status=status)
