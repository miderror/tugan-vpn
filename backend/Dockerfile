FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    POETRY_VERSION=2.0.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

# ================= DEVELOPMENT =================
FROM base AS dev
RUN poetry install --no-root
COPY . .

# ================= PRODUCTION =================
FROM base AS prod
RUN poetry install --only main --no-root
COPY . .
