-- =====================================================================
-- TelecomNexus - Member 3: SQL Analytics & Power BI
-- Script 02: TRAI Regulatory & Industry KPIs
-- Purpose: Extract exact metrics for Power BI Cards, Charts & Slicers
-- Target: workspace.gold.trai_lsa_switching_usage_context,
--         workspace.gold.trai_national_wireless_usage_trends,
--         workspace.silver.trai_qos
-- =====================================================================

USE CATALOG workspace;
USE SCHEMA gold;

-- ---------------------------------------------------------------------
-- 1. Headline Industry KPI Cards (Control Values for Power BI Cards)
-- ---------------------------------------------------------------------
SELECT
    COUNT(DISTINCT canonical_lsa) AS total_active_lsas,
    COUNT(DISTINCT zone) AS total_zones,
    -- MNP Porting Volume (Unit: Millions of Requests)
    ROUND(SUM(may_2026_porting_requests_millions), 2) AS total_may_porting_requests_m,
    ROUND(SUM(june_2026_porting_requests_millions), 2) AS total_june_porting_requests_m,
    -- Net Change & Growth
    ROUND(SUM(june_2026_porting_requests_millions) - SUM(may_2026_porting_requests_millions), 2) AS net_porting_change_m,
    ROUND(
        ((SUM(june_2026_porting_requests_millions) - SUM(may_2026_porting_requests_millions)) 
        / SUM(may_2026_porting_requests_millions)) * 100, 2
    ) AS porting_growth_pct,
    -- Unweighted Service-Area Averages (Label clearly as unweighted)
    ROUND(AVG(arpu_inr_per_month), 2) AS unweighted_avg_arpu_inr,
    ROUND(AVG(prepaid_percentage), 2) AS unweighted_avg_prepaid_pct,
    ROUND(AVG(total_mou_per_month), 1) AS unweighted_avg_total_mou
FROM workspace.gold.trai_lsa_switching_usage_context;
-- Control Baseline:
-- May MNP: 14.47 Million
-- June MNP: 14.79 Million
-- MoM Growth: +2.21%
-- Unweighted Avg ARPU: ₹ 187.95
-- Unweighted Avg Prepaid: 82.77%


-- ---------------------------------------------------------------------
-- 2. Power BI Page 1: Porting Requests by LSA (Clustered Bar Chart)
-- ---------------------------------------------------------------------
SELECT
    canonical_lsa,
    zone,
    category,
    ROUND(may_2026_porting_requests_millions, 3) AS may_requests_m,
    ROUND(june_2026_porting_requests_millions, 3) AS june_requests_m,
    ROUND(june_2026_porting_requests_millions - may_2026_porting_requests_millions, 3) AS mom_net_change_m
FROM workspace.gold.trai_lsa_switching_usage_context
ORDER BY june_requests_m DESC;


-- ---------------------------------------------------------------------
-- 3. Power BI Page 1: Porting Requests by Geographic Zone
-- ---------------------------------------------------------------------
SELECT
    zone,
    COUNT(DISTINCT canonical_lsa) AS circle_count,
    ROUND(SUM(may_2026_porting_requests_millions), 2) AS may_requests_m,
    ROUND(SUM(june_2026_porting_requests_millions), 2) AS june_requests_m,
    ROUND(
        (SUM(june_2026_porting_requests_millions) / 
        (SELECT SUM(june_2026_porting_requests_millions) FROM workspace.gold.trai_lsa_switching_usage_context)) * 100, 1
    ) AS share_of_national_porting_pct
FROM workspace.gold.trai_lsa_switching_usage_context
GROUP BY zone
ORDER BY june_requests_m DESC;


-- ---------------------------------------------------------------------
-- 4. Power BI Page 2: Service Consumption (ARPU & MOU by LSA)
-- ---------------------------------------------------------------------
SELECT
    canonical_lsa,
    zone,
    category,
    arpu_inr_per_month,
    prepaid_percentage,
    outgoing_mou_per_month,
    incoming_mou_per_month,
    total_mou_per_month,
    outgoing_sms_per_month
FROM workspace.gold.trai_lsa_switching_usage_context
ORDER BY arpu_inr_per_month DESC;


-- ---------------------------------------------------------------------
-- 5. Power BI Page 2: 5-Quarter National Wireless Trends (Line Chart)
-- ---------------------------------------------------------------------
SELECT
    reporting_period,
    arpu_inr_per_month,
    revenue_realization_per_gb_inr,
    mou_per_subscriber,
    local_outgoing_mou,
    nld_outgoing_mou
FROM workspace.gold.trai_national_wireless_usage_trends
ORDER BY reporting_period ASC;


-- ---------------------------------------------------------------------
-- 6. Power BI Page 3: TRAI QoS Benchmarking by Operator
-- ---------------------------------------------------------------------
-- Selected key parameters from 13 reported metrics
SELECT
    operator,
    COUNT(*) AS reported_circles,
    ROUND(AVG(metric_02), 2) AS avg_cell_downtime_pct,
    ROUND(AVG(metric_05), 2) AS call_setup_success_intra_pct,
    ROUND(AVG(metric_06), 2) AS call_setup_success_inter_pct,
    ROUND(AVG(metric_12), 2) AS avg_4g_5g_latency_ms,
    ROUND(AVG(metric_13), 2) AS avg_packet_drop_rate_pct
FROM workspace.silver.trai_qos
GROUP BY operator
ORDER BY avg_4g_5g_latency_ms ASC;
