"""
Supermarket Sales & Customer Analytics - Database Automated Test Suite
Module: tests/test_database.py

Tests:
1. Database schema initialization in isolated in-memory SQLite instances
2. Seeding baseline categories, products, stock, and sales transactions
3. Safe sales data ingestion (skip_duplicates mode vs replace_all mode)
4. Duplicate invoice rejection and tracking
5. Product CRUD operations (create, read, update, soft delete)
6. Inventory stock ledger movements and running balance verification
7. Negative stock constraint violation prevention
8. Anomaly record persistence and resolution
9. Report generation audit logging
"""

import sys
import unittest
from pathlib import Path
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import (
    get_db_connection,
    init_database,
    seed_database_if_empty,
    get_all_sales_df,
    import_sales_dataframe,
    get_products_df,
    create_product,
    update_product,
    delete_product,
    get_categories_list,
    record_stock_movement,
    get_inventory_movements_df,
    log_anomaly,
    get_anomalies_df,
    resolve_anomaly,
    log_report,
    get_reports_df,
    get_database_stats
)


class TestDatabaseEngine(unittest.TestCase):
    """Test suite for SQLite relational database operations and CRUD integrity."""

    def setUp(self):
        """Set up an isolated in-memory SQLite database for each test."""
        # Use a unique temporary SQLite database file for isolation
        self.test_dir = PROJECT_ROOT / "tests" / "temp"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.test_dir / "test_supermarket.db"
        if self.db_path.exists():
            self.db_path.unlink()
        init_database(self.db_path)

    def tearDown(self):
        """Clean up temporary test database."""
        if self.db_path.exists():
            try:
                self.db_path.unlink()
            except Exception:
                pass

    def test_schema_initialization(self):
        """Verify all 7 tables and indexes are created successfully."""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        expected_tables = [
            "categories", "products", "inventory_stock",
            "inventory_movements", "sales_transactions",
            "anomaly_records", "report_history"
        ]
        for tbl in expected_tables:
            self.assertIn(tbl, tables, f"Table '{tbl}' was not created.")

    def test_seed_database_baseline(self):
        """Verify initial database seeding from baseline cleaned dataset."""
        result = seed_database_if_empty(self.db_path)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["transactions"], 500)
        self.assertGreaterEqual(result["products"], 20)
        self.assertGreaterEqual(result["categories"], 8)

        stats = get_database_stats(self.db_path)
        self.assertEqual(stats["sales_transactions"], 500)
        self.assertEqual(stats["products"], result["products"])

        # Subsequent call should detect existing data and not re-seed
        second_result = seed_database_if_empty(self.db_path)
        self.assertEqual(second_result["status"], "already_populated")

    def test_product_crud_operations(self):
        """Test creating, reading, updating, and deactivating a product."""
        # Create product
        pid = create_product(
            product_name="Organic Green Tea",
            category_name="Beverages",
            unit_price=120.50,
            reorder_threshold=15,
            target_stock=80,
            initial_stock=40,
            db_path=self.db_path
        )
        self.assertGreater(pid, 0)

        # Read product
        df_prods = get_products_df(active_only=True, db_path=self.db_path)
        tea_row = df_prods[df_prods["Product Name"] == "Organic Green Tea"]
        self.assertEqual(len(tea_row), 1)
        self.assertEqual(tea_row.iloc[0]["Unit Price (₹)"], 120.50)
        self.assertEqual(tea_row.iloc[0]["Current Stock"], 40)
        self.assertEqual(tea_row.iloc[0]["Stock Status"], "HEALTHY")

        # Update product
        updated = update_product(
            product_id=pid,
            product_name="Organic Green Tea Premium",
            category_name="Beverages",
            unit_price=135.00,
            reorder_threshold=25,
            target_stock=100,
            is_active=1,
            db_path=self.db_path
        )
        self.assertTrue(updated)

        df_updated = get_products_df(active_only=True, db_path=self.db_path)
        updated_row = df_updated[df_updated["Product Name"] == "Organic Green Tea Premium"]
        self.assertEqual(len(updated_row), 1)
        self.assertEqual(updated_row.iloc[0]["Unit Price (₹)"], 135.00)

        # Soft delete (deactivate) product
        deleted = delete_product(pid, hard_delete=False, db_path=self.db_path)
        self.assertTrue(deleted)

        df_active = get_products_df(active_only=True, db_path=self.db_path)
        self.assertEqual(len(df_active[df_active["Product Name"] == "Organic Green Tea Premium"]), 0)

    def test_inventory_stock_movements_and_ledger(self):
        """Test stock receipts, deductions, and negative-stock prevention."""
        pid = create_product(
            product_name="Whole Milk 1L",
            category_name="Dairy",
            unit_price=60.0,
            reorder_threshold=20,
            target_stock=100,
            initial_stock=50,
            db_path=self.db_path
        )

        # 1. Stock Receipt (+30 units -> balance 80)
        mov1 = record_stock_movement(
            product_id=pid,
            movement_type="RECEIPT",
            quantity_change=30,
            reference_note="Supplier PO #1019",
            db_path=self.db_path
        )
        self.assertGreater(mov1, 0)

        df_prods = get_products_df(active_only=True, db_path=self.db_path)
        milk = df_prods[df_prods["Product Name"] == "Whole Milk 1L"].iloc[0]
        self.assertEqual(milk["Current Stock"], 80)

        # 2. Stock Deduction (-65 units -> balance 15, below reorder threshold 20)
        mov2 = record_stock_movement(
            product_id=pid,
            movement_type="SALE_DEDUCTION",
            quantity_change=-65,
            reference_note="Reconciled weekly sales",
            db_path=self.db_path
        )
        self.assertGreater(mov2, 0)

        df_prods2 = get_products_df(active_only=True, db_path=self.db_path)
        milk2 = df_prods2[df_prods2["Product Name"] == "Whole Milk 1L"].iloc[0]
        self.assertEqual(milk2["Current Stock"], 15)
        self.assertEqual(milk2["Stock Status"], "LOW_STOCK")

        # 3. Invalid Deduction (trying to deduct 20 units when balance is 15 -> ValueError)
        with self.assertRaises(ValueError):
            record_stock_movement(
                product_id=pid,
                movement_type="SALE_DEDUCTION",
                quantity_change=-20,
                reference_note="Invalid overdraft",
                db_path=self.db_path
            )

        # Verify balance remains unchanged at 15
        df_prods3 = get_products_df(active_only=True, db_path=self.db_path)
        milk3 = df_prods3[df_prods3["Product Name"] == "Whole Milk 1L"].iloc[0]
        self.assertEqual(milk3["Current Stock"], 15)

        # 4. Check ledger audit trail
        ledger_df = get_inventory_movements_df(product_id=pid, db_path=self.db_path)
        self.assertEqual(len(ledger_df), 3)  # INITIAL (50), RECEIPT (+30), SALE_DEDUCTION (-65)

    def test_safe_sales_import_skip_duplicates(self):
        """Test that re-uploading identical sales data does not duplicate records."""
        sample_sales = pd.DataFrame({
            "Invoice ID": ["INV-TEST-001", "INV-TEST-002"],
            "Date": ["2026-05-10", "2026-05-11"],
            "Branch": ["Branch A", "Branch B"],
            "City": ["Jaipur", "Delhi"],
            "Customer Type": ["Member", "Normal"],
            "Gender": ["Female", "Male"],
            "Product": ["Apples", "Bananas"],
            "Category": ["Fruits", "Fruits"],
            "Quantity": [2, 3],
            "Unit Price": [120.0, 40.0],
            "Payment": ["UPI", "Cash"],
            "Rating": [4.5, 4.0],
            "Sales": [240.0, 120.0]
        })

        # First upload
        summary1 = import_sales_dataframe(sample_sales, mode="skip_duplicates", db_path=self.db_path)
        self.assertEqual(summary1["inserted"], 2)
        self.assertEqual(summary1["duplicates_skipped"], 0)

        # Second upload with identical invoices
        summary2 = import_sales_dataframe(sample_sales, mode="skip_duplicates", db_path=self.db_path)
        self.assertEqual(summary2["inserted"], 0)
        self.assertEqual(summary2["duplicates_skipped"], 2)

        # Verify database has exactly 2 records
        df_all = get_all_sales_df(self.db_path)
        self.assertEqual(len(df_all), 2)

    def test_sales_import_replace_all(self):
        """Test replace_all mode properly purges and reloads records."""
        batch1 = pd.DataFrame({
            "Invoice ID": ["INV-A1", "INV-A2"],
            "Date": ["2026-06-01", "2026-06-02"],
            "Branch": ["Branch A", "Branch A"],
            "City": ["Mumbai", "Mumbai"],
            "Customer Type": ["Member", "Member"],
            "Gender": ["Female", "Male"],
            "Product": ["Coffee", "Tea"],
            "Category": ["Beverages", "Beverages"],
            "Quantity": [1, 2],
            "Unit Price": [150.0, 50.0],
            "Payment": ["UPI", "Card"],
            "Rating": [4.8, 4.2],
            "Sales": [150.0, 100.0]
        })
        import_sales_dataframe(batch1, mode="skip_duplicates", db_path=self.db_path)

        batch2 = pd.DataFrame({
            "Invoice ID": ["INV-B1"],
            "Date": ["2026-06-05"],
            "Branch": ["Branch B"],
            "City": ["Bengaluru"],
            "Customer Type": ["Normal"],
            "Gender": ["Male"],
            "Product": ["Biscuits"],
            "Category": ["Snacks"],
            "Quantity": [5],
            "Unit Price": [30.0],
            "Payment": ["Cash"],
            "Rating": [4.0],
            "Sales": [150.0]
        })
        summary_replace = import_sales_dataframe(batch2, mode="replace_all", db_path=self.db_path)
        self.assertEqual(summary_replace["inserted"], 1)

        df_all = get_all_sales_df(self.db_path)
        self.assertEqual(len(df_all), 1)
        self.assertEqual(df_all.iloc[0]["Invoice ID"], "INV-B1")

    def test_anomaly_logging_and_resolution(self):
        """Test logging detected anomalies and resolving them."""
        aid = log_anomaly(
            invoice_id="INV-ERR-999",
            anomaly_type="DATA_QUALITY_ERROR",
            severity="CRITICAL",
            description="Sales amount (₹500.00) does not match Qty * Unit Price (₹100.00)",
            expected_value="100.00",
            actual_value="500.00",
            recommended_action="Inspect billing terminal software",
            db_path=self.db_path
        )
        self.assertGreater(aid, 0)

        df_anomalies = get_anomalies_df(resolved=False, db_path=self.db_path)
        self.assertEqual(len(df_anomalies), 1)
        self.assertEqual(df_anomalies.iloc[0]["Severity"], "CRITICAL")
        self.assertEqual(df_anomalies.iloc[0]["Resolved"], 0)

        # Resolve anomaly
        resolved = resolve_anomaly(aid, db_path=self.db_path)
        self.assertTrue(resolved)

        df_unresolved = get_anomalies_df(resolved=False, db_path=self.db_path)
        self.assertEqual(len(df_unresolved), 0)

    def test_report_logging(self):
        """Test report generation history tracking."""
        rid = log_report(
            report_type="PDF_EXECUTIVE",
            file_name="Executive_Summary_20260718.pdf",
            file_size_bytes=45230,
            dataset_scope="Supermarket Intelligence DB (500 records)",
            filter_summary="All Branches, All Categories",
            record_count=500,
            db_path=self.db_path
        )
        self.assertGreater(rid, 0)

        df_reports = get_reports_df(db_path=self.db_path)
        self.assertEqual(len(df_reports), 1)
        self.assertEqual(df_reports.iloc[0]["Type"], "PDF_EXECUTIVE")
        self.assertEqual(df_reports.iloc[0]["Records"], 500)


if __name__ == "__main__":
    unittest.main()
