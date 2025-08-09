import django_rq
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from wagtail import hooks
from wagtail.admin.menu import AdminOnlyMenuItem
from wagtail.admin.models import Admin

from apps.staticbuild.jobs import store_static_page
from apps.staticbuild.views import BuildSpecificPageView


@hooks.register("register_admin_menu_item")
def register_rebuild_menu_item():
    return AdminOnlyMenuItem("Rebuild Static Site", reverse("rebuild-static"), icon_name="upload")


@hooks.register("after_publish_page")
def trigger_static_build(request, page):
    django_rq.enqueue(static_build_job, page.id)


def static_build_job(page_id):
    BuildSpecificPageView.for_page(page_id).build_method()
    store_static_page()


@hooks.register("register_permissions")
def register_static_permissions():
    content_type = ContentType.objects.get_for_model(Admin)
    permission, _ = Permission.objects.get_or_create(
        content_type=content_type,
        codename="can_rebuild_site",
        defaults={
            "name": "Can force a site rebuild",
        },
    )

    return Permission.objects.filter(id=permission.id)
