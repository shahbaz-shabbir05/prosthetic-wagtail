@echo off
setlocal enabledelayedexpansion

set "env=dev"
set "args="

:parse_args
if "%~1"=="-e" (
    set "env=%~2"
    shift
    shift
) else (
    set "args=!args! %1"
    shift
)
if not "%~1"=="" goto parse_args

set "cmd=podman compose exec -e DJANGO_SETTINGS_MODULE=website_django.settings.%env% django poetry run python ./manage.py"

%cmd%%args%