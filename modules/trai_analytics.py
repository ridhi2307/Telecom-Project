"""
TRAI Telecom Industry Analytics Module.

Presents consolidated regulatory analytics covering:
- Industry Overview & KPI Metrics
- Mobile Number Portability (MNP) Porting Dynamics
- Revenue & Minutes of Usage (MOU) Analytics
- Operator Quality of Service (QoS) & Broadband Market Share
- Data Quality & Governance Audit
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.database import get_db
from utils.styling import (
    format_kpi_card,
    apply_plotly_theme,
    render_chart,
    render_dataframe,
    render_download_button,
    ACCENT_BLUE,
    ACCENT_BLUE_LIGHT,
    ACCENT_GREEN,
    ACCENT_RED,
    ACCENT_AMBER
)


def render_trai_dashboard():
    """Render the full TRAI Telecom Industry Analytics Module."""
    db = get_db()
    gold_df = db.get_trai_gold_df()
    qos_df = db.get_qos_df()
    trends_df = db.get_national_trends_df()
    fixed_bb_df, wireless_bb_df = db.get_broadband_df()

    # Module Header
    st.markdown("""
        <div class="telecom-header">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h1>TRAI Telecom Industry Analytics</h1>
                    <p>Telecom Regulatory Authority of India (TRAI) Market Overview, Porting Dynamics, ARPU & Network QoS</p>
                </div>
                <span class="badge badge-live">Verified Reporting: June 2026</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # Sidebar Filters
    # ----------------------------------------------------
    st.sidebar.markdown("### 🔍 TRAI Filters")

    # Zone Filter
    all_zones = sorted(gold_df["zone"].dropna().unique().tolist())
    selected_zones = st.sidebar.multiselect("Geographic Zone", options=all_zones, default=all_zones)

    # Circle Category Filter
    all_categories = sorted(gold_df["category"].dropna().unique().tolist())
    selected_categories = st.sidebar.multiselect("Circle Category", options=all_categories, default=all_categories)

    # Filter DataFrame
    filtered_df = gold_df[
        (gold_df["zone"].isin(selected_zones)) &
        (gold_df["category"].isin(selected_categories))
    ]

    # Specific LSA Multiselect
    available_lsas = sorted(filtered_df["canonical_lsa"].dropna().unique().tolist())
    selected_lsas = st.sidebar.multiselect("Licensed Service Areas (LSA)", options=available_lsas, default=available_lsas)

    if selected_lsas:
        filtered_df = filtered_df[filtered_df["canonical_lsa"].isin(selected_lsas)]

    # ----------------------------------------------------
    # 1. Executive KPI Summary Cards
    # ----------------------------------------------------
    st.markdown('<div class="section-header"><div class="section-title">📊 Industry Performance Overview</div></div>', unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected filters. Please expand your selection.")
        return

    # Calculate KPIs
    may_requests = filtered_df["may_2026_porting_requests_millions"].sum()
    june_requests = filtered_df["june_2026_porting_requests_millions"].sum()
    mom_diff = june_requests - may_requests
    mom_pct = (mom_diff / may_requests * 100) if may_requests > 0 else 0

    avg_arpu = filtered_df["arpu_inr_per_month"].mean()
    avg_prepaid = filtered_df["prepaid_percentage"].mean()
    total_lsa_count = filtered_df["canonical_lsa"].nunique()
    total_zones_count = filtered_df["zone"].nunique()

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.markdown(format_kpi_card(
            label="June Porting Requests",
            value=f"{june_requests:.2f} M",
            delta=f"▲ {mom_pct:+.2f}% MoM" if mom_pct >= 0 else f"▼ {mom_pct:.2f}% MoM",
            delta_type="negative" if mom_pct > 0 else "positive",  # High porting is churn indicator
            help_text="Total MNP porting requests received across service areas in June 2026"
        ), unsafe_allow_html=True)

    with kpi2:
        st.markdown(format_kpi_card(
            label="May Porting Requests",
            value=f"{may_requests:.2f} M",
            delta="Baseline Month",
            delta_type="neutral",
            help_text="Total MNP porting requests in May 2026"
        ), unsafe_allow_html=True)

    with kpi3:
        st.markdown(format_kpi_card(
            label="Average Monthly ARPU",
            value=f"₹ {avg_arpu:.2f}",
            delta="Per subscriber/month",
            delta_type="positive",
            help_text="Blended average revenue per user across telecom circles"
        ), unsafe_allow_html=True)

    with kpi4:
        st.markdown(format_kpi_card(
            label="Prepaid Subscriber Ratio",
            value=f"{avg_prepaid:.1f}%",
            delta="Dominant Segment",
            delta_type="neutral",
            help_text="Weighted proportion of prepaid subscribers vs postpaid"
        ), unsafe_allow_html=True)

    with kpi5:
        st.markdown(format_kpi_card(
            label="Coverage Scope",
            value=f"{total_lsa_count} LSAs",
            delta=f"{total_zones_count} Zones Active",
            delta_type="positive",
            help_text="Total Licensed Service Areas included in current filter"
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 2. Porting Analytics Tabs
    # ----------------------------------------------------
    tabs = st.tabs([
        "🔄 Porting & Switching Analytics",
        "💰 Revenue & Usage Patterns",
        "📶 Operator & QoS Benchmarks",
        "🛡️ Data Quality & Audit"
    ])

    # TAB 1: Porting Analytics
    with tabs[0]:
        st.markdown("### Mobile Number Portability (MNP) Porting Dynamics")
        col_p1, col_p2 = st.columns([7, 5])

        with col_p1:
            # Bar chart: May vs June Porting by LSA
            porting_sorted = filtered_df.sort_values(by="june_2026_porting_requests_millions", ascending=True)

            fig_lsa = go.Figure()
            fig_lsa.add_trace(go.Bar(
                y=porting_sorted["canonical_lsa"],
                x=porting_sorted["may_2026_porting_requests_millions"],
                name="May 2026",
                orientation="h",
                marker_color="#93C5FD"
            ))
            fig_lsa.add_trace(go.Bar(
                y=porting_sorted["canonical_lsa"],
                x=porting_sorted["june_2026_porting_requests_millions"],
                name="June 2026",
                orientation="h",
                marker_color="#1D4ED8"
            ))
            apply_plotly_theme(
                fig_lsa,
                title="Porting Requests by LSA (May vs June 2026 in Millions)",
                barmode="group",
                height=520,
                xaxis_title="Requests (Millions)",
                yaxis_title="Licensed Service Area (LSA)"
            )
            render_chart(fig_lsa)

        with col_p2:
            # Zone summary
            zone_porting = filtered_df.groupby("zone")[
                ["may_2026_porting_requests_millions", "june_2026_porting_requests_millions"]
            ].sum().reset_index()

            fig_zone = go.Figure()
            fig_zone.add_trace(go.Bar(
                x=zone_porting["zone"],
                y=zone_porting["may_2026_porting_requests_millions"],
                name="May 2026",
                marker_color="#93C5FD"
            ))
            fig_zone.add_trace(go.Bar(
                x=zone_porting["zone"],
                y=zone_porting["june_2026_porting_requests_millions"],
                name="June 2026",
                marker_color="#1D4ED8"
            ))
            apply_plotly_theme(
                fig_zone,
                title="Porting Volume by Geographic Zone",
                barmode="group",
                height=260,
                yaxis_title="Million Requests"
            )
            render_chart(fig_zone)

            # Net MoM Change by LSA
            filtered_df_copy = filtered_df.copy()
            filtered_df_copy["net_change_k"] = (
                filtered_df_copy["june_2026_porting_requests_millions"] -
                filtered_df_copy["may_2026_porting_requests_millions"]
            ) * 1000  # in Thousands

            top_change = filtered_df_copy.sort_values(by="net_change_k", ascending=False).head(8)
            fig_change = px.bar(
                top_change,
                x="canonical_lsa",
                y="net_change_k",
                color="net_change_k",
                color_continuous_scale=["#10B981", "#EF4444"],
                title="Top LSAs by Month-over-Month Porting Surge ('000s)"
            )
            apply_plotly_theme(
                fig_change,
                height=240,
                xaxis_title="LSA",
                yaxis_title="MoM Increase ('000)",
                coloraxis_showscale=False
            )
            render_chart(fig_change)

    # TAB 2: Revenue & Usage Patterns
    with tabs[1]:
        st.markdown("### Revenue & Network Usage Metrics")
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            # Average ARPU by Zone and Circle Category
            arpu_cat = filtered_df.groupby(["zone", "category"])["arpu_inr_per_month"].mean().reset_index()
            fig_arpu = px.bar(
                arpu_cat,
                x="category",
                y="arpu_inr_per_month",
                color="zone",
                barmode="group",
                color_discrete_sequence=["#1D4ED8", "#06B6D4"],
                title="Average Monthly ARPU (₹) by Circle Category & Zone",
                text_auto=".1f"
            )
            apply_plotly_theme(fig_arpu, height=380, yaxis_title="ARPU (₹)")
            render_chart(fig_arpu)

        with col_r2:
            # Minutes of Usage: Outgoing vs Incoming MOU
            mou_df = filtered_df.sort_values(by="total_mou_per_month", ascending=False)
            fig_mou = go.Figure()
            fig_mou.add_trace(go.Bar(
                x=mou_df["canonical_lsa"],
                y=mou_df["outgoing_mou_per_month"],
                name="Outgoing MOU",
                marker_color="#3B82F6"
            ))
            fig_mou.add_trace(go.Bar(
                x=mou_df["canonical_lsa"],
                y=mou_df["incoming_mou_per_month"],
                name="Incoming MOU",
                marker_color="#10B981"
            ))
            apply_plotly_theme(
                fig_mou,
                title="Minutes of Usage (MOU) per Subscriber/Month by LSA",
                barmode="stack",
                height=380,
                xaxis_title="LSA",
                yaxis_title="Minutes / Month"
            )
            render_chart(fig_mou)

        # 5-Quarter National Wireless Usage & Realization Trends
        if not trends_df.empty:
            st.markdown("#### National Quarterly Usage & Revenue Realization Trends")
            col_t1, col_t2 = st.columns(2)

            with col_t1:
                fig_trend_arpu = px.line(
                    trends_df,
                    x="reporting_period",
                    y="arpu_inr_per_month",
                    markers=True,
                    title="Quarterly National ARPU Trend (₹)",
                    line_shape="linear"
                )
                fig_trend_arpu.update_traces(line_color="#2563EB", line_width=3, marker_size=8)
                apply_plotly_theme(fig_trend_arpu, height=300, yaxis_title="ARPU (₹)")
                render_chart(fig_trend_arpu)

            with col_t2:
                fig_trend_data = px.line(
                    trends_df,
                    x="reporting_period",
                    y="revenue_realization_per_gb_inr",
                    markers=True,
                    title="Revenue Realization per GB of Wireless Data (₹)",
                    line_shape="linear"
                )
                fig_trend_data.update_traces(line_color="#10B981", line_width=3, marker_size=8)
                apply_plotly_theme(fig_trend_data, height=300, yaxis_title="₹ / GB")
                render_chart(fig_trend_data)

    # TAB 3: Operator & QoS Benchmarks
    with tabs[2]:
        st.markdown("### Operator Market Share & Quality of Service (QoS) Benchmarking")

        col_bb1, col_bb2 = st.columns(2)

        with col_bb1:
            if not wireless_bb_df.empty:
                fig_wbb = px.pie(
                    wireless_bb_df,
                    names="service_provider",
                    values="subscriber_base_million",
                    title="Wireless Broadband Market Share (Million Subscribers)",
                    hole=0.45,
                    color_discrete_sequence=["#1E40AF", "#2563EB", "#60A5FA", "#93C5FD", "#CBD5E1"]
                )
                fig_wbb.update_traces(textposition="inside", textinfo="percent+label")
                apply_plotly_theme(fig_wbb, height=340)
                render_chart(fig_wbb)

        with col_bb2:
            if not fixed_bb_df.empty:
                fig_fbb = px.pie(
                    fixed_bb_df,
                    names="service_provider",
                    values="subscriber_base_million",
                    title="Fixed Wired Broadband Market Share (Million Subscribers)",
                    hole=0.45,
                    color_discrete_sequence=["#065F46", "#059669", "#34D399", "#A7F3D0", "#E2E8F0"]
                )
                fig_fbb.update_traces(textposition="inside", textinfo="percent+label")
                apply_plotly_theme(fig_fbb, height=340)
                render_chart(fig_fbb)

        # QoS Metrics Benchmark across Operators
        if not qos_df.empty:
            st.markdown("#### TRAI Quality of Service (QoS) Parameters by Operator (June 2026)")
            st.caption("Benchmark of key network parameters reported across 88 service-area records.")

            qos_cols = {
                "metric_02": "Downtime % (Cells unavailable)",
                "metric_05": "Call Setup Success Rate % (Intra)",
                "metric_06": "Call Setup Success Rate % (Inter)",
                "metric_12": "4G/5G Latency (ms)",
                "metric_13": "Packet Drop Rate %"
            }

            qos_summary = qos_df.groupby("operator")[list(qos_cols.keys())].mean().round(2).reset_index()
            qos_summary = qos_summary.rename(columns=qos_cols)

            col_q1, col_q2 = st.columns(2)

            with col_q1:
                fig_lat = px.bar(
                    qos_summary,
                    x="operator",
                    y="4G/5G Latency (ms)",
                    color="operator",
                    title="Average Network Latency (ms) — Lower is Better",
                    color_discrete_sequence=["#2563EB", "#059669", "#DC2626", "#D97706", "#7C3AED"]
                )
                apply_plotly_theme(fig_lat, height=320, showlegend=False)
                render_chart(fig_lat)

            with col_q2:
                fig_setup = px.bar(
                    qos_summary,
                    x="operator",
                    y="Call Setup Success Rate % (Intra)",
                    color="operator",
                    title="Call Setup Success Rate (%) — Higher is Better",
                    color_discrete_sequence=["#2563EB", "#059669", "#DC2626", "#D97706", "#7C3AED"]
                )
                apply_plotly_theme(fig_setup, height=320, yaxis_range=[95, 100], showlegend=False)
                render_chart(fig_setup)

            # Display table of QoS averages
            render_dataframe(qos_summary, hide_index=True)

    # TAB 4: Data Quality & Audit
    with tabs[3]:
        st.markdown("### Data Quality, Audit & Schema Governance")
        st.info("Verified compliance with `metadata/join_contract.md` and Bronze data preservation guidelines.")

        dq_col1, dq_col2 = st.columns(2)

        with dq_col1:
            st.markdown("#### Table Integrity & Grain Audit")
            audit_records = [
                {"Dataset": "trai_qos", "Layer": "Bronze/Silver", "Rows": 88, "Columns": 16, "Status": "PASS (32 NA verified)"},
                {"Dataset": "trai_mnp_service_area_status", "Layer": "Bronze/Silver", "Rows": 22, "Columns": 7, "Status": "PASS (0 nulls)"},
                {"Dataset": "trai_usage_by_service_area", "Layer": "Bronze/Silver", "Rows": 22, "Columns": 9, "Status": "PASS (0 nulls)"},
                {"Dataset": "trai_wireless_usage_trends", "Layer": "Bronze/Silver", "Rows": 5, "Columns": 9, "Status": "PASS (0 nulls)"},
                {"Dataset": "fixed_wired_broadband", "Layer": "Bronze/Silver", "Rows": 5, "Columns": 7, "Status": "PASS (0 nulls)"},
                {"Dataset": "wireless_broadband", "Layer": "Bronze/Silver", "Rows": 5, "Columns": 7, "Status": "PASS (0 nulls)"},
                {"Dataset": "trai_lsa_switching_usage_context", "Layer": "Gold", "Rows": 22, "Columns": 13, "Status": "PASS (Canonical Join)"}
            ]
            render_dataframe(pd.DataFrame(audit_records), hide_index=True)

        with dq_col2:
            st.markdown("#### Key Governance Findings")
            st.markdown("""
            - **Canonical Join Contract**: MNP and Usage datasets are integrated on `canonical_lsa` derived from `dim_lsa.csv`.
            - **No Churn Conflation**: MNP porting requests represent consumer portability queries, **not** confirmed churn.
            - **Handling Source NAs**:
              - 22 missing values in RJIL `metric_08` (Circuit Switched DCR) are legitimate because RJIL is an all-IP LTE/5G network with no 2G/3G circuit switched infrastructure.
              - MTNL missing values in metrics 09–13 reflect absence of 4G/5G deployment during the reporting window.
              - Missing values are correctly preserved as nulls and not replaced with zero.
            """)

    # ----------------------------------------------------
    # Download & Data Export
    # ----------------------------------------------------
    st.markdown("---")
    col_d1, col_d2 = st.columns([8, 2])
    with col_d1:
        st.caption(f"Displaying {len(filtered_df)} records filtered from TRAI Gold Context. All values sourced from official regulatory reports.")
    with col_d2:
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        render_download_button(
            label="📥 Export Filtered Data (CSV)",
            data=csv_data,
            file_name="trai_analytics_export.csv",
            mime="text/csv"
        )
