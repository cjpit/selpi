# Selpi

Python backend with a Datastar UI frontend for showing Selectronics SP Pro inverter information.

## Setup

Edit directly on the Pi. Uses `uv` for Python dependency management.

```bash
cp src/.env.dist src/.env.local
# edit src/.env.local as needed
cd src
uv sync
uv run selpi.py http
```

Open `http://<pi-ip>:8000` in a browser.

## Development

```bash
cd src
uv run selpi.py http
```
