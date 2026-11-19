"""Validate source controls and the saved report bindings without network access."""
from math import isclose
from statistics import mean
from datetime import datetime
import hashlib
import json
from build_model import AREA, QOS, IBM, FIXED, WIRELESS, NATIONAL, DATA, MODEL, ROOT, read, write


def validate():
    checks = {}

    def check(label, actual, expected, tolerance=0):
        if isinstance(expected, (int, float)):
            ok = isclose(actual, expected, rel_tol=0, abs_tol=tolerance)
        else:
            ok = actual == expected
        if not ok:
            raise ValueError(f"{label}: observed {actual}, expected {expected}")
        checks[label] = actual

    def values(rows, field):
        return [float(row[field]) for row in rows if row[field].strip()]

    a, q, b = read(AREA), read(QOS), read(IBM)
    for table, count in [(AREA,22),(QOS,88),(IBM,7043),(NATIONAL,5),(WIRELESS,5),(FIXED,5)]:
        check(table + " rows", len(read(table)), count)
    check("IBM distinct customers", len({r["CustomerID"] for r in b if r["CustomerID"]}), 7043)
    churned = [r for r in b if r["Churn_Value"] == "1"]
    check("IBM churned customers", len(churned), 1869)
    check("IBM churn percent", len(churned)*100/len(b), 26.536987, 0.000001)
    check("IBM average bill USD", mean(values(b,"Monthly_Charges")), 64.7617, 0.0001)
    check("IBM monthly charges of churned customers USD", sum(values(churned,"Monthly_Charges")),139130.85,0.00001)
    check("IBM missing total charges", sum(not r["Total_Charges"].strip() for r in b),11)
    monthly = [r for r in b if r["Contract"] == "Month-to-month"]
    check("Month-to-month customers",len(monthly),3875)
    check("Month-to-month churned",sum(values(monthly,"Churn_Value")),1655)
    may, june = "may_2026_porting_requests_millions", "june_2026_porting_requests_millions"
    check("May MNP millions",sum(values(a,may)),14.47,1e-9)
    check("June MNP millions",sum(values(a,june)),14.79,1e-9)
    check("Unweighted ARPU INR",mean(values(a,"arpu_inr_per_month")),187.9545,0.0001)
    check("Unweighted prepaid percent",mean(values(a,"prepaid_percentage")),82.7659,0.0001)
    check("Unweighted MOU",mean(values(a,"total_mou_per_month")),926.5909,0.0001)
    zone = [r for r in a if r["zone"] == "Zone I"]
    check("Zone I circles",len(zone),11)
    check("Zone I May millions",sum(values(zone,may)),7.80,1e-9)
    check("Zone I June millions",sum(values(zone,june)),8.07,1e-9)
    check("Area keys",len({r["canonical_lsa"] for r in a if r["canonical_lsa"]}),22)
    check("QoS distinct grain",len({(r["operator"],r["lsa"]) for r in q}),88)
    check("QoS operators",len({r["operator"] for r in q}),5)
    check("QoS distinct service areas",len({r["lsa"] for r in q}),22)
    check("QoS orphan LSAs",sorted({r["lsa"] for r in q}-{r["canonical_lsa"] for r in a}),[])
    check("QoS intra success percent",mean(values(q,"metric_05")),99.503977,1e-6)
    check("QoS mean latency ms",mean(values(q,"metric_12")),27.223023,1e-6)
    check("QoS mean downtime percent",mean(values(q,"metric_02")),0.390795,1e-6)
    check("QoS blank metric cells",sum(not v.strip() for row in q for f,v in row.items() if f.startswith("metric_")),32)
    mtnl = [r for r in q if r["operator"]=="MTNL"]
    check("MTNL latency observations",len(values(mtnl,"metric_12")),0)
    check("MTNL intra success percent",mean(values(mtnl,"metric_05")),98.74,1e-6)
    national = sorted(read(NATIONAL),key=lambda row:datetime.strptime(row["reporting_period"],"%B %Y"))
    check("National quarter sequence",[r["reporting_period"] for r in national],["June 2025","September 2025","December 2025","March 2026","June 2026"])

    model = json.loads((MODEL/"model.bim").read_text(encoding="utf-8"))["model"]
    rels = [(r["fromTable"],r["fromColumn"],r["toTable"],r["toColumn"],r.get("crossFilteringBehavior","oneDirection")) for r in model["relationships"]]
    check("Model relationships",rels,[(QOS,"lsa",AREA,"canonical_lsa","oneDirection")])
    fields = {}
    for t in model["tables"]:
        fields[t["name"]] = {kind:{f["name"] for f in t.get(group, [])} for kind,group in [("Column","columns"),("Measure","measures")]}
        check(t["name"]+" partition mode",t["partitions"][0]["mode"],"import")
    folder = ROOT/"TelecomNexus.Report/definition/pages"
    pages = json.loads((folder/"pages.json").read_text())["pageOrder"]
    check("Page count",len(pages),4)
    for index,page in enumerate(pages):
        types = []
        for file in (folder/page/"visuals").glob("*/visual.json"):
            v = json.loads(file.read_text(encoding="utf-8"))["visual"]
            types.append(v["visualType"])
            for role in v.get("query",{}).get("queryState",{}).values():
                for projection in role["projections"]:
                    kind,ref = next(iter(projection["field"].items()))
                    table = ref["Expression"]["SourceRef"]["Entity"]
                    if ref["Property"] not in fields[table][kind] or (index==3)!=(table==IBM):
                        raise ValueError(f"Invalid binding in {file}")
        for kind,count in [("pageNavigator",1),("actionButton",1),("slicer",[2,3,2,5][index]),("card",[4,3,3,5][index])]:
            check(f"Page {index+1} {kind}",types.count(kind),count)

    return {"checks":checks, "csv_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DATA.glob("*.csv"))}}


if __name__ == "__main__":
    results = validate()
    write(ROOT/"validation_results.json",results)
    print(f"Passed {len(results['checks'])} source and project checks.")
