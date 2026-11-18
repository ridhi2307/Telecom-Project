# Ingestion Layer

Data extraction and parsing scripts to ingest raw telecom sources into Bronze CSVs:
- **`extract_ibm_telco.py`**: Ingests IBM Telco Customer Churn data.
- **`extract_qos.py`**: Ingests TRAI Quality of Service indicators.
- **`extract_subscribers.py`**: Parses TRAI subscriber base and MNP status.
- **`extract_usage.py`**: Ingests circle-wise usage and national wireless trends.
- **`validate_qos.py` & `test_qos_tables.py`**: Verification checks on extracted indicators.
