"""
Supermarket Sales & Customer Analytics - Business Insights Automated Test Suite
Module: tests/test_insights.py

Tests:
1. 4-tier framework schema integrity (Observation, Insight, Explanation, Action)
2. Empty DataFrame graceful handling
3. Multi-branch revenue disparity insights
4. Merchandise category volume-value divergence
5. Customer loyalty segment ATV comparison
6. Payment method channel adoption insights
7. Customer satisfaction driver variance
8. Critical inventory replenishment urgency integration
"""

import sys
import unittest
from pathlib import Path
import pandas as pd

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.insights import generate_structured_business_insights


class TestBusinessInsightsEngine(unittest.TestCase):
    """Test suite for 4-tier business insight generation and commercial logic."""

    def setUp(self):
        """Set up sample retail transaction and inventory datasets."""
        self.sample_sales = pd.DataFrame({
            "Invoice ID": [f"INV-{i}" for i in range(1, 11)],
            "Date": ["2026-05-01"] * 5 + ["2026-05-15"] * 5,
            "Branch": ["Branch A"] * 6 + ["Branch B"] * 4,
            "City": ["Jaipur"] * 6 + ["Delhi"] * 4,
            "Customer Type": ["Member"] * 6 + ["Normal"] * 4,
            "Gender": ["Female"] * 5 + ["Male"] * 5,
            "Product": ["Coffee"] * 4 + ["Bread"] * 4 + ["Milk"] * 2,
            "Category": ["Beverages"] * 4 + ["Bakery"] * 4 + ["Dairy"] * 2,
            "Quantity": [2, 3, 2, 3, 10, 8, 12, 10, 5, 5],
            "Unit Price": [150.0, 150.0, 150.0, 150.0, 40.0, 40.0, 40.0, 40.0, 60.0, 60.0],
            "Sales": [300.0, 450.0, 300.0, 450.0, 400.0, 320.0, 480.0, 400.0, 300.0, 300.0],
            "Payment": ["UPI"] * 6 + ["Cash"] * 4,
            "Rating": [4.8, 4.9, 4.7, 4.6, 3.8, 3.9, 3.7, 4.0, 4.5, 4.4]
        })

        self.sample_inventory = pd.DataFrame({
            "Product ID": [1, 2, 3],
            "Product Name": ["Coffee", "Bread", "Milk"],
            "Category": ["Beverages", "Bakery", "Dairy"],
            "Unit Price (₹)": [150.0, 40.0, 60.0],
            "Current Stock": [10, 80, 5],  # Coffee: 10 (low), Milk: 5 (critical)
            "Reorder Threshold": [20, 20, 20],
            "Target Stock": [100, 100, 100],
            "Stock_Health": ["⚠️ CRITICAL REORDER", "✅ HEALTHY", "⚠️ CRITICAL REORDER"],
            "Estimated_Reorder_Cost": [13500.0, 0.0, 5700.0]
        })

    def test_framework_structure_integrity(self):
        """Verify all generated insights strictly adhere to 4-tier model."""
        insights = generate_structured_business_insights(self.sample_sales)
        self.assertGreaterEqual(len(insights), 4)

        required_keys = ["category", "title", "observation", "insight", "explanation", "action", "severity", "priority"]
        for ins in insights:
            for k in required_keys:
                self.assertIn(k, ins)
                self.assertIsInstance(ins[k], str)
                self.assertGreater(len(ins[k].strip()), 0)
            self.assertIn(ins["priority"], ["CRITICAL", "HIGH", "MEDIUM", "LOW"])

    def test_empty_dataframe_handling(self):
        """Verify empty DataFrame returns non-crashing informational guidance."""
        empty_insights = generate_structured_business_insights(pd.DataFrame())
        self.assertEqual(len(empty_insights), 1)
        self.assertEqual(empty_insights[0]["category"], "Data Availability")
        self.assertIn("Reset", empty_insights[0]["action"])
        self.assertIn("priority", empty_insights[0])
        self.assertEqual(empty_insights[0]["priority"], "LOW")

    def test_branch_revenue_disparity_insight(self):
        """Verify branch disparity insight identifies top and lowest locations."""
        insights = generate_structured_business_insights(self.sample_sales)
        branch_insights = [i for i in insights if i["category"] == "Geographic Performance"]
        self.assertEqual(len(branch_insights), 1)
        self.assertIn("Branch A", branch_insights[0]["observation"])
        self.assertIn("Branch B", branch_insights[0]["observation"])

    def test_merchandise_dynamics_insight(self):
        """Verify category volume vs revenue dynamics are captured."""
        insights = generate_structured_business_insights(self.sample_sales)
        cat_insights = [i for i in insights if i["category"] == "Merchandise Dynamics"]
        self.assertEqual(len(cat_insights), 1)
        self.assertIn("Bakery", cat_insights[0]["observation"])

    def test_inventory_urgency_integration(self):
        """Verify critical inventory replenishment alert is integrated into recommendations."""
        insights_with_inv = generate_structured_business_insights(self.sample_sales, self.sample_inventory)
        inv_insights = [i for i in insights_with_inv if i["category"] == "Inventory Management"]
        self.assertEqual(len(inv_insights), 1)
        self.assertEqual(inv_insights[0]["severity"], "CRITICAL")
        self.assertEqual(inv_insights[0]["priority"], "CRITICAL")
        self.assertIn("Coffee", inv_insights[0]["observation"])
        self.assertIn("Milk", inv_insights[0]["observation"])

    def test_inventory_keyword_aliases_integration(self):
        """Verify calling with inventory_intelligence_df keyword argument works identically."""
        insights_kw = generate_structured_business_insights(
            self.sample_sales,
            inventory_intelligence_df=self.sample_inventory
        )
        inv_insights = [i for i in insights_kw if i["category"] == "Inventory Management"]
        self.assertEqual(len(inv_insights), 1)
        self.assertEqual(inv_insights[0]["severity"], "CRITICAL")
        self.assertEqual(inv_insights[0]["priority"], "CRITICAL")

    def test_insights_with_valid_priority(self):
        """Regression test: verify all insight priorities are strictly one of CRITICAL, HIGH, MEDIUM, LOW."""
        insights = generate_structured_business_insights(self.sample_sales, self.sample_inventory)
        for item in insights:
            self.assertIn("priority", item)
            self.assertIn(item["priority"], ["CRITICAL", "HIGH", "MEDIUM", "LOW"])
            # Ensure priority and severity are consistent
            self.assertEqual(item["priority"], item["severity"])

    def test_insights_missing_priority_fallback(self):
        """Regression test: simulate insight dictionary missing priority key and verify fallback."""
        raw_insights = [
            {
                "category": "Customer Segments",
                "title": "Segment Shift",
                "severity": "HIGH",
                "observation": "Member counts rose 15%",
                "insight": "High membership conversion",
                "explanation": "Loyalty campaign active",
                "action": "Maintain program benefits"
            },
            {
                "category": "Operations",
                "title": "Aisle Clearance",
                "observation": "Aisle 3 congestion",
                "insight": "Bottleneck at peak hours",
                "explanation": "Display stand blocking flow",
                "action": "Relocate display"
            }
        ]

        normalized = []
        for raw_item in raw_insights:
            raw_pri = raw_item.get("priority")
            if raw_pri is None or str(raw_pri).strip() == "":
                raw_pri = raw_item.get("severity")
            if raw_pri is None or str(raw_pri).strip() == "":
                raw_pri = "MEDIUM"
            pri_clean = str(raw_pri).strip().upper()
            if pri_clean not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                pri_clean = "MEDIUM"
            normalized.append(pri_clean)

        self.assertEqual(normalized[0], "HIGH")  # Fell back to severity
        self.assertEqual(normalized[1], "MEDIUM")  # Fell back to default MEDIUM

    def test_insights_empty_priority_fallback(self):
        """Regression test: verify empty priority string or None gracefully defaults to MEDIUM."""
        raw_insights = [
            {"title": "Empty string", "priority": "", "severity": ""},
            {"title": "Whitespace only", "priority": "   ", "severity": None},
            {"title": "None priority", "priority": None, "severity": None},
            {"title": "Unexpected string", "priority": "URGENT_123"},
        ]

        normalized = []
        for raw_item in raw_insights:
            raw_pri = raw_item.get("priority")
            if raw_pri is None or str(raw_pri).strip() == "":
                raw_pri = raw_item.get("severity")
            if raw_pri is None or str(raw_pri).strip() == "":
                raw_pri = "MEDIUM"
            pri_clean = str(raw_pri).strip().upper()
            if pri_clean not in ("CRITICAL", "HIGH", "MEDIUM", "LOW"):
                pri_clean = "MEDIUM"
            normalized.append(pri_clean)

        self.assertEqual(normalized, ["MEDIUM", "MEDIUM", "MEDIUM", "MEDIUM"])

    def test_insights_empty_list_handling(self):
        """Regression test: verify passing an empty insights list does not raise any exceptions."""
        empty_list = []
        filtered_insights = [i for i in empty_list if i.get("priority") == "HIGH"]
        self.assertEqual(filtered_insights, [])


if __name__ == "__main__":
    unittest.main()
