# Power BI Data Model, Power Query M-Code & Complete DAX Repository

This technical companion provides all ready-to-use **Power Query (M)** scripts and **DAX measures** required to construct the TelecomNexus Power BI report.

---

## 1. Power Query M-Code (DirectQuery / Databricks)

If connecting directly to Databricks SQL Warehouse, paste this into the Power Query Advanced Editor:

```powerquery
let
    Source = Databricks.Catalogs(
        "adb-xxxxxxxxxxxxxxxx.xx.azuredatabricks.net", 
        "/sql/1.0/warehouses/xxxxxxxxxxxxxxxx", 
        [Catalog="workspace", Database="gold"]
    ),
    Gold_Data = Source{[Name="gold"]}[Data],
    trai_context = Gold_Data{[Name="trai_lsa_switching_usage_context"]}[Data]
in
    trai_context
```

---

## 2. Power Query M-Code (Local CSV Fallback)

If loading local CSV files directly:

```powerquery
let
    Source = Csv.Document(File.Contents("E:\Big Data\Telecom-Project-main\data\bronze\ibm_telco\ibm_telco_customer_churn.csv"), [Delimiter=",", Columns=33, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Cleaned Total Charges" = Table.ReplaceValue(#"Promoted Headers"," ",null,Replacer.ReplaceValue,{"Total Charges"}),
    #"Changed Types" = Table.TransformColumnTypes(#"Cleaned Total Charges",{
        {"Tenure Months", Int64.Type}, 
        {"Monthly Charges", type number}, 
        {"Total Charges", type number}, 
        {"Churn Value", Int64.Type}, 
        {"Churn Score", Int64.Type}, 
        {"CLTV", Int64.Type}
    })
in
    #"Changed Types"
```

---

## 3. Complete Master DAX Measures Table (`_Measures`)

```dax
// ==========================================
// IBM CUSTOMER CHURN RETENTION MEASURES
// ==========================================

Total Customers = DISTINCTCOUNT('ibm_telco_customer_churn'[CustomerID])

Churned Customers = 
CALCULATE(
    DISTINCTCOUNT('ibm_telco_customer_churn'[CustomerID]),
    'ibm_telco_customer_churn'[Churn Value] = 1
)

Retained Customers = 
CALCULATE(
    DISTINCTCOUNT('ibm_telco_customer_churn'[CustomerID]),
    'ibm_telco_customer_churn'[Churn Value] = 0
)

Churn Rate % = 
DIVIDE([Churned Customers], [Total Customers], 0)

Avg Monthly Charges = 
AVERAGE('ibm_telco_customer_churn'[Monthly Charges])

Avg Customer Tenure = 
AVERAGE('ibm_telco_customer_churn'[Tenure Months])

Monthly Revenue Lost = 
CALCULATE(
    SUM('ibm_telco_customer_churn'[Monthly Charges]),
    'ibm_telco_customer_churn'[Churn Value] = 1
)

Annualized Revenue Lost = 
[Monthly Revenue Lost] * 12


// ==========================================
// TRAI TELECOM INDUSTRY MEASURES
// ==========================================

May MNP Porting Requests (M) = 
SUM('trai_lsa_switching_usage_context'[may_2026_porting_requests_millions])

June MNP Porting Requests (M) = 
SUM('trai_lsa_switching_usage_context'[june_2026_porting_requests_millions])

MoM Net Porting Change (M) = 
[June MNP Porting Requests (M)] - [May MNP Porting Requests (M)]

MoM Porting Growth % = 
DIVIDE([MoM Net Porting Change (M)], [May MNP Porting Requests (M)], 0)

Unweighted Avg ARPU (INR) = 
AVERAGE('trai_lsa_switching_usage_context'[arpu_inr_per_month])

Unweighted Prepaid Ratio % = 
AVERAGE('trai_lsa_switching_usage_context'[prepaid_percentage]) / 100

Unweighted Avg Total MOU = 
AVERAGE('trai_lsa_switching_usage_context'[total_mou_per_month])

Active Telecom Circles = 
DISTINCTCOUNT('trai_lsa_switching_usage_context'[canonical_lsa])


// ==========================================
// QUALITY OF SERVICE (QoS) MEASURES
// ==========================================

Avg Cell Downtime % = 
AVERAGE('trai_qos'[metric_02])

Call Setup Success Rate % = 
AVERAGE('trai_qos'[metric_05]) / 100

Avg 4G/5G Latency (ms) = 
AVERAGE('trai_qos'[metric_12])

Packet Drop Rate % = 
AVERAGE('trai_qos'[metric_13])
```
