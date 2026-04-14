#!/usr/bin/env sh
set -e

export FLASK_ENV="${FLASK_ENV:-production}"

flask db upgrade
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --timeout 120 \
    --graceful-timeout 30 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
