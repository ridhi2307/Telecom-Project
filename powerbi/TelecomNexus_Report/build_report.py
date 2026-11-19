"""Write the native PBIR page definitions. All visual values bind to explicit measures."""
import hashlib
from build_model import ROOT, AREA, QOS, IBM, NATIONAL, WIRELESS, build, write

REPORT = ROOT / "TelecomNexus.Report"
DEF = REPORT / "definition"
BASE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
PAGES = ["TRAI Industry Overview", "TRAI Usage & Subscribers", "TRAI Network Quality", "IBM Customer Churn"]


def schema(item, version):
    return {"$schema": f"{BASE}{item}/{version}/schema.json"}


def uid(name):
    return hashlib.sha256(name.encode()).hexdigest()[:20]


def literal(value):
    if isinstance(value, bool):
        token = str(value).lower()
    elif isinstance(value, int):
        token = f"{value}D"
    else:
        token = "'" + value.replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": token}}}


def color(value):
    return {"solid": {"color": literal(value)}}


def obj(**props):
    return [{"properties": props}]


def field(table, name, measure):
    kind = "Measure" if measure else "Column"
    return {kind: {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}}


class Page:
    def __init__(self, index, subtitle):
        self.name = PAGES[index]
        key = uid(self.name)
        self.path = DEF / "pages" / key
        self.number = 0
        write(self.path / "page.json", dict(**schema("page", "2.0.0"), name=key, displayName=self.name,
              displayOption="FitToPage", width=1440, height=810,
              objects={"background": obj(color=color("#10283F"), transparency=literal(0))}))
        paragraphs = [{"textRuns": [{"value": value, "textStyle": {"fontFamily": "Segoe UI", "fontSize": size, "color": tone}}]}
                      for value, size, tone in [(self.name, "22pt", "#FFFFFF"), (subtitle, "11pt", "#AEE5DC")]]
        self.visual("textbox", "", (18, 6, 565, 75), objects={"general": obj(paragraphs=paragraphs)})
        self.visual("pageNavigator", "", (590, 14, 698, 52))

    def reset(self):
        self.visual("actionButton", "", (1296,14,126,52), objects={
            "icon": obj(show=literal(False)),
            "text": obj(show=literal(True)) + [{"selector":{"id":"default"},"properties":{
                "text":literal("Reset filters"),"horizontalAlignment":literal("center")}}]})

    def visual(self, kind, title, rect, table=None, roles=None, order=None, objects=None):
        self.number += 1
        key = uid(self.name + str(self.number))
        container = {"title": obj(show=literal(False)), "background": obj(show=literal(bool(title) or kind in {"pageNavigator","actionButton"}),
                                       color=color("#FFFFFF"), transparency=literal(0))}
        if title:
            container["title"] = obj(show=literal(True), text=literal(title), fontSize=literal(12),
                                     fontColor=color("#10283F"))
        visual = {"visualType": kind, "visualContainerObjects": container, "drillFilterOtherVisuals": True}
        if objects:
            visual["objects"] = objects
        if kind == "actionButton":
            container["visualLink"] = obj(show=literal(True), type=literal("ClearAllSlicers"))
        if roles:
            state = {}
            for role, names in roles.items():
                projections = []
                for item in names:
                    is_measure = item.startswith("@")
                    name = item.lstrip("@")
                    projections.append({"field": field(table, name, is_measure), "queryRef": table + "." + name,
                                        "nativeQueryRef": name})
                state[role] = {"projections": projections}
            visual["query"] = {"queryState": state}
            if order:
                name, direction = order
                visual["query"]["sortDefinition"] = {"sort": [{"field": field(table, name.lstrip("@"), name.startswith("@")),
                                                               "direction": direction}]}
        x, y, w, h = rect
        write(self.path / "visuals" / key / "visual.json",
              dict(**schema("visualContainer", "2.1.0"), name=key, position=dict(x=x, y=y, width=w, height=h,
                   z=self.number, tabOrder=self.number), visual=visual))

    def row(self, items, table, slicers=False):
        step = 1416 / len(items)
        for i, (title, name) in enumerate(items):
            rect = (16 + round(i * step), 84 if slicers else 161, round(step) - 8, 69 if slicers else 93)
            if slicers:
                self.visual("slicer", title, rect, table, {"Values": [name]}, objects={"data": obj(mode=literal("Dropdown")),
                            "header": obj(show=literal(False))})
            else:
                self.visual("card", title, rect, table, {"Values": ["@" + name]}, objects={"labels": obj(labelDisplayUnits=literal(0),
                            fontSize=literal(23)), "categoryLabels": obj(show=literal(False))})

    def bars(self, title, rect, table, category, measures, order=None, kind="clusteredBarChart"):
        self.visual(kind, title, rect, table, {"Category": [category], "Y": ["@" + m for m in measures]}, order)


def build_pages():
    p = Page(0, "TRAI India  •  May–June 2026  •  Porting requests do not confirm churn.")
    p.row([("Zone", "zone"), ("Circle category", "category")], AREA, True)
    p.row([("June MNP requests (M)", "TRAI June MNP M"), ("May MNP requests (M)", "TRAI May MNP M"),
           ("Request growth • MoM", "TRAI MNP Growth Pct"), ("Unweighted LSA ARPU (₹/month)", "TRAI Unweighted ARPU INR")], AREA)
    p.bars("May and June requests by service area (M)", (16,264,696,528), AREA, "canonical_lsa",
           ["TRAI May MNP M","TRAI June MNP M"], ("@TRAI June MNP M","Descending"))
    p.visual("donutChart","June requests by zone (M)",(722,264,700,228),AREA,{"Category":["zone"],"Y":["@TRAI June MNP M"]})
    p.visual("pivotTable","Porting requests by area (M)",(722,502,700,290),AREA,
             {"Rows":["canonical_lsa","zone","category"],"Values":["@TRAI May MNP M","@TRAI June MNP M","@TRAI MNP Growth M"]})

    p.reset()
    p = Page(1, "TRAI India  •  April–June 2026 circles  •  Five national quarters")
    p.row([("Service area","canonical_lsa"),("Zone","zone"),("Circle category","category")],AREA,True)
    p.row([("Unweighted prepaid share","TRAI Unweighted Prepaid Share"),("Unweighted voice minutes/month","TRAI Unweighted Total MOU"),
           ("Active circles","TRAI Active Circles")],AREA)
    p.bars("Mean outgoing and incoming minutes by service area",(16,264,696,528),AREA,"canonical_lsa",["TRAI Outgoing MOU","TRAI Incoming MOU"])
    p.bars("Unweighted ARPU by category (₹/month)",(722,264,700,192),AREA,"category",["TRAI Unweighted ARPU INR"])
    for i,(title,measure) in enumerate([("National ARPU (₹/month)","National ARPU INR"),("National realization (₹/GB)","National Revenue per GB INR")]):
        p.bars(title,(722,466+168*i,700,158),NATIONAL,"reporting_period",[measure],("reporting_period","Ascending"),"lineChart")

    p.reset()
    p = Page(2, "TRAI India  •  June 2026  •  Operator QoS and provider broadband")
    p.row([("Network operator","operator"),("QoS service area","lsa")],QOS,True)
    p.row([("Intra-network call setup success","QoS Intra Call Setup Rate"),("Mean latency (ms)","QoS Avg Latency ms"),
           ("Mean cell downtime","QoS Avg Cell Downtime Pct")],QOS)
    p.visual("pivotTable","Mean latency (ms) • blank cells indicate unavailable readings",(16,264,696,528),QOS,
             {"Rows":["lsa"],"Columns":["operator"],"Values":["@QoS Avg Latency ms"]},
             objects={"values":[{"selector":{"data":[{"dataViewWildcard":{"matchingOption":1}}],
                       "metadata":QOS+".QoS Avg Latency ms"},"properties":{
                       "backColor":{"solid":{"color":{"expr":field(QOS,"Latency cell color",True)}}}}}]})
    p.bars("Mean intra- and inter-network call setup success",(722,264,700,259),QOS,"operator",["QoS Intra Call Setup Rate","QoS Inter Call Setup Rate"])
    p.bars("June wireless broadband subscribers (M)",(722,533,700,259),WIRELESS,"service_provider",["Wireless Subscribers M"],("@Wireless Subscribers M","Descending"))

    p.reset()
    p = Page(3, "IBM Telco  /  United States     •     Customer churn benchmark sample")
    slicers = [("Contract","Contract"),("Payment method","Payment_Method"),("Internet service","Internet_Service"),
               ("Gender","Gender"),("Senior citizen","Senior_Citizen")]
    p.row(slicers,IBM,True)
    p.row([("Customers","IBM Customers"),("Churned customers","IBM Churned Customers"),("Churn rate","IBM Churn Rate"),
           ("Avg monthly charges (USD)","IBM Avg Monthly Charges"),("Monthly charges of churned customers (USD)","IBM Churned Monthly Charges")],IBM)
    for i,(label,f) in enumerate(slicers[:3]+[("Tenure band","Tenure_Band")]):
        p.bars("Churn rate by "+label.lower(),(16+(i%2)*706,264+(i//2)*269,696,259),IBM,f,["IBM Churn Rate"],
               (f,"Ascending") if i==3 else ("@IBM Churn Rate","Descending"))
    p.reset()


def build_report():
    theme = "TelecomNexus.json"
    write(REPORT / "StaticResources/RegisteredResources" / theme, {
        "name":"TelecomNexus", "dataColors":["#007F79","#5079AD","#D69838","#42637B","#79B9AB"],
        "background":"#FFFFFF","foreground":"#10283F","tableAccent":"#007F79"})
    themes = {}
    for key,name,kind in [("baseTheme","CY24SU06","SharedResources"),("customTheme",theme,"RegisteredResources")]:
        themes[key] = dict(name=name,reportVersionAtImport="5.55",type=kind)
    write(DEF / "report.json", dict(**schema("report","2.1.0"),themeCollection=themes,resourcePackages=[
        dict(name="SharedResources",type="SharedResources",items=[dict(name="CY24SU06",path="BaseThemes/CY24SU06.json",type="BaseTheme")]),
        dict(name="RegisteredResources",type="RegisteredResources",items=[dict(name=theme,path=theme,type="CustomTheme")])]))
    write(DEF / "version.json",dict(**schema("versionMetadata","1.0.0"),version="2.0.0"))
    ids = [uid(p) for p in PAGES]
    write(DEF / "pages/pages.json",dict(**schema("pagesMetadata","1.0.0"),pageOrder=ids,activePageName=ids[0]))
    build_pages()


if __name__ == "__main__":
    build()
    build_report()
