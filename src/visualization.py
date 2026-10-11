
"""
Supermarket Sales & Customer Analytics - Plotly Visualization Module
Module: src/visualization.py

Reusable Plotly charts with consistent styling, clean tooltips,
responsive layouts, and improved title/legend spacing.
"""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Corporate color palette
PRIMARY_COLOR = "#1f4e79"
SECONDARY_COLOR = "#008080"
ACCENT_COLOR = "#e67e22"
SUCCESS_COLOR = "#27ae60"
MUTED_COLOR = "#7f8c8d"

CATEGORY_PALETTE = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
]

# Shared layout: margin is defined only once.
LAYOUT_THEME = {
    "font": {
        "family": "Inter, Segoe UI, sans-serif",
        "size": 12,
        "color": "#e5e7eb",
    },
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "margin": {"l": 45, "r": 35, "t": 105, "b": 55},
    "legend": {
        "orientation": "h",
        "yanchor": "top",
        "y": -0.18,
        "xanchor": "center",
        "x": 0.5,
    },
}


def _apply_layout(
    fig: go.Figure,
    top: int = 105,
    bottom: int = 65,
    showlegend: Optional[bool] = None,
) -> go.Figure:
    """Apply shared layout safely without duplicate keyword arguments."""
    layout = LAYOUT_THEME.copy()
    layout["margin"] = {
        "l": 45,
        "r": 35,
        "t": top,
        "b": bottom,
    }

    if showlegend is not None:
        layout["showlegend"] = showlegend

    fig.update_layout(**layout)
    return fig


def _center_title(fig: go.Figure, title: str) -> None:
    """Center a chart title and reserve space above the plotting area."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "x": 0.5,
            "xanchor": "center",
            "y": 0.98,
            "yanchor": "top",
        }
    )


def plot_sales_trend(
    df_trend: pd.DataFrame,
    freq_name: str = "Month",
) -> go.Figure:
    """Plot sales over time with transaction counts on a secondary axis."""
    if df_trend.empty:
        return go.Figure()

    x_values = (
        df_trend["Period"]
        if "Period" in df_trend.columns
        else df_trend["Date"]
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=x_values,
            y=df_trend["Sales"],
            name="Total Sales (Rs.)",
            marker_color=PRIMARY_COLOR,
            hovertemplate=(
                "<b>Period:</b> %{x}<br>"
                "<b>Sales:</b> Rs. %{y:,.2f}<extra></extra>"
            ),
        )
    )

    if "Transactions" in df_trend.columns:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=df_trend["Transactions"],
                name="Transactions",
                yaxis="y2",
                mode="lines+markers",
                line={"color": ACCENT_COLOR, "width": 3},
                marker={"size": 8},
                hovertemplate=(
                    "<b>Transactions:</b> %{y}<extra></extra>"
                ),
            )
        )

    _apply_layout(fig, top=120, bottom=70)
    _center_title(fig, f"Sales & Transaction Trend Over {freq_name}")

    fig.update_layout(
        xaxis_title="",
        yaxis={
            "title": "Sales (Rs.)",
            "showgrid": True,
            "gridcolor": "#374151",
        },
        yaxis2={
            "title": "Transactions",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
        },
        hovermode="x unified",
    )

    return fig


def plot_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: Optional[str] = None,
    orientation: str = "v",
    format_currency: bool = True,
) -> go.Figure:
    """Generate a standardized bar chart with improved spacing."""
    if df.empty:
        return go.Figure()

    horizontal = orientation == "h"

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        orientation="h" if horizontal else "v",
        color=color_col if color_col else None,
        color_discrete_sequence=(
            CATEGORY_PALETTE if color_col else [PRIMARY_COLOR]
        ),
        title=f"<b>{title}</b>",
    )

    if format_currency:
        if horizontal:
            fig.update_traces(
                hovertemplate=(
                    f"<b>%{{y}}:</b> Rs. %{{x:,.2f}}<extra></extra>"
                )
            )
        else:
            fig.update_traces(
                hovertemplate=(
                    f"<b>%{{x}}:</b> Rs. %{{y:,.2f}}<extra></extra>"
                )
            )

    # Reserve room for the title and put the legend below the plot.
    _apply_layout(fig, top=120, bottom=95)
    _center_title(fig, title)

    fig.update_xaxes(
        showgrid=not horizontal,
        gridcolor="#374151",
        zerolinecolor="#6b7280",
    )
    fig.update_yaxes(
        showgrid=horizontal,
        gridcolor="#374151",
        zerolinecolor="#6b7280",
    )

    return fig


def plot_donut(
    df: pd.DataFrame,
    names_col: str,
    values_col: str,
    title: str,
) -> go.Figure:
    """Generate a donut chart with percentage labels."""
    if df.empty:
        return go.Figure()

    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        hole=0.45,
        color_discrete_sequence=CATEGORY_PALETTE,
        title=f"<b>{title}</b>",
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Sales: Rs. %{value:,.2f}<br>"
            "Share: %{percent}<extra></extra>"
        ),
    )

    _apply_layout(fig, top=110, bottom=65)
    _center_title(fig, title)

    return fig


def plot_scatter_quadrant(df: pd.DataFrame) -> go.Figure:
    """Plot average unit price against total quantity sold."""
    if df.empty:
        return go.Figure()

    fig = px.scatter(
        df,
        x="Avg_Unit_Price",
        y="Total_Quantity",
        size="Total_Sales",
        color="Category",
        hover_name="Product",
        title=(
            "<b>Product Matrix: Unit Price vs Total Quantity Sold</b>"
            " (Bubble Size = Sales)"
        ),
        color_discrete_sequence=CATEGORY_PALETTE,
        labels={
            "Avg_Unit_Price": "Avg Unit Price (Rs.)",
            "Total_Quantity": "Total Quantity (Units)",
        },
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Unit Price: Rs. %{x:.2f}<br>"
            "Qty Sold: %{y}<extra></extra>"
        )
    )

    _apply_layout(fig, top=125, bottom=65)
    _center_title(
        fig,
        "Product Matrix: Unit Price vs Total Quantity Sold"
        " (Bubble Size = Sales)",
    )

    fig.update_xaxes(showgrid=True, gridcolor="#374151")
    fig.update_yaxes(showgrid=True, gridcolor="#374151")

    return fig


def plot_rating_histogram(df: pd.DataFrame) -> go.Figure:
    """Plot customer rating distribution with a mean indicator."""
    if df.empty:
        return go.Figure()

    avg_rating = df["Rating"].mean()

    fig = px.histogram(
        df,
        x="Rating",
        nbins=20,
        color_discrete_sequence=[SECONDARY_COLOR],
        title=(
            f"<b>Customer Rating Distribution</b>"
            f" (Mean = {avg_rating:.2f} / 5.0)"
        ),
    )

    fig.add_vline(
        x=avg_rating,
        line_dash="dash",
        line_color=ACCENT_COLOR,
        annotation_text=f"Mean: {avg_rating:.2f}",
        annotation_position="top right",
    )

    _apply_layout(fig, top=125, bottom=65)
    _center_title(
        fig,
        f"Customer Rating Distribution (Mean = {avg_rating:.2f} / 5.0)",
    )

    fig.update_layout(
        xaxis_title="Rating (1 to 5)",
        yaxis_title="Number of Reviews",
    )
    fig.update_yaxes(showgrid=True, gridcolor="#374151")

    return fig


def plot_grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    title: str,
    barmode: str = "group",
) -> go.Figure:
    """Generate a grouped bar chart for comparisons."""
    if df.empty:
        return go.Figure()

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        barmode=barmode,
        color_discrete_sequence=[
            PRIMARY_COLOR,
            ACCENT_COLOR,
            SECONDARY_COLOR,
        ],
        title=f"<b>{title}</b>",
    )

    _apply_layout(fig, top=120, bottom=90)
    _center_title(fig, title)

    fig.update_yaxes(showgrid=True, gridcolor="#374151")

    return fig