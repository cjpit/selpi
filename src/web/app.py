from __future__ import annotations

import asyncio
import logging

from quart import Quart

from web.formatting import refresh_seconds
from web.routes import view_model, web_bp

logger = logging.getLogger(__name__)


async def _background_refresh() -> None:
    """Periodically refresh the view model in a background thread."""
    while True:
        try:
            await view_model.refresh_async()
        except Exception:  # pragma: no cover - hardware path
            logger.exception("background refresh failed")
        await asyncio.sleep(refresh_seconds())


def create_app() -> Quart:
    app = Quart(__name__, static_folder="static", template_folder="templates")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    app.register_blueprint(web_bp)

    @app.before_serving
    async def _start_background_refresh() -> None:
        await view_model.refresh_async()
        asyncio.create_task(_background_refresh())

    @app.route("/health")
    async def health() -> str:
        return "ok"

    return app
