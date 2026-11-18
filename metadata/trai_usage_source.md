# TRAI Wireless Usage Dataset – Source Documentation

## Source Information

- Publisher: Telecom Regulatory Authority of India (TRAI)
- Report: The Indian Telecom Services Performance Indicators
- Reporting period: April–June 2026
- Publication date: 12 October 2026
- Source file: data/raw/trai_usage/QPIR_12102026.pdf

## Extracted Tables

### 1. Annexure 2.1 – Wireless Revenue Service: Service Area-wise Statistics

- Source page: Printed page 123
- Output: usage_by_service_area.csv
- Records: 22
- Columns: 9
- Coverage: 22 service areas across categories A, B, C and Metro.
- Indicators: prepaid percentage, ARPU, outgoing SMS, outgoing MOU, incoming MOU and total MOU.

### 2. Table 2.7 – Trends of Key Parameters: Wireless Services

- Source page: Printed page 75
- Output: wireless_usage_trends.csv
- Records: 5
- Columns: 9
- Coverage: June 2025 to June 2026 (five quarters).
- Indicators: ARPU, revenue realization per GB, MOU, outgoing MOU and outgoing SMS.

## Extraction Method

- Python
- PyMuPDF for PDF text extraction
- Pandas for CSV creation and validation
- Regular expressions for service-area table extraction.
- Table 2.7 values were structured in Python using the values read from the extracted PDF text and checked against the source report.

## Data Quality

| Dataset | Records | Columns | Missing | Duplicates |
|---|---:|---:|---:|---:|
| usage_by_service_area.csv | 22 | 9 | 0 | 0 |
| wireless_usage_trends.csv | 5 | 9 | 0 | 0 |

## Limitations

1. Data is aggregated at service-area level, not individual customer level.
2. The five-quarter trend table contains aggregate wireless indicators.
3. These datasets cannot independently support individual customer churn prediction.
4. The data comes from TRAI and should not be represented as an independent telecom operator dataset.
5. Values should be interpreted according to the definitions and units in the original report.