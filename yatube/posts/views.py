from django.http import HttpResponse, HttpRequest
from django.template import loader


def index(request: HttpRequest) -> HttpResponse:
    template = loader.get_template("posts/index.html")

    title = "Это главная страница проекта Yatube"

    context = {
        "title": title,
    }

    return HttpResponse(template.render(context, request))


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    template = loader.get_template("posts/group_posts.html")

    title = "Здесь будет информация о группах проекта Yatube"

    context = {
        "title": title,
    }

    return HttpResponse(template.render(context, request))
