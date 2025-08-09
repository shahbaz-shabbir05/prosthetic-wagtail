from django.http import Http404
from django.templatetags.static import static
from wagtail import hooks
from wagtail.admin.panels import FieldPanel
from wagtail.rich_text import LinkHandler
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from apps.website.models import BottomNavigation, HeaderNavigation, StandardPage, StayInTouch


class HeaderNavigationViewSet(SnippetViewSet):
    model = HeaderNavigation

    panels = [FieldPanel("central_nav"), FieldPanel("right_hand_nav")]


class FooterNavigationViewSet(SnippetViewSet):
    model = BottomNavigation

    panels = [FieldPanel("nav_blocks"), FieldPanel("extra_links")]


class StayInTouchViewSet(SnippetViewSet):
    model = StayInTouch

    panels = [FieldPanel("image"), FieldPanel("content")]


register_snippet(FooterNavigationViewSet)
register_snippet(HeaderNavigationViewSet)
register_snippet(StayInTouchViewSet)


@hooks.register("register_rich_text_features")
def make_h1_default(features):
    features.default_features.append("h5")
    features.default_features.sort()


@hooks.register("before_serve_page")
def dont_show_hidden_pages(page, request, serve_args, serve_kwargs):
    if isinstance(page, StandardPage) and page.hidden:
        raise Http404()


@hooks.register("insert_editor_js")
def editor_js():
    js_files = [
        "admin/custom.js",
    ]
    js_includes = "".join([f'<script src="{static(js_file)}"></script>' for js_file in js_files])
    return js_includes


class CustomLinkHandler(LinkHandler):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        return f'<a href="{href}" class="font-bold text-taskalink hover:underline transition-colors duration-500 decoration-transparent hover:decoration-taskalink" target="_blank" rel="noreferrer noopener nofollow">'


@hooks.register("register_rich_text_features")
def register_custom_link_feature(features):
    features.register_link_type(CustomLinkHandler)
