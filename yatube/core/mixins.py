from http import HTTPStatus
from typing import Callable, Dict, Union

from django import forms
from django.db import models
from django.http import HttpResponse


class TestViewsMixin:
    def context_pagination_checks(
        self,
        path_name: str,
        response: HttpResponse,
        checks: Dict[
            str,
            Union[
                Dict[int, int], models.Model, Callable[[models.Model], bool]
            ],
        ],
    ):
        context_key = "page_obj"
        context_value = checks

        items_page_first = response.context.get(context_key)
        items_page_first_count = len(items_page_first)
        items_page_first_count_expected = context_value["pages"][1]

        with self.subTest(f"{path_name} page 1 items count"):
            self.assertEqual(
                items_page_first_count,
                items_page_first_count_expected,
            )

        if "item_criteria" in context_value:
            with self.subTest(f"{path_name} page 1 items criteria"):
                for item in items_page_first:
                    self.assertTrue(context_value["item_criteria"](item))

        for (
            page_number,
            items_page_n_count_expected,
        ) in context_value["pages"].items():
            if page_number != 1:
                response_page_n = self.client.get(
                    f"{path_name}?page={page_number}"
                )
                items_page_n = response_page_n.context.get(context_key)
                items_page_n_count = len(items_page_n)

                with self.subTest(
                    f"{path_name} page {page_number} items count"
                ):
                    self.assertEqual(
                        items_page_n_count,
                        items_page_n_count_expected,
                    )

                if "item_criteria" in context_value:
                    with self.subTest(
                        f"{path_name} page {page_number} " f"items criteria"
                    ):
                        for item in items_page_n:
                            self.assertTrue(
                                context_value["item_criteria"](item)
                            )

        with self.subTest(f"{path_name} pagination item type"):
            item = response.context.get(context_key).object_list[0]
            item_type_expected = context_value["type"]

            self.assertIsInstance(item, item_type_expected)

    def context_form_checks(
        self,
        path_name: str,
        response: HttpResponse,
        form_fields: Dict[str, forms.fields.Field],
    ):
        for (
            form_field_key,
            form_field_expected,
        ) in form_fields.items():
            with self.subTest(f"{path_name} form {form_field_key}"):
                form_field = response.context.get("form").fields.get(
                    form_field_key
                )

                self.assertIsInstance(
                    form_field,
                    form_field_expected,
                )

    def test_template_and_context(self):
        """
        Соответствие имен `urlpatterns` ожидаемым шаблонам и их содержимому.

        - полям форм
        - длине списков паджинации постранично
        - типу элемента списка паджинации
        - любому доп. условию для элемента списка паджинации (если задано)
        - контекстным переменным из `views_dict`
        """
        for path_name, view_expected in self.views_dict.items():
            response = self.client.get(path_name)

            with self.subTest(f"{path_name} {view_expected['template']}"):
                self.assertTemplateUsed(response, view_expected["template"])

            if "context" not in view_expected:
                continue

            for context_key, context_value in view_expected["context"].items():
                if context_key == "page_obj":
                    self.context_pagination_checks(
                        path_name, response, context_value
                    )

                elif context_key == "form":
                    self.context_form_checks(
                        path_name, response, context_value
                    )

                else:
                    with self.subTest(f"{path_name} context {context_key}"):
                        self.assertEqual(
                            response.context.get(context_key),
                            context_value,
                        )


class TestURLsMixin:
    @staticmethod
    def is_redirect(http_code: int) -> bool:
        return http_code == HTTPStatus.FOUND

    @staticmethod
    def is_ok(http_code: int) -> bool:
        return http_code == HTTPStatus.OK

    @staticmethod
    def is_not_found(http_code: int) -> bool:
        return http_code == HTTPStatus.NOT_FOUND

    @staticmethod
    def get_url_redirect_default(url: str) -> str:
        """
        Возвращает URL, куда должен перенаправляться пользователь если
        отсутствует доступ (для случаев когда в `urls_dict` не задан
        ожидаемый URL перенаправления проверяемой страницы).
        """
        return f"/auth/login/?next={url}"

    def test_pages_http_code_and_template(self):
        """
        Проверка ожидаемого кода ответа страниц и соответствия шаблона.
        (для кодов ответа 200 и 404)
        """
        for user_type, urls in self.urls_dict.items():
            for http_code_expected, urls_data in urls.items():
                is_redirect = self.is_redirect(http_code_expected)
                is_ok = self.is_ok(http_code_expected)
                is_not_found = self.is_not_found(http_code_expected)

                for url, value_expected in urls_data.items():
                    response = getattr(self, f"{user_type}_client").get(
                        url, follow=is_redirect
                    )

                    with self.subTest(f"{user_type} http_code {url}"):
                        if is_redirect:
                            redirect_url = (
                                value_expected["url_redirect"]
                                if "url_redirect" in value_expected
                                else self.get_url_redirect_default(url)
                            )

                            self.assertRedirects(response, redirect_url)
                        else:
                            self.assertEqual(
                                response.status_code, http_code_expected
                            )

                    if is_ok or is_not_found:
                        with self.subTest(
                            f"{user_type} http_response "
                            f"{value_expected['template']}"
                        ):
                            self.assertTemplateUsed(
                                response, value_expected["template"]
                            )
