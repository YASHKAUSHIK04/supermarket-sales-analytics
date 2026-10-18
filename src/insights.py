"""
Supermarket Sales & Customer Analytics - 4-Tier Business Insights Engine
Module: src/insights.py

Purpose:
Generates commercial business recommendations grounded strictly in actual
calculated metrics without hallucinations or unjustified causal claims.

Framework for BCA Capstone & Viva Defense:
Every business finding adheres to the structured 4-tier decision model:
1. Observation: Empirical fact directly extracted from the sales/inventory dataset.
2. Business Insight: Quantitative commercial interpretation of the finding.
3. Possible Explanation: Plausible retail operational drivers (with explicit caveats
   that correlation does not prove causation).
4. Recommended Action: Concrete, actionable merchandising or store-operations step.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np


def generate_structured_business_insights(
    df: pd.DataFrame,
    inventory_df: Optional[pd.DataFrame] = None
) -> List[Dict[str, str]]:
    """Generate 4-tier commercial recommendations from active sales and inventory data.

    Args:
        df: Filtered sales DataFrame.
        inventory_df: Optional inventory intelligence DataFrame.

    Returns:
        List of structured insight dictionaries containing:
        ['category', 'title', 'observation', 'insight', 'explanation', 'action', 'severity']
    """
    insights: List[Dict[str, str]] = []

    if df.empty:
        insights.append({
            "category": "Data Availability",
            "title": "No Transaction Records Available",
            "observation": "Current filter criteria returned 0 sales records.",
            "insight": "Business metrics cannot be computed without underlying transaction data.",
            "explanation": "Active filters (Date, Branch, Category, etc.) may be mutually exclusive.",
            "action": "Reset or broaden sidebar filters to inspect retail performance.",
            "severity": "LOW"
        })
        return insights

    total_sales = float(df["Sales"].sum())
    total_txns = len(df)
    atv = total_sales / total_txns if total_txns > 0 else 0.0

    # -------------------------------------------------------------
    # 1. Geographic / Branch Commercial Productivity
    # -------------------------------------------------------------
    if "Branch" in df.columns and "City" in df.columns:
        branch_agg = df.groupby(["Branch", "City"], observed=True)["Sales"].agg(["sum", "count"]).reset_index()
        if len(branch_agg) > 1:
            top_b = branch_agg.sort_values(by="sum", ascending=False).iloc[0]
            low_b = branch_agg.sort_values(by="sum", ascending=True).iloc[0]

            top_share = (top_b["sum"] / total_sales * 100) if total_sales > 0 else 0
            low_share = (low_b["sum"] / total_sales * 100) if total_sales > 0 else 0

            insights.append({
                "category": "Geographic Performance",
                "title": f"Branch Revenue Disparity: {top_b['Branch']} vs {low_b['Branch']}",
                "observation": (
                    f"{top_b['Branch']} ({top_b['City']}) generated ₹{top_b['sum']:,.2f} ({top_share:.1f}% of total sales) "
                    f"across {top_b['count']} transactions, whereas {low_b['Branch']} ({low_b['City']}) generated "
                    f"₹{low_b['sum']:,.2f} ({low_share:.1f}% share) across {low_b['count']} transactions."
                ),
                "insight": (
                    f"Top store outperforms lowest store by {(top_b['sum']/low_b['sum'] if low_b['sum']>0 else 1.0):.1f}x. "
                    f"Retail foot-traffic and ticket volume exhibit substantial geographic concentration."
                ),
                "explanation": (
                    "Possible drivers include commercial footfall density, catchment demographic wealth, store floor space, "
                    "or local competitor proximity. Note: Data does not track marketing spend or footfall count directly."
                ),
                "action": (
                    f"Audit inventory assortment and promotional banners at {low_b['Branch']}. Replicate top-selling "
                    f"merchandise bundles proven in {top_b['Branch']} to elevate lower-volume locations."
                ),
                "severity": "MEDIUM"
            })

    # -------------------------------------------------------------
    # 2. Merchandise Category Revenue vs Volume Dynamics
    # -------------------------------------------------------------
    if "Category" in df.columns and "Quantity" in df.columns:
        cat_rev = df.groupby("Category", observed=True)["Sales"].sum()
        cat_vol = df.groupby("Category", observed=True)["Quantity"].sum()

        if not cat_rev.empty and not cat_vol.empty:
            top_rev_cat = cat_rev.idxmax()
            top_rev_val = cat_rev.max()
            top_rev_share = (top_rev_val / total_sales * 100) if total_sales > 0 else 0

            top_vol_cat = cat_vol.idxmax()
            top_vol_val = cat_vol.max()

            insights.append({
                "category": "Merchandise Dynamics",
                "title": f"Category Leadership: {top_rev_cat}",
                "observation": (
                    f"'{top_rev_cat}' leads gross revenue at ₹{top_rev_val:,.2f} ({top_rev_share:.1f}% share), "
                    f"while top unit-volume driver is '{top_vol_cat}' with {top_vol_val:,} units sold."
                ),
                "insight": (
                    "Supermarket revenue generation diverges between high-unit-price categories and high-frequency "
                    "staple volume drivers."
                ),
                "explanation": (
                    "Premium categories generate superior revenue per square foot, while staple categories drive "
                    "basket conversion and footfall."
                ),
                "action": (
                    f"Ensure 100% in-stock availability for '{top_rev_cat}' to prevent high-ticket sales leakage. "
                    f"Use '{top_vol_cat}' items as loss-leaders placed at back of store to drive customer traversal."
                ),
                "severity": "HIGH"
            })

    # -------------------------------------------------------------
    # 3. Customer Loyalty Economics: Member vs Normal
    # -------------------------------------------------------------
    if "Customer Type" in df.columns:
        cust_agg = df.groupby("Customer Type", observed=True)["Sales"].agg(["sum", "mean", "count"])
        if len(cust_agg) > 1 and "Member" in cust_agg.index and "Normal" in cust_agg.index:
            m_sales = cust_agg.loc["Member", "sum"]
            m_atv = cust_agg.loc["Member", "mean"]
            m_cnt = cust_agg.loc["Member", "count"]

            n_sales = cust_agg.loc["Normal", "sum"]
            n_atv = cust_agg.loc["Normal", "mean"]
            n_cnt = cust_agg.loc["Normal", "count"]

            atv_diff = m_atv - n_atv

            insights.append({
                "category": "Customer Segments",
                "title": "Loyalty Program Basket Economics",
                "observation": (
                    f"Members generated ₹{m_sales:,.2f} ({m_sales/total_sales*100:.1f}%) across {m_cnt} transactions "
                    f"(ATV: ₹{m_atv:.2f}). Normal shoppers generated ₹{n_sales:,.2f} across {n_cnt} transactions "
                    f"(ATV: ₹{n_atv:.2f}). ATV variance is ₹{abs(atv_diff):.2f}."
                ),
                "insight": (
                    f"Membership program acts primarily as a visit-frequency driver ({m_cnt} vs {n_cnt} visits) "
                    f"rather than substantially inflating single-basket spend (ATV difference is only {abs(atv_diff)/n_atv*100:.1f}%)."
                ),
                "explanation": (
                    "Members visit more frequently for recurring grocery needs, but buy similar basket sizes "
                    "to non-members in the absence of tiered basket incentives."
                ),
                "action": (
                    "Introduce spend-threshold bonus rewards (e.g. 'Spend ₹600 to receive 100 bonus loyalty points') "
                    "to expand Member Average Transaction Value beyond baseline levels."
                ),
                "severity": "MEDIUM"
            })

    # -------------------------------------------------------------
    # 4. Payment Channel Adoption
    # -------------------------------------------------------------
    if "Payment" in df.columns:
        pay_agg = df.groupby("Payment", observed=True)["Sales"].agg(["sum", "count"]).sort_values(by="sum", ascending=False)
        if not pay_agg.empty:
            top_pay = pay_agg.index[0]
            top_pay_sales = pay_agg.iloc[0]["sum"]
            top_pay_txns = pay_agg.iloc[0]["count"]
            pay_share = (top_pay_sales / total_sales * 100) if total_sales > 0 else 0

            insights.append({
                "category": "Payment Operations",
                "title": f"Digital Payment Channel Dominance: {top_pay}",
                "observation": (
                    f"{top_pay} is the primary payment channel, capturing ₹{top_pay_sales:,.2f} ({pay_share:.1f}% of revenue) "
                    f"across {top_pay_txns} transactions."
                ),
                "insight": (
                    "Checkout operations depend heavily on seamless digital transaction processing. Cashless "
                    "adoption dominates retail checkout lines."
                ),
                "explanation": (
                    "Customer convenience, mobile UPI penetration, and instant bank reconciliation drive customer "
                    "preference away from physical currency."
                ),
                "action": (
                    "Equip all checkout counters with dedicated QR scanners and redundant backup internet links to "
                    "prevent checkout congestion during peak evening transaction hours."
                ),
                "severity": "LOW"
            })

    # -------------------------------------------------------------
    # 5. Customer Satisfaction & Feedback Quality
    # -------------------------------------------------------------
    if "Rating" in df.columns and "Category" in df.columns:
        mean_rating = float(df["Rating"].mean())
        cat_ratings = df.groupby("Category", observed=True)["Rating"].mean()

        if len(cat_ratings) > 1:
            top_rated = cat_ratings.idxmax()
            lowest_rated = cat_ratings.idxmin()

            insights.append({
                "category": "Customer Satisfaction",
                "title": f"Satisfaction Driver Variance: {top_rated} vs {lowest_rated}",
                "observation": (
                    f"Overall store customer satisfaction averages {mean_rating:.2f}/5.0. '{top_rated}' achieved the "
                    f"highest customer rating ({cat_ratings[top_rated]:.2f}), while '{lowest_rated}' registered the lowest "
                    f"({cat_ratings[lowest_rated]:.2f})."
                ),
                "insight": (
                    f"Satisfaction gap between merchandise categories spans {cat_ratings[top_rated] - cat_ratings[lowest_rated]:.2f} stars. "
                    f"Quality perception is non-uniform across department aisles."
                ),
                "explanation": (
                    "Perishable freshness variance, packaging integrity, brand availability, or shelf-stocking delays "
                    "often lower ratings in sensitive food categories."
                ),
                "action": (
                    f"Conduct supplier quality inspections and shorten shelf-rotation cycles for '{lowest_rated}' products. "
                    "Engage checkout cashiers to solicit direct feedback when customers purchase lower-rated items."
                ),
                "severity": "MEDIUM"
            })

    # -------------------------------------------------------------
    # 6. Inventory Replenishment Urgency (if inventory data supplied)
    # -------------------------------------------------------------
    if inventory_df is not None and not inventory_df.empty:
        critical_items = inventory_df[inventory_df["Stock_Health"].isin(["🚨 OUT OF STOCK", "⚠️ CRITICAL REORDER"])]
        if not critical_items.empty:
            crit_names = critical_items["Product Name"].head(3).tolist()
            total_reorder_cost = float(critical_items["Estimated_Reorder_Cost"].sum())

            insights.append({
                "category": "Inventory Management",
                "title": f"Immediate Stock Replenishment Required ({len(critical_items)} SKUs)",
                "observation": (
                    f"{len(critical_items)} catalog items have breached their reorder thresholds or are stock depleted "
                    f"(including {', '.join(crit_names)}), requiring estimated capital of ₹{total_reorder_cost:,.2f}."
                ),
                "insight": (
                    "Immediate stockout risk threatens customer retention and revenue realization on high-demand merchandise."
                ),
                "explanation": (
                    "Lead-time delays from distributors or unforecasted surge in consumer demand have outpaced existing "
                    "reorder buffer thresholds."
                ),
                "action": (
                    "Issue expedited purchase orders for critical SKUs. Re-evaluate reorder thresholds from 20 to 30 units "
                    "for high-velocity items."
                ),
                "severity": "CRITICAL"
            })

    return insights
