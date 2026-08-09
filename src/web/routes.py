from __future__ import annotations

import asyncio
import logging
from typing import Any

from quart import Blueprint, render_template

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
    """SSE endpoint: renders HTML fragments and pushes them as morph patches."""
    while True:
        snapshot = view_model.snapshot

        # Render each section server-side and push as morph patches
        header_html = await render_template(
            "partials/header.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            header_html, selector="#header-meta"
        )

        alarm_html = await render_template(
            "partials/alarm_banner.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            alarm_html, selector="#alarm-banner"
        )

        overview_html = await render_template(
            "partials/overview.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            overview_html, selector="#tab-overview"
        )

        battery_html = await render_template(
            "partials/battery.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            battery_html, selector="#tab-battery"
        )

        solar_html = await render_template(
            "partials/solar.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            solar_html, selector="#tab-solar"
        )

        load_html = await render_template(
            "partials/load.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            load_html, selector="#tab-load"
        )

        generator_html = await render_template(
            "partials/generator.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            generator_html, selector="#tab-generator"
        )

        temperatures_html = await render_template(
            "partials/temperatures.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            temperatures_html, selector="#tab-temperatures"
        )

        alarms_html = await render_template(
            "partials/alarms.html", snapshot=snapshot
        )
        yield ServerSentEventGenerator.patch_elements(
            alarms_html, selector="#tab-alarms"
        )

        await asyncio.sleep(refresh_seconds())


@web_bp.route("/api/stats")
async def api_stats() -> Any:
    return view_model.snapshot
