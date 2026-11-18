from pathlib import Path
import pandas as pd

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_FILE = BASE_DIR / "data" / "raw" / "ibm_telco" / "Telco_customer_churn.xlsx"

BRONZE_DIR = BASE_DIR / "data" / "bronze" / "ibm_telco"
BRONZE_FILE = BRONZE_DIR / "ibm_telco_customer_churn.csv"


def extract_ibm_telco():

    # Check whether source file exists
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Source file not found: {RAW_FILE}")

    # Create Bronze directory
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    # Read original Excel workbook
    df = pd.read_excel(
        RAW_FILE,
        sheet_name="Telco_Churn"
    )

    # Preserve original columns and values
    df.to_csv(
        BRONZE_FILE,
        index=False
    )

    print("IBM Telco extraction completed successfully!")
    print("Source file:", RAW_FILE)
    print("Bronze file:", BRONZE_FILE)
    print("Records:", len(df))
    print("Columns:", len(df.columns))


if __name__ == "__main__":
    extract_ibm_telco()
