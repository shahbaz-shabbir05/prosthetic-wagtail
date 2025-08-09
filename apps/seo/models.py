from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Locale, Page


class SEOMixin(models.Model):
    # Wagtail provides two meta fields by default:
    # - seo_title
    # - search_description

    charset = models.CharField(default="utf-8", max_length=50)
    viewport = models.CharField(default="width=device-width, initial-scale=1", max_length=50)

    # title (provided by Wagtail)
    # description (provided by Wagtail)

    og_title = models.CharField(max_length=200, blank=True, null=True)
    og_description = models.CharField(max_length=200, blank=True, null=True)
    og_image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.SET_NULL, related_name="+", blank=True, null=True
    )

    promote_panels = [
        MultiFieldPanel(
            heading="Search engine Optimisation",
            children=(
                FieldPanel("slug"),
                FieldPanel(
                    "seo_title",
                    heading="Meta title",
                    help_text="The title of the page as it should appear in search results. Defaults to the page title if empty.",
                ),
                FieldPanel("search_description"),
            ),
        ),
        MultiFieldPanel(
            heading="Social media optimisation",
            children=(
                FieldPanel(
                    "og_title",
                    heading="Social media title",
                    help_text="The title of the page as it should appear in social media. Defaults to the page title if empty.",
                ),
                FieldPanel(
                    "og_description",
                    heading="Social media description",
                    help_text="The descriptive text displayed on a social media card.",
                ),
                FieldPanel(
                    "og_image",
                    heading="Social media image",
                    help_text="The image displayed on a social media card.",
                ),
            ),
        ),
    ]

    @property
    def meta_title(self):
        return self.seo_title or self.title

    @property
    def og_type(self):
        return "website"

    @property
    def twitter_site(self):
        return "@TaskaGlobal"

    def get_link_tags(self, context) -> list:
        tags = [
            f'<link rel="canonical" href="{context["request"].build_absolute_uri()}" />',
        ]
        for locale in Locale.objects.all():
            try:
                translation = self.get_translation(locale).get_full_url()
                tags.append(f'<link rel="alternate" hreflang="{locale.language_code}" href="{translation}" />')
                if locale.language_code == "en":
                    tags.append(f'<link rel="alternate" hreflang="x-default" href="{translation}" />')
            except Page.DoesNotExist:
                pass
        return tags

    def get_meta_tags(self) -> dict:
        tags = {
            "viewport": self.viewport,
            "referrer": "strict-origin",
            "theme-color": "#ffffff",
            "color-scheme": "only light",
            "description": self.search_description,
        }

        return {k: v for k, v in tags.items() if v}

    def get_og_tags(self, context) -> dict:
        tags = {
            "og:title": self.og_title or self.meta_title or self.title,
            "og:type": self.og_type,
            "og:description": self.og_description or self.search_description,
            "og:image": self.og_image.file.url if self.og_image else "",
            "og:url": context["request"].build_absolute_uri(),
        }

        return {k: v for k, v in tags.items() if v}

    class Meta:
        abstract = True
