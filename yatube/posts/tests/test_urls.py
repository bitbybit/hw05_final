from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Post, Group, User

URLS_GUEST_ALLOWED = {
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

URLS_USER_ALLOWED = {
    "/create/": {
        "template": "posts/create_post.html",
    }
}

URLS_AUTHOR_ALLOWED = {
    "/posts/1/edit/": {
        "template": "posts/create_post.html",
        "url_redirect": "/posts/1/",
    }
}

URLS_NOT_EXISTING = {
    "/unexisting_page/": None,
}


class URLTests(TestCase):
    urls_dict = {
        "guest": {
            HTTPStatus.OK: URLS_GUEST_ALLOWED,
            HTTPStatus.FOUND: {**URLS_AUTHOR_ALLOWED, **URLS_USER_ALLOWED},
            HTTPStatus.NOT_FOUND: URLS_NOT_EXISTING,
        },
        "user": {
            HTTPStatus.OK: {**URLS_USER_ALLOWED, **URLS_GUEST_ALLOWED},
            HTTPStatus.FOUND: URLS_AUTHOR_ALLOWED,
            HTTPStatus.NOT_FOUND: URLS_NOT_EXISTING,
        },
        "author": {
            HTTPStatus.OK: {
                **URLS_AUTHOR_ALLOWED,
                **URLS_USER_ALLOWED,
                **URLS_GUEST_ALLOWED,
            },
            HTTPStatus.NOT_FOUND: URLS_NOT_EXISTING,
        },
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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

    @staticmethod
    def get_url_redirect_default(url: str) -> str:
        """
        Возвращает URL, куда должен перенаправляться пользователь если
        отсутствует доступ (для случаев когда в `urls_dict` не задан
        ожидаемый URL перенаправления проверяемой страницы).
        """
        return f"/auth/login/?next={url}"

    def test_pages_http_code_and_template(self):
        """
        Проверка ожидаемого кода ответа страниц и соответствия шаблона.
        (только для кода ответа 200)
        """
        for user_type, urls in self.urls_dict.items():
            for http_code_expected, urls_data in urls.items():
                is_redirect = http_code_expected == HTTPStatus.FOUND
                is_ok = http_code_expected == HTTPStatus.OK

                for url, value_expected in urls_data.items():
                    response = getattr(self, f"{user_type}_client").get(
                        url, follow=is_redirect
                    )

                    with self.subTest(f"{user_type} http_code {url}"):
                        if is_redirect:
                            redirect_url = (
                                value_expected["url_redirect"]
                                if "url_redirect" in value_expected
                                else URLTests.get_url_redirect_default(url)
                            )

                            self.assertRedirects(response, redirect_url)
                        else:
                            self.assertEqual(
                                response.status_code, http_code_expected
                            )

                    if is_ok:
                        with self.subTest(
                            f"{user_type} http_response "
                            f"{value_expected['template']}"
                        ):
                            self.assertTemplateUsed(
                                response, value_expected["template"]
                            )
