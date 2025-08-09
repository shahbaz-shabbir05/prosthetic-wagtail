import concurrent.futures
import logging
import os
import subprocess
import time

import django_rq
from django.conf import settings
from django.core.management import call_command

from apps.storages.bunny import BunnyStorage

logger = logging.getLogger(__name__)


class JobFailed(Exception):
    pass


class _Job:
    @classmethod
    def run_async(cls, wait=False, *args, **kwargs):
        job = django_rq.enqueue(cls.run_sync, *args, **kwargs)
        while not job.is_finished and not job.is_failed:
            time.sleep(0.1)
            job.refresh()
        if job.is_failed:
            raise JobFailed()

    @classmethod
    def run_sync(cls):
        raise NotImplementedError()


class build_static(_Job):
    @classmethod
    def run_sync(cls, minify=False):
        call_command("build")
        logger.info("Static build finished.")

        if minify:
            subprocess.run(["npm", "run", "minify", settings.BUILD_DIR])  # noqa: S603, S607
            logger.info("Static HTML minified.")


def save_file(storage, relative_path, path):
    with open(path, "rb") as f:
        logger.debug(f"Uploading {relative_path}")
        storage._save(relative_path, f)


class store_static_page(_Job):
    @classmethod
    def run_sync(cls):
        from django.conf import settings

        storage = BunnyStorage(bunny_settings=settings.BUNNY_STORAGE)

        build_dir = settings.BUILD_DIR
        to_upload = {}

        for root, _, files in os.walk(build_dir):
            relative_dirpath = os.path.relpath(root, build_dir).lstrip(".")

            if all(f.endswith(".html") for f in files):
                # Dont list folders that only contain html files. We'll be uploading them
                # anyway.
                remote_files = []
            else:
                remote_files = storage.listdir(relative_dirpath)

            for file in files:
                path = os.path.join(root, file)
                relative_path = os.path.relpath(path, build_dir)

                if relative_path in remote_files and not relative_path.endswith(".html"):
                    # Skip files already uploaded and skip any html files. There's probably a
                    # better way to do this.
                    logger.debug(f"File already uploaded: {relative_path}")
                    continue
                else:
                    to_upload[relative_path] = path

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for relative_path, path in to_upload.items():
                executor.submit(save_file, storage, relative_path, path)
