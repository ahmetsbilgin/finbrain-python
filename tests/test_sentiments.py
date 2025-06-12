from .conftest import stub_json


def test_sentiments_ok(client, _activate_responses):
    stub_json(
        _activate_responses,
        "GET",
        "sentiments/sp500/AMZN",
        {"ticker": "AMZN", "sentimentAnalysis": {}},
        params={"dateFrom": "2024-01-01", "dateTo": "2024-02-02"},
    )

    data = client.sentiments.ticker(
        market="sp500",
        symbol="AMZN",
        date_from="2024-01-01",
        date_to="2024-02-02",
    )
    assert data["ticker"] == "AMZN"
