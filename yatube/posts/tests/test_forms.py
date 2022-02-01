import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from http import HTTPStatus
from ..models import Post, User

APP_NAME = "posts"

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test")

        cls.post = Post.objects.create(
            text="Текст",
            author=cls.user,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.force_login(FormTests.user)

    def test_entities_creation(self):
        """
        Отправка валидной формы со страницы создания поста.
        """
        post_count = Post.objects.count()

        text = "Текст с картинкой"

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

        response = self.client.post(
            reverse(f"{APP_NAME}:post_create"),
            data={
                "text": text,
                "image": image,
            },
            follow=True,
        )

        self.assertEqual(Post.objects.count(), post_count + 1)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertTrue(
            Post.objects.filter(
                text=text, image=f"{APP_NAME}/{image.name}"
            ).exists()
        )

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
