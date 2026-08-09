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
    Returns a Datastar morph patch to update the UI.
    """
    from muster import Muster
    from memory import variable
    from datastar_py.sse import ServerSentEventGenerator
    from datastar_py import consts
    
    data = await request.get_json()
    if not data or "action" not in data:
        error_html = '<div class="control-status control-status--error">Missing action</div>'
        return DatastarResponse(ServerSentEventGenerator.patch_elements(
            error_html,
            selector="#generator-status",
            mode=consts.ElementPatchMode.INNER,
        )), 400
    
    action = data["action"]
    if action not in ("start", "stop"):
        error_html = '<div class="control-status control-status--error">Invalid action</div>'
        return DatastarResponse(ServerSentEventGenerator.patch_elements(
            error_html,
            selector="#generator-status",
            mode=consts.ElementPatchMode.INNER,
        )), 400
    
    # Short press (1) = start, Long press (2) = stop
    press_value = 1 if action == "start" else 2
    
    try:
        muster = Muster()
        muster.write("GeneratorBtnPressPort1", press_value)
        logger.info("Generator %s requested (button press value=%d)", action, press_value)
        
        # Return a morph patch showing the command was sent
        success_html = (
            '<div class="control-status control-status--success">'
            f'Generator {action} command sent'
            '</div>'
        )
        return DatastarResponse(ServerSentEventGenerator.patch_elements(
            success_html,
            selector="#generator-status",
            mode=consts.ElementPatchMode.INNER,
        ))
    except Exception as exc:
        logger.exception("Generator control failed")
        error_html = f'<div class="control-status control-status--error">{exc}</div>'
        return DatastarResponse(ServerSentEventGenerator.patch_elements(
            error_html,
            selector="#generator-status",
            mode=consts.ElementPatchMode.INNER,
        )), 500
