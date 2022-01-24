from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name="Название группы",
        help_text="Введите название группы",
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name="Адрес страницы",
        help_text="Введите адрес страницы",
        max_length=255,
        unique=True,
    )
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст поста", help_text="Введите текст поста"
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации",
        help_text="Выберите дату публикации",
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
        help_text="Выберите автора",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name="Группа",
        help_text="Группа, к которой относится пост",
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:15]
