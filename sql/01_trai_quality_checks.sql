-- =====================================================================
-- TelecomNexus - Member 3: SQL Analytics & Power BI
-- Script 01: TRAI Data Quality & Integrity Checks
-- Purpose: Validate table grain, row counts, canonical LSAs, and nulls
-- Target: workspace.silver and workspace.gold tables
-- =====================================================================

USE CATALOG workspace;
USE SCHEMA gold;

-- ---------------------------------------------------------------------
-- 1. Inspect Table Inventory & Row Counts
-- ---------------------------------------------------------------------
-- Verify TRAI Gold Context row count (Expected: exactly 22 LSAs)
SELECT 
    'trai_lsa_switching_usage_context' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT canonical_lsa) AS distinct_lsas
FROM workspace.gold.trai_lsa_switching_usage_context;

-- Verify TRAI QoS Silver row count (Expected: 88 rows = 4 operators x 22 LSAs)
SELECT 
    'trai_qos' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT operator) AS distinct_operators,
    COUNT(DISTINCT lsa) AS distinct_lsas
FROM workspace.silver.trai_qos;

-- Verify National Trends row count (Expected: 5 reporting quarters)
SELECT 
    'trai_national_wireless_usage_trends' AS table_name,
    COUNT(*) AS total_quarters
FROM workspace.gold.trai_national_wireless_usage_trends;


-- ---------------------------------------------------------------------
-- 2. Verify Canonical LSA Join Uniqueness (Grain = 1 row per LSA)
-- ---------------------------------------------------------------------
SELECT 
    canonical_lsa, 
    COUNT(*) AS records_per_lsa
FROM workspace.gold.trai_lsa_switching_usage_context
GROUP BY canonical_lsa
HAVING COUNT(*) > 1;
-- Expected output: 0 rows (no duplicates)


-- ---------------------------------------------------------------------
-- 3. Verify Null Handling in Gold Context
-- ---------------------------------------------------------------------
SELECT
    SUM(CASE WHEN canonical_lsa IS NULL THEN 1 ELSE 0 END) AS null_lsas,
    SUM(CASE WHEN zone IS NULL THEN 1 ELSE 0 END) AS null_zones,
    SUM(CASE WHEN may_2026_porting_requests_millions IS NULL THEN 1 ELSE 0 END) AS null_may_porting,
    SUM(CASE WHEN june_2026_porting_requests_millions IS NULL THEN 1 ELSE 0 END) AS null_june_porting,
    SUM(CASE WHEN arpu_inr_per_month IS NULL THEN 1 ELSE 0 END) AS null_arpu,
    SUM(CASE WHEN prepaid_percentage IS NULL THEN 1 ELSE 0 END) AS null_prepaid_pct
FROM workspace.gold.trai_lsa_switching_usage_context;
-- Expected output: All 0s


-- ---------------------------------------------------------------------
-- 4. Audit QoS Missing Values (RJIL & MTNL Source-Level N/A)
-- ---------------------------------------------------------------------
-- Note: As per metadata/trai_qos_data_quality_report.md, missing values
-- are NOT errors and must remain NULL (never replaced with 0).
SELECT 
    operator,
    COUNT(*) AS circle_count,
    SUM(CASE WHEN metric_08 IS NULL THEN 1 ELSE 0 END) AS null_metric_08_cs_dcr,
    SUM(CASE WHEN metric_09 IS NULL THEN 1 ELSE 0 END) AS null_metric_09_ps_dcr,
    SUM(CASE WHEN metric_12 IS NULL THEN 1 ELSE 0 END) AS null_metric_12_latency
FROM workspace.silver.trai_qos
GROUP BY operator
ORDER BY operator;
-- Verification:
-- RJIL has 22 NULLs for metric_08 (All-IP LTE/5G network, no circuit-switched infrastructure)
-- MTNL has 2 NULLs for metrics 09-13 (absence of 4G/5G deployment)
