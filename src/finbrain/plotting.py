# src/finbrain/plotting.py
from __future__ import annotations
from typing import Union, TYPE_CHECKING
import numpy as np
import pandas as pd
import plotly.graph_objects as go

if TYPE_CHECKING:  # imported only by static-type tools
    from .client import FinBrainClient


class _PlotNamespace:
    """
    Internal helper that hangs off FinBrainClient as `client.plot`.
    Each public method should return either a Plotly Figure or a JSON string.
    """

    def __init__(self, parent: "FinBrainClient"):
        self._fb = parent  # keep a reference to the main client

    # ────────────────────────────────────────────────────────────────────────────
    #  App-ratings plot  •  bars = counts  •  lines = scores
    # ────────────────────────────────────────────────────────────────────────────
    def app_ratings(
        self,
        ticker: str,
        *,
        store: str = "play",
        date_from: str | None = None,
        date_to: str | None = None,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kwargs,
    ):
        """
        Plot ratings for a single mobile store (Google Play **or** Apple App Store).

        Bars  → ratings count • primary y-axis (auto-scaled)
        Line  → average score • secondary y-axis (auto-scaled within 0-5)

        Parameters
        ----------
        store : {'play', 'app'}, default 'play'
            Which store to visualise.
        Other args/kwargs identical to the other plotting wrappers.
        """
        # 1) pull data
        df = self._fb.app_ratings.ticker(
            ticker,
            date_from=date_from,
            date_to=date_to,
            as_dataframe=True,
            **kwargs,
        )

        # 2) pick columns & colours
        s = store.lower()
        if s in ("play", "playstore", "google", "android"):
            count_col, score_col = "android_ratingsCount", "android_score"
            count_name, score_name = "Android Ratings Count", "Android Score"
            count_color, score_color = "rgba(0,190,0,0.65)", "#02d2ff"
        elif s in ("app", "appstore", "apple", "ios"):
            count_col, score_col = "ios_ratingsCount", "ios_score"
            count_name, score_name = "iOS Ratings Count", "iOS Score"
            count_color, score_color = "rgba(0,190,0,0.65)", "#02d2ff"
        else:
            raise ValueError("store must be 'play' or 'app'")

        # 3) dynamic axis ranges
        max_cnt = float(df[count_col].max())
        min_cnt = float(df[count_col].min())

        # raw span; fall back to max_cnt when all bars are equal
        span = max_cnt - min_cnt
        pad = (span if span else max_cnt) * 0.10  # 10 % of the data spread

        cnt_lower = max(0.0, min_cnt - pad)
        cnt_upper = max_cnt + pad

        # scores (secondary axis) – same as before
        score_min, score_max = float(df[score_col].min()), float(df[score_col].max())
        pad = 0.25
        score_lower = max(0, score_min - pad)
        score_upper = min(5, score_max + pad)

        # 4) build figure
        fig = go.Figure(
            layout=dict(
                template=template,
                title=f"{score_name.split()[0]} · {ticker}",
                hovermode="x unified",
            )
        )

        fig.add_bar(
            name=count_name, x=df.index, y=df[count_col], marker_color=count_color
        )
        fig.add_scatter(
            name=score_name,
            x=df.index,
            y=df[score_col],
            mode="lines",
            line=dict(width=2, color=score_color),
            yaxis="y2",
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis=dict(
                title="Ratings Count",
                range=[cnt_lower, cnt_upper],
                fixedrange=True,
                showgrid=True,
            ),
            yaxis2=dict(
                title="Score",
                overlaying="y",
                side="right",
                range=[score_lower, score_upper],
                fixedrange=True,
                showgrid=False,
                zeroline=False,
            ),
        )

        # 5) show / return
        if show and not as_json:
            fig.show()
            return None
        return fig.to_json() if as_json else fig

    # ────────────────────────────────────────────────────────────────────────────
    #  LinkedIn plot  •  bars = employeeCount  •  line = followerCount
    # ────────────────────────────────────────────────────────────────────────────
    def linkedin(
        self,
        ticker: str,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kwargs,
    ):
        """
        Plot LinkedIn company metrics.

        * **Bars**   → ``employeeCount`` (primary y-axis)
        * **Line**   → ``followerCount`` (secondary y-axis)
        """
        df = self._fb.linkedin_data.ticker(
            ticker,
            date_from=date_from,
            date_to=date_to,
            as_dataframe=True,
            **kwargs,
        )

        fig = go.Figure(
            layout=dict(
                template=template,
                title=f"LinkedIn Metrics · {ticker}",
                hovermode="x unified",
            )
        )

        # employees (bars)
        fig.add_bar(
            name="Employees",
            x=df.index,
            y=df["employeeCount"],
            marker_color="rgba(0,190,0,0.6)",
        )

        # followers (line on secondary axis)
        fig.add_scatter(
            name="Followers",
            x=df.index,
            y=df["followerCount"],
            mode="lines",
            line=dict(width=2, color="#f9c80e"),
            yaxis="y2",
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis=dict(title="Employee Count", showgrid=True),
            yaxis2=dict(
                title="Follower Count",
                overlaying="y",
                side="right",
                showgrid=False,
                zeroline=False,
            ),
        )

        if show and not as_json:
            fig.show()
            return None
        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Sentiment  → green/red bar                                             #
    # --------------------------------------------------------------------- #
    def sentiments(
        self,
        ticker: str,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kw,
    ) -> Union[go.Figure, str]:
        """
        Visualise FinBrain news-sentiment scores for a single ticker.

        A green bar represents a non-negative score (bullish news); a red
        bar represents a negative score (bearish news).  Bars are plotted on
        the primary y-axis, with dates on the x-axis.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g. ``"AMZN"``).
        date_from, date_to : str or None, optional
            Inclusive date range in ``YYYY-MM-DD`` format.  If omitted,
            FinBrain returns its full available range.
        as_json : bool, default ``False``
            • ``False`` → return a :class:`plotly.graph_objects.Figure`.
            • ``True``  → return ``figure.to_json()`` (``str``).
        show : bool, default ``True``
            If ``True`` *and* ``as_json=False``, immediately display the
            figure via :meth:`plotly.graph_objects.Figure.show`.  When
            ``as_json=True`` this flag is ignored.
        template : str, default ``"plotly_dark"``
            Name of a built-in Plotly template.
        **kwargs
            Passed straight through to
            :meth:`FinBrainClient.sentiments.ticker`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
            *Figure*: when ``as_json=False`` **and** ``show=False``
            *str*   : JSON representation when ``as_json=True``
            *None*  : when ``show=True`` and the figure is already shown.

        Examples
        --------
        >>> fb.plot.sentiments("AMZN",
        ...                    date_from="2025-01-01",
        ...                    date_to="2025-05-31")
        """
        df: pd.DataFrame = self._fb.sentiments.ticker(
            ticker,
            date_from=date_from,
            date_to=date_to,
            as_dataframe=True,
            **kw,
        )

        # 2) build colour array: green for ≥0, red for <0
        colors = np.where(
            df["sentiment"] >= 0, "rgba(0,190,0,0.8)", "rgba(190,0,0,0.8)"
        )

        # 3) bar chart (index on x-axis, sentiment on y-axis)
        fig = go.Figure(
            data=[
                go.Bar(
                    x=df.index,
                    y=df["sentiment"],
                    marker_color=colors,
                    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Sentiment: %{y:.3f}<extra></extra>",
                )
            ],
            layout=dict(
                template=template,
                title=f"News Sentiment · {ticker}",
                xaxis_title="Date",
                yaxis_title="Sentiment Score",
                hovermode="x unified",
            ),
        )

        if show and not as_json:  # don't “show” raw JSON
            fig.show()
            return None  # <- silences the echo

        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Put/Call ratios  → stacked bars + ratio line                           #
    # --------------------------------------------------------------------- #
    def options(
        self,
        ticker: str,
        *,
        kind: str = "put_call",
        date_from=None,
        date_to=None,
        as_json=False,
        show=True,
        template="plotly_dark",
        **kw,
    ):
        """
        Plot options-market activity for a given ticker.

        Currently implemented ``kind`` values
        --------------------------------------
        ``"put_call"`` (default)
            *Stacked* bars of ``callVolume`` (green, bottom) and
            ``putVolume`` (red, top) plus a yellow line for the ``ratio``
            on a secondary y-axis.

        Additional kinds can be added in future without changing the
        public API—just extend the internal ``elif`` block.

        Parameters
        ----------
        ticker : str
            Ticker symbol.
        kind : {'put_call', ...}, default ``"put_call"``
            Which visualisation to render.  Unknown values raise
            :class:`ValueError`.
        date_from, date_to, as_json, show, template, **kwargs
            Same semantics as :pymeth:`~_PlotNamespace.sentiments`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
            As described for :pymeth:`~_PlotNamespace.sentiments`.

        Examples
        --------
        >>> fb.plot.options("AMZN",
        ...                 kind="put_call",
        ...                 date_from="2025-01-01",
        ...                 date_to="2025-05-31")
        """
        if kind == "put_call":
            df = self._fb.options.put_call(
                ticker,
                date_from=date_from,
                date_to=date_to,
                as_dataframe=True,
                **kw,
            )
            fig = self._plot_put_call(df, ticker, template)  # helper below
        else:
            raise ValueError(f"Unknown kind '{kind}'. Supported values: 'put_call'")

        if show and not as_json:
            fig.show()
            return None  # <- silences the echo

        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Predictions  → price + CI band                                         #
    # --------------------------------------------------------------------- #
    def predictions(
        self,
        ticker: str,
        *,
        prediction_type: str = "daily",
        as_json=False,
        show=True,
        template="plotly_dark",
        **kw,
    ):
        """
        Plot FinBrain price predictions with confidence intervals.

        The figure shows the predicted price (solid line) and a shaded
        confidence band between the upper and lower bounds.

        Parameters
        ----------
        ticker : str
            Ticker symbol.
        prediction_type : {'daily', 'monthly'}, default ``"daily"``
            Granularity of the prediction data requested from FinBrain.
        as_json, show, template, **kwargs
            Same semantics as :pymeth:`~_PlotNamespace.sentiments`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
            As described for :pymeth:`~_PlotNamespace.sentiments`.

        Examples
        --------
        >>> fb.plot.predictions("AMZN", prediction_type="monthly")
        """
        df = self._fb.predictions.ticker(
            ticker, prediction_type=prediction_type, as_dataframe=True, **kw
        )

        fig = go.Figure(
            layout=dict(
                template=template,
                title=f"Price Prediction · {ticker}",
                xaxis_title="Date",
                yaxis_title="Price",
                hovermode="x unified",
            )
        )

        # add the three lines
        fig.add_scatter(x=df.index, y=df["mid"], mode="lines", name="Predicted")
        fig.add_scatter(
            x=df.index,
            y=df["upper"],
            mode="lines",
            name="Upper CI",
            line=dict(width=0),
            showlegend=False,
        )
        fig.add_scatter(
            x=df.index,
            y=df["lower"],
            mode="lines",
            name="Lower CI",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(2,210,255,0.2)",
            showlegend=False,
        )

        if show and not as_json:
            fig.show()
            return None  # <- silences the echo

        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Insider Transactions  → markers on price chart                        #
    # --------------------------------------------------------------------- #
    def insider_transactions(
        self,
        ticker: str,
        price_data: pd.DataFrame,
        *,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kwargs,
    ):
        """
        Plot insider transactions overlaid on a price chart.

        This method requires user-provided historical price data, as FinBrain
        does not currently offer a price history endpoint.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g. ``"AAPL"``).
        price_data : pandas.DataFrame
            **User-provided** price history with a DatetimeIndex and a column
            containing prices (e.g. ``"close"``, ``"Close"``, or ``"price"``).
            The index must be timezone-naive or UTC.
        as_json : bool, default False
            If ``True``, return JSON string instead of Figure object.
        show : bool, default True
            If ``True`` and ``as_json=False``, display the figure immediately.
        template : str, default "plotly_dark"
            Plotly template name.
        **kwargs
            Additional arguments passed to
            :meth:`FinBrainClient.insider_transactions.ticker`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
            Figure object, JSON string, or None (when shown).

        Raises
        ------
        ValueError
            If ``price_data`` is empty or missing required price column.

        Examples
        --------
        >>> import pandas as pd
        >>> # User provides their own price data from any legal source
        >>> price_df = pd.DataFrame({
        ...     "close": [150, 152, 151, 155],
        ...     "date": pd.date_range("2024-01-01", periods=4)
        ... }).set_index("date")
        >>> fb.plot.insider_transactions("AAPL", price_df)
        """
        # Validate price_data
        if price_data.empty:
            raise ValueError("price_data cannot be empty")

        # Flatten MultiIndex columns if present (e.g., from yf.download())
        if isinstance(price_data.columns, pd.MultiIndex):
            # Get the first level (price types like 'Close', 'Open', etc.)
            price_data = price_data.copy()
            price_data.columns = price_data.columns.get_level_values(0)

        # Find price column (case-insensitive search)
        price_col = None
        for col in ["close", "Close", "price", "Price", "adj_close", "Adj Close"]:
            if col in price_data.columns:
                price_col = col
                break
        if price_col is None:
            raise ValueError(
                f"price_data must contain a price column (e.g. 'close', 'Close', 'price'). "
                f"Found columns: {price_data.columns.tolist()}"
            )

        # Fetch insider transactions
        transactions_df = self._fb.insider_transactions.ticker(
            ticker, as_dataframe=True, **kwargs
        )

        fig = self._plot_transactions_on_price(
            price_data=price_data,
            price_col=price_col,
            transactions_df=transactions_df,
            ticker=ticker,
            template=template,
            transaction_type="Insider",
        )

        if show and not as_json:
            fig.show()
            return None
        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # House Trades  → markers on price chart                                #
    # --------------------------------------------------------------------- #
    def house_trades(
        self,
        ticker: str,
        price_data: pd.DataFrame,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kwargs,
    ):
        """
        Plot U.S. House member trades overlaid on a price chart.

        This method requires user-provided historical price data, as FinBrain
        does not currently offer a price history endpoint.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g. ``"AAPL"``).
        price_data : pandas.DataFrame
            **User-provided** price history with a DatetimeIndex and a column
            containing prices (e.g. ``"close"``, ``"Close"``, or ``"price"``).
            The index must be timezone-naive or UTC.
        date_from, date_to : str or None, optional
            Date range for transactions in ``YYYY-MM-DD`` format.
        as_json : bool, default False
            If ``True``, return JSON string instead of Figure object.
        show : bool, default True
            If ``True`` and ``as_json=False``, display the figure immediately.
        template : str, default "plotly_dark"
            Plotly template name.
        **kwargs
            Additional arguments passed to
            :meth:`FinBrainClient.house_trades.ticker`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
            Figure object, JSON string, or None (when shown).

        Raises
        ------
        ValueError
            If ``price_data`` is empty or missing required price column.

        Examples
        --------
        >>> import pandas as pd
        >>> # User provides their own price data from any legal source
        >>> price_df = pd.DataFrame({
        ...     "close": [150, 152, 151, 155],
        ...     "date": pd.date_range("2024-01-01", periods=4)
        ... }).set_index("date")
        >>> fb.plot.house_trades("AAPL", price_df,
        ...                      date_from="2024-01-01", date_to="2024-12-31")
        """
        # Validate price_data
        if price_data.empty:
            raise ValueError("price_data cannot be empty")

        # Flatten MultiIndex columns if present (e.g., from yf.download())
        if isinstance(price_data.columns, pd.MultiIndex):
            # Get the first level (price types like 'Close', 'Open', etc.)
            price_data = price_data.copy()
            price_data.columns = price_data.columns.get_level_values(0)

        # Find price column (case-insensitive search)
        price_col = None
        for col in ["close", "Close", "price", "Price", "adj_close", "Adj Close"]:
            if col in price_data.columns:
                price_col = col
                break
        if price_col is None:
            raise ValueError(
                f"price_data must contain a price column (e.g. 'close', 'Close', 'price'). "
                f"Found columns: {price_data.columns.tolist()}"
            )

        # Fetch house trades
        transactions_df = self._fb.house_trades.ticker(
            ticker,
            date_from=date_from,
            date_to=date_to,
            as_dataframe=True,
            **kwargs,
        )

        fig = self._plot_transactions_on_price(
            price_data=price_data,
            price_col=price_col,
            transactions_df=transactions_df,
            ticker=ticker,
            template=template,
            transaction_type="House",
        )

        if show and not as_json:
            fig.show()
            return None
        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Senate Trades  → markers on price chart                               #
    # --------------------------------------------------------------------- #
    def senate_trades(
        self,
        ticker: str,
        price_data: pd.DataFrame,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kwargs,
    ):
        """
        Plot U.S. Senate member trades overlaid on a price chart.

        This method requires user-provided historical price data, as FinBrain
        does not currently offer a price history endpoint.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g. ``"META"``).
        price_data : pandas.DataFrame
            **User-provided** price history with a DatetimeIndex and a column
            containing prices (e.g. ``"close"``, ``"Close"``, or ``"price"``).
            The index must be timezone-naive or UTC.
        date_from, date_to : str or None, optional
            Date range for transactions in ``YYYY-MM-DD`` format.
        as_json : bool, default False
            If ``True``, return JSON string instead of Figure object.
        show : bool, default True
            If ``True`` and ``as_json=False``, display the figure immediately.
        template : str, default "plotly_dark"
            Plotly template name.
        **kwargs
            Additional arguments passed to
            :meth:`FinBrainClient.senate_trades.ticker`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
            Figure object, JSON string, or None (when shown).

        Raises
        ------
        ValueError
            If ``price_data`` is empty or missing required price column.

        Examples
        --------
        >>> import pandas as pd
        >>> # User provides their own price data from any legal source
        >>> price_df = pd.DataFrame({
        ...     "close": [500, 510, 505, 520],
        ...     "date": pd.date_range("2024-01-01", periods=4)
        ... }).set_index("date")
        >>> fb.plot.senate_trades("META", price_df,
        ...                       date_from="2024-01-01", date_to="2024-12-31")
        """
        # Validate price_data
        if price_data.empty:
            raise ValueError("price_data cannot be empty")

        # Flatten MultiIndex columns if present (e.g., from yf.download())
        if isinstance(price_data.columns, pd.MultiIndex):
            # Get the first level (price types like 'Close', 'Open', etc.)
            price_data = price_data.copy()
            price_data.columns = price_data.columns.get_level_values(0)

        # Find price column (case-insensitive search)
        price_col = None
        for col in ["close", "Close", "price", "Price", "adj_close", "Adj Close"]:
            if col in price_data.columns:
                price_col = col
                break
        if price_col is None:
            raise ValueError(
                f"price_data must contain a price column (e.g. 'close', 'Close', 'price'). "
                f"Found columns: {price_data.columns.tolist()}"
            )

        # Fetch senate trades
        transactions_df = self._fb.senate_trades.ticker(
            ticker,
            date_from=date_from,
            date_to=date_to,
            as_dataframe=True,
            **kwargs,
        )

        fig = self._plot_transactions_on_price(
            price_data=price_data,
            price_col=price_col,
            transactions_df=transactions_df,
            ticker=ticker,
            template=template,
            transaction_type="Senate",
        )

        if show and not as_json:
            fig.show()
            return None
        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Corporate Lobbying  → bars on price chart                              #
    # --------------------------------------------------------------------- #
    def corporate_lobbying(
        self,
        ticker: str,
        price_data: pd.DataFrame,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kwargs,
    ):
        """
        Plot corporate lobbying spend overlaid on a price chart.

        This method requires user-provided historical price data, as FinBrain
        does not currently offer a price history endpoint.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g. ``"AAPL"``).
        price_data : pandas.DataFrame
            **User-provided** price history with a DatetimeIndex and a column
            containing prices (e.g. ``"close"``, ``"Close"``, or ``"price"``).
            The index must be timezone-naive or UTC.
        date_from, date_to : str or None, optional
            Date range for filings in ``YYYY-MM-DD`` format.
        as_json : bool, default False
            If ``True``, return JSON string instead of Figure object.
        show : bool, default True
            If ``True`` and ``as_json=False``, display the figure immediately.
        template : str, default "plotly_dark"
            Plotly template name.
        **kwargs
            Additional arguments passed to
            :meth:`FinBrainClient.corporate_lobbying.ticker`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
            Figure object, JSON string, or None (when shown).

        Raises
        ------
        ValueError
            If ``price_data`` is empty or missing required price column.
        """
        # Validate price_data
        if price_data.empty:
            raise ValueError("price_data cannot be empty")

        # Flatten MultiIndex columns if present (e.g., from yf.download())
        if isinstance(price_data.columns, pd.MultiIndex):
            price_data = price_data.copy()
            price_data.columns = price_data.columns.get_level_values(0)

        # Find price column (case-insensitive search)
        price_col = None
        for col in ["close", "Close", "price", "Price", "adj_close", "Adj Close"]:
            if col in price_data.columns:
                price_col = col
                break
        if price_col is None:
            raise ValueError(
                f"price_data must contain a price column (e.g. 'close', 'Close', 'price'). "
                f"Found columns: {price_data.columns.tolist()}"
            )

        # Fetch lobbying filings
        filings_df = self._fb.corporate_lobbying.ticker(
            ticker,
            date_from=date_from,
            date_to=date_to,
            as_dataframe=True,
            **kwargs,
        )

        # Normalize timezones
        price_data_normalized = price_data.copy()
        if price_data_normalized.index.tz is not None:
            price_data_normalized.index = price_data_normalized.index.tz_localize(None)

        fig = go.Figure(
            layout=dict(
                template=template,
                title=f"Corporate Lobbying · {ticker}",
                xaxis_title="Date",
                hovermode="x unified",
            )
        )

        # Plot price line on primary y-axis
        fig.add_scatter(
            name="Price",
            x=price_data_normalized.index,
            y=price_data_normalized[price_col],
            mode="lines",
            line=dict(width=2, color="#02d2ff"),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Price: $%{y:.2f}<extra></extra>",
        )

        if not filings_df.empty:
            filings_normalized = filings_df.copy()
            if filings_normalized.index.tz is not None:
                filings_normalized.index = filings_normalized.index.tz_localize(None)

            # Compute total spend per filing (income + expenses)
            spend = filings_normalized.get("income", 0) + filings_normalized.get(
                "expenses", 0
            )

            hover_text = []
            for _, row in filings_normalized.iterrows():
                registrant = row.get("registrantName", "N/A")
                quarter = row.get("quarter", "")
                income = row.get("income", 0)
                expenses = row.get("expenses", 0)
                hover_text.append(
                    f"Registrant: {registrant}<br>"
                    f"Quarter: {quarter}<br>"
                    f"Income: ${income:,.0f}<br>"
                    f"Expenses: ${expenses:,.0f}"
                )

            # Plot lobbying spend as bars on secondary y-axis
            fig.add_bar(
                name="Lobbying Spend",
                x=filings_normalized.index,
                y=spend,
                marker_color="rgba(249,200,14,0.6)",
                yaxis="y2",
                hovertext=hover_text,
                hovertemplate="<b>%{x|%Y-%m-%d}</b><br>%{hovertext}<extra></extra>",
            )

        fig.update_layout(
            yaxis=dict(title="Price", showgrid=True),
            yaxis2=dict(
                title="Lobbying Spend ($)",
                overlaying="y",
                side="right",
                showgrid=False,
                zeroline=False,
                rangemode="tozero",
            ),
        )

        if show and not as_json:
            fig.show()
            return None
        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Reddit Mentions  → bars on price chart                                 #
    # --------------------------------------------------------------------- #
    def reddit_mentions(
        self,
        ticker: str,
        price_data: pd.DataFrame,
        *,
        date_from: str | None = None,
        date_to: str | None = None,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kwargs,
    ):
        """
        Plot Reddit mention counts overlaid on a price chart.

        This method requires user-provided historical price data, as FinBrain
        does not currently offer a price history endpoint.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g. ``"AAPL"``).
        price_data : pandas.DataFrame
            **User-provided** price history with a DatetimeIndex and a column
            containing prices (e.g. ``"close"``, ``"Close"``, or ``"price"``).
            The index must be timezone-naive or UTC.
        date_from, date_to : str or None, optional
            Date range for mentions in ``YYYY-MM-DD`` format.
        as_json : bool, default False
            If ``True``, return JSON string instead of Figure object.
        show : bool, default True
            If ``True`` and ``as_json=False``, display the figure immediately.
        template : str, default "plotly_dark"
            Plotly template name.
        **kwargs
            Additional arguments passed to
            :meth:`FinBrainClient.reddit_mentions.ticker`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
            Figure object, JSON string, or None (when shown).

        Raises
        ------
        ValueError
            If ``price_data`` is empty or missing required price column.
        """
        # Validate price_data
        if price_data.empty:
            raise ValueError("price_data cannot be empty")

        # Flatten MultiIndex columns if present (e.g., from yf.download())
        if isinstance(price_data.columns, pd.MultiIndex):
            price_data = price_data.copy()
            price_data.columns = price_data.columns.get_level_values(0)

        # Find price column (case-insensitive search)
        price_col = None
        for col in ["close", "Close", "price", "Price", "adj_close", "Adj Close"]:
            if col in price_data.columns:
                price_col = col
                break
        if price_col is None:
            raise ValueError(
                f"price_data must contain a price column (e.g. 'close', 'Close', 'price'). "
                f"Found columns: {price_data.columns.tolist()}"
            )

        # Fetch Reddit mentions
        mentions_df = self._fb.reddit_mentions.ticker(
            ticker,
            date_from=date_from,
            date_to=date_to,
            as_dataframe=True,
            **kwargs,
        )

        # Normalize timezones
        price_data_normalized = price_data.copy()
        if price_data_normalized.index.tz is not None:
            price_data_normalized.index = price_data_normalized.index.tz_localize(None)

        fig = go.Figure(
            layout=dict(
                template=template,
                title=f"Reddit Mentions · {ticker}",
                xaxis_title="Date",
                hovermode="x unified",
            )
        )

        # Plot price line on primary y-axis
        fig.add_scatter(
            name="Price",
            x=price_data_normalized.index,
            y=price_data_normalized[price_col],
            mode="lines",
            line=dict(width=2, color="#02d2ff"),
            hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>Price: $%{y:.2f}<extra></extra>",
        )

        if not mentions_df.empty:
            mentions_normalized = mentions_df.copy()
            if mentions_normalized.index.tz is not None:
                mentions_normalized.index = mentions_normalized.index.tz_localize(None)

            # Exclude _all (aggregate) — use individual subreddits for stacked bars
            per_sub = mentions_normalized[
                mentions_normalized["subreddit"] != "_all"
            ]

            if not per_sub.empty:
                for subreddit in sorted(per_sub["subreddit"].unique()):
                    sub_data = per_sub[per_sub["subreddit"] == subreddit]
                    fig.add_bar(
                        name=f"r/{subreddit}",
                        x=sub_data.index,
                        y=sub_data["mentions"],
                        yaxis="y2",
                        hovertemplate=(
                            "<b>%{x|%Y-%m-%d %H:%M}</b><br>"
                            f"r/{subreddit}: " + "%{y:,}<extra></extra>"
                        ),
                    )

        fig.update_layout(
            barmode="stack",
            yaxis=dict(title="Price", showgrid=True),
            yaxis2=dict(
                title="Mentions",
                overlaying="y",
                side="right",
                showgrid=False,
                zeroline=False,
                rangemode="tozero",
            ),
        )

        if show and not as_json:
            fig.show()
            return None
        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Reddit Mentions Screener  → stacked horizontal bars (top N tickers)    #
    # --------------------------------------------------------------------- #
    def reddit_mentions_screener(
        self,
        *,
        top_n: int = 15,
        market: str | None = None,
        region: str | None = None,
        limit: int | None = None,
        as_json: bool = False,
        show: bool = True,
        template: str = "plotly_dark",
        **kwargs,
    ):
        """
        Plot a stacked horizontal bar chart of the most mentioned tickers
        from the latest Reddit mentions screener snapshot.

        Parameters
        ----------
        top_n : int, default 15
            Number of top-mentioned tickers to display.
        market : str or None, optional
            Filter by market name (e.g. ``"S&P 500"``).
        region : str or None, optional
            Filter by region (e.g. ``"US"``).
        limit : int or None, optional
            Maximum records to fetch from the screener API.
        as_json : bool, default False
            If ``True``, return JSON string instead of Figure object.
        show : bool, default True
            If ``True`` and ``as_json=False``, display the figure immediately.
        template : str, default "plotly_dark"
            Plotly template name.
        **kwargs
            Additional arguments passed to
            :meth:`FinBrainClient.reddit_mentions.screener`.

        Returns
        -------
        plotly.graph_objects.Figure or str or None
        """
        data = self._fb.reddit_mentions.screener(
            market=market,
            region=region,
            limit=limit,
            **kwargs,
        )

        rows = data.get("data", [])
        if not rows:
            raise ValueError("No screener data returned")

        # Keep only the latest snapshot per ticker
        latest: dict[str, dict] = {}
        for row in rows:
            sym = row["symbol"]
            if sym not in latest or row["date"] > latest[sym]["date"]:
                latest[sym] = row

        # Sort by totalMentions descending, take top N
        ranked = sorted(latest.values(), key=lambda r: r.get("totalMentions", 0), reverse=True)
        top = ranked[:top_n]

        # Reverse so the highest-mentioned ticker is at the top of the chart
        top = list(reversed(top))

        symbols = [r["symbol"] for r in top]

        # Collect all subreddit names across top tickers
        all_subs: set[str] = set()
        for r in top:
            all_subs.update(r.get("subreddits", {}).keys())

        fig = go.Figure(
            layout=dict(
                template=template,
                title=f"Reddit Mentions · Top {len(top)} Tickers",
                xaxis_title="Mentions",
                hovermode="y unified",
                barmode="stack",
            )
        )

        for subreddit in sorted(all_subs):
            values = [r.get("subreddits", {}).get(subreddit, 0) for r in top]
            fig.add_bar(
                name=f"r/{subreddit}",
                y=symbols,
                x=values,
                orientation="h",
                hovertemplate=f"r/{subreddit}: " + "%{x:,}<extra></extra>",
            )

        if show and not as_json:
            fig.show()
            return None
        return fig.to_json() if as_json else fig

    # --------------------------------------------------------------------- #
    # Helper methods                                                         #
    # --------------------------------------------------------------------- #

    @staticmethod
    def _plot_transactions_on_price(
        price_data: pd.DataFrame,
        price_col: str,
        transactions_df: pd.DataFrame,
        ticker: str,
        template: str,
        transaction_type: str,
    ) -> go.Figure:
        """
        Helper to plot transaction markers on a price chart.

        Parameters
        ----------
        price_data : pd.DataFrame
            Price history with DatetimeIndex.
        price_col : str
            Name of the price column in price_data.
        transactions_df : pd.DataFrame
            Transaction data with DatetimeIndex and a 'transactionType' column
            (v2 API), or legacy 'transaction'/'type' column.
        ticker : str
            Ticker symbol for title.
        template : str
            Plotly template.
        transaction_type : str
            "Insider" or "House" for labeling.

        Returns
        -------
        go.Figure
        """
        # Normalize timezones - convert both to timezone-naive for comparison
        # yfinance often returns timezone-aware data, FinBrain returns naive
        price_data_normalized = price_data.copy()
        if price_data_normalized.index.tz is not None:
            price_data_normalized.index = price_data_normalized.index.tz_localize(None)

        transactions_df_normalized = transactions_df.copy()
        if transactions_df_normalized.index.tz is not None:
            transactions_df_normalized.index = (
                transactions_df_normalized.index.tz_localize(None)
            )

        fig = go.Figure(
            layout=dict(
                template=template,
                title=f"{transaction_type} Transactions · {ticker}",
                xaxis_title="Date",
                yaxis_title="Price",
                hovermode="x unified",
            )
        )

        # Plot price line
        fig.add_scatter(
            name="Price",
            x=price_data_normalized.index,
            y=price_data_normalized[price_col],
            mode="lines",
            line=dict(width=2, color="#02d2ff"),
            hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Price: $%{y:.2f}<extra></extra>",
        )

        if transactions_df_normalized.empty:
            # No transactions to plot
            return fig

        # Determine which column contains transaction type
        # v2 API uses 'transactionType'; fall back to legacy column names
        if "transactionType" in transactions_df_normalized.columns:
            tx_col = "transactionType"
        elif "transaction" in transactions_df_normalized.columns:
            tx_col = "transaction"
        else:
            tx_col = "type"

        # Separate buy and sell transactions
        buys = transactions_df_normalized[
            transactions_df_normalized[tx_col].str.contains(
                "Buy|Purchase", case=False, na=False
            )
        ]
        sells = transactions_df_normalized[
            transactions_df_normalized[tx_col].str.contains(
                "Sell|Sale", case=False, na=False
            )
        ]

        # For each transaction, find the closest price date
        def get_price_at_date(tx_date):
            """Find closest available price for a transaction date."""
            if tx_date in price_data_normalized.index:
                return price_data_normalized.loc[tx_date, price_col]
            # Find nearest date
            idx = price_data_normalized.index.get_indexer([tx_date], method="nearest")[
                0
            ]
            if idx >= 0 and idx < len(price_data_normalized):
                return price_data_normalized.iloc[idx][price_col]
            return None

        # Plot buy markers
        if not buys.empty:
            buy_prices = [get_price_at_date(dt) for dt in buys.index]
            # Filter out None values
            valid_buys = [
                (dt, p) for dt, p in zip(buys.index, buy_prices) if p is not None
            ]
            if valid_buys:
                buy_dates, buy_vals = zip(*valid_buys)
                fig.add_scatter(
                    name="Buy",
                    x=buy_dates,
                    y=buy_vals,
                    mode="markers",
                    marker=dict(
                        size=10, color="rgba(0,255,0,0.8)", symbol="triangle-up"
                    ),
                    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>BUY<extra></extra>",
                )

        # Plot sell markers
        if not sells.empty:
            sell_prices = [get_price_at_date(dt) for dt in sells.index]
            # Filter out None values
            valid_sells = [
                (dt, p) for dt, p in zip(sells.index, sell_prices) if p is not None
            ]
            if valid_sells:
                sell_dates, sell_vals = zip(*valid_sells)
                fig.add_scatter(
                    name="Sell",
                    x=sell_dates,
                    y=sell_vals,
                    mode="markers",
                    marker=dict(
                        size=10, color="rgba(255,0,0,0.8)", symbol="triangle-down"
                    ),
                    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>SELL<extra></extra>",
                )

        return fig

    @staticmethod
    def _plot_put_call(df, ticker, template):
        fig = go.Figure(
            layout=dict(
                template=template,
                title=f"Options Activity · {ticker}",
                hovermode="x unified",
                barmode="stack",
            )
        )

        # Calls (green)  - added first so it sits *below* in the stack
        fig.add_bar(
            name="Calls",
            x=df.index,
            y=df["callVolume"],
            marker_color="rgba(0,190,0,0.6)",
        )
        # Puts (red) - added second so it appears *on top* of Calls
        fig.add_bar(
            name="Puts", x=df.index, y=df["putVolume"], marker_color="rgba(190,0,0,0.6)"
        )
        # Put/Call ratio line (secondary axis)
        fig.add_scatter(
            name="Put/Call Ratio",
            x=df.index,
            y=df["ratio"],
            mode="lines",
            line=dict(width=2, color="#F9C80E"),
            yaxis="y2",
        )

        # axes & layout tweaks
        fig.update_layout(
            xaxis_title="Date",
            yaxis=dict(
                title="Volume",
                showgrid=True,
            ),
            yaxis2=dict(
                title="Ratio",
                overlaying="y",
                side="right",
                rangemode="tozero",
                showgrid=False,
                zeroline=False,
            ),
        )

        return fig
