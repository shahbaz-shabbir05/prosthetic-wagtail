import os

from django.conf import settings
from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class HashedStaticFilesStorage(ManifestStaticFilesStorage):
    """
    A custom static files storage backend that appends an MD5 hash to the filenames
    of static files for cache busting purposes. This storage backend discards the
    original files without the hash and does not generate a manifest file.
    """

    exclude_files = getattr(settings, "STATICFILES_NO_HASH", [])

    def hashed_name(self, name, content=None, filename=None):
        if name in self.exclude_files:
            return name
        return super().hashed_name(name, content, filename)

    def post_process(self, paths, dry_run=False, **options):
        files_to_remove = {}

        for original_path, processed_path, processed in super().post_process(paths, dry_run, **options):
            if original_path in self.exclude_files:
                yield original_path, original_path, processed
            else:
                yield original_path, processed_path, processed
                files_to_remove[original_path] = processed_path

        for original_path, processed_path in files_to_remove.items():
            if original_path not in self.exclude_files:
                original_full_path = self.path(original_path)
                if os.path.exists(original_full_path):
                    os.remove(original_full_path)

        manifest_path = self.path(self.manifest_name)
        if os.path.exists(manifest_path):
            os.remove(manifest_path)
