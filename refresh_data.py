#!/usr/bin/env python3
"""Server-side public-data collector for MILCHO HUB. No credentials are stored here."""
import json, math, re, time, os, copy, html, subprocess, tempfile, shutil
from datetime import datetime, timezone
from urllib.request import Request, urlopen

BASE = "https://raw.githubusercontent.com/yyoncho/eso-dashboard/data/data/"
URLS = {
    "generation": "https://www.eso.bg/api/rabota_na_EEC_json.php",
    "flows": "https://www.eso.bg/api/scada_live_json_pure.php",
    "frequency": "https://www.eso.bg/api/freq.json.php",
    "load": BASE + "today.jsonl",
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

def browser_dump(url, wait_ms=4500):
    """Fresh headless Chromium session: hard-refresh the JavaScript-rendered ESO page."""
    candidates = [
        os.getenv("CHROME_BIN"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chrome"),
    ]
    chrome = next((p for p in candidates if p and os.path.isfile(p)), None)
    if not chrome:
        raise RuntimeError("Chromium/Chrome executable not found on server")
    token = str(time.time_ns())
    fresh_url = url + ("&" if "?" in url else "?") + "_scada_refresh=" + token
    profile = tempfile.mkdtemp(prefix="eso_scada_browser_")
    try:
        cmd = [
            chrome, "--headless=new", "--disable-gpu", "--disable-cache",
            "--disk-cache-size=1", "--media-cache-size=1", "--incognito",
            "--no-first-run", "--no-default-browser-check",
            "--disable-background-networking", "--disable-extensions",
            "--no-sandbox", "--disable-dev-shm-usage",
            "--user-data-dir=" + profile,
            "--virtual-time-budget=" + str(wait_ms), "--dump-dom", fresh_url,
        ]
        cp = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            errors="ignore", timeout=max(20, int(wait_ms / 1000) + 15),
        )
        if cp.returncode != 0 and not cp.stdout:
            raise RuntimeError((cp.stderr or "Chromium failed")[-600:])
        if not cp.stdout.strip():
            raise RuntimeError("Chromium returned an empty DOM")
        return cp.stdout
    finally:
        shutil.rmtree(profile, ignore_errors=True)

def text_from_dom(dom):
    dom = re.sub(r"<script\b.*?</script>", " ", dom, flags=re.I | re.S)
    dom = re.sub(r"<style\b.*?</style>", " ", dom, flags=re.I | re.S)
    dom = re.sub(r"<[^>]+>", " ", dom)
    return re.sub(r"\s+", " ", html.unescape(dom)).strip()

def browser_number(text, label):
    esc = re.escape(label)
    patterns = [
        rf"{esc}\s+[0-9]{{1,3}}(?:[.,][0-9]+)?\s*%\s+([0-9][0-9\s.,]*)",
        rf"{esc}\s+[0-9]{{1,3}}(?:[.,][0-9]+)?\s*%\s+([0-9][0-9\s.,]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.I)
        if match:
            val = number(match.group(1))
            if val is not None:
                return val
    return None

def read_eso_browser_generation():
    dom = browser_dump("https://www.eso.bg/doc/?460", wait_ms=4500)
    text = text_from_dom(dom)
    labels = {
        "АЕЦ": "АЕЦ",
        "Кондензационни ТЕЦ": "Кондензационни ТЕЦ",
        "Топлофикационни ТЕЦ": "Топлофикационни ТЕЦ",
        "Заводски ТЕЦ": "Заводски ТЕЦ",
        "ВЕЦ": "ВЕЦ",
        "Малки ВЕЦ": "Малки ВЕЦ",
        "ВяЕЦ": "ВяЕЦ",
        "ФЕЦ": "ФЕЦ",
        "Био ЕЦ": "Био ЕЦ",
        "batt_discharge_mw": "ССЕЕ - разреждане",
        "batt_charge_mw": "ССЕЕ - зареждане",
        "batt_discharge_sseb_mw": "ССЕБ - разреждане",
        "batt_charge_sseb_mw": "ССЕБ - зареждане",
        "pump_mw": "Помпи",
        "load_mw": "Товар на РБ",
    }
    data = {}
    for key, label in labels.items():
        val = browser_number(text, label)
        if val is not None:
            data[key] = val
    if "batt_charge_sseb_mw" in data and "batt_charge_mw" not in data:
        data["batt_charge_mw"] = data["batt_charge_sseb_mw"]
    if "batt_discharge_sseb_mw" in data and "batt_discharge_mw" not in data:
        data["batt_discharge_mw"] = data["batt_discharge_sseb_mw"]
    for key, label in {
        "SR_mw": "Сърбия", "RO_mw": "Румъния", "TR_mw": "Турция",
        "MK_mw": "Северна Македония", "GR_mw": "Гърция",
    }.items():
        val = browser_number(text, label)
        if val is not None:
            data[key] = val
    if not any(k in data for k in ("АЕЦ", "Кондензационни ТЕЦ", "Топлофикационни ТЕЦ", "Заводски ТЕЦ", "ВЕЦ", "Малки ВЕЦ", "ВяЕЦ", "ФЕЦ", "Био ЕЦ")):
        raise RuntimeError("Fresh ESO browser DOM contained no recognized generation values")
    data["_live_source"] = "ESO BROWSER HARD REFRESH"
    data["_received_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return data

def run():
    try:
        with open("data.json", "r", encoding="utf-8") as old_file:
            previous = json.load(old_file)
    except Exception:
        previous = {}
    result = {"updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "revision": int(previous.get("revision", 0)) + 1, "sources": copy.deepcopy(previous.get("sources", {})), "values": copy.deepcopy(previous.get("values", {})), "series": copy.deepcopy(previous.get("series", []))}
    def source(name, fn):
        before_values = copy.deepcopy(result["values"])
        before_series = copy.deepcopy(result["series"])
        old_meta = result["sources"].get(name, {})
        checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        owned = {"eso_generation": ("АЕЦ", "Кондензационни ТЕЦ", "Топлофикационни ТЕЦ", "Заводски ТЕЦ", "ВЕЦ", "Малки ВЕЦ", "ВяЕЦ", "ФЕЦ", "Био ЕЦ", "nuclear", "thermal", "hydro", "renew", "batt_charge_mw", "batt_discharge_mw", "pump_mw", "pumps_mw", "bess"), "eso_flows": ("SR_mw", "RO_mw", "TR_mw", "MK_mw", "GR_mw", "net"), "eso_load": ("load",), "frequency": ("frequency",), "ibex": ("ibex_price",), "co2_eua": ("co2_eur_t", "co2_daily_percent", "co2_quote_date"), "kozloduy": ("block5", "block6")}.get(name, ())
        for field in owned:
            result["values"].pop(field, None)
        if name == "eso_load":
            result["series"] = []
        try:
            fn()
            changed_keys = [key for key, value in result["values"].items() if before_values.get(key) != value]
            changed = bool(changed_keys or before_series != result["series"])
            result["sources"][name] = {
                **old_meta, "ok": True, "checked_at": checked_at,
                "last_success_at": checked_at,
                "last_change_at": checked_at if changed or not old_meta.get("last_change_at") else old_meta["last_change_at"],
                "changed": changed, "changed_fields": changed_keys,
            }
        except Exception as exc:
            result["values"].update({key: value for key, value in before_values.items() if key in owned})
            result["series"] = before_series
            result["sources"][name] = {
                **old_meta, "ok": False, "checked_at": checked_at,
                "last_success_at": old_meta.get("last_success_at"),
                "last_change_at": old_meta.get("last_change_at"),
                "changed": False, "error": str(exc)[:240],
            }
    def generation():
        # This replaces the former direct-JSON/mirror-first ESO generation path.
        # The official operational page is opened in a fresh browser context with cache disabled.
        data = read_eso_browser_generation()
        v = result["values"]
        for key in ("АЕЦ", "Кондензационни ТЕЦ", "Топлофикационни ТЕЦ", "Заводски ТЕЦ",
                    "ВЕЦ", "Малки ВЕЦ", "ВяЕЦ", "ФЕЦ", "Био ЕЦ",
                    "batt_charge_mw", "batt_discharge_mw", "pump_mw", "load_mw",
                    "SR_mw", "RO_mw", "TR_mw", "MK_mw", "GR_mw"):
            if key in data:
                v[key] = data[key]
        v["nuclear"] = v.get("АЕЦ", 0)
        thermal_keys = ("Кондензационни ТЕЦ", "Топлофикационни ТЕЦ", "Заводски ТЕЦ")
        v["thermal"] = sum(v.get(k, 0) for k in thermal_keys)
        v["hydro"] = v.get("ВЕЦ", 0) + v.get("Малки ВЕЦ", 0)
        v["renew"] = v.get("ВяЕЦ", 0) + v.get("ФЕЦ", 0) + v.get("Био ЕЦ", 0)
        if any(k in v for k in ("batt_charge_mw", "batt_discharge_mw", "pump_mw")):
            v["bess"] = v.get("pump_mw", 0) + v.get("batt_charge_mw", 0) - v.get("batt_discharge_mw", 0)
    def flows():
        try:
            raw=json.loads(get(URLS["flows"]))
        except Exception as direct_error:
            # Same fresh-browser fallback as the supplied desktop monitor.
            try:
                dom = browser_dump(URLS["flows"], wait_ms=1800)
                rendered = text_from_dom(dom)
                match = re.search(r"(\\{.*\\}|\\[.*\\])", rendered, flags=re.S)
                if not match:
                    raise RuntimeError("ESO flow page returned no JSON after browser refresh")
                raw = json.loads(match.group(1))
            except Exception:
                # Keep the last-resort mirror, but the primary route is the ESO endpoint/browser.
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
    result["sources"]["eso_generation"]["provider"]="ЕСО оперативна страница · Chromium hard refresh · JavaScript DOM"
    result["sources"]["eso_flows"]["provider"]="ЕСО SCADA JSON API · Chromium refresh fallback · mirror резерв"
    result["sources"]["eso_load"]["provider"]="ESO dashboard mirror (външен проект; резервен източник)"
    result["sources"]["frequency"]["provider"]="ЕСО frequency endpoint"
    result["sources"]["ibex"]["provider"]="БНЕБ/IBEX — няма конфигуриран официален API достъп"
    result["sources"]["co2_eua"]["provider"]="Trading Economics · EU Carbon Permits · дневна котировка CFD, EUR/tCO₂"
    result["sources"]["kozloduy"]["provider"]="Официален сайт на АЕЦ Козлодуй"
    # Publish every cycle. Healthy feeds update independently; failed feeds retain last-known-good values.
    result["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    result["collector_interval_seconds"] = int(os.getenv("COLLECTOR_INTERVAL_SECONDS", "15"))
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    core = ("eso_generation", "eso_flows", "eso_load", "frequency")
    healthy = sum(1 for key in core if result["sources"].get(key, {}).get("ok"))
    print(json.dumps({"revision": result["revision"], "core_healthy": str(healthy) + "/4", "sources": result["sources"]}, ensure_ascii=False))
if __name__=="__main__":run()

# Manual trigger: verify that the live data collector is still running.
# Commit-triggered validation: keep this collector path eligible for workflow checks.

# Scheduled refresh health-check marker. Trigger a fresh scheduled collector run after stale snapshot detection.
