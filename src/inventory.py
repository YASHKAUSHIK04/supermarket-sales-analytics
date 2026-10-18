"""
Supermarket Sales & Customer Analytics - Inventory Intelligence Engine
Module: src/inventory.py

Purpose:
Provides inventory stock management, velocity analysis, longevity forecasting,
and automated replenishment intelligence for supermarket retail operations.

Key Features for BCA Capstone & Viva:
1. Sales Velocity: Computes average daily unit consumption over dynamic time windows.
2. Days of Stock Remaining: Calculates stock runway (Current Stock / Daily Sales).
3. Product Velocity Classification: Categorizes SKUs into Fast-Moving, Moderate,
   Slow-Moving, and Dormant based on empirical sales velocity.
4. Smart Reorder Alerts: Flags stockout risks and suggests exact reorder quantities
   based on target stock policies without negative overdrafts.
5. Explicit Reconciliation: Controlled sales-to-inventory deduction workflow
   with full ledger audit trail.
6. Multi-Source Compatibility: Seamlessly supports SQLite persistent storage,
   default dataset, and custom CSV/Excel uploads with defensive handling of empty
   or missing inventory records without fabricating artificial data.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
import pandas as pd
import numpy as np

from src.database import (
    get_products_df,
    record_stock_movement,
    get_inventory_movements_df,
    get_db_connection,
    get_all_sales_df,
)

# Standard empty DataFrame schema for safe downstream indexing
EMPTY_INVENTORY_COLUMNS = [
    "Product ID", "product_id",
    "Product Name", "product_name",
    "Category", "category_name",
    "Unit Price (₹)", "unit_price",
    "Current Stock", "current_stock",
    "Reorder Threshold", "safety_stock_level",
    "Target Stock", "target_stock",
    "Stock Status", "Active", "Created At",
    "Units_Sold", "units_sold",
    "Revenue_Generated", "revenue_generated",
    "Avg_Daily_Sales", "daily_sales_velocity",
    "Days_Stock_Remaining", "days_of_stock_remaining",
    "Velocity_Classification", "velocity_tier",
    "Stock_Health", "health_status",
    "reorder_flag",
    "Suggested_Reorder_Qty", "recommended_reorder_qty",
    "Estimated_Reorder_Cost", "estimated_reorder_cost"
]


def calculate_inventory_intelligence(
    products_df: Optional[pd.DataFrame] = None,
    sales_df: Optional[pd.DataFrame] = None,
    lookback_days: int = 30,
    db_path: Optional[Union[str, Path]] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Calculate comprehensive inventory intelligence metrics for catalog products.

    Args:
        products_df: Optional DataFrame from `get_products_df()` with catalog columns.
                     If None, automatically loaded from the persistent SQLite database.
        sales_df: Optional DataFrame of sales transactions. If None, loaded from SQLite.
        lookback_days: Number of days in observation window for velocity calculation.
        db_path: Optional custom path to SQLite database (for isolated testing).
        **kwargs: Absorbs alternative parameter aliases (e.g., df_filtered, sales, catalog).

    Returns:
        Enriched DataFrame with velocity, days remaining, stock health, and reorder metrics.
        Returns an empty DataFrame with canonical columns if inventory records are unavailable.
    """
    # 0. Resolve kwargs aliases if parameters were not supplied explicitly
    if sales_df is None:
        for alias in ("sales", "df", "df_filtered", "sales_data", "transactions_df", "transactions"):
            val = kwargs.get(alias)
            if isinstance(val, pd.DataFrame):
                sales_df = val
                break

    if products_df is None:
        for alias in ("products", "catalog", "catalog_df", "inventory_df", "products_catalog"):
            val = kwargs.get(alias)
            if isinstance(val, pd.DataFrame):
                products_df = val
                break

    # Handle positional argument disambiguation:
    # If caller called calculate_inventory_intelligence(df_filtered) positionally,
    # products_df holds the sales dataframe, while sales_df is None.
    if products_df is not None and sales_df is None:
        is_sales_like = "Date" in products_df.columns and "Quantity" in products_df.columns
        is_catalog_like = "Current Stock" in products_df.columns or "current_stock" in products_df.columns
        if is_sales_like and not is_catalog_like:
            sales_df = products_df
            products_df = None

    # Validate lookback_days
    try:
        lookback_days = int(lookback_days) if lookback_days is not None else 30
    except (ValueError, TypeError):
        lookback_days = 30
    lookback_days = max(1, lookback_days)

    # 1. Resolve product catalog
    if products_df is None:
        try:
            products_df = get_products_df(active_only=True, db_path=db_path)
        except Exception:
            products_df = pd.DataFrame()
    elif not isinstance(products_df, pd.DataFrame):
        try:
            products_df = pd.DataFrame(products_df)
        except Exception:
            products_df = pd.DataFrame()

    if products_df is None or products_df.empty:
        return pd.DataFrame(columns=EMPTY_INVENTORY_COLUMNS)

    df_inv = products_df.copy()

    # Normalize canonical product column names if needed
    if "Product Name" not in df_inv.columns and "product_name" in df_inv.columns:
        df_inv["Product Name"] = df_inv["product_name"]
    if "Current Stock" not in df_inv.columns and "current_stock" in df_inv.columns:
        df_inv["Current Stock"] = df_inv["current_stock"]
    if "Category" not in df_inv.columns and "category_name" in df_inv.columns:
        df_inv["Category"] = df_inv["category_name"]
    if "Unit Price (₹)" not in df_inv.columns:
        if "selling_price" in df_inv.columns:
            df_inv["Unit Price (₹)"] = df_inv["selling_price"]
        elif "unit_price" in df_inv.columns:
            df_inv["Unit Price (₹)"] = df_inv["unit_price"]
        elif "Unit Price" in df_inv.columns:
            df_inv["Unit Price (₹)"] = df_inv["Unit Price"]
        else:
            df_inv["Unit Price (₹)"] = 50.0

    if "Reorder Threshold" not in df_inv.columns:
        df_inv["Reorder Threshold"] = df_inv.get("safety_stock_level", 15)
    if "Target Stock" not in df_inv.columns:
        df_inv["Target Stock"] = df_inv["Reorder Threshold"].apply(lambda x: max(int(x * 2.5), 50))
    if "Product ID" not in df_inv.columns:
        df_inv["Product ID"] = df_inv.get("product_id", range(1, len(df_inv) + 1))

    # 2. Resolve sales transaction data
    if sales_df is None:
        try:
            sales_df = get_all_sales_df(db_path=db_path)
        except Exception:
            sales_df = pd.DataFrame()
    elif not isinstance(sales_df, pd.DataFrame):
        try:
            sales_df = pd.DataFrame(sales_df)
        except Exception:
            sales_df = pd.DataFrame()

    # Determine effective observation date range from sales data
    has_valid_sales = (
        sales_df is not None
        and not sales_df.empty
        and "Date" in sales_df.columns
        and "Quantity" in sales_df.columns
        and "Product" in sales_df.columns
    )

    if has_valid_sales:
        sales_clean = sales_df.dropna(subset=["Date", "Quantity", "Product"]).copy()
        sales_clean["Date"] = pd.to_datetime(sales_clean["Date"], errors="coerce")
        sales_clean["Quantity"] = pd.to_numeric(sales_clean["Quantity"], errors="coerce").fillna(0)
        sales_clean["Product"] = sales_clean["Product"].astype(str).str.strip()
        if "Sales" in sales_clean.columns:
            sales_clean["Sales"] = pd.to_numeric(sales_clean["Sales"], errors="coerce").fillna(0.0)
        sales_clean = sales_clean.dropna(subset=["Date"])
        sales_clean = sales_clean[(sales_clean["Quantity"] > 0) & (sales_clean["Product"] != "")]

        # Check product name overlap between sales and inventory catalog
        sales_products = set(sales_clean["Product"].dropna().astype(str).str.strip().str.lower())
        catalog_products = set(df_inv["Product Name"].dropna().astype(str).str.strip().str.lower())
        overlap = sales_products & catalog_products

        # If the sales dataset has products, but ZERO products match the catalog,
        # inventory records are unavailable for this sales dataset.
        if len(sales_products) > 0 and len(overlap) == 0:
            return pd.DataFrame(columns=EMPTY_INVENTORY_COLUMNS)

        if not sales_clean.empty:
            max_date = sales_clean["Date"].max()
            min_date = max_date - pd.Timedelta(days=max(1, lookback_days))

            # Filter sales within observation window
            window_sales = sales_clean[sales_clean["Date"] >= min_date]
            effective_days = (
                max(1, (max_date - window_sales["Date"].min()).days + 1)
                if not window_sales.empty
                else lookback_days
            )

            # Aggregate sales by product name (case-insensitive mapping)
            sales_summary = window_sales.groupby(
                window_sales["Product"].astype(str).str.strip().str.lower()
            ).agg(
                Units_Sold=("Quantity", "sum"),
                Revenue_Generated=("Sales", "sum") if "Sales" in window_sales.columns else ("Quantity", lambda x: 0.0)
            ).reset_index()
            sales_summary.rename(columns={"Product": "prod_key"}, inplace=True)
        else:
            sales_summary = pd.DataFrame(columns=["prod_key", "Units_Sold", "Revenue_Generated"])
            effective_days = lookback_days
    else:
        sales_summary = pd.DataFrame(columns=["prod_key", "Units_Sold", "Revenue_Generated"])
        effective_days = max(1, lookback_days)

    # 3. Merge product catalog with sales velocity
    df_inv["prod_key"] = df_inv["Product Name"].astype(str).str.strip().str.lower()
    df_merged = df_inv.merge(sales_summary, on="prod_key", how="left")
    df_merged.drop(columns=["prod_key"], inplace=True)

    df_merged["Units_Sold"] = df_merged["Units_Sold"].fillna(0).astype(int)
    df_merged["Revenue_Generated"] = df_merged["Revenue_Generated"].fillna(0.0).round(2)

    # 4. Average Daily Sales Velocity
    df_merged["Avg_Daily_Sales"] = (df_merged["Units_Sold"] / float(effective_days)).round(2)

    # 5. Days of Stock Remaining
    def compute_days_remaining(row):
        stock = row["Current Stock"]
        velocity = row["Avg_Daily_Sales"]
        if stock <= 0:
            return 0.0
        if velocity <= 0.001:
            return 999.0  # Infinite stock runway when no recent sales exist
        return round(float(stock) / float(velocity), 1)

    df_merged["Days_Stock_Remaining"] = df_merged.apply(compute_days_remaining, axis=1)

    # 6. Product Velocity Classification (Fast / Moderate / Slow / Dormant)
    def classify_velocity(row):
        daily = row["Avg_Daily_Sales"]
        sold = row["Units_Sold"]
        if sold == 0:
            return "Dormant (No Sales)"
        if daily >= 1.0:
            return "Fast-Moving"
        if daily >= 0.35:
            return "Moderate"
        return "Slow-Moving"

    df_merged["Velocity_Classification"] = df_merged.apply(classify_velocity, axis=1)

    # 7. Stock Health Status Badges
    def classify_health_status(row):
        stock = row["Current Stock"]
        reorder = row["Reorder Threshold"]
        target = row["Target Stock"]
        days = row["Days_Stock_Remaining"]

        if stock <= 0:
            return "Out of Stock"
        if stock <= reorder or days <= 7.0:
            return "Low Stock"
        if stock > target * 1.5 and days > 60:
            return "Overstocked"
        return "Healthy"

    def classify_stock_health_badge(row):
        status = row["health_status"]
        if status == "Out of Stock":
            return "🚨 OUT OF STOCK"
        if status == "Low Stock":
            return "⚠️ CRITICAL REORDER"
        if status == "Overstocked":
            return "🔵 OVERSTOCKED"
        return "✅ HEALTHY"

    df_merged["health_status"] = df_merged.apply(classify_health_status, axis=1)
    df_merged["Stock_Health"] = df_merged.apply(classify_stock_health_badge, axis=1)

    # 8. Suggested Reorder Quantity & Cost
    def compute_reorder_qty(row):
        stock = row["Current Stock"]
        target = row["Target Stock"]
        if stock <= row["Reorder Threshold"]:
            return max(0, int(target - stock))
        return 0

    df_merged["Suggested_Reorder_Qty"] = df_merged.apply(compute_reorder_qty, axis=1)
    df_merged["Estimated_Reorder_Cost"] = (
        df_merged["Suggested_Reorder_Qty"] * df_merged["Unit Price (₹)"]
    ).round(2)

    # 9. Dual-Naming Compatibility Aliases (supporting both conventions)
    df_merged["product_id"] = df_merged["Product ID"]
    df_merged["product_name"] = df_merged["Product Name"]
    df_merged["category_name"] = df_merged["Category"]
    df_merged["current_stock"] = df_merged["Current Stock"]
    df_merged["safety_stock_level"] = df_merged["Reorder Threshold"]
    df_merged["target_stock"] = df_merged["Target Stock"]
    df_merged["units_sold"] = df_merged["Units_Sold"]
    df_merged["revenue_generated"] = df_merged["Revenue_Generated"]
    df_merged["daily_sales_velocity"] = df_merged["Avg_Daily_Sales"]
    df_merged["days_of_stock_remaining"] = df_merged["Days_Stock_Remaining"]
    df_merged["velocity_tier"] = df_merged["Velocity_Classification"]
    df_merged["reorder_flag"] = (df_merged["Suggested_Reorder_Qty"] > 0).astype(int)
    df_merged["recommended_reorder_qty"] = df_merged["Suggested_Reorder_Qty"]
    df_merged["estimated_reorder_cost"] = df_merged["Estimated_Reorder_Cost"]

    return df_merged


def get_inventory_summary_kpis(intel_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """Compute high-level executive inventory metrics for dashboard KPI cards.

    Returns a comprehensive dictionary supporting all key variations to ensure
    seamless compatibility with both frontend metric cards and automated tests.
    """
    empty_result = {
        "total_skus": 0,
        "total_products": 0,
        "total_units": 0,
        "valuation": 0.0,
        "total_stock_value": 0.0,
        "out_of_stock": 0,
        "out_of_stock_count": 0,
        "critical_reorder": 0,
        "low_stock_count": 0,
        "fast_moving": 0,
        "slow_moving": 0,
        "total_reorder_capital": 0.0,
        "total_reorder_cost": 0.0
    }

    if intel_df is None or intel_df.empty:
        return empty_result

    stock_col = "Current Stock" if "Current Stock" in intel_df.columns else "current_stock"
    price_col = "Unit Price (₹)" if "Unit Price (₹)" in intel_df.columns else ("unit_price" if "unit_price" in intel_df.columns else "Unit Price")
    cost_col = "Estimated_Reorder_Cost" if "Estimated_Reorder_Cost" in intel_df.columns else "estimated_reorder_cost"
    health_col = "Stock_Health" if "Stock_Health" in intel_df.columns else "health_status"
    vel_col = "Velocity_Classification" if "Velocity_Classification" in intel_df.columns else "velocity_tier"

    total_skus = len(intel_df)
    total_units = int(intel_df[stock_col].sum()) if stock_col in intel_df.columns else 0
    valuation = (
        float((intel_df[stock_col] * intel_df[price_col]).sum())
        if (stock_col in intel_df.columns and price_col in intel_df.columns)
        else 0.0
    )

    out_of_stock = int((intel_df[stock_col] <= 0).sum()) if stock_col in intel_df.columns else 0
    critical_reorder = (
        int(intel_df[health_col].astype(str).str.upper().str.contains("OUT OF STOCK|CRITICAL|LOW").sum())
        if health_col in intel_df.columns
        else 0
    )

    fast_moving = (
        int(intel_df[vel_col].astype(str).str.upper().str.contains("FAST").sum())
        if vel_col in intel_df.columns
        else 0
    )
    slow_moving = (
        int(intel_df[vel_col].astype(str).str.upper().str.contains("SLOW|DORMANT|NON-MOVING").sum())
        if vel_col in intel_df.columns
        else 0
    )

    total_reorder_capital = float(intel_df[cost_col].sum()) if cost_col in intel_df.columns else 0.0

    return {
        "total_skus": total_skus,
        "total_products": total_skus,
        "total_units": total_units,
        "valuation": round(valuation, 2),
        "total_stock_value": round(valuation, 2),
        "out_of_stock": out_of_stock,
        "out_of_stock_count": out_of_stock,
        "critical_reorder": critical_reorder,
        "low_stock_count": critical_reorder,
        "fast_moving": fast_moving,
        "slow_moving": slow_moving,
        "total_reorder_capital": round(total_reorder_capital, 2),
        "total_reorder_cost": round(total_reorder_capital, 2)
    }


def reconcile_sales_deduction(
    sales_df: pd.DataFrame,
    reference_note: str = "Sales Reconciliation Deduction",
    allow_partial: bool = False,
    db_path: Optional[Any] = None
) -> Dict[str, Any]:
    """Explicitly reconcile and deduct inventory stock based on sales transactions.

    Decouples sales data upload from silent inventory decrements:
    Users review and trigger stock deduction explicitly with full ledger audit.

    Args:
        sales_df: DataFrame with 'Product' and 'Quantity'.
        reference_note: Audit note recorded in immutable ledger.
        allow_partial: If True, deducts available balance when full quantity is unavailable.
                       If False, halts atomically if any product has insufficient stock.
        db_path: Database path for connection.

    Returns:
        Structured audit report with items deducted, shortfalls, and ledger movement IDs.
    """
    if sales_df is None or sales_df.empty or "Product" not in sales_df.columns or "Quantity" not in sales_df.columns:
        return {
            "success": False,
            "status": "error",
            "deducted_items": 0,
            "products_reconciled": 0,
            "total_units_deducted": 0,
            "errors": ["Invalid sales DataFrame for reconciliation."]
        }

    # Aggregate quantities to deduct per product
    demand = sales_df.groupby("Product", observed=True)["Quantity"].sum().to_dict()

    products_catalog = get_products_df(active_only=True, db_path=db_path)
    if products_catalog.empty:
        return {
            "success": False,
            "status": "error",
            "deducted_items": 0,
            "products_reconciled": 0,
            "total_units_deducted": 0,
            "errors": ["Product catalog is empty."]
        }

    stock_lookup = dict(zip(products_catalog["Product Name"], products_catalog["Current Stock"]))
    pid_lookup = dict(zip(products_catalog["Product Name"], products_catalog["Product ID"]))

    shortfalls: List[Dict[str, Any]] = []
    deductions: List[Dict[str, Any]] = []

    # Pre-validation check: inspect for overdrafts
    for prod_name, req_qty in demand.items():
        if prod_name not in stock_lookup:
            continue
        curr_stock = stock_lookup[prod_name]
        if curr_stock < req_qty:
            shortfalls.append({
                "product": prod_name,
                "current_stock": curr_stock,
                "requested_deduction": int(req_qty),
                "shortfall": int(req_qty - curr_stock)
            })

    # If shortfalls exist and partial deduction is not permitted, safely abort
    if shortfalls and not allow_partial:
        return {
            "success": False,
            "status": "aborted",
            "shortfalls": shortfalls,
            "deducted_items": 0,
            "products_reconciled": 0,
            "total_units_deducted": 0,
            "message": "Reconciliation aborted: Some products have insufficient stock to cover requested sales volume."
        }

    # Execute atomic ledger updates
    movement_ids: List[int] = []
    total_units_deducted = 0
    for prod_name, req_qty in demand.items():
        if prod_name not in pid_lookup:
            continue
        pid = pid_lookup[prod_name]
        curr_stock = stock_lookup[prod_name]

        qty_to_deduct = min(curr_stock, int(req_qty)) if allow_partial else int(req_qty)
        if qty_to_deduct <= 0:
            continue

        mov_id = record_stock_movement(
            product_id=pid,
            movement_type="SALE_DEDUCTION",
            quantity_change=-qty_to_deduct,
            reference_note=f"{reference_note} (Sold: {req_qty})",
            db_path=db_path
        )
        movement_ids.append(mov_id)
        total_units_deducted += qty_to_deduct
        deductions.append({
            "product": prod_name,
            "deducted": qty_to_deduct,
            "remaining_balance": curr_stock - qty_to_deduct
        })

    return {
        "success": True,
        "status": "success",
        "deducted_items": len(deductions),
        "products_reconciled": len(deductions),
        "total_units_deducted": total_units_deducted,
        "deductions": deductions,
        "movement_ids": movement_ids,
        "shortfalls": shortfalls,
        "message": f"Successfully reconciled inventory stock for {len(deductions)} products."
    }
