# tests/test_client.py
import pytest

from finbrain import FinBrainClient

# Every endpoint namespace that must be wired onto the sync client.
EXPECTED_ENDPOINTS = [
    "available",
    "predictions",
    "sentiments",
    "app_ratings",
    "analyst_ratings",
    "house_trades",
    "senate_trades",
    "insider_transactions",
    "linkedin_data",
    "options",
    "news",
    "screener",
    "recent",
    "corporate_lobbying",
    "reddit_mentions",
    "government_contracts",
    "patent_filings",
]


@pytest.fixture()
def client():
    return FinBrainClient(api_key="test_key")


@pytest.mark.parametrize("name", EXPECTED_ENDPOINTS)
def test_sync_endpoint_wired(client, name):
    """Each endpoint namespace is initialized on the sync client."""
    assert hasattr(client, name)


def test_sync_plot_namespace(client):
    assert hasattr(client, "plot")


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("FINBRAIN_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key missing"):
        FinBrainClient(api_key=None)
