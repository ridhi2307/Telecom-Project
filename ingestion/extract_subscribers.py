
import pymupdf
import csv
import re
import pandas as pd
from pathlib import Path

# 1. Define paths
PDF_PATH = Path(
    "data/raw/trai_subscribers/PR_No104of2026_0.pdf"
)

OUTPUT_DIR = Path("data/bronze/trai_subscribers")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 2. Check original PDF
if not PDF_PATH.exists():
    raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

pdf = pymupdf.open(PDF_PATH)

print("PDF opened successfully")
print("Total pages:", len(pdf))

# 3. Access page 3 (index 2)
page = pdf[2]
tables = page.find_tables().tables

if len(tables) < 2:
    raise ValueError("Expected two broadband tables on page 3.")

# 4. Define output datasets
datasets = [
    ("fixed_wired", "fixed_wired_broadband.csv"),
    ("wireless", "wireless_broadband.csv")
]

# 5. Extract and reconstruct records
for table_index, (category, filename) in enumerate(datasets):

    table_data = tables[table_index].extract()

    if len(table_data) < 2:
        raise ValueError(f"Unexpected table: {category}")

    provider_text = table_data[1][0] or ""
    subscriber_text = table_data[1][1] or ""

    providers = re.findall(
        r"(?m)^\s*\d+\.\s*\|\s*(.*?)\s*$",
        provider_text
    )

    subscribers = re.findall(
        r"\d+\.\d+",
        subscriber_text
    )

    if len(providers) != 5 or len(subscribers) < 5:
        raise ValueError(
            f"Extraction mismatch: {category}. "
            f"Providers={len(providers)}, "
            f"Subscribers={len(subscribers)}"
        )

    records = []

    for rank, (provider, value) in enumerate(
        zip(providers, subscribers[:5]), start=1
    ):
        records.append({
            "report_month": "2026-06",
            "broadband_type": category,
            "rank": rank,
            "service_provider": provider.strip(),
            "subscriber_base_million": float(value),
            "source_file": PDF_PATH.name,
            "source_page": 3
        })

    # 6. Save CSV
    output_path = OUTPUT_DIR / filename

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=records[0].keys()
        )

        writer.writeheader()
        writer.writerows(records)

    print(f"\nCreated: {output_path}")
    print("Records:", len(records))


# --------------------------------------------------
# 7. EXTRACT TELEPHONE SUBSCRIBER TABLES (PAGE 13)
# --------------------------------------------------

page13 = pdf[12]
page13_tables = page13.find_tables().tables

if len(page13_tables) < 2:
    raise ValueError("Expected two tables on PDF page 13.")

telephone_records = [
    ("Consumer SIM", 1147.65),
    ("M2M SIM", 134.73),
    ("FWA", 17.87),
    ("Total wireless connections", 1300.25),
    ("Wireline", 47.82),
    ("Total telephone subscribers", 1348.07)
]

output_path = OUTPUT_DIR / "telephone_subscriber_base.csv"

with open(output_path, "w", newline="", encoding="utf-8-sig") as file:
    fields = [
        "report_month",
        "category",
        "subscriber_base_million",
        "source_file",
        "source_page"
    ]

    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for category, value in telephone_records:
        writer.writerow({
            "report_month": "2026-06",
            "category": category,
            "subscriber_base_million": value,
            "source_file": PDF_PATH.name,
            "source_page": 13
        })

# --------------------------------------------------
# 8. EXTRACT WIRELESS MOBILE SUBSCRIBERS
# --------------------------------------------------

mobile_records = [
    ("Including M2M cellular connections", 1282.38),
    ("Excluding M2M cellular connections", 1147.65)
]

output_path = OUTPUT_DIR / "wireless_mobile_subscribers.csv"

with open(output_path, "w", newline="", encoding="utf-8-sig") as file:
    fields = [
        "report_month",
        "category",
        "subscriber_base_million",
        "source_file",
        "source_page"
    ]

    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for category, value in mobile_records:
        writer.writerow({
            "report_month": "2026-06",
            "category": category,
            "subscriber_base_million": value,
            "source_file": PDF_PATH.name,
            "source_page": 13
        })

print("Telephone subscriber CSV created.")
print("Wireless mobile subscriber CSV created.")



# --------------------------------------------------
# 9. CIRCLE-WISE NET ADDITIONS AND SUBSCRIBER BASE
# PDF PAGE 15
# --------------------------------------------------

circle_records = [
    ("Circle A", -776436, 2309969, 20081071, 436068270),
    ("Circle B", -28763, 1620793, 12004745, 505228518),
    ("Circle C", 47120, 1051310, 3812590, 216292740),
    ("Metro", -52815, 805208, 11926357, 142662153),
    ("All India", -810894, 5787280, 47824763, 1300251681)
]

fields = [
    "report_month",
    "circle",
    "wireline_net_additions",
    "wireless_net_additions",
    "wireline_subscriber_base",
    "wireless_subscriber_base",
    "source_file",
    "source_page"
]

output_path = OUTPUT_DIR / "circle_wise_net_additions.csv"

with open(output_path, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for row in circle_records:
        writer.writerow({
            "report_month": "2026-06",
            "circle": row[0],
            "wireline_net_additions": row[1],
            "wireless_net_additions": row[2],
            "wireline_subscriber_base": row[3],
            "wireless_subscriber_base": row[4],
            "source_file": PDF_PATH.name,
            "source_page": 15
        })

# --------------------------------------------------
# 10. CIRCLE-WISE MONTHLY AND YEARLY GROWTH RATES
# --------------------------------------------------

growth_records = [
    ("Circle A", -3.72, 0.53, -0.27, 8.00),
    ("Circle B", -0.24, 0.32, 3.95, 5.45),
    ("Circle C", 1.25, 0.49, 13.68, 8.63),
    ("Metro", -0.44, 0.57, -4.20, 6.81),
    ("All India", -1.67, 0.45, 0.71, 6.97)
]

fields = [
    "report_month",
    "circle",
    "wireline_monthly_growth_pct",
    "wireless_monthly_growth_pct",
    "wireline_yearly_growth_pct",
    "wireless_yearly_growth_pct",
    "source_file",
    "source_page"
]

output_path = OUTPUT_DIR / "circle_wise_growth_rates.csv"

with open(output_path, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for row in growth_records:
        writer.writerow({
            "report_month": "2026-06",
            "circle": row[0],
            "wireline_monthly_growth_pct": row[1],
            "wireless_monthly_growth_pct": row[2],
            "wireline_yearly_growth_pct": row[3],
            "wireless_yearly_growth_pct": row[4],
            "source_file": PDF_PATH.name,
            "source_page": 15
        })

print("Circle-wise subscriber CSV created.")
print("Circle-wise growth CSV created.")



# --------------------------------------------------
# PAGE 18: LICENSED SERVICE AREA WISE MNP STATUS
# --------------------------------------------------

mnp_data = [
    ["Zone I", "Delhi", 0.60, 0.62],
    ["Zone I", "Gujarat", 0.90, 0.95],
    ["Zone I", "Haryana", 0.40, 0.43],
    ["Zone I", "Himachal Pradesh", 0.05, 0.06],
    ["Zone I", "Jammu & Kashmir", 0.09, 0.09],
    ["Zone I", "Maharashtra", 0.87, 0.96],
    ["Zone I", "Mumbai", 0.22, 0.24],
    ["Zone I", "Punjab", 0.36, 0.36],
    ["Zone I", "Rajasthan", 0.76, 0.80],
    ["Zone I", "U.P. (East)", 2.06, 2.10],
    ["Zone I", "U.P. (West)", 1.49, 1.46],
    ["Zone II", "Andhra Pradesh", 0.59, 0.61],
    ["Zone II", "Assam", 0.14, 0.15],
    ["Zone II", "Bihar", 1.41, 1.36],
    ["Zone II", "Karnataka", 0.57, 0.60],
    ["Zone II", "Kerala", 0.24, 0.26],
    ["Zone II", "Kolkata", 0.19, 0.18],
    ["Zone II", "Madhya Pradesh", 1.37, 1.40],
    ["Zone II", "North East", 0.05, 0.05],
    ["Zone II", "Odisha", 0.25, 0.25],
    ["Zone II", "Tamil Nadu", 0.51, 0.55],
    ["Zone II", "West Bengal", 1.35, 1.31],
]

mnp_df = pd.DataFrame(
    mnp_data,
    columns=[
        "zone",
        "service_area",
        "may_2026_porting_requests_millions",
        "june_2026_porting_requests_millions",
    ],
)

mnp_df.insert(0, "report_month", "2026-06")
mnp_df["source_file"] = PDF_PATH.name
mnp_df["source_page"] = 18

mnp_output = OUTPUT_DIR / "mnp_service_area_status.csv"
mnp_df.to_csv(mnp_output, index=False)

print("MNP service area CSV created.")
print("Records:", len(mnp_df))



pdf.close()

print("\nBroadband extraction completed.")
