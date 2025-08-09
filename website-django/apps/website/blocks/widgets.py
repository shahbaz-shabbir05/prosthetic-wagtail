from django.db import models
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class LinkButton(blocks.StructBlock):
    display_text = blocks.CharBlock()
    path = blocks.PageChooserBlock(help_text="Relative URL to page, e.g. /about-us/meet-the-team")

    class Meta:
        template = "widgets/link_button.html"


class ScrollButton(blocks.StructBlock):
    show_button = blocks.BooleanBlock(required=False)

    class Meta:
        template = "widgets/scroll_button.html"


class ColorChoiceBlock(blocks.ChoiceBlock):
    choices = [
        ("aqua", "Aqua"),
        ("black", "Black"),
        ("charbrown", "Charcoal Brown"),
        ("g2", "Gen2"),
        ("g2blk", "Gen2 Black"),
        ("racing", "Racing"),
        ("seventycx", "Seventy CX"),
        ("taskabackgroundgrey", "TASKA Background Grey"),
        ("taskablack", "TASKA Black"),
        ("taskablue", "TASKA Blue"),
        ("taskacharcoal", "TASKA Charcoal"),
        ("taskacoolgrey", "TASKA Cool Grey"),
        ("taskadarkblue", "TASKA Dark Blue"),
        ("taskagrey", "TASKA Grey"),
        ("taskapink", "TASKA Pink"),
        ("taskared", "TASKA RED"),
        ("taskaultralightgrey", "TASKA Ultralight Grey"),
        ("taskawheat", "TASKA Wheat"),
        ("white", "White"),
    ]

    class Meta:
        icon = "palette"


class Title(blocks.StructBlock):
    text = blocks.CharBlock()

    class Meta:
        template = "blocks/title.html"


class StaffMember(blocks.StructBlock):
    name = blocks.CharBlock()
    role = blocks.CharBlock()
    image = ImageChooserBlock()

    class Meta:
        template = "blocks/staff.html"


class StaffGrid(blocks.StructBlock):
    staff = blocks.ListBlock(StaffMember())

    class Meta:
        template = "blocks/staff_grid.html"


class DisplayStyleChoices(models.TextChoices):
    STANDARD = "Standard"
    CARD = "Card"
    FOOTNOTE = "Footnote"


class Display(blocks.StructBlock):
    columns = blocks.ListBlock(blocks.RichTextBlock())
    style = blocks.ChoiceBlock(choices=DisplayStyleChoices.choices, default=DisplayStyleChoices.STANDARD)

    class Meta:
        template = "blocks/display.html"


class PrivacyPolicy(blocks.StructBlock):
    class Meta:
        template = "widgets/privacy_policy.html"
