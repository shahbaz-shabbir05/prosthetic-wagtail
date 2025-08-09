from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-3mba#isl1rk^8^yig4y_3*n=g*)q5o5wp5mwe63kv!09okyyqq"  # noqa: S105

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


INSTALLED_APPS = INSTALLED_APPS + [  # noqa: F405
    "debug_toolbar",
    "django_browser_reload",
]

MIDDLEWARE = (
    [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]
    + MIDDLEWARE  # noqa: F405
    + [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ]
)

INTERNAL_IPS = ("127.0.0.1",)

try:
    from .local import *  # noqa: F403
except ImportError:
    pass
