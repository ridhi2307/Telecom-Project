import pdfplumber
from pathlib import Path

pdf_path = Path("data/raw/trai_qos/PMR_20072026.pdf")

with pdfplumber.open(pdf_path) as pdf:

    page = pdf.pages[1]

    cropped_page = page.crop((25, 75, 815, 570))

    tables = cropped_page.extract_tables(
        table_settings={
            "vertical_strategy": "text",
            "horizontal_strategy": "text",
            "text_x_tolerance": 3,
            "text_y_tolerance": 3,
            "min_words_vertical": 2,
            "min_words_horizontal": 1
        }
    )

    for table in tables:
        for row in table:
            if not row:
                continue

            first = (row[0] or "").strip()
            second = (row[1] or "").strip()

            # Repair the split first record
            if first == "1 A" and second == "IRTEL":
                row[0] = "1"
                row[1] = "AIRTEL"

            if (
    row[0] in ["1", "2", "3"]
    and row[1] in ["AIRTEL", "BSNL", "RJIL", "VIL", "MTNL"]
):
                print("\nRecord:", row[0])
                print("Operator:", row[1])
                print("Service area:", row[2])
                print("Total columns:", len(row))
                print("Complete row:", row)

