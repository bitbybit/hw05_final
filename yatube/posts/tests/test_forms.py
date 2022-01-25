from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from ..models import Post, User

APP_NAME = "posts"


class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test")

        cls.post = Post.objects.create(
            text="Текст",
            author=cls.user,
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(FormTests.user)

    def test_entities_creation(self):
        """
        Отправка валидной формы со страницы создания поста.
        """
        post_count = Post.objects.count()

        response = self.client.post(
            reverse(f"{APP_NAME}:post_create"),
            data={
                "text": "Текст",
            },
            follow=True,
        )

        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_entities_modification(self):
        """
        Отправка валидной формы со страницы редактирования поста.
        """
        text_new = "Текст измененный"

        response = self.client.post(
            reverse(
                f"{APP_NAME}:post_update", kwargs={"pk": FormTests.post.id}
            ),
            data={
                "text": text_new,
            },
            follow=True,
        )

        self.assertEqual(Post.objects.get(pk=FormTests.post.id).text, text_new)

        self.assertEqual(response.status_code, HTTPStatus.OK)
