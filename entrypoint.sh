#!/bin/bash
set -e
python /app/manage.py migrate
daphne -b 0.0.0.0 -p 8000 nevroth.asgi:application