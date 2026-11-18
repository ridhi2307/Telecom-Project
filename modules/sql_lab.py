"""
Interactive SQL Query Lab & Data Explorer Module.

Empowers evaluators, data analysts, and engineers to execute live ANSI SQL queries
against the Gold and Silver relational tables directly from the browser interface.
"""

import streamlit as st
import pandas as pd
import time
from utils.database import get_db
from utils.styling import (
    render_dataframe,
    render_download_button,
    render_button,
    format_kpi_card,
    NAVY_PRIMARY,
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_RED
)


# Curated SQL Query Templates
QUERY_TEMPLATES = {
    "1. High-Risk Customer Retention Targets": """-- Identify high-value customers at immediate risk of churn
SELECT
    CustomerID,
    Contract,
    `Payment Method` AS Payment_Method,
    `Internet Service` AS Internet_Service,
    Tenure_Months,
    Monthly_Charges,
    Churn_Score,
    CLTV
FROM workspace.silver.ibm_telco_customer_churn
WHERE Churn_Value = 0
  AND Churn_Score >= 75
  AND Contract = 'Month-to-month'
ORDER BY Monthly_Charges DESC, Churn_Score DESC
LIMIT 25;""",

    "2. Regional TRAI ARPU & MNP Volume by Zone": """-- Analyze switching pressure vs revenue by geographic zone
SELECT
    zone,
    COUNT(DISTINCT canonical_lsa) AS active_lsas,
    ROUND(SUM(may_2026_porting_requests_millions), 2) AS may_porting_requests_m,
    ROUND(SUM(june_2026_porting_requests_millions), 2) AS june_porting_requests_m,
    ROUND(AVG(arpu_inr_per_month), 2) AS avg_arpu_inr,
    ROUND(AVG(prepaid_percentage), 2) AS avg_prepaid_pct
FROM workspace.gold.trai_lsa_switching_usage_context
GROUP BY zone
ORDER BY june_porting_requests_m DESC;""",

    "3. QoS Operator Benchmark (Latency & Setup)": """-- Benchmark operator network quality across all circles
SELECT
    operator,
    COUNT(*) AS total_circles_measured,
    ROUND(AVG(metric_02), 2) AS avg_cell_downtime_pct,
    ROUND(AVG(metric_05), 2) AS call_setup_success_intra_pct,
    ROUND(AVG(metric_06), 2) AS call_setup_success_inter_pct,
    ROUND(AVG(metric_12), 2) AS avg_4g_5g_latency_ms,
    ROUND(AVG(metric_13), 2) AS avg_packet_drop_rate_pct
FROM workspace.silver.trai_qos
GROUP BY operator
ORDER BY avg_4g_5g_latency_ms ASC;""",

    "4. Churn Drivers Segmentation Mart": """-- Query the Gold Churn Segment Analysis table
SELECT
    segment_type,
    segment,
    total_customers,
    churned_customers,
    churn_rate_percent
FROM workspace.gold.ibm_churn_segment_analysis
ORDER BY churn_rate_percent DESC;""",

    "5. Broadband Provider Leadership Ranking": """-- Compare market share for fixed wired and wireless broadband
SELECT
    'Wireless' AS broadband_domain,
    service_provider,
    subscriber_base_million
FROM workspace.silver.trai_wireless_broadband
UNION ALL
SELECT
    'Fixed Wired' AS broadband_domain,
    service_provider,
    subscriber_base_million
FROM workspace.silver.trai_fixed_wired_broadband
ORDER BY subscriber_base_million DESC;"""
}


def render_sql_lab():
    """Render the Interactive SQL Query Lab."""
    db = get_db()
    is_live = db.is_databricks()

    st.markdown("""
        <div class="telecom-header">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                <div>
                    <h1>Interactive SQL Query Lab & Data Explorer</h1>
                    <p>Execute live analytical SQL queries against Databricks Gold / Silver tables directly in your browser</p>
                </div>
                <span class="badge badge-live">ANSI SQL Execution Engine</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_meta1, col_meta2 = st.columns([8, 4])

    with col_meta1:
        st.markdown("### 📝 SQL Query Editor")

        # Template Selector
        template_choice = st.selectbox(
            "Select an Analytical Query Template or Write Custom SQL:",
            options=list(QUERY_TEMPLATES.keys()),
            index=0
        )

        query_text = st.text_area(
            "SQL Query:",
            value=QUERY_TEMPLATES[template_choice],
            height=200,
            help="Supports standard SQL syntax and references to workspace.gold.* and workspace.silver.* tables."
        )

        execute_clicked = render_button("▶ Run Query", type="primary")

    with col_meta2:
        st.markdown("### 📚 Table Catalog")
        st.markdown("""
        **Gold Marts:**
        - `workspace.gold.trai_lsa_switching_usage_context`
        - `workspace.gold.trai_national_wireless_usage_trends`
        - `workspace.gold.ibm_churn_segment_analysis`

        **Silver Cleansed:**
        - `workspace.silver.ibm_telco_customer_churn`
        - `workspace.silver.trai_qos`
        - `workspace.silver.trai_fixed_wired_broadband`
        - `workspace.silver.trai_wireless_broadband`
        """)

    # Query Execution & Results
    if execute_clicked or "last_query" not in st.session_state:
        st.session_state["last_query"] = query_text

        st.markdown('<div class="section-header"><div class="section-title">📊 Query Results</div></div>', unsafe_allow_html=True)

        start_time = time.time()
        try:
            results_df = db.execute_query(query_text)
            elapsed_time = (time.time() - start_time) * 1000

            if results_df.empty:
                st.info("Query executed successfully. 0 rows returned.")
            else:
                st.success(f"Execution complete: **{len(results_df):,} rows** returned in **{elapsed_time:.1f} ms**.")
                render_dataframe(results_df, hide_index=True)

                # Export option
                csv_bytes = results_df.to_csv(index=False).encode("utf-8")
                render_download_button(
                    label="📥 Export Result as CSV",
                    data=csv_bytes,
                    file_name="sql_query_result.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"SQL Execution Error: {str(e)}")
            st.caption("Tip: Ensure table names match catalog entities such as `workspace.gold.trai_lsa_switching_usage_context`.")
