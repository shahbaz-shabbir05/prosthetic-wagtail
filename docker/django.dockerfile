FROM python:3.13.1-alpine

RUN apk add npm && pip install poetry==1.8.5 --root-user-action=ignore

WORKDIR /app

ENTRYPOINT ["docker/django_init.sh"]
