import html

import pytest
from django.template import Context, Template
from django.test import RequestFactory
from wagtail.models import Page

from apps.website.models import HomePage


@pytest.mark.django_db
def test_seomixin_meta_title():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", seo_title="SEO Title", path="00010010", depth=2)
    root.add_child(instance=page)
    assert page.meta_title == "SEO Title"
    page.seo_title = ""
    assert page.meta_title == "Test Title"


@pytest.mark.django_db
def test_seomixin_meta_title_fallback():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", seo_title="", path="00010016", depth=2)
    root.add_child(instance=page)
    assert page.meta_title == "Test Title"


@pytest.mark.django_db
def test_seomixin_og_type():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", path="00010011", depth=2)
    root.add_child(instance=page)
    assert page.og_type == "website"


@pytest.mark.django_db
def test_seomixin_twitter_site():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", path="00010012", depth=2)
    root.add_child(instance=page)
    assert page.twitter_site == "@TaskaGlobal"


@pytest.mark.django_db
def test_seomixin_get_link_tags():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", seo_title="SEO Title", path="00010013", depth=2)
    root.add_child(instance=page)
    factory = RequestFactory()
    request = factory.get("/")
    context = {"request": request}
    tags = page.get_link_tags(context)
    assert any('rel="canonical"' in tag for tag in tags)
    assert any('hreflang="en"' in tag for tag in tags)


@pytest.mark.django_db
def test_seomixin_get_meta_tags():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", search_description="desc", path="00010014", depth=2)
    root.add_child(instance=page)
    tags = page.get_meta_tags()
    assert tags["description"] == "desc"
    assert "viewport" in tags


@pytest.mark.django_db
def test_seomixin_get_meta_tags_empty():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", path="00010017", depth=2)
    root.add_child(instance=page)
    tags = page.get_meta_tags()
    # description key may not be present if not set
    assert "description" not in tags or tags["description"] == ""


@pytest.mark.django_db
def test_seomixin_get_og_tags():
    root = Page.objects.get(id=1)
    page = HomePage(
        title="Test Title",
        og_title="OG Title",
        og_description="OG Desc",
        search_description="desc",
        path="00010015",
        depth=2,
    )
    root.add_child(instance=page)
    factory = RequestFactory()
    request = factory.get("/")
    context = {"request": request}
    tags = page.get_og_tags(context)
    assert tags["og:title"] == "OG Title"
    assert tags["og:type"] == "website"
    assert tags["og:description"] == "OG Desc"
    assert tags["og:url"].endswith("/")


@pytest.mark.django_db
def test_seomixin_get_og_tags_defaults():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", path="00010018", depth=2)
    root.add_child(instance=page)
    factory = RequestFactory()
    request = factory.get("/test/")
    context = {"request": request}
    tags = page.get_og_tags(context)
    assert tags["og:title"] == "Test Title"
    assert tags["og:type"] == "website"
    assert tags["og:url"].endswith("/test/")


@pytest.mark.django_db
def test_seomixin_template_rendering():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", seo_title="SEO Title", path="00010019", depth=2)
    root.add_child(instance=page)
    template = Template("""
        <title>{{ page.meta_title }}</title>
        <meta name="description" content="{{ page.get_meta_tags.description }}">
    """)
    context = Context({"page": page})
    rendered = template.render(context)
    assert "SEO Title" in rendered
    assert "description" in rendered


@pytest.mark.django_db
def test_seomixin_meta_title_none_and_unicode():
    root = Page.objects.get(id=1)
    # Use empty string for seo_title (not nullable)
    page = HomePage(title="Tést Tïtle 🚀", seo_title="", path="00010020", depth=2)
    root.add_child(instance=page)
    assert page.meta_title == "Tést Tïtle 🚀"
    page.seo_title = "<b>SEO & Title</b>"
    assert page.meta_title == "<b>SEO & Title</b>"


@pytest.mark.django_db
def test_seomixin_get_link_tags_missing_request():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", seo_title="SEO Title", path="00010021", depth=2)
    root.add_child(instance=page)
    # context without request, should raise KeyError
    context = {}
    with pytest.raises(KeyError):
        page.get_link_tags(context)


@pytest.mark.django_db
def test_seomixin_get_og_tags_missing_fields():
    root = Page.objects.get(id=1)
    # Use minimal valid non-empty strings for title and slug
    page = HomePage(title="x", seo_title="", slug="x", path="00010022", depth=2)
    root.add_child(instance=page)
    factory = RequestFactory()
    request = factory.get("/og-missing/")
    context = {"request": request}
    tags = page.get_og_tags(context)
    assert tags["og:title"] == "x"
    assert tags["og:type"] == "website"
    assert tags["og:url"].endswith("/og-missing/")


@pytest.mark.django_db
def test_seomixin_template_tag_rendering():
    root = Page.objects.get(id=1)
    page = HomePage(title="Test Title", seo_title="SEO Title", slug="test-title", path="00010023", depth=2)
    root.add_child(instance=page)
    page.live = True
    page.save()
    factory = RequestFactory()
    request = factory.get("/test-title/")
    link_tags = page.get_link_tags({"request": request})
    template = Template("""
        {% for tag in link_tags %}{{ tag }}{% endfor %}
    """)
    context = Context({"link_tags": link_tags})
    rendered = template.render(context)
    unescaped = html.unescape(rendered)
    assert 'rel="canonical"' in unescaped
