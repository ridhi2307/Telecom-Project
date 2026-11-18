# TRAI QoS Dataset – Data Quality Report

## 1. Dataset Information

- Source: TRAI QoS Report (Wireless Access Services)
- Original file: `PMR_20072026.pdf`
- Extracted dataset: `trai_qos_june_2026.csv`
- Data layer: Bronze
- Total records: 88
- Total columns: 16
- Operators: AIRTEL, BSNL, RJIL, MTNL, VIL

## 2. Data Validation Results

| Validation             | Result |
| ---------------------- | ------ |
| CSV readability        | Passed |
| Total records          | 88     |
| Total columns          | 16     |
| Duplicate records      | 0      |
| Missing serial numbers | 0      |
| Missing operator names | 0      |
| Missing LSA values     | 0      |

## 3. Missing Value Analysis

A total of 32 missing metric values were identified.

| Operator  | Metric    | Missing Values |
| --------- | --------- | -------------: |
| RJIL      | metric_08 |             22 |
| MTNL      | metric_09 |              2 |
| MTNL      | metric_10 |              2 |
| MTNL      | metric_11 |              2 |
| MTNL      | metric_12 |              2 |
| MTNL      | metric_13 |              2 |
| **Total** |           |         **32** |

## 4. Missing Value Investigation

The missing values were compared against the original TRAI PDF.

Findings:

- RJIL entries contain NA values in metric_08.
- Both MTNL records contain NA values in metrics 09–13.
- The original PDF explicitly represents these unavailable measurements as NA.

These are source-level missing values and should not be classified as extraction errors.

## 5. Data Handling Decisions

- Original extracted data is preserved.
- Missing values are not replaced with zero.
- Records containing missing values are not deleted.
- Missing values will be documented and handled appropriately during Silver-layer processing.
- The Bronze layer remains unchanged.

## 6. Dataset Storage

Original PDF:
`data/raw/trai_qos/PMR_20072026.pdf`

Extracted CSV:
`data/bronze/trai_qos/trai_qos_june_2026.csv`

Data dictionary:
`metadata/qos_data_dictionary.csv`

## 7. Conclusion

The TRAI QoS dataset was successfully extracted and validated.

The dataset contains 88 records and 16 columns, with zero duplicate records.

All 32 identified missing metric values have been investigated and their source-level representation has been verified against the original report.

The dataset is suitable for proceeding to the next stage of the data engineering pipeline, subject to downstream schema and transformation checks.
