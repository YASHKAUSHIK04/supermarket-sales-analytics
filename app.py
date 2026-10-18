"""
Supermarket Sales & Retail Intelligence System
================================================
Full-Stack Retail Analytics, Relational Database Backend, Inventory Intelligence,
Automated Anomaly Detection, 4-Tier Business Insights, and Executive Report Engine.

Author: Yash Kaushik (BCA Capstone Project)
Repository: https://github.com/YASHKAUSHIK04/supermarket-sales-analytics
"""

import sys
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Add project root to system path
sys.path.append(str(Path(__file__).resolve().parent))

# Analytics & Visualizations
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

# Relational Database, Inventory, Anomalies, Insights & Reports
from src.database import (
    get_connection,
    init_db,
    seed_database_if_empty,
    get_sales_dataframe,
    import_sales_dataframe,
    get_products_df,
    get_all_products,
    create_product,
    update_product,
    deactivate_product,
    get_all_categories,
    get_inventory_movements,
    record_stock_movement,
    log_anomalies_to_db,
    get_anomalies_from_db,
    resolve_anomaly_in_db,
    log_report_generation,
    get_report_history,
)
from src.inventory import (
    calculate_inventory_intelligence,
    get_inventory_summary_kpis,
    reconcile_sales_deduction,
)
from src.anomaly import (
    detect_anomalies,
    get_anomaly_summary,
)
from src.insights import (
    generate_structured_business_insights,
)
from src.reports import (
    generate_pdf_report,
    generate_excel_workbook,
    generate_csv_export,
)

# Page configuration
st.set_page_config(
    page_title="Supermarket Sales & Retail Intelligence",
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

    /* 4-Tier Insight Cards */
    .insight-card-4tier {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .insight-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 10px;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
    }
    .tier-row {
        margin-bottom: 8px;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .tier-label {
        font-weight: 700;
        display: inline-block;
        min-width: 130px;
        color: #94a3b8;
    }
    .tier-obs { color: #cbd5e1; }
    .tier-ins { color: #67e8f9; }
    .tier-exp { color: #fde047; }
    .tier-act { color: #4ade80; font-weight: 600; }

    /* Badges */
    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-critical { background-color: #7f1d1d; color: #fecaca; border: 1px solid #b91c1c; }
    .badge-high { background-color: #7c2d12; color: #fed7aa; border: 1px solid #ea580c; }
    .badge-medium { background-color: #713f12; color: #fef08a; border: 1px solid #ca8a04; }
    .badge-low { background-color: #14532d; color: #bbf7d0; border: 1px solid #16a34a; }
    .badge-cat { background-color: #1e1b4b; color: #c7d2fe; border: 1px solid #4338ca; }

    /* Report Card */
    .report-export-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px;
        height: 100%;
        box-sizing: border-box;
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


# Initialize persistent SQLite tables and baseline seed
@st.cache_resource
def setup_sqlite_database():
    """Ensure database schema and initial data are present."""
    init_db()
    seed_database_if_empty()
    return True

setup_sqlite_database()


@st.cache_data
def get_default_dataset() -> pd.DataFrame:
    """Load and cache default cleaned dataset from CSV."""
    return load_data()


# -------------------------------------------------------------
# DATASET SELECTION & INGESTION PIPELINE
# -------------------------------------------------------------
st.sidebar.markdown("## 📁 **Data Source**")
data_source_mode = st.sidebar.radio(
    "Data Source Selection",
    options=[
        "SQLite Database (Persistent)",
        "Default Dataset (500 Rows)",
        "Upload CSV or Excel"
    ],
    index=0,
    label_visibility="collapsed"
)

df_full: Optional[pd.DataFrame] = None
active_dataset_name = "SQLite Database (Persistent)"
upload_summary: Optional[Dict[str, Any]] = None
current_dataset_token = "sqlite_persistent"

if data_source_mode == "SQLite Database (Persistent)":
    df_full = get_sales_dataframe()
    current_dataset_token = f"sqlite_{len(df_full)}"
    active_dataset_name = f"SQLite Database ({len(df_full):,} records)"
elif data_source_mode == "Default Dataset (500 Rows)":
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
                st.sidebar.success(f"✅ Loaded {len(df_full):,} records successfully!")

                # SQLite Ingestion button
                with st.sidebar.expander("💾 Ingest to SQLite Database", expanded=False):
                    st.caption("Store these transactions permanently in the relational database:")
                    ingest_mode = st.radio("Conflict Strategy:", ["Skip Duplicates", "Replace All"], index=0, key="ingest_strat")
                    if st.button("🚀 Write to Database", use_container_width=True):
                        strategy = "skip_duplicates" if ingest_mode == "Skip Duplicates" else "replace_all"
                        res = import_sales_dataframe(df_processed, if_exists=strategy)
                        st.success(f"Successfully ingested {res['inserted_count']:,} records! (Skipped {res['skipped_duplicates']:,} duplicates)")
                        st.rerun()

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
        st.title("🛒 Supermarket Sales & Retail Intelligence")
        st.info("👋 **Welcome!** Please upload a CSV or Excel (`.xlsx`, `.xls`) file in the sidebar to begin analysis, or switch to **'SQLite Database (Persistent)'**.")
        
        st.markdown("### 📋 Expected Data Format")
        st.markdown("""
        Your dataset should contain standard retail sales fields:
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

# Compute filter summary dictionary for reports
active_filter_summary = {
    "date_range": f"{date_range[0]} to {date_range[1]}" if isinstance(date_range, tuple) and len(date_range) == 2 else "All",
    "cities": selected_cities,
    "branches": selected_branches,
    "categories": selected_categories,
}

# -------------------------------------------------------------
# HEADER & EXECUTIVE SUMMARY
# -------------------------------------------------------------
st.title("🛒 Supermarket Sales & Retail Intelligence System")

# Active dataset indicator badge
st.markdown(
    f"""<div class="dataset-badge">
        <span>📊 <b>Active Source:</b> {active_dataset_name}</span>
        <span>•</span>
        <span><b>{len(df_filtered):,}</b> of <b>{len(df_full):,}</b> transactions analyzed</span>
    </div>""",
    unsafe_allow_html=True
)

st.caption(
    "A full-stack enterprise retail analytics dashboard powered by Python, Streamlit, SQLite, and ReportLab. "
    "Features automated anomaly detection, inventory velocity audits, and prescriptive business intelligence."
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
        <div class="metric-value" title="${kpis['total_sales']:,.2f}">${kpis['total_sales']:,.0f}</div>
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
        <div class="metric-value" title="${kpis['avg_transaction_value']:,.2f}">${kpis['avg_transaction_value']:,.1f}</div>
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


# Load physical product catalog from SQLite relational database
try:
    products_catalog_df = get_products_df(active_only=True)
except Exception:
    products_catalog_df = pd.DataFrame()

# Pre-compute Inventory Intelligence, Anomalies & 4-Tier Insights
inv_intel_df = calculate_inventory_intelligence(
    products_df=products_catalog_df,
    sales_df=df_filtered
)
detected_anomalies = detect_anomalies(df_filtered)
anomaly_summary = get_anomaly_summary(detected_anomalies)
structured_insights = generate_structured_business_insights(
    df_filtered,
    inventory_df=inv_intel_df
)


# -------------------------------------------------------------
# TABS NAVIGATION
# -------------------------------------------------------------
tabs = st.tabs([
    "📈 Sales Overview",
    "🛍️ Product Analysis",
    "👥 Customer Analysis",
    "💳 Payment Analytics",
    "⭐ Ratings & Feedback",
    "💡 Business Insights",
    "📦 Inventory Intelligence",
    "🚨 Anomaly Detection",
    "📄 Report Center",
    "🗄️ Database & CRUD",
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
            title="Top 10 Products by Revenue ($)",
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
            "Total_Sales": "Total Sales ($)",
            "Total_Quantity": "Total Units",
            "Avg_Unit_Price": "Avg Unit Price ($)",
            "Avg_Rating": "Avg Rating"
        }).style.format({
            "Total Sales ($)": "${:,.2f}",
            "Total Units": "{:,}",
            "Avg Unit Price ($)": "${:.2f}",
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
            title="Average Order Value (AOV) by Customer Type",
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
# TAB 6: BUSINESS INSIGHTS (4-TIER FRAMEWORK)
# -------------------------------------------------------------
with tabs[5]:
    st.subheader("💡 Strategic Business Insights (4-Tier Framework)")
    st.caption(
        "Structured retail intelligence mapping empirical data to actionable manager decisions: "
        "Observation ➔ Analytical Insight ➔ Possible Explanation ➔ Recommended Action."
    )

    # Defensive normalization of business insights
    raw_insights = structured_insights if isinstance(structured_insights, list) else []
    normalized_insights: List[Dict[str, str]] = []

    for raw_item in raw_insights:
        if not isinstance(raw_item, dict):
            continue

        # Extract fields safely
        cat = str(raw_item.get("category") or "General").strip()
        title = str(raw_item.get("title") or "Strategic Business Finding").strip()

        # Priority resolution and normalization: handle missing, empty, or unexpected values
        raw_pri = raw_item.get("priority")
        if raw_pri is None or str(raw_pri).strip() == "":
            raw_pri = raw_item.get("severity")
        if raw_pri is None or str(raw_pri).strip() == "":
            raw_pri = "MEDIUM"

        pri_clean = str(raw_pri).strip().upper()
        if pri_clean not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
            pri_clean = "MEDIUM"

        obs = str(raw_item.get("observation") or raw_item.get("insight") or "Observation noted from retail data.").strip()
        ins_val = str(raw_item.get("insight") or raw_item.get("observation") or "Analytical finding derived from metrics.").strip()
        exp = str(raw_item.get("explanation") or "Operational and commercial performance factors.").strip()
        act = str(raw_item.get("action") or raw_item.get("recommendation") or "Review operational benchmarks.").strip()

        normalized_insights.append({
            "category": cat,
            "title": title,
            "priority": pri_clean,
            "severity": pri_clean,
            "observation": obs,
            "insight": ins_val,
            "explanation": exp,
            "action": act,
            "recommendation": act
        })

    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        ins_categories = ["All"] + sorted(list(set(i["category"] for i in normalized_insights)))
        selected_ins_cat = st.selectbox("Filter Insight Category:", ins_categories, key="ins_cat_filter")
    with col_f2:
        ins_priorities = ["All", "Critical", "High", "Medium", "Low"]
        selected_ins_pri = st.selectbox("Filter Priority Level:", ins_priorities, key="ins_pri_filter")

    filtered_insights = normalized_insights
    if selected_ins_cat != "All":
        filtered_insights = [i for i in filtered_insights if i["category"] == selected_ins_cat]
    if selected_ins_pri != "All":
        filtered_insights = [i for i in filtered_insights if i["priority"] == selected_ins_pri.upper()]

    if not filtered_insights:
        st.info("No insights matching the selected category and priority filters.")
    else:
        for ins in filtered_insights:
            pri = ins.get("priority", "MEDIUM").upper()
            badge_class = (
                "badge-critical" if pri == "CRITICAL"
                else ("badge-high" if pri == "HIGH"
                else ("badge-medium" if pri == "MEDIUM" else "badge-low"))
            )
            display_pri = pri.capitalize()

            st.markdown(f"""
            <div class="insight-card-4tier">
                <div class="insight-header">
                    <span style="font-size:1.05rem; font-weight:700; color:#f8fafc;">{ins['title']}</span>
                    <div>
                        <span class="badge-pill badge-cat">{ins['category']}</span>
                        <span class="badge-pill {badge_class}">{display_pri} Priority</span>
                    </div>
                </div>
                <div class="tier-row">
                    <span class="tier-label">👁️ Observation:</span>
                    <span class="tier-obs">{ins['observation']}</span>
                </div>
                <div class="tier-row">
                    <span class="tier-label">📊 Insight:</span>
                    <span class="tier-ins">{ins['insight']}</span>
                </div>
                <div class="tier-row">
                    <span class="tier-label">❓ Explanation:</span>
                    <span class="tier-exp">{ins['explanation']}</span>
                </div>
                <div class="tier-row">
                    <span class="tier-label">🎯 Action:</span>
                    <span class="tier-act">{ins['action']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


# -------------------------------------------------------------
# TAB 7: INVENTORY INTELLIGENCE (NEW)
# -------------------------------------------------------------
with tabs[6]:
    st.subheader("📦 Inventory Stock Health & Replenishment Intelligence")
    st.caption(
        "Real-time velocity tracking, days-of-stock countdown, and automated reorder triggers "
        "calculated directly against transactional demand."
    )

    if inv_intel_df is None or inv_intel_df.empty:
        if products_catalog_df is None or products_catalog_df.empty:
            st.warning(
                "⚠️ **Inventory Catalog Empty or Uninitialized**\n\n"
                "The product inventory database is currently empty or has not been initialized.\n\n"
                "• **Initialization Required**: Navigate to the **🗄️ Database & CRUD** tab to seed baseline products or create new catalog items.\n"
                "• Once products are created or seeded, inventory health and replenishment intelligence will automatically calculate.\n\n"
                "*(The rest of the dashboard remains fully operational.)*"
            )
        else:
            st.info(
                "ℹ️ **Inventory Records Unavailable for this Sales Dataset**\n\n"
                "The active sales dataset contains products that are not currently tracked in the inventory catalog.\n\n"
                "• **SQLite Database**: Ensure the active sales products match catalog SKUs.\n"
                "• **Uploaded Datasets**: Register custom products in the **🗄️ Database & CRUD** tab or ingest the dataset into the SQLite database to link sales with inventory.\n\n"
                "*(In accordance with retail data auditing standards, stock levels are verified against actual physical catalog records and never artificially invented.)*"
            )
    else:
        inv_kpis = get_inventory_summary_kpis(inv_intel_df)

        # Inventory KPI Cards
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="metric-card">
                <div class="metric-title">Catalog SKUs</div>
                <div class="metric-value">{inv_kpis['total_products']}</div>
                <div class="metric-subtitle">Active Products</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Inventory Valuation</div>
                <div class="metric-value">${inv_kpis['total_stock_value']:,.2f}</div>
                <div class="metric-subtitle">Holding Value</div>
            </div>
            <div class="metric-card" style="border-left: 3px solid #dc2626;">
                <div class="metric-title" style="color: #f87171;">Out of Stock</div>
                <div class="metric-value" style="color: #f87171;">{inv_kpis['out_of_stock_count']}</div>
                <div class="metric-subtitle">Immediate Stockout</div>
            </div>
            <div class="metric-card" style="border-left: 3px solid #f59e0b;">
                <div class="metric-title" style="color: #fbbf24;">Low Stock Alerts</div>
                <div class="metric-value" style="color: #fbbf24;">{inv_kpis['low_stock_count']}</div>
                <div class="metric-subtitle">Below Safety Stock</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Est. Reorder Cost</div>
                <div class="metric-value">${inv_kpis['total_reorder_cost']:,.2f}</div>
                <div class="metric-subtitle">Replenishment Budget</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_inv_f1, col_inv_f2 = st.columns(2)
        with col_inv_f1:
            health_opts = ["All", "Out of Stock", "Low Stock", "Healthy", "Overstocked"]
            sel_health = st.selectbox("Filter Stock Health:", health_opts, key="inv_health_filter")
        with col_inv_f2:
            vel_opts = ["All", "Fast Moving", "Moderate", "Slow Moving", "Dormant (No Sales)"]
            sel_vel = st.selectbox("Filter Velocity Tier:", vel_opts, key="inv_vel_filter")

        display_inv_df = inv_intel_df.copy()
        if sel_health != "All":
            display_inv_df = display_inv_df[display_inv_df["health_status"] == sel_health]
        if sel_vel != "All":
            if sel_vel in ["Fast Moving", "Fast-Moving"]:
                display_inv_df = display_inv_df[display_inv_df["velocity_tier"].astype(str).str.contains("Fast", case=False, na=False)]
            elif sel_vel in ["Moderate", "Normal Moving"]:
                display_inv_df = display_inv_df[display_inv_df["velocity_tier"].astype(str).str.contains("Moderate|Normal", case=False, na=False)]
            elif sel_vel in ["Slow Moving", "Slow-Moving"]:
                display_inv_df = display_inv_df[display_inv_df["velocity_tier"].astype(str).str.contains("Slow", case=False, na=False)]
            else:
                display_inv_df = display_inv_df[display_inv_df["velocity_tier"].astype(str).str.contains("Dormant|Non-Moving", case=False, na=False)]

        st.markdown("#### SKU Health & Velocity Table")
        st.dataframe(
            display_inv_df[[
                "product_name", "category_name", "current_stock", "safety_stock_level",
                "daily_sales_velocity", "days_of_stock_remaining", "velocity_tier",
                "health_status", "recommended_reorder_qty", "estimated_reorder_cost"
            ]].rename(columns={
                "product_name": "Product Name",
                "category_name": "Category",
                "current_stock": "Current Stock",
                "safety_stock_level": "Safety Stock",
                "daily_sales_velocity": "Daily Velocity (Units/d)",
                "days_of_stock_remaining": "Days Remaining",
                "velocity_tier": "Velocity Tier",
                "health_status": "Health Status",
                "recommended_reorder_qty": "Reorder Qty",
                "estimated_reorder_cost": "Est Reorder Cost ($)",
            }).style.format({
                "Current Stock": "{:,}",
                "Safety Stock": "{:,}",
                "Daily Velocity (Units/d)": "{:.2f}",
                "Days Remaining": "{:.1f}",
                "Reorder Qty": "{:,}",
                "Est Reorder Cost ($)": "${:,.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    col_act1, col_act2 = st.columns(2)
    with col_act1:
        st.markdown("#### 📥 Receive New Stock Shipment")
        st.caption("Record incoming stock delivery from suppliers into the inventory ledger:")
        products_list = get_all_products()
        if products_list:
            prod_names = [p["product_name"] for p in products_list]
            selected_prod_for_rcv = st.selectbox("Select Product to Receive:", prod_names, key="rcv_prod_sel")
            rcv_qty = st.number_input("Shipment Quantity (Units):", min_value=1, max_value=1000, value=25, key="rcv_qty_input")
            if st.button("📦 Confirm Stock Receipt", use_container_width=True):
                target_prod = next((p for p in products_list if p["product_name"] == selected_prod_for_rcv), None)
                if target_prod:
                    res = record_stock_movement(
                        product_id=target_prod["product_id"],
                        movement_type="receipt",
                        quantity_change=rcv_qty,
                        reference_reason="Supplier purchase order delivery"
                    )
                    if res["success"]:
                        st.success(f"Successfully received {rcv_qty} units of '{selected_prod_for_rcv}'! New stock balance: {res['new_stock_level']}.")
                        st.rerun()
                    else:
                        st.error(f"Stock receipt failed: {res.get('error')}")
        else:
            st.caption("No products currently available in the database to receive stock.")

    with col_act2:
        st.markdown("#### 🔄 Reconcile Sales Against Inventory")
        st.caption("Decoupled batch ledger reconciliation deducting sold quantities while preventing negative stock overdrafts:")
        if st.button("⚖️ Run Batch Sales Deduction Simulation", use_container_width=True):
            rec_result = reconcile_sales_deduction(df_filtered)
            if rec_result.get("success") or rec_result.get("status") == "success":
                p_reconciled = rec_result.get("products_reconciled", rec_result.get("deducted_items", 0))
                units_deducted = rec_result.get("total_units_deducted", 0)
                st.success(f"Reconciled {p_reconciled} products! Total units deducted from warehouse ledger: {units_deducted:,}.")
                st.rerun()
            elif rec_result.get("shortfalls"):
                st.warning("⚠️ Reconciliation aborted: Some products have insufficient stock to cover sales volume.")
                for sf in rec_result["shortfalls"]:
                    st.caption(f"• {sf['product']}: Current stock {sf['current_stock']} < Requested {sf['requested_deduction']} (Shortfall: {sf['shortfall']})")
            else:
                err_msg = rec_result.get("message", rec_result.get("errors", ["Unknown reconciliation error"]))
                st.error(f"Reconciliation error: {err_msg}")


# -------------------------------------------------------------
# TAB 8: ANOMALY DETECTION (NEW)
# -------------------------------------------------------------
with tabs[7]:
    st.subheader("🚨 Automated Anomaly & Data Quality Engine")
    st.caption(
        "Dual-layer detection: Deterministic business rules (arithmetic mismatches, negative quantities, "
        "corrupted ratings) combined with statistical distribution models (Tukey's IQR method & temporal surge analysis)."
    )

    # Anomaly KPI Cards
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="metric-card">
            <div class="metric-title">Total Anomalies</div>
            <div class="metric-value">{anomaly_summary['total_anomalies']}</div>
            <div class="metric-subtitle">Flagged Issues</div>
        </div>
        <div class="metric-card" style="border-left: 3px solid #dc2626;">
            <div class="metric-title" style="color: #f87171;">Critical</div>
            <div class="metric-value" style="color: #f87171;">{anomaly_summary['by_severity'].get('CRITICAL', 0)}</div>
            <div class="metric-subtitle">Severe Violations</div>
        </div>
        <div class="metric-card" style="border-left: 3px solid #ea580c;">
            <div class="metric-title" style="color: #fb923c;">High</div>
            <div class="metric-value" style="color: #fb923c;">{anomaly_summary['by_severity'].get('HIGH', 0)}</div>
            <div class="metric-subtitle">Statistical Outliers</div>
        </div>
        <div class="metric-card">
            <div class="metric-title">Medium / Low</div>
            <div class="metric-value">{anomaly_summary['by_severity'].get('MEDIUM', 0) + anomaly_summary['by_severity'].get('LOW', 0)}</div>
            <div class="metric-subtitle">Warnings & Audits</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if detected_anomalies:
        col_anom_btn1, col_anom_btn2 = st.columns([1, 1])
        with col_anom_btn1:
            if st.button("💾 Persist Detected Anomalies to SQLite Audit Log", use_container_width=True):
                logged_count = log_anomalies_to_db(detected_anomalies)
                st.success(f"Persisted {logged_count} anomaly records to the relational database!")

        st.markdown("#### Detected Anomalies List")
        anom_table_data = []
        for a in detected_anomalies:
            anom_table_data.append({
                "Invoice ID": a.get("invoice_id", "N/A"),
                "Error Type": a.get("error_type", ""),
                "Severity": a.get("severity", ""),
                "Affected Field": a.get("affected_field", ""),
                "Recorded": a.get("recorded_value", ""),
                "Expected": a.get("expected_value", ""),
                "Description": a.get("description", ""),
                "Recommended Action": a.get("action_recommendation", ""),
            })
        st.dataframe(pd.DataFrame(anom_table_data), use_container_width=True, hide_index=True)
    else:
        st.success("✅ **Clean Data Audit:** No deterministic math discrepancies or statistical anomalies were detected in the active dataset view.")

    st.markdown("---")
    st.markdown("#### 🗄️ Relational Database Anomaly Audit Trail")
    db_anomalies = get_anomalies_from_db(status="OPEN")
    if db_anomalies:
        st.caption(f"Currently tracking {len(db_anomalies)} open anomalies in the SQLite database:")
        st.dataframe(pd.DataFrame(db_anomalies), use_container_width=True, hide_index=True)

        col_res1, col_res2 = st.columns([2, 1])
        with col_res1:
            anom_ids = [a["anomaly_id"] for a in db_anomalies]
            selected_anom_id = st.selectbox("Select Anomaly ID to Mark Resolved:", anom_ids, key="resolve_anom_sel")
            res_notes = st.text_input("Resolution Notes:", value="Verified corrected transaction via store manager", key="res_notes_input")
        with col_res2:
            st.write("")
            st.write("")
            if st.button("✅ Mark Anomaly Resolved", use_container_width=True):
                ok = resolve_anomaly_in_db(selected_anom_id, resolution_notes=res_notes)
                if ok:
                    st.success(f"Anomaly #{selected_anom_id} marked as RESOLVED.")
                    st.rerun()
    else:
        st.info("Zero open anomalies currently pending in the SQLite database.")


# -------------------------------------------------------------
# TAB 9: REPORT CENTER (NEW)
# -------------------------------------------------------------
with tabs[8]:
    st.subheader("📄 Executive Report Center")
    st.caption(
        "Generate and download publication-ready executive briefings and comprehensive workbooks "
        "incorporating active filters, financial KPIs, 4-tier business insights, and inventory status."
    )

    col_rep1, col_rep2, col_rep3 = st.columns(3)

    # 1. PDF Briefing
    with col_rep1:
        st.markdown("""
        <div class="report-export-box">
            <h4 style="color:#38bdf8; margin-top:0;">📑 Executive PDF Briefing</h4>
            <p style="font-size:0.84rem; color:#cbd5e1;">
                Publication-ready PDF document built with ReportLab Flowable architecture, dynamic page budgeting,
                4-tier strategic recommendations, and high-contrast tables.
            </p>
        </div>
        """, unsafe_allow_html=True)
        try:
            pdf_buf = generate_pdf_report(
                df=df_filtered,
                dataset_name=active_dataset_name,
                filter_summary=active_filter_summary,
                insights=structured_insights,
                anomalies=detected_anomalies,
                inventory_df=inv_intel_df
            )
            st.download_button(
                label="📥 Download Executive PDF Briefing",
                data=pdf_buf.getvalue(),
                file_name=f"Executive_Sales_Report_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True,
                on_click=lambda: log_report_generation(
                    report_type="PDF",
                    dataset_scope=active_dataset_name,
                    filter_summary_json=str(active_filter_summary),
                    total_sales_analyzed=float(kpis["total_sales"]),
                    total_transactions=int(kpis["total_transactions"])
                )
            )
        except Exception as ex:
            st.error(f"Error compiling PDF: {ex}")

    # 2. Multi-Sheet Excel Workbook
    with col_rep2:
        st.markdown("""
        <div class="report-export-box">
            <h4 style="color:#4ade80; margin-top:0;">📊 Multi-Sheet Excel Report</h4>
            <p style="font-size:0.84rem; color:#cbd5e1;">
                Enterprise-grade workbook with 7 styled sheets: Executive Summary, Transactions, Products, Categories,
                Inventory Intelligence, Anomaly Log, and Insights Matrix.
            </p>
        </div>
        """, unsafe_allow_html=True)
        try:
            excel_buf = generate_excel_workbook(
                df=df_filtered,
                dataset_name=active_dataset_name,
                filter_summary=active_filter_summary,
                insights=structured_insights,
                anomalies=detected_anomalies,
                inventory_df=inv_intel_df
            )
            st.download_button(
                label="📊 Download Excel Workbook (.xlsx)",
                data=excel_buf.getvalue(),
                file_name=f"Supermarket_Intelligence_Report_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                on_click=lambda: log_report_generation(
                    report_type="Excel",
                    dataset_scope=active_dataset_name,
                    filter_summary_json=str(active_filter_summary),
                    total_sales_analyzed=float(kpis["total_sales"]),
                    total_transactions=int(kpis["total_transactions"])
                )
            )
        except Exception as ex:
            st.error(f"Error compiling Excel: {ex}")

    # 3. Filtered Raw CSV
    with col_rep3:
        st.markdown("""
        <div class="report-export-box">
            <h4 style="color:#fbbf24; margin-top:0;">📄 Filtered Dataset CSV</h4>
            <p style="font-size:0.84rem; color:#cbd5e1;">
                Export active filtered transaction data formatted as an RFC-4180 compliant CSV for downstream data modeling,
                R scripts, or external BI tools.
            </p>
        </div>
        """, unsafe_allow_html=True)
        csv_str = generate_csv_export(df_filtered)
        st.download_button(
            label="📄 Download Filtered CSV",
            data=csv_str.encode("utf-8"),
            file_name=f"Filtered_Transactions_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
            on_click=lambda: log_report_generation(
                report_type="CSV",
                dataset_scope=active_dataset_name,
                filter_summary_json=str(active_filter_summary),
                total_sales_analyzed=float(kpis["total_sales"]),
                total_transactions=int(kpis["total_transactions"])
            )
        )

    st.markdown("---")
    st.markdown("#### 📜 Report Generation History (SQLite Audit)")
    rep_history = get_report_history(limit=10)
    if rep_history:
        st.dataframe(pd.DataFrame(rep_history), use_container_width=True, hide_index=True)
    else:
        st.info("No report generation events logged yet.")


# -------------------------------------------------------------
# TAB 10: DATABASE & CRUD (NEW - CAPSTONE SHOWCASE)
# -------------------------------------------------------------
with tabs[9]:
    st.subheader("🗄️ Relational Database & Master Data Operations")
    st.caption(
        "Demonstrates relational DBMS principles (ACID transactions, foreign key integrity, "
        "and double-entry inventory ledger accounting) implemented in Python's built-in sqlite3."
    )

    db_crud_choice = st.radio(
        "Database Management Area:",
        ["Product Catalog CRUD", "Inventory Ledger Audit", "Database Health & Factory Reset"],
        horizontal=True
    )

    if db_crud_choice == "Product Catalog CRUD":
        st.markdown("#### Master Product Catalog")
        all_prods = get_all_products()
        if all_prods:
            st.dataframe(pd.DataFrame(all_prods), use_container_width=True, hide_index=True)

        col_prod_add, col_prod_upd = st.columns(2)
        with col_prod_add:
            with st.expander("➕ Add New Product SKU", expanded=False):
                new_sku = st.text_input("Product SKU Code:", value="SKU-NEW-01", key="add_sku")
                new_name = st.text_input("Product Name:", value="Premium Greek Yogurt", key="add_name")
                cats = get_all_categories()
                cat_choices = {c["category_name"]: c["category_id"] for c in cats}
                sel_cat_name = st.selectbox("Category:", list(cat_choices.keys()), key="add_cat")
                new_cost = st.number_input("Unit Cost ($):", min_value=0.01, value=5.0, step=0.5, key="add_cost")
                new_price = st.number_input("Selling Price ($):", min_value=0.01, value=9.5, step=0.5, key="add_price")
                new_safety = st.number_input("Safety Stock Level:", min_value=1, value=20, key="add_safety")
                new_stock = st.number_input("Initial Warehouse Stock:", min_value=0, value=60, key="add_stock")

                if st.button("Save New Product", use_container_width=True):
                    pid = create_product(
                        sku=new_sku,
                        name=new_name,
                        category_id=cat_choices[sel_cat_name],
                        unit_cost=new_cost,
                        selling_price=new_price,
                        safety_stock=new_safety,
                        initial_stock=new_stock
                    )
                    st.success(f"Product created successfully with ID #{pid}!")
                    st.rerun()

        with col_prod_upd:
            with st.expander("✏️ Update Product Pricing or Stock Thresholds", expanded=False):
                if all_prods:
                    prod_map = {f"{p['product_name']} ({p['product_sku']})": p for p in all_prods}
                    sel_p_label = st.selectbox("Select Product to Update:", list(prod_map.keys()), key="upd_p_sel")
                    target = prod_map[sel_p_label]

                    upd_price = st.number_input("New Selling Price ($):", value=float(target["selling_price"]), key="upd_price")
                    upd_safety = st.number_input("New Safety Stock:", value=int(target["safety_stock_level"]), key="upd_safety")
                    upd_active = st.checkbox("Active Status", value=bool(target["is_active"]), key="upd_active")

                    if st.button("Update Product Details", use_container_width=True):
                        ok = update_product(
                            product_id=target["product_id"],
                            selling_price=upd_price,
                            safety_stock_level=upd_safety,
                            is_active=1 if upd_active else 0
                        )
                        if ok:
                            st.success(f"Updated product '{target['product_name']}'!")
                            st.rerun()

    elif db_crud_choice == "Inventory Ledger Audit":
        st.markdown("#### Append-Only Inventory Ledger (`inventory_movements`)")
        st.caption("Immutable transaction history preventing phantom inventory or unauthorized stock balances:")
        movements = get_inventory_movements(limit=50)
        if movements:
            st.dataframe(pd.DataFrame(movements), use_container_width=True, hide_index=True)
        else:
            st.info("No stock movement events recorded in the ledger yet.")

    else:
        st.markdown("#### 🔄 Database Maintenance & Reset")
        st.warning("Re-seeding will restore the SQLite database back to the factory 500 baseline transaction records and baseline SKU catalog.")
        if st.button("⚠️ Reset / Re-seed SQLite Database to Factory Baseline", use_container_width=False):
            # Purge and re-seed
            seed_database_if_empty(force_reseed=True)
            st.success("Database successfully reset and seeded with baseline retail catalog and 500 sales transactions!")
            st.rerun()


# -------------------------------------------------------------
# TAB 11: DATA EXPLORER & EXPORT
# -------------------------------------------------------------
with tabs[10]:
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
