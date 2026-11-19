"""Materialize the project entry point and Import semantic model from repository sources."""
import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data"
MODEL = ROOT / "TelecomNexus.SemanticModel"
AREA = "trai_lsa_switching_usage_context"
QOS = "trai_qos"
IBM = "ibm_telco_customer_churn"
NATIONAL = "trai_national_wireless_usage_trends"
WIRELESS = "trai_wireless_broadband"
FIXED = "trai_fixed_wired_broadband"


def write(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read(name):
    with (DATA / f"{name}.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def type_name(table, field):
    if field in "Count Tenure_Months Churn_Value Churn_Score CLTV serial_number rank source_page".split():
        return "int64"
    if field in {"Monthly_Charges", "Total_Charges"}:
        return "decimal"
    if field in {"Latitude", "Longitude", "subscriber_base_million"} or field.startswith("metric_"):
        return "double"
    if table == AREA and field not in {"canonical_lsa", "zone", "category", "mnp_report_month", "usage_reporting_period"}:
        return "double"
    if table == NATIONAL and field not in {"reporting_period", "source_table"}:
        return "double"
    return "string"


def display_format(name):
    if any(term in name for term in ("Rate", "Pct", "Share")):
        return "0.00%"
    if "INR" in name:
        return '"₹"#,0.00'
    if "Charges" in name:
        return '"$"#,0.00'
    if "Customers" in name or "Circles" in name:
        return "#,0"
    return "#,0.00"


def build():
    dax = (ROOT.parent / "DAX_MEASURES.md").read_text(encoding="utf-8")
    measures, bands = re.findall(r"(?s)\x60{3}dax\n(.*?)\n\x60{3}", dax)
    tables = []
    for name in (AREA, QOS, IBM, NATIONAL, WIRELESS, FIXED):
        fields = list(read(name)[0])
        columns = []
        transforms = []
        numeric = []
        for f in fields:
            kind = type_name(name, f)
            mtype = {"int64": "Int64.Type", "decimal": "Currency.Type", "double": "type number", "string": "type text"}[kind]
            transforms.append('{"%s", %s}' % (f, mtype))
            if kind != "string":
                numeric.append('"%s"' % f)
            columns.append(dict(name=f, sourceColumn=f, dataType=kind, summarizeBy="none"))
        query = ["let", f'    Source = Csv.Document(File.Contents(DataFolder & "\\{name}.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
                 '    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
                 '    Clean = Table.TransformColumns(Headers, List.Transform({' + ", ".join(numeric) + '}, (col) => {col, each if _ = null or Text.Trim(_) = "" then null else _})),',
                 '    Typed = Table.TransformColumnTypes(Clean, {' + ", ".join(transforms) + '}, "en-US")']
        result = "Typed"
        if name == NATIONAL:
            query[-1] += ","
            query.append('    Periods = Table.AddColumn(Typed, "Period_Order", each let d = Date.FromText("1 " & [reporting_period], [Format="d MMMM yyyy", Culture="en-US"]) in Date.Year(d)*100 + Date.Month(d), Int64.Type)')
            result = "Periods"
            columns[0]["sortByColumn"] = "Period_Order"
            columns.append(dict(name="Period_Order", sourceColumn="Period_Order", dataType="int64", isHidden=True, summarizeBy="none"))
        if name == IBM:
            for line in bands.splitlines():
                f, expression = line.split(" = ", 1)
                band = f == "Tenure_Band"
                columns.append(dict(name=f, type="calculated", dataType="string" if band else "int64",
                                    expression=expression, summarizeBy="none",
                                    **({"sortByColumn": "Tenure_Band_Order"} if band else {"isHidden": True})))
        partition = dict(name=name, mode="import", source=dict(type="m", expression=query + ["in", "    " + result]))
        table = dict(name=name, columns=columns, partitions=[partition], measures=[])
        for line in measures.splitlines():
            f, expr = line.split(" = ", 1)
            owner = {"IBM": IBM, "TRAI": AREA, "QoS": QOS, "National": NATIONAL, "Wireless": WIRELESS}[f.split()[0]]
            if owner == name:
                table["measures"].append(dict(name=f, expression=expr, formatString=display_format(f)))
        if name == QOS:
            table["measures"].append(dict(name="Latency cell color", isHidden=True,
                expression='VAR ms = [QoS Avg Latency ms] RETURN IF(ISBLANK(ms), BLANK(), IF(ms >= MEDIANX(ALLSELECTED(trai_qos), trai_qos[metric_12]), "#F6E2BD", "#C6E5DF"))'))
        tables.append(table)
    areas = [r["canonical_lsa"] for r in read(AREA)]
    qos = read(QOS)
    valid = (len(areas) == len(set(areas)) and all(areas) and all(r["lsa"] in areas for r in qos)
             and len({(r["operator"], r["lsa"]) for r in qos}) == len(qos))
    relationships = [dict(name="LSAContextToQoS", fromTable=QOS, fromColumn="lsa", fromCardinality="many",
                          toTable=AREA, toColumn="canonical_lsa", toCardinality="one", crossFilteringBehavior="oneDirection")] if valid else []
    model = dict(culture="en-US", sourceQueryCulture="en-US", defaultPowerBIDataSourceVersion="powerBI_V3",
                 tables=tables, relationships=relationships, expressions=[dict(name="DataFolder", kind="m",
                 expression='"' + str(DATA).replace('"', '""') + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]')])
    write(MODEL / "model.bim", dict(name="TelecomNexus", compatibilityLevel=1600, model=model))
    write(MODEL / "definition.pbism", {"version": "1.0", "settings": {}})
    write(ROOT / "TelecomNexus.pbip", {"version": "1.0", "artifacts": [{"report": {"path": "TelecomNexus.Report"}}], "settings": {"enableAutoRecovery": True}})
    write(ROOT / "TelecomNexus.Report/definition.pbir", {"version": "4.0", "datasetReference": {"byPath": {"path": "../TelecomNexus.SemanticModel"}}})


if __name__ == "__main__":
    build()
