# tests/test_async_client.py
import pytest
import httpx
from finbrain.aio import AsyncFinBrainClient


@pytest.mark.asyncio
async def test_async_client_context_manager():
    """Test that async client works as context manager."""
    async with AsyncFinBrainClient(api_key="test_key") as client:
        assert client._client is not None
        assert isinstance(client._client, httpx.AsyncClient)

    # After context exit, client should be closed
    assert client._client is None


@pytest.mark.asyncio
async def test_async_client_missing_api_key():
    """Test that missing API key raises ValueError."""
    import os

    # Temporarily remove env var if it exists
    old_key = os.environ.pop("FINBRAIN_API_KEY", None)

    try:
        with pytest.raises(ValueError, match="API key missing"):
            AsyncFinBrainClient(api_key=None)
    finally:
        # Restore env var
        if old_key:
            os.environ["FINBRAIN_API_KEY"] = old_key


@pytest.mark.asyncio
async def test_async_client_not_initialized():
    """Test that using client without context manager raises RuntimeError."""
    client = AsyncFinBrainClient(api_key="test_key")

    with pytest.raises(RuntimeError, match="not initialized"):
        await client._request("GET", "test/path")


@pytest.mark.asyncio
async def test_async_client_close_method():
    """Test explicit close method."""
    client = AsyncFinBrainClient(api_key="test_key")

    async with client:
        assert client._client is not None

    # Already closed by context manager
    assert client._client is None

    # Should be safe to call again
    await client.close()
    assert client._client is None


@pytest.mark.asyncio
async def test_async_endpoints_exist():
    """Test that all async endpoint wrappers are initialized."""
    async with AsyncFinBrainClient(api_key="test_key") as client:
        assert hasattr(client, "available")
        assert hasattr(client, "predictions")
        assert hasattr(client, "sentiments")
        assert hasattr(client, "app_ratings")
        assert hasattr(client, "analyst_ratings")
        assert hasattr(client, "house_trades")
        assert hasattr(client, "insider_transactions")
        assert hasattr(client, "linkedin_data")
        assert hasattr(client, "options")
