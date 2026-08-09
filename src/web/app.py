from __future__ import annotations

import logging

from quart import Quart

from web.routes import web_bp

logger = logging.getLogger(__name__)


def create_app() -> Quart:
    app = Quart(__name__, static_folder="static", template_folder="templates")
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    app.register_blueprint(web_bp)

    @app.route("/health")
    async def health() -> str:
        return "ok"

    return app
