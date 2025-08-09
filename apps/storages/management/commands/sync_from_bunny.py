from io import BytesIO

from django.core.management import call_command
from django.core.management.base import BaseCommand
from PIL import Image as PILImage
from wagtail.images import get_image_model

from apps.storages.bunny import BunnyStorage


class Command(BaseCommand):
    help = "Create wagtail Image objects from files in the original_images folder of the CDN"

    def handle(self, *args, **options):
        storage = BunnyStorage()
        Image = get_image_model()

        # List all files in the original_images folder of the CDN
        cdn_files = storage._get("original_images/").json()

        success = []
        for file in cdn_files:
            if self._is_image(file):
                success.append(self._create_image(storage, file, Image))

        if any(success):
            self.stdout.write(self.style.NOTICE("Updating Wagtail image renditions. This may take a while."))
            call_command("wagtail_update_image_renditions")

    def _is_image(self, file):
        valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
        return any(file["ObjectName"].lower().endswith(ext) for ext in valid_extensions)

    def _create_image(self, storage, file, Image):
        try:
            file_name = file["ObjectName"]
            file_size = file["Length"]

            # Check if image already exists
            if Image.objects.filter(title=file_name).exists():
                self.stdout.write(self.style.WARNING(f"Image '{file_name}' already exists. Skipping."))
                return False

            # Prepend 'original_images/' to the file_name for CDN access
            cdn_path = f"original_images/{file_name}"

            # Get file content from CDN
            file_content = storage._open(cdn_path, "rb").read()

            with PILImage.open(BytesIO(file_content)) as pil_image:
                width, height = pil_image.size

            # Create Image object
            image = Image(title=file_name, file=cdn_path, file_size=file_size, width=width, height=height)
            image.save()

            self.stdout.write(self.style.SUCCESS(f"Successfully created Image object for '{file_name}'"))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating Image object for '{file_name}': {str(e)}"))
            return False
