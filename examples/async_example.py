"""
Example demonstrating async usage of FinBrain Python SDK.

Install with async support:
    pip install finbrain-python[async]

Run this example:
    python async_example.py
"""

import asyncio
import os
from finbrain.aio import AsyncFinBrainClient


async def fetch_data():
    """Fetch multiple data points concurrently."""
    api_key = os.getenv("FINBRAIN_API_KEY", "YOUR_KEY_HERE")

    async with AsyncFinBrainClient(api_key=api_key) as fb:
        # Example 1: Get available markets
        print("Fetching available markets...")
        markets = await fb.available.markets()
        print(f"✓ Found {len(markets)} markets: {markets[:3]}...")

        # Example 2: Get predictions for a ticker
        print("\nFetching predictions for AAPL...")
        predictions = await fb.predictions.ticker("AAPL", as_dataframe=True)
        print(f"✓ Retrieved {len(predictions)} prediction rows")
        print(predictions.head())

        # Example 3: Concurrent requests using asyncio.gather
        print("\nFetching multiple tickers concurrently...")
        tickers = ["AAPL", "MSFT", "GOOGL"]

        tasks = [
            fb.predictions.ticker(ticker, as_dataframe=True) for ticker in tickers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for ticker, result in zip(tickers, results):
            if isinstance(result, Exception):
                print(f"✗ {ticker}: {result}")
            else:
                print(f"✓ {ticker}: {len(result)} rows")


async def fetch_sentiment():
    """Fetch sentiment data for a specific stock."""
    api_key = os.getenv("FINBRAIN_API_KEY", "YOUR_KEY_HERE")

    async with AsyncFinBrainClient(api_key=api_key) as fb:
        print("\nFetching sentiment data for AMZN...")
        sentiment = await fb.sentiments.ticker(
            "S&P 500",
            "AMZN",
            date_from="2025-01-01",
            date_to="2025-06-30",
            as_dataframe=True,
        )
        print(f"✓ Retrieved {len(sentiment)} sentiment records")
        print(sentiment.head())


def main():
    """Run async examples."""
    print("=== FinBrain Async Client Examples ===\n")

    # Run examples
    asyncio.run(fetch_data())
    asyncio.run(fetch_sentiment())

    print("\n=== Examples completed ===")


if __name__ == "__main__":
    main()
