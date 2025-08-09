from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.blocks import PageChooserBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageBlock
from wagtail.models import Page, TranslatableMixin

from apps.seo.models import SEOMixin

from .blocks.content import FAQ, FiftyFifty, OverflowCardList, ProductComparison, SelectDisplay
from .blocks.cover import FullScreenImageWithTextOver, HomePageCover, SideBySide
from .blocks.resources import Downloads
from .blocks.widgets import Display, PrivacyPolicy, StaffGrid, Title


class HomePage(SEOMixin, Page):
    overlap_call_to_action = models.BooleanField(default=False, help_text="Display call to action above content.")
    content = StreamField(
        [
            ("fifty_fifty", FiftyFifty()),
            ("home_page_cover", HomePageCover()),
            ("side_by_side", SideBySide()),
            ("full_screen_image_with_text_over", FullScreenImageWithTextOver()),
            ("product_comparison", ProductComparison()),
        ],
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [FieldPanel("content")]

    promote_panels = Page.promote_panels + [
        FieldPanel("overlap_call_to_action"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["website.StandardPage", "website.BlogOverviewPage"]


class HeaderMixin(models.Model):
    header_image = models.ForeignKey(
        "wagtailimages.Image", blank=True, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    header_quote = models.CharField(max_length=200, blank=True)
    header_quote_attribution = models.CharField(max_length=200, blank=True)
    header_options = models.IntegerField(default=0, choices=((0, "Title and Image"), (1, "Quote and Image")))

    header_panels = [
        MultiFieldPanel(
            heading="Header",
            children=[
                FieldPanel("header_image"),
                FieldPanel("header_options"),
                FieldPanel("header_quote"),
                FieldPanel("header_quote_attribution"),
            ],
        ),
    ]

    class Meta:
        abstract = True


class StandardPage(SEOMixin, HeaderMixin, Page):
    hidden = models.BooleanField(default=False, help_text="Hide page from users.")
    overlap_call_to_action = models.BooleanField(default=False, help_text="Display call to action above content.")

    content = StreamField(
        [
            ("page_title", Title()),
            ("display", Display()),
            ("staff_grid", StaffGrid()),
            ("fifty_fifty", FiftyFifty()),
            ("side_by_side", SideBySide()),
            ("full_screen_image_with_text_over", FullScreenImageWithTextOver()),
            ("privacy_policy", PrivacyPolicy()),
            ("downloads", Downloads()),
            ("overflow_card_list", OverflowCardList()),
            ("frequently_asked_questions", FAQ()),
            ("select_display", SelectDisplay()),
        ],
        blank=True,
        null=True,
    )

    content_panels = (
        Page.content_panels
        + HeaderMixin.header_panels
        + [
            FieldPanel("hidden"),
            FieldPanel("content"),
        ]
    )

    promote_panels = Page.promote_panels + [
        FieldPanel("overlap_call_to_action"),
    ]

    add_bottom_padding = models.BooleanField(default=True)


class BlogOverviewPage(SEOMixin, HeaderMixin, Page):
    parent_page_types = ["website.StandardPage", "website.HomePage"]
    subpage_types = ["website.BlogPost"]

    content_panels = Page.content_panels + HeaderMixin.header_panels

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        setattr(context["page"], "background_class", "bg-taskabackgroundgrey")
        return context


class BlogPost(SEOMixin, HeaderMixin, Page):
    date = models.DateField("Post date")

    content = StreamField(
        (
            ("text", blocks.RichTextBlock()),
            ("image", ImageBlock()),
        )
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            heading="Header",
            children=[
                FieldPanel("header_image"),
                FieldPanel("header_options"),
                FieldPanel("header_quote"),
                FieldPanel("header_quote_attribution"),
            ],
        ),
        FieldPanel("date"),
        FieldPanel("content"),
    ]

    parent_page_types = [
        "website.BlogOverviewPage",
    ]


class NavigationBlock(blocks.StructBlock):
    title = blocks.CharBlock()
    links = blocks.ListBlock(blocks.PageChooserBlock())

    class Meta:
        icon = "link"
        template = "layout/footer_widgets/nav_block.html"


class HeaderNavigation(TranslatableMixin, models.Model):
    central_nav = StreamField([("navigation_block", NavigationBlock())])
    right_hand_nav = StreamField([("navigation_block", NavigationBlock())])

    def __str__(self):
        return f"Header Navigation ({self.locale})"

    class Meta:
        # This was required after a migration. I don't think it should be required.
        constraints = [
            models.UniqueConstraint(
                fields=("translation_key", "locale"),
                name="unique_translation_key_locale_home_headernavigation",
            )
        ]

        verbose_name = verbose_name_plural = "Header Navigation"


class BottomNavigation(TranslatableMixin, models.Model):
    nav_blocks = StreamField([("navigation_block", NavigationBlock())])
    extra_links = StreamField(
        [("page", PageChooserBlock())],
        help_text="Extra links to display at bottom of page.",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Footer Navigation ({self.locale})"

    class Meta:
        # This was required after a migration. I don't think it should be required.
        constraints = [
            models.UniqueConstraint(
                fields=("translation_key", "locale"),
                name="unique_translation_key_locale_home_bottomnavigation",
            )
        ]
        verbose_name = verbose_name_plural = "Footer Navigation"


class StayInTouch(TranslatableMixin, models.Model):
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
    )
    content = RichTextField(blank=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("text"),
    ]

    def __str__(self):
        return f"Stay in Touch ({self.locale})"
