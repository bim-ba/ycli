# syntax=docker/dockerfile:1
# Builds the ycli image from this source tree: the whole CLI, which serves MCP over stdio when
# run with no arguments (`docker run IMAGE tracker issues get KEY` runs that command instead).
# Stage one installs the project (with the `mcp` extra) and its locked dependencies into a virtual
# environment; stage two copies only that environment onto a plain Python runtime. Both stages use
# the same Python so the venv's interpreter link holds.

FROM ghcr.io/astral-sh/uv:0.12.22-python3.12-trixie-slim AS build
# The locked dependency set CI tested, installed (not editable) into /opt/ycli. --frozen, not
# --locked: the release builds from its tag, where pyproject already has the new version and the
# re-lock commit that follows the tag has not touched uv.lock yet; the dependencies are the same.
ENV UV_PROJECT_ENVIRONMENT=/opt/ycli UV_COMPILE_BYTECODE=1 UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy
WORKDIR /src
COPY pyproject.toml uv.lock README.md LICENSE CHANGELOG.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --extra mcp --extra jq --no-editable --no-cache

FROM python:3.12-slim-trixie
LABEL org.opencontainers.image.title="ycli" \
      org.opencontainers.image.description="Yandex 360 (Tracker, Wiki, Forms) MCP server and CLI" \
      org.opencontainers.image.source="https://github.com/bim-ba/ycli" \
      org.opencontainers.image.licenses="MIT" \
      io.modelcontextprotocol.server.name="io.github.bim-ba/ycli"
COPY --from=build /opt/ycli /opt/ycli
# `mcp start --transport http` keeps OAuth client registrations under FASTMCP_HOME: mount a
# volume on /data to keep users signed in across restarts.
RUN install -d -o nobody /data
ENV PATH=/opt/ycli/bin:$PATH FASTMCP_HOME=/data
USER nobody
ENTRYPOINT ["ycli"]
CMD ["mcp", "start"]
