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
        market: str,
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
            market,
            ticker,
            date_from=date_from,
            date_to=date_to,
            as_dataframe=True,
            **kwargs,
        )

        # 2) pick columns & colours
        s = store.lower()
        if s in ("play", "playstore", "google"):
            count_col, score_col = "playStoreRatingsCount", "playStoreScore"
            count_name, score_name = "Play Store Ratings Count", "Play Store Score"
            count_color, score_color = "rgba(0,190,0,0.65)", "#02d2ff"
        elif s in ("app", "appstore", "apple"):
            count_col, score_col = "appStoreRatingsCount", "appStoreScore"
            count_name, score_name = "App Store Ratings Count", "App Store Score"
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
    #  LinkedIn plot  •  bars = employeeCount  •  line = followersCount
    # ────────────────────────────────────────────────────────────────────────────
    def linkedin(
        self,
        market: str,
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
        * **Line**   → ``followersCount`` (secondary y-axis)
        """
        df = self._fb.linkedin_data.ticker(
            market,
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
            y=df["followersCount"],
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
        market: str,
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
        market : str
            Market identifier (e.g. ``"S&P 500"``).
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
        >>> fb.plot.sentiments("S&P 500", "AMZN",
        ...                    date_from="2025-01-01",
        ...                    date_to="2025-05-31")
        """
        df: pd.DataFrame = self._fb.sentiments.ticker(
            market,
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
        market: str,
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
            *Stacked* bars of ``callCount`` (green, bottom) and
            ``putCount`` (red, top) plus a yellow line for the ``ratio``
            on a secondary y-axis.

        Additional kinds can be added in future without changing the
        public API—just extend the internal ``elif`` block.

        Parameters
        ----------
        market, ticker : str
            Market identifier and ticker symbol.
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
        >>> fb.plot.options("S&P 500", "AMZN",
        ...                 kind="put_call",
        ...                 date_from="2025-01-01",
        ...                 date_to="2025-05-31")
        """
        if kind == "put_call":
            df = self._fb.options.put_call(
                market,
                ticker,
                date_from=date_from,
                date_to=date_to,
                as_dataframe=True,
                **kw,
            )
            fig = self._plot_put_call(df, ticker, template)  # helper below

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
        fig.add_scatter(x=df.index, y=df["main"], mode="lines", name="Predicted")
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
    # TODO: insider_transactions, house_trades, analyst_ratings ...         #
    # Add more methods here following the same pattern.                     #
    # --------------------------------------------------------------------- #

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
            y=df["callCount"],
            marker_color="rgba(0,190,0,0.6)",
        )
        # Puts (red) - added second so it appears *on top* of Calls
        fig.add_bar(
            name="Puts", x=df.index, y=df["putCount"], marker_color="rgba(190,0,0,0.6)"
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
