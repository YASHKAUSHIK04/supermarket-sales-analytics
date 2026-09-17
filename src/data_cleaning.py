"""
Supermarket Sales & Customer Analytics - Data Cleaning & Validation Pipeline
Module: src/data_cleaning.py

Handles:
- Ingestion of raw PDF OCR text dump
- Line reconstruction and regex tokenization
- Raw structured CSV generation (data/raw/supermarket_sales_raw.csv)
- Data type casting, validation, and math integrity checks
- Feature engineering (Date parts, Transaction Value, Unit verification)
- Cleaned dataset export (data/processed/supermarket_sales_cleaned.csv)
- Audit log & data quality report generation
"""

import re
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Resolve project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_TXT_PATH = PROJECT_ROOT / "data" / "raw" / "supermarket_sales_raw.txt"
RAW_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "supermarket_sales_raw.csv"
CLEANED_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "supermarket_sales_cleaned.csv"

CATEGORIES = [
    "Personal Care", "Dairy", "Grocery", "Fruits", "Vegetables", "Snacks", "Beverages", "Bakery"
]
CATEGORIES_SORTED = sorted(CATEGORIES, key=len, reverse=True)

PRODUCTS = [
    "Cooking Oil", "Cold Drink", "Face Wash", "Milk", "Rice", "Shampoo", "Apples", "Soap",
    "Potato", "Biscuits", "Chips", "Coffee", "Tomato", "Bread", "Tea", "Cheese",
    "Noodles", "Bananas", "Chocolate", "Eggs"
]
PRODUCTS_SORTED = sorted(PRODUCTS, key=len, reverse=True)

PAYMENTS = ["Net Banking", "UPI", "Card", "Cash"]
PAYMENTS_SORTED = sorted(PAYMENTS, key=len, reverse=True)


def parse_raw_text(raw_text_path: Path) -> pd.DataFrame:
    """Parse raw OCR text file into a structured DataFrame."""
    if not raw_text_path.exists():
        raise FileNotFoundError(f"Raw text file not found at: {raw_text_path}")

    with open(raw_text_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Split records by INV\d{4}
    records_raw = re.split(r"(?=(?:^|\n)INV\d{4}\b)", text)
    records_raw = [r.strip() for r in records_raw if r.strip() and not r.strip().startswith("Invoice ID")]

    cat_pattern = "|".join(re.escape(c) for c in CATEGORIES_SORTED)
    prod_pattern = "|".join(re.escape(p) for p in PRODUCTS_SORTED)
    pay_pattern = "|".join(re.escape(p) for p in PAYMENTS_SORTED)
    pattern = (
        rf"^(INV\d{{4}})\s+(\d{{4}}-\d{{2}}-\d{{2}})\s+([A-D])\s+"
        rf"(Jaipur|Mumbai|Delhi|Bengaluru)\s+(Member|Normal)\s+(Male|Female)\s+"
        rf"({prod_pattern})\s+({cat_pattern})\s+(\d+)\s+([\d\.]+)\s+"
        rf"({pay_pattern})\s+([\d\.]+)\s+([\d\.]+)$"
    )

    rows = []
    failed_records = []

    for r in records_raw:
        s = " ".join(r.split())
        m = re.match(pattern, s)
        if m:
            g = m.groups()
            rows.append({
                "Invoice ID": g[0],
                "Date": g[1],
                "Branch": g[2],
                "City": g[3],
                "Customer Type": g[4],
                "Gender": g[5],
                "Product": g[6],
                "Category": g[7],
                "Quantity": int(g[8]),
                "Unit Price": float(g[9]),
                "Payment": g[10],
                "Rating": float(g[11]),
                "Sales": float(g[12])
            })
        else:
            failed_records.append(s)

    if failed_records:
        raise ValueError(f"Failed to parse {len(failed_records)} records: {failed_records[:3]}")

    df_raw = pd.DataFrame(rows)
    return df_raw


def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate data integrity, handle types, and perform feature engineering."""
    df_clean = df.copy()

    # 1. Type casting
    df_clean["Invoice ID"] = df_clean["Invoice ID"].astype(str)
    df_clean["Date"] = pd.to_datetime(df_clean["Date"])
    df_clean["Branch"] = df_clean["Branch"].astype("category")
    df_clean["City"] = df_clean["City"].astype("category")
    df_clean["Customer Type"] = df_clean["Customer Type"].astype("category")
    df_clean["Gender"] = df_clean["Gender"].astype("category")
    df_clean["Product"] = df_clean["Product"].astype("category")
    df_clean["Category"] = df_clean["Category"].astype("category")
    df_clean["Quantity"] = df_clean["Quantity"].astype(int)
    df_clean["Unit Price"] = df_clean["Unit Price"].astype(float).round(2)
    df_clean["Payment"] = df_clean["Payment"].astype("category")
    df_clean["Rating"] = df_clean["Rating"].astype(float).round(1)
    df_clean["Sales"] = df_clean["Sales"].astype(float).round(2)

    # 2. Validation Checks
    # a. Check nulls
    null_counts = df_clean.isnull().sum()
    if null_counts.any():
        raise AssertionError(f"Unexpected missing values found:\n{null_counts[null_counts > 0]}")

    # b. Check duplicates
    dup_ids = df_clean["Invoice ID"].duplicated().sum()
    if dup_ids > 0:
        raise AssertionError(f"Found {dup_ids} duplicate Invoice IDs.")

    # c. Mathematical integrity: Sales == Quantity * Unit Price
    calc_sales = (df_clean["Quantity"] * df_clean["Unit Price"]).round(2)
    discrepancy = (df_clean["Sales"] - calc_sales).abs()
    max_disc = discrepancy.max()
    if max_disc > 0.05:
        mismatches = df_clean[discrepancy > 0.05]
        raise AssertionError(f"Found {len(mismatches)} mathematical discrepancies:\n{mismatches}")

    # d. Rating range
    if not df_clean["Rating"].between(1.0, 5.0).all():
        raise AssertionError("Ratings detected outside the valid 1.0 to 5.0 range.")

    # e. Quantity range
    if not (df_clean["Quantity"] > 0).all():
        raise AssertionError("Non-positive quantity detected.")

    # 3. Feature Engineering
    df_clean["Year"] = df_clean["Date"].dt.year
    df_clean["Month"] = df_clean["Date"].dt.month
    df_clean["Month_Name"] = df_clean["Date"].dt.strftime("%B")
    df_clean["Day"] = df_clean["Date"].dt.day
    df_clean["Day_Of_Week"] = df_clean["Date"].dt.day_name()
    df_clean["Transaction_Value"] = df_clean["Sales"]
    df_clean["Sales_Per_Quantity"] = (df_clean["Sales"] / df_clean["Quantity"]).round(2)

    return df_clean


def run_pipeline():
    """Execute complete ingestion, validation, and feature engineering pipeline."""
    print("=" * 60)
    print("SUPERMARKET SALES & CUSTOMER ANALYTICS: DATA PIPELINE")
    print("=" * 60)

    print(f"Reading raw OCR text from: {RAW_TXT_PATH}")
    df_raw = parse_raw_text(RAW_TXT_PATH)
    print(f"-> Successfully extracted {len(df_raw)} records with {df_raw.shape[1]} columns.")

    # Save raw CSV
    RAW_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_raw.to_csv(RAW_CSV_PATH, index=False)
    print(f"-> Raw structured dataset saved to: {RAW_CSV_PATH}")

    # Clean & validate
    print("Validating data integrity and performing feature engineering...")
    df_cleaned = validate_and_clean_data(df_raw)
    print(f"-> Validation passed: 0 missing values, 0 duplicate IDs, 100% math validation.")

    # Save processed CSV
    CLEANED_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_cleaned.to_csv(CLEANED_CSV_PATH, index=False)
    print(f"-> Cleaned dataset saved to: {CLEANED_CSV_PATH}")

    # Audit summary
    print("-" * 60)
    print("DATA AUDIT SUMMARY:")
    print(f"  Total Records:           {len(df_cleaned)}")
    print(f"  Date Range:              {df_cleaned['Date'].min().strftime('%Y-%m-%d')} to {df_cleaned['Date'].max().strftime('%Y-%m-%d')}")
    print(f"  Total Sales:             Rs. {df_cleaned['Sales'].sum():,.2f}")
    print(f"  Total Quantity Sold:     {df_cleaned['Quantity'].sum():,} units")
    print(f"  Average Order Value:     Rs. {df_cleaned['Sales'].mean():,.2f}")
    print(f"  Average Rating:          {df_cleaned['Rating'].mean():.2f} / 5.0")
    print(f"  Unique Cities:           {df_cleaned['City'].nunique()} ({', '.join(sorted(df_cleaned['City'].unique()))})")
    print(f"  Unique Branches:         {df_cleaned['Branch'].nunique()} ({', '.join(sorted(df_cleaned['Branch'].unique()))})")
    print(f"  Unique Categories:       {df_cleaned['Category'].nunique()}")
    print(f"  Unique Products:         {df_cleaned['Product'].nunique()}")
    print(f"  Customer Types:          {', '.join(sorted(df_cleaned['Customer Type'].unique()))}")
    print(f"  Payment Methods:         {', '.join(sorted(df_cleaned['Payment'].unique()))}")
    print("=" * 60)
    print("Pipeline completed successfully!")
    return df_cleaned


if __name__ == "__main__":
    run_pipeline()
