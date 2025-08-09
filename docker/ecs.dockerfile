FROM python:3.13-alpine AS python-builder

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN pip install poetry==1.8.5 && \
    poetry config virtualenvs.in-project true && \
    poetry install --without=dev

COPY . .

FROM node:22-alpine AS node-builder

WORKDIR /app

COPY package.json package.json
COPY package-lock.json package-lock.json

RUN npm install

COPY . .

RUN npx --yes @tailwindcss/cli -i /app/theme/src/theme.css -o /app/website_django/static/css/taska.css

FROM python:3.13-alpine

COPY --from=python-builder /app /app
COPY --from=node-builder /app/website_django/static/css/taska.css /app/website_django/static/css/taska.css

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=website_django.settings.base

RUN apk add --no-cache npm && \
    ./.venv/bin/python ./manage.py collectstatic --noinput

ENTRYPOINT ["/app/entrypoint-ecs.sh"]
