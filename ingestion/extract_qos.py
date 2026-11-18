
import pdfplumber
import csv
import re
from pathlib import Path

def is_number(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

# Input PDF
pdf_path = Path("data/raw/trai_qos/PMR_20072026.pdf")

# Data dictionary
dictionary_path = Path("metadata/qos_data_dictionary.csv")

# Output CSV
output_path = Path(
    "data/bronze/trai_qos/trai_qos_june_2026.csv"
)

valid_operators = {"AIRTEL", "BSNL", "RJIL", "VIL", "MTNL"}

# Read column names from the data dictionary
with open(dictionary_path, "r", encoding="utf-8") as file:
    dictionary = list(csv.DictReader(file))

columns = [row["column_name"] for row in dictionary]

records = []

with pdfplumber.open(pdf_path) as pdf:

    # PDF pages 2 to 6
    for page_index in range(1, 6):

        page = pdf.pages[page_index]
        text = page.extract_text()

        if not text:
            continue

        for line in text.splitlines():

            parts = line.split()

            if len(parts) != 16:
                continue

            serial, operator, lsa = parts[:3]
            measurements = parts[3:]

            if not serial.isdigit():
                continue

            if operator not in valid_operators:
                continue

            if not re.fullmatch(r"[A-Z]{2,3}", lsa):
                continue

            valid_values = all(
                value == "NA" or is_number(value)
                for value in measurements
            )

            if not valid_values:
                continue

            record = {
                "serial_number": int(serial),
                "operator": operator,
                "lsa": lsa
            }

            for index, value in enumerate(measurements, start=3):
                record[columns[index]] = value

            records.append(record)


# Validate before exporting
serial_numbers = [record["serial_number"] for record in records]

if len(records) != 88:
    raise ValueError(f"Expected 88 records, found {len(records)}")

if len(set(serial_numbers)) != 88:
    raise ValueError("Duplicate serial numbers detected")

if sorted(serial_numbers) != list(range(1, 89)):
    raise ValueError("Some serial numbers are missing")

# Create output directory
output_path.parent.mkdir(parents=True, exist_ok=True)

# Export CSV
with open(output_path, "w", newline="", encoding="utf-8") as file:

    writer = csv.DictWriter(file, fieldnames=columns)

    writer.writeheader()
    writer.writerows(records)

print("QoS extraction completed successfully!")
print("Records exported:", len(records))
print("Columns exported:", len(columns))
print("Output:", output_path)

