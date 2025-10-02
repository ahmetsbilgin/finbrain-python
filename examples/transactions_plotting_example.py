"""
Example: Plotting Insider Transactions and House Trades with User-Provided Price Data

This example demonstrates how to visualize insider transactions and House member trades
on a price chart. Since FinBrain doesn't provide historical price data, users must
bring their own price data from legal sources (e.g., their broker, Bloomberg, etc.).
"""

import os
import pandas as pd
from finbrain import FinBrainClient

# Initialize client
api_key = os.environ.get("FINBRAIN_API_KEY")
if not api_key:
    raise ValueError("Please set FINBRAIN_API_KEY environment variable")

fb = FinBrainClient(api_key=api_key)

# ============================================================================
# Example 1: Mock price data for demonstration
# ============================================================================
# In production, replace this with real price data from your legal source
# (broker API, Bloomberg, Alpha Vantage, yfinance with proper licensing, etc.)

mock_prices = pd.DataFrame({
    "date": pd.date_range("2024-01-01", "2024-12-31", freq="D"),
    "close": [150 + i * 0.5 for i in range(366)],  # Simulated price trend
})
mock_prices.set_index("date", inplace=True)

print("=" * 70)
print("Example 1: Insider Transactions with Mock Price Data")
print("=" * 70)

# Plot insider transactions for AAPL
# This will fetch real transaction data from FinBrain and overlay on your price data
fig_insider = fb.plot.insider_transactions(
    market="S&P 500",
    ticker="AAPL",
    price_data=mock_prices,
    show=False,  # Don't display immediately for this example
)

print(f"Created insider transactions plot with {len(fig_insider.data)} traces")
print("Green triangles (▲) = Buys | Red triangles (▼) = Sells")

# Uncomment to display the figure:
# fig_insider.show()

# ============================================================================
# Example 2: House Trades with Date Filtering
# ============================================================================
print("\n" + "=" * 70)
print("Example 2: House Trades with Date Filtering")
print("=" * 70)

# Plot House member trades for a specific date range
fig_house = fb.plot.house_trades(
    market="S&P 500",
    ticker="NVDA",
    price_data=mock_prices,
    date_from="2024-06-01",
    date_to="2024-12-31",
    show=False,
)

print(f"Created House trades plot with {len(fig_house.data)} traces")

# Uncomment to display the figure:
# fig_house.show()

# ============================================================================
# Example 3: Using Real Price Data (conceptual - adjust to your source)
# ============================================================================
print("\n" + "=" * 70)
print("Example 3: Integration with Real Price Data (Conceptual)")
print("=" * 70)

# Example pattern for integrating with real data sources:

# Option A: If you have CSV files from your broker
# real_prices = pd.read_csv("path/to/your/price_data.csv", parse_dates=["date"], index_col="date")

# Option B: If you have access to a licensed API (e.g., Alpha Vantage)
# import requests
# api_key = "your_alpha_vantage_key"
# response = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey={api_key}")
# # ... parse and create DataFrame ...

# Option C: If you have a Bloomberg Terminal subscription
# from blpapi import Session
# # ... Bloomberg API code ...

# Then use it with FinBrain plotting:
# fb.plot.insider_transactions("S&P 500", "AAPL", price_data=real_prices)

print("""
To use real price data, replace mock_prices with data from your legal source:
  - Broker API (Interactive Brokers, TD Ameritrade, etc.)
  - Licensed data provider (Bloomberg, Refinitiv, Alpha Vantage, etc.)
  - Your own database/warehouse

Required DataFrame format:
  - DatetimeIndex with dates
  - Column named 'close', 'Close', 'price', or 'Price'

Example:
             close
  date
  2024-01-01  150.25
  2024-01-02  151.30
  2024-01-03  149.80
""")

# ============================================================================
# Example 4: Exporting to JSON for web applications
# ============================================================================
print("\n" + "=" * 70)
print("Example 4: Export to JSON for Web Applications")
print("=" * 70)

# Get the plot as JSON (useful for web apps, dashboards, etc.)
json_plot = fb.plot.insider_transactions(
    market="S&P 500",
    ticker="TSLA",
    price_data=mock_prices,
    as_json=True,
    show=False,
)

print(f"Generated JSON plot (length: {len(json_plot)} characters)")
print("This can be sent to a web frontend using Plotly.js")

# Example: Save to file for web app
# with open("insider_plot.json", "w") as f:
#     f.write(json_plot)

print("\n" + "=" * 70)
print("Examples completed!")
print("=" * 70)
print("\nNote: To actually display the plots, uncomment the fig.show() lines above.")
print("Make sure you have real price data from a legal source for production use.")
