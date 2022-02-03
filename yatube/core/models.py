from django.db import models


class CreatedModel(models.Model):
    created = models.DateTimeField(
        verbose_name="Дата создания",
        help_text="Выберите дату",
        auto_now_add=True,
    )

    class Meta:
        abstract = True
