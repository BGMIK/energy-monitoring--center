#!/usr/bin/env python3
"""Server-side public-data collector for MILCHO HUB. No credentials are stored here."""
import json, math, re, time, os, shutil, subprocess, tempfile, html
from datetime import datetime, timezone
from urllib.request import Request, urlopen

BASE = "https://raw.githubusercontent.com/yyoncho/eso-dashboard/data/data/"
URLS = {
    "generation": "https://www.eso.bg/api/rabota_na_EEC_json.php",
    "flows": "https://www.eso.bg/api/scada_live_json_pure.php",
    "frequency": "https://www.eso.bg/api/freq.json.php",
    "load": BASE + "today.jsonl",
    "official_load": "https://www.eso.bg/api/last24load.json.php",
    "ibex": "https://api.energy-charts.info/price?bzn=BG",
    "npp": "https://www.kznpp.org/bg/proizvodstvo/danni-za-elektroproizvodstvoto",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MILCHO-HUB/1.0)",
    "Accept": "application/json,text/plain,text/html,*/*",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": "https://www.eso.bg/doc/?460",
}
def get(url, timeout=18):
    req=Request(url + ("&" if "?" in url else "?") + "_hub=" + str(int(time.time()*1000)), headers=HEADERS)
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", "replace")
def number(v):
    try:
        x=float(str(v).replace(" ", "").replace(",", "."))
        return x if math.isfinite(x) else None
    except Exception:
        return None
def flatten(obj, out=None):
    out={} if out is None else out
    if isinstance(obj, dict):
        for k,v in obj.items():
            if isinstance(v,(dict,list)): flatten(v,out)
            else: out[str(k)]=v
    elif isinstance(obj,list):
        for item in obj:
            if isinstance(item,(list,tuple)) and len(item)>=2 and isinstance(item[0],str):
                out[item[0]]=item[1]
                flatten(item,out)
            elif isinstance(item,(dict,list)): flatten(item,out)
    return out
def pick(flat,*names):
    norm=lambda x: re.sub(r"\s+"," ",re.sub(r"\s*[0-9]+(?:[.,][0-9]+)?%","",str(x).strip().lower())).strip(" :;-—")
    wanted=[norm(n) for n in names]
    for exact in (True,False):
        for k,v in flat.items():
            nk=norm(k)
            if (nk in wanted) if exact else any(nk.startswith(w) for w in wanted if w):
                x=number(v)
                if x is not None: return x
    return None
def find_frequency(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if any(t in str(k).lower() for t in ("freq","hz","чест")):
                x=number(v)
                if x is not None and 45<=x<=55: return x
            x=find_frequency(v)
            if x is not None: return x
    elif isinstance(obj,list):
        for v in obj:
            x=find_frequency(v)
            if x is not None:return x
    elif isinstance(obj,(int,float)) and 45<=float(obj)<=55:return float(obj)
    return None
def fresh_mirror():
    mirror=json.loads(get(BASE+"latest.json",18))
    stamp=mirror.get("timestamp_utc")
    if not stamp:
        raise RuntimeError("ESO mirror timestamp missing")
    from datetime import datetime
    dt=datetime.fromisoformat(stamp.replace("Z","+00:00"))
    if (datetime.now(timezone.utc)-dt).total_seconds()>20*60:
        raise RuntimeError("ESO mirror snapshot is older than 20 minutes")
    return mirror

def browser_generation():
    """Render the official ESO operational page with a fresh Chromium profile."""
    chrome = next((p for p in (shutil.which("chromium"), shutil.which("chromium-browser"),
                               shutil.which("google-chrome"), shutil.which("google-chrome-stable"))
                   if p), None)
    if not chrome:
        raise RuntimeError("Chromium unavailable on collector runner")
    with tempfile.TemporaryDirectory(prefix="eso_hub_") as profile:
        url = "https://www.eso.bg/doc/?460&_scada_refresh=" + str(time.time_ns())
        cmd = [chrome, "--headless=new", "--no-sandbox", "--disable-gpu",
               "--disable-dev-shm-usage", "--disable-cache", "--incognito",
               "--no-first-run", "--disable-background-networking",
               "--disable-extensions", "--user-data-dir=" + profile,
               "--virtual-time-budget=4500", "--dump-dom", url]
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if not cp.stdout:
            raise RuntimeError("ESO browser render failed: " + cp.stderr[-200:])
    page = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", cp.stdout, flags=re.I | re.S)
    page = html.unescape(re.sub(r"<[^>]+>", " ", page))
    page = re.sub(r"\s+", " ", page)
    out = {}
    labels = ["АЕЦ", "Кондензационни ТЕЦ", "Топлофикационни ТЕЦ",
              "Заводски ТЕЦ", "ВЕЦ", "Малки ВЕЦ", "ВяЕЦ", "ФЕЦ", "Био ЕЦ",
              "ССЕЕ - зареждане", "ССЕЕ - разреждане",
              "ССЕБ - зареждане", "ССЕБ - разреждане", "Помпи", "Товар на РБ"]
    for label in labels:
        pat = re.escape(label) + r"\s+(?:[0-9]{1,3}(?:[.,][0-9]+)?\s*%\s+)?([0-9][0-9\s.,]*)"
        m = re.search(pat, page, re.I)
        if m:
            value = number(m.group(1))
            if value is not None:
                out[label] = value
    if not any(k in out for k in ("АЕЦ", "ФЕЦ", "ВЕЦ")):
        raise RuntimeError("Rendered ESO page contains no valid generation measurements")
    return out

def official_current_load():
    """Extract the latest valid system load from the official ESO endpoint."""
    raw = json.loads(get(URLS["official_load"]))
    f = flatten(raw)
    value = pick(f, "load_mw", "Товар на РБ", "Товар")
    if value is None:
        found = []
        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if str(k).strip().lower() in ("load_mw", "товар на рб", "товар", "load"):
                        n = number(v)
                        if n is not None and n > 0: found.append(n)
                    if isinstance(v, (dict, list)): walk(v)
            elif isinstance(x, list):
                for item in x: walk(item)
        walk(raw)
        value = found[-1] if found else None
    if value is None or value <= 0:
        raise RuntimeError("Official ESO load endpoint returned no valid value")
    return value

def run():
    result={"updated_at":datetime.now(timezone.utc).isoformat(timespec="seconds"),"sources":{},"values":{},"series":[]}
    def source(name, fn):
        try:
            fn()
            result["sources"][name]={"ok":True}
        except Exception as e:
            result["sources"][name]={"ok":False,"error":str(e)[:240]}
    def generation():
        try:
            raw=browser_generation()
        except Exception:
            try:
                raw=json.loads(get(URLS["generation"]))
            except Exception:
                raw=fresh_mirror().get("raw_gen_api",[])
        f=flatten(raw); v=result["values"]
        keys=["АЕЦ","Кондензационни ТЕЦ","Топлофикационни ТЕЦ","Заводски ТЕЦ","ВЕЦ","Малки ВЕЦ","ВяЕЦ","ФЕЦ","Био ЕЦ"]
        for k in keys:
            x=pick(f,k)
            if x is not None:v[k]=x
        charge=pick(f,"ССЕБ - зареждане","ССЕЕ - зареждане")
        discharge=pick(f,"ССЕБ - разреждане","ССЕЕ - разреждане")
        pumps=pick(f,"Помпи")
        if charge is not None:v["batt_charge_mw"]=charge
        if discharge is not None:v["batt_discharge_mw"]=discharge
        if pumps is not None:v["pump_mw"]=pumps
        v["nuclear"]=v.get("АЕЦ")
        thermal_keys=["Кондензационни ТЕЦ","Топлофикационни ТЕЦ","Заводски ТЕЦ"]
        if any(k in v for k in thermal_keys):v["thermal"]=sum(v.get(k,0) for k in thermal_keys)
        hydro_keys=["ВЕЦ","Малки ВЕЦ"]
        if any(k in v for k in hydro_keys):v["hydro"]=sum(v.get(k,0) for k in hydro_keys)
        renewable_keys=["ВяЕЦ","ФЕЦ","Био ЕЦ"]
        if any(k in v for k in renewable_keys):v["renew"]=sum(v.get(k,0) for k in renewable_keys)
        if charge is not None or discharge is not None or pumps is not None:
            v["bess"]=(pumps or 0)+(charge or 0)-(discharge or 0)
        if not any(k in v for k in keys):
            mirror=fresh_mirror()
            for k in keys:
                x=number(mirror.get(k))
                if x is not None:v[k]=x
            for key in ("batt_charge_mw","batt_discharge_mw","pumps_mw","pump_mw","load_mw","Товар на РБ"):
                x=number(mirror.get(key))
                if x is not None:v[key]=x
            v["nuclear"]=v.get("АЕЦ")
            if any(k in v for k in ("Кондензационни ТЕЦ","Топлофикационни ТЕЦ","Заводски ТЕЦ")):v["thermal"]=sum(v.get(k,0) for k in ("Кондензационни ТЕЦ","Топлофикационни ТЕЦ","Заводски ТЕЦ"))
            if any(k in v for k in ("ВЕЦ","Малки ВЕЦ")):v["hydro"]=sum(v.get(k,0) for k in ("ВЕЦ","Малки ВЕЦ"))
            if any(k in v for k in ("ВяЕЦ","ФЕЦ","Био ЕЦ")):v["renew"]=sum(v.get(k,0) for k in ("ВяЕЦ","ФЕЦ","Био ЕЦ"))
            if any(k in v for k in ("batt_charge_mw","batt_discharge_mw","pump_mw","pumps_mw")):v["bess"]=(v.get("pump_mw",v.get("pumps_mw",0)) or 0)+(v.get("batt_charge_mw",0) or 0)-(v.get("batt_discharge_mw",0) or 0)
        if not any(k in v for k in keys):raise RuntimeError("ESO generation endpoint returned no recognized generation rows")
    def flows():
        try:
            raw=json.loads(get(URLS["flows"]))
        except Exception:
            raw=fresh_mirror()
        f=flatten(raw); v=result["values"]
        aliases={"SR_mw":("SR_mw","SR","Сърбия","Serbia"),"RO_mw":("RO_mw","RO","Румъния","Romania"),"TR_mw":("TR_mw","TR","Турция","Turkey"),"MK_mw":("MK_mw","MK","Македония","Северна Македония","North Macedonia"),"GR_mw":("GR_mw","GR","Гърция","Greece")}
        for k,a in aliases.items():
            x=pick(f,*a)
            if x is not None:v[k]=x
        if not any(k in v for k in aliases):
            mirror=fresh_mirror()
            for k in aliases:
                x=number(mirror.get(k))
                if x is not None:v[k]=x
        if not any(k in v for k in aliases):raise RuntimeError("ESO flow endpoint returned no country values")
        v["net"]=sum(v[k] for k in aliases if k in v)
    def load():
        rows=[json.loads(line) for line in get(URLS["load"],25).splitlines() if line.strip()]
        pts=[]
        for row in rows:
            t=row.get("timestamp_utc") or row.get("timestamp")
            x=number(row.get("load_mw",row.get("Товар на РБ")))
            if t and x is not None and x>0:pts.append({"t":t,"v":x})
        pts=pts[-288:]
        if len(pts)<2:raise RuntimeError("ESO load feed has fewer than two valid points")
        result["series"]=pts
        try:
            result["values"]["load"]=official_current_load()
        except Exception:
            result["values"]["load"]=pts[-1]["v"]
    def frequency():
        raw=json.loads(get(URLS["frequency"]))
        x=find_frequency(raw)
        if x is None:raise RuntimeError("Frequency value not found in ESO response")
        result["values"]["frequency"]=x
    def co2():
        # Trading Economics public EU Carbon Permits page (daily CFD benchmark).
        page=get("https://tradingeconomics.com/commodity/carbon",25)
        txt=re.sub(r"<script\\b.*?</script>|<style\\b.*?</style>", " ", page, flags=re.I|re.S)
        txt=re.sub(r"<[^>]+>", " ", txt)
        txt=re.sub(r"&nbsp;|&#160;", " ", txt, flags=re.I)
        txt=re.sub(r"\\s+", " ", txt)
        # Prefer the dated summary sentence; do not mistake other commodity prices for EUA.
        m=re.search(r"EU Carbon Permits\\s+(?:rose|fell|increased|decreased)\\s+to\\s+([0-9][0-9,.]*)\\s+EUR\\s+on\\s+([A-Za-z]+\\s+[0-9]{1,2},\\s+[0-9]{4}),\\s+(?:up|down)\\s+([0-9,.]+)%", txt, re.I)
        if not m:
            # The page also exposes the headline quote as Actual / Daily Change.
            m=re.search(r"Actual\\s+([0-9][0-9,.]*)\\s+Daily Change\\s+([+-]?[0-9,.]+)%", txt, re.I)
            if m:
                # Keep date tied to the page's explicit update stamp when available.
                d=re.search(r"last updated on\\s+([A-Za-z]+\\s+[0-9]{1,2}\\s+of\\s+[0-9]{4})", txt, re.I)
                quote_date=d.group(1) if d else datetime.now(timezone.utc).strftime("%Y-%m-%d")
                price=number(m.group(1))
                change=number(m.group(2))
            else:
                pos=txt.lower().find("eu carbon permits")
                excerpt=txt[max(0,pos-80):pos+500] if pos>=0 else txt[:500]
                raise RuntimeError("Trading Economics quote not present in fetched HTML: "+excerpt[:400])
        else:
            price=number(m.group(1))
            change=number(m.group(3))
            quote_date=m.group(2)
        if price is None or not 1 <= price <= 1000:
            raise RuntimeError("Trading Economics EUA price failed validation")
        result["values"]["co2_eur_t"]=price
        result["values"]["co2_daily_percent"]=change
        result["values"]["co2_quote_date"]=quote_date
    def ibex():
        # Do not relabel Energy-Charts BG prices as official IBEX data.
        # Public redistribution terms for the BG series are restrictive;
        # official IBEX API access requires a separate agreement/account.
        raise RuntimeError("Официален IBEX API достъп не е конфигуриран. Не публикуваме заместителна цена от Energy-Charts.")
    def npp():
        page=get(URLS["npp"])
        txt=re.sub(r"<script\b.*?</script>|<style\b.*?</style>"," ",page,flags=re.I|re.S)
        txt=re.sub(r"<[^>]+>"," ",txt);txt=re.sub(r"\s+"," ",txt)
        for n in (5,6):
            m=re.search(r"Блок\s*"+str(n)+r"\s+([0-9][0-9\s.,]*)\s*MW",txt,re.I)
            if m:
                x=number(m.group(1))
                if x is not None:result["values"]["block"+str(n)]=x
        if "block5" not in result["values"] and "block6" not in result["values"]:
            raise RuntimeError("Unit 5/6 output not found in official page")
    for name,fn in [("eso_generation",generation),("eso_flows",flows),("eso_load",load),("frequency",frequency),("ibex",ibex),("co2_eua",co2),("kozloduy",npp)]:
        source(name,fn)
    result["sources"]["eso_generation"]["provider"]="ЕСО оперативна страница Chromium; резервен ЕСО API / валидирано огледало"
    result["sources"]["eso_flows"]["provider"]="ЕСО SCADA API; при недостъпност се използва резервно копие"
    result["sources"]["eso_load"]["provider"]="ЕСО last24load за текущ товар (при достъпност); външно огледало за 24h серия и резервен товар"
    result["sources"]["frequency"]["provider"]="ЕСО frequency endpoint"
    result["sources"]["ibex"]["provider"]="БНЕБ/IBEX — няма конфигуриран официален API достъп"
    result["sources"]["co2_eua"]["provider"]="Trading Economics · EU Carbon Permits · дневна котировка CFD, EUR/tCO₂"
    result["sources"]["kozloduy"]["provider"]="Официален сайт на АЕЦ Козлодуй"
    # Publish a complete fresh snapshot only when every core ESO feed is valid.
    required_eso = ("eso_generation", "eso_flows", "eso_load", "frequency")
    failed = [name for name in required_eso if not result["sources"].get(name, {}).get("ok")]
    if failed:
        details = {name: result["sources"].get(name, {}) for name in failed}
        raise RuntimeError("Fresh ESO snapshot rejected; previous data.json preserved: " +
                           json.dumps(details, ensure_ascii=False))
    result["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open("data.json","w",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print(json.dumps(result["sources"],ensure_ascii=False))
if __name__=="__main__":run()

# Manual trigger: verify that the live data collector is still running.
# Commit-triggered validation: keep this collector path eligible for workflow checks.

# Scheduled refresh health-check marker. Trigger a fresh scheduled collector run after stale snapshot detection.
# Manual validation trigger: verify the scheduled ESO collector on main.
