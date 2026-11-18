"""
Database Connection & Data Access Layer for Telecom Analytics Platform.

Supports dual-mode execution:
1. Live Databricks SQL Warehouse: When DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH,
   and DATABRICKS_TOKEN are provided in environment variables or .env file.
2. Local Verified Data Pipeline: High-performance embedded SQL database pre-loaded
   with the Bronze, Silver, and Gold datasets matching the Databricks Delta Lake schema.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np

# Load environment variables if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "bronze"
METADATA_DIR = BASE_DIR / "metadata"


class TelecomDataLoader:
    """Manages loading, cleaning, and querying telecom datasets."""

    _instance = None
    _sqlite_conn = None
    _is_databricks = False

    def __init__(self):
        self._check_databricks_connection()
        if not self._is_databricks:
            self._init_local_database()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _check_databricks_connection(self):
        """Check if Databricks credentials are fully configured."""
        host = os.getenv("DATABRICKS_SERVER_HOSTNAME")
        http_path = os.getenv("DATABRICKS_HTTP_PATH")
        token = os.getenv("DATABRICKS_TOKEN")

        if host and http_path and token:
            try:
                from databricks import sql
                self._is_databricks = True
                print("Databricks configuration detected. Live warehouse mode enabled.")
            except ImportError:
                print("databricks-sql-connector not installed. Defaulting to local pipeline mode.")
                self._is_databricks = False
        else:
            self._is_databricks = False

    def is_databricks(self) -> bool:
        return self._is_databricks

    def _init_local_database(self):
        """Build and populate in-memory relational database mirroring Databricks Gold/Silver."""
        self._sqlite_conn = sqlite3.connect(":memory:", check_same_thread=False)

        # 1. Load Metadata
        dim_lsa_file = METADATA_DIR / "dim_lsa.csv"
        dim_lsa = pd.read_csv(dim_lsa_file)
        dim_lsa.to_sql("dim_lsa", self._sqlite_conn, index=False, if_exists="replace")

        # 2. Ingest and Clean IBM Telco Customer Churn (Silver & Gold)
        ibm_file = DATA_DIR / "ibm_telco" / "ibm_telco_customer_churn.csv"
        ibm = pd.read_csv(ibm_file)

        # Cleaning matching Databricks Silver layer in 01_bronze_ingestion.ipynb
        ibm["Total_Charges"] = pd.to_numeric(ibm["Total Charges"].astype(str).str.strip(), errors="coerce")
        ibm["Senior_Citizen"] = ibm["Senior Citizen"]
        ibm["Tenure_Months"] = pd.to_numeric(ibm["Tenure Months"], errors="coerce").fillna(0).astype(int)
        ibm["Monthly_Charges"] = pd.to_numeric(ibm["Monthly Charges"], errors="coerce").fillna(0.0)
        ibm["Churn_Value"] = pd.to_numeric(ibm["Churn Value"], errors="coerce").fillna(0).astype(int)
        ibm["Churn_Score"] = pd.to_numeric(ibm["Churn Score"], errors="coerce").fillna(0).astype(int)
        ibm["CLTV"] = pd.to_numeric(ibm["CLTV"], errors="coerce").fillna(0).astype(int)

        # Tenure Bands matching Gold layer
        ibm["tenure_band"] = pd.cut(
            ibm["Tenure_Months"],
            bins=[-1, 12, 24, 48, 120],
            labels=["0-12 months", "13-24 months", "25-48 months", "49+ months"]
        ).astype(str)

        # Register Silver and Gold IBM tables
        ibm.to_sql("silver_ibm_telco_customer_churn", self._sqlite_conn, index=False, if_exists="replace")
        ibm.to_sql("gold_ibm_telco_customer_churn", self._sqlite_conn, index=False, if_exists="replace")

        # Create IBM Churn Segment Analysis view
        self._sqlite_conn.execute("""
            CREATE VIEW IF NOT EXISTS gold_ibm_churn_segment_analysis AS
            SELECT 'Contract' AS segment_type, Contract AS segment,
                   COUNT(*) AS total_customers,
                   SUM(Churn_Value) AS churned_customers,
                   ROUND(CAST(SUM(Churn_Value) AS FLOAT) / COUNT(*) * 100, 2) AS churn_rate_percent
            FROM gold_ibm_telco_customer_churn GROUP BY Contract
            UNION ALL
            SELECT 'Payment Method' AS segment_type, `Payment Method` AS segment,
                   COUNT(*) AS total_customers,
                   SUM(Churn_Value) AS churned_customers,
                   ROUND(CAST(SUM(Churn_Value) AS FLOAT) / COUNT(*) * 100, 2) AS churn_rate_percent
            FROM gold_ibm_telco_customer_churn GROUP BY `Payment Method`
            UNION ALL
            SELECT 'Internet Service' AS segment_type, `Internet Service` AS segment,
                   COUNT(*) AS total_customers,
                   SUM(Churn_Value) AS churned_customers,
                   ROUND(CAST(SUM(Churn_Value) AS FLOAT) / COUNT(*) * 100, 2) AS churn_rate_percent
            FROM gold_ibm_telco_customer_churn GROUP BY `Internet Service`
            UNION ALL
            SELECT 'Customer Tenure' AS segment_type, tenure_band AS segment,
                   COUNT(*) AS total_customers,
                   SUM(Churn_Value) AS churned_customers,
                   ROUND(CAST(SUM(Churn_Value) AS FLOAT) / COUNT(*) * 100, 2) AS churn_rate_percent
            FROM gold_ibm_telco_customer_churn GROUP BY tenure_band;
        """)

        # 3. Ingest and Clean TRAI Subscribers, Usage & QoS
        mnp_file = DATA_DIR / "trai_subscribers" / "mnp_service_area_status.csv"
        usage_file = DATA_DIR / "trai_usage" / "usage_by_service_area.csv"
        qos_file = DATA_DIR / "trai_qos" / "trai_qos_june_2026.csv"
        trends_file = DATA_DIR / "trai_usage" / "wireless_usage_trends.csv"
        fixed_bb_file = DATA_DIR / "trai_subscribers" / "fixed_wired_broadband.csv"
        wireless_bb_file = DATA_DIR / "trai_subscribers" / "wireless_broadband.csv"
        growth_rates_file = DATA_DIR / "trai_subscribers" / "circle_wise_growth_rates.csv"
        net_adds_file = DATA_DIR / "trai_subscribers" / "circle_wise_net_additions.csv"
        tele_base_file = DATA_DIR / "trai_subscribers" / "telephone_subscriber_base.csv"
        mobile_subs_file = DATA_DIR / "trai_subscribers" / "wireless_mobile_subscribers.csv"

        mnp = pd.read_csv(mnp_file)
        usage = pd.read_csv(usage_file)
        qos = pd.read_csv(qos_file)
        trends = pd.read_csv(trends_file)
        fixed_bb = pd.read_csv(fixed_bb_file)
        wireless_bb = pd.read_csv(wireless_bb_file)
        growth_rates = pd.read_csv(growth_rates_file)
        net_adds = pd.read_csv(net_adds_file)
        tele_base = pd.read_csv(tele_base_file)
        mobile_subs = pd.read_csv(mobile_subs_file)

        # Standardise and Clean Usage
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

        # Build Gold TRAI Context table (exact join contract from 01_bronze_ingestion.ipynb)
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

        # Register TRAI tables
        trai_gold.to_sql("gold_trai_lsa_switching_usage_context", self._sqlite_conn, index=False, if_exists="replace")
        qos.to_sql("silver_trai_qos", self._sqlite_conn, index=False, if_exists="replace")
        trends.to_sql("gold_trai_national_wireless_usage_trends", self._sqlite_conn, index=False, if_exists="replace")
        fixed_bb.to_sql("silver_trai_fixed_wired_broadband", self._sqlite_conn, index=False, if_exists="replace")
        wireless_bb.to_sql("silver_trai_wireless_broadband", self._sqlite_conn, index=False, if_exists="replace")
        growth_rates.to_sql("silver_trai_circle_wise_growth_rates", self._sqlite_conn, index=False, if_exists="replace")
        net_adds.to_sql("silver_trai_circle_wise_net_additions", self._sqlite_conn, index=False, if_exists="replace")
        tele_base.to_sql("silver_trai_telephone_subscriber_base", self._sqlite_conn, index=False, if_exists="replace")
        mobile_subs.to_sql("silver_trai_wireless_mobile_subscribers", self._sqlite_conn, index=False, if_exists="replace")

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """
        Execute an analytical SQL query against Databricks or local fallback database.
        Maps 'workspace.gold.*' and 'workspace.silver.*' table names to corresponding local tables.
        """
        if self._is_databricks:
            from databricks import sql
            with sql.connect(
                server_hostname=os.getenv("DATABRICKS_SERVER_HOSTNAME"),
                http_path=os.getenv("DATABRICKS_HTTP_PATH"),
                access_token=os.getenv("DATABRICKS_TOKEN")
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchall_arrow()
                    return result.to_pandas()
        else:
            # Normalize Databricks 3-part / 2-part table references for local SQLite
            local_query = query
            table_mappings = {
                "workspace.gold.trai_lsa_switching_usage_context": "gold_trai_lsa_switching_usage_context",
                "workspace.gold.trai_national_wireless_usage_trends": "gold_trai_national_wireless_usage_trends",
                "workspace.gold.ibm_churn_overview": "gold_ibm_telco_customer_churn",
                "workspace.gold.ibm_churn_segment_analysis": "gold_ibm_churn_segment_analysis",
                "workspace.silver.ibm_telco_customer_churn": "silver_ibm_telco_customer_churn",
                "workspace.silver.trai_qos": "silver_trai_qos",
                "workspace.silver.trai_fixed_wired_broadband": "silver_trai_fixed_wired_broadband",
                "workspace.silver.trai_wireless_broadband": "silver_trai_wireless_broadband",
                "workspace.silver.trai_circle_wise_growth_rates": "silver_trai_circle_wise_growth_rates",
                "workspace.silver.trai_circle_wise_net_additions": "silver_trai_circle_wise_net_additions",
                "workspace.silver.trai_telephone_subscriber_base": "silver_trai_telephone_subscriber_base",
                "workspace.silver.trai_wireless_mobile_subscribers": "silver_trai_wireless_mobile_subscribers",
                # Handle 2-part catalog.schema syntax
                "gold.trai_lsa_switching_usage_context": "gold_trai_lsa_switching_usage_context",
                "gold.ibm_churn_segment_analysis": "gold_ibm_churn_segment_analysis",
                "silver.trai_qos": "silver_trai_qos"
            }
            for remote, local in table_mappings.items():
                local_query = local_query.replace(remote, local)

            return pd.read_sql_query(local_query, self._sqlite_conn, params=params)

    def get_trai_gold_df(self) -> pd.DataFrame:
        """Return the complete TRAI Gold analytical DataFrame."""
        return self.execute_query("SELECT * FROM workspace.gold.trai_lsa_switching_usage_context")

    def get_ibm_df(self) -> pd.DataFrame:
        """Return the complete IBM Customer Churn DataFrame."""
        return self.execute_query("SELECT * FROM workspace.silver.ibm_telco_customer_churn")

    def get_qos_df(self) -> pd.DataFrame:
        """Return the TRAI QoS DataFrame."""
        return self.execute_query("SELECT * FROM workspace.silver.trai_qos")

    def get_national_trends_df(self) -> pd.DataFrame:
        """Return the TRAI National Wireless Trends DataFrame."""
        return self.execute_query("SELECT * FROM workspace.gold.trai_national_wireless_usage_trends")

    def get_broadband_df(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Return fixed wired and wireless broadband DataFrames."""
        fixed = self.execute_query("SELECT * FROM workspace.silver.trai_fixed_wired_broadband")
        wireless = self.execute_query("SELECT * FROM workspace.silver.trai_wireless_broadband")
        return fixed, wireless


def get_db():
    """Convenience helper to obtain the singleton data loader."""
    return TelecomDataLoader.get_instance()
