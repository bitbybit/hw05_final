from django.http import (
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseServerError,
    HttpRequest,
)
from django.template import loader


def page_not_found(
    request: HttpRequest, exception: Exception
) -> HttpResponseNotFound:
    content = loader.render_to_string(
        "core/404.html", {"path": request.path}, request
    )
    return HttpResponseNotFound(content)


def server_error(request: HttpRequest) -> HttpResponseServerError:
    content = loader.render_to_string("core/500.html")
    return HttpResponseServerError(content, None, request)


def permission_denied(
    request: HttpRequest, exception: Exception
) -> HttpResponseForbidden:
    content = loader.render_to_string("core/403.html")
    return HttpResponseForbidden(content, None, request)


def csrf_failure(
    request: HttpRequest, reason: str = ""
) -> HttpResponseForbidden:
    content = loader.render_to_string("core/403csrf.html")
    return HttpResponseForbidden(content, None, request)
