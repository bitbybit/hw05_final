from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("group/<slug:slug>/", views.group_posts, name="group_list"),
    path("", views.index, name="index"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("posts/<int:pk>/", views.PostDetail.as_view(), name="post_detail"),
    path(
        "create/",
        login_required(views.PostCreate.as_view()),
        name="post_create",
    ),
    path(
        "posts/<int:pk>/edit/",
        views.PostUpdate.as_view(),
        name="post_update",
    ),
    path(
        "posts/<int:pk>/comment/",
        login_required(views.PostDetail.as_view()),
        name="add_comment",
    ),
]
