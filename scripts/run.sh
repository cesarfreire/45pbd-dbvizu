#!/bin/sh

set -e
python manage.py migrate
python manage.py collectstatic --noinput
uvicorn dbvizu.asgi:application --host 0.0.0.0 --port 80