FROM python:3.14-slim-trixie AS builder
# python slim -> uses glibc -> most compatible with wheels

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# Running three inline commands
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

COPY pyproject.toml README.md ./

RUN mkdir app && touch app/__init__.py
RUN pip install --upgrade pip setuptools wheel && pip install ".[dev]"

COPY ./app ./app

RUN pip install --no-deps -e .

FROM python:3.14-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

RUN mkdir -p /app/celery-state && chown app:app /app/celery-state

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app ./app ./app

COPY --chown=app:app ./alembic.ini ./alembic.ini
COPY --chown=app:app ./alembic ./alembic

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

