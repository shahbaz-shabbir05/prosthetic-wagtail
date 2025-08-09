from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from . import widgets


class ProductCard(blocks.StructBlock):
    title = blocks.CharBlock()
    description = blocks.TextBlock()
    image = ImageChooserBlock()

    new = blocks.BooleanBlock(required=False)

    button = widgets.LinkButton()

    bg_color = widgets.ColorChoiceBlock()

    class Meta:
        template = "widgets/product_card.html"


class OverflowCard(blocks.StructBlock):
    title = blocks.CharBlock()
    description = blocks.TextBlock()

    image = ImageChooserBlock()
    image_on_right = blocks.BooleanBlock(required=False)
    image_pop_out = blocks.BooleanBlock(required=False)

    bg_color = widgets.ColorChoiceBlock()
    text_color = widgets.ColorChoiceBlock()

    class Meta:
        template = "widgets/overflow_card.html"
