import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Post, User

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

        cls.post_image_text = "Текст с картинкой"
        cls.post_image_small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        cls.comment_text = "Комментарий"
        cls.comment_text_modified = "Текст измененный"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.force_login(FormTests.user)

    def entities_creation_post(self):
        count = Post.objects.count()

        image = SimpleUploadedFile(
            name="small.gif",
            content=FormTests.post_image_small_gif,
            content_type="image/gif",
        )

        response = self.client.post(
            reverse(f"{APP_NAME}:post_create"),
            data={
                "text": FormTests.post_image_text,
                "image": image,
            },
            follow=True,
        )

        self.assertEqual(Post.objects.count(), count + 1)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertTrue(
            Post.objects.filter(
                text=FormTests.post_image_text,
                image=f"{APP_NAME}/{image.name}",
            ).exists()
        )

    def entities_creation_comment(self):
        count = Comment.objects.count()

        response = self.client.post(
            reverse(
                f"{APP_NAME}:add_comment", kwargs={"pk": FormTests.post.id}
            ),
            data={
                "text": FormTests.comment_text,
            },
            follow=True,
        )

        self.assertEqual(Comment.objects.count(), count + 1)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertTrue(
            Comment.objects.filter(text=FormTests.comment_text).exists()
        )

    def test_entities_creation(self):
        """
        Отправка валидной формы со страниц создания поста и комментария поста.
        """
        self.entities_creation_post()
        self.entities_creation_comment()

    def entities_modification_post(self):
        response = self.client.post(
            reverse(
                f"{APP_NAME}:post_update", kwargs={"pk": FormTests.post.id}
            ),
            data={
                "text": FormTests.comment_text_modified,
            },
            follow=True,
        )

        self.assertEqual(
            Post.objects.get(pk=FormTests.post.id).text,
            FormTests.comment_text_modified,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_entities_modification(self):
        """
        Отправка валидной формы со страницы редактирования поста.
        """
        self.entities_modification_post()
