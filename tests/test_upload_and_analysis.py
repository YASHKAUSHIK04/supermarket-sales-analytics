"""
Supermarket Sales & Customer Analytics - Automated Test Suite
Module: tests/test_upload_and_analysis.py

Tests:
1. Default dataset loading and KPI calculation
2. CSV upload ingestion with exact canonical columns
3. CSV upload with header alias detection and mapping
4. Excel upload (.xlsx) using openpyxl engine
5. Automatic Sales calculation when Sales column is missing
6. Automatic Unit Price calculation when Unit Price column is missing
7. Mathematical integrity check and discrepancy tracking
8. Schema validation failure when mandatory columns are omitted
9. Defensive handling in analytical insights for single-city datasets
10. Defensive handling for single-customer-type and non-standard customer types
11. Empty dataframe and edge cases across analytical and visualization functions
"""

import io
import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import (
    load_data,
    compute_kpis,
    analyze_sales_over_time,
    aggregate_by_dimension,
    analyze_customer_segments,
    analyze_product_performance,
    analyze_payments,
    analyze_ratings,
    generate_key_insights
)
from src.data_loader import (
    load_uploaded_file,
    detect_and_map_columns,
    validate_and_process_uploaded_data,
    CANONICAL_COLUMNS,
    CORE_MANDATORY_COLUMNS
)
from src.visualization import (
    plot_sales_trend,
    plot_bar,
    plot_donut,
    plot_scatter_quadrant,
    plot_rating_histogram,
    plot_grouped_bar
)


class TestSupermarketAnalytics(unittest.TestCase):
    """Exhaustive test suite for supermarket sales analytics & data ingestion."""

    @classmethod
    def setUpClass(cls):
        """Prepare sample test records."""
        cls.sample_data = {
            "Invoice ID": ["INV0001", "INV0002", "INV0003", "INV0004"],
            "Date": ["2026-01-15", "2026-02-20", "2026-03-10", "2026-04-05"],
            "Branch": ["A", "B", "C", "D"],
            "City": ["Jaipur", "Mumbai", "Delhi", "Bengaluru"],
            "Customer Type": ["Member", "Normal", "Member", "Normal"],
            "Gender": ["Female", "Male", "Female", "Male"],
            "Product": ["Milk", "Soap", "Rice", "Tea"],
            "Category": ["Dairy", "Personal Care", "Grocery", "Beverages"],
            "Quantity": [2, 5, 1, 4],
            "Unit Price": [60.0, 45.0, 120.0, 80.0],
            "Payment": ["UPI", "Card", "Cash", "Net Banking"],
            "Rating": [4.5, 4.0, 3.8, 4.9],
            "Sales": [120.0, 225.0, 120.0, 320.0]
        }
        cls.sample_df = pd.DataFrame(cls.sample_data)

    def test_default_dataset_integrity(self):
        """Test default processed dataset loads properly with 500 records and computes KPIs."""
        df = load_data()
        self.assertEqual(len(df), 500)
        self.assertIn("Sales", df.columns)
        self.assertIn("Rating", df.columns)

        kpis = compute_kpis(df)
        self.assertGreater(kpis["total_sales"], 0)
        self.assertGreater(kpis["total_quantity"], 0)
        self.assertEqual(kpis["total_transactions"], 500)
        self.assertGreaterEqual(kpis["avg_rating"], 1.0)
        self.assertLessEqual(kpis["avg_rating"], 5.0)

    def test_csv_upload_exact_columns(self):
        """Test parsing and validating a CSV file with exact canonical columns."""
        csv_buffer = io.BytesIO()
        self.sample_df.to_csv(csv_buffer, index=False)
        csv_buffer.name = "test_sales.csv"
        csv_buffer.seek(0)

        df_raw = load_uploaded_file(csv_buffer)
        self.assertEqual(len(df_raw), 4)

        df_processed, summary = validate_and_process_uploaded_data(df_raw)
        self.assertTrue(summary["is_valid"])
        self.assertEqual(len(df_processed), 4)
        self.assertEqual(summary["math_discrepancy_count"], 0)
        self.assertIn("Year", df_processed.columns)
        self.assertIn("Day_Of_Week", df_processed.columns)

    def test_csv_upload_aliased_columns(self):
        """Test automatic header alias detection and mapping."""
        aliased_df = pd.DataFrame({
            "order_id": ["ORD-101", "ORD-102"],
            "txn_date": ["2026-05-01", "2026-05-02"],
            "store": ["Store East", "Store West"],
            "location": ["Pune", "Kolkata"],
            "membership": ["Gold", "Silver"],
            "sex": ["Female", "Male"],
            "item_name": ["Cooking Oil", "Biscuits"],
            "merchandise group": ["Grocery", "Snacks"],
            "qty": [3, 2],
            "rate": [150.0, 30.0],
            "mode": ["UPI", "Card"],
            "csat": [4.8, 4.2],
            "total_amount": [450.0, 60.0]
        })

        mapping = detect_and_map_columns(list(aliased_df.columns))
        self.assertEqual(mapping["Invoice ID"], "order_id")
        self.assertEqual(mapping["Date"], "txn_date")
        self.assertEqual(mapping["Branch"], "store")
        self.assertEqual(mapping["City"], "location")
        self.assertEqual(mapping["Customer Type"], "membership")
        self.assertEqual(mapping["Gender"], "sex")
        self.assertEqual(mapping["Product"], "item_name")
        self.assertEqual(mapping["Category"], "merchandise group")
        self.assertEqual(mapping["Quantity"], "qty")
        self.assertEqual(mapping["Unit Price"], "rate")
        self.assertEqual(mapping["Payment"], "mode")
        self.assertEqual(mapping["Rating"], "csat")
        self.assertEqual(mapping["Sales"], "total_amount")

        df_processed, summary = validate_and_process_uploaded_data(aliased_df, column_mapping=mapping)
        self.assertTrue(summary["is_valid"])
        self.assertEqual(len(df_processed), 2)
        self.assertEqual(df_processed["Sales"].sum(), 510.0)

    def test_excel_upload_xlsx(self):
        """Test Excel .xlsx ingestion using openpyxl engine."""
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            self.sample_df.to_excel(writer, index=False, sheet_name="Transactions")
        excel_buffer.name = "sample_data.xlsx"
        excel_buffer.seek(0)

        df_excel = load_uploaded_file(excel_buffer)
        self.assertEqual(len(df_excel), 4)

        df_processed, summary = validate_and_process_uploaded_data(df_excel)
        self.assertTrue(summary["is_valid"])
        self.assertEqual(summary["final_rows"], 4)

    def test_missing_sales_auto_calculation(self):
        """Test that Sales is automatically calculated if omitted."""
        df_no_sales = self.sample_df.drop(columns=["Sales"]).copy()
        df_processed, summary = validate_and_process_uploaded_data(df_no_sales)

        self.assertTrue(summary["is_valid"])
        self.assertIn("Sales", df_processed.columns)
        # 2*60=120, 5*45=225, 1*120=120, 4*80=320 -> Total = 785
        self.assertEqual(df_processed["Sales"].sum(), 785.0)

    def test_missing_unit_price_auto_calculation(self):
        """Test that Unit Price is automatically calculated if omitted."""
        df_no_price = self.sample_df.drop(columns=["Unit Price"]).copy()
        df_processed, summary = validate_and_process_uploaded_data(df_no_price)

        self.assertTrue(summary["is_valid"])
        self.assertIn("Unit Price", df_processed.columns)
        self.assertEqual(df_processed.loc[0, "Unit Price"], 60.0)

    def test_math_discrepancy_detection(self):
        """Test detection and tracking of discrepancies when Sales != Quantity * Unit Price."""
        df_disc = self.sample_df.copy()
        df_disc.loc[0, "Sales"] = 999.0  # expected 2 * 60 = 120.0

        df_processed, summary = validate_and_process_uploaded_data(df_disc)
        self.assertTrue(summary["is_valid"])
        self.assertEqual(summary["math_discrepancy_count"], 1)
        self.assertAlmostEqual(summary["max_math_discrepancy"], 879.0, places=1)
        self.assertTrue(any("discrepancy" in w.lower() for w in summary["warnings"]))

    def test_missing_required_columns(self):
        """Test graceful validation failure when core mandatory columns are missing."""
        df_missing_cat = self.sample_df.drop(columns=["Category"]).copy()
        df_processed, summary = validate_and_process_uploaded_data(df_missing_cat)

        self.assertFalse(summary["is_valid"])
        self.assertTrue(len(summary["errors"]) > 0)
        self.assertIn("Category", summary["missing_mandatory"])
        self.assertTrue(df_processed.empty)

    def test_defensive_insights_single_city(self):
        """Verify insight generation does not crash when all rows belong to 1 city."""
        df_single_city = self.sample_df.copy()
        df_single_city["City"] = "Bengaluru"

        insights = generate_key_insights(df_single_city)
        self.assertIsInstance(insights, list)
        self.assertTrue(len(insights) > 0)
        city_insights = [i for i in insights if i["category"] == "Geographic Performance"]
        self.assertEqual(len(city_insights), 1)
        self.assertIn("Bengaluru", city_insights[0]["insight"])

    def test_defensive_insights_custom_customer_types(self):
        """Verify customer segmentation insights work with arbitrary customer types."""
        df_custom_types = self.sample_df.copy()
        df_custom_types["Customer Type"] = ["VIP", "Standard", "VIP", "Standard"]

        insights = generate_key_insights(df_custom_types)
        self.assertIsInstance(insights, list)
        cust_insights = [i for i in insights if i["category"] == "Customer Segments"]
        self.assertEqual(len(cust_insights), 1)
        self.assertIn("VIP", cust_insights[0]["insight"])

    def test_empty_dataframe_handling(self):
        """Verify all analytical and visualization functions gracefully handle empty DataFrames."""
        empty_df = pd.DataFrame()

        # KPIs
        kpis = compute_kpis(empty_df)
        self.assertEqual(kpis["total_sales"], 0.0)
        self.assertEqual(kpis["total_transactions"], 0)

        # Insights
        insights = generate_key_insights(empty_df)
        self.assertEqual(len(insights), 1)
        self.assertEqual(insights[0]["category"], "No Data")

        # Time analysis
        df_time = analyze_sales_over_time(empty_df, freq="M")
        self.assertTrue(df_time.empty)

        # Plot functions
        fig1 = plot_sales_trend(empty_df)
        fig2 = plot_bar(empty_df, x_col="City", y_col="Sales", title="Empty Bar")
        fig3 = plot_donut(empty_df, names_col="City", values_col="Sales", title="Empty Donut")
        fig4 = plot_scatter_quadrant(empty_df)
        fig5 = plot_rating_histogram(empty_df)
        fig6 = plot_grouped_bar(empty_df, x_col="Customer Type", y_col="Sales", color_col="Gender", title="Empty")

        for fig in [fig1, fig2, fig3, fig4, fig5, fig6]:
            self.assertIsNotNone(fig)


if __name__ == "__main__":
    unittest.main()
