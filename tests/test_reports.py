"""
Unit Tests for Supermarket Sales Intelligence Reporting Engine
===============================================================
Tests executive PDF document generation (ReportLab) and multi-sheet
Excel workbook creation (openpyxl).
"""

import io
import unittest
import pandas as pd
import openpyxl

from src.reports import (
    generate_pdf_report,
    generate_excel_workbook,
    generate_csv_export,
)
from src.inventory import calculate_inventory_intelligence
from src.anomaly import detect_anomalies
from src.insights import generate_structured_business_insights


class TestReportingEngine(unittest.TestCase):
    """Test suite for PDF and Excel business report generation."""

    def setUp(self):
        """Create sample sales, inventory, insights, and anomaly fixtures."""
        self.sample_df = pd.DataFrame([
            {
                "Invoice ID": "INV-1001",
                "Branch": "A",
                "City": "Yangon",
                "Customer Type": "Member",
                "Gender": "Female",
                "Product": "Organic Apples",
                "Product Category": "Food and beverages",
                "Unit Price": 10.0,
                "Quantity": 5,
                "Sales": 50.0,
                "Date": "2023-01-15",
                "Payment": "Ewallet",
                "Rating": 4.5,
            },
            {
                "Invoice ID": "INV-1002",
                "Branch": "B",
                "City": "Mandalay",
                "Customer Type": "Normal",
                "Gender": "Male",
                "Product": "Smartphone Case",
                "Product Category": "Electronic accessories",
                "Unit Price": 20.0,
                "Quantity": 2,
                "Sales": 40.0,
                "Date": "2023-01-16",
                "Payment": "Cash",
                "Rating": 3.8,
            },
            {
                "Invoice ID": "INV-1003",
                "Branch": "C",
                "City": "Naypyitaw",
                "Customer Type": "Member",
                "Gender": "Female",
                "Product": "Face Wash",
                "Product Category": "Health and beauty",
                "Unit Price": 15.0,
                "Quantity": 4,
                "Sales": 60.0,
                "Date": "2023-01-17",
                "Payment": "Credit card",
                "Rating": 4.9,
            },
        ])

        # Generate anomalies & insights
        self.anomalies = detect_anomalies(self.sample_df)
        self.insights = generate_structured_business_insights(self.sample_df)

        # Sample inventory DataFrame
        self.inventory_df = pd.DataFrame([
            {
                "product_id": 1,
                "product_name": "Organic Apples",
                "category_name": "Food and beverages",
                "current_stock": 10,
                "safety_stock_level": 20,
                "unit_cost": 7.0,
                "unit_selling_price": 10.0,
                "daily_sales_velocity": 2.5,
                "days_of_stock_remaining": 4.0,
                "velocity_tier": "Fast Moving",
                "health_status": "Low Stock",
                "reorder_flag": 1,
                "recommended_reorder_qty": 50,
                "estimated_reorder_cost": 350.0,
            },
            {
                "product_id": 2,
                "product_name": "Smartphone Case",
                "category_name": "Electronic accessories",
                "current_stock": 45,
                "safety_stock_level": 15,
                "unit_cost": 12.0,
                "unit_selling_price": 20.0,
                "daily_sales_velocity": 0.8,
                "days_of_stock_remaining": 56.2,
                "velocity_tier": "Normal Moving",
                "health_status": "Healthy",
                "reorder_flag": 0,
                "recommended_reorder_qty": 0,
                "estimated_reorder_cost": 0.0,
            },
        ])

    def test_pdf_report_generation(self):
        """Verify PDF generation returns valid binary data starting with %PDF."""
        filter_summary = {
            "date_range": "2023-01-15 to 2023-01-17",
            "branch": ["A", "B", "C"],
            "city": ["Yangon", "Mandalay", "Naypyitaw"],
        }
        pdf_buf = generate_pdf_report(
            df=self.sample_df,
            dataset_name="Supermarket Baseline Fixture",
            filter_summary=filter_summary,
            insights=self.insights,
            anomalies=self.anomalies,
            inventory_df=self.inventory_df,
        )

        self.assertIsInstance(pdf_buf, io.BytesIO)
        pdf_bytes = pdf_buf.getvalue()
        self.assertGreater(len(pdf_bytes), 1000, "PDF should contain compiled pages.")
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "PDF binary header must start with %PDF.")

    def test_pdf_report_empty_dataframe(self):
        """Verify PDF report generates cleanly even with an empty DataFrame."""
        empty_df = pd.DataFrame(columns=["Invoice ID", "Branch", "City", "Sales", "Quantity", "Rating"])
        pdf_buf = generate_pdf_report(
            df=empty_df,
            dataset_name="Empty Scope Dataset",
            filter_summary={},
            insights=[],
            anomalies=[],
            inventory_df=None,
        )

        self.assertIsInstance(pdf_buf, io.BytesIO)
        pdf_bytes = pdf_buf.getvalue()
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_excel_workbook_generation(self):
        """Verify multi-sheet Excel generation and validate sheet names and content."""
        filter_summary = {"branch": ["A", "B"]}
        xlsx_buf = generate_excel_workbook(
            df=self.sample_df,
            dataset_name="Test Store Scope",
            filter_summary=filter_summary,
            insights=self.insights,
            anomalies=self.anomalies,
            inventory_df=self.inventory_df,
        )

        self.assertIsInstance(xlsx_buf, io.BytesIO)
        xlsx_bytes = xlsx_buf.getvalue()
        self.assertGreater(len(xlsx_bytes), 2000, "Excel workbook should contain formatted tabs.")

        # Reopen workbook with openpyxl to inspect sheet structure
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
        sheet_names = wb.sheetnames

        expected_sheets = [
            "Executive Summary",
            "Sales Transactions",
            "Product Performance",
            "Category Performance",
            "Inventory Intelligence",
            "Anomaly Audit Log",
            "Business Insights Matrix",
        ]
        for sheet in expected_sheets:
            self.assertIn(sheet, sheet_names, f"Expected sheet '{sheet}' missing from workbook.")

        # Check Executive Summary content
        ws_sum = wb["Executive Summary"]
        self.assertEqual(ws_sum["A1"].value, "Supermarket Sales & Retail Intelligence System")
        self.assertEqual(ws_sum["B5"].value, 3)  # Total records

        # Check Sales Transactions row count (header + 3 rows = 4)
        ws_tx = wb["Sales Transactions"]
        self.assertEqual(ws_tx.max_row, 4)

    def test_excel_workbook_empty_dataframe(self):
        """Verify Excel workbook generates without crashing when passed empty data."""
        empty_df = pd.DataFrame()
        xlsx_buf = generate_excel_workbook(
            df=empty_df,
            dataset_name="Empty Scope",
            filter_summary=None,
            insights=None,
            anomalies=None,
            inventory_df=None,
        )

        self.assertIsInstance(xlsx_buf, io.BytesIO)
        wb = openpyxl.load_workbook(xlsx_buf)
        self.assertIn("Executive Summary", wb.sheetnames)

    def test_csv_export(self):
        """Verify CSV export utility."""
        csv_str = generate_csv_export(self.sample_df)
        self.assertIn("INV-1001", csv_str)
        self.assertIn("INV-1002", csv_str)
        self.assertIn("Organic Apples", csv_str)

        # Empty df test
        empty_csv = generate_csv_export(pd.DataFrame())
        self.assertEqual(empty_csv, "")


if __name__ == "__main__":
    unittest.main()
