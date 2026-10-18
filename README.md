# Supermarket Sales & Retail Intelligence System

![Project Status](https://img.shields.io/badge/Status-Upgraded%20%26%20Production--Ready-success)
![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue)
![Backend](https://img.shields.io/badge/Backend-SQLite3%20Relational%20DB-lightgrey)
![Framework](https://img.shields.io/badge/Framework-Streamlit-red)
![Reporting](https://img.shields.io/badge/Reporting-ReportLab%20%7C%20openpyxl-orange)
![Tests](https://img.shields.io/badge/Unit%20Tests-46%20Passed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

**Project Owner**: [Yash Kaushik](https://github.com/YASHKAUSHIK04)  
**Academic Level**: BCA Capstone / Final Year Software & Data Engineering Project  
**Repository**: [github.com/YASHKAUSHIK04/supermarket-sales-analytics](https://github.com/YASHKAUSHIK04/supermarket-sales-analytics)

---

## 📌 Executive Overview

The **Supermarket Sales & Retail Intelligence System** is an enterprise-grade, full-stack business intelligence and data engineering application. Built with Python 3.12, Streamlit, and a persistent SQLite relational database, the system transforms raw supermarket point-of-sale (POS) data into real-time operational insights, inventory stock monitoring, automated data-quality anomaly auditing, and publication-ready executive PDF and Excel reports.

Unlike static dashboards, this system provides:
1. **Persistent Relational Database Backend**: Built-in `sqlite3` relational schema with foreign key constraints, indexes, transaction ACID semantics, and non-destructive CSV/Excel ingestion.
2. **Double-Entry Inventory Stock Ledger**: Real-time sales velocity monitoring, safety stock thresholds, days-of-stock countdown, and overdraft-protected ledger reconciliation.
3. **Dual-Layer Anomaly Detection**: Deterministic mathematical discrepancies and bounds checks combined with statistical outlier detection (Tukey's IQR method and temporal daily volume surges).
4. **4-Tier Business Insights**: Structured actionable recommendations following the **Observation ➔ Analytical Insight ➔ Possible Explanation ➔ Recommended Action** framework.
5. **Executive Reporting Engine**: Automated generation of styled multi-page PDF executive briefings via ReportLab flowables and 7-sheet formatted Excel audit workbooks via `openpyxl`.

---

## 🏗️ System Architecture

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                  USER PRESENTATION TIER                                │
│                     Streamlit Reactive Web Application (11 Analytical Tabs)             │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    ▼                                               ▼
┌───────────────────────────────────────┐       ┌────────────────────────────────────────┐
│         DATA INGESTION ENGINE         │       │          ANALYTICS & BI ENGINE         │
│  • CSV / Excel (openpyxl) Ingestion   │       │  • Sales, Product & Customer KPIs      │
│  • Smart Canonical Column Aliasing    │       │  • Plotly Express & Graph Objects      │
│  • Math & Bounds Validation Checks    │       │  • 4-Tier Prescriptive Insights        │
└───────────────────┬───────────────────┘       └───────────────────┬────────────────────┘
                    │                                               │
                    ▼                                               ▼
┌───────────────────────────────────────┐       ┌────────────────────────────────────────┐
│     INVENTORY & ANOMALY ENGINES       │       │        EXECUTIVE REPORT ENGINE         │
│  • Sales Velocity & Days Remaining    │       │  • ReportLab Two-Pass NumberedCanvas   │
│  • Automated Reorder Calculations     │       │  • Multi-Sheet Formatted Excel Reports │
│  • Tukey IQR & 2.5σ Surge Anomaly Log │       │  • RFC-4180 Compliant CSV Export       │
└───────────────────┬───────────────────┘       └───────────────────┬────────────────────┘
                    │                                               │
                    └───────────────────────┬───────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               RELATIONAL STORAGE ENGINE                                │
│                        SQLite 3 Persistent Database (WAL Mode)                         │
│  [categories] ──< [products] ──< [inventory_stock] ──< [inventory_movements]          │
│                       │                                                                │
│                       └──< [sales_transactions]  |  [anomaly_records]  |  [report_hist]│
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema & Relational Design

The system implements a normalized relational database in `data/supermarket_intelligence.db` enforcing strict primary and foreign key constraints (`PRAGMA foreign_keys = ON;`).

```sql
-- 1. Merchandise Categories
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Master Product Catalog
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_sku TEXT UNIQUE NOT NULL,
    product_name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(category_id),
    unit_cost REAL NOT NULL CHECK(unit_cost > 0),
    selling_price REAL NOT NULL CHECK(selling_price > 0),
    safety_stock_level INTEGER DEFAULT 15 CHECK(safety_stock_level >= 0),
    is_active INTEGER DEFAULT 1 CHECK(is_active IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Warehouse Stock Balance
CREATE TABLE inventory_stock (
    stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER UNIQUE NOT NULL REFERENCES products(product_id),
    current_stock INTEGER NOT NULL CHECK(current_stock >= 0),
    reorder_point INTEGER NOT NULL DEFAULT 20,
    last_restocked_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Immutable Stock Movement Ledger
CREATE TABLE inventory_movements (
    movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    movement_type TEXT NOT NULL CHECK(movement_type IN ('receipt', 'sale_deduction', 'adjustment', 'return')),
    quantity_change INTEGER NOT NULL,
    resulting_stock INTEGER NOT NULL CHECK(resulting_stock >= 0),
    reference_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Sales Transactions
CREATE TABLE sales_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id TEXT UNIQUE NOT NULL,
    branch TEXT NOT NULL,
    city TEXT NOT NULL,
    customer_type TEXT NOT NULL,
    gender TEXT NOT NULL,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    unit_price REAL NOT NULL CHECK(unit_price > 0),
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    sales REAL NOT NULL CHECK(sales > 0),
    transaction_date DATE NOT NULL,
    payment_method TEXT NOT NULL,
    rating REAL CHECK(rating >= 1.0 AND rating <= 5.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Anomaly Audit Records
CREATE TABLE anomaly_records (
    anomaly_id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id TEXT,
    anomaly_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    description TEXT NOT NULL,
    expected_value TEXT,
    actual_value TEXT,
    recommended_action TEXT,
    is_resolved INTEGER DEFAULT 0 CHECK(is_resolved IN (0, 1)),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Report Generation History
CREATE TABLE report_history (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    dataset_scope TEXT NOT NULL,
    filter_summary TEXT,
    record_count INTEGER NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📦 Inventory Intelligence Engine

Retail operations require predictive stock replenishment to prevent out-of-stock losses while minimizing holding costs. The inventory engine executes the following core algorithms:

### 1. Daily Sales Velocity ($V$)
$$\text{Velocity} = \frac{\sum \text{Quantity Sold}}{\text{Active Calendar Days Analyzed}}$$

- **Fast Moving**: Velocity $\ge 1.5$ units/day
- **Normal Moving**: $0.5 \le \text{Velocity} < 1.5$ units/day
- **Slow Moving**: $0.0 < \text{Velocity} < 0.5$ units/day
- **Non-Moving**: Velocity $= 0.0$ units/day

### 2. Days of Stock Remaining ($D$)
$$D = \frac{\text{Current Stock Level}}{\text{Daily Sales Velocity}}$$

### 3. Stock Health Badges
- 🔴 **Out of Stock**: $\text{Current Stock} = 0$
- 🟡 **Low Stock**: $0 < \text{Current Stock} \le \text{Safety Stock Level}$
- 🟢 **Healthy**: $\text{Safety Stock Level} < \text{Current Stock} \le (\text{Safety Stock} \times 3)$
- 🔵 **Overstocked**: $\text{Current Stock} > (\text{Safety Stock} \times 3)$

### 4. Automated Reorder Policy
$$\text{Target Stock} = \max(\text{Safety Stock} \times 2.5, 50)$$
$$\text{Reorder Quantity} = \max(0, \text{Target Stock} - \text{Current Stock})$$
$$\text{Estimated Reorder Cost} = \text{Reorder Quantity} \times \text{Unit Cost}$$

---

## 🚨 Dual-Layer Anomaly Detection Engine

The anomaly detection engine safeguards data quality through two distinct complementary layers:

### Layer 1: Deterministic Business Rule Violations
1. **Arithmetic Calculation Discrepancies**:
   $$|\text{Sales} - (\text{Quantity} \times \text{Unit Price})| > \$0.05$$
   Flags point-of-sale software bugs or rounding corruptions (`CRITICAL` severity).
2. **Negative / Zero Values**: Detects quantities $\le 0$ or unit prices $\le 0$ violating physical retail constraints (`CRITICAL` severity).
3. **Rating Range Violations**: Flags satisfaction scores outside standard $1.0 \le \text{Rating} \le 5.0$ bounds (`MEDIUM` severity).
4. **Duplicate Invoice IDs**: Detects conflicting or duplicated transaction numbers (`CRITICAL` severity).

### Layer 2: Statistical Anomaly Detection
1. **Tukey's Interquartile Range (IQR) Outlier Rule**:
   $$IQR = Q_3 - Q_1$$
   $$\text{Upper Threshold} = Q_3 + 1.5 \times IQR$$
   - Guarded by $N \ge 15$ minimum sample size to prevent false positives on small subsets.
   - Includes standard deviation fallback ($\mu + 3\sigma$) when low variance results in $IQR = 0$.
2. **Temporal Volume Surge Analysis**:
   - Computes daily aggregated transaction counts across $15+$ days.
   - Flags days exceeding $\mu_{\text{daily}} + 2.5\sigma_{\text{daily}}$ as unexplained demand surges.

---

## 💡 4-Tier Business Insights Framework

Rather than generating generic AI commentary, the system generates empirical, verifiable insights formatted into four rigorous tiers:

| Tier | Component | Definition | Example from Supermarket System |
| :---: | :--- | :--- | :--- |
| **Tier 1** | **👁️ Observation** | Objective, verifiable mathematical statement directly extracted from filtered data. | *"Branch C accounts for \$72,469.45 (29.7% of total sales), outperforming Branch A by \$20,112.37 (38.4% higher)."* |
| **Tier 2** | **📊 Analytical Insight** | Business implication and context derived from the observation. | *"Regional revenue generation is heavily concentrated in Branch C, indicating strong market penetration but high revenue reliance on a single outlet."* |
| **Tier 3** | **❓ Possible Explanation** | Plausible operational, demographic, or foot-traffic hypotheses. | *"Branch C may enjoy higher foot traffic, an optimal downtown retail location, or superior category merchandising."* |
| **Tier 4** | **🎯 Recommended Action** | Specific, measurable, and actionable directive for retail store managers. | *"Audit Branch C's promotional strategy and inventory mix to identify transferable best practices for Branch A and B."* |

---

## 📄 Executive Reporting Engine

### 1. Executive PDF Briefing (ReportLab)
- **Flowable Architecture**: Uses ReportLab `SimpleDocTemplate`, `Paragraph`, `Table`, and `HRFlowable` to eliminate layout clipping.
- **Dynamic Two-Pass `NumberedCanvas`**: Computes total page count dynamically to stamp clean headers and `"Page X of Y"` footers on every page.
- **Executive Styling**: Incorporates deep navy headers (`#1E3A8A`), high-contrast metric cards, structured 4-tier insight blocks, and stock replenishment tables.

### 2. Formatted Multi-Sheet Excel Report (`openpyxl`)
Generates a structured 7-sheet workbook:
1. `Executive Summary`: High-level KPIs, date range, active filters, and dataset metadata.
2. `Sales Transactions`: Complete filtered sales transactions with frozen header rows and currency formatting.
3. `Product Performance`: Aggregated by SKU with units sold, total revenue, average price, and rating.
4. `Category Performance`: Merchandise group breakdown with revenue share percentage and volume.
5. `Inventory Intelligence`: Current stock levels, daily sales velocity, days remaining, health badges, and reorder cost.
6. `Anomaly Audit Log`: Complete list of flagged issues with rule IDs, affected fields, and suggested actions.
7. `Business Insights Matrix`: Full structured 4-tier insight matrix.

---

## 🧪 Automated Test Suite

The project includes **46 comprehensive automated unit tests** covering all modules:

```powershell
py -3.12 -m unittest discover -s tests -p "test_*.py" -v
```

### Test Suite Breakdown:
- `tests/test_database.py` (8 tests): Schema DDL, foreign key enforcement, baseline seeding, idempotent imports (`skip_duplicates` / `replace_all`), product CRUD, stock movement ledger, anomaly and report logging.
- `tests/test_inventory.py` (5 tests): Sales velocity, days remaining, safety stock health badges, reorder calculations, ledger overdraft protection.
- `tests/test_anomaly.py` (9 tests): Math mismatch detection, negative value traps, rating bounds, duplicate invoices, Tukey's IQR rule, temporal spikes, small dataset safety.
- `tests/test_insights.py` (5 tests): 4-tier structure integrity, branch disparity insights, category volume dynamics, inventory urgency integration, empty DataFrame safety.
- `tests/test_reports.py` (5 tests): PDF generation, binary `%PDF` verification, 7-sheet Excel workbook structure, column width auto-adjustment, CSV export.
- `tests/test_upload_and_analysis.py` (14 tests): CSV/Excel ingestion, alias auto-mapping, KPI calculations, Plotly dark-theme styling, empty dataset handling.

---

## 🚀 Installation & Local Execution

### 1. Prerequisites
- Python 3.12 or higher (64-bit AMD64)
- Git installed

### 2. Clone the Repository
```powershell
git clone https://github.com/YASHKAUSHIK04/supermarket-sales-analytics.git
cd supermarket-sales-analytics
```

### 3. Install Dependencies
```powershell
py -3.12 -m pip install -r requirements.txt
```

### 4. Run the Automated Test Suite
```powershell
py -3.12 -m unittest discover -s tests -p "test_*.py" -v
```

### 5. Launch the Streamlit Dashboard
```powershell
py -3.12 -m streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🎓 BCA / Final Year Capstone Viva Preparation Guide

When presenting this project during a college viva examination or technical interview, use the following structured answers:

### Q1: Why did you choose SQLite over in-memory Pandas or flat CSV files?
> **Answer**: *"Flat CSV files lack ACID transaction guarantees, referential integrity, and concurrency controls. By implementing SQLite with `PRAGMA foreign_keys = ON;`, we ensure that sales transactions cannot reference non-existent products, inventory deductions cannot result in negative stock, and all inventory receipts are recorded in an immutable, append-only ledger (`inventory_movements`). Furthermore, SQLite is built into Python's standard library, making the project 100% portable with zero external database server setup required."*

### Q2: How does your inventory system prevent negative stock overdrafts?
> **Answer**: *"Our inventory deduction engine in `src/inventory.py` and `src/database.py` executes a two-phase check. In Phase 1, it queries current stock for each product and verifies whether $\text{Current Stock} \ge \text{Deduction Qty}$. If any product suffers a shortfall, the entire transaction is safely aborted without partial deductions. In Phase 2, the ledger balance is updated atomically using a database transaction with `CHECK(resulting_stock >= 0)` constraint enforcement."*

### Q3: How does the anomaly detection engine work without paid machine learning APIs?
> **Answer**: *"We implemented a dual-layer architecture. Layer 1 uses deterministic rules: mathematical consistency verification ($|\text{Sales} - (\text{Quantity} \times \text{Unit Price})| \le \$0.05$), positive number constraints, and bounds checking. Layer 2 uses statistical distribution modeling: Tukey's Interquartile Range ($Q_3 + 1.5 \times IQR$) to identify price and volume outliers, combined with a daily aggregate rolling standard deviation test ($> 2.5\sigma$) to catch abnormal single-day sales spikes. This is deterministic, explainable, lightweight, and requires no external API tokens."*

### Q4: What is the 4-tier business insight framework?
> **Answer**: *"Many dashboards present isolated charts that leave managers wondering 'what should I do?'. Our 4-tier framework systematically bridges the gap between raw data and executive decision-making:
> 1. **Observation**: What the data literally shows ($X > Y$).
> 2. **Analytical Insight**: Why this matters to store operations.
> 3. **Possible Explanation**: Plausible retail hypotheses (foot traffic, stock placement).
> 4. **Recommended Action**: Concrete operational directives for the store manager."*

### Q5: How did you implement automated PDF and Excel report generation?
> **Answer**: *"We utilized ReportLab's Platypus flowable architecture. Instead of hardcoding absolute coordinates that clip text on different screen resolutions, we used `SimpleDocTemplate` with flowable `Paragraph`s and `Table`s that wrap automatically. To display dynamic 'Page X of Y' page numbers, we implemented a custom two-pass `NumberedCanvas`. For Excel, we used `openpyxl` to build a 7-sheet workbook featuring custom navy headers, auto-adjusted column dimensions, and formatted currency numbers."*

---

## 👤 Author & Attribution

- **Project Lead**: [Yash Kaushik](https://github.com/YASHKAUSHIK04)
- **Degree**: Bachelor of Computer Applications (BCA) Capstone Project
- **GitHub Repository**: [YASHKAUSHIK04/supermarket-sales-analytics](https://github.com/YASHKAUSHIK04/supermarket-sales-analytics)
- **License**: MIT Open Source License
