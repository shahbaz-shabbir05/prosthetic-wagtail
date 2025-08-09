from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView

from apps.staticbuild.views import wagtail_serve_drafts
from localize_crowdin import views

urlpatterns = [
    path("", include("apps.staticbuild.urls")),
    path("django-admin/", admin.site.urls),
    re_path(r"^images/([^/]*)/(\d*)/([^/]*)/[^/]*$", ServeView.as_view(redirect=True), name="wagtailimages_serve"),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sync/", views.sync),
    path("pretranslate/", views.pretranslate),
    path("django-rq/", include("django_rq.urls")),
    path("robots.txt", RedirectView.as_view(url="/static/robots.txt")),
]


if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]


urlpatterns += i18n_patterns(
    re_path(r"^(?P<path>.*)$", wagtail_serve_drafts, name="wagtail_serve_drafts"),
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)
