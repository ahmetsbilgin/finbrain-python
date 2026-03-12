# FinBrain Python SDK&nbsp;<!-- omit in toc -->

[![PyPI version](https://img.shields.io/pypi/v/finbrain-python.svg)](https://pypi.org/project/finbrain-python/)
[![CI](https://github.com/ahmetsbilgin/finbrain-python/actions/workflows/ci.yml/badge.svg)](https://github.com/ahmetsbilgin/finbrain-python/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

**Official Python client** for the [FinBrain API v2](https://docs.finbrain.tech).
Fetch deep-learning price predictions, sentiment scores, insider trades, LinkedIn metrics, options data, news and more — with a single import.

*Python ≥ 3.9  •  requests, pandas, numpy & plotly  •  asyncio optional.*

---

## ✨ Features

- One-line auth (`FinBrainClient(api_key="…")`) with Bearer token
- Complete v2 endpoint coverage (predictions, sentiments, options, insider, news, screener, etc.)
- Transparent retries & custom error hierarchy (`FinBrainError`)
- Response envelope auto-unwrapping (v2 `{success, data, meta}` format)
- Async parity with `finbrain.aio` (`httpx`)
- Auto-version from Git tags (setuptools-scm)
- MIT-licensed, fully unit-tested

---

## 🚀 Quick start

Install the SDK:

```bash
pip install finbrain-python
```

Create a client and fetch data:

```python
from finbrain import FinBrainClient

fb = FinBrainClient(api_key="YOUR_KEY")        # create once, reuse below

# ---------- discovery ----------
fb.available.markets()                         # list markets with regions
fb.available.tickers("daily", as_dataframe=True)
fb.available.regions()                         # markets grouped by region

# ---------- app ratings ----------
fb.app_ratings.ticker("AMZN",
                      date_from="2025-01-01",
                      date_to="2025-06-30",
                      as_dataframe=True)

# ---------- analyst ratings ----------
fb.analyst_ratings.ticker("AMZN",
                          date_from="2025-01-01",
                          date_to="2025-06-30",
                          as_dataframe=True)

# ---------- house trades ----------
fb.house_trades.ticker("AMZN",
                       date_from="2025-01-01",
                       date_to="2025-06-30",
                       as_dataframe=True)

# ---------- senate trades ----------
fb.senate_trades.ticker("META",
                        date_from="2025-01-01",
                        date_to="2025-06-30",
                        as_dataframe=True)

# ---------- corporate lobbying ----------
fb.corporate_lobbying.ticker("AAPL",
                             date_from="2024-01-01",
                             date_to="2025-06-30",
                             as_dataframe=True)

# ---------- insider transactions ----------
fb.insider_transactions.ticker("AMZN", as_dataframe=True)

# ---------- LinkedIn metrics ----------
fb.linkedin_data.ticker("AMZN",
                        date_from="2025-01-01",
                        date_to="2025-06-30",
                        as_dataframe=True)

# ---------- options put/call ----------
fb.options.put_call("AMZN",
                    date_from="2025-01-01",
                    date_to="2025-06-30",
                    as_dataframe=True)

# ---------- price predictions ----------
fb.predictions.ticker("AMZN", as_dataframe=True)

# ---------- news sentiment ----------
fb.sentiments.ticker("AMZN",
                     date_from="2025-01-01",
                     date_to="2025-06-30",
                     as_dataframe=True)

# ---------- news articles ----------
fb.news.ticker("AMZN", limit=20, as_dataframe=True)

# ---------- screener (cross-ticker) ----------
fb.screener.sentiment(market="S&P 500", as_dataframe=True)
fb.screener.predictions_daily(limit=100, as_dataframe=True)
fb.screener.insider_trading(limit=50)

# ---------- recent data ----------
fb.recent.news(limit=100, as_dataframe=True)
fb.recent.analyst_ratings(limit=50)
```

## ⚡ Async Usage

For async/await support, install with the `async` extra:

```bash
pip install finbrain-python[async]
```

Then use `AsyncFinBrainClient` with `httpx`:

```python
import asyncio
from finbrain.aio import AsyncFinBrainClient

async def main():
    async with AsyncFinBrainClient(api_key="YOUR_KEY") as fb:
        # All methods are async and return the same data structures
        markets = await fb.available.markets()

        # Fetch predictions
        predictions = await fb.predictions.ticker("AMZN", as_dataframe=True)

        # Fetch sentiment data
        sentiment = await fb.sentiments.ticker(
            "AMZN",
            date_from="2025-01-01",
            date_to="2025-06-30",
            as_dataframe=True
        )

        # All other endpoints work the same way
        app_ratings = await fb.app_ratings.ticker("AMZN", as_dataframe=True)
        analyst_ratings = await fb.analyst_ratings.ticker("AMZN", as_dataframe=True)
        news = await fb.news.ticker("AMZN", limit=10)
        screener = await fb.screener.sentiment(market="S&P 500")

asyncio.run(main())
```

**Note**: The async client uses `httpx.AsyncClient` and must be used with `async with` context manager for proper resource cleanup.

## 📈 Plotting

Plot helpers in a nutshell

- `show` – defaults to True, so the chart appears immediately.

- `as_json=True` – skips display and returns the figure as a Plotly-JSON string, ready to embed elsewhere.

```python
# ---------- App Ratings Chart - Apple App Store or Google Play Store ----------
fb.plot.app_ratings("AMZN",
                    store="app",                # "play" for Google Play Store
                    date_from="2025-01-01",
                    date_to="2025-06-30")

# ---------- LinkedIn Metrics Chart ----------
fb.plot.linkedin("AMZN",
                 date_from="2025-01-01",
                 date_to="2025-06-30")

# ---------- Put-Call Ratio Chart ----------
fb.plot.options("AMZN",
                kind="put_call",
                date_from="2025-01-01",
                date_to="2025-06-30")

# ---------- Predictions Chart ----------
fb.plot.predictions("AMZN")         # prediction_type="monthly" for monthly predictions

# ---------- Sentiments Chart ----------
fb.plot.sentiments("AMZN",
                   date_from="2025-01-01",
                   date_to="2025-06-30")

# ---------- Insider Transactions, House & Senate Trades, Corporate Lobbying (requires user price data) ----------
# These plots overlay transaction markers on a price chart.
# Since FinBrain doesn't provide historical prices, you must provide your own:

import pandas as pd

# Example: Load your price data from any legal source
# (broker API, licensed data provider, CSV file, etc.)
price_df = pd.DataFrame({
    "close": [150.25, 151.30, 149.80],  # Your price data
    "date": pd.date_range("2025-01-01", periods=3)
}).set_index("date")

# Plot insider transactions on your price chart
fb.plot.insider_transactions("AAPL", price_data=price_df)

# Plot House member trades on your price chart
fb.plot.house_trades("NVDA",
                     price_data=price_df,
                     date_from="2025-01-01",
                     date_to="2025-06-30")

# Plot Senate member trades on your price chart
fb.plot.senate_trades("META",
                      price_data=price_df,
                      date_from="2025-01-01",
                      date_to="2025-06-30")

# Plot corporate lobbying spend on your price chart
fb.plot.corporate_lobbying("AAPL",
                           price_data=price_df,
                           date_from="2024-01-01",
                           date_to="2025-06-30")
```

**Price Data Requirements:**

- DataFrame with DatetimeIndex
- Must contain a price column: `close`, `Close`, `price`, `Price`, `adj_close`, or `Adj Close`
- Obtain from legal sources: broker API, Bloomberg, Alpha Vantage, FMP, etc.

## 🔑 Authentication

To call the API you need an **API key**, obtained by purchasing a **FinBrain API subscription**.
*(The Terminal-only subscription does **not** include an API key.)*

1. Subscribe at <https://www.finbrain.tech> → FinBrain API.
2. Copy the key from your dashboard.
3. Pass it once when you create the client:

```python
from finbrain import FinBrainClient
fb = FinBrainClient(api_key="YOUR_KEY")
```

Or set the `FINBRAIN_API_KEY` environment variable and omit the argument:

```python
fb = FinBrainClient()  # reads from FINBRAIN_API_KEY env var
```

---

## 📚 Supported endpoints

| Category             | Method                                   | v2 Path                                     |
|----------------------|------------------------------------------|---------------------------------------------|
| Discovery            | `client.available.markets()`             | `/markets`                                  |
|                      | `client.available.tickers()`             | `/tickers`                                  |
|                      | `client.available.regions()`             | `/regions`                                  |
| Predictions          | `client.predictions.ticker()`            | `/predictions/{daily\|monthly}/{SYMBOL}`    |
| Sentiments           | `client.sentiments.ticker()`             | `/sentiment/{SYMBOL}`                       |
| News                 | `client.news.ticker()`                   | `/news/{SYMBOL}`                            |
| App ratings          | `client.app_ratings.ticker()`            | `/app-ratings/{SYMBOL}`                     |
| Analyst ratings      | `client.analyst_ratings.ticker()`        | `/analyst-ratings/{SYMBOL}`                 |
| House trades         | `client.house_trades.ticker()`           | `/congress/house/{SYMBOL}`                  |
| Senate trades        | `client.senate_trades.ticker()`          | `/congress/senate/{SYMBOL}`                 |
| Corporate lobbying   | `client.corporate_lobbying.ticker()`     | `/lobbying/{SYMBOL}`                        |
| Insider transactions | `client.insider_transactions.ticker()`   | `/insider-trading/{SYMBOL}`                 |
| LinkedIn             | `client.linkedin_data.ticker()`          | `/linkedin/{SYMBOL}`                        |
| Options – Put/Call   | `client.options.put_call()`              | `/put-call-ratio/{SYMBOL}`                  |
| Screener             | `client.screener.sentiment()`            | `/screener/sentiment`                       |
|                      | `client.screener.predictions_daily()`    | `/screener/predictions/daily`               |
|                      | `client.screener.insider_trading()`      | `/screener/insider-trading`                 |
|                      | ... and 8 more screener methods          |                                             |
| Recent               | `client.recent.news()`                   | `/recent/news`                              |
|                      | `client.recent.analyst_ratings()`        | `/recent/analyst-ratings`                   |

---

## 🛠️ Error-handling

```python
from finbrain.exceptions import BadRequest
try:
    fb.predictions.ticker("MSFT", prediction_type="weekly")
except BadRequest as exc:
    print("Invalid parameters:", exc)
    print("Error code:", exc.error_code)        # e.g. "VALIDATION_ERROR"
    print("Details:", exc.error_details)         # structured details dict
```

| HTTP status | Exception class          | Meaning                               |
|-------------|--------------------------|---------------------------------------|
| 400         | `BadRequest`             | The request is invalid or malformed   |
| 401         | `AuthenticationError`    | API key missing or incorrect          |
| 403         | `PermissionDenied`       | Authenticated, but not authorised     |
| 404         | `NotFound`               | Resource or endpoint not found        |
| 405         | `MethodNotAllowed`       | HTTP method not supported on endpoint |
| 429         | `RateLimitError`         | Too many requests                     |
| 500         | `ServerError`            | FinBrain internal error               |

---

## 🔄 Versioning & release

- Semantic Versioning (`MAJOR.MINOR.PATCH`)

- Version auto-generated from Git tags (setuptools-scm)

```bash
git tag -a v0.2.0 -m "v2 API migration"
git push --tags # GitHub Actions builds & uploads to PyPI
```

---

## 🧑‍💻 Development

```bash
git clone https://github.com/finbrain-tech/finbrain-python
cd finbrain-python
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]

ruff check . # lint / format
pytest -q # unit tests (mocked)
```

---

## 🤝 Contributing

1. Fork → create a feature branch

2. Add tests & run `ruff check --fix`

3. Ensure `pytest` & CI pass

4. Open a PR — thanks!

---

## 🔒 Security

Please report vulnerabilities to **<info@finbrain.tech>**.
We respond within 48 hours.

---

## 📜 License

MIT — see [LICENSE](LICENSE).

---

© 2026 FinBrain Technologies — Built with ❤️ for the quant community.
