from typing import Optional

from django import forms
from django.core.exceptions import ValidationError


def clean_int(value) -> Optional[int]:
    try:
        return forms.IntegerField().clean(value)
    except ValidationError:
        return None
