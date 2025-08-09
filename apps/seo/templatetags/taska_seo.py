from django import template
from django.utils.safestring import mark_safe

from apps.seo.models import SEOMixin

register = template.Library()


@register.simple_tag(takes_context=True)
def seo(context: dict):
    page = context.get("page")

    if not isinstance(page, SEOMixin):
        return

    meta = []

    for key, value in page.get_meta_tags().items():
        meta.append(f'<meta name="{key}" content="{value}">')

    for key, value in page.get_og_tags(context).items():
        meta.append(f'<meta property="{key}" content="{value}">')

    meta.extend(page.get_link_tags(context))
    return mark_safe("\n".join(meta))  # noqa: S308
