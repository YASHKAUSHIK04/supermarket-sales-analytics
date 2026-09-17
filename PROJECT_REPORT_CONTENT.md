# SUPERMARKET SALES & CUSTOMER ANALYTICS DASHBOARD
## Formal Internship Project Report

**Project Title:** Supermarket Sales & Customer Analytics Dashboard  
**Academic / Professional Level:** Data Analyst Internship Project  
**Author:** Data Analyst Intern  
**Dataset Reference:** Supermarket Sales Dataset (500 Transactions)  
**Tools & Technologies:** Python, Pandas, NumPy, Plotly, Streamlit, Jupyter  

---

# TABLE OF CONTENTS
1. Title Page
2. Certificate of Internship Completion
3. Student / Intern Declaration
4. Acknowledgements
5. Abstract
6. Introduction
7. Problem Statement
8. Project Objectives
9. Dataset Description
10. Data Dictionary
11. Tools & Technologies
12. Methodology & Analytical Framework
13. Data Ingestion, Reconstruction & Cleaning
14. Exploratory Data Analysis (EDA)
15. Dashboard Architecture & Interactive Development
16. Results & Empirical Findings
17. Key Business Insights & Strategic Recommendations
18. Limitations of Study
19. Future Scope
20. Conclusion
21. References

---

## 1. Title Page

```
================================================================================
                    INTERNSHIP PROJECT REPORT
                                ON
       SUPERMARKET SALES & CUSTOMER ANALYTICS DASHBOARD

          Submitted in partial fulfillment of the requirements 
                     for the completion of the
                 DATA ANALYST INTERNSHIP PROGRAM

Submitted By:
[Intern Name Placeholder]
[Intern ID / Roll No Placeholder]
[Department of Computer Science / Data Science]

Under the Supervision & Guidance of:
[Industry Mentor / Guide Name]
[Designation Placeholder]
[Organization / Institutional Placeholder]
[Date: September 2026]
================================================================================
```

---

## 2. Certificate Placeholder

```
                            CERTIFICATE OF COMPLETION

This is to certify that the project entitled "Supermarket Sales & Customer Analytics 
Dashboard" submitted by [Intern Name Placeholder] (ID: [Intern ID Placeholder]) in partial 
fulfillment of the Data Analyst Internship Program is a bona fide record of work carried out 
under my supervision and guidance.

To the best of my knowledge, the matter embodied in this report has not been submitted to any 
other university or institution for the award of any degree or diploma.


________________________                     ________________________
[Mentor / Guide Name]                        [Head of Department / HR]
Designation: Data Analytics Lead             Department: Analytics & BI
Date: [DD/MM/YYYY]                           Date: [DD/MM/YYYY]
```

---

## 3. Declaration Placeholder

```
                              CANDIDATE DECLARATION

I, [Intern Name Placeholder], hereby declare that the project report entitled "Supermarket Sales 
& Customer Analytics Dashboard" is an original work conducted by me under the guidance of 
[Mentor Name Placeholder].

I confirm that:
1. The empirical calculations and visualizations are derived solely from the authentic supermarket 
   dataset provided.
2. No fabricated financial variables (such as unsubstantiated profit, cost, or margin numbers) have 
   been introduced.
3. This work adheres to rigorous academic integrity and data analysis standards.


________________________
[Intern Signature]
Name: [Intern Name Placeholder]
Date: [DD/MM/YYYY]
```

---

## 4. Acknowledgements

I express my deepest gratitude to my mentor, **[Mentor Name Placeholder]**, for continuous guidance, constructive feedback, and technical mentorship throughout the course of this Data Analyst Internship. Their insights on business problem formulation, data cleaning rigor, and executive dashboard design were instrumental in bringing this project to completion.

I also extend my heartfelt appreciation to the analytics team and peer interns for their collaborative reviews and intellectual environment. Finally, I thank my family and friends for their encouragement and support during this endeavor.

---

## 5. Abstract

Retail FMCG (Fast-Moving Consumer Goods) supermarkets operate in dynamic, competitive environments where customer purchasing behaviors, multi-channel payment adoptions, and inventory turnover fluctuate rapidly across geographic branches. This project develops an end-to-end data analytics and business intelligence solution utilizing an empirical supermarket sales dataset containing 500 transaction records across four major Indian metropolitan centers: Jaipur (Branch A), Delhi (Branch B), Mumbai (Branch C), and Bengaluru (Branch D).

A robust data pipeline was engineered in Python to parse multi-line PDF OCR transaction text, reconstruct fragmented records, validate datatypes, and enforce mathematical integrity ($Sales = Quantity \times Unit Price$). An extensive Exploratory Data Analysis (EDA) was executed across five critical analytical dimensions: temporal sales patterns, geographic and branch performance, product category volume-to-revenue ratios, customer loyalty segmentation (Member vs. Normal), and payment method utilization.

To translate analytical insights into executive decision support, an interactive web dashboard was constructed using **Streamlit** and **Plotly**. The application features an executive KPI ribbon, multi-dimensional dynamic filtering with state reset capabilities, graceful empty-data handling, and seven structured analytics modules. The findings provide verified retail operational recommendations without inventing unobserved variables.

---

## 6. Introduction

Modern supermarket analytics has transitioned from backward-looking accounting summaries to forward-looking operational intelligence. As retail chains expand across multiple geographic regions, store directors require granular visibility into transaction mechanics:
- Which product categories generate recurring volume versus high gross revenue?
- How do loyalty club memberships impact basket sizes across demographics?
- What settlement methods dominate checkout counters, and how do they correlate with ticket size?

By combining reproducible data engineering with reactive interactive visualizations, data analysts provide supermarket leadership with the tools necessary to optimize shelf space, refine promotional bundles, and streamline checkout operations.

---

## 7. Problem Statement

A retail chain operating four branches across India (Jaipur, Delhi, Mumbai, Bengaluru) possesses raw transaction logs that are stored in document-based formats with formatting inconsistencies caused by OCR text wrapping. Retail managers currently lack:
1. A clean, verified, centralized data repository with verified mathematical integrity.
2. Visibility into whether loyalty memberships (Member vs. Normal) correlate with larger basket sizes or merely repeat transactions.
3. Clear differentiation between high-volume staple items (e.g., Vegetables, Snacks) and high-value revenue drivers (e.g., Beverages, Personal Care, Dairy).
4. An interactive executive interface allowing localized store managers to filter performance by date, city, product category, customer segment, and payment method without requiring technical SQL queries.

---

## 8. Project Objectives

1. **Data Ingestion & Cleaning**: Ingest raw OCR transaction records, resolve multi-line token wrapping, enforce strict data validation, verify mathematical consistency ($Sales = Quantity \times Unit Price$), and export clean, audit-compliant datasets.
2. **Feature Engineering**: Derive temporal and unit-level attributes (Year, Month, Month Name, Day, Day of Week, Transaction Value, Unit verification).
3. **Exploratory Data Analysis**: Comprehensively analyze the dataset across Sales, Customers, Products, Payment Methods, and Customer Ratings.
4. **Interactive Dashboard Development**: Construct a responsive, modern web dashboard in Streamlit and Plotly featuring 7 KPI cards, comprehensive multi-select filters, filter reset capability, and 7 analytical tabs.
5. **Business Insights Formulation**: Derive verified, data-backed operational recommendations without fabricating unobserved business metrics or claiming unproven causal links.

---

## 9. Dataset Description

The dataset comprises **500 transaction records** recorded between **January 1, 2026, and July 1, 2026**.

Key Characteristics:
- **Total Records:** 500 unique invoices (`INV0001` through `INV0500`)
- **Total Fields:** 13 primary attributes + 7 feature-engineered attributes
- **Cities Covered:** Jaipur, Delhi, Mumbai, Bengaluru
- **Branches Covered:** A, B, C, D
- **Categories Covered:** 8 distinct merchandise departments (Bakery, Beverages, Dairy, Fruits, Grocery, Personal Care, Snacks, Vegetables)
- **Products Covered:** 20 distinct retail SKUs
- **Customer Classifications:** Member, Normal
- **Gender Categories:** Male, Female
- **Payment Modes:** UPI, Net Banking, Card, Cash
- **Customer Rating Scale:** Continuous numeric scale from 3.0 to 5.0 (Mean: 3.99)

---

## 10. Data Dictionary

| Field | Source Type | Model Type | Description | Constraints / Validation |
| :--- | :--- | :--- | :--- | :--- |
| **Invoice ID** | Raw String | `object` | Alphanumeric transaction ID | Unique, matches `INV\d{4}` |
| **Date** | Raw String | `datetime64[ns]` | Date of purchase | Between 2026-01-01 & 2026-07-01 |
| **Branch** | Raw String | `category` | Supermarket branch code | One of: `A`, `B`, `C`, `D` |
| **City** | Raw String | `category` | Operating metropolitan city | Jaipur, Mumbai, Delhi, Bengaluru |
| **Customer Type**| Raw String | `category` | Shopper loyalty classification | `Member`, `Normal` |
| **Gender** | Raw String | `category` | Customer gender | `Male`, `Female` |
| **Product** | Raw String | `category` | Specific item SKU purchased | 20 unique product names |
| **Category** | Raw String | `category` | Merchandise department | 8 unique department names |
| **Quantity** | Raw String | `int64` | Number of units purchased | Integer in range [1, 10] |
| **Unit Price** | Raw String | `float64` | Selling price per unit (Rs.) | Positive float, rounded to 2 decimals |
| **Payment** | Raw String | `category` | Payment settlement method | `UPI`, `Net Banking`, `Card`, `Cash` |
| **Rating** | Raw String | `float64` | Customer rating score | Float in range [3.0, 5.0] |
| **Sales** | Raw String | `float64` | Total transaction value (Rs.) | Must equal $Quantity \times Unit Price$ |
| **Year** | Derived | `int32` | Calendar year | 2026 |
| **Month** | Derived | `int32` | Calendar month number | Range [1, 7] |
| **Month_Name** | Derived | `object` | Full month name | January through July |
| **Day** | Derived | `int32` | Day of the month | Range [1, 31] |
| **Day_Of_Week** | Derived | `object` | Name of weekday | Monday through Sunday |
| **Transaction_Value** | Derived | `float64` | Total transaction revenue | Equal to Sales |
| **Sales_Per_Quantity**| Derived | `float64` | Computed unit revenue | Equal to Unit Price |

---

## 11. Tools & Technologies

| Tool / Technology | Version | Purpose in Project |
| :--- | :--- | :--- |
| **Python** | 3.12.10 (x64) | Core programming language environment |
| **Pandas** | 3.0.5 | Data wrangling, regex extraction, aggregations, cross-tabulations |
| **NumPy** | 2.5.3 | Vectorized numerical operations and statistical validations |
| **Plotly Express / Graph Objects** | 5.24.1 | Production-grade responsive, interactive charts with custom hover templates |
| **Streamlit** | 1.42.0 | Full-stack interactive analytics web application framework |
| **Jupyter Notebook (`nbformat`)** | 5.11.1 | Exploratory data analysis documentation and step-by-step code verification |
| **Regular Expressions (`re`)** | Built-in | Multi-line OCR string reconstruction and pattern parsing |

---

## 12. Methodology & Analytical Framework

The project adopted a structured five-phase Data Analytics Lifecycle:

```
+-----------------------------------------------------------------------+
| 1. INGESTION & DATA ENGINEERING                                       |
|    - Raw OCR token extraction -> Multi-line regex reconstruction      |
|    - Mathematical assertions (Sales == Quantity x Unit Price)         |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| 2. AUDIT & CLEANING QUALITY ASSURANCE                                 |
|    - 0 null values, 0 duplicate IDs, valid numeric boundaries         |
|    - Export to data/raw/ and data/processed/                          |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| 3. EXPLORATORY DATA ANALYSIS (EDA)                                    |
|    - 5-number summaries, temporal trends, cross-tabulations           |
|    - Segmentations: Customer Type, Gender, Category, Product, City    |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| 4. INTERACTIVE DASHBOARD DEVELOPMENT                                  |
|    - Streamlit web architecture + Plotly visualization engine         |
|    - 7 KPI cards, 8-filter dynamic sidebar, 7 analytical tabs         |
+-----------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
| 5. BUSINESS INSIGHTS & REPORTING                                      |
|    - Verifiable findings strictly derived from empirical data         |
|    - Formulation of practical retail recommendations                  |
+-----------------------------------------------------------------------+
```

---

## 13. Data Ingestion, Reconstruction & Cleaning

### Technical Challenge
The raw PDF dataset contained multi-line wrapped text records where product names (e.g. `Face Wash`, `Cooking Oil`), category names (`Personal Care`), and payment methods (`Net Banking`) wrapped onto subsequent lines. A naive line-by-line CSV parser would fail or produce corrupt rows.

### Ingestion Solution
An automated pipeline was built in `src/data_cleaning.py`:
1. The text stream was segmented using positive lookahead regex matching the primary key pattern `INV\d{4}`.
2. Multi-line whitespace was collapsed into single normalized record strings.
3. A compiled regex pattern with sorted categorical tokens matched all 13 columns simultaneously.
4. Each record was asserted against strict mathematical constraints:
   $$|\text{Sales} - (\text{Quantity} \times \text{Unit Price})| \le 0.05$$

### Cleaning Results
- Raw records ingested: **500**
- Successfully parsed records: **500 (100.0%)**
- Missing fields: **0 (0.0%)**
- Duplicate records: **0 (0.0%)**
- Calculation errors: **0 (0.0%)**

---

## 14. Exploratory Data Analysis (EDA)

The complete exploratory analysis was executed in `notebooks/supermarket_eda.ipynb`. Key statistical findings include:

### Descriptive Statistics

| Statistic | Quantity (Units) | Unit Price (Rs.) | Rating (1–5) | Sales (Rs.) |
| :--- | :---: | :---: | :---: | :---: |
| **Mean** | 5.54 | 93.30 | 3.99 | 488.82 |
| **Std Dev** | 2.87 | 59.88 | 0.58 | 448.33 |
| **Min** | 1.00 | 27.67 | 3.00 | 28.61 |
| **25% (Q1)** | 3.00 | 42.94 | 3.50 | 170.80 |
| **50% (Median)** | 6.00 | 67.33 | 4.00 | 344.66 |
| **75% (Q3)** | 8.00 | 145.32 | 4.50 | 651.78 |
| **Max** | 10.00 | 236.71 | 5.00 | 2,114.82 |

### Key Observations from EDA:
1. **Sales Distribution**: Sales exhibit a positive right skew (Mean = Rs. 488.82 vs Median = Rs. 344.66) due to premium transactions involving high-unit-price items (Cheese, Coffee, Shampoo, Cooking Oil).
2. **Quantity Spread**: Unit purchases per invoice range uniformly from 1 to 10 units with a mean of 5.54 units.
3. **Rating Concentration**: Customer ratings have a narrow standard deviation of 0.58 centered tightly around 3.99, indicating consistent service delivery across all four branches.

---

## 15. Dashboard Development

The interactive dashboard was built using Streamlit in `app.py`:

### UI & UX Design Architecture
- **Color Theme**: Professional corporate navy (`#1f4e79`), vibrant teal (`#008080`), and warm amber (`#e67e22`).
- **Responsive KPI Cards**: Styled with CSS box-shadows, subtle border radii, and clear typography.
- **Sidebar Interactive Controls**:
  - Date Range Picker (Jan 1, 2026 to Jul 1, 2026)
  - City (Multi-select)
  - Branch (Multi-select)
  - Category (Multi-select)
  - Product (Multi-select, dynamically updating based on selected category)
  - Customer Type (Member vs Normal)
  - Gender (Male vs Female)
  - Payment Method (UPI, Net Banking, Card, Cash)
  - One-click **Reset All Filters** button
- **Defensive Engineering**: Empty-state guard prevents application exceptions when active filters match zero records.
- **Tabbed Structure**: Seven dedicated functional tabs for focused analysis without overwhelming visual clutter.

---

## 16. Results & Empirical Findings

### 1. Overall Supermarket Performance
- **Gross Revenue:** Rs. 2,44,411.08
- **Total Units Sold:** 2,768 units
- **Total Transactions:** 500 invoices
- **Average Order Value (ATV):** Rs. 488.82
- **Average Customer Rating:** 3.99 / 5.0

### 2. Geographic & Branch Breakdown
- **Mumbai (Branch C):** Rs. 72,469.45 (29.65% share, 143 transactions, ATV: Rs. 506.78)
- **Delhi (Branch B):** Rs. 64,116.26 (26.23% share, 133 transactions, ATV: Rs. 482.08)
- **Bengaluru (Branch D):** Rs. 55,468.29 (22.70% share, 119 transactions, ATV: Rs. 466.12)
- **Jaipur (Branch A):** Rs. 52,357.08 (21.42% share, 105 transactions, ATV: Rs. 498.64)
*Insight: Mumbai and Delhi represent the strongest revenue centers, while all 4 branches maintain healthy transaction volume.*

### 3. Customer Loyalty Segment Findings
- **Members:** 296 transactions (59.2%), Total Sales Rs. 1,43,009.30 (58.5%), ATV = Rs. 483.14.
- **Normal Shoppers:** 204 transactions (40.8%), Total Sales Rs. 1,01,401.78 (41.5%), ATV = Rs. 497.07.
*Insight: Loyalty membership correlates with higher transaction frequency (59.2% vs 40.8%) rather than larger basket size per checkout.*

### 4. Product Dynamics: High-Revenue vs. High-Volume
- **Top Revenue Products:**
  1. Cheese: Rs. 27,906.30 (Dairy)
  2. Coffee: Rs. 27,694.87 (Beverages)
  3. Shampoo: Rs. 27,497.48 (Personal Care)
  4. Cooking Oil: Rs. 21,525.06 (Grocery)
  5. Tea: Rs. 17,681.59 (Beverages)
- **Top Volume Products:**
  1. Potato: 194 units sold (Vegetables)
  2. Chips: 168 units sold (Snacks)
  3. Rice: 167 units sold (Grocery)
  4. Cold Drink: 166 units sold (Beverages)
  5. Bread: 164 units sold (Bakery)
- **Top Rated Products:**
  1. Bread: 4.24 / 5.0 (28 reviews)
  2. Chocolate: 4.23 / 5.0 (23 reviews)
  3. Milk: 4.10 / 5.0 (22 reviews)
  4. Chips: 4.08 / 5.0 (26 reviews)
  5. Eggs: 4.03 / 5.0 (20 reviews)

### 5. Category Revenue Breakdown
- **Beverages:** Rs. 56,108.24 (82 transactions, ATV: Rs. 684.25)
- **Personal Care:** Rs. 45,943.96 (73 transactions, ATV: Rs. 629.37)
- **Dairy:** Rs. 43,992.00 (68 transactions, ATV: Rs. 646.94)
- **Grocery:** Rs. 40,470.47 (82 transactions, ATV: Rs. 493.54)
- **Fruits:** Rs. 23,263.17 (44 transactions, ATV: Rs. 528.71)
- **Snacks:** Rs. 16,992.97 (75 transactions, ATV: Rs. 226.57)
- **Vegetables:** Rs. 11,124.17 (48 transactions, ATV: Rs. 231.75)
- **Bakery:** Rs. 6,516.10 (28 transactions, ATV: Rs. 232.72)

### 6. Payment Settlement Channels
- **UPI:** Rs. 67,910.33 (127 transactions, ATV: Rs. 534.73)
- **Net Banking:** Rs. 65,194.93 (126 transactions, ATV: Rs. 517.42)
- **Card:** Rs. 57,265.64 (125 transactions, ATV: Rs. 458.13)
- **Cash:** Rs. 54,040.18 (122 transactions, ATV: Rs. 442.95)

---

## 17. Key Business Insights & Strategic Recommendations

### Empirical Insights
1. **Revenue Decoupling from Volume**: Beverages, Personal Care, and Dairy generate 59.8% of total gross sales despite accounting for only 44.6% of transaction checkouts. Staple categories (Vegetables, Bakery, Snacks) serve as foot-traffic drivers.
2. **Loyalty Program Structure**: Members do not spend more per order than non-members (Member ATV = Rs. 483.14 vs Normal ATV = Rs. 497.07). The loyalty program drives visit retention rather than checkout ticket size.
3. **Digital Settlement Dominance**: UPI and Net Banking combined account for over **54.5%** of gross sales and higher order sizes compared to Cash settlements.

### Strategic Actionable Recommendations
1. **Curated Cross-Merchandising**:
   - Place high-value SKUs (Cheese, Coffee, Shampoo) in direct visual proximity to staple volume drivers (Bread, Biscuits, Chips) to trigger impulse basket additions.
2. **Revamp Loyalty Tier Incentives**:
   - Introduce tiered minimum-spend thresholds (e.g., "Spend Rs. 600 as a Member to unlock 5% instant discount") to deliberately lift Member ATV from Rs. 483 toward Rs. 600+.
3. **Regional Inventory Optimization**:
   - Prioritize inventory allocations of Beverages and Personal Care in Mumbai and Delhi branches where transaction volumes and ticket sizes are highest.

---

## 18. Limitations of Study

1. **Absence of Cost and Margin Variables**: The raw dataset contains only Unit Price and Sales. Cost of Goods Sold (COGS), operating expenses, and net profit margins are not recorded. Any calculation of profitability would be speculative and was deliberately avoided.
2. **Lack of Intraday Timestamps**: Transactions provide purchase dates but omit time-of-day records (hours/minutes), precluding morning vs. evening rush-hour staffing analysis.
3. **Limited Observation Window**: The 500 records span 7 months, providing high cross-sectional reliability across 4 branches, but insufficient depth for multi-year seasonal forecasting.

---

## 19. Future Scope

1. **Predictive Time-Series Forecasting**: Deploy automated machine learning (ARIMA/Prophet) to forecast monthly demand by category.
2. **Market Basket Association Mining**: With transaction data expanded to multi-item checkouts, implement the Apriori algorithm to identify itemset affinities.
3. **Customer Lifetime Value (CLV) Modeling**: Track customer purchase frequencies longitudinally to identify high-value customer churn risk.

---

## 20. Conclusion

The **Supermarket Sales & Customer Analytics Dashboard** project successfully demonstrates practical, portfolio-grade Data Analyst competencies. Through rigorous data parsing, 100% mathematical integrity validation, modular Python engineering, and an intuitive Streamlit dashboard, raw supermarket records were transformed into actionable business intelligence. The resulting solution equips retail managers with the empirical tools necessary to make data-driven decisions on inventory, loyalty incentives, and operational execution.

---

## 21. References

1. McKinney, W. (2022). *Python for Data Analysis: Data Wrangling with pandas, NumPy, and Jupyter* (3rd ed.). O'Reilly Media.
2. Streamlit Inc. (2024). *Streamlit Documentation: Building Interactive Web Applications with Python*. https://docs.streamlit.io
3. Plotly Technologies Inc. (2024). *Plotly Python Open Source Graphing Library*. https://plotly.com/python/
4. Few, S. (2013). *Information Dashboard Design: Displaying Data for At-a-Glance Monitoring* (2nd ed.). Analytics Press.
5. Anderson, C. (2015). *Creating a Data-Driven Organization: Practical Advice from the Trenches*. O'Reilly Media.
