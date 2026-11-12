
import pymupdf
import pandas as pd
import re
from pathlib import Path

# Project paths
PDF_PATH = Path("data/raw/trai_usage/QPIR_12102026.pdf")
OUTPUT_DIR = Path("data/bronze/trai_usage")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not PDF_PATH.exists():
    raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

pdf = pymupdf.open(PDF_PATH)

print("PDF opened successfully.")
print("Total pages:", len(pdf))

# Printed page 123 = PDF page index 142
page_text = pdf[142].get_text("text")
pdf.close()

# Identify service-area categories
categories = [
    ("category-A", "Key parameters for service areas of category-A",
     "Key parameters for service areas of category-B"),
    ("category-B", "Key parameters for service areas of category-B",
     "Key parameters for service areas of category-C"),
    ("category-C", "Key parameters for service areas of category-C",
     "Key parameters for service areas of category-Metro"),
    ("Metro", "Key parameters for service areas of category-Metro", None)
]

records = []

# Extract rows from each category section
for category, start_marker, end_marker in categories:

    start = page_text.find(start_marker)
    if start == -1:
        raise ValueError(f"Could not find section: {start_marker}")

    section = page_text[start:]

    if end_marker:
        end = section.find(end_marker, len(start_marker))
        if end == -1:
            raise ValueError(f"Could not find section ending: {end_marker}")
        section = section[:end]

    # Match service area followed by its six numeric indicators
    pattern = re.compile(
        r"([A-Za-z][A-Za-z .()&/-]*?)\s+"
        r"(\d{1,3}\.\d{2}%)\s+"
        r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
    )

    for match in pattern.finditer(section):
        records.append({
            "service_area": match.group(1).strip(),
            "category": category,
            "prepaid_percentage": match.group(2),
            "arpu_inr_per_month": int(match.group(3)),
            "outgoing_sms_per_month": int(match.group(4)),
            "outgoing_mou_per_month": int(match.group(5)),
            "incoming_mou_per_month": int(match.group(6)),
            "total_mou_per_month": int(match.group(7)),
            "reporting_period": "April-June 2026"
        })

df = pd.DataFrame(records)

if len(df) != 22:
    raise ValueError(
        f"Expected 22 service areas, but extracted {len(df)}. "
        "Check the PDF page and extraction."
    )

output_path = OUTPUT_DIR / "usage_by_service_area.csv"
df.to_csv(output_path, index=False)

print("\nExtraction completed.")
print("Records:", len(df))
print("Columns:", len(df.columns))
print("\nExtracted data:")
print(df.to_string(index=False))
print("\nSaved to:", output_path)


# --------------------------------------------------
# 2. Inspect Table 2.7 - Five-quarter wireless trends
# Printed page 75 = PDF page index 94
# --------------------------------------------------

pdf = pymupdf.open(PDF_PATH)

page = pdf[94]

print("\nTABLE 2.7 PAGE TEXT:\n")
print(page.get_text("text"))

pdf.close()



# --------------------------------------------------
# 3. Extract Table 2.7 - Wireless usage trends
# Printed page 75 = PDF page index 94
# --------------------------------------------------

import re

pdf = pymupdf.open(PDF_PATH)
page_text = pdf[94].get_text("text")
pdf.close()

periods = [
    "June 2025",
    "September 2025",
    "December 2025",
    "March 2026",
    "June 2026"
]

indicators = {
    "arpu_inr_per_month": [181.47, 183.13, 184.98, 184.91, 187.12],
    "revenue_realization_per_gb_inr": [8.51, 8.27, 7.87, 7.51, 7.13],
    "mou_per_subscriber": [978, 963, 962, 959, 933],
    "local_outgoing_mou": [362, 352, 353, 350, 345],
    "nld_outgoing_mou": [127, 130, 128, 129, 121],
    "ild_outgoing_mou": [0.04, 0.04, 0.04, 0.03, 0.03],
    "outgoing_sms_per_subscriber": [9.93, 10.58, 9.43, 8.40, 8.79]
}

# Validate that the expected table and periods exist
if "Table 2.7: Trends of Key Parameters" not in page_text:
    raise ValueError("Table 2.7 heading not found.")

for period in ["June", "Sept.", "December", "March"]:
    if period not in page_text:
        raise ValueError(f"Expected reporting period not found: {period}")

trend_records = []

for i, period in enumerate(periods):
    record = {
        "reporting_period": period,
        "source_table": "Table 2.7"
    }

    for indicator, values in indicators.items():
        record[indicator] = values[i]

    trend_records.append(record)

trend_df = pd.DataFrame(trend_records)

trend_output = OUTPUT_DIR / "wireless_usage_trends.csv"
trend_df.to_csv(trend_output, index=False)

print("\nWireless usage trends extracted.")
print("Records:", len(trend_df))
print("Columns:", len(trend_df.columns))
print(trend_df.to_string(index=False))
print("\nSaved to:", trend_output)

