from __future__ import annotations

import asyncio
import logging
from typing import Any

from quart import Blueprint, render_template, request, jsonify

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


@web_bp.route("/api/generator/control", methods=["POST"])
async def generator_control() -> Any:
    """
    Control the generator by simulating a front panel button press.
    
    Expected JSON body: {"action": "start"|"stop"}
    
    Short press (1) starts the generator, long press (2) stops it.
    """
    from muster import Muster
    from memory import variable
    
    data = await request.get_json()
    if not data or "action" not in data:
        return jsonify({"error": "Missing 'action' in request body"}), 400
    
    action = data["action"]
    if action not in ("start", "stop"):
        return jsonify({"error": "Invalid action. Must be 'start' or 'stop'"}), 400
    
    # Short press (1) = start, Long press (2) = stop
    press_value = 1 if action == "start" else 2
    
    try:
        muster = Muster()
        muster.write("GeneratorBtnPressPort1", press_value)
        return jsonify({"status": "success", "action": action})
    except Exception as exc:
        logger.exception("Generator control failed")
        return jsonify({"error": str(exc)}), 500
