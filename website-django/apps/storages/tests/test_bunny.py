import io

import pytest
import requests

from apps.storages.bunny import BunnyStorage


class DummySettings:
    BUNNYCDN_HOST = "https://storage.bunnycdn.com"
    BUNNYCDN_ZONE = "taska-dev"
    BUNNYCDN_KEY = "bdecf5b7-3f7a-40c6-bfeaf69ee98e-5778-49e2"
    BUNNYCDN_PUBLIC_HOST = "https://taska-dev.b-cdn.net"


@pytest.fixture
def mock_bunny_storage(settings):
    settings.BUNNYCDN_HOST = DummySettings.BUNNYCDN_HOST
    settings.BUNNYCDN_ZONE = DummySettings.BUNNYCDN_ZONE
    settings.BUNNYCDN_KEY = DummySettings.BUNNYCDN_KEY
    settings.BUNNYCDN_PUBLIC_HOST = DummySettings.BUNNYCDN_PUBLIC_HOST


# Helper for mock responses
class MockResp:
    def __init__(self, status_code=200, content=b"", raise_exc=None):
        self.status_code = status_code
        self.content = content
        self._raise_exc = raise_exc

    def raise_for_status(self):
        if self._raise_exc:
            raise self._raise_exc
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


def test_bunny_storage_init(mock_bunny_storage):
    storage = BunnyStorage()
    assert storage.hostname.rstrip("/") == DummySettings.BUNNYCDN_HOST.rstrip("/")
    assert storage.zone == DummySettings.BUNNYCDN_ZONE
    # BunnyStorage uses zone-based public host
    assert DummySettings.BUNNYCDN_ZONE in storage.public_host
    assert storage.public_host.rstrip("/").endswith(".b-cdn.net")


def test_bunny_storage_url(mock_bunny_storage):
    storage = BunnyStorage()
    url = storage._url("file.txt")
    assert DummySettings.BUNNYCDN_ZONE in url
    assert url.endswith("file.txt")


def test_bunny_storage_save(monkeypatch, mock_bunny_storage):
    storage = BunnyStorage()
    called = {}

    def fake_put(url, data, headers, timeout):
        called["url"] = url
        called["data"] = data.read() if hasattr(data, "read") else data
        called["headers"] = headers
        called["timeout"] = timeout
        return MockResp(201)

    monkeypatch.setattr(requests, "put", fake_put)
    name = "folder/test.txt"
    content = io.BytesIO(b"hello world")
    result = storage._save(name, content)
    assert result == name
    assert DummySettings.BUNNYCDN_ZONE in called["url"]
    assert called["data"] == b"hello world"


def test_bunny_storage_open(monkeypatch, mock_bunny_storage):
    storage = BunnyStorage()

    def fake_get(url, headers, timeout):
        return MockResp(200, b"filedata")

    monkeypatch.setattr(requests, "get", fake_get)
    f = storage._open("file.txt", "rb")
    assert f.read() == b"filedata"


def test_bunny_storage_open_404(monkeypatch, mock_bunny_storage):
    storage = BunnyStorage()

    def fake_get(url, headers, timeout):
        return MockResp(404)

    monkeypatch.setattr(requests, "get", fake_get)
    with pytest.raises(ValueError):
        storage._open("missing.txt", "rb")


def test_bunny_storage_delete(monkeypatch, mock_bunny_storage):
    storage = BunnyStorage()
    called = {}

    def fake_delete(url, headers, timeout):
        called["url"] = url
        called["headers"] = headers
        called["timeout"] = timeout
        return MockResp(204)

    monkeypatch.setattr(requests, "delete", fake_delete)
    result = storage.delete("file.txt")
    assert result == "file.txt"
    assert DummySettings.BUNNYCDN_ZONE in called["url"]


def test_bunny_storage_exists(monkeypatch, mock_bunny_storage):
    storage = BunnyStorage()

    def fake_get(url, headers, timeout):
        return MockResp(200)

    monkeypatch.setattr(requests, "get", fake_get)
    # Patch listdir to avoid real HTTP
    monkeypatch.setattr(storage, "listdir", lambda dirname="": ["file.txt"])
    assert storage.exists("file.txt")
    monkeypatch.setattr(storage, "listdir", lambda dirname="": [])
    assert not storage.exists("file.txt")


def test_bunny_storage_url_public(mock_bunny_storage):
    storage = BunnyStorage()
    url = storage.url("file.txt")
    # BunnyStorage may use zone-based public host, e.g. https://taska-dev.b-cdn.net
    assert "b-cdn.net" in url
    assert url.endswith("file.txt")


def test_bunny_storage_save_error(monkeypatch, mock_bunny_storage):
    storage = BunnyStorage()

    def fake_put(url, data, headers, timeout):
        return MockResp(500)

    monkeypatch.setattr(requests, "put", fake_put)
    with pytest.raises(Exception):
        storage._save("file.txt", io.BytesIO(b"fail"))
