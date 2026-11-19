# TelecomNexus — validated-schema DAX measures

Create these **one measure at a time** in Power BI (or with supported semantic-model authoring tools). Ensure displayed table names match CSV basenames. Use explicit number formats in Power BI.

```dax
IBM Customers = DISTINCTCOUNT('ibm_telco_customer_churn'[CustomerID])
IBM Churned Customers = CALCULATE(DISTINCTCOUNT('ibm_telco_customer_churn'[CustomerID]), 'ibm_telco_customer_churn'[Churn_Value] = 1)
IBM Retained Customers = CALCULATE(DISTINCTCOUNT('ibm_telco_customer_churn'[CustomerID]), 'ibm_telco_customer_churn'[Churn_Value] = 0)
IBM Churn Rate = DIVIDE([IBM Churned Customers], [IBM Customers])
IBM Avg Monthly Charges = AVERAGE('ibm_telco_customer_churn'[Monthly_Charges])
IBM Churned Monthly Charges = CALCULATE(SUM('ibm_telco_customer_churn'[Monthly_Charges]), 'ibm_telco_customer_churn'[Churn_Value] = 1)
IBM Avg Tenure = AVERAGE('ibm_telco_customer_churn'[Tenure_Months])
TRAI May MNP M = SUM('trai_lsa_switching_usage_context'[may_2026_porting_requests_millions])
TRAI June MNP M = SUM('trai_lsa_switching_usage_context'[june_2026_porting_requests_millions])
TRAI MNP Growth M = [TRAI June MNP M] - [TRAI May MNP M]
TRAI MNP Growth Pct = DIVIDE([TRAI MNP Growth M], [TRAI May MNP M])
TRAI Unweighted ARPU INR = AVERAGE('trai_lsa_switching_usage_context'[arpu_inr_per_month])
TRAI Unweighted Prepaid Share = DIVIDE(AVERAGE('trai_lsa_switching_usage_context'[prepaid_percentage]), 100)
TRAI Unweighted Total MOU = AVERAGE('trai_lsa_switching_usage_context'[total_mou_per_month])
TRAI Active Circles = DISTINCTCOUNT('trai_lsa_switching_usage_context'[canonical_lsa])
TRAI Outgoing MOU = AVERAGE('trai_lsa_switching_usage_context'[outgoing_mou_per_month])
TRAI Incoming MOU = AVERAGE('trai_lsa_switching_usage_context'[incoming_mou_per_month])
QoS Avg Latency ms = AVERAGE('trai_qos'[metric_12])
QoS Intra Call Setup Rate = DIVIDE(AVERAGE('trai_qos'[metric_05]), 100)
QoS Inter Call Setup Rate = DIVIDE(AVERAGE('trai_qos'[metric_06]), 100)
QoS Avg Cell Downtime Pct = DIVIDE(AVERAGE('trai_qos'[metric_02]), 100)
Wireless Subscribers M = SUM('trai_wireless_broadband'[subscriber_base_million])
National ARPU INR = AVERAGE('trai_national_wireless_usage_trends'[arpu_inr_per_month])
National Revenue per GB INR = AVERAGE('trai_national_wireless_usage_trends'[revenue_realization_per_gb_inr])
```

Percent measures return fractions and should be formatted using **Percentage**; raw MNP measures are already in **millions** and should use decimals not automatic million display unit; the source is already in millions.

Calculated columns in `ibm_telco_customer_churn`:

```dax
Tenure_Band = SWITCH(TRUE(), 'ibm_telco_customer_churn'[Tenure_Months] <= 12, "0–12 months", 'ibm_telco_customer_churn'[Tenure_Months] <= 24, "13–24 months", 'ibm_telco_customer_churn'[Tenure_Months] <= 48, "25–48 months", "49+ months")
Tenure_Band_Order = SWITCH(TRUE(), 'ibm_telco_customer_churn'[Tenure_Months] <= 12, 1, 'ibm_telco_customer_churn'[Tenure_Months] <= 24, 2, 'ibm_telco_customer_churn'[Tenure_Months] <= 48, 3, 4)
```

Sort `Tenure_Band` by `Tenure_Band_Order`.
