import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image as PILImage
from wagtail.images.models import Image
from wagtail.models import Locale, Page

from apps.tests.fixtures import django_no_storage  # noqa: F401
from apps.website.models import (
    BlogOverviewPage,
    BlogPost,
    BottomNavigation,
    HeaderNavigation,
    HomePage,
    StandardPage,
    StayInTouch,
)


@pytest.mark.django_db
def test_homepage_creation():
    root = Page.objects.get(id=1)
    page = HomePage(title="Home", path="00010001", depth=2)
    root.add_child(instance=page)
    assert page.title == "Home"
    assert hasattr(page, "overlap_call_to_action")
    assert hasattr(page, "content")


@pytest.mark.django_db
def test_standardpage_creation():
    root = Page.objects.get(id=1)
    page = StandardPage(title="Standard", path="00010002", depth=2)
    root.add_child(instance=page)
    assert page.title == "Standard"
    assert hasattr(page, "hidden")
    assert hasattr(page, "content")


@pytest.mark.django_db
def test_blogoverviewpage_context():
    root = Page.objects.get(id=1)
    page = BlogOverviewPage(title="Blog Overview", path="00010003", depth=2)
    root.add_child(instance=page)
    context = page.get_context({})
    assert "page" in context


@pytest.mark.django_db
def test_blogpost_creation():
    root = Page.objects.get(id=1)
    overview = BlogOverviewPage(title="Blog Overview", path="00010004", depth=2)
    root.add_child(instance=overview)
    post = BlogPost(title="Blog Post", date="2024-01-01", path="000100040001", depth=3)
    overview.add_child(instance=post)
    assert post.title == "Blog Post"
    assert hasattr(post, "date")
    assert hasattr(post, "content")


@pytest.mark.django_db
def test_header_navigation_str():
    nav = HeaderNavigation.objects.create()
    nav.locale = Locale.objects.get(language_code="en")
    nav.save()
    assert "Header Navigation" in str(nav)


@pytest.mark.django_db
def test_bottom_navigation_str():
    nav = BottomNavigation.objects.create()
    nav.locale = Locale.objects.get(language_code="en")
    nav.save()
    assert "Footer Navigation" in str(nav)


@pytest.mark.django_db
def test_stay_in_touch_str(django_no_storage):  # noqa: F811
    # Generate a real in-memory PNG image using Pillow
    img_bytes = io.BytesIO()
    pil_img = PILImage.new("RGBA", (1, 1), (255, 0, 0, 0))
    pil_img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    image = Image.objects.create(title="test", file=ContentFile(img_bytes.read(), "test.png"))
    sit = StayInTouch.objects.create(image=image)
    sit.locale = Locale.objects.get(language_code="en")
    sit.save()
    assert "Stay in Touch" in str(sit)


@pytest.mark.django_db
def test_standardpage_required_fields():
    Page.objects.get(id=1)
    # Missing title should raise error
    with pytest.raises(ValidationError):
        page = StandardPage(path="00010005", depth=2)
        page.full_clean()


@pytest.mark.django_db
def test_blogpost_relationship_and_delete():
    root = Page.objects.get(id=1)
    overview = BlogOverviewPage(title="Blog Overview", path="00010006", depth=2)
    root.add_child(instance=overview)
    post = BlogPost(title="Blog Post", date="2024-01-01", path="000100060001", depth=3)
    overview.add_child(instance=post)
    post_id = post.id
    post.delete()
    assert not BlogPost.objects.filter(id=post_id).exists()


@pytest.mark.django_db
def test_blogoverviewpage_get_context_fields():
    page = BlogOverviewPage(title="Blog Overview", path="00010007", depth=2)
    Page.objects.get(id=1).add_child(instance=page)
    context = page.get_context({"extra": "value"})
    assert "page" in context
