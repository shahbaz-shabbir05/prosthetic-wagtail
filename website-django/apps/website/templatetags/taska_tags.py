from django import template
from django.conf import settings
from django.templatetags.static import static

from apps.website.models import BottomNavigation, HeaderNavigation, StayInTouch

register = template.Library()


@register.simple_tag(takes_context=True)
def get_footer_nav(context: dict) -> BottomNavigation | None:
    """
    Returns the footer navigation object for the current language.

    Args:
        context (dict): The Django template context object.

    Returns:
        BottomNavigation | None: The footer navigation object if found, otherwise None.
    """
    return BottomNavigation.objects.filter(locale__language_code=context.get("LANGUAGE_CODE", "en")).first()


@register.simple_tag(takes_context=True)
def get_header_nav(context: dict) -> HeaderNavigation | None:
    """
    Returns the header navigation object for the current language.

    Args:
        context (dict): The Django template context object.

    Returns:
        HeaderNavigation | None: The header navigation object if found, otherwise None.
    """
    return HeaderNavigation.objects.filter(locale__language_code=context.get("LANGUAGE_CODE", "en")).first()


@register.simple_tag(takes_context=True)
def get_call_to_action(context: dict) -> StayInTouch | None:
    """
    Returns the StayInTouch object for the current language.

    Args:
        context (dict): The Django template context object.

    Returns:
        StayInTouch | None: The StayInTouch object if found, otherwise None.
    """
    return StayInTouch.objects.filter(locale__language_code=context.get("LANGUAGE_CODE", "en")).first()


@register.simple_tag(takes_context=True)
def get_store_img(context: dict, store: str) -> str:
    """
    Returns the URL for the given app store badge for the current language.

    Args:
        context (dict): The Django template context object.
        store (str): The app store name. Supported values are "apple", "google".

    Returns:
        str: The URL for the app store badge image.

    Raises:
        KeyError: If the store is not supported.
    """
    if store not in ["apple", "google"]:
        raise KeyError("Store unsupported.")

    language_code = context.get("LANGUAGE_CODE", "en")
    if language_code not in [lang[0] for lang in settings.LANGUAGES]:
        language_code = "en"  # default to English if language code is invalid

    return static(f"img/store/{store}/{language_code}.svg")


@register.simple_tag(takes_context=False)
def get_socials() -> list[dict]:
    """
    Returns a list of social media platforms with their names, links, and images.

    Returns:
        list[dict]: A list of dictionaries containing the social media platform information.
    """
    return [
        {
            "name": "Instagram",
            "link": "https://www.instagram.com/taskaglobal/",
            "image": static("img/socials/socials_ig_white.svg"),
        },
        {
            "name": "Facebook",
            "link": "https://www.facebook.com/TaskaGlobal",
            "image": static("img/socials/socials_fb_white.svg"),
        },
        {
            "name": "YouTube",
            "link": "https://www.youtube.com/channel/UCUPrtJtSPBVR0yCwSOA4a9Q",
            "image": static("img/socials/socials_yt_white.svg"),
        },
        {
            "name": "X",
            "link": "https://twitter.com/TaskaGlobal",
            "image": static("img/socials/socials_tw_white.svg"),
        },
        {
            "name": "LinkedIn",
            "link": "https://www.linkedin.com/company/taska-prosthetics",
            "image": static("img/socials/socials_ln_white.svg"),
        },
    ]


@register.simple_tag(takes_context=False)
def bytes_to_mb(size_bytes: int) -> str:
    """
    Converts a size in bytes to a human-readable format in megabytes.

    Args:
        size_bytes (int): The size in bytes.

    Returns:
        str: The size in megabytes with one decimal place.
    """
    if not size_bytes:
        return "0.0 MB"
    size_mb = round(size_bytes / (1024**2), 1)
    return f"{size_mb:.1f} MB"


@register.simple_tag(takes_context=False)
def is_static() -> bool:
    return getattr(settings, "STATIC_BUILD", False)


@register.inclusion_tag("tags/ribbon.html", takes_context=True)
def ribbon(context: dict) -> dict:
    page = context.get("page")
    if not page:
        return {}

    is_draft = page.has_unpublished_changes
    text = "Draft" if is_draft else "Published"
    color = "#F07818" if is_draft else "#32a852"
    return {"text": text, "color": color}


@register.filter(name="download_icon")
def download_icon(value):
    if "file_type" in value:
        return f"img/downloads/{value['file_type']}.svg"
    return "img/downloads/document.svg"


@register.filter(name="download_user_categories")
def download_user_categories(value):
    user_categories = set()
    for download in value["downloads"]:
        user_categories.update(download.value["category"])
    return list(user_categories)


@register.filter(name="download_file_categories")
def download_file_categories(value):
    file_categories = set()
    for download in value["downloads"]:
        file_categories.add(download.value["file_type"])
    return list(file_categories)
