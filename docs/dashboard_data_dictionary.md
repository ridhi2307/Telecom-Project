# TelecomNexus — Dashboard Data Dictionary

This document maps all reporting fields utilized across the **Power BI Dashboard** and **Databricks SQL Gold / Silver layers**.

---

## 1. Table: `workspace.gold.trai_lsa_switching_usage_context`
- **Grain:** One record per Licensed Service Area (LSA)
- **Total Records:** 22 rows
- **Join Key:** `canonical_lsa` (from `metadata/dim_lsa.csv`)

| Field Name | Data Type | Reporting Label in Power BI | Description | Unit |
| :--- | :--- | :--- | :--- | :--- |
| `canonical_lsa` | String | Service Area (LSA) | Standardized circle identifier (e.g. DL, MH, GJ) | Text Code |
| `zone` | String | Geographic Zone | Macro regulatory division (Zone I, Zone II) | Text |
| `mnp_report_month` | String | MNP Reporting Period | Reporting month of MNP statistics (June 2026) | YYYY-MM |
| `may_2026_porting_requests_millions` | Double | May Porting Requests | Porting requests received in May 2026 | Million requests |
| `june_2026_porting_requests_millions` | Double | June Porting Requests | Porting requests received in June 2026 | Million requests |
| `category` | String | Circle Category | TRAI circle tier: Metro, Circle A, Circle B, Circle C | Category |
| `prepaid_percentage` | Double | Prepaid Share (%) | Proportion of prepaid wireless subscribers | Percentage (%) |
| `arpu_inr_per_month` | Double | Monthly ARPU (₹) | Blended Average Revenue Per User per month | INR / user / mo |
| `outgoing_sms_per_month` | Integer | Outgoing SMS | Average outgoing SMS messages per user/month | Count |
| `outgoing_mou_per_month` | Double | Outgoing MOU | Average outgoing voice minutes per user/month | Minutes |
| `incoming_mou_per_month` | Double | Incoming MOU | Average incoming voice minutes per user/month | Minutes |
| `total_mou_per_month` | Double | Total MOU | Total voice minutes of usage per user/month | Minutes |
| `usage_reporting_period` | String | Usage Period | Quarter of usage statistics (QE Jun-26) | Quarter |

---

## 2. Table: `workspace.silver.trai_qos`
- **Grain:** Operator × Licensed Service Area (LSA)
- **Total Records:** 88 rows (22 circles × 4 operators)

| Field Name | Data Type | Reporting Label in Power BI | Description |
| :--- | :--- | :--- | :--- |
| `operator` | String | Service Provider | Name of telecom operator (AIRTEL, RJIL, VIL, BSNL, MTNL) |
| `lsa` | String | Service Area | Telecom circle code |
| `metric_01` | Double | Coverage Map Availability | Geospatial coverage map availability (%) |
| `metric_02` | Double | Cell Downtime (%) | Cumulative downtime of non-available cells (%) |
| `metric_05` | Double | Call Setup Success (Intra) | Intra-network call setup success rate (%) |
| `metric_06` | Double | Call Setup Success (Inter) | Inter-network call setup success rate (%) |
| `metric_12` | Double | 4G/5G Latency (ms) | Network latency in milliseconds |
| `metric_13` | Double | Packet Drop Rate (%) | 4G and 5G packet drop rate (%) |

---

## 3. Table: `workspace.silver.ibm_telco_customer_churn`
- **Grain:** One record per Customer Account
- **Total Records:** 7,043 rows

| Field Name | Data Type | Reporting Label in Power BI | Description |
| :--- | :--- | :--- | :--- |
| `CustomerID` | String | Customer ID | Unique subscriber account identifier |
| `Gender` | String | Gender | Male / Female |
| `Senior_Citizen` | String | Senior Citizen | Yes / No |
| `Tenure_Months` | Integer | Tenure (Months) | Total months subscribed |
| `Contract` | String | Contract Type | Month-to-month, One year, Two year |
| `Payment Method` | String | Payment Channel | Electronic check, Mailed check, Bank transfer, Credit card |
| `Internet Service` | String | Internet Technology | DSL, Fiber optic, No |
| `Monthly_Charges` | Double | Monthly Bill ($) | Monthly subscription charge |
| `Total_Charges` | Double | Total Billed ($) | Cumulative billing (11 blank records cast to NULL) |
| `Churn Label` | String | Churn Status | Yes / No |
| `Churn_Value` | Integer | Churn Indicator | 1 = Churned, 0 = Retained |
| `Churn_Score` | Integer | Risk Score | Predictive churn score (0 to 100) |
| `CLTV` | Integer | Customer Lifetime Value | Historical customer value |
| `Churn Reason` | String | Exit Reason | Primary recorded reason for departure |
