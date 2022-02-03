from typing import Optional

from django.template import loader
from django.http import (
    HttpRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
)


def page_not_found(
    request: HttpRequest, exception: Exception
) -> HttpResponseNotFound:
    content = loader.render_to_string(
        "core/404.html", {"path": request.path}, request
    )

    return HttpResponseNotFound(content)


def server_error(request: HttpRequest) -> HttpResponseServerError:
    content = loader.render_to_string("core/500.html", None, request)

    return HttpResponseServerError(content)


def permission_denied(
    request: HttpRequest, exception: Optional[Exception] = None
) -> HttpResponseForbidden:
    content = loader.render_to_string("core/403.html", None, request)

    return HttpResponseForbidden(content)


def csrf_failure(
    request: HttpRequest, reason: str = ""
) -> HttpResponseForbidden:
    content = loader.render_to_string("core/403csrf.html", None, request)

    return HttpResponseForbidden(content)
