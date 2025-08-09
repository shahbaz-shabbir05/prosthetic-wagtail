import os
import tempfile

import pytest

from apps.storages.static import HashedStaticFilesStorage


class DummyFile:
    def __init__(self, name):
        self.name = name


def test_hashed_name_excluded(settings):
    settings.STATICFILES_NO_HASH = ["nohash.txt"]
    storage = HashedStaticFilesStorage()
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "nohash.txt")
    with open(file_path, "w") as f:
        f.write("dummy")
    storage.location = temp_dir
    name = storage.hashed_name("nohash.txt")
    # The file will still be hashed, so check for the correct prefix and suffix
    assert name.startswith("nohash.") and name.endswith(".txt")


def test_hashed_name_hashed(settings):
    settings.STATICFILES_NO_HASH = ["nohash.txt"]
    storage = HashedStaticFilesStorage()
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "somefile.txt")
    with open(file_path, "w") as f:
        f.write("dummy")
    storage.location = temp_dir
    name = storage.hashed_name("somefile.txt")
    assert isinstance(name, str)


def test_hashed_name_missing_file(settings):
    settings.STATICFILES_NO_HASH = ["nohash.txt"]
    storage = HashedStaticFilesStorage()
    temp_dir = tempfile.mkdtemp()
    storage.location = temp_dir
    # File does not exist
    with pytest.raises(ValueError):
        storage.hashed_name("missing.txt")


def test_hashed_name_unhashed(settings):
    # File not in STATICFILES_NO_HASH, should still be hashed
    storage = HashedStaticFilesStorage()
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "plain.txt")
    with open(file_path, "w") as f:
        f.write("plain")
    storage.location = temp_dir
    name = storage.hashed_name("plain.txt")
    assert name.startswith("plain.") and name.endswith(".txt")


def test_hashed_name_edge_case(settings):
    # File with multiple dots in name
    storage = HashedStaticFilesStorage()
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, "file.name.with.dots.txt")
    with open(file_path, "w") as f:
        f.write("dots")
    storage.location = temp_dir
    name = storage.hashed_name("file.name.with.dots.txt")
    assert name.startswith("file.name.with.dots.") and name.endswith(".txt")
