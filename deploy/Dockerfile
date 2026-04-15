FROM python:3.14.4-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

FROM python:3.14.4-slim

ENV PYTHONPATH="${PYTHONPATH}:/app/src/"
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:${PATH}"ENV DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY . .
