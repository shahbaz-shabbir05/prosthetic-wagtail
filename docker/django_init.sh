#!/bin/sh

cd /app

poetry install

exec poetry "$@"