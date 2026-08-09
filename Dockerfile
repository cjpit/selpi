FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim
ADD ./src /app
WORKDIR /app
RUN ["uv", "sync", "--locked", "--python", "3.14"]
CMD ["uv", "run", "selpi.py", "http"]
