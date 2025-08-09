import logging
import os
import shutil
import subprocess
from urllib.parse import urljoin

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateView
from wagtail.admin.models import Admin
from wagtail.admin.views.generic import WagtailAdminTemplateMixin
from wagtail.admin.views.generic.permissions import PermissionCheckedMixin
from wagtail.models import Page, Site
from wagtail.permission_policies import ModelPermissionPolicy
from wagtail.views import serve as wagtail_serve
from wagtailbakery.views import AllPublishedPagesView

from . import forms, jobs

logger = logging.getLogger(__name__)


def wagtail_serve_drafts(request, path):
    """
    Serve Wagtail pages, showing draft versions to authenticated users.

    This view function overrides the default Wagtail page serving mechanism to display draft (unpublished)
    versions of pages to authenticated users, while serving live (published) versions to anonymous users.
    """

    if not request.user.is_authenticated:
        return wagtail_serve(request, path)

    site = Site.find_for_request(request)
    root_path = site.root_page.localized.url_path
    try:
        page = Page.objects.specific().get(url_path=urljoin(root_path, path)).get_latest_revision_as_object()
    except Exception as e:
        logger.error(f"Page not found {path}, {e}")
        raise Http404()
    return page.serve(request)


class BuildSpecificPageView(AllPublishedPagesView):
    _build_paths = []

    @classmethod
    def for_page(cls, page_id: int):
        view = cls()
        view.get_queryset = lambda: Page.objects.filter(id=page_id).live()
        return view

    def get_build_path(self, obj):
        build_path = super().get_build_path(obj)
        self._build_paths.append(build_path)
        return build_path

    def build_queryset(self):
        super().build_queryset()
        self.remove_static_dir()
        self.prettify_built_files()

    def remove_static_dir(self):
        try:
            if getattr(settings, "STATIC_ROOT", False):
                shutil.rmtree(settings.STATIC_ROOT)
                logger.debug(f"Removed temporary static file dir: {settings.STATIC_ROOT}")
        except FileNotFoundError:
            pass

        for directory in getattr(settings, "EXCLUDE_STATIC_DIRS", []):
            try:
                path = os.path.join(
                    settings.BUILD_DIR,
                    settings.STATIC_URL.lstrip("/"),
                    directory,
                )
                shutil.rmtree(path)
                logger.debug(f"Removed excluded static file dir: {path}")
            except FileNotFoundError:
                pass

    def prettify_built_files(self):
        try:
            result = subprocess.run(  # noqa: S603
                [  # noqa: S607
                    "npx",
                    "--yes",
                    "prettier",
                    "--write",
                    "--ignore-path=.prettierignore",
                    *self._build_paths,
                ],
                cwd="/app",
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout:
                logger.info(f"Prettier stdout: {result.stdout}")

            if result.stderr:
                logger.warning(f"Prettier stderr: {result.stderr}")

            logger.info("Prettier completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Prettier failed with return code {e.returncode}")
            logger.error(f"Prettier stdout: {e.stdout}")
            logger.error(f"Prettier stderr: {e.stderr}")
        except Exception as e:
            logger.exception(f"An unexpected error occurred while running Prettier: {e}")


class RebuildSiteView(PermissionCheckedMixin, WagtailAdminTemplateMixin, TemplateView):
    template_name = "wagtailadmin/generic/form.html"
    page_title = "Rebuild Static Site"
    header_icon = "upload"
    form_class = forms.RebuildSiteForm
    permission_policy = ModelPermissionPolicy(Admin)
    permission_required = "can_rebuild_site"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(self.request.POST)
        context["submit_button_label"] = "Submit"
        context["submit_button_active_label"] = "Rebuild in Progress"
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid() and form.cleaned_data["rebuild"]:
            try:
                jobs.build_static.run_async(wait=True)
            except jobs.JobFailed:
                messages.error(request, "Failed to build the site")
            else:
                try:
                    jobs.store_static_page.run_async(wait=True)
                except jobs.JobFailed:
                    messages.error(request, "Failed to upload the site")
                else:
                    messages.success(request, "Site rebuilt")
        return TemplateResponse(request, self.template_name, self.get_context_data())
