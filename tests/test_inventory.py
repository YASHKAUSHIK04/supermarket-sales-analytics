"""
Supermarket Sales & Customer Analytics - Inventory Automated Test Suite
Module: tests/test_inventory.py

Tests:
1. Inventory intelligence calculation on catalog and historical sales
2. Sales velocity and days-remaining estimation
3. Velocity classification (Fast-Moving vs Slow-Moving)
4. Stock health badge assignments and low-stock flagging
5. Suggested replenishment quantities and investment calculation
6. Inventory KPI rollups (valuation, stockout count, reorder capital)
7. Safe sales-to-inventory deduction with overdraft prevention
"""

import sys
import unittest
from pathlib import Path
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import (
    init_database,
    seed_database_if_empty,
    get_products_df,
    create_product,
    record_stock_movement
)
from src.inventory import (
    calculate_inventory_intelligence,
    get_inventory_summary_kpis,
    reconcile_sales_deduction
)


class TestInventoryIntelligence(unittest.TestCase):
    """Test suite for retail inventory intelligence and stock ledger logic."""

    def setUp(self):
        """Set up an isolated temporary database with seed data."""
        self.test_dir = PROJECT_ROOT / "tests" / "temp"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.test_dir / "test_inventory.db"
        if self.db_path.exists():
            self.db_path.unlink()
        init_database(self.db_path)
        seed_database_if_empty(self.db_path)

        # Create mock 30-day sales data
        self.mock_sales = pd.DataFrame({
            "Invoice ID": [f"INV-{i}" for i in range(1, 11)],
            "Date": ["2026-06-15"] * 5 + ["2026-06-25"] * 5,
            "Branch": ["Branch A"] * 10,
            "City": ["Jaipur"] * 10,
            "Customer Type": ["Member"] * 10,
            "Gender": ["Female"] * 10,
            "Product": ["Milk"] * 5 + ["Bread"] * 3 + ["Cheese"] * 2,
            "Category": ["Dairy"] * 5 + ["Bakery"] * 3 + ["Dairy"] * 2,
            "Quantity": [10, 8, 12, 10, 10, 4, 3, 3, 2, 3],  # Milk: 50 units, Bread: 10 units, Cheese: 5 units
            "Unit Price": [60.0] * 5 + [40.0] * 3 + [220.0] * 2,
            "Sales": [600.0, 480.0, 720.0, 600.0, 600.0, 160.0, 120.0, 120.0, 440.0, 660.0],
            "Payment": ["UPI"] * 10,
            "Rating": [4.5] * 10
        })

    def tearDown(self):
        """Clean up temporary test database."""
        if self.db_path.exists():
            try:
                self.db_path.unlink()
            except Exception:
                pass

    def test_calculate_inventory_intelligence(self):
        """Verify sales velocity and days-remaining calculations."""
        prods_df = get_products_df(active_only=True, db_path=self.db_path)
        self.assertGreater(len(prods_df), 0)

        intel_df = calculate_inventory_intelligence(prods_df, self.mock_sales, lookback_days=30)
        self.assertEqual(len(intel_df), len(prods_df))

        # Check Milk metrics (50 units sold over ~11 days in window -> daily velocity ~4.5)
        milk_row = intel_df[intel_df["Product Name"] == "Milk"].iloc[0]
        self.assertEqual(milk_row["Units_Sold"], 50)
        self.assertGreater(milk_row["Avg_Daily_Sales"], 1.0)
        self.assertEqual(milk_row["Velocity_Classification"], "Fast-Moving")

        # Check Dormant product (e.g., Cooking Oil has 0 units in mock sales)
        oil_row = intel_df[intel_df["Product Name"] == "Cooking Oil"].iloc[0]
        self.assertEqual(oil_row["Units_Sold"], 0)
        self.assertEqual(oil_row["Avg_Daily_Sales"], 0.0)
        self.assertEqual(oil_row["Velocity_Classification"], "Dormant (No Sales)")
        self.assertEqual(oil_row["Days_Stock_Remaining"], 999.0)

    def test_stock_health_and_reorder_flags(self):
        """Verify low-stock and out-of-stock health flags."""
        prods_df = get_products_df(active_only=True, db_path=self.db_path)

        # Manually set a product's stock to 10 (below reorder threshold 20)
        bread_id = prods_df[prods_df["Product Name"] == "Bread"].iloc[0]["Product ID"]
        current_bread_stock = prods_df[prods_df["Product Name"] == "Bread"].iloc[0]["Current Stock"]
        record_stock_movement(
            product_id=bread_id,
            movement_type="ADJUSTMENT_SUB",
            quantity_change=-(current_bread_stock - 10),
            reference_note="Reduce for low-stock test",
            db_path=self.db_path
        )

        updated_prods = get_products_df(active_only=True, db_path=self.db_path)
        intel_df = calculate_inventory_intelligence(updated_prods, self.mock_sales, lookback_days=30)

        bread_intel = intel_df[intel_df["Product Name"] == "Bread"].iloc[0]
        self.assertEqual(bread_intel["Current Stock"], 10)
        self.assertEqual(bread_intel["Stock_Health"], "⚠️ CRITICAL REORDER")
        # Target stock is 100, current is 10 -> suggested reorder = 90
        self.assertEqual(bread_intel["Suggested_Reorder_Qty"], 90)
        self.assertGreater(bread_intel["Estimated_Reorder_Cost"], 0)

    def test_inventory_summary_kpis(self):
        """Verify aggregated inventory KPI values."""
        prods_df = get_products_df(active_only=True, db_path=self.db_path)
        intel_df = calculate_inventory_intelligence(prods_df, self.mock_sales, lookback_days=30)

        kpis = get_inventory_summary_kpis(intel_df)
        self.assertGreaterEqual(kpis["total_skus"], 20)
        self.assertGreater(kpis["total_units"], 0)
        self.assertGreater(kpis["valuation"], 0.0)
        self.assertIsInstance(kpis["critical_reorder"], int)

    def test_reconcile_sales_deduction_safe(self):
        """Test controlled stock deduction against sales demand."""
        # Create a small sales batch for Milk (10 units) and Bread (5 units)
        deduct_batch = pd.DataFrame({
            "Product": ["Milk", "Bread"],
            "Quantity": [10, 5]
        })

        prods_before = get_products_df(active_only=True, db_path=self.db_path)
        milk_stock_before = prods_before[prods_before["Product Name"] == "Milk"].iloc[0]["Current Stock"]
        bread_stock_before = prods_before[prods_before["Product Name"] == "Bread"].iloc[0]["Current Stock"]

        result = reconcile_sales_deduction(deduct_batch, db_path=self.db_path)
        self.assertTrue(result["success"])
        self.assertEqual(result["deducted_items"], 2)

        prods_after = get_products_df(active_only=True, db_path=self.db_path)
        milk_stock_after = prods_after[prods_after["Product Name"] == "Milk"].iloc[0]["Current Stock"]
        bread_stock_after = prods_after[prods_after["Product Name"] == "Bread"].iloc[0]["Current Stock"]

        self.assertEqual(milk_stock_after, milk_stock_before - 10)
        self.assertEqual(bread_stock_after, bread_stock_before - 5)

    def test_reconcile_sales_deduction_shortfall_abort(self):
        """Test that excessive deduction aborts safely without corrupting stock."""
        # Request 9999 units of Milk (far exceeding stock)
        excess_batch = pd.DataFrame({
            "Product": ["Milk"],
            "Quantity": [9999]
        })

        prods_before = get_products_df(active_only=True, db_path=self.db_path)
        milk_stock_before = prods_before[prods_before["Product Name"] == "Milk"].iloc[0]["Current Stock"]

        result = reconcile_sales_deduction(excess_batch, allow_partial=False, db_path=self.db_path)
        self.assertFalse(result["success"])
        self.assertGreater(len(result["shortfalls"]), 0)

        prods_after = get_products_df(active_only=True, db_path=self.db_path)
        milk_stock_after = prods_after[prods_after["Product Name"] == "Milk"].iloc[0]["Current Stock"]
        self.assertEqual(milk_stock_after, milk_stock_before)  # Stock untouched


if __name__ == "__main__":
    unittest.main()
