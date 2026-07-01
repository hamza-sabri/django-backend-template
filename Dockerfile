# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Minimal runtime deps. psycopg2-binary and Pillow ship manylinux wheels, so no
# build toolchain is needed; curl is only for the container healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching.
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# App code.
COPY . .

# Collect static at build time (WhiteNoise serves them). Uses throwaway env just
# so settings can import — collectstatic never touches the database.
RUN SECRET_KEY=build-only DATABASE_URL=postgres://u:p@localhost:5432/db \
    python manage.py collectstatic --noinput

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/api/docs/" || exit 1

# Entrypoint migrates then launches gunicorn (see entrypoint.sh).
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
