"""
Supermarket Sales & Customer Analytics - Plotly Visualization Module
Module: src/visualization.py

Provides reusable, professionally styled Plotly figures:
- Unified typography, cohesive executive color palettes
- Clean hover tooltips with explicit currency/quantity formatting
- Responsive layouts with transparent/clean backgrounds
"""

from typing import Optional, List
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Color Palette: Corporate Slate / Deep Navy / Vibrant Teal / Warm Amber
PRIMARY_COLOR = "#1f4e79"
SECONDARY_COLOR = "#008080"
ACCENT_COLOR = "#e67e22"
SUCCESS_COLOR = "#27ae60"
MUTED_COLOR = "#7f8c8d"

CATEGORY_PALETTE = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728",
    "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"
]

LAYOUT_THEME = {
    "font": {"family": "Inter, Segoe UI, sans-serif", "size": 12, "color": "#2c3e50"},
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(248,249,250,0.8)",
    "margin": {"l": 40, "r": 30, "t": 50, "b": 40},
    "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1}
}


def plot_sales_trend(df_trend: pd.DataFrame, freq_name: str = "Month") -> go.Figure:
    """Plot temporal sales trend with transaction volume bars on dual axis."""
    if df_trend.empty:
        return go.Figure()

    fig = go.Figure()

    # Sales bar
    fig.add_trace(go.Bar(
        x=df_trend["Period"] if "Period" in df_trend.columns else df_trend["Date"],
        y=df_trend["Sales"],
        name="Total Sales (Rs.)",
        marker_color=PRIMARY_COLOR,
        hovertemplate="<b>Period:</b> %{x}<br><b>Sales:</b> Rs. %{y:,.2f}<extra></extra>"
    ))

    # Transaction count line
    if "Transactions" in df_trend.columns:
        fig.add_trace(go.Scatter(
            x=df_trend["Period"] if "Period" in df_trend.columns else df_trend["Date"],
            y=df_trend["Transactions"],
            name="Transactions",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color=ACCENT_COLOR, width=3),
            marker=dict(size=8),
            hovertemplate="<b>Transactions:</b> %{y}<extra></extra>"
        ))

    fig.update_layout(
        **LAYOUT_THEME,
        title=f"<b>Sales & Transaction Trend Over {freq_name}</b>",
        xaxis_title="",
        yaxis=dict(title="Sales (Rs.)", showgrid=True, gridcolor="#e2e8f0"),
        yaxis2=dict(title="Transactions", overlaying="y", side="right", showgrid=False),
        hovermode="x unified"
    )
    return fig


def plot_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: Optional[str] = None,
    orientation: str = "v",
    format_currency: bool = True
) -> go.Figure:
    """Generate standardized clean bar chart."""
    if df.empty:
        return go.Figure()

    if orientation == "h":
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            orientation="h",
            color=color_col if color_col else None,
            color_discrete_sequence=CATEGORY_PALETTE if color_col else [PRIMARY_COLOR],
            title=f"<b>{title}</b>"
        )
        if format_currency:
            fig.update_traces(hovertemplate=f"<b>%{{y}}:</b> Rs. %{{x:,.2f}}<extra></extra>")
    else:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            orientation="v",
            color=color_col if color_col else None,
            color_discrete_sequence=CATEGORY_PALETTE if color_col else [PRIMARY_COLOR],
            title=f"<b>{title}</b>"
        )
        if format_currency:
            fig.update_traces(hovertemplate=f"<b>%{{x}}:</b> Rs. %{{y:,.2f}}<extra></extra>")

    fig.update_layout(**LAYOUT_THEME)
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig


def plot_donut(df: pd.DataFrame, names_col: str, values_col: str, title: str) -> go.Figure:
    """Generate clean donut chart with percentage labels."""
    if df.empty:
        return go.Figure()

    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.45,
        color_discrete_sequence=CATEGORY_PALETTE,
        title=f"<b>{title}</b>"
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Sales: Rs. %{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )
    fig.update_layout(**LAYOUT_THEME)
    return fig


def plot_scatter_quadrant(df: pd.DataFrame) -> go.Figure:
    """Generate product volume vs unit price scatter with bubble size proportional to sales."""
    if df.empty:
        return go.Figure()

    fig = px.scatter(
        df,
        x="Avg_Unit_Price",
        y="Total_Quantity",
        size="Total_Sales",
        color="Category",
        hover_name="Product",
        title="<b>Product Matrix: Unit Price vs Total Quantity Sold</b> (Bubble Size = Sales)",
        color_discrete_sequence=CATEGORY_PALETTE,
        labels={"Avg_Unit_Price": "Avg Unit Price (Rs.)", "Total_Quantity": "Total Quantity (Units)"}
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Unit Price: Rs. %{x:.2f}<br>Qty Sold: %{y}<extra></extra>"
    )
    fig.update_layout(**LAYOUT_THEME)
    fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0")
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig


def plot_rating_histogram(df: pd.DataFrame) -> go.Figure:
    """Plot customer rating distribution histogram with average line."""
    if df.empty:
        return go.Figure()

    avg_rating = df["Rating"].mean()
    fig = px.histogram(
        df,
        x="Rating",
        nbins=20,
        color_discrete_sequence=[SECONDARY_COLOR],
        title=f"<b>Customer Rating Distribution</b> (Mean = {avg_rating:.2f} / 5.0)"
    )
    fig.add_vline(
        x=avg_rating,
        line_dash="dash",
        line_color=ACCENT_COLOR,
        annotation_text=f"Mean: {avg_rating:.2f}",
        annotation_position="top right"
    )
    fig.update_layout(**LAYOUT_THEME, xaxis_title="Rating (1 to 5)", yaxis_title="Number of Reviews")
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig


def plot_grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    title: str,
    barmode: str = "group"
) -> go.Figure:
    """Generate grouped comparison bar chart."""
    if df.empty:
        return go.Figure()

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        barmode=barmode,
        color_discrete_sequence=[PRIMARY_COLOR, ACCENT_COLOR, SECONDARY_COLOR],
        title=f"<b>{title}</b>"
    )
    fig.update_layout(**LAYOUT_THEME)
    fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0")
    return fig
