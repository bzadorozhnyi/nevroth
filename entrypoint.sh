#!/bin/bash
set -e
python /app/manage.py migrate
gunicorn nevroth.wsgi:application --workers 3 --bind 0.0.0.0:8000