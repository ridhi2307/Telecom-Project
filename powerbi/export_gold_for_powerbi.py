"""
Export Gold & Silver Tables for Power BI Desktop Ingestion.

Generates validated CSV data files formatted specifically for Power BI Desktop
Direct Import mode, with standard headers, typed nulls, and clean data types.
"""

from pathlib import Path
import sys
import pandas as pd

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from utils.database import get_db

POWERBI_DATA_DIR = BASE_DIR / "powerbi" / "data"
POWERBI_DATA_DIR.mkdir(parents=True, exist_ok=True)


def export_powerbi_data():
    db = get_db()
    print("Loading Gold and Silver tables from Medallion pipeline...")

    # 1. TRAI Gold Context
    trai_gold = db.get_trai_gold_df()
    trai_gold_path = POWERBI_DATA_DIR / "trai_lsa_switching_usage_context.csv"
    trai_gold.to_csv(trai_gold_path, index=False)
    print(f"Exported: {trai_gold_path.name} ({len(trai_gold)} rows)")

    # 2. IBM Customer Churn Silver/Gold
    ibm_df = db.get_ibm_df()
    ibm_path = POWERBI_DATA_DIR / "ibm_telco_customer_churn.csv"
    ibm_df.to_csv(ibm_path, index=False)
    print(f"Exported: {ibm_path.name} ({len(ibm_df)} rows)")

    # 3. TRAI QoS Silver
    qos_df = db.get_qos_df()
    qos_path = POWERBI_DATA_DIR / "trai_qos.csv"
    qos_df.to_csv(qos_path, index=False)
    print(f"Exported: {qos_path.name} ({len(qos_df)} rows)")

    # 4. TRAI National Trends Gold
    trends_df = db.get_national_trends_df()
    trends_path = POWERBI_DATA_DIR / "trai_national_wireless_usage_trends.csv"
    trends_df.to_csv(trends_path, index=False)
    print(f"Exported: {trends_path.name} ({len(trends_df)} rows)")

    # 5. Broadband Rankings
    fixed_bb, wireless_bb = db.get_broadband_df()
    fixed_path = POWERBI_DATA_DIR / "trai_fixed_wired_broadband.csv"
    wireless_path = POWERBI_DATA_DIR / "trai_wireless_broadband.csv"
    fixed_bb.to_csv(fixed_path, index=False)
    wireless_bb.to_csv(wireless_path, index=False)
    print(f"Exported: {fixed_path.name} ({len(fixed_bb)} rows)")
    print(f"Exported: {wireless_path.name} ({len(wireless_bb)} rows)")

    print("\nAll Power BI dataset exports completed successfully!")
    print(f"Target Directory: {POWERBI_DATA_DIR}")


if __name__ == "__main__":
    export_powerbi_data()
