from django.urls import path

from . import views

app_name = "posts"

urlpatterns = [
    path("group/<slug:slug>/", views.group_posts, name="group_list"),
    path("", views.index, name="index"),
]
