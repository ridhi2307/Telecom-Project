# TelecomNexus — Member 3: KPI Dictionary
### SQL Analytics, Formulations, Data Grains & Audit Controls

Prepared for: **Member 3 (SQL Analytics, KPIs & Power BI)**  
Project Snapshot: **16 November 2026**  
Submission Deadline: **20 November 2026**

---

## 1. Domain Separation Directive

> [!IMPORTANT]
> **TRAI India industry analytics and IBM US customer-churn analytics must remain strictly separate.**  
> - **TRAI Grain:** Regional aggregates by Licensed Service Area (LSA) and Operator.
> - **IBM Grain:** Individual customer accounts (fictional US benchmark).  
> **Never** merge IBM customer rows with TRAI records or claim the IBM churn rate represents Indian customers.

---

## 2. Comprehensive KPI Dictionary

### A. TRAI Telecom Industry KPIs (Pages 1–3 of Power BI Dashboard)

| KPI Name | Business Question | Formula / Aggregation | Grain & Filters | Units & Null Treatment | Gold Source Table | Control / Validation Value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **May 2026 MNP Requests** | What was the baseline switching inquiry volume in May? | `SUM(may_2026_porting_requests_millions)` | National / LSA; No filter | Millions of requests; Not completed ports | `workspace.gold.trai_lsa_switching_usage_context` | **14.470 Million** |
| **June 2026 MNP Requests** | What was the monthly switching inquiry volume in June? | `SUM(june_2026_porting_requests_millions)` | National / LSA; No filter | Millions of requests; Not operator-specific | `workspace.gold.trai_lsa_switching_usage_context` | **14.790 Million** |
| **MoM Net Porting Change** | Did customer porting activity increase or decrease month-over-month? | `June_Total - May_Total` | National / LSA; No filter | Millions of requests (`+0.320 M`) | `workspace.gold.trai_lsa_switching_usage_context` | **+0.320 Million (+2.21%)** |
| **Unweighted Average ARPU** | What is the average revenue per user across telecom circles? | `AVG(arpu_inr_per_month)` | Telecom Service Area (LSA) | INR / subscriber / month; Simple mean, not subscriber-weighted | `workspace.gold.trai_lsa_switching_usage_context` | **₹ 187.95** (Zone I: ₹ 180.27, Zone II: ₹ 195.64) |
| **Unweighted Prepaid Share** | What proportion of subscribers use prepaid vs postpaid services? | `AVG(prepaid_percentage)` | Telecom Service Area (LSA) | Percentage (%); Simple circle average | `workspace.gold.trai_lsa_switching_usage_context` | **82.77%** |
| **Average Total MoU** | How many voice minutes does an average subscriber consume per month? | `AVG(total_mou_per_month)` | Telecom Service Area (LSA) | Minutes / subscriber / month | `workspace.gold.trai_lsa_switching_usage_context` | **955.5 Minutes** |
| **Cell Downtime % (QoS)** | What percentage of network cells are unavailable due to outages? | `AVG(metric_02)` | Operator × LSA | Percentage (%); Preserved source nulls | `workspace.silver.trai_qos` | Airtel: 1.45%, RJIL: 0.82%, Vi: 2.10%, BSNL: 3.40% |
| **Call Setup Success Rate (QoS)** | What is the internal network call setup completion rate? | `AVG(metric_05)` | Operator × LSA | Percentage (%); Target ≥ 95% | `workspace.silver.trai_qos` | RJIL: 99.4%, Airtel: 99.1%, Vi: 98.7% |
| **4G / 5G Latency (QoS)** | What is the average packet transmission delay across operators? | `AVG(metric_12)` | Operator × LSA | Milliseconds (ms); Lower is better | `workspace.silver.trai_qos` | RJIL: 24.2 ms, Airtel: 26.5 ms, Vi: 32.1 ms |

---

### B. IBM Customer Churn Retention KPIs (Page 4 of Power BI Dashboard)

| KPI Name | Business Question | Formula / Aggregation | Grain & Filters | Units & Null Treatment | Gold / Silver Source Table | Control / Validation Value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Customers** | What is the total active subscriber base evaluated? | `COUNT(DISTINCT CustomerID)` | Customer Account | Customer accounts; Distinct count | `workspace.silver.ibm_telco_customer_churn` | **7,043 Customers** |
| **Churned Customers** | How many customers terminated their subscriptions? | `CALCULATE(DISTINCTCOUNT(CustomerID), Churn_Value = 1)` | Customer Account | Customer accounts | `workspace.silver.ibm_telco_customer_churn` | **1,869 Customers** |
| **Retained Customers** | How many customers maintained active service? | `CALCULATE(DISTINCTCOUNT(CustomerID), Churn_Value = 0)` | Customer Account | Customer accounts | `workspace.silver.ibm_telco_customer_churn` | **5,174 Customers** |
| **Customer Churn Rate** | What proportion of the subscriber base was lost? | `DIVIDE([Churned Customers], [Total Customers])` | Customer Account | Percentage (%); Benchmark target < 15% | `workspace.silver.ibm_telco_customer_churn` | **26.54%** |
| **Average Monthly Charges** | What is the average monthly recurring billing per subscriber? | `AVERAGE(Monthly_Charges)` | Customer Account | USD ($) / subscriber / month | `workspace.silver.ibm_telco_customer_churn` | **$64.76** |
| **Monthly Revenue Lost** | How much monthly recurring revenue is lost due to departing customers? | `CALCULATE(SUM(Monthly_Charges), Churn_Value = 1)` | Customer Account | USD ($) / month | `workspace.silver.ibm_telco_customer_churn` | **$139,130.85 / month** |
| **Average Customer Tenure** | What is the average customer relationship lifespan? | `AVERAGE(Tenure_Months)` | Customer Account | Months of service | `workspace.silver.ibm_telco_customer_churn` | **32.4 Months** |

---

## 3. Critical Analytical & Audit Rules

1. **Unweighted vs Weighted ARPU:** Averaging the 22 LSA ARPU values directly produces an **unweighted service-area mean**. It is not a population-weighted national average. It must be explicitly labeled as *unweighted* on Power BI cards.
2. **Missing is Not Zero (TRAI QoS):** Missing QoS values (e.g. RJIL `metric_08` has 22 missing values) reflect physical network realities (all-IP network with no circuit-switched infrastructure). They must remain blank in Power BI and never be imputed with zero.
3. **11 Whitespace Total Charges (IBM):** 11 customers with 0 tenure have whitespace charges. They are cleansed to `NULL` in Silver to avoid corrupting financial metrics.
4. **Denominator Discipline:** Always divide by total eligible customers (`COUNT(DISTINCT CustomerID)`); never divide a filtered count by an arbitrary constant.
