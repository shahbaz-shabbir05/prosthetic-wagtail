from django.urls import path

from . import views

urlpatterns = [
    path("admin/static-site-rebuild", view=views.RebuildSiteView.as_view(), name="rebuild-static"),
]
