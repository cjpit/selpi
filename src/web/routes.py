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
