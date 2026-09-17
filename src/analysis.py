"""
Supermarket Sales & Customer Analytics - Core Analytical Engine
Module: src/analysis.py

Provides modular computation functions for:
- Executive KPIs
- Temporal sales trends
- Dimensional aggregations (City, Branch, Category, Product)
- Customer demographic & behavioral segmentation
- Payment method adoption & ticket size
- Customer satisfaction / rating patterns
- Data-driven business insights generation
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "supermarket_sales_cleaned.csv"


def load_data(filepath: Optional[Path] = None) -> pd.DataFrame:
    """Load cleaned supermarket dataset."""
    path = filepath or CLEANED_CSV_PATH
    if not Path(path).exists():
        raise FileNotFoundError(f"Cleaned dataset not found at: {path}. Run data_cleaning.py first.")
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute top-level executive KPIs."""
    if df.empty:
        return {
            "total_sales": 0.0,
            "total_quantity": 0,
            "total_transactions": 0,
            "avg_transaction_value": 0.0,
            "avg_rating": 0.0,
            "unique_products": 0,
            "unique_categories": 0,
        }

    return {
        "total_sales": float(df["Sales"].sum()),
        "total_quantity": int(df["Quantity"].sum()),
        "total_transactions": int(len(df)),
        "avg_transaction_value": float(df["Sales"].mean()),
        "avg_rating": float(df["Rating"].mean()),
        "unique_products": int(df["Product"].nunique()),
        "unique_categories": int(df["Category"].nunique()),
    }


def analyze_sales_over_time(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """Aggregate sales and transaction metrics over time."""
    if df.empty:
        return pd.DataFrame()

    if freq == "M":
        grouped = df.groupby(pd.Grouper(key="Date", freq="ME")).agg(
            Sales=("Sales", "sum"),
            Quantity=("Quantity", "sum"),
            Transactions=("Invoice ID", "count"),
            Avg_Order_Value=("Sales", "mean"),
            Avg_Rating=("Rating", "mean")
        ).reset_index()
        grouped["Period"] = grouped["Date"].dt.strftime("%b %Y")
        return grouped
    elif freq == "D":
        grouped = df.groupby("Date").agg(
            Sales=("Sales", "sum"),
            Quantity=("Quantity", "sum"),
            Transactions=("Invoice ID", "count"),
            Avg_Order_Value=("Sales", "mean")
        ).reset_index()
        return grouped
    elif freq == "Day_Of_Week":
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        grouped = df.groupby("Day_Of_Week").agg(
            Sales=("Sales", "sum"),
            Quantity=("Quantity", "sum"),
            Transactions=("Invoice ID", "count"),
            Avg_Order_Value=("Sales", "mean")
        ).reindex(days_order).reset_index()
        return grouped
    else:
        raise ValueError(f"Unsupported frequency: {freq}")


def aggregate_by_dimension(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """Aggregate core metrics by specified categorical dimension."""
    if df.empty or dimension not in df.columns:
        return pd.DataFrame()

    agg = df.groupby(dimension, observed=True).agg(
        Sales=("Sales", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Unit_Price=("Unit Price", "mean"),
        Avg_Order_Value=("Sales", "mean"),
        Avg_Rating=("Rating", "mean")
    ).reset_index()

    total_sales = df["Sales"].sum()
    agg["Sales_Share_Pct"] = (agg["Sales"] / total_sales * 100).round(2) if total_sales > 0 else 0
    return agg.sort_values(by="Sales", ascending=False)


def analyze_customer_segments(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Analyze customer behavior by Customer Type, Gender, and their combination."""
    if df.empty:
        return {}

    by_type = df.groupby("Customer Type", observed=True).agg(
        Sales=("Sales", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Order_Value=("Sales", "mean"),
        Avg_Rating=("Rating", "mean")
    ).reset_index()
    by_type["Sales_Share_Pct"] = (by_type["Sales"] / df["Sales"].sum() * 100).round(2)

    by_gender = df.groupby("Gender", observed=True).agg(
        Sales=("Sales", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Order_Value=("Sales", "mean"),
        Avg_Rating=("Rating", "mean")
    ).reset_index()
    by_gender["Sales_Share_Pct"] = (by_gender["Sales"] / df["Sales"].sum() * 100).round(2)

    combo = df.groupby(["Customer Type", "Gender"], observed=True).agg(
        Sales=("Sales", "sum"),
        Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Order_Value=("Sales", "mean"),
        Avg_Rating=("Rating", "mean")
    ).reset_index()
    combo["Sales_Share_Pct"] = (combo["Sales"] / df["Sales"].sum() * 100).round(2)

    return {
        "by_type": by_type,
        "by_gender": by_gender,
        "combination": combo
    }


def analyze_product_performance(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Analyze product level performance: Revenue vs Volume vs Customer Satisfaction."""
    if df.empty:
        return {}

    prod_summary = df.groupby(["Product", "Category"], observed=True).agg(
        Total_Sales=("Sales", "sum"),
        Total_Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Unit_Price=("Unit Price", "mean"),
        Avg_Rating=("Rating", "mean")
    ).reset_index()

    top_revenue = prod_summary.sort_values(by="Total_Sales", ascending=False).reset_index(drop=True)
    top_volume = prod_summary.sort_values(by="Total_Quantity", ascending=False).reset_index(drop=True)
    top_rating = prod_summary.sort_values(by="Avg_Rating", ascending=False).reset_index(drop=True)

    cat_summary = df.groupby("Category", observed=True).agg(
        Total_Sales=("Sales", "sum"),
        Total_Quantity=("Quantity", "sum"),
        Transactions=("Invoice ID", "count"),
        Avg_Unit_Price=("Unit Price", "mean"),
        Avg_Rating=("Rating", "mean")
    ).reset_index().sort_values(by="Total_Sales", ascending=False)

    return {
        "summary": prod_summary,
        "top_revenue": top_revenue,
        "top_volume": top_volume,
        "top_rating": top_rating,
        "category_summary": cat_summary
    }


def analyze_payments(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Analyze payment method usage and customer preferences."""
    if df.empty:
        return {}

    pay_summary = df.groupby("Payment", observed=True).agg(
        Total_Sales=("Sales", "sum"),
        Transactions=("Invoice ID", "count"),
        Total_Quantity=("Quantity", "sum"),
        Avg_Transaction_Value=("Sales", "mean"),
        Avg_Rating=("Rating", "mean")
    ).reset_index()
    pay_summary["Sales_Share_Pct"] = (pay_summary["Total_Sales"] / df["Sales"].sum() * 100).round(2)
    pay_summary["Txn_Share_Pct"] = (pay_summary["Transactions"] / len(df) * 100).round(2)
    pay_summary = pay_summary.sort_values(by="Total_Sales", ascending=False)

    pref_cross = pd.crosstab(
        df["Customer Type"],
        df["Payment"],
        normalize="index"
    ) * 100

    return {
        "summary": pay_summary,
        "crosstab_pct": pref_cross.round(2)
    }


def analyze_ratings(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze customer ratings and satisfaction across categories, cities, and types."""
    if df.empty:
        return {}

    by_cat = df.groupby("Category", observed=True)["Rating"].agg(["mean", "std", "count"]).reset_index()
    by_cat.columns = ["Category", "Mean_Rating", "Std_Rating", "Reviews_Count"]
    by_cat = by_cat.sort_values(by="Mean_Rating", ascending=False)

    by_city = df.groupby("City", observed=True)["Rating"].agg(["mean", "count"]).reset_index()
    by_city.columns = ["City", "Mean_Rating", "Reviews_Count"]
    by_city = by_city.sort_values(by="Mean_Rating", ascending=False)

    by_type = df.groupby("Customer Type", observed=True)["Rating"].agg(["mean", "count"]).reset_index()
    by_type.columns = ["Customer Type", "Mean_Rating", "Reviews_Count"]

    return {
        "overall_mean": float(df["Rating"].mean()),
        "overall_median": float(df["Rating"].median()),
        "by_category": by_cat,
        "by_city": by_city,
        "by_customer_type": by_type
    }


def generate_key_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Derive verifiable, empirical business insights directly from dataset calculations."""
    if df.empty:
        return [{"category": "No Data", "title": "Empty Dataset", "insight": "No data available for the current filter criteria."}]

    insights = []

    # 1. Category Leader
    cat_sales = df.groupby("Category", observed=True)["Sales"].sum()
    top_cat = cat_sales.idxmax()
    top_cat_sales = cat_sales.max()
    top_cat_share = (top_cat_sales / df["Sales"].sum()) * 100
    insights.append({
        "category": "Revenue Driver",
        "title": f"Leading Category: {top_cat}",
        "insight": f"{top_cat} generated Rs. {top_cat_sales:,.2f} ({top_cat_share:.1f}% of total revenue), making it the single largest category by gross sales."
    })

    # 2. Product Volume vs Value
    prod_rev = df.groupby("Product", observed=True)["Sales"].sum()
    prod_vol = df.groupby("Product", observed=True)["Quantity"].sum()
    top_rev_prod = prod_rev.idxmax()
    top_vol_prod = prod_vol.idxmax()
    insights.append({
        "category": "Product Dynamics",
        "title": "Revenue vs Volume Divergence",
        "insight": f"Top revenue product is '{top_rev_prod}' (Rs. {prod_rev[top_rev_prod]:,.2f}), whereas top quantity volume product is '{top_vol_prod}' ({prod_vol[top_vol_prod]} units sold). High unit prices drive revenue independently of unit sales volume."
    })

    # 3. Customer Type Comparison
    cust_sales = df.groupby("Customer Type", observed=True)["Sales"].agg(["sum", "mean", "count"])
    if len(cust_sales) > 1:
        member_atv = cust_sales.loc["Member", "mean"]
        normal_atv = cust_sales.loc["Normal", "mean"]
        member_sales = cust_sales.loc["Member", "sum"]
        normal_sales = cust_sales.loc["Normal", "sum"]
        diff_atv = member_atv - normal_atv
        insights.append({
            "category": "Customer Segments",
            "title": "Member vs Normal Spending Behavior",
            "insight": f"Members generated Rs. {member_sales:,.2f} across {cust_sales.loc['Member', 'count']} transactions (ATV: Rs. {member_atv:.2f}), while Normal customers generated Rs. {normal_sales:,.2f} across {cust_sales.loc['Normal', 'count']} transactions (ATV: Rs. {normal_atv:.2f}). ATV difference is Rs. {abs(diff_atv):.2f}."
        })

    # 4. City & Branch Sales
    city_sales = df.groupby("City", observed=True)["Sales"].sum()
    top_city = city_sales.idxmax()
    lowest_city = city_sales.idxmin()
    insights.append({
        "category": "Geographic Performance",
        "title": f"City Performance Spread",
        "insight": f"{top_city} is the highest revenue market with Rs. {city_sales[top_city]:,.2f} ({city_sales[top_city]/df['Sales'].sum()*100:.1f}%), compared to {lowest_city} at Rs. {city_sales[lowest_city]:,.2f} ({city_sales[lowest_city]/df['Sales'].sum()*100:.1f}%)."
    })

    # 5. Payment Channel Preferences
    pay_sales = df.groupby("Payment", observed=True)["Sales"].sum()
    pay_txns = df.groupby("Payment", observed=True)["Invoice ID"].count()
    top_pay_method = pay_sales.idxmax()
    top_pay_txns = pay_txns.idxmax()
    insights.append({
        "category": "Payment Analysis",
        "title": f"Payment Dominance: {top_pay_method}",
        "insight": f"{top_pay_method} accounted for the highest sales volume at Rs. {pay_sales[top_pay_method]:,.2f} ({pay_sales[top_pay_method]/df['Sales'].sum()*100:.1f}% share) and {pay_txns[top_pay_method]} transactions."
    })

    # 6. Customer Satisfaction
    cat_ratings = df.groupby("Category", observed=True)["Rating"].mean()
    top_rated_cat = cat_ratings.idxmax()
    lowest_rated_cat = cat_ratings.idxmin()
    insights.append({
        "category": "Customer Satisfaction",
        "title": "Rating Spread Across Categories",
        "insight": f"Average customer rating is {df['Rating'].mean():.2f}/5.0. '{top_rated_cat}' achieved the highest average rating ({cat_ratings[top_rated_cat]:.2f}), while '{lowest_rated_cat}' recorded the lowest ({cat_ratings[lowest_rated_cat]:.2f})."
    })

    return insights
