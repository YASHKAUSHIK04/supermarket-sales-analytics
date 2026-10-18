"""
Supermarket Sales & Customer Analytics Dashboard
Interactive Dashboard built with Streamlit, Plotly, and Pandas.

Author: Yash Kaushik
Repository: https://github.com/YASHKAUSHIK04/supermarket-sales-analytics
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
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
    apply_layout_theme,
    get_layout_theme,
    LAYOUT_THEME,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR
)
from src.data_loader import (
    load_uploaded_file,
    detect_and_map_columns,
    validate_and_process_uploaded_data,
    CANONICAL_COLUMNS,
    CORE_MANDATORY_COLUMNS
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
    /* Responsive KPI Cards Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
        margin-bottom: 24px;
        width: 100%;
    }
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 96px;
        box-sizing: border-box;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -2px rgba(0, 0, 0, 0.3);
        border-color: #475569;
    }
    .metric-title {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #94a3b8;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .metric-value {
        font-size: clamp(1.15rem, 1.55vw, 1.45rem);
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.25;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .metric-subtitle {
        font-size: 0.70rem;
        color: #cbd5e1;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Dataset Banner */
    .dataset-badge {
        display: inline-flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
        background: #1e1b4b;
        border: 1px solid #4338ca;
        color: #c7d2fe;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 20px;
        margin-bottom: 16px;
        max-width: 100%;
        word-break: break-word;
        line-height: 1.4;
    }

    /* Insight Cards */
    .insight-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-left: 4px solid #38bdf8;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 14px;
        word-break: break-word;
        overflow-wrap: break-word;
    }
    .insight-badge {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        background-color: #0f172a;
        color: #38bdf8;
        border: 1px solid #0284c7;
        padding: 2px 8px;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 6px;
    }
    .insight-title {
        font-size: 0.96rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 4px;
        word-break: break-word;
        line-height: 1.35;
    }
    .insight-text {
        font-size: 0.88rem;
        color: #cbd5e1;
        line-height: 1.5;
        word-break: break-word;
    }

    /* Quality Summary Card */
    .quality-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 14px;
        font-size: 0.85rem;
        color: #cbd5e1;
        word-break: break-word;
    }
    
    /* Streamlit Tabs text wrap protection */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 12px;
        white-space: nowrap;
        font-size: 0.88rem;
    }

    /* Sidebar controls protection */
    section[data-testid="stSidebar"] [data-baseweb="tag"] {
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Container padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)



@st.cache_data
def get_default_dataset() -> pd.DataFrame:
    """Load and cache default cleaned dataset."""
    return load_data()


# -------------------------------------------------------------
# DATASET SELECTION & INGESTION PIPELINE
# -------------------------------------------------------------
st.sidebar.markdown("## 📁 **Data Source**")
data_source_mode = st.sidebar.radio(
    "Data Source Selection",
    options=["Default Dataset (500 Rows)", "Upload CSV or Excel"],
    index=0,
    label_visibility="collapsed"
)

df_full: Optional[pd.DataFrame] = None
active_dataset_name = "Supermarket Sales (Default - 500 Records)"
upload_summary: Optional[Dict[str, Any]] = None
current_dataset_token = "default"

if data_source_mode == "Default Dataset (500 Rows)":
    df_full = get_default_dataset()
    current_dataset_token = "default_500"
    active_dataset_name = "Supermarket Sales (Default - 500 Records)"
else:
    st.sidebar.markdown("### 📤 **File Upload**")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Sales Data (.csv, .xlsx, .xls)",
        type=["csv", "xlsx", "xls"],
        help="Upload supermarket transaction records in CSV or Excel format."
    )

    if uploaded_file is not None:
        try:
            df_raw = load_uploaded_file(uploaded_file)
            current_dataset_token = f"upload_{uploaded_file.name}_{uploaded_file.size}"
            active_dataset_name = f"{uploaded_file.name} ({len(df_raw):,} records)"

            # Smart column mapping detection
            raw_cols = list(df_raw.columns)
            detected_mapping = detect_and_map_columns(raw_cols)

            # Manual column mapping interface in expander
            with st.sidebar.expander("🛠️ Column Mapping Settings", expanded=False):
                st.caption("Review or adjust detected column mappings:")
                custom_mapping: Dict[str, Optional[str]] = {}
                col_options = ["(None)"] + raw_cols

                for canon in CANONICAL_COLUMNS:
                    initial_match = detected_mapping.get(canon)
                    default_idx = col_options.index(initial_match) if initial_match in col_options else 0
                    selected_col = st.selectbox(
                        f"**{canon}** {'*(Required)*' if canon in CORE_MANDATORY_COLUMNS else ''}",
                        options=col_options,
                        index=default_idx,
                        key=f"map_{canon}"
                    )
                    custom_mapping[canon] = None if selected_col == "(None)" else selected_col

            # Validate and clean uploaded data
            df_processed, upload_summary = validate_and_process_uploaded_data(
                df_raw, column_mapping=custom_mapping
            )

            if not upload_summary["is_valid"]:
                st.sidebar.error("❌ Dataset validation failed.")
                for err in upload_summary["errors"]:
                    st.sidebar.error(f"• {err}")
                st.error("### ⚠️ Dataset Ingestion Failed")
                st.write("The uploaded file could not be processed due to the following schema issues:")
                for err in upload_summary["errors"]:
                    st.markdown(f"- **{err}**")
                st.write("#### Raw File Preview:")
                st.dataframe(df_raw.head(10), use_container_width=True)
                st.stop()
            else:
                df_full = df_processed
                st.sidebar.success(f"✅ Ingested {len(df_full):,} records successfully!")

                # Quality audit notice in sidebar
                if upload_summary["math_discrepancy_count"] > 0 or upload_summary["warnings"]:
                    with st.sidebar.expander(f"⚠️ Ingestion Audit ({len(upload_summary['warnings'])})", expanded=False):
                        for warn in upload_summary["warnings"]:
                            st.caption(f"• {warn}")

        except Exception as ex:
            st.sidebar.error(f"Error parsing file: {ex}")
            st.error(f"### ⚠️ File Read Error\n{ex}")
            st.stop()
    else:
        # Prompt user to upload file
        st.title("🛒 Supermarket Sales & Customer Analytics")
        st.info("👋 **Welcome!** Please upload a CSV or Excel (`.xlsx`, `.xls`) file in the sidebar to begin analysis, or switch back to **'Default Dataset (500 Rows)'**.")
        
        st.markdown("### 📋 Expected Data Format")
        st.markdown("""
        Your dataset should ideally contain the following transaction fields (standard aliases are recognized automatically):
        - **Invoice ID** (`Invoice ID`, `Order ID`, `Bill No`)
        - **Date** (`Date`, `Invoice Date`, `Txn Date`)
        - **Branch** (`Branch`, `Store`, `Outlet`)
        - **City** (`City`, `Location`, `Market`)
        - **Customer Type** (`Customer Type`, `Membership`, `Type`)
        - **Gender** (`Gender`, `Sex`)
        - **Product** (`Product`, `Item`, `SKU`)
        - **Category** (`Category`, `Department`, `Dept`)
        - **Quantity** (`Quantity`, `Qty`, `Units`)
        - **Unit Price** (`Unit Price`, `Price`, `Rate`)
        - **Payment** (`Payment`, `Payment Method`, `Mode`)
        - **Rating** (`Rating`, `Satisfaction`, `Score`)
        - **Sales** (`Sales`, `Total`, `Amount`) *(Optional: automatically computed as $Quantity \\times Unit Price$ if omitted)*
        """)
        st.stop()

# -------------------------------------------------------------
# DYNAMIC FILTER STATE SYNCHRONIZATION
# -------------------------------------------------------------
# Check if active dataset changed; if so, clear filter session state to prevent stale collisions
if st.session_state.get("active_dataset_token") != current_dataset_token:
    filter_keys_to_reset = [
        "filter_cities", "filter_branches", "filter_categories",
        "filter_products", "filter_customer_types", "filter_genders",
        "filter_payments", "filter_date_range"
    ]
    for k in filter_keys_to_reset:
        st.session_state.pop(k, None)
    st.session_state["active_dataset_token"] = current_dataset_token


def get_sanitized_selection(session_key: str, available_options: List[str]) -> List[str]:
    """Retrieve or initialize filter selection safely."""
    if session_key in st.session_state:
        current_val = st.session_state[session_key]
        if isinstance(current_val, list):
            valid = [item for item in current_val if item in available_options]
            if valid:
                st.session_state[session_key] = valid
                return valid
    st.session_state[session_key] = available_options
    return available_options


# -------------------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("## 🔍 **Analytics Filters**")

# Reset filters button
if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
    st.session_state["filter_cities"] = sorted(df_full["City"].dropna().unique())
    st.session_state["filter_branches"] = sorted(df_full["Branch"].dropna().unique())
    st.session_state["filter_categories"] = sorted(df_full["Category"].dropna().unique())
    st.session_state["filter_products"] = sorted(df_full["Product"].dropna().unique())
    st.session_state["filter_customer_types"] = sorted(df_full["Customer Type"].dropna().unique())
    st.session_state["filter_genders"] = sorted(df_full["Gender"].dropna().unique())
    st.session_state["filter_payments"] = sorted(df_full["Payment"].dropna().unique())
    min_d = df_full["Date"].min().date()
    max_d = df_full["Date"].max().date()
    st.session_state["filter_date_range"] = (min_d, max_d)
    st.rerun()

# 1. Date Range Filter
min_date = df_full["Date"].min().date()
max_date = df_full["Date"].max().date()

if min_date == max_date:
    date_range = (min_date, max_date)
    st.sidebar.caption(f"📅 Date: {min_date}")
else:
    current_date_val = st.session_state.get("filter_date_range", (min_date, max_date))
    if not (isinstance(current_date_val, tuple) and len(current_date_val) == 2):
        current_date_val = (min_date, max_date)

    date_range = st.sidebar.date_input(
        "Date Range",
        value=current_date_val,
        min_value=min_date,
        max_value=max_date,
        key="filter_date_range"
    )

# 2. City Filter
all_cities = sorted(df_full["City"].dropna().unique())
default_cities = get_sanitized_selection("filter_cities", all_cities)
selected_cities = st.sidebar.multiselect(
    "City",
    options=all_cities,
    default=default_cities,
    key="filter_cities"
)

# 3. Branch Filter
all_branches = sorted(df_full["Branch"].dropna().unique())
default_branches = get_sanitized_selection("filter_branches", all_branches)
selected_branches = st.sidebar.multiselect(
    "Branch",
    options=all_branches,
    default=default_branches,
    key="filter_branches"
)

# 4. Product Category Filter
all_categories = sorted(df_full["Category"].dropna().unique())
default_categories = get_sanitized_selection("filter_categories", all_categories)
selected_categories = st.sidebar.multiselect(
    "Product Category",
    options=all_categories,
    default=default_categories,
    key="filter_categories"
)

# 5. Product Filter (dynamically cascaded based on selected category)
if selected_categories:
    available_products = sorted(df_full[df_full["Category"].isin(selected_categories)]["Product"].dropna().unique())
else:
    available_products = sorted(df_full["Product"].dropna().unique())

default_products = get_sanitized_selection("filter_products", available_products)
selected_products = st.sidebar.multiselect(
    "Product",
    options=available_products,
    default=default_products,
    key="filter_products"
)

# 6. Customer Type Filter
all_customer_types = sorted(df_full["Customer Type"].dropna().unique())
default_types = get_sanitized_selection("filter_customer_types", all_customer_types)
selected_customer_types = st.sidebar.multiselect(
    "Customer Type",
    options=all_customer_types,
    default=default_types,
    key="filter_customer_types"
)

# 7. Gender Filter
all_genders = sorted(df_full["Gender"].dropna().unique())
default_genders = get_sanitized_selection("filter_genders", all_genders)
selected_genders = st.sidebar.multiselect(
    "Gender",
    options=all_genders,
    default=default_genders,
    key="filter_genders"
)

# 8. Payment Method Filter
all_payments = sorted(df_full["Payment"].dropna().unique())
default_payments = get_sanitized_selection("filter_payments", all_payments)
selected_payments = st.sidebar.multiselect(
    "Payment Method",
    options=all_payments,
    default=default_payments,
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

# Active dataset indicator badge
st.markdown(
    f"""<div class="dataset-badge">
        <span>📊 <b>Active Dataset:</b> {active_dataset_name}</span>
        <span>•</span>
        <span><b>{len(df_filtered):,}</b> of <b>{len(df_full):,}</b> records analyzed</span>
    </div>""",
    unsafe_allow_html=True
)

st.caption(
    "A portfolio-ready data analytics dashboard examining supermarket revenue, customer segmentation, "
    "product dynamics, and payment behaviors across retail branches."
)

# Optional Data Quality audit expander for uploaded data
if upload_summary:
    with st.expander("📋 Data Ingestion & Quality Audit Report", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Records Ingested", f"{upload_summary['final_rows']:,}")
        c2.metric("Date Span", f"{upload_summary['date_range'][0]} to {upload_summary['date_range'][1]}")
        c3.metric("Math Discrepancy Rows", f"{upload_summary['math_discrepancy_count']:,}")
        c4.metric("Duplicate Invoices", f"{upload_summary['duplicate_invoices']:,}")

        if upload_summary["defaults_applied"]:
            st.markdown("**Applied Defaults / Imputations:**")
            for d in upload_summary["defaults_applied"]:
                st.markdown(f"- {d}")

        if upload_summary["warnings"]:
            st.markdown("**Quality Notices:**")
            for w in upload_summary["warnings"]:
                st.markdown(f"- {w}")

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

st.markdown(f"""
<div class="kpi-grid">
    <div class="metric-card">
        <div class="metric-title" title="Total Sales">Total Sales</div>
        <div class="metric-value" title="₹{kpis['total_sales']:,.2f}">₹{kpis['total_sales']:,.0f}</div>
        <div class="metric-subtitle" title="Gross Revenue">Gross Revenue</div>
    </div>
    <div class="metric-card">
        <div class="metric-title" title="Total Quantity">Total Quantity</div>
        <div class="metric-value" title="{kpis['total_quantity']:,} units">{kpis['total_quantity']:,}</div>
        <div class="metric-subtitle" title="Units Sold">Units Sold</div>
    </div>
    <div class="metric-card">
        <div class="metric-title" title="Transactions">Transactions</div>
        <div class="metric-value" title="{kpis['total_transactions']:,} orders">{kpis['total_transactions']:,}</div>
        <div class="metric-subtitle" title="Customer Orders">Customer Orders</div>
    </div>
    <div class="metric-card">
        <div class="metric-title" title="Avg Order Value">Avg Order Value</div>
        <div class="metric-value" title="₹{kpis['avg_transaction_value']:,.2f}">₹{kpis['avg_transaction_value']:,.1f}</div>
        <div class="metric-subtitle" title="Per Transaction">Per Transaction</div>
    </div>
    <div class="metric-card">
        <div class="metric-title" title="Avg Rating">Avg Rating</div>
        <div class="metric-value" title="{kpis['avg_rating']:.2f} out of 5.0">{kpis['avg_rating']:.2f} <span style="font-size:1.0rem; color:#f59e0b;">★</span></div>
        <div class="metric-subtitle" title="Out of 5.0">Out of 5.0</div>
    </div>
    <div class="metric-card">
        <div class="metric-title" title="Products">Products</div>
        <div class="metric-value" title="{kpis['unique_products']} SKUs">{kpis['unique_products']}</div>
        <div class="metric-subtitle" title="SKUs Filtered">SKUs Filtered</div>
    </div>
    <div class="metric-card">
        <div class="metric-title" title="Categories">Categories</div>
        <div class="metric-value" title="{kpis['unique_categories']} Groups">{kpis['unique_categories']}</div>
        <div class="metric-subtitle" title="Merchandise Groups">Merchandise Groups</div>
    </div>
</div>
""", unsafe_allow_html=True)


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
            title="Top 10 Products by Revenue (₹)",
            color_col="Category",
            show_legend=True
        )
        st.plotly_chart(fig_rev, use_container_width=True)

    with col_p2:
        top_vol = prod_perf["top_volume"].head(10)
        fig_vol = plot_bar(
            top_vol,
            x_col="Total_Quantity",
            y_col="Product",
            orientation="h",
            title="Top 10 Products by Quantity Sold (Units)",
            color_col="Category",
            format_currency=False,
            show_legend=True
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown("---")
    st.markdown("#### High-Volume vs High-Value Product Matrix")
    st.caption("Scatter relationship between Unit Price (x-axis) and Total Volume Sold (y-axis). Bubble size corresponds to Total Sales revenue.")
    fig_quad = plot_scatter_quadrant(prod_perf["summary"])
    st.plotly_chart(fig_quad, use_container_width=True)

    st.markdown("#### Category Summary Breakdown")
    st.dataframe(
        prod_perf["category_summary"].rename(columns={
            "Total_Sales": "Total Sales (₹)",
            "Total_Quantity": "Total Units",
            "Avg_Unit_Price": "Avg Unit Price (₹)",
            "Avg_Rating": "Avg Rating"
        }).style.format({
            "Total Sales (₹)": "₹{:,.2f}",
            "Total Units": "{:,}",
            "Avg Unit Price (₹)": "₹{:.2f}",
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
            title="Total Sales: Customer Type",
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
        fig_cat_rating.update_traces(hovertemplate="<b>%{y}:</b> Rating: %{x:.2f}<extra></extra>")
        apply_layout_theme(
            fig_cat_rating,
            title=dict(text="<b>Average Customer Rating by Category</b>", font=dict(color="#f8fafc", size=13), x=0.02, y=0.98, xanchor="left", yanchor="top"),
            xaxis=dict(
                range=[1.0, 5.0],
                title="Mean Rating (1-5)",
                automargin=True,
                tickfont=dict(color="#cbd5e1"),
                title_font=dict(color="#f8fafc"),
                showgrid=True,
                gridcolor="#334155"
            ),
            yaxis=dict(
                automargin=True,
                tickfont=dict(color="#cbd5e1"),
                title_font=dict(color="#f8fafc"),
                showgrid=False
            ),
            coloraxis_colorbar=dict(
                title=dict(text="Rating", font=dict(color="#f8fafc", size=10)),
                tickfont=dict(color="#cbd5e1", size=9),
                thickness=12,
                len=0.8
            ),
            coloraxis_showscale=True,
            margin=dict(t=42, b=45, l=60, r=25)
        )
        st.plotly_chart(fig_cat_rating, use_container_width=True)

    st.markdown("---")
    col_r3, col_r4 = st.columns(2)
    with col_r3:
        fig_city_rating = plot_bar(
            ratings_data["by_city"],
            x_col="City",
            y_col="Mean_Rating",
            title="Average Rating by City",
            color_col="City",
            format_currency=False,
            show_legend=False
        )
        fig_city_rating.update_yaxes(range=[1.0, 5.0], title="Mean Rating", tickfont=dict(color="#cbd5e1"), title_font=dict(color="#f8fafc"))
        st.plotly_chart(fig_city_rating, use_container_width=True)

    with col_r4:
        fig_type_rating = plot_bar(
            ratings_data["by_customer_type"],
            x_col="Customer Type",
            y_col="Mean_Rating",
            title="Average Rating by Customer Type",
            color_col="Customer Type",
            format_currency=False,
            show_legend=False
        )
        fig_type_rating.update_yaxes(range=[1.0, 5.0], title="Mean Rating", tickfont=dict(color="#cbd5e1"), title_font=dict(color="#f8fafc"))
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
       - High-value categories deliver superior revenue per square foot and require stringent stock availability.
       - High-volume staple categories should be positioned strategically for basket-building and foot-traffic conversion.
    2. **Loyalty Program Enhancements**:
       - Continuously evaluate Member Average Transaction Value relative to Normal shoppers to optimize membership perks, targeted digital discounts, and member-exclusive bundle offers.
    3. **Payment Terminal Optimization**:
       - Ensure robust uptime and zero-latency connectivity for top digital payment channels, which represent the largest transaction shares.
    4. **Quality & Satisfaction Assurance**:
       - Focus quality assurance audits on categories showing lower average rating variance to maintain brand trust and consistent customer retention.
    """)


# -------------------------------------------------------------
# TAB 7: DATA EXPLORER & EXPORT
# -------------------------------------------------------------
with tabs[6]:
    st.subheader("Filtered Dataset Explorer")
    st.caption(f"Showing {len(df_filtered):,} filtered records out of {len(df_full):,} total transactions.")

    # CSV Download
    csv_data = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="supermarket_filtered_sales.csv",
        mime="text/csv",
        use_container_width=False
    )

    export_cols = [c for c in CANONICAL_COLUMNS if c in df_filtered.columns]
    st.dataframe(
        df_filtered[export_cols],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("#### Summary Statistics (Numerical Columns)")
    numeric_cols = [c for c in ["Quantity", "Unit Price", "Rating", "Sales"] if c in df_filtered.columns]
    if numeric_cols:
        st.dataframe(
            df_filtered[numeric_cols].describe().T.style.format({
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
