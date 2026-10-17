"""
Supermarket Sales & Customer Analytics - Data Ingestion & Upload Engine
Module: src/data_loader.py

Provides:
- Ingestion of user-uploaded datasets in CSV and Excel (.xlsx, .xls) formats
- Smart column alias recognition and auto-mapping
- Schema validation against canonical retail dataset schema
- Mathematical integrity check: Sales = Quantity * Unit Price
- Data type conversion, missing value handling, and robust feature engineering
- Data quality auditing and summary report generation
"""

import io
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import pandas as pd
import numpy as np


# Canonical required and optional fields
CANONICAL_COLUMNS = [
    "Invoice ID",
    "Date",
    "Branch",
    "City",
    "Customer Type",
    "Gender",
    "Product",
    "Category",
    "Quantity",
    "Unit Price",
    "Payment",
    "Rating",
    "Sales",
]

# Essential columns without which core dashboard analysis cannot run
CORE_MANDATORY_COLUMNS = ["Date", "Quantity", "Product", "Category"]

# Default values for optional columns if absent from an uploaded file
DEFAULT_COLUMN_VALUES = {
    "Branch": "Branch A",
    "City": "General",
    "Customer Type": "Normal",
    "Gender": "Not Specified",
    "Payment": "Cash",
    "Rating": 4.0,
}

# Alias dictionary mapping normalized header variations to canonical names
COLUMN_ALIASES: Dict[str, List[str]] = {
    "Invoice ID": [
        "invoice id", "invoice_id", "invoice", "invoice no", "invoiceno",
        "inv_id", "inv id", "order id", "order_id", "orderno", "order no",
        "bill no", "bill_no", "id", "transaction id", "txn_id", "txn id"
    ],
    "Date": [
        "date", "invoice date", "invoice_date", "order date", "order_date",
        "txn date", "txn_date", "transaction date", "transaction_date",
        "sale date", "sale_date", "saledate", "created at", "timestamp"
    ],
    "Branch": [
        "branch", "store", "outlet", "branch id", "store id", "location id",
        "outlet id", "branch code", "store code"
    ],
    "City": [
        "city", "location", "region", "town", "market", "metro", "city name",
        "store location", "geography"
    ],
    "Customer Type": [
        "customer type", "customer_type", "type", "membership", "member type",
        "customer status", "loyalty tier", "customer category", "tier"
    ],
    "Gender": [
        "gender", "sex"
    ],
    "Product": [
        "product", "product name", "product_name", "item", "item name",
        "item_name", "sku", "item description", "description", "goods"
    ],
    "Category": [
        "category", "product category", "product_category", "department",
        "dept", "merchandise group", "category name", "product group"
    ],
    "Quantity": [
        "quantity", "qty", "units", "quantity sold", "volume", "count",
        "items count", "number of items"
    ],
    "Unit Price": [
        "unit price", "unit_price", "price", "rate", "unit cost",
        "price per unit", "mrp", "item price", "selling price"
    ],
    "Payment": [
        "payment", "payment method", "payment_method", "mode", "payment mode",
        "payment_type", "payment type", "tender", "transaction mode"
    ],
    "Rating": [
        "rating", "satisfaction", "score", "feedback", "customer rating",
        "stars", "csat", "review", "review score"
    ],
    "Sales": [
        "sales", "total sales", "total_sales", "total", "amount", "revenue",
        "gross sales", "total amount", "net sales", "line total", "final amount"
    ],
}


def normalize_col_name(col: str) -> str:
    """Normalize a column header for alias matching."""
    s = str(col).strip().lower()
    s = s.replace("_", " ").replace("-", " ")
    return " ".join(s.split())


def detect_and_map_columns(raw_columns: List[str]) -> Dict[str, Optional[str]]:
    """Automatically match raw column names against canonical aliases.

    Returns:
        Dict mapping canonical column names to the detected raw column name,
        or None if no confident match was found.
    """
    normalized_raw = {normalize_col_name(col): col for col in raw_columns}
    mapping: Dict[str, Optional[str]] = {}
    used_raw_cols = set()

    for canonical, aliases in COLUMN_ALIASES.items():
        matched_raw = None
        # 1. Exact canonical name match (case-insensitive)
        can_norm = normalize_col_name(canonical)
        if can_norm in normalized_raw and normalized_raw[can_norm] not in used_raw_cols:
            matched_raw = normalized_raw[can_norm]
        else:
            # 2. Check alias list
            for alias in aliases:
                norm_alias = normalize_col_name(alias)
                if norm_alias in normalized_raw and normalized_raw[norm_alias] not in used_raw_cols:
                    matched_raw = normalized_raw[norm_alias]
                    break

        if matched_raw:
            mapping[canonical] = matched_raw
            used_raw_cols.add(matched_raw)
        else:
            mapping[canonical] = None

    return mapping


def load_uploaded_file(file_input: Union[str, Path, io.BytesIO, Any]) -> pd.DataFrame:
    """Read an uploaded file or file path into a pandas DataFrame.

    Supports:
    - CSV (.csv) with UTF-8 and Latin-1 fallback
    - Excel (.xlsx, .xls) using openpyxl / pandas
    """
    # Determine filename
    filename = ""
    if hasattr(file_input, "name"):
        filename = file_input.name
    elif isinstance(file_input, (str, Path)):
        filename = str(file_input)

    filename_lower = filename.lower()

    if filename_lower.endswith(".xlsx") or filename_lower.endswith(".xls"):
        try:
            # Try openpyxl first
            return pd.read_excel(file_input, engine="openpyxl")
        except Exception:
            # Fallback for standard excel reader
            try:
                return pd.read_excel(file_input)
            except Exception as e:
                raise ValueError(
                    f"Could not read Excel file: {str(e)}. "
                    "Please ensure the file is a valid .xlsx workbook."
                )

    # Default to CSV reading
    try:
        if hasattr(file_input, "seek"):
            file_input.seek(0)
        return pd.read_csv(file_input, encoding="utf-8")
    except UnicodeDecodeError:
        if hasattr(file_input, "seek"):
            file_input.seek(0)
        return pd.read_csv(file_input, encoding="latin1")
    except Exception as e:
        raise ValueError(f"Could not parse file as CSV or Excel: {str(e)}")


def validate_and_process_uploaded_data(
    df_raw: pd.DataFrame,
    column_mapping: Optional[Dict[str, Optional[str]]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Validate, standardize, clean, and feature-engineer an uploaded dataset.

    Args:
        df_raw: Raw DataFrame loaded from file.
        column_mapping: Optional mapping from canonical column names to raw column names.
                       If None, automated detection is performed.

    Returns:
        Tuple of (processed_df, quality_summary_dict).
        If validation fails fatally, processed_df is empty and summary contains errors.
    """
    summary: Dict[str, Any] = {
        "is_valid": False,
        "total_raw_rows": len(df_raw),
        "total_raw_columns": df_raw.shape[1],
        "mapping_used": {},
        "missing_mandatory": [],
        "defaults_applied": [],
        "math_discrepancy_count": 0,
        "max_math_discrepancy": 0.0,
        "null_counts": {},
        "duplicate_invoices": 0,
        "date_range": None,
        "warnings": [],
        "errors": []
    }

    if df_raw.empty:
        summary["errors"].append("Uploaded file is empty (0 rows).")
        return pd.DataFrame(), summary

    # Detect mapping if not provided
    if column_mapping is None:
        column_mapping = detect_and_map_columns(list(df_raw.columns))
    summary["mapping_used"] = column_mapping

    # Check pricing availability: either Unit Price or Sales must be present
    has_unit_price = bool(column_mapping.get("Unit Price"))
    has_sales = bool(column_mapping.get("Sales"))

    if not has_unit_price and not has_sales:
        summary["missing_mandatory"].append("Unit Price or Sales")
        summary["errors"].append(
            "Dataset must contain either 'Unit Price' or 'Sales' to compute financial metrics."
        )

    # Check mandatory columns
    for col in CORE_MANDATORY_COLUMNS:
        if not column_mapping.get(col):
            summary["missing_mandatory"].append(col)
            summary["errors"].append(f"Required column '{col}' could not be mapped.")

    if summary["errors"]:
        return pd.DataFrame(), summary

    # Construct standardized dataframe
    df = pd.DataFrame()

    # Map mapped columns
    for canonical, raw_col in column_mapping.items():
        if raw_col and raw_col in df_raw.columns:
            df[canonical] = df_raw[raw_col].copy()

    # Fill optional columns with defaults if unmapped
    for opt_col, def_val in DEFAULT_COLUMN_VALUES.items():
        if opt_col not in df.columns:
            df[opt_col] = def_val
            summary["defaults_applied"].append(f"'{opt_col}' defaulted to '{def_val}'")

    # Generate Invoice ID if missing
    if "Invoice ID" not in df.columns:
        df["Invoice ID"] = [f"INV{i+1:04d}" for i in range(len(df))]
        summary["defaults_applied"].append("'Invoice ID' auto-generated sequentially")

    # 1. Date processing
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    null_dates = df["Date"].isnull().sum()
    if null_dates > 0:
        summary["warnings"].append(f"Found {null_dates} unparseable date values; rows with invalid dates will be removed.")
        df = df.dropna(subset=["Date"])
        if df.empty:
            summary["errors"].append("All rows contain invalid dates.")
            return pd.DataFrame(), summary

    # 2. Quantity processing
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(1)
    df["Quantity"] = df["Quantity"].clip(lower=1).round().astype(int)

    # 3. Unit Price & Sales Calculation / Validation
    if "Unit Price" in df.columns and "Sales" in df.columns:
        df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce")
        df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

        # Fill missing Unit Price from Sales / Quantity if possible
        unit_price_null = df["Unit Price"].isnull()
        if unit_price_null.any():
            df.loc[unit_price_null, "Unit Price"] = (
                df.loc[unit_price_null, "Sales"] / df.loc[unit_price_null, "Quantity"]
            ).round(2)

        # Fill missing Sales from Quantity * Unit Price if possible
        sales_null = df["Sales"].isnull()
        if sales_null.any():
            df.loc[sales_null, "Sales"] = (
                df.loc[sales_null, "Quantity"] * df.loc[sales_null, "Unit Price"]
            ).round(2)

        # Check mathematical integrity
        expected_sales = (df["Quantity"] * df["Unit Price"]).round(2)
        discrepancy = (df["Sales"] - expected_sales).abs()
        mismatch_mask = discrepancy > 0.05
        disc_count = int(mismatch_mask.sum())
        summary["math_discrepancy_count"] = disc_count
        if disc_count > 0:
            summary["max_math_discrepancy"] = float(discrepancy.max())
            summary["warnings"].append(
                f"Identified {disc_count} rows where Sales != Quantity * Unit Price "
                f"(max discrepancy: ₹{discrepancy.max():.2f}). Recorded for audit review."
            )

    elif "Unit Price" in df.columns and "Sales" not in df.columns:
        df["Unit Price"] = pd.to_numeric(df["Unit Price"], errors="coerce").fillna(0.0).round(2)
        df["Sales"] = (df["Quantity"] * df["Unit Price"]).round(2)
        summary["defaults_applied"].append("'Sales' automatically computed as Quantity × Unit Price")

    elif "Sales" in df.columns and "Unit Price" not in df.columns:
        df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce").fillna(0.0).round(2)
        df["Unit Price"] = (df["Sales"] / df["Quantity"]).round(2)
        summary["defaults_applied"].append("'Unit Price' automatically computed as Sales ÷ Quantity")

    # Clean numeric types
    df["Unit Price"] = df["Unit Price"].astype(float).round(2)
    df["Sales"] = df["Sales"].astype(float).round(2)

    # 4. Rating processing
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce").fillna(4.0)
    df["Rating"] = df["Rating"].clip(lower=1.0, upper=5.0).round(1)

    # 5. String / Categorical columns cleanup
    for col in ["Invoice ID", "Branch", "City", "Customer Type", "Gender", "Product", "Category", "Payment"]:
        df[col] = df[col].astype(str).str.strip()
        # Replace empty strings with default
        if col in DEFAULT_COLUMN_VALUES:
            df[col] = df[col].replace("", DEFAULT_COLUMN_VALUES[col])

    # 6. Duplicate check
    summary["duplicate_invoices"] = int(df["Invoice ID"].duplicated().sum())

    # 7. Null counts
    summary["null_counts"] = {col: int(df[col].isnull().sum()) for col in df.columns}

    # 8. Date range
    summary["date_range"] = (
        df["Date"].min().strftime("%Y-%m-%d"),
        df["Date"].max().strftime("%Y-%m-%d")
    )

    # 9. Feature Engineering
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%B")
    df["Day"] = df["Date"].dt.day
    df["Day_Of_Week"] = df["Date"].dt.day_name()
    df["Transaction_Value"] = df["Sales"]
    df["Sales_Per_Quantity"] = (df["Sales"] / df["Quantity"].replace(0, 1)).round(2)

    # Summary completion
    summary["is_valid"] = True
    summary["final_rows"] = len(df)
    summary["final_columns"] = df.shape[1]

    return df, summary
