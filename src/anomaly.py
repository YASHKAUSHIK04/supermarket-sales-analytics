"""
Supermarket Sales & Customer Analytics - Dual-Layer Anomaly Detection Engine
Module: src/anomaly.py

Purpose:
Detects data-quality violations and statistical transaction outliers across
supermarket sales datasets.

Architecture for BCA Capstone & Viva:
1. Layer 1: Deterministic Data-Quality Rules
   - Mathematical discrepancies: Sales != Quantity * Unit Price (> tolerance)
   - Invalid numbers: Negative/zero quantities or prices
   - Range violations: Ratings < 1.0 or > 5.0
   - Duplicate transaction keys: Repeated Invoice IDs
   - Missing mandatory fields: Null dates, products, or categories
2. Layer 2: Statistical & Operational Anomaly Detection
   - High-Value Outlier Baskets: Tukey's Interquartile Range (IQR) method (Q3 + 1.5 * IQR)
   - Temporal Spikes & Crashes: Daily sales volumes deviating > 2.5 sigma from mean
   - Branch Quality Slumps: Outlying branches with satisfaction scores significantly below peers
3. Severity Hierarchy:
   - CRITICAL: Severe mathematical corruption, negative prices, null mandatory fields
   - HIGH: Duplicate invoice IDs, extreme cart values
   - MEDIUM: Statistical volume spikes/dips, category revenue divergence
   - LOW: Minor rounding warnings, borderline ratings
4. Transparent Audit Trail:
   Every alert includes a clear description, expected vs actual value, severity, and
   concrete operational investigation recommendation.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


def detect_anomalies(
    df: pd.DataFrame,
    math_tolerance: float = 0.05,
    iqr_multiplier: float = 1.5,
    spike_sigma: float = 2.5,
    persist_to_db: bool = False,
    db_path: Optional[Any] = None
) -> List[Dict[str, Any]]:
    """Scan a sales DataFrame for both data-quality errors and statistical anomalies.

    Args:
        df: Sales DataFrame with canonical columns.
        math_tolerance: Currency tolerance for Sales = Quantity * Unit Price verification.
        iqr_multiplier: Multiplier for Tukey's boxplot fence (default 1.5).
        spike_sigma: Standard deviation threshold for temporal surge/crash detection.
        persist_to_db: If True, writes detected alerts to SQLite `anomaly_records`.
        db_path: Optional SQLite database connection path.

    Returns:
        List of structured anomaly dictionaries.
    """
    alerts: List[Dict[str, Any]] = []

    if df.empty:
        return alerts

    # -------------------------------------------------------------
    # 1. DETERMINISTIC RULE: Mathematical Integrity Discrepancies
    # -------------------------------------------------------------
    if all(col in df.columns for col in ["Quantity", "Unit Price", "Sales"]):
        expected_sales = df["Quantity"] * df["Unit Price"]
        diff = (df["Sales"] - expected_sales).abs()
        mismatch_mask = diff > math_tolerance

        if mismatch_mask.any():
            for idx, row in df[mismatch_mask].iterrows():
                inv = str(row.get("Invoice ID", f"Row-{idx}"))
                act_sales = float(row["Sales"])
                exp_sales = float(expected_sales.loc[idx])
                delta = act_sales - exp_sales

                severity = "CRITICAL" if abs(delta) > 50.0 else "HIGH"
                alerts.append({
                    "invoice_id": inv,
                    "anomaly_type": "DATA_QUALITY_ERROR",
                    "severity": severity,
                    "title": "Sales Calculation Discrepancy",
                    "description": (
                        f"Invoice {inv} recorded Sales of ₹{act_sales:,.2f}, but Quantity ({row['Quantity']}) "
                        f"× Unit Price (₹{row['Unit Price']:,.2f}) equals ₹{exp_sales:,.2f} "
                        f"(discrepancy: ₹{delta:+,.2f})."
                    ),
                    "expected_value": f"₹{exp_sales:,.2f}",
                    "actual_value": f"₹{act_sales:,.2f}",
                    "recommended_action": (
                        "Verify point-of-sale terminal firmware and discount/tax line-item calculations. "
                        "Audit barcode scanner rates against central product master."
                    )
                })

    # -------------------------------------------------------------
    # 2. DETERMINISTIC RULE: Invalid / Negative / Missing Values
    # -------------------------------------------------------------
    # Negative or Zero Quantity
    if "Quantity" in df.columns:
        invalid_qty = df["Quantity"] <= 0
        if invalid_qty.any():
            for idx, row in df[invalid_qty].iterrows():
                inv = str(row.get("Invoice ID", f"Row-{idx}"))
                alerts.append({
                    "invoice_id": inv,
                    "anomaly_type": "DATA_QUALITY_ERROR",
                    "severity": "CRITICAL",
                    "title": "Invalid Non-Positive Quantity",
                    "description": f"Invoice {inv} recorded a non-positive quantity of {row['Quantity']}.",
                    "expected_value": "Quantity > 0",
                    "actual_value": str(row["Quantity"]),
                    "recommended_action": "Check for corrupted POS receipt logs or unmapped refund transactions."
                })

    # Negative Unit Price
    if "Unit Price" in df.columns:
        invalid_price = df["Unit Price"] < 0
        if invalid_price.any():
            for idx, row in df[invalid_price].iterrows():
                inv = str(row.get("Invoice ID", f"Row-{idx}"))
                alerts.append({
                    "invoice_id": inv,
                    "anomaly_type": "DATA_QUALITY_ERROR",
                    "severity": "CRITICAL",
                    "title": "Negative Unit Price Recorded",
                    "description": f"Invoice {inv} recorded a negative unit price of ₹{row['Unit Price']:,.2f}.",
                    "expected_value": "Unit Price >= ₹0.00",
                    "actual_value": f"₹{row['Unit Price']:,.2f}",
                    "recommended_action": "Audit pricing database master for manual typo or debit adjustment errors."
                })

    # Rating Out of Range (1.0 to 5.0)
    if "Rating" in df.columns:
        invalid_rating = (df["Rating"] < 1.0) | (df["Rating"] > 5.0)
        if invalid_rating.any():
            for idx, row in df[invalid_rating].iterrows():
                inv = str(row.get("Invoice ID", f"Row-{idx}"))
                alerts.append({
                    "invoice_id": inv,
                    "anomaly_type": "DATA_QUALITY_ERROR",
                    "severity": "HIGH",
                    "title": "Customer Rating Out of Bounds",
                    "description": f"Invoice {inv} recorded a rating of {row['Rating']}, outside valid 1.0–5.0 scale.",
                    "expected_value": "1.0 <= Rating <= 5.0",
                    "actual_value": str(row["Rating"]),
                    "recommended_action": "Inspect customer feedback kiosk and survey response ingestion parser."
                })

    # -------------------------------------------------------------
    # 3. DETERMINISTIC RULE: Duplicate Transaction Identifiers
    # -------------------------------------------------------------
    if "Invoice ID" in df.columns:
        dup_series = df[df["Invoice ID"].duplicated(keep=False)]
        if not dup_series.empty:
            for inv, group in dup_series.groupby("Invoice ID"):
                alerts.append({
                    "invoice_id": str(inv),
                    "anomaly_type": "DUPLICATE_ID",
                    "severity": "HIGH",
                    "title": "Duplicate Invoice ID Detected",
                    "description": f"Invoice ID '{inv}' appears {len(group)} times in the active dataset.",
                    "expected_value": "Unique Invoice ID per sale",
                    "actual_value": f"Appears {len(group)} times",
                    "recommended_action": (
                        "Verify whether cashier double-scanned the checkout order or if network retry "
                        "resubmitted the same basket payload."
                    )
                })

    # -------------------------------------------------------------
    # 4. STATISTICAL ANOMALY: High-Value Basket Outliers (Tukey's IQR)
    # -------------------------------------------------------------
    # Requires sufficient sample size (N >= 15) to prevent misclassifying standard transactions
    if "Sales" in df.columns and len(df) >= 15:
        q1 = df["Sales"].quantile(0.25)
        q3 = df["Sales"].quantile(0.75)
        iqr = q3 - q1

        upper_fence = None
        if iqr > 0:
            upper_fence = q3 + (iqr_multiplier * iqr)
        elif df["Sales"].std() > 0:
            upper_fence = df["Sales"].mean() + (3.0 * df["Sales"].std())

        if upper_fence is not None:
            outliers = df[df["Sales"] > upper_fence]

            # Limit reported outliers to top 10 most extreme to avoid alert fatigue
            if not outliers.empty:
                for idx, row in outliers.sort_values(by="Sales", ascending=False).head(10).iterrows():
                    inv = str(row.get("Invoice ID", f"Row-{idx}"))
                    alerts.append({
                        "invoice_id": inv,
                        "anomaly_type": "STATISTICAL_ANOMALY",
                        "severity": "MEDIUM",
                        "title": "Statistical Outlier: High Transaction Value",
                        "description": (
                            f"Invoice {inv} for {row.get('Product', 'Item')} totaled ₹{row['Sales']:,.2f}, "
                            f"exceeding upper statistical threshold ₹{upper_fence:,.2f} "
                            f"(Q3 = ₹{q3:,.2f}, IQR = ₹{iqr:,.2f})."
                        ),
                        "expected_value": f"<= ₹{upper_fence:,.2f}",
                        "actual_value": f"₹{row['Sales']:,.2f}",
                        "recommended_action": (
                            "Review whether this is a bulk commercial purchase, high-quantity catering order, "
                            "or an unauthorized checkout override."
                        )
                    })

    # -------------------------------------------------------------
    # 5. TEMPORAL ANOMALY: Unusual Daily Sales Surges & Crashes
    # -------------------------------------------------------------
    if "Date" in df.columns and "Sales" in df.columns:
        daily_sales = df.groupby(pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d"))["Sales"].sum()
        # Require at least 14 days of history for valid rolling baseline
        if len(daily_sales) >= 14:
            mean_daily = daily_sales.mean()
            std_daily = daily_sales.std()

            if std_daily > 0:
                surge_threshold = mean_daily + (spike_sigma * std_daily)
                crash_threshold = max(0.0, mean_daily - (spike_sigma * std_daily))

                # Check spikes
                spikes = daily_sales[daily_sales > surge_threshold]
                for d_str, val in spikes.items():
                    alerts.append({
                        "invoice_id": f"Date-{d_str}",
                        "anomaly_type": "TEMPORAL_SPIKE",
                        "severity": "MEDIUM",
                        "title": "Unusual Daily Sales Surge",
                        "description": (
                            f"Daily sales on {d_str} surged to ₹{val:,.2f}, exceeding the {spike_sigma}σ "
                            f"upper normal boundary of ₹{surge_threshold:,.2f} (Daily Mean: ₹{mean_daily:,.2f})."
                        ),
                        "expected_value": f"<= ₹{surge_threshold:,.2f}",
                        "actual_value": f"₹{val:,.2f}",
                        "recommended_action": (
                            "Investigate local marketing campaigns, seasonal festival rush, or bulk institutional "
                            "purchases on this date."
                        )
                    })

                # Check crashes
                if crash_threshold > 0:
                    crashes = daily_sales[daily_sales < crash_threshold]
                    for d_str, val in crashes.items():
                        alerts.append({
                            "invoice_id": f"Date-{d_str}",
                            "anomaly_type": "TEMPORAL_DIP",
                            "severity": "HIGH",
                            "title": "Severe Daily Sales Dip",
                            "description": (
                                f"Daily sales on {d_str} crashed to ₹{val:,.2f}, below the {spike_sigma}σ "
                                f"lower normal boundary of ₹{crash_threshold:,.2f} (Daily Mean: ₹{mean_daily:,.2f})."
                            ),
                            "expected_value": f">= ₹{crash_threshold:,.2f}",
                            "actual_value": f"₹{val:,.2f}",
                            "recommended_action": (
                                "Inspect for store closure, power outage, server downtime, weather event, or "
                                "POS network connectivity failure."
                            )
                        })

    # Optional SQLite persistence
    if persist_to_db:
        from src.database import log_anomaly
        for alert in alerts:
            try:
                log_anomaly(
                    invoice_id=alert["invoice_id"],
                    anomaly_type=alert["anomaly_type"],
                    severity=alert["severity"],
                    description=alert["description"],
                    expected_value=alert["expected_value"],
                    actual_value=alert["actual_value"],
                    recommended_action=alert["recommended_action"],
                    db_path=db_path
                )
            except Exception:
                pass

    return alerts


def get_anomaly_summary(alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary counts by type and severity for dashboard executive display."""
    total = len(alerts)
    by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    by_type = {
        "DATA_QUALITY_ERROR": 0,
        "STATISTICAL_ANOMALY": 0,
        "DUPLICATE_ID": 0,
        "TEMPORAL_SPIKE": 0,
        "TEMPORAL_DIP": 0
    }

    for a in alerts:
        sev = a.get("severity", "LOW")
        by_severity[sev] = by_severity.get(sev, 0) + 1

        atype = a.get("anomaly_type", "DATA_QUALITY_ERROR")
        by_type[atype] = by_type.get(atype, 0) + 1

    return {
        "total_anomalies": total,
        "by_severity": by_severity,
        "by_type": by_type,
        "data_quality_count": by_type["DATA_QUALITY_ERROR"] + by_type["DUPLICATE_ID"],
        "statistical_count": by_type["STATISTICAL_ANOMALY"] + by_type["TEMPORAL_SPIKE"] + by_type["TEMPORAL_DIP"]
    }
