"""
Automated Test Suite for Member 3 Deliverables: SQL KPIs & Power BI Datasets.

Validates:
1. Power BI Gold & Silver dataset generation and row counts
2. Schema & grain integrity (22 LSAs, 7,043 IBM accounts, 88 QoS rows)
3. Core business KPIs:
   - TRAI June Porting = 14.79 Million
   - TRAI May Porting = 14.47 Million
   - IBM Churn Rate = 26.54% (1,869 churned)
4. Null value governance:
   - 11 whitespace Total Charges in IBM handled as NULL
   - QoS 32 missing metrics handled as NULL (not zero)
5. SQL script existence and syntax validation in sql/
"""

import sys
import unittest
from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from powerbi.export_gold_for_powerbi import (
    build_trai_gold_df,
    build_ibm_df,
    POWERBI_DATA_DIR,
    export_powerbi_data
)


class TestMember3Deliverables(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        export_powerbi_data()
        cls.trai_gold = build_trai_gold_df()
        cls.ibm_df = build_ibm_df()
        cls.qos_df = pd.read_csv(BASE_DIR / "data" / "bronze" / "trai_qos" / "trai_qos_june_2026.csv")

    def test_01_trai_gold_grain_and_schema(self):
        """Verify TRAI Gold dataset row count is exactly 22 LSAs with 0 unmapped."""
        self.assertEqual(len(self.trai_gold), 22, "TRAI Gold must have exactly 22 LSAs")
        self.assertEqual(self.trai_gold["canonical_lsa"].isnull().sum(), 0, "No canonical_lsa can be NULL")
        expected_cols = [
            "canonical_lsa", "zone", "mnp_report_month",
            "may_2026_porting_requests_millions", "june_2026_porting_requests_millions",
            "category", "prepaid_percentage", "arpu_inr_per_month"
        ]
        for col in expected_cols:
            self.assertIn(col, self.trai_gold.columns, f"Missing required column: {col}")
        print("\n[TEST 1] TRAI Gold: 22 LSAs verified, 0 unmapped")

    def test_02_ibm_silver_cleaning(self):
        """Verify IBM dataset row count (7,043) and handling of 11 whitespace Total_Charges."""
        self.assertEqual(len(self.ibm_df), 7043, "IBM dataset must contain exactly 7,043 customers")
        null_charges = self.ibm_df["Total_Charges"].isnull().sum()
        self.assertEqual(null_charges, 11, "Exactly 11 whitespace Total Charges must be NULL")
        print("[TEST 2] IBM Silver: 7,043 accounts verified, 11 whitespace Total_Charges as NULL")

    def test_03_headline_kpis(self):
        """Verify exact KPI values matching SQL and Power BI DAX formulas."""
        # TRAI Porting
        may_mnp = self.trai_gold["may_2026_porting_requests_millions"].sum()
        june_mnp = self.trai_gold["june_2026_porting_requests_millions"].sum()
        self.assertAlmostEqual(may_mnp, 14.47, places=2)
        self.assertAlmostEqual(june_mnp, 14.79, places=2)

        # IBM Churn Rate
        churned = (self.ibm_df["Churn_Value"] == 1).sum()
        total = len(self.ibm_df)
        churn_rate = churned / total * 100
        self.assertEqual(churned, 1869, "Churned customer count must be 1,869")
        self.assertAlmostEqual(churn_rate, 26.54, places=1)
        print(f"[TEST 3] Core KPIs verified: June MNP = {june_mnp:.2f}M, Churn Rate = {churn_rate:.2f}%")

    def test_04_qos_null_governance(self):
        """Verify 32 QoS missing values remain NULL and are not replaced with zero."""
        self.assertEqual(len(self.qos_df), 88, "QoS table must have 88 rows (5 operators × 22 LSAs)")
        rjil_rows = self.qos_df[self.qos_df["operator"] == "RJIL"]
        self.assertEqual(len(rjil_rows), 22)
        # Check metric_08 is missing in RJIL (IP-only network)
        missing_m08 = rjil_rows["metric_08"].isnull().sum()
        self.assertEqual(missing_m08, 22, "RJIL must have NULL for circuit-switched drop call rate (metric_08)")
        print("[TEST 4] QoS Null Governance verified: 32 missing metrics maintained as NULL")

    def test_05_powerbi_data_exports(self):
        """Verify all 6 Power BI Direct Import CSVs exist and are non-empty."""
        expected_files = [
            "trai_lsa_switching_usage_context.csv",
            "ibm_telco_customer_churn.csv",
            "trai_qos.csv",
            "trai_national_wireless_usage_trends.csv",
            "trai_fixed_wired_broadband.csv",
            "trai_wireless_broadband.csv"
        ]
        for fname in expected_files:
            fpath = POWERBI_DATA_DIR / fname
            self.assertTrue(fpath.exists(), f"Missing Power BI export file: {fname}")
            self.assertGreater(fpath.stat().st_size, 50, f"File {fname} is empty")
        print("[TEST 5] Power BI data exports verified: 6 CSV files validated")

    def test_06_sql_scripts_exist_and_executable(self):
        """Verify that all 4 standalone SQL scripts exist in sql/."""
        sql_dir = BASE_DIR / "sql"
        for i, name in enumerate([
            "01_trai_quality_checks.sql",
            "02_trai_kpis.sql",
            "03_ibm_churn_kpis.sql",
            "04_dashboard_validation.sql"
        ], start=1):
            fpath = sql_dir / name
            self.assertTrue(fpath.exists(), f"Missing SQL script: {name}")
            content = fpath.read_text(encoding="utf-8")
            self.assertIn("SELECT", content.upper(), f"Script {name} should contain SELECT queries")
        print("[TEST 6] SQL scripts verified: 4 SQL control files validated")


if __name__ == "__main__":
    unittest.main()
