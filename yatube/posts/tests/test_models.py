from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Post, Group

User = get_user_model()

FIELDS_POST = {
    "text": {
        "verbose_name": "Текст поста",
        "help_text": "Введите текст поста",
    },
    "pub_date": {
        "verbose_name": "Дата публикации",
        "help_text": "Выберите дату публикации",
    },
    "author": {
        "verbose_name": "Автор",
        "help_text": "Выберите автора",
    },
    "group": {
        "verbose_name": "Группа",
        "help_text": "Группа, к которой относится пост",
    },
}

FIELDS_GROUP = {
    "title": {
        "verbose_name": "Название группы",
        "help_text": "Введите название группы",
    },
    "slug": {
        "verbose_name": "Адрес страницы",
        "help_text": "Введите адрес страницы",
    },
}


class ModelTests(TestCase):
    fields_dict = {
        "post": FIELDS_POST,
        "group": FIELDS_GROUP,
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="test")

        cls.group = Group.objects.create(title="Название", slug="test")

        cls.post = Post.objects.create(
            text="Текст больше 15 символов",
            group=cls.group,
            author=cls.user,
        )

    def test_post_object_name_is_cropped_text_field(self):
        """`__str__` класса `Post` — первые 15 символов поста."""
        post = ModelTests.post
        self.assertEqual(str(post), post.text[:15])

    def test_group_object_name_is_title_field(self):
        """`__str__` класса `Group` — название группы."""
        group = ModelTests.group
        self.assertEqual(str(group), group.title)

    def test_models_fields_verbose_name_and_help(self):
        """Заполнение `verbose_name` и `help_text` полей моделей."""
        for model_name, model_fields in self.fields_dict.items():
            model = getattr(ModelTests, model_name)

            for field_name, field_attrs in model_fields.items():
                for attr_name, attr_expected_value in field_attrs.items():
                    with self.subTest(
                        f"{model_name} {field_name} {attr_name}"
                    ):
                        self.assertEqual(
                            getattr(
                                model._meta.get_field(field_name),
                                attr_name,
                            ),
                            attr_expected_value,
                        )
