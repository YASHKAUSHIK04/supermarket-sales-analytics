# Supermarket Sales & Customer Analytics Dashboard

![Project Status](https://img.shields.io/badge/Status-Upgraded%20%26%20Tested-success)
![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red)
![Analytics](https://img.shields.io/badge/Analytics-Pandas%20%7C%20Plotly-green)
![Tests](https://img.shields.io/badge/Unit%20Tests-11%20Passed-brightgreen)

**Project Owner**: [Yash Kaushik](https://github.com/YASHKAUSHIK04)  
**Repository**: [github.com/YASHKAUSHIK04/supermarket-sales-analytics](https://github.com/YASHKAUSHIK04/supermarket-sales-analytics)  

A portfolio-ready **Data Analytics Application** delivering end-to-end business intelligence, customer segmentation, dynamic dataset upload (CSV & Excel), automated column mapping, and product performance analytics for retail supermarket chains.

---

## 📌 Executive Summary & Business Problem

Retail supermarket operations generate high-velocity transaction streams encompassing diverse customer segments, varying merchandise categories, and changing payment preferences across different regional branches. Without structured data analytics and interactive executive dashboards, retail leaders face significant operational friction:

1. **Revenue vs. Volume Disconnect**: High-volume staple items often generate modest revenue per unit, while premium beverage, personal care, and dairy items drive major gross cash flow.
2. **Customer Segmentation Blind Spots**: Supermarket managers often lack visibility into whether membership loyalty tiers actually deliver higher Average Transaction Values (ATV) or simply increase repeat purchase frequency.
3. **Regional Branch Discrepancies**: Variance across branches (Jaipur, Mumbai, Delhi, Bengaluru) requires localized inventory allocations and targeted category promotions.
4. **Digital Settlement Adoption**: Fast-moving consumer goods (FMCG) retailers need accurate visibility into payment methods (UPI, Net Banking, Card, Cash) to optimize checkout counter throughput and banking fee reconciliation.
5. **Universal Dataset Portability**: Store operators need the ability to seamlessly upload external CSV or Excel spreadsheets, automatically reconcile differing column naming schemes, validate mathematical integrity, and instantly generate interactive visual analytics.

This project delivers a complete solution: ingesting, validating, transforming, and visualizing both the baseline **500 authentic transaction records** and **any user-uploaded retail dataset** through an interactive Streamlit and Plotly dashboard.

---

## 🎯 Upgraded Core Features

### 1. 📤 Universal Dataset Upload (CSV & Excel)
- **Multi-Format Support**: Ingest `.csv` (with UTF-8 and Latin-1 encoding fallbacks) and Excel `.xlsx` / `.xls` spreadsheets via `openpyxl`.
- **Smart Column Alias Detection**: Automatically maps common retail header variations to canonical fields.
- **Interactive Manual Mapping**: If non-standard column headers are encountered, users can easily map them via an intuitive Streamlit dropdown interface.
- **Missing Metric Computation**: If `Sales` is omitted, it is automatically computed as $\text{Sales} = \text{Quantity} \times \text{Unit Price}$. If `Unit Price` is missing, it is derived as $\text{Sales} \div \text{Quantity}$.
- **Mathematical Integrity & Discrepancy Auditing**: Real-time validation checks whether $\text{Sales} = \text{Quantity} \times \text{Unit Price}$. Any discrepancies ($> ₹0.05$) are highlighted in an audit report.

### 2. ⚡ Dynamic Reactive Filters
- **Zero-Stale State Re-indexing**: Switching between datasets immediately flushes stale filter selections, preventing `KeyError` or empty DataFrame collisions.
- **Dynamic Date Bounds & Categories**: Date pickers and multi-select filters dynamically populate from the active dataset.
- **Active Dataset Badge**: Header banner clearly identifies the currently analyzed dataset name, record count, and active filter subset.

### 3. 🔬 Robust Business Intelligence & Standardized Currency
- **Defensive Insight Engine**: Empirical insight calculations dynamically adapt to single-city, single-category, or non-standard customer loyalty tiers without crashes.
- **Consistent Currency Formatting**: All metric cards, Plotly charts, hover tooltips, and data tables uniformly use the Indian Rupee symbol (**₹**).
- **Strict Empirical Integrity**: Zero fabricated metrics (no invented profit, COGS, margins, or synthetic customers).

---

## 📊 Dataset Schema & Canonical Data Dictionary

| Canonical Column | Data Type | Recognized Aliases / Variations | Description |
| :--- | :--- | :--- | :--- |
| **Invoice ID** | String | `invoice_id`, `invoice no`, `order id`, `bill no`, `id`, `txn_id` | Alphanumeric invoice identifier |
| **Date** | Datetime | `invoice date`, `order date`, `txn date`, `sale date`, `timestamp` | Date of customer purchase |
| **Branch** | Category | `store`, `outlet`, `branch id`, `store id`, `location id` | Retail branch identifier |
| **City** | Category | `location`, `region`, `town`, `market`, `metro` | City where branch operates |
| **Customer Type** | Category | `customer_type`, `membership`, `member type`, `loyalty tier` | Customer loyalty status (`Member` / `Normal`) |
| **Gender** | Category | `sex` | Customer gender (`Male` / `Female`) |
| **Product** | Category | `product name`, `item`, `item name`, `sku`, `description` | Specific retail SKU purchased |
| **Category** | Category | `product category`, `department`, `dept`, `merchandise group` | Merchandise department |
| **Quantity** | Integer | `qty`, `units`, `quantity sold`, `volume`, `count` | Units purchased (1–10) |
| **Unit Price** | Float (₹) | `price`, `rate`, `unit cost`, `mrp`, `selling price` | Price per single product unit |
| **Payment** | Category | `payment method`, `mode`, `payment mode`, `payment type`, `tender` | Payment method utilized at POS |
| **Rating** | Float | `satisfaction`, `score`, `feedback`, `stars`, `csat` | Customer satisfaction rating (1.0–5.0) |
| **Sales** | Float (₹) | `total sales`, `total`, `amount`, `revenue`, `gross sales` | Total transaction amount ($\text{Qty} \times \text{Price}$) |

---

## 🛠️ Technology Stack

- **Core Language**: Python 3.12+ (64-bit AMD64)
- **Data Manipulation**: Pandas 2.2+, NumPy 1.26+
- **Spreadsheet Parsing**: openpyxl 3.1+
- **Interactive Visualization**: Plotly Express, Plotly Graph Objects 5.20+
- **Web Dashboard**: Streamlit 1.35+
- **Notebook & Research**: Jupyter Notebook (`nbformat`, `ipykernel`)
- **Automated Testing**: Python `unittest` framework (11 passing tests)

---

## 📁 Project Architecture

```
supermarket-sales-analytics/
│
├── data/
│   ├── raw/
│   │   ├── supermarket_sales_raw.txt          # Original unedited OCR text dump
│   │   └── supermarket_sales_raw.csv          # Reconstructed tabular raw dataset
│   └── processed/
│       └── supermarket_sales_cleaned.csv      # Cleaned baseline dataset (500 records)
│
├── notebooks/
│   └── supermarket_eda.ipynb                  # Executed & annotated Jupyter EDA notebook
│
├── src/
│   ├── __init__.py                            # Module package initializer
│   ├── data_cleaning.py                       # OCR parsing and baseline cleaning pipeline
│   ├── data_loader.py                         # Multi-format CSV/Excel upload & validation engine
│   ├── analysis.py                            # Modular KPI engine, aggregations, & defensive insights
│   └── visualization.py                       # Plotly figures, unified layouts, & ₹ currency styling
│
├── tests/
│   ├── __init__.py                            # Test package initializer
│   └── test_upload_and_analysis.py            # Automated test suite (11 unit tests)
│
├── app.py                                     # Interactive Streamlit dashboard application
├── requirements.txt                           # Pinned package dependencies (including openpyxl)
├── README.md                                  # Complete project documentation
├── .gitignore                                 # Git ignore patterns
└── PROJECT_REPORT_CONTENT.md                  # Comprehensive formal internship report
```

---

## 💻 Dashboard Tabs & Visualizations

1. **📈 Sales Overview**: Monthly / Daily / Day-of-Week sales trendlines with dual-axis transaction counts, city sales donut chart, and branch/category bar charts.
2. **🛍️ Product Analysis**: Top 10 by Revenue vs. Top 10 by Volume sold, plus a High-Volume vs High-Value bubble scatter matrix ($\text{Unit Price} \times \text{Quantity}$).
3. **👥 Customer Analysis**: Member vs. Normal spending behavior, gender distribution, segment interaction bar charts, and Average Transaction Value (ATV).
4. **💳 Payment Analytics**: Payment channel share donut chart, ATV per payment mode, and customer type preference cross-tabulation table.
5. **⭐ Ratings & Feedback**: Customer rating histogram with mean line, alongside category, city, and customer-type satisfaction comparisons.
6. **💡 Key Business Insights**: Empirical data-derived observations dynamically adapted to active data, accompanied by strategic operational recommendations.
7. **📋 Data Explorer**: Full filtered data table with sorting, column statistics, and CSV download capability.

---

## 🧪 Automated Testing

The project includes an automated test suite verifying data ingestion, alias mapping, mathematical assertions, defensive insight calculations, and empty-state handling.

Run tests using Python 3.12:
```powershell
py -3.12 -m unittest discover -s tests -p "test_*.py" -v
```

### Test Coverage Results:
```text
test_csv_upload_aliased_columns ... ok
test_csv_upload_exact_columns ... ok
test_default_dataset_integrity ... ok
test_defensive_insights_custom_customer_types ... ok
test_defensive_insights_single_city ... ok
test_empty_dataframe_handling ... ok
test_excel_upload_xlsx ... ok
test_math_discrepancy_detection ... ok
test_missing_required_columns ... ok
test_missing_sales_auto_calculation ... ok
test_missing_unit_price_auto_calculation ... ok

----------------------------------------------------------------------
Ran 11 tests in 1.18s

OK
```

---

## 🚀 Local Installation & Execution

### 1. Prerequisites
Ensure you have Python 3.12+ (64-bit) installed.

### 2. Clone the Repository
```powershell
git clone https://github.com/YASHKAUSHIK04/supermarket-sales-analytics.git
cd supermarket-sales-analytics
```

### 3. Install Dependencies
```powershell
py -3.12 -m pip install -r requirements.txt
```

### 4. Run the Baseline Data Pipeline (Optional)
```powershell
py -3.12 src/data_cleaning.py
```

### 5. Launch the Streamlit Dashboard
```powershell
py -3.12 -m streamlit run app.py
```
The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## ☁️ Streamlit Cloud Deployment Guide

1. Push your updated repository to GitHub:
   ```powershell
   git add .
   git commit -m "Upgrade: CSV/Excel upload, alias mapping, dynamic filters, test suite"
   git push origin master
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **"New app"** and select:
   - **Repository**: `YASHKAUSHIK04/supermarket-sales-analytics`
   - **Branch**: `master`
   - **Main file path**: `app.py`
4. Click **"Deploy!"**. Streamlit Cloud will automatically install all dependencies from `requirements.txt` (including `openpyxl`) and host your dashboard live.

---

## 📈 Key Verifiable Findings (Baseline Dataset)

1. **Price-Driven vs Volume-Driven SKUs**: Products like `Cheese` (Unit price ~₹200–₹235), `Coffee` (~₹170–₹195), and `Shampoo` (~₹165–₹195) generate the highest sales revenue despite modest purchase counts. Conversely, `Potato` (194 units), `Chips` (168 units), and `Rice` (167 units) lead unit volume.
2. **Loyalty Program Dynamics**: Customer Type breakdown shows 296 transactions from Members (59.2%) and 204 from Normal shoppers (40.8%). The similarity in ATV (~₹483 vs ₹497) indicates that membership acts primarily as a visit-frequency driver rather than an order-size inflator.
3. **Geographic Distribution**: Mumbai (Branch C) leads total sales with ₹72,469.45 (29.7%), followed by Delhi (₹64,116.26), Bengaluru (₹55,468.29), and Jaipur (₹52,357.08).
4. **Digital Settlement Dominance**: UPI and Net Banking combined account for **54.5%** of revenue with significantly higher ATV (>₹515) than Cash (₹442.95).

---

## 👤 Author & Attribution

- **Project Lead**: [Yash Kaushik](https://github.com/YASHKAUSHIK04)
- **Repository**: [YASHKAUSHIK04/supermarket-sales-analytics](https://github.com/YASHKAUSHIK04/supermarket-sales-analytics)
- **License**: MIT Open Source License
