from datetime import datetime

from django.http import HttpRequest


def year(request: HttpRequest):
    """Добавляет переменную с текущим годом."""
    return {"year": int(datetime.now().strftime("%Y"))}
