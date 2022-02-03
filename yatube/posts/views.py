from core.views import permission_denied
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import CommentForm, PostForm
from .models import Group, Post

User = get_user_model()

POSTS_LIMIT = 10
COMMENTS_LIMIT = 10
POST_TITLE_LENGTH_LIMIT = 30


class Index(TemplateView):
    template_name = "posts/index.html"

    def get_context_data(self, **kwargs):
        posts = Post.objects.all()

        paginator = Paginator(posts, POSTS_LIMIT)
        page_number = self.request.GET.get("page")

        context = super().get_context_data(**kwargs)
        context["title"] = "Последние обновления на сайте"
        context["page_obj"] = paginator.get_page(page_number)

        return context


class GroupPosts(TemplateView):
    template_name = "posts/group_list.html"

    def get_context_data(self, **kwargs):
        group = get_object_or_404(Group, slug=kwargs["slug"])
        posts = group.posts.all()

        paginator = Paginator(posts, POSTS_LIMIT)
        page_number = self.request.GET.get("page")

        context = super().get_context_data(**kwargs)
        context["title"] = f"Записи сообщества {group}"
        context["group"] = group
        context["page_obj"] = paginator.get_page(page_number)

        return context


class Profile(TemplateView):
    template_name = "posts/profile.html"

    def get_context_data(self, **kwargs):
        author = get_object_or_404(User, username=kwargs["username"])
        posts = author.posts.all()
        title = (
            f"Профайл пользователя {author.get_full_name() or author.username}"
        )

        paginator = Paginator(posts, POSTS_LIMIT)
        page_number = self.request.GET.get("page")

        context = super().get_context_data(**kwargs)
        context["title"] = title
        context["author"] = author
        context["page_obj"] = paginator.get_page(page_number)

        return context


class PostDetail(CreateView):
    form_class = CommentForm
    template_name = "posts/post_detail.html"
    post_object = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs["pk"])

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        comments = self.post_object.comments.all()

        paginator = Paginator(comments, COMMENTS_LIMIT)
        page_number = self.request.GET.get("page")

        context = super().get_context_data(**kwargs)
        context[
            "title"
        ] = f"Пост {self.post_object.text[:POST_TITLE_LENGTH_LIMIT]}"
        context["post"] = self.post_object
        context["page_obj"] = paginator.get_page(page_number)

        return context

    def get_success_url(self):
        return reverse_lazy(
            "posts:post_detail",
            kwargs={"pk": self.post_object.id},
        )

    def form_valid(self, form: CommentForm):
        if not self.request.user.is_authenticated:
            return permission_denied(self.request)

        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.post = self.post_object
        self.object.save()

        return super().form_valid(form)


class PostCreate(LoginRequiredMixin, CreateView):
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

    def form_valid(self, form: PostForm):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()

        return super().form_valid(form)


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/create_post.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs["pk"])

        if post.author.id != request.user.id:
            return redirect(
                "posts:post_detail",
                pk=post.id,
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
