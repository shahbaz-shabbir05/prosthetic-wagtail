from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from . import cards, widgets


class FiftyFifty(blocks.StructBlock):
    text = blocks.RichTextBlock()
    image = ImageChooserBlock()

    image_on_left = blocks.BooleanBlock(required=False)

    # Todo - turn this into a single (optional) button rather than a list!
    button = blocks.ListBlock(widgets.LinkButton(), min_num=0, max_num=1)
    scroll_button = widgets.ScrollButton()

    bg_color = widgets.ColorChoiceBlock(default="white")
    text_color = widgets.ColorChoiceBlock(default="black")

    class Meta:
        template = "blocks/fifty_fifty.html"


class OverflowCardList(blocks.StructBlock):
    title = blocks.RichTextBlock()
    cards = blocks.ListBlock(cards.OverflowCard())

    bg_color = widgets.ColorChoiceBlock()
    text_color = widgets.ColorChoiceBlock()

    class Meta:
        template = "blocks/overflow_card_list.html"


class ProductComparison(blocks.StructBlock):
    text = blocks.RichTextBlock()
    images = blocks.ListBlock(ImageChooserBlock(), max_num=2)

    button = widgets.LinkButton()

    class Meta:
        template = "blocks/product_comparison.html"


class TextBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock()


class FAQ(blocks.StructBlock):
    title = blocks.CharBlock()
    entries = blocks.ListBlock(TextBlock())

    class Meta:
        template = "blocks/faq.html"


class SelectDisplayEntry(blocks.StructBlock):
    title = blocks.CharBlock()
    text = blocks.RichTextBlock()


class SelectDisplay(blocks.StructBlock):
    title = blocks.CharBlock()
    entries = blocks.ListBlock(SelectDisplayEntry())

    class Meta:
        template = "blocks/select_display.html"
