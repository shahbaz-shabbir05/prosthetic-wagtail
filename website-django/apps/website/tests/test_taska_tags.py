from unittest import mock

import pytest
from django.template import Context, Template
from django.template import Context as DjangoContext
from django.test import TestCase
from wagtail.models import Locale

from apps.website.models import BottomNavigation, HeaderNavigation
from apps.website.templatetags.taska_tags import bytes_to_mb, get_footer_nav, get_header_nav, get_socials, get_store_img

pytestmark = pytest.mark.django_db


class TestTaskaTags(TestCase):
    def setUp(self):
        self.locale_en = Locale.objects.get(language_code="en")
        self.bottom_nav = BottomNavigation.objects.create(locale=self.locale_en)
        self.header_nav = HeaderNavigation.objects.create(locale=self.locale_en)

    def test_get_footer_nav(self):
        context = Context({"LANGUAGE_CODE": "en"})
        footer_nav = get_footer_nav(context)
        assert isinstance(footer_nav, BottomNavigation)

    def test_get_footer_nav_invalid_language_code(self):
        context = Context({"LANGUAGE_CODE": " invalid_language_code"})
        footer_nav = get_footer_nav(context)
        assert footer_nav is None

    def test_get_header_nav(self):
        context = Context({"LANGUAGE_CODE": "en"})
        header_nav = get_header_nav(context)
        assert isinstance(header_nav, HeaderNavigation)

    def test_get_header_nav_invalid_language_code(self):
        context = Context({"LANGUAGE_CODE": " invalid_language_code"})
        header_nav = get_header_nav(context)
        assert header_nav is None

    @mock.patch("django.contrib.staticfiles.storage.staticfiles_storage.url", return_value="/static/dummy.svg")
    def test_get_store_img(self, mock_static):
        context = Context({"LANGUAGE_CODE": "en"})
        store_img_url = get_store_img(context, "apple")
        assert isinstance(store_img_url, str)
        assert store_img_url == "/static/dummy.svg"

    def test_get_store_img_invalid_store(self):
        context = Context({"LANGUAGE_CODE": "en"})
        with pytest.raises(KeyError):
            get_store_img(context, " invalid_store")

    @mock.patch("django.contrib.staticfiles.storage.staticfiles_storage.url", return_value="/static/dummy.svg")
    def test_get_store_img_invalid_language_code(self, mock_static):
        context = Context({"LANGUAGE_CODE": " invalid_language_code"})
        store_img_url = get_store_img(context, "apple")
        assert isinstance(store_img_url, str)
        assert store_img_url == "/static/dummy.svg"

    @mock.patch("django.contrib.staticfiles.storage.staticfiles_storage.url", return_value="/static/dummy.svg")
    def test_get_socials(self, mock_static):
        socials = get_socials()
        assert isinstance(socials, list)
        assert all(isinstance(social, dict) for social in socials)

    def test_bytes_to_mb(self):
        size_bytes = 1024 * 1024
        size_mb = bytes_to_mb(size_bytes)
        assert size_mb == "1.0 MB"

    def test_bytes_to_mb_invalid_input(self):
        with pytest.raises(TypeError):
            bytes_to_mb(" invalid_input")

    def test_get_footer_nav_with_extra_context(self):
        context = Context({"LANGUAGE_CODE": "en", "extra": "value"})
        footer_nav = get_footer_nav(context)
        assert isinstance(footer_nav, BottomNavigation)

    def test_get_header_nav_with_extra_context(self):
        context = Context({"LANGUAGE_CODE": "en", "extra": "value"})
        header_nav = get_header_nav(context)
        assert isinstance(header_nav, HeaderNavigation)

    def test_get_store_img_error(self):
        context = Context({"LANGUAGE_CODE": "en"})
        with pytest.raises(KeyError):
            get_store_img(context, "notastore")

    @mock.patch("django.contrib.staticfiles.storage.staticfiles_storage.url", return_value="/static/dummy.svg")
    def test_template_rendering_with_tags(self, mock_static):
        # Integration test: render a template using the tags
        template = Template("""
            {% load taska_tags %}
            {% get_footer_nav as footer_nav %}
            {% get_header_nav as header_nav %}
            {% get_store_img 'apple' as apple_img %}
            {{ footer_nav }} {{ header_nav }} {{ apple_img }}
        """)
        context = DjangoContext({"LANGUAGE_CODE": "en"})
        rendered = template.render(context)
        assert "Footer Navigation" in rendered
        assert "Header Navigation" in rendered
        assert "/static/" in rendered or ".svg" in rendered

    def test_bytes_to_mb_zero(self):
        assert bytes_to_mb(0) == "0.0 MB"
