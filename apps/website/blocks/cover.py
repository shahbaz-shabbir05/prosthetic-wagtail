from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from . import cards, widgets


class SideBySide(blocks.StructBlock):
    text = blocks.RichTextBlock()
    image = ImageChooserBlock()

    button = widgets.LinkButton()
    scroll_button = widgets.ScrollButton()

    bg_color = widgets.ColorChoiceBlock()
    text_color = widgets.ColorChoiceBlock()

    class Meta:
        template = "blocks/side_by_side.html"


class FullScreenImageWithTextOver(blocks.StructBlock):
    heading = blocks.TextBlock(help_text="Text to display in a heading font.")
    text = blocks.RichTextBlock()
    image = ImageChooserBlock()

    fade_image = blocks.BooleanBlock(required=False)
    show_button = blocks.BooleanBlock(required=False)
    text_on_left = blocks.BooleanBlock(required=False)

    button = widgets.LinkButton()
    cards = blocks.ListBlock(cards.ProductCard())

    class Meta:
        template = "blocks/full_screen_image_with_text_over.html"


class HomePageCover(blocks.StructBlock):
    text = blocks.RichTextBlock()
    image = ImageChooserBlock()

    button = widgets.LinkButton()

    class Meta:
        template = "blocks/home_page_cover.html"
