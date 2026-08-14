from __future__ import annotations

import asyncio
import logging
from typing import Any

from quart import Blueprint, jsonify, redirect, render_template, request

from datastar_py import consts
from datastar_py.quart import DatastarResponse, datastar_response
from datastar_py.sse import ServerSentEventGenerator

from history import HistoryStore, TRACKED_METRICS
from web.viewmodel import DashboardViewModel
from web.formatting import refresh_seconds

logger = logging.getLogger(__name__)

web_bp = Blueprint("web", __name__)
view_model = DashboardViewModel()
history_store = HistoryStore()

# Tab registry: tab_name → has SSE
TABS: dict[str, bool] = {
    "overview": True,
    "battery": True,
    "solar": True,
    "load": True,
    "generator": True,
    "temperatures": True,
    "history": True,
    "charts": False,  # charts uses own /api/history fetch
    "extra": True,
    "alarms": True,
}


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@web_bp.route("/")
async def index() -> Any:
    return redirect("/overview")


@web_bp.route("/<tab_name>")
async def tab_page(tab_name: str) -> Any:
    if tab_name not in TABS:
        return "Not found", 404
    snapshot = view_model.snapshot
    return await render_template("tab.html", tab=tab_name, snapshot=snapshot)


# ---------------------------------------------------------------------------
# Per-tab SSE endpoint
# ---------------------------------------------------------------------------

@web_bp.route("/sse/<tab_name>")
@datastar_response
async def sse_tab(tab_name: str) -> Any:
    """SSE endpoint: pushes targeted patches for one tab plus shared elements."""
    if tab_name not in TABS or not TABS[tab_name]:
        return

    while True:
        snapshot = view_model.snapshot

        # Push lastUpdated signal for client-side connection detection
        yield ServerSentEventGenerator.patch_signals(
            {"lastUpdated": snapshot["meta"]["last_updated_ms"]}
        )

        # Shared elements: header and alarm banner
        yield ServerSentEventGenerator.patch_elements(
            await render_template("partials/header.html", snapshot=snapshot),
            selector="#header-meta",
            mode=consts.ElementPatchMode.INNER,
        )
        yield ServerSentEventGenerator.patch_elements(
            await render_template("partials/alarm_banner.html", snapshot=snapshot),
            selector="#alarm-banner",
            mode=consts.ElementPatchMode.INNER,
        )

        # Tab content
        yield ServerSentEventGenerator.patch_elements(
            await render_template(f"partials/{tab_name}.html", snapshot=snapshot),
            selector="#tab-content",
            mode=consts.ElementPatchMode.INNER,
        )

        await asyncio.sleep(refresh_seconds())


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@web_bp.route("/preview/energy-flow")
async def preview_energy_flow() -> Any:
    """Render the energy flow template with mock data for visual development.

    Note: Uses mock data directly in the template, so no viewmodel/inverter
    connection is needed. The preview app (preview.py) serves this without
    any hardware dependencies.
    """
    return await render_template("preview_energy_flow.html")


@web_bp.route("/api/stats")
async def api_stats() -> Any:
    return view_model.snapshot


@web_bp.route("/api/history/<variable_name>")
async def api_history(variable_name: str) -> Any:
    """Return historical time-series data for a variable.

    Query params:
      range: 1h | 6h | 24h | 7d | 30d | 1y  (default: 24h)
    """
    range_str = request.args.get("range", "24h")
    valid_ranges = {"1h", "6h", "24h", "7d", "30d", "1y"}
    if range_str not in valid_ranges:
        return jsonify({"error": f"Invalid range. Must be one of: {', '.join(sorted(valid_ranges))}"}), 400

    data = await asyncio.to_thread(history_store.query, variable_name, range_str)
    return jsonify({
        "variable": variable_name,
        "range": range_str,
        "points": data,
    })


@web_bp.route("/api/history/variables")
async def api_history_variables() -> Any:
    """Return the list of tracked metric names available for charting."""
    return jsonify({
        "variables": sorted(TRACKED_METRICS),
    })


# ---------------------------------------------------------------------------
# Generator control
# ---------------------------------------------------------------------------

def _generator_status_morph(message: str, error: bool = False) -> DatastarResponse:
    """Build a Datastar morph patch updating the generator control status element."""
    css = "control-status--error" if error else "control-status--success"
    html = f'<div class="control-status {css}">{message}</div>'
    return DatastarResponse(ServerSentEventGenerator.patch_elements(
        html,
        selector="#generator-status",
        mode=consts.ElementPatchMode.INNER,
    ))


@web_bp.route("/api/generator/start", methods=["POST"])
async def generator_start() -> Any:
    """Start the generator by simulating a front-panel short press (value 1)."""
    from muster import Muster

    status = view_model.snapshot.get("generator", {}).get("status", "")
    if status in ("Running", "Starting", "Stopping"):
        logger.info("Generator start ignored: already %s", status)
        return _generator_status_morph(f"Generator already {status.lower()}", error=True)

    try:
        muster = Muster()
        muster.write("GeneratorBtnPressPort1", 1)
        logger.info("Generator start requested")
        return _generator_status_morph("Generator start command sent")
    except Exception as exc:
        logger.exception("Generator start failed")
        return _generator_status_morph(str(exc), error=True)


@web_bp.route("/api/generator/stop", methods=["POST"])
async def generator_stop() -> Any:
    """Stop the generator by simulating a front-panel long press (value 2)."""
    from muster import Muster

    status = view_model.snapshot.get("generator", {}).get("status", "")
    if status in ("Not Running", "Starting", "Stopping"):
        logger.info("Generator stop ignored: already %s", status)
        return _generator_status_morph(f"Generator already {status.lower()}", error=True)

    try:
        muster = Muster()
        muster.write("GeneratorBtnPressPort1", 2)
        logger.info("Generator stop requested")
        return _generator_status_morph("Generator start command sent")
    except Exception as exc:
        logger.exception("Generator stop failed")
        return _generator_status_morph(str(exc), error=True)
