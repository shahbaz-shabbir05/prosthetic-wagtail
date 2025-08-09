import logging
from io import BytesIO
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage

logger = logging.getLogger(__name__)


class BunnyStorage(Storage):
    _default_settings = {
        "BUNNYCDN_HOST": "hostname",
        "BUNNYCDN_ZONE": "zone",
        "BUNNYCDN_KEY": "api_key",
        "BUNNYCDN_PUBLIC_HOST": "public_host",
    }

    def __init__(self, bunny_settings=None) -> None:
        self._parse_storage_settings(bunny_settings)

    def _parse_storage_settings(self, bunny_settings=None) -> None:
        if not bunny_settings:
            for setting, attr in self._default_settings.items():
                try:
                    setattr(self, attr, getattr(settings, setting))
                except AttributeError:
                    raise ImproperlyConfigured(f"{setting} must be set.")
        else:
            for setting, attr in self._default_settings.items():
                try:
                    setattr(self, attr, bunny_settings[setting])
                except KeyError:
                    raise ImproperlyConfigured(f"{setting} must be set.")

        self.headers = {"AccessKey": self.api_key}
        self.base_url = urljoin(self.hostname, f"{self.zone}/")

    def _url(self, name: str) -> str:
        return urljoin(self.base_url, name)

    def _get(self, name: str, **kwargs) -> requests.Response:
        return requests.get(self._url(name), headers=self.headers, timeout=30, **kwargs)

    def _put(self, name: str, content: bytes) -> requests.Response:
        return requests.put(self._url(name), content, headers=self.headers, timeout=30)

    def listdir(self, dirname: str = "") -> list:
        response = self._get(dirname)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            return []
        return [obj["ObjectName"] for obj in response.json()]

    def exists(self, name: str) -> bool:
        return any(remote_name == name for remote_name in self.listdir())

    def _save(self, name: str, content: bytes) -> str:
        response = self._put(name, content)
        response.raise_for_status()
        return name

    def url(self, name):
        return urljoin(self.public_host, name)

    def delete(self, name):
        requests.delete(self._url(name), headers=self.headers, timeout=30)
        return name

    def _open(self, name, mode):
        response = self._get(name)

        if response.status_code == 404:
            raise ValueError("File not found.")

        return BytesIO(response.content)
