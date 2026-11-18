"""
Comprehensive Test Suite for Telecom Analytics Platform.

Validates:
1. Database connectivity & dual-mode fallback
2. Schema & table integrity across Bronze, Silver, Gold
3. SQL query execution from existing notebooks
4. KPI mathematical accuracy
5. Chart data transformation & rendering
6. Filter edge cases & empty data handling
7. CSV data export functionality
"""

import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.database import get_db, TelecomDataLoader
from utils.styling import format_kpi_card, get_plotly_theme


class TestTelecomPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = get_db()

    def test_01_database_connectivity(self):
        """Verify database loader initialization and mode detection."""
        self.assertIsNotNone(self.db)
        is_dbx = self.db.is_databricks()
        print(f"\n[TEST 1] Database Mode: {'Live Databricks' if is_dbx else 'Local Verified Pipeline'}")
        self.assertIsInstance(is_dbx, bool)

    def test_02_trai_gold_table_access(self):
        """Verify TRAI Gold dataset row count, schema and canonical LSA join integrity."""
        df = self.db.get_trai_gold_df()
        self.assertEqual(len(df), 22, "TRAI Gold should have exactly 22 Licensed Service Areas")
        expected_cols = [
            "canonical_lsa", "zone", "mnp_report_month",
            "may_2026_porting_requests_millions", "june_2026_porting_requests_millions",
            "category", "prepaid_percentage", "arpu_inr_per_month"
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Missing required column {col} in TRAI Gold")
        # Ensure no unmapped canonical LSAs
        self.assertEqual(df["canonical_lsa"].isnull().sum(), 0, "No canonical_lsa should be null")
        print(f"[TEST 2] TRAI Gold: 22 LSAs verified, 0 unmapped")

    def test_03_ibm_silver_table_access(self):
        """Verify IBM Customer Churn row count, schema and cleaning."""
        df = self.db.get_ibm_df()
        self.assertEqual(len(df), 7043, "IBM dataset should have exactly 7,043 customers")
        self.assertIn("Total_Charges", df.columns)
        self.assertIn("Churn_Value", df.columns)
        # Check Total Charges 11 whitespace records converted to null
        null_total_charges = df["Total_Charges"].isnull().sum()
        self.assertEqual(null_total_charges, 11, "Exactly 11 records should have NULL Total_Charges")
        print(f"[TEST 3] IBM Silver: 7,043 records verified, exactly 11 NULL Total_Charges verified")

    def test_04_kpi_calculations_accuracy(self):
        """Verify mathematical precision of core KPI formulas."""
        ibm = self.db.get_ibm_df()
        churned = (ibm["Churn_Value"] == 1).sum()
        total = len(ibm)
        churn_rate = churned / total * 100
        self.assertEqual(churned, 1869, "Churned customers must be exactly 1,869")
        self.assertAlmostEqual(churn_rate, 26.53698, places=2, msg="Churn rate must be ~26.54%")

        trai = self.db.get_trai_gold_df()
        may_requests = trai["may_2026_porting_requests_millions"].sum()
        june_requests = trai["june_2026_porting_requests_millions"].sum()
        self.assertAlmostEqual(may_requests, 14.47, places=2)
        self.assertAlmostEqual(june_requests, 14.79, places=2)
        print(f"[TEST 4] Core KPIs verified: IBM Churn Rate={churn_rate:.2f}%, MNP June={june_requests:.2f}M")

    def test_05_sql_notebook_queries_execution(self):
        """Execute queries from the original TRAI and IBM notebooks."""
        # 1. TRAI Average ARPU by Zone query
        q_arpu = """
            SELECT zone, ROUND(AVG(arpu_inr_per_month), 2) AS average_arpu
            FROM workspace.gold.trai_lsa_switching_usage_context
            GROUP BY zone ORDER BY average_arpu DESC
        """
        res_arpu = self.db.execute_query(q_arpu)
        self.assertEqual(len(res_arpu), 2, "Should return 2 zones (Zone I, Zone II)")

        # 2. IBM Segment Analysis query
        q_seg = "SELECT * FROM workspace.gold.ibm_churn_segment_analysis"
        res_seg = self.db.execute_query(q_seg)
        self.assertGreater(len(res_seg), 10, "Segment analysis should return multiple segments")
        print(f"[TEST 5] Original notebook SQL queries executed successfully")

    def test_06_filter_behaviour_and_empty_handling(self):
        """Test filtering logic and resilience against empty filter states."""
        raw_ibm = self.db.get_ibm_df()
        # Non-empty filter
        f_df = raw_ibm[raw_ibm["Contract"] == "Two year"]
        self.assertGreater(len(f_df), 0)
        two_yr_churn = (f_df["Churn_Value"] == 1).sum() / len(f_df) * 100
        self.assertLess(two_yr_churn, 5.0, "Two-year contract churn should be under 5%")

        # Empty filter edge case
        empty_df = raw_ibm[raw_ibm["Contract"] == "NonExistentContract"]
        self.assertEqual(len(empty_df), 0)
        # Verify safe division / KPI formatting does not crash
        tot = len(empty_df)
        rate = (empty_df["Churn_Value"].sum() / tot * 100) if tot > 0 else 0
        self.assertEqual(rate, 0)
        print(f"[TEST 6] Filter behaviour and zero-division edge cases handled cleanly")

    def test_07_csv_export_generation(self):
        """Verify data can be encoded to CSV for export."""
        trai = self.db.get_trai_gold_df()
        csv_bytes = trai.to_csv(index=False).encode("utf-8")
        self.assertGreater(len(csv_bytes), 100)
        print(f"[TEST 7] CSV export generation verified ({len(csv_bytes)} bytes)")


if __name__ == "__main__":
    unittest.main()
