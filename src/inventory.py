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
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import pandas as pd
import numpy as np
from src.database import (
    get_products_df,
    record_stock_movement,
    get_inventory_movements_df,
    get_db_connection
)


def calculate_inventory_intelligence(
    products_df: pd.DataFrame,
    sales_df: pd.DataFrame,
    lookback_days: int = 30
) -> pd.DataFrame:
    """Calculate comprehensive inventory intelligence metrics for all catalog products.

    Args:
        products_df: DataFrame from `get_products_df()` with columns:
                     ['Product ID', 'Product Name', 'Category', 'Unit Price (₹)',
                      'Current Stock', 'Reorder Threshold', 'Target Stock']
        sales_df: DataFrame of sales transactions with ['Product', 'Date', 'Quantity', 'Sales'].
        lookback_days: Number of days in observation window for velocity calculation.

    Returns:
        Enriched DataFrame with velocity, days remaining, stock health, and reorder metrics.
    """
    if products_df.empty:
        return pd.DataFrame()

    df_inv = products_df.copy()

    # Determine effective observation date range from sales data
    if not sales_df.empty and "Date" in sales_df.columns and "Quantity" in sales_df.columns:
        sales_clean = sales_df.dropna(subset=["Date", "Quantity", "Product"]).copy()
        sales_clean["Date"] = pd.to_datetime(sales_clean["Date"], errors="coerce")
        sales_clean = sales_clean.dropna(subset=["Date"])

        if not sales_clean.empty:
            max_date = sales_clean["Date"].max()
            min_date = max_date - pd.Timedelta(days=max(1, lookback_days))

            # Filter sales within window
            window_sales = sales_clean[sales_clean["Date"] >= min_date]
            effective_days = max(1, (max_date - window_sales["Date"].min()).days + 1) if not window_sales.empty else lookback_days

            # Aggregate sales by product name (case-insensitive mapping)
            sales_summary = window_sales.groupby(
                window_sales["Product"].str.strip().str.lower()
            ).agg(
                Units_Sold=("Quantity", "sum"),
                Revenue_Generated=("Sales", "sum")
            ).reset_index()
            sales_summary.rename(columns={"Product": "prod_key"}, inplace=True)
        else:
            sales_summary = pd.DataFrame(columns=["prod_key", "Units_Sold", "Revenue_Generated"])
            effective_days = lookback_days
    else:
        sales_summary = pd.DataFrame(columns=["prod_key", "Units_Sold", "Revenue_Generated"])
        effective_days = max(1, lookback_days)

    # Merge product catalog with sales summary
    df_inv["prod_key"] = df_inv["Product Name"].str.strip().str.lower()
    df_merged = df_inv.merge(sales_summary, on="prod_key", how="left")
    df_merged.drop(columns=["prod_key"], inplace=True)

    df_merged["Units_Sold"] = df_merged["Units_Sold"].fillna(0).astype(int)
    df_merged["Revenue_Generated"] = df_merged["Revenue_Generated"].fillna(0.0).round(2)

    # 1. Average Daily Sales Velocity
    df_merged["Avg_Daily_Sales"] = (df_merged["Units_Sold"] / float(effective_days)).round(2)

    # 2. Days of Stock Remaining
    def compute_days_remaining(row):
        stock = row["Current Stock"]
        velocity = row["Avg_Daily_Sales"]
        if stock == 0:
            return 0.0
        if velocity <= 0.001:
            return 999.0  # Represents essentially infinite stock with no recent sales
        return round(stock / velocity, 1)

    df_merged["Days_Stock_Remaining"] = df_merged.apply(compute_days_remaining, axis=1)

    # 3. Product Velocity Classification (Fast / Moderate / Slow / Dormant)
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

    # 4. Stock Health Status Badge
    def classify_health(row):
        stock = row["Current Stock"]
        reorder = row["Reorder Threshold"]
        target = row["Target Stock"]
        days = row["Days_Stock_Remaining"]

        if stock <= 0:
            return "🚨 OUT OF STOCK"
        if stock <= reorder or days <= 7.0:
            return "⚠️ CRITICAL REORDER"
        if stock <= reorder * 1.3:
            return "📦 LOW STOCK"
        if stock > target * 1.5 and days > 60:
            return "🔵 OVERSTOCKED"
        return "✅ HEALTHY"

    df_merged["Stock_Health"] = df_merged.apply(classify_health, axis=1)

    # 5. Suggested Reorder Quantity
    def compute_reorder_qty(row):
        stock = row["Current Stock"]
        target = row["Target Stock"]
        if stock <= row["Reorder Threshold"]:
            return max(0, target - stock)
        return 0

    df_merged["Suggested_Reorder_Qty"] = df_merged.apply(compute_reorder_qty, axis=1)

    # 6. Estimated Reorder Investment Required
    df_merged["Estimated_Reorder_Cost"] = (
        df_merged["Suggested_Reorder_Qty"] * df_merged["Unit Price (₹)"]
    ).round(2)

    return df_merged


def get_inventory_summary_kpis(intel_df: pd.DataFrame) -> Dict[str, Any]:
    """Compute high-level executive inventory metrics for dashboard KPI cards."""
    if intel_df.empty:
        return {
            "total_skus": 0,
            "total_units": 0,
            "valuation": 0.0,
            "out_of_stock": 0,
            "critical_reorder": 0,
            "fast_moving": 0,
            "slow_moving": 0,
            "total_reorder_capital": 0.0
        }

    total_skus = len(intel_df)
    total_units = int(intel_df["Current Stock"].sum())
    valuation = float((intel_df["Current Stock"] * intel_df["Unit Price (₹)"]).sum())

    out_of_stock = int((intel_df["Current Stock"] == 0).sum())
    critical_reorder = int(intel_df["Stock_Health"].isin(["🚨 OUT OF STOCK", "⚠️ CRITICAL REORDER"]).sum())

    fast_moving = int((intel_df["Velocity_Classification"] == "Fast-Moving").sum())
    slow_moving = int(intel_df["Velocity_Classification"].isin(["Slow-Moving", "Dormant (No Sales)"]).sum())

    total_reorder_capital = float(intel_df["Estimated_Reorder_Cost"].sum())

    return {
        "total_skus": total_skus,
        "total_units": total_units,
        "valuation": round(valuation, 2),
        "out_of_stock": out_of_stock,
        "critical_reorder": critical_reorder,
        "fast_moving": fast_moving,
        "slow_moving": slow_moving,
        "total_reorder_capital": round(total_reorder_capital, 2)
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
    if sales_df.empty or "Product" not in sales_df.columns or "Quantity" not in sales_df.columns:
        return {"success": False, "deducted_items": 0, "errors": ["Invalid sales DataFrame for reconciliation."]}

    # Aggregate quantities to deduct per product
    demand = sales_df.groupby("Product", observed=True)["Quantity"].sum().to_dict()

    products_catalog = get_products_df(active_only=True, db_path=db_path)
    if products_catalog.empty:
        return {"success": False, "deducted_items": 0, "errors": ["Product catalog is empty."]}

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
            "shortfalls": shortfalls,
            "deducted_items": 0,
            "message": "Reconciliation aborted: Some products have insufficient stock to cover requested sales volume."
        }

    # Execute atomic ledger updates
    movement_ids: List[int] = []
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
        deductions.append({
            "product": prod_name,
            "deducted": qty_to_deduct,
            "remaining_balance": curr_stock - qty_to_deduct
        })

    return {
        "success": True,
        "deducted_items": len(deductions),
        "deductions": deductions,
        "movement_ids": movement_ids,
        "shortfalls": shortfalls,
        "message": f"Successfully reconciled inventory stock for {len(deductions)} products."
    }
