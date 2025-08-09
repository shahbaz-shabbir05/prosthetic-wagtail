import pytest


@pytest.fixture
def django_no_storage(settings):
    settings.STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
    }
