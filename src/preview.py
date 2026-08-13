"""Standalone preview app — serves the energy flow preview without any
inverter connection.  Run with:

    cd src && uv run python preview.py

Open http://localhost:8000/preview/energy-flow
"""
from __future__ import annotations

from quart import Quart, render_template


def create_preview_app() -> Quart:
    app = Quart(__name__, static_folder="web/static", template_folder="web/templates")
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    @app.route("/preview/energy-flow")
    async def preview_energy_flow():
        return await render_template("preview_energy_flow.html")

    return app


app = create_preview_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
