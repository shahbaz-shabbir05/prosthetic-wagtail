import os
import tempfile
from unittest import mock

import pytest
from django.core.management.base import CommandError

from apps.staticbuild.jobs import build_static


@pytest.mark.django_db
def test_build_static_calls_build(monkeypatch, settings):
    build_dir = tempfile.mkdtemp()
    settings.BUILD_DIR = build_dir
    settings.BAKERY_VIEWS = ["apps.staticbuild.views.BuildSpecificPageView"]
    with mock.patch("django.core.management.call_command") as call_mock:
        build_static.run_sync()
        call_mock.assert_any_call("collectstatic", interactive=False, verbosity=0)


@pytest.mark.django_db
def test_build_static_minify(monkeypatch, settings):
    build_dir = tempfile.mkdtemp()
    settings.BUILD_DIR = build_dir
    settings.BAKERY_VIEWS = ["apps.staticbuild.views.BuildSpecificPageView"]
    with mock.patch("django.core.management.call_command") as call_mock, mock.patch("subprocess.run") as subproc_mock:
        build_static.run_sync(minify=True)
        call_mock.assert_any_call("collectstatic", interactive=False, verbosity=0)
        subproc_mock.assert_called()


@pytest.mark.django_db
def test_build_static_missing_build_dir(monkeypatch, settings):
    # Remove BUILD_DIR to simulate missing setting
    if hasattr(settings, "BUILD_DIR"):
        del settings.BUILD_DIR
    settings.BAKERY_VIEWS = ["apps.staticbuild.views.BuildSpecificPageView"]
    with pytest.raises(CommandError):
        build_static.run_sync()


@pytest.mark.django_db
def test_build_static_error(monkeypatch, settings):
    build_dir = tempfile.mkdtemp()
    settings.BUILD_DIR = build_dir
    settings.BAKERY_VIEWS = ["apps.staticbuild.views.BuildSpecificPageView"]

    def fake_call_command(*args, **kwargs):
        raise Exception("fail")

    monkeypatch.setattr("django.core.management.call_command", fake_call_command)
    with pytest.raises(Exception):
        build_static.run_sync()


@pytest.mark.django_db
def test_build_static_file_system(monkeypatch, settings):
    build_dir = tempfile.mkdtemp()
    settings.BUILD_DIR = build_dir
    settings.BAKERY_VIEWS = ["apps.staticbuild.views.BuildSpecificPageView"]
    # Simulate a file in build dir
    test_file = os.path.join(build_dir, "test.html")
    with open(test_file, "w") as f:
        f.write("<html></html>")
    with mock.patch("django.core.management.call_command"):
        build_static.run_sync()
        assert os.path.exists(build_dir)
