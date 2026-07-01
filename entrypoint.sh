#!/usr/bin/env sh
set -e

# Apply database migrations (requires DATABASE_URL to be set at runtime).
# Platforms with a dedicated "release" phase (Heroku/Railway) can run migrate
# there instead and remove this line — running it here is safe and universal.
python manage.py migrate --noinput

# Start the app. Tune with WEB_CONCURRENCY / PORT env vars.
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-3}" \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
