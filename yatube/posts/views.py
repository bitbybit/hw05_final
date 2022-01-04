from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Post, Group

User = get_user_model()

POSTS_LIMIT = 10
POST_TITLE_LENGTH_LIMIT = 30


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


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    title = f"Профайл пользователя {author.get_full_name() or author.username}"

    paginator = Paginator(posts, POSTS_LIMIT)
    page_number = request.GET.get("page")

    context = {
        "title": title,
        "author": author,
        "page_obj": paginator.get_page(page_number),
    }

    return render(request, "posts/profile.html", context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=post_id)

    context = {
        "title": f"Пост {post.text[:POST_TITLE_LENGTH_LIMIT]}",
        "post": post,
    }

    return render(request, "posts/post_detail.html", context)
