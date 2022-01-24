from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.views.generic.edit import CreateView, UpdateView
from .models import Post, Group
from .forms import PostForm

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
        "group": group,
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


class PostCreate(CreateView):
    form_class = PostForm
    template_name = "posts/create_post.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Новый пост"

        return context

    def get_success_url(self):
        return reverse_lazy(
            "posts:profile",
            kwargs={"username": self.request.user.username},
        )

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()

        return super().form_valid(form)


class PostUpdate(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/create_post.html"

    def dispatch(self, request, *args, **kwargs):
        post = Post.objects.get(id=kwargs["pk"])

        if post.author.id != request.user.id:
            return redirect(
                "posts:post_detail",
                post_id=post.id,
            )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"Редактировать пост #{self.object.id}"
        context["is_edit"] = True

        return context

    def get_success_url(self):
        return reverse_lazy(
            "posts:post_update",
            kwargs={"pk": self.object.id},
        )
