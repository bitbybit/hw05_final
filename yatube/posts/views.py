from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404

from .models import Post, Group


def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.order_by("-pub_date")[:10]

    title = "Последние обновления на сайте"

    context = {
        "title": title,
        "posts": posts,
    }

    return HttpResponse(render(request, "posts/index.html", context))


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by("-pub_date")[:10]

    title = f"Записи сообщества {group.title}"

    context = {
        "title": title,
        "posts": posts,
    }

    return HttpResponse(render(request, "posts/group_posts.html", context))
