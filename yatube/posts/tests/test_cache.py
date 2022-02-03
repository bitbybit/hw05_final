from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, User

APP_NAME = "posts"


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username="test")

        Post.objects.create(
            text="Закешированный текст",
            author=cls.user,
        )

        cache.clear()

    def setUp(self):
        self.client = Client()

    def cache_post_index(self):
        """Проверка кэширования списка постов главной страницы."""
        post = Post.objects.latest("id")
        post_text = str.encode(post.text)
        cache_key = make_template_fragment_key("index_page", [1])

        with self.subTest("Текст поста на странице"):
            response = self.client.get(reverse(f"{APP_NAME}:index"))
            self.assertIn(post_text, response.content)

        with self.subTest("Кеш создан"):
            self.assertIsNotNone(cache.get(cache_key))

        with self.subTest("Текст поста на странице после удаления поста"):
            post.delete()
            response = self.client.get(reverse(f"{APP_NAME}:index"))
            self.assertIn(post_text, response.content)

        with self.subTest("Текста поста нет на странице после очистки кеша"):
            cache.delete(cache_key)
            response = self.client.get(reverse(f"{APP_NAME}:index"))
            self.assertNotIn(post_text, response.content)

    def test_cache(self):
        """Проверка кэширования."""
        self.cache_post_index()
