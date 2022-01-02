from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404

from .models import Post, Group

POSTS_LIMIT = 10


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "title": "Последние обновления на сайте",
        "posts": Post.objects.all()[:POSTS_LIMIT],
    }

    return HttpResponse(render(request, "posts/index.html", context))


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)

    context = {
        "title": f"Записи сообщества {group}",
        "posts": group.posts.all(),
    }

    return HttpResponse(render(request, "posts/group_list.html", context))
