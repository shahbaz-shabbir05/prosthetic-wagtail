#!/bin/sh

. ./.venv/bin/activate

echo "${DJANGO_CONFIG}" > .env

./manage.py migrate --noinput || true

exec "$@"