from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.responses import JSONResponse
from nicegui import app, ui

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data.json"
COLLECTOR_FILE = ROOT / "refresh_data.py"
LOG = logging.getLogger("milcho_hub")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
COLLECT_LOCK = threading.Lock()
SCHEDULER = BackgroundScheduler(timezone="UTC")
REFRESH_SECONDS = int(os.getenv("COLLECTOR_INTERVAL_SECONDS", "15"))

BG = "#07141B"
PANEL = "#10232D"
BORDER = "#2A4652"
TEXT = "#EAF4F7"
MUTED = "#7F9AA5"
CYAN = "#2BC7F0"
GREEN = "#28DE8B"
ORANGE = "#FF963D"
BLUE = "#438DFF"
PURPLE = "#B77CFF"
RED = "#FF525D"


def read_snapshot() -> dict[str, Any]:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            result = json.load(handle)
        if isinstance(result, dict):
            return result
        raise ValueError("Snapshot root is not an object")
    except Exception as exc:
        LOG.warning("Snapshot unavailable: %s", exc)
        return {"updated_at": None, "sources": {}, "values": {}, "series": [], "error": str(exc)}


def number(values: dict[str, Any], *keys: str, default: float = 0.0) -> float:
    for key in keys:
        try:
            value = float(str(values.get(key)).replace(",", "."))
            if value == value and abs(value) != float("inf"):
                return value
        except (TypeError, ValueError):
            continue
    return default


def fmt(value: Any, digits: int = 0) -> str:
    try:
        return f"{float(value):,.{digits}f}".replace(",", " ").replace(".", ",")
    except (TypeError, ValueError):
        return "—"


def collect_once() -> None:
    if not COLLECTOR_FILE.exists():
        LOG.error("Collector not found: %s", COLLECTOR_FILE)
        return
    if not COLLECT_LOCK.acquire(blocking=False):
        LOG.info("Collector already running; skipping overlapping run")
        return
    try:
        result = subprocess.run(
            [sys.executable, str(COLLECTOR_FILE)],
            cwd=ROOT, capture_output=True, text=True,
            timeout=int(os.getenv("COLLECTOR_TIMEOUT_SECONDS", "90")),
            check=False,
        )
        if result.stdout:
            LOG.info("Collector: %s", result.stdout.strip()[-2500:])
        if result.returncode:
            LOG.error("Collector exit %s: %s", result.returncode, result.stderr[-2500:])
    except Exception:
        LOG.exception("Collector execution failed")
    finally:
        COLLECT_LOCK.release()


@app.get("/api/data")
def api_data() -> JSONResponse:
    return JSONResponse(read_snapshot(), headers={"Cache-Control": "no-store"})


@app.get("/api/health")
def api_health() -> dict[str, Any]:
    snap = read_snapshot()
    return {
        "service": "MILCHO HUB",
        "status": "ok",
        "updated_at": snap.get("updated_at"),
        "collector_running": COLLECT_LOCK.locked(),
    }


def gauge_options(title: str, value: float, minimum: float, maximum: float, color: str, unit: str = "MW") -> dict[str, Any]:
    return {
        "animationDuration": 350,
        "series": [{
            "type": "gauge",
            "min": minimum,
            "max": maximum,
            "startAngle": 225,
            "endAngle": -45,
            "splitNumber": 4,
            "radius": "88%",
            "center": ["50%", "56%"],
            "axisLine": {"lineStyle": {"width": 13, "color": [[1, "#DDE4E7"]]}},
            "progress": {"show": True, "width": 5, "itemStyle": {"color": color}},
            "pointer": {"show": True, "length": "62%", "width": 3, "itemStyle": {"color": "#D82F3B"}},
            "anchor": {"show": True, "showAbove": True, "size": 9, "itemStyle": {"color": "#26343A", "borderColor": "#AAB4B8", "borderWidth": 2}},
            "axisTick": {"distance": -17, "length": 4, "lineStyle": {"color": "#26343A", "width": 1}},
            "splitLine": {"distance": -18, "length": 9, "lineStyle": {"color": "#26343A", "width": 2}},
            "axisLabel": {"distance": 22, "color": "#26343A", "fontSize": 8},
            "title": {"show": True, "offsetCenter": [0, "-28%"], "color": "#EAF4F7", "fontSize": 10, "fontWeight": "bold"},
            "detail": {"valueAnimation": True, "offsetCenter": [0, "47%"], "fontSize": 17, "fontWeight": "bold", "color": "#10191D", "formatter": "{value}"},
            "data": [{"value": round(value, 1), "name": title}],
        }],
    }


def gauge_card(title: str, key: str, minimum: float, maximum: float, accent: str, unit: str = "MW"):
    with ui.card().classes("gauge-card"):
        chart = ui.echart(gauge_options(title, 0, minimum, maximum, accent, unit)).classes("w-full")
        chart.style("height: 188px;")
        return chart


def panel(title: str):
    card = ui.card().classes("scada-panel")
    with card:
        ui.label(title).classes("panel-heading")
    return card


def build_energy_dashboard() -> None:
    snap = read_snapshot()
    v = snap.get("values", {})

    ui.label("ЕЛЕКТРОЕНЕРГИЙНА СИСТЕМА НА БЪЛГАРИЯ").classes("main-title")
    ui.label("ОПЕРАТИВЕН МОНИТОРИНГ · РЕАЛНО ВРЕМЕ · ЕСО").classes("main-subtitle")

    gauge_specs = [
        ("ТОВАР НА РБ", "load", 0, 10000, CYAN),
        ("ВНОС / ИЗНОС", "flow", -4000, 4000, GREEN),
        ("ССЕЕ + ПОМПИ", "battery", -5000, 5000, PURPLE),
        ("АЕЦ", "nuclear", 0, 2500, BLUE),
        ("ТЕЦ", "thermal", 0, 6500, ORANGE),
        ("ВЕЦ + МВЕЦ", "hydro", 0, 3500, CYAN),
        ("ВЕИ", "renew", 0, 10000, GREEN),
    ]
    gauge_charts = {}
    with ui.column().classes("w-full gap-1"):
        with ui.row().classes("w-full no-wrap gap-1"):
            for title, key, lo, hi, accent in gauge_specs[:4]:
                gauge_charts[key] = gauge_card(title, key, lo, hi, accent)
        with ui.row().classes("w-full no-wrap gap-1 justify-center"):
            for title, key, lo, hi, accent in gauge_specs[4:]:
                gauge_charts[key] = gauge_card(title, key, lo, hi, accent)

    with ui.grid(columns=12).classes("w-full gap-2"):
        with ui.element("div").classes("col-span-12 lg:col-span-4"):
            production_panel = panel("ПРОИЗВОДСТВО ПО ЦЕНТРАЛИ / ИЗТОЧНИЦИ")
            with production_panel:
                source_rows = {}
                source_names = [
                    ("АЕЦ", "АЕЦ"), ("Кондензационни ТЕЦ", "Кондензационни ТЕЦ"),
                    ("Топлофикационни ТЕЦ", "Топлофикационни ТЕЦ"),
                    ("Заводски ТЕЦ", "Заводски ТЕЦ"), ("ВЕЦ", "ВЕЦ"),
                    ("Малки ВЕЦ", "Малки ВЕЦ"), ("ВяЕЦ", "ВяЕЦ"),
                    ("ФЕЦ", "ФЕЦ"), ("Био ЕЦ", "Био ЕЦ"),
                    ("ССЕЕ", "ССЕЕ"), ("Помпи ПАВЕЦ", "Помпи ПАВЕЦ"),
                ]
                for label, key in source_names:
                    with ui.row().classes("source-row w-full items-center justify-between"):
                        ui.label(label).classes("source-label")
                        source_rows[key] = ui.label("— MW").classes("source-value")

        with ui.element("div").classes("col-span-12 lg:col-span-4"):
            graph_panel = panel("ТОВАР НА ЕСО · ПОСЛЕДНИТЕ 24 ЧАСА")
            with graph_panel:
                load_chart = ui.echart({
                    "tooltip": {"trigger": "axis"},
                    "grid": {"left": 52, "right": 18, "top": 18, "bottom": 32},
                    "xAxis": {"type": "category", "data": [], "axisLabel": {"color": "#AFC2C9", "fontSize": 9}},
                    "yAxis": {"type": "value", "name": "MW", "axisLabel": {"color": "#AFC2C9"}},
                    "series": [{"type": "line", "name": "Товар", "smooth": True, "showSymbol": False,
                                "lineStyle": {"width": 2, "color": CYAN},
                                "areaStyle": {"color": "rgba(43,199,240,0.12)"}, "data": []}],
                }).classes("w-full").style("height: 230px;")

            flows_panel = panel("ТРАНСГРАНИЧНИ ПОТОЦИ · MW")
            with flows_panel:
                flow_chart = ui.echart({
                    "tooltip": {"trigger": "axis"},
                    "grid": {"left": 105, "right": 30, "top": 10, "bottom": 20},
                    "xAxis": {"type": "value", "axisLabel": {"color": "#AFC2C9"}},
                    "yAxis": {"type": "category", "data": ["Сърбия", "Румъния", "Турция", "С. Македония", "Гърция"],
                              "axisLabel": {"color": "#EAF4F7"}},
                    "series": [{"type": "bar", "data": [], "barWidth": 13,
                                "itemStyle": {"color": GREEN}, "label": {"show": True, "position": "right", "color": TEXT}}],
                }).classes("w-full").style("height: 235px;")

        with ui.element("div").classes("col-span-12 lg:col-span-4"):
            npp_panel = panel("АЕЦ КОЗЛОДУЙ · БЛОК 5 / БЛОК 6")
            with npp_panel:
                with ui.card().classes("unit-card w-full"):
                    ui.label("БЛОК 5").classes("unit-title")
                    block5 = ui.label("— MW").classes("unit-value").style(f"color:{BLUE}")
                    block5_state = ui.label("● WAITING").classes("unit-state")
                with ui.card().classes("unit-card w-full"):
                    ui.label("БЛОК 6").classes("unit-title")
                    block6 = ui.label("— MW").classes("unit-value").style(f"color:{GREEN}")
                    block6_state = ui.label("● WAITING").classes("unit-state")
                with ui.card().classes("unit-card w-full"):
                    ui.label("ОБЩО АЕЦ КОЗЛОДУЙ").classes("unit-title")
                    nuclear_total = ui.label("— MW").classes("total-value")
                ui.label("Източник: официален сайт на АЕЦ „Козлодуй“").classes("source-note")
                ui.separator().classes("my-2")
                ui.label("ТЕМПЕРАТУРА · СОФИЯ").classes("unit-title")
                temp_value = ui.label("— °C").classes("temp-value")
                ui.separator().classes("my-2")
                ui.label("СТАТУС НА ИЗТОЧНИЦИТЕ").classes("unit-title")
                source_status_rows = {}
                source_labels = [("eso_generation", "ЕСО · производство"), ("eso_flows", "ЕСО · потоци"), ("eso_load", "ЕСО · товар"), ("frequency", "ЕСО · честота"), ("kozloduy", "АЕЦ Козлодуй"), ("co2_eua", "CO₂ · EUA"), ("ibex", "IBEX")]
                for source_key, source_label in source_labels:
                    with ui.row().classes("w-full items-center justify-between source-status-row"):
                        ui.label(source_label).classes("source-label")
                        source_status_rows[source_key] = ui.label("WAITING").classes("source-status-value")

    last_revision = {"value": None}

    def update_dashboard() -> None:
        current = read_snapshot()
        revision = current.get("revision", current.get("updated_at"))
        if revision == last_revision["value"]:
            return
        last_revision["value"] = revision
        values = current.get("values", {})
        nuclear = number(values, "nuclear", "АЕЦ")
        thermal = number(values, "thermal")
        if not thermal:
            thermal = number(values, "Кондензационни ТЕЦ") + number(values, "Топлофикационни ТЕЦ") + number(values, "Заводски ТЕЦ")
        hydro = number(values, "hydro")
        if not hydro:
            hydro = number(values, "ВЕЦ") + number(values, "Малки ВЕЦ")
        renew = number(values, "renew")
        if not renew:
            renew = number(values, "ВяЕЦ") + number(values, "ФЕЦ") + number(values, "Био ЕЦ")
        load = number(values, "load", "load_mw", "Товар на РБ")
        # Sign convention follows the supplied Full HD SCADA reference:
        # positive upper gauge = export; positive battery gauge = charging/pumping.
        flow = -number(values, "net", "net_import_mw")
        battery = -number(values, "bess")
        gauge_values = {
            "load": load, "flow": flow, "battery": battery,
            "nuclear": nuclear, "thermal": thermal, "hydro": hydro, "renew": renew,
        }
        for title, key, lo, hi, accent in gauge_specs:
            gauge_charts[key].options = gauge_options(title, gauge_values[key], lo, hi, accent)
            gauge_charts[key].update()

        for label, key in source_names:
            raw = values.get(key)
            if raw is None and key == "Помпи ПАВЕЦ":
                raw = values.get("pump_mw", values.get("pumps_mw"))
            if raw is None and key == "ССЕЕ":
                raw = values.get("bess")
            source_rows[key].text = f"{fmt(raw)} MW"

        series = current.get("series", [])[-288:]
        load_chart.options["xAxis"]["data"] = [str(p.get("t", ""))[11:16] for p in series]
        load_chart.options["series"][0]["data"] = [p.get("v") for p in series]
        load_chart.update()

        flow_keys = ["SR_mw", "RO_mw", "TR_mw", "MK_mw", "GR_mw"]
        # Per the supplied monitor, positive bars denote export.
        flow_chart.options["series"][0]["data"] = [-number(values, key) for key in flow_keys]
        flow_chart.update()

        b5 = values.get("block5")
        b6 = values.get("block6")
        block5.text = f"{fmt(b5)} MW" if b5 is not None else "— MW"
        block6.text = f"{fmt(b6)} MW" if b6 is not None else "— MW"
        block5_state.text = "● RUN / LIVE" if b5 is not None and float(b5) > 1 else "● OFFLINE / NO DATA"
        block6_state.text = "● RUN / LIVE" if b6 is not None and float(b6) > 1 else "● OFFLINE / NO DATA"
        block5_state.style(f"color:{GREEN if b5 is not None and float(b5) > 1 else RED}")
        block6_state.style(f"color:{GREEN if b6 is not None and float(b6) > 1 else RED}")
        nuclear_total.text = f"{fmt(nuclear)} MW"
        temp = values.get("sofia_temperature")
        temp_value.text = f"{fmt(temp, 1)} °C" if temp is not None else "— °C"
        sources = current.get("sources", {})
        for source_key, source_label in source_labels:
            meta = sources.get(source_key, {})
            ok = meta.get("ok") is True
            checked = meta.get("checked_at")
            changed = meta.get("last_change_at")
            checked_text = checked[11:19] if isinstance(checked, str) and len(checked) >= 19 else "—"
            changed_text = changed[11:19] if isinstance(changed, str) and len(changed) >= 19 else "—"
            state = "ONLINE" if ok else ("STALE" if meta.get("last_success_at") else "OFFLINE")
            source_status_rows[source_key].text = f"{state} · check {checked_text} · change {changed_text}"
            source_status_rows[source_key].style(f"color:{GREEN if ok else ORANGE if meta.get(\"last_success_at\") else RED}")
            source_status_rows[source_key].tooltip(f"{meta.get(\"provider\", source_label)} | Последен успех: {meta.get(\"last_success_at\") or \"няма\"} | Последна промяна: {meta.get(\"last_change_at\") or \"няма\"} | {meta.get(\"error\", \"\")}")
        update_header(current)

    update_dashboard()
    ui.timer(1, update_dashboard)


header_status = None
header_clock = None
header_freq = None
header_ibex = None


def update_header(snapshot: dict[str, Any] | None = None) -> None:
    if snapshot is None:
        snapshot = read_snapshot()
    values = snapshot.get("values", {})
    sources = snapshot.get("sources", {})
    core = ["eso_generation", "eso_flows", "eso_load", "frequency"]
    online = sum(1 for key in core if sources.get(key, {}).get("ok"))
    if header_status is not None:
        header_status.text = f"● ONLINE {online}/{len(core)}" if online == len(core) else f"● PARTIAL {online}/{len(core)}"
        header_status.style(f"color:{GREEN if online == len(core) else ORANGE}")
    if header_freq is not None:
        freq = values.get("frequency")
        header_freq.text = f"ЧЕСТОТА: {fmt(freq, 2)} Hz" if freq is not None else "ЧЕСТОТА: — Hz"
    if header_ibex is not None:
        price = values.get("ibex_price")
        header_ibex.text = f"IBEX: {fmt(price, 2)} €/MWh" if price is not None else "IBEX: N/A €/MWh"
    if header_clock is not None:
        header_clock.text = datetime.now().astimezone().strftime("%d.%m.%Y  %H:%M:%S")


def build_markets() -> None:
    ui.label("ЕНЕРГИЙНИ ПАЗАРИ").classes("main-title")
    with ui.row().classes("w-full"):
        with ui.card().classes("unit-card"):
            ui.label("IBEX · ДЕН НАПРЕД").classes("unit-title")
            price = ui.label("— €/MWh").classes("unit-value")
            ui.label("Потвърдена котировка от източника").classes("source-note")
            def update_price():
                val = read_snapshot().get("values", {}).get("ibex_price")
                price.text = f"{fmt(val, 2)} €/MWh" if val is not None else "N/A €/MWh"
            ui.timer(30, update_price)
            update_price()
        with ui.card().classes("unit-card"):
            ui.label("CO₂ · EU ETS / EUA").classes("unit-title")
            co2 = ui.label("— €/tCO₂").classes("unit-value")
            def update_co2():
                val = read_snapshot().get("values", {}).get("co2_eur_t")
                co2.text = f"{fmt(val, 2)} €/tCO₂" if val is not None else "НЯМА ПОТВЪРДЕНА КОТИРОВКА"
            ui.timer(30, update_co2)
            update_co2()


def build_weather() -> None:
    ui.label("WEATHER CENTER").classes("main-title")
    ui.label("СОФИЯ · ДЖУЛЮНИЦА · МАЛТА").classes("main-subtitle")
    ui.label("Тук ще бъде пренесен метеорологичният модул с текущи условия, 24-часова и 7-дневна прогноза.").classes("module-note")


def build_news() -> None:
    ui.label("NEWS CENTER").classes("main-title")
    ui.label("ЕНЕРГЕТИКА · БЪЛГАРИЯ · ЕВРОПА · СВЯТ").classes("main-subtitle")
    ui.label("Новинарският модул ще използва проверени RSS източници и отделни категории.").classes("module-note")


def build_cameras() -> None:
    ui.label("MOUNTAIN CAMERAS").classes("main-title")
    ui.label("БОТЕВ · БОРОВЕЦ / МАРКУДЖИК · РОДОПИ · ВИТОША").classes("main-subtitle")
    ui.label("Камерите ще се пренесат с отделни панели, fullscreen режим и независимо обновяване.").classes("module-note")


def build_devices() -> None:
    ui.label("PERSONAL DEVICES").classes("main-title")
    ui.label("TUYA · ZIGBEE · ESP32 · ICSEE · СЕНЗОРИ").classes("main-subtitle")
    ui.label("Интеграциите ще се добавят след миграцията на основните SCADA панели.").classes("module-note")


def build_app() -> None:
    global header_status, header_clock, header_freq, header_ibex
    ui.add_head_html("""
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body { background:#07141B; color:#EAF4F7; }
      .q-header { background:#081A22 !important; border-bottom:1px solid #2A4652; }
      .q-drawer { background:#0B2029 !important; color:#EAF4F7; }
      .main-title {font-size:clamp(17px,1.5vw,25px);font-weight:900;letter-spacing:.04em;color:#EAF4F7}
      .main-subtitle {font-size:11px;letter-spacing:.12em;color:#7F9AA5;margin-bottom:8px}
      .gauge-card {background:#10232D;border:1px solid #2A4652;border-radius:5px;padding:2px;flex:1;min-width:0;box-shadow:none}
      .scada-panel {background:#10232D;border:1px solid #2A4652;border-radius:5px;padding:10px;margin-bottom:8px;box-shadow:none}
      .panel-heading {font-size:12px;font-weight:900;color:#EAF4F7;letter-spacing:.04em;margin-bottom:8px}
      .source-row {background:#112A34;border:1px solid #203D48;padding:7px 9px;margin:2px 0;border-radius:2px}
      .source-label {font-size:12px;font-weight:700;color:#EAF4F7}
      .source-value {font-family:Consolas,monospace;font-size:12px;font-weight:800;color:#EAF4F7}
      .unit-card {background:#112A34;border:1px solid #2A4652;border-radius:4px;padding:12px;margin:4px 0;box-shadow:none}
      .unit-title {font-size:12px;font-weight:900;color:#AFC2C9;letter-spacing:.05em}
      .unit-value {font-family:Consolas,monospace;font-size:27px;font-weight:900}
      .unit-state {font-size:11px;font-weight:900;color:#7F9AA5}
      .total-value {font-family:Consolas,monospace;font-size:24px;font-weight:900;color:#EAF4F7}
      .temp-value {font-family:Consolas,monospace;font-size:30px;font-weight:900;color:#F2F7F9}
      .source-note,.module-note {font-size:11px;color:#7F9AA5}
      .source-status-row {background:#112A34;border:1px solid #203D48;padding:6px 8px;margin:2px 0;border-radius:2px;gap:8px}
      .source-status-value {font-family:Consolas,monospace;font-size:10px;font-weight:800;text-align:right}
      @media(max-width:800px) {
        .gauge-card {min-width:46%}
        .q-drawer {width:230px}
      }
    </style>
    """)

    with ui.header().classes("items-center px-3 gap-4"):
        ui.label("MILCHO HUB").classes("text-lg font-black tracking-widest")
        ui.label("SCADA / ENERGY CONTROL").classes("text-xs text-slate-400")
        ui.space()
        header_ibex = ui.label("IBEX: N/A €/MWh").classes("text-xs font-bold").style(f"color:{ORANGE}")
        header_freq = ui.label("ЧЕСТОТА: — Hz").classes("text-xs font-bold")
        header_status = ui.label("● STARTING").classes("text-xs font-bold")
        header_clock = ui.label("--:--:--").classes("text-xs font-bold").style(f"color:{GREEN}")

    with ui.left_drawer(value=True).classes("p-2"):
        ui.label("КОНТРОЛНИ ЦЕНТРОВЕ").classes("text-xs font-black text-slate-400 p-2")
        pages = [
            ("⚡  ENERGY SCADA", build_energy_dashboard),
            ("📊  MARKETS / CO₂", build_markets),
            ("🌤️  WEATHER CENTER", build_weather),
            ("📰  NEWS CENTER", build_news),
            ("⛰️  MOUNTAIN CAMERAS", build_cameras),
            ("📱  PERSONAL DEVICES", build_devices),
        ]
        host = ui.column().classes("w-full p-3 gap-2")
        def show(builder):
            host.clear()
            with host:
                builder()
        for label, builder in pages:
            ui.button(label, on_click=lambda b=builder: show(b)).props("flat align=left no-caps").classes("w-full text-left")
    show(build_energy_dashboard)
    ui.timer(1, update_header)


@ui.page("/")
def home() -> None:
    build_app()


def start_scheduler() -> None:
    if SCHEDULER.running:
        return
    SCHEDULER.add_job(
        collect_once, "interval", seconds=REFRESH_SECONDS,
        id="data-collector", max_instances=1, coalesce=True, replace_existing=True,
        next_run_time=datetime.now(timezone.utc),
    )
    SCHEDULER.start()
    LOG.info("MILCHO HUB collector scheduler started: %s seconds", REFRESH_SECONDS)


def stop_scheduler() -> None:
    if SCHEDULER.running:
        SCHEDULER.shutdown(wait=False)


app.on_startup(start_scheduler)
app.on_shutdown(stop_scheduler)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8080")),
           title="MILCHO HUB", dark=True, reload=False, show=False)
