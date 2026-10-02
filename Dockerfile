# syntax=docker/dockerfile:1
# Builds the MCP server image from this source tree: stage one builds the wheel and installs it
# (with the `mcp` extra) into an isolated tool environment; stage two copies only that environment
# onto a plain Python runtime. Both stages use the same Python so the venv's interpreter link holds.

FROM ghcr.io/astral-sh/uv:0.12.22-python3.12-trixie-slim AS build
ENV UV_TOOL_BIN_DIR=/opt/ycli/bin UV_TOOL_DIR=/opt/ycli/tools UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=never
WORKDIR /src
COPY pyproject.toml README.md LICENSE CHANGELOG.md ./
COPY src ./src
RUN uv build --wheel --out-dir /dist \
    && uv tool install --no-cache "yandex-cli[mcp] @ $(ls /dist/*.whl)"

FROM python:3.12-slim-trixie
LABEL org.opencontainers.image.title="ycli" \
      org.opencontainers.image.description="Yandex 360 (Tracker, Wiki, Forms) MCP server and CLI" \
      org.opencontainers.image.source="https://github.com/bim-ba/ycli" \
      org.opencontainers.image.licenses="MIT" \
      io.modelcontextprotocol.server.name="io.github.bim-ba/ycli"
COPY --from=build /opt/ycli /opt/ycli
ENV PATH=/opt/ycli/bin:$PATH
USER nobody
ENTRYPOINT ["ycli"]
CMD ["mcp", "start"]
