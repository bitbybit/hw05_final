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

        for i in range(5):
            Post.objects.create(
                text="Текст",
                author=cls.user,
            )

    def setUp(self):
        self.client = Client()

    def cache_post_index(self):
        """Проверка кэширования списка постов главной страницы."""
        self.client.get(reverse(f"{APP_NAME}:index"))

        cache_key = make_template_fragment_key("index_page", [1])
        cached_fragment = cache.get(cache_key)

        with self.subTest(
            "Кеш фрагмента шаблона постов главной страницы создан"
        ):
            self.assertIsNotNone(cached_fragment)

    def test_cache(self):
        """Проверка кэширования."""
        self.cache_post_index()
