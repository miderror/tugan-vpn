FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    POETRY_VERSION=2.2.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/opt/poetry_cache

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

# ================= DEVELOPMENT =================
FROM base AS dev
RUN id=tugan-poetry,target=/opt/poetry_cache \
    poetry install --no-root --no-interaction --no-ansi

# ================= PRODUCTION =================
FROM base AS prod
RUN poetry install --no-root --no-interaction --no-ansi
COPY . .
