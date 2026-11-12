# TelecomNexus – Data Join Contract

## 1. Purpose

This document defines the approved join keys, data grain,
periods and limitations for integrating TRAI datasets.

## 2. Canonical service-area key

The canonical service-area key is `canonical_lsa`,
defined in `metadata/dim_lsa.csv`.

Original service-area values must be preserved in Bronze.
Standardisation must happen in Silver.

## 3. Dataset grains

| Dataset               | Grain          | Period            |
| --------------------- | -------------- | ----------------- |
| TRAI QoS              | Operator × LSA | June 2026         |
| TRAI MNP              | LSA            | May and June 2026 |
| TRAI Usage            | LSA            | April–June 2026   |
| Wireless usage trends | National       | Quarterly trends  |

## 4. Approved joins

### A. QoS and MNP

Not a direct operator-level join.

MNP data is at LSA level and does not identify
which operator lost or gained each subscriber.

### B. QoS and Usage

Can be joined after QoS is aggregated to LSA level.

The resulting dataset must retain the distinction
between operator-level source data and LSA-level aggregates.

### C. MNP and Usage

Can be joined using `canonical_lsa`.

The result is an area-level analytical dataset,
not a customer-level churn dataset.

## 5. Important limitations

- MNP porting requests are not confirmed customer churn.
- June MNP figures must not be treated as operator-specific churn.
- Usage data covers April–June 2026, while MNP includes May and June values.
- QoS missing values must remain missing, not be replaced with zero.
- LSA values must not automatically be described as state-level values.
- National and circle-level datasets must not be joined directly
  to LSA-level datasets without a valid aggregation rule.

## 6. Data preservation

Bronze data must remain unchanged.
Cleaning, standardisation, aggregation and joining
must be performed in Silver or Gold.
