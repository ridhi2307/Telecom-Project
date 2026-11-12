# TRAI Subscriber Statistics – Source Documentation

## Source Information

- Publisher: Telecom Regulatory Authority of India (TRAI)
- Source file: PR_No104of2026_0.pdf
- Reporting period: June 2026
- Source type: Official TRAI press release
- Extraction script: ingestion/extract_subscribers.py
- Output directory: data/bronze/trai_subscribers/

## Extracted Datasets

| CSV file                        | Records | Columns |
| ------------------------------- | ------: | ------: |
| circle_wise_growth_rates.csv    |       5 |       8 |
| circle_wise_net_additions.csv   |       5 |       8 |
| fixed_wired_broadband.csv       |       5 |       7 |
| mnp_service_area_status.csv     |      22 |       7 |
| telephone_subscriber_base.csv   |       6 |       5 |
| wireless_broadband.csv          |       5 |       7 |
| wireless_mobile_subscribers.csv |       2 |       5 |
| **Total**                       |  **50** |       — |

## Dataset Descriptions

1. Circle-wise growth rates: Monthly and yearly growth rates for wireline and wireless subscribers.
2. Circle-wise net additions: Net subscriber additions and subscriber bases for wireline and wireless services.
3. Fixed wired broadband: Provider-wise fixed broadband subscriber statistics.
4. MNP service-area status: Service-area-wise mobile number portability requests for May and June 2026.
5. Telephone subscriber base: Subscriber counts by category.
6. Wireless broadband: Provider-wise wireless broadband subscriber statistics.
7. Wireless mobile subscribers: Wireless subscriber statistics by category.

## Extraction Method

Python-based extraction using PyMuPDF, regular expressions, CSV handling and Pandas.

Some tables were manually reconstructed from the original PDF where automatic extraction was unreliable.

## Data Quality and Limitations

- Initial structural validation found 50 records across seven CSV files.
- All seven CSVs had zero missing values and zero duplicate rows in the initial check.
- Structural checks do not guarantee every extracted value is correct.
- Page 19 wireline subscriber table was excluded because reliable extraction could not be achieved.
- Manually reconstructed figures should be checked against the original source PDF.
- MNP porting requests indicate portability activity and must not automatically be interpreted as confirmed customer churn.
- Subscriber statistics are aggregate data, not individual customer records.

## Intended Use

These datasets can support aggregate telecom subscriber growth, broadband provider comparisons, service-area analysis and MNP activity analysis.
