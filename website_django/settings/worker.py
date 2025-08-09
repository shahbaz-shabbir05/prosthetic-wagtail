import os

from decouple import config

from .base import *  # noqa: F403

DEBUG = False

# This flag ensures that the "published/draft" ribbon is not shown in the static build.
STATIC_BUILD = True

# Bakery
BAKERY_VIEWS = ("apps.staticbuild.views.BuildSpecificPageView",)

STATIC_ROOT = os.path.join(BASE_DIR, "static_static")  # noqa: F405
BUILD_DIR = os.path.join(BASE_DIR, "static_build")  # noqa: F405
BAKERY_MULTISITE = True
BAKERY_GZIP = False

EXCLUDE_STATIC_DIRS = [
    "admin",
    "wagtail_localize",
    "wagtailadmin",
    "wagtaildocs",
    "wagtailembeds",
    "wagtailimages",
    "wagtailsnippets",
    "wagtailusers",
]

BUNNY_STORAGE = {
    "BUNNYCDN_HOST": "https://storage.bunnycdn.com",
    "BUNNYCDN_ZONE": config("BUNNYCDN_ZONE", default=""),
    "BUNNYCDN_KEY": config("BUNNYCDN_KEY", default=""),
    "BUNNYCDN_PUBLIC_HOST": config("BUNNYCDN_PUBLIC_HOST", default=""),
}

STATICFILES_NO_HASH = [
    "robots.txt",
]

try:
    STORAGES["staticfiles"] = {  # noqa: F405
        # Replace the manifest storage, because we can rely on ETAGs in production and
        # don't need to include md5 hashes in file names.
        "BACKEND": "apps.storages.static.HashedStaticFilesStorage",
    }
except NameError:
    pass

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} [{levelname}] {name}: {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}
