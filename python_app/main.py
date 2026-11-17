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
scheduler = BackgroundScheduler(timezone="UTC")


def read_snapshot() -> dict[str, Any]:
    try:
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("Snapshot root must be an object")
        return data
    except Exception as exc:
        LOG.warning("Cannot read data snapshot: %s", exc)
        return {
            "updated_at": None,
            "sources": {},
            "values": {},
            "series": [],
            "error": str(exc),
        }


def collect_once() -> None:
    """Run the existing validated collector; retain its last-good-snapshot rules."""
    if not COLLECTOR_FILE.exists():
        LOG.error("Collector not found: %s", COLLECTOR_FILE)
        return
    if not COLLECT_LOCK.acquire(blocking=False):
        LOG.info("Collector already running; skipping overlapping invocation")
        return
    try:
        result = subprocess.run(
            [sys.executable, str(COLLECTOR_FILE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=int(os.getenv("COLLECTOR_TIMEOUT_SECONDS", "90")),
            check=False,
        )
        if result.stdout:
            LOG.info("Collector: %s", result.stdout.strip()[-3000:])
        if result.returncode:
            LOG.error("Collector failed (%s): %s", result.returncode, result.stderr[-3000:])
    except Exception:
        LOG.exception("Collector execution failed")
    finally:
        COLLECT_LOCK.release()


@app.get("/api/data")
def api_data() -> JSONResponse:
    return JSONResponse(read_snapshot(), headers={"Cache-Control": "no-store"})


@app.get("/api/health")
def api_health() -> dict[str, Any]:
    snapshot = read_snapshot()
    return {
        "service": "MILCHO HUB",
        "status": "ok",
        "updated_at": snapshot.get("updated_at"),
        "collector_running": COLLECT_LOCK.locked(),
    }


def fmt(value: Any, digits: int = 0) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):,.{digits}f}".replace(",", " ").replace(".", ",")
    except (TypeError, ValueError):
        return "—"


def source_status(snapshot: dict[str, Any], name: str) -> str:
    source = snapshot.get("sources", {}).get(name, {})
    return "ONLINE" if source.get("ok") else "NO DATA"


def metric_card(title: str, key: str, unit: str = "MW", digits: int = 0) -> None:
    with ui.card().classes("metric-card"):
        ui.label(title).classes("metric-title")
        value = ui.label("—").classes("metric-value")
        ui.label(unit).classes("metric-unit")

        def update() -> None:
            value.text = fmt(read_snapshot().get("values", {}).get(key), digits)

        ui.timer(10, update)
        update()


def build_energy_page() -> None:
    ui.label("ЕЛЕКТРОЕНЕРГИЙНА СИСТЕМА НА БЪЛГАРИЯ").classes("page-title")
    ui.label("Оперативни данни · ЕСО · Енергийни пазари").classes("page-subtitle")
    with ui.row().classes("w-full flex-wrap"):
        metric_card("ТОВАР НА РБ", "load")
        metric_card("ВНОС / ИЗНОС", "net")
        metric_card("ССЕЕ + ПОМПИ", "bess")
        metric_card("ЧЕСТОТА", "frequency", "Hz", 2)
        metric_card("АЕЦ", "nuclear")
        metric_card("ТЕЦ", "thermal")
        metric_card("ВЕЦ", "hydro")
        metric_card("ВЕИ", "renew")

    with ui.row().classes("w-full items-stretch"):
        with ui.card().classes("data-panel grow"):
            ui.label("ПРОИЗВОДСТВО ПО ИЗТОЧНИЦИ").classes("panel-title")
            chart = ui.echart({
                "tooltip": {"trigger": "item"},
                "legend": {"bottom": 0, "textStyle": {"color": "#dbe8ec"}},
                "series": [{
                    "type": "pie", "radius": ["38%", "68%"],
                    "data": [], "label": {"color": "#eaf2f4"},
                }],
            }).classes("w-full h-80")

            def update_generation() -> None:
                v = read_snapshot().get("values", {})
                keys = [
                    ("АЕЦ", "АЕЦ"), ("Кондензационни ТЕЦ", "Кондензационни ТЕЦ"),
                    ("Топлофикационни ТЕЦ", "Топлофикационни ТЕЦ"),
                    ("Заводски ТЕЦ", "Заводски ТЕЦ"), ("ВЕЦ", "ВЕЦ"),
                    ("Малки ВЕЦ", "Малки ВЕЦ"), ("ВяЕЦ", "ВяЕЦ"),
                    ("ФЕЦ", "ФЕЦ"), ("Био ЕЦ", "Био ЕЦ"),
                ]
                rows = [{"name": label, "value": max(0, float(v[key]))}
                        for key, label in keys if v.get(key) is not None]
                chart.options["series"][0]["data"] = rows
                chart.update()

            ui.timer(10, update_generation)
            update_generation()

        with ui.card().classes("data-panel grow"):
            ui.label("ТРАНСГРАНИЧНИ ПОТОЦИ · MW").classes("panel-title")
            flow_chart = ui.echart({
                "tooltip": {"trigger": "axis"},
                "xAxis": {"type": "value", "axisLabel": {"color": "#c6d5da"}},
                "yAxis": {"type": "category", "data": ["Сърбия", "Румъния", "Турция", "С. Македония", "Гърция"],
                          "axisLabel": {"color": "#c6d5da"}},
                "series": [{"type": "bar", "data": [], "label": {"show": True, "position": "right"}}],
                "grid": {"left": 95, "right": 35, "top": 15, "bottom": 25},
            }).classes("w-full h-80")

            def update_flows() -> None:
                v = read_snapshot().get("values", {})
                keys = [("SR_mw", "Сърбия"), ("RO_mw", "Румъния"),
                        ("TR_mw", "Турция"), ("MK_mw", "С. Македония"),
                        ("GR_mw", "Гърция")]
                vals = [float(v[k]) if v.get(k) is not None else 0 for k, _ in keys]
                flow_chart.options["series"][0]["data"] = vals
                flow_chart.update()

            ui.timer(10, update_flows)
            update_flows()

    with ui.card().classes("data-panel w-full"):
        ui.label("ТОВАР НА ЕЛЕКТРОЕНЕРГИЙНАТА СИСТЕМА").classes("panel-title")
        load_chart = ui.echart({
            "tooltip": {"trigger": "axis"},
            "xAxis": {"type": "category", "data": [], "axisLabel": {"color": "#c6d5da"}},
            "yAxis": {"type": "value", "name": "MW", "axisLabel": {"color": "#c6d5da"}},
            "series": [{"name": "Товар", "type": "line", "smooth": True, "showSymbol": False,
                        "areaStyle": {"opacity": 0.16}, "data": []}],
            "grid": {"left": 55, "right": 25, "top": 25, "bottom": 35},
        }).classes("w-full h-72")

        def update_load() -> None:
            points = read_snapshot().get("series", [])[-144:]
            load_chart.options["xAxis"]["data"] = [
                str(p.get("t", ""))[11:16] for p in points
            ]
            load_chart.options["series"][0]["data"] = [p.get("v") for p in points]
            load_chart.update()

        ui.timer(30, update_load)
        update_load()


def build_market_page() -> None:
    ui.label("ЕНЕРГИЙНИ ПАЗАРИ").classes("page-title")
    with ui.row().classes("w-full flex-wrap"):
        with ui.card().classes("metric-card"):
            ui.label("CO₂ · EU ETS / EUA").classes("metric-title")
            price = ui.label("—").classes("metric-value")
            ui.label("€/tCO₂").classes("metric-unit")
            detail = ui.label("Няма потвърдена котировка").classes("text-xs text-slate-300")

            def update_co2() -> None:
                v = read_snapshot().get("values", {})
                price.text = fmt(v.get("co2_eur_t"), 2)
                date = v.get("co2_quote_date") or "дата няма"
                change = v.get("co2_daily_percent")
                detail.text = f"{date} · дневна промяна: {fmt(change, 2)}%" if change is not None else str(date)

            ui.timer(30, update_co2)
            update_co2()
        with ui.card().classes("metric-card"):
            ui.label("IBEX · БЪЛГАРИЯ").classes("metric-title")
            ui.label("—").classes("metric-value")
            ui.label("€/MWh").classes("metric-unit")
            ui.label("Официален API достъп не е конфигуриран").classes("text-xs text-slate-300")


def build_weather_page() -> None:
    ui.label("WEATHER CENTER").classes("page-title")
    ui.label("София · Джулюница · Малта").classes("page-subtitle")
    ui.label("Метеорологичният модул ще бъде пренесен със същите локации и прогнози.").classes("text-slate-300")
    ui.link("Open-Meteo", "https://open-meteo.com/").classes("text-cyan-300")


def build_news_page() -> None:
    ui.label("NEWS CENTER").classes("page-title")
    ui.label("Енергетика · България · Европа · Свят").classes("page-subtitle")
    ui.label("Новинарският модул ще бъде свързан към RSS източниците в следващия етап.").classes("text-slate-300")


def build_mountain_page() -> None:
    ui.label("ПЛАНИНСКИ КАМЕРИ").classes("page-title")
    cameras = [
        ("БОРОВЕЦ · МАРКУДЖИК 1", "https://weather-webcam.eu/webcam-borovec-markudjik1/"),
        ("БОТЕВ · ЗАСЛОН", "https://www.alpinsport-bg.com/"),
    ]
    with ui.row().classes("w-full flex-wrap"):
        for title, url in cameras:
            with ui.card().classes("camera-card"):
                ui.label(title).classes("panel-title")
                ui.html(f'<iframe src="{url}" loading="lazy" referrerpolicy="no-referrer"></iframe>',
                        sanitize=False).classes("w-full")


def build_devices_page() -> None:
    ui.label("ЛИЧНИ УСТРОЙСТВА").classes("page-title")
    ui.label("Tuya · Zigbee · ESP32 · Камери · Сензори").classes("page-subtitle")
    ui.label("Интеграциите ще се прехвърлят след основните енергийни и метеорологични модули.").classes("text-slate-300")


@ui.page("/")
def home() -> None:
    ui.add_head_html("""
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body { background:#07171f; color:#edf4f6; }
      .page-title {font-size:1.45rem;font-weight:800;color:#eaf4f6}
      .page-subtitle {color:#91aab3;margin-bottom:1rem}
      .metric-card {background:#102832;border:1px solid #294954;min-width:170px;flex:1;padding:16px}
      .metric-title,.panel-title {font-weight:800;color:#c2d1d6;font-size:.85rem}
      .metric-value {font-size:2rem;font-weight:900;color:#ffb34d}
      .metric-unit {font-size:.8rem;color:#91aab3}
      .data-panel {background:#102832;border:1px solid #294954;padding:16px}
      .camera-card {background:#102832;border:1px solid #294954;min-width:min(100%,420px);flex:1}
      .camera-card iframe {width:100%;height:280px;border:0;background:#07171f}
      .q-drawer {background:#0d232c!important;color:#edf4f6}
      .q-header {background:#0d232c!important}
    </style>
    """)

    with ui.header().classes("items-center justify-between px-4"):
        ui.label("MILCHO HUB").classes("text-xl font-black tracking-wider")
        stamp = ui.label("Зареждане на данните…").classes("text-xs text-slate-300")

        def update_stamp() -> None:
            updated = read_snapshot().get("updated_at")
            stamp.text = f"Последно обновяване: {updated or 'няма данни'}"

        ui.timer(10, update_stamp)
        update_stamp()

    with ui.left_drawer(value=True).classes("p-3"):
        ui.label("ИНФОРМАЦИОННИ ЦЕНТРОВЕ").classes("text-xs font-bold text-slate-400 mb-3")
        pages = [
            ("⚡  ENERGY HUB", build_energy_page),
            ("📈  MARKETS / CO₂", build_market_page),
            ("🌤️  WEATHER CENTER", build_weather_page),
            ("📰  NEWS CENTER", build_news_page),
            ("⛰️  MOUNTAIN CAMERAS", build_mountain_page),
            ("📱  PERSONAL DEVICES", build_devices_page),
        ]
        content = ui.column().classes("w-full p-4 gap-3")
        for label, builder in pages:
            ui.button(label, on_click=lambda b=builder: show_page(b)).props("flat align=left").classes("w-full text-left")

    def show_page(builder) -> None:
        content.clear()
        with content:
            builder()

    show_page(build_energy_page)


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(
        collect_once, "interval", seconds=int(os.getenv("COLLECTOR_INTERVAL_SECONDS", "60")),
        id="data-collector", max_instances=1, coalesce=True, replace_existing=True,
    )
    scheduler.start()
    LOG.info("MILCHO HUB scheduler started")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


app.on_startup(start_scheduler)
app.on_shutdown(stop_scheduler)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        title="MILCHO HUB",
        dark=True,
        reload=False,
        show=False,
    )
