-- =====================================================================
-- TelecomNexus - Member 3: SQL Analytics & Power BI
-- Script 03: IBM Customer Churn KPIs & Segmentation
-- Purpose: Control SQL queries for Power BI Page 4 (IBM Customer Churn)
-- Target: workspace.silver.ibm_telco_customer_churn,
--         workspace.gold.ibm_churn_segment_analysis,
--         workspace.gold.ibm_churn_overview
-- =====================================================================

USE CATALOG workspace;
USE SCHEMA silver;

-- ---------------------------------------------------------------------
-- 1. Headline Retention KPI Cards (Control Values for Power BI Cards)
-- ---------------------------------------------------------------------
SELECT
    COUNT(DISTINCT CustomerID) AS total_customers,
    SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS churned_customers,
    SUM(CASE WHEN Churn_Value = 0 THEN 1 ELSE 0 END) AS retained_customers,
    -- Churn Rate Formula: Churned Customers / Total Customers * 100
    ROUND(
        (CAST(SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS DOUBLE) 
        / COUNT(DISTINCT CustomerID)) * 100, 2
    ) AS churn_rate_percent,
    -- Financial Exposure
    ROUND(AVG(Monthly_Charges), 2) AS avg_monthly_charges,
    ROUND(SUM(CASE WHEN Churn_Value = 1 THEN Monthly_Charges ELSE 0 END), 2) AS monthly_revenue_lost,
    ROUND(AVG(Tenure_Months), 1) AS avg_customer_tenure_months
FROM workspace.silver.ibm_telco_customer_churn;
-- Control Baseline:
-- Total Customers: 7,043
-- Churned: 1,869
-- Retained: 5,174
-- Churn Rate: 26.54%
-- Avg Monthly Charges: $64.76
-- Avg Tenure: 32.4 months


-- ---------------------------------------------------------------------
-- 2. Power BI Page 4: Churn Rate by Contract Type (Bar Chart)
-- ---------------------------------------------------------------------
SELECT
    Contract,
    COUNT(DISTINCT CustomerID) AS total_customers,
    SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        (CAST(SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS DOUBLE) 
        / COUNT(DISTINCT CustomerID)) * 100, 2
    ) AS churn_rate_percent
FROM workspace.silver.ibm_telco_customer_churn
GROUP BY Contract
ORDER BY churn_rate_percent DESC;
-- Baseline:
-- Month-to-month: 42.71%
-- One year: 11.27%
-- Two year: 2.83%


-- ---------------------------------------------------------------------
-- 3. Power BI Page 4: Churn Rate by Payment Method (Bar Chart)
-- ---------------------------------------------------------------------
SELECT
    `Payment Method` AS payment_method,
    COUNT(DISTINCT CustomerID) AS total_customers,
    SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        (CAST(SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS DOUBLE) 
        / COUNT(DISTINCT CustomerID)) * 100, 2
    ) AS churn_rate_percent
FROM workspace.silver.ibm_telco_customer_churn
GROUP BY `Payment Method`
ORDER BY churn_rate_percent DESC;
-- Baseline:
-- Electronic check: 45.29%
-- Mailed check: 19.11%
-- Bank transfer: 16.71%
-- Credit card: 15.24%


-- ---------------------------------------------------------------------
-- 4. Power BI Page 4: Churn Rate by Internet Service (Bar Chart)
-- ---------------------------------------------------------------------
SELECT
    `Internet Service` AS internet_service,
    COUNT(DISTINCT CustomerID) AS total_customers,
    SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        (CAST(SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS DOUBLE) 
        / COUNT(DISTINCT CustomerID)) * 100, 2
    ) AS churn_rate_percent
FROM workspace.silver.ibm_telco_customer_churn
GROUP BY `Internet Service`
ORDER BY churn_rate_percent DESC;
-- Baseline:
-- Fiber optic: 41.89%
-- DSL: 18.96%
-- No: 7.40%


-- ---------------------------------------------------------------------
-- 5. Power BI Page 4: Churn Rate by Documented Tenure Bands
-- ---------------------------------------------------------------------
SELECT
    CASE 
        WHEN Tenure_Months <= 12 THEN '0-12 months'
        WHEN Tenure_Months <= 24 THEN '13-24 months'
        WHEN Tenure_Months <= 48 THEN '25-48 months'
        ELSE '49+ months'
    END AS tenure_band,
    COUNT(DISTINCT CustomerID) AS total_customers,
    SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        (CAST(SUM(CASE WHEN Churn_Value = 1 THEN 1 ELSE 0 END) AS DOUBLE) 
        / COUNT(DISTINCT CustomerID)) * 100, 2
    ) AS churn_rate_percent
FROM workspace.silver.ibm_telco_customer_churn
GROUP BY 1
ORDER BY churn_rate_percent DESC;
-- Baseline:
-- 0-12 months: 47.68%
-- 13-24 months: 28.71%
-- 25-48 months: 19.43%
-- 49+ months: 9.47%


-- ---------------------------------------------------------------------
-- 6. Gold Multi-Dimensional Churn Segment Mart
-- ---------------------------------------------------------------------
SELECT
    segment_type,
    segment,
    total_customers,
    churned_customers,
    churn_rate_percent
FROM workspace.gold.ibm_churn_segment_analysis
ORDER BY segment_type, churn_rate_percent DESC;
