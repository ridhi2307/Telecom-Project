# Open TelecomNexus in Power BI Desktop

1. Double-click **TelecomNexus.pbip** in this folder. Keep the adjacent `TelecomNexus.Report` and `TelecomNexus.SemanticModel` directories together. The project uses enhanced PBIR and an Import model. The Desktop version used here was 2.158.1177.0.
2. The **DataFolder** parameter points to this checkout's `powerbi\data`. If you move the repository, choose **Home → Transform data ▼ → Edit parameters**, select **DataFolder**, and enter the full path to the new `powerbi\data` directory.
3. Choose **Apply changes** if Desktop shows pending query edits, then **Home → Refresh**. On first open the source project can show blank cards until the six CSV partitions finish loading. If Desktop requests permission for the local file sources, review the listed paths. Wait for the data to load and press **Ctrl+S**. The local cache belongs to your Desktop session.
4. Use the bottom tabs or **Ctrl+click** a header navigation button. **Ctrl+click Reset filters** to clear the current page's slicers. Hover a chart mark for its category and measure values. Expand a service area in the Overview matrix to see its zone and category.

## Reconcile the presentation

| Page | With filters cleared | Interaction to check |
| --- | --- | --- |
| TRAI Industry Overview | June 14.79M, May 14.47M, growth 2.21%, unweighted LSA ARPU ₹187.95 | Select Zone I. June becomes 8.07M and May 7.80M across 11 circles. Hover the zone donut. |
| TRAI Usage & Subscribers | Unweighted prepaid 82.77%, voice 926.59 minutes/month, 22 circles | Select one LSA. The active-circle count becomes 1. Both national lines still span June 2025 through June 2026. |
| TRAI Network Quality | Intra-network success 99.50%, latency 27.22 ms, downtime 0.39% | Select MTNL. Intra-network success becomes 98.74% and latency is blank. The independent wireless broadband chart still shows five providers, led by Reliance Jio at 517.63M. |
| IBM Customer Churn | 7,043 customers, 1,869 churned, 26.54%, average bill $64.76, monthly charges of churned customers $139,130.85 | Select Month-to-month. Expect 3,875 customers, 1,655 churned, and 42.71%. Reset the page before presenting. |

MNP counts porting requests. IBM measures describe the US customer benchmark. The only relationship filters QoS from the unique LSA context. The national trend and both broadband tables are disconnected. QoS latency averages use 86 reported observations. The heatmap compares reported cells with the selected population's median. The fixed-wired export is available in the model.

## Reproduce the checks

The four PNGs in `screenshots` are captures from a refreshed Desktop verification copy. Desktop displayed the baseline cards on all four pages. Live slicer checks confirmed the Zone I volumes, the MTNL blank latency and independent broadband value, and all three Month-to-month customer counts/rate controls above. The IBM charges card abbreviates the full $139,130.85 value as $139.13K.

From the repository root, run the following in PowerShell with Python 3.

```powershell
python -B powerbi/TelecomNexus_Report/validate.py
```

The script checks local source values, relationship keys, report bindings and page structure. It writes observed values and the six source hashes to `validation_results.json`. The CSV-derived IBM rate is 1,869 ÷ 7,043 = 26.536987%, displayed as 26.54%. The SQL comments for Zone I and the brief's extra churn-rate decimals differ from the exported rows.

Power Query, DAX, calculated columns and formats are in `TelecomNexus.SemanticModel/model.bim`. The theme is in `TelecomNexus.Report/StaticResources/RegisteredResources/TelecomNexus.json`. To regenerate the authored definitions on a fresh copy, run `python -B powerbi/TelecomNexus_Report/build_report.py` before validation. This overwrites generated definitions and sets DataFolder to that checkout.
