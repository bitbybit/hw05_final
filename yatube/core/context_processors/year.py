from django.http import HttpRequest
from django.utils import timezone


def year(request: HttpRequest):
    """Добавляет переменную с текущим годом."""
    return {"year": int(timezone.now().strftime("%Y"))}
