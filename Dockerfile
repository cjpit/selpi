FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
ADD ./src /app
# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked
CMD ["uv", "run", "selpi.py", "http"]

