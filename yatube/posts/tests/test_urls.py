from http import HTTPStatus
from typing import Dict, Mapping

from core.mixins import TestURLsMixin
from django.test import Client, TestCase

from ..models import Group, Post, User

typing_urls = Mapping[str, Dict[str, str]]

URLS_GUEST_ALLOWED: typing_urls = {
    "/": {
        "template": "posts/index.html",
    },
    "/group/test/": {
        "template": "posts/group_list.html",
    },
    "/profile/test/": {
        "template": "posts/profile.html",
    },
    "/posts/1/": {
        "template": "posts/post_detail.html",
    },
}

URLS_USER_ALLOWED: typing_urls = {
    "/create/": {
        "template": "posts/create_post.html",
    },
    "/posts/1/comment/": {
        "template": "posts/post_detail.html",
    },
}

URLS_AUTHOR_ALLOWED: typing_urls = {
    "/posts/1/edit/": {
        "template": "posts/create_post.html",
        "url_redirect": "/posts/1/",
    }
}

URLS_NOT_EXISTING: typing_urls = {
    "/unexisting_page/": {"template": "core/404.html"},
}

URLS_GUEST_SUBSCRIPTIONS: typing_urls = {
    "/profile/test/follow/": {},
}

URLS_USER_SUBSCRIPTIONS: typing_urls = {
    "/profile/test/follow/": {
        "url_redirect": "/profile/test/",
    },
}


class URLTests(TestURLsMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.urls_dict = {
            "guest": {
                HTTPStatus.OK: URLS_GUEST_ALLOWED,
                HTTPStatus.FOUND: {
                    **URLS_AUTHOR_ALLOWED,
                    **URLS_USER_ALLOWED,
                    **URLS_GUEST_SUBSCRIPTIONS,
                },
                HTTPStatus.NOT_FOUND: URLS_NOT_EXISTING,
            },
            "user": {
                HTTPStatus.OK: {**URLS_USER_ALLOWED, **URLS_GUEST_ALLOWED},
                HTTPStatus.FOUND: {
                    **URLS_AUTHOR_ALLOWED,
                    **URLS_USER_SUBSCRIPTIONS,
                },
                HTTPStatus.NOT_FOUND: URLS_NOT_EXISTING,
            },
            "author": {
                HTTPStatus.OK: {
                    **URLS_AUTHOR_ALLOWED,
                    **URLS_USER_ALLOWED,
                    **URLS_GUEST_ALLOWED,
                },
                HTTPStatus.FOUND: URLS_USER_SUBSCRIPTIONS,
                HTTPStatus.NOT_FOUND: URLS_NOT_EXISTING,
            },
        }

        cls.author = User.objects.create(username="test_author")
        cls.group = Group.objects.create(title="Название", slug="test")
        cls.post = Post.objects.create(
            text="Текст",
            group=cls.group,
            author=cls.author,
        )

        cls.user = User.objects.create(username="test")

    def setUp(self):
        self.guest_client = Client()

        self.user_client = Client()
        self.user_client.force_login(URLTests.user)

        self.author_client = Client()
        self.author_client.force_login(URLTests.author)
