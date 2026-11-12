# TRAI Subscriber Dataset – Data Quality Report

## Dataset Summary

Seven CSV files were extracted from the TRAI June 2026 subscriber statistics report.

| Dataset                         | Rows | Columns |
| ------------------------------- | ---: | ------: |
| circle_wise_growth_rates.csv    |    5 |       8 |
| circle_wise_net_additions.csv   |    5 |       8 |
| fixed_wired_broadband.csv       |    5 |       7 |
| mnp_service_area_status.csv     |   22 |       7 |
| telephone_subscriber_base.csv   |    6 |       5 |
| wireless_broadband.csv          |    5 |       7 |
| wireless_mobile_subscribers.csv |    2 |       5 |
| Total                           |   50 |       — |

## Initial Structural Checks

- Missing values: 0 across all seven files.
- Duplicate rows: 0 across all seven files.
- Total extracted records: 50.

## Extraction Limitations

- Some source tables required manual reconstruction.
- Page 19 wireline subscriber table was excluded because extraction could not be reliably verified.
- Zero missing values and duplicates do not establish complete numerical accuracy.
- Values should be compared with the original TRAI PDF before final analytical use.

## Important Analytical Caution

Mobile Number Portability (MNP) requests are not equivalent to confirmed churn. They represent portability activity and should be interpreted separately.
