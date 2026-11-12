
import pdfplumber
import re
from pathlib import Path

# Original QoS PDF
pdf_path = Path("data/raw/trai_qos/PMR_20072026.pdf")

# Expected operators
valid_operators = {"AIRTEL", "BSNL", "RJIL", "VIL", "MTNL"}

# Pages 2 to 6 (Python indexes 1 to 5)
pages_to_check = range(1, 6)

records = []
issues = []

with pdfplumber.open(pdf_path) as pdf:

    for page_index in pages_to_check:

        page = pdf.pages[page_index]
        page_text = page.extract_text()

        print(f"\nChecking PDF page {page_index + 1}")

        if not page_text:
            issues.append(f"Page {page_index + 1}: No text found")
            continue

        for line in page_text.splitlines():

            parts = line.split()

            # A valid data row should have 16 fields
            if len(parts) != 16:
                continue

            serial, operator, lsa = parts[:3]
            measurements = parts[3:]

            # Check serial number
            if not serial.isdigit():
                continue

            # Check operator
            if operator not in valid_operators:
                continue

            # Check service area format
            if not re.fullmatch(r"[A-Z]{2,3}", lsa):
                issues.append(
                    f"Record {serial}: Invalid LSA code: {lsa}"
                )
                continue

            # Check measurement values
            valid_values = True

            for value in measurements:
                if value != "NA":
                    try:
                        float(value)
                    except ValueError:
                        valid_values = False
                        break

            if not valid_values:
                issues.append(
                    f"Record {serial}: Invalid measurement value"
                )
                continue

            records.append({
                "serial": int(serial),
                "operator": operator,
                "lsa": lsa,
                "measurements": measurements
            })


# Validation summary
serial_numbers = [record["serial"] for record in records]

print("\n========== VALIDATION SUMMARY ==========")

print("Total records extracted:", len(records))
print("Unique serial numbers:", len(set(serial_numbers)))

print(
    "Missing serial numbers:",
    sorted(set(range(1, 89)) - set(serial_numbers))
)

print(
    "Duplicate serial numbers:",
    sorted({
        number for number in serial_numbers
        if serial_numbers.count(number) > 1
    })
)

print(
    "Operators found:",
    sorted({record["operator"] for record in records})
)

print(
    "Service areas found:",
    len({record["lsa"] for record in records})
)

print(
    "Total missing measurement values (NA):",
    sum(
        value == "NA"
        for record in records
        for value in record["measurements"]
    )
)

print("\nIssues found:", len(issues))

for issue in issues:
    print(issue)

# Final status
if (
    len(records) == 88
    and len(set(serial_numbers)) == 88
    and sorted(serial_numbers) == list(range(1, 89))
    and not issues
):
    print("\nRESULT: ALL VALIDATION CHECKS PASSED")
else:
    print("\nRESULT: VALIDATION NEEDS REVIEW")
