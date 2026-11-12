# IBM Telco Customer Churn – Data Quality Report

## 1. Dataset Information

- Project: TelecomNexus
- Source: Kaggle – IBM Telco Customer Churn
- Source file: Telco_customer_churn.xlsx
- Worksheet: Telco_Churn
- Bronze file: ibm_telco_customer_churn.csv
- Records: 7,043
- Columns: 33
- Geographic coverage: United States (California)
- Data grain: One record per customer

## 2. Extraction

Extraction script:
ingestion/extract_ibm_telco.py

Source format: XLSX
Bronze format: CSV

The original source file remains unchanged.

## 3. Validation Results

- Raw records: 7,043
- Bronze records: 7,043
- Raw columns: 33
- Bronze columns: 33
- Column names match: Yes
- Duplicate records: 0
- Duplicate CustomerIDs: 0
- Unique CustomerIDs: 7,043

## 4. Missing and Invalid Values

### Total Charges

11 records contain whitespace-only values.

All 11 records have:
- Tenure Months = 0
- Churn Label = No

The whitespace values were preserved in Bronze.

Silver recommendation:
Convert whitespace-only values to null and cast
Total Charges to a numeric data type.

Do not automatically replace missing values with zero.

### Churn Reason

5,174 records have missing Churn Reason values.

All 5,174 are non-churned customers.
All 1,869 churned customers have a Churn Reason.

These missing values are structurally not applicable.

## 5. Churn Distribution

- Non-churned: 5,174
- Churned: 1,869
- Total: 7,043
- Churn rate: approximately 26.54%

Churn Label and Churn Value are consistent
across all records.

## 6. Data Integration Limitations

The IBM dataset contains customer-level US data.

TRAI datasets contain Indian telecom market
and network-performance aggregates.

These datasets must not be directly joined.

They support separate analytical domains within
the TelecomNexus architecture.

## 7. Bronze Preservation Policy

- Do not remove records.
- Do not rename columns.
- Do not replace missing values.
- Do not perform feature engineering.
- Preserve the original source workbook.
- Perform cleaning and transformation in Silver.

## 8. Validation Status

PASS – Initial structural and targeted data-quality
checks completed.

Note: Full cell-by-cell equality and numeric range
validation have not yet been performed.
