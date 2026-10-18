"""
Supermarket Sales & Customer Analytics - Plotly Visualization Module
Module: src/visualization.py

Provides reusable, professionally styled Plotly figures:
- Unified typography, cohesive executive color palettes
- Clean hover tooltips with explicit currency/quantity formatting
- Responsive layouts with transparent/clean backgrounds
- Safe layout theming preventing duplicate keyword argument errors
- Strict text-overlap and text-overflow protection (isolated titles and legends, automargin enabled)
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


def get_layout_theme(**overrides) -> dict:
    """Return a clean copy of the layout theme with optional keyword overrides safely merged.

    Prevents text collisions and TypeError: got multiple values for keyword argument.
    Titles are anchored to the top-left, horizontal legends are placed cleanly below the plot area,
    and margins are configured to prevent label clipping.
    """
    theme = {
        "font": {"family": "Inter, Segoe UI, sans-serif", "size": 11, "color": "#2c3e50"},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(248,249,250,0.8)",
        "margin": {"l": 55, "r": 30, "t": 48, "b": 50},
        "title": {
            "font": {"size": 13, "color": "#0f172a"},
            "x": 0.02,
            "xanchor": "left",
            "y": 0.98,
            "yanchor": "top"
        },
        "legend": {
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "xanchor": "center",
            "x": 0.5,
            "title_text": "",
            "font": {"size": 10}
        }
    }
    for key, val in overrides.items():
        if key in theme and isinstance(theme[key], dict) and isinstance(val, dict):
            theme[key] = {**theme[key], **val}
        else:
            theme[key] = val
    return theme


def apply_layout_theme(fig: go.Figure, **overrides) -> go.Figure:
    """Safely apply layout theme to a Plotly figure without duplicate keyword argument errors."""
    layout_settings = get_layout_theme(**overrides)
    fig.update_layout(**layout_settings)
    return fig


# Exported default theme dict for backward compatibility
LAYOUT_THEME = get_layout_theme()


def plot_sales_trend(df_trend: pd.DataFrame, freq_name: str = "Month") -> go.Figure:
    """Plot temporal sales trend with transaction volume bars on dual axis."""
    if df_trend.empty:
        return go.Figure()

    fig = go.Figure()

    # Sales bar
    fig.add_trace(go.Bar(
        x=df_trend["Period"] if "Period" in df_trend.columns else df_trend["Date"],
        y=df_trend["Sales"],
        name="Total Sales (₹)",
        marker_color=PRIMARY_COLOR,
        hovertemplate="<b>Period:</b> %{x}<br><b>Sales:</b> ₹%{y:,.2f}<extra></extra>"
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

    apply_layout_theme(
        fig,
        title=dict(
            text=f"<b>Sales & Transaction Trend Over {freq_name}</b>",
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        xaxis=dict(title="", automargin=True),
        yaxis=dict(title="Sales (₹)", automargin=True, showgrid=True, gridcolor="#e2e8f0"),
        yaxis2=dict(title="Transactions", automargin=True, overlaying="y", side="right", showgrid=False),
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(t=48, b=65, l=60, r=60)
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
    show_legend: Optional[bool] = None
) -> go.Figure:
    """Generate standardized clean bar chart with safe layout and automargins.
    
    Prevents title/legend collisions and y-axis label clipping.
    """
    if df.empty:
        return go.Figure()

    # Determine whether a legend is needed when not explicitly set
    if show_legend is None:
        if color_col is None:
            show_legend = False
        elif (orientation == "h" and color_col == y_col) or (orientation == "v" and color_col == x_col):
            show_legend = False
        else:
            show_legend = False

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
            fig.update_traces(hovertemplate=f"<b>%{{y}}:</b> ₹%{{x:,.2f}}<extra></extra>")
        else:
            fig.update_traces(hovertemplate=f"<b>%{{y}}:</b> %{{x:,}}<extra></extra>")
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
            fig.update_traces(hovertemplate=f"<b>%{{x}}:</b> ₹%{{y:,.2f}}<extra></extra>")
        else:
            fig.update_traces(hovertemplate=f"<b>%{{x}}:</b> %{{y:,.2f}}<extra></extra>")

    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True, showgrid=True, gridcolor="#e2e8f0")

    if show_legend:
        apply_layout_theme(
            fig,
            showlegend=True,
            title=dict(text=f"<b>{title}</b>", x=0.02, y=0.98, xanchor="left", yanchor="top"),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.22,
                xanchor="center",
                x=0.5,
                font=dict(size=10)
            ),
            margin=dict(t=48, b=70, l=60, r=25)
        )
    else:
        apply_layout_theme(
            fig,
            showlegend=False,
            title=dict(text=f"<b>{title}</b>", x=0.02, y=0.98, xanchor="left", yanchor="top"),
            margin=dict(t=42, b=45, l=60, r=25)
        )

    return fig


def plot_donut(df: pd.DataFrame, names_col: str, values_col: str, title: str) -> go.Figure:
    """Generate clean donut chart with percentage labels and isolated bottom legend.
    
    Prevents text collision inside slices and title collisions at the top.
    """
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
        textinfo="percent",
        insidetextorientation="horizontal",
        hovertemplate="<b>%{label}</b><br>Sales: ₹%{value:,.2f}<br>Share: %{percent}<extra></extra>"
    )
    apply_layout_theme(
        fig,
        title=dict(text=f"<b>{title}</b>", x=0.02, y=0.98, xanchor="left", yanchor="top"),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(t=48, b=60, l=20, r=20)
    )
    return fig


def plot_scatter_quadrant(df: pd.DataFrame) -> go.Figure:
    """Generate product volume vs unit price scatter with bubble size proportional to sales.
    
    Uses concise title and bottom legend to prevent text overlap across wide/narrow viewports.
    """
    if df.empty:
        return go.Figure()

    fig = px.scatter(
        df,
        x="Avg_Unit_Price",
        y="Total_Quantity",
        size="Total_Sales",
        color="Category",
        hover_name="Product",
        title="<b>Product Matrix: Unit Price vs Quantity Sold</b>",
        color_discrete_sequence=CATEGORY_PALETTE,
        labels={"Avg_Unit_Price": "Avg Unit Price (₹)", "Total_Quantity": "Total Quantity (Units)"}
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Unit Price: ₹%{x:.2f}<br>Qty Sold: %{y}<extra></extra>"
    )
    fig.update_xaxes(automargin=True, showgrid=True, gridcolor="#e2e8f0")
    fig.update_yaxes(automargin=True, showgrid=True, gridcolor="#e2e8f0")
    apply_layout_theme(
        fig,
        title=dict(
            text="<b>Product Matrix: Unit Price vs Quantity Sold</b>",
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(t=48, b=80, l=60, r=30)
    )
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
    fig.update_xaxes(title="Rating (1 to 5)", automargin=True)
    fig.update_yaxes(title="Number of Reviews", automargin=True, showgrid=True, gridcolor="#e2e8f0")
    apply_layout_theme(
        fig,
        title=dict(
            text=f"<b>Customer Rating Distribution</b> (Mean = {avg_rating:.2f} / 5.0)",
            x=0.02,
            y=0.98,
            xanchor="left",
            yanchor="top"
        ),
        margin=dict(t=48, b=48, l=55, r=30)
    )
    return fig


def plot_grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    title: str,
    barmode: str = "group"
) -> go.Figure:
    """Generate grouped comparison bar chart with bottom legend and automargins."""
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
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True, showgrid=True, gridcolor="#e2e8f0")
    apply_layout_theme(
        fig,
        title=dict(text=f"<b>{title}</b>", x=0.02, y=0.98, xanchor="left", yanchor="top"),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.20,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(t=48, b=65, l=60, r=30)
    )
    return fig
