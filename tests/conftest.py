from __future__ import annotations

import pytest
import responses
from urllib.parse import urljoin, urlencode
from finbrain import FinBrainClient

BASE = "https://api.finbrain.tech/v1/"


# ------------------------------------------------------------------ #
@pytest.fixture()
def client():
    # Use a dummy key; _request adds it as ?token=dummy
    return FinBrainClient(api_key="dummy", retries=0)


# ------------------------------------------------------------------ #
@pytest.fixture(autouse=True)
def _activate_responses():
    """Activate responses for every test automatically."""
    with responses.RequestsMock() as rsps:
        yield rsps


# ------------------------------------------------------------------ #


def stub_json(
    rsps,
    method: str,
    path: str,
    json,
    *,
    status: int = 200,
    params: dict[str, str] | None = None,
):
    params = params or {}
    params["token"] = "dummy"  # always add token
    url = urljoin(BASE, path) + "?" + urlencode(params)
    rsps.add(method, url, json=json, status=status)
