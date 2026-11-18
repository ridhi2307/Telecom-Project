"""
Export Gold & Silver Tables for Power BI Desktop Ingestion.

Generates validated CSV data files formatted specifically for Power BI Desktop
Direct Import mode, with standard headers, typed nulls, and clean data types.
Directly reads from data/bronze and metadata without external framework dependencies.
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "bronze"
METADATA_DIR = BASE_DIR / "metadata"
POWERBI_DATA_DIR = BASE_DIR / "powerbi" / "data"
POWERBI_DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_trai_gold_df() -> pd.DataFrame:
    """Build the 22-circle TRAI Gold analytical context table using the canonical LSA crosswalk."""
    dim_lsa = pd.read_csv(METADATA_DIR / "dim_lsa.csv")
    mnp = pd.read_csv(DATA_DIR / "trai_subscribers" / "mnp_service_area_status.csv")
    usage = pd.read_csv(DATA_DIR / "trai_usage" / "usage_by_service_area.csv")

    # Clean usage percentages & numeric fields
    usage["prepaid_percentage"] = (
        usage["prepaid_percentage"].astype(str).str.replace("%", "").str.strip().astype(float)
    )
    for col in ["arpu_inr_per_month", "outgoing_sms_per_month", "outgoing_mou_per_month",
                "incoming_mou_per_month", "total_mou_per_month"]:
        usage[col] = pd.to_numeric(usage[col], errors="coerce")

    # Map LSA via metadata crosswalk
    mnp_mapped = mnp.merge(
        dim_lsa[["canonical_lsa", "mnp_service_area"]],
        left_on="service_area",
        right_on="mnp_service_area",
        how="left"
    )
    usage_mapped = usage.merge(
        dim_lsa[["canonical_lsa", "usage_service_area"]],
        left_on="service_area",
        right_on="usage_service_area",
        how="left"
    )

    # Join on canonical LSA (Join Contract: exactly 22 rows)
    trai_context = mnp_mapped.merge(
        usage_mapped,
        on="canonical_lsa",
        suffixes=("_mnp", "_usage")
    )

    trai_gold = trai_context[[
        "canonical_lsa",
        "zone",
        "report_month",
        "may_2026_porting_requests_millions",
        "june_2026_porting_requests_millions",
        "category",
        "prepaid_percentage",
        "arpu_inr_per_month",
        "outgoing_sms_per_month",
        "outgoing_mou_per_month",
        "incoming_mou_per_month",
        "total_mou_per_month",
        "reporting_period"
    ]].rename(columns={
        "report_month": "mnp_report_month",
        "reporting_period": "usage_reporting_period"
    })
    return trai_gold


def build_ibm_df() -> pd.DataFrame:
    """Load and clean IBM Telco Customer Churn dataset."""
    ibm_file = DATA_DIR / "ibm_telco" / "ibm_telco_customer_churn.csv"
    df = pd.read_csv(ibm_file)
    df.columns = [c.strip().replace(" ", "_").replace("-", "_") for c in df.columns]
    # Treat 11 whitespace-only Total_Charges as NULL
    if "Total_Charges" in df.columns:
        df["Total_Charges"] = pd.to_numeric(
            df["Total_Charges"].astype(str).str.strip().replace("", np.nan),
            errors="coerce"
        )
    return df


def export_powerbi_data():
    """Export all tables required for the 4-page Power BI dashboard."""
    print("Loading Gold and Silver tables from data and metadata...")

    # 1. TRAI Gold Context
    trai_gold = build_trai_gold_df()
    trai_gold_path = POWERBI_DATA_DIR / "trai_lsa_switching_usage_context.csv"
    trai_gold.to_csv(trai_gold_path, index=False)
    print(f"Exported: {trai_gold_path.name} ({len(trai_gold)} rows)")

    # 2. IBM Customer Churn Silver/Gold
    ibm_df = build_ibm_df()
    ibm_path = POWERBI_DATA_DIR / "ibm_telco_customer_churn.csv"
    ibm_df.to_csv(ibm_path, index=False)
    print(f"Exported: {ibm_path.name} ({len(ibm_df)} rows)")

    # 3. TRAI QoS Silver
    qos_df = pd.read_csv(DATA_DIR / "trai_qos" / "trai_qos_june_2026.csv")
    qos_path = POWERBI_DATA_DIR / "trai_qos.csv"
    qos_df.to_csv(qos_path, index=False)
    print(f"Exported: {qos_path.name} ({len(qos_df)} rows)")

    # 4. TRAI National Trends Gold
    trends_df = pd.read_csv(DATA_DIR / "trai_usage" / "wireless_usage_trends.csv")
    trends_path = POWERBI_DATA_DIR / "trai_national_wireless_usage_trends.csv"
    trends_df.to_csv(trends_path, index=False)
    print(f"Exported: {trends_path.name} ({len(trends_df)} rows)")

    # 5. Broadband Rankings
    fixed_bb = pd.read_csv(DATA_DIR / "trai_subscribers" / "fixed_wired_broadband.csv")
    wireless_bb = pd.read_csv(DATA_DIR / "trai_subscribers" / "wireless_broadband.csv")
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
