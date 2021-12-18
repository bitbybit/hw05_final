from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title: str = models.CharField(max_length=255)
    slug: str = models.CharField(max_length=255, unique=True)
    description: str = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text: str = models.TextField()
    pub_date: str = models.DateTimeField(auto_now_add=True)
    author: int = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    group: int = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="group",
        blank=True,
        null=True,
    )
