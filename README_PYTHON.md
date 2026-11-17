# MILCHO HUB — Python Web Application

This is the parallel Python/NiceGUI implementation. The existing GitHub Pages application remains untouched while this version is developed and validated.

## Stack

- Python 3.12
- NiceGUI for the browser UI, authored in Python
- APScheduler for server-side collection cadence
- Existing `refresh_data.py` collector retained initially as the validated data-source adapter
- Docker deployment target

## Local run

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r python_app/requirements.txt
python python_app/main.py
```

Open http://localhost:8080.

## Health endpoints

- `/api/health`
- `/api/data`

## Data integrity

The app reads the existing `data.json` snapshot and runs the existing collector at the configured server-side interval. The collector's validation and last-good-snapshot behavior remain authoritative. Missing or unverified feeds are displayed as unavailable; no placeholder market prices are presented as live data.

## Deployment

A persistent Python host is required. GitHub Pages cannot execute a Python web server. The included Dockerfile and Render Blueprint are a starting deployment configuration. A persistent disk is required if the host does not preserve the repository working directory between deploys, because the current collector writes its snapshot to `data.json`.

## Migration status

This is the first application shell. Weather, news, mountain cameras, detailed TPP2 unit extraction, device integrations, and full bilingual coverage are not yet migrated. They will be brought across and tested module by module before the new app replaces the current public site.
