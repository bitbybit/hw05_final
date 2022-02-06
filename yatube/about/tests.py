from http import HTTPStatus

from core.mixins import TestURLsMixin, TestViewsMixin
from django.test import Client, TestCase
from django.urls import reverse

APP_NAME = "about"


class URLTests(TestURLsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.urls_dict = {
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

    def setUp(self):
        self.guest_client = Client()


class ViewTests(TestViewsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.views_dict = {
            reverse(f"{APP_NAME}:author"): {
                "template": "about/author.html",
            },
            reverse(f"{APP_NAME}:tech"): {
                "template": "about/tech.html",
            },
        }

    def setUp(self):
        self.client = Client()
