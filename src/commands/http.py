from __future__ import annotations

import logging
import os

from hypercorn.asyncio import serve as hypercorn_serve  # type: ignore[import-untyped]
from hypercorn.config import Config  # type: ignore[import-untyped]

from web.app import create_app


def add_parser(subparsers):
    parser = subparsers.add_parser("http", help="start http server")
    parser.set_defaults(func=run)


def run(args: object) -> None:
    host = os.getenv("SELPI_HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("SELPI_HTTP_PORT", "8000"))

    app = create_app()
    config = Config()
    config.bind = [f"{host}:{port}"]
    config.use_reloader = False

    logging.getLogger("hypercorn.access").setLevel(logging.WARNING)
    logging.getLogger("hypercorn.error").setLevel(logging.WARNING)

    import asyncio

    asyncio.run(hypercorn_serve(app, config))
