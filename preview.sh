#!/bin/bash
# Start the standalone energy flow preview server
# No inverter connection needed — uses mock data
# Open http://localhost:8000/preview/energy-flow in your browser
set -e
cd "$(dirname "$0")/src"
uv run python preview.py
