#!/usr/bin/env bash
set -e
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py seed || true
exec gunicorn msms.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 60
