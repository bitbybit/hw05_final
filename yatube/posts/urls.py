from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = "posts"

urlpatterns = [
    path("group/<slug:slug>/", views.group_posts, name="group_list"),
    path("", views.index, name="index"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path(
        "create/",
        login_required(views.PostCreate.as_view()),
        name="post_create",
    ),
    path(
        "posts/<int:pk>/edit/",
        login_required(views.PostUpdate.as_view()),
        name="post_update",
    ),
]
