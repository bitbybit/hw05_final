from posts.tests.test_urls import URLTests as PostsURLTests
from posts.tests.test_views import ViewTests as PostsViewTests
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from http import HTTPStatus

User = get_user_model()

APP_NAME = "users"


class URLTests(PostsURLTests):
    urls_dict = {
        "guest": {
            HTTPStatus.OK: {
                "/auth/login/": {
                    "template": "users/login.html",
                },
                "/auth/logout/": {
                    "template": "users/logged_out.html",
                },
                "/auth/signup/": {
                    "template": "users/signup.html",
                },
                "/auth/password_reset/": {
                    "template": "users/password_reset_form.html",
                },
                "/auth/password_reset/done/": {
                    "template": "users/password_reset_done.html",
                },
                "/auth/reset/done/": {
                    "template": "users/password_reset_complete.html",
                },
                "/auth/reset/Mw/5xn-a8ccc0c97383dfb210cb/": {
                    "template": "users/password_reset_confirm.html",
                },
            },
            HTTPStatus.FOUND: {
                "/auth/password_change/": {
                    "template": "users/password_change_form.html",
                },
                "/auth/password_change/done/": {
                    "template": "users/password_change_done.html",
                },
            },
        },
    }

    @classmethod
    def setUpTestData(cls):
        cls.guest_client = Client()


class ViewTests(PostsViewTests):
    views_dict = {
        reverse(f"{APP_NAME}:login"): {
            "template": "users/login.html",
        },
        reverse(f"{APP_NAME}:logout"): {
            "template": "users/logged_out.html",
        },
        reverse(f"{APP_NAME}:signup"): {
            "template": "users/signup.html",
            "context": {
                "form": {
                    "first_name": forms.fields.CharField,
                    "last_name": forms.fields.CharField,
                    "username": forms.fields.CharField,
                    "email": forms.fields.EmailField,
                    "password1": forms.fields.CharField,
                    "password2": forms.fields.CharField,
                }
            },
        },
        reverse(f"{APP_NAME}:password_reset_form"): {
            "template": "users/password_reset_form.html",
        },
        reverse(f"{APP_NAME}:password_reset_done"): {
            "template": "users/password_reset_done.html",
        },
        reverse(f"{APP_NAME}:password_reset_complete"): {
            "template": "users/password_reset_complete.html",
        },
        reverse(
            f"{APP_NAME}:password_reset_confirm",
            kwargs={"uidb64": "Mw", "token": "5xn-a8ccc0c97383dfb210cb"},
        ): {
            "template": "users/password_reset_confirm.html",
        },
    }

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_entities_creation(self):
        pass


class FormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_entities_creation(self):
        """
        Отправка валидной формы со страницы регистрации.
        """
        user_count = User.objects.count()

        response = FormTests.client.post(
            reverse(f"{APP_NAME}:signup"),
            data={
                "username": "test",
                "password1": "cER5JuQqm",
                "password2": "cER5JuQqm",
            },
            follow=True,
        )

        self.assertEqual(User.objects.count(), user_count + 1)

        self.assertEqual(response.status_code, HTTPStatus.OK)
