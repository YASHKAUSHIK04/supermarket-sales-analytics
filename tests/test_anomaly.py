"""
Supermarket Sales & Customer Analytics - Anomaly Detection Automated Test Suite
Module: tests/test_anomaly.py

Tests:
1. Detection of mathematical discrepancies (|Sales - Qty*Price| > 0.05)
2. Detection of negative and non-positive quantities
3. Detection of negative unit prices
4. Detection of invalid rating scale violations (< 1.0 or > 5.0)
5. Detection of duplicate invoice identifiers
6. Statistical outlier detection (Tukey's IQR method) on sample size >= 15
7. Safe handling on small sample sizes (N < 15) without false-positive fraud flagging
8. Temporal volume spike and crash detection
9. Anomaly summary rollup and database persistence
"""

import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import init_database, get_anomalies_df
from src.anomaly import detect_anomalies, get_anomaly_summary


class TestAnomalyDetection(unittest.TestCase):
    """Test suite for dual-layer retail anomaly and data-quality detection."""

    def setUp(self):
        """Set up clean temporary test database."""
        self.test_dir = PROJECT_ROOT / "tests" / "temp"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.test_dir / "test_anomaly.db"
        if self.db_path.exists():
            self.db_path.unlink()
        init_database(self.db_path)

        # Baseline clean 20-row dataframe
        self.clean_df = pd.DataFrame({
            "Invoice ID": [f"INV-10{i:02d}" for i in range(20)],
            "Date": [f"2026-05-{1+i%25:02d}" for i in range(20)],
            "Branch": ["Branch A"] * 10 + ["Branch B"] * 10,
            "City": ["Jaipur"] * 10 + ["Delhi"] * 10,
            "Customer Type": ["Member"] * 10 + ["Normal"] * 10,
            "Gender": ["Female"] * 10 + ["Male"] * 10,
            "Product": ["Apples"] * 10 + ["Milk"] * 10,
            "Category": ["Fruits"] * 10 + ["Dairy"] * 10,
            "Quantity": [2] * 20,
            "Unit Price": [100.0] * 20,
            "Sales": [200.0] * 20,
            "Payment": ["UPI"] * 20,
            "Rating": [4.5] * 20
        })

    def tearDown(self):
        """Clean up temporary test database."""
        if self.db_path.exists():
            try:
                self.db_path.unlink()
            except Exception:
                pass

    def test_clean_data_zero_quality_errors(self):
        """Verify perfectly clean dataset raises zero data-quality errors."""
        alerts = detect_anomalies(self.clean_df, persist_to_db=False)
        quality_errors = [a for a in alerts if a["anomaly_type"] == "DATA_QUALITY_ERROR"]
        self.assertEqual(len(quality_errors), 0)

    def test_math_discrepancy_detection(self):
        """Verify corrupted sales amount triggers calculation error alert."""
        corrupt_df = self.clean_df.copy()
        corrupt_df.loc[0, "Sales"] = 999.0  # expected 2 * 100 = 200

        alerts = detect_anomalies(corrupt_df)
        math_alerts = [a for a in alerts if a["title"] == "Sales Calculation Discrepancy"]
        self.assertEqual(len(math_alerts), 1)
        self.assertEqual(math_alerts[0]["invoice_id"], "INV-1000")
        self.assertEqual(math_alerts[0]["severity"], "CRITICAL")
        self.assertIn("999.00", math_alerts[0]["actual_value"])

    def test_negative_quantity_and_price_detection(self):
        """Verify negative quantities and prices are flagged with CRITICAL severity."""
        bad_df = self.clean_df.copy()
        bad_df.loc[1, "Quantity"] = -5
        bad_df.loc[2, "Unit Price"] = -50.0

        alerts = detect_anomalies(bad_df)
        qty_alerts = [a for a in alerts if a["title"] == "Invalid Non-Positive Quantity"]
        price_alerts = [a for a in alerts if a["title"] == "Negative Unit Price Recorded"]

        self.assertEqual(len(qty_alerts), 1)
        self.assertEqual(len(price_alerts), 1)
        self.assertEqual(qty_alerts[0]["severity"], "CRITICAL")
        self.assertEqual(price_alerts[0]["severity"], "CRITICAL")

    def test_out_of_bounds_rating_detection(self):
        """Verify customer ratings > 5.0 or < 1.0 are flagged."""
        rating_df = self.clean_df.copy()
        rating_df.loc[3, "Rating"] = 7.5
        rating_df.loc[4, "Rating"] = 0.5

        alerts = detect_anomalies(rating_df)
        rating_alerts = [a for a in alerts if a["title"] == "Customer Rating Out of Bounds"]
        self.assertEqual(len(rating_alerts), 2)
        self.assertEqual(rating_alerts[0]["severity"], "HIGH")

    def test_duplicate_invoice_detection(self):
        """Verify repeated invoice numbers are detected and reported."""
        dup_df = self.clean_df.copy()
        dup_df.loc[1, "Invoice ID"] = "INV-1000"  # Duplicates row 0

        alerts = detect_anomalies(dup_df)
        dup_alerts = [a for a in alerts if a["anomaly_type"] == "DUPLICATE_ID"]
        self.assertEqual(len(dup_alerts), 1)
        self.assertEqual(dup_alerts[0]["invoice_id"], "INV-1000")

    def test_statistical_outlier_iqr_detection(self):
        """Verify extremely high transaction is flagged using Tukey's IQR rule."""
        outlier_df = self.clean_df.copy()
        outlier_df.loc[0, "Quantity"] = 50
        outlier_df.loc[0, "Sales"] = 5000.0  # 25x normal sales

        alerts = detect_anomalies(outlier_df, iqr_multiplier=1.5)
        stat_alerts = [a for a in alerts if a["anomaly_type"] == "STATISTICAL_ANOMALY"]
        self.assertEqual(len(stat_alerts), 1)
        self.assertEqual(stat_alerts[0]["invoice_id"], "INV-1000")
        self.assertEqual(stat_alerts[0]["severity"], "MEDIUM")

    def test_small_dataset_safety(self):
        """Verify datasets with N < 15 do not produce false-positive statistical outliers."""
        small_df = self.clean_df.head(5).copy()
        small_df.loc[0, "Quantity"] = 10
        small_df.loc[0, "Sales"] = 1000.0

        alerts = detect_anomalies(small_df)
        # Should NOT trigger statistical outlier because N < 15
        stat_alerts = [a for a in alerts if a["anomaly_type"] == "STATISTICAL_ANOMALY"]
        self.assertEqual(len(stat_alerts), 0)

    def test_temporal_surge_detection(self):
        """Verify unusual daily spike across 15+ days is flagged."""
        # Create 15 distinct days with baseline ~₹200 and one day with ₹5000
        days = [f"2026-05-{i:02d}" for i in range(1, 16)]
        spike_data = []
        for d in days:
            spike_data.append({
                "Invoice ID": f"INV-{d}",
                "Date": d,
                "Branch": "Branch A",
                "City": "Jaipur",
                "Customer Type": "Member",
                "Gender": "Female",
                "Product": "Apples",
                "Category": "Fruits",
                "Quantity": 2 if d != "2026-05-15" else 50,
                "Unit Price": 100.0,
                "Sales": 200.0 if d != "2026-05-15" else 5000.0,
                "Payment": "UPI",
                "Rating": 4.5
            })
        spike_df = pd.DataFrame(spike_data)

        alerts = detect_anomalies(spike_df, spike_sigma=2.0)
        surge_alerts = [a for a in alerts if a["anomaly_type"] == "TEMPORAL_SPIKE"]
        self.assertEqual(len(surge_alerts), 1)
        self.assertIn("2026-05-15", surge_alerts[0]["description"])

    def test_anomaly_summary_and_persistence(self):
        """Verify anomaly summary rollup and SQLite logging."""
        corrupt_df = self.clean_df.copy()
        corrupt_df.loc[0, "Sales"] = 999.0
        corrupt_df.loc[1, "Rating"] = 9.0

        alerts = detect_anomalies(corrupt_df, persist_to_db=True, db_path=self.db_path)
        summary = get_anomaly_summary(alerts)

        self.assertGreaterEqual(summary["total_anomalies"], 2)
        self.assertGreater(summary["data_quality_count"], 0)
        self.assertIn("CRITICAL", summary["by_severity"])

        # Check records in database
        db_anomalies = get_anomalies_df(db_path=self.db_path)
        self.assertGreaterEqual(len(db_anomalies), 2)


if __name__ == "__main__":
    unittest.main()
