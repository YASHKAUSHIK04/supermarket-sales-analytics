"""
Supermarket Sales & Customer Analytics Dashboard
Interactive Dashboard built with Streamlit, Plotly, and Pandas.

Author: Data Analyst Intern
Dataset: Supermarket Sales Dataset (500 Transactions)
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Add src to system path
sys.path.append(str(Path(__file__).resolve().parent))
from src.analysis import (
    load_data,
    compute_kpis,
    analyze_sales_over_time,
    aggregate_by_dimension,
    analyze_customer_segments,
    analyze_product_performance,
    analyze_payments,
    analyze_ratings,
    generate_key_insights
)
from src.visualization import (
    plot_sales_trend,
    plot_bar,
    plot_donut,
    plot_scatter_quadrant,
    plot_rating_histogram,
    plot_grouped_bar,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR
)

# Page configuration
st.set_page_config(
    page_title="Supermarket Sales & Customer Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive portfolio styling
st.markdown("""
<style>
    /* Metric Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    .metric-subtitle {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 4px;
    }

    /* Insight Cards */
    .insight-card {
        background-color: #f8fafc;
        border-left: 4px solid #1f4e79;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }
    .insight-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        background-color: #e2e8f0;
        color: #334155;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .insight-title {
        font-size: 1.0rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .insight-text {
        font-size: 0.90rem;
        color: #475569;
        line-height: 1.45;
    }
    
    /* Hide top padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_dataset():
    """Load and cache cleaned dataset."""
    return load_data()


# Load full data
df_full = get_dataset()

# -------------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------------
st.sidebar.markdown("## 🔍 **Analytics Filters**")

# Reset filters button
if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
    st.session_state["filter_cities"] = []
    st.session_state["filter_branches"] = []
    st.session_state["filter_categories"] = []
    st.session_state["filter_products"] = []
    st.session_state["filter_customer_types"] = []
    st.session_state["filter_genders"] = []
    st.session_state["filter_payments"] = []
    st.session_state["filter_date_range"] = (df_full["Date"].min().date(), df_full["Date"].max().date())
    st.rerun()

# 1. Date Range Filter
min_date = df_full["Date"].min().date()
max_date = df_full["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="filter_date_range"
)

# 2. City Filter
all_cities = sorted(df_full["City"].unique())
selected_cities = st.sidebar.multiselect(
    "City",
    options=all_cities,
    default=all_cities,
    key="filter_cities"
)

# 3. Branch Filter
all_branches = sorted(df_full["Branch"].unique())
selected_branches = st.sidebar.multiselect(
    "Branch",
    options=all_branches,
    default=all_branches,
    key="filter_branches"
)

# 4. Product Category Filter
all_categories = sorted(df_full["Category"].unique())
selected_categories = st.sidebar.multiselect(
    "Product Category",
    options=all_categories,
    default=all_categories,
    key="filter_categories"
)

# 5. Product Filter (dynamically cascaded based on category)
if selected_categories:
    available_products = sorted(df_full[df_full["Category"].isin(selected_categories)]["Product"].unique())
else:
    available_products = sorted(df_full["Product"].unique())

selected_products = st.sidebar.multiselect(
    "Product",
    options=available_products,
    default=available_products,
    key="filter_products"
)

# 6. Customer Type Filter
all_customer_types = sorted(df_full["Customer Type"].unique())
selected_customer_types = st.sidebar.multiselect(
    "Customer Type",
    options=all_customer_types,
    default=all_customer_types,
    key="filter_customer_types"
)

# 7. Gender Filter
all_genders = sorted(df_full["Gender"].unique())
selected_genders = st.sidebar.multiselect(
    "Gender",
    options=all_genders,
    default=all_genders,
    key="filter_genders"
)

# 8. Payment Method Filter
all_payments = sorted(df_full["Payment"].unique())
selected_payments = st.sidebar.multiselect(
    "Payment Method",
    options=all_payments,
    default=all_payments,
    key="filter_payments"
)

# -------------------------------------------------------------
# APPLY FILTERING LOGIC
# -------------------------------------------------------------
df_filtered = df_full.copy()

# Date filter
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
    df_filtered = df_filtered[
        (df_filtered["Date"].dt.date >= start_d) &
        (df_filtered["Date"].dt.date <= end_d)
    ]

# Categorical filters
if selected_cities:
    df_filtered = df_filtered[df_filtered["City"].isin(selected_cities)]
else:
    df_filtered = df_filtered.iloc[0:0]

if selected_branches:
    df_filtered = df_filtered[df_filtered["Branch"].isin(selected_branches)]
else:
    df_filtered = df_filtered.iloc[0:0]

if selected_categories:
    df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]
else:
    df_filtered = df_filtered.iloc[0:0]

if selected_products:
    df_filtered = df_filtered[df_filtered["Product"].isin(selected_products)]
else:
    df_filtered = df_filtered.iloc[0:0]

if selected_customer_types:
    df_filtered = df_filtered[df_filtered["Customer Type"].isin(selected_customer_types)]
else:
    df_filtered = df_filtered.iloc[0:0]

if selected_genders:
    df_filtered = df_filtered[df_filtered["Gender"].isin(selected_genders)]
else:
    df_filtered = df_filtered.iloc[0:0]

if selected_payments:
    df_filtered = df_filtered[df_filtered["Payment"].isin(selected_payments)]
else:
    df_filtered = df_filtered.iloc[0:0]


# -------------------------------------------------------------
# HEADER & EXECUTIVE SUMMARY
# -------------------------------------------------------------
st.title("🛒 Supermarket Sales & Customer Analytics")
st.caption(
    "A portfolio-ready data analytics dashboard examining supermarket revenue, customer segmentation, "
    "product dynamics, and payment behaviors across retail branches."
)

# -------------------------------------------------------------
# EMPTY FILTER GUARD
# -------------------------------------------------------------
if df_filtered.empty:
    st.warning("⚠️ No records match the active filter criteria. Please broaden your filter selections or click 'Reset All Filters' in the sidebar.")
    st.stop()

# -------------------------------------------------------------
# KPI SUMMARY CARDS
# -------------------------------------------------------------
kpis = compute_kpis(df_filtered)

kpi_cols = st.columns(7)
with kpi_cols[0]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Sales</div>
        <div class="metric-value">₹{kpis['total_sales']:,.0f}</div>
        <div class="metric-subtitle">Gross Revenue</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Quantity</div>
        <div class="metric-value">{kpis['total_quantity']:,}</div>
        <div class="metric-subtitle">Units Sold</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Transactions</div>
        <div class="metric-value">{kpis['total_transactions']:,}</div>
        <div class="metric-subtitle">Customer Orders</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg Order Value</div>
        <div class="metric-value">₹{kpis['avg_transaction_value']:,.1f}</div>
        <div class="metric-subtitle">Per Transaction</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[4]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg Rating</div>
        <div class="metric-value">{kpis['avg_rating']:.2f} <span style="font-size:1.1rem; color:#f59e0b;">★</span></div>
        <div class="metric-subtitle">Out of 5.0</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[5]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Products</div>
        <div class="metric-value">{kpis['unique_products']}</div>
        <div class="metric-subtitle">SKUs Filtered</div>
    </div>
    """, unsafe_allow_html=True)

with kpi_cols[6]:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Categories</div>
        <div class="metric-value">{kpis['unique_categories']}</div>
        <div class="metric-subtitle">Merchandise Groups</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# TABS NAVIGATION
# -------------------------------------------------------------
tabs = st.tabs([
    "📈 Sales Overview",
    "🛍️ Product Analysis",
    "👥 Customer Analysis",
    "💳 Payment Analytics",
    "⭐ Ratings & Feedback",
    "💡 Key Business Insights",
    "📋 Data Explorer"
])

# -------------------------------------------------------------
# TAB 1: SALES OVERVIEW
# -------------------------------------------------------------
with tabs[0]:
    st.subheader("Sales & Revenue Dynamics")
    
    col_time1, col_time2 = st.columns([2, 1])
    with col_time1:
        time_freq = st.radio("Time Aggregation:", ["Monthly", "Daily", "Day of Week"], horizontal=True)
        if time_freq == "Monthly":
            df_time = analyze_sales_over_time(df_filtered, freq="M")
            fig_time = plot_sales_trend(df_time, freq_name="Month")
        elif time_freq == "Daily":
            df_time = analyze_sales_over_time(df_filtered, freq="D")
            fig_time = plot_sales_trend(df_time, freq_name="Date")
        else:
            df_time = analyze_sales_over_time(df_filtered, freq="Day_Of_Week")
            fig_time = plot_bar(df_time, x_col="Day_Of_Week", y_col="Sales", title="Sales by Day of Week")
        st.plotly_chart(fig_time, use_container_width=True)

    with col_time2:
        df_city = aggregate_by_dimension(df_filtered, "City")
        fig_city = plot_donut(df_city, names_col="City", values_col="Sales", title="Sales Share by City")
        st.plotly_chart(fig_city, use_container_width=True)

    st.markdown("---")
    col_br1, col_br2 = st.columns(2)
    with col_br1:
        df_branch = aggregate_by_dimension(df_filtered, "Branch")
        fig_branch = plot_bar(df_branch, x_col="Branch", y_col="Sales", title="Total Sales by Branch", color_col="Branch")
        st.plotly_chart(fig_branch, use_container_width=True)

    with col_br2:
        df_cat_sales = aggregate_by_dimension(df_filtered, "Category")
        fig_cat_sales = plot_bar(df_cat_sales, x_col="Sales", y_col="Category", orientation="h", title="Sales by Product Category", color_col="Category")
        st.plotly_chart(fig_cat_sales, use_container_width=True)


# -------------------------------------------------------------
# TAB 2: PRODUCT ANALYSIS
# -------------------------------------------------------------
with tabs[1]:
    st.subheader("Product & Category Analytics")
    prod_perf = analyze_product_performance(df_filtered)

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        top_rev = prod_perf["top_revenue"].head(10)
        fig_rev = plot_bar(
            top_rev,
            x_col="Total_Sales",
            y_col="Product",
            orientation="h",
            title="Top 10 Products by Revenue (Rs.)",
            color_col="Category"
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_p2:
        top_vol = prod_perf["top_volume"].head(10)
        fig_vol = px.bar(
            top_vol,
            x="Total_Quantity",
            y="Product",
            orientation="h",
            color="Category",
            title="<b>Top 10 Products by Quantity Sold (Units)</b>",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_vol.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(248,249,250,0.8)")
        st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown("---")
    st.markdown("#### High-Volume vs High-Value Product Matrix")
    st.caption("Scatter relationship between Unit Price (x-axis) and Total Volume Sold (y-axis). Bubble size corresponds to Total Sales revenue.")
    fig_quad = plot_scatter_quadrant(prod_perf["summary"])
    st.plotly_chart(fig_quad, use_container_width=True)

    st.markdown("#### Category Summary Breakdown")
    st.dataframe(
        prod_perf["category_summary"].rename(columns={
            "Total_Sales": "Total Sales (Rs.)",
            "Total_Quantity": "Total Units",
            "Avg_Unit_Price": "Avg Unit Price (Rs.)",
            "Avg_Rating": "Avg Rating"
        }).style.format({
            "Total Sales (Rs.)": "₹{:,.2f}",
            "Total Units": "{:,}",
            "Avg Unit Price (Rs.)": "₹{:.2f}",
            "Avg Rating": "{:.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )


# -------------------------------------------------------------
# TAB 3: CUSTOMER ANALYSIS
# -------------------------------------------------------------
with tabs[2]:
    st.subheader("Customer Demographics & Segmentation")
    cust_data = analyze_customer_segments(df_filtered)

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        fig_cust_type = plot_bar(
            cust_data["by_type"],
            x_col="Customer Type",
            y_col="Sales",
            title="Total Sales: Member vs Normal",
            color_col="Customer Type"
        )
        st.plotly_chart(fig_cust_type, use_container_width=True)

    with col_c2:
        fig_gender = plot_donut(
            cust_data["by_gender"],
            names_col="Gender",
            values_col="Sales",
            title="Sales Share by Gender"
        )
        st.plotly_chart(fig_gender, use_container_width=True)

    st.markdown("---")
    col_c3, col_c4 = st.columns(2)
    with col_c3:
        fig_combo = plot_grouped_bar(
            cust_data["combination"],
            x_col="Customer Type",
            y_col="Sales",
            color_col="Gender",
            title="Sales by Customer Type & Gender Segment"
        )
        st.plotly_chart(fig_combo, use_container_width=True)

    with col_c4:
        fig_atv = plot_bar(
            cust_data["by_type"],
            x_col="Customer Type",
            y_col="Avg_Order_Value",
            title="Average Order Value (ATV) by Customer Type",
            color_col="Customer Type"
        )
        st.plotly_chart(fig_atv, use_container_width=True)


# -------------------------------------------------------------
# TAB 4: PAYMENT ANALYSIS
# -------------------------------------------------------------
with tabs[3]:
    st.subheader("Payment Channel Adoption & Order Size")
    pay_data = analyze_payments(df_filtered)

    col_pay1, col_pay2 = st.columns(2)
    with col_pay1:
        fig_pay_share = plot_donut(
            pay_data["summary"],
            names_col="Payment",
            values_col="Total_Sales",
            title="Sales Share by Payment Method"
        )
        st.plotly_chart(fig_pay_share, use_container_width=True)

    with col_pay2:
        fig_pay_atv = plot_bar(
            pay_data["summary"],
            x_col="Payment",
            y_col="Avg_Transaction_Value",
            title="Average Transaction Value by Payment Method",
            color_col="Payment"
        )
        st.plotly_chart(fig_pay_atv, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Payment Preference by Customer Type (%)")
    st.caption("Row percentages indicating what proportion of each customer group pays with each method.")
    st.dataframe(
        pay_data["crosstab_pct"].style.format("{:.2f}%").background_gradient(cmap="Blues"),
        use_container_width=True
    )


# -------------------------------------------------------------
# TAB 5: RATINGS & FEEDBACK
# -------------------------------------------------------------
with tabs[4]:
    st.subheader("Customer Satisfaction & Rating Distribution")
    ratings_data = analyze_ratings(df_filtered)

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        fig_hist = plot_rating_histogram(df_filtered)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_r2:
        fig_cat_rating = px.bar(
            ratings_data["by_category"],
            x="Mean_Rating",
            y="Category",
            orientation="h",
            title="<b>Average Customer Rating by Category</b>",
            color="Mean_Rating",
            color_continuous_scale="Viridis"
        )
        fig_cat_rating.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248,249,250,0.8)",
            xaxis=dict(range=[3.0, 5.0], title="Mean Rating (1-5)")
        )
        st.plotly_chart(fig_cat_rating, use_container_width=True)

    st.markdown("---")
    col_r3, col_r4 = st.columns(2)
    with col_r3:
        fig_city_rating = px.bar(
            ratings_data["by_city"],
            x="City",
            y="Mean_Rating",
            color="City",
            title="<b>Average Rating by City</b>"
        )
        fig_city_rating.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248,249,250,0.8)",
            yaxis=dict(range=[3.0, 5.0], title="Mean Rating")
        )
        st.plotly_chart(fig_city_rating, use_container_width=True)

    with col_r4:
        fig_type_rating = px.bar(
            ratings_data["by_customer_type"],
            x="Customer Type",
            y="Mean_Rating",
            color="Customer Type",
            title="<b>Average Rating: Member vs Normal</b>"
        )
        fig_type_rating.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(248,249,250,0.8)",
            yaxis=dict(range=[3.0, 5.0], title="Mean Rating")
        )
        st.plotly_chart(fig_type_rating, use_container_width=True)


# -------------------------------------------------------------
# TAB 6: KEY BUSINESS INSIGHTS
# -------------------------------------------------------------
with tabs[5]:
    st.subheader("Empirical Business Findings")
    st.caption("Verifiable data-driven insights computed strictly from actual transactions without fabrication.")

    insights = generate_key_insights(df_filtered)

    for ins in insights:
        st.markdown(f"""
        <div class="insight-card">
            <span class="insight-badge">{ins['category']}</span>
            <div class="insight-title">{ins['title']}</div>
            <div class="insight-text">{ins['insight']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Strategic Recommendations for Store Operations")
    st.markdown("""
    1. **Inventory Alignment with Revenue vs Volume**:
       - High-value categories (Dairy, Personal Care) deliver superior revenue per square foot and require stringent stock availability.
       - High-volume staple categories (Snacks, Vegetables) should be positioned strategically for basket-building and foot-traffic conversion.
    2. **Loyalty Program Enhancements**:
       - Evaluate Member Average Transaction Value relative to Normal shoppers to optimize membership perks, targeted digital discounts, and member-exclusive bundle offers.
    3. **Payment Terminal Optimization**:
       - Ensure robust uptime and zero-latency connectivity for top digital payment channels (UPI and Net Banking), which represent the largest transaction shares.
    4. **Quality & Satisfaction Assurance**:
       - Focus quality assurance audits on categories showing lower average rating variance to maintain brand trust and consistent customer retention.
    """)


# -------------------------------------------------------------
# TAB 7: DATA EXPLORER & EXPORT
# -------------------------------------------------------------
with tabs[6]:
    st.subheader("Filtered Dataset Explorer")
    st.caption(f"Showing {len(df_filtered)} filtered records out of {len(df_full)} total transactions.")

    # CSV Download
    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="supermarket_filtered_sales.csv",
        mime="text/csv",
        use_container_width=False
    )

    st.dataframe(
        df_filtered[[
            "Invoice ID", "Date", "City", "Branch", "Customer Type", "Gender",
            "Product", "Category", "Quantity", "Unit Price", "Payment", "Rating", "Sales"
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("#### Summary Statistics (Numerical Columns)")
    st.dataframe(
        df_filtered[["Quantity", "Unit Price", "Rating", "Sales"]].describe().T.style.format({
            "count": "{:,.0f}",
            "mean": "{:,.2f}",
            "std": "{:,.2f}",
            "min": "{:,.2f}",
            "25%": "{:,.2f}",
            "50%": "{:,.2f}",
            "75%": "{:,.2f}",
            "max": "{:,.2f}"
        }),
        use_container_width=True
    )
