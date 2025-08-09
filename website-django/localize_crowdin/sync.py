import os
import tempfile
import time
import zipfile
from io import BytesIO

import requests
from crowdin_api import CrowdinClient
from polib import pofile
from wagtail.models import Locale, Page, Site
from wagtail_localize.models import Translation, TranslationSource
from wagtail_localize.operations import TranslationCreator
from wagtail_localize.tasks import get_backend

SETTINGS = {"token": "59af92bb3792e98654b4eb4b604f316248cbf2f3eb1b71ccfc1f7104319f34fb5b8b2231fc9e4b7c"}


class TranslationClient(CrowdinClient):
    TOKEN = SETTINGS["token"]
    PROJECT_ID = 748441
    PAGE_SIZE = 50


cli = TranslationClient()


def enqueue(func, *args, **kwargs):
    get_backend().enqueue(func, args, kwargs)


def pretranslate():
    lang_ids = [d["id"] for d in cli.projects.get_project()["data"]["targetLanguages"]]

    files = [d["data"]["id"] for d in cli.source_files.list_files()["data"]]
    cli.translations.apply_pre_translation(lang_ids, files, method="ai", aiPromptId=113909)
    pass


def task_parse_build(data):
    with tempfile.TemporaryDirectory(delete=False) as tmpdirname:
        with zipfile.ZipFile(data) as z:
            z.extractall(tmpdirname)
            # Not enqueueing this to allow the context manager can clean up.
            task_parse_build_files(tmpdirname)


def task_parse_build_files(dirname):
    available_locales = {obj.language_code: obj for obj in Locale.objects.all()}
    root_page_path = Site.objects.get(is_default_site=True).root_page.url_path
    for locale_dir in (d for d in os.scandir(dirname) if d.is_dir()):
        locale = available_locales.get(locale_dir.name)
        if not locale:
            continue

        base_path = locale_dir.path

        for current_dir, _, files in os.walk(locale_dir):
            page_path = current_dir.replace(base_path, "").lstrip("/")
            for filename in (f for f in files if f.endswith(".po")):
                full_path = os.path.join(root_page_path, page_path, filename.rstrip(".po"))
                full_path = full_path if full_path.endswith("/") else f"{full_path}/"

                page = Page.objects.get(url_path=full_path)
                source, _ = TranslationSource.get_or_create_from_instance(page)
                TranslationCreator(None, [locale]).create_translations(page)
                translation = Translation.objects.get(source=source, target_locale=locale)
                translation.import_po(pofile(os.path.join(current_dir, filename)))


def task_download_build(build_id):
    response = cli.translations.download_project_translations(build_id)
    download = requests.get(response["data"]["url"], timeout=10)
    download.raise_for_status()

    enqueue(task_parse_build, BytesIO(download.content))


def task_check_build_status(response, retries=0):
    if response["data"]["status"] == "finished":
        enqueue(task_download_build, response["data"]["id"])

    else:
        # Todo - add a timeout and a max retry count
        time.sleep(2)

        enqueue(task_check_build_status, response, retries=retries + 1)

    return


def task_fetch_translations():
    response = cli.translations.build_project_translation({})

    enqueue(task_check_build_status, response)


def fetch_translations():
    enqueue(task_fetch_translations)
    # translations = cli.translations.build_project_translation({})
    # translations = cli.translations.download_project_translations(68)
    # print("Translations: ", translations)
    pass
