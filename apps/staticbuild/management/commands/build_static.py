import logging

from django.core.management.base import BaseCommand

from apps.staticbuild.jobs import build_static

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--minify", "-m", action="store_true", help="Minify the static HTML after building", default=False
        )

    def handle(self, *args, **options):
        build_static.run_async(minify=options["minify"])
