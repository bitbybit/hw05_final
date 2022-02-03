import shutil
import tempfile
from typing import Callable, Dict, Union

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from ..models import Comment, Group, Post, User

APP_NAME = "posts"

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

FORM_FIELDS_POST = {
    "text": forms.fields.CharField,
    "group": forms.fields.ChoiceField,
}
FORM_FIELDS_COMMENT = {
    "text": forms.fields.CharField,
}

POSTS_LIMIT = 10
POST_TITLE_LENGTH_LIMIT = 30
COMMENTS_LIMIT = 10


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="test")

        cls.group = Group.objects.create(title="Название", slug="test")
        cls.group_another = Group.objects.create(
            title="Название другой группы", slug="test-another"
        )

        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        image = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        posts = []
        for i in range(POSTS_LIMIT + 5):
            posts.append(
                Post.objects.create(
                    text="Текст",
                    image=image,
                    group=cls.group,
                    author=cls.user,
                )
            )
        cls.posts = posts
        cls.post = posts[0]
        cls.post_last = posts[-1]

        for i in range(COMMENTS_LIMIT + 5):
            Comment.objects.create(
                text="Комментарий",
                post=cls.post,
                author=cls.user,
            )

        cls.set_views_dict(cls)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.force_login(ViewTests.user)

    def set_views_dict(self):
        """
        Создает словарь-конфиг проверяемых сущностей формата:
        - url pattern
          - template path
          - context vars
            - page_obj
              - pages
                - page number
                  - page items count
              - type
                - item class
              - item additional criteria
            - form
              - field name
                - field class
            - ...

        Вызывается после создания фикстур.
        """
        self.views_dict = {
            reverse(
                f"{APP_NAME}:group_list", kwargs={"slug": ViewTests.group.slug}
            ): {
                "template": "posts/group_list.html",
                "context": {
                    "title": f"Записи сообщества {ViewTests.group.title}",
                    "group": ViewTests.group,
                    "page_obj": {
                        "pages": {
                            1: POSTS_LIMIT,
                            2: ViewTests.group.posts.count() - POSTS_LIMIT,
                        },
                        "type": Post,
                        "item_criteria": lambda item: item.group.id
                        == ViewTests.group.id,
                    },
                },
            },
            reverse(f"{APP_NAME}:index"): {
                "template": "posts/index.html",
                "context": {
                    "title": "Последние обновления на сайте",
                    "year": int(timezone.now().strftime("%Y")),
                    "page_obj": {
                        "pages": {
                            1: POSTS_LIMIT,
                            2: len(ViewTests.posts) - POSTS_LIMIT,
                        },
                        "type": Post,
                    },
                },
            },
            reverse(
                f"{APP_NAME}:profile",
                kwargs={"username": ViewTests.user.username},
            ): {
                "template": "posts/profile.html",
                "context": {
                    "title": f"Профайл пользователя {ViewTests.user.username}",
                    "author": ViewTests.user,
                    "page_obj": {
                        "pages": {
                            1: POSTS_LIMIT,
                            2: ViewTests.user.posts.count() - POSTS_LIMIT,
                        },
                        "type": Post,
                        "item_criteria": lambda item: item.author.id
                        == ViewTests.user.id,
                    },
                },
            },
            reverse(
                f"{APP_NAME}:post_detail",
                kwargs={"pk": ViewTests.post.id},
            ): {
                "template": "posts/post_detail.html",
                "context": {
                    "title": f"Пост "
                    f"{ViewTests.post.text[:POST_TITLE_LENGTH_LIMIT]}",
                    "post": ViewTests.post,
                    "form": FORM_FIELDS_COMMENT,
                    "page_obj": {
                        "pages": {
                            1: COMMENTS_LIMIT,
                            2: ViewTests.post.comments.count()
                            - COMMENTS_LIMIT,
                        },
                        "type": Comment,
                        "item_criteria": lambda item: item.post.id
                        == ViewTests.post.id,
                    },
                },
            },
            reverse(f"{APP_NAME}:post_create"): {
                "template": "posts/create_post.html",
                "context": {
                    "title": "Новый пост",
                    "form": FORM_FIELDS_POST,
                },
            },
            reverse(
                f"{APP_NAME}:post_update", kwargs={"pk": ViewTests.post.id}
            ): {
                "template": "posts/create_post.html",
                "context": {
                    "title": f"Редактировать пост #{ViewTests.post.id}",
                    "is_edit": True,
                    "form": FORM_FIELDS_POST,
                },
            },
        }

    def context_pagination_checks(
        self,
        path_name: str,
        response: HttpResponse,
        checks: Dict[
            str,
            Union[
                Dict[int, int], models.Model, Callable[[models.Model], bool]
            ],
        ],
    ):
        context_key = "page_obj"
        context_value = checks

        items_page_first = response.context.get(context_key)
        items_page_first_count = len(items_page_first)
        items_page_first_count_expected = context_value["pages"][1]

        with self.subTest(f"{path_name} page 1 items count"):
            self.assertEqual(
                items_page_first_count,
                items_page_first_count_expected,
            )

        if "item_criteria" in context_value:
            with self.subTest(f"{path_name} page 1 items criteria"):
                for item in items_page_first:
                    self.assertTrue(context_value["item_criteria"](item))

        for (
            page_number,
            items_page_n_count_expected,
        ) in context_value["pages"].items():
            if page_number != 1:
                response_page_n = self.client.get(
                    f"{path_name}?page={page_number}"
                )
                items_page_n = response_page_n.context.get(context_key)
                items_page_n_count = len(items_page_n)

                with self.subTest(
                    f"{path_name} page {page_number} items count"
                ):
                    self.assertEqual(
                        items_page_n_count,
                        items_page_n_count_expected,
                    )

                if "item_criteria" in context_value:
                    with self.subTest(
                        f"{path_name} page {page_number} " f"items criteria"
                    ):
                        for item in items_page_n:
                            self.assertTrue(
                                context_value["item_criteria"](item)
                            )

        with self.subTest(f"{path_name} pagination item type"):
            item = response.context.get(context_key).object_list[0]
            item_type_expected = context_value["type"]

            self.assertIsInstance(item, item_type_expected)

    def context_form_checks(
        self,
        path_name: str,
        response: HttpResponse,
        form_fields: Dict[str, forms.fields.Field],
    ):
        for (
            form_field_key,
            form_field_expected,
        ) in form_fields.items():
            with self.subTest(f"{path_name} form {form_field_key}"):
                form_field = response.context.get("form").fields.get(
                    form_field_key
                )

                self.assertIsInstance(
                    form_field,
                    form_field_expected,
                )

    def test_template_and_context(self):
        """
        Соответствие имен `urlpatterns` ожидаемым шаблонам и их содержимому.

        - полям форм
        - длине списков паджинации постранично
        - типу элемента списка паджинации
        - любому доп. условию для элемента списка паджинации (если задано)
        - контекстным переменным из `views_dict`
        """
        for path_name, view_expected in self.views_dict.items():
            response = self.client.get(path_name)

            with self.subTest(f"{path_name} {view_expected['template']}"):
                self.assertTemplateUsed(response, view_expected["template"])

            if "context" not in view_expected:
                continue

            for context_key, context_value in view_expected["context"].items():
                if context_key == "page_obj":
                    self.context_pagination_checks(
                        path_name, response, context_value
                    )

                elif context_key == "form":
                    self.context_form_checks(
                        path_name, response, context_value
                    )

                else:
                    with self.subTest(f"{path_name} context {context_key}"):
                        self.assertEqual(
                            response.context.get(context_key),
                            context_value,
                        )

    def entities_creation_post_index(self):
        """
        Проверка вывода поста в группе на главную страницу.
        """
        response = self.client.get(reverse(f"{APP_NAME}:index"))
        items = response.context.get("page_obj")

        with self.subTest("Пост на главной странице"):
            self.assertIn(ViewTests.post_last, items)

    def entities_creation_post_group(self):
        """
        Проверка вывода поста в группе на страницу группы.
        """
        response = self.client.get(
            reverse(f"{APP_NAME}:group_list", kwargs={"slug": "test"})
        )
        items = response.context.get("page_obj")

        with self.subTest("Пост в своей группе"):
            self.assertIn(ViewTests.post_last, items)

    def entities_creation_post_group_another(self):
        """
        Проверка вывода поста в группе на страницу чужой группы.
        """
        response = self.client.get(
            reverse(f"{APP_NAME}:group_list", kwargs={"slug": "test-another"})
        )
        items = response.context.get("page_obj")

        with self.subTest("Пост в не связанной группе"):
            self.assertNotIn(ViewTests.post_last, items)

    def entities_creation_post_profile(self):
        """
        Проверка вывода поста в группе на страницу профиля автора.
        """
        response = self.client.get(
            reverse(
                f"{APP_NAME}:profile",
                kwargs={"username": ViewTests.post_last.author.username},
            )
        )
        items = response.context.get("page_obj")

        with self.subTest("Пост в профиле автора"):
            self.assertIn(ViewTests.post_last, items)

    def entities_creation_post_detail(self):
        """
        Проверка вывода поста в группе на детальную страницу поста.
        """
        response = self.client.get(
            reverse(
                f"{APP_NAME}:post_detail",
                kwargs={"pk": ViewTests.post_last.id},
            )
        )
        item = response.context.get("post")

        with self.subTest("Пост на детальной странице"):
            self.assertEqual(ViewTests.post_last, item)

    def entities_creation_comment_post(self):
        """
        Проверка вывода комментария на детальную страницу поста.
        """
        response = self.client.get(
            reverse(
                f"{APP_NAME}:post_detail",
                kwargs={"pk": ViewTests.post.id},
            )
        )
        items = response.context.get("page_obj")
        comment_last = ViewTests.post.comments.latest("id")

        with self.subTest("Комментарий на детальной странице своего поста"):
            self.assertIn(comment_last, items)

    def entities_creation_comment_post_another(self):
        """
        Проверка вывода комментария на детальную страницу другого поста.
        """
        response = self.client.get(
            reverse(
                f"{APP_NAME}:post_detail",
                kwargs={"pk": ViewTests.post_last.id},
            )
        )
        items = response.context.get("page_obj")
        comment_last = ViewTests.post.comments.latest("id")

        with self.subTest("Комментарий на детальной странице другого поста"):
            self.assertNotIn(comment_last, items)

    def test_entities_creation(self):
        """
        Проверка создания поста и комментария.
        """
        self.entities_creation_post_index()
        self.entities_creation_post_group()
        self.entities_creation_post_group_another()
        self.entities_creation_post_profile()
        self.entities_creation_post_detail()

        self.entities_creation_comment_post()
        self.entities_creation_comment_post_another()
