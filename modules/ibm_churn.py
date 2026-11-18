"""
IBM Customer Churn Analytics Module.

Presents enterprise customer-level churn intelligence covering:
- Executive KPI Metrics (Total, Churned, Retained, Churn Rate %, Avg Monthly Charges)
- Strategic Churn Drivers (Contract, Payment Method, Internet Service, Tenure Bands)
- Financial Exposure & Monthly Charges Distribution
- Customer Segmentation, Reason Breakdown & High-Risk Drilldown
- Interactive Cohort Filtering & Data Export
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
    ACCENT_GREEN,
    ACCENT_RED,
    ACCENT_AMBER,
    CHURN_COLOR_MAP
)


def render_ibm_dashboard():
    """Render the full IBM Telco Customer Churn Analytics Module."""
    db = get_db()
    raw_df = db.get_ibm_df()

    # Module Header
    st.markdown("""
        <div class="telecom-header">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h1>IBM Customer Churn Analytics</h1>
                    <p>Enterprise Churn Drivers, Retention Diagnostics, Cohort Segmentation & Financial Impact</p>
                </div>
                <span class="badge badge-live">Dataset Grain: Customer-Level (7,043 Records)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # Sidebar Filters
    # ----------------------------------------------------
    st.sidebar.markdown("### 🔍 Customer Filters")

    # Contract Filter
    contracts = sorted(raw_df["Contract"].dropna().unique().tolist())
    selected_contracts = st.sidebar.multiselect("Contract Type", options=contracts, default=contracts)

    # Internet Service Filter
    internet_services = sorted(raw_df["Internet Service"].dropna().unique().tolist())
    selected_services = st.sidebar.multiselect("Internet Service", options=internet_services, default=internet_services)

    # Payment Method Filter
    payment_methods = sorted(raw_df["Payment Method"].dropna().unique().tolist())
    selected_payments = st.sidebar.multiselect("Payment Method", options=payment_methods, default=payment_methods)

    # Demographic Filters (Expandable)
    with st.sidebar.expander("Demographic & Tenure Filters", expanded=False):
        genders = sorted(raw_df["Gender"].dropna().unique().tolist())
        selected_genders = st.multiselect("Gender", options=genders, default=genders)

        senior_citizens = sorted(raw_df["Senior_Citizen"].dropna().unique().tolist())
        selected_seniors = st.multiselect("Senior Citizen", options=senior_citizens, default=senior_citizens)

        min_tenure = int(raw_df["Tenure_Months"].min())
        max_tenure = int(raw_df["Tenure_Months"].max())
        tenure_range = st.slider("Tenure (Months)", min_value=min_tenure, max_value=max_tenure, value=(min_tenure, max_tenure))

        min_charge = float(raw_df["Monthly_Charges"].min())
        max_charge = float(raw_df["Monthly_Charges"].max())
        charge_range = st.slider("Monthly Charges ($)", min_value=min_charge, max_value=max_charge, value=(min_charge, max_charge))

    # Apply Filters
    filtered_df = raw_df[
        (raw_df["Contract"].isin(selected_contracts)) &
        (raw_df["Internet Service"].isin(selected_services)) &
        (raw_df["Payment Method"].isin(selected_payments)) &
        (raw_df["Gender"].isin(selected_genders)) &
        (raw_df["Senior_Citizen"].isin(selected_seniors)) &
        (raw_df["Tenure_Months"] >= tenure_range[0]) &
        (raw_df["Tenure_Months"] <= tenure_range[1]) &
        (raw_df["Monthly_Charges"] >= charge_range[0]) &
        (raw_df["Monthly_Charges"] <= charge_range[1])
    ]

    # ----------------------------------------------------
    # 1. Executive KPI Cards
    # ----------------------------------------------------
    st.markdown('<div class="section-header"><div class="section-title">📊 Churn Key Performance Indicators</div></div>', unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("⚠️ No customers match the selected filter criteria. Please adjust your filters.")
        return

    total_customers = len(filtered_df)
    churned_customers = (filtered_df["Churn_Value"] == 1).sum()
    retained_customers = (filtered_df["Churn_Value"] == 0).sum()
    churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0
    avg_monthly_charges = filtered_df["Monthly_Charges"].mean()
    avg_tenure = filtered_df["Tenure_Months"].mean()

    # Compare with baseline (unfiltered total churn rate 26.54%)
    baseline_churn_rate = 26.54
    churn_rate_diff = churn_rate - baseline_churn_rate

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

    with kpi1:
        st.markdown(format_kpi_card(
            label="Total Customers",
            value=f"{total_customers:,}",
            delta=f"{total_customers / len(raw_df) * 100:.1f}% of base",
            delta_type="neutral",
            help_text="Total number of customer accounts in filtered cohort"
        ), unsafe_allow_html=True)

    with kpi2:
        st.markdown(format_kpi_card(
            label="Churned Accounts",
            value=f"{churned_customers:,}",
            delta="Departed Customers",
            delta_type="negative",
            help_text="Total customers who discontinued service"
        ), unsafe_allow_html=True)

    with kpi3:
        st.markdown(format_kpi_card(
            label="Churn Rate",
            value=f"{churn_rate:.2f}%",
            delta=f"{churn_rate_diff:+.1f}% vs Baseline",
            delta_type="negative" if churn_rate_diff > 0 else "positive",
            help_text="Proportion of customer base lost (Target < 15%)"
        ), unsafe_allow_html=True)

    with kpi4:
        st.markdown(format_kpi_card(
            label="Retained Accounts",
            value=f"{retained_customers:,}",
            delta=f"{retained_customers / total_customers * 100:.1f}% Active",
            delta_type="positive",
            help_text="Customers who remain active"
        ), unsafe_allow_html=True)

    with kpi5:
        st.markdown(format_kpi_card(
            label="Avg Monthly Bill",
            value=f"${avg_monthly_charges:.2f}",
            delta="Per subscriber/month",
            delta_type="neutral",
            help_text="Average recurring revenue per subscriber"
        ), unsafe_allow_html=True)

    with kpi6:
        st.markdown(format_kpi_card(
            label="Average Tenure",
            value=f"{avg_tenure:.1f} Mo",
            delta="Customer Lifetime",
            delta_type="neutral",
            help_text="Average duration of customer relationship"
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # 2. Strategic Visualizations Tabs
    # ----------------------------------------------------
    tabs = st.tabs([
        "🎯 Core Churn Drivers",
        "💵 Financial & Revenue Impact",
        "🚨 High-Risk Segmentation",
        "📋 Customer Drilldown & Export",
        "🔮 What-If Churn & ROI Simulator"
    ])

    # TAB 1: Core Churn Drivers
    with tabs[0]:
        st.markdown("### Strategic Churn Drivers & Behavioral Analysis")
        col_d1, col_d2 = st.columns(2)

        with col_d1:
            # 1. Churn by Contract Type
            contract_churn = filtered_df.groupby("Contract").agg(
                total=("CustomerID", "count"),
                churned=("Churn_Value", "sum")
            ).reset_index()
            contract_churn["churn_rate"] = (contract_churn["churned"] / contract_churn["total"] * 100).round(2)

            fig_contract = px.bar(
                contract_churn,
                x="Contract",
                y="churn_rate",
                text="churn_rate",
                title="Churn Rate by Contract Type (%)",
                color="churn_rate",
                color_continuous_scale=["#10B981", "#EF4444"]
            )
            fig_contract.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            apply_plotly_theme(fig_contract, height=340, yaxis_title="Churn Rate (%)", coloraxis_showscale=False)
            render_chart(fig_contract)

        with col_d2:
            # 2. Churn by Payment Method
            pay_churn = filtered_df.groupby("Payment Method").agg(
                total=("CustomerID", "count"),
                churned=("Churn_Value", "sum")
            ).reset_index()
            pay_churn["churn_rate"] = (pay_churn["churned"] / pay_churn["total"] * 100).round(2)
            pay_churn = pay_churn.sort_values(by="churn_rate", ascending=True)

            fig_pay = px.bar(
                pay_churn,
                y="Payment Method",
                x="churn_rate",
                text="churn_rate",
                orientation="h",
                title="Churn Rate by Payment Method (%)",
                color="churn_rate",
                color_continuous_scale=["#10B981", "#EF4444"]
            )
            fig_pay.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            apply_plotly_theme(fig_pay, height=340, xaxis_title="Churn Rate (%)", coloraxis_showscale=False)
            render_chart(fig_pay)

        col_d3, col_d4 = st.columns(2)

        with col_d3:
            # 3. Churn by Internet Service
            service_churn = filtered_df.groupby("Internet Service").agg(
                total=("CustomerID", "count"),
                churned=("Churn_Value", "sum")
            ).reset_index()
            service_churn["churn_rate"] = (service_churn["churned"] / service_churn["total"] * 100).round(2)

            fig_service = px.bar(
                service_churn,
                x="Internet Service",
                y="churn_rate",
                text="churn_rate",
                title="Churn Rate by Internet Service Type (%)",
                color="churn_rate",
                color_continuous_scale=["#10B981", "#EF4444"]
            )
            fig_service.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            apply_plotly_theme(fig_service, height=340, yaxis_title="Churn Rate (%)", coloraxis_showscale=False)
            render_chart(fig_service)

        with col_d4:
            # 4. Churn by Customer Tenure Bands
            tenure_churn = filtered_df.groupby("tenure_band").agg(
                total=("CustomerID", "count"),
                churned=("Churn_Value", "sum")
            ).reset_index()
            tenure_churn["churn_rate"] = (tenure_churn["churned"] / tenure_churn["total"] * 100).round(2)

            # Sort by canonical order
            order = ["0-12 months", "13-24 months", "25-48 months", "49+ months"]
            tenure_churn["sort_order"] = tenure_churn["tenure_band"].map({k: i for i, k in enumerate(order)})
            tenure_churn = tenure_churn.sort_values(by="sort_order")

            fig_tenure = px.bar(
                tenure_churn,
                x="tenure_band",
                y="churn_rate",
                text="churn_rate",
                title="Churn Rate by Tenure Cohort (%)",
                color="churn_rate",
                color_continuous_scale=["#10B981", "#EF4444"]
            )
            fig_tenure.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            apply_plotly_theme(fig_tenure, height=340, yaxis_title="Churn Rate (%)", coloraxis_showscale=False)
            render_chart(fig_tenure)

    # TAB 2: Financial & Revenue Impact
    with tabs[1]:
        st.markdown("### Pricing Pressure & Financial Exposure")
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            # Monthly Charges Boxplot: Retained vs Churned
            fig_box = px.box(
                filtered_df,
                x="Churn Label",
                y="Monthly_Charges",
                color="Churn Label",
                color_discrete_map={"No": "#10B981", "Yes": "#EF4444"},
                title="Monthly Charges Distribution: Retained vs Churned ($)",
                points="outliers"
            )
            apply_plotly_theme(fig_box, height=360, yaxis_title="Monthly Charges ($)")
            render_chart(fig_box)

        with col_f2:
            # Revenue Exposure: Monthly recurring revenue at risk vs retained
            rev_exposure = filtered_df.groupby("Churn Label")["Monthly_Charges"].sum().reset_index()
            rev_exposure.columns = ["Status", "Total_Monthly_Revenue"]

            fig_rev = px.pie(
                rev_exposure,
                names="Status",
                values="Total_Monthly_Revenue",
                title="Total Monthly Recurring Revenue (MRR) Breakdown",
                color="Status",
                color_discrete_map={"No": "#10B981", "Yes": "#EF4444"},
                hole=0.45
            )
            fig_rev.update_traces(textposition="inside", textinfo="percent+value")
            apply_plotly_theme(fig_rev, height=360)
            render_chart(fig_rev)

        # Churn Reasons Pareto
        churn_reasons = (
            filtered_df[filtered_df["Churn_Value"] == 1]["Churn Reason"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        churn_reasons.columns = ["Reason", "Count"]

        if not churn_reasons.empty:
            st.markdown("#### Primary Customer Exit Drivers (Top 10 Recorded Reasons)")
            fig_reasons = px.bar(
                churn_reasons,
                x="Count",
                y="Reason",
                orientation="h",
                text="Count",
                color="Count",
                color_continuous_scale=["#FCA5A5", "#DC2626"]
            )
            apply_plotly_theme(
                fig_reasons,
                height=350,
                coloraxis_showscale=False,
                xaxis_title="Number of Churned Customers"
            )
            fig_reasons.update_yaxes(autorange="reversed")
            render_chart(fig_reasons)

    # TAB 3: High-Risk Segmentation
    with tabs[2]:
        st.markdown("### Predictive Churn Score & Customer Risk Matrix")

        col_s1, col_s2 = st.columns(2)

        with col_s1:
            # Churn Score Distribution
            fig_score = px.histogram(
                filtered_df,
                x="Churn_Score",
                color="Churn Label",
                nbins=30,
                color_discrete_map={"No": "#10B981", "Yes": "#EF4444"},
                title="Churn Score Frequency Distribution (0 = Lowest Risk, 100 = Highest Risk)",
                barmode="overlay",
                opacity=0.75
            )
            apply_plotly_theme(fig_score, height=340, xaxis_title="Churn Score", yaxis_title="Customer Count")
            render_chart(fig_score)

        with col_s2:
            # Customer Lifetime Value (CLTV) vs Churn Score
            sample_size = min(800, len(filtered_df))
            sampled_df = filtered_df.sample(sample_size, random_state=42) if sample_size > 0 else filtered_df
            fig_scatter = px.scatter(
                sampled_df,
                x="Tenure_Months",
                y="CLTV",
                color="Churn Label",
                color_discrete_map={"No": "#10B981", "Yes": "#EF4444"},
                title="Customer Lifetime Value (CLTV) vs Tenure (Sampled View)",
                opacity=0.7
            )
            apply_plotly_theme(fig_scatter, height=340, xaxis_title="Tenure (Months)", yaxis_title="CLTV")
            render_chart(fig_scatter)

    # TAB 4: Customer Drilldown & Export
    with tabs[3]:
        st.markdown("### Filtered Customer Cohort Drilldown")
        st.caption("Inspect individual customer profiles, contract terms, churn scores, and recorded reasons.")

        display_cols = [
            "CustomerID", "Gender", "Senior_Citizen", "Tenure_Months", "Contract",
            "Internet Service", "Payment Method", "Monthly_Charges", "Total_Charges",
            "Churn Label", "Churn_Score", "CLTV", "Churn Reason"
        ]

        render_dataframe(
            filtered_df[display_cols].sort_values(by="Churn_Score", ascending=False).head(100),
            hide_index=True
        )

    # TAB 5: What-If Churn & ROI Simulator
    with tabs[4]:
        st.markdown("### Interactive Retention Scenario & Financial ROI Simulator")
        st.markdown("Simulate targeted retention interventions and project their financial impact on recurring revenue and customer lifetime.")

        sim_col1, sim_col2 = st.columns([5, 7])

        with sim_col1:
            st.markdown("#### ⚙️ Retention Intervention Levers")
            contract_convert_pct = st.slider(
                "Convert Month-to-Month customers to 1-Year Contracts (%):",
                min_value=0, max_value=60, value=25, step=5,
                help="Month-to-month contracts churn at 42.7% vs 11.3% for 1-year contracts."
            )
            pay_convert_pct = st.slider(
                "Shift Electronic Check users to Automated Auto-Pay (%):",
                min_value=0, max_value=60, value=20, step=5,
                help="Electronic checks churn at 45.3% vs ~16% for automated bank/card payments."
            )
            support_convert_pct = st.slider(
                "Target Tech Support bundle to Fiber Optic users (%):",
                min_value=0, max_value=50, value=15, step=5,
                help="Fiber optic accounts churn at 41.9% primarily due to support friction."
            )

            # Baseline calculations on filtered_df
            m2m_churned = len(filtered_df[(filtered_df["Contract"] == "Month-to-month") & (filtered_df["Churn_Value"] == 1)])
            echeck_churned = len(filtered_df[(filtered_df["Payment Method"] == "Electronic check") & (filtered_df["Churn_Value"] == 1)])
            fiber_churned = len(filtered_df[(filtered_df["Internet Service"] == "Fiber optic") & (filtered_df["Churn_Value"] == 1)])

            # Calculate incremental customers saved
            saved_contract = int(m2m_churned * (contract_convert_pct / 100.0) * (0.4271 - 0.1127))
            saved_pay = int(echeck_churned * (pay_convert_pct / 100.0) * (0.4529 - 0.1598))
            saved_support = int(fiber_churned * (support_convert_pct / 100.0) * 0.35)

            total_saved_customers = min(churned_customers, saved_contract + saved_pay + saved_support)
            monthly_rev_saved = total_saved_customers * avg_monthly_charges
            annual_rev_saved = monthly_rev_saved * 12
            new_churned = max(0, churned_customers - total_saved_customers)
            new_churn_rate = (new_churned / total_customers * 100) if total_customers > 0 else 0

        with sim_col2:
            st.markdown("#### 📈 Projected Financial & Retention Outcomes")
            s_kpi1, s_kpi2, s_kpi3 = st.columns(3)
            with s_kpi1:
                st.markdown(format_kpi_card(
                    label="Customers Saved",
                    value=f"{total_saved_customers:,}",
                    delta=f"{(total_saved_customers / max(1, churned_customers) * 100):.1f}% Churn Drop",
                    delta_type="positive",
                    help_text="Projected customer accounts retained through interventions"
                ), unsafe_allow_html=True)
            with s_kpi2:
                st.markdown(format_kpi_card(
                    label="Monthly MRR Protected",
                    value=f"${monthly_rev_saved:,.0f}",
                    delta="Per Month",
                    delta_type="positive",
                    help_text="Protected monthly recurring subscription revenue"
                ), unsafe_allow_html=True)
            with s_kpi3:
                st.markdown(format_kpi_card(
                    label="Annual Retained Value",
                    value=f"${annual_rev_saved:,.0f}",
                    delta="Annualized ROI",
                    delta_type="positive",
                    help_text="Annual retained customer revenue"
                ), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            # Visual comparison bar chart
            sim_chart_df = pd.DataFrame({
                "Scenario": ["Current Baseline", "Projected Post-Intervention"],
                "Churn Rate (%)": [churn_rate, new_churn_rate]
            })
            fig_sim = px.bar(
                sim_chart_df,
                x="Scenario",
                y="Churn Rate (%)",
                text="Churn Rate (%)",
                color="Scenario",
                color_discrete_sequence=["#EF4444", "#10B981"],
                title="Impact on Overall Churn Rate (%)"
            )
            fig_sim.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            apply_plotly_theme(fig_sim, height=280, yaxis_range=[0, max(35, churn_rate + 5)], showlegend=False)
            render_chart(fig_sim)

    # ----------------------------------------------------
    # Download & Data Export
    # ----------------------------------------------------
    st.markdown("---")
    col_d1, col_d2 = st.columns([8, 2])
    with col_d1:
        st.caption(f"Displaying {len(filtered_df):,} customers matching current filter criteria. Total dataset size: {len(raw_df):,} records.")
    with col_d2:
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        render_download_button(
            label="📥 Export Cohort (CSV)",
            data=csv_data,
            file_name="ibm_customer_churn_cohort.csv",
            mime="text/csv"
        )
