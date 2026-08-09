from __future__ import annotations

import asyncio
import logging
from typing import Any

from quart import Blueprint, render_template

from datastar_py import consts
from datastar_py.quart import DatastarResponse, datastar_response
from datastar_py.sse import ServerSentEventGenerator

from web.viewmodel import DashboardViewModel
from web.formatting import refresh_seconds

logger = logging.getLogger(__name__)

web_bp = Blueprint("web", __name__)
view_model = DashboardViewModel()


@web_bp.route("/")
async def index() -> str:
    snapshot = view_model.snapshot
    return await render_template("dashboard.html", snapshot=snapshot)


@web_bp.route("/sse")
@datastar_response
async def sse() -> Any:
    """SSE endpoint: renders full dashboard content and pushes as a single morph patch."""
    while True:
        snapshot = view_model.snapshot
        content_html = await render_template(
            "partials/dashboard_content.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            content_html,
            selector="#content",
            mode=consts.ElementPatchMode.INNER,
        )
        await asyncio.sleep(refresh_seconds())


@web_bp.route("/api/stats")
async def api_stats() -> Any:
    return view_model.snapshot


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
        return _generator_status_morph("Generator stop command sent")
    except Exception as exc:
        logger.exception("Generator stop failed")
        return _generator_status_morph(str(exc), error=True)
