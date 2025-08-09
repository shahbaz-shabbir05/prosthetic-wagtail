import logging

from django.core.management.base import BaseCommand

from apps.staticbuild.jobs import store_static_page

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        store_static_page.run_async()
