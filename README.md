# Supermarket Sales & Customer Analytics Dashboard

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red)
![Analytics](https://img.shields.io/badge/Analytics-Pandas%20%7C%20Plotly-green)

A production-grade, portfolio-ready **Data Analyst Internship Project** delivering end-to-end business intelligence, customer segmentation, and product performance analytics for a multi-city retail supermarket chain across India.

---

## 📌 Executive Summary & Business Problem

Retail supermarket operations generate high-velocity transaction streams encompassing diverse customer segments, varying merchandise categories, and changing payment preferences across different regional branches. Without structured data analytics and interactive executive dashboards, retail leaders face significant operational friction:

1. **Revenue vs. Volume Disconnect**: High-volume staple items often generate modest revenue per unit, while premium beverage, personal care, and dairy items drive major gross cash flow.
2. **Customer Segmentation Blind Spots**: Supermarket managers often lack visibility into whether membership loyalty tiers actually deliver higher Average Transaction Values (ATV) or simply increase repeat purchase frequency.
3. **Regional Branch Discrepancies**: Variance across branches (Jaipur, Mumbai, Delhi, Bengaluru) requires localized inventory allocations and targeted category promotions.
4. **Digital Settlement Adoption**: Fast-moving consumer goods (FMCG) retailers need accurate visibility into payment methods (UPI, Net Banking, Card, Cash) to optimize checkout counter throughput and banking fee reconciliation.

This project addresses these challenges by ingesting, validating, transforming, and visualizing **500 authentic transaction records**, presenting executive insights through an interactive Streamlit and Plotly dashboard.

---

## 🎯 Project Objectives

- Ingest and reconstruct multi-line raw OCR records extracted from PDF documents with 100% mathematical integrity.
- Build a reproducible, audit-logged data cleaning pipeline handling missing values, datatypes, and derived fields.
- Perform exploratory data analysis (EDA) investigating sales velocity, customer types, gender behaviors, product performance, payment channels, and satisfaction ratings.
- Create an interactive, responsive business analytics dashboard with dynamic multi-select filters, filter reset capabilities, and empty-state safeguards.
- Formulate factual, verifiable business insights strictly backed by empirical metrics—avoiding fabricated variables (such as fake profit/costs) or unproven causal claims.

---

## 📊 Dataset Description & Data Dictionary

The analysis is based strictly on the provided supermarket sales dataset containing **500 unique transaction records** spanning January 2026 to July 2026 across four major Indian metropolitan branches.

### Data Dictionary

| Column Name | Data Type | Description | Example Values |
| :--- | :--- | :--- | :--- |
| **Invoice ID** | String / Object | Unique alphanumeric invoice transaction identifier | `INV0001`, `INV0042` |
| **Date** | Datetime (`YYYY-MM-DD`) | Date of transaction purchase | `2026-06-01`, `2026-01-12` |
| **Branch** | Category | Supermarket branch identifier | `A`, `B`, `C`, `D` |
| **City** | Category | City where the supermarket branch operates | `Jaipur`, `Mumbai`, `Delhi`, `Bengaluru` |
| **Customer Type** | Category | Loyalty classification of customer | `Member`, `Normal` |
| **Gender** | Category | Customer biological gender | `Male`, `Female` |
| **Product** | Category | Specific retail SKU purchased (20 products) | `Cooking Oil`, `Milk`, `Tea`, `Cheese` |
| **Category** | Category | Broad merchandise department (8 categories) | `Dairy`, `Grocery`, `Personal Care`, etc. |
| **Quantity** | Integer (1–10) | Number of units purchased per transaction | `1`, `4`, `10` |
| **Unit Price** | Float (Rs.) | Selling price per single product unit | `57.13`, `219.06` |
| **Payment** | Category | Payment method utilized at point of sale | `UPI`, `Net Banking`, `Card`, `Cash` |
| **Rating** | Float (1.0–5.0) | Post-purchase customer satisfaction score | `3.8`, `4.5`, `5.0` |
| **Sales** | Float (Rs.) | Total transaction revenue ($Quantity \times Unit Price$) | `228.52`, `1308.78` |

### Derived Feature Engineering Fields

| Derived Field | Formula / Logic | Business Rationale |
| :--- | :--- | :--- |
| **Year** | `Date.dt.year` | Annual aggregation (2026) |
| **Month** | `Date.dt.month` | Monthly trend evaluation (1–7) |
| **Month_Name** | `Date.dt.strftime('%B')` | Human-readable monthly groupings |
| **Day** | `Date.dt.day` | Day of month distribution (1–31) |
| **Day_Of_Week** | `Date.dt.day_name()` | Weekly cyclicality and weekend shopping surge |
| **Transaction_Value** | Identical to `Sales` | Standardized retail analytics terminology |
| **Sales_Per_Quantity** | `Sales / Quantity` | Empirical verification of `Unit Price` consistency |

---

## 🛠️ Technology Stack

- **Core Language**: Python 3.12+ (64-bit AMD64)
- **Data Manipulation & Ingestion**: Pandas, NumPy
- **Interactive Visualization**: Plotly Express, Plotly Graph Objects
- **Web Application Framework**: Streamlit
- **Notebook & Research**: Jupyter Notebook (`nbformat`, `ipykernel`)
- **Version Control & Quality**: Git, Flake8 / PEP-8 standards

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
│       └── supermarket_sales_cleaned.csv      # Cleaned, validated, feature-engineered dataset
│
├── notebooks/
│   └── supermarket_eda.ipynb                  # Fully executed & annotated Jupyter EDA notebook
│
├── src/
│   ├── __init__.py                            # Module package initialiser
│   ├── data_cleaning.py                       # Automated parsing, data checks, and feature engineering
│   ├── analysis.py                            # KPI engine, aggregations, cross-tabs, insight generator
│   └── visualization.py                       # Standardized Plotly figure templates & palettes
│
├── app.py                                     # Interactive Streamlit dashboard application
├── requirements.txt                           # Pinned Python package dependencies
├── README.md                                  # Complete GitHub repository documentation
├── .gitignore                                 # Git configuration ignores
└── PROJECT_REPORT_CONTENT.md                  # Comprehensive 21-section formal internship report
```

---

## 🧹 Data Cleaning & Validation Pipeline

The source PDF contained transactions with word wraps and multi-line breaks caused by optical character recognition (e.g. multi-word products like `Face Wash`, `Cooking Oil`, and multi-word payment methods like `Net Banking`).

The automated cleaning pipeline (`src/data_cleaning.py`) executes:
1. **Logical Record Boundary Reconstruction**: Regex boundary grouping on invoice pattern `INV\d{4}` to reconstruct wrapped rows into single record strings.
2. **Multi-token Regular Expression Matching**: Strict deterministic pattern matching against known categorical dictionaries and numeric formats.
3. **Data Type Casting**: Converts date strings to `datetime64[ns]`, counts to integers, prices/sales to rounded 2-decimal floats, and categories to memory-efficient pandas `category` dtypes.
4. **Mathematical Integrity Assertions**:
   $$\max |\text{Sales} - (\text{Quantity} \times \text{Unit Price})| \le 0.05$$
   Verified across all 500 records with **zero discrepancies**.
5. **Quality Check Summary**:
   - Total records parsed: **500 / 500 (100%)**
   - Missing values: **0**
   - Duplicate Invoice IDs: **0**
   - Invalid ratings or negative quantities: **0**

---

## 🔬 Exploratory Data Analysis (Key Questions Answered)

The analysis in `notebooks/supermarket_eda.ipynb` directly addresses core retail questions:

1. **What is the chain's total gross sales and average transaction size?**
   - Gross Revenue: **Rs. 2,44,411.08** across 500 transactions.
   - Overall Average Transaction Value (ATV): **Rs. 488.82**.
   - Total Units Sold: **2,768 units**.
2. **Which cities and branches generate the highest revenue?**
   - **Mumbai (Branch C):** Rs. 72,469.45 (143 transactions, ATV: Rs. 506.78)
   - **Delhi (Branch B):** Rs. 64,116.26 (133 transactions, ATV: Rs. 482.08)
   - **Bengaluru (Branch D):** Rs. 55,468.29 (119 transactions, ATV: Rs. 466.12)
   - **Jaipur (Branch A):** Rs. 52,357.08 (105 transactions, ATV: Rs. 498.64)
   - All 4 branches operate within a tight performance band, with Mumbai generating the highest overall sales volume.
3. **Which categories and individual products are the primary revenue drivers?**
   - **Top Categories by Revenue:** **Beverages** (Rs. 56,108.24), **Personal Care** (Rs. 45,943.96), **Dairy** (Rs. 43,992.00), and **Grocery** (Rs. 40,470.47).
   - **Top Products by Revenue:** **Cheese** (Rs. 27,906.30), **Coffee** (Rs. 27,694.87), **Shampoo** (Rs. 27,497.48), and **Cooking Oil** (Rs. 21,525.06).
   - **Top Products by Quantity Volume:** **Potato** (194 units), **Chips** (168 units), **Rice** (167 units), **Cold Drink** (166 units), and **Bread** (164 units).
4. **Do loyalty program Members spend significantly more than Normal customers?**
   - Members generated **Rs. 1,43,009.30** across 296 transactions (ATV: **Rs. 483.14**).
   - Normal shoppers generated **Rs. 101,401.78** across 204 transactions (ATV: **Rs. 497.07**).
   - Normal shoppers have a slightly higher ATV (+Rs. 13.93), proving that membership acts as a transaction visit frequency driver (59.2% of transactions) rather than an order-size inflator.
5. **Which payment channels dominate checkout lanes?**
   - **UPI:** Rs. 67,910.33 (127 transactions, ATV: Rs. 534.73)
   - **Net Banking:** Rs. 65,194.93 (126 transactions, ATV: Rs. 517.42)
   - **Card:** Rs. 57,265.64 (125 transactions, ATV: Rs. 458.13)
   - **Cash:** Rs. 54,040.18 (122 transactions, ATV: Rs. 442.95)
   - Digital settlement methods (UPI + Net Banking) account for **54.5%** of gross sales and higher order sizes compared to Cash.

---

## 💻 Dashboard Features & Capabilities

The Streamlit dashboard (`app.py`) provides:

- **Executive KPI Ribbon**: Real-time cards displaying Total Sales, Total Quantity Sold, Total Transactions, Average Order Value (ATV), Average Rating (with star icon), Filtered SKUs, and Filtered Categories.
- **Dynamic Sidebar Filters**:
  - Date Range selector
  - City (Multi-select)
  - Branch (Multi-select)
  - Product Category (Multi-select)
  - Product (Multi-select, dynamically filtered by selected categories)
  - Customer Type (Member / Normal)
  - Gender (Male / Female)
  - Payment Method (UPI, Net Banking, Card, Cash)
  - **Reset Filters Button**: One-click restore to full dataset.
  - **Graceful Empty State**: Clear warning banner without application crashes.
- **7 Dedicated Analytical Views (Tabs)**:
  1. **Sales Overview**: Monthly/Daily/Day-of-Week sales trendline with dual-axis transaction counts, city sales donut chart, and branch/category bar charts.
  2. **Product Analysis**: Side-by-side comparison of Top 10 by Revenue vs. Top 10 by Quantity, plus a scatter quadrant matrix (Unit Price vs Quantity with bubble size = Sales).
  3. **Customer Analysis**: Member vs Normal comparison, gender distribution, segment heatmaps, and ATV analysis.
  4. **Payment Analytics**: Donut charts for transaction share vs revenue share, ATV per payment mode, and cross-tabulation table.
  5. **Ratings & Feedback**: Customer rating histogram with average reference line, plus category/city/customer-type satisfaction breakdowns.
  6. **Key Business Insights**: Empirical, data-derived insight cards and strategic operational recommendations.
  7. **Data Explorer**: Interactive table with column sorting, summary statistics, and one-click CSV export.

---

## 🚀 Installation & Running Instructions

### 1. Prerequisites
Ensure you have Python 3.12+ (64-bit) installed.

### 2. Clone / Navigate to Directory
```powershell
cd C:\Users\Admin\.gemini\antigravity\scratch\supermarket-sales-analytics
```

### 3. Install Dependencies
```powershell
py -3.12 -m pip install -r requirements.txt
```

### 4. Run the Data Pipeline (Extract, Clean, Validate)
```powershell
py -3.12 src/data_cleaning.py
```

### 5. Launch the Streamlit Dashboard
```powershell
py -3.12 -m streamlit run app.py
```
The dashboard will open automatically in your default browser at `http://localhost:8501`.

---

## 📈 Key Verifiable Findings

1. **Price-Driven vs Volume-Driven SKUs**: Products like `Cheese` (Unit price ~Rs. 200–235), `Coffee` (~Rs. 170–195), and `Shampoo` (~Rs. 165–195) generate the highest sales revenue despite modest purchase counts. Conversely, `Potato` (194 units), `Chips` (168 units), and `Rice` (167 units) lead unit volume and generate foot traffic.
2. **Loyalty Program Dynamics**: Customer Type breakdown shows 296 transactions from Members (59.2%) and 204 from Normal shoppers (40.8%). The similarity in ATV (~Rs. 483 vs Rs. 497) indicates that loyalty programs should implement minimum-spend tier bonuses to lift transaction values.
3. **Balanced Geographic Footprint**: Mumbai (Branch C) leads total sales with Rs. 72,469.45 (29.7%), followed closely by Delhi (Rs. 64,116.26), Bengaluru (Rs. 55,468.29), and Jaipur (Rs. 52,357.08).
4. **Digital Settlement Dominance**: UPI and Net Banking combined account for **54.5%** of revenue with significantly higher ATV (>Rs. 515) than Cash (Rs. 442.95).

---

## ⚠️ Known Limitations

- **Absence of Cost/Margin Data**: The dataset contains Sales and Unit Price but no Cost of Goods Sold (COGS). Gross margin, net profit, and item profitability cannot be computed without inventing numbers.
- **Lack of Time-of-Day Data**: Transactions record transaction dates but lack hour/minute timestamps, preventing rush-hour or daypart staffing analysis.
- **Cross-Sectional Timeframe**: 500 records spanning 7 months provide robust operational visibility across branches, but multi-year seasonal cycles (e.g. annual festival spikes) cannot be projected.

---

## 🔮 Future Scope

1. **Predictive Sales Forecasting**: Integrate ARIMA / Prophet models to forecast weekly inventory demand by product category.
2. **Market Basket Analysis (Apriori)**: If transaction data is expanded to multi-item baskets, apply Association Rule Mining to identify co-purchased SKUs.
3. **Customer Lifetime Value (CLV)**: Capture recurring customer identifiers to compute retention curves and churn probabilities.
