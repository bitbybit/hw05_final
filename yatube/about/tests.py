from posts.tests.test_urls import URLTests as PostsURLTests
from posts.tests.test_views import ViewTests as PostsViewTests
from django.test import Client
from django.urls import reverse
from http import HTTPStatus

APP_NAME = "about"


class URLTests(PostsURLTests):
    urls_dict = {
        "guest": {
            HTTPStatus.OK: {
                "/about/author/": {
                    "template": "about/author.html",
                },
                "/about/tech/": {
                    "template": "about/tech.html",
                },
            }
        }
    }

    @classmethod
    def setUpTestData(cls):
        cls.guest_client = Client()


class ViewTests(PostsViewTests):
    views_dict = {
        reverse(f"{APP_NAME}:author"): {
            "template": "about/author.html",
        },
        reverse(f"{APP_NAME}:tech"): {
            "template": "about/tech.html",
        },
    }

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_entities_creation(self):
        pass
