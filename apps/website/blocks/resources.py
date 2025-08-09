from django.db import models
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock


class DownloadCategory(blocks.MultipleChoiceBlock):
    choices = [
        ("clinician", "Clinicians"),
        ("user", "Users"),
    ]


class FileTypeChoices(models.TextChoices):
    # Don't forget to update templates/widgets/download_filter if you change this!
    DOCUMENT = "document", "Document"
    IMAGE = "image", "Image"
    LINK = "link", "Link"
    SOFTWARE = "software", "Software"
    VIDEO = "video", "Video"
    OTHER = "other", "Other"


class File(blocks.StructBlock):
    title = blocks.CharBlock()
    category = DownloadCategory()
    file_type = blocks.ChoiceBlock(choices=FileTypeChoices.choices)

    file = DocumentChooserBlock()

    class Meta:
        template = "blocks/file.html"


class ExternalFile(blocks.StructBlock):
    title = blocks.CharBlock()
    category = DownloadCategory()
    file_type = blocks.ChoiceBlock(choices=FileTypeChoices.choices)

    url = blocks.URLBlock()

    class Meta:
        template = "blocks/file.html"


class DownloadCategory(blocks.StructBlock):
    title = blocks.CharBlock()

    downloads = blocks.StreamBlock(
        [
            ("file", File()),
            ("external_content", ExternalFile()),
        ]
    )

    class Meta:
        template = "blocks/download_category.html"


class Downloads(blocks.StructBlock):
    categories = blocks.ListBlock(DownloadCategory())

    class Meta:
        template = "blocks/downloads.html"
