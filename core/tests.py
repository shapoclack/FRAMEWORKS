"""Тесты приложения core."""

from django.test import Client, TestCase
from django.urls import reverse


class CoreBasicTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_status(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)

    def test_about_status(self):
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)

    def test_http_info_status(self):
        response = self.client.get(reverse("core:http_info"))
        self.assertEqual(response.status_code, 200)
