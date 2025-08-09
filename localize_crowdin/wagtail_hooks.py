import io
import json
import logging

from crowdin_api import CrowdinClient
from crowdin_api.exceptions import ValidationError
from wagtail import models
from wagtail_localize.models import TranslationSource

SETTINGS = {"token": "59af92bb3792e98654b4eb4b604f316248cbf2f3eb1b71ccfc1f7104319f34fb5b8b2231fc9e4b7c"}

logger = logging.getLogger(__name__)


class TranslationClient(CrowdinClient):
    TOKEN = SETTINGS["token"]
    PROJECT_ID = 748441
    PAGE_SIZE = 50


cli = TranslationClient()


def source_file_exists(context):
    context = json.loads(context.decode("utf-8"))
    for error in context["errors"]:
        if error["error"] == "name" and any(entry["code"] == "notUnique" for entry in error["errors"]):
            return True
    return False


def submit_file(page, dir_id):
    fname = f"{page.slug}.po"
    source, _ = TranslationSource.get_or_create_from_instance(page)
    source_file = io.BytesIO(source.export_po().__unicode__().encode("utf-8"))
    source_file.name = fname
    try:
        storage = cli.storages.add_storage(source_file)
        cli.source_files.add_file(storage["data"]["id"], fname, directoryId=dir_id)
    except ValidationError as e:
        if source_file_exists(e.context):
            files = cli.source_files.list_files(directoryId=dir_id)
            file_id = [f["data"]["id"] for f in files["data"] if f["data"]["name"] == fname][0]
            cli.source_files.update_file(file_id, storage["data"]["id"], fname, directoryId=dir_id)
    except Exception as e:
        logger.error(f"Error submitting page {fname} for translation: {str(e)}")


def make_crowdin_dirs(directories, path):
    if path in directories:
        return directories

    path = path.lstrip("/")
    head, _, this = path.rpartition("/")

    if head and f"/{head}" not in directories:
        directories = make_crowdin_dirs(directories, f"/{head}")

    if not this:
        return directories

    remote_dir = directories.get(f"/{head}", {})
    response = cli.source_files.add_directory(this, directoryId=remote_dir.get("id"))
    directories[response["data"]["path"]] = response["data"]

    return directories


def submit_to_crowdin(page: models.Page):
    directories = {d["data"]["path"]: d["data"] for d in cli.source_files.list_directories()["data"]}

    parent_url = page.get_parent().get_url()
    parent_path = parent_url.rstrip("/") if parent_url else "/"

    directories = make_crowdin_dirs(directories, parent_path)
    return submit_file(page, directories.get(parent_path, {}).get("id"))


# @hooks.register("after_publish_page")
# @hooks.register("after_create_page")
# @hooks.register("after_delete_page")
# @hooks.register("after_unpublish_page")
# @hooks.register("after_edit_page")
# def trigger_static_build(request, page: models.Page):
#     if page.locale.is_default:
#         get_backend().enqueue(submit_to_crowdin, [page], {})
