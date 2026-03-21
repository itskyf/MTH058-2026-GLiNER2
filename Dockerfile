FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder
# https://docs.astral.sh/uv/guides/integration/docker/#caching
ENV UV_LINK_MODE=copy 
# No downloads needed, final stage uses system Python
ENV UV_PYTHON_DOWNLOADS=0
# Use lock file for reproducible builds
ENV UV_LOCKED=1
# Skip development dependencies
ENV UV_NO_DEV=1
# Non-editable installs for production deployment
ENV UV_NO_EDITABLE=1

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,readonly \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,readonly \
    uv sync --no-install-project

COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,readonly \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,readonly \
    uv sync 

FROM docker.io/python:3.13-slim-trixie
# https://www.fourdigits.nl/blog/python-containers-best-practices/
ENV PYTHONUNBUFFERED=1

COPY --from=builder /app/.venv /app/.venv

WORKDIR /app

ENV GRADIO_SERVER_NAME=0.0.0.0
EXPOSE 7860
ENTRYPOINT ["/app/.venv/bin/python"]
CMD ["-m", "mth058.gradio_app"]
