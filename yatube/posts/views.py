from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Group

POSTS_LIMIT = 10


def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.all()

    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get("page")

    context = {
        "title": "Последние обновления на сайте",
        "page_obj": paginator.get_page(page_number),
    }

    return HttpResponse(render(request, "posts/index.html", context))


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get("page")

    context = {
        "title": f"Записи сообщества {group}",
        "page_obj": paginator.get_page(page_number),
    }

    return HttpResponse(render(request, "posts/group_list.html", context))
