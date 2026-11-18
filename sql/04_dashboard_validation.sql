-- =====================================================================
-- TelecomNexus - Member 3: SQL Analytics & Power BI
-- Script 04: Dashboard Validation & Reconciliation Suite
-- Purpose: Validate Power BI numbers against Gold SQL queries (Audit Trail)
-- =====================================================================

USE CATALOG workspace;

-- ---------------------------------------------------------------------
-- 1. Reconciliation Test 1: Total Base & Churn Rate
-- ---------------------------------------------------------------------
-- Run this query to reconcile with the Power BI "Total Customers" and "Churn Rate" cards.
SELECT 
    'IBM Churn Reconciliation' AS test_name,
    COUNT(DISTINCT CustomerID) AS expected_powerbi_total_customers,
    SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS expected_powerbi_churned,
    ROUND(
        (CAST(SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS DOUBLE) 
        / COUNT(DISTINCT CustomerID)) * 100, 2
    ) AS expected_powerbi_churn_rate_pct
FROM workspace.silver.ibm_telco_customer_churn;
-- Expected Power BI values: 7,043 | 1,869 | 26.54%


-- ---------------------------------------------------------------------
-- 2. Reconciliation Test 2: Slicer Impact Test (Month-to-Month Filter)
-- ---------------------------------------------------------------------
-- Select 'Month-to-month' on the Power BI Contract slicer;
-- Verify the cards update exactly to the numbers below:
SELECT 
    'Contract Slicer: Month-to-month' AS test_name,
    COUNT(DISTINCT CustomerID) AS filtered_customers,
    SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS filtered_churned,
    ROUND(
        (CAST(SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS DOUBLE) 
        / COUNT(DISTINCT CustomerID)) * 100, 2
    ) AS filtered_churn_rate_pct,
    ROUND(AVG(Monthly_Charges), 2) AS filtered_avg_monthly_charges
FROM workspace.silver.ibm_telco_customer_churn
WHERE Contract = 'Month-to-month';
-- Expected Power BI values: 3,875 | 1,655 | 42.71% | $66.40


-- ---------------------------------------------------------------------
-- 3. Reconciliation Test 3: TRAI MNP National Totals
-- ---------------------------------------------------------------------
-- Verify Power BI Page 1 headline cards match:
SELECT
    'TRAI MNP Reconciliation' AS test_name,
    COUNT(DISTINCT canonical_lsa) AS active_circles,
    ROUND(SUM(may_2026_porting_requests_millions), 3) AS may_requests_millions,
    ROUND(SUM(june_2026_porting_requests_millions), 3) AS june_requests_millions,
    ROUND(
        SUM(june_2026_porting_requests_millions) - SUM(may_2026_porting_requests_millions), 3
    ) AS net_change_millions
FROM workspace.gold.trai_lsa_switching_usage_context;
-- Expected Power BI values: 22 | 14.470 M | 14.790 M | +0.320 M


-- ---------------------------------------------------------------------
-- 4. Reconciliation Test 4: TRAI Zone Slicer Test (Zone I Filter)
-- ---------------------------------------------------------------------
-- Select 'Zone I' on the Power BI Zone slicer;
-- Verify the cards update to:
SELECT
    'Zone Slicer: Zone I' AS test_name,
    COUNT(DISTINCT canonical_lsa) AS zone_circles,
    ROUND(SUM(may_2026_porting_requests_millions), 3) AS may_requests_millions,
    ROUND(SUM(june_2026_porting_requests_millions), 3) AS june_requests_millions,
    ROUND(AVG(arpu_inr_per_month), 2) AS unweighted_avg_arpu,
    ROUND(AVG(prepaid_percentage), 2) AS unweighted_avg_prepaid_pct
FROM workspace.gold.trai_lsa_switching_usage_context
WHERE zone = 'Zone I';
-- Expected Power BI values: 11 | 7.740 M | 7.960 M | ₹ 180.27 | 81.98%


-- ---------------------------------------------------------------------
-- 5. Reconciliation Test 5: Cartesian Join Multiplier Check
-- ---------------------------------------------------------------------
-- Verify that relationships in Power BI data model did NOT inflate records:
SELECT 
    'Gold Context Multiplier Check' AS test_name,
    COUNT(*) AS total_records,
    COUNT(DISTINCT canonical_lsa) AS distinct_lsas
FROM workspace.gold.trai_lsa_switching_usage_context;
-- If total_records > distinct_lsas (22), a relationship or join duplicated rows!
